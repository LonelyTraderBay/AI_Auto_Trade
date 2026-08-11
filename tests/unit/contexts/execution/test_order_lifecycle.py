"""Unit tests for the pure OMS order lifecycle transition contract."""

import pytest

from ai_auto_trade.contexts.execution.domain.order_lifecycle import (
    InvalidOrderTransition,
    OrderLifecycleEvent,
    OrderState,
    transition_order_state,
)


@pytest.mark.parametrize(
    ("current_state", "event", "expected_state"),
    [
        (None, OrderLifecycleEvent.ORDER_CREATED, OrderState.CREATED),
        (OrderState.CREATED, OrderLifecycleEvent.ORDER_RISK_REJECTED, OrderState.RISK_REJECTED),
        (
            OrderState.CREATED,
            OrderLifecycleEvent.ORDER_MANUAL_APPROVAL_REQUESTED,
            OrderState.PENDING_MANUAL_APPROVAL,
        ),
        (OrderState.CREATED, OrderLifecycleEvent.ORDER_RISK_APPROVED, OrderState.RISK_APPROVED),
        (
            OrderState.PENDING_MANUAL_APPROVAL,
            OrderLifecycleEvent.ORDER_RISK_APPROVED,
            OrderState.RISK_APPROVED,
        ),
        (
            OrderState.PENDING_MANUAL_APPROVAL,
            OrderLifecycleEvent.ORDER_EXPIRED,
            OrderState.EXPIRED,
        ),
        (
            OrderState.PENDING_MANUAL_APPROVAL,
            OrderLifecycleEvent.ORDER_RISK_REJECTED,
            OrderState.RISK_REJECTED,
        ),
        (
            OrderState.RISK_APPROVED,
            OrderLifecycleEvent.ORDER_SUBMISSION_QUEUED,
            OrderState.SUBMISSION_QUEUED,
        ),
        (
            OrderState.SUBMISSION_QUEUED,
            OrderLifecycleEvent.ORDER_SUBMITTING,
            OrderState.SUBMITTING,
        ),
        (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_ACKNOWLEDGED, OrderState.OPEN),
        (
            OrderState.SUBMITTING,
            OrderLifecycleEvent.ORDER_PARTIALLY_FILLED,
            OrderState.PARTIALLY_FILLED,
        ),
        (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_FILLED, OrderState.FILLED),
        (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_REJECTED, OrderState.REJECTED),
        (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_UNKNOWN, OrderState.UNKNOWN),
        (
            OrderState.OPEN,
            OrderLifecycleEvent.ORDER_PARTIALLY_FILLED,
            OrderState.PARTIALLY_FILLED,
        ),
        (OrderState.OPEN, OrderLifecycleEvent.ORDER_FILLED, OrderState.FILLED),
        (
            OrderState.OPEN,
            OrderLifecycleEvent.ORDER_CANCEL_REQUESTED,
            OrderState.CANCEL_REQUESTED,
        ),
        (OrderState.OPEN, OrderLifecycleEvent.ORDER_EXPIRED, OrderState.EXPIRED),
        (OrderState.PARTIALLY_FILLED, OrderLifecycleEvent.ORDER_FILLED, OrderState.FILLED),
        (
            OrderState.PARTIALLY_FILLED,
            OrderLifecycleEvent.ORDER_CANCEL_REQUESTED,
            OrderState.CANCEL_REQUESTED,
        ),
        (
            OrderState.PARTIALLY_FILLED,
            OrderLifecycleEvent.ORDER_EXPIRED,
            OrderState.EXPIRED,
        ),
        (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_CANCELLED, OrderState.CANCELLED),
        (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_EXPIRED, OrderState.EXPIRED),
        (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_UNKNOWN, OrderState.UNKNOWN),
        (OrderState.UNKNOWN, OrderLifecycleEvent.ORDER_RECONCILING, OrderState.RECONCILING),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_ACKNOWLEDGED, OrderState.OPEN),
        (
            OrderState.RECONCILING,
            OrderLifecycleEvent.ORDER_PARTIALLY_FILLED,
            OrderState.PARTIALLY_FILLED,
        ),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_FILLED, OrderState.FILLED),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_CANCELLED, OrderState.CANCELLED),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_REJECTED, OrderState.REJECTED),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_EXPIRED, OrderState.EXPIRED),
        (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_LOST, OrderState.LOST),
    ],
)
def test_allowed_transition_returns_canonical_target(
    current_state: OrderState | None,
    event: OrderLifecycleEvent,
    expected_state: OrderState,
) -> None:
    """Every approved transition produces its exact canonical target."""
    assert transition_order_state(current_state, event) is expected_state


@pytest.mark.parametrize(
    ("current_state", "event"),
    [
        (OrderState.CREATED, OrderLifecycleEvent.ORDER_CREATED),
        (OrderState.OPEN, OrderLifecycleEvent.ORDER_ACKNOWLEDGED),
        (OrderState.PARTIALLY_FILLED, OrderLifecycleEvent.ORDER_PARTIALLY_FILLED),
        (OrderState.FILLED, OrderLifecycleEvent.ORDER_CANCEL_REQUESTED),
        (OrderState.CANCELLED, OrderLifecycleEvent.ORDER_FILLED),
        (OrderState.EXPIRED, OrderLifecycleEvent.ORDER_RECONCILING),
        (OrderState.LOST, OrderLifecycleEvent.ORDER_ACKNOWLEDGED),
    ],
)
def test_invalid_duplicate_or_out_of_order_transition_is_rejected(
    current_state: OrderState,
    event: OrderLifecycleEvent,
) -> None:
    """Duplicate, terminal and out-of-order events fail closed."""
    with pytest.raises(InvalidOrderTransition):
        transition_order_state(current_state, event)


@pytest.mark.parametrize("current_state", [OrderState.CREATED, OrderState.RISK_APPROVED])
def test_proposed_expiry_transitions_are_rejected(current_state: OrderState) -> None:
    """Unratified §3a expiry transitions remain invalid."""
    with pytest.raises(InvalidOrderTransition):
        transition_order_state(current_state, OrderLifecycleEvent.ORDER_EXPIRED)


@pytest.mark.parametrize(
    ("current_state", "target_state"),
    [
        (OrderState.CANCELLED, OrderState.CANCELLED),
        (OrderState.CANCELLED, OrderState.FILLED),
        (OrderState.EXPIRED, OrderState.EXPIRED),
        (OrderState.EXPIRED, OrderState.FILLED),
        (OrderState.LOST, OrderState.FILLED),
        (OrderState.LOST, OrderState.CANCELLED),
        (OrderState.LOST, OrderState.EXPIRED),
        (OrderState.LOST, OrderState.REJECTED),
    ],
)
def test_terminal_correction_requires_proven_terminal_target(
    current_state: OrderState,
    target_state: OrderState,
) -> None:
    """Only approved terminal correction targets are accepted."""
    assert (
        transition_order_state(
            current_state,
            OrderLifecycleEvent.ORDER_TERMINAL_CORRECTED,
            terminal_target=target_state,
        )
        is target_state
    )


def test_terminal_correction_without_target_is_rejected() -> None:
    """A correction cannot infer a terminal target."""
    with pytest.raises(InvalidOrderTransition):
        transition_order_state(OrderState.LOST, OrderLifecycleEvent.ORDER_TERMINAL_CORRECTED)


def test_non_correction_event_rejects_terminal_target_argument() -> None:
    """A target cannot be smuggled into a normal transition."""
    with pytest.raises(InvalidOrderTransition):
        transition_order_state(
            OrderState.CREATED,
            OrderLifecycleEvent.ORDER_RISK_APPROVED,
            terminal_target=OrderState.FILLED,
        )
