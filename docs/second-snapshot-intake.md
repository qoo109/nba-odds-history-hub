# Second Snapshot Intake Runbook

## Purpose

This runbook activates the next V0.4 data step without fabricating history. A second real snapshot is accepted only after the package and import-quality checks pass.

## Required package

Create one local directory containing exactly:

```text
matchups.json
straight.json
metadata.json
```

Start from [`data/templates/second-snapshot/metadata.json`](../data/templates/second-snapshot/metadata.json) and replace `observedAt` with the true time the prices were visible, including the timezone offset.

Example:

```json
{
  "observedAt": "2026-07-21T11:10:00+08:00",
  "sourceId": "pinnacle_manual",
  "bookmakerId": "pinnacle",
  "notes": "Second owner-supplied NBA Futures snapshot"
}
```

## Prohibited content

Do not include:

- cookies
- authorization headers
- passwords
- API or session tokens
- private account data
- HAR files
- automated access or bypass logic

The intake validator scans JSON keys for common credential and session terms. A finding blocks import until reviewed and removed.

## Validate before import

```bash
odds-hub-validate-intake \
  --package-dir /path/to/second-snapshot
```

The command writes:

```text
/path/to/second-snapshot/intake_report.json
```

A package is ready only when:

```text
readyForImport = true
```

The report includes:

- file sizes and SHA-256 hashes
- normalized `observedAt`
- matched and unmatched `matchupId`
- duplicate matchup and market diagnostics
- duplicate participant diagnostics
- orphan participant prices
- invalid price entries
- possible sensitive-key paths

## Import after review

```bash
odds-hub-import \
  --matchups /path/to/second-snapshot/matchups.json \
  --straight /path/to/second-snapshot/straight.json \
  --observed-at "2026-07-21T11:10:00+08:00" \
  --source pinnacle_manual \
  --bookmaker pinnacle \
  --dedupe-mode changes-only
```

Do not overwrite the first snapshot database or public archive files manually. Import into the existing SQLite history database so quote identities can be compared across time.

## Build history outputs

```bash
odds-hub-build-history \
  --database data/databases/odds_history.sqlite \
  --output-dir exports/history
```

Only quote identities with at least two distinct observation times become movement-ready.

## GitHub intake form

Use the repository issue form when the files are ready:

```text
https://github.com/qoo109/nba-odds-history-hub/issues/new?template=second-snapshot.yml
```

The files should be shared only after confirming they contain response bodies without credentials or private session material.
