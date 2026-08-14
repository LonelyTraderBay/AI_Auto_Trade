"""PostgreSQL durable-submit adapter for the local Phase 1 simulator."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.row import RowMapping

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    LeaseLostError,
    PersistedSubmissionResult,
    SubmissionConflictError,
    SubmissionIdentity,
    SubmissionOutcome,
    SubmissionSafetyContext,
    SubmissionSafetyError,
    VenueSubmitResponse,
    is_blind_retry_forbidden,
    state_for_outcome,
)
from ai_auto_trade.contexts.execution.ports.submission_port import PreparedSubmission
from ai_auto_trade.contexts.risk.domain.risk_gate import RiskDecision, RiskVerdict
from ai_auto_trade.shared_kernel.decimal_value import serialize_decimal
from ai_auto_trade.shared_kernel.identity import generate_uuid7, parse_uuid7

_RESERVATION_KIND = "ORDER_NOTIONAL"
_RESERVATION_ASSET = "LOCAL_QUOTE"
_SHA256_LENGTH = 64
_KNOWN_OUTCOMES = frozenset(outcome.value for outcome in SubmissionOutcome)
_EVENT_BY_OUTCOME = {
    SubmissionOutcome.ACCEPTED: ("execution.order_acknowledged.v1", "OPEN", "ACKNOWLEDGED"),
    SubmissionOutcome.REJECTED: ("execution.order_rejected.v1", "REJECTED", "REJECTED"),
    SubmissionOutcome.PARTIAL_FILL: (
        "execution.order_partially_filled.v1",
        "PARTIALLY_FILLED",
        "PARTIAL_FILL",
    ),
    SubmissionOutcome.FILLED: ("execution.order_filled.v1", "FILLED", "FILLED"),
    SubmissionOutcome.TIMEOUT: ("execution.order_unknown.v1", "UNKNOWN", "TIMEOUT"),
    SubmissionOutcome.UNKNOWN: ("execution.order_unknown.v1", "UNKNOWN", "UNKNOWN"),
}
_TERMINAL_REASON = {
    SubmissionOutcome.REJECTED: "REJECTED",
    SubmissionOutcome.FILLED: "FILLED",
}


@dataclass(frozen=True, slots=True)
class _EventAppend:
    """Immutable input for one lifecycle event/outbox append."""

    request: DurableSubmitRequest
    attempt_id: str
    event_type: str
    state: str
    previous_state: str | None
    order_version: int
    reason_code: str
    occurred_at: datetime
    venue_order_id: str | None = None
    executed_quantity: Decimal = Decimal("0")
    terminal_reason: str | None = None


class PostgresTradingSubmissionUnitOfWork:
    """Persist and recover one local submit using approved PostgreSQL boundaries."""

    def __init__(self, engine: Engine) -> None:
        """Bind a synchronous PostgreSQL engine used outside the venue call."""
        self._engine = engine

    def prepare(
        self,
        request: DurableSubmitRequest,
        risk_decision: RiskDecision,
        safety: SubmissionSafetyContext,
    ) -> PreparedSubmission:
        """Commit risk, queue, first attempt, lifecycle and outbox facts atomically."""
        identity = _require_identity(request)
        _validate_persistable_decision(risk_decision)
        _validate_request_ids(request)
        with self._engine.connect() as connection:
            serializable = connection.execution_options(isolation_level="SERIALIZABLE")
            with serializable.begin():
                _lock_limit_state(serializable, identity.scope_key, safety)
                _validate_policy(serializable, risk_decision, identity.scope_key, safety.now)
                _ensure_reservation(serializable, request, risk_decision, safety.now)
                _ensure_decision(serializable, identity.order_intent_id, risk_decision, safety.now)
                existing = _load_order(serializable, request)
                if existing is not None:
                    return _replay_existing(serializable, request, existing)
                _insert_order(serializable, request, risk_decision, safety.now)
                _insert_first_attempt(serializable, request, safety)
                _ensure_reconciliation_case(serializable, request, safety.now)
                _append_event(
                    serializable,
                    _EventAppend(
                        request=request,
                        attempt_id=request.attempt_id,
                        event_type="execution.order_submission_queued.v1",
                        state="SUBMISSION_QUEUED",
                        previous_state="RISK_APPROVED",
                        order_version=1,
                        reason_code="SUBMISSION_QUEUED",
                        occurred_at=safety.now,
                    ),
                )
        return PreparedSubmission(
            request=request,
            order_id=request.order_id,
            attempt_id=request.attempt_id,
            request_hash=request.request_hash(),
            scope_key=identity.scope_key,
        )

    def claim_for_submit(
        self,
        prepared: PreparedSubmission,
        safety: SubmissionSafetyContext,
    ) -> bool:
        """Claim one queued attempt with a lease before making the venue call."""
        identity = _require_identity(prepared.request)
        with self._engine.connect() as connection:
            serializable = connection.execution_options(isolation_level="SERIALIZABLE")
            with serializable.begin():
                _lock_limit_state(serializable, identity.scope_key, safety)
                order = _lock_order(serializable, prepared.order_id)
                attempt = _lock_attempt(serializable, prepared.attempt_id)
                _validate_attempt_binding(attempt, prepared)
                if _text_value(attempt, "outcome") != SubmissionOutcome.UNKNOWN.value:
                    return False
                if _text_value(order, "state") != "SUBMISSION_QUEUED":
                    return False
                _validate_lease_owner(attempt, safety)
                next_version = _int_value(order, "aggregate_version") + 1
                serializable.execute(
                    sa.text(
                        "UPDATE execution.orders SET state = 'SUBMITTING', "
                        "aggregate_version = :version, recorded_at = :recorded_at "
                        "WHERE order_id = :order_id AND aggregate_version = :previous_version"
                    ),
                    {
                        "version": next_version,
                        "recorded_at": safety.now,
                        "order_id": prepared.order_id,
                        "previous_version": next_version - 1,
                    },
                )
                serializable.execute(
                    sa.text(
                        "UPDATE execution.submission_attempts SET sent_at = :sent_at "
                        "WHERE attempt_id = :attempt_id AND outcome = 'UNKNOWN'"
                    ),
                    {"sent_at": safety.now, "attempt_id": prepared.attempt_id},
                )
                _append_event(
                    serializable,
                    _EventAppend(
                        request=prepared.request,
                        attempt_id=prepared.attempt_id,
                        event_type="execution.order_submitting.v1",
                        state="SUBMITTING",
                        previous_state="SUBMISSION_QUEUED",
                        order_version=next_version,
                        reason_code="SUBMISSION_CLAIMED",
                        occurred_at=safety.now,
                    ),
                )
        return True

    def record_outcome(
        self,
        prepared: PreparedSubmission,
        response: VenueSubmitResponse,
        safety: SubmissionSafetyContext,
    ) -> PersistedSubmissionResult:
        """Apply one response with fencing, lifecycle CAS and fill dedupe."""
        identity = _require_identity(prepared.request)
        if response.outcome is SubmissionOutcome.CANCELLED:
            raise SubmissionSafetyError("CANCELLED requires the explicit cancel workflow")
        if response.attempt_id is not None and response.attempt_id != prepared.attempt_id:
            raise SubmissionConflictError("venue response is bound to another attempt")
        with self._engine.connect() as connection:
            transaction_connection = connection.execution_options(isolation_level="READ COMMITTED")
            with transaction_connection.begin():
                _lock_limit_state(transaction_connection, identity.scope_key, safety)
                order = _lock_order(transaction_connection, prepared.order_id)
                attempt = _lock_attempt(transaction_connection, prepared.attempt_id)
                _validate_attempt_binding(attempt, prepared)
                existing_outcome = _outcome_value(attempt)
                if existing_outcome is not SubmissionOutcome.UNKNOWN:
                    return _result(existing_outcome, str(attempt["attempt_id"]))
                _validate_lease_owner(attempt, safety)
                if _text_value(order, "state") != "SUBMITTING":
                    raise SubmissionSafetyError("submission is not in SUBMITTING state")
                event_type, state, reason_code = _EVENT_BY_OUTCOME[response.outcome]
                executed_quantity = _insert_fills(
                    transaction_connection, prepared, response, safety.now
                )
                next_version = _int_value(order, "aggregate_version") + 1
                terminal_reason = _TERMINAL_REASON.get(response.outcome)
                transaction_connection.execute(
                    sa.text(
                        "UPDATE execution.orders SET state = :state, "
                        "terminal_reason = :terminal_reason, "
                        "aggregate_version = :version, recorded_at = :recorded_at "
                        "WHERE order_id = :order_id AND aggregate_version = :previous_version "
                        "AND state = 'SUBMITTING'"
                    ),
                    {
                        "state": state,
                        "terminal_reason": terminal_reason,
                        "version": next_version,
                        "recorded_at": safety.now,
                        "order_id": prepared.order_id,
                        "previous_version": next_version - 1,
                    },
                )
                transaction_connection.execute(
                    sa.text(
                        "UPDATE execution.submission_attempts SET outcome = :outcome, "
                        "venue_order_id = :venue_order_id, received_at = :received_at, "
                        "evidence_json = CAST(:evidence_json AS jsonb) "
                        "WHERE attempt_id = :attempt_id AND outcome = 'UNKNOWN'"
                    ),
                    {
                        "outcome": response.outcome.value,
                        "venue_order_id": response.venue_order_id,
                        "received_at": safety.now,
                        "evidence_json": _json_text(_response_evidence(response)),
                        "attempt_id": prepared.attempt_id,
                    },
                )
                _resolve_reconciliation_case(
                    transaction_connection,
                    prepared.attempt_id,
                    response.outcome,
                    safety.now,
                )
                _append_event(
                    transaction_connection,
                    _EventAppend(
                        request=prepared.request,
                        attempt_id=prepared.attempt_id,
                        event_type=event_type,
                        state=state,
                        previous_state="SUBMITTING",
                        order_version=next_version,
                        reason_code=reason_code,
                        occurred_at=safety.now,
                        venue_order_id=response.venue_order_id,
                        executed_quantity=executed_quantity,
                        terminal_reason=terminal_reason,
                    ),
                )
        return _result(response.outcome, prepared.attempt_id)

    def claim_outbox(
        self,
        outbox_id: str,
        claim_owner: str,
        fencing_token: int,
        now: datetime,
        claim_expires_at: datetime,
    ) -> bool:
        """Claim delivery state with a short lease and monotonic fencing token."""
        _validate_delivery_lease(claim_owner, fencing_token, now, claim_expires_at)
        with self._engine.begin() as connection:
            delivery = _lock_delivery(connection, outbox_id)
            status = _text_value(delivery, "status")
            if status in {"PUBLISHED", "DEAD_LETTER"}:
                return False
            existing_expiry = delivery.get("claim_expires_at")
            if (
                status == "CLAIMED"
                and isinstance(existing_expiry, datetime)
                and existing_expiry > now
                and (
                    _optional_text(delivery, "claim_owner") != claim_owner
                    or _optional_int(delivery, "claim_fencing_token") != fencing_token
                )
            ):
                return False
            connection.execute(
                sa.text(
                    "UPDATE platform.outbox_delivery_state SET status = 'CLAIMED', "
                    "claim_owner = :claim_owner, claim_fencing_token = :fencing_token, "
                    "claim_expires_at = :claim_expires_at, last_attempt_at = :now, "
                    "delivery_version = delivery_version + 1, updated_at = :now "
                    "WHERE outbox_id = :outbox_id"
                ),
                {
                    "claim_owner": claim_owner,
                    "fencing_token": fencing_token,
                    "claim_expires_at": claim_expires_at,
                    "now": now,
                    "outbox_id": outbox_id,
                },
            )
        return True

    def mark_outbox_published(
        self,
        outbox_id: str,
        claim_owner: str,
        fencing_token: int,
        now: datetime,
    ) -> bool:
        """CAS one claimed delivery to PUBLISHED; duplicate acknowledgements are safe."""
        if now.tzinfo != UTC or not claim_owner or fencing_token <= 0:
            raise SubmissionSafetyError("invalid outbox publisher authority")
        with self._engine.begin() as connection:
            delivery = _lock_delivery(connection, outbox_id)
            status = _text_value(delivery, "status")
            if status == "PUBLISHED":
                return True
            if status != "CLAIMED":
                raise SubmissionSafetyError("outbox delivery is not claimed")
            if (
                _optional_text(delivery, "claim_owner") != claim_owner
                or _optional_int(delivery, "claim_fencing_token") != fencing_token
            ):
                raise LeaseLostError("outbox delivery fencing token is stale")
            claim_expires_at = _optional_datetime(delivery, "claim_expires_at")
            if claim_expires_at is None or claim_expires_at <= now:
                raise LeaseLostError("outbox delivery lease has expired")
            connection.execute(
                sa.text(
                    "UPDATE platform.outbox_delivery_state SET status = 'PUBLISHED', "
                    "published_at = :published_at, claim_expires_at = NULL, "
                    "delivery_version = delivery_version + 1, updated_at = :published_at "
                    "WHERE outbox_id = :outbox_id AND status = 'CLAIMED' "
                    "AND claim_owner = :claim_owner AND claim_fencing_token = :fencing_token"
                ),
                {
                    "published_at": now,
                    "outbox_id": outbox_id,
                    "claim_owner": claim_owner,
                    "fencing_token": fencing_token,
                },
            )
        return True

    def consume_outbox(self, outbox_id: str, consumer_id: str, processed_at: datetime) -> bool:
        """Record one inbox receipt; duplicate publish/consume has no second effect."""
        if processed_at.tzinfo != UTC or not consumer_id:
            raise SubmissionSafetyError("invalid inbox consumer context")
        with self._engine.begin() as connection:
            outbox = (
                connection.execute(
                    sa.text(
                        "SELECT event_id, event_type, schema_version, partition_key, "
                        "source_context, "
                        "payload_hash, correlation_id "
                        "FROM platform.outbox WHERE outbox_id = :outbox_id"
                    ),
                    {"outbox_id": outbox_id},
                )
                .mappings()
                .one_or_none()
            )
            if outbox is None:
                raise SubmissionSafetyError("outbox message does not exist")
            result = connection.execute(
                sa.text(
                    "INSERT INTO platform.inbox "
                    "(inbox_id, consumer_id, event_id, event_type, schema_version, partition_key, "
                    "source_context, result_hash, processed_at, recorded_at, "
                    "correlation_id) VALUES "
                    "(:inbox_id, :consumer_id, :event_id, :event_type, "
                    ":schema_version, :partition_key, "
                    ":source_context, :result_hash, :processed_at, :recorded_at, :correlation_id) "
                    "ON CONFLICT (consumer_id, event_id) DO NOTHING"
                ),
                {
                    "inbox_id": str(generate_uuid7()),
                    "consumer_id": consumer_id,
                    "event_id": outbox["event_id"],
                    "event_type": outbox["event_type"],
                    "schema_version": outbox["schema_version"],
                    "partition_key": outbox["partition_key"],
                    "source_context": outbox["source_context"],
                    "result_hash": outbox["payload_hash"],
                    "processed_at": processed_at,
                    "recorded_at": processed_at,
                    "correlation_id": outbox["correlation_id"],
                },
            )
        return result.rowcount == 1


def _require_identity(request: DurableSubmitRequest) -> SubmissionIdentity:
    """Return the persistence identity or fail closed before touching PostgreSQL."""
    if request.identity is None:
        raise SubmissionSafetyError("durable persistence requires complete submission identity")
    return request.identity


def _validate_request_ids(request: DurableSubmitRequest) -> None:
    """Validate UUIDv7 IDs at the persistence boundary."""
    for value in (request.order_id, request.client_order_id, request.attempt_id):
        parse_uuid7(value)


def _validate_persistable_decision(decision: RiskDecision) -> None:
    """Require all immutable risk evidence needed by the approved schema."""
    if decision.verdict is not RiskVerdict.APPROVE:
        raise SubmissionSafetyError("only APPROVE decisions may enter durable submit")
    if not decision.decision_id or not decision.policy_id or not decision.reservation_id:
        raise SubmissionSafetyError("risk decision identifiers are incomplete")
    if decision.portfolio_snapshot_hash is None or decision.market_snapshot_hash is None:
        raise SubmissionSafetyError("risk snapshot hashes are required")
    for value in (
        decision.decision_id,
        decision.policy_id,
        decision.reservation_id,
    ):
        parse_uuid7(value)
    for value in (
        decision.policy_hash,
        decision.input_hash,
        decision.portfolio_snapshot_hash,
        decision.market_snapshot_hash,
    ):
        _validate_hash(value)


def _validate_hash(value: str) -> None:
    """Validate a raw lowercase SHA-256 value used by database constraints."""
    if len(value) != _SHA256_LENGTH or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise SubmissionSafetyError("hash must be lowercase SHA-256")


def _lock_limit_state(
    connection: Connection, scope_key: str, safety: SubmissionSafetyContext
) -> None:
    """Lock the risk scope first and verify its fencing token."""
    row = (
        connection.execute(
            sa.text(
                "SELECT fencing_token FROM risk.limit_state WHERE scope_key = :scope_key FOR UPDATE"
            ),
            {"scope_key": scope_key},
        )
        .mappings()
        .one_or_none()
    )
    if row is None or _int_value(row, "fencing_token") != safety.fencing_token:
        raise LeaseLostError("risk scope fencing token does not match execution lease")


def _validate_policy(
    connection: Connection,
    decision: RiskDecision,
    scope_key: str,
    now: datetime,
) -> None:
    """Ensure the referenced policy remains active and bound to the decision."""
    row = (
        connection.execute(
            sa.text(
                "SELECT scope_key, status, policy_version, policy_hash, effective_at, expires_at "
                "FROM risk.policies WHERE policy_id = :policy_id"
            ),
            {"policy_id": decision.policy_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("risk policy is missing")
    if _text_value(row, "scope_key") != scope_key:
        raise SubmissionSafetyError("risk policy scope mismatch")
    if _text_value(row, "status") != "ACTIVE":
        raise SubmissionSafetyError("risk policy is not active")
    if _text_value(row, "policy_version") != decision.policy_version:
        raise SubmissionSafetyError("risk policy version mismatch")
    if _text_value(row, "policy_hash") != decision.policy_hash:
        raise SubmissionSafetyError("risk policy hash mismatch")
    effective_at = _datetime_value(row, "effective_at")
    expires_at = _datetime_value(row, "expires_at")
    if not effective_at <= now < expires_at:
        raise SubmissionSafetyError("risk policy is outside its effective window")


def _ensure_reservation(
    connection: Connection,
    request: DurableSubmitRequest,
    decision: RiskDecision,
    recorded_at: datetime,
) -> None:
    """Insert or validate the active reservation before execution facts."""
    identity = _require_identity(request)
    assert decision.policy_id is not None
    assert decision.reservation_id is not None
    reserved_amount = decision.approved_quantity * request.limit_price
    existing_by_intent = (
        connection.execute(
            sa.text(
                "SELECT reservation_id FROM risk.reservations "
                "WHERE order_intent_id = :order_intent_id AND reservation_kind = :kind FOR UPDATE"
            ),
            {"order_intent_id": identity.order_intent_id, "kind": _RESERVATION_KIND},
        )
        .mappings()
        .one_or_none()
    )
    if (
        existing_by_intent is not None
        and str(existing_by_intent["reservation_id"]) != decision.reservation_id
    ):
        raise SubmissionConflictError("order intent already has a different reservation")
    connection.execute(
        sa.text(
            "INSERT INTO risk.reservations "
            "(reservation_id, order_intent_id, reservation_kind, scope_key, asset, "
            "reserved_amount, "
            "lifecycle, policy_id, expires_at, aggregate_version, recorded_at) VALUES "
            "(:reservation_id, :order_intent_id, :kind, :scope_key, :asset, :reserved_amount, "
            "'ACTIVE', :policy_id, :expires_at, 0, :recorded_at) "
            "ON CONFLICT (reservation_id) DO NOTHING"
        ),
        {
            "reservation_id": decision.reservation_id,
            "order_intent_id": identity.order_intent_id,
            "kind": _RESERVATION_KIND,
            "scope_key": identity.scope_key,
            "asset": _RESERVATION_ASSET,
            "reserved_amount": reserved_amount,
            "policy_id": decision.policy_id,
            "expires_at": decision.expires_at,
            "recorded_at": recorded_at,
        },
    )
    row = (
        connection.execute(
            sa.text(
                "SELECT order_intent_id, scope_key, asset, reserved_amount, lifecycle, policy_id, "
                "expires_at, released_at, consumed_at FROM risk.reservations "
                "WHERE reservation_id = :reservation_id FOR UPDATE"
            ),
            {"reservation_id": decision.reservation_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("reservation could not be persisted")
    if (
        str(row["order_intent_id"]) != identity.order_intent_id
        or _text_value(row, "scope_key") != identity.scope_key
        or _text_value(row, "asset") != _RESERVATION_ASSET
        or _text_value(row, "lifecycle") != "ACTIVE"
        or str(row["policy_id"]) != decision.policy_id
        or _optional_datetime(row, "released_at") is not None
        or _optional_datetime(row, "consumed_at") is not None
        or _decimal_value(row, "reserved_amount") != reserved_amount
        or _datetime_value(row, "expires_at") != decision.expires_at
        or _datetime_value(row, "expires_at") <= recorded_at
    ):
        raise SubmissionConflictError("risk reservation does not match the approval")


def _ensure_decision(
    connection: Connection,
    order_intent_id: str,
    decision: RiskDecision,
    recorded_at: datetime,
) -> None:
    """Insert or validate immutable risk decision evidence."""
    assert decision.decision_id is not None
    assert decision.policy_id is not None
    assert decision.reservation_id is not None
    connection.execute(
        sa.text(
            "INSERT INTO risk.decisions "
            "(decision_id, order_intent_id, verdict, approved_quantity, policy_id, policy_version, "
            "policy_hash, reservation_id, portfolio_snapshot_hash, market_snapshot_hash, "
            "input_hash, "
            "reason_code, decided_at, expires_at, recorded_at) VALUES "
            "(:decision_id, :order_intent_id, 'APPROVE', :approved_quantity, :policy_id, "
            ":policy_version, :policy_hash, :reservation_id, :portfolio_hash, :market_hash, "
            ":input_hash, "
            ":reason_code, :decided_at, :expires_at, :recorded_at) "
            "ON CONFLICT (decision_id) DO NOTHING"
        ),
        {
            "decision_id": decision.decision_id,
            "order_intent_id": order_intent_id,
            "approved_quantity": decision.approved_quantity,
            "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
            "policy_hash": decision.policy_hash,
            "reservation_id": decision.reservation_id,
            "portfolio_hash": decision.portfolio_snapshot_hash,
            "market_hash": decision.market_snapshot_hash,
            "input_hash": decision.input_hash,
            "reason_code": decision.reason_code,
            "decided_at": decision.decided_at,
            "expires_at": decision.expires_at,
            "recorded_at": recorded_at,
        },
    )
    row = (
        connection.execute(
            sa.text(
                "SELECT order_intent_id, verdict, approved_quantity, policy_id, policy_version, "
                "policy_hash, reservation_id, portfolio_snapshot_hash, "
                "market_snapshot_hash, input_hash, expires_at FROM risk.decisions "
                "WHERE decision_id = :decision_id FOR UPDATE"
            ),
            {"decision_id": decision.decision_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("risk decision could not be persisted")
    if (
        str(row["order_intent_id"]) != order_intent_id
        or _text_value(row, "verdict") != RiskVerdict.APPROVE.value
        or _decimal_value(row, "approved_quantity") != decision.approved_quantity
        or str(row["policy_id"]) != decision.policy_id
        or _text_value(row, "policy_version") != decision.policy_version
        or _text_value(row, "policy_hash") != decision.policy_hash
        or str(row["reservation_id"]) != decision.reservation_id
        or _text_value(row, "portfolio_snapshot_hash") != decision.portfolio_snapshot_hash
        or _text_value(row, "market_snapshot_hash") != decision.market_snapshot_hash
        or _text_value(row, "input_hash") != decision.input_hash
        or _datetime_value(row, "expires_at") != decision.expires_at
    ):
        raise SubmissionConflictError("risk decision identity is reused with different evidence")


def _load_order(
    connection: Connection,
    request: DurableSubmitRequest,
) -> RowMapping | None:
    """Load the canonical order by venue/account/client identity."""
    identity = _require_identity(request)
    return (
        connection.execute(
            sa.text(
                "SELECT order_id, order_intent_id, state, aggregate_version, request_hash "
                "FROM execution.orders WHERE venue_id = :venue_id AND account_id = :account_id "
                "AND client_order_id = :client_order_id FOR UPDATE"
            ),
            {
                "venue_id": identity.venue_id,
                "account_id": identity.account_id,
                "client_order_id": request.client_order_id,
            },
        )
        .mappings()
        .one_or_none()
    )


def _insert_order(
    connection: Connection,
    request: DurableSubmitRequest,
    decision: RiskDecision,
    recorded_at: datetime,
) -> None:
    """Insert one queue state bound to the approved risk evidence."""
    identity = _require_identity(request)
    connection.execute(
        sa.text(
            "INSERT INTO execution.orders "
            "(order_id, order_intent_id, client_order_id, venue_id, account_id, "
            "instrument_id, state, "
            "aggregate_version, request_hash, quantity, limit_price, created_at, expires_at, "
            "recorded_at, correlation_id) VALUES "
            "(:order_id, :order_intent_id, :client_order_id, :venue_id, :account_id, "
            ":instrument_id, 'SUBMISSION_QUEUED', 1, :request_hash, :quantity, :limit_price, "
            ":created_at, :expires_at, "
            ":recorded_at, :correlation_id)"
        ),
        {
            "order_id": request.order_id,
            "order_intent_id": identity.order_intent_id,
            "client_order_id": request.client_order_id,
            "venue_id": identity.venue_id,
            "account_id": identity.account_id,
            "instrument_id": identity.instrument_id,
            "request_hash": request.request_hash(),
            "quantity": request.quantity,
            "limit_price": request.limit_price,
            "created_at": request.submitted_at,
            "expires_at": decision.expires_at,
            "recorded_at": recorded_at,
            "correlation_id": identity.correlation_id,
        },
    )


def _insert_first_attempt(
    connection: Connection,
    request: DurableSubmitRequest,
    safety: SubmissionSafetyContext,
) -> None:
    """Record a conservative UNKNOWN attempt before any venue call."""
    connection.execute(
        sa.text(
            "INSERT INTO execution.submission_attempts "
            "(attempt_id, order_id, attempt_ordinal, request_hash, outcome, lease_owner, "
            "fencing_token, "
            "recorded_at, evidence_json) VALUES "
            "(:attempt_id, :order_id, 1, :request_hash, 'UNKNOWN', :lease_owner, :fencing_token, "
            ":recorded_at, CAST(:evidence_json AS jsonb))"
        ),
        {
            "attempt_id": request.attempt_id,
            "order_id": request.order_id,
            "request_hash": request.request_hash(),
            "lease_owner": safety.lease_owner,
            "fencing_token": safety.fencing_token,
            "recorded_at": safety.now,
            "evidence_json": _json_text(
                {"phase": "PRE_SUBMIT_COMMITTED", "request_hash": request.request_hash()}
            ),
        },
    )


def _ensure_reconciliation_case(
    connection: Connection,
    request: DurableSubmitRequest,
    opened_at: datetime,
) -> None:
    """Link conservative pre-submit uncertainty to an open recovery case."""
    existing = connection.execute(
        sa.text(
            "SELECT case_id FROM execution.reconciliation_cases "
            "WHERE attempt_id = :attempt_id AND status IN ('OPEN','IN_PROGRESS')"
        ),
        {"attempt_id": request.attempt_id},
    ).first()
    if existing is not None:
        return
    connection.execute(
        sa.text(
            "INSERT INTO execution.reconciliation_cases "
            "(case_id, order_id, attempt_id, classification, status, evidence_json, "
            "opened_at) VALUES "
            "(:case_id, :order_id, :attempt_id, 'UNKNOWN', 'OPEN', "
            "CAST(:evidence_json AS jsonb), :opened_at)"
        ),
        {
            "case_id": str(generate_uuid7()),
            "order_id": request.order_id,
            "attempt_id": request.attempt_id,
            "evidence_json": _json_text({"reason": "PRE_SUBMIT_UNCERTAIN"}),
            "opened_at": opened_at,
        },
    )


def _replay_existing(
    connection: Connection,
    request: DurableSubmitRequest,
    order: RowMapping,
) -> PreparedSubmission:
    """Return the prior canonical result and never re-enter the venue."""
    if str(order["order_id"]) != request.order_id:
        raise SubmissionConflictError("client order identity is bound to another order")
    if _text_value(order, "request_hash") != request.request_hash():
        raise SubmissionConflictError("request hash conflicts with canonical order")
    attempt = (
        connection.execute(
            sa.text(
                "SELECT attempt_id, request_hash, outcome FROM execution.submission_attempts "
                "WHERE order_id = :order_id ORDER BY attempt_ordinal DESC LIMIT 1"
            ),
            {"order_id": request.order_id},
        )
        .mappings()
        .one_or_none()
    )
    if attempt is None:
        raise SubmissionSafetyError("canonical order has no submission attempt")
    if _text_value(attempt, "request_hash") != request.request_hash():
        raise SubmissionConflictError("attempt hash conflicts with canonical order")
    outcome = _outcome_value(attempt)
    return PreparedSubmission(
        request=request,
        order_id=request.order_id,
        attempt_id=str(attempt["attempt_id"]),
        request_hash=request.request_hash(),
        scope_key=_require_identity(request).scope_key,
        replay=_result(outcome, str(attempt["attempt_id"])),
    )


def _lock_order(connection: Connection, order_id: str) -> RowMapping:
    """Lock one order aggregate for a CAS transition."""
    row = (
        connection.execute(
            sa.text(
                "SELECT order_id, state, aggregate_version FROM execution.orders "
                "WHERE order_id = :order_id FOR UPDATE"
            ),
            {"order_id": order_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("canonical order does not exist")
    return row


def _lock_attempt(connection: Connection, attempt_id: str) -> RowMapping:
    """Lock one immutable-attempt envelope for a guarded response update."""
    row = (
        connection.execute(
            sa.text(
                "SELECT attempt_id, order_id, request_hash, outcome, lease_owner, fencing_token "
                "FROM execution.submission_attempts WHERE attempt_id = :attempt_id FOR UPDATE"
            ),
            {"attempt_id": attempt_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("submission attempt does not exist")
    return row


def _validate_attempt_binding(
    attempt: RowMapping,
    prepared: PreparedSubmission,
) -> None:
    """Reject stale or cross-order attempt writes."""
    if (
        str(attempt["order_id"]) != prepared.order_id
        or _text_value(attempt, "request_hash") != prepared.request_hash
    ):
        raise SubmissionConflictError("attempt is not bound to the canonical request")


def _validate_lease_owner(
    attempt: RowMapping,
    safety: SubmissionSafetyContext,
) -> None:
    """Enforce owner and fencing token on every pre-submit response write."""
    if (
        _optional_text(attempt, "lease_owner") != safety.lease_owner
        or _optional_int(attempt, "fencing_token") != safety.fencing_token
    ):
        raise LeaseLostError("submission attempt fencing token is stale")


def _insert_fills(
    connection: Connection,
    prepared: PreparedSubmission,
    response: VenueSubmitResponse,
    recorded_at: datetime,
) -> Decimal:
    """Insert response fills once and return their cumulative quantity."""
    identity = _require_identity(prepared.request)
    total = Decimal("0")
    for index, fill in enumerate(response.fills, start=1):
        total += fill.quantity
        fingerprint = hashlib.sha256(
            f"{prepared.order_id}:{response.response_sequence}:{index}:"
            f"{serialize_decimal(fill.quantity)}:{serialize_decimal(fill.price)}".encode()
        ).hexdigest()
        connection.execute(
            sa.text(
                "INSERT INTO execution.fills "
                "(fill_id, order_id, venue_id, account_id, venue_fill_id, source_fingerprint, "
                "price, quantity, fee_amount, fee_asset, liquidity_flag, sequence, "
                "occurred_at, received_at, "
                "processed_at, recorded_at, quality_flags) VALUES "
                "(:fill_id, :order_id, :venue_id, :account_id, NULL, :source_fingerprint, :price, "
                ":quantity, :fee_amount, :fee_asset, 'UNKNOWN', :sequence, "
                ":occurred_at, :received_at, "
                ":processed_at, :recorded_at, CAST(:quality_flags AS jsonb)) "
                "ON CONFLICT (venue_id, account_id, source_fingerprint) DO NOTHING"
            ),
            {
                "fill_id": str(generate_uuid7()),
                "order_id": prepared.order_id,
                "venue_id": identity.venue_id,
                "account_id": identity.account_id,
                "source_fingerprint": fingerprint,
                "price": fill.price,
                "quantity": fill.quantity,
                "fee_amount": fill.fee_amount,
                "fee_asset": fill.fee_asset,
                "sequence": index,
                "occurred_at": recorded_at,
                "received_at": recorded_at,
                "processed_at": recorded_at,
                "recorded_at": recorded_at,
                "quality_flags": _json_text({"source": "fake_venue"}),
            },
        )
    return total


def _resolve_reconciliation_case(
    connection: Connection,
    attempt_id: str,
    outcome: SubmissionOutcome,
    resolved_at: datetime,
) -> None:
    """Keep unknown/timeouts open and close only proven responses."""
    if is_blind_retry_forbidden(outcome):
        return
    connection.execute(
        sa.text(
            "UPDATE execution.reconciliation_cases SET status = 'RESOLVED', "
            "resolved_at = :resolved_at "
            "WHERE attempt_id = :attempt_id AND status IN ('OPEN','IN_PROGRESS')"
        ),
        {"resolved_at": resolved_at, "attempt_id": attempt_id},
    )


def _append_event(
    connection: Connection,
    event: _EventAppend,
) -> None:
    """Append one immutable lifecycle event and its delivery state atomically."""
    request = event.request
    identity = _require_identity(request)
    event_id = str(generate_uuid7())
    outbox_id = str(generate_uuid7())
    payload = {
        "id": event_id,
        "type": event.event_type,
        "schema_version": 1,
        "source": "execution",
        "occurred_at": _iso(event.occurred_at),
        "received_at": None,
        "processed_at": None,
        "recorded_at": _iso(event.occurred_at),
        "correlation_id": identity.correlation_id,
        "causation_id": event.attempt_id,
        "trace_id": identity.trace_id,
        "subject_id": request.order_id,
        "partition_key": request.client_order_id,
        "data": {
            "order_id": request.order_id,
            "order_intent_id": identity.order_intent_id,
            "client_order_id": request.client_order_id,
            "account_id": identity.account_id,
            "venue_id": identity.venue_id,
            "instrument_id": identity.instrument_id,
            "state": event.state,
            "previous_state": event.previous_state,
            "order_version": event.order_version,
            "event_reason_code": event.reason_code,
            "executed_quantity": serialize_decimal(event.executed_quantity),
            "canonical_request_hash": f"sha256:{request.request_hash()}",
            "venue_order_id": event.venue_order_id,
            "terminal_reason": event.terminal_reason,
            "fill_id": None,
            "submission_attempt_id": event.attempt_id,
        },
    }
    payload_text = _json_text(payload)
    payload_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    connection.execute(
        sa.text(
            "INSERT INTO execution.order_events "
            "(event_id, order_id, sequence, event_type, schema_version, payload_json, "
            "recorded_at, "
            "correlation_id, causation_id) VALUES "
            "(:event_id, :order_id, :sequence, :event_type, 1, CAST(:payload AS jsonb), "
            ":recorded_at, "
            ":correlation_id, :causation_id)"
        ),
        {
            "event_id": event_id,
            "order_id": request.order_id,
            "sequence": event.order_version,
            "event_type": event.event_type,
            "payload": payload_text,
            "recorded_at": event.occurred_at,
            "correlation_id": identity.correlation_id,
            "causation_id": event.attempt_id,
        },
    )
    connection.execute(
        sa.text(
            "INSERT INTO platform.outbox "
            "(outbox_id, event_id, source_context, source_aggregate_type, source_aggregate_id, "
            "event_type, schema_version, partition_key, payload, payload_hash, occurred_at, "
            "recorded_at, "
            "correlation_id, causation_id, trace_id) VALUES "
            "(:outbox_id, :event_id, 'execution', 'ORDER', :order_id, :event_type, 1, "
            ":partition_key, "
            "CAST(:payload AS jsonb), :payload_hash, :occurred_at, :recorded_at, :correlation_id, "
            ":causation_id, :trace_id)"
        ),
        {
            "outbox_id": outbox_id,
            "event_id": event_id,
            "order_id": request.order_id,
            "event_type": event.event_type,
            "partition_key": request.client_order_id,
            "payload": payload_text,
            "payload_hash": payload_hash,
            "occurred_at": event.occurred_at,
            "recorded_at": event.occurred_at,
            "correlation_id": identity.correlation_id,
            "causation_id": event.attempt_id,
            "trace_id": identity.trace_id,
        },
    )
    connection.execute(
        sa.text(
            "INSERT INTO platform.outbox_delivery_state "
            "(outbox_id, status, attempt_count, next_attempt_at, delivery_version, "
            "updated_at) VALUES "
            "(:outbox_id, 'PENDING', 0, :next_attempt_at, 0, :updated_at)"
        ),
        {
            "outbox_id": outbox_id,
            "next_attempt_at": event.occurred_at,
            "updated_at": event.occurred_at,
        },
    )


def _lock_delivery(connection: Connection, outbox_id: str) -> RowMapping:
    """Lock a delivery row for publisher CAS."""
    row = (
        connection.execute(
            sa.text(
                "SELECT status, claim_owner, claim_fencing_token, claim_expires_at, "
                "delivery_version "
                "FROM platform.outbox_delivery_state WHERE outbox_id = :outbox_id FOR UPDATE"
            ),
            {"outbox_id": outbox_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise SubmissionSafetyError("outbox delivery state does not exist")
    return row


def _validate_delivery_lease(
    claim_owner: str,
    fencing_token: int,
    now: datetime,
    claim_expires_at: datetime,
) -> None:
    """Validate explicit publisher lease input without hidden defaults."""
    if (
        not claim_owner
        or fencing_token <= 0
        or now.tzinfo != UTC
        or claim_expires_at.tzinfo != UTC
        or claim_expires_at <= now
    ):
        raise SubmissionSafetyError("invalid outbox delivery lease")


def _outcome_value(row: RowMapping) -> SubmissionOutcome:
    """Convert a constrained database outcome into the domain enum."""
    value = _text_value(row, "outcome")
    if value not in _KNOWN_OUTCOMES:
        raise SubmissionSafetyError("database contains an unknown submission outcome")
    return SubmissionOutcome(value)


def _result(outcome: SubmissionOutcome, attempt_id: str) -> PersistedSubmissionResult:
    """Build a canonical replay-safe result."""
    return PersistedSubmissionResult(
        outcome=outcome,
        state=state_for_outcome(outcome),
        attempt_id=attempt_id,
        retry_forbidden=is_blind_retry_forbidden(outcome),
    )


def _response_evidence(response: VenueSubmitResponse) -> dict[str, object]:
    """Build redacted, deterministic response evidence."""
    return {
        "response_sequence": response.response_sequence,
        "outcome": response.outcome.value,
        "venue_order_id": response.venue_order_id,
        "fault_code": response.fault_code,
        "fills": [
            {
                "quantity": serialize_decimal(fill.quantity),
                "price": serialize_decimal(fill.price),
                "fee_amount": serialize_decimal(fill.fee_amount),
                "fee_asset": fill.fee_asset,
            }
            for fill in response.fills
        ],
    }


def _json_text(value: Mapping[str, object]) -> str:
    """Serialize a JSON object with stable ordering and no non-JSON values."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _iso(value: datetime) -> str:
    """Serialize a UTC timestamp in contract form."""
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _text_value(row: RowMapping, key: str) -> str:
    """Read a required text column without coercing unexpected values."""
    value = row[key]
    if not isinstance(value, str):
        raise SubmissionSafetyError(f"database column {key} is not text")
    return value


def _optional_text(row: RowMapping, key: str) -> str | None:
    """Read an optional text column."""
    value = row[key]
    if value is not None and not isinstance(value, str):
        raise SubmissionSafetyError(f"database column {key} is not optional text")
    return value


def _int_value(row: RowMapping, key: str) -> int:
    """Read an integer database column."""
    value = row[key]
    if not isinstance(value, int):
        raise SubmissionSafetyError(f"database column {key} is not integer")
    return value


def _optional_int(row: RowMapping, key: str) -> int | None:
    """Read an optional integer database column."""
    value = row[key]
    if value is not None and not isinstance(value, int):
        raise SubmissionSafetyError(f"database column {key} is not optional integer")
    return value


def _decimal_value(row: RowMapping, key: str) -> Decimal:
    """Read a Decimal database column without float conversion."""
    value = row[key]
    if not isinstance(value, Decimal):
        raise SubmissionSafetyError(f"database column {key} is not Decimal")
    return value


def _datetime_value(row: RowMapping, key: str) -> datetime:
    """Read a required UTC timestamp column."""
    value = row[key]
    if not isinstance(value, datetime) or value.tzinfo != UTC:
        raise SubmissionSafetyError(f"database column {key} is not UTC timestamp")
    return value


def _optional_datetime(row: RowMapping, key: str) -> datetime | None:
    """Read an optional UTC timestamp column."""
    value = row[key]
    if value is not None and (not isinstance(value, datetime) or value.tzinfo != UTC):
        raise SubmissionSafetyError(f"database column {key} is not optional UTC timestamp")
    return value
