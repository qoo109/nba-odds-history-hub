# Offseason Reference Foundation v1

## Purpose

This slice builds static NBA reference data before live monitoring begins. It performs no source retrieval and does not modify `qoo109/nba-value-lab`.

Expected validation state:

```text
OFFSEASON_REFERENCE_FOUNDATION_V1_READY
```

## Assets

### Team registry

`config/nba-team-registry-v1.json` defines 30 active teams, conferences, divisions, canonical abbreviations, current source aliases and historical aliases requiring season validation.

Key rules:

- 30 active teams;
- 15 East and 15 West;
- six divisions with five teams each;
- unknown aliases are quarantined;
- no automatic fuzzy matching;
- historical relocation aliases require season validation.

### Market taxonomy

`config/market-taxonomy-v1.json` separates game and futures records and defines normalized classes for full-game, first-half and futures data. Source market keys and source period codes remain preserved. Unknown classes are quarantined rather than guessed.

### Offseason readiness

`config/offseason-capture-readiness-v1.json` keeps the system in `offseason_sleep`. All cadence templates remain inactive. Exact event mapping is required; unverified source events remain `unmapped`.

## Validator

`scripts/validate_offseason_reference_foundation_v1.py` checks team counts, uniqueness, divisions, aliases, required market classes, event identity, inactive schedules and retention boundaries.

Negative self-tests ensure duplicate team identities, semantic inference, accidental cadence activation and restricted-access permission drift fail closed.

## Validation boundary

- no network calls;
- no source payload reads;
- no raw rows or files;
- no automatic write to NBA Value Lab;
- formal Stake remains 0.

A later activation change must separately review its source, timing fields and manual first run. This reference foundation does not activate live collection.
