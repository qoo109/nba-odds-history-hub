import json
from pathlib import Path

from nba_odds_history_hub.preseason_dry_run import run_dry_run

ROOT = Path(__file__).resolve().parents[1]


def test_committed_preseason_status_is_reproducible(tmp_path):
    actual = run_dry_run(ROOT, tmp_path / "preseason.sqlite")
    expected = json.loads(
        (ROOT / "data/preseason-dry-run-current-status-v1.json").read_text(encoding="utf-8")
    )
    assert actual == expected
