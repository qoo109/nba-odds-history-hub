"""Command-line interface for second-snapshot intake validation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .intake import validate_intake_package, write_intake_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odds-hub-validate-intake",
        description=(
            "Validate matchups.json, straight.json, and metadata.json before "
            "importing a second real odds snapshot."
        ),
    )
    parser.add_argument(
        "--package-dir",
        required=True,
        help="Directory containing matchups.json, straight.json, and metadata.json",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report path; defaults to <package-dir>/intake_report.json",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    package_dir = Path(args.package_dir)
    report = validate_intake_package(package_dir)
    output = Path(args.output) if args.output else package_dir / "intake_report.json"
    write_intake_report(report, output)

    summary = {
        "package_dir": str(package_dir),
        "report": str(output),
        "ready_for_import": report["readyForImport"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "matched_matchup_ids": (
            report.get("qualityReport", {})
            .get("counts", {})
            .get("matchedMatchupIds", 0)
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if report["readyForImport"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
