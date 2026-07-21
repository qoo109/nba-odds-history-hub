# Project Status

Updated: 2026-07-21

## Current phase

**V0.19 — Aggregate owner-review packet and disabled control-step plan ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.19 merge: d4c35b1bcb1001afe0d48b41f1c64f36d5a202e3
current mode: offseason_sleep
scheduled collection: false
manual Phase 2 approval granted: false
owner review decision requested: false
owner review decision recorded: false
owner review approval granted: false
manual schedule execution enabled: false
maximum schedule execution count: 0
production schedule imported: false
external schedule read: false
real snapshots: 1
movement-ready quote identities: 0
```

## Completed through V0.19

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
- Aggregate owner-review packet tied to the exact V0.18 evidence
- Six-step non-executable control plan with unresolved approval, file, database and backup placeholders

## V0.19 validation evidence

```text
formal state: OFFSEASON_PRESEASON_OWNER_REVIEW_PACKET_AND_DISABLED_IMPORT_COMMAND_PLAN_V1_READY
merge commit: d4c35b1bcb1001afe0d48b41f1c64f36d5a202e3
pull request: #41
focused workflow run: 29852455631
full test workflow run: 29852455545
manual preflight workflow run: 29852455102
preseason workflow run: 29852455129
public-schema workflow run: 29852455323
artifact id: 8503909693
artifact digest: sha256:10e8e2e366b1ceb2b29cb6185d37d29b9d0399cfb968c9404522281b6e0fe3e2
checks: 31 / 31
all workflows: success
```

Published assets:

```text
config/preseason-owner-review-packet-v1.json
config/disabled-manual-import-command-plan-v1.json
data/preseason-owner-review-current-status-v1.json
src/nba_odds_history_hub/owner_review_packet.py
scripts/validate_owner_review_packet_v1.py
tests/test_owner_review_packet_v1.py
docs/preseason-owner-review-packet-v1.md
.github/workflows/validate-owner-review-packet-v1.yml
```

## Owner-review packet

```text
packet id: SCHEDULE-OWNER-REVIEW-2026-07-21-001
state: review_ready_disabled
source preflight request: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
decision requested: false
decision recorded: false
approval granted: false
separate approval request required: true
```

Evidence carried forward:

```text
preflight checks: 19 / 19
target path: data/fixtures/preseason-dry-run-v1.json
target bytes: 2204
target sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
preflight artifact id: 8500959742
preflight artifact digest: sha256:cd398c5a3bba096b1f5ba392bb47c8afff766be66a2d955a267d0360bfd4d654
rollback executed: true
post-rollback total rows: 0
```

The only current review outcomes are `keep_disabled` and `request_new_synthetic_review`. V0.19 does not ask the owner to approve a production import.

## Disabled control-step plan

```text
plan id: SCHEDULE-IMPORT-COMMAND-PLAN-2026-07-21-001
state: disabled_non_executable
representation: ordered_control_steps
control steps: 6
required placeholders: 5
executable: false
shell command emitted: false
implementation module present: false
execution count: 0
```

The six steps describe future controls only:

1. validate aggregate review evidence
2. bind a separate approval request
3. bind an exact approved file identity
4. verify an independent database backup reference
5. describe a transactional import without execution
6. require post-import aggregate checks and a rollback decision

Unresolved placeholders:

```text
SEPARATE_APPROVAL_REQUEST_ID
APPROVED_FILE_PATH
APPROVED_FILE_SHA256
APPROVED_DATABASE_PATH
BACKUP_ID
```

No command string, shell body, argument vector or executable import module is emitted.

## Preserved V0.18 rollback evidence

Inside the temporary transaction:

```text
data sources: 1
source events: 3
schedule versions: 5
current schedules: 3
mapping audit decisions: 5
canonical events: 0
raw imports: 0
odds snapshots: 0
```

After rollback every listed count is zero. Production database access remained false.

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
OFFSEASON_PRESEASON_APPROVAL_STATE_MACHINE_AND_CHANGE_CONTROL_MATRIX
```

The next safe task is to define a fixture-only approval state machine and change-control matrix covering allowed transitions, rejection, expiry, revocation and re-preflight requirements. It must remain non-executable, must not request approval, and must not read an external schedule or touch a production database.

## Safety boundary

- No access-control or website-policy bypass.
- No external schedule retrieval in V0.19.
- No production database access in V0.19.
- No production schedule import in V0.19.
- No scheduled collection during offseason sleep mode.
- No canonical event ID creation.
- No row-level owner-review artifact.
- No automatic write to `qoo109/nba-value-lab`.
