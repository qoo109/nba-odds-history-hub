# Preseason dry run v1

This stage validates the repository's schedule intake and persistence path with synthetic data only.

## Scope

- validate a season configuration
- process two timezone-aware fixture observations
- pass accepted rows through the existing schedule output gate
- preserve rejected and quarantined counts as aggregates
- register source-event placeholders without canonical IDs
- record audited candidate mapping decisions
- create additive schedule versions
- verify one schedule-time change
- verify exact replay idempotency
- produce a deterministic aggregate report

## Expected result

```text
formal state: OFFSEASON_PRESEASON_ACTIVATION_GATE_AND_DRY_RUN_FIXTURES_V1_READY
checks: 15 / 15
observations: 2
accepted rows: 5
excluded rows: 2
source events: 3
schedule versions: 5
current schedules: 3
audit decisions: 5
canonical IDs created: 0
```

The final simulated state is:

```text
preseason_dry_run_ready_awaiting_owner_approval
```

This state does not authorize a production schedule import or any recurring collection.

## Rebuild

```bash
python scripts/validate_preseason_dry_run_v1.py \
  --output runtime/reports/preseason-dry-run-v1.json
```

## Boundaries

```text
fixture only: true
external read: false
production import: false
scheduled collection: false
cross-repository write: false
row-level report output: false
```
