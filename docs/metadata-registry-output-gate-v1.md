# Metadata Registry and Schedule Output Gate v1

## Purpose

This offseason slice upgrades explicit source metadata and proves that fixture-only schedule adapter output can enter the additive schedule-version database without importing rejected or quarantined records.

Expected state:

```text
OFFSEASON_EXPLICIT_SOURCE_METADATA_AND_SCHEDULE_OUTPUT_GATE_V1_READY_WITH_PROVIDER_METADATA_GAPS
```

## Source metadata upgrade

`config/source-registry.json` now explicitly records:

- `active`
- `reviewStatus`
- `rightsStatus`
- `metadataVersion`

The existing source remains manual-only and `automationApproved` remains false. No new source is activated.

## Provider metadata status

The legacy provider registry remains compatible with existing code, but still lacks explicit:

- `definitionStatus`
- `supportedFormats`
- `dataScope`

The validator reports these as unresolved metadata gaps. It does not infer values or change access permissions.

## Schedule adapter output gate

The gate accepts only `candidate_unverified` fixture records with:

- a valid source event ID;
- timezone-aware scheduled time;
- resolved and distinct current team aliases;
- preserved source observation time and payload hash.

Accepted fixture records may create:

- a source-event placeholder;
- one schedule-version record;
- one audited mapping decision.

The gate does not create canonical event IDs or market snapshot rows.

Rejected and quarantined fixture records are excluded from database persistence and represented only by aggregate reason counts.

## Validation fixture

From six fixture games:

```text
accepted candidate records: 2
quarantined records: 2
rejected records: 2
```

Expected fixture database state:

```text
source events: 2
schedule versions: 2
mapping audit decisions: 2
verified events: 0
canonical events created: 0
snapshot rows written: 0
multiple current schedule groups: 0
```

Writing an identical schedule record a second time must return `exact_current_schedule_duplicate` and must not create a second version.

## Boundary

- fixture data only;
- no network calls;
- no external schedule read;
- no raw row or file output;
- no cross-repository write;
- no production schedule import;
- no live collection activation.
