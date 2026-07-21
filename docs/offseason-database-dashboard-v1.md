# Offseason Database Contract and Dashboard Fixtures v1

## Purpose

This step builds additive database structures and a public readiness page before any new external schedule or multi-observation data is collected.

Expected validation state:

```text
OFFSEASON_DATABASE_CONTRACT_AND_DASHBOARD_FIXTURES_V1_READY
```

## Additive database structures

`sql/schema.sql` now includes two new tables:

```text
source_event_schedule_versions
source_event_mapping_audit
```

and two aggregate/current-state views:

```text
current_source_event_schedules
source_event_mapping_status_summary
```

Existing import, snapshot, source, bookmaker and canonical-event tables are preserved.

### Schedule versions

A new version is inserted only when the current scheduled time, teams, mapping state, method or payload hash changes. One source event may have many historical versions but only one current version.

Stored fields include:

- source and source event ID;
- version number;
- timezone-aware scheduled time;
- canonical home and away team abbreviations;
- mapping status and method;
- observation time;
- source payload SHA-256;
- current-version flag.

### Mapping audit

Every explicit mapping decision may record:

- previous and new status;
- canonical event ID when verified;
- mapping method;
- reason code;
- actor type;
- decision time;
- optional payload hash and note.

The contract supports `unmapped`, `candidate_unverified`, `verified`, `rejected`, `quarantined`, and the legacy `mapped` status.

## Python helpers

`src/nba_odds_history_hub/mapping.py` provides:

```text
record_schedule_version
record_mapping_decision
build_mapping_readiness_report
write_mapping_readiness_report
```

The helpers reject naive timestamps, invalid hashes, same-team events, unknown methods, verified mappings without a canonical event ID, and rejected/quarantined states that still carry a canonical ID.

## Dashboard fixture

`readiness.html` loads:

```text
data/public/offseason-readiness.json
```

It displays the current static foundation, mapping contract, database structures and intentionally waiting modules. It does not load an external schedule or fabricate a second observation.

## Validation fixture

The dedicated validator creates a temporary SQLite database with two synthetic source events. It checks:

1. version 1 insertion;
2. exact-current duplicate skipping;
3. changed scheduled time creating version 2;
4. exactly one current version per event;
5. one verified and one quarantined mapping decision;
6. mapping audit rows;
7. aggregate readiness output;
8. public readiness JSON and HTML references.

## Runtime boundary

Pull-request validation:

- reads repository fixtures only;
- makes no network calls;
- imports no official or external schedule;
- emits no raw rows or raw source files;
- performs no cross-repository write;
- leaves recurring collection inactive.

## Next step after validation

The next safe offseason slice is source/provider metadata QA plus a production-schedule adapter contract. A real schedule import remains a separate reviewed action.
