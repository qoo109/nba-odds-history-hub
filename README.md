# NBA Odds History Hub

NBA odds history ingestion, normalization, storage, visualization, and export hub for NBA Value Lab.

## Current status

**V0.1 — project bootstrap**

This repository will provide:

- Manual JSON import for `matchups` and `straight` responses
- Timestamped odds snapshots with `observed_at` and `ingested_at`
- American-to-decimal odds conversion
- Event, market, and participant normalization
- SQLite storage and deduplication
- CSV/JSON exports for NBA Value Lab
- A local dashboard for current odds and historical movement

## Data flow

```text
Source page data
      ↓
Manual JSON import
      ↓
Validation and normalization
      ↓
SQLite history database
      ↓
Dashboard and exports
      ↓
NBA Value Lab
```

## Public repository boundary

This repository contains source code, schemas, documentation, tests, and small sanitized samples. Large or continuously changing databases should be stored outside Git.

The project does not require all third-party data to remain private. Each source can be reviewed individually. Public samples should document their source and usage boundary.

## Security rules

- Never commit cookies, authorization headers, session tokens, passwords, or private account data.
- Preserve the true observation time separately from market cutoff and game start times.
- Keep source attribution and usage notes with each imported dataset.
- Do not bypass access controls, authentication, CAPTCHAs, or rate limits.

## Planned milestones

- **V0.1** Repository structure and data contract
- **V0.2** Pinnacle manual JSON importer
- **V0.3** SQLite history storage and deduplication
- **V0.4** Historical odds dashboard
- **V0.5** NBA Value Lab export contract
