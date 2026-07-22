# NBA Odds History Hub

A dedicated, auditable repository for preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.20 — Fixture-only approval state machine and fail-closed change-control matrix ready; collection remains asleep.**

The repository currently provides:

1. source-health monitoring for approved free/public sources;
2. canonical NBA team and market reference data;
3. schedule adapter, mapping and versioned SQLite contracts;
4. aggregate readiness exports and public governance checks;
5. synthetic preseason schedule dry runs;
6. a disabled three-stage manual schedule preflight;
7. an aggregate owner-review packet and non-executable six-step control plan;
8. a fixture-only approval state machine and change-control matrix;
9. Phase 2 collection, which remains inactive pending a separate explicit decision.

Nothing in this repository automatically connects to or modifies `qoo109/nba-value-lab`.

## V0.20 approval state machine

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
maximum execution count: 0
```

Available states:

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
re-preflight fields: 6
prohibited activation fields: 11
default action: fail_closed_manual_review
```

These identity fields always require a new preflight and invalidate the current owner-review packet:

```text
targetFile.path
targetFile.filename
targetFile.bytes
targetFile.sha256
targetFile.schemaVersion
targetFile.seasonId
```

Fail-closed behavior:

```text
identity drift -> re_preflight_required
schema or season drift -> re_preflight_required
quality failure -> rejected_closed
review age above 14 days -> expired_closed
owner rejection -> rejected_closed
owner revocation -> revoked_closed
execution-boundary drift -> revoked_closed
unknown change -> fail_closed_manual_review
```

Artifact identity changes require a fresh owner-review packet. Production database and backup references remain future-request-only inputs.

## V0.20 validation

```text
formal state:
OFFSEASON_PRESEASON_APPROVAL_STATE_MACHINE_AND_CHANGE_CONTROL_MATRIX_V1_READY

checks: 60 / 60
focused workflow: 29935044320
full test workflow: 29935042766
owner-review workflow: 29935043529
manual-preflight workflow: 29935042714
preseason workflow: 29935042773
public-schema workflow: 29935043676
artifact: 8535722355
artifact digest:
sha256:d9503f85b5081c5cdbb62ea07d164ad30b76be9212712fd61250bbed0c21bc04
```

## V0.20 assets

```text
config/preseason-approval-state-machine-v1.json
config/preseason-change-control-matrix-v1.json
src/nba_odds_history_hub/approval_state_machine.py
scripts/validate_approval_state_machine_v1.py
tests/test_approval_state_machine_v1.py
docs/preseason-approval-state-machine-v1.md
.github/workflows/validate-approval-state-machine-v1.yml
```

## Preserved V0.19 owner review

```text
packet id: SCHEDULE-OWNER-REVIEW-2026-07-21-001
state: review_ready_disabled
source preflight request: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
decision requested: false
decision recorded: false
approval granted: false
```

The packet references the validated V0.18 evidence:

```text
preflight checks: 19 / 19
path: data/fixtures/preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
rollback executed: true
post-rollback total rows: 0
```

The six-step control plan remains non-executable:

```text
plan id: SCHEDULE-IMPORT-COMMAND-PLAN-2026-07-21-001
executable: false
shell command emitted: false
implementation module present: false
execution count: 0
```

## Current execution boundary

```text
current mode: offseason_sleep
approval requested: false
approval recorded: false
approval granted: false
manual schedule execution enabled: false
maximum schedule execution count: 0
external schedule read: false
production database touched: false
production schedule imported: false
scheduled collection: false
canonical event IDs created: 0
cross-repository write: false
```

## Existing foundation

- `matchups.json` + `straight.json` intake
- American-to-decimal and implied-probability normalization
- separate `observed_at` and `ingested_at`
- SQLite snapshot history and changes-only retention
- source and provider registries
- canonical 30-team registry
- market taxonomy
- schedule-import and mapping contracts
- schedule-version history and mapping audit records
- aggregate readiness dashboard
- public release manifest and static release index
- deterministic drift report
- Draft 2020-12 JSON Schema declarations
- SHA-256 governance asset manifest
- synthetic preseason schedule dry run
- three-stage manual schedule preflight
- aggregate owner-review packet
- fixture-only approval state machine

## Current real-data state

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
production schedule imported: false
external schedule read: false
scheduled collection: false
Phase 2 approval granted: false
```

## Run validation

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Rebuild the V0.20 report:

```bash
python scripts/validate_approval_state_machine_v1.py \
  --output runtime/reports/preseason-approval-state-machine-v1.json
```

Rebuild the V0.19 report:

```bash
python scripts/validate_owner_review_packet_v1.py \
  --output runtime/reports/preseason-owner-review-packet-v1.json
```

## Public status pages

- [`readiness.html`](readiness.html) — aggregate offseason readiness
- [`release-index.html`](release-index.html) — public contract versions and drift status

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`docs/preseason-approval-state-machine-v1.md`](docs/preseason-approval-state-machine-v1.md)
- [`docs/preseason-owner-review-packet-v1.md`](docs/preseason-owner-review-packet-v1.md)
- [`docs/manual-schedule-import-preflight-v1.md`](docs/manual-schedule-import-preflight-v1.md)
- [`docs/preseason-dry-run-v1.md`](docs/preseason-dry-run-v1.md)
- [`docs/public-data-declarations-v1.md`](docs/public-data-declarations-v1.md)
- [`docs/static-release-index-drift-v1.md`](docs/static-release-index-drift-v1.md)
- [`docs/readiness-release-v1.md`](docs/readiness-release-v1.md)
- [`docs/offseason-aggregate-metadata-dashboard-v1.md`](docs/offseason-aggregate-metadata-dashboard-v1.md)
- [`docs/offseason-reference-foundation-v1.md`](docs/offseason-reference-foundation-v1.md)
- [`docs/offseason-schedule-mapping-v1.md`](docs/offseason-schedule-mapping-v1.md)
- [`docs/offseason-database-dashboard-v1.md`](docs/offseason-database-dashboard-v1.md)
- [`docs/source-provider-schedule-adapter-v1.md`](docs/source-provider-schedule-adapter-v1.md)
- [`docs/manual-import.md`](docs/manual-import.md)
- [`docs/data-contract.md`](docs/data-contract.md)

## Public repository boundary

Large or continuously changing raw data, complete SQLite databases, private browser material, HAR files, account exports, cookies, sessions and authorization material do not belong in this repository. Code, schemas, manifests, QA reports, documentation, tests and small privacy-safe fixtures are appropriate here.
