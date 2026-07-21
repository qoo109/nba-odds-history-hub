#!/usr/bin/env python3
"""Validate the static schedule-import contract and synthetic mapping fixtures."""
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

READY = "OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY"
INVALID = "OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_INVALID"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def timezone_aware(value: Any) -> bool:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def alias_maps(teams_doc: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    current: dict[str, str] = {}
    historical: dict[str, str] = {}
    for team in teams_doc.get("teams") or []:
        canonical = str(team.get("canonicalAbbr"))
        for alias in team.get("sourceAliases") or []:
            current[str(alias).lower()] = canonical
        for alias in team.get("historicalAliases") or []:
            historical[str(alias).lower()] = canonical
    return current, historical


def classify(case: dict[str, Any], current: dict[str, str], historical: dict[str, str]) -> str:
    home_raw = str(case.get("homeTeamAlias", "")).lower()
    away_raw = str(case.get("awayTeamAlias", "")).lower()
    home = current.get(home_raw)
    away = current.get(away_raw)

    if home_raw in historical or away_raw in historical:
        return "quarantined"
    if home is None or away is None:
        return "quarantined"
    if home == away:
        return "rejected"
    if case.get("canonicalEventId") and case.get("mappingMethod") == "synthetic_fixture_only":
        return "verified"
    return "candidate_unverified"


def validate(contract: dict[str, Any], teams_doc: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    current, historical = alias_maps(teams_doc)
    cases = fixture.get("cases") or []
    source_event_ids = [case.get("sourceEventId") for case in cases]
    required_fields = set(contract.get("requiredSourceFields") or [])
    allowed_statuses = set(contract.get("mappingStatuses") or [])
    allowed_methods = set(contract.get("mappingMethods") or [])
    identity = contract.get("identityPolicy") or {}
    time_policy = contract.get("timePolicy") or {}
    quality_gates = contract.get("qualityGates") or {}

    case_results: list[dict[str, Any]] = []
    for case in cases:
        missing = sorted(field for field in required_fields if case.get(field) in (None, ""))
        actual = classify(case, current, historical)
        case_results.append({
            "caseId": case.get("caseId"),
            "actualStatus": actual,
            "expectedStatus": case.get("expectedStatus"),
            "passed": actual == case.get("expectedStatus") and not missing,
            "missingRequiredFields": missing,
        })

    checks = {
        "contract_schema": contract.get("schemaVersion") == "schedule-import-contract-v1",
        "fixture_schema": fixture.get("schemaVersion") == "offseason-schedule-mapping-fixture-v1",
        "fixture_mode": fixture.get("fixtureMode") is True,
        "team_registry_schema": teams_doc.get("schemaVersion") == "nba-team-registry-v1",
        "required_fields_present": all(not result["missingRequiredFields"] for result in case_results),
        "unique_source_event_ids": len(source_event_ids) == len(set(source_event_ids)),
        "mapping_statuses_complete": {"unmapped", "candidate_unverified", "verified", "rejected", "quarantined"}.issubset(allowed_statuses),
        "mapping_methods_complete": {"none", "explicit_official_id", "explicit_project_id", "exact_date_home_away_candidate", "manual_audited_mapping", "synthetic_fixture_only"}.issubset(allowed_methods),
        "exact_candidate_key": identity.get("exactCandidateKey") == ["scheduled_game_date", "home_team_abbr", "away_team_abbr"],
        "no_fuzzy_matching": identity.get("fuzzyMatchingAllowed") is False,
        "no_score_repair": identity.get("scoreAssistedIdentityRepairAllowed") is False,
        "no_many_to_many": identity.get("manyToManyMappingAllowed") is False,
        "historical_alias_review": identity.get("historicalAliasRequiresSeasonValidation") is True,
        "unknown_alias_quarantined": identity.get("unknownTeamAliasBehavior") == "quarantined",
        "timezone_policy": (
            time_policy.get("scheduledTipoffMustBeTimezoneAware") is True
            and time_policy.get("retrievedAtMustBeTimezoneAware") is True
            and time_policy.get("normalizedTimezone") == "UTC"
            and time_policy.get("dateOnlyScheduleAccepted") is False
        ),
        "fixture_times_timezone_aware": all(
            timezone_aware(case.get("scheduledTipoff")) and timezone_aware(case.get("retrievedAt"))
            for case in cases
        ),
        "fixture_hashes_valid": all(
            len(str(case.get("payloadSha256", ""))) == 64
            and all(char in "0123456789abcdef" for char in str(case.get("payloadSha256", "")).lower())
            for case in cases
        ),
        "quality_gates_enabled": all(
            quality_gates.get(key) is True
            for key in (
                "uniqueSourceEventIdWithinSource",
                "homeAndAwayMustDiffer",
                "bothTeamsMustResolve",
                "scheduledTipoffRequired",
                "payloadHashRequired",
            )
        ),
        "all_fixture_cases_pass": all(result["passed"] for result in case_results),
        "collection_inactive": contract.get("currentState", {}).get("collectionActive") is False,
        "schedule_not_imported": contract.get("currentState", {}).get("scheduleImported") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "offseason-schedule-mapping-validation-report-v1",
        "validatedAt": now_utc(),
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "caseResults": case_results,
        "summary": {
            "fixtureCases": len(cases),
            "currentAliases": len(current),
            "historicalAliases": len(historical),
            "verifiedCases": sum(result["actualStatus"] == "verified" for result in case_results),
            "candidateCases": sum(result["actualStatus"] == "candidate_unverified" for result in case_results),
            "quarantinedCases": sum(result["actualStatus"] == "quarantined" for result in case_results),
            "rejectedCases": sum(result["actualStatus"] == "rejected" for result in case_results),
        },
        "quality": {
            "networkCallsMade": False,
            "sourceScheduleRead": False,
            "rawRowsEmitted": 0,
            "rawFilesEmitted": False,
            "crossRepositoryWrite": False,
        },
    }


def self_test(contract: dict[str, Any], teams_doc: dict[str, Any], fixture: dict[str, Any]) -> None:
    report = validate(contract, teams_doc, fixture)
    assert report["formalState"] == READY, report

    changed = copy.deepcopy(contract)
    changed["identityPolicy"]["fuzzyMatchingAllowed"] = True
    report = validate(changed, teams_doc, fixture)
    assert report["formalState"] == INVALID
    assert "no_fuzzy_matching" in report["failedChecks"]

    changed = copy.deepcopy(fixture)
    changed["cases"][0]["expectedStatus"] = "verified"
    report = validate(contract, teams_doc, changed)
    assert report["formalState"] == INVALID
    assert "all_fixture_cases_pass" in report["failedChecks"]

    changed = copy.deepcopy(fixture)
    changed["cases"][1]["scheduledTipoff"] = "2026-10-20"
    report = validate(contract, teams_doc, changed)
    assert report["formalState"] == INVALID
    assert "fixture_times_timezone_aware" in report["failedChecks"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path("config/schedule-import-contract-v1.json"))
    parser.add_argument("--teams", type=Path, default=Path("config/nba-team-registry-v1.json"))
    parser.add_argument("--fixture", type=Path, default=Path("data/fixtures/offseason-schedule-mapping-v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    contract = load(args.contract)
    teams_doc = load(args.teams)
    fixture = load(args.fixture)
    if args.self_test:
        self_test(contract, teams_doc, fixture)
    report = validate(contract, teams_doc, fixture)
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
