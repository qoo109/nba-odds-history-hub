# Project Status

Updated: 2026-07-20

## Current phase

**V0.1 — Repository bootstrap and data contract**

## Objective

Build a standalone odds-history system that receives manually captured JSON, validates and normalizes it, stores timestamped snapshots, and exports stable data for NBA Value Lab.

## Completed

- Repository created
- Public code/data boundary documented
- Initial README added
- Ignore rules added for local databases, credentials, HAR files, and generated exports

## In progress

- Core odds conversion helpers
- Pinnacle `matchups` and `straight` manual importer
- SQLite schema
- Snapshot deduplication contract
- Command-line import workflow

## Next milestone

**V0.2 — First usable manual import pipeline**

Acceptance criteria:

1. Read one `matchups.json` and one `straight.json` file.
2. Validate required fields.
3. Join records by `matchupId` and `participantId`.
4. Add `observed_at` and `ingested_at` separately.
5. Convert American odds to decimal odds and raw implied probability.
6. Write normalized rows into SQLite.
7. Avoid inserting exact duplicate snapshots.
8. Export normalized CSV and JSON.

## Research boundary

This repository is a data-engineering component. It does not by itself unlock NBA Value Lab market backtesting. Point-in-time joins, closing-line validation, CLV, EV, ROI, and staking remain separate research gates.
