from copy import deepcopy
from pathlib import Path

from nba_odds_history_hub.database import (
    connect_database,
    fetch_snapshots,
    insert_snapshot_rows_detailed,
    map_source_event,
    register_bookmaker,
    register_source,
    register_source_events,
    upsert_canonical_event,
)
from nba_odds_history_hub.importer import build_import_quality_report, normalize_snapshots

MATCHUPS = [
    {
        "id": 1001,
        "league": {"name": "NBA", "sport": {"name": "Basketball"}},
        "participants": [{"id": 2001, "name": "A"}, {"id": 2002, "name": "B"}],
        "special": {"category": "Futures", "description": "NBA Champion"},
        "startTime": "2026-10-31T16:00:00Z",
    }
]
STRAIGHT = [
    {
        "matchupId": 1001,
        "period": 0,
        "type": "moneyline",
        "key": "s;0;m",
        "cutoffAt": "2026-10-31T16:00:00Z",
        "prices": [
            {"participantId": 2001, "price": 188},
            {"participantId": 2002, "price": 250},
        ],
    }
]


def test_quality_report_exposes_unmatched_and_orphan_rows() -> None:
    straight = deepcopy(STRAIGHT)
    straight.append(
        {
            "matchupId": 9999,
            "type": "moneyline",
            "prices": [{"participantId": 1, "price": 200}],
        }
    )
    straight[0]["prices"].append({"participantId": 2999, "price": 400})
    report = build_import_quality_report(MATCHUPS, straight)
    assert report["matchedMatchupIds"] == [1001]
    assert report["unmatchedMarketMatchupIds"] == [9999]
    assert report["counts"]["orphanParticipantPrices"] == 1
    assert report["qualityFlags"]["allMarketsMatched"] is False


def test_changes_only_keeps_only_real_price_changes(tmp_path: Path) -> None:
    database = tmp_path / "history.sqlite"
    rows1 = normalize_snapshots(
        MATCHUPS, STRAIGHT, observed_at="2026-07-20T11:10:00+08:00"
    )
    first = insert_snapshot_rows_detailed(
        database,
        rows1,
        matchup_count=1,
        market_count=1,
        dedupe_mode="changes-only",
    )
    rows2 = normalize_snapshots(
        MATCHUPS, STRAIGHT, observed_at="2026-07-20T12:10:00+08:00"
    )
    second = insert_snapshot_rows_detailed(
        database,
        rows2,
        matchup_count=1,
        market_count=1,
        dedupe_mode="changes-only",
    )
    changed = deepcopy(STRAIGHT)
    changed[0]["prices"][0]["price"] = 205
    rows3 = normalize_snapshots(
        MATCHUPS, changed, observed_at="2026-07-20T13:10:00+08:00"
    )
    third = insert_snapshot_rows_detailed(
        database,
        rows3,
        matchup_count=1,
        market_count=1,
        dedupe_mode="changes-only",
    )
    # An out-of-order backfill compares only with earlier observations, not future rows.
    rows_mid = normalize_snapshots(
        MATCHUPS, STRAIGHT, observed_at="2026-07-20T12:30:00+08:00"
    )
    middle = insert_snapshot_rows_detailed(
        database,
        rows_mid,
        matchup_count=1,
        market_count=1,
        dedupe_mode="changes-only",
    )
    assert first["inserted"] == 2
    assert second["inserted"] == 0 and second["unchanged_skipped"] == 2
    assert third["inserted"] == 1 and third["unchanged_skipped"] == 1
    assert middle["inserted"] == 0 and middle["unchanged_skipped"] == 2
    assert len(fetch_snapshots(database)) == 3


def test_registry_and_canonical_mapping_are_explicit(tmp_path: Path) -> None:
    database = tmp_path / "registry.sqlite"
    register_source(
        database, source_id="pinnacle_manual", display_name="Pinnacle manual"
    )
    register_bookmaker(
        database,
        bookmaker_id="pinnacle",
        display_name="Pinnacle",
        source_id="pinnacle_manual",
    )
    rows = normalize_snapshots(
        MATCHUPS, STRAIGHT, observed_at="2026-07-20T11:10:00+08:00"
    )
    assert register_source_events(database, rows) == 1
    insert_snapshot_rows_detailed(
        database, rows, matchup_count=1, market_count=1
    )
    upsert_canonical_event(
        database,
        canonical_event_id="nba:futures:2026-27-champion",
        league="NBA",
        event_type="futures",
        title="NBA Champion",
    )
    map_source_event(
        database,
        source_id="pinnacle_manual",
        source_event_id=1001,
        canonical_event_id="nba:futures:2026-27-champion",
    )
    with connect_database(database) as connection:
        event = connection.execute(
            "SELECT mapping_status, canonical_event_id FROM source_events"
        ).fetchone()
        snapshots = connection.execute(
            "SELECT DISTINCT canonical_event_id FROM odds_snapshots"
        ).fetchall()
    assert dict(event) == {
        "mapping_status": "mapped",
        "canonical_event_id": "nba:futures:2026-27-champion",
    }
    assert [row[0] for row in snapshots] == ["nba:futures:2026-27-champion"]


def test_v02_database_migrates_additively(tmp_path: Path) -> None:
    import sqlite3

    from nba_odds_history_hub.database import initialize_database

    database = tmp_path / "legacy.sqlite"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE raw_imports (
              import_id INTEGER PRIMARY KEY, source TEXT, observed_at TEXT,
              ingested_at TEXT, raw_sha256 TEXT, matchup_count INTEGER,
              market_count INTEGER, normalized_row_count INTEGER
            );
            CREATE TABLE odds_snapshots (
              snapshot_id INTEGER PRIMARY KEY, import_id INTEGER, source TEXT,
              league TEXT, sport TEXT, source_event_id INTEGER, market_name TEXT,
              market_type TEXT, period INTEGER, side TEXT, participant_id INTEGER,
              participant_name TEXT, line REAL, american_odds INTEGER,
              decimal_odds REAL, raw_implied_probability REAL, observed_at TEXT,
              ingested_at TEXT, scheduled_tipoff TEXT, cutoff_at TEXT,
              source_version INTEGER, market_key TEXT, is_alternate INTEGER,
              raw_sha256 TEXT
            );
            """
        )
    initialize_database(database)
    with connect_database(database) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(odds_snapshots)")
        }
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {"bookmaker_id", "canonical_event_id"} <= columns
    assert {"data_sources", "bookmakers", "source_events", "canonical_events"} <= tables
