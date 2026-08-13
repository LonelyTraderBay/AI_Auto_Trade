"""Pure submit request and outcome primitives for Task 1.3."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from ai_auto_trade.shared_kernel.decimal_value import serialize_decimal


class SubmissionOutcome(StrEnum):
    """Normalized fake-venue submission outcomes."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class SubmitContractError(ValueError):
    """Raised when a durable submit request violates the contract."""


@dataclass(frozen=True, slots=True)
class VenueFill:
    """Immutable fill evidence returned by a venue port."""

    quantity: Decimal
    price: Decimal
    fee_amount: Decimal = Decimal("0")
    fee_asset: str | None = None


@dataclass(frozen=True, slots=True)
class VenueSubmitResponse:
    """Normalized response crossing the execution/venue port."""

    outcome: SubmissionOutcome
    response_sequence: int
    venue_order_id: str | None = None
    fills: tuple[VenueFill, ...] = ()
    fault_code: str | None = None
    attempt_id: str | None = None


@dataclass(frozen=True, slots=True)
class DurableSubmitRequest:
    """Canonical request passed to a local fake venue."""

    order_id: str
    client_order_id: str
    attempt_id: str
    scenario_id: str
    scenario_revision: int
    side: str
    order_type: str
    quantity: Decimal
    limit_price: Decimal
    time_in_force: str
    submitted_at: datetime

    def __post_init__(self) -> None:
        """Validate non-secret identity, time and Decimal boundaries."""
        identities = (self.order_id, self.client_order_id, self.attempt_id, self.scenario_id)
        if any(not value for value in identities):
            raise SubmitContractError("submit identities and scenario_id are required")
        if self.scenario_revision <= 0:
            raise SubmitContractError("scenario_revision must be positive")
        if self.submitted_at.tzinfo != UTC:
            raise SubmitContractError("submitted_at must be timezone-aware UTC")
        if self.quantity <= 0 or self.limit_price <= 0:
            raise SubmitContractError("quantity and limit_price must be positive")
        if self.side not in {"BUY", "SELL"}:
            raise SubmitContractError("side is invalid")
        if self.order_type != "LIMIT" or self.time_in_force not in {"GTC", "IOC", "FOK", "GTD"}:
            raise SubmitContractError("unsupported order type or time in force")

    def payload(self) -> dict[str, str | int]:
        """Return canonical string-based payload for hashing and evidence."""
        return {
            "order_id": self.order_id,
            "client_order_id": self.client_order_id,
            "attempt_id": self.attempt_id,
            "scenario_id": self.scenario_id,
            "scenario_revision": self.scenario_revision,
            "side": self.side,
            "order_type": self.order_type,
            "quantity": serialize_decimal(self.quantity),
            "limit_price": serialize_decimal(self.limit_price),
            "time_in_force": self.time_in_force,
            "submitted_at": self.submitted_at.isoformat().replace("+00:00", "Z"),
        }

    def request_hash(self) -> str:
        """Return the stable SHA-256 hash of the canonical request."""
        encoded = json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def state_for_outcome(outcome: SubmissionOutcome) -> str:
    """Map a venue outcome to the canonical OMS state."""
    states = {
        SubmissionOutcome.ACCEPTED: "OPEN",
        SubmissionOutcome.REJECTED: "REJECTED",
        SubmissionOutcome.PARTIAL_FILL: "PARTIALLY_FILLED",
        SubmissionOutcome.FILLED: "FILLED",
        SubmissionOutcome.CANCELLED: "CANCELLED",
        SubmissionOutcome.TIMEOUT: "UNKNOWN",
        SubmissionOutcome.UNKNOWN: "UNKNOWN",
    }
    return states[outcome]


def is_blind_retry_forbidden(outcome: SubmissionOutcome) -> bool:
    """Return whether a previous result requires reconciliation first."""
    return outcome in {SubmissionOutcome.TIMEOUT, SubmissionOutcome.UNKNOWN}
