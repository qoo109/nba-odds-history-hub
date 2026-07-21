"""Static schedule-file normalization helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def aware_utc(value: str) -> str:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def team_aliases(registry: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    current: dict[str, str] = {}
    historical: set[str] = set()
    for team in registry.get("teams", []):
        canonical = team["canonicalAbbr"].upper()
        current[canonical.lower()] = canonical
        for alias in team.get("sourceAliases", []):
            current[str(alias).lower()] = canonical
        for alias in team.get("historicalAliases", []):
            historical.add(str(alias).lower())
    return current, historical


def adapt_fixture(payload: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    current, historical = team_aliases(registry)
    counts = {"candidate_unverified": 0, "quarantined": 0, "rejected": 0}
    results = []
    seen = set()
    for game in payload.get("games", []):
        status = "candidate_unverified"
        reason = "exact_current_aliases"
        try:
            event_id = int(game["gameId"])
            tipoff = aware_utc(game["gameTimeUTC"])
        except (KeyError, TypeError, ValueError):
            event_id = None
            tipoff = None
            status = "rejected"
            reason = "invalid_id_or_time"
        home_raw = str(game.get("homeTeam", {}).get("teamTricode", "")).lower()
        away_raw = str(game.get("awayTeam", {}).get("teamTricode", "")).lower()
        home = current.get(home_raw)
        away = current.get(away_raw)
        if home_raw in historical or away_raw in historical:
            status, reason = "quarantined", "historical_alias"
        elif home is None or away is None:
            status, reason = "quarantined", "unknown_alias"
        elif home == away:
            status, reason = "rejected", "same_team"
        if event_id in seen:
            status, reason = "rejected", "duplicate_event_id"
        if event_id is not None:
            seen.add(event_id)
        counts[status] += 1
        results.append({
            "caseId": game.get("caseId"),
            "status": status,
            "reason": reason,
            "eventId": event_id,
            "tipoff": tipoff,
            "homeTeamAbbr": home,
            "awayTeamAbbr": away,
        })
    return {"results": results, "counts": counts}
