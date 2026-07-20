# Full automation: phased source health, download, deduplicate, import, and Google Drive backup

This automation belongs only to `qoo109/nba-odds-history-hub`. It does not read from or write to `qoo109/nba-value-lab`.

## Phase 1 — active before NBA odds capture

The workflow `.github/workflows/full-automation.yml` runs every day at 09:11 Asia/Taipei and can also be started manually. Scheduled runs are intentionally **source-health only**. They do not expose the configured odds URLs and therefore cannot import live odds.

Each Phase 1 run:

1. Restores the previous fingerprint state and any existing SQLite database from Google Drive.
2. Checks approved free/public sources using `ETag`, `Last-Modified`, URL, file size, and SHA-256.
3. Downloads only new or changed source files.
4. Records exact duplicates as `skipped_duplicate`.
5. Creates source-health and automation reports.
6. Uploads immutable raw versions, current reports, persistent state, exports, backups, and SQLite to Google Drive.
7. Uploads a small 14-day GitHub Actions Artifact containing reports and safe run evidence.

The persistent state is deterministic rather than an opaque machine-learning model. It remembers prior URLs, ETags, Last-Modified values, SHA-256 fingerprints, and imported package identities.

## Phase 2 — odds capture, intentionally disabled for now

Odds capture runs only from a manual workflow dispatch with `enable_odds_capture=true`. It also requires both `ODDS_MATCHUPS_URL` and `ODDS_STRAIGHT_URL` secrets. Scheduled daily runs never use those secrets.

When later enabled, the pipeline:

1. Downloads the owner-approved `matchups` and `straight` JSON responses.
2. Builds `metadata.json` with `observedAt`, source, bookmaker, and a package fingerprint.
3. Requires `intake_report.json` to contain `readyForImport: true` before import.
4. Imports with `changes-only` deduplication and rebuilds grouped history exports.
5. Creates a timestamped compressed SQLite backup and SHA-256 sidecar.

Before the NBA season or desired monitoring window begins, a separate reviewed change can switch from daily source health to hourly odds snapshots.

## Google Drive layout

The configured Drive folder is used as the root:

```text
00-incoming/odds_snapshots/
01-raw-snapshots/source_archive/
02-sqlite/odds_history.sqlite
03-exports/
04-source-health/
05-backups/
06-logs/
07-state/automation_state.json
99-quarantine/
```

The workflow uses `rclone copy`, never `sync`, so it does not delete Drive history. Timestamped raw files and backups use `--immutable` and are not overwritten.

## Required Phase 1 GitHub Secrets

Create these under **Repository → Settings → Secrets and variables → Actions**:

| Secret | Purpose |
| --- | --- |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Full Google service-account JSON, stored only as an encrypted GitHub secret |
| `GDRIVE_FOLDER_ID` | Destination Drive folder ID |

The Drive destination folder ID is:

```text
1ms8f8WxnvN-n163kGQRhtnDVORB3Oqa7
```

Share that Drive folder with the service account's `client_email` as **Editor**. Never commit the service-account JSON, tokens, cookies, authorization headers, HAR files, or private account exports.

## Phase 2 secrets, not required yet

| Secret | Purpose |
| --- | --- |
| `ODDS_MATCHUPS_URL` | Owner-approved URL returning `matchups.json` data |
| `ODDS_STRAIGHT_URL` | Owner-approved URL returning `straight.json` data |

## Optional GitHub Variables

| Variable | Default |
| --- | --- |
| `ODDS_SOURCE_ID` | `configured_http_source` |
| `ODDS_SOURCE_NAME` | `Configured HTTP odds source` |
| `ODDS_BOOKMAKER_ID` | `configured_bookmaker` |
| `ODDS_BOOKMAKER_NAME` | `Configured bookmaker` |

## Safety boundaries

- No cookies, authorization headers, session tokens, HAR files, or private account data.
- No bypass of authentication, CAPTCHA, HTTP 403, robots, rate limits, or Terms of Service.
- OddsPortal, Covers, Basketball Reference, and unvalidated SBR legacy data remain manual-only.
- A single snapshot is never labelled opening, closing, or movement.
- No file deletion or history overwrite is performed on Google Drive.
