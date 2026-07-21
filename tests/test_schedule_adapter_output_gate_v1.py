import json
from pathlib import Path

from nba_odds_history_hub.database import register_source, register_source_events
from nba_odds_history_hub.mapping import (
    build_mapping_readiness_report,
    record_mapping_decision,
    record_schedule_version,
)
from nba_odds_history_hub.schedule_output_gate import gate_fixture

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def persist_fixture_candidates(database: Path):
    payload = load("data/fixtures/official-schedule-adapter-v1.json")
    teams = load("config/nba-team-registry-v1.json")
    gated = gate_fixture(payload, teams)

    register_source(
        database,
        source_id=gated["sourceId"],
        display_name="Synthetic schedule fixture",
        source_class="synthetic_fixture",
        access_mode="fixture_only",
        usage_boundary="Repository tests only.",
    )
    rows = [
        {
            "source": row["source_id"],
            "source_event_id": row["source_event_id"],
            "bookmaker_id": None,
            "league": "NBA",
            "event_type": "game",
            "market_name": "fixture schedule",
            "scheduled_tipoff": row["scheduled_tipoff"],
            "cutoff_at": None,
            "canonical_event_id": None,
            "observed_at": row["observed_at"],
        }
        for row in gated["accepted"]
    ]
    register_source_events(database, rows)
    for row in gated["accepted"]:
        record_mapping_decision(
            database,
            source_id=row["source_id"],
            source_event_id=row["source_event_id"],
            new_status=row["mapping_status"],
            mapping_method=row["mapping_method"],
            reason_code="fixture_output_gate",
            actor_type="synthetic_fixture_gate",
            decided_at=row["observed_at"],
            source_payload_sha256=row["source_payload_sha256"],
        )
        record_schedule_version(
            database,
            source_id=row["source_id"],
            source_event_id=row["source_event_id"],
            scheduled_tipoff=row["scheduled_tipoff"],
            home_team_abbr=row["home_team_abbr"],
            away_team_abbr=row["away_team_abbr"],
            observed_at=row["observed_at"],
            source_payload_sha256=row["source_payload_sha256"],
            mapping_status=row["mapping_status"],
            mapping_method=row["mapping_method"],
        )
    return gated


def test_explicit_source_registry_upgrade():
    source = load("config/source-registry.json")
    assert source["schemaVersion"] == "v0.11-source-registry"
    assert len(source["sources"]) == 1
    record = source["sources"][0]
    assert record["active"] is True
    assert record["reviewStatus"] == "manual_only"
    assert record["rightsStatus"] == "owner_supplied_research"
    assert record["automationApproved"] is False


def test_gate_accepts_only_current_alias_candidates():
    payload = load("data/fixtures/official-schedule-adapter-v1.json")
    teams = load("config/nba-team-registry-v1.json")
    gated = gate_fixture(payload, teams)
    assert gated["acceptedCount"] == 2
    assert gated["excludedCount"] == 4
    assert gated["adapterCounts"] == {
        "candidate_unverified": 2,
        "quarantined": 2,
        "rejected": 2,
    }
    assert gated["canonicalEventIdsCreated"] == 0
    assert all(row["mapping_status"] == "candidate_unverified" for row in gated["accepted"])
    assert all(row["scheduled_tipoff"].endswith("Z") for row in gated["accepted"])


def test_fixture_output_gate_persists_only_accepted_rows(tmp_path):
    database = tmp_path / "fixture.sqlite"
    gated = persist_fixture_candidates(database)
    readiness = build_mapping_readiness_report(database)
    assert readiness["formalState"] == "OFFSEASON_MAPPING_DATABASE_READY"
    assert readiness["database"]["sourceEventCount"] == gated["acceptedCount"] == 2
    assert readiness["database"]["scheduleVersionCount"] == 2
    assert readiness["database"]["currentScheduleCount"] == 2
    assert readiness["database"]["auditDecisionCount"] == 2
    assert readiness["database"]["multipleCurrentScheduleGroups"] == 0
    assert readiness["mapping"]["statusCounts"] == {"candidate_unverified": 2}
    assert readiness["mapping"]["verifiedEventCount"] == 0


def test_exact_schedule_output_is_idempotent(tmp_path):
    database = tmp_path / "fixture.sqlite"
    gated = persist_fixture_candidates(database)
    row = gated["accepted"][0]
    result = record_schedule_version(
        database,
        source_id=row["source_id"],
        source_event_id=row["source_event_id"],
        scheduled_tipoff=row["scheduled_tipoff"],
        home_team_abbr=row["home_team_abbr"],
        away_team_abbr=row["away_team_abbr"],
        observed_at=row["observed_at"],
        source_payload_sha256=row["source_payload_sha256"],
        mapping_status=row["mapping_status"],
        mapping_method=row["mapping_method"],
    )
    assert result == {
        "inserted": False,
        "version_number": 1,
        "reason": "exact_current_schedule_duplicate",
    }
