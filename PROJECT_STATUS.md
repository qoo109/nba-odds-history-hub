# Project Status

Updated: 2026-07-21

## Current phase

**V0.8 — Offseason schedule and event-mapping contracts ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest schedule-mapping merge: 4655e51579b4607e6f71096a062f073753359620
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

Assets:

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
data/offseason-reference-foundation-current-status-v1.json
```

## Offseason schedule mapping

```text
formal state: OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
workflow run: 29800088012
artifact id: 8483412043
artifact digest: sha256:bb35c2c983d0241fa27cc050110b1358b561e14214015f47aa2fb45082a88b04
checks: 21 / 21
fixture cases: 5
verified fixture-only: 1
candidate unverified: 1
quarantined: 2
rejected: 1
```

Assets:

```text
config/schedule-import-contract-v1.json
data/fixtures/offseason-schedule-mapping-v1.json
data/offseason-schedule-mapping-current-status-v1.json
scripts/validate_offseason_schedule_mapping_v1.py
docs/offseason-schedule-mapping-v1.md
```

## Identity rules

- Current aliases may create an unverified candidate only.
- Historical aliases require season validation.
- Unknown aliases are quarantined.
- Identical home and away teams are rejected.
- Source event ID and timezone-aware scheduled time are mandatory.
- Canonical event ID may remain null until explicitly verified.
- Exact candidate key is scheduled date + home team + away team.
- Fuzzy, score-assisted, and many-to-many mapping are disabled.
- Schedule changes create a new version and preserve the prior value.

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
OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES
```

The next safe work is additive database mapping tables, metadata QA, mapping-status exports, and dashboard readiness fixtures.

## Safety boundary

- No private credentials or browser exports in the repository.
- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No scheduled collection during offseason sleep mode.
