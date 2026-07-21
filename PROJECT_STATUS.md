# Project Status

Updated: 2026-07-21

## Current phase

**V0.10 — Source/provider metadata QA and fixture schedule adapter validated; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.10 merge: b61d25843447adadaa4214098d4082f29ff25864
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

## Source/provider metadata and schedule adapter

```text
formal state: OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS
merge commit: b61d25843447adadaa4214098d4082f29ff25864
test workflow run: 29806193268
test status: success
checks: 24 / 24
```

Assets:

```text
config/source-provider-metadata-contract-v1.json
config/official-schedule-adapter-contract-v1.json
data/fixtures/official-schedule-adapter-v1.json
data/offseason-provider-schedule-adapter-current-status-v1.json
src/nba_odds_history_hub/schedule_adapter.py
scripts/validate_source_provider_schedule_adapter_v1.py
tests/test_source_provider_schedule_adapter_v1.py
docs/source-provider-schedule-adapter-v1.md
```

Metadata QA result:

```text
sources checked: 1
providers checked: 1
new sources activated: 0
new providers activated: 0
legacy metadata upgrade required: true
```

The V0.3 source registry still lacks explicit `active`, `reviewStatus`, and `rightsStatus` fields. The V0.3 provider registry still lacks explicit `definitionStatus`, `supportedFormats`, and `dataScope` fields. These gaps are recorded instead of inferred.

Fixture schedule adapter result:

```text
fixture games: 6
candidate unverified: 2
quarantined: 2
rejected: 2
canonical event IDs created: 0
database rows written: 0
```

Adapter rules:

- Input event ID is preserved as the source event ID.
- Timestamps must contain a timezone and normalize to UTC.
- Current team aliases may form an unverified candidate.
- Historical aliases require season review and are quarantined.
- Unknown teams are quarantined.
- Same-team, invalid-time, and duplicate-ID cases are rejected.
- Canonical event IDs are never created automatically.
- Fuzzy, score-assisted, and many-to-many mapping remain disabled.

## Current data validation

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
OFFSEASON_EXPLICIT_METADATA_REGISTRY_UPGRADE_AND_SCHEDULE_ADAPTER_OUTPUT_GATE
```

The next safe work is a backwards-compatible registry upgrade adding the missing explicit review/definition fields, followed by a fixture-only adapter-output gate for the additive schedule-version database. It does not require an external schedule or live collection.

## Safety boundary

- No private credentials or browser exports in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval or database import in V0.10.
- No scheduled collection during offseason sleep mode.
