import json
from pathlib import Path

from nba_odds_history_hub.schedule_adapter import adapt_fixture

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_schedule_adapter_fixture_outcomes():
    payload = load("data/fixtures/official-schedule-adapter-v1.json")
    teams = load("config/nba-team-registry-v1.json")
    result = adapt_fixture(payload, teams)
    assert result["counts"] == {
        "candidate_unverified": 2,
        "quarantined": 2,
        "rejected": 2,
    }
    expected = {game["caseId"]: game["expectedStatus"] for game in payload["games"]}
    actual = {row["caseId"]: row["status"] for row in result["results"]}
    assert actual == expected


def test_duplicate_event_id_fails_closed():
    payload = load("data/fixtures/official-schedule-adapter-v1.json")
    payload["games"][1]["gameId"] = payload["games"][0]["gameId"]
    teams = load("config/nba-team-registry-v1.json")
    result = adapt_fixture(payload, teams)
    assert result["results"][1]["status"] == "rejected"
    assert result["results"][1]["reason"] == "duplicate_event_id"


def test_current_registries_remain_role_limited():
    sources = load("config/source-registry.json")["sources"]
    providers = load("config/bookmaker-registry.json")["bookmakers"]
    source_ids = {source["sourceId"] for source in sources}
    assert len(source_ids) == len(sources)
    assert all(source["automationApproved"] is False for source in sources)
    assert all(source["usageBoundary"].strip() for source in sources)
    assert all(provider["sourceId"] in source_ids for provider in providers)
    assert all(provider["note"].strip() for provider in providers)
