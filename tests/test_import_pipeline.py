from pathlib import Path

from nba_odds_history_hub.database import fetch_snapshots, insert_snapshot_rows
from nba_odds_history_hub.importer import normalize_snapshots


MATCHUPS = [
    {
        "id": 1001,
        "league": {"name": "NBA", "sport": {"name": "Basketball"}},
        "participants": [
            {"id": 2001, "name": "Example A", "alignment": "neutral"},
            {"id": 2002, "name": "Example B", "alignment": "neutral"},
        ],
        "special": {"category": "Futures", "description": "Example Award"},
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
        "version": 123,
        "prices": [
            {"participantId": 2001, "price": 188},
            {"participantId": 2002, "price": -211},
        ],
    }
]


def test_normalize_and_insert(tmp_path: Path) -> None:
    rows = normalize_snapshots(
        MATCHUPS,
        STRAIGHT,
        observed_at="2026-07-20T11:10:00+08:00",
    )
    assert len(rows) == 2
    assert rows[0]["participant_name"] == "Example A"
    assert rows[0]["decimal_odds"] == 2.88

    database = tmp_path / "odds.sqlite"
    first = insert_snapshot_rows(
        database,
        rows,
        matchup_count=len(MATCHUPS),
        market_count=len(STRAIGHT),
    )
    second = insert_snapshot_rows(
        database,
        rows,
        matchup_count=len(MATCHUPS),
        market_count=len(STRAIGHT),
    )

    assert first == {"inserted": 2, "skipped": 0}
    assert second == {"inserted": 0, "skipped": 2}
    stored = fetch_snapshots(database)
    assert len(stored) == 2
