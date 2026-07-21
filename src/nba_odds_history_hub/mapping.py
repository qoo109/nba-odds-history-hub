"""Additive schedule-version and source-event mapping helpers."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .database import connect_database, initialize_database

ALLOWED_STATUSES = {
    "unmapped",
    "candidate_unverified",
    "verified",
    "rejected",
    "quarantined",
    "mapped",
}
ALLOWED_METHODS = {
    "none",
    "explicit_official_id",
    "explicit_project_id",
    "exact_date_home_away_candidate",
    "manual_audited_mapping",
    "synthetic_fixture_only",
    "legacy_explicit_mapping",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _require_timezone_aware(value: str, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed.isoformat()


def _require_sha256(value: str | None, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    normalized = str(value or "").lower()
    if not _SHA256.fullmatch(normalized):
        raise ValueError("source_payload_sha256 must be 64 lowercase hex characters")
    return normalized


def _require_status(value: str) -> str:
    if value not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported mapping status: {value}")
    return value


def _require_method(value: str) -> str:
    if value not in ALLOWED_METHODS:
        raise ValueError(f"Unsupported mapping method: {value}")
    return value


def record_schedule_version(
    database: str | Path,
    *,
    source_id: str,
    source_event_id: int,
    scheduled_tipoff: str,
    home_team_abbr: str,
    away_team_abbr: str,
    observed_at: str,
    source_payload_sha256: str,
    mapping_status: str = "candidate_unverified",
    mapping_method: str = "exact_date_home_away_candidate",
) -> dict[str, Any]:
    """Insert a new schedule version only when identity or tipoff changed."""
    initialize_database(database)
    tipoff = _require_timezone_aware(scheduled_tipoff, "scheduled_tipoff")
    observed = _require_timezone_aware(observed_at, "observed_at")
    payload_hash = _require_sha256(source_payload_sha256)
    status = _require_status(mapping_status)
    method = _require_method(mapping_method)
    home = home_team_abbr.strip().upper()
    away = away_team_abbr.strip().upper()
    if not home or not away:
        raise ValueError("home_team_abbr and away_team_abbr are required")
    if home == away:
        raise ValueError("home and away teams must differ")

    with connect_database(database) as connection:
        source_event = connection.execute(
            "SELECT mapping_status FROM source_events WHERE source_id = ? AND source_event_id = ?",
            (source_id, int(source_event_id)),
        ).fetchone()
        if source_event is None:
            raise KeyError(f"Unknown source event: {source_id}/{source_event_id}")

        current = connection.execute(
            """
            SELECT version_number, scheduled_tipoff, home_team_abbr, away_team_abbr,
                   mapping_status, mapping_method, source_payload_sha256
            FROM source_event_schedule_versions
            WHERE source_id = ? AND source_event_id = ? AND is_current = 1
            """,
            (source_id, int(source_event_id)),
        ).fetchone()
        identity = (tipoff, home, away, status, method, payload_hash)
        if current is not None:
            current_identity = (
                current["scheduled_tipoff"],
                current["home_team_abbr"],
                current["away_team_abbr"],
                current["mapping_status"],
                current["mapping_method"],
                current["source_payload_sha256"],
            )
            if current_identity == identity:
                return {
                    "inserted": False,
                    "version_number": int(current["version_number"]),
                    "reason": "exact_current_schedule_duplicate",
                }

        next_version = int(current["version_number"]) + 1 if current is not None else 1
        connection.execute(
            """
            UPDATE source_event_schedule_versions
            SET is_current = 0
            WHERE source_id = ? AND source_event_id = ? AND is_current = 1
            """,
            (source_id, int(source_event_id)),
        )
        connection.execute(
            """
            INSERT INTO source_event_schedule_versions (
                source_id, source_event_id, version_number, scheduled_tipoff,
                home_team_abbr, away_team_abbr, mapping_status, mapping_method,
                observed_at, source_payload_sha256, is_current, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                source_id,
                int(source_event_id),
                next_version,
                tipoff,
                home,
                away,
                status,
                method,
                observed,
                payload_hash,
                _utc_now_iso(),
            ),
        )
        connection.execute(
            """
            UPDATE source_events
            SET scheduled_tipoff = ?, last_observed_at = MAX(last_observed_at, ?)
            WHERE source_id = ? AND source_event_id = ?
            """,
            (tipoff, observed, source_id, int(source_event_id)),
        )
    return {"inserted": True, "version_number": next_version, "reason": "new_schedule_version"}


def record_mapping_decision(
    database: str | Path,
    *,
    source_id: str,
    source_event_id: int,
    new_status: str,
    mapping_method: str,
    reason_code: str,
    actor_type: str,
    decided_at: str,
    canonical_event_id: str | None = None,
    source_payload_sha256: str | None = None,
    note: str | None = None,
    propagate_verified_mapping: bool = False,
) -> dict[str, Any]:
    """Record one audited mapping decision and update source-event status."""
    initialize_database(database)
    status = _require_status(new_status)
    method = _require_method(mapping_method)
    decided = _require_timezone_aware(decided_at, "decided_at")
    payload_hash = _require_sha256(source_payload_sha256, optional=True)
    reason = reason_code.strip()
    actor = actor_type.strip()
    if not reason or not actor:
        raise ValueError("reason_code and actor_type are required")
    if status in {"verified", "mapped"} and not canonical_event_id:
        raise ValueError("verified or mapped status requires canonical_event_id")
    if status in {"rejected", "quarantined", "unmapped"} and canonical_event_id is not None:
        raise ValueError(f"{status} status cannot retain canonical_event_id")

    with connect_database(database) as connection:
        current = connection.execute(
            """
            SELECT mapping_status, canonical_event_id
            FROM source_events
            WHERE source_id = ? AND source_event_id = ?
            """,
            (source_id, int(source_event_id)),
        ).fetchone()
        if current is None:
            raise KeyError(f"Unknown source event: {source_id}/{source_event_id}")
        if canonical_event_id is not None:
            canonical = connection.execute(
                "SELECT 1 FROM canonical_events WHERE canonical_event_id = ?",
                (canonical_event_id,),
            ).fetchone()
            if canonical is None:
                raise KeyError(f"Unknown canonical event: {canonical_event_id}")

        previous_status = str(current["mapping_status"])
        connection.execute(
            """
            INSERT INTO source_event_mapping_audit (
                source_id, source_event_id, canonical_event_id, previous_status,
                new_status, mapping_method, reason_code, actor_type, decided_at,
                source_payload_sha256, note, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                int(source_event_id),
                canonical_event_id,
                previous_status,
                status,
                method,
                reason,
                actor,
                decided,
                payload_hash,
                note,
                _utc_now_iso(),
            ),
        )
        connection.execute(
            """
            UPDATE source_events
            SET mapping_status = ?, canonical_event_id = ?,
                last_observed_at = MAX(last_observed_at, ?)
            WHERE source_id = ? AND source_event_id = ?
            """,
            (status, canonical_event_id, decided, source_id, int(source_event_id)),
        )
        if propagate_verified_mapping and status in {"verified", "mapped"}:
            connection.execute(
                """
                UPDATE odds_snapshots
                SET canonical_event_id = ?
                WHERE source = ? AND source_event_id = ?
                """,
                (canonical_event_id, source_id, int(source_event_id)),
            )

    return {
        "source_id": source_id,
        "source_event_id": int(source_event_id),
        "previous_status": previous_status,
        "new_status": status,
        "canonical_event_id": canonical_event_id,
        "propagated_to_snapshots": bool(
            propagate_verified_mapping and status in {"verified", "mapped"}
        ),
    }


def build_mapping_readiness_report(database: str | Path) -> dict[str, Any]:
    """Return an aggregate-only readiness report suitable for public dashboards."""
    initialize_database(database)
    with connect_database(database) as connection:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        views = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'view'"
            )
        }
        status_rows = connection.execute(
            "SELECT mapping_status, COUNT(*) AS count FROM source_events GROUP BY mapping_status"
        ).fetchall()
        status_counts = {str(row["mapping_status"]): int(row["count"]) for row in status_rows}
        source_event_count = int(
            connection.execute("SELECT COUNT(*) FROM source_events").fetchone()[0]
        )
        schedule_version_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM source_event_schedule_versions"
            ).fetchone()[0]
        )
        current_schedule_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM source_event_schedule_versions WHERE is_current = 1"
            ).fetchone()[0]
        )
        audit_decision_count = int(
            connection.execute("SELECT COUNT(*) FROM source_event_mapping_audit").fetchone()[0]
        )
        multiple_current_groups = int(
            connection.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT source_id, source_event_id
                    FROM source_event_schedule_versions
                    WHERE is_current = 1
                    GROUP BY source_id, source_event_id
                    HAVING COUNT(*) > 1
                )
                """
            ).fetchone()[0]
        )

    verified = status_counts.get("verified", 0) + status_counts.get("mapped", 0)
    verified_pct = round((verified / source_event_count) * 100, 3) if source_event_count else 0.0
    required_tables = {
        "source_event_schedule_versions",
        "source_event_mapping_audit",
    }
    required_views = {
        "current_source_event_schedules",
        "source_event_mapping_status_summary",
    }
    schema_ready = required_tables <= tables and required_views <= views
    return {
        "schemaVersion": "offseason-mapping-database-readiness-report-v1",
        "generatedAt": _utc_now_iso(),
        "formalState": (
            "OFFSEASON_MAPPING_DATABASE_READY"
            if schema_ready and multiple_current_groups == 0
            else "OFFSEASON_MAPPING_DATABASE_INVALID"
        ),
        "database": {
            "schemaReady": schema_ready,
            "requiredTablesPresent": sorted(required_tables & tables),
            "requiredViewsPresent": sorted(required_views & views),
            "sourceEventCount": source_event_count,
            "scheduleVersionCount": schedule_version_count,
            "currentScheduleCount": current_schedule_count,
            "auditDecisionCount": audit_decision_count,
            "multipleCurrentScheduleGroups": multiple_current_groups,
        },
        "mapping": {
            "statusCounts": status_counts,
            "verifiedEventCount": verified,
            "verifiedCoveragePct": verified_pct,
        },
        "readiness": {
            "databaseContractReady": schema_ready,
            "dashboardAggregateReady": schema_ready,
            "productionScheduleImported": False,
            "liveCollectionActive": False,
            "multiObservationHistoryReady": False,
        },
        "quality": {
            "aggregateOnly": True,
            "rawRowsEmitted": 0,
            "rawFilesEmitted": False,
            "networkCallsMade": False,
            "crossRepositoryWrite": False,
        },
    }


def write_mapping_readiness_report(database: str | Path, output: str | Path) -> dict[str, Any]:
    report = build_mapping_readiness_report(database)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
