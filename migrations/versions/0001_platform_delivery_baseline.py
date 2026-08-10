"""Create platform delivery baseline tables.

Revision ID: 0001_platform_delivery_baseline
Revises: (base)
Create Date: 2026-08-06

Task: 0.3
Refs: ADR-0003, ADR-0004, ADR-0012, DATA-003 §3-6
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_platform_delivery_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APPROVED_CONTEXTS = (
    "reference",
    "market_data",
    "strategy",
    "risk",
    "execution",
    "portfolio_ledger",
    "research",
    "operations",
    "platform",
)


def upgrade() -> None:
    """Create platform schema and delivery tables per data-dictionary §3-6."""
    op.execute("CREATE SCHEMA IF NOT EXISTS platform")

    op.create_table(
        "outbox",
        sa.Column("outbox_id", sa.UUID(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column(
            "source_context",
            sa.Text(),
            sa.CheckConstraint(
                "source_context IN ('reference','market_data','strategy','risk',"
                "'execution','portfolio_ledger','research','operations','platform')",
                name="ck_outbox_source_context",
            ),
            nullable=False,
        ),
        sa.Column("source_aggregate_type", sa.Text(), nullable=False),
        sa.Column("source_aggregate_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column(
            "schema_version",
            sa.SmallInteger(),
            sa.CheckConstraint("schema_version > 0", name="ck_outbox_schema_version"),
            nullable=False,
        ),
        sa.Column("partition_key", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "payload_hash",
            sa.CHAR(64),
            sa.CheckConstraint("payload_hash ~ '^[0-9a-f]{64}$'", name="ck_outbox_payload_hash"),
            nullable=False,
        ),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column("causation_id", sa.UUID(), nullable=True),
        sa.Column("trace_id", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("outbox_id", name="pk_outbox"),
        sa.UniqueConstraint("event_id", name="uq_outbox_event_id"),
        sa.CheckConstraint("event_type <> ''", name="ck_outbox_event_type_nonempty"),
        sa.CheckConstraint("partition_key <> ''", name="ck_outbox_partition_key_nonempty"),
        sa.CheckConstraint("recorded_at >= occurred_at", name="ck_outbox_recorded_after_occurred"),
        schema="platform",
    )
    op.create_index(
        "ix_outbox_source_audit",
        "outbox",
        ["source_context", "source_aggregate_id", "recorded_at"],
        schema="platform",
    )

    op.create_table(
        "outbox_delivery_state",
        sa.Column("outbox_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            sa.CheckConstraint(
                "status IN ('PENDING','CLAIMED','PUBLISHED','DEAD_LETTER')",
                name="ck_ods_status",
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            sa.CheckConstraint("attempt_count >= 0", name="ck_ods_attempt_count"),
            nullable=False,
            server_default="0",
        ),
        sa.Column("next_attempt_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("claim_owner", sa.Text(), nullable=True),
        sa.Column(
            "claim_fencing_token",
            sa.BigInteger(),
            sa.CheckConstraint(
                "claim_fencing_token IS NULL OR claim_fencing_token > 0",
                name="ck_ods_fencing_token",
            ),
            nullable=True,
        ),
        sa.Column("claim_expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.Text(), nullable=True),
        sa.Column(
            "last_error_hash",
            sa.CHAR(64),
            sa.CheckConstraint(
                "last_error_hash IS NULL OR last_error_hash ~ '^[0-9a-f]{64}$'",
                name="ck_ods_error_hash",
            ),
            nullable=True,
        ),
        sa.Column(
            "delivery_version",
            sa.BigInteger(),
            sa.CheckConstraint("delivery_version >= 0", name="ck_ods_delivery_version"),
            nullable=False,
            server_default="0",
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("outbox_id", name="pk_outbox_delivery_state"),
        sa.ForeignKeyConstraint(
            ["outbox_id"],
            ["platform.outbox.outbox_id"],
            name="fk_ods_outbox",
            ondelete="RESTRICT",
        ),
        schema="platform",
    )
    op.create_index(
        "ix_ods_pending_claim",
        "outbox_delivery_state",
        ["next_attempt_at", "outbox_id"],
        schema="platform",
        postgresql_where=sa.text("status IN ('PENDING','CLAIMED')"),
    )
    op.create_index(
        "ix_ods_active_claims",
        "outbox_delivery_state",
        ["claim_owner", "claim_expires_at"],
        schema="platform",
        postgresql_where=sa.text("status = 'CLAIMED'"),
    )

    op.create_table(
        "inbox",
        sa.Column("inbox_id", sa.UUID(), nullable=False),
        sa.Column("consumer_id", sa.Text(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column(
            "schema_version",
            sa.SmallInteger(),
            sa.CheckConstraint("schema_version > 0", name="ck_inbox_schema_version"),
            nullable=False,
        ),
        sa.Column("partition_key", sa.Text(), nullable=False),
        sa.Column("source_context", sa.Text(), nullable=False),
        sa.Column(
            "result_hash",
            sa.CHAR(64),
            sa.CheckConstraint("result_hash ~ '^[0-9a-f]{64}$'", name="ck_inbox_result_hash"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("inbox_id", name="pk_inbox"),
        sa.UniqueConstraint("consumer_id", "event_id", name="uq_inbox_consumer_event"),
        sa.CheckConstraint("consumer_id <> ''", name="ck_inbox_consumer_nonempty"),
        sa.CheckConstraint("event_type <> ''", name="ck_inbox_event_type_nonempty"),
        sa.CheckConstraint("partition_key <> ''", name="ck_inbox_partition_key_nonempty"),
        sa.CheckConstraint("source_context <> ''", name="ck_inbox_source_context_nonempty"),
        sa.CheckConstraint("recorded_at >= processed_at", name="ck_inbox_recorded_after_processed"),
        schema="platform",
    )
    op.create_index(
        "ix_inbox_consumer_time",
        "inbox",
        ["consumer_id", "processed_at"],
        schema="platform",
    )
    op.create_index(
        "ix_inbox_correlation",
        "inbox",
        ["correlation_id", "processed_at"],
        schema="platform",
        postgresql_where=sa.text("correlation_id IS NOT NULL"),
    )

    op.create_table(
        "dead_letters",
        sa.Column("dead_letter_id", sa.UUID(), nullable=False),
        sa.Column("outbox_id", sa.UUID(), nullable=True),
        sa.Column("consumer_id", sa.Text(), nullable=True),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column(
            "failure_stage",
            sa.Text(),
            sa.CheckConstraint(
                "failure_stage IN ('PUBLISH','CONSUME')", name="ck_dl_failure_stage"
            ),
            nullable=False,
        ),
        sa.Column("failure_code", sa.Text(), nullable=False),
        sa.Column("failure_detail_redacted", sa.Text(), nullable=True),
        sa.Column(
            "payload_hash",
            sa.CHAR(64),
            sa.CheckConstraint("payload_hash ~ '^[0-9a-f]{64}$'", name="ck_dl_payload_hash"),
            nullable=False,
        ),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            sa.CheckConstraint("attempt_count > 0", name="ck_dl_attempt_count"),
            nullable=False,
        ),
        sa.Column("first_failed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("dead_letter_id", name="pk_dead_letters"),
        sa.ForeignKeyConstraint(
            ["outbox_id"],
            ["platform.outbox.outbox_id"],
            name="fk_dl_outbox",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("failure_code <> ''", name="ck_dl_failure_code_nonempty"),
        sa.CheckConstraint("event_type <> ''", name="ck_dl_event_type_nonempty"),
        sa.CheckConstraint("recorded_at >= first_failed_at", name="ck_dl_recorded_after_first"),
        schema="platform",
    )
    op.create_index(
        "ix_dl_event_time",
        "dead_letters",
        ["event_id", "recorded_at"],
        schema="platform",
    )
    op.create_index(
        "ix_dl_outbox_time",
        "dead_letters",
        ["outbox_id", "recorded_at"],
        schema="platform",
        postgresql_where=sa.text("outbox_id IS NOT NULL"),
    )
    op.create_index(
        "ix_dl_stage_time",
        "dead_letters",
        ["failure_stage", "recorded_at"],
        schema="platform",
    )


def downgrade() -> None:
    """Drop platform delivery tables (dev/rollback only — never on financial/audit data)."""
    op.drop_index("ix_dl_stage_time", table_name="dead_letters", schema="platform")
    op.drop_index("ix_dl_outbox_time", table_name="dead_letters", schema="platform")
    op.drop_index("ix_dl_event_time", table_name="dead_letters", schema="platform")
    op.drop_table("dead_letters", schema="platform")
    op.drop_index("ix_inbox_correlation", table_name="inbox", schema="platform")
    op.drop_index("ix_inbox_consumer_time", table_name="inbox", schema="platform")
    op.drop_table("inbox", schema="platform")
    op.drop_index(
        "ix_ods_active_claims",
        table_name="outbox_delivery_state",
        schema="platform",
    )
    op.drop_index(
        "ix_ods_pending_claim",
        table_name="outbox_delivery_state",
        schema="platform",
    )
    op.drop_table("outbox_delivery_state", schema="platform")
    op.drop_index("ix_outbox_source_audit", table_name="outbox", schema="platform")
    op.drop_table("outbox", schema="platform")
    op.execute("DROP SCHEMA IF EXISTS platform")
