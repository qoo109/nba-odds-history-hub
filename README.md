# NBA Odds History Hub

NBA odds history ingestion, normalization, storage, visualization, and export hub for NBA Value Lab.

## Live dashboard

https://qoo109.github.io/nba-odds-history-hub/

The dashboard currently contains one owner-supplied NBA Futures snapshot observed at `2026-07-20T11:10:00+08:00`: 5 markets, 91 options, 5 matched `matchupId`, and 0 unmatched IDs. It is a historical snapshot viewer, not a live odds feed.

## Current status

**V0.3 — first real futures snapshot and GitHub Pages dashboard**

Implemented:

- Manual `matchups` + `straight` JSON importer
- Separate `observed_at` and `ingested_at`
- American-to-decimal conversion and raw implied probability
- SQLite history storage and exact-snapshot deduplication
- CSV/JSON exports
- Automated Python tests and GitHub Actions
- First reviewed public NBA Futures snapshot
- Snapshot manifest with SHA-256, counts, matching results, and quality flags
- Static dashboard with search, sorting, overround display, and generated CSV/JSON downloads

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
  --observed-at "2026-07-20T11:10:00+08:00"
```

See [`docs/manual-import.md`](docs/manual-import.md), [`docs/data-contract.md`](docs/data-contract.md), and [`docs/v0.3-futures-dashboard.md`](docs/v0.3-futures-dashboard.md).

## Public repository boundary

The repository contains code, schemas, documentation, tests, and small reviewed snapshots. Large or continuously changing databases stay outside Git. Never commit cookies, authorization headers, session tokens, credentials, HAR files, or private account data. Do not bypass access controls, CAPTCHAs, authentication, or rate limits.

A single snapshot cannot be called opening, closing, or line movement history without additional timestamped observations.

## Roadmap

- **V0.1** Repository structure and data contract — implemented
- **V0.2** Manual JSON importer — implemented
- **V0.3** Real snapshot validation and first dashboard — active
- **V0.3 next** Import quality report, change-aware deduplication, bookmaker/source registry tables, and NBA Value Lab event identity placeholders
- **V0.4** Multi-snapshot historical movement dashboard
- **V0.5** NBA Value Lab export contract
