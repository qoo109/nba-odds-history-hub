#!/usr/bin/env python3
"""Build a privacy-safe aggregate metadata/readiness export from repository fixtures only."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from nba_odds_history_hub.schedule_output_gate import gate_fixture

READY = "OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY"
INVALID = "OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_INVALID"

SOURCE_REQUIRED = {
    "sourceId", "displayName", "sourceClass", "accessMode", "usageBoundary",
    "automationApproved", "reviewStatus", "rightsStatus", "active",
}
PROVIDER_REQUIRED = {
    "providerId", "bookmakerId", "displayName", "sourceId", "active",
    "definitionStatus", "supportedFormats", "dataScope", "automationApproved", "note",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def count_values(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts = Counter(str(row.get(field)) for row in rows)
    return dict(sorted(counts.items()))


def count_list_values(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for value in row.get(field) or []:
            counts[str(value)] += 1
    return dict(sorted(counts.items()))


def missing_fields(rows: list[dict[str, Any]], required: set[str], identity_field: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row in rows:
        missing = sorted(required - set(row))
        if missing:
            result[str(row.get(identity_field, "<missing>"))] = missing
    return result


def build_export(
    teams_doc: dict[str, Any],
    markets_doc: dict[str, Any],
    sources_doc: dict[str, Any],
    providers_doc: dict[str, Any],
    capture_doc: dict[str, Any],
    request_doc: dict[str, Any],
    fixture_doc: dict[str, Any],
    *,
    as_of: str,
) -> dict[str, Any]:
    teams = teams_doc.get("teams") or []
    markets = markets_doc.get("markets") or []
    sources = sources_doc.get("sources") or []
    providers = providers_doc.get("bookmakers") or []
    source_gaps = missing_fields(sources, SOURCE_REQUIRED, "sourceId")
    provider_gaps = missing_fields(providers, PROVIDER_REQUIRED, "providerId")
    source_ids = {str(row.get("sourceId")) for row in sources}
    gated = gate_fixture(fixture_doc, teams_doc)
    safety = capture_doc.get("safetyBoundary") or {}
    readiness = capture_doc.get("readiness") or {}
    cadence = capture_doc.get("dormantCadenceTemplates") or []

    checks = {
        "team_registry_schema": teams_doc.get("schemaVersion") == "nba-team-registry-v1",
        "team_count": len(teams) == teams_doc.get("teamCount") == 30,
        "market_taxonomy_schema": markets_doc.get("schemaVersion") == "nba-market-taxonomy-v1",
        "market_classes_present": len(markets) == 11,
        "source_registry_schema": sources_doc.get("schemaVersion") == "v0.11-source-registry",
        "source_metadata_complete": not source_gaps,
        "source_ids_unique": len(source_ids) == len(sources),
        "source_automation_disabled": all(row.get("automationApproved") is False for row in sources),
        "provider_registry_schema": providers_doc.get("schemaVersion") == "v0.12-provider-registry",
        "provider_metadata_complete": not provider_gaps,
        "provider_ids_unique": len({str(row.get("providerId")) for row in providers}) == len(providers),
        "provider_sources_exist": all(str(row.get("sourceId")) in source_ids for row in providers),
        "provider_automation_disabled": all(row.get("automationApproved") is False for row in providers),
        "capture_mode_sleeping": capture_doc.get("currentMode") == "offseason_sleep",
        "live_capture_disabled": capture_doc.get("liveCaptureActive") is False,
        "scheduled_capture_disabled": capture_doc.get("scheduledCaptureActive") is False,
        "cadence_templates_dormant": all(row.get("active") is False for row in cadence),
        "phase2_not_approved": request_doc.get("approval_granted") is False,
        "phase2_execution_disabled": request_doc.get("execution_enabled") is False,
        "phase2_execution_count_zero": request_doc.get("execution_count") == 0,
        "fixture_mode_only": fixture_doc.get("fixtureMode") is True,
        "fixture_gate_counts": gated.get("adapterCounts") == {
            "candidate_unverified": 2,
            "quarantined": 2,
            "rejected": 2,
        },
        "fixture_canonical_ids_not_created": gated.get("canonicalEventIdsCreated") == 0,
        "restricted_access_disabled": all(value is False for value in safety.values()),
        "research_gates_closed": (
            readiness.get("liveCaptureReady") is False
            and readiness.get("historicalMovementReady") is False
            and readiness.get("openingClosingReady") is False
            and readiness.get("pointInTimeJoinReady") is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)

    conferences = Counter(str(row.get("conference")) for row in teams)
    divisions = Counter(str(row.get("division")) for row in teams)
    event_types = Counter(str(row.get("eventType")) for row in markets)

    return {
        "schemaVersion": "offseason-aggregate-metadata-readiness-v1",
        "asOf": as_of,
        "fixtureMode": True,
        "currentMode": capture_doc.get("currentMode"),
        "formalState": READY if not failed else INVALID,
        "validation": {
            "checksPassed": len(checks) - len(failed),
            "checksTotal": len(checks),
            "checksFailed": len(failed),
            "failedChecks": failed,
        },
        "summary": {
            "teams": len(teams),
            "marketClasses": len(markets),
            "sources": len(sources),
            "providers": len(providers),
            "metadataMissingFields": sum(len(value) for value in source_gaps.values())
            + sum(len(value) for value in provider_gaps.values()),
            "automationApprovals": sum(row.get("automationApproved") is True for row in sources)
            + sum(row.get("automationApproved") is True for row in providers),
            "activeCadenceTemplates": sum(row.get("active") is True for row in cadence),
            "fixtureScheduleGames": len(fixture_doc.get("games") or []),
        },
        "teamRegistry": {
            "count": len(teams),
            "conferenceCounts": dict(sorted(conferences.items())),
            "divisionCounts": dict(sorted(divisions.items())),
            "automaticFuzzyMatchingAllowed": teams_doc.get("identityPolicy", {}).get("automaticFuzzyMatchingAllowed"),
        },
        "marketTaxonomy": {
            "classCount": len(markets),
            "eventTypeCounts": dict(sorted(event_types.items())),
            "movementEligibleCount": sum(row.get("movementEligible") is True for row in markets),
            "pointInTimeEligibleCount": sum(row.get("pointInTimeEligible") is True for row in markets),
            "openingClosingInferenceAllowed": markets_doc.get("normalizationPolicy", {}).get("openingClosingInferenceAllowed"),
        },
        "sourceMetadata": {
            "schemaVersion": sources_doc.get("schemaVersion"),
            "count": len(sources),
            "activeCount": sum(row.get("active") is True for row in sources),
            "automationApprovedCount": sum(row.get("automationApproved") is True for row in sources),
            "reviewStatusCounts": count_values(sources, "reviewStatus"),
            "rightsStatusCounts": count_values(sources, "rightsStatus"),
            "missingRequiredFieldCount": sum(len(value) for value in source_gaps.values()),
        },
        "providerMetadata": {
            "schemaVersion": providers_doc.get("schemaVersion"),
            "count": len(providers),
            "activeCount": sum(row.get("active") is True for row in providers),
            "automationApprovedCount": sum(row.get("automationApproved") is True for row in providers),
            "definitionStatusCounts": count_values(providers, "definitionStatus"),
            "supportedFormatCounts": count_list_values(providers, "supportedFormats"),
            "dataScopeCounts": count_list_values(providers, "dataScope"),
            "missingRequiredFieldCount": sum(len(value) for value in provider_gaps.values()),
        },
        "scheduleFixture": {
            "gameCount": len(fixture_doc.get("games") or []),
            "acceptedCount": gated.get("acceptedCount"),
            "excludedCount": gated.get("excludedCount"),
            "statusCounts": gated.get("adapterCounts"),
            "excludedReasonCounts": gated.get("excludedReasonCounts"),
            "canonicalEventIdsCreated": gated.get("canonicalEventIdsCreated"),
            "rowLevelRecordsIncluded": False,
        },
        "collectionState": {
            "liveCaptureActive": capture_doc.get("liveCaptureActive"),
            "scheduledCaptureActive": capture_doc.get("scheduledCaptureActive"),
            "phase2ApprovalGranted": request_doc.get("approval_granted"),
            "phase2ExecutionEnabled": request_doc.get("execution_enabled"),
            "phase2ExecutionCount": request_doc.get("execution_count"),
            "phase2MaximumExecutionCount": request_doc.get("maximum_execution_count"),
            "productionScheduleImported": False,
            "externalScheduleRead": False,
        },
        "researchReadiness": {
            "referenceDataReady": readiness.get("referenceDataReady"),
            "liveCaptureReady": readiness.get("liveCaptureReady"),
            "historicalMovementReady": readiness.get("historicalMovementReady"),
            "openingClosingReady": readiness.get("openingClosingReady"),
            "pointInTimeJoinReady": readiness.get("pointInTimeJoinReady"),
        },
        "privacyBoundary": {
            "aggregateOnly": True,
            "rowLevelRecordsIncluded": False,
            "sourceUrlsIncluded": False,
            "sourceNamesIncluded": False,
            "providerNamesIncluded": False,
            "credentialsIncluded": False,
            "cookiesOrSessionsIncluded": False,
            "authorizationHeadersIncluded": False,
            "networkCallsMade": False,
            "externalFilesRead": False,
            "rawRowsEmitted": 0,
            "crossRepositoryWrite": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--teams", type=Path, default=Path("config/nba-team-registry-v1.json"))
    parser.add_argument("--markets", type=Path, default=Path("config/market-taxonomy-v1.json"))
    parser.add_argument("--sources", type=Path, default=Path("config/source-registry.json"))
    parser.add_argument("--providers", type=Path, default=Path("config/bookmaker-registry.json"))
    parser.add_argument("--capture", type=Path, default=Path("config/offseason-capture-readiness-v1.json"))
    parser.add_argument("--request", type=Path, default=Path("data/phase2-odds-capture-request-v1.json"))
    parser.add_argument("--fixture", type=Path, default=Path("data/fixtures/official-schedule-adapter-v1.json"))
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = build_export(
        load(args.teams),
        load(args.markets),
        load(args.sources),
        load(args.providers),
        load(args.capture),
        load(args.request),
        load(args.fixture),
        as_of=args.as_of,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "formalState": report["formalState"],
        "checksPassed": report["validation"]["checksPassed"],
        "checksTotal": report["validation"]["checksTotal"],
        "checksFailed": report["validation"]["checksFailed"],
    }, indent=2))
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
