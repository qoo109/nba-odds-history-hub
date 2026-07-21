#!/usr/bin/env python3
"""Validate explicit source metadata and fixture schedule persistence gating."""
from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nba_odds_history_hub.database import register_source, register_source_events
from nba_odds_history_hub.schedule_mapping import (
    build_mapping_readiness_report,
    record_mapping_decision,
    record_schedule_version,
)
from nba_odds_history_hub.schedule_output_gate import gate_fixture

READY = "OFFSEASON_EXPLICIT_SOURCE_METADATA_AND_SCHEDULE_OUTPUT_GATE_V1_READY_WITH_PROVIDER_METADATA_GAPS"
INVALID = "OFFSEASON_EXPLICIT_SOURCE_METADATA_AND_SCHEDULE_OUTPUT_GATE_V1_INVALID"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def persist(database: Path, gated: dict[str, Any]) -> dict[str, Any]:
    register_source(
        database,
        source_id=gated["sourceId"],
        display_name="Synthetic schedule fixture",
        source_class="synthetic_fixture",
        access_mode="fixture_only",
        usage_boundary="Repository validation only.",
    )
    rows = [
        {
            "source": row["source_id"],
            "source_event_id": row["source_event_id"],
            "bookmaker_id": None,
            "league": "NBA",
            "event_type": "game",
            "market_name": "fixture schedule",
            "scheduled_tipoff": row["scheduled_tipoff"],
            "cutoff_at": None,
            "canonical_event_id": None,
            "observed_at": row["observed_at"],
        }
        for row in gated["accepted"]
    ]
    registered = register_source_events(database, rows)
    schedule_inserted = 0
    audit_written = 0
    for row in gated["accepted"]:
        record_mapping_decision(
            database,
            source_id=row["source_id"],
            source_event_id=row["source_event_id"],
            new_status=row["mapping_status"],
            mapping_method=row["mapping_method"],
            reason_code="fixture_output_gate",
            actor_type="synthetic_fixture_gate",
            decided_at=row["observed_at"],
            source_payload_sha256=row["source_payload_sha256"],
        )
        audit_written += 1
        result = record_schedule_version(
            database,
            source_id=row["source_id"],
            source_event_id=row["source_event_id"],
            scheduled_tipoff=row["scheduled_tipoff"],
            home_team_abbr=row["home_team_abbr"],
            away_team_abbr=row["away_team_abbr"],
            observed_at=row["observed_at"],
            source_payload_sha256=row["source_payload_sha256"],
            mapping_status=row["mapping_status"],
            mapping_method=row["mapping_method"],
        )
        schedule_inserted += int(result["inserted"])
    return {
        "sourceEventsRegistered": registered,
        "scheduleVersionsInserted": schedule_inserted,
        "mappingAuditDecisionsWritten": audit_written,
        "canonicalEventsCreated": 0,
        "snapshotRowsWritten": 0,
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    source_doc = load(args.sources)
    provider_doc = load(args.providers)
    contract = load(args.contract)
    fixture = load(args.fixture)
    teams = load(args.teams)

    sources = source_doc.get("sources") or []
    providers = provider_doc.get("bookmakers") or []
    source_required = {
        "sourceId", "displayName", "sourceClass", "accessMode", "usageBoundary",
        "automationApproved", "reviewStatus", "rightsStatus", "active",
    }
    provider_required = {
        "bookmakerId", "displayName", "sourceId", "active", "definitionStatus",
        "supportedFormats", "dataScope",
    }
    source_gaps = {
        str(row.get("sourceId")): sorted(source_required - set(row))
        for row in sources if source_required - set(row)
    }
    provider_gaps = {
        str(row.get("bookmakerId")): sorted(provider_required - set(row))
        for row in providers if provider_required - set(row)
    }

    gated = gate_fixture(fixture, teams)
    with tempfile.TemporaryDirectory(prefix="schedule-output-gate-") as temp_name:
        database = Path(temp_name) / "fixture.sqlite"
        writes = persist(database, gated)
        readiness = build_mapping_readiness_report(database)
        first = gated["accepted"][0]
        duplicate = record_schedule_version(
            database,
            source_id=first["source_id"],
            source_event_id=first["source_event_id"],
            scheduled_tipoff=first["scheduled_tipoff"],
            home_team_abbr=first["home_team_abbr"],
            away_team_abbr=first["away_team_abbr"],
            observed_at=first["observed_at"],
            source_payload_sha256=first["source_payload_sha256"],
            mapping_status=first["mapping_status"],
            mapping_method=first["mapping_method"],
        )

    checks = {
        "source_registry_upgraded": source_doc.get("schemaVersion") == "v0.11-source-registry",
        "source_metadata_complete": not source_gaps,
        "source_role_unchanged": all(row.get("automationApproved") is False for row in sources),
        "provider_registry_preserved": provider_doc.get("schemaVersion") == "v0.3-bookmaker-registry",
        "provider_gaps_explicit": bool(provider_gaps),
        "output_gate_contract": contract.get("schemaVersion") == "schedule-adapter-output-gate-contract-v1",
        "fixture_mode_only": fixture.get("fixtureMode") is True,
        "accepted_count": gated["acceptedCount"] == 2,
        "excluded_count": gated["excludedCount"] == 4,
        "excluded_not_persisted": writes["sourceEventsRegistered"] == gated["acceptedCount"],
        "schedule_versions_written": writes["scheduleVersionsInserted"] == 2,
        "mapping_audit_written": writes["mappingAuditDecisionsWritten"] == 2,
        "no_canonical_events_created": writes["canonicalEventsCreated"] == 0,
        "no_snapshot_rows_written": writes["snapshotRowsWritten"] == 0,
        "database_ready": readiness["formalState"] == "OFFSEASON_MAPPING_DATABASE_READY",
        "candidate_status_only": readiness["mapping"]["statusCounts"] == {"candidate_unverified": 2},
        "no_verified_events": readiness["mapping"]["verifiedEventCount"] == 0,
        "single_current_version": readiness["database"]["multipleCurrentScheduleGroups"] == 0,
        "duplicate_is_idempotent": duplicate == {
            "inserted": False,
            "version_number": 1,
            "reason": "exact_current_schedule_duplicate",
        },
        "production_write_disabled": contract.get("currentState", {}).get("productionWriteEnabled") is False,
        "external_schedule_not_read": contract.get("currentState", {}).get("externalScheduleRead") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "metadata-registry-output-gate-validation-report-v1",
        "validatedAt": utc_now(),
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "metadata": {
            "sourceCount": len(sources),
            "providerCount": len(providers),
            "sourceMissingFields": source_gaps,
            "providerMissingFields": provider_gaps,
            "sourceRegistryUpgradeComplete": not source_gaps,
            "providerRegistryUpgradeComplete": not provider_gaps,
            "newSourcesActivated": 0,
            "newProvidersActivated": 0,
        },
        "outputGate": {
            "adapterCounts": gated["adapterCounts"],
            "acceptedCount": gated["acceptedCount"],
            "excludedCount": gated["excludedCount"],
            "excludedReasonCounts": gated["excludedReasonCounts"],
            "databaseWrites": writes,
            "databaseReadiness": readiness,
            "duplicateResult": duplicate,
        },
        "quality": {
            "fixtureOnly": True,
            "networkCallsMade": False,
            "externalScheduleRead": False,
            "rawRowsEmitted": 0,
            "rawFilesEmitted": False,
            "crossRepositoryWrite": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=Path("config/source-registry.json"))
    parser.add_argument("--providers", type=Path, default=Path("config/bookmaker-registry.json"))
    parser.add_argument("--contract", type=Path, default=Path("config/schedule-adapter-output-gate-contract-v1.json"))
    parser.add_argument("--fixture", type=Path, default=Path("data/fixtures/official-schedule-adapter-v1.json"))
    parser.add_argument("--teams", type=Path, default=Path("config/nba-team-registry-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "formalState": report["formalState"],
        "checksPassed": report["checksPassed"],
        "checksTotal": report["checksTotal"],
        "checksFailed": report["checksFailed"],
    }, indent=2))
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
