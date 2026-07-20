from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
SNAPSHOT = PUBLIC / "snapshots" / "2026-07-20"


def american_to_decimal(price: int) -> float:
    return 1 + price / 100 if price > 0 else 1 + 100 / abs(price)


def test_snapshot_index_manifest_and_hashes() -> None:
    index = json.loads((SNAPSHOT / "index.json").read_text(encoding="utf-8"))
    manifest = json.loads((PUBLIC / "manifest.json").read_text(encoding="utf-8"))
    assert index["capturedAt"] == manifest["observedAt"]
    assert index["marketCount"] == manifest["marketCount"] == 5
    assert index["optionCount"] == manifest["optionCount"] == 91
    assert manifest["unmatchedMatchupIds"] == []
    for name, expected in manifest["files"].items():
        path = SNAPSHOT / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["sha256"]


def test_market_files_and_odds_consistency() -> None:
    index = json.loads((SNAPSHOT / "index.json").read_text(encoding="utf-8"))
    ids = set()
    options = 0
    for summary in index["markets"]:
        market = json.loads((ROOT / summary["file"]).read_text(encoding="utf-8"))
        assert market["matchupId"] not in ids
        ids.add(market["matchupId"])
        participant_ids = [o["participantId"] for o in market["options"]]
        assert len(participant_ids) == len(set(participant_ids))
        options += len(market["options"])
        for option in market["options"]:
            assert abs(option["decimal"] - american_to_decimal(option["american"])) <= 0.001
            assert abs(option["impliedPct"] - round(100 / option["decimal"], 2)) <= 0.01
    assert len(ids) == 5
    assert options == 91


def test_v04_public_history_gate_is_honest() -> None:
    latest = json.loads((PUBLIC / "latest.json").read_text(encoding="utf-8"))
    status = json.loads((ROOT / latest["historyStatus"]).read_text(encoding="utf-8"))
    assert status["snapshotCount"] == 1
    assert status["quoteCount"] == 91
    assert status["movementReadyQuoteCount"] == 0
    assert status["historyReady"] is False
    assert status["executableBacktestReady"] is False


def test_dashboard_contract() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "NBA Odds History Hub" in html
    assert "index.json" in html
    assert "下載完整 JSON" in html
    assert "下載完整 CSV" in html
    assert "登入繞過" in html
    assert "V0.4" in html
    assert "history-status.json" in html
