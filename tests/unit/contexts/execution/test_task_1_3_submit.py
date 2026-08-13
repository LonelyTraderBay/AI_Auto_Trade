from datetime import UTC, datetime
from decimal import Decimal

import pytest

from ai_auto_trade.adapters.venues.fake.fake_venue import FakeVenue, default_scenarios
from ai_auto_trade.contexts.execution.application.durable_submit import (
    DurableSubmitBoundary,
    SubmissionBlocked,
)
from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    SubmissionOutcome,
)
from ai_auto_trade.contexts.risk.domain.risk_gate import (
    RiskDecision,
    RiskVerdict,
)


def _request(scenario_id: str = "immediate_accept") -> DurableSubmitRequest:
    """Build a deterministic local submit request."""
    return DurableSubmitRequest(
        order_id="018f8c7c-0001-7001-8001-000000000001",
        client_order_id="018f8c7c-0002-7002-8002-000000000002",
        attempt_id="018f8c7c-0003-7003-8003-000000000003",
        scenario_id=scenario_id,
        scenario_revision=1,
        side="BUY",
        order_type="LIMIT",
        quantity=Decimal("0.5"),
        limit_price=Decimal("10"),
        time_in_force="GTC",
        submitted_at=datetime(2026, 8, 13, 14, 10, tzinfo=UTC),
    )


def _approved() -> RiskDecision:
    """Build a risk approval suitable for the boundary unit test."""
    return RiskDecision(
        verdict=RiskVerdict.APPROVE,
        reason_code="RISK_APPROVED",
        approved_quantity=Decimal("0.5"),
        policy_version="1.0.0",
        policy_hash="a" * 64,
        input_hash="b" * 64,
        decided_at=datetime(2026, 8, 13, 14, 10, tzinfo=UTC),
        expires_at=datetime(2026, 8, 13, 14, 10, 30, tzinfo=UTC),
        reservation_id="018f8c7c-0004-7004-8004-000000000004",
    )


def test_duplicate_submit_returns_same_response_without_second_side_effect() -> None:
    """Replay of one client identity is idempotent."""
    venue = FakeVenue(default_scenarios())
    boundary = DurableSubmitBoundary(venue)
    request = _request()

    first = boundary.submit(request, _approved())
    second = boundary.submit(request, _approved())

    assert first.outcome is SubmissionOutcome.ACCEPTED
    assert second == first
    assert venue.submission_count(request.client_order_id) == 1


def test_unknown_outcome_blocks_blind_retry() -> None:
    """Timeout/unknown is a reconciliation boundary, never an automatic retry."""
    venue = FakeVenue(default_scenarios())
    boundary = DurableSubmitBoundary(venue)
    request = _request("unknown")

    result = boundary.submit(request, _approved())

    assert result.outcome is SubmissionOutcome.UNKNOWN
    assert result.state == "UNKNOWN"
    assert result.retry_forbidden is True
    with pytest.raises(SubmissionBlocked, match="reconciliation"):
        boundary.submit(request, _approved(), previous_outcome=result.outcome)


def test_partial_fill_progression_is_not_a_resubmit() -> None:
    """Scripted fill progression advances evidence without duplicating submit."""
    venue = FakeVenue(default_scenarios())
    boundary = DurableSubmitBoundary(venue)
    request = _request("partial_then_fill")

    first = boundary.submit(request, _approved())
    response = venue.advance(request)

    assert first.outcome is SubmissionOutcome.PARTIAL_FILL
    assert response.outcome is SubmissionOutcome.FILLED
    assert venue.submission_count(request.client_order_id) == 1
