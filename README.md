# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA market history independently from `qoo109/nba-value-lab`.

## Current phase

**V0.8 — Offseason schedule and event-mapping contracts ready; collection remains asleep.**

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
   - fail-closed validation and aggregate evidence
3. **Schedule and event mapping**
   - required source-event and timezone-aware schedule fields
   - exact scheduled-date + home + away candidate key
   - explicit verified, candidate, quarantine, and rejection states
   - no fuzzy or score-assisted identity repair
4. **Phase 2 collection**
   - remains disabled until a monitoring window is needed
   - requires separate explicit approval and reviewed configuration
   - begins with a manual first run; no recurring schedule is active

The automation belongs only to this repository. It does **not** connect to or modify `qoo109/nba-value-lab`.

## Implemented

- `matchups.json` + `straight.json` intake
- `matchupId` and `participantId` normalization
- American-to-decimal conversion
- raw implied-probability calculation
- separate `observed_at` and `ingested_at`
- SQLite historical storage
- exact snapshot deduplication
- changes-only retention
- CSV and JSON exports
- source-health tracking
- bookmaker registry
- grouped history builder
- automated tests and GitHub Actions
- daily source-health and optional manual collection workflow
- optional Google Drive restore/backup code, disabled by default
- canonical NBA team registry v1
- market taxonomy v1
- offseason capture-readiness policy v1
- schedule-import contract v1
- deterministic schedule-mapping fixtures v1

## Reference assets

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
config/schedule-import-contract-v1.json
data/offseason-reference-foundation-current-status-v1.json
data/offseason-schedule-mapping-current-status-v1.json
data/fixtures/offseason-schedule-mapping-v1.json
```

Validation results:

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY
34 / 34 checks passed

OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
21 / 21 checks passed
5 / 5 fixture cases passed
```

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate the offseason foundation:

```bash
python scripts/validate_offseason_reference_foundation_v1.py \
  --self-test \
  --output /tmp/offseason-reference-foundation-v1.json
```

Validate schedule mapping:

```bash
python scripts/validate_offseason_schedule_mapping_v1.py \
  --self-test \
  --output /tmp/offseason-schedule-mapping-v1.json
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

Build grouped history:

```bash
odds-hub-build-history \
  --database data/databases/odds_history.sqlite \
  --output-dir exports/history
```

## Documentation

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- [`docs/offseason-reference-foundation-v1.md`](docs/offseason-reference-foundation-v1.md)
- [`docs/offseason-schedule-mapping-v1.md`](docs/offseason-schedule-mapping-v1.md)
- [`docs/full-automation.md`](docs/full-automation.md)
- [`docs/second-snapshot-intake.md`](docs/second-snapshot-intake.md)
- [`docs/manual-import.md`](docs/manual-import.md)
- [`docs/data-contract.md`](docs/data-contract.md)
- [`docs/v0.3-history-quality-controls.md`](docs/v0.3-history-quality-controls.md)
- [`docs/v0.4-multi-snapshot-history.md`](docs/v0.4-multi-snapshot-history.md)

## Public repository boundary

Large or continuously changing raw data, complete SQLite databases, private credentials, cookies, authorization headers, HAR files, and account exports do not belong in the public repository.

The repository keeps code, schemas, manifests, QA reports, documentation, tests, and small privacy-safe samples. Large data and current backups belong in owner-controlled storage or short-lived GitHub Actions Artifacts.
