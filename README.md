# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.16 — Public JSON Schema declarations and deterministic integrity manifest ready; collection remains asleep.**

Current operating layers:

1. **Daily source health**
   - runs daily at 09:11 Asia/Taipei
   - monitors approved free/public sources
   - uploads short-lived GitHub Actions Artifacts
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
6. **Aggregate readiness export**
   - deterministic repository-only JSON builder
   - aggregate counts and readiness booleans
7. **Public release governance**
   - versioned release manifest
   - legacy/current compatibility tests
   - static release index
   - deterministic contract drift report
   - Draft 2020-12 JSON Schema declarations
   - deterministic SHA-256 integrity manifest
8. **Phase 2 collection**
   - remains disabled until a monitoring window is needed
   - requires a separate explicit decision
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
- canonical NBA team registry v1
- market taxonomy v1
- schedule-import contract and mapping fixtures v1
- schedule-version and mapping-audit database layer v1
- explicit source metadata registry v0.11
- explicit provider metadata registry v0.12
- fixture-only schedule output gate v2
- aggregate metadata/readiness export v1
- aggregate readiness dashboard v1
- public readiness release manifest v1
- public contract drift report v1
- static release index
- three public JSON Schema declarations
- deterministic public integrity manifest v1
- automated tests and GitHub Actions

## Public status pages

- [`readiness.html`](readiness.html) — aggregate offseason readiness
- [`release-index.html`](release-index.html) — public contract versions and drift status

## Public declarations and integrity assets

```text
schemas/public/readiness-release-manifest-v1.schema.json
schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json
schemas/public/public-contract-drift-report-v1.schema.json
data/public/public-governance-checksums-v1.json
scripts/build_public_governance_checksums_v1.py
```

Declaration map:

```text
data/public/readiness-release-manifest-v1.json
  -> schemas/public/readiness-release-manifest-v1.schema.json

data/public/offseason-metadata-readiness-v1.json
  -> schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json

data/public/readiness-contract-drift-report-v1.json
  -> schemas/public/public-contract-drift-report-v1.schema.json
```

## Current validation

```text
OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY
25 / 25 checks passed

OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_READY
9 / 9 checks passed
0 detected drift

OFFSEASON_PUBLIC_JSON_SCHEMA_AND_CHECKSUM_MANIFEST_V1_READY
3 schema declarations
8 integrity assets
sha256

V0.16 focused workflow: 29840324365
V0.16 full test workflow: 29840324295
V0.16 artifact: 8499063803
```

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

Build the integrity manifest:

```bash
python scripts/build_public_governance_checksums_v1.py \
  --output data/public/public-governance-checksums-v1.json
```

Run focused governance tests:

```bash
pytest -q \
  tests/test_public_readiness_contracts.py \
  tests/test_readiness_release_index_drift_v1.py \
  tests/test_public_contract_schema_checksums_v1.py
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

## Current execution boundary

```text
new sources activated: 0
new providers activated: 0
source automation approved: false
provider automation approved: false
external schedule read: false
production schedule imported: false
scheduled collection: false
Phase 2 approval granted: false
```

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate an incoming package:

```bash
odds-hub-validate-intake --package-dir data/incoming/example
```

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`docs/public-data-declarations-v1.md`](docs/public-data-declarations-v1.md)
- [`docs/static-release-index-drift-v1.md`](docs/static-release-index-drift-v1.md)
- [`docs/readiness-release-v1.md`](docs/readiness-release-v1.md)
- [`docs/offseason-aggregate-metadata-dashboard-v1.md`](docs/offseason-aggregate-metadata-dashboard-v1.md)
- [`docs/provider-metadata-upgrade-v1.md`](docs/provider-metadata-upgrade-v1.md)
- [`docs/offseason-reference-foundation-v1.md`](docs/offseason-reference-foundation-v1.md)
- [`docs/offseason-schedule-mapping-v1.md`](docs/offseason-schedule-mapping-v1.md)
- [`docs/offseason-database-dashboard-v1.md`](docs/offseason-database-dashboard-v1.md)
- [`docs/source-provider-schedule-adapter-v1.md`](docs/source-provider-schedule-adapter-v1.md)
- [`docs/manual-import.md`](docs/manual-import.md)
- [`docs/data-contract.md`](docs/data-contract.md)

## Public repository boundary

Large or continuously changing raw data and complete SQLite databases do not belong in the public repository. The repository keeps code, schemas, manifests, QA reports, documentation, tests and small privacy-safe samples.
