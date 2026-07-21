# NBA Odds History Hub

A dedicated, auditable repository for preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.18 — Three-stage manual schedule import preflight and rollback rehearsal ready; collection remains asleep.**

The repository currently provides:

1. source-health monitoring for approved free/public sources;
2. canonical NBA team and market reference data;
3. schedule adapter, mapping and versioned SQLite contracts;
4. aggregate readiness exports and public governance checks;
5. synthetic preseason schedule dry runs;
6. a disabled three-stage manual schedule import preflight;
7. Phase 2 collection, which remains inactive pending a separate explicit decision.

Nothing in this repository automatically connects to or modifies `qoo109/nba-value-lab`.

## V0.18: three completed preflight stages

### 1. Exact identity and schema

The fixture is locked by:

```text
path: data/fixtures/preseason-dry-run-v1.json
filename: preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
schema: preseason-dry-run-fixture-v1
season: 2026-27
```

A mismatch in path, filename, size, checksum, schema or season fails closed.

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

### 3. Transaction rollback and post-check

The accepted synthetic rows are written inside a temporary SQLite transaction:

```text
source events: 3
schedule versions: 5
current schedules: 3
mapping audit decisions: 5
canonical events: 0
raw imports: 0
odds snapshots: 0
```

The transaction is always rolled back. Every target table is verified as zero afterward.

## V0.18 validation

```text
formal state:
OFFSEASON_PRESEASON_MANUAL_SCHEDULE_IMPORT_PREFLIGHT_AND_ROLLBACK_V1_READY

checks: 19 / 19
focused workflow: 29845051057
full test workflow: 29845050863
preseason workflow: 29845050942
public-schema workflow: 29845051009
artifact: 8500959742
artifact digest:
sha256:cd398c5a3bba096b1f5ba392bb47c8afff766be66a2d955a267d0360bfd4d654
```

## V0.18 assets

```text
config/manual-schedule-import-preflight-v1.json
data/manual-schedule-import-preflight-current-status-v1.json
src/nba_odds_history_hub/manual_schedule_preflight.py
scripts/validate_manual_schedule_preflight_v1.py
tests/test_manual_schedule_preflight_v1.py
docs/manual-schedule-import-preflight-v1.md
.github/workflows/validate-manual-schedule-preflight-v1.yml
```

## Approval boundary

```text
request id: SCHEDULE-IMPORT-PREFLIGHT-2026-07-21-001
state: disabled_preapproval
owner approval granted: false
execution enabled: false
maximum execution count: 0
production import executed: false
external files read: false
network calls made: false
production database touched: false
scheduled collection: false
canonical event IDs created: 0
cross-repository write: false
```

The preflight is a safety rehearsal, not a production import tool.

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

Install and run all tests:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Rebuild the V0.18 preflight report:

```bash
python scripts/validate_manual_schedule_preflight_v1.py \
  --output runtime/reports/manual-schedule-import-preflight-v1.json
```

Run the earlier preseason dry run:

```bash
python scripts/validate_preseason_dry_run_v1.py \
  --output runtime/reports/preseason-dry-run-v1.json
```

## Public status pages

- [`readiness.html`](readiness.html) — aggregate offseason readiness
- [`release-index.html`](release-index.html) — public contract versions and drift status

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
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
