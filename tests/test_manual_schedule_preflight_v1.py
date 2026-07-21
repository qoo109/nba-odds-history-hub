import copy
import json
from pathlib import Path

import pytest

from nba_odds_history_hub.manual_schedule_preflight import (
    READY,
    run_preflight,
    validate_contract,
    validate_file_identity,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_three_stage_preflight_passes_and_rolls_back(tmp_path):
    report = run_preflight(ROOT, tmp_path / "preflight.sqlite")
    assert report["formalState"] == READY
    assert report["checksPassed"] == report["checksTotal"] == 19
    assert [row["stage"] for row in report["stages"]] == [1, 2, 3]
    assert all(row["passed"] for row in report["stages"])
    preview = report["stages"][1]["result"]
    assert preview["observations"] == 2
    assert preview["acceptedRows"] == 5
    assert preview["excludedRows"] == 2
    assert preview["uniqueAcceptedEvents"] == 3
    rollback = report["stages"][2]["result"]
    assert rollback["insideTransaction"] == {
        "dataSources": 1,
        "sourceEvents": 3,
        "scheduleVersions": 5,
        "currentSchedules": 3,
        "mappingAuditDecisions": 5,
        "canonicalEvents": 0,
        "rawImports": 0,
        "oddsSnapshots": 0,
    }
    assert rollback["allPreviewRowsRemoved"] is True
    assert all(value == 0 for value in rollback["afterRollback"].values())


def test_committed_aggregate_status_is_reproducible(tmp_path):
    generated = run_preflight(ROOT, tmp_path / "preflight.sqlite")
    committed = load("data/manual-schedule-import-preflight-current-status-v1.json")
    assert generated == committed


def test_preflight_remains_disabled_and_fixture_only(tmp_path):
    report = run_preflight(ROOT, tmp_path / "preflight.sqlite")
    assert report["approval"] == {
        "ownerApprovalGranted": False,
        "executionEnabled": False,
        "executionCount": 0,
        "productionImportExecuted": False,
        "postImportVerificationState": "not_applicable_preapproval",
    }
    assert report["boundary"]["fixtureOnly"] is True
    assert report["boundary"]["externalFilesRead"] is False
    assert report["boundary"]["networkCallsMade"] is False
    assert report["boundary"]["productionDatabaseTouched"] is False
    assert report["boundary"]["productionScheduleImported"] is False
    assert report["boundary"]["crossRepositoryWrite"] is False


def test_contract_rejects_execution_activation():
    contract = load("config/manual-schedule-import-preflight-v1.json")
    changed = copy.deepcopy(contract)
    changed["executionEnabled"] = True
    with pytest.raises(ValueError, match="execution must remain disabled"):
        validate_contract(changed)


def test_contract_rejects_external_file_boundary():
    contract = load("config/manual-schedule-import-preflight-v1.json")
    changed = copy.deepcopy(contract)
    changed["executionBoundary"]["externalFileAllowed"] = True
    with pytest.raises(ValueError, match="inactive execution boundary changed"):
        validate_contract(changed)


def test_file_identity_rejects_hash_drift():
    contract = load("config/manual-schedule-import-preflight-v1.json")
    changed = copy.deepcopy(contract)
    changed["targetFile"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="target sha256 mismatch"):
        validate_file_identity(ROOT, changed)
