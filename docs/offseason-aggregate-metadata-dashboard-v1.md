# Offseason Aggregate Metadata Dashboard v1

V0.13 combines the static team, market, source, provider, capture-readiness, Phase 2, and synthetic schedule-fixture states into one public aggregate JSON file.

Formal state:

```text
OFFSEASON_AGGREGATE_METADATA_EXPORT_AND_READINESS_DASHBOARD_V1_READY
```

## Public export

```text
data/public/offseason-metadata-readiness-v1.json
```

The export contains counts and readiness booleans only. It does not contain source links, named source records, named provider records, event IDs, event rows, price rows, or external payload content.

## Builder

```text
scripts/build_offseason_aggregate_metadata_export_v1.py
```

The builder reads repository metadata and synthetic fixtures only. It performs no network request and writes to no database or other repository.

It fails closed when metadata fields are missing, automation permission changes, collection becomes active, Phase 2 becomes executable, fixture counts drift, or research gates open unexpectedly.

## Dashboard

`readiness.html` displays team and market counts, source and provider counts, metadata gaps, automation approvals, fixture output-gate counts, Phase 2 status, historical-movement readiness, and aggregate-only status.

## Reproducibility

```bash
python scripts/build_offseason_aggregate_metadata_export_v1.py \
  --as-of 2026-07-21 \
  --output /tmp/offseason-metadata-readiness-v1.json
```

CI compares the generated document with the committed public export. Any drift fails validation.

## Boundaries

- no external schedule retrieval;
- no live or scheduled collection;
- no new source or provider activation;
- no canonical event creation;
- no snapshot import;
- no cross-repository write;
- Phase 2 remains unapproved and disabled.
