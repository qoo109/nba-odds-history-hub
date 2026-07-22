import copy
import json
from pathlib import Path

import pytest

from nba_odds_history_hub.approval_state_machine import (
    READY,
    ApprovalStateMachineError,
    build_report,
    evaluate_change,
    validate_machine,
    validate_matrix,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_state_machine_and_change_matrix_are_ready_and_disabled():
    report = build_report(ROOT)
    assert report["formalState"] == READY
    assert report["checksPassed"] == report["checksTotal"]
    assert report["checksTotal"] >= 60
    assert report["failedChecks"] == []
    assert report["machine"] == {
        "machineId": "SCHEDULE-APPROVAL-STATE-MACHINE-2026-07-21-001",
        "sourcePacketId": "SCHEDULE-OWNER-REVIEW-2026-07-21-001",
        "currentState": "review_ready_disabled",
        "stateCount": 8,
        "transitionCount": 15,
        "terminalStateCount": 4,
        "maxReviewAgeDays": 14,
    }
    assert report["matrix"] == {
        "matrixId": "SCHEDULE-CHANGE-CONTROL-2026-07-21-001",
        "changeRuleCount": 16,
        "rePreflightFieldCount": 6,
        "prohibitedActivationCount": 11,
        "defaultAction": "fail_closed_manual_review",
    }


def test_change_scenarios_fail_closed():
    matrix = load("config/preseason-change-control-matrix-v1.json")
    assert evaluate_change(matrix, "targetFile.sha256") == "re_preflight_required"
    assert evaluate_change(matrix, "targetFile.schemaVersion") == "re_preflight_required"
    assert evaluate_change(matrix, "preflight.failedChecks") == "rejected_closed"
    assert evaluate_change(matrix, "review.ageDays", 14) == "no_change"
    assert evaluate_change(matrix, "review.ageDays", 15) == "expired_closed"
    assert evaluate_change(matrix, "ownerDecision.rejected") == "rejected_closed"
    assert evaluate_change(matrix, "ownerDecision.revoked") == "revoked_closed"
    assert evaluate_change(matrix, "executionBoundary") == "revoked_closed"
    assert evaluate_change(matrix, "unknown.field") == "fail_closed_manual_review"


def test_machine_rejects_approval_activation():
    machine = load("config/preseason-approval-state-machine-v1.json")
    changed = copy.deepcopy(machine)
    changed["approvalGranted"] = True
    with pytest.raises(ApprovalStateMachineError, match="approvalGranted must remain false"):
        validate_machine(changed)


def test_machine_rejects_new_approval_state():
    machine = load("config/preseason-approval-state-machine-v1.json")
    changed = copy.deepcopy(machine)
    changed["states"].append("production_approved")
    with pytest.raises(ApprovalStateMachineError, match="state set changed"):
        validate_machine(changed)


def test_machine_rejects_unknown_transition_target():
    machine = load("config/preseason-approval-state-machine-v1.json")
    changed = copy.deepcopy(machine)
    changed["allowedTransitions"][0]["to"] = "unknown_state"
    with pytest.raises(ApprovalStateMachineError, match="unknown state"):
        validate_machine(changed)


def test_matrix_rejects_identity_action_relaxation():
    matrix = load("config/preseason-change-control-matrix-v1.json")
    changed = copy.deepcopy(matrix)
    changed["changes"][3]["action"] = "no_change"
    with pytest.raises(ApprovalStateMachineError, match="identity drift must require re-preflight"):
        validate_matrix(changed)


def test_matrix_rejects_boundary_activation():
    matrix = load("config/preseason-change-control-matrix-v1.json")
    changed = copy.deepcopy(matrix)
    changed["boundary"]["externalFilesRead"] = True
    with pytest.raises(ApprovalStateMachineError, match="matrix boundary changed"):
        validate_matrix(changed)


def test_matrix_rejects_prohibited_activation_removal():
    matrix = load("config/preseason-change-control-matrix-v1.json")
    changed = copy.deepcopy(matrix)
    changed["prohibitedV020Activations"].remove("productionImportAllowed")
    with pytest.raises(ApprovalStateMachineError, match="prohibited activation set changed"):
        validate_matrix(changed)
