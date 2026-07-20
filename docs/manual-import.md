# Manual Import Guide

## 1. Prepare the two files

Export only the JSON response bodies from the browser network inspector:

- `matchups.json`
- `straight.json`

The two files must describe the same set of `matchupId` values.

Do not include browser cookies, authorization headers, or account information.

## 2. Install locally

```bash
git clone https://github.com/qoo109/nba-odds-history-hub.git
cd nba-odds-history-hub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 3. Import a snapshot

Use the time when the prices were actually observed. Include the timezone offset.

```bash
odds-hub-import \
  --matchups /path/to/matchups.json \
  --straight /path/to/straight.json \
  --observed-at "2026-07-20T11:10:00+08:00" \
  --database data/databases/odds_history.sqlite \
  --export-dir exports
```

## 4. Outputs

The command creates or updates:

```text
data/databases/odds_history.sqlite
exports/odds_history.json
exports/odds_history.csv
```

The database and generated exports are ignored by Git by default.

## 5. Example using synthetic samples

```bash
odds-hub-import \
  --matchups data/samples/matchups.sample.json \
  --straight data/samples/straight.sample.json \
  --observed-at "2026-07-20T11:10:00+08:00"
```

## Important time rule

`observed_at` is not the same as:

- `cutoff_at`
- `scheduled_tipoff`
- `ingested_at`

The original observation time is essential for future opening, pregame, closing-line, and point-in-time analysis.
