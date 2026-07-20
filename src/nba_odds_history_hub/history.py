"""Build quote histories, coverage summaries, and NBA Value Lab exports."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_STORAGE_NULL_LINE = -999999.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {value}")
    return parsed


def _public_line(value: Any) -> float | None:
    if value is None:
        return None
    number = float(value)
    return None if number == _STORAGE_NULL_LINE else number


def quote_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    """Return the stable identity of a quote, excluding line and price values."""
    return (
        str(row.get("source") or "unknown"),
        str(row.get("bookmaker_id") or "unknown"),
        int(row.get("source_event_id")),
        str(row.get("market_type") or "unknown"),
        int(row.get("period") or 0),
        str(row.get("side") or ""),
        int(row.get("participant_id") if row.get("participant_id") is not None else -1),
        bool(row.get("is_alternate")),
    )


def quote_identity_key(row: dict[str, Any]) -> str:
    return "|".join(str(value).lower() for value in quote_identity(row))


def _observation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "observedAt": str(row["observed_at"]),
        "line": _public_line(row.get("line")),
        "americanOdds": int(row["american_odds"]),
        "decimalOdds": float(row["decimal_odds"]),
        "rawImpliedProbability": float(row["raw_implied_probability"]),
        "rawSha256": row.get("raw_sha256"),
    }


def _movement(first: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any]:
    decimal_delta = round(latest["decimalOdds"] - first["decimalOdds"], 6)
    probability_delta = round(
        latest["rawImpliedProbability"] - first["rawImpliedProbability"], 8
    )
    if decimal_delta < 0:
        direction = "shortened"
    elif decimal_delta > 0:
        direction = "lengthened"
    else:
        direction = "unchanged"
    first_line = first["line"]
    latest_line = latest["line"]
    line_delta = (
        round(float(latest_line) - float(first_line), 6)
        if first_line is not None and latest_line is not None
        else None
    )
    return {
        "direction": direction,
        "americanOddsDelta": latest["americanOdds"] - first["americanOdds"],
        "decimalOddsDelta": decimal_delta,
        "rawImpliedProbabilityDelta": probability_delta,
        "lineDelta": line_delta,
    }


def build_history_payload(
    rows: Iterable[dict[str, Any]], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Group normalized rows into auditable quote histories.

    A quote becomes movement-ready only when it has at least two distinct
    observation timestamps. Multiple rows at one timestamp are retained and
    flagged instead of being silently collapsed.
    """
    materialized = list(rows)
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in materialized:
        _parse_time(str(row["observed_at"]))
        groups[quote_identity(row)].append(row)

    histories: list[dict[str, Any]] = []
    all_times: set[str] = set()
    source_events: set[tuple[str, int]] = set()
    mapped_quotes = 0

    for identity, group_rows in groups.items():
        group_rows.sort(
            key=lambda row: (
                _parse_time(str(row["observed_at"])),
                int(row.get("snapshot_id") or 0),
            )
        )
        observations = [_observation(row) for row in group_rows]
        distinct_times = sorted(
            {item["observedAt"] for item in observations}, key=_parse_time
        )
        all_times.update(distinct_times)
        source_events.add((identity[0], identity[2]))
        first_row = group_rows[0]
        canonical_event_id = first_row.get("canonical_event_id")
        if canonical_event_id:
            mapped_quotes += 1
        first = observations[0]
        latest = observations[-1]
        duplicate_observed_at = len(distinct_times) != len(observations)
        transitions = 0
        for previous, current in zip(observations, observations[1:]):
            if (
                previous["americanOdds"] != current["americanOdds"]
                or previous["line"] != current["line"]
            ):
                transitions += 1
        movement_ready = len(distinct_times) >= 2
        histories.append(
            {
                "quoteKey": quote_identity_key(first_row),
                "sourceId": identity[0],
                "bookmakerId": identity[1],
                "sourceEventId": identity[2],
                "canonicalEventId": canonical_event_id,
                "marketName": first_row.get("market_name"),
                "marketType": identity[3],
                "period": identity[4],
                "side": identity[5] or None,
                "participantId": identity[6] if identity[6] != -1 else None,
                "participantName": first_row.get("participant_name"),
                "isAlternate": identity[7],
                "scheduledTipoff": first_row.get("scheduled_tipoff"),
                "cutoffAt": first_row.get("cutoff_at"),
                "observationCount": len(observations),
                "distinctObservationCount": len(distinct_times),
                "changedTransitionCount": transitions,
                "duplicateObservedAt": duplicate_observed_at,
                "movementReady": movement_ready,
                "first": first,
                "latest": latest,
                "movement": _movement(first, latest) if movement_ready else None,
                "observations": observations,
            }
        )

    histories.sort(
        key=lambda item: (
            str(item["marketName"] or ""),
            str(item["participantName"] or ""),
            item["quoteKey"],
        )
    )
    snapshot_times = sorted(all_times, key=_parse_time)
    movement_ready_count = sum(1 for item in histories if item["movementReady"])
    quote_count = len(histories)
    mapping_pct = round(mapped_quotes / quote_count * 100, 4) if quote_count else 0.0
    history_ready = len(snapshot_times) >= 2 and movement_ready_count > 0

    coverage_by_snapshot = []
    for observed_at in snapshot_times:
        snapshot_rows = [
            row for row in materialized if str(row["observed_at"]) == observed_at
        ]
        coverage_by_snapshot.append(
            {
                "observedAt": observed_at,
                "rowCount": len(snapshot_rows),
                "sourceEventCount": len(
                    {
                        (str(row.get("source")), int(row["source_event_id"]))
                        for row in snapshot_rows
                    }
                ),
                "bookmakerCount": len(
                    {
                        str(row.get("bookmaker_id") or "unknown")
                        for row in snapshot_rows
                    }
                ),
            }
        )

    return {
        "schemaVersion": "v0.4-quote-history",
        "generatedAt": generated_at or _utc_now_iso(),
        "coverage": {
            "snapshotCount": len(snapshot_times),
            "earliestObservedAt": snapshot_times[0] if snapshot_times else None,
            "latestObservedAt": snapshot_times[-1] if snapshot_times else None,
            "sourceEventCount": len(source_events),
            "quoteCount": quote_count,
            "movementReadyQuoteCount": movement_ready_count,
            "singleObservationQuoteCount": quote_count - movement_ready_count,
            "canonicalMappedQuoteCount": mapped_quotes,
            "canonicalMappingCoveragePct": mapping_pct,
            "coverageBySnapshot": coverage_by_snapshot,
        },
        "qualityFlags": {
            "hasAtLeastTwoSnapshots": len(snapshot_times) >= 2,
            "hasMovementReadyQuotes": movement_ready_count > 0,
            "historyReady": history_ready,
            "executableBacktestReady": False,
            "reason": (
                "At least two timestamped observations exist for one or more quote identities."
                if history_ready
                else "A second real observed_at snapshot is required before movement charts are enabled."
            ),
        },
        "quotes": histories,
    }


def build_nba_value_lab_export(
    rows: Iterable[dict[str, Any]], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Create a stable point-in-time export without claiming backtest readiness."""
    materialized = sorted(
        list(rows),
        key=lambda row: (
            _parse_time(str(row["observed_at"])),
            str(row.get("source") or ""),
            int(row["source_event_id"]),
            str(row.get("participant_name") or ""),
        ),
    )
    exported = []
    for row in materialized:
        exported.append(
            {
                "canonical_event_id": row.get("canonical_event_id"),
                "source_event_id": int(row["source_event_id"]),
                "source_id": str(row.get("source") or "unknown"),
                "bookmaker_id": str(row.get("bookmaker_id") or "unknown"),
                "market_name": row.get("market_name"),
                "market_type": row.get("market_type"),
                "period": int(row.get("period") or 0),
                "side": row.get("side") or None,
                "participant_id": (
                    int(row["participant_id"])
                    if row.get("participant_id") not in (None, -1)
                    else None
                ),
                "participant_name": row.get("participant_name"),
                "line": _public_line(row.get("line")),
                "american_odds": int(row["american_odds"]),
                "decimal_odds": float(row["decimal_odds"]),
                "raw_implied_probability": float(row["raw_implied_probability"]),
                "observed_at": str(row["observed_at"]),
                "scheduled_tipoff": row.get("scheduled_tipoff"),
                "cutoff_at": row.get("cutoff_at"),
                "raw_sha256": row.get("raw_sha256"),
            }
        )
    mapped = sum(1 for row in exported if row["canonical_event_id"])
    return {
        "schemaVersion": "nba-value-lab-odds-export-v0.1",
        "generatedAt": generated_at or _utc_now_iso(),
        "researchStatus": "NOT_BACKTEST_READY",
        "rowCount": len(exported),
        "canonicalMappedRowCount": mapped,
        "gates": {
            "observedAtPresent": all(bool(row["observed_at"]) for row in exported),
            "canonicalMappingComplete": bool(exported) and mapped == len(exported),
            "openingClosingClassified": False,
            "executableBacktestReady": False,
            "clvReady": False,
            "evRoiReady": False,
        },
        "rows": exported,
    }


def write_json(payload: dict[str, Any], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def build_source_health_payload(
    rows: Iterable[dict[str, Any]], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Summarize accepted rows without treating absent rows as unchanged prices."""
    materialized = list(rows)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in materialized:
        _parse_time(str(row["observed_at"]))
        groups[
            (
                str(row.get("source") or "unknown"),
                str(row.get("bookmaker_id") or "unknown"),
            )
        ].append(row)

    sources = []
    for (source_id, bookmaker_id), source_rows in sorted(groups.items()):
        times = sorted(
            {str(row["observed_at"]) for row in source_rows}, key=_parse_time
        )
        sources.append(
            {
                "sourceId": source_id,
                "bookmakerId": bookmaker_id,
                "rowCount": len(source_rows),
                "snapshotCount": len(times),
                "sourceEventCount": len(
                    {int(row["source_event_id"]) for row in source_rows}
                ),
                "earliestObservedAt": times[0] if times else None,
                "latestObservedAt": times[-1] if times else None,
            }
        )
    all_times = sorted(
        {str(row["observed_at"]) for row in materialized}, key=_parse_time
    )
    quote_times: dict[tuple[Any, ...], set[str]] = defaultdict(set)
    for row in materialized:
        quote_times[quote_identity(row)].add(str(row["observed_at"]))
    movement_ready = any(len(times) >= 2 for times in quote_times.values())
    return {
        "schemaVersion": "v0.4-source-health",
        "generatedAt": generated_at or _utc_now_iso(),
        "acceptedRowCount": len(materialized),
        "snapshotCount": len(all_times),
        "sourceCount": len({item["sourceId"] for item in sources}),
        "bookmakerCount": len({item["bookmakerId"] for item in sources}),
        "sources": sources,
        "qualityFlags": {
            "allRowsHaveObservedAt": all(
                bool(row.get("observed_at")) for row in materialized
            ),
            "missingRowsInterpretedAsUnchanged": False,
            "multipleSnapshotTimesPresent": len(all_times) >= 2,
            "historicalMovementReady": movement_ready,
        },
    }


def export_history_bundle(
    database: str | Path,
    output_dir: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Write history, source-health, and NBA Value Lab research exports."""
    from .database import fetch_snapshots

    rows = fetch_snapshots(database)
    output = Path(output_dir)
    history = build_history_payload(rows, generated_at=generated_at)
    source_health = build_source_health_payload(rows, generated_at=generated_at)
    nba_export = build_nba_value_lab_export(rows, generated_at=generated_at)
    write_json(history, output / "odds_history_grouped.json")
    write_json(source_health, output / "source_health.json")
    write_json(nba_export, output / "nba_value_lab_odds_export.json")
    return {
        "database": str(database),
        "outputDir": str(output),
        "rowCount": len(rows),
        "snapshotCount": history["coverage"]["snapshotCount"],
        "quoteCount": history["coverage"]["quoteCount"],
        "movementReadyQuoteCount": history["coverage"][
            "movementReadyQuoteCount"
        ],
        "historyReady": history["qualityFlags"]["historyReady"],
        "executableBacktestReady": False,
    }
