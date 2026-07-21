# Project Status

Updated: 2026-07-21

## Current phase

**V0.7 — Offseason reference foundation ready; live collection remains asleep**

This repository remains fully separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest reference merge: a4164ddd7a50eb054036f4cb0966ec84656b4591
current mode: offseason_sleep
daily source-health schedule: 09:11 Asia/Taipei
scheduled live collection: false
manual Phase 2 approval granted: false
Google Drive automatic backup default: false
backup mode: GitHub Actions Artifact + manual Drive upload
real snapshots: 1
movement-ready quote identities: 0
```

## Completed

- V0.2 importer, SQLite storage, exports, tests, and GitHub Actions
- V0.3 first real snapshot validation, public dashboard, source/bookmaker registries, QA report, and changes-only retention
- V0.4 grouped multi-snapshot history builder and second-snapshot intake gate
- V0.5 daily approved free/public source-health checks and 14-day safe Artifact output
- V0.6 disabled one-time Phase 2 request packet and approval gate
- V0.7 canonical NBA team registry, market taxonomy, exact event-identity policy, and dormant cadence templates

## Offseason reference foundation

Formal state:

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY
```

Evidence:

```text
workflow run: 29799499405
artifact id: 8483214949
artifact digest: sha256:b169859615391932b09c344d0b288c776106d71c91016a22222982032ce6bc70
checks: 34 / 34
```

Reference assets:

```text
config/nba-team-registry-v1.json
config/market-taxonomy-v1.json
config/offseason-capture-readiness-v1.json
data/offseason-reference-foundation-current-status-v1.json
```

Validated summary:

```text
teams: 30
East: 15
West: 15
divisions: 6
market classes: 11
dormant cadence templates: 5
active cadence templates: 0
```

## Identity and taxonomy rules

- All 30 active NBA teams have canonical abbreviations, conferences and divisions.
- Current source aliases are unique.
- Historical relocation aliases require season validation.
- Unknown team and market aliases are quarantined.
- Automatic fuzzy matching is disabled.
- Game and futures records are separated.
- Source market keys and source period codes remain preserved.
- Unverified source events remain `unmapped`.
- Exact event candidate key is scheduled date + home team + away team.
- Scores cannot repair event identity.

## Current real-data validation

```text
real snapshots: 1
futures markets: 5
quote identities: 91
movement-ready quote identities: 0
canonical mapping coverage: 0%
multi-observation history ready: false
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

The request remains valid but intentionally inactive during the offseason. It does not need approval now.

## Next unique mainline

```text
OFFSEASON_DATA_QUALITY_AND_MAPPING_FIXTURES
```

The next safe work is non-live infrastructure: canonical event-mapping fixtures, schedule import contracts, source/bookmaker metadata QA, database migrations, and dashboard readiness tests.

## Required activation gates later

1. Owner-reviewed lawful source.
2. Encrypted configuration only.
3. True timezone-aware observation time.
4. Scheduled event time and exact team identities.
5. Intake report accepted before import.
6. Changes-only retention.
7. Manual first-run review.
8. No automatic classification from a single observation.

## Safety boundary

- No login/session credentials or private browser exports in the repository.
- No access-control or website-policy bypass.
- No raw continuously changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No scheduled live collection during offseason sleep mode.
