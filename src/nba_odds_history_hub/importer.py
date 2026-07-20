"""Manual JSON importer and quality reporting for odds snapshots."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .odds import american_to_decimal, american_to_implied_probability


class ImportValidationError(ValueError):
    """Raised when an imported snapshot does not satisfy the data contract."""


def parse_iso_datetime(value: str, *, field_name: str) -> str:
    if not value or not isinstance(value, str):
        raise ImportValidationError(f"{field_name} must be a non-empty ISO timestamp")
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ImportValidationError(f"Invalid {field_name}: {value}") from exc
    if parsed.tzinfo is None:
        raise ImportValidationError(f"{field_name} must include a timezone offset")
    return parsed.isoformat()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str | Path) -> Any:
    file_path = Path(path)
    try:
        return json.loads(file_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ImportValidationError(f"File not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise ImportValidationError(
            f"Invalid JSON in {file_path}: line {exc.lineno}, column {exc.colno}"
        ) from exc


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_list(value: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ImportValidationError(f"{name} must be a JSON array")
    if not all(isinstance(item, dict) for item in value):
        raise ImportValidationError(f"Every {name} item must be a JSON object")
    return value


def _participant_index(matchup: dict[str, Any]) -> dict[int, dict[str, Any]]:
    participants = matchup.get("participants") or []
    return {
        participant["id"]: participant
        for participant in participants
        if isinstance(participant, dict) and isinstance(participant.get("id"), int)
    }


def _participant_from_designation(
    matchup: dict[str, Any], designation: str
) -> dict[str, Any] | None:
    participants = matchup.get("participants") or []
    for participant in participants:
        if isinstance(participant, dict) and participant.get("alignment") == designation:
            return participant
    ordered = sorted(
        (p for p in participants if isinstance(p, dict)),
        key=lambda item: item.get("order", 0),
    )
    if designation == "home" and ordered:
        return ordered[0]
    if designation == "away" and len(ordered) > 1:
        return ordered[1]
    return None


def build_import_quality_report(
    matchups_payload: Any, straight_payload: Any
) -> dict[str, Any]:
    """Return a JSON-safe structural QA report before normalization.

    The report never turns missing or orphaned records into valid rows. It exposes
    matching coverage so a green workflow cannot hide an incomplete import.
    """
    matchups = _require_list(matchups_payload, "matchups")
    straight = _require_list(straight_payload, "straight")

    matchup_ids = [m.get("id") for m in matchups if isinstance(m.get("id"), int)]
    market_matchup_ids = [
        m.get("matchupId") for m in straight if isinstance(m.get("matchupId"), int)
    ]
    matchup_set = set(matchup_ids)
    market_set = set(market_matchup_ids)

    duplicate_matchup_ids = sorted(
        identifier for identifier, count in Counter(matchup_ids).items() if count > 1
    )
    market_keys: list[str] = []
    duplicate_participants: list[dict[str, Any]] = []
    orphan_participants: list[dict[str, Any]] = []
    invalid_price_entries = 0
    price_entry_count = 0
    matchups_by_id = {
        matchup.get("id"): matchup
        for matchup in matchups
        if isinstance(matchup.get("id"), int)
    }

    for market_index, market in enumerate(straight):
        matchup_id = market.get("matchupId")
        key = "|".join(
            str(value)
            for value in (
                matchup_id,
                market.get("period", 0),
                market.get("type"),
                market.get("key"),
            )
        )
        market_keys.append(key)
        prices = market.get("prices") or []
        if not isinstance(prices, list):
            invalid_price_entries += 1
            continue
        participant_ids: list[int] = []
        participant_index = _participant_index(matchups_by_id.get(matchup_id, {}))
        for price_index, price in enumerate(prices):
            price_entry_count += 1
            if not isinstance(price, dict) or not isinstance(price.get("price"), (int, float)):
                invalid_price_entries += 1
                continue
            participant_id = price.get("participantId")
            if isinstance(participant_id, int):
                participant_ids.append(participant_id)
                if matchup_id in matchups_by_id and participant_id not in participant_index:
                    orphan_participants.append(
                        {
                            "marketIndex": market_index,
                            "priceIndex": price_index,
                            "matchupId": matchup_id,
                            "participantId": participant_id,
                        }
                    )
        duplicates = sorted(
            identifier
            for identifier, count in Counter(participant_ids).items()
            if count > 1
        )
        if duplicates:
            duplicate_participants.append(
                {"marketIndex": market_index, "matchupId": matchup_id, "participantIds": duplicates}
            )

    duplicate_market_keys = sorted(
        key for key, count in Counter(market_keys).items() if count > 1
    )
    matched = sorted(matchup_set & market_set)
    unmatched_market = sorted(market_set - matchup_set)
    matchups_without_market = sorted(matchup_set - market_set)
    invalid_matchup_id_count = len(matchups) - len(matchup_ids)
    invalid_market_matchup_id_count = len(straight) - len(market_matchup_ids)

    return {
        "schemaVersion": "v0.3-import-quality-report",
        "rawSha256": canonical_json_sha256(
            {"matchups": matchups_payload, "straight": straight_payload}
        ),
        "counts": {
            "matchupRecords": len(matchups),
            "marketRecords": len(straight),
            "priceEntries": price_entry_count,
            "matchedMatchupIds": len(matched),
            "unmatchedMarketMatchupIds": len(unmatched_market),
            "matchupsWithoutMarket": len(matchups_without_market),
            "orphanParticipantPrices": len(orphan_participants),
            "invalidPriceEntries": invalid_price_entries,
        },
        "matchedMatchupIds": matched,
        "unmatchedMarketMatchupIds": unmatched_market,
        "matchupsWithoutMarket": matchups_without_market,
        "duplicateMatchupIds": duplicate_matchup_ids,
        "duplicateMarketKeys": duplicate_market_keys,
        "duplicateParticipantIdsWithinMarket": duplicate_participants,
        "orphanParticipantPrices": orphan_participants,
        "invalidMatchupIdCount": invalid_matchup_id_count,
        "invalidMarketMatchupIdCount": invalid_market_matchup_id_count,
        "qualityFlags": {
            "allMarketsMatched": not unmatched_market,
            "noDuplicateMatchupIds": not duplicate_matchup_ids,
            "noDuplicateMarketKeys": not duplicate_market_keys,
            "noDuplicateParticipantIdsWithinMarket": not duplicate_participants,
            "noOrphanParticipantPrices": not orphan_participants,
            "allPriceEntriesValid": invalid_price_entries == 0,
        },
    }


def normalize_snapshots(
    matchups_payload: Any,
    straight_payload: Any,
    *,
    observed_at: str,
    source: str = "pinnacle_manual",
    bookmaker: str = "pinnacle",
    ingested_at: str | None = None,
) -> list[dict[str, Any]]:
    """Join matchup metadata and straight prices into normalized snapshot rows."""
    matchups = _require_list(matchups_payload, "matchups")
    straight = _require_list(straight_payload, "straight")
    observed = parse_iso_datetime(observed_at, field_name="observed_at")
    ingested = parse_iso_datetime(ingested_at or utc_now_iso(), field_name="ingested_at")

    matchups_by_id: dict[int, dict[str, Any]] = {}
    for matchup in matchups:
        matchup_id = matchup.get("id")
        if not isinstance(matchup_id, int):
            raise ImportValidationError("Each matchup requires an integer id")
        matchups_by_id[matchup_id] = matchup

    raw_sha256 = canonical_json_sha256(
        {"matchups": matchups_payload, "straight": straight_payload}
    )
    rows: list[dict[str, Any]] = []

    for market in straight:
        matchup_id = market.get("matchupId")
        if matchup_id not in matchups_by_id:
            continue
        matchup = matchups_by_id[matchup_id]
        participant_by_id = _participant_index(matchup)
        prices = market.get("prices") or []
        if not isinstance(prices, list):
            raise ImportValidationError(f"prices must be an array for matchupId {matchup_id}")

        league = matchup.get("league") or {}
        sport = league.get("sport") or {}
        special = matchup.get("special") or {}
        market_name = special.get("description") or market.get("type")

        for price_entry in prices:
            if not isinstance(price_entry, dict):
                continue
            american = price_entry.get("price")
            if not isinstance(american, (int, float)):
                continue

            participant: dict[str, Any] | None = None
            participant_id = price_entry.get("participantId")
            designation = price_entry.get("designation")
            if isinstance(participant_id, int):
                participant = participant_by_id.get(participant_id)
            elif isinstance(designation, str):
                participant = _participant_from_designation(matchup, designation)
                participant_id = participant.get("id") if participant else None

            participant_name = (
                participant.get("name")
                if participant
                else str(designation or participant_id or "unknown")
            )
            rows.append(
                {
                    "source": source,
                    "bookmaker_id": bookmaker,
                    "canonical_event_id": None,
                    "event_type": str(special.get("category") or "market").lower(),
                    "league": league.get("name"),
                    "sport": sport.get("name"),
                    "source_event_id": matchup_id,
                    "market_name": market_name,
                    "market_type": market.get("type"),
                    "period": market.get("period", 0),
                    "side": designation or market.get("side"),
                    "participant_id": participant_id,
                    "participant_name": participant_name,
                    "line": price_entry.get("points"),
                    "american_odds": int(american),
                    "decimal_odds": american_to_decimal(american),
                    "raw_implied_probability": american_to_implied_probability(american),
                    "observed_at": observed,
                    "ingested_at": ingested,
                    "scheduled_tipoff": matchup.get("startTime"),
                    "cutoff_at": market.get("cutoffAt"),
                    "source_version": market.get("version"),
                    "market_key": market.get("key"),
                    "is_alternate": bool(market.get("isAlternate", False)),
                    "raw_sha256": raw_sha256,
                }
            )

    if not rows:
        raise ImportValidationError(
            "No joinable odds rows were produced; confirm both files describe the same matchups"
        )
    return rows
