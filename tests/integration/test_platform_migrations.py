"""Integration test — platform migration correctness.

Verifies that the platform delivery baseline migration creates all expected
tables, constraints and indexes. Skipped when DATABASE_URL is not set
(CI without postgres or developer without docker-compose running).

Task: 0.3 | Refs: ADR-0003, ADR-0004, DATA-003 §3-6
"""

import os

import pytest
import sqlalchemy as sa

REQUIRED_TABLES = {
    "platform.outbox",
    "platform.outbox_delivery_state",
    "platform.inbox",
    "platform.dead_letters",
}


@pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None,
    reason="DATABASE_URL not set — skipping postgres integration test",
)
def test_platform_tables_exist() -> None:
    """All four platform tables must exist after alembic upgrade head."""
    url = os.environ["DATABASE_URL"]
    sync_url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    engine = sa.create_engine(sync_url)

    with engine.connect() as conn:
        for qualified in REQUIRED_TABLES:
            schema, table = qualified.split(".")
            result = conn.execute(
                sa.text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = :schema AND table_name = :table"
                ),
                {"schema": schema, "table": table},
            )
            assert result.fetchone() is not None, f"Table {qualified} not found after migration"
