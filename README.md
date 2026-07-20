# NBA Odds History Hub

A dedicated, auditable repository for collecting and preserving NBA odds history independently from `qoo109/nba-value-lab`.

## Current phase

The project is activating in two stages:

1. **Phase 1 — daily source health and Google Drive backup**
   - runs daily at 09:11 Asia/Taipei
   - monitors approved free/public sources
   - saves new or changed files only
   - records ETag, Last-Modified, SHA-256, source health, and duplicate skips
   - backs up reports, state, raw archives, exports, backups, and SQLite to Google Drive
   - does not ingest live odds
2. **Phase 2 — timestamped odds capture**
   - remains intentionally disabled until an NBA monitoring window is needed
   - requires owner-approved `matchups` and `straight` JSON URLs
   - runs only from an explicit manual dispatch until an hourly schedule is separately reviewed

The automation belongs only to this repository. It does **not** connect to or modify `qoo109/nba-value-lab`.

## Implemented

- `matchups.json` + `straight.json` intake
- `matchupId` and `participantId` normalization
- American-to-decimal price conversion
- raw implied probability calculation
- separate `observed_at` and `ingested_at`
- SQLite historical storage
- exact snapshot deduplication
- changes-only retention
- CSV and JSON exports
- source health tracking
- bookmaker registry
- grouped history builder
- automated tests and GitHub Actions
- phased daily source-health and optional odds-capture workflow
- Google Drive restore and backup

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Validate a package:

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

Expected outputs include:

```text
exports/history/source_health.json
exports/history/nba_value_lab_odds_export.json
```

See [`docs/full-automation.md`](docs/full-automation.md), [`docs/second-snapshot-intake.md`](docs/second-snapshot-intake.md), [`docs/manual-import.md`](docs/manual-import.md), [`docs/data-contract.md`](docs/data-contract.md), [`docs/v0.3-history-quality-controls.md`](docs/v0.3-history-quality-controls.md), and [`docs/v0.4-multi-snapshot-history.md`](docs/v0.4-multi-snapshot-history.md).

## Public repository boundary

Large or continuously changing raw data, complete SQLite databases, private credentials, cookies, authorization headers, HAR files, and account exports do not belong in the public repository.

The repository keeps code, schema, manifests, QA reports, documentation, tests, and small privacy-safe samples. Large data and current backups belong in Google Drive or short-lived GitHub Actions Artifacts.
