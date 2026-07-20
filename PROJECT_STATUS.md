# Project Status

Updated: 2026-07-20

## Current phase

**V0.3 — Real snapshot validation and history-quality controls**

## Completed

- V0.2 Python package, CLI, importer, SQLite schema, exports, tests, and GitHub Actions
- First owner-supplied NBA Futures snapshot and GitHub Pages dashboard
- 5 futures markets, 91 options, 5 matched `matchupId`, 0 unmatched IDs in the reviewed public snapshot
- Formal import-quality report generator
- Matched/unmatched matchup reporting
- Duplicate market, matchup, and participant diagnostics
- Orphan participant and invalid price diagnostics
- `exact` and `changes-only` retention modes
- Strictly-prior comparison for out-of-order historical backfills
- Source and bookmaker registry tables
- Unmapped source-event placeholders for future NBA Value Lab joins
- Explicit canonical-event mapping functions
- Additive V0.2 SQLite migration
- Unit tests for QA reports, changed-price retention, out-of-order backfills, registries, mappings, and migration

## Validation boundary

The first public snapshot is still only one observation time. Historical movement, opening/closing labels, CLV, EV, ROI, and market backtesting remain blocked.

## Next milestone

**V0.4 — Multi-snapshot history builder**

1. Import a second owner-supplied raw `matchups.json` + `straight.json` pair with its true `observed_at`.
2. Review the generated quality report before accepting the snapshot.
3. Build a history export grouped by quote identity.
4. Add movement charts only for quotes with at least two observations.
5. Add source-health and snapshot-coverage summaries.
6. Define the first NBA Value Lab odds export contract without claiming executable backtest readiness.

## Research boundary

This repository is a data-engineering component. It does not by itself unlock NBA Value Lab point-in-time joins, closing-line validation, CLV, EV, ROI, betting edge, or staking.
