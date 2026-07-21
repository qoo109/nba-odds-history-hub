# Phase 2 one-time odds capture request v1

Request ID:

```text
ODDS-PHASE2-CAPTURE-2026-07-21-001
```

Formal state before approval:

```text
PHASE2_ODDS_CAPTURE_REQUEST_VALID_AWAITING_EXPLICIT_OWNER_APPROVAL
```

## Purpose

This packet prepares one manual Phase 2 attempt to obtain the second real NBA odds snapshot required by the multi-snapshot history builder.

It belongs only to `qoo109/nba-odds-history-hub`. It does not connect to or modify `qoo109/nba-value-lab`.

## What is prepared

The existing `.github/workflows/full-automation.yml` already supports a manual run with:

```text
enable_odds_capture = true
dry_run = false
```

The URL values must be stored only in the encrypted repository secrets:

```text
ODDS_MATCHUPS_URL
ODDS_STRAIGHT_URL
```

The request packet does not contain or reveal those URL values.

## Required approval

No capture may be executed until the owner explicitly approves this exact request ID.

The approval authorizes no more than one manual capture attempt against the two already reviewed and configured URLs. It does not authorize an hourly schedule, daily odds capture, source substitution, repeated attempts, or any write to NBA Value Lab.

## Source restrictions

The source must be lawful, free or publicly accessible, and explicitly owner-approved.

The capture may not require or use:

- account login;
- cookies or browser sessions;
- authorization headers or tokens;
- HAR files or private account exports;
- CAPTCHA, HTTP 403, geographic, robots, Terms of Service, or rate-limit bypasses.

OddsPortal, Covers, and Basketball Reference remain manual low-frequency QA sources and are not authorized for automated odds capture.

## Data contract

A successful capture must create:

```text
matchups.json
straight.json
metadata.json
```

`metadata.json` must preserve the true timezone-aware retrieval time as `observedAt`, plus the reviewed `sourceId` and `bookmakerId`.

Before import:

```text
readyForImport = true
```

must be produced by the existing intake validator.

Import must use `changes-only` retention and must not overwrite the first snapshot. Missing rows are never interpreted as unchanged prices.

## Output boundary

- No raw capture is committed to the public repository.
- No credentials, cookies, authorization headers, sessions, or HAR files are emitted.
- GitHub Actions Artifact retention remains 14 days.
- Google Drive automation remains disabled by default; backup is manual unless separately reconfigured.
- Opening and Closing labels remain unset.
- Market Backtest, CLV, EV, ROI, Drawdown, betting-edge claims, and staking remain blocked.
- Formal Stake remains `0`.

## After explicit approval

A separate approval record must be reviewed and merged before the workflow is dispatched. The one-time request must then be marked consumed whether the capture succeeds or fails, preventing silent retries under the same request ID.
