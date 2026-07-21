# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.12 — Explicit source and provider metadata complete; collection remains asleep.**

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
   - verified, candidate, quarantine, and rejection states
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
- explicit source metadata registry v0.11
- explicit provider metadata registry v0.12
- fixture-only schedule output gate v2

## Reference and status assets

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
config/schedule-import-contract-v1.json
config/source-provider-metadata-contract-v1.json
config/official-schedule-adapter-contract-v1.json
config/source-registry.json
config/bookmaker-registry.json
data/offseason-reference-foundation-current-status-v1.json
data/offseason-schedule-mapping-current-status-v1.json
data/offseason-database-dashboard-current-status-v1.json
data/offseason-provider-schedule-adapter-current-status-v1.json
data/fixtures/offseason-schedule-mapping-v1.json
data/fixtures/official-schedule-adapter-v1.json
data/public/offseason-readiness.json
readiness.html
```

## Validation results

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY
34 / 34 checks passed

OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
21 / 21 checks passed

OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY
30 / 30 checks passed

OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V2_READY
28 / 28 checks passed

OFFSEASON_EXPLICIT_SOURCE_PROVIDER_METADATA_AND_SCHEDULE_OUTPUT_GATE_V2_READY
26 / 26 checks passed

validation workflow run: 29810808509
test workflow run: 29810808595
artifact id: 8487322908
```

## Metadata boundary

The existing source remains manual-only. The existing provider record is classified as `source_label_only`, supports the explicit `american` format field, and is limited to `owner_supplied_nba_futures_snapshots`.

```text
new sources activated: 0
new providers activated: 0
source automation approved: false
provider automation approved: false
external schedule read: false
production schedule imported: false
```

These fields document the existing evidence. They do not authorize new access or expand data coverage claims.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate explicit metadata and the fixture schedule adapter:

```bash
python scripts/validate_source_provider_schedule_adapter_v1.py \
  --self-test \
  --output /tmp/source-provider-schedule-adapter-v2.json
```

Validate the fixture output gate:

```bash
python scripts/validate_metadata_registry_output_gate_v1.py \
  --output /tmp/schedule-output-gate-v2.json
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

Large or continuously changing raw data, complete SQLite databases, private credentials, cookies, authorization headers, HAR files, and account exports do not belong in the public repository.

The repository keeps code, schemas, manifests, QA reports, documentation, tests, and small privacy-safe samples. Large data and current backups belong in owner-controlled storage or short-lived GitHub Actions Artifacts.
