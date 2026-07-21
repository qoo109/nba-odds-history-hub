import copy
import json
from pathlib import Path

import pytest

from nba_odds_history_hub.owner_review_packet import (
    READY,
    ReviewPacketError,
    build_review_report,
    validate_command_plan,
    validate_packet,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_owner_review_packet_is_complete_and_disabled():
    report = build_review_report(ROOT)
    assert report["formalState"] == READY
    assert report["checksPassed"] == report["checksTotal"] == 31
    assert report["failedChecks"] == []
    assert report["packet"] == {
        "packetId": "SCHEDULE-OWNER-REVIEW-2026-07-21-001",
        "state": "review_ready_disabled",
        "sourcePreflightRequestId": "SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001",
        "decisionRequested": False,
        "decisionRecorded": False,
        "approvalGranted": False,
    }
    assert report["evidence"]["preflightChecks"] == {"passed": 19, "total": 19}
    assert report["evidence"]["postRollbackTotalRows"] == 0


def test_command_plan_is_control_steps_not_a_runnable_command():
    report = build_review_report(ROOT)
    plan = report["commandPlan"]
    assert plan["state"] == "disabled_non_executable"
    assert plan["representation"] == "ordered_control_steps"
    assert plan["executable"] is False
    assert plan["shellCommandEmitted"] is False
    assert plan["implementationModulePresent"] is False
    assert plan["controlStepCount"] == 6
    assert plan["requiredPlaceholderCount"] == 5
    assert all(value in (False, 0, True) for value in report["boundary"].values())
    assert report["boundary"]["fixtureOnly"] is True
    assert report["boundary"]["executionCount"] == 0


def test_packet_rejects_approval_activation():
    packet = load("config/preseason-owner-review-packet-v1.json")
    changed = copy.deepcopy(packet)
    changed["ownerDecision"]["approvalGranted"] = True
    with pytest.raises(ReviewPacketError, match="approval must remain false"):
        validate_packet(changed)


def test_packet_rejects_execution_activation():
    packet = load("config/preseason-owner-review-packet-v1.json")
    changed = copy.deepcopy(packet)
    changed["executionBoundary"]["executionEnabled"] = True
    with pytest.raises(ReviewPacketError, match="execution boundary changed"):
        validate_packet(changed)


def test_plan_rejects_executable_state():
    plan = load("config/disabled-manual-import-command-plan-v1.json")
    changed = copy.deepcopy(plan)
    changed["executable"] = True
    with pytest.raises(ReviewPacketError, match="non-executable"):
        validate_command_plan(changed)


def test_plan_rejects_command_like_fields():
    plan = load("config/disabled-manual-import-command-plan-v1.json")
    changed = copy.deepcopy(plan)
    changed["command"] = "not allowed"
    with pytest.raises(ReviewPacketError, match="command-like fields"):
        validate_command_plan(changed)
