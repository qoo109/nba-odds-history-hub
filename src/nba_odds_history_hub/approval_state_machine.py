import json
from pathlib import Path
from typing import Any

READY = "OFFSEASON_PRESEASON_APPROVAL_STATE_MACHINE_AND_CHANGE_CONTROL_MATRIX_V1_READY"

EXPECTED_STATES = {
    "review_ready_disabled",
    "synthetic_review_requested",
    "synthetic_review_in_progress",
    "synthetic_review_complete_disabled",
    "re_preflight_required",
    "rejected_closed",
    "expired_closed",
    "revoked_closed",
}

REQUIRED_REPREFLIGHT_FIELDS = {
    "targetFile.path",
    "targetFile.filename",
    "targetFile.bytes",
    "targetFile.sha256",
    "targetFile.schemaVersion",
    "targetFile.seasonId",
}

PROHIBITED_ACTIVATIONS = {
    "approvalGranted",
    "executionEnabled",
    "productionDatabaseAllowed",
    "productionImportAllowed",
    "externalFileAllowed",
    "networkCallsAllowed",
    "scheduledCollectionAllowed",
    "canonicalEventIdCreationAllowed",
    "crossRepositoryWriteAllowed",
    "shellCommandAllowed",
    "implementationModuleAllowed",
}

SAFE_MACHINE_BOUNDARY = {
    "fixtureOnly": True,
    "externalFileAllowed": False,
    "productionDatabaseAllowed": False,
    "productionImportAllowed": False,
    "networkCallsAllowed": False,
    "scheduledCollectionAllowed": False,
    "canonicalEventIdCreationAllowed": False,
    "crossRepositoryWriteAllowed": False,
    "rowLevelRecordsAllowed": False,
    "shellCommandAllowed": False,
    "implementationModuleAllowed": False,
}


class ApprovalStateMachineError(ValueError):
    pass


def _load(root: Path, relative_path: str) -> dict[str, Any]:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))


def _transition_keys(machine: dict[str, Any]) -> set[tuple[str, str, str]]:
    return {
        (row["from"], row["event"], row["to"])
        for row in machine["allowedTransitions"]
    }


def validate_machine(machine: dict[str, Any]) -> None:
    if machine.get("schemaVersion") != "preseason-approval-state-machine-v1":
        raise ApprovalStateMachineError("unexpected state machine schema")
    if machine.get("initialState") != "review_ready_disabled":
        raise ApprovalStateMachineError("initial state must remain disabled")
    if machine.get("currentState") != "review_ready_disabled":
        raise ApprovalStateMachineError("current state must remain disabled")
    for field in ("approvalRequested", "approvalRecorded", "approvalGranted", "executionEnabled"):
        if machine.get(field) is not False:
            raise ApprovalStateMachineError(f"{field} must remain false")
    if machine.get("maximumExecutionCount") != 0:
        raise ApprovalStateMachineError("maximum execution count must remain zero")

    states = machine.get("states", [])
    if len(states) != len(set(states)) or set(states) != EXPECTED_STATES:
        raise ApprovalStateMachineError("state set changed")
    if any("approved" in state or "execut" in state for state in states):
        raise ApprovalStateMachineError("approval or execution state is prohibited")

    transitions = machine.get("allowedTransitions", [])
    keys = _transition_keys(machine)
    if len(transitions) != 15 or len(keys) != len(transitions):
        raise ApprovalStateMachineError("transition set changed")
    for source, _, target in keys:
        if source not in EXPECTED_STATES or target not in EXPECTED_STATES:
            raise ApprovalStateMachineError("transition references unknown state")

    required = {
        ("review_ready_disabled", "request_new_synthetic_review", "synthetic_review_requested"),
        ("synthetic_review_requested", "reject", "rejected_closed"),
        ("synthetic_review_requested", "expire", "expired_closed"),
        ("synthetic_review_requested", "revoke", "revoked_closed"),
        ("synthetic_review_in_progress", "identity_drift", "re_preflight_required"),
        ("synthetic_review_in_progress", "schema_or_season_drift", "re_preflight_required"),
        ("synthetic_review_complete_disabled", "evidence_drift", "re_preflight_required"),
    }
    if not required.issubset(keys):
        raise ApprovalStateMachineError("required fail-closed transitions missing")

    expected_terminal = {
        "re_preflight_required",
        "rejected_closed",
        "expired_closed",
        "revoked_closed",
    }
    if set(machine.get("terminalStateRules", {})) != expected_terminal:
        raise ApprovalStateMachineError("terminal state rules changed")
    if machine.get("executionBoundary") != SAFE_MACHINE_BOUNDARY:
        raise ApprovalStateMachineError("execution boundary changed")


def validate_matrix(matrix: dict[str, Any]) -> None:
    if matrix.get("schemaVersion") != "preseason-change-control-matrix-v1":
        raise ApprovalStateMachineError("unexpected change-control schema")
    if matrix.get("defaultAction") != "fail_closed_manual_review":
        raise ApprovalStateMachineError("default action must fail closed")

    changes = matrix.get("changes", [])
    fields = [row["field"] for row in changes]
    if len(fields) != 16 or len(fields) != len(set(fields)):
        raise ApprovalStateMachineError("change-control fields changed")
    by_field = {row["field"]: row for row in changes}

    if set(matrix.get("requiredRePreflightFields", [])) != REQUIRED_REPREFLIGHT_FIELDS:
        raise ApprovalStateMachineError("re-preflight field set changed")
    for field in REQUIRED_REPREFLIGHT_FIELDS:
        if by_field[field]["action"] != "re_preflight_required":
            raise ApprovalStateMachineError("identity drift must require re-preflight")
        if by_field[field]["invalidateOwnerPacket"] is not True:
            raise ApprovalStateMachineError("identity drift must invalidate owner packet")

    if by_field["preflight.checksPassed"]["action"] != "rejected_closed":
        raise ApprovalStateMachineError("quality regression must reject")
    if by_field["preflight.failedChecks"]["action"] != "rejected_closed":
        raise ApprovalStateMachineError("failed checks must reject")
    if by_field["preflight.artifact.id"]["action"] != "new_owner_review_packet_required":
        raise ApprovalStateMachineError("artifact change must require new packet")
    if by_field["preflight.artifact.digest"]["action"] != "new_owner_review_packet_required":
        raise ApprovalStateMachineError("artifact digest change must require new packet")
    if by_field["review.ageDays"].get("threshold") != 14:
        raise ApprovalStateMachineError("review expiry threshold changed")
    if by_field["ownerDecision.rejected"]["action"] != "rejected_closed":
        raise ApprovalStateMachineError("owner rejection must close")
    if by_field["ownerDecision.revoked"]["action"] != "revoked_closed":
        raise ApprovalStateMachineError("owner revocation must close")
    if by_field["executionBoundary"]["action"] != "revoked_closed":
        raise ApprovalStateMachineError("boundary drift must revoke")
    for field in ("approvedDatabasePath", "backupId"):
        if by_field[field]["action"] != "separate_future_request_required":
            raise ApprovalStateMachineError("production references require future request")

    if set(matrix.get("prohibitedV020Activations", [])) != PROHIBITED_ACTIVATIONS:
        raise ApprovalStateMachineError("prohibited activation set changed")

    expected_boundary = {
        "fixtureOnly": True,
        "approvalRequested": False,
        "approvalRecorded": False,
        "approvalGranted": False,
        "executionEnabled": False,
        "maximumExecutionCount": 0,
        "externalFilesRead": False,
        "productionDatabaseTouched": False,
        "productionScheduleImported": False,
        "networkCallsMade": False,
        "scheduledCollection": False,
        "canonicalEventIdsCreated": 0,
        "crossRepositoryWrite": False,
        "rowLevelRecordsEmitted": False,
    }
    if matrix.get("boundary") != expected_boundary:
        raise ApprovalStateMachineError("matrix boundary changed")


def evaluate_change(matrix: dict[str, Any], field: str, value: Any = True) -> str:
    by_field = {row["field"]: row for row in matrix["changes"]}
    if field == "review.ageDays":
        threshold = by_field[field]["threshold"]
        return "expired_closed" if int(value) > threshold else "no_change"
    row = by_field.get(field)
    return row["action"] if row else matrix["defaultAction"]


def build_report(root: Path) -> dict[str, Any]:
    machine = _load(root, "config/preseason-approval-state-machine-v1.json")
    matrix = _load(root, "config/preseason-change-control-matrix-v1.json")
    packet = _load(root, "config/preseason-owner-review-packet-v1.json")
    plan = _load(root, "config/disabled-manual-import-command-plan-v1.json")

    validate_machine(machine)
    validate_matrix(matrix)

    transitions = _transition_keys(machine)
    fields = {row["field"]: row for row in matrix["changes"]}
    packet_boundary = packet["executionBoundary"]
    plan_boundary = plan["executionBoundary"]

    scenarios = {
        "unchanged_evidence": "no_change",
        "file_sha_drift": evaluate_change(matrix, "targetFile.sha256"),
        "schema_drift": evaluate_change(matrix, "targetFile.schemaVersion"),
        "quality_regression": evaluate_change(matrix, "preflight.failedChecks"),
        "review_age_14_days": evaluate_change(matrix, "review.ageDays", 14),
        "review_age_15_days": evaluate_change(matrix, "review.ageDays", 15),
        "owner_rejection": evaluate_change(matrix, "ownerDecision.rejected"),
        "owner_revocation": evaluate_change(matrix, "ownerDecision.revoked"),
        "boundary_drift": evaluate_change(matrix, "executionBoundary"),
        "unknown_change": evaluate_change(matrix, "unknown.field"),
    }

    checks = {
        "machine_schema": machine["schemaVersion"] == "preseason-approval-state-machine-v1",
        "matrix_schema": matrix["schemaVersion"] == "preseason-change-control-matrix-v1",
        "source_packet_bound": machine["sourcePacketId"] == packet["packetId"] == matrix["sourcePacketId"],
        "command_plan_bound": plan["sourcePacketId"] == packet["packetId"],
        "initial_state_disabled": machine["initialState"] == "review_ready_disabled",
        "current_state_disabled": machine["currentState"] == "review_ready_disabled",
        "approval_not_requested": machine["approvalRequested"] is False,
        "approval_not_recorded": machine["approvalRecorded"] is False,
        "approval_not_granted": machine["approvalGranted"] is False,
        "execution_disabled": machine["executionEnabled"] is False,
        "maximum_execution_zero": machine["maximumExecutionCount"] == 0,
        "state_set_exact": set(machine["states"]) == EXPECTED_STATES,
        "state_names_unique": len(machine["states"]) == len(set(machine["states"])),
        "transition_count_exact": len(machine["allowedTransitions"]) == 15,
        "transitions_unique": len(transitions) == 15,
        "transition_sources_known": all(row[0] in EXPECTED_STATES for row in transitions),
        "transition_targets_known": all(row[2] in EXPECTED_STATES for row in transitions),
        "no_approval_or_execution_state": not any("approved" in value or "execut" in value for value in machine["states"]),
        "rejection_transition_present": ("synthetic_review_requested", "reject", "rejected_closed") in transitions,
        "expiry_transition_present": ("synthetic_review_requested", "expire", "expired_closed") in transitions,
        "revocation_transition_present": ("synthetic_review_requested", "revoke", "revoked_closed") in transitions,
        "identity_drift_repreflight": ("synthetic_review_in_progress", "identity_drift", "re_preflight_required") in transitions,
        "schema_drift_repreflight": ("synthetic_review_in_progress", "schema_or_season_drift", "re_preflight_required") in transitions,
        "terminal_rules_complete": set(machine["terminalStateRules"]) == {"re_preflight_required", "rejected_closed", "expired_closed", "revoked_closed"},
        "matrix_fields_unique": len(fields) == len(matrix["changes"]) == 16,
        "repreflight_fields_complete": set(matrix["requiredRePreflightFields"]) == REQUIRED_REPREFLIGHT_FIELDS,
        "identity_actions_repreflight": all(fields[name]["action"] == "re_preflight_required" for name in REQUIRED_REPREFLIGHT_FIELDS),
        "identity_changes_invalidate_packet": all(fields[name]["invalidateOwnerPacket"] is True for name in REQUIRED_REPREFLIGHT_FIELDS),
        "quality_failure_rejects": fields["preflight.failedChecks"]["action"] == "rejected_closed",
        "evidence_change_requires_new_packet": fields["preflight.artifact.digest"]["action"] == "new_owner_review_packet_required",
        "expiry_threshold_14": fields["review.ageDays"]["threshold"] == 14,
        "owner_rejection_closes": fields["ownerDecision.rejected"]["action"] == "rejected_closed",
        "owner_revocation_closes": fields["ownerDecision.revoked"]["action"] == "revoked_closed",
        "boundary_drift_revokes": fields["executionBoundary"]["action"] == "revoked_closed",
        "production_references_future_only": all(fields[name]["action"] == "separate_future_request_required" for name in ("approvedDatabasePath", "backupId")),
        "prohibited_activations_complete": set(matrix["prohibitedV020Activations"]) == PROHIBITED_ACTIVATIONS,
        "fixture_only": machine["executionBoundary"]["fixtureOnly"] is True and matrix["boundary"]["fixtureOnly"] is True,
        "no_external_files": machine["executionBoundary"]["externalFileAllowed"] is False and matrix["boundary"]["externalFilesRead"] is False,
        "no_production_database": machine["executionBoundary"]["productionDatabaseAllowed"] is False and matrix["boundary"]["productionDatabaseTouched"] is False,
        "no_production_import": machine["executionBoundary"]["productionImportAllowed"] is False and matrix["boundary"]["productionScheduleImported"] is False,
        "no_network": machine["executionBoundary"]["networkCallsAllowed"] is False and matrix["boundary"]["networkCallsMade"] is False,
        "no_scheduled_collection": machine["executionBoundary"]["scheduledCollectionAllowed"] is False and matrix["boundary"]["scheduledCollection"] is False,
        "no_canonical_ids": machine["executionBoundary"]["canonicalEventIdCreationAllowed"] is False and matrix["boundary"]["canonicalEventIdsCreated"] == 0,
        "no_cross_repository_write": machine["executionBoundary"]["crossRepositoryWriteAllowed"] is False and matrix["boundary"]["crossRepositoryWrite"] is False,
        "no_row_level_records": machine["executionBoundary"]["rowLevelRecordsAllowed"] is False and matrix["boundary"]["rowLevelRecordsEmitted"] is False,
        "no_shell_command": machine["executionBoundary"]["shellCommandAllowed"] is False and plan["shellCommandEmitted"] is False,
        "no_implementation_module": machine["executionBoundary"]["implementationModuleAllowed"] is False and plan["implementationModulePresent"] is False,
        "source_packet_not_approval": packet["ownerDecision"]["decisionRequested"] is False and packet["ownerDecision"]["approvalGranted"] is False,
        "source_packet_fixture_only": packet_boundary["fixtureOnly"] is True and packet_boundary["executionEnabled"] is False,
        "command_plan_non_executable": plan["state"] == "disabled_non_executable" and plan["executable"] is False,
        "command_plan_boundary_safe": plan_boundary["fixtureOnly"] is True and plan_boundary["maximumExecutionCount"] == 0,
        "scenario_sha_repreflight": scenarios["file_sha_drift"] == "re_preflight_required",
        "scenario_schema_repreflight": scenarios["schema_drift"] == "re_preflight_required",
        "scenario_quality_rejected": scenarios["quality_regression"] == "rejected_closed",
        "scenario_age_14_unchanged": scenarios["review_age_14_days"] == "no_change",
        "scenario_age_15_expired": scenarios["review_age_15_days"] == "expired_closed",
        "scenario_owner_rejected": scenarios["owner_rejection"] == "rejected_closed",
        "scenario_owner_revoked": scenarios["owner_revocation"] == "revoked_closed",
        "scenario_boundary_revoked": scenarios["boundary_drift"] == "revoked_closed",
        "scenario_unknown_fails_closed": scenarios["unknown_change"] == "fail_closed_manual_review",
    }

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "schemaVersion": "preseason-approval-state-machine-report-v1",
        "asOf": machine["asOf"],
        "formalState": READY if not failed else "APPROVAL_STATE_MACHINE_VALIDATION_FAILED",
        "checks": checks,
        "checksPassed": sum(checks.values()),
        "checksTotal": len(checks),
        "failedChecks": failed,
        "machine": {
            "machineId": machine["machineId"],
            "sourcePacketId": machine["sourcePacketId"],
            "currentState": machine["currentState"],
            "stateCount": len(machine["states"]),
            "transitionCount": len(machine["allowedTransitions"]),
            "terminalStateCount": len(machine["terminalStateRules"]),
            "maxReviewAgeDays": machine["reviewPolicy"]["maxReviewAgeDays"],
        },
        "matrix": {
            "matrixId": matrix["matrixId"],
            "changeRuleCount": len(matrix["changes"]),
            "rePreflightFieldCount": len(matrix["requiredRePreflightFields"]),
            "prohibitedActivationCount": len(matrix["prohibitedV020Activations"]),
            "defaultAction": matrix["defaultAction"],
        },
        "scenarios": scenarios,
        "boundary": matrix["boundary"],
    }
