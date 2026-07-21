#!/usr/bin/env python3
"""Validate the disabled one-time Phase 2 odds capture request packet."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "phase2-odds-capture-request-v1"
EXPECTED_REQUEST_ID = "ODDS-PHASE2-CAPTURE-2026-07-21-001"
EXPECTED_STATE = "AWAITING_EXPLICIT_OWNER_APPROVAL"
FORMAL_STATE = "PHASE2_ODDS_CAPTURE_REQUEST_VALID_AWAITING_EXPLICIT_OWNER_APPROVAL"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("request packet must be a JSON object")
    return value


def validate(packet: dict[str, Any]) -> dict[str, Any]:
    source = packet.get("source_approval") or {}
    capture = packet.get("capture_contract") or {}
    storage = packet.get("storage_and_output_boundary") or {}
    research = packet.get("research_boundary") or {}
    effect = packet.get("approval_effect") or {}

    checks: dict[str, bool] = {
        "schema_version": packet.get("schema_version") == EXPECTED_SCHEMA,
        "request_id": packet.get("request_id") == EXPECTED_REQUEST_ID,
        "repository_scope": packet.get("repository_scope") == "qoo109/nba-odds-history-hub",
        "request_state": packet.get("request_state") == EXPECTED_STATE,
        "approval_disabled": packet.get("approval_granted") is False,
        "execution_disabled": packet.get("execution_enabled") is False,
        "one_execution_maximum": packet.get("maximum_execution_count") == 1,
        "no_execution_yet": packet.get("execution_count") == 0,
        "manual_dispatch_only": packet.get("execution_mode") == "manual_workflow_dispatch_only",
        "workflow_path": packet.get("workflow") == ".github/workflows/full-automation.yml",
        "dispatch_inputs": packet.get("required_dispatch_inputs") == {
            "enable_odds_capture": True,
            "dry_run": False,
        },
        "required_secrets": set(packet.get("required_repository_secrets") or [])
        == {"ODDS_MATCHUPS_URL", "ODDS_STRAIGHT_URL"},
        "secret_values_not_committed": packet.get("secret_values_committed_to_repository") is False,
        "lawful_owner_approved_source": (
            source.get("owner_approved_urls_required") is True
            and source.get("lawful_free_or_public_source_required") is True
            and source.get("paid_source_allowed") is False
        ),
        "no_restricted_access": all(
            source.get(key) is False
            for key in (
                "login_required_source_allowed",
                "cookie_or_session_access_allowed",
                "authorization_header_or_token_allowed",
                "har_or_account_export_allowed",
                "captcha_bypass_allowed",
                "geo_restriction_bypass_allowed",
                "robots_or_terms_bypass_allowed",
                "rate_limit_bypass_allowed",
            )
        ),
        "manual_only_sites_not_automated": all(
            source.get(key) is False
            for key in (
                "automatic_oddsportal_access_allowed",
                "automatic_covers_access_allowed",
                "automatic_basketball_reference_access_allowed",
            )
        ),
        "required_payloads": set(capture.get("required_payloads") or [])
        == {"matchups.json", "straight.json"},
        "point_in_time_metadata": (
            capture.get("metadata_generated_at_capture") is True
            and capture.get("observed_at_must_be_timezone_aware") is True
            and capture.get("observed_at_source") == "actual_retrieval_time"
            and capture.get("source_id_required") is True
            and capture.get("bookmaker_id_required") is True
        ),
        "intake_and_retention_gates": (
            capture.get("intake_ready_for_import_required") is True
            and capture.get("changes_only_retention_required") is True
            and capture.get("overwrite_existing_snapshot_allowed") is False
            and capture.get("missing_rows_treated_as_unchanged") is False
        ),
        "no_opening_closing_labels": (
            capture.get("opening_label_allowed") is False
            and capture.get("closing_label_allowed") is False
        ),
        "public_storage_boundary": (
            storage.get("public_repository_raw_snapshot_commit_allowed") is False
            and storage.get("large_raw_file_commit_allowed") is False
            and storage.get("github_artifact_retention_days") == 14
            and storage.get("google_drive_automation_enabled_by_default") is False
            and storage.get("manual_google_drive_upload_mode") is True
        ),
        "no_sensitive_output": all(
            storage.get(key) is False
            for key in (
                "raw_credentials_emitted",
                "cookie_or_session_data_emitted",
                "authorization_headers_emitted",
                "har_files_emitted",
                "nba_value_lab_write_allowed",
            )
        ),
        "research_gates_closed": all(
            research.get(key) is False
            for key in (
                "historical_movement_ready",
                "opening_closing_classification_ready",
                "point_in_time_join_ready",
                "market_backtest_ready",
                "clv_ready",
                "ev_ready",
                "roi_ready",
                "drawdown_ready",
                "betting_edge_claim_allowed",
            )
        ) and research.get("formal_stake") == 0,
        "approval_scope_is_one_time_only": (
            effect.get("allows_exactly_one_manual_capture_attempt") is True
            and effect.get("allows_hourly_schedule") is False
            and effect.get("allows_daily_odds_capture") is False
            and effect.get("allows_new_source_without_review") is False
            and effect.get("allows_repeat_execution") is False
            and effect.get("allows_nba_value_lab_integration") is False
        ),
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schema_version": "phase2-odds-capture-request-validation-report-v1",
        "validated_at": utc_now(),
        "request_id": packet.get("request_id"),
        "formal_state": FORMAL_STATE if not failed else "PHASE2_ODDS_CAPTURE_REQUEST_INVALID",
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "checks_failed": len(failed),
        "failed_checks": failed,
        "approval_granted": False,
        "execution_enabled": False,
        "network_calls_made": 0,
        "odds_payloads_downloaded": 0,
        "snapshot_imported": False,
        "nba_value_lab_modified": False,
        "formal_stake": 0,
    }


def self_test(packet: dict[str, Any]) -> None:
    report = validate(packet)
    assert report["formal_state"] == FORMAL_STATE, report
    assert report["checks_failed"] == 0, report

    changed = json.loads(json.dumps(packet))
    changed["execution_enabled"] = True
    report = validate(changed)
    assert report["formal_state"] == "PHASE2_ODDS_CAPTURE_REQUEST_INVALID", report
    assert "execution_disabled" in report["failed_checks"], report

    changed = json.loads(json.dumps(packet))
    changed["source_approval"]["cookie_or_session_access_allowed"] = True
    report = validate(changed)
    assert report["formal_state"] == "PHASE2_ODDS_CAPTURE_REQUEST_INVALID", report
    assert "no_restricted_access" in report["failed_checks"], report

    changed = json.loads(json.dumps(packet))
    changed["approval_effect"]["allows_repeat_execution"] = True
    report = validate(changed)
    assert report["formal_state"] == "PHASE2_ODDS_CAPTURE_REQUEST_INVALID", report
    assert "approval_scope_is_one_time_only" in report["failed_checks"], report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--request",
        type=Path,
        default=Path("data/phase2-odds-capture-request-v1.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    packet = load_json(args.request)
    if args.self_test:
        self_test(packet)
    report = validate(packet)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "formal_state": report["formal_state"],
        "checks_passed": report["checks_passed"],
        "checks_total": report["checks_total"],
        "checks_failed": report["checks_failed"],
    }, indent=2))
    return 0 if report["formal_state"] == FORMAL_STATE else 1


if __name__ == "__main__":
    raise SystemExit(main())
