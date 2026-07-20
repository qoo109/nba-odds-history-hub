# Normalized Odds Data Contract

Version: `v0.3`

## Purpose

This contract separates source-specific payloads from the stable format consumed by SQLite, exports, dashboards, and future NBA Value Lab joins.

## Time fields

| Field | Meaning |
|---|---|
| `observed_at` | When the quoted price was actually observed |
| `ingested_at` | When Odds History Hub processed the payload |
| `scheduled_tipoff` | Scheduled game or source-market start time |
| `cutoff_at` | Source market cutoff time |

All timestamps must be ISO-8601 with a timezone. `cutoff_at` must never be substituted for `observed_at`.

## Identity fields

| Field | Meaning |
|---|---|
| `source` | Source registry ID |
| `bookmaker_id` | Bookmaker registry ID |
| `source_event_id` | Source-native event or futures-market ID |
| `canonical_event_id` | Explicit NBA Value Lab mapping; nullable until verified |
| `participant_id` | Source-native participant ID |
| `market_key` | Source-native market identity |

`source_events` begin with `mapping_status = unmapped`. The importer does not invent canonical NBA Value Lab IDs.

## Normalized row

```json
{
  "source": "pinnacle_manual",
  "bookmaker_id": "pinnacle",
  "canonical_event_id": null,
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

## Change-aware quote identity

For `changes-only` retention, one quote is identified by:

```text
source, bookmaker_id, source_event_id, market_type, period,
side, participant_id, is_alternate
```

A new history row is kept when `line` or `american_odds` differs from the latest earlier row. Missing source rows are not interpreted as unchanged.

## Probability warning

`raw_implied_probability` is the direct probability implied by one price. It is not de-vigged and must not be treated as fair probability.
