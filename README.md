# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.13 — Privacy-safe aggregate metadata export and readiness dashboard ready; collection remains asleep.**

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
6. **Aggregate readiness export**
   - deterministic repository-only JSON builder
   - aggregate counts and readiness booleans
   - no named source/provider records or row-level events
   - synced static readiness dashboard
7. **Phase 2 collection**
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
data/public/offseason-readiness.json
data/public/offseason-metadata-readiness-v1.json
data/offseason-aggregate-metadata-dashboard-current-status-v1.json
scripts/build_offseason_aggregate_metadata_export_v1.py
readiness.html
```

## Current validation

```text
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V2_READY
28 / 28 checks passed

OFFSEASON_EXPLICIT_SOURCE_PROVIDER_METADATA_AND_SCHEDULE_OUTPUT_GATE_V2_READY
26 / 26 checks passed

OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY
25 / 25 checks passed

V0.13 validation workflow: 29812604778
V0.13 test workflow: 29812604707
V0.13 compatibility workflow: 29812604790
V0.13 artifact: 8488029509
```

## Aggregate export

Build the public aggregate JSON:

```bash
python scripts/build_offseason_aggregate_metadata_export_v1.py \
  --as-of 2026-07-21 \
  --output data/public/offseason-metadata-readiness-v1.json
```

The export includes:

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

The export contains aggregate categories and readiness booleans only. It does not publish named source/provider records, event IDs, event rows, price rows, or external payload content.

## Metadata boundary

The existing source remains manual-only. The existing provider remains a descriptive `source_label_only` record for owner-supplied futures snapshots.

```text
new sources activated: 0
new providers activated: 0
source automation approved: false
provider automation approved: false
external schedule read: false
production schedule imported: false
```

These fields document existing evidence. They do not authorize new access or expand data coverage claims.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate the aggregate export:

```bash
pytest -q tests/test_offseason_aggregate_metadata_export_v1.py
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

Large or continuously changing raw data, complete SQLite databases, private browser material, HAR files, and account exports do not belong in the public repository.

The repository keeps code, schemas, manifests, QA reports, documentation, tests, and small privacy-safe samples. Large data and current backups belong in owner-controlled storage or short-lived GitHub Actions Artifacts.
