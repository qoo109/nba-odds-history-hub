# Project Status

Updated: 2026-07-21

## Current phase

**V0.12 — Explicit source and provider metadata complete; fixture schedule output gate remains ready**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.12 merge: b511e4a2c25b452b5c7a5ae1eceb74b1449f2bc2
current mode: offseason_sleep
daily source-health schedule: 09:11 Asia/Taipei
scheduled collection: false
manual Phase 2 approval granted: false
backup mode: GitHub Actions Artifact + manual Drive upload
real snapshots: 1
movement-ready quote identities: 0
```

## Completed

- V0.2 importer, SQLite storage, exports, tests, and GitHub Actions
- V0.3 first snapshot validation, dashboard, registries, QA report, and changes-only retention
- V0.4 grouped history builder and second-snapshot intake gate
- V0.5 daily public-source health checks and safe Artifact output
- V0.6 disabled one-time Phase 2 request packet
- V0.7 canonical team registry, market taxonomy, event-identity policy, and dormant cadence templates
- V0.8 schedule-import contract and deterministic synthetic event-mapping fixtures
- V0.9 additive schedule-version tables, mapping-audit tables, helper functions, tests, and readiness page
- V0.10 source/provider metadata gap audit, fixture schedule adapter, and aggregate mapping-status validation
- V0.11 explicit source metadata fields and fixture-only output gate
- V0.12 explicit provider metadata fields and completed metadata validation

## V0.12 validation evidence

```text
formal state 1: OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V2_READY
formal state 2: OFFSEASON_EXPLICIT_SOURCE_PROVIDER_METADATA_AND_SCHEDULE_OUTPUT_GATE_V2_READY
merge commit: b511e4a2c25b452b5c7a5ae1eceb74b1449f2bc2
validation workflow run: 29810808509
validation artifact id: 8487322908
validation artifact digest: sha256:bc475505dbef497007326794d447edc838c7d6ff8e80e20a6ac2b4fc89e42acc
metadata and adapter checks: 28 / 28
output gate checks: 26 / 26
test workflow run: 29810808595
test status: success
```

## Metadata status

Source registry:

```text
schema: v0.11-source-registry
records: 1
missing explicit fields: 0
automation approved: false
upgrade complete: true
```

Provider registry:

```text
schema: v0.12-provider-registry
records: 1
provider ID: pinnacle
definition status: source_label_only
supported formats: american
data scope: owner_supplied_nba_futures_snapshots
automation approved: false
missing explicit fields: 0
upgrade complete: true
```

The provider record remains a descriptive label for existing owner-supplied manual snapshots. The metadata upgrade does not add access capability, expand coverage claims, or activate collection.

## Fixture schedule output gate

```text
fixture games: 6
accepted candidate_unverified records: 2
excluded records: 4
source events registered: 2
schedule versions inserted: 2
mapping audit decisions written: 2
canonical events created: 0
snapshot rows written: 0
verified events: 0
multiple current schedule groups: 0
```

Excluded aggregate reasons remain:

```text
historical alias: 1
unknown alias: 1
same team: 1
invalid ID or time: 1
```

An identical schedule write remains idempotent and creates no new version.

## Preserved earlier evidence

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY — 34 / 34
OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY — 21 / 21
OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY — 30 / 30
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS — 24 / 24
OFFSEASON_EXPLICIT_SOURCE_METADATA_AND_SCHEDULE_OUTPUT_GATE_V1_READY_WITH_PROVIDER_METADATA_GAPS — 21 / 21
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
OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_SYNC
```

The next safe task is to generate a privacy-safe aggregate metadata export and connect it to the offseason readiness dashboard. It must use repository metadata and synthetic fixtures only, without external retrieval or production imports.

## Safety boundary

- No private credentials or browser exports in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.12.
- No scheduled collection during offseason sleep mode.
