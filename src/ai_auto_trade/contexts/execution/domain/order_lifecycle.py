"""Pure deterministic order lifecycle transition validation."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class OrderState(StrEnum):
    """Canonical execution order states from DOM-OMS-001."""

    CREATED = "CREATED"
    PENDING_MANUAL_APPROVAL = "PENDING_MANUAL_APPROVAL"
    RISK_APPROVED = "RISK_APPROVED"
    RISK_REJECTED = "RISK_REJECTED"
    SUBMISSION_QUEUED = "SUBMISSION_QUEUED"
    SUBMITTING = "SUBMITTING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"
    LOST = "LOST"


class OrderLifecycleEvent(StrEnum):
    """Canonical lifecycle events that may advance an order state."""

    ORDER_CREATED = "ORDER_CREATED"
    ORDER_RISK_REJECTED = "ORDER_RISK_REJECTED"
    ORDER_MANUAL_APPROVAL_REQUESTED = "ORDER_MANUAL_APPROVAL_REQUESTED"
    ORDER_RISK_APPROVED = "ORDER_RISK_APPROVED"
    ORDER_SUBMISSION_QUEUED = "ORDER_SUBMISSION_QUEUED"
    ORDER_SUBMITTING = "ORDER_SUBMITTING"
    ORDER_ACKNOWLEDGED = "ORDER_ACKNOWLEDGED"
    ORDER_REJECTED = "ORDER_REJECTED"
    ORDER_PARTIALLY_FILLED = "ORDER_PARTIALLY_FILLED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_CANCEL_REQUESTED = "ORDER_CANCEL_REQUESTED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_EXPIRED = "ORDER_EXPIRED"
    ORDER_UNKNOWN = "ORDER_UNKNOWN"
    ORDER_RECONCILING = "ORDER_RECONCILING"
    ORDER_LOST = "ORDER_LOST"
    ORDER_TERMINAL_CORRECTED = "ORDER_TERMINAL_CORRECTED"


class InvalidOrderTransition(ValueError):
    """Raised when a lifecycle event is not valid for the current state."""


_ALLOWED_TRANSITIONS: Final[
    dict[tuple[OrderState | None, OrderLifecycleEvent], frozenset[OrderState]]
] = {
    (None, OrderLifecycleEvent.ORDER_CREATED): frozenset({OrderState.CREATED}),
    (OrderState.CREATED, OrderLifecycleEvent.ORDER_RISK_REJECTED): frozenset(
        {OrderState.RISK_REJECTED}
    ),
    (OrderState.CREATED, OrderLifecycleEvent.ORDER_MANUAL_APPROVAL_REQUESTED): frozenset(
        {OrderState.PENDING_MANUAL_APPROVAL}
    ),
    (OrderState.CREATED, OrderLifecycleEvent.ORDER_RISK_APPROVED): frozenset(
        {OrderState.RISK_APPROVED}
    ),
    (OrderState.PENDING_MANUAL_APPROVAL, OrderLifecycleEvent.ORDER_RISK_APPROVED): frozenset(
        {OrderState.RISK_APPROVED}
    ),
    (OrderState.PENDING_MANUAL_APPROVAL, OrderLifecycleEvent.ORDER_EXPIRED): frozenset(
        {OrderState.EXPIRED}
    ),
    (OrderState.PENDING_MANUAL_APPROVAL, OrderLifecycleEvent.ORDER_RISK_REJECTED): frozenset(
        {OrderState.RISK_REJECTED}
    ),
    (OrderState.RISK_APPROVED, OrderLifecycleEvent.ORDER_SUBMISSION_QUEUED): frozenset(
        {OrderState.SUBMISSION_QUEUED}
    ),
    (OrderState.SUBMISSION_QUEUED, OrderLifecycleEvent.ORDER_SUBMITTING): frozenset(
        {OrderState.SUBMITTING}
    ),
    (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_ACKNOWLEDGED): frozenset({OrderState.OPEN}),
    (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_PARTIALLY_FILLED): frozenset(
        {OrderState.PARTIALLY_FILLED}
    ),
    (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_FILLED): frozenset({OrderState.FILLED}),
    (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_REJECTED): frozenset({OrderState.REJECTED}),
    (OrderState.SUBMITTING, OrderLifecycleEvent.ORDER_UNKNOWN): frozenset({OrderState.UNKNOWN}),
    (OrderState.OPEN, OrderLifecycleEvent.ORDER_PARTIALLY_FILLED): frozenset(
        {OrderState.PARTIALLY_FILLED}
    ),
    (OrderState.OPEN, OrderLifecycleEvent.ORDER_FILLED): frozenset({OrderState.FILLED}),
    (OrderState.OPEN, OrderLifecycleEvent.ORDER_CANCEL_REQUESTED): frozenset(
        {OrderState.CANCEL_REQUESTED}
    ),
    (OrderState.OPEN, OrderLifecycleEvent.ORDER_EXPIRED): frozenset({OrderState.EXPIRED}),
    (OrderState.PARTIALLY_FILLED, OrderLifecycleEvent.ORDER_FILLED): frozenset({OrderState.FILLED}),
    (OrderState.PARTIALLY_FILLED, OrderLifecycleEvent.ORDER_CANCEL_REQUESTED): frozenset(
        {OrderState.CANCEL_REQUESTED}
    ),
    (OrderState.PARTIALLY_FILLED, OrderLifecycleEvent.ORDER_EXPIRED): frozenset(
        {OrderState.EXPIRED}
    ),
    (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_CANCELLED): frozenset(
        {OrderState.CANCELLED}
    ),
    (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_EXPIRED): frozenset(
        {OrderState.EXPIRED}
    ),
    (OrderState.CANCEL_REQUESTED, OrderLifecycleEvent.ORDER_UNKNOWN): frozenset(
        {OrderState.UNKNOWN}
    ),
    (OrderState.UNKNOWN, OrderLifecycleEvent.ORDER_RECONCILING): frozenset(
        {OrderState.RECONCILING}
    ),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_ACKNOWLEDGED): frozenset({OrderState.OPEN}),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_PARTIALLY_FILLED): frozenset(
        {OrderState.PARTIALLY_FILLED}
    ),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_FILLED): frozenset({OrderState.FILLED}),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_CANCELLED): frozenset(
        {OrderState.CANCELLED}
    ),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_REJECTED): frozenset({OrderState.REJECTED}),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_EXPIRED): frozenset({OrderState.EXPIRED}),
    (OrderState.RECONCILING, OrderLifecycleEvent.ORDER_LOST): frozenset({OrderState.LOST}),
}

_TERMINAL_CORRECTION_TARGETS: Final[dict[OrderState, frozenset[OrderState]]] = {
    OrderState.CANCELLED: frozenset({OrderState.CANCELLED, OrderState.FILLED}),
    OrderState.EXPIRED: frozenset({OrderState.EXPIRED, OrderState.FILLED}),
    OrderState.LOST: frozenset(
        {OrderState.FILLED, OrderState.CANCELLED, OrderState.EXPIRED, OrderState.REJECTED}
    ),
}


def transition_order_state(
    current_state: OrderState | None,
    event: OrderLifecycleEvent,
    *,
    terminal_target: OrderState | None = None,
) -> OrderState:
    """Apply one approved lifecycle event without side effects.

    Args:
        current_state: Current state, or ``None`` when creating an order.
        event: Canonical lifecycle event to apply.
        terminal_target: Required target for a terminal-correction event.

    Returns:
        The deterministic next state.

    Raises:
        InvalidOrderTransition: If the event is not allowed or its target is invalid.
    """
    if event is OrderLifecycleEvent.ORDER_TERMINAL_CORRECTED:
        return _apply_terminal_correction(current_state, terminal_target)
    if terminal_target is not None:
        raise InvalidOrderTransition("terminal_target is only valid for terminal correction")
    targets = _ALLOWED_TRANSITIONS.get((current_state, event))
    if targets is None:
        raise InvalidOrderTransition(f"event {event} is invalid from state {current_state}")
    return next(iter(targets))


def _apply_terminal_correction(
    current_state: OrderState | None,
    terminal_target: OrderState | None,
) -> OrderState:
    """Validate a proven terminal correction target."""
    if terminal_target is None:
        raise InvalidOrderTransition("terminal_target is required for terminal correction")
    if current_state is None:
        raise InvalidOrderTransition("terminal correction requires an existing terminal state")
    targets = _TERMINAL_CORRECTION_TARGETS.get(current_state)
    if targets is None or terminal_target not in targets:
        raise InvalidOrderTransition(
            f"terminal correction to {terminal_target} is invalid from state {current_state}"
        )
    return terminal_target
