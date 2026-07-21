#!/usr/bin/env python3
"""Validate role-limited metadata and the fixture-only schedule adapter."""
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nba_odds_history_hub.schedule_adapter import adapt_fixture

READY = "OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS"
INVALID = "OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_INVALID"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate(
    metadata_contract: dict[str, Any],
    adapter_contract: dict[str, Any],
    sources_doc: dict[str, Any],
    providers_doc: dict[str, Any],
    teams_doc: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    sources = sources_doc.get("sources") or []
    providers = providers_doc.get("bookmakers") or []
    source_ids = [str(row.get("sourceId")) for row in sources]
    provider_ids = [str(row.get("bookmakerId")) for row in providers]
    source_required = set(metadata_contract.get("sourceRequiredFields") or [])
    provider_required = set(metadata_contract.get("providerRequiredFields") or [])

    source_missing: dict[str, list[str]] = {}
    for row in sources:
        missing = sorted(field for field in source_required if field not in row)
        if missing:
            source_missing[str(row.get("sourceId"))] = missing
    provider_missing: dict[str, list[str]] = {}
    for row in providers:
        present = set(row)
        if "providerId" in provider_required and "bookmakerId" in row:
            present.add("providerId")
        missing = sorted(field for field in provider_required if field not in present)
        if missing:
            provider_missing[str(row.get("bookmakerId"))] = missing

    adapted = adapt_fixture(fixture, teams_doc)
    expected = {str(game.get("caseId")): str(game.get("expectedStatus")) for game in fixture.get("games") or []}
    actual = {str(row.get("caseId")): str(row.get("status")) for row in adapted["results"]}
    adapter_identity = adapter_contract.get("identityPolicy") or {}
    adapter_output = adapter_contract.get("outputPolicy") or {}
    source_schema = sources_doc.get("schemaVersion")
    source_metadata_state_valid = (
        (source_schema == "v0.3-source-registry" and bool(source_missing))
        or (source_schema == "v0.11-source-registry" and not source_missing)
    )

    checks = {
        "metadata_contract_schema": metadata_contract.get("schemaVersion") == "source-provider-metadata-contract-v1",
        "adapter_contract_schema": adapter_contract.get("schemaVersion") == "official-schedule-adapter-contract-v1",
        "source_registry_schema": source_schema in {"v0.3-source-registry", "v0.11-source-registry"},
        "provider_registry_schema": providers_doc.get("schemaVersion") == "v0.3-bookmaker-registry",
        "source_ids_unique": len(source_ids) == len(set(source_ids)),
        "provider_ids_unique": len(provider_ids) == len(set(provider_ids)),
        "provider_sources_exist": all(str(row.get("sourceId")) in set(source_ids) for row in providers),
        "source_boundaries_present": all(str(row.get("usageBoundary", "")).strip() for row in sources),
        "manual_sources_not_automated": all(row.get("automationApproved") is False for row in sources),
        "provider_notes_present": all(str(row.get("note", "")).strip() for row in providers),
        "legacy_source_gaps_explicit": source_metadata_state_valid,
        "legacy_provider_gaps_explicit": bool(provider_missing),
        "team_registry_ready": teams_doc.get("schemaVersion") == "nba-team-registry-v1" and teams_doc.get("teamCount") == 30,
        "fixture_mode_only": fixture.get("fixtureMode") is True,
        "fixture_outcomes_match": actual == expected,
        "fixture_counts": adapted["counts"] == {"candidate_unverified": 2, "quarantined": 2, "rejected": 2},
        "canonical_ids_not_created": adapter_identity.get("canonicalEventIdCreatedAutomatically") is False,
        "no_fuzzy_matching": adapter_identity.get("fuzzyMatchingAllowed") is False,
        "no_score_repair": adapter_identity.get("scoreAssistedRepairAllowed") is False,
        "no_many_to_many": adapter_identity.get("manyToManyMappingAllowed") is False,
        "database_write_disabled": adapter_output.get("databaseWriteEnabled") is False,
        "cross_repository_write_disabled": adapter_output.get("crossRepositoryWriteEnabled") is False,
        "production_schedule_not_imported": adapter_contract.get("currentState", {}).get("productionScheduleImported") is False,
        "collection_inactive": adapter_contract.get("currentState", {}).get("collectionActive") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "source-provider-schedule-adapter-validation-report-v1",
        "validatedAt": now_utc(),
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "metadataQa": {
            "sourceCount": len(sources),
            "providerCount": len(providers),
            "sourceIds": sorted(source_ids),
            "providerIds": sorted(provider_ids),
            "sourceMissingExplicitFields": source_missing,
            "providerMissingExplicitFields": provider_missing,
            "legacyMetadataUpgradeRequired": bool(source_missing or provider_missing),
            "newSourcesActivated": 0,
            "newProvidersActivated": 0,
        },
        "scheduleAdapter": {
            "fixtureGames": len(fixture.get("games") or []),
            "statusCounts": adapted["counts"],
            "allExpectedOutcomesMatched": actual == expected,
            "canonicalEventIdsCreated": 0,
            "databaseRowsWritten": 0,
        },
        "mappingStatusExport": {
            "schemaVersion": "aggregate-mapping-status-export-v1",
            "fixtureMode": True,
            "statusCounts": adapted["counts"],
            "rowLevelRecordsIncluded": False,
        },
        "quality": {
            "aggregateOnly": True,
            "networkCallsMade": False,
            "externalScheduleRead": False,
            "rawScheduleRowsEmitted": 0,
            "rawScheduleFilesEmitted": False,
            "databaseWrite": False,
            "crossRepositoryWrite": False,
        },
    }


def self_test(args: argparse.Namespace) -> None:
    docs = [load(path) for path in (args.metadata_contract, args.adapter_contract, args.sources, args.providers, args.teams, args.fixture)]
    report = validate(*docs)
    assert report["formalState"] == READY, report

    changed = copy.deepcopy(docs[2])
    changed["sources"][0]["automationApproved"] = True
    assert validate(docs[0], docs[1], changed, docs[3], docs[4], docs[5])["formalState"] == INVALID

    changed = copy.deepcopy(docs[1])
    changed["identityPolicy"]["fuzzyMatchingAllowed"] = True
    assert validate(docs[0], changed, docs[2], docs[3], docs[4], docs[5])["formalState"] == INVALID

    changed = copy.deepcopy(docs[5])
    changed["games"][0]["expectedStatus"] = "verified"
    assert validate(docs[0], docs[1], docs[2], docs[3], docs[4], changed)["formalState"] == INVALID


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-contract", type=Path, default=Path("config/source-provider-metadata-contract-v1.json"))
    parser.add_argument("--adapter-contract", type=Path, default=Path("config/official-schedule-adapter-contract-v1.json"))
    parser.add_argument("--sources", type=Path, default=Path("config/source-registry.json"))
    parser.add_argument("--providers", type=Path, default=Path("config/bookmaker-registry.json"))
    parser.add_argument("--teams", type=Path, default=Path("config/nba-team-registry-v1.json"))
    parser.add_argument("--fixture", type=Path, default=Path("data/fixtures/official-schedule-adapter-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(args)
    docs = [load(path) for path in (args.metadata_contract, args.adapter_contract, args.sources, args.providers, args.teams, args.fixture)]
    report = validate(*docs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
