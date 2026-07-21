# Project Status

Updated: 2026-07-21

## Current phase

**V0.18 — Three-stage manual schedule import preflight and rollback rehearsal ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.18 merge: 6b9cc5e62bb7922d62d10b6315836838fa95dd1d
current mode: offseason_sleep
scheduled collection: false
manual Phase 2 approval granted: false
manual schedule preflight approval granted: false
manual schedule execution enabled: false
production schedule imported: false
external schedule read: false
real snapshots: 1
movement-ready quote identities: 0
```

## Completed through V0.18

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

## V0.18 validation evidence

```text
formal state: OFFSEASON_PRESEASON_MANUAL_SCHEDULE_IMPORT_PREFLIGHT_AND_ROLLBACK_V1_READY
merge commit: 6b9cc5e62bb7922d62d10b6315836838fa95dd1d
pull request: #39
focused workflow run: 29845051057
full test workflow run: 29845050863
preseason workflow run: 29845050942
public-schema workflow run: 29845051009
artifact id: 8500959742
artifact digest: sha256:cd398c5a3bba096b1f5ba392bb47c8afff766be66a2d955a267d0360bfd4d654
checks: 19 / 19
all workflows: success
```

Published assets:

```text
config/manual-schedule-import-preflight-v1.json
data/manual-schedule-import-preflight-current-status-v1.json
src/nba_odds_history_hub/manual_schedule_preflight.py
scripts/validate_manual_schedule_preflight_v1.py
tests/test_manual_schedule_preflight_v1.py
docs/manual-schedule-import-preflight-v1.md
.github/workflows/validate-manual-schedule-preflight-v1.yml
```

## Three completed stages

### Stage 1 — Identity and schema preflight

```text
target path: data/fixtures/preseason-dry-run-v1.json
filename: preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
schema: preseason-dry-run-fixture-v1
season: 2026-27
result: pass
```

Path, filename, byte count, SHA-256, schema version and season ID are exact and fail closed on drift.

### Stage 2 — Aggregate preview

```text
observations: 2
accepted rows: 5
excluded rows: 2
unique accepted events: 3
unknown alias exclusions: 1
same-team exclusions: 1
row-level excluded records emitted: false
result: pass
```

### Stage 3 — Transaction rollback and post-check

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

After rollback:

```text
data sources: 0
source events: 0
schedule versions: 0
current schedules: 0
mapping audit decisions: 0
canonical events: 0
raw imports: 0
odds snapshots: 0
result: pass
```

## Approval and execution state

```text
request id: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
request state: disabled_preapproval
owner approval granted: false
execution enabled: false
maximum execution count: 0
execution count: 0
production import executed: false
post-import verification: not_applicable_preapproval
```

V0.18 validates the safety path only. It does not create a runnable production import request.

## Preserved governance state

```text
public contract drift count: 0
JSON Schema declarations: 3
integrity assets: 8
integrity algorithm: sha256
teams: 30
market classes: 11
metadata missing fields: 0
automation approvals: 0
active cadence templates: 0
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
OFFSEASON_PRESEASON_OWNER_REVIEW_PACKET_AND_DISABLED_IMPORT_COMMAND_PLAN
```

The next safe task is to generate an aggregate owner-review packet and a non-executable manual import command plan that references the exact preflight identity and rollback evidence. It must remain disabled, synthetic-fixture-only and incapable of importing a production schedule without a separate explicit approval.

## Safety boundary

- No access-control or website-policy bypass.
- No external schedule retrieval in V0.18.
- No production database access in V0.18.
- No production schedule import in V0.18.
- No scheduled collection during offseason sleep mode.
- No canonical event ID creation by the preflight.
- No automatic write to `qoo109/nba-value-lab`.
