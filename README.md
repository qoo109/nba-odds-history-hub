# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.10 — Source/provider metadata QA and fixture schedule adapter validated; collection remains asleep.**

Current operating layers:

1. **Daily source health**
   - runs daily at 09:11 Asia/Taipei
   - monitors approved free/public sources
   - records ETag, Last-Modified, file size, SHA-256, and duplicate skips
   - uploads safe 14-day GitHub Actions Artifacts
   - Google Drive automation is disabled by default; backup is manual
2. **Static offseason foundation**
   - canonical 30-team registry
   - normalized game/futures taxonomy
   - inactive observation cadence templates
3. **Schedule and event mapping**
   - timezone-aware schedule fields
   - exact scheduled-date + home + away candidate key
   - verified, candidate, quarantine, and rejection states
   - no fuzzy or score-assisted identity repair
4. **Additive mapping database**
   - schedule-version history
   - audited mapping decisions
   - current-state and aggregate mapping views
5. **Metadata QA and schedule adapter**
   - explicit audit of legacy registry gaps
   - fixture-only schedule normalization
   - aggregate mapping-status output
   - no new source or provider activation
6. **Phase 2 collection**
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
- static offseason readiness dashboard
- source/provider metadata contract v1
- fixture-only official schedule adapter contract v1

## Reference and status assets

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
config/schedule-import-contract-v1.json
config/source-provider-metadata-contract-v1.json
config/official-schedule-adapter-contract-v1.json
data/offseason-reference-foundation-current-status-v1.json
data/offseason-schedule-mapping-current-status-v1.json
data/offseason-database-dashboard-current-status-v1.json
data/offseason-provider-schedule-adapter-current-status-v1.json
data/fixtures/offseason-schedule-mapping-v1.json
data/fixtures/official-schedule-adapter-v1.json
data/public/offseason-readiness.json
readiness.html
```

Validation results:

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY
34 / 34 checks passed

OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
21 / 21 checks passed

OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY
30 / 30 checks passed

OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS
24 / 24 checks passed
pytest run 29806193268: success
```

## Known metadata gaps

The current legacy source registry does not yet contain explicit `active`, `reviewStatus`, and `rightsStatus` fields. The provider registry does not yet contain explicit `definitionStatus`, `supportedFormats`, and `dataScope` fields.

V0.10 records these gaps without guessing values. No new source or provider was activated.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate metadata and the fixture schedule adapter:

```bash
python scripts/validate_source_provider_schedule_adapter_v1.py \
  --self-test \
  --output /tmp/source-provider-schedule-adapter-v1.json
```

Validate the database and dashboard fixtures:

```bash
python scripts/validate_offseason_database_dashboard_v1.py \
  --output /tmp/offseason-database-dashboard-v1.json
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
- [`readiness.html`](readiness.html)
- [`docs/offseason-reference-foundation-v1.md`](docs/offseason-reference-foundation-v1.md)
- [`docs/offseason-schedule-mapping-v1.md`](docs/offseason-schedule-mapping-v1.md)
- [`docs/offseason-database-dashboard-v1.md`](docs/offseason-database-dashboard-v1.md)
- [`docs/source-provider-schedule-adapter-v1.md`](docs/source-provider-schedule-adapter-v1.md)
- [`docs/full-automation.md`](docs/full-automation.md)
- [`docs/second-snapshot-intake.md`](docs/second-snapshot-intake.md)
- [`docs/manual-import.md`](docs/manual-import.md)
- [`docs/data-contract.md`](docs/data-contract.md)

## Public repository boundary

Large or continuously changing raw data, complete SQLite databases, private credentials, cookies, authorization headers, HAR files, and account exports do not belong in the public repository.

The repository keeps code, schemas, manifests, QA reports, documentation, tests, and small privacy-safe samples. Large data and current backups belong in owner-controlled storage or short-lived GitHub Actions Artifacts.
