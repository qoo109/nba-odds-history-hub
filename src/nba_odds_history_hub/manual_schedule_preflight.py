"""Disabled three-stage manual schedule import preflight.

This module validates one repository fixture, builds an aggregate-only preview,
and rehearses a transaction that is always rolled back. It never enables a
production import or reads an external file.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .database import connect_database, initialize_database
from .schedule_output_gate import gate_fixture

READY = "OFFSEASON_PRESEASON_MANUAL_SCHEDULE_IMPORT_PREFLIGHT_AND_ROLLBACK_V1_READY"
INVALID = "OFFSEASON_PRESEASON_MANUAL_SCHEDULE_IMPORT_PREFLIGHT_AND_ROLLBACK_V1_INVALID"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("schemaVersion") != "manual-schedule-import-preflight-v1":
        raise ValueError("unsupported preflight contract")
    if contract.get("state") != "disabled_preapproval":
        raise ValueError("preflight must remain disabled before approval")
    if contract.get("mode") != "synthetic_fixture":
        raise ValueError("preflight must use synthetic_fixture mode")
    if contract.get("ownerApprovalGranted") is not False:
        raise ValueError("owner approval must remain false")
    if contract.get("executionEnabled") is not False:
        raise ValueError("execution must remain disabled")
    if int(contract.get("maximumExecutionCount", -1)) != 0:
        raise ValueError("execution count must remain zero")
    stages = contract.get("stages") or []
    expected = [
        "identity_and_schema_preflight",
        "aggregate_preview",
        "transaction_rollback_and_postcheck",
    ]
    if [row.get("id") for row in stages] != expected:
        raise ValueError("three preflight stages must remain ordered and complete")
    if any(row.get("required") is not True for row in stages):
        raise ValueError("all three preflight stages are required")
    boundary = contract.get("executionBoundary") or {}
    if boundary.get("fixtureOnly") is not True:
        raise ValueError("fixture-only boundary is required")
    forbidden = [
        "externalFileAllowed",
        "productionDatabaseAllowed",
        "productionImportAllowed",
        "networkCallsAllowed",
        "scheduledCollectionAllowed",
        "canonicalEventIdCreationAllowed",
        "crossRepositoryWriteAllowed",
    ]
    if any(boundary.get(key) is not False for key in forbidden):
        raise ValueError("inactive execution boundary changed")


def validate_file_identity(root: Path, contract: dict[str, Any]) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    target = contract["targetFile"]
    relative = Path(str(target["path"]))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("target path must remain repository-relative")
    path = root / relative
    if path.name != target["filename"]:
        raise ValueError("target filename mismatch")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != int(target["bytes"]):
        raise ValueError("target byte count mismatch")
    if digest != target["sha256"]:
        raise ValueError("target sha256 mismatch")
    document = json.loads(payload.decode("utf-8"))
    if not isinstance(document, dict):
        raise ValueError("target must contain one JSON object")
    if document.get("schemaVersion") != target["schemaVersion"]:
        raise ValueError("target schema version mismatch")
    if document.get("seasonId") != target["seasonId"]:
        raise ValueError("target season mismatch")
    if document.get("fixtureMode") is not True:
        raise ValueError("target must remain fixture-only")
    observations = document.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("target observations are required")
    return path, document, {
        "path": relative.as_posix(),
        "filename": path.name,
        "bytes": len(payload),
        "sha256": digest,
        "schemaVersion": document["schemaVersion"],
        "seasonId": document["seasonId"],
    }


def build_aggregate_preview(document: dict[str, Any], teams: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    observation_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    reasons: dict[str, int] = {}
    for index, observation in enumerate(document["observations"], start=1):
        gated = gate_fixture(observation, teams)
        accepted_rows.extend(gated["accepted"])
        for reason, count in gated["excludedReasonCounts"].items():
            reasons[reason] = reasons.get(reason, 0) + int(count)
        observation_rows.append({
            "observation": index,
            "accepted": gated["acceptedCount"],
            "excluded": gated["excludedCount"],
            "excludedReasonCounts": gated["excludedReasonCounts"],
        })
    identities = {
        (row["source_id"], int(row["source_event_id"]))
        for row in accepted_rows
    }
    expected = document.get("expected") or {}
    preview = {
        "observations": len(observation_rows),
        "acceptedRows": len(accepted_rows),
        "excludedRows": sum(row["excluded"] for row in observation_rows),
        "uniqueAcceptedEvents": len(identities),
        "excludedReasonCounts": dict(sorted(reasons.items())),
        "observationSummary": observation_rows,
        "expectedCountsMatch": (
            len(observation_rows) == int(expected.get("observationCount", -1))
            and len(accepted_rows) == int(expected.get("acceptedRows", -1))
            and sum(row["excluded"] for row in observation_rows) == int(expected.get("excludedRows", -1))
            and len(identities) == int(expected.get("sourceEvents", -1))
        ),
        "rowLevelExcludedRecordsEmitted": False,
    }
    return preview, accepted_rows


def _table_count(connection: Any, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def rehearse_rollback(database: Path, accepted_rows: list[dict[str, Any]], as_of: str) -> dict[str, Any]:
    initialize_database(database)
    created_at = f"{as_of}T00:00:00+00:00"
    with connect_database(database) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            INSERT INTO data_sources (
                source_id, display_name, source_class, access_mode, usage_boundary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "fixture_preseason_schedule",
                "Synthetic manual import preflight",
                "synthetic_fixture",
                "fixture_only",
                "Transaction rehearsal only; rollback is mandatory.",
                created_at,
            ),
        )
        version_numbers: dict[tuple[str, int], int] = {}
        for row in accepted_rows:
            source_id = str(row["source_id"])
            event_id = int(row["source_event_id"])
            key = (source_id, event_id)
            connection.execute(
                """
                INSERT INTO source_events (
                    source_id, source_event_id, league, event_type, title,
                    scheduled_tipoff, canonical_event_id, mapping_status,
                    first_observed_at, last_observed_at
                ) VALUES (?, ?, 'NBA', 'game', 'synthetic preflight', ?, NULL,
                          'candidate_unverified', ?, ?)
                ON CONFLICT(source_id, source_event_id) DO UPDATE SET
                    scheduled_tipoff=excluded.scheduled_tipoff,
                    mapping_status='candidate_unverified',
                    last_observed_at=MAX(source_events.last_observed_at, excluded.last_observed_at)
                """,
                (
                    source_id,
                    event_id,
                    row["scheduled_tipoff"],
                    row["observed_at"],
                    row["observed_at"],
                ),
            )
            current_version = version_numbers.get(key, 0)
            if current_version:
                connection.execute(
                    """
                    UPDATE source_event_schedule_versions
                    SET is_current = 0
                    WHERE source_id = ? AND source_event_id = ? AND is_current = 1
                    """,
                    key,
                )
            next_version = current_version + 1
            version_numbers[key] = next_version
            connection.execute(
                """
                INSERT INTO source_event_schedule_versions (
                    source_id, source_event_id, version_number, scheduled_tipoff,
                    home_team_abbr, away_team_abbr, mapping_status, mapping_method,
                    observed_at, source_payload_sha256, is_current, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'candidate_unverified',
                          'exact_date_home_away_candidate', ?, ?, 1, ?)
                """,
                (
                    source_id,
                    event_id,
                    next_version,
                    row["scheduled_tipoff"],
                    row["home_team_abbr"],
                    row["away_team_abbr"],
                    row["observed_at"],
                    row["source_payload_sha256"],
                    created_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO source_event_mapping_audit (
                    source_id, source_event_id, canonical_event_id, previous_status,
                    new_status, mapping_method, reason_code, actor_type, decided_at,
                    source_payload_sha256, note, created_at
                ) VALUES (?, ?, NULL, 'candidate_unverified', 'candidate_unverified',
                          'exact_date_home_away_candidate', 'manual_preflight_preview',
                          'synthetic_preflight', ?, ?, 'rolled back', ?)
                """,
                (
                    source_id,
                    event_id,
                    row["observed_at"],
                    row["source_payload_sha256"],
                    created_at,
                ),
            )
        inside = {
            "dataSources": _table_count(connection, "data_sources"),
            "sourceEvents": _table_count(connection, "source_events"),
            "scheduleVersions": _table_count(connection, "source_event_schedule_versions"),
            "currentSchedules": int(connection.execute(
                "SELECT COUNT(*) FROM source_event_schedule_versions WHERE is_current = 1"
            ).fetchone()[0]),
            "mappingAuditDecisions": _table_count(connection, "source_event_mapping_audit"),
            "canonicalEvents": _table_count(connection, "canonical_events"),
            "rawImports": _table_count(connection, "raw_imports"),
            "oddsSnapshots": _table_count(connection, "odds_snapshots"),
        }
        connection.rollback()
        after = {
            "dataSources": _table_count(connection, "data_sources"),
            "sourceEvents": _table_count(connection, "source_events"),
            "scheduleVersions": _table_count(connection, "source_event_schedule_versions"),
            "currentSchedules": int(connection.execute(
                "SELECT COUNT(*) FROM source_event_schedule_versions WHERE is_current = 1"
            ).fetchone()[0]),
            "mappingAuditDecisions": _table_count(connection, "source_event_mapping_audit"),
            "canonicalEvents": _table_count(connection, "canonical_events"),
            "rawImports": _table_count(connection, "raw_imports"),
            "oddsSnapshots": _table_count(connection, "odds_snapshots"),
        }
    return {
        "transactionStarted": True,
        "rollbackExecuted": True,
        "insideTransaction": inside,
        "afterRollback": after,
        "allPreviewRowsRemoved": all(value == 0 for value in after.values()),
        "productionDatabaseTouched": False,
    }


def run_preflight(root: Path, database: Path) -> dict[str, Any]:
    contract = load_object(root / "config/manual-schedule-import-preflight-v1.json")
    teams = load_object(root / "config/nba-team-registry-v1.json")
    validate_contract(contract)
    _, document, identity = validate_file_identity(root, contract)
    preview, accepted_rows = build_aggregate_preview(document, teams)
    rollback = rehearse_rollback(database, accepted_rows, contract["asOf"])
    expected = document["expected"]
    checks = {
        "contract_disabled": contract["state"] == "disabled_preapproval",
        "owner_approval_false": contract["ownerApprovalGranted"] is False,
        "execution_disabled": contract["executionEnabled"] is False,
        "three_stages_present": len(contract["stages"]) == 3,
        "exact_file_identity": identity["sha256"] == contract["targetFile"]["sha256"],
        "schema_match": identity["schemaVersion"] == contract["targetFile"]["schemaVersion"],
        "season_match": identity["seasonId"] == contract["targetFile"]["seasonId"],
        "aggregate_preview": preview["expectedCountsMatch"],
        "source_event_preview": rollback["insideTransaction"]["sourceEvents"] == expected["sourceEvents"],
        "schedule_version_preview": rollback["insideTransaction"]["scheduleVersions"] == expected["scheduleVersions"],
        "current_schedule_preview": rollback["insideTransaction"]["currentSchedules"] == expected["currentSchedules"],
        "mapping_audit_preview": rollback["insideTransaction"]["mappingAuditDecisions"] == expected["auditDecisions"],
        "no_canonical_ids": rollback["insideTransaction"]["canonicalEvents"] == 0,
        "no_market_rows": rollback["insideTransaction"]["rawImports"] == 0 and rollback["insideTransaction"]["oddsSnapshots"] == 0,
        "rollback_executed": rollback["rollbackExecuted"],
        "post_rollback_zero_rows": rollback["allPreviewRowsRemoved"],
        "production_import_false": contract["executionBoundary"]["productionImportAllowed"] is False,
        "network_false": contract["executionBoundary"]["networkCallsAllowed"] is False,
        "cross_repository_false": contract["executionBoundary"]["crossRepositoryWriteAllowed"] is False,
    }
    failed = sorted(key for key, value in checks.items() if not value)
    return {
        "schemaVersion": "manual-schedule-import-preflight-report-v1",
        "asOf": contract["asOf"],
        "requestId": contract["requestId"],
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "failedChecks": failed,
        "stages": [
            {"stage": 1, "id": "identity_and_schema_preflight", "passed": True, "result": identity},
            {"stage": 2, "id": "aggregate_preview", "passed": preview["expectedCountsMatch"], "result": preview},
            {"stage": 3, "id": "transaction_rollback_and_postcheck", "passed": rollback["allPreviewRowsRemoved"], "result": rollback},
        ],
        "approval": {
            "ownerApprovalGranted": False,
            "executionEnabled": False,
            "executionCount": 0,
            "productionImportExecuted": False,
            "postImportVerificationState": "not_applicable_preapproval",
        },
        "boundary": {
            "fixtureOnly": True,
            "externalFilesRead": False,
            "networkCallsMade": False,
            "productionDatabaseTouched": False,
            "productionScheduleImported": False,
            "scheduledCollection": False,
            "canonicalEventIdsCreated": 0,
            "crossRepositoryWrite": False,
            "rowLevelExcludedRecordsEmitted": False,
        },
    }
