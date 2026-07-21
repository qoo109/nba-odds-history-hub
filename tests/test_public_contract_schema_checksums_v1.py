import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate(document_path, schema_path):
    schema = read(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(read(document_path))


def load_builder():
    path = ROOT / "scripts/build_public_governance_checksums_v1.py"
    spec = importlib.util.spec_from_file_location("checksum_builder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_public_documents_match_declared_json_schemas():
    validate(
        "data/public/readiness-release-manifest-v1.json",
        "schemas/public/readiness-release-manifest-v1.schema.json",
    )
    validate(
        "data/public/offseason-metadata-readiness-v1.json",
        "schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json",
    )
    validate(
        "data/public/readiness-contract-drift-report-v1.json",
        "schemas/public/public-contract-drift-report-v1.schema.json",
    )


def test_release_schema_fails_closed_on_activation_change():
    schema = read("schemas/public/readiness-release-manifest-v1.schema.json")
    document = copy.deepcopy(read("data/public/readiness-release-manifest-v1.json"))
    document["releaseBoundary"]["collectionActivated"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(document)


def test_aggregate_schema_fails_closed_on_row_level_change():
    schema = read("schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json")
    document = copy.deepcopy(read("data/public/offseason-metadata-readiness-v1.json"))
    document["privacyBoundary"]["rowLevelRecordsIncluded"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(document)


def test_committed_checksum_manifest_is_reproducible():
    module = load_builder()
    committed = read("data/public/public-governance-checksums-v1.json")
    assert committed == module.build()
    assert committed["assetCount"] == len(module.ASSETS) == len(committed["assets"])
    assert committed["algorithm"] == "sha256"


def test_each_committed_checksum_matches_file_bytes():
    manifest = read("data/public/public-governance-checksums-v1.json")
    for row in manifest["assets"]:
        payload = (ROOT / row["path"]).read_bytes()
        assert row["bytes"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
