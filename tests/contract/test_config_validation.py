"""Contract tests for the local configuration validation path."""

import json
from pathlib import Path
from typing import Protocol, cast

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ai_auto_trade.contexts.operations.application.config_validation import (
    ConfigValidationError,
    load_json_yaml_document,
    validate_config_layers,
)

REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "configs" / "sample-manifest.yaml"
SCHEMA_PATH = REPO_ROOT / "contracts" / "config" / "deployment-manifest.v1.schema.json"
BASE_PATH = REPO_ROOT / "configs" / "base.yaml"
LOCAL_PATH = REPO_ROOT / "configs" / "environments" / "local.yaml"


class _SchemaValidator(Protocol):
    """Minimal typed surface needed from jsonschema's validator."""

    def validate(self, instance: object) -> None:
        """Validate one instance or raise a schema validation error."""


def _load_json(path: Path) -> dict[str, object]:
    """Load a JSON object fixture."""
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return cast(dict[str, object], parsed)


def test_sample_manifest_passes_canonical_schema() -> None:
    """The local BACKTEST manifest must satisfy the deployment contract."""
    schema = _load_json(SCHEMA_PATH)
    manifest = load_json_yaml_document(MANIFEST_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    cast(_SchemaValidator, validator).validate(manifest)


def test_invalid_manifest_tuple_is_rejected() -> None:
    """A BACKTEST manifest cannot claim venue execution or credentials."""
    schema = _load_json(SCHEMA_PATH)
    manifest = load_json_yaml_document(MANIFEST_PATH)
    manifest["execution_target"] = "VENUE_LIVE"

    with pytest.raises(ValidationError):
        validator = Draft202012Validator(schema)
        cast(_SchemaValidator, validator).validate(manifest)


def test_config_precedence_is_base_then_environment() -> None:
    """Environment values override allowed keys without replacing the base map."""
    effective = validate_config_layers(BASE_PATH, LOCAL_PATH)

    assert effective["config_version"] == 1
    assert effective["environment"] == "local"
    service = effective["service"]
    assert isinstance(service, dict)
    assert service["name"] == "ai-auto-trade"
    assert service["bind_host"] == "127.0.0.1"


def test_environment_cannot_override_safety_owned_sections(tmp_path: Path) -> None:
    """Risk/strategy/execution/venue/AI sections cannot be environment overrides."""
    unsafe = tmp_path / "unsafe.yaml"
    unsafe.write_text(
        '{"config_version": 1, "environment": "local", "risk": {"cap": "1"}}',
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError, match="safety-owned"):
        validate_config_layers(BASE_PATH, unsafe)
