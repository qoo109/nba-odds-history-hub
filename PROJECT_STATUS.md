# Project Status

Updated: 2026-07-21

## Current phase

**V0.15 — Static public release index and deterministic contract drift report ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.15 merge: a5c20df88f64c0216e447f74baff9d131524de1d
current mode: offseason_sleep
daily source-health schedule: 09:11 Asia/Taipei
scheduled collection: false
manual Phase 2 approval granted: false
backup mode: GitHub Actions Artifact + manual Drive upload
real snapshots: 1
movement-ready quote identities: 0
```

## Completed

- V0.2 importer, storage, exports, tests and Actions
- V0.3 first snapshot validation and dashboard
- V0.4 grouped history builder and second-snapshot gate
- V0.5 public-source health checks
- V0.6 disabled one-time Phase 2 request packet
- V0.7 canonical teams, market taxonomy and dormant cadence templates
- V0.8 schedule-import contract and mapping fixtures
- V0.9 additive schedule-version and mapping-audit database layer
- V0.10 source/provider metadata QA and fixture adapter
- V0.11 explicit source metadata and output gate
- V0.12 explicit provider metadata and completed metadata validation
- V0.13 aggregate metadata export and readiness dashboard
- V0.14 static public release manifest and compatibility tests
- V0.15 static release index, deterministic drift report, fail-closed tests and focused validation

## V0.15 validation evidence

```text
formal state: OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_READY
merge commit: a5c20df88f64c0216e447f74baff9d131524de1d
pull request: #33
focused workflow run: 29818988525
full test workflow run: 29818988517
validation artifact id: 8490529626
validation artifact digest: sha256:f20031ea9b0a48ef98358044b72584b6e0d813b943bd801d6caa7eaf66067794
checks: 9 / 9
drift count: 0
all workflows: success
```

Published assets:

```text
release-index.html
data/public/readiness-contract-drift-report-v1.json
scripts/build_public_contract_drift_report_v1.py
tests/test_readiness_release_index_drift_v1.py
docs/static-release-index-drift-v1.md
.github/workflows/validate-public-contract-drift-v1.yml
```

V0.15 adds release-governance tooling around the existing V0.14 public contracts. It does not silently change either public readiness schema.

## Public contract comparison

The drift report compares:

```text
legacy readiness schema: offseason-readiness-v1
aggregate readiness schema: offseason-aggregate-metadata-readiness-v1
release manifest schema: readiness-release-manifest-v1
drift report schema: public-contract-drift-report-v1
```

Required shared values remain:

```text
teams: 30
market classes: 11
fixture mode: true
current mode: offseason_sleep
```

Current result:

```text
contract schema mismatches: 0
fixture flag mismatches: 0
missing shared fields: 0
shared field drift: 0
unsafe release-boundary checks: 0
```

The validator fails closed when the release version, committed schema, shared field, or inactive execution boundary changes unexpectedly.

## Static release index

`release-index.html` reads only:

```text
data/public/readiness-release-manifest-v1.json
data/public/readiness-contract-drift-report-v1.json
```

It displays contract IDs, schema versions, compatibility state, shared-field comparisons, checks passed and detected drift count.

## Privacy and execution boundary

```text
repository only: true
fixture only: true
aggregate only: true
row-level records included: false
collection activated: false
production schedule imported: false
network calls made: false
external files read: false
cross-repository write: false
```

The public governance assets contain no event rows, price rows, source URLs, provider names, credentials, cookies, sessions or authorization headers.

## Preserved aggregate state

```text
formal state: OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY
teams: 30
market classes: 11
sources: 1
providers: 1
metadata missing fields: 0
automation approvals: 0
active cadence templates: 0
fixture schedule games: 6
fixture accepted: 2
fixture excluded: 4
```

## Current real-data state

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
multi-observation history ready: false
production schedule imported: false
external schedule read: false
```

## Phase 2 request

```text
request id: ODDS-PHASE2-CAPTURE-2026-07-21-001
request state: awaiting explicit owner approval
approval granted: false
execution enabled: false
execution count: 0
maximum execution count: 1
```

The request remains inactive during the offseason.

## Next unique mainline

```text
OFFSEASON_PUBLIC_CONTRACT_JSON_SCHEMA_DECLARATIONS_AND_CHECKSUMS
```

The next safe task is to publish machine-readable JSON Schema declarations for the public release manifest, aggregate readiness export and drift report, then generate deterministic checksums for committed public governance assets. It must remain repository-only and must not activate collection, retrieve an external schedule or import production data.

## Safety boundary

- No private browser material or access configuration in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.15.
- No scheduled collection during offseason sleep mode.
