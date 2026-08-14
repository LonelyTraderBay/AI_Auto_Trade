"""Ports for execution submission adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    PersistedSubmissionResult,
    SubmissionSafetyContext,
    VenueSubmitResponse,
)
from ai_auto_trade.contexts.risk.domain.risk_gate import RiskDecision


class VenueSubmitPort(Protocol):
    """Minimal port required by the durable submit application service."""

    def submit(self, request: DurableSubmitRequest) -> VenueSubmitResponse:
        """Submit one already-approved request to a deterministic adapter."""
        ...


@dataclass(frozen=True, slots=True)
class PreparedSubmission:
    """Committed pre-submit facts or a canonical replay result."""

    request: DurableSubmitRequest
    order_id: str
    attempt_id: str
    request_hash: str
    scope_key: str
    replay: PersistedSubmissionResult | None = None


class TradingSubmissionPersistencePort(Protocol):
    """Port for the serializable pre-submit and recovery transactions."""

    def prepare(
        self,
        request: DurableSubmitRequest,
        risk_decision: RiskDecision,
        safety: SubmissionSafetyContext,
    ) -> PreparedSubmission:
        """Persist approved facts before any venue call, or return a replay."""
        ...

    def claim_for_submit(
        self,
        prepared: PreparedSubmission,
        safety: SubmissionSafetyContext,
    ) -> bool:
        """Advance one queued attempt under its lease before the venue call."""
        ...

    def record_outcome(
        self,
        prepared: PreparedSubmission,
        response: VenueSubmitResponse,
        safety: SubmissionSafetyContext,
    ) -> PersistedSubmissionResult:
        """Persist one response with CAS/dedupe semantics."""
        ...
