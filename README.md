# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.15 — Static public release index and deterministic contract drift report ready; collection remains asleep.**

Current operating layers:

1. **Daily source health**
   - runs daily at 09:11 Asia/Taipei
   - monitors approved free/public sources
   - uploads safe 14-day GitHub Actions Artifacts
   - Google Drive automation remains disabled by default
2. **Static offseason foundation**
   - canonical 30-team registry
   - normalized game/futures taxonomy
   - inactive observation cadence templates
3. **Schedule and event mapping**
   - timezone-aware schedule fields
   - exact scheduled-date + home + away candidate key
   - verified, candidate, quarantine and rejection states
   - no fuzzy or score-assisted identity repair
4. **Additive mapping database**
   - schedule-version history
   - audited mapping decisions
   - current-state and aggregate mapping views
5. **Explicit metadata and fixture output gate**
   - complete source and provider metadata fields
   - fixture-only schedule normalization
   - additive candidate persistence
   - no new source or provider activation
6. **Aggregate readiness export**
   - deterministic repository-only JSON builder
   - aggregate counts and readiness booleans
   - no named source/provider records or row-level events
7. **Public release governance**
   - versioned release manifest
   - compatibility tests for legacy and aggregate readiness contracts
   - static release index
   - deterministic fail-closed drift report
8. **Phase 2 collection**
   - remains disabled until a monitoring window is needed
   - requires separate explicit approval and reviewed configuration
   - no recurring collection schedule is active

The automation belongs only to this repository. It does **not** connect to or modify `qoo109/nba-value-lab`.

## Implemented

- `matchups.json` + `straight.json` intake
- American-to-decimal conversion and implied-probability calculation
- separate `observed_at` and `ingested_at`
- SQLite historical storage
- exact snapshot deduplication and changes-only retention
- source-health tracking and registries
- grouped history builder
- automated tests and GitHub Actions
- canonical NBA team registry v1
- market taxonomy v1
- offseason capture-readiness policy v1
- schedule-import contract v1
- deterministic schedule-mapping fixtures v1
- schedule-version and mapping-audit database layer v1
- explicit source metadata registry v0.11
- explicit provider metadata registry v0.12
- fixture-only schedule output gate v2
- aggregate metadata/readiness export v1
- aggregate readiness dashboard v1
- public readiness release manifest v1
- public contract drift report v1
- static release index

## Public status pages

- [`readiness.html`](readiness.html) — aggregate offseason readiness
- [`release-index.html`](release-index.html) — public contract versions and drift status

## Reference and governance assets

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
config/schedule-import-contract-v1.json
config/source-provider-metadata-contract-v1.json
config/official-schedule-adapter-contract-v1.json
config/source-registry.json
config/bookmaker-registry.json
data/public/offseason-readiness.json
data/public/offseason-metadata-readiness-v1.json
data/public/readiness-release-manifest-v1.json
data/public/readiness-contract-drift-report-v1.json
scripts/build_offseason_aggregate_metadata_export_v1.py
scripts/build_public_contract_drift_report_v1.py
readiness.html
release-index.html
```

## Current validation

```text
OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY
25 / 25 checks passed

OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_READY
9 / 9 checks passed
0 detected drift

V0.15 focused workflow: 29818988525
V0.15 full test workflow: 29818988517
V0.15 artifact: 8490529626
```

The drift validator compares:

```text
summary.teams
summary.marketClasses
fixtureMode
currentMode
```

It also verifies committed schema versions and the inactive repository-only boundary. Unexpected drift produces a non-zero exit code.

## Rebuild validation assets

Build the aggregate readiness export:

```bash
python scripts/build_offseason_aggregate_metadata_export_v1.py \
  --as-of 2026-07-21 \
  --output data/public/offseason-metadata-readiness-v1.json
```

Build the contract drift report:

```bash
python scripts/build_public_contract_drift_report_v1.py \
  --output data/public/readiness-contract-drift-report-v1.json
```

Run focused tests:

```bash
pytest -q \
  tests/test_public_readiness_contracts.py \
  tests/test_readiness_release_index_drift_v1.py
```

## Current aggregate state

```text
teams: 30
market classes: 11
sources: 1
providers: 1
metadata missing fields: 0
automation approvals: 0
active cadence templates: 0
fixture schedule games: 6
```

The public exports contain aggregate categories and readiness booleans only. They do not publish named source/provider records, event IDs, event rows, price rows or external payload content.

## Metadata and execution boundary

The existing source remains manual-only. The existing provider remains a descriptive `source_label_only` record for owner-supplied futures snapshots.

```text
new sources activated: 0
new providers activated: 0
source automation approved: false
provider automation approved: false
external schedule read: false
production schedule imported: false
scheduled collection: false
```

These fields document existing evidence. They do not authorize new access or expand data coverage claims.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate an incoming package:

```bash
odds-hub-validate-intake --package-dir data/incoming/example
```

Import an approved package:

```bash
odds-hub-import \
  --matchups data/incoming/example/matchups.json \
  --straight data/incoming/example/straight.json \
  --observed-at 2026-07-20T12:00:00Z \
  --database data/databases/odds_history.sqlite \
  --source manual_json \
  --source-name "Manual JSON" \
  --bookmaker example_book \
  --bookmaker-name "Example Book" \
  --dedupe-mode changes-only \
  --export-dir exports
```

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`docs/static-release-index-drift-v1.md`](docs/static-release-index-drift-v1.md)
- [`docs/readiness-release-v1.md`](docs/readiness-release-v1.md)
- [`docs/offseason-aggregate-metadata-dashboard-v1.md`](docs/offseason-aggregate-metadata-dashboard-v1.md)
- [`docs/provider-metadata-upgrade-v1.md`](docs/provider-metadata-upgrade-v1.md)
- [`docs/offseason-reference-foundation-v1.md`](docs/offseason-reference-foundation-v1.md)
- [`docs/offseason-schedule-mapping-v1.md`](docs/offseason-schedule-mapping-v1.md)
- [`docs/offseason-database-dashboard-v1.md`](docs/offseason-database-dashboard-v1.md)
- [`docs/source-provider-schedule-adapter-v1.md`](docs/source-provider-schedule-adapter-v1.md)
- [`docs/full-automation.md`](docs/full-automation.md)
- [`docs/second-snapshot-intake.md`](docs/second-snapshot-intake.md)
- [`docs/manual-import.md`](docs/manual-import.md)
- [`docs/data-contract.md`](docs/data-contract.md)

## Public repository boundary

Large or continuously changing raw data, complete SQLite databases, private browser material, HAR files and account exports do not belong in the public repository.

The repository keeps code, schemas, manifests, QA reports, documentation, tests and small privacy-safe samples. Large data and current backups belong in owner-controlled storage or short-lived GitHub Actions Artifacts.
