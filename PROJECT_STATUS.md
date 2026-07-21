# Project Status

Updated: 2026-07-21

## Current phase

**V0.17 — Preseason schedule dry-run gate ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.17 merge: e17854f1f2bf516f66808eabcec063028fa4a400
current mode: offseason_sleep
scheduled collection: false
manual Phase 2 approval granted: false
production schedule imported: false
external schedule read: false
real snapshots: 1
movement-ready quote identities: 0
```

## Completed through V0.17

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

## V0.17 validation evidence

```text
formal state: OFFSEASON_PRESEASON_ACTIVATION_GATE_AND_DRY_RUN_FIXTURES_V1_READY
merge commit: e17854f1f2bf516f66808eabcec063028fa4a400
pull request: #37
focused workflow run: 29842819060
full test workflow run: 29842819689
public-schema workflow run: 29842820112
artifact id: 8500060347
artifact digest: sha256:617421e5dfa2039cbee79c25c28dedf3055eba21eec0f0cadd78d219e1f35021
checks: 15 / 15
all workflows: success
```

Published assets:

```text
config/preseason-readiness-v1.json
config/season-configuration-v1.json
data/fixtures/preseason-dry-run-v1.json
data/preseason-dry-run-current-status-v1.json
src/nba_odds_history_hub/preseason_dry_run.py
scripts/validate_preseason_dry_run_v1.py
tests/test_preseason_dry_run_v1.py
tests/test_preseason_dry_run_status_v1.py
docs/preseason-dry-run-v1.md
.github/workflows/validate-preseason-dry-run-v1.yml
```

## Dry-run result

```text
observations: 2
accepted rows: 5
excluded rows: 2
source events: 3
schedule versions: 5
current schedules: 3
audit decisions: 5
schedule identity changes: 1
payload-only revisions: 1
idempotent replay rows: 3
multiple current schedule groups: 0
canonical event IDs created: 0
production rows written: 0
```

State sequence:

```text
offseason_sleep
-> preseason_dry_run_config_valid
-> preseason_dry_run_partial
-> preseason_dry_run_ready_awaiting_owner_approval
```

The final state is a simulated readiness state. It does not authorize external retrieval, production import or recurring collection.

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

The request remains inactive during the offseason.

## Next unique mainline

```text
OFFSEASON_PRESEASON_MANUAL_SCHEDULE_IMPORT_PREFLIGHT_AND_ROLLBACK_CONTRACT
```

The next safe task is to define a disabled, owner-reviewed manual schedule import preflight with exact file identity, schema checks, aggregate preview, transaction rollback and post-import verification. It must use synthetic fixtures until a separate explicit approval is provided and must not retrieve an external schedule or enable recurring collection.

## Safety boundary

- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.17.
- No scheduled collection during offseason sleep mode.
- No production schedule import without separate explicit owner approval.
