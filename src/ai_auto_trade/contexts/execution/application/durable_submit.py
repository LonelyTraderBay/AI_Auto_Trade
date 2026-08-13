"""Application boundary for one durable, idempotent local submission."""

from __future__ import annotations

from dataclasses import dataclass

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    SubmissionOutcome,
    is_blind_retry_forbidden,
    state_for_outcome,
)
from ai_auto_trade.contexts.execution.ports.submission_port import VenueSubmitPort
from ai_auto_trade.contexts.risk.domain.risk_gate import RiskDecision, RiskVerdict


class SubmissionBlocked(RuntimeError):
    """Raised when safety rules prevent a submission."""


@dataclass(frozen=True, slots=True)
class DurableSubmitResult:
    """Normalized outcome and canonical state after one adapter call."""

    outcome: SubmissionOutcome
    state: str
    attempt_id: str | None
    retry_forbidden: bool


class DurableSubmitBoundary:
    """Enforce risk approval and no-blind-retry semantics around a venue port."""

    def __init__(self, venue: VenueSubmitPort) -> None:
        """Bind one deterministic venue port to the application boundary."""
        self._venue = venue

    def submit(
        self,
        request: DurableSubmitRequest,
        risk_decision: RiskDecision,
        previous_outcome: SubmissionOutcome | None = None,
    ) -> DurableSubmitResult:
        """Submit once after approval, blocking retry after unknown outcome."""
        if risk_decision.verdict is not RiskVerdict.APPROVE:
            raise SubmissionBlocked("risk decision is not APPROVE")
        if previous_outcome is not None and is_blind_retry_forbidden(previous_outcome):
            raise SubmissionBlocked("unknown outcome requires reconciliation before submit")
        response = self._venue.submit(request)
        return DurableSubmitResult(
            outcome=response.outcome,
            state=state_for_outcome(response.outcome),
            attempt_id=response.attempt_id,
            retry_forbidden=is_blind_retry_forbidden(response.outcome),
        )
