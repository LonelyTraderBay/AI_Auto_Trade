"""Immutable audit event value object for operations command lifecycle."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

UUID_V7_VERSION = 7


class AuditStatus(StrEnum):
    """Command lifecycle states that may be recorded in an audit event."""

    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Immutable command lifecycle audit event."""

    command_id: str
    actor_id: str
    type: str
    schema_version: int
    status: AuditStatus
    correlation_id: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        """Validate identifiers, type and UTC timestamp."""
        for field_name, value in (
            ("command_id", self.command_id),
            ("actor_id", self.actor_id),
            ("correlation_id", self.correlation_id),
        ):
            _validate_uuid_v7(value, field_name)
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        if not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+\.v[1-9][0-9]*", self.type):
            raise ValueError("type must be a versioned event name")
        if self.recorded_at.tzinfo != UTC:
            raise ValueError("recorded_at must use UTC")

    def to_dict(self) -> dict[str, object]:
        """Serialize the event using the canonical field names."""
        return {
            "command_id": self.command_id,
            "actor_id": self.actor_id,
            "type": self.type,
            "schema_version": self.schema_version,
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "recorded_at": self.recorded_at.isoformat().replace("+00:00", "Z"),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> AuditEvent:
        """Deserialize and validate a command lifecycle audit event."""
        recorded_at = payload.get("recorded_at")
        if not isinstance(recorded_at, str):
            raise ValueError("recorded_at must be an ISO-8601 string")
        if not recorded_at.endswith("Z"):
            raise ValueError("recorded_at must use UTC Z suffix")
        try:
            parsed_recorded_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("recorded_at must be an ISO-8601 timestamp") from exc
        return cls(
            command_id=_required_string(payload, "command_id"),
            actor_id=_required_string(payload, "actor_id"),
            type=_required_string(payload, "type"),
            schema_version=_required_int(payload, "schema_version"),
            status=AuditStatus(_required_string(payload, "status")),
            correlation_id=_required_string(payload, "correlation_id"),
            recorded_at=parsed_recorded_at,
        )


def _required_string(payload: dict[str, object], key: str) -> str:
    """Read a non-empty string field."""
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(payload: dict[str, object], key: str) -> int:
    """Read an integer field without accepting booleans."""
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _validate_uuid_v7(value: str, field_name: str) -> None:
    """Require a canonical lowercase UUIDv7 string."""
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a UUIDv7") from exc
    if parsed.version != UUID_V7_VERSION or str(parsed) != value:
        raise ValueError(f"{field_name} must be a canonical UUIDv7")
