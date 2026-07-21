#!/usr/bin/env python3
"""Build deterministic SHA-256 checksums for committed public governance assets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = (
    "data/public/offseason-readiness.json",
    "data/public/offseason-metadata-readiness-v1.json",
    "data/public/readiness-release-manifest-v1.json",
    "data/public/readiness-contract-drift-report-v1.json",
    "release-index.html",
    "schemas/public/readiness-release-manifest-v1.schema.json",
    "schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json",
    "schemas/public/public-contract-drift-report-v1.schema.json",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build() -> dict:
    release = json.loads((ROOT / "data/public/readiness-release-manifest-v1.json").read_text(encoding="utf-8"))
    rows = []
    for relative in sorted(ASSETS):
        payload = (ROOT / relative).read_bytes()
        rows.append({"path": relative, "bytes": len(payload), "sha256": sha256(payload)})
    return {
        "schemaVersion": "public-governance-checksum-manifest-v1",
        "asOf": release["asOf"],
        "releaseVersion": release["releaseVersion"],
        "algorithm": "sha256",
        "assetCount": len(rows),
        "assets": rows,
        "quality": {
            "deterministicOrder": True,
            "repositoryOnly": True,
            "externalFilesRead": False,
            "networkCallsMade": False,
            "crossRepositoryWrite": False,
            "selfChecksumExcluded": True
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "data/public/public-governance-checksums-v1.json")
    args = parser.parse_args()
    report = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"assetCount": report["assetCount"], "algorithm": report["algorithm"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
