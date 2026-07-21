import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readiness_export_v2():
    data = json.loads((ROOT / "data/public/offseason-readiness.json").read_text())
    assert data["schemaVersion"] == "offseason-readiness-v2"
    assert data["fixtureMode"] is True
    assert data["currentMode"] == "offseason_sleep"
    assert data["collection"]["scheduled"] is False
    assert data["collection"]["productionScheduleImported"] is False
    assert data["reference"]["teams"] == 30
    assert data["reference"]["marketClasses"] == 11
    assert data["reference"]["sourceMetadataComplete"] is True
    assert data["reference"]["providerMetadataComplete"] is True
    assert data["mapping"]["acceptedCandidateUnverified"] == 2
    assert data["mapping"]["excluded"] == 4
    assert data["mapping"]["canonicalEventsCreated"] == 0
    assert data["realData"]["movementReadyQuoteIdentities"] == 0
    assert data["quality"]["aggregateOnly"] is True
    assert data["quality"]["rowLevelRecordsIncluded"] is False
    assert data["quality"]["networkCallsMade"] is False


def test_dashboard_uses_v2_fields():
    html = (ROOT / "readiness.html").read_text()
    assert "d.reference.teams" in html
    assert "d.mapping.acceptedCandidateUnverified" in html
    assert "d.quality.aggregateOnly" in html
