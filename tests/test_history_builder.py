from nba_odds_history_hub.history import (
    build_history_payload,
    build_nba_value_lab_export,
    build_source_health_payload,
)


def row(
    observed_at: str,
    american: int,
    decimal: float,
    implied: float,
    *,
    snapshot_id: int = 1,
):
    return {
        "snapshot_id": snapshot_id,
        "source": "pinnacle_manual",
        "bookmaker_id": "pinnacle",
        "canonical_event_id": None,
        "source_event_id": 1001,
        "market_name": "NBA Champion",
        "market_type": "moneyline",
        "period": 0,
        "side": None,
        "participant_id": 2001,
        "participant_name": "Example Team",
        "line": -999999.0,
        "american_odds": american,
        "decimal_odds": decimal,
        "raw_implied_probability": implied,
        "observed_at": observed_at,
        "scheduled_tipoff": "2026-10-31T16:00:00Z",
        "cutoff_at": "2026-10-31T16:00:00Z",
        "is_alternate": 0,
        "raw_sha256": f"sha-{snapshot_id}",
    }


def test_one_snapshot_stays_not_movement_ready() -> None:
    payload = build_history_payload(
        [row("2026-07-20T11:10:00+08:00", 200, 3.0, 0.33333333)],
        generated_at="2026-07-20T12:00:00+08:00",
    )
    assert payload["coverage"]["snapshotCount"] == 1
    assert payload["coverage"]["movementReadyQuoteCount"] == 0
    assert payload["qualityFlags"]["historyReady"] is False
    assert payload["qualityFlags"]["executableBacktestReady"] is False
    assert payload["quotes"][0]["movement"] is None


def test_two_snapshots_build_shortening_history() -> None:
    payload = build_history_payload(
        [
            row(
                "2026-07-20T11:10:00+08:00",
                200,
                3.0,
                0.33333333,
                snapshot_id=1,
            ),
            row(
                "2026-07-21T11:10:00+08:00",
                150,
                2.5,
                0.4,
                snapshot_id=2,
            ),
        ],
        generated_at="2026-07-21T12:00:00+08:00",
    )
    quote = payload["quotes"][0]
    assert payload["qualityFlags"]["historyReady"] is True
    assert quote["distinctObservationCount"] == 2
    assert quote["changedTransitionCount"] == 1
    assert quote["movement"]["direction"] == "shortened"
    assert quote["movement"]["decimalOddsDelta"] == -0.5


def test_duplicate_time_is_flagged_not_silently_collapsed() -> None:
    payload = build_history_payload(
        [
            row(
                "2026-07-20T11:10:00+08:00",
                200,
                3.0,
                0.33333333,
                snapshot_id=1,
            ),
            row(
                "2026-07-20T11:10:00+08:00",
                190,
                2.9,
                0.34482759,
                snapshot_id=2,
            ),
        ]
    )
    quote = payload["quotes"][0]
    assert quote["observationCount"] == 2
    assert quote["distinctObservationCount"] == 1
    assert quote["duplicateObservedAt"] is True
    assert quote["movementReady"] is False


def test_source_health_and_nba_export_keep_gates_closed() -> None:
    rows = [row("2026-07-20T11:10:00+08:00", 200, 3.0, 0.33333333)]
    health = build_source_health_payload(rows, generated_at="x")
    export = build_nba_value_lab_export(rows, generated_at="x")
    assert health["snapshotCount"] == 1
    assert health["qualityFlags"]["missingRowsInterpretedAsUnchanged"] is False
    assert export["rowCount"] == 1
    assert export["gates"]["canonicalMappingComplete"] is False
    assert export["gates"]["executableBacktestReady"] is False
    assert export["gates"]["clvReady"] is False


def test_two_global_times_without_quote_overlap_are_not_movement_ready() -> None:
    first = row("2026-07-20T11:10:00+08:00", 200, 3.0, 0.33333333)
    second = row("2026-07-21T11:10:00+08:00", 150, 2.5, 0.4, snapshot_id=2)
    second["participant_id"] = 9999
    second["participant_name"] = "Different Team"
    health = build_source_health_payload([first, second], generated_at="x")
    assert health["qualityFlags"]["multipleSnapshotTimesPresent"] is True
    assert health["qualityFlags"]["historicalMovementReady"] is False
