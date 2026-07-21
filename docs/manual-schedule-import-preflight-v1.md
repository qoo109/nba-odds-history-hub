# Manual schedule import preflight v1

V0.18 adds a disabled, repository-only rehearsal for a future owner-reviewed schedule import. It does not authorize or execute a production import.

## Three stages

### 1. Identity and schema preflight

The target fixture is locked by repository path, filename, byte count, SHA-256, schema version and season ID. A mismatch fails closed before database work begins.

### 2. Aggregate preview

The existing schedule output gate processes two synthetic observations and emits aggregate counts only. The expected result is five accepted rows, two excluded rows and three unique source events. Excluded row details are not published.

### 3. Transaction rollback and post-check

The accepted fixture rows are written to a temporary SQLite transaction. The rehearsal checks source events, schedule versions, current schedules and mapping audits inside the transaction, then always rolls back. Every target table must contain zero rows afterward.

## Disabled boundary

```text
owner approval granted: false
execution enabled: false
maximum execution count: 0
external file allowed: false
production database allowed: false
production import allowed: false
network calls allowed: false
scheduled collection allowed: false
canonical event ID creation allowed: false
cross-repository write allowed: false
```

The dry run uses `data/fixtures/preseason-dry-run-v1.json` only. It does not read an external schedule, create canonical NBA game IDs, write odds rows, or modify `qoo109/nba-value-lab`.

## Run locally

```bash
python scripts/validate_manual_schedule_preflight_v1.py \
  --output runtime/reports/manual-schedule-import-preflight-v1.json
```

Run focused tests:

```bash
pytest -q tests/test_manual_schedule_preflight_v1.py
```
