"""Command-line entry point for grouped odds-history exports."""
from __future__ import annotations

import argparse
import json

from .history import export_history_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odds-hub-build-history",
        description="Build grouped quote histories and research-safe exports from SQLite.",
    )
    parser.add_argument(
        "--database",
        default="data/databases/odds_history.sqlite",
        help="SQLite odds-history database",
    )
    parser.add_argument(
        "--output-dir",
        default="exports/history",
        help="Directory for grouped history and coverage outputs",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = export_history_bundle(args.database, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
