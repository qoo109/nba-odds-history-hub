import copy
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


def test_documents_match_schemas():
    validate("data/public/readiness-release-manifest-v1.json", "schemas/public/readiness-release-manifest-v1.schema.json")
    validate("data/public/offseason-metadata-readiness-v1.json", "schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json")
    validate("data/public/readiness-contract-drift-report-v1.json", "schemas/public/public-contract-drift-report-v1.schema.json")


def test_release_schema_rejects_activation_change():
    schema = read("schemas/public/readiness-release-manifest-v1.schema.json")
    document = copy.deepcopy(read("data/public/readiness-release-manifest-v1.json"))
    document["releaseBoundary"]["collectionActivated"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(document)


def test_aggregate_schema_rejects_row_level_change():
    schema = read("schemas/public/offseason-aggregate-metadata-readiness-v1.schema.json")
    document = copy.deepcopy(read("data/public/offseason-metadata-readiness-v1.json"))
    document["privacyBoundary"]["rowLevelRecordsIncluded"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(document)


def test_builder_is_deterministic():
    module = load_builder()
    first = module.build()
    second = module.build()
    assert first == second
    assert first["assetCount"] == len(module.ASSETS) == len(first["assets"])
    assert first["algorithm"] == "sha256"
