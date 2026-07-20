# NBA Odds History Hub

NBA odds ingestion, normalization, timestamped storage, quality reporting, visualization, and export hub for NBA Value Lab.

## Live dashboard

https://qoo109.github.io/nba-odds-history-hub/

The dashboard contains one reviewed NBA Futures snapshot observed at `2026-07-20T11:10:00+08:00`: 5 markets, 91 options, 5 matched `matchupId`, and 0 unmatched IDs. It is a historical snapshot viewer, not a live feed.

## Current status

**V0.3 — real snapshot validation and history-quality controls**

Implemented:

- Manual `matchups` + `straight` JSON importer
- Separate `observed_at`, `ingested_at`, scheduled time, and cutoff time
- American-to-decimal conversion and raw implied probability
- SQLite history storage
- Exact timestamped deduplication
- Optional `changes-only` retention for genuine line/price changes
- Strictly-prior change comparison for out-of-order backfills
- Formal matched/unmatched import quality report
- Duplicate, orphan-participant, and invalid-price diagnostics
- Source and bookmaker registries
- Unmapped source-event placeholders and explicit canonical mappings
- CSV/JSON exports
- Automated tests and GitHub Actions
- First reviewed public NBA Futures snapshot and static dashboard

## Quick start

```bash
git clone https://github.com/qoo109/nba-odds-history-hub.git
cd nba-odds-history-hub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

```bash
odds-hub-import \
  --matchups data/samples/matchups.sample.json \
  --straight data/samples/straight.sample.json \
  --observed-at "2026-07-20T11:10:00+08:00" \
  --source pinnacle_manual \
  --bookmaker pinnacle \
  --dedupe-mode changes-only
```

Generated outputs:

```text
data/databases/odds_history.sqlite
exports/odds_history.json
exports/odds_history.csv
exports/import_quality_report.json
```

See [`docs/manual-import.md`](docs/manual-import.md), [`docs/data-contract.md`](docs/data-contract.md), [`docs/v0.3-futures-dashboard.md`](docs/v0.3-futures-dashboard.md), and [`docs/v0.3-history-quality-controls.md`](docs/v0.3-history-quality-controls.md).

## Public repository boundary

The repository contains code, schemas, documentation, tests, and small reviewed snapshots. Large or continuously changing databases stay outside Git. Never commit cookies, authorization headers, session tokens, credentials, HAR files, or private account data. Do not bypass access controls, CAPTCHAs, authentication, or rate limits.

A single snapshot cannot be called opening, closing, or line movement history without additional timestamped observations.

## Roadmap

- **V0.1** Repository structure and data contract — implemented
- **V0.2** Manual JSON importer — implemented
- **V0.3** Real snapshot validation, dashboard, QA report, registries, and history-quality controls — implemented
- **V0.4** Multi-snapshot history builder and movement dashboard — next
- **V0.5** NBA Value Lab odds export contract
