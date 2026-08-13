"""PostgreSQL integration checks for Task 1.3 persistence and safety constraints."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from ai_auto_trade.shared_kernel.identity import generate_uuid7

REQUIRED_TABLES = {
    "risk.policies",
    "risk.reservations",
    "risk.decisions",
    "risk.limit_state",
    "execution.orders",
    "execution.submission_attempts",
    "execution.order_events",
    "execution.fills",
    "execution.reconciliation_cases",
}
NOW = datetime(2026, 8, 13, 14, 20, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class OrderIds:
    """Synthetic UUIDv7 identities used by one integration case."""

    order_id: str
    account_id: str
    instrument_id: str
    correlation_id: str
    client_order_id: str


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Upgrade a local PostgreSQL database and yield a synchronous engine."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:
        pytest.skip("DATABASE_URL not set — skipping Task 1.3 PostgreSQL integration")
    sync_url = _sync_url(database_url)
    root = Path(__file__).resolve().parents[2]
    config = Config()
    config.set_main_option("script_location", str(root / "migrations"))
    config.set_main_option("sqlalchemy.url", sync_url)
    command.upgrade(config, "head")
    engine = sa.create_engine(sync_url)
    try:
        yield engine
    finally:
        engine.dispose()


def test_task_1_3_tables_exist(postgres_engine: Engine) -> None:
    """All approved risk and execution tables exist after migration upgrade."""
    with postgres_engine.connect() as connection:
        for qualified in REQUIRED_TABLES:
            schema, table = qualified.split(".")
            result = connection.execute(
                sa.text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = :schema AND table_name = :table"
                ),
                {"schema": schema, "table": table},
            )
            assert result.fetchone() is not None, f"Table {qualified} not found"


def test_client_order_and_event_dedupe_constraints(postgres_engine: Engine) -> None:
    """Client identity and lifecycle sequence cannot create duplicate effects."""
    ids = _ids()
    with postgres_engine.begin() as connection:
        _insert_order(connection, ids)
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        _insert_order(connection, ids, order_id=str(generate_uuid7(1_754_000_000_001)))
    with postgres_engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO execution.order_events "
                "(event_id, order_id, sequence, event_type, schema_version, payload_json, "
                "recorded_at, correlation_id) VALUES "
                "(:event_id, :order_id, 1, 'execution.order_created.v1', 1, '{}'::jsonb, "
                ":recorded_at, :correlation_id)"
            ),
            {
                "event_id": str(generate_uuid7(1_754_000_000_002)),
                "order_id": ids.order_id,
                "recorded_at": NOW,
                "correlation_id": ids.correlation_id,
            },
        )
    with pytest.raises(IntegrityError), postgres_engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO execution.order_events "
                "(event_id, order_id, sequence, event_type, schema_version, payload_json, "
                "recorded_at, correlation_id) VALUES "
                "(:event_id, :order_id, 1, 'execution.order_created.v1', 1, '{}'::jsonb, "
                ":recorded_at, :correlation_id)"
            ),
            {
                "event_id": str(generate_uuid7(1_754_000_000_003)),
                "order_id": ids.order_id,
                "recorded_at": NOW,
                "correlation_id": ids.correlation_id,
            },
        )


def test_unknown_attempt_is_persisted_as_reconciliation_case(postgres_engine: Engine) -> None:
    """UNKNOWN is durable and linked to a reconciliation case without retry."""
    ids = _ids()
    attempt_id = str(generate_uuid7(1_754_000_000_004))
    case_id = str(generate_uuid7(1_754_000_000_005))
    with postgres_engine.begin() as connection:
        _insert_order(connection, ids)
        connection.execute(
            sa.text(
                "INSERT INTO execution.submission_attempts "
                "(attempt_id, order_id, attempt_ordinal, request_hash, outcome, evidence_json, "
                "recorded_at) VALUES (:attempt_id, :order_id, 1, :request_hash, 'UNKNOWN', "
                "'{}'::jsonb, :recorded_at)"
            ),
            {
                "attempt_id": attempt_id,
                "order_id": ids.order_id,
                "request_hash": "a" * 64,
                "recorded_at": NOW,
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO execution.reconciliation_cases "
                "(case_id, order_id, attempt_id, classification, status, evidence_json, opened_at) "
                "VALUES (:case_id, :order_id, :attempt_id, 'UNKNOWN', 'OPEN', '{}'::jsonb, "
                ":opened_at)"
            ),
            {
                "case_id": case_id,
                "order_id": ids.order_id,
                "attempt_id": attempt_id,
                "opened_at": NOW,
            },
        )
        result = connection.execute(
            sa.text(
                "SELECT a.outcome, c.status FROM execution.submission_attempts a "
                "JOIN execution.reconciliation_cases c ON c.attempt_id = a.attempt_id "
                "WHERE a.attempt_id = :attempt_id"
            ),
            {"attempt_id": attempt_id},
        ).one()
    assert result == ("UNKNOWN", "OPEN")


def _sync_url(database_url: str) -> str:
    """Convert supported async/plain PostgreSQL URLs to psycopg2 URLs."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return database_url


def _ids() -> OrderIds:
    """Create unique UUIDv7 identities for an isolated integration run."""
    base = 1_754_000_100_000
    return OrderIds(
        order_id=str(generate_uuid7(base)),
        account_id=str(generate_uuid7(base + 1)),
        instrument_id=str(generate_uuid7(base + 2)),
        correlation_id=str(generate_uuid7(base + 3)),
        client_order_id=str(generate_uuid7(base + 4)),
    )


def _insert_order(
    connection: sa.Connection,
    ids: OrderIds,
    *,
    order_id: str | None = None,
) -> None:
    """Insert a minimal valid canonical order row."""
    connection.execute(
        sa.text(
            "INSERT INTO execution.orders "
            "(order_id, order_intent_id, client_order_id, venue_id, account_id, instrument_id, "
            "state, aggregate_version, request_hash, quantity, limit_price, created_at, "
            "expires_at, recorded_at, correlation_id) VALUES "
            "(:order_id, :order_intent_id, :client_order_id, 'FAKE-LOCAL-001', :account_id, "
            ":instrument_id, 'SUBMISSION_QUEUED', 0, :request_hash, :quantity, :limit_price, "
            ":created_at, :expires_at, :recorded_at, :correlation_id)"
        ),
        {
            "order_id": order_id or ids.order_id,
            "order_intent_id": str(generate_uuid7(1_754_000_200_000)),
            "client_order_id": ids.client_order_id,
            "account_id": ids.account_id,
            "instrument_id": ids.instrument_id,
            "request_hash": "b" * 64,
            "quantity": Decimal("0.5"),
            "limit_price": Decimal("10"),
            "created_at": NOW,
            "expires_at": NOW + timedelta(minutes=5),
            "recorded_at": NOW,
            "correlation_id": ids.correlation_id,
        },
    )
