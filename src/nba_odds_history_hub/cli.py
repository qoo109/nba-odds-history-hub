"""Command-line entry point for manual odds imports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .database import (
    export_csv,
    export_json,
    insert_snapshot_rows_detailed,
    register_bookmaker,
    register_source,
    register_source_events,
)
from .importer import build_import_quality_report, load_json, normalize_snapshots


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
        "--source", default="pinnacle_manual", help="Source registry identifier"
    )
    parser.add_argument(
        "--source-name",
        default="Pinnacle manual browser capture",
        help="Human-readable source name",
    )
    parser.add_argument(
        "--bookmaker", default="pinnacle", help="Bookmaker registry identifier"
    )
    parser.add_argument(
        "--bookmaker-name",
        default="Pinnacle",
        help="Human-readable bookmaker name",
    )
    parser.add_argument(
        "--dedupe-mode",
        choices=("exact", "changes-only"),
        default="exact",
        help="Keep every timestamped quote or only rows whose line/price changed",
    )
    parser.add_argument(
        "--export-dir", default="exports", help="Directory for outputs"
    )
    parser.add_argument(
        "--quality-report", default=None, help="Optional quality report path"
    )
    parser.add_argument("--note", default=None, help="Optional import note")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    matchups = load_json(args.matchups)
    straight = load_json(args.straight)
    quality = build_import_quality_report(matchups, straight)
    rows = normalize_snapshots(
        matchups,
        straight,
        observed_at=args.observed_at,
        source=args.source,
        bookmaker=args.bookmaker,
    )

    register_source(
        args.database,
        source_id=args.source,
        display_name=args.source_name,
        source_class="manual_browser_capture",
        access_mode="manual",
        usage_boundary=(
            "Owner-supplied snapshot; no credentials, cookies, HAR, "
            "or automated access logic."
        ),
    )
    register_bookmaker(
        args.database,
        bookmaker_id=args.bookmaker,
        display_name=args.bookmaker_name,
        source_id=args.source,
    )
    source_event_count = register_source_events(args.database, rows)
    result = insert_snapshot_rows_detailed(
        args.database,
        rows,
        matchup_count=len(matchups),
        market_count=len(straight),
        note=args.note,
        dedupe_mode=args.dedupe_mode,
    )

    export_dir = Path(args.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    json_count = export_json(args.database, export_dir / "odds_history.json")
    csv_count = export_csv(args.database, export_dir / "odds_history.csv")
    quality.update(
        {
            "observedAt": args.observed_at,
            "sourceId": args.source,
            "bookmakerId": args.bookmaker,
            "dedupeMode": args.dedupe_mode,
            "normalizedRows": len(rows),
            "sourceEventPlaceholders": source_event_count,
            "insertResult": result,
        }
    )
    quality_path = (
        Path(args.quality_report)
        if args.quality_report
        else export_dir / "import_quality_report.json"
    )
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    quality_path.write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "database": str(args.database),
        "normalized_rows": len(rows),
        "inserted": result["inserted"],
        "skipped": result["skipped"],
        "unchanged_skipped": result["unchanged_skipped"],
        "dedupe_mode": args.dedupe_mode,
        "matched_matchup_ids": quality["counts"]["matchedMatchupIds"],
        "unmatched_matchup_ids": quality["counts"]["unmatchedMarketMatchupIds"],
        "source_event_placeholders": source_event_count,
        "quality_report": str(quality_path),
        "json_export_rows": json_count,
        "csv_export_rows": csv_count,
        "raw_sha256": rows[0]["raw_sha256"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
