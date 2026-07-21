# Project Status

Updated: 2026-07-21

## Current phase

**V0.14 — Public readiness schema compatibility and static release manifest ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.14 merge: 9ba2254b997312b787b843cec47d5a429b83350e
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

## V0.14 release evidence

```text
merge commit: 9ba2254b997312b787b843cec47d5a429b83350e
pull request: #31
test workflow run: 29814842727
test status: success
```

Published assets:

```text
data/public/readiness-release-manifest-v1.json
docs/readiness-release-v1.md
tests/test_public_readiness_contracts.py
```

The release manifest records both public readiness contracts:

```text
offseason-readiness-v1 — supported legacy contract
offseason-aggregate-metadata-readiness-v1 — current aggregate contract
```

Compatibility tests require both contracts to preserve:

```text
teams: 30
market classes: 11
fixture mode: true
current mode: offseason_sleep
```

## Preserved V0.13 aggregate state

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

## Privacy and execution boundary

```text
repository only: true
aggregate only: true
collection activated: false
production schedule imported: false
network calls made: false
external files read: false
cross-repository write: false
```

The public contracts contain no event rows, price rows, source URLs, provider names, credentials, cookies, sessions or authorization headers.

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
OFFSEASON_STATIC_RELEASE_INDEX_AND_CONTRACT_DRIFT_REPORT
```

The next safe task is to add a small static release index and a deterministic drift report that compares committed public contract versions and required shared fields. It must stay repository-only and must not activate collection or import production data.

## Safety boundary

- No private browser material or access configuration in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.14.
- No scheduled collection during offseason sleep mode.
