#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from nba_odds_history_hub.disabled_import_request import READY, build_report

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        report = build_report(ROOT, Path(directory))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(report["formalState"])
    print(f"checks={report['checksPassed']}/{report['checksTotal']}")
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
