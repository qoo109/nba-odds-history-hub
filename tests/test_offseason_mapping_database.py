from pathlib import Path

import pytest

from nba_odds_history_hub.database import (
    connect_database,
    register_source,
    register_source_events,
    upsert_canonical_event,
)
from nba_odds_history_hub.mapping import (
    build_mapping_readiness_report,
    record_mapping_decision,
    record_schedule_version,
)


def _source_event_row(event_id: int, observed_at: str) -> dict:
    return {
        "source": "fixture_schedule",
        "source_event_id": event_id,
        "bookmaker_id": None,
        "league": "NBA",
        "event_type": "game",
        "market_name": f"Fixture event {event_id}",
        "scheduled_tipoff": "2026-10-20T23:30:00+00:00",
        "cutoff_at": None,
        "canonical_event_id": None,
        "observed_at": observed_at,
    }


def test_schedule_versions_and_mapping_audit_are_additive(tmp_path: Path) -> None:
    database = tmp_path / "mapping.sqlite"
    register_source(
        database,
        source_id="fixture_schedule",
        display_name="Fixture Schedule",
        source_class="synthetic_fixture",
        access_mode="offline",
    )
    observed = "2026-07-21T12:00:00+08:00"
    assert register_source_events(
        database,
        [_source_event_row(1001, observed), _source_event_row(1002, observed)],
    ) == 2

    first = record_schedule_version(
        database,
        source_id="fixture_schedule",
        source_event_id=1001,
        scheduled_tipoff="2026-10-20T19:30:00-04:00",
        home_team_abbr="BOS",
        away_team_abbr="ATL",
        observed_at=observed,
        source_payload_sha256="1" * 64,
    )
    duplicate = record_schedule_version(
        database,
        source_id="fixture_schedule",
        source_event_id=1001,
        scheduled_tipoff="2026-10-20T19:30:00-04:00",
        home_team_abbr="BOS",
        away_team_abbr="ATL",
        observed_at="2026-07-21T12:05:00+08:00",
        source_payload_sha256="1" * 64,
    )
    changed = record_schedule_version(
        database,
        source_id="fixture_schedule",
        source_event_id=1001,
        scheduled_tipoff="2026-10-20T20:00:00-04:00",
        home_team_abbr="BOS",
        away_team_abbr="ATL",
        observed_at="2026-07-21T12:10:00+08:00",
        source_payload_sha256="2" * 64,
    )
    second_event = record_schedule_version(
        database,
        source_id="fixture_schedule",
        source_event_id=1002,
        scheduled_tipoff="2026-10-20T22:00:00-04:00",
        home_team_abbr="NYK",
        away_team_abbr="PHI",
        observed_at=observed,
        source_payload_sha256="3" * 64,
    )

    assert first == {
        "inserted": True,
        "version_number": 1,
        "reason": "new_schedule_version",
    }
    assert duplicate == {
        "inserted": False,
        "version_number": 1,
        "reason": "exact_current_schedule_duplicate",
    }
    assert changed["inserted"] is True and changed["version_number"] == 2
    assert second_event["version_number"] == 1

    upsert_canonical_event(
        database,
        canonical_event_id="fixture-only:nba-game-1001",
        league="NBA",
        event_type="game",
        scheduled_tipoff="2026-10-21T00:00:00+00:00",
        home_team="BOS",
        away_team="ATL",
    )
    verified = record_mapping_decision(
        database,
        source_id="fixture_schedule",
        source_event_id=1001,
        new_status="verified",
        mapping_method="synthetic_fixture_only",
        reason_code="fixture_explicit_identity",
        actor_type="synthetic_test",
        decided_at="2026-07-21T12:20:00+08:00",
        canonical_event_id="fixture-only:nba-game-1001",
        source_payload_sha256="2" * 64,
    )
    quarantined = record_mapping_decision(
        database,
        source_id="fixture_schedule",
        source_event_id=1002,
        new_status="quarantined",
        mapping_method="none",
        reason_code="fixture_historical_alias_requires_review",
        actor_type="synthetic_test",
        decided_at="2026-07-21T12:20:00+08:00",
        source_payload_sha256="3" * 64,
    )

    assert verified["previous_status"] == "unmapped"
    assert verified["new_status"] == "verified"
    assert quarantined["new_status"] == "quarantined"

    with connect_database(database) as connection:
        versions = connection.execute(
            """
            SELECT source_event_id, version_number, is_current
            FROM source_event_schedule_versions
            ORDER BY source_event_id, version_number
            """
        ).fetchall()
        audits = connection.execute(
            "SELECT previous_status, new_status FROM source_event_mapping_audit ORDER BY mapping_audit_id"
        ).fetchall()
        statuses = connection.execute(
            "SELECT source_event_id, mapping_status FROM source_events ORDER BY source_event_id"
        ).fetchall()

    assert [tuple(row) for row in versions] == [
        (1001, 1, 0),
        (1001, 2, 1),
        (1002, 1, 1),
    ]
    assert [tuple(row) for row in audits] == [
        ("unmapped", "verified"),
        ("unmapped", "quarantined"),
    ]
    assert [tuple(row) for row in statuses] == [
        (1001, "verified"),
        (1002, "quarantined"),
    ]

    report = build_mapping_readiness_report(database)
    assert report["formalState"] == "OFFSEASON_MAPPING_DATABASE_READY"
    assert report["database"]["sourceEventCount"] == 2
    assert report["database"]["scheduleVersionCount"] == 3
    assert report["database"]["currentScheduleCount"] == 2
    assert report["database"]["auditDecisionCount"] == 2
    assert report["mapping"]["verifiedEventCount"] == 1
    assert report["mapping"]["verifiedCoveragePct"] == 50.0
    assert report["quality"]["rawRowsEmitted"] == 0
    assert report["quality"]["networkCallsMade"] is False


def test_mapping_contract_rejects_invalid_identity_inputs(tmp_path: Path) -> None:
    database = tmp_path / "invalid.sqlite"
    register_source(database, source_id="fixture_schedule", display_name="Fixture")
    register_source_events(
        database,
        [_source_event_row(1001, "2026-07-21T12:00:00+08:00")],
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        record_schedule_version(
            database,
            source_id="fixture_schedule",
            source_event_id=1001,
            scheduled_tipoff="2026-10-20T19:30:00",
            home_team_abbr="BOS",
            away_team_abbr="ATL",
            observed_at="2026-07-21T12:00:00+08:00",
            source_payload_sha256="1" * 64,
        )

    with pytest.raises(ValueError, match="must differ"):
        record_schedule_version(
            database,
            source_id="fixture_schedule",
            source_event_id=1001,
            scheduled_tipoff="2026-10-20T19:30:00-04:00",
            home_team_abbr="BOS",
            away_team_abbr="BOS",
            observed_at="2026-07-21T12:00:00+08:00",
            source_payload_sha256="1" * 64,
        )

    with pytest.raises(ValueError, match="requires canonical_event_id"):
        record_mapping_decision(
            database,
            source_id="fixture_schedule",
            source_event_id=1001,
            new_status="verified",
            mapping_method="synthetic_fixture_only",
            reason_code="missing_identity",
            actor_type="synthetic_test",
            decided_at="2026-07-21T12:00:00+08:00",
        )

    with pytest.raises(ValueError, match="Unsupported mapping method"):
        record_mapping_decision(
            database,
            source_id="fixture_schedule",
            source_event_id=1001,
            new_status="candidate_unverified",
            mapping_method="fuzzy_guess",
            reason_code="not_allowed",
            actor_type="synthetic_test",
            decided_at="2026-07-21T12:00:00+08:00",
        )
