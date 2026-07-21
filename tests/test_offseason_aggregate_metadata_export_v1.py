import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "offseason_aggregate_metadata_builder",
    ROOT / "scripts/build_offseason_aggregate_metadata_export_v1.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
INVALID = MODULE.INVALID
READY = MODULE.READY
build_export = MODULE.build_export


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def docs():
    return [
        load("config/nba-team-registry-v1.json"),
        load("config/market-taxonomy-v1.json"),
        load("config/source-registry.json"),
        load("config/bookmaker-registry.json"),
        load("config/offseason-capture-readiness-v1.json"),
        load("data/phase2-odds-capture-request-v1.json"),
        load("data/fixtures/official-schedule-adapter-v1.json"),
    ]


def test_aggregate_export_matches_current_offseason_state():
    report = build_export(*docs(), as_of="2026-07-21")
    assert report["formalState"] == READY
    assert report["validation"]["checksPassed"] == 25
    assert report["validation"]["checksFailed"] == 0
    assert report["summary"] == {
        "teams": 30,
        "marketClasses": 11,
        "sources": 1,
        "providers": 1,
        "metadataMissingFields": 0,
        "automationApprovals": 0,
        "activeCadenceTemplates": 0,
        "fixtureScheduleGames": 6,
    }
    assert report["scheduleFixture"]["statusCounts"] == {
        "candidate_unverified": 2,
        "quarantined": 2,
        "rejected": 2,
    }
    assert report["privacyBoundary"]["rowLevelRecordsIncluded"] is False
    assert report["collectionState"]["phase2ApprovalGranted"] is False


def test_export_fails_closed_on_automation_permission_drift():
    values = docs()
    changed = copy.deepcopy(values[2])
    changed["sources"][0]["automationApproved"] = True
    report = build_export(values[0], values[1], changed, *values[3:], as_of="2026-07-21")
    assert report["formalState"] == INVALID
    assert "source_automation_disabled" in report["validation"]["failedChecks"]


def test_export_fails_closed_on_provider_metadata_gap():
    values = docs()
    changed = copy.deepcopy(values[3])
    del changed["bookmakers"][0]["definitionStatus"]
    report = build_export(values[0], values[1], values[2], changed, *values[4:], as_of="2026-07-21")
    assert report["formalState"] == INVALID
    assert "provider_metadata_complete" in report["validation"]["failedChecks"]


def test_committed_public_export_is_reproducible(tmp_path: Path):
    output = tmp_path / "offseason-metadata-readiness-v1.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_offseason_aggregate_metadata_export_v1.py",
            "--as-of",
            "2026-07-21",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
    )
    generated = json.loads(output.read_text(encoding="utf-8"))
    committed = load("data/public/offseason-metadata-readiness-v1.json")
    assert generated == committed


def test_public_export_omits_named_records():
    export = load("data/public/offseason-metadata-readiness-v1.json")
    text = json.dumps(export, sort_keys=True).lower()
    assert "pinnacle" not in text
    assert "fixture_official_schedule" not in text
    assert "20260001" not in text
    assert "displayname" not in text
