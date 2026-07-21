# NBA Odds History Hub

A dedicated, auditable repository for preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.19 — Aggregate owner-review packet and disabled control-step plan ready; collection remains asleep.**

The repository currently provides:

1. source-health monitoring for approved free/public sources;
2. canonical NBA team and market reference data;
3. schedule adapter, mapping and versioned SQLite contracts;
4. aggregate readiness exports and public governance checks;
5. synthetic preseason schedule dry runs;
6. a disabled three-stage manual schedule preflight;
7. an aggregate owner-review packet and non-executable six-step control plan;
8. Phase 2 collection, which remains inactive pending a separate explicit decision.

Nothing in this repository automatically connects to or modifies `qoo109/nba-value-lab`.

## V0.19 owner-review packet

```text
packet id: SCHEDULE-OWNER-REVIEW-2026-07-21-001
state: review_ready_disabled
source preflight request: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
decision requested: false
decision recorded: false
approval granted: false
execution enabled: false
maximum execution count: 0
```

The packet references the exact validated V0.18 evidence:

```text
preflight checks: 19 / 19
path: data/fixtures/preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
preflight artifact: 8500959742
rollback executed: true
post-rollback total rows: 0
```

It does not ask for production approval. The only current outcomes are to keep the packet disabled or request another synthetic review.

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
```

The six steps describe controls rather than a runnable command:

1. validate aggregate review evidence;
2. bind a separate approval request;
3. bind an exact approved file identity;
4. verify an independent database backup reference;
5. describe a transactional import without execution;
6. require post-import aggregate checks and a rollback decision.

No command string, shell body, argument vector or executable import module is emitted.

## V0.19 validation

```text
formal state:
OFFSEASON_PRESEASON_OWNER_REVIEW_PACKET_AND_DISABLED_IMPORT_COMMAND_PLAN_V1_READY

checks: 31 / 31
focused workflow: 29852455631
full test workflow: 29852455545
manual preflight workflow: 29852455102
preseason workflow: 29852455129
public-schema workflow: 29852455323
artifact: 8503909693
artifact digest:
sha256:10e8e2e366b1ceb2b29cb6185d37d29b9d0399cfb968c9404522281b6e0fe3e2
```

## V0.19 assets

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

## Preserved V0.18 preflight

### 1. Exact identity and schema

```text
path: data/fixtures/preseason-dry-run-v1.json
filename: preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
schema: preseason-dry-run-fixture-v1
season: 2026-27
```

### 2. Aggregate preview

```text
observations: 2
accepted rows: 5
excluded rows: 2
unique accepted events: 3
unknown aliases: 1
same-team rows: 1
row-level excluded records emitted: false
```

### 3. Transaction rollback

Inside the temporary transaction:

```text
source events: 3
schedule versions: 5
current schedules: 3
mapping audit decisions: 5
canonical events: 0
raw imports: 0
odds snapshots: 0
```

After rollback every target count is zero.

## Current execution boundary

```text
current mode: offseason_sleep
owner review decision requested: false
owner review approval granted: false
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

Rebuild the V0.19 report:

```bash
python scripts/validate_owner_review_packet_v1.py \
  --output runtime/reports/preseason-owner-review-packet-v1.json
```

Rebuild the V0.18 preflight report:

```bash
python scripts/validate_manual_schedule_preflight_v1.py \
  --output runtime/reports/manual-schedule-import-preflight-v1.json
```

## Public status pages

- [`readiness.html`](readiness.html) — aggregate offseason readiness
- [`release-index.html`](release-index.html) — public contract versions and drift status

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
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
