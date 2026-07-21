# Project Status

Updated: 2026-07-21

## Current phase

**V0.11 — Explicit source metadata and fixture schedule output gate ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.11 merge: a6e5b12c5ac9503bea606f209bda9df73782ad9f
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
- V0.11 explicit source metadata fields, fixture-only output gate, additive persistence tests, and per-file test diagnostics

## V0.11 validation evidence

```text
formal state: OFFSEASON_EXPLICIT_SOURCE_METADATA_AND_SCHEDULE_OUTPUT_GATE_V1_READY_WITH_PROVIDER_METADATA_GAPS
merge commit: a6e5b12c5ac9503bea606f209bda9df73782ad9f
validation workflow run: 29808510396
validation artifact id: 8486429903
validation artifact digest: sha256:2338024b3809ecd6b185d62ad765ef1ac0b57ac0fc3107c00cda8e6bdbeaec21
checks: 21 / 21
test workflow run: 29808510428
test files: 11 / 11
```

## Metadata status

Source registry upgrade:

```text
schema: v0.11-source-registry
records: 1
explicit active field: present
explicit reviewStatus field: present
explicit rightsStatus field: present
automation approved: false
new sources activated: 0
upgrade complete: true
```

The existing source remains manual-only. The metadata upgrade does not grant automated retrieval permission.

Provider registry status:

```text
schema: v0.3-bookmaker-registry
records: 1
missing explicit fields:
- definitionStatus
- supportedFormats
- dataScope
new providers activated: 0
upgrade complete: false
```

These remaining fields are recorded as pending rather than inferred.

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

Excluded aggregate reasons:

```text
historical alias: 1
unknown alias: 1
same team: 1
invalid id or time: 1
```

An identical schedule write is idempotent and returns `exact_current_schedule_duplicate` without creating another version.

## Preserved earlier evidence

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY — 34 / 34
OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY — 21 / 21
OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY — 30 / 30
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS — 24 / 24
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
OFFSEASON_PROVIDER_METADATA_EXPLICIT_UPGRADE_PENDING
```

The next safe task is a separately reviewed, backwards-compatible provider metadata upgrade. It must not change the manual-only source role, activate collection, import a production schedule, or create canonical event IDs.

## Safety boundary

- No private credentials or browser exports in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.11.
- No scheduled collection during offseason sleep mode.
