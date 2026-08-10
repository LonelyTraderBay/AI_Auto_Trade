"""Unit tests for the immutable audit event."""

import json
from pathlib import Path

import pytest

from ai_auto_trade.shared_kernel.audit import AuditEvent, AuditStatus

FIXTURE = Path("tests/fixtures/operations/audit-event.valid.json")


def test_audit_event_round_trip() -> None:
    """A command lifecycle audit event round-trips with UTC serialization."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    event = AuditEvent.from_dict(payload)

    assert event.status is AuditStatus.ACCEPTED
    assert event.to_dict() == payload


def test_audit_event_rejects_non_utc_timestamp() -> None:
    """Audit timestamps must use the canonical UTC Z suffix."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["recorded_at"] = "2026-08-10T20:07:02+00:00"

    with pytest.raises(ValueError, match="UTC"):
        AuditEvent.from_dict(payload)
