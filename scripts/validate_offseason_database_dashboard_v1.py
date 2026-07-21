#!/usr/bin/env python3
"""Validate additive mapping database tables and the static readiness dashboard."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from nba_odds_history_hub.database import (
    connect_database,
    register_source,
    register_source_events,
    upsert_canonical_event,
)
from nba_odds_history_hub.mapping import (
    build_mapping_readiness_report,
    record_mapping_decision,
    record_schedule_version,
)

READY = "OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY"
INVALID = "OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_INVALID"


def _fixture_event(event_id: int, observed_at: str) -> dict[str, Any]:
    return {
        "source": "offseason_fixture",
        "source_event_id": event_id,
        "bookmaker_id": None,
        "league": "NBA",
        "event_type": "game",
        "market_name": f"Offseason fixture {event_id}",
        "scheduled_tipoff": "2026-10-21T00:00:00+00:00",
        "cutoff_at": None,
        "canonical_event_id": None,
        "observed_at": observed_at,
    }


def validate(readiness_path: Path, page_path: Path) -> dict[str, Any]:
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    page = page_path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="nba-odds-offseason-db-") as tmp:
        database = Path(tmp) / "fixture.sqlite"
        observed = "2026-07-21T12:30:00+08:00"
        register_source(
            database,
            source_id="offseason_fixture",
            display_name="Offseason Fixture",
            source_class="synthetic_fixture",
            access_mode="offline",
        )
        register_source_events(
            database,
            [_fixture_event(7001, observed), _fixture_event(7002, observed)],
        )
        version_one = record_schedule_version(
            database,
            source_id="offseason_fixture",
            source_event_id=7001,
            scheduled_tipoff="2026-10-20T19:30:00-04:00",
            home_team_abbr="BOS",
            away_team_abbr="ATL",
            observed_at=observed,
            source_payload_sha256="a" * 64,
        )
        duplicate = record_schedule_version(
            database,
            source_id="offseason_fixture",
            source_event_id=7001,
            scheduled_tipoff="2026-10-20T19:30:00-04:00",
            home_team_abbr="BOS",
            away_team_abbr="ATL",
            observed_at="2026-07-21T12:31:00+08:00",
            source_payload_sha256="a" * 64,
        )
        version_two = record_schedule_version(
            database,
            source_id="offseason_fixture",
            source_event_id=7001,
            scheduled_tipoff="2026-10-20T20:00:00-04:00",
            home_team_abbr="BOS",
            away_team_abbr="ATL",
            observed_at="2026-07-21T12:32:00+08:00",
            source_payload_sha256="b" * 64,
        )
        record_schedule_version(
            database,
            source_id="offseason_fixture",
            source_event_id=7002,
            scheduled_tipoff="2026-10-20T22:00:00-04:00",
            home_team_abbr="NYK",
            away_team_abbr="PHI",
            observed_at=observed,
            source_payload_sha256="c" * 64,
        )
        upsert_canonical_event(
            database,
            canonical_event_id="fixture-only:7001",
            league="NBA",
            event_type="game",
            scheduled_tipoff="2026-10-21T00:00:00+00:00",
            home_team="BOS",
            away_team="ATL",
        )
        record_mapping_decision(
            database,
            source_id="offseason_fixture",
            source_event_id=7001,
            new_status="verified",
            mapping_method="synthetic_fixture_only",
            reason_code="fixture_explicit_mapping",
            actor_type="synthetic_validator",
            decided_at="2026-07-21T12:35:00+08:00",
            canonical_event_id="fixture-only:7001",
            source_payload_sha256="b" * 64,
        )
        record_mapping_decision(
            database,
            source_id="offseason_fixture",
            source_event_id=7002,
            new_status="quarantined",
            mapping_method="none",
            reason_code="fixture_requires_review",
            actor_type="synthetic_validator",
            decided_at="2026-07-21T12:35:00+08:00",
            source_payload_sha256="c" * 64,
        )
        database_report = build_mapping_readiness_report(database)
        with connect_database(database) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            views = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='view'"
                )
            }

    checks = {
        "readiness_schema": readiness.get("schemaVersion") == "offseason-readiness-v1",
        "readiness_fixture_mode": readiness.get("fixtureMode") is True,
        "readiness_sleep_mode": readiness.get("currentMode") == "offseason_sleep",
        "readiness_team_count": readiness.get("summary", {}).get("teams") == 30,
        "readiness_market_count": readiness.get("summary", {}).get("marketClasses") == 11,
        "readiness_mapping_cases": readiness.get("summary", {}).get("mappingCases") == 5,
        "readiness_database_tables": readiness.get("summary", {}).get("databaseTables") == 2,
        "readiness_database_views": readiness.get("summary", {}).get("databaseViews") == 2,
        "readiness_active_templates_zero": readiness.get("summary", {}).get("activeTemplates") == 0,
        "dashboard_declares_zh_hant": 'lang="zh-Hant"' in page,
        "dashboard_loads_readiness_json": "data/public/offseason-readiness.json" in page,
        "dashboard_links_home": 'href="index.html"' in page,
        "dashboard_mentions_fixture_boundary": "synthetic fixtures" in page,
        "database_ready": database_report.get("formalState") == "OFFSEASON_MAPPING_DATABASE_READY",
        "database_tables_present": {
            "source_event_schedule_versions",
            "source_event_mapping_audit",
        } <= tables,
        "database_views_present": {
            "current_source_event_schedules",
            "source_event_mapping_status_summary",
        } <= views,
        "first_version_inserted": version_one.get("inserted") is True and version_one.get("version_number") == 1,
        "duplicate_version_skipped": duplicate.get("inserted") is False,
        "changed_version_inserted": version_two.get("inserted") is True and version_two.get("version_number") == 2,
        "schedule_versions_count": database_report.get("database", {}).get("scheduleVersionCount") == 3,
        "current_schedule_count": database_report.get("database", {}).get("currentScheduleCount") == 2,
        "audit_decision_count": database_report.get("database", {}).get("auditDecisionCount") == 2,
        "verified_count": database_report.get("mapping", {}).get("verifiedEventCount") == 1,
        "verified_coverage": database_report.get("mapping", {}).get("verifiedCoveragePct") == 50.0,
        "no_multiple_current_versions": database_report.get("database", {}).get("multipleCurrentScheduleGroups") == 0,
        "aggregate_only": database_report.get("quality", {}).get("aggregateOnly") is True,
        "raw_rows_zero": database_report.get("quality", {}).get("rawRowsEmitted") == 0,
        "raw_files_false": database_report.get("quality", {}).get("rawFilesEmitted") is False,
        "network_calls_false": database_report.get("quality", {}).get("networkCallsMade") is False,
        "cross_repository_write_false": database_report.get("quality", {}).get("crossRepositoryWrite") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "offseason-database-dashboard-validation-report-v1",
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "fixtureDatabase": database_report,
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
    parser.add_argument(
        "--readiness",
        type=Path,
        default=Path("data/public/offseason-readiness.json"),
    )
    parser.add_argument("--page", type=Path, default=Path("readiness.html"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = validate(args.readiness, args.page)
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
