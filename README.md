# NBA Odds History Hub

NBA odds ingestion, normalization, timestamped storage, quality reporting, history building, visualization, and research-safe export hub for NBA Value Lab.

## Live pages

- Dashboard: https://qoo109.github.io/nba-odds-history-hub/
- Second snapshot intake: https://qoo109.github.io/nba-odds-history-hub/snapshot-intake.html

The public dashboard currently contains one reviewed NBA Futures snapshot observed at `2026-07-20T11:10:00+08:00`: 5 markets, 91 options, 5 matched `matchupId`, and 0 unmatched IDs. It is a historical snapshot viewer, not a live feed.

## Current status

**V0.4 — multi-snapshot history builder and second-snapshot intake gate ready**

Implemented:

- Manual `matchups` + `straight` JSON importer
- Separate `observed_at`, `ingested_at`, scheduled time, and cutoff time
- American-to-decimal conversion and raw implied probability
- SQLite history storage
- Exact timestamped deduplication
- Optional `changes-only` retention for genuine line/price changes
- Strictly-prior change comparison for out-of-order backfills
- Formal matched/unmatched import quality report
- Source and bookmaker registries
- Unmapped source-event placeholders and explicit canonical mappings
- Quote-history grouping by stable identity
- Movement readiness only after two distinct `observed_at` values
- Snapshot coverage and source-health summaries
- Research-safe NBA Value Lab odds export with all market gates closed by default
- Dashboard history-readiness panel and dormant movement chart renderer
- Second-snapshot intake package validator with SHA-256 and sensitive-key checks
- GitHub issue form and public intake page
- Automated tests and GitHub Actions

## Quick start

```bash
git clone https://github.com/qoo109/nba-odds-history-hub.git
cd nba-odds-history-hub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Validate a candidate second snapshot before import:

```bash
odds-hub-validate-intake \
  --package-dir /path/to/second-snapshot
```

The directory must contain:

```text
matchups.json
straight.json
metadata.json
```

Import only after `intake_report.json` shows `readyForImport: true`:

```bash
odds-hub-import \
  --matchups /path/to/second-snapshot/matchups.json \
  --straight /path/to/second-snapshot/straight.json \
  --observed-at "2026-07-21T11:10:00+08:00" \
  --source pinnacle_manual \
  --bookmaker pinnacle \
  --dedupe-mode changes-only
```

Build grouped histories and research exports:

```bash
odds-hub-build-history \
  --database data/databases/odds_history.sqlite \
  --output-dir exports/history
```

Generated history outputs:

```text
exports/history/odds_history_grouped.json
exports/history/source_health.json
exports/history/nba_value_lab_odds_export.json
```

See [`docs/second-snapshot-intake.md`](docs/second-snapshot-intake.md), [`docs/manual-import.md`](docs/manual-import.md), [`docs/data-contract.md`](docs/data-contract.md), [`docs/v0.3-history-quality-controls.md`](docs/v0.3-history-quality-controls.md), and [`docs/v0.4-multi-snapshot-history.md`](docs/v0.4-multi-snapshot-history.md).

## Public repository boundary

The repository contains code, schemas, documentation, tests, and small reviewed snapshots. Large or continuously changing databases stay outside Git. Never commit cookies, authorization headers, session tokens, credentials, HAR files, or private account data. Do not bypass access controls, CAPTCHAs, authentication, or rate limits.

A single snapshot cannot be called opening, closing, or line movement history. Missing rows are never interpreted as unchanged prices.

## Roadmap

- **V0.1** Repository structure and data contract — implemented
- **V0.2** Manual JSON importer — implemented
- **V0.3** Real snapshot validation, dashboard, QA, registries, and history-quality controls — implemented
- **V0.4** History builder and second-snapshot intake gate — implemented; awaiting the second real snapshot
- **V0.5** Canonical NBA Value Lab join validation and point-in-time export hardening — blocked until real multi-snapshot data exists
