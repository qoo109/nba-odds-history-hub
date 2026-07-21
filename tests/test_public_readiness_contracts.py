import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text())


def test_public_contract_versions():
    manifest = read("data/public/readiness-release-manifest-v1.json")
    legacy = read("data/public/offseason-readiness.json")
    current = read("data/public/offseason-metadata-readiness-v1.json")
    contracts = {item["contractId"]: item for item in manifest["contracts"]}
    assert manifest["releaseVersion"] == "v0.14"
    assert legacy["schemaVersion"] == contracts["legacy-readiness"]["schemaVersion"]
    assert current["schemaVersion"] == contracts["aggregate-readiness"]["schemaVersion"]
    assert legacy["summary"]["teams"] == current["summary"]["teams"] == 30
    assert legacy["summary"]["marketClasses"] == current["summary"]["marketClasses"] == 11


def test_public_release_is_inactive():
    boundary = read("data/public/readiness-release-manifest-v1.json")["releaseBoundary"]
    assert boundary["repositoryOnly"] is True
    assert boundary["collectionActivated"] is False
    assert boundary["productionScheduleImported"] is False
    assert boundary["networkCallsMade"] is False
    assert boundary["crossRepositoryWrite"] is False
