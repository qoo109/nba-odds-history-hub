"""Repository-only preseason schedule dry-run orchestration."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .database import register_source, register_source_events
from .mapping import build_mapping_readiness_report, record_mapping_decision, record_schedule_version
from .schedule_output_gate import gate_fixture

READY = "OFFSEASON_PRESEASON_ACTIVATION_GATE_AND_DRY_RUN_FIXTURES_V1_READY"
INVALID = "OFFSEASON_PRESEASON_ACTIVATION_GATE_AND_DRY_RUN_FIXTURES_V1_INVALID"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def validate_configuration(readiness: dict[str, Any], season: dict[str, Any]) -> None:
    if readiness.get("schemaVersion") != "preseason-readiness-v1":
        raise ValueError("unsupported preseason readiness schema")
    if readiness.get("currentState") != "offseason_sleep" or readiness.get("mode") != "synthetic_fixture":
        raise ValueError("dry run must start from offseason_sleep in synthetic_fixture mode")
    if any(readiness.get(key) is not False for key in ("externalRead", "productionImport", "scheduledRun")):
        raise ValueError("inactive boundary must remain false")
    if season.get("schemaVersion") != "season-configuration-v1":
        raise ValueError("unsupported season configuration schema")
    if season.get("scheduleInputMode") != "synthetic_fixture":
        raise ValueError("only synthetic_fixture input is allowed")
    if season.get("mappingPolicy") != "candidate_unverified_only":
        raise ValueError("dry run mapping policy must remain candidate-only")
    if season.get("canonicalEventIdCreationAllowed") is not False:
        raise ValueError("canonical event ID creation must remain disabled")
    if any(season.get(key) is not False for key in ("externalScheduleRead", "productionScheduleImported", "scheduledCollection")):
        raise ValueError("season configuration crossed the inactive boundary")


def _source_rows(gated: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source": row["source_id"],
            "source_event_id": row["source_event_id"],
            "bookmaker_id": None,
            "league": "NBA",
            "event_type": "game",
            "market_name": "synthetic preseason schedule",
            "scheduled_tipoff": row["scheduled_tipoff"],
            "cutoff_at": None,
            "canonical_event_id": None,
            "observed_at": row["observed_at"],
        }
        for row in gated["accepted"]
    ]


def run_dry_run(root: Path, database: Path) -> dict[str, Any]:
    readiness_config = load_json(root / "config/preseason-readiness-v1.json")
    season_config = load_json(root / "config/season-configuration-v1.json")
    fixture = load_json(root / "data/fixtures/preseason-dry-run-v1.json")
    teams = load_json(root / "config/nba-team-registry-v1.json")
    validate_configuration(readiness_config, season_config)

    observations = fixture.get("observations") or []
    if len(observations) != int(season_config["expectedObservationCount"]):
        raise ValueError("unexpected observation count")

    states = ["offseason_sleep", "preseason_dry_run_config_valid"]
    observation_reports: list[dict[str, Any]] = []
    accepted_total = excluded_total = inserted_versions = 0
    canonical_created = 0
    previous_identity: dict[tuple[str, int], tuple[str, str, str]] = {}
    schedule_identity_changes = payload_only_revisions = 0
    last_accepted: list[dict[str, Any]] = []

    for index, observation in enumerate(observations, start=1):
        gated = gate_fixture(observation, teams)
        register_source(
            database,
            source_id=gated["sourceId"],
            display_name="Synthetic preseason fixture",
            source_class="synthetic_fixture",
            access_mode="fixture_only",
            usage_boundary="Repository dry-run tests only.",
        )
        register_source_events(database, _source_rows(gated))
        writes = []
        for row in gated["accepted"]:
            key = (row["source_id"], int(row["source_event_id"]))
            identity = (row["scheduled_tipoff"], row["home_team_abbr"], row["away_team_abbr"])
            if key in previous_identity:
                if previous_identity[key] == identity:
                    payload_only_revisions += 1
                else:
                    schedule_identity_changes += 1
            previous_identity[key] = identity
            record_mapping_decision(
                database,
                source_id=row["source_id"],
                source_event_id=row["source_event_id"],
                new_status=row["mapping_status"],
                mapping_method=row["mapping_method"],
                reason_code="preseason_fixture_gate",
                actor_type="synthetic_dry_run",
                decided_at=row["observed_at"],
                source_payload_sha256=row["source_payload_sha256"],
            )
            write = record_schedule_version(database, **row)
            writes.append(write)
            inserted_versions += int(write["inserted"])
        accepted_total += gated["acceptedCount"]
        excluded_total += gated["excludedCount"]
        canonical_created += gated["canonicalEventIdsCreated"]
        observation_reports.append({
            "observation": index,
            "accepted": gated["acceptedCount"],
            "excluded": gated["excludedCount"],
            "excludedReasonCounts": gated["excludedReasonCounts"],
            "versionsInserted": sum(int(item["inserted"]) for item in writes),
        })
        states.append("preseason_dry_run_partial" if index < len(observations) else "preseason_dry_run_ready_awaiting_owner_approval")
        last_accepted = gated["accepted"]

    replay_results = [record_schedule_version(database, **row) for row in last_accepted]
    idempotent_replays = sum(not item["inserted"] for item in replay_results)
    mapping = build_mapping_readiness_report(database)
    expected = fixture["expected"]
    checks = {
        "configuration": True,
        "observation_count": len(observations) == expected["observationCount"],
        "accepted_rows": accepted_total == expected["acceptedRows"],
        "excluded_rows": excluded_total == expected["excludedRows"],
        "source_events": mapping["database"]["sourceEventCount"] == expected["sourceEvents"],
        "schedule_versions": mapping["database"]["scheduleVersionCount"] == expected["scheduleVersions"],
        "current_schedules": mapping["database"]["currentScheduleCount"] == expected["currentSchedules"],
        "audit_decisions": mapping["database"]["auditDecisionCount"] == expected["auditDecisions"],
        "single_current_version": mapping["database"]["multipleCurrentScheduleGroups"] == 0,
        "candidate_only": mapping["mapping"]["statusCounts"] == {"candidate_unverified": expected["sourceEvents"]},
        "canonical_ids_not_created": canonical_created == 0 and mapping["mapping"]["verifiedEventCount"] == 0,
        "idempotent_replay": idempotent_replays == len(last_accepted),
        "schedule_revision": schedule_identity_changes == 1,
        "state_transition": states[-1] == expected["finalState"],
        "inactive_boundary": not readiness_config["externalRead"] and not readiness_config["productionImport"] and not readiness_config["scheduledRun"],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "preseason-activation-dry-run-report-v1",
        "asOf": readiness_config["asOf"],
        "seasonId": season_config["seasonId"],
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "failedChecks": failed,
        "stateTransitions": states,
        "observations": observation_reports,
        "totals": {
            "acceptedRows": accepted_total,
            "excludedRows": excluded_total,
            "scheduleVersionsInserted": inserted_versions,
            "scheduleIdentityChanges": schedule_identity_changes,
            "payloadOnlyRevisions": payload_only_revisions,
            "idempotentReplayRows": idempotent_replays,
        },
        "database": mapping["database"],
        "mapping": mapping["mapping"],
        "boundary": {
            "fixtureOnly": True,
            "externalRead": False,
            "productionImport": False,
            "scheduledCollection": False,
            "crossRepositoryWrite": False,
            "rowLevelRecordsEmitted": False,
        },
    }
