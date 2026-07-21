"""Gate normalized fixture schedule records before persistence."""
from __future__ import annotations

from typing import Any

from .schedule_adapter import adapt_fixture, aware_utc


def gate_fixture(payload: dict[str, Any], team_registry: dict[str, Any]) -> dict[str, Any]:
    if payload.get("fixtureMode") is not True:
        raise ValueError("fixtureMode must be true")
    source_id = str(payload.get("sourceId") or "").strip()
    observed_at = aware_utc(str(payload.get("observedAt") or ""))
    payload_hash = str(payload.get("payloadSha256") or "").strip().lower()
    if not source_id:
        raise ValueError("sourceId is required")
    if len(payload_hash) != 64 or any(char not in "0123456789abcdef" for char in payload_hash):
        raise ValueError("payloadSha256 must be 64 lowercase hex characters")

    adapted = adapt_fixture(payload, team_registry)
    accepted = []
    reason_counts: dict[str, int] = {}
    for row in adapted["results"]:
        if row["status"] == "candidate_unverified":
            accepted.append({
                "source_id": source_id,
                "source_event_id": int(row["eventId"]),
                "scheduled_tipoff": str(row["tipoff"]),
                "home_team_abbr": str(row["homeTeamAbbr"]),
                "away_team_abbr": str(row["awayTeamAbbr"]),
                "mapping_status": "candidate_unverified",
                "mapping_method": "exact_date_home_away_candidate",
                "observed_at": observed_at,
                "source_payload_sha256": payload_hash,
            })
        else:
            reason = str(row["reason"])
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    return {
        "schemaVersion": "schedule-adapter-output-gate-v1",
        "fixtureMode": True,
        "sourceId": source_id,
        "accepted": accepted,
        "acceptedCount": len(accepted),
        "excludedCount": len(adapted["results"]) - len(accepted),
        "excludedReasonCounts": reason_counts,
        "adapterCounts": adapted["counts"],
        "canonicalEventIdsCreated": 0,
        "rowLevelExcludedRecordsEmitted": False,
    }
