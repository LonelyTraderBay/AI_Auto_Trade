"""Operations audit envelope compatibility tests."""

from datetime import UTC, datetime

from ai_auto_trade.shared_kernel.audit import AuditEvent, AuditStatus


def test_operations_audit_contains_command_lifecycle_fields() -> None:
    """Audit events contain the fields required by master §11.2."""
    event = AuditEvent(
        command_id="0190f000-0000-7000-8000-000000000021",
        actor_id="0190f000-0000-7000-8000-000000000022",
        type="operations.command_succeeded.v1",
        schema_version=1,
        status=AuditStatus.SUCCEEDED,
        correlation_id="0190f000-0000-7000-8000-000000000023",
        recorded_at=datetime(2026, 8, 10, 20, 7, 2, tzinfo=UTC),
    )

    assert set(event.to_dict()) == {
        "command_id",
        "actor_id",
        "type",
        "schema_version",
        "status",
        "correlation_id",
        "recorded_at",
    }
