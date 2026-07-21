import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_committed_drift_report_is_reproducible(tmp_path: Path):
    generated = tmp_path / "generated.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_public_contract_drift_report_v1.py",
            "--output",
            str(generated),
        ],
        cwd=ROOT,
        check=True,
    )
    assert json.loads(generated.read_text(encoding="utf-8")) == read(
        "data/public/readiness-contract-drift-report-v1.json"
    )


def test_drift_report_is_ready_and_repository_only():
    report = read("data/public/readiness-contract-drift-report-v1.json")
    assert report["formalState"] == "OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_READY"
    assert report["checksPassed"] == report["checksTotal"] == 9
    assert report["driftCount"] == 0
    assert all(row["schemaMatch"] for row in report["contracts"])
    assert all(row["fixtureOnlyMatch"] for row in report["contracts"])
    assert all(row["allEqual"] for row in report["sharedFieldComparisons"])
    assert report["quality"] == {
        "repositoryOnly": True,
        "fixtureOnly": True,
        "networkCallsMade": False,
        "externalFilesRead": False,
        "rowLevelRecordsIncluded": False,
        "crossRepositoryWrite": False,
    }


def test_release_index_reads_only_committed_public_assets():
    html = (ROOT / "release-index.html").read_text(encoding="utf-8")
    assert "data/public/readiness-release-manifest-v1.json" in html
    assert "data/public/readiness-contract-drift-report-v1.json" in html
    assert "http://" not in html
    assert "https://" not in html


def test_changed_manifest_fails_closed(tmp_path: Path):
    manifest = read("data/public/readiness-release-manifest-v1.json")
    manifest["releaseVersion"] = "unexpected"
    changed = tmp_path / "manifest.json"
    output = tmp_path / "report.json"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_public_contract_drift_report_v1.py",
            "--manifest",
            str(changed),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert report["formalState"] == "OFFSEASON_PUBLIC_CONTRACT_DRIFT_REPORT_V1_DRIFT_DETECTED"
    assert report["driftCount"] >= 1
    assert "release_version" in report["failedChecks"]
