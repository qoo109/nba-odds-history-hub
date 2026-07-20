from __future__ import annotations

import json
from pathlib import Path

from nba_odds_history_hub.intake import validate_intake_package


MATCHUPS = [
    {
        "id": 1001,
        "league": {"name": "NBA", "sport": {"name": "Basketball"}},
        "participants": [
            {"id": 2001, "name": "Example Team", "alignment": "neutral"}
        ],
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
        "prices": [{"participantId": 2001, "price": 188}],
    }
]


def write_package(
    root: Path,
    *,
    observed_at: str = "2026-07-21T11:10:00+08:00",
    sensitive: bool = False,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    matchups = list(MATCHUPS)
    if sensitive:
        matchups = [dict(MATCHUPS[0], access_token="must-not-be-present")]
    (root / "matchups.json").write_text(json.dumps(matchups), encoding="utf-8")
    (root / "straight.json").write_text(json.dumps(STRAIGHT), encoding="utf-8")
    (root / "metadata.json").write_text(
        json.dumps(
            {
                "observedAt": observed_at,
                "sourceId": "pinnacle_manual",
                "bookmakerId": "pinnacle",
                "notes": "second owner-supplied snapshot",
            }
        ),
        encoding="utf-8",
    )


def test_valid_intake_is_ready(tmp_path: Path) -> None:
    package = tmp_path / "candidate"
    write_package(package)
    report = validate_intake_package(package)

    assert report["readyForImport"] is True
    assert report["errors"] == []
    assert report["qualityReport"]["counts"]["matchedMatchupIds"] == 1
    assert set(report["files"]) == {"matchups.json", "straight.json", "metadata.json"}
    assert all(item["sha256"] for item in report["files"].values())


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "candidate"
    write_package(package)
    (package / "straight.json").unlink()

    report = validate_intake_package(package)
    assert report["readyForImport"] is False
    assert "missing required files" in report["errors"][0]


def test_naive_observation_time_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "candidate"
    write_package(package, observed_at="2026-07-21T11:10:00")

    report = validate_intake_package(package)
    assert report["readyForImport"] is False
    assert any("timezone offset" in error for error in report["errors"])


def test_sensitive_key_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "candidate"
    write_package(package, sensitive=True)

    report = validate_intake_package(package)
    assert report["readyForImport"] is False
    assert report["sensitiveKeyPaths"] == ["$[0].access_token"]
    assert any("sensitive keys" in error for error in report["errors"])
