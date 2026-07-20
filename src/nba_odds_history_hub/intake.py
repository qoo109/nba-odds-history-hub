"""Validation helpers for owner-supplied snapshot intake packages."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .importer import (
    ImportValidationError,
    build_import_quality_report,
    load_json,
    parse_iso_datetime,
)

REQUIRED_FILES = ("matchups.json", "straight.json", "metadata.json")
SENSITIVE_KEY_FRAGMENTS = (
    "authorization",
    "cookie",
    "password",
    "secret",
    "session",
    "token",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _find_sensitive_key_paths(value: Any, *, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            child_path = f"{prefix}.{key_text}"
            if any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
                findings.append(child_path)
            findings.extend(_find_sensitive_key_paths(child, prefix=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_sensitive_key_paths(child, prefix=f"{prefix}[{index}]"))
    return findings


def _base_report(package_dir: Path) -> dict[str, Any]:
    return {
        "schemaVersion": "v0.4-snapshot-intake-report",
        "packageDir": str(package_dir),
        "requiredFiles": list(REQUIRED_FILES),
        "files": {},
        "metadata": None,
        "qualityReport": None,
        "errors": [],
        "warnings": [],
        "sensitiveKeyPaths": [],
        "readyForImport": False,
    }


def validate_intake_package(package_dir: str | Path) -> dict[str, Any]:
    """Validate one candidate package without importing it into SQLite.

    The package must contain ``matchups.json``, ``straight.json``, and
    ``metadata.json``. This function performs structural QA, timezone validation,
    basic sensitive-key detection, and file hashing. It never changes the
    database and never treats a failed check as an accepted snapshot.
    """
    root = Path(package_dir)
    report = _base_report(root)

    if not root.exists() or not root.is_dir():
        report["errors"].append("package directory does not exist")
        return report

    paths = {name: root / name for name in REQUIRED_FILES}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        report["errors"].append(f"missing required files: {', '.join(missing)}")
        return report

    for name, path in paths.items():
        report["files"][name] = {
            "bytes": path.stat().st_size,
            "sha256": _file_sha256(path),
        }

    try:
        metadata = load_json(paths["metadata.json"])
    except ImportValidationError as exc:
        report["errors"].append(str(exc))
        return report
    if not isinstance(metadata, dict):
        report["errors"].append("metadata.json must be a JSON object")
        return report

    observed_at = metadata.get("observedAt")
    source_id = metadata.get("sourceId")
    bookmaker_id = metadata.get("bookmakerId")

    try:
        normalized_observed_at = parse_iso_datetime(
            observed_at, field_name="metadata.observedAt"
        )
    except ImportValidationError as exc:
        report["errors"].append(str(exc))
        normalized_observed_at = None

    if not isinstance(source_id, str) or not source_id.strip():
        report["errors"].append("metadata.sourceId must be a non-empty string")
    if not isinstance(bookmaker_id, str) or not bookmaker_id.strip():
        report["errors"].append("metadata.bookmakerId must be a non-empty string")

    report["metadata"] = {
        "observedAt": normalized_observed_at or observed_at,
        "sourceId": source_id,
        "bookmakerId": bookmaker_id,
        "notes": metadata.get("notes"),
    }

    try:
        matchups = load_json(paths["matchups.json"])
        straight = load_json(paths["straight.json"])
        quality = build_import_quality_report(matchups, straight)
    except ImportValidationError as exc:
        report["errors"].append(str(exc))
        return report

    sensitive_paths = sorted(
        set(
            _find_sensitive_key_paths(metadata)
            + _find_sensitive_key_paths(matchups)
            + _find_sensitive_key_paths(straight)
        )
    )
    report["sensitiveKeyPaths"] = sensitive_paths
    if sensitive_paths:
        report["errors"].append(
            "possible sensitive keys detected; remove credentials, cookies, tokens, or session data"
        )

    report["qualityReport"] = quality
    flags = quality.get("qualityFlags", {})
    matched_count = int(quality.get("counts", {}).get("matchedMatchupIds", 0))
    all_quality_flags_pass = bool(flags) and all(bool(value) for value in flags.values())

    if matched_count == 0:
        report["errors"].append("no matched matchupId values were found")
    if not all_quality_flags_pass:
        report["warnings"].append(
            "one or more structural quality flags failed; review the nested quality report"
        )

    report["readyForImport"] = (
        not report["errors"] and all_quality_flags_pass and matched_count > 0
    )
    return report


def write_intake_report(report: dict[str, Any], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
