from __future__ import annotations

import argparse
import json
from pathlib import Path

from nba_odds_history_hub.owner_review_packet import READY, build_review_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = build_review_report(root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
