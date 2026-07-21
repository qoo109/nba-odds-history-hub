#!/usr/bin/env python3
"""Validate static NBA team, market, and offseason capture reference data."""
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORMAL_STATE = "OFFSEASON_REFERENCE_FOUNDATION_V1_READY"
INVALID_STATE = "OFFSEASON_REFERENCE_FOUNDATION_V1_INVALID"
EXPECTED_TEAMS = {
    "ATL","BOS","BKN","CHA","CHI","CLE","DAL","DEN","DET","GSW",
    "HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK",
    "OKC","ORL","PHI","PHX","POR","SAC","SAS","TOR","UTA","WAS",
}
EXPECTED_DIVISIONS = {
    "Atlantic": "East",
    "Central": "East",
    "Southeast": "East",
    "Northwest": "West",
    "Pacific": "West",
    "Southwest": "West",
}
REQUIRED_MARKETS = {
    "game_moneyline_full_game",
    "game_spread_full_game",
    "game_total_full_game",
    "futures_championship",
    "futures_award",
    "futures_season_win_total",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def validate(teams_doc: dict[str, Any], markets_doc: dict[str, Any], readiness_doc: dict[str, Any]) -> dict[str, Any]:
    teams = teams_doc.get("teams") or []
    markets = markets_doc.get("markets") or []
    labels = readiness_doc.get("snapshotLabels") or []
    cadence = readiness_doc.get("dormantCadenceTemplates") or []
    safety = readiness_doc.get("safetyBoundary") or {}
    event_identity = readiness_doc.get("eventIdentityContract") or {}

    abbreviations = [team.get("canonicalAbbr") for team in teams]
    full_names = [team.get("fullName") for team in teams]
    source_aliases = [alias for team in teams for alias in (team.get("sourceAliases") or [])]
    divisions = Counter(team.get("division") for team in teams)
    conferences = Counter(team.get("conference") for team in teams)
    market_classes = [market.get("marketClass") for market in markets]
    label_by_name = {item.get("label"): item for item in labels}

    checks: dict[str, bool] = {
        "team_schema": teams_doc.get("schemaVersion") == "nba-team-registry-v1",
        "team_count": teams_doc.get("teamCount") == 30 and len(teams) == 30,
        "team_set": set(abbreviations) == EXPECTED_TEAMS,
        "unique_team_abbreviations": len(abbreviations) == len(set(abbreviations)),
        "unique_team_names": len(full_names) == len(set(full_names)),
        "all_teams_active": all(team.get("active") is True for team in teams),
        "conference_balance": conferences == Counter({"East": 15, "West": 15}),
        "division_balance": all(divisions[name] == 5 for name in EXPECTED_DIVISIONS),
        "division_conference_consistency": all(
            team.get("conference") == EXPECTED_DIVISIONS.get(team.get("division"))
            for team in teams
        ),
        "source_aliases_present": all(team.get("sourceAliases") for team in teams),
        "unique_source_aliases": len(source_aliases) == len(set(source_aliases)),
        "no_automatic_fuzzy_team_matching": (
            teams_doc.get("identityPolicy", {}).get("automaticFuzzyMatchingAllowed") is False
        ),
        "historical_alias_requires_season": (
            teams_doc.get("identityPolicy", {}).get("historicalRelocationAliasRequiresSeasonValidation") is True
        ),
        "market_schema": markets_doc.get("schemaVersion") == "nba-market-taxonomy-v1",
        "unique_market_classes": len(market_classes) == len(set(market_classes)),
        "required_market_classes": REQUIRED_MARKETS.issubset(set(market_classes)),
        "game_markets_require_canonical_event": all(
            event.get("canonicalEventRequired") is True
            for event in markets_doc.get("eventTypes") or []
            if event.get("eventType") == "game"
        ),
        "unknown_market_quarantined": (
            markets_doc.get("normalizationPolicy", {}).get("unknownMarketBehavior") == "quarantine_unclassified"
        ),
        "no_semantic_guessing": (
            markets_doc.get("normalizationPolicy", {}).get("automaticSemanticGuessingAllowed") is False
        ),
        "no_opening_closing_inference": (
            markets_doc.get("normalizationPolicy", {}).get("openingClosingInferenceAllowed") is False
        ),
        "single_observation_not_movement_ready": (
            markets_doc.get("researchBoundary", {}).get("singleObservationMovementReady") is False
        ),
        "readiness_schema": readiness_doc.get("schemaVersion") == "offseason-capture-readiness-v1",
        "offseason_sleep": readiness_doc.get("currentMode") == "offseason_sleep",
        "live_capture_inactive": readiness_doc.get("liveCaptureActive") is False,
        "scheduled_capture_inactive": readiness_doc.get("scheduledCaptureActive") is False,
        "manual_capture_not_approved": readiness_doc.get("manualCaptureRequestApproved") is False,
        "cadence_templates_all_dormant": bool(cadence) and all(item.get("active") is False for item in cadence),
        "opening_candidate_not_automatic": (
            label_by_name.get("opening_candidate", {}).get("automaticAssignmentAllowed") is False
        ),
        "closing_candidate_not_automatic": (
            label_by_name.get("closing_candidate", {}).get("automaticAssignmentAllowed") is False
        ),
        "exact_event_identity": (
            event_identity.get("exactCandidateKey") == ["scheduled_game_date", "home_team_abbr", "away_team_abbr"]
            and event_identity.get("fuzzyMatchingAllowed") is False
            and event_identity.get("scoreUsedForIdentityRepair") is False
            and event_identity.get("manyToManyMappingAllowed") is False
        ),
        "canonical_event_not_invented": event_identity.get("inventedCanonicalEventIdAllowed") is False,
        "changes_only_retention": (
            readiness_doc.get("retentionPolicy", {}).get("changedPriceOrLineRetention") is True
            and readiness_doc.get("retentionPolicy", {}).get("exactDuplicateRetention") is False
            and readiness_doc.get("retentionPolicy", {}).get("missingRowsTreatedAsUnchanged") is False
        ),
        "restricted_access_disabled": all(value is False for value in safety.values()),
        "reference_ready_live_not_ready": (
            readiness_doc.get("readiness", {}).get("referenceDataReady") is True
            and readiness_doc.get("readiness", {}).get("liveCaptureReady") is False
            and readiness_doc.get("readiness", {}).get("historicalMovementReady") is False
            and readiness_doc.get("readiness", {}).get("openingClosingReady") is False
            and readiness_doc.get("readiness", {}).get("pointInTimeJoinReady") is False
        ),
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "offseason-reference-foundation-validation-report-v1",
        "validatedAt": utc_now(),
        "formalState": FORMAL_STATE if not failed else INVALID_STATE,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "summary": {
            "teamCount": len(teams),
            "eastTeams": conferences.get("East", 0),
            "westTeams": conferences.get("West", 0),
            "divisionCount": len(divisions),
            "marketClassCount": len(markets),
            "cadenceTemplateCount": len(cadence),
            "activeCadenceTemplates": sum(item.get("active") is True for item in cadence),
        },
        "quality": {
            "networkCallsMade": False,
            "liveOddsCaptured": False,
            "sourcePayloadsRead": False,
            "rawRowsEmitted": 0,
            "rawFilesEmitted": False,
            "nbaValueLabModified": False,
            "formalStake": 0,
        },
    }


def self_test(teams_doc: dict[str, Any], markets_doc: dict[str, Any], readiness_doc: dict[str, Any]) -> None:
    report = validate(teams_doc, markets_doc, readiness_doc)
    assert report["formalState"] == FORMAL_STATE, report

    changed = copy.deepcopy(teams_doc)
    changed["teams"][0]["canonicalAbbr"] = "BOS"
    report = validate(changed, markets_doc, readiness_doc)
    assert report["formalState"] == INVALID_STATE
    assert "unique_team_abbreviations" in report["failedChecks"]

    changed = copy.deepcopy(markets_doc)
    changed["normalizationPolicy"]["openingClosingInferenceAllowed"] = True
    report = validate(teams_doc, changed, readiness_doc)
    assert report["formalState"] == INVALID_STATE
    assert "no_opening_closing_inference" in report["failedChecks"]

    changed = copy.deepcopy(readiness_doc)
    changed["dormantCadenceTemplates"][0]["active"] = True
    report = validate(teams_doc, markets_doc, changed)
    assert report["formalState"] == INVALID_STATE
    assert "cadence_templates_all_dormant" in report["failedChecks"]

    changed = copy.deepcopy(readiness_doc)
    changed["safetyBoundary"]["cookieOrSessionAllowed"] = True
    report = validate(teams_doc, markets_doc, changed)
    assert report["formalState"] == INVALID_STATE
    assert "restricted_access_disabled" in report["failedChecks"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--teams", type=Path, default=Path("config/nba-team-registry-v1.json"))
    parser.add_argument("--markets", type=Path, default=Path("config/market-taxonomy-v1.json"))
    parser.add_argument("--readiness", type=Path, default=Path("config/offseason-capture-readiness-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    teams_doc = load(args.teams)
    markets_doc = load(args.markets)
    readiness_doc = load(args.readiness)
    if args.self_test:
        self_test(teams_doc, markets_doc, readiness_doc)
    report = validate(teams_doc, markets_doc, readiness_doc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "formalState": report["formalState"],
        "checksPassed": report["checksPassed"],
        "checksTotal": report["checksTotal"],
        "checksFailed": report["checksFailed"],
    }, indent=2))
    return 0 if report["formalState"] == FORMAL_STATE else 1


if __name__ == "__main__":
    raise SystemExit(main())
