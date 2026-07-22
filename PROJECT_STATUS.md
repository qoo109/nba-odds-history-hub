# Project Status

Updated: 2026-07-22

## Current phase

**V0.20 — Fixture-only approval state machine and fail-closed change-control matrix ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.20 merge: f7b9bda017bd2b1111dfcb6eb9720aeca5849295
current mode: offseason_sleep
scheduled collection: false
manual Phase 2 approval granted: false
approval requested: false
approval recorded: false
approval granted: false
manual schedule execution enabled: false
maximum schedule execution count: 0
production schedule imported: false
production database touched: false
external schedule read: false
real snapshots: 1
movement-ready quote identities: 0
```

## Completed through V0.20

- Import, normalized storage, exports and tests
- First snapshot dashboard and grouped history builder
- Daily public-source health checks
- Disabled one-time Phase 2 request packet
- Canonical teams, market taxonomy and dormant cadence templates
- Schedule-import contract and deterministic mapping fixtures
- Additive schedule-version and mapping-audit database layer
- Explicit source and provider metadata
- Fixture-only schedule output gate
- Aggregate readiness export and dashboard
- Public release manifest, JSON Schema declarations and checksums
- Static release index and deterministic drift report
- Synthetic preseason configuration and two-observation dry run
- Three-stage manual schedule preflight with mandatory rollback and zero-row post-check
- Aggregate owner-review packet and six-step non-executable control plan
- Fixture-only approval state machine with rejection, expiry, revocation and re-preflight transitions
- Sixteen-rule change-control matrix with fail-closed unknown-change handling

## V0.20 validation evidence

```text
formal state: OFFSEASON_PRESEASON_APPROVAL_STATE_MACHINE_AND_CHANGE_CONTROL_MATRIX_V1_READY
merge commit: f7b9bda017bd2b1111dfcb6eb9720aeca5849295
pull request: #43
focused workflow run: 29935044320
full test workflow run: 29935042766
owner-review workflow run: 29935043529
manual-preflight workflow run: 29935042714
preseason workflow run: 29935042773
public-schema workflow run: 29935043676
artifact id: 8535722355
artifact digest: sha256:d9503f85b5081c5cdbb62ea07d164ad30b76be9212712fd61250bbed0c21bc04
checks: 60 / 60
all workflows: success
```

Published assets:

```text
config/preseason-approval-state-machine-v1.json
config/preseason-change-control-matrix-v1.json
src/nba_odds_history_hub/approval_state_machine.py
scripts/validate_approval_state_machine_v1.py
tests/test_approval_state_machine_v1.py
docs/preseason-approval-state-machine-v1.md
.github/workflows/validate-approval-state-machine-v1.yml
```

## Approval state machine

```text
machine id: SCHEDULE-APPROVAL-STATE-MACHINE-2026-07-21-001
source packet: SCHEDULE-OWNER-REVIEW-2026-07-21-001
current state: review_ready_disabled
states: 8
allowed transitions: 15
terminal states: 4
maximum review age: 14 days
approval requested: false
approval recorded: false
approval granted: false
execution enabled: false
```

States:

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

## Change-control matrix

```text
matrix id: SCHEDULE-CHANGE-CONTROL-2026-07-21-001
change rules: 16
re-preflight identity fields: 6
prohibited activation fields: 11
default unknown-change action: fail_closed_manual_review
```

The following fields always require a new preflight and invalidate the current owner-review packet:

```text
targetFile.path
targetFile.filename
targetFile.bytes
targetFile.sha256
targetFile.schemaVersion
targetFile.seasonId
```

Fail-closed outcomes:

```text
file identity drift -> re_preflight_required
schema or season drift -> re_preflight_required
quality failure -> rejected_closed
review age above 14 days -> expired_closed
owner rejection -> rejected_closed
owner revocation -> revoked_closed
execution-boundary drift -> revoked_closed
unknown change -> fail_closed_manual_review
```

Artifact identity changes require a new owner-review packet. Production database and backup references remain separate-future-request inputs and do not activate execution.

## Preserved review and rollback evidence

```text
owner-review packet: SCHEDULE-OWNER-REVIEW-2026-07-21-001
owner-review state: review_ready_disabled
preflight request: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
preflight checks: 19 / 19
target path: data/fixtures/preseason-dry-run-v1.json
target bytes: 2204
target sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
rollback executed: true
post-rollback total rows: 0
```

The disabled command plan remains non-executable:

```text
plan id: SCHEDULE-IMPORT-COMMAND-PLAN-2026-07-21-001
shell command emitted: false
implementation module present: false
execution count: 0
```

## Current real-data state

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
multi-observation history ready: false
production schedule imported: false
external schedule read: false
```

## Phase 2 request

```text
request id: ODDS-PHASE2-CAPTURE-2026-07-21-001
request state: awaiting explicit owner approval
approval granted: false
execution enabled: false
execution count: 0
maximum execution count: 1
```

The Phase 2 request remains inactive during the offseason.

## Next unique mainline

```text
OFFSEASON_PRESEASON_DISABLED_IMPORT_REQUEST_CONTRACT_AND_BACKUP_RESTORE_FIXTURES
```

The next safe task is to define a disabled import-request contract and synthetic backup/restore fixtures. It may bind only repository synthetic file identities and a temporary SQLite database. It must not request or record owner approval, emit a runnable production command, read an external schedule, access a production database, enable recurring collection or write to another repository.

## Safety boundary

- No access-control or website-policy bypass.
- No external schedule retrieval in V0.20.
- No production database access in V0.20.
- No production schedule import in V0.20.
- No scheduled collection during offseason sleep mode.
- No canonical event ID creation.
- No row-level approval artifact.
- No runnable import command or production implementation module.
- No automatic write to `qoo109/nba-value-lab`.
