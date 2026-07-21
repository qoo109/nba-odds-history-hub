# Static Release Index and Contract Drift Report v1

This repository publishes a small static release index for the two supported public readiness contracts.

## Assets

```text
release-index.html
data/public/readiness-release-manifest-v1.json
data/public/readiness-contract-drift-report-v1.json
scripts/build_public_contract_drift_report_v1.py
```

## Compared shared fields

```text
summary.teams
summary.marketClasses
fixtureMode
currentMode
```

The report also checks each committed schema version against the release manifest and verifies the inactive repository-only boundary.

## Fail-closed behavior

A mismatch produces:

```text
OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_DRIFT_DETECTED
```

and a non-zero script exit code. CI rejects schema drift, shared-field drift, collection activation, production import, network use, external file reads, or cross-repository writes.

## Current boundary

- Repository metadata and synthetic fixtures only.
- No external schedule retrieval.
- No live collection activation.
- No production import.
- No row-level event or quote data in the report.
- No write to `qoo109/nba-value-lab`.
