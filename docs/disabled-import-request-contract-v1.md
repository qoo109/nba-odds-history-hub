# Disabled import request contract and backup/restore fixtures v1

V0.21 defines the next fixture-only governance layer after the V0.20 approval state machine. It does not request approval and does not authorize a production schedule import.

## Bound synthetic identity

The contract binds only the committed repository fixture:

```text
path: data/fixtures/preseason-dry-run-v1.json
filename: preseason-dry-run-v1.json
bytes: 2204
sha256: 1e91072905dc8b68972fee255d85146eae171bfa9ae539faad25b1246d942512
schema: preseason-dry-run-fixture-v1
season: 2026-27
```

Any path, filename, byte-count, hash, schema or season change remains subject to the V0.20 fail-closed re-preflight rules.

## Disabled request boundary

```text
approval requested: false
approval recorded: false
approval granted: false
execution enabled: false
maximum execution count: 0
approved production database path: null
production backup id: null
external schedule read: false
production database access: false
production import: false
network calls: false
scheduled collection: false
canonical event ID creation: false
cross-repository write: false
shell command emitted: false
```

The contract contains no runnable production command, no argument vector and no production implementation module.

## Synthetic backup/restore fixture

The validator creates a new SQLite database inside a process-owned temporary directory. It then:

1. initializes the normal schema;
2. inserts one synthetic source event and aggregate schedule/audit records;
3. copies the closed SQLite file to a temporary backup;
4. mutates the temporary database with a second synthetic event;
5. restores the backup bytes over the mutated database;
6. verifies the restored SHA-256 and aggregate table counts;
7. confirms that canonical events, raw imports and odds snapshots remain zero.

No database path is accepted from the contract or command line. The workspace must remain outside the repository, and the report emits aggregate counts and hashes only.

## Run locally

```bash
python -m pip install -e ".[dev]"
python scripts/validate_disabled_import_request_v1.py \
  --output runtime/reports/disabled-import-request-contract-v1.json
```

Focused tests:

```bash
pytest -q tests/test_disabled_import_request_v1.py
```

## Explicit non-activation

A successful report proves only that the disabled contract is internally consistent and that temporary backup/restore behavior is reversible. It does not grant owner approval, import a production schedule, touch a production database, start recurring collection or modify `qoo109/nba-value-lab`.
