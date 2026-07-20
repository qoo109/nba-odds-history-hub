# Project Status

Updated: 2026-07-20

## Current phase

**V0.4 — Multi-snapshot history builder and second-snapshot intake gate ready**

## Completed

- V0.2 importer, SQLite storage, exports, tests, and GitHub Actions
- V0.3 real snapshot validation, public dashboard, QA report, registries, canonical mapping placeholders, and history-aware retention
- Stable quote identity that excludes price and line values
- Grouped quote-history export
- Distinct-observation counting and duplicate-observed-time flags
- First/latest quote comparison and movement direction
- Snapshot coverage summaries
- Source-health summaries that never treat missing rows as unchanged
- NBA Value Lab research export contract with `observed_at` preserved
- Explicit gates keeping opening/closing, executable backtest, CLV, EV, and ROI disabled
- `odds-hub-build-history` command
- Dashboard readiness card and movement chart renderer
- Public status file showing one real snapshot and zero movement-ready quotes
- `odds-hub-validate-intake` command
- Three-file intake package contract: `matchups.json`, `straight.json`, and `metadata.json`
- SHA-256, timezone, structural QA, and possible sensitive-key checks before import
- Public second-snapshot intake page and GitHub issue form

## Current real-data validation

- Real snapshots: 1
- Futures markets: 5
- Quote identities: 91
- Movement-ready quote identities: 0
- Canonical mapping coverage: 0%
- Historical movement ready: no
- Executable market backtest ready: no

## Exact next input required

A second owner-supplied package:

```text
matchups.json
straight.json
metadata.json
```

`metadata.json` must contain the true timezone-aware `observedAt`, `sourceId`, and `bookmakerId`.

The package must first produce:

```text
readyForImport = true
```

It must then be imported without overwriting the first snapshot. The intake report and generated import-quality report must both be reviewed before acceptance.

## Next milestone

**V0.4 data activation**

1. Receive the second real snapshot package.
2. Run the intake validator and review SHA-256, sensitive-key findings, and structural QA.
3. Import the snapshot with `changes-only` retention.
4. Confirm matched/unmatched IDs, duplicate diagnostics, and source health.
5. Generate grouped histories.
6. Publish only quote identities with at least two distinct observations to the movement chart.
7. Keep opening/closing labels unset unless their definitions are independently verified.
8. Begin canonical NBA Value Lab event mapping only with explicit, audited IDs.

## Research boundary

The history builder and intake gate being ready do not mean the project has historical movement data. With only one real `observed_at`, opening/closing classification, executable point-in-time joins, CLV, EV, ROI, betting edge, and staking remain blocked.
