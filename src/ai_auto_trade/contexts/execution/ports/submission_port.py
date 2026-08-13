"""Ports for execution submission adapters."""

from __future__ import annotations

from typing import Protocol

from ai_auto_trade.contexts.execution.domain.submit_contract import (
    DurableSubmitRequest,
    VenueSubmitResponse,
)


class VenueSubmitPort(Protocol):
    """Minimal port required by the durable submit application service."""

    def submit(self, request: DurableSubmitRequest) -> VenueSubmitResponse:
        """Submit one already-approved request to a deterministic adapter."""
        ...
