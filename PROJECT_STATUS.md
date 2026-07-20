# Project Status

Updated: 2026-07-20

## Current phase

**V0.2 — First usable manual import pipeline implemented**

## Objective

Build a standalone odds-history system that receives manually captured JSON, validates and normalizes it, stores timestamped snapshots, and exports stable data for NBA Value Lab.

## Completed

- Repository created
- Public code/data boundary documented
- Python package and CLI configured
- American-to-decimal conversion implemented
- Raw implied probability calculation implemented
- Pinnacle-style `matchups` and `straight` manual normalizer implemented
- Futures records joined by `matchupId` and `participantId`
- SQLite schema implemented
- Separate `observed_at`, `ingested_at`, `scheduled_tipoff`, and `cutoff_at` fields
- Exact-snapshot deduplication implemented
- CSV and JSON exports implemented
- Synthetic sample payloads added
- Unit and integration tests added
- GitHub Actions test workflow added
- Manual import and data-contract documentation added

## Validation status

- Code review: completed for the first implementation slice
- Automated test workflow: added; latest run must be checked in GitHub Actions
- Real captured Pinnacle files: not committed to the public repository
- General NBA game markets: parser support is provisional and requires real-file validation

## Next milestone

**V0.3 — Real snapshot validation and history-quality controls**

Planned work:

1. Validate the importer against the captured NBA Futures files.
2. Add an import quality report showing matched and unmatched `matchupId` values.
3. Add change-aware deduplication options.
4. Add bookmaker and source registry tables.
5. Add canonical event identity placeholders for NBA Value Lab joins.
6. Add a browser dashboard for current snapshots and historical movement.

## Research boundary

This repository is a data-engineering component. It does not by itself unlock NBA Value Lab market backtesting. Point-in-time joins, closing-line validation, CLV, EV, ROI, and staking remain separate research gates.
