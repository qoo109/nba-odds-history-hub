import argparse
import json
from pathlib import Path

from nba_odds_history_hub.approval_state_machine import build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["failedChecks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
