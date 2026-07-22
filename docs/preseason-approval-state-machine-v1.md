# Preseason Approval State Machine and Change Control v1

V0.20 defines a fixture-only, non-executable governance layer for future manual schedule review. It does not request approval, record approval, read an external schedule, touch a production database or enable collection.

## Current state

```text
review_ready_disabled
approval requested: false
approval recorded: false
approval granted: false
execution enabled: false
maximum execution count: 0
```

## States

```text
review_ready_disabled
synthetic_review_requested
synthetic_review_in_progress
synthetic_review_complete_disabled
re_preflight_required
rejected_closed
expired_closed
revoked_closed
```

No approved or executable state exists in V0.20.

## Fail-closed transitions

- file identity drift -> `re_preflight_required`
- schema or season drift -> `re_preflight_required`
- failed quality checks -> `rejected_closed`
- review age above 14 days -> `expired_closed`
- owner rejection -> `rejected_closed`
- owner revocation -> `revoked_closed`
- execution-boundary drift -> `revoked_closed`
- unknown changes -> `fail_closed_manual_review`

## Change-control matrix

Six fields always require a new preflight and invalidate the current owner packet:

```text
targetFile.path
targetFile.filename
targetFile.bytes
targetFile.sha256
targetFile.schemaVersion
targetFile.seasonId
```

Artifact identity changes require a new owner-review packet. Production database and backup references remain future-request-only inputs and do not activate execution.

## Validation

```bash
python scripts/validate_approval_state_machine_v1.py \
  --output runtime/reports/preseason-approval-state-machine-v1.json
```

The report is aggregate-only. It contains no row-level schedule records, shell command, executable import module, production database path or external file content.

## Safety boundary

- synthetic fixture only
- no external file read
- no production database access
- no production schedule import
- no network call
- no scheduled collection
- no canonical event ID creation
- no cross-repository write
- no automatic write to `qoo109/nba-value-lab`
