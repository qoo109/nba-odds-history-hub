# Source Metadata QA and Schedule Adapter v1

## Purpose

This offseason slice validates the existing source and provider registries, defines a future schedule-file adapter, and produces an aggregate mapping-status report from synthetic fixtures.

Expected state:

```text
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V1_READY_WITH_LEGACY_METADATA_GAPS
```

## Metadata QA

The existing V0.3 registries remain unchanged. The validator confirms unique IDs, valid source references, explicit usage boundaries, disabled automation, and provider notes.

The new metadata contract also records which explicit fields are still absent from the legacy registries. Those gaps remain visible rather than being inferred or silently filled. No new source or provider is activated.

## Schedule adapter

The adapter accepts a file-shaped schedule payload with:

```text
gameId
gameTimeUTC
homeTeam.teamTricode
awayTeam.teamTricode
```

Rules:

- timestamps must include a timezone;
- current team aliases may form an unverified candidate;
- historical aliases require season review and are quarantined;
- unknown teams are quarantined;
- same-team events are rejected;
- duplicate source event IDs are rejected;
- no canonical event ID is created automatically;
- fuzzy, score-assisted, and many-to-many matching remain disabled.

## Synthetic fixture

The six fixture cases contain two valid candidates, two quarantines, and two rejections. The validator checks every expected outcome and emits aggregate counts only.

## Boundary

The workflow reads repository fixtures only. It does not retrieve an external schedule, write to SQLite, publish row-level schedule data, activate collection, or write to NBA Value Lab.
