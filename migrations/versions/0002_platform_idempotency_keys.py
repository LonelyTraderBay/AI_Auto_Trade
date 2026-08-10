"""Add platform.idempotency_keys table.

Revision ID: 0002_platform_idempotency_keys
Revises: 0001_platform_delivery_baseline
Create Date: 2026-08-06

Task: 0.4
Refs: ADR-0012, DATA-003 §7 (platform.idempotency_keys — unlocks at Task 0.5/OpenAPI)
Note: Table created here as platform schema extension; used from Task 0.5 onward.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_platform_idempotency_keys"
down_revision: str | None = "0001_platform_delivery_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add platform.idempotency_keys for HTTP idempotency enforcement."""
    op.create_table(
        "idempotency_keys",
        sa.Column("idempotency_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.Text(), nullable=False),
        sa.Column("route_scope", sa.Text(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column(
            "payload_hash",
            sa.CHAR(64),
            sa.CheckConstraint(
                "payload_hash ~ '^[0-9a-f]{64}$'",
                name="ck_ik_payload_hash",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            sa.CheckConstraint(
                "status IN ('PROCESSING','COMPLETED','FAILED')",
                name="ck_ik_status",
            ),
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.Column("response_hash", sa.CHAR(64), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("idempotency_id", name="pk_idempotency_keys"),
        sa.UniqueConstraint(
            "actor_id",
            "route_scope",
            "idempotency_key",
            name="uq_ik_actor_route_key",
        ),
        sa.CheckConstraint("actor_id <> ''", name="ck_ik_actor_nonempty"),
        sa.CheckConstraint("route_scope <> ''", name="ck_ik_route_nonempty"),
        sa.CheckConstraint("idempotency_key <> ''", name="ck_ik_key_nonempty"),
        sa.CheckConstraint("expires_at > created_at", name="ck_ik_expiry_after_created"),
        schema="platform",
    )
    op.create_index(
        "ix_ik_expiry",
        "idempotency_keys",
        ["expires_at"],
        schema="platform",
        postgresql_where=sa.text("status = 'PROCESSING'"),
    )


def downgrade() -> None:
    """Drop platform.idempotency_keys (dev/rollback only)."""
    op.drop_index("ix_ik_expiry", table_name="idempotency_keys", schema="platform")
    op.drop_table("idempotency_keys", schema="platform")
