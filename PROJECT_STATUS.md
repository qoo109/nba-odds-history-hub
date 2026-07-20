# Project Status

Updated: 2026-07-20

## Current phase

**V0.3 — First real NBA Futures snapshot and public dashboard**

## Completed

- V0.2 Python package, CLI, importer, SQLite schema, exact deduplication, exports, tests, and GitHub Actions
- First owner-supplied NBA Futures snapshot prepared for public validation
- Static GitHub Pages dashboard added
- Snapshot split into an index and five market files
- Manifest added with SHA-256, counts, matched/unmatched IDs, and quality flags
- Browser-generated full JSON and CSV downloads added
- Public snapshot tests added

## First real snapshot validation

- Source mode: manual browser capture supplied by repository owner
- Bookmaker label: Pinnacle
- `observed_at`: `2026-07-20T11:10:00+08:00`
- Futures markets: 5
- Options: 91
- Matched `matchupId`: 5
- Unmatched `matchupId`: 0
- Duplicate market IDs: 0
- Duplicate participant IDs within a market: 0
- Local public-snapshot tests: 3 passed
- Historical movement ready: no — only one observation time exists

## Pull request validation

GitHub Actions must pass before merge. CI proves execution only; the manifest and QA counts must also be reviewed.

## Next V0.3 slice

1. Run the repository importer against the original raw `matchups.json` and `straight.json` pair.
2. Emit a formal matched/unmatched import quality report.
3. Add change-aware deduplication.
4. Add bookmaker and source registry tables.
5. Add canonical event identity placeholders for NBA Value Lab joins.
6. Add movement charts only after a second `observed_at` snapshot exists.

## Research boundary

This repository remains a data-engineering component. The dashboard does not unlock point-in-time NBA Value Lab backtesting, CLV, EV, ROI, or staking.
