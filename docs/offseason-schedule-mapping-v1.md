# Offseason Schedule Mapping Contract v1

This slice prepares deterministic schedule and event-identity rules before live collection begins.

Formal validation state:

```text
OFFSEASON_SCHEDULE_MAPPING_CONTRACT_V1_READY
```

## Inputs

A schedule record must preserve source ID, source event ID, timezone-aware scheduled time, source timezone, home and away aliases, retrieval time and payload hash.

## Mapping rules

- canonical event ID may remain null until verified;
- exact candidate key is scheduled date + home + away;
- current aliases may form an unverified candidate;
- historical aliases require season review;
- unknown aliases are quarantined;
- same-team events are rejected;
- fuzzy, score-assisted and many-to-many matching are disabled;
- manual mappings require an audit record.

## Synthetic fixtures

`data/fixtures/offseason-schedule-mapping-v1.json` contains five non-production cases:

1. current aliases produce an unverified candidate;
2. an explicit fixture-only ID produces a verified fixture;
3. a historical alias is quarantined;
4. an unknown alias is quarantined;
5. identical home and away teams are rejected.

## Validation boundary

The workflow reads only repository contracts and synthetic fixtures. It makes no network calls, imports no schedule, emits no raw rows, and writes to no other repository.
