import copy
import json
from pathlib import Path

import pytest

from nba_odds_history_hub.disabled_import_request import (
    READY,
    DisabledImportRequestError,
    build_report,
    validate_contract,
)
from nba_odds_history_hub.manual_schedule_preflight import validate_file_identity

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_disabled_import_request_and_backup_restore_pass(tmp_path):
    report = build_report(ROOT, tmp_path / "workspace")
    assert report["formalState"] == READY
    assert report["checksPassed"] == report["checksTotal"]
    assert report["failedChecks"] == []
    assert all(report["checks"].values())


def test_backup_restore_returns_exact_seed_state(tmp_path):
    report = build_report(ROOT, tmp_path / "workspace")
    result = report["backupRestore"]
    expected = load("config/disabled-import-request-contract-v1.json")[
        "backupRestoreFixture"
    ]
    assert result["seedCounts"] == expected["expectedSeedCounts"]
    assert result["mutationCounts"] == expected["expectedMutationCounts"]
    assert result["restoredCounts"] == expected["expectedSeedCounts"]
    assert result["seedBackupBytesMatch"] is True
    assert result["mutationChangedDatabase"] is True
    assert result["restoreBytesMatchBackup"] is True


def test_report_remains_disabled_and_aggregate_only(tmp_path):
    report = build_report(ROOT, tmp_path / "workspace")
    assert report["approval"] == {
        "requested": False,
        "recorded": False,
        "granted": False,
        "executionEnabled": False,
        "executionCount": 0,
    }
    assert report["boundary"] == {
        "fixtureOnly": True,
        "temporaryDatabaseOnly": True,
        "externalScheduleRead": False,
        "productionDatabaseTouched": False,
        "productionScheduleImported": False,
        "scheduledCollection": False,
        "canonicalEventIdsCreated": 0,
        "crossRepositoryWrite": False,
        "rowLevelRecordsEmitted": False,
        "shellCommandEmitted": False,
    }


def test_contract_rejects_approval_activation():
    contract = load("config/disabled-import-request-contract-v1.json")
    changed = copy.deepcopy(contract)
    changed["approvalGranted"] = True
    with pytest.raises(DisabledImportRequestError, match="approvalGranted must remain false"):
        validate_contract(changed)


def test_contract_rejects_production_database_reference():
    contract = load("config/disabled-import-request-contract-v1.json")
    changed = copy.deepcopy(contract)
    changed["productionReferences"]["approvedDatabasePath"] = "data/odds.sqlite"
    with pytest.raises(DisabledImportRequestError, match="production database path is prohibited"):
        validate_contract(changed)


def test_contract_rejects_production_backup_reference():
    contract = load("config/disabled-import-request-contract-v1.json")
    changed = copy.deepcopy(contract)
    changed["productionReferences"]["backupId"] = "real-backup"
    with pytest.raises(DisabledImportRequestError, match="production backup id is prohibited"):
        validate_contract(changed)


def test_contract_rejects_boundary_drift():
    contract = load("config/disabled-import-request-contract-v1.json")
    changed = copy.deepcopy(contract)
    changed["executionBoundary"]["networkCallsAllowed"] = True
    with pytest.raises(DisabledImportRequestError, match="disabled execution boundary changed"):
        validate_contract(changed)


def test_target_file_identity_rejects_hash_drift():
    contract = load("config/disabled-import-request-contract-v1.json")
    changed = copy.deepcopy(contract)
    changed["targetFile"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="target sha256 mismatch"):
        validate_file_identity(ROOT, changed)


def test_workspace_inside_repository_is_rejected():
    with pytest.raises(
        DisabledImportRequestError,
        match="workspace must remain outside the repository",
    ):
        build_report(ROOT, ROOT / "runtime" / "forbidden-workspace")
