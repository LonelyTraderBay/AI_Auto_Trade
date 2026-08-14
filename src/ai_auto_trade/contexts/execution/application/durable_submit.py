"""Application boundary for one durable, idempotent local submission."""

from __future__ import annotations

from dataclasses import dataclass

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    PersistedSubmissionResult,
    SubmissionBlocked,
    SubmissionOutcome,
    SubmissionSafetyContext,
    SubmissionSafetyError,
    VenueSubmitResponse,
    is_blind_retry_forbidden,
    state_for_outcome,
)
from ai_auto_trade.contexts.execution.ports.submission_port import (
    TradingSubmissionPersistencePort,
    VenueSubmitPort,
)
from ai_auto_trade.contexts.risk.domain.risk_gate import RiskDecision, RiskVerdict


@dataclass(frozen=True, slots=True)
class DurableSubmitResult:
    """Normalized outcome and canonical state after one adapter call."""

    outcome: SubmissionOutcome
    state: str
    attempt_id: str | None
    retry_forbidden: bool


class DurableSubmitBoundary:
    """Enforce risk approval and no-blind-retry semantics around a venue port."""

    def __init__(
        self,
        venue: VenueSubmitPort,
        persistence: TradingSubmissionPersistencePort | None = None,
    ) -> None:
        """Bind one deterministic venue port to the application boundary."""
        self._venue = venue
        self._persistence = persistence

    def submit(
        self,
        request: DurableSubmitRequest,
        risk_decision: RiskDecision,
        previous_outcome: SubmissionOutcome | None = None,
        safety: SubmissionSafetyContext | None = None,
    ) -> DurableSubmitResult:
        """Submit once after approval, blocking retry after unknown outcome."""
        _validate_preconditions(request, risk_decision, previous_outcome, safety)
        assert safety is not None
        if self._persistence is not None:
            prepared = self._persistence.prepare(request, risk_decision, safety)
            if prepared.replay is not None:
                return _from_persisted(prepared.replay)
            if not self._persistence.claim_for_submit(prepared, safety):
                return DurableSubmitResult(
                    outcome=SubmissionOutcome.UNKNOWN,
                    state="UNKNOWN",
                    attempt_id=prepared.attempt_id,
                    retry_forbidden=True,
                )
            response = self._venue.submit(request)
            return _from_persisted(self._persistence.record_outcome(prepared, response, safety))
        response = self._venue.submit(request)
        return _from_response(response)


def _validate_preconditions(
    request: DurableSubmitRequest,
    risk_decision: RiskDecision,
    previous_outcome: SubmissionOutcome | None,
    safety: SubmissionSafetyContext | None,
) -> None:
    """Validate risk freshness, quantity binding and internal execution authority."""
    if risk_decision.verdict is not RiskVerdict.APPROVE:
        raise SubmissionBlocked("risk decision is not APPROVE")
    if safety is None:
        raise SubmissionSafetyError("explicit lease and kill-switch context is required")
    if risk_decision.expires_at <= safety.now or risk_decision.decided_at > safety.now:
        raise SubmissionSafetyError("risk approval is expired or not yet effective")
    if risk_decision.reservation_id is None:
        raise SubmissionSafetyError("approved risk decision has no reservation")
    if risk_decision.approved_quantity != request.quantity:
        raise SubmissionSafetyError("risk approval quantity does not match submit quantity")
    if previous_outcome is not None and is_blind_retry_forbidden(previous_outcome):
        raise SubmissionBlocked("unknown outcome requires reconciliation before submit")


def _from_response(response: VenueSubmitResponse) -> DurableSubmitResult:
    """Normalize a direct venue response."""
    return DurableSubmitResult(
        outcome=response.outcome,
        state=state_for_outcome(response.outcome),
        attempt_id=response.attempt_id,
        retry_forbidden=is_blind_retry_forbidden(response.outcome),
    )


def _from_persisted(result: PersistedSubmissionResult) -> DurableSubmitResult:
    """Normalize an adapter result without exposing persistence details."""
    return DurableSubmitResult(
        outcome=result.outcome,
        state=result.state,
        attempt_id=result.attempt_id,
        retry_forbidden=result.retry_forbidden,
    )
