import copy
import json
from pathlib import Path

import pytest

from nba_odds_history_hub.database import connect_database
from nba_odds_history_hub.preseason_dry_run import READY, load_json, run_dry_run, validate_configuration

ROOT = Path(__file__).resolve().parents[1]


def test_preseason_dry_run_reaches_awaiting_approval_state(tmp_path):
    database = tmp_path / "preseason.sqlite"
    report = run_dry_run(ROOT, database)
    assert report["formalState"] == READY
    assert report["checksPassed"] == report["checksTotal"] == 15
    assert report["stateTransitions"] == [
        "offseason_sleep",
        "preseason_dry_run_config_valid",
        "preseason_dry_run_partial",
        "preseason_dry_run_ready_awaiting_owner_approval",
    ]
    assert report["totals"] == {
        "acceptedRows": 5,
        "excludedRows": 2,
        "scheduleVersionsInserted": 5,
        "scheduleIdentityChanges": 1,
        "payloadOnlyRevisions": 1,
        "idempotentReplayRows": 3,
    }
    assert report["database"]["sourceEventCount"] == 3
    assert report["database"]["scheduleVersionCount"] == 5
    assert report["database"]["currentScheduleCount"] == 3
    assert report["database"]["auditDecisionCount"] == 5
    assert report["mapping"]["statusCounts"] == {"candidate_unverified": 3}


def test_dry_run_writes_no_production_rows_or_canonical_ids(tmp_path):
    database = tmp_path / "preseason.sqlite"
    report = run_dry_run(ROOT, database)
    with connect_database(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM odds_snapshots").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM canonical_events").fetchone()[0] == 0
    assert report["boundary"] == {
        "fixtureOnly": True,
        "externalRead": False,
        "productionImport": False,
        "scheduledCollection": False,
        "crossRepositoryWrite": False,
        "rowLevelRecordsEmitted": False,
    }


def test_configuration_fails_closed_when_external_read_changes():
    readiness = load_json(ROOT / "config/preseason-readiness-v1.json")
    season = load_json(ROOT / "config/season-configuration-v1.json")
    changed = copy.deepcopy(readiness)
    changed["externalRead"] = True
    with pytest.raises(ValueError, match="inactive boundary"):
        validate_configuration(changed, season)


def test_configuration_fails_closed_when_canonical_creation_changes():
    readiness = load_json(ROOT / "config/preseason-readiness-v1.json")
    season = copy.deepcopy(load_json(ROOT / "config/season-configuration-v1.json"))
    season["canonicalEventIdCreationAllowed"] = True
    with pytest.raises(ValueError, match="canonical event ID creation"):
        validate_configuration(readiness, season)


def test_fixture_expected_counts_are_explicit():
    fixture = json.loads((ROOT / "data/fixtures/preseason-dry-run-v1.json").read_text(encoding="utf-8"))
    assert fixture["expected"] == {
        "observationCount": 2,
        "acceptedRows": 5,
        "excludedRows": 2,
        "sourceEvents": 3,
        "scheduleVersions": 5,
        "currentSchedules": 3,
        "auditDecisions": 5,
        "finalState": "preseason_dry_run_ready_awaiting_owner_approval",
    }
