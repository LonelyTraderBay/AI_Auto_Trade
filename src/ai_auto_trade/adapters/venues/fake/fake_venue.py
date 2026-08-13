"""Deterministic, network-free fake venue for Task 1.3."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from decimal import Decimal

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    SubmissionOutcome,
    VenueFill,
    VenueSubmitResponse,
)

FakeVenueFill = VenueFill
FakeVenueResponse = VenueSubmitResponse


@dataclass(frozen=True, slots=True)
class FakeVenueScenario:
    """Pinned response sequence for one deterministic scenario."""

    scenario_id: str
    revision: int
    responses: tuple[FakeVenueResponse, ...]

    def __post_init__(self) -> None:
        """Reject empty or unversioned scenario definitions."""
        if not self.scenario_id or self.revision <= 0 or not self.responses:
            raise ValueError("scenario_id, positive revision and responses are required")


class FakeVenue:
    """In-process fake venue with idempotent client-order behavior."""

    def __init__(self, scenarios: Mapping[str, FakeVenueScenario]) -> None:
        """Create a simulator with an immutable scenario catalog."""
        self._scenarios = dict(scenarios)
        self._first_responses: dict[str, tuple[str, FakeVenueResponse]] = {}
        self._cursors: dict[str, int] = {}

    def submit(self, request: DurableSubmitRequest) -> FakeVenueResponse:
        """Return one deterministic response and never duplicate a side effect."""
        previous = self._first_responses.get(request.client_order_id)
        if previous is not None:
            if previous[0] != request.request_hash():
                return FakeVenueResponse(
                    outcome=SubmissionOutcome.REJECTED,
                    response_sequence=previous[1].response_sequence,
                    fault_code="REQUEST_HASH_MISMATCH",
                    attempt_id=request.attempt_id,
                )
            return previous[1]
        scenario = self._scenarios.get(request.scenario_id)
        if scenario is None or scenario.revision != request.scenario_revision:
            return FakeVenueResponse(
                outcome=SubmissionOutcome.REJECTED,
                response_sequence=1,
                fault_code="SCENARIO_NOT_FOUND",
                attempt_id=request.attempt_id,
            )
        response = replace(scenario.responses[0], attempt_id=request.attempt_id)
        self._first_responses[request.client_order_id] = (request.request_hash(), response)
        self._cursors[request.client_order_id] = 0
        return response

    def advance(self, request: DurableSubmitRequest) -> FakeVenueResponse:
        """Advance a scripted scenario without resubmitting the order."""
        scenario = self._scenarios.get(request.scenario_id)
        if scenario is None or scenario.revision != request.scenario_revision:
            return FakeVenueResponse(
                outcome=SubmissionOutcome.REJECTED,
                response_sequence=1,
                fault_code="SCENARIO_NOT_FOUND",
                attempt_id=request.attempt_id,
            )
        cursor = self._cursors.get(request.client_order_id, 0) + 1
        self._cursors[request.client_order_id] = min(cursor, len(scenario.responses) - 1)
        response = scenario.responses[self._cursors[request.client_order_id]]
        return replace(response, attempt_id=request.attempt_id)

    def submission_count(self, client_order_id: str) -> int:
        """Return one when a client order produced a side effect, otherwise zero."""
        return int(client_order_id in self._first_responses)


def default_scenarios() -> dict[str, FakeVenueScenario]:
    """Build the approved deterministic scenario catalog."""
    return {
        "immediate_accept": FakeVenueScenario(
            "immediate_accept", 1, (FakeVenueResponse(SubmissionOutcome.ACCEPTED, 1, "fake-ack-1"),)
        ),
        "explicit_reject": FakeVenueScenario(
            "explicit_reject",
            1,
            (FakeVenueResponse(SubmissionOutcome.REJECTED, 1, fault_code="VENUE_REJECTED"),),
        ),
        "partial_then_fill": FakeVenueScenario(
            "partial_then_fill",
            1,
            (
                FakeVenueResponse(
                    SubmissionOutcome.PARTIAL_FILL,
                    1,
                    "fake-order-partial",
                    (FakeVenueFill(Decimal("0.5"), Decimal("10")),),
                ),
                FakeVenueResponse(
                    SubmissionOutcome.FILLED,
                    2,
                    "fake-order-partial",
                    (FakeVenueFill(Decimal("0.5"), Decimal("10")),),
                ),
            ),
        ),
        "timeout": FakeVenueScenario(
            "timeout", 1, (FakeVenueResponse(SubmissionOutcome.TIMEOUT, 1, fault_code="TIMEOUT"),)
        ),
        "unknown": FakeVenueScenario(
            "unknown", 1, (FakeVenueResponse(SubmissionOutcome.UNKNOWN, 1, fault_code="AMBIGUOUS"),)
        ),
    }
