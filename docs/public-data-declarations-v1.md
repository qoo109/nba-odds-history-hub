# Public data declarations v1

This stage adds three JSON Schema Draft 2020-12 declarations and a deterministic integrity manifest for committed public governance files.

Run the focused validation:

```bash
pytest -q tests/test_public_contract_schema_checksums_v1.py
```

Rebuild the committed manifest:

```bash
python scripts/build_public_governance_checksums_v1.py --output data/public/public-governance-checksums-v1.json
```

The process reads repository files only and keeps the existing inactive operating mode.
