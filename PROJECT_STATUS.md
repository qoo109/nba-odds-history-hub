# Project Status

Updated: 2026-07-21

## Current phase

**V0.5 — Daily lawful source health and GitHub Actions Artifact backup active; Phase 2 odds capture disabled**

This repository remains fully separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest main before this request: 281148b557171ee06c5254baba4ffcef69f3cd30
daily source-health schedule: 09:11 Asia/Taipei
scheduled odds capture: false
Google Drive automatic backup default: false
backup mode: GitHub Actions Artifact + manual Drive upload
real snapshots: 1
movement-ready quote identities: 0
formal stake: 0
```

## Completed

- V0.2 importer, SQLite storage, exports, tests, and GitHub Actions
- V0.3 first real snapshot validation, public dashboard, source/bookmaker registries, QA report, and changes-only retention
- V0.4 grouped multi-snapshot history builder and second-snapshot intake gate
- Stable quote identity excluding price and line values
- Distinct `observed_at` counting, duplicate-time detection, first/latest comparison, and dormant movement charts
- Three-file package validation: `matchups.json`, `straight.json`, and `metadata.json`
- Sensitive-key scanning, SHA-256 reporting, structural QA, and `readyForImport` gate
- V0.5 daily approved free/public source-health checks
- ETag, Last-Modified, file-size, SHA-256, and exact-duplicate tracking
- 14-day safe GitHub Actions Artifact output
- Optional Google Drive restore/upload implementation retained but disabled by default after the service-account quota failure
- Odds capture remains manual-dispatch only and disabled by default

## Current real-data validation

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
historical movement ready: false
executable market backtest ready: false
```

## Next unique mainline

```text
PHASE2_ODDS_CAPTURE_REQUEST_VALID_AWAITING_EXPLICIT_OWNER_APPROVAL
```

Request ID:

```text
ODDS-PHASE2-CAPTURE-2026-07-21-001
```

The request packet prepares exactly one manual Phase 2 capture attempt. It does not contain URL values and does not authorize execution.

Current request controls:

```text
approval granted: false
execution enabled: false
maximum execution count: 1
execution count: 0
manual workflow dispatch only: true
scheduled capture allowed: false
repeat execution allowed: false
NBA Value Lab write allowed: false
formal stake: 0
```

## Exact next input required

One of these two equivalent routes is required:

1. A second owner-supplied package containing `matchups.json`, `straight.json`, and `metadata.json`; or
2. Explicit owner approval of request `ODDS-PHASE2-CAPTURE-2026-07-21-001` after the two reviewed URL values are configured only as encrypted repository secrets.

The two secret names are:

```text
ODDS_MATCHUPS_URL
ODDS_STRAIGHT_URL
```

No URL value, cookie, authorization header, token, account export, or HAR file may be committed to the repository.

## Required capture and import gates

1. Source is lawful, free/public, and owner-approved.
2. No login, cookie/session, authorization token, CAPTCHA, geographic, robots, Terms of Service, HTTP 403, or rate-limit bypass.
3. OddsPortal, Covers, and Basketball Reference remain manual low-frequency QA only.
4. `observedAt` is the true timezone-aware retrieval time.
5. `sourceId` and `bookmakerId` are preserved.
6. Intake report must produce `readyForImport = true`.
7. Import uses `changes-only` retention and does not overwrite the first snapshot.
8. Intake and import-quality reports are reviewed before acceptance.
9. Only quote identities with at least two distinct observations may enter movement charts.
10. Opening and Closing labels remain unset unless independently verified.

## Research boundary

The current automation and request packet do not establish historical movement, Opening, Closing, point-in-time joins, executable market backtesting, CLV, EV, ROI, Drawdown, betting edge, or staking.

Formal Stake remains `0`.
