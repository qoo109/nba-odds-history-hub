"""Validate aggregate owner-review evidence and a disabled control-step plan."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

READY = "OFFSEASON_PRESEASON_OWNER_REVIEW_PACKET_AND_DISABLED_IMPORT_COMMAND_PLAN_V1_READY"
INVALID = "OFFSEASON_PRESEASON_OWNER_REVIEW_PACKET_AND_DISABLED_IMPORT_COMMAND_PLAN_V1_INVALID"

PACKET_PATH = Path("config/preseason-owner-review-packet-v1.json")
PLAN_PATH = Path("config/disabled-manual-import-command-plan-v1.json")
PREFLIGHT_PATH = Path("data/manual-schedule-import-preflight-current-status-v1.json")


class ReviewPacketError(ValueError):
    """Raised when a disabled review contract crosses its declared boundary."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewPacketError(f"{path} must contain one JSON object")
    return value


def _forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("_", "")
            if normalized in {"command", "shell", "argv", "tokens", "script"}:
                found.add(str(key))
            found.update(_forbidden_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_forbidden_keys(child))
    return found


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != "preseason-owner-review-packet-v1":
        raise ReviewPacketError("unsupported owner review packet schema")
    if packet.get("state") != "review_ready_disabled":
        raise ReviewPacketError("owner review packet must remain disabled")
    decision = packet.get("ownerDecision") or {}
    if decision.get("decisionRequested") is not False:
        raise ReviewPacketError("owner decision must not be requested")
    if decision.get("decisionRecorded") is not False:
        raise ReviewPacketError("owner decision must not be recorded")
    if decision.get("approvalGranted") is not False:
        raise ReviewPacketError("owner approval must remain false")
    if decision.get("approvalRequiresSeparateRequest") is not True:
        raise ReviewPacketError("separate approval request must remain required")
    boundary = packet.get("executionBoundary") or {}
    if boundary.get("fixtureOnly") is not True:
        raise ReviewPacketError("owner review packet must remain fixture-only")
    false_keys = (
        "executionEnabled",
        "externalFileAllowed",
        "productionDatabaseAllowed",
        "productionImportAllowed",
        "networkCallsAllowed",
        "scheduledCollectionAllowed",
        "canonicalEventIdCreationAllowed",
        "crossRepositoryWriteAllowed",
        "rowLevelRecordsAllowed",
    )
    if any(boundary.get(key) is not False for key in false_keys):
        raise ReviewPacketError("owner review execution boundary changed")
    if boundary.get("maximumExecutionCount") != 0:
        raise ReviewPacketError("maximum execution count must remain zero")


def validate_command_plan(plan: dict[str, Any]) -> None:
    if plan.get("schemaVersion") != "disabled-manual-import-command-plan-v1":
        raise ReviewPacketError("unsupported command plan schema")
    if plan.get("state") != "disabled_non_executable":
        raise ReviewPacketError("command plan must remain disabled")
    if plan.get("representation") != "ordered_control_steps":
        raise ReviewPacketError("command plan representation changed")
    if plan.get("executable") is not False:
        raise ReviewPacketError("command plan must remain non-executable")
    if plan.get("shellCommandEmitted") is not False:
        raise ReviewPacketError("shell command emission must remain false")
    if plan.get("implementationModulePresent") is not False:
        raise ReviewPacketError("implementation module must remain absent")
    forbidden = _forbidden_keys(plan)
    if forbidden:
        raise ReviewPacketError(f"command-like fields are forbidden: {sorted(forbidden)}")
    expected_placeholders = {
        "SEPARATE_APPROVAL_REQUEST_ID",
        "APPROVED_FILE_PATH",
        "APPROVED_FILE_SHA256",
        "APPROVED_DATABASE_PATH",
        "BACKUP_ID",
    }
    if set(plan.get("requiredPlaceholders") or []) != expected_placeholders:
        raise ReviewPacketError("required placeholders changed")
    steps = plan.get("steps") or []
    if [item.get("sequence") for item in steps] != list(range(1, 7)):
        raise ReviewPacketError("control-step sequence must be one through six")
    boundary = plan.get("executionBoundary") or {}
    if boundary.get("fixtureOnly") is not True:
        raise ReviewPacketError("command plan must remain fixture-only")
    false_keys = (
        "executionEnabled",
        "externalFileAllowed",
        "productionDatabaseAllowed",
        "productionImportAllowed",
        "networkCallsAllowed",
        "scheduledCollectionAllowed",
        "canonicalEventIdCreationAllowed",
        "crossRepositoryWriteAllowed",
        "rowLevelRecordsAllowed",
    )
    if any(boundary.get(key) is not False for key in false_keys):
        raise ReviewPacketError("command plan execution boundary changed")
    if boundary.get("maximumExecutionCount") != 0:
        raise ReviewPacketError("command plan maximum execution count must remain zero")


def build_review_report(root: Path) -> dict[str, Any]:
    packet = load_json(root / PACKET_PATH)
    plan = load_json(root / PLAN_PATH)
    preflight = load_json(root / PREFLIGHT_PATH)
    validate_packet(packet)
    validate_command_plan(plan)

    preflight_stage_1 = preflight["stages"][0]["result"]
    preflight_stage_3 = preflight["stages"][2]["result"]
    packet_evidence = packet["evidence"]
    packet_boundary = packet["executionBoundary"]
    plan_boundary = plan["executionBoundary"]
    post_rollback = preflight_stage_3["afterRollback"]
    post_rollback_total = sum(int(value) for value in post_rollback.values())
    module_absent = not (root / "src/nba_odds_history_hub/manual_schedule_import.py").exists()

    checks = {
        "packet_schema": packet["schemaVersion"] == "preseason-owner-review-packet-v1",
        "packet_state_disabled": packet["state"] == "review_ready_disabled",
        "source_request_match": packet["sourcePreflightRequestId"] == preflight["requestId"],
        "preflight_ready": packet["sourcePreflightFormalState"] == preflight["formalState"],
        "preflight_checks_complete": preflight["checksPassed"] == preflight["checksTotal"] == 19,
        "file_identity_exact": packet_evidence["targetFile"] == preflight_stage_1,
        "rollback_executed": packet_evidence["rollback"]["executed"] is True and preflight_stage_3["rollbackExecuted"] is True,
        "rollback_zero_rows": packet_evidence["rollback"]["postRollbackTotalRows"] == post_rollback_total == 0,
        "rollback_preview_removed": packet_evidence["rollback"]["allPreviewRowsRemoved"] is True and preflight_stage_3["allPreviewRowsRemoved"] is True,
        "artifact_identity_exact": packet_evidence["artifact"] == {
            "id": 8500959742,
            "digest": "sha256:cd398c5a3bba096b1f5ba392bb47c8afff766be66a2d955a267d0360bfd4d654",
        },
        "decision_not_requested": packet["ownerDecision"]["decisionRequested"] is False,
        "decision_not_recorded": packet["ownerDecision"]["decisionRecorded"] is False,
        "approval_false": packet["ownerDecision"]["approvalGranted"] is False,
        "separate_request_required": packet["ownerDecision"]["approvalRequiresSeparateRequest"] is True,
        "execution_disabled": packet_boundary["executionEnabled"] is False and plan_boundary["executionEnabled"] is False,
        "maximum_execution_zero": packet_boundary["maximumExecutionCount"] == plan_boundary["maximumExecutionCount"] == 0,
        "plan_schema": plan["schemaVersion"] == "disabled-manual-import-command-plan-v1",
        "plan_state_disabled": plan["state"] == "disabled_non_executable",
        "plan_non_executable": plan["executable"] is False,
        "no_shell_command": plan["shellCommandEmitted"] is False,
        "no_command_fields": not _forbidden_keys(plan),
        "placeholders_present": len(plan["requiredPlaceholders"]) == 5,
        "six_control_steps": len(plan["steps"]) == 6,
        "implementation_module_absent": module_absent,
        "production_import_false": packet_boundary["productionImportAllowed"] is False and plan_boundary["productionImportAllowed"] is False,
        "external_and_network_false": all(
            boundary["externalFileAllowed"] is False and boundary["networkCallsAllowed"] is False
            for boundary in (packet_boundary, plan_boundary)
        ),
        "scheduled_collection_false": packet_boundary["scheduledCollectionAllowed"] is False and plan_boundary["scheduledCollectionAllowed"] is False,
        "canonical_creation_false": packet_boundary["canonicalEventIdCreationAllowed"] is False and plan_boundary["canonicalEventIdCreationAllowed"] is False,
        "cross_repository_false": packet_boundary["crossRepositoryWriteAllowed"] is False and plan_boundary["crossRepositoryWriteAllowed"] is False,
        "aggregate_only": packet_boundary["rowLevelRecordsAllowed"] is False and plan_boundary["rowLevelRecordsAllowed"] is False,
        "synthetic_fixture_only": packet_boundary["fixtureOnly"] is True and plan_boundary["fixtureOnly"] is True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schemaVersion": "preseason-owner-review-packet-report-v1",
        "asOf": packet["asOf"],
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "failedChecks": failed,
        "packet": {
            "packetId": packet["packetId"],
            "state": packet["state"],
            "sourcePreflightRequestId": packet["sourcePreflightRequestId"],
            "decisionRequested": packet["ownerDecision"]["decisionRequested"],
            "decisionRecorded": packet["ownerDecision"]["decisionRecorded"],
            "approvalGranted": packet["ownerDecision"]["approvalGranted"],
        },
        "evidence": {
            "targetFile": packet_evidence["targetFile"],
            "preflightChecks": {
                "passed": preflight["checksPassed"],
                "total": preflight["checksTotal"],
            },
            "artifact": packet_evidence["artifact"],
            "rollbackExecuted": preflight_stage_3["rollbackExecuted"],
            "postRollbackTotalRows": post_rollback_total,
        },
        "commandPlan": {
            "planId": plan["planId"],
            "state": plan["state"],
            "representation": plan["representation"],
            "executable": plan["executable"],
            "shellCommandEmitted": plan["shellCommandEmitted"],
            "implementationModulePresent": not module_absent,
            "controlStepCount": len(plan["steps"]),
            "requiredPlaceholderCount": len(plan["requiredPlaceholders"]),
        },
        "boundary": {
            "fixtureOnly": True,
            "externalFilesRead": False,
            "networkCallsMade": False,
            "productionDatabaseTouched": False,
            "productionScheduleImported": False,
            "scheduledCollection": False,
            "canonicalEventIdsCreated": 0,
            "crossRepositoryWrite": False,
            "rowLevelRecordsEmitted": False,
            "executionCount": 0,
        },
    }
