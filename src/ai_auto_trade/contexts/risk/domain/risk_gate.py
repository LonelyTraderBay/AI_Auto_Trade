"""Deterministic local-simulator risk gate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from ai_auto_trade.shared_kernel.decimal_value import serialize_decimal


class RiskVerdict(StrEnum):
    """Canonical pre-trade risk verdicts."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUIRE_MANUAL_APPROVAL = "REQUIRE_MANUAL_APPROVAL"


@dataclass(frozen=True, slots=True)
class LocalSimulatorRiskPolicy:
    """Pinned risk limits approved for the synthetic local simulator."""

    profile_id: str
    profile_version: str
    policy_hash: str
    max_order_quantity: Decimal
    max_order_notional: Decimal
    market_data_freshness_seconds: int
    reservation_expiry_seconds: int


@dataclass(frozen=True, slots=True)
class RiskOrderInput:
    """Immutable inputs evaluated by the deterministic risk gate."""

    order_intent_id: str
    quantity: Decimal
    limit_price: Decimal
    market_timestamp: datetime
    now: datetime
    reservation_id: str
    kill_switch_active: bool = False


@dataclass(frozen=True, slots=True)
class RiskDecision:
    """Risk result and immutable evidence needed by execution."""

    verdict: RiskVerdict
    reason_code: str
    approved_quantity: Decimal
    policy_version: str
    policy_hash: str
    input_hash: str
    decided_at: datetime
    expires_at: datetime
    reservation_id: str | None
    decision_id: str | None = None
    policy_id: str | None = None
    portfolio_snapshot_hash: str | None = None
    market_snapshot_hash: str | None = None


def evaluate_local_simulator_order(
    order: RiskOrderInput,
    policy: LocalSimulatorRiskPolicy,
) -> RiskDecision:
    """Evaluate one order using only pinned deterministic inputs.

    Args:
        order: Immutable order and snapshot inputs.
        policy: Approved local-simulator policy.

    Returns:
        An immutable risk decision with a reproducible input hash.

    Raises:
        ValueError: If a timestamp or decimal input violates the domain boundary.
    """
    _validate_order(order)
    input_hash = _hash_order_input(order, policy)
    if order.kill_switch_active:
        return _decision(order, policy, input_hash, RiskVerdict.REJECT, "KILL_SWITCH_ACTIVE")
    if _market_data_is_stale(order, policy):
        return _decision(order, policy, input_hash, RiskVerdict.REJECT, "MARKET_DATA_STALE")
    if order.quantity > policy.max_order_quantity:
        return _decision(order, policy, input_hash, RiskVerdict.REJECT, "ORDER_QUANTITY_LIMIT")
    if order.quantity * order.limit_price > policy.max_order_notional:
        return _decision(order, policy, input_hash, RiskVerdict.REJECT, "ORDER_NOTIONAL_LIMIT")
    if not order.reservation_id:
        return _decision(order, policy, input_hash, RiskVerdict.REJECT, "RESERVATION_MISSING")
    return _decision(order, policy, input_hash, RiskVerdict.APPROVE, "RISK_APPROVED")


def _validate_order(order: RiskOrderInput) -> None:
    """Validate timestamps, identity and Decimal-only financial inputs."""
    if not order.order_intent_id or not order.reservation_id:
        raise ValueError("order and reservation identities are required")
    if order.now.tzinfo != UTC or order.market_timestamp.tzinfo != UTC:
        raise ValueError("risk timestamps must be timezone-aware UTC")
    if not order.quantity.is_finite() or not order.limit_price.is_finite():
        raise ValueError("risk financial values must be finite")
    if order.quantity <= 0 or order.limit_price <= 0:
        raise ValueError("quantity and limit price must be positive")


def _market_data_is_stale(order: RiskOrderInput, policy: LocalSimulatorRiskPolicy) -> bool:
    """Return whether market data is older than the approved freshness window."""
    age = (order.now - order.market_timestamp).total_seconds()
    return age < 0 or age > policy.market_data_freshness_seconds


def _hash_order_input(order: RiskOrderInput, policy: LocalSimulatorRiskPolicy) -> str:
    """Hash canonical risk inputs without float conversion."""
    payload = {
        "order_intent_id": order.order_intent_id,
        "quantity": serialize_decimal(order.quantity),
        "limit_price": serialize_decimal(order.limit_price),
        "market_timestamp": order.market_timestamp.isoformat().replace("+00:00", "Z"),
        "now": order.now.isoformat().replace("+00:00", "Z"),
        "reservation_id": order.reservation_id,
        "kill_switch_active": order.kill_switch_active,
        "profile_id": policy.profile_id,
        "profile_version": policy.profile_version,
        "policy_hash": policy.policy_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _decision(
    order: RiskOrderInput,
    policy: LocalSimulatorRiskPolicy,
    input_hash: str,
    verdict: RiskVerdict,
    reason_code: str,
) -> RiskDecision:
    """Build an immutable risk result with the policy expiry window."""
    expires_at = order.now + timedelta(seconds=policy.reservation_expiry_seconds)
    reservation_id = order.reservation_id if verdict is RiskVerdict.APPROVE else None
    return RiskDecision(
        verdict=verdict,
        reason_code=reason_code,
        approved_quantity=order.quantity if verdict is RiskVerdict.APPROVE else Decimal("0"),
        policy_version=policy.profile_version,
        policy_hash=policy.policy_hash,
        input_hash=input_hash,
        decided_at=order.now,
        expires_at=expires_at,
        reservation_id=reservation_id,
    )
