"""Contract tests — integration event envelope schema — Task 0.4.

Validates that the canonical event envelope JSON Schema correctly accepts
valid fixtures and rejects known-invalid payloads.

Refs: ADR-0004, contracts/events/platform/integration-event-envelope.v1.schema.json
"""

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = (
    REPO_ROOT / "contracts" / "events" / "platform" / "integration-event-envelope.v1.schema.json"
)
VALID_FIXTURE_PATH = (
    REPO_ROOT / "contracts" / "fixtures" / "integration-event-envelope.v1.valid.json"
)


@pytest.fixture(scope="module")
def envelope_schema() -> dict[str, Any]:
    """Load the event envelope JSON Schema."""
    with SCHEMA_PATH.open() as f:
        schema: dict[str, Any] = json.load(f)
        return schema


@pytest.fixture(scope="module")
def valid_fixture() -> dict[str, Any]:
    """Load the valid event envelope fixture."""
    with VALID_FIXTURE_PATH.open() as f:
        fixture: dict[str, Any] = json.load(f)
        return fixture


def _validate(schema: dict[str, Any], instance: dict[str, Any]) -> list[ValidationError]:
    """Run Draft202012Validator and return all errors.

    Args:
        schema: JSON Schema dict.
        instance: Instance dict to validate.

    Returns:
        List of ValidationError objects; empty means valid.
    """
    validator = Draft202012Validator(schema)
    return list(validator.iter_errors(instance))  # pyright: ignore[reportUnknownMemberType]


def test_schema_is_valid_draft_2020_12(envelope_schema: dict[str, Any]) -> None:
    """The event envelope schema must itself be a valid JSON Schema Draft 2020-12."""
    Draft202012Validator.check_schema(envelope_schema)


def test_valid_fixture_passes_schema(
    envelope_schema: dict[str, Any],
    valid_fixture: dict[str, Any],
) -> None:
    """The canonical valid fixture must validate against the envelope schema."""
    errors = _validate(envelope_schema, valid_fixture)
    assert not errors, f"Valid fixture failed schema validation: {errors}"


def test_missing_required_field_fails(envelope_schema: dict[str, Any]) -> None:
    """An envelope missing a required field must fail validation."""
    invalid: dict[str, Any] = {"id": "01932d4e-7a3b-7000-8000-000000000001"}
    errors = _validate(envelope_schema, invalid)
    assert errors, "Expected validation errors for incomplete envelope"


def test_invalid_event_type_format_fails(
    envelope_schema: dict[str, Any],
    valid_fixture: dict[str, Any],
) -> None:
    """An event type not matching the versioned past-tense pattern must fail."""
    bad: dict[str, Any] = {**valid_fixture, "type": "InvalidType"}
    errors = _validate(envelope_schema, bad)
    assert errors, "Expected validation error for invalid event type format"


def test_wrong_schema_version_fails(
    envelope_schema: dict[str, Any],
    valid_fixture: dict[str, Any],
) -> None:
    """schema_version must be exactly 1 (const); any other value must fail."""
    bad: dict[str, Any] = {**valid_fixture, "schema_version": 2}
    errors = _validate(envelope_schema, bad)
    assert errors, "Expected validation error for schema_version != 1"


def test_float_timestamp_fails(
    envelope_schema: dict[str, Any],
    valid_fixture: dict[str, Any],
) -> None:
    """Timestamps must be strings (ISO-8601 UTC with Z); float is not allowed."""
    bad: dict[str, Any] = {**valid_fixture, "occurred_at": 1234567890.0}
    errors = _validate(envelope_schema, bad)
    assert errors, "Expected validation error for float timestamp"


def test_non_utc_timestamp_fails(
    envelope_schema: dict[str, Any],
    valid_fixture: dict[str, Any],
) -> None:
    """Timestamps without Z suffix must fail (UTC enforcement)."""
    bad: dict[str, Any] = {**valid_fixture, "occurred_at": "2026-08-06T00:00:00+00:00"}
    errors = _validate(envelope_schema, bad)
    assert errors, "Expected validation error for non-Z timestamp"
