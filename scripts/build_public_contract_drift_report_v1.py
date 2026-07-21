#!/usr/bin/env python3
"""Build a deterministic, repository-only drift report for public readiness contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
READY = "OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_READY"
DRIFT = "OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_DRIFT_DETECTED"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def nested_get(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for key in dotted_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def build(manifest_path: Path) -> dict[str, Any]:
    manifest = load(manifest_path)
    contracts: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}

    for item in manifest.get("contracts") or []:
        contract_id = str(item.get("contractId"))
        relative_path = str(item.get("path"))
        document = load(ROOT / relative_path)
        loaded[contract_id] = document
        contracts.append(
            {
                "contractId": contract_id,
                "path": relative_path,
                "compatibility": item.get("compatibility"),
                "expectedSchemaVersion": item.get("schemaVersion"),
                "actualSchemaVersion": document.get("schemaVersion"),
                "schemaMatch": document.get("schemaVersion") == item.get("schemaVersion"),
                "expectedFixtureOnly": item.get("fixtureOnly"),
                "actualFixtureOnly": document.get("fixtureMode"),
                "fixtureOnlyMatch": document.get("fixtureMode") == item.get("fixtureOnly"),
            }
        )

    shared_paths = ["summary.teams", "summary.marketClasses", "fixtureMode", "currentMode"]
    shared: list[dict[str, Any]] = []
    for dotted_path in shared_paths:
        values = {contract_id: nested_get(document, dotted_path) for contract_id, document in loaded.items()}
        comparable = list(values.values())
        shared.append(
            {
                "field": dotted_path,
                "values": values,
                "allPresent": all(value is not None for value in comparable),
                "allEqual": bool(comparable) and len(set(json.dumps(value, sort_keys=True) for value in comparable)) == 1,
            }
        )

    boundary = manifest.get("releaseBoundary") or {}
    safe_boundary = {
        "repositoryOnly": boundary.get("repositoryOnly") is True,
        "aggregateOnly": boundary.get("aggregateOnly") is True,
        "collectionActivated": boundary.get("collectionActivated") is False,
        "productionScheduleImported": boundary.get("productionScheduleImported") is False,
        "networkCallsMade": boundary.get("networkCallsMade") is False,
        "externalFilesRead": boundary.get("externalFilesRead") is False,
        "crossRepositoryWrite": boundary.get("crossRepositoryWrite") is False,
    }

    checks = {
        "manifest_schema": manifest.get("schemaVersion") == "readiness-release-manifest-v1",
        "release_version": manifest.get("releaseVersion") == "v0.14",
        "exact_contract_count": len(contracts) == 2,
        "contract_ids_unique": len({row["contractId"] for row in contracts}) == len(contracts),
        "contract_schemas_match": all(row["schemaMatch"] for row in contracts),
        "fixture_flags_match": all(row["fixtureOnlyMatch"] for row in contracts),
        "shared_fields_present": all(row["allPresent"] for row in shared),
        "shared_fields_equal": all(row["allEqual"] for row in shared),
        "release_boundary_safe": all(safe_boundary.values()),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)

    return {
        "schemaVersion": "public-contract-drift-report-v1",
        "asOf": manifest.get("asOf"),
        "releaseVersion": manifest.get("releaseVersion"),
        "formalState": READY if not failed else DRIFT,
        "checks": checks,
        "checksPassed": len(checks) - len(failed),
        "checksTotal": len(checks),
        "checksFailed": len(failed),
        "failedChecks": failed,
        "driftCount": len(failed),
        "contracts": contracts,
        "sharedFieldComparisons": shared,
        "releaseBoundary": boundary,
        "quality": {
            "repositoryOnly": True,
            "fixtureOnly": True,
            "networkCallsMade": False,
            "externalFilesRead": False,
            "rowLevelRecordsIncluded": False,
            "crossRepositoryWrite": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/public/readiness-release-manifest-v1.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "runtime/reports/readiness-contract-drift-v1.json",
    )
    args = parser.parse_args()

    report = build(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"formalState": report["formalState"], "checksPassed": report["checksPassed"], "checksTotal": report["checksTotal"], "driftCount": report["driftCount"]}, indent=2))
    return 0 if report["formalState"] == READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
