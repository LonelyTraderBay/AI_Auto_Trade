"""Unit tests for the safe error envelope."""

import json
from pathlib import Path

import pytest

from ai_auto_trade.shared_kernel.error import ErrorCode, ErrorEnvelope

FIXTURE = Path("tests/fixtures/operations/error-envelope.valid.json")
INVALID_FIXTURE = Path("tests/fixtures/operations/error-envelope.invalid.json")


def test_error_envelope_round_trip() -> None:
    """A valid OpenAPI error envelope round-trips without data loss."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    envelope = ErrorEnvelope.from_dict(payload)

    assert envelope.code is ErrorCode.VALIDATION_FAILED
    assert envelope.to_dict() == payload


def test_error_envelope_rejects_unknown_code() -> None:
    """Unknown error codes must not enter the public envelope."""
    payload = json.loads(INVALID_FIXTURE.read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="UNKNOWN_CODE"):
        ErrorEnvelope.from_dict(payload)


def test_error_envelope_rejects_non_v7_correlation_id() -> None:
    """Correlation IDs must be canonical UUIDv7 values."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["correlation_id"] = "0190f000-0000-4000-8000-000000000010"

    with pytest.raises(ValueError, match="UUIDv7"):
        ErrorEnvelope.from_dict(payload)


def test_error_envelope_rejects_secret_like_details() -> None:
    """Structured details cannot carry secret-like fields."""
    with pytest.raises(ValueError, match="secret-like"):
        ErrorEnvelope(
            code=ErrorCode.VALIDATION_FAILED,
            message="invalid",
            details={"api_key": "redacted"},
            correlation_id="0190f000-0000-7000-8000-000000000010",
            retryable=False,
            remediation_hint="fix the input",
        )
