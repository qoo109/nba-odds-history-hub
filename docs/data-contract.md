# Normalized Odds Data Contract

Version: `v0.1`

## Purpose

This contract separates source-specific payloads from the stable format consumed by storage, exports, dashboards, and NBA Value Lab.

## Time fields

| Field | Meaning |
|---|---|
| `observed_at` | When the price was actually observed at the source |
| `ingested_at` | When Odds History Hub processed and stored the payload |
| `scheduled_tipoff` | Scheduled game or market start time from the source |
| `cutoff_at` | Source market cutoff time |

All timestamps must be ISO-8601 and include a timezone.

## Normalized row

```json
{
  "source": "pinnacle_manual",
  "league": "NBA",
  "sport": "Basketball",
  "source_event_id": 1631943127,
  "market_name": "2026-2027 NBA Regular Season MVP",
  "market_type": "moneyline",
  "period": 0,
  "side": null,
  "participant_id": 1631943128,
  "participant_name": "Example Participant",
  "line": null,
  "american_odds": 188,
  "decimal_odds": 2.88,
  "raw_implied_probability": 0.34722222,
  "observed_at": "2026-07-20T11:10:00+08:00",
  "ingested_at": "2026-07-20T03:11:00+00:00",
  "scheduled_tipoff": "2026-10-31T16:00:00Z",
  "cutoff_at": "2026-10-31T16:00:00Z",
  "source_version": 6262718600,
  "market_key": "s;0;m",
  "is_alternate": false,
  "raw_sha256": "..."
}
```

## Required fields

- `source`
- `source_event_id`
- `market_type`
- `period`
- `participant_name`
- `american_odds`
- `decimal_odds`
- `raw_implied_probability`
- `observed_at`
- `ingested_at`
- `raw_sha256`

## Probability warning

`raw_implied_probability` is the direct probability implied by one quoted price. It is not de-vigged and must not be treated as fair probability.

## Identity strategy

V0.1 preserves source-native identifiers:

- `source_event_id`
- `participant_id`
- `market_key`

A later milestone will add canonical event, team, participant, and bookmaker identifiers for cross-source joins.
