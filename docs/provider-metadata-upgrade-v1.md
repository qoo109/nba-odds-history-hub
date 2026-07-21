# Provider Metadata Upgrade v1

This offseason change completes explicit fields for the existing provider record.

Expected validation states:

```text
OFFSEASON_SOURCE_PROVIDER_METADATA_QA_AND_SCHEDULE_ADAPTER_V2_READY
OFFSEASON_EXPLICIT_SOURCE_PROVIDER_METADATA_AND_SCHEDULE_OUTPUT_GATE_V2_READY
```

The registry now records a stable provider ID, definition status, supported format, data scope, automation status, and metadata version.

The existing record remains a source label for owner-supplied manual snapshots. No new source or provider is added, no collection permission changes, and no production schedule is imported.

The fixture output gate continues to accept only two current-alias candidate rows. Historical aliases, unknown aliases, same-team records, and invalid timestamps remain excluded. It creates no canonical event IDs and writes no market snapshot rows.

Validation uses repository metadata and synthetic fixtures only. It makes no network calls and writes to no other repository.
