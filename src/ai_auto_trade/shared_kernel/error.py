"""Safe structured error envelope shared by operations boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import cast
from uuid import UUID

MAX_TEXT_LENGTH = 1024
UUID_V7_VERSION = 7


class ErrorCode(StrEnum):
    """Stable machine-readable error codes from C-ERR-001."""

    VALIDATION_FAILED = "VALIDATION_FAILED"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    IDEMPOTENCY_KEY_REUSED = "IDEMPOTENCY_KEY_REUSED"
    PRECONDITION_FAILED = "PRECONDITION_FAILED"
    COMMAND_NOT_FOUND = "COMMAND_NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    COMMAND_STATE_CONFLICT = "COMMAND_STATE_CONFLICT"
    RISK_REJECTED = "RISK_REJECTED"
    RUNTIME_NOT_READY = "RUNTIME_NOT_READY"
    RECONCILIATION_BLOCKED = "RECONCILIATION_BLOCKED"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    EXTERNAL_OUTCOME_UNKNOWN = "EXTERNAL_OUTCOME_UNKNOWN"
    AI_PROVIDER_NOT_ALLOWED = "AI_PROVIDER_NOT_ALLOWED"
    AI_MODEL_NOT_ALLOWED = "AI_MODEL_NOT_ALLOWED"
    AI_CONNECTION_SCOPE_DENIED = "AI_CONNECTION_SCOPE_DENIED"
    AI_CREDENTIAL_NOT_CONFIGURED = "AI_CREDENTIAL_NOT_CONFIGURED"
    AI_CREDENTIAL_VALIDATION_FAILED = "AI_CREDENTIAL_VALIDATION_FAILED"
    AI_ENROLLMENT_NOT_PERMITTED = "AI_ENROLLMENT_NOT_PERMITTED"
    AI_EGRESS_POLICY_DENIED = "AI_EGRESS_POLICY_DENIED"
    AI_BUDGET_EXCEEDED = "AI_BUDGET_EXCEEDED"
    AI_PROVIDER_UNAVAILABLE = "AI_PROVIDER_UNAVAILABLE"
    AI_OUTPUT_INVALID = "AI_OUTPUT_INVALID"
    AI_OUTCOME_UNKNOWN = "AI_OUTCOME_UNKNOWN"
    SENSITIVE_INPUT_REJECTED = "SENSITIVE_INPUT_REJECTED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    """Safe public error payload with no raw exception or secret data."""

    code: ErrorCode
    message: str
    details: Mapping[str, object]
    correlation_id: str
    retryable: bool
    remediation_hint: str

    def __post_init__(self) -> None:
        """Validate invariant fields at construction time."""
        if not self.message or len(self.message) > MAX_TEXT_LENGTH:
            raise ValueError("message must contain 1-1024 characters")
        if not self.remediation_hint or len(self.remediation_hint) > MAX_TEXT_LENGTH:
            raise ValueError("remediation_hint must contain 1-1024 characters")
        _validate_uuid_v7(self.correlation_id)
        _validate_details(self.details)

    def to_dict(self) -> dict[str, object]:
        """Serialize the envelope using the OpenAPI field names."""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": dict(self.details),
            "correlation_id": self.correlation_id,
            "retryable": self.retryable,
            "remediation_hint": self.remediation_hint,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ErrorEnvelope:
        """Deserialize and validate a structured error payload.

        Args:
            payload: OpenAPI-compatible mapping.

        Returns:
            A validated error envelope.

        Raises:
            ValueError: If a required field is absent or malformed.
        """
        code = _required_string(payload, "code")
        details = payload.get("details")
        if not isinstance(details, Mapping):
            raise ValueError("details must be an object")
        typed_details = cast(Mapping[str, object], details)
        retryable = payload.get("retryable")
        if not isinstance(retryable, bool):
            raise ValueError("retryable must be a boolean")
        return cls(
            code=ErrorCode(code),
            message=_required_string(payload, "message"),
            details=dict(typed_details),
            correlation_id=_required_string(payload, "correlation_id"),
            retryable=retryable,
            remediation_hint=_required_string(payload, "remediation_hint"),
        )


def _required_string(payload: Mapping[str, object], key: str) -> str:
    """Read a non-empty string field from a mapping."""
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _validate_uuid_v7(value: str) -> None:
    """Require a canonical lowercase UUIDv7 string."""
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise ValueError("correlation_id must be a UUIDv7") from exc
    if parsed.version != UUID_V7_VERSION or str(parsed) != value:
        raise ValueError("correlation_id must be a canonical UUIDv7")


def _validate_details(value: object, path: str = "details") -> None:
    """Reject secrets, exceptions and non-JSON values in structured details."""
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        for key, nested in mapping.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} keys must be strings")
            if any(
                fragment in key.lower() for fragment in ("secret", "password", "token", "api_key")
            ):
                raise ValueError(f"secret-like detail key is not allowed: {path}.{key}")
            _validate_details(nested, f"{path}.{key}")
        return
    if isinstance(value, list):
        items = cast(list[object], value)
        for index, nested in enumerate(items):
            _validate_details(nested, f"{path}[{index}]")
        return
    if value is None or isinstance(value, (str, int, float, bool)):
        return
    raise ValueError(f"{path} contains a non-JSON value")
