# Project Status

Updated: 2026-07-21

## Current phase

**V0.9 — Offseason database contracts and readiness dashboard are ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.9 merge: 2803e9f1edaca34dbe595b90ce89a672f3878623
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

## Offseason reference foundation

```text
formal state: OFFSEASON_REFERENCE_FOUNDATION_V1_READY
workflow run: 29799499405
artifact id: 8483214949
artifact digest: sha256:b169859615391932b09c344d0b288c776106d71c91016a22222982032ce6bc70
checks: 34 / 34
teams: 30
market classes: 11
active cadence templates: 0
```

## Offseason schedule mapping

```text
formal state: OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
workflow run: 29800088012
artifact id: 8483412043
artifact digest: sha256:bb35c2c983d0241fa27cc050110b1358b561e14214015f47aa2fb45082a88b04
checks: 21 / 21
fixture cases: 5 / 5
```

## Offseason database and dashboard

```text
formal state: OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY
workflow run: 29804012066
artifact id: 8484784752
artifact digest: sha256:cc7de32c80e06173d60124a696d4c837d0c75562171052eabcde71dad6c15c51
checks: 30 / 30
pytest run: 29804012062
pytest status: success
```

Database additions:

```text
source_event_schedule_versions
source_event_mapping_audit
current_source_event_schedules
source_event_mapping_status_summary
```

Validated fixture summary:

```text
source events: 2
schedule versions: 3
current schedules: 2
mapping decisions: 2
verified events: 1
multiple current schedule groups: 0
```

Public readiness assets:

```text
readiness.html
data/public/offseason-readiness.json
data/offseason-database-dashboard-current-status-v1.json
```

## Identity and versioning rules

- Source event ID and timezone-aware scheduled time are mandatory.
- Exact-current schedule duplicates are skipped.
- Schedule changes create a new preserved version.
- Only one current schedule version may exist per source event.
- Verified mappings require an existing canonical event ID.
- Rejected, quarantined, and unmapped states cannot retain a canonical ID.
- Invalid hashes, naive timestamps, unknown methods, and same-team events fail closed.
- Mapping decisions retain previous state, new state, reason, actor, and decision time.

## Current data validation

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
multi-observation history ready: false
production schedule imported: false
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
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_CONTRACT
```

The next safe work is source/provider metadata QA, adapter contracts for a future official schedule import, and aggregate mapping-status exports. It does not require external collection now.

## Safety boundary

- No private credentials or browser exports in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No scheduled collection during offseason sleep mode.
