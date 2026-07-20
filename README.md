# NBA Odds History Hub

NBA odds history ingestion, normalization, storage, visualization, and export hub for NBA Value Lab.

## Current status

**V0.2 — first manual import pipeline implemented**

The repository currently includes:

- Manual JSON import for `matchups` and `straight` responses
- Timestamped odds snapshots with separate `observed_at` and `ingested_at`
- American-to-decimal odds conversion
- Raw implied probability calculation
- Event, market, and participant normalization
- SQLite storage and exact-snapshot deduplication
- CSV/JSON exports for NBA Value Lab
- Synthetic sample files and automated tests

## Data flow

```text
Source page data
      ↓
Manual JSON import
      ↓
Validation and normalization
      ↓
SQLite history database
      ↓
CSV / JSON exports
      ↓
NBA Value Lab
```

## Quick start

```bash
git clone https://github.com/qoo109/nba-odds-history-hub.git
cd nba-odds-history-hub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the synthetic example:

```bash
odds-hub-import \
  --matchups data/samples/matchups.sample.json \
  --straight data/samples/straight.sample.json \
  --observed-at "2026-07-20T11:10:00+08:00"
```

Generated local outputs:

```text
data/databases/odds_history.sqlite
exports/odds_history.json
exports/odds_history.csv
```

See [`docs/manual-import.md`](docs/manual-import.md) for the full workflow and [`docs/data-contract.md`](docs/data-contract.md) for the normalized schema.

## Public repository boundary

This repository contains source code, schemas, documentation, tests, and small sanitized samples. Large or continuously changing databases should be stored outside Git.

The project does not require all third-party data to remain private. Each source can be reviewed individually. Public samples should document their source and usage boundary.

## Security rules

- Never commit cookies, authorization headers, session tokens, passwords, or private account data.
- Preserve the true observation time separately from market cutoff and game start times.
- Keep source attribution and usage notes with each imported dataset.
- Do not bypass access controls, authentication, CAPTCHAs, or rate limits.

## Planned milestones

- **V0.1** Repository structure and data contract — implemented
- **V0.2** Pinnacle manual JSON importer — implemented, validation in progress
- **V0.3** SQLite history quality checks and change-aware deduplication
- **V0.4** Historical odds dashboard
- **V0.5** NBA Value Lab export contract
