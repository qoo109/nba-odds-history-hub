"""Fixture-only disabled import request and temporary SQLite backup/restore checks.

The module binds one committed synthetic schedule identity to a disabled request,
creates only a temporary SQLite database, proves that a byte-for-byte backup can
restore aggregate fixture state, and never exposes a production import command.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .database import connect_database, initialize_database
from .manual_schedule_preflight import validate_file_identity

READY = "OFFSEASON_PRESEASON_DISABLED_IMPORT_REQUEST_CONTRACT_AND_BACKUP_RESTORE_FIXTURES_V1_READY"
INVALID = "OFFSEASON_PRESEASON_DISABLED_IMPORT_REQUEST_CONTRACT_AND_BACKUP_RESTORE_FIXTURES_V1_INVALID"

SAFE_BOUNDARY = {
    "fixtureOnly": True,
    "repositoryFixtureIdentityOnly": True,
    "temporaryDatabaseOnly": True,
    "externalFileAllowed": False,
    "productionDatabaseAllowed": False,
    "productionImportAllowed": False,
    "networkCallsAllowed": False,
    "scheduledCollectionAllowed": False,
    "canonicalEventIdCreationAllowed": False,
    "crossRepositoryWriteAllowed": False,
    "rowLevelRecordsAllowed": False,
    "shellCommandAllowed": False,
    "productionImplementationModuleAllowed": False,
}

EXPECTED_COUNT_KEYS = {
    "dataSources",
    "sourceEvents",
    "scheduleVersions",
    "currentSchedules",
    "mappingAuditDecisions",
    "canonicalEvents",
    "rawImports",
    "oddsSnapshots",
}


class DisabledImportRequestError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DisabledImportRequestError(f"{path} must contain one JSON object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("schemaVersion") != "disabled-import-request-contract-v1":
        raise DisabledImportRequestError("unexpected disabled import request schema")
    if contract.get("state") != "draft_disabled_fixture_only":
        raise DisabledImportRequestError("request must remain draft and disabled")
    if contract.get("requestType") != "synthetic_disabled_import_request":
        raise DisabledImportRequestError("request type must remain synthetic")
    for field in (
        "approvalRequested",
        "approvalRecorded",
        "approvalGranted",
        "executionEnabled",
    ):
        if contract.get(field) is not False:
            raise DisabledImportRequestError(f"{field} must remain false")
    if contract.get("maximumExecutionCount") != 0:
        raise DisabledImportRequestError("maximum execution count must remain zero")
    if contract.get("executionBoundary") != SAFE_BOUNDARY:
        raise DisabledImportRequestError("disabled execution boundary changed")

    references = contract.get("productionReferences") or {}
    if references.get("approvedDatabasePath") is not None:
        raise DisabledImportRequestError("production database path is prohibited")
    if references.get("backupId") is not None:
        raise DisabledImportRequestError("production backup id is prohibited")
    if references.get("separateFutureRequestRequired") is not True:
        raise DisabledImportRequestError("production references require a future request")

    fixture = contract.get("backupRestoreFixture") or {}
    if fixture.get("workspaceMode") != "temporary_directory_only":
        raise DisabledImportRequestError("backup restore workspace must be temporary only")
    for name in ("databaseFilename", "backupFilename"):
        value = Path(str(fixture.get(name, "")))
        if not value.name or value.is_absolute() or len(value.parts) != 1:
            raise DisabledImportRequestError(f"{name} must be a plain temporary filename")
    seed = fixture.get("expectedSeedCounts") or {}
    mutation = fixture.get("expectedMutationCounts") or {}
    if set(seed) != EXPECTED_COUNT_KEYS or set(mutation) != EXPECTED_COUNT_KEYS:
        raise DisabledImportRequestError("backup restore count keys changed")
    if any(int(seed[key]) < 0 or int(mutation[key]) < 0 for key in EXPECTED_COUNT_KEYS):
        raise DisabledImportRequestError("backup restore counts must be non-negative")
    if int(fixture.get("seedSourceEventId", 0)) == int(fixture.get("mutationSourceEventId", 0)):
        raise DisabledImportRequestError("seed and mutation event ids must differ")


def _table_count(connection: Any, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _counts(database: Path) -> dict[str, int]:
    with connect_database(database) as connection:
        return {
            "dataSources": _table_count(connection, "data_sources"),
            "sourceEvents": _table_count(connection, "source_events"),
            "scheduleVersions": _table_count(connection, "source_event_schedule_versions"),
            "currentSchedules": int(
                connection.execute(
                    "SELECT COUNT(*) FROM source_event_schedule_versions WHERE is_current = 1"
                ).fetchone()[0]
            ),
            "mappingAuditDecisions": _table_count(connection, "source_event_mapping_audit"),
            "canonicalEvents": _table_count(connection, "canonical_events"),
            "rawImports": _table_count(connection, "raw_imports"),
            "oddsSnapshots": _table_count(connection, "odds_snapshots"),
        }


def _insert_event(connection: Any, event_id: int, created_at: str, note: str) -> None:
    observed_at = f"{created_at[:10]}T12:00:00+00:00"
    scheduled_tipoff = f"{created_at[:10]}T23:00:00+00:00"
    payload_sha256 = hashlib.sha256(f"synthetic:{event_id}".encode("utf-8")).hexdigest()
    connection.execute(
        """
        INSERT INTO source_events (
            source_id, source_event_id, league, event_type, title,
            scheduled_tipoff, canonical_event_id, mapping_status,
            first_observed_at, last_observed_at
        ) VALUES (?, ?, 'NBA', 'game', 'synthetic backup restore fixture', ?, NULL,
                  'candidate_unverified', ?, ?)
        """,
        (
            "fixture_disabled_import_request",
            event_id,
            scheduled_tipoff,
            observed_at,
            observed_at,
        ),
    )
    connection.execute(
        """
        INSERT INTO source_event_schedule_versions (
            source_id, source_event_id, version_number, scheduled_tipoff,
            home_team_abbr, away_team_abbr, mapping_status, mapping_method,
            observed_at, source_payload_sha256, is_current, created_at
        ) VALUES (?, ?, 1, ?, 'BOS', 'NYK', 'candidate_unverified',
                  'synthetic_backup_restore_fixture', ?, ?, 1, ?)
        """,
        (
            "fixture_disabled_import_request",
            event_id,
            scheduled_tipoff,
            observed_at,
            payload_sha256,
            created_at,
        ),
    )
    connection.execute(
        """
        INSERT INTO source_event_mapping_audit (
            source_id, source_event_id, canonical_event_id, previous_status,
            new_status, mapping_method, reason_code, actor_type, decided_at,
            source_payload_sha256, note, created_at
        ) VALUES (?, ?, NULL, 'candidate_unverified', 'candidate_unverified',
                  'synthetic_backup_restore_fixture', 'disabled_import_request_fixture',
                  'synthetic_fixture', ?, ?, ?, ?)
        """,
        (
            "fixture_disabled_import_request",
            event_id,
            observed_at,
            payload_sha256,
            note,
            created_at,
        ),
    )


def run_backup_restore_fixture(workspace: Path, contract: dict[str, Any]) -> dict[str, Any]:
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    fixture = contract["backupRestoreFixture"]
    database = workspace / fixture["databaseFilename"]
    backup = workspace / fixture["backupFilename"]
    created_at = f"{contract['asOf']}T00:00:00+00:00"

    initialize_database(database)
    with connect_database(database) as connection:
        connection.execute(
            """
            INSERT INTO data_sources (
                source_id, display_name, source_class, access_mode, usage_boundary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "fixture_disabled_import_request",
                "Synthetic disabled import request",
                "synthetic_fixture",
                "fixture_only",
                "Temporary backup/restore validation only.",
                created_at,
            ),
        )
        _insert_event(
            connection,
            int(fixture["seedSourceEventId"]),
            created_at,
            "seed state retained by synthetic backup",
        )

    seed_counts = _counts(database)
    seed_sha256 = _sha256(database)
    shutil.copyfile(database, backup)
    backup_sha256 = _sha256(backup)

    with connect_database(database) as connection:
        _insert_event(
            connection,
            int(fixture["mutationSourceEventId"]),
            created_at,
            "mutation state must disappear after restore",
        )

    mutation_counts = _counts(database)
    mutation_sha256 = _sha256(database)
    shutil.copyfile(backup, database)
    restored_counts = _counts(database)
    restored_sha256 = _sha256(database)

    return {
        "workspaceMode": "temporary_directory_only",
        "databaseCreated": database.is_file(),
        "backupCreated": backup.is_file(),
        "seedCounts": seed_counts,
        "mutationCounts": mutation_counts,
        "restoredCounts": restored_counts,
        "seedDatabaseSha256": seed_sha256,
        "backupSha256": backup_sha256,
        "mutationDatabaseSha256": mutation_sha256,
        "restoredDatabaseSha256": restored_sha256,
        "seedBackupBytesMatch": seed_sha256 == backup_sha256,
        "mutationChangedDatabase": mutation_sha256 != backup_sha256,
        "restoreBytesMatchBackup": restored_sha256 == backup_sha256,
        "productionDatabaseTouched": False,
        "externalFilesRead": False,
        "networkCallsMade": False,
        "rowLevelRecordsEmitted": False,
    }


def build_report(root: Path, workspace: Path) -> dict[str, Any]:
    root = root.resolve()
    workspace = workspace.resolve()
    if workspace == root or workspace.is_relative_to(root):
        raise DisabledImportRequestError("workspace must remain outside the repository")

    contract = _load(root / "config/disabled-import-request-contract-v1.json")
    machine = _load(root / "config/preseason-approval-state-machine-v1.json")
    packet = _load(root / "config/preseason-owner-review-packet-v1.json")
    validate_contract(contract)
    _, _, identity = validate_file_identity(root, contract)
    backup_restore = run_backup_restore_fixture(workspace, contract)
    fixture = contract["backupRestoreFixture"]

    checks = {
        "contract_schema": contract["schemaVersion"] == "disabled-import-request-contract-v1",
        "state_disabled": contract["state"] == "draft_disabled_fixture_only",
        "state_machine_bound": contract["sourceStateMachineId"] == machine["machineId"],
        "owner_packet_bound": contract["sourcePacketId"] == packet["packetId"],
        "source_machine_disabled": machine["currentState"] == "review_ready_disabled",
        "source_packet_disabled": packet["state"] == "review_ready_disabled",
        "approval_not_requested": contract["approvalRequested"] is False,
        "approval_not_recorded": contract["approvalRecorded"] is False,
        "approval_not_granted": contract["approvalGranted"] is False,
        "execution_disabled": contract["executionEnabled"] is False,
        "maximum_execution_zero": contract["maximumExecutionCount"] == 0,
        "target_file_identity_exact": identity == contract["targetFile"],
        "temporary_database_only": contract["executionBoundary"]["temporaryDatabaseOnly"] is True,
        "production_references_empty": all(
            contract["productionReferences"][name] is None
            for name in ("approvedDatabasePath", "backupId")
        ),
        "seed_counts_exact": backup_restore["seedCounts"] == fixture["expectedSeedCounts"],
        "mutation_counts_exact": backup_restore["mutationCounts"] == fixture["expectedMutationCounts"],
        "restored_counts_exact": backup_restore["restoredCounts"] == fixture["expectedSeedCounts"],
        "backup_created": backup_restore["backupCreated"],
        "seed_backup_bytes_match": backup_restore["seedBackupBytesMatch"],
        "mutation_changed_database": backup_restore["mutationChangedDatabase"],
        "restore_bytes_match_backup": backup_restore["restoreBytesMatchBackup"],
        "no_canonical_ids": backup_restore["restoredCounts"]["canonicalEvents"] == 0,
        "no_market_rows": (
            backup_restore["restoredCounts"]["rawImports"] == 0
            and backup_restore["restoredCounts"]["oddsSnapshots"] == 0
        ),
        "no_external_files": backup_restore["externalFilesRead"] is False,
        "no_production_database": backup_restore["productionDatabaseTouched"] is False,
        "no_network": backup_restore["networkCallsMade"] is False,
        "no_row_level_output": backup_restore["rowLevelRecordsEmitted"] is False,
        "no_shell_command": contract["executionBoundary"]["shellCommandAllowed"] is False,
        "no_production_module": contract["executionBoundary"]["productionImplementationModuleAllowed"] is False,
        "no_scheduled_collection": contract["executionBoundary"]["scheduledCollectionAllowed"] is False,
        "no_cross_repository_write": contract["executionBoundary"]["crossRepositoryWriteAllowed"] is False,
    }
    failed = sorted(name for name, value in checks.items() if not value)
    return {
        "schemaVersion": "disabled-import-request-contract-report-v1",
        "asOf": contract["asOf"],
        "requestId": contract["requestId"],
        "formalState": READY if not failed else INVALID,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "failedChecks": failed,
        "targetFileIdentity": identity,
        "backupRestore": backup_restore,
        "approval": {
            "requested": False,
            "recorded": False,
            "granted": False,
            "executionEnabled": False,
            "executionCount": 0,
        },
        "boundary": {
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
        },
    }
