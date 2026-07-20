# Full automation: download, deduplicate, import, and Google Drive backup

This automation belongs only to `qoo109/nba-odds-history-hub`. It does not read from or write to `qoo109/nba-value-lab`.

## What runs automatically

The GitHub Actions workflow `.github/workflows/full-automation.yml` runs hourly and can also be started manually. Each run:

1. Restores the previous fingerprint state and current SQLite database from Google Drive.
2. Checks approved free/public sources using `ETag`, `Last-Modified`, URL, file size, and SHA-256.
3. Downloads only new or changed source files.
4. Builds an odds intake package from owner-configured `matchups` and `straight` URLs.
5. Requires `intake_report.json` to contain `readyForImport: true` before import.
6. Imports with `changes-only` deduplication and rebuilds grouped history exports.
7. Creates a timestamped compressed SQLite backup and SHA-256 sidecar.
8. Uploads immutable raw versions, backups, current SQLite, exports, reports, and persistent state to Google Drive.
9. Uploads a small 14-day GitHub Actions Artifact containing reports and safe run evidence.

The persistent state is deterministic rather than an opaque machine-learning model. It remembers prior URLs, ETags, Last-Modified values, SHA-256 fingerprints, and imported package identities. Exact repeats are recorded as `skipped_duplicate`; changed content becomes a new immutable version.

## Google Drive layout

The configured Drive folder is used as the root:

```text
raw/source_archive/
raw/odds_snapshots/
sqlite/odds_history.sqlite
exports/
reports/
backups/
state/automation_state.json
```

The workflow uses `rclone copy`, never `sync`, so it does not delete Drive history. Timestamped raw files and backups use `--immutable` and are not overwritten.

## Required GitHub Secrets

Create these under **Repository → Settings → Secrets and variables → Actions**:

| Secret | Purpose |
| --- | --- |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Full Google service-account JSON, stored only as an encrypted GitHub secret |
| `GDRIVE_FOLDER_ID` | Destination Drive folder ID |
| `ODDS_MATCHUPS_URL` | Owner-approved URL returning `matchups.json` data |
| `ODDS_STRAIGHT_URL` | Owner-approved URL returning `straight.json` data |

The current Drive destination folder ID is:

```text
1ms8f8WxnvN-n163kGQRhtnDVORB3Oqa7
```

Share that Drive folder with the service account's `client_email` as **Editor**. Never commit the service-account JSON, tokens, cookies, authorization headers, HAR files, or private account exports.

## Optional GitHub Variables

| Variable | Default |
| --- | --- |
| `ODDS_SOURCE_ID` | `configured_http_source` |
| `ODDS_SOURCE_NAME` | `Configured HTTP odds source` |
| `ODDS_BOOKMAKER_ID` | `configured_bookmaker` |
| `ODDS_BOOKMAKER_NAME` | `Configured bookmaker` |

## Source policy

`config/automation-sources.json` separates automatic and manual-only sources. Automatic checks stop on access controls, changed terms, HTTP 403, rate limits, or schema failures. OddsPortal, Covers, Basketball Reference, and unvalidated legacy archives remain manual-only.

A single snapshot is never labelled opening, closing, or movement. Real movement history requires at least two distinct `observed_at` values for the same stable market identity.

## First activation

1. Add the two Google Drive secrets.
2. Share the Drive folder with the service account email.
3. Add the two approved odds source URL secrets.
4. Run **Full odds download and Drive backup** manually with `dry_run=true`.
5. Inspect the Artifact and `latest_automation_report.json`.
6. Run once with `dry_run=false`.
7. Leave the hourly schedule enabled only after the first real intake passes.
