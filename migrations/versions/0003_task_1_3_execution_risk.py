"""Create Task 1.3 execution and risk persistence tables.

Revision ID: 0003_task_1_3_execution_risk
Revises: 0002_platform_idempotency_keys
Create Date: 2026-08-13

Task: 1.3
Refs: ADR-0002, ADR-0004, ADR-0005, ADR-0007, ADR-0012, DATA-DICT-T1.3-ADDENDUM-001
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003_task_1_3_execution_risk"
down_revision: str | None = "0002_platform_idempotency_keys"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UTC = sa.TIMESTAMP(timezone=True)
_DECIMAL = sa.Numeric(38, 18)
_HASH = sa.CHAR(64)


def upgrade() -> None:
    """Create immutable execution/risk facts and mutable CAS state."""
    op.execute("CREATE SCHEMA IF NOT EXISTS risk")
    op.execute("CREATE SCHEMA IF NOT EXISTS execution")

    op.create_table(
        "policies",
        sa.Column("policy_id", sa.UUID(), nullable=False),
        sa.Column("scope_key", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("policy_hash", _HASH, nullable=False),
        sa.Column("parameters", JSONB, nullable=False),
        sa.Column("effective_at", _UTC, nullable=False),
        sa.Column("expires_at", _UTC, nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("approval_evidence_ref", sa.Text(), nullable=False),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.PrimaryKeyConstraint("policy_id", name="pk_risk_policies"),
        sa.UniqueConstraint("scope_key", "policy_version", name="uq_risk_policy_scope_version"),
        sa.CheckConstraint("scope_key <> ''", name="ck_risk_policy_scope_nonempty"),
        sa.CheckConstraint("policy_version <> ''", name="ck_risk_policy_version_nonempty"),
        sa.CheckConstraint("policy_hash ~ '^[0-9a-f]{64}$'", name="ck_risk_policy_hash"),
        sa.CheckConstraint(
            "status IN ('DRAFT','ACTIVE','SUPERSEDED','EXPIRED')",
            name="ck_risk_policy_status",
        ),
        sa.CheckConstraint("expires_at > effective_at", name="ck_risk_policy_expiry"),
        schema="risk",
    )

    op.create_table(
        "reservations",
        sa.Column("reservation_id", sa.UUID(), nullable=False),
        sa.Column("order_intent_id", sa.UUID(), nullable=False),
        sa.Column("reservation_kind", sa.Text(), nullable=False),
        sa.Column("scope_key", sa.Text(), nullable=False),
        sa.Column("asset", sa.Text(), nullable=False),
        sa.Column("reserved_amount", _DECIMAL, nullable=False),
        sa.Column("lifecycle", sa.Text(), nullable=False),
        sa.Column("policy_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", _UTC, nullable=False),
        sa.Column("released_at", _UTC, nullable=True),
        sa.Column("consumed_at", _UTC, nullable=True),
        sa.Column("aggregate_version", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.PrimaryKeyConstraint("reservation_id", name="pk_risk_reservations"),
        sa.ForeignKeyConstraint(
            ["policy_id"], ["risk.policies.policy_id"], name="fk_reservation_policy"
        ),
        sa.UniqueConstraint(
            "order_intent_id", "reservation_kind", name="uq_risk_reservation_intent_kind"
        ),
        sa.CheckConstraint("reservation_kind <> ''", name="ck_risk_reservation_kind"),
        sa.CheckConstraint("scope_key <> ''", name="ck_risk_reservation_scope"),
        sa.CheckConstraint("asset <> ''", name="ck_risk_reservation_asset"),
        sa.CheckConstraint("reserved_amount >= 0", name="ck_risk_reservation_amount"),
        sa.CheckConstraint(
            "lifecycle IN ('ACTIVE','RELEASED','CONSUMED','EXPIRED')",
            name="ck_risk_reservation_lifecycle",
        ),
        sa.CheckConstraint("aggregate_version >= 0", name="ck_risk_reservation_version"),
        schema="risk",
    )

    op.create_table(
        "decisions",
        sa.Column("decision_id", sa.UUID(), nullable=False),
        sa.Column("order_intent_id", sa.UUID(), nullable=False),
        sa.Column("verdict", sa.Text(), nullable=False),
        sa.Column("approved_quantity", _DECIMAL, nullable=False),
        sa.Column("policy_id", sa.UUID(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("policy_hash", _HASH, nullable=False),
        sa.Column("reservation_id", sa.UUID(), nullable=True),
        sa.Column("portfolio_snapshot_hash", _HASH, nullable=False),
        sa.Column("market_snapshot_hash", _HASH, nullable=False),
        sa.Column("input_hash", _HASH, nullable=False),
        sa.Column("reason_code", sa.Text(), nullable=False),
        sa.Column("decided_at", _UTC, nullable=False),
        sa.Column("expires_at", _UTC, nullable=False),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.PrimaryKeyConstraint("decision_id", name="pk_risk_decisions"),
        sa.ForeignKeyConstraint(
            ["policy_id"], ["risk.policies.policy_id"], name="fk_decision_policy"
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"], ["risk.reservations.reservation_id"], name="fk_decision_reservation"
        ),
        sa.CheckConstraint(
            "verdict IN ('APPROVE','REJECT','REQUIRE_MANUAL_APPROVAL')",
            name="ck_risk_decision_verdict",
        ),
        sa.CheckConstraint("approved_quantity >= 0", name="ck_risk_decision_quantity"),
        sa.CheckConstraint("policy_version <> ''", name="ck_risk_decision_policy_version"),
        sa.CheckConstraint("policy_hash ~ '^[0-9a-f]{64}$'", name="ck_risk_decision_policy_hash"),
        sa.CheckConstraint(
            "portfolio_snapshot_hash ~ '^[0-9a-f]{64}$'",
            name="ck_risk_decision_portfolio_hash",
        ),
        sa.CheckConstraint(
            "market_snapshot_hash ~ '^[0-9a-f]{64}$'", name="ck_risk_decision_market_hash"
        ),
        sa.CheckConstraint("input_hash ~ '^[0-9a-f]{64}$'", name="ck_risk_decision_input_hash"),
        sa.CheckConstraint("reason_code <> ''", name="ck_risk_decision_reason"),
        sa.CheckConstraint("expires_at > decided_at", name="ck_risk_decision_expiry"),
        schema="risk",
    )

    op.create_table(
        "limit_state",
        sa.Column("scope_key", sa.Text(), nullable=False),
        sa.Column("counters", JSONB, nullable=False),
        sa.Column("aggregate_version", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("fencing_token", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("updated_at", _UTC, nullable=False),
        sa.PrimaryKeyConstraint("scope_key", name="pk_risk_limit_state"),
        sa.CheckConstraint("scope_key <> ''", name="ck_risk_limit_scope"),
        sa.CheckConstraint("aggregate_version >= 0", name="ck_risk_limit_version"),
        sa.CheckConstraint("fencing_token > 0", name="ck_risk_limit_fencing"),
        schema="risk",
    )

    op.create_table(
        "orders",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("order_intent_id", sa.UUID(), nullable=False),
        sa.Column("client_order_id", sa.Text(), nullable=False),
        sa.Column("venue_id", sa.Text(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("instrument_id", sa.UUID(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("terminal_reason", sa.Text(), nullable=True),
        sa.Column("aggregate_version", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("request_hash", _HASH, nullable=False),
        sa.Column("quantity", _DECIMAL, nullable=False),
        sa.Column("limit_price", _DECIMAL, nullable=True),
        sa.Column("created_at", _UTC, nullable=False),
        sa.Column("expires_at", _UTC, nullable=False),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("order_id", name="pk_execution_orders"),
        sa.UniqueConstraint(
            "venue_id", "account_id", "client_order_id", name="uq_execution_client_order"
        ),
        sa.CheckConstraint(
            "state IN ('CREATED','PENDING_MANUAL_APPROVAL','RISK_APPROVED',"
            "'RISK_REJECTED','SUBMISSION_QUEUED','SUBMITTING','OPEN',"
            "'PARTIALLY_FILLED','FILLED','REJECTED','CANCEL_REQUESTED',"
            "'CANCELLED','EXPIRED','UNKNOWN','RECONCILING','LOST')",
            name="ck_execution_order_state",
        ),
        sa.CheckConstraint("client_order_id <> ''", name="ck_execution_client_order_nonempty"),
        sa.CheckConstraint("venue_id <> ''", name="ck_execution_venue_nonempty"),
        sa.CheckConstraint("aggregate_version >= 0", name="ck_execution_order_version"),
        sa.CheckConstraint("request_hash ~ '^[0-9a-f]{64}$'", name="ck_execution_order_hash"),
        sa.CheckConstraint("quantity > 0", name="ck_execution_order_quantity"),
        sa.CheckConstraint(
            "limit_price IS NULL OR limit_price > 0", name="ck_execution_order_price"
        ),
        sa.CheckConstraint("expires_at > created_at", name="ck_execution_order_expiry"),
        sa.CheckConstraint("recorded_at >= created_at", name="ck_execution_order_recorded"),
        schema="execution",
    )

    op.create_index(
        "ix_execution_orders_state_time", "orders", ["state", "recorded_at"], schema="execution"
    )
    op.create_index(
        "ix_execution_orders_account_instrument",
        "orders",
        ["account_id", "instrument_id", "recorded_at"],
        schema="execution",
    )

    op.create_table(
        "submission_attempts",
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("attempt_ordinal", sa.Integer(), nullable=False),
        sa.Column("request_hash", _HASH, nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("venue_order_id", sa.Text(), nullable=True),
        sa.Column("lease_owner", sa.Text(), nullable=True),
        sa.Column("fencing_token", sa.BigInteger(), nullable=True),
        sa.Column("sent_at", _UTC, nullable=True),
        sa.Column("received_at", _UTC, nullable=True),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.Column("evidence_json", JSONB, nullable=False),
        sa.PrimaryKeyConstraint("attempt_id", name="pk_execution_submission_attempts"),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["execution.orders.order_id"],
            name="fk_submission_attempt_order",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("order_id", "attempt_ordinal", name="uq_submission_attempt_ordinal"),
        sa.CheckConstraint("attempt_ordinal > 0", name="ck_submission_attempt_ordinal"),
        sa.CheckConstraint("request_hash ~ '^[0-9a-f]{64}$'", name="ck_submission_attempt_hash"),
        sa.CheckConstraint(
            "outcome IN ('ACCEPTED','REJECTED','PARTIAL_FILL','FILLED','CANCELLED','TIMEOUT',"
            "'UNKNOWN')",
            name="ck_submission_attempt_outcome",
        ),
        sa.CheckConstraint(
            "fencing_token IS NULL OR fencing_token > 0", name="ck_submission_fencing"
        ),
        sa.CheckConstraint(
            "received_at IS NULL OR sent_at IS NULL OR received_at >= sent_at",
            name="ck_submission_attempt_times",
        ),
        schema="execution",
    )

    op.create_table(
        "order_events",
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("sequence", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.SmallInteger(), nullable=False),
        sa.Column("payload_json", JSONB, nullable=False),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=False),
        sa.Column("causation_id", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("event_id", name="pk_execution_order_events"),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["execution.orders.order_id"],
            name="fk_order_event_order",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("order_id", "sequence", name="uq_execution_order_event_sequence"),
        sa.CheckConstraint("sequence > 0", name="ck_execution_order_event_sequence"),
        sa.CheckConstraint("event_type <> ''", name="ck_execution_order_event_type"),
        sa.CheckConstraint("schema_version > 0", name="ck_execution_order_event_version"),
        schema="execution",
    )

    op.create_table(
        "fills",
        sa.Column("fill_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("venue_id", sa.Text(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("venue_fill_id", sa.Text(), nullable=True),
        sa.Column("source_fingerprint", _HASH, nullable=False),
        sa.Column("price", _DECIMAL, nullable=False),
        sa.Column("quantity", _DECIMAL, nullable=False),
        sa.Column("fee_amount", _DECIMAL, nullable=False),
        sa.Column("fee_asset", sa.Text(), nullable=True),
        sa.Column("liquidity_flag", sa.Text(), nullable=False),
        sa.Column("sequence", sa.BigInteger(), nullable=False),
        sa.Column("occurred_at", _UTC, nullable=False),
        sa.Column("received_at", _UTC, nullable=False),
        sa.Column("processed_at", _UTC, nullable=False),
        sa.Column("recorded_at", _UTC, nullable=False),
        sa.Column("quality_flags", JSONB, nullable=False),
        sa.PrimaryKeyConstraint("fill_id", name="pk_execution_fills"),
        sa.ForeignKeyConstraint(
            ["order_id"], ["execution.orders.order_id"], name="fk_fill_order", ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("order_id", "sequence", name="uq_execution_fill_sequence"),
        sa.CheckConstraint("venue_id <> ''", name="ck_execution_fill_venue"),
        sa.CheckConstraint("source_fingerprint ~ '^[0-9a-f]{64}$'", name="ck_fill_fingerprint"),
        sa.CheckConstraint("price > 0", name="ck_fill_price"),
        sa.CheckConstraint("quantity > 0", name="ck_fill_quantity"),
        sa.CheckConstraint("fee_amount >= 0", name="ck_fill_fee"),
        sa.CheckConstraint(
            "fee_amount = 0 OR (fee_asset IS NOT NULL AND fee_asset <> '')",
            name="ck_fill_fee_asset",
        ),
        sa.CheckConstraint(
            "liquidity_flag IN ('MAKER','TAKER','UNKNOWN')", name="ck_fill_liquidity"
        ),
        sa.CheckConstraint("sequence > 0", name="ck_fill_sequence"),
        sa.CheckConstraint("received_at >= occurred_at", name="ck_fill_received"),
        sa.CheckConstraint("processed_at >= received_at", name="ck_fill_processed"),
        sa.CheckConstraint("recorded_at >= processed_at", name="ck_fill_recorded"),
        schema="execution",
    )
    op.create_index(
        "uq_execution_fill_venue_identity",
        "fills",
        ["venue_id", "account_id", "venue_fill_id"],
        schema="execution",
        unique=True,
        postgresql_where=sa.text("venue_fill_id IS NOT NULL"),
    )
    op.create_index(
        "uq_execution_fill_source_fingerprint",
        "fills",
        ["venue_id", "account_id", "source_fingerprint"],
        schema="execution",
        unique=True,
    )

    op.create_table(
        "reconciliation_cases",
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("attempt_id", sa.UUID(), nullable=True),
        sa.Column("classification", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("evidence_json", JSONB, nullable=False),
        sa.Column("resolution_command_id", sa.UUID(), nullable=True),
        sa.Column("opened_at", _UTC, nullable=False),
        sa.Column("resolved_at", _UTC, nullable=True),
        sa.PrimaryKeyConstraint("case_id", name="pk_execution_reconciliation_cases"),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["execution.orders.order_id"],
            name="fk_reconciliation_order",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["execution.submission_attempts.attempt_id"],
            name="fk_reconciliation_attempt",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "classification IN ('UNKNOWN','DUPLICATE','OUT_OF_ORDER','MISMATCH')",
            name="ck_reconciliation_classification",
        ),
        sa.CheckConstraint(
            "status IN ('OPEN','IN_PROGRESS','RESOLVED','BLOCKED')",
            name="ck_reconciliation_status",
        ),
        sa.CheckConstraint(
            "resolved_at IS NULL OR resolved_at >= opened_at", name="ck_reconciliation_resolved"
        ),
        schema="execution",
    )
    op.create_index(
        "ix_reconciliation_status_time",
        "reconciliation_cases",
        ["status", "opened_at"],
        schema="execution",
    )


def downgrade() -> None:
    """Drop Task 1.3 tables for local rollback/forward-fix only."""
    op.drop_index(
        "ix_reconciliation_status_time", table_name="reconciliation_cases", schema="execution"
    )
    op.drop_table("reconciliation_cases", schema="execution")
    op.drop_index("uq_execution_fill_source_fingerprint", table_name="fills", schema="execution")
    op.drop_index("uq_execution_fill_venue_identity", table_name="fills", schema="execution")
    op.drop_table("fills", schema="execution")
    op.drop_table("order_events", schema="execution")
    op.drop_table("submission_attempts", schema="execution")
    op.drop_index("ix_execution_orders_account_instrument", table_name="orders", schema="execution")
    op.drop_index("ix_execution_orders_state_time", table_name="orders", schema="execution")
    op.drop_table("orders", schema="execution")
    op.drop_table("limit_state", schema="risk")
    op.drop_table("decisions", schema="risk")
    op.drop_table("reservations", schema="risk")
    op.drop_table("policies", schema="risk")
    op.execute("DROP SCHEMA IF EXISTS execution")
    op.execute("DROP SCHEMA IF EXISTS risk")
