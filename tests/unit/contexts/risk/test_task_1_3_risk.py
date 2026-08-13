from datetime import UTC, datetime
from decimal import Decimal

from ai_auto_trade.contexts.risk.domain.risk_gate import (
    LocalSimulatorRiskPolicy,
    RiskOrderInput,
    RiskVerdict,
    evaluate_local_simulator_order,
)

POLICY = LocalSimulatorRiskPolicy(
    profile_id="LOCAL_SIMULATOR_TEST",
    profile_version="1.0.0",
    policy_hash="9b7cf6ecabbf7a6687ae008a52497290685a08b99f9f1fe281224f8f986d3c16",
    max_order_quantity=Decimal("1000"),
    max_order_notional=Decimal("1000"),
    market_data_freshness_seconds=5,
    reservation_expiry_seconds=30,
)
NOW = datetime(2026, 8, 13, 14, 10, tzinfo=UTC)


def _order(
    *,
    quantity: Decimal = Decimal("0.01"),
    limit_price: Decimal = Decimal("10"),
    market_timestamp: datetime = NOW,
    kill_switch_active: bool = False,
) -> RiskOrderInput:
    """Build a deterministic valid risk input with typed overrides."""
    return RiskOrderInput(
        order_intent_id="018f8c7c-0021-7021-8021-000000000021",
        quantity=quantity,
        limit_price=limit_price,
        market_timestamp=market_timestamp,
        now=NOW,
        reservation_id="018f8c7c-0032-7032-8032-000000000032",
        kill_switch_active=kill_switch_active,
    )


def test_local_policy_approves_with_stable_hash_and_reservation() -> None:
    """A valid synthetic order gets an auditable deterministic approval."""
    first = evaluate_local_simulator_order(_order(), POLICY)
    second = evaluate_local_simulator_order(_order(), POLICY)

    assert first.verdict is RiskVerdict.APPROVE
    assert first.reason_code == "RISK_APPROVED"
    assert first.reservation_id == "018f8c7c-0032-7032-8032-000000000032"
    assert first.input_hash == second.input_hash
    assert first.expires_at.isoformat() == "2026-08-13T14:10:30+00:00"


def test_stale_market_data_fails_closed() -> None:
    """Market data older than the approved window is rejected."""
    decision = evaluate_local_simulator_order(
        _order(market_timestamp=datetime(2026, 8, 13, 14, 9, 54, tzinfo=UTC)), POLICY
    )

    assert decision.verdict is RiskVerdict.REJECT
    assert decision.reason_code == "MARKET_DATA_STALE"
    assert decision.reservation_id is None


def test_kill_switch_and_notional_limits_fail_closed() -> None:
    """The safety freeze and approved notional cap reject exposure."""
    frozen = evaluate_local_simulator_order(_order(kill_switch_active=True), POLICY)
    oversized = evaluate_local_simulator_order(
        _order(quantity=Decimal("101"), limit_price=Decimal("10")), POLICY
    )

    assert frozen.reason_code == "KILL_SWITCH_ACTIVE"
    assert oversized.reason_code == "ORDER_NOTIONAL_LIMIT"
