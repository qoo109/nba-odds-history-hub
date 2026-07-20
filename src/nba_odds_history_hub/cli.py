"""Command-line entry point for manual odds imports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .database import export_csv, export_json, insert_snapshot_rows
from .importer import load_json, normalize_snapshots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odds-hub-import",
        description="Import matchup and straight JSON snapshots into SQLite.",
    )
    parser.add_argument("--matchups", required=True, help="Path to matchups JSON")
    parser.add_argument("--straight", required=True, help="Path to straight JSON")
    parser.add_argument(
        "--observed-at",
        required=True,
        help="Timezone-aware ISO-8601 observation time",
    )
    parser.add_argument(
        "--database",
        default="data/databases/odds_history.sqlite",
        help="SQLite output path",
    )
    parser.add_argument(
        "--source",
        default="pinnacle_manual",
        help="Source identifier stored with each row",
    )
    parser.add_argument(
        "--export-dir",
        default="exports",
        help="Directory for normalized CSV and JSON exports",
    )
    parser.add_argument("--note", default=None, help="Optional import note")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    matchups = load_json(args.matchups)
    straight = load_json(args.straight)
    rows = normalize_snapshots(
        matchups,
        straight,
        observed_at=args.observed_at,
        source=args.source,
    )
    result = insert_snapshot_rows(
        args.database,
        rows,
        matchup_count=len(matchups),
        market_count=len(straight),
        note=args.note,
    )

    export_dir = Path(args.export_dir)
    json_count = export_json(args.database, export_dir / "odds_history.json")
    csv_count = export_csv(args.database, export_dir / "odds_history.csv")
    summary = {
        "database": str(args.database),
        "normalized_rows": len(rows),
        "inserted": result["inserted"],
        "skipped": result["skipped"],
        "json_export_rows": json_count,
        "csv_export_rows": csv_count,
        "raw_sha256": rows[0]["raw_sha256"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
