# Project Status

Updated: 2026-07-21

## Current phase

**V0.16 — Public JSON Schema declarations and deterministic integrity manifest ready; collection remains asleep**

This repository remains separate from `qoo109/nba-value-lab`.

## Current control block

```text
latest V0.16 merge: 9a69d822db7fa47d928e40fbbbacb06c69208ca6
current mode: offseason_sleep
daily source-health schedule: 09:11 Asia/Taipei
scheduled collection: false
manual Phase 2 approval granted: false
real snapshots: 1
movement-ready quote identities: 0
```

## Completed through V0.16

- Import, normalized storage, exports and tests
- First snapshot dashboard and grouped history builder
- Daily public-source health checks
- Disabled one-time Phase 2 request packet
- Canonical teams, market taxonomy and dormant cadence templates
- Schedule-import contract and deterministic mapping fixtures
- Additive schedule-version and mapping-audit database layer
- Explicit source and provider metadata
- Fixture-only schedule output gate
- Aggregate readiness export and dashboard
- Public release manifest and compatibility tests
- Static release index and deterministic drift report
- Three Draft 2020-12 declarations and deterministic SHA-256 integrity manifest

## V0.16 validation evidence

```text
formal state: OFFSEASON_PUBLIC_JSON_SCHEMA_AND_CHECKSUM_MANIFEST_V1_READY
merge commit: 9a69d822db7fa47d928e40fbbbacb06c69208ca6
pull request: #35
focused workflow run: 29840324365
full test workflow run: 29840324295
artifact id: 8499063803
artifact digest: sha256:cffd2a3990a45716e8d2803f26f2e481feea3f69c5c8c4eb7a0d1d3452b8f185
schema declarations: 3
integrity assets: 8
algorithm: sha256
all workflows: success
```

Published assets:

```text
schemas/public/readiness-release-manifest-v1.schema.json
schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json
schemas/public/public-contract-drift-report-v1.schema.json
data/public/public-governance-checksums-v1.json
scripts/build_public_governance_checksums_v1.py
tests/test_public_contract_schema_checksums_v1.py
docs/public-data-declarations-v1.md
.github/workflows/validate-public-schema-checksums-v1.yml
```

## Declaration map

```text
data/public/readiness-release-manifest-v1.json
  -> schemas/public/readiness-release-manifest-v1.schema.json

data/public/offseason-metadata-readiness-v1.json
  -> schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json

data/public/readiness-contract-drift-report-v1.json
  -> schemas/public/public-contract-drift-report-v1.schema.json
```

The focused validator checks all three documents, exercises two negative fail-closed cases, rebuilds the integrity manifest and compares it byte-for-byte with the committed copy.

## Integrity manifest

```text
schema: public-governance-checksum-manifest-v1
release version: v0.14
asset count: 8
algorithm: sha256
deterministic ordering: true
self checksum excluded: true
```

## Preserved aggregate state

```text
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
contract drift count: 0
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
OFFSEASON_PRESEASON_ACTIVATION_GATE_AND_DRY_RUN_FIXTURES
```

The next safe task is to build a preseason activation checklist, season-configuration contract and synthetic dry-run package for schedule intake, mapping, database persistence and readiness state transitions. It must not retrieve an external schedule or enable live collection.

## Safety boundary

- No access-control or website-policy bypass.
- No large changing archives committed publicly.
- No automatic write to `qoo109/nba-value-lab`.
- No external schedule retrieval in V0.16.
- No scheduled collection during offseason sleep mode.
