"""DEV/CI-only conformance + negative tests for the Scriptorium contracts.

Two layers, deliberately independent of the portable runtime validator:

1. Conformance (catches schema<->example drift): validate EVERY examples/*.json
   against schemas/<format>/v<major>.json using the real `jsonschema` library,
   dispatching on each file's `schema_version`.

2. Negatives: every tests/fixtures/invalid/*.json must be REJECTED by BOTH
   tools/validate.py (the stdlib structural validator) AND jsonschema.

`jsonschema` is a DEV/CI-only dependency. tools/validate.py must stay stdlib-only
and is imported here purely as a module under test — it never imports jsonschema.
"""
import importlib.util
import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SCHEMAS_DIR = REPO_ROOT / "schemas"
INVALID_DIR = Path(__file__).resolve().parent / "fixtures" / "invalid"

SCHEMA_VERSION_RE = re.compile(r"^([a-z-]+)/(\d+)\.(\d+)$")


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _import_validate_module():
    """Import tools/validate.py as a module (it is stdlib-only)."""
    spec = importlib.util.spec_from_file_location(
        "scriptorium_validate", REPO_ROOT / "tools" / "validate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_mod = _import_validate_module()


def _schema_path_for(doc):
    """Map a document's schema_version (e.g. 'proposal/1.1') to schemas/proposal/v1.json."""
    m = SCHEMA_VERSION_RE.match(doc.get("schema_version", ""))
    assert m, f"malformed schema_version: {doc.get('schema_version')!r}"
    fmt, major = m.group(1), m.group(2)
    return SCHEMAS_DIR / fmt / f"v{major}.json"


EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.json"))
SCHEMA_FILES = sorted(SCHEMAS_DIR.glob("*/v*.json"))
INVALID_FILES = sorted(INVALID_DIR.glob("*.json"))

assert EXAMPLE_FILES, "no examples/*.json found"
assert SCHEMA_FILES, "no schemas/*/v*.json found"
assert INVALID_FILES, "no negative fixtures found under tests/fixtures/invalid/"


@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_schema_is_valid_draft_2020_12(schema_path):
    """Every authoritative schema must itself be valid Draft 2020-12 JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(_load_json(schema_path))


@pytest.mark.parametrize("example_path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_conforms_to_schema(example_path):
    """Every example validates against its dispatched schema (schema<->example drift)."""
    doc = _load_json(example_path)
    schema_path = _schema_path_for(doc)
    assert schema_path.exists(), f"missing schema for {example_path.name}: {schema_path}"
    schema = _load_json(schema_path)
    # Raises jsonschema.ValidationError on drift; fail loudly with the example name.
    jsonschema.validate(instance=doc, schema=schema)


@pytest.mark.parametrize("example_path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_passes_stdlib_validator(example_path):
    """The portable stdlib validator must also accept every example."""
    errors = validate_mod.validate_file(str(example_path))
    assert errors == [], f"stdlib validator rejected a valid example: {errors}"


def test_library_kb_examples_cover_1_0_and_1_1_honestly():
    """First-party examples demonstrate both compatibility and producer honesty."""
    legacy_path = EXAMPLES_DIR / "library-kb.v1.0.example.json"
    current_path = EXAMPLES_DIR / "library-kb.v1.1.example.json"
    assert legacy_path in EXAMPLE_FILES
    assert current_path in EXAMPLE_FILES

    for path in (legacy_path, current_path):
        doc = _load_json(path)
        match = SCHEMA_VERSION_RE.match(doc["schema_version"])
        assert match
        major, minor = int(match.group(2)), int(match.group(3))
        expected = re.search(r"\.v(\d+)\.(\d+)\.example\.json$", path.name)
        assert expected
        assert (major, minor) == (int(expected.group(1)), int(expected.group(2)))

        carries_citekey = any("citekey" in item for item in doc["items"])
        if carries_citekey:
            assert (major, minor) >= (1, 1), (
                "first-party library-kb examples carrying citekey must declare 1.1+"
            )

    assert not any("citekey" in item for item in _load_json(legacy_path)["items"])
    assert any("citekey" in item for item in _load_json(current_path)["items"])


def test_library_kb_1_1_keeps_citekey_optional():
    """The additive field remains optional even for documents declaring 1.1."""
    doc = _load_json(EXAMPLES_DIR / "library-kb.v1.1.example.json")
    for item in doc["items"]:
        item.pop("citekey", None)
    schema = _load_json(SCHEMAS_DIR / "library-kb" / "v1.json")
    jsonschema.validate(instance=doc, schema=schema)


def test_historical_library_kb_1_0_with_citekey_remains_accepted(tmp_path):
    """Do not turn the producer-version correction into a consumer break."""
    doc = _load_json(EXAMPLES_DIR / "library-kb.v1.1.example.json")
    doc["schema_version"] = "library-kb/1.0"

    schema = _load_json(SCHEMAS_DIR / "library-kb" / "v1.json")
    jsonschema.validate(instance=doc, schema=schema)

    historical_path = tmp_path / "historical-library-kb.json"
    historical_path.write_text(json.dumps(doc), encoding="utf-8")
    assert validate_mod.validate_file(str(historical_path)) == []


@pytest.mark.parametrize("invalid_path", INVALID_FILES, ids=lambda p: p.name)
def test_negative_rejected_by_stdlib_validator(invalid_path):
    """tools/validate.py must report INVALID (non-empty errors), never crash."""
    errors = validate_mod.validate_file(str(invalid_path))
    assert errors, f"stdlib validator unexpectedly accepted {invalid_path.name}"


@pytest.mark.parametrize("invalid_path", INVALID_FILES, ids=lambda p: p.name)
def test_negative_rejected_by_jsonschema(invalid_path):
    """jsonschema must also reject every negative fixture against its dispatched schema."""
    doc = _load_json(invalid_path)
    schema = _load_json(_schema_path_for(doc))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=doc, schema=schema)
