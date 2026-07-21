#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from nba_odds_history_hub.preseason_dry_run import READY, run_dry_run

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/reports/preseason-dry-run-v1.json")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        report = run_dry_run(ROOT, Path(directory) / "preseason.sqlite")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "formalState": report["formalState"],
        "checksPassed": report["checksPassed"],
        "checksTotal": report["checksTotal"],
        "sourceEvents": report["database"]["sourceEventCount"],
        "scheduleVersions": report["database"]["scheduleVersionCount"],
    }, indent=2))
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
