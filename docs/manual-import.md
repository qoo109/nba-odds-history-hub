# Manual Import Guide

## 1. Prepare the two files

Export only JSON response bodies from the browser network inspector:

- `matchups.json`
- `straight.json`

Do not include cookies, authorization headers, account information, or HAR files. The quality report shows which `matchupId` values matched instead of silently assuming the two files are complete.

## 2. Install locally

```bash
git clone https://github.com/qoo109/nba-odds-history-hub.git
cd nba-odds-history-hub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 3. Import every exact timestamped quote

```bash
odds-hub-import \
  --matchups /path/to/matchups.json \
  --straight /path/to/straight.json \
  --observed-at "2026-07-20T11:10:00+08:00" \
  --source pinnacle_manual \
  --bookmaker pinnacle \
  --dedupe-mode exact \
  --database data/databases/odds_history.sqlite \
  --export-dir exports
```

## 4. Save only genuine line or price changes

```bash
odds-hub-import \
  --matchups /path/to/matchups.json \
  --straight /path/to/straight.json \
  --observed-at "2026-07-20T12:10:00+08:00" \
  --source pinnacle_manual \
  --bookmaker pinnacle \
  --dedupe-mode changes-only
```

`changes-only` compares each quote with the latest strictly earlier observation. It is safe for out-of-order historical backfills and never compares an older row with future data.

## 5. Build grouped histories

```bash
odds-hub-build-history \
  --database data/databases/odds_history.sqlite \
  --output-dir exports/history
```

Outputs:

```text
exports/history/odds_history_grouped.json
exports/history/source_health.json
exports/history/nba_value_lab_odds_export.json
```

A quote is movement-ready only after it has at least two distinct `observed_at` values. Multiple rows at the same time are flagged rather than silently collapsed.

## 6. Review before publishing

Always inspect:

- `exports/import_quality_report.json`
- matched and unmatched `matchupId`
- duplicate market and participant diagnostics
- orphan participant prices
- invalid prices
- source-health snapshot count
- quote identities with duplicate `observed_at`

Missing rows are not evidence that a price was unchanged.

## Important time rule

`observed_at` is not the same as `cutoff_at`, `scheduled_tipoff`, or `ingested_at`. A second real `observed_at` is required before the project can describe movement between two points.
