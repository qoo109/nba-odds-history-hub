from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "automation" / "full_pipeline.py"
SPEC = importlib.util.spec_from_file_location("full_pipeline", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_redact_url_removes_credentials_query_and_fragment() -> None:
    value = MODULE.redact_url(
        "https://user:pass@example.com:8443/path/data.json?token=secret#section"
    )
    assert value == "https://example.com:8443/path/data.json"


def test_sha256_bytes_is_stable() -> None:
    assert MODULE.sha256_bytes(b"nba") == (
        "1f1a4d92af8fbe2e099df1ef369738ce76713c614a8f03a29546d8b1f3b27c04"
    )


def test_normalize_filename_sanitizes_path() -> None:
    assert MODULE.normalize_filename("https://example.com/a%20b/file.json", "fallback") == "file.json"


def test_state_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "state" / "automation_state.json"
    payload = {"schema_version": "automation-state-v1", "sources": {"x": {"sha256": "a"}}}
    MODULE.write_json(path, payload)
    assert MODULE.load_json(path, {}) == payload
