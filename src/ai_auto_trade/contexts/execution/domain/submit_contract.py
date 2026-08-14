"""Pure submit request and outcome primitives for Task 1.3."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from ai_auto_trade.shared_kernel.decimal_value import serialize_decimal
from ai_auto_trade.shared_kernel.identity import parse_uuid7


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


class SubmissionSafetyError(SubmitContractError):
    """Raised when a submission safety precondition is not satisfied."""


class SubmissionBlocked(SubmitContractError):
    """Raised when a safety rule intentionally blocks a submission."""


class SubmissionConflictError(SubmitContractError):
    """Raised when an idempotency identity is reused with different data."""


class LeaseLostError(SubmitContractError):
    """Raised when a stale execution owner attempts a protected write."""


@dataclass(frozen=True, slots=True)
class VenueFill:
    """Immutable fill evidence returned by a venue port."""

    quantity: Decimal
    price: Decimal
    fee_amount: Decimal = Decimal("0")
    fee_asset: str | None = None


@dataclass(frozen=True, slots=True)
class SubmissionIdentity:
    """Stable owner, venue and correlation identities for durable persistence."""

    order_intent_id: str
    account_id: str
    instrument_id: str
    correlation_id: str
    trace_id: str
    venue_id: str
    scope_key: str

    def __post_init__(self) -> None:
        """Validate UUIDv7 identity boundaries and non-empty storage scopes."""
        for value in (
            self.order_intent_id,
            self.account_id,
            self.instrument_id,
            self.correlation_id,
            self.trace_id,
            self.venue_id,
        ):
            parse_uuid7(value)
        if not self.scope_key:
            raise SubmitContractError("scope_key is required")

    def payload(self) -> Mapping[str, str]:
        """Return the canonical identity fields included in request hashing."""
        return {
            "order_intent_id": self.order_intent_id,
            "account_id": self.account_id,
            "instrument_id": self.instrument_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "venue_id": self.venue_id,
            "scope_key": self.scope_key,
        }


@dataclass(frozen=True, slots=True)
class SubmissionSafetyContext:
    """Lease and operator safety snapshot required for a protected submit."""

    now: datetime
    lease_owner: str
    lease_expires_at: datetime
    fencing_token: int
    kill_switch_active: bool = False

    def __post_init__(self) -> None:
        """Reject missing, non-UTC or expired internal execution authority."""
        if self.now.tzinfo != UTC or self.lease_expires_at.tzinfo != UTC:
            raise SubmissionSafetyError("safety timestamps must be timezone-aware UTC")
        if not self.lease_owner:
            raise SubmissionSafetyError("lease owner is required")
        if self.fencing_token <= 0:
            raise SubmissionSafetyError("fencing token must be positive")
        if self.lease_expires_at <= self.now:
            raise SubmissionSafetyError("execution lease is expired")
        if self.kill_switch_active:
            raise SubmissionSafetyError("kill switch is active")


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
    identity: SubmissionIdentity | None = None

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

    def payload(self) -> dict[str, object]:
        """Return canonical string-based payload for hashing and evidence."""
        payload: dict[str, object] = {
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
        if self.identity is not None:
            payload["identity"] = dict(self.identity.payload())
        return payload

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


@dataclass(frozen=True, slots=True)
class PersistedSubmissionResult:
    """Canonical result returned by a durable persistence adapter."""

    outcome: SubmissionOutcome
    state: str
    attempt_id: str
    retry_forbidden: bool
