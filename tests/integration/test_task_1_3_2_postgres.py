"""PostgreSQL fault and recovery checks for Task 1.3.2."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

from ai_auto_trade.adapters.persistence.durable_submission import (
    PostgresTradingSubmissionUnitOfWork,
)
from ai_auto_trade.adapters.venues.fake.fake_venue import FakeVenue, default_scenarios
from ai_auto_trade.contexts.execution.application.durable_submit import (
    DurableSubmitBoundary,
    SubmissionBlocked,
)
from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    LeaseLostError,
    SubmissionConflictError,
    SubmissionIdentity,
    SubmissionOutcome,
    SubmissionSafetyContext,
    SubmissionSafetyError,
)
from ai_auto_trade.contexts.risk.domain.risk_gate import RiskDecision, RiskVerdict
from ai_auto_trade.shared_kernel.identity import generate_uuid7

NOW = datetime(2026, 8, 13, 14, 20, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class SubmissionFixture:
    """All identities and evidence for one isolated local submission."""

    request: DurableSubmitRequest
    decision: RiskDecision
    safety: SubmissionSafetyContext
    scope_key: str


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Upgrade the configured local PostgreSQL database and yield a sync engine."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:
        pytest.skip("DATABASE_URL not set — skipping Task 1.3.2 PostgreSQL integration")
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


def test_atomic_submit_replay_and_delivery_dedupe(postgres_engine: Engine) -> None:
    """One submit persists all facts and replay/publish/consume have no second effect."""
    fixture = _fixture("immediate_accept")
    _seed_scope(postgres_engine, fixture)
    venue = FakeVenue(default_scenarios())
    unit_of_work = PostgresTradingSubmissionUnitOfWork(postgres_engine)
    boundary = DurableSubmitBoundary(venue, unit_of_work)

    first = boundary.submit(fixture.request, fixture.decision, safety=fixture.safety)
    second = boundary.submit(fixture.request, fixture.decision, safety=fixture.safety)

    assert first.outcome is SubmissionOutcome.ACCEPTED
    assert second == first
    assert venue.submission_count(fixture.request.client_order_id) == 1
    conflicting_request = replace(fixture.request, limit_price=Decimal("11"))
    with pytest.raises(SubmissionConflictError, match="reservation"):
        boundary.submit(conflicting_request, fixture.decision, safety=fixture.safety)
    assert venue.submission_count(fixture.request.client_order_id) == 1
    assert fixture.request.identity is not None
    with postgres_engine.connect() as connection:
        counts = connection.execute(
            sa.text(
                "SELECT "
                "(SELECT count(*) FROM risk.decisions WHERE order_intent_id = :intent_id), "
                "(SELECT count(*) FROM risk.reservations WHERE order_intent_id = :intent_id), "
                "(SELECT count(*) FROM execution.orders WHERE order_id = :order_id), "
                "(SELECT count(*) FROM execution.submission_attempts WHERE order_id = :order_id), "
                "(SELECT count(*) FROM execution.order_events WHERE order_id = :order_id), "
                "(SELECT count(*) FROM platform.outbox WHERE source_aggregate_id = :order_id), "
                "(SELECT count(*) FROM execution.reconciliation_cases WHERE order_id = :order_id)"
            ),
            {
                "intent_id": fixture.request.identity.order_intent_id,
                "order_id": fixture.request.order_id,
            },
        ).one()
        assert tuple(counts) == (1, 1, 1, 1, 3, 3, 1)
        sequences = (
            connection.execute(
                sa.text(
                    "SELECT sequence FROM execution.order_events WHERE order_id = :order_id "
                    "ORDER BY sequence"
                ),
                {"order_id": fixture.request.order_id},
            )
            .scalars()
            .all()
        )
        assert sequences == [1, 2, 3]
        outbox_id = connection.execute(
            sa.text(
                "SELECT outbox_id FROM platform.outbox "
                "WHERE source_aggregate_id = :order_id ORDER BY recorded_at LIMIT 1"
            ),
            {"order_id": fixture.request.order_id},
        ).scalar_one()

    outbox_id_text = str(outbox_id)
    assert (
        unit_of_work.claim_outbox(
            outbox_id_text,
            fixture.safety.lease_owner,
            fixture.safety.fencing_token,
            fixture.safety.now,
            fixture.safety.lease_expires_at,
        )
        is True
    )
    assert (
        unit_of_work.mark_outbox_published(
            outbox_id_text,
            fixture.safety.lease_owner,
            fixture.safety.fencing_token,
            fixture.safety.now,
        )
        is True
    )
    assert (
        unit_of_work.mark_outbox_published(
            outbox_id_text,
            fixture.safety.lease_owner,
            fixture.safety.fencing_token,
            fixture.safety.now,
        )
        is True
    )
    assert unit_of_work.consume_outbox(outbox_id_text, "task-1.3.2-test-consumer", NOW) is True
    assert unit_of_work.consume_outbox(outbox_id_text, "task-1.3.2-test-consumer", NOW) is False


def test_unknown_restart_and_lease_loss_never_resubmit(postgres_engine: Engine) -> None:
    """UNKNOWN is recovery-bound; restart and stale fencing never call the venue twice."""
    fixture = _fixture("unknown")
    _seed_scope(postgres_engine, fixture)
    venue = FakeVenue(default_scenarios())
    unit_of_work = PostgresTradingSubmissionUnitOfWork(postgres_engine)
    boundary = DurableSubmitBoundary(venue, unit_of_work)

    first = boundary.submit(fixture.request, fixture.decision, safety=fixture.safety)
    replay = boundary.submit(fixture.request, fixture.decision, safety=fixture.safety)
    assert first.outcome is SubmissionOutcome.UNKNOWN
    assert replay == first
    assert venue.submission_count(fixture.request.client_order_id) == 1
    with pytest.raises(SubmissionBlocked, match="reconciliation"):
        boundary.submit(
            fixture.request,
            fixture.decision,
            previous_outcome=SubmissionOutcome.UNKNOWN,
            safety=fixture.safety,
        )
    with postgres_engine.connect() as connection:
        status = connection.execute(
            sa.text(
                "SELECT status FROM execution.reconciliation_cases WHERE attempt_id = :attempt_id"
            ),
            {"attempt_id": fixture.request.attempt_id},
        ).scalar_one()
    assert status == "OPEN"

    stale = _fixture("immediate_accept")
    _seed_scope(postgres_engine, stale)
    stale_safety = SubmissionSafetyContext(
        now=NOW,
        lease_owner=stale.safety.lease_owner,
        lease_expires_at=NOW + timedelta(minutes=1),
        fencing_token=2,
    )
    with pytest.raises(LeaseLostError):
        DurableSubmitBoundary(FakeVenue(default_scenarios()), unit_of_work).submit(
            stale.request,
            stale.decision,
            safety=stale_safety,
        )


def test_crash_boundaries_and_duplicate_response_are_recoverable(postgres_engine: Engine) -> None:
    """Crash-before-call and crash-after-apply paths remain canonical and side-effect safe."""
    before_call = _fixture("immediate_accept")
    _seed_scope(postgres_engine, before_call)
    unit_of_work = PostgresTradingSubmissionUnitOfWork(postgres_engine)
    prepared = unit_of_work.prepare(before_call.request, before_call.decision, before_call.safety)
    restarted = DurableSubmitBoundary(FakeVenue(default_scenarios()), unit_of_work).submit(
        before_call.request,
        before_call.decision,
        safety=before_call.safety,
    )
    assert prepared.replay is None
    assert restarted.outcome is SubmissionOutcome.UNKNOWN

    after_apply = _fixture("partial_then_fill")
    _seed_scope(postgres_engine, after_apply)
    venue = FakeVenue(default_scenarios())
    prepared = unit_of_work.prepare(after_apply.request, after_apply.decision, after_apply.safety)
    assert unit_of_work.claim_for_submit(prepared, after_apply.safety) is True
    response = venue.submit(after_apply.request)
    applied = unit_of_work.record_outcome(prepared, response, after_apply.safety)
    duplicate = unit_of_work.record_outcome(prepared, response, after_apply.safety)
    assert applied == duplicate
    assert venue.submission_count(after_apply.request.client_order_id) == 1
    with postgres_engine.connect() as connection:
        fill_count = connection.execute(
            sa.text("SELECT count(*) FROM execution.fills WHERE order_id = :order_id"),
            {"order_id": after_apply.request.order_id},
        ).scalar_one()
    assert fill_count == 1


def test_expired_quantity_and_kill_switch_fail_closed() -> None:
    """The application boundary blocks stale approval, quantity mismatch and freeze state."""
    fixture = _fixture("immediate_accept")
    venue = FakeVenue(default_scenarios())
    boundary = DurableSubmitBoundary(venue)
    expired_safety = SubmissionSafetyContext(
        now=NOW + timedelta(minutes=1),
        lease_owner=fixture.safety.lease_owner,
        lease_expires_at=NOW + timedelta(minutes=2),
        fencing_token=1,
    )
    with pytest.raises(SubmissionSafetyError, match="expired"):
        boundary.submit(fixture.request, fixture.decision, safety=expired_safety)
    mismatched = RiskDecision(
        verdict=RiskVerdict.APPROVE,
        reason_code=fixture.decision.reason_code,
        approved_quantity=Decimal("0.6"),
        policy_version=fixture.decision.policy_version,
        policy_hash=fixture.decision.policy_hash,
        input_hash=fixture.decision.input_hash,
        decided_at=fixture.decision.decided_at,
        expires_at=fixture.decision.expires_at,
        reservation_id=fixture.decision.reservation_id,
    )
    with pytest.raises(SubmissionSafetyError, match="quantity"):
        boundary.submit(fixture.request, mismatched, safety=fixture.safety)
    with pytest.raises(SubmissionSafetyError, match="kill switch"):
        SubmissionSafetyContext(
            now=NOW,
            lease_owner=fixture.safety.lease_owner,
            lease_expires_at=fixture.safety.lease_expires_at,
            fencing_token=1,
            kill_switch_active=True,
        )
    assert venue.submission_count(fixture.request.client_order_id) == 0


def _fixture(scenario_id: str) -> SubmissionFixture:
    """Build one UUIDv7-backed fixture with immutable local risk evidence."""
    identity = SubmissionIdentity(
        order_intent_id=str(generate_uuid7()),
        account_id=str(generate_uuid7()),
        instrument_id=str(generate_uuid7()),
        correlation_id=str(generate_uuid7()),
        trace_id=str(generate_uuid7()),
        venue_id=str(generate_uuid7()),
        scope_key=f"task-1.3.2-{generate_uuid7()}",
    )
    request = DurableSubmitRequest(
        order_id=str(generate_uuid7()),
        client_order_id=str(generate_uuid7()),
        attempt_id=str(generate_uuid7()),
        scenario_id=scenario_id,
        scenario_revision=1,
        side="BUY",
        order_type="LIMIT",
        quantity=Decimal("0.5"),
        limit_price=Decimal("10"),
        time_in_force="GTC",
        submitted_at=NOW,
        identity=identity,
    )
    decision = RiskDecision(
        verdict=RiskVerdict.APPROVE,
        reason_code="RISK_APPROVED",
        approved_quantity=Decimal("0.5"),
        policy_version="1.0.0",
        policy_hash="a" * 64,
        input_hash="b" * 64,
        decided_at=NOW,
        expires_at=NOW + timedelta(seconds=30),
        reservation_id=str(generate_uuid7()),
        decision_id=str(generate_uuid7()),
        policy_id=str(generate_uuid7()),
        portfolio_snapshot_hash="c" * 64,
        market_snapshot_hash="d" * 64,
    )
    safety = SubmissionSafetyContext(
        now=NOW,
        lease_owner=f"leader-{identity.scope_key}",
        lease_expires_at=NOW + timedelta(minutes=5),
        fencing_token=1,
    )
    return SubmissionFixture(request, decision, safety, identity.scope_key)


def _seed_scope(engine: Engine, fixture: SubmissionFixture) -> None:
    """Insert approved policy and fencing state for a local fixture."""
    assert fixture.request.identity is not None
    assert fixture.decision.policy_id is not None
    with engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO risk.policies "
                "(policy_id, scope_key, policy_version, policy_hash, parameters, effective_at, "
                "expires_at, status, approval_evidence_ref, recorded_at) VALUES "
                "(:policy_id, :scope_key, :policy_version, :policy_hash, '{}'::jsonb, "
                ":effective_at, "
                ":expires_at, 'ACTIVE', 'task-1.3.2-test', :recorded_at)"
            ),
            {
                "policy_id": fixture.decision.policy_id,
                "scope_key": fixture.scope_key,
                "policy_version": fixture.decision.policy_version,
                "policy_hash": fixture.decision.policy_hash,
                "effective_at": NOW - timedelta(minutes=1),
                "expires_at": NOW + timedelta(hours=1),
                "recorded_at": NOW,
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO risk.limit_state "
                "(scope_key, counters, aggregate_version, fencing_token, updated_at) VALUES "
                "(:scope_key, '{}'::jsonb, 0, 1, :updated_at)"
            ),
            {"scope_key": fixture.scope_key, "updated_at": NOW},
        )


def _sync_url(database_url: str) -> str:
    """Convert supported async/plain PostgreSQL URLs to psycopg2 URLs."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return database_url
