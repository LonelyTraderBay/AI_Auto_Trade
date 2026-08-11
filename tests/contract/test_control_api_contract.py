"""Contract checks for the local control API route skeleton."""

import asyncio
from collections.abc import Mapping
from typing import Protocol, cast

import httpx
from fastapi import FastAPI

from ai_auto_trade.apps.control_api.app import create_app

HTTP_ACCEPTED = 202


class _Response(Protocol):
    """Typed subset of the test client's response object."""

    status_code: int
    headers: Mapping[str, str]

    def json(self) -> object:
        """Return a decoded response payload."""
        ...


class _Client(Protocol):
    """Typed subset of the test client used by this contract test."""

    def post(self, url: str, *, headers: Mapping[str, str], json: object) -> _Response:
        """Issue a JSON POST request."""
        ...


async def _send(app: FastAPI, url: str, *, headers: Mapping[str, str], json: object) -> _Response:
    """Send one request through the ASGI app without a deprecated test client."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(url, headers=headers, json=json)
    return cast(_Response, response)


class _ClientAdapter:
    """Synchronous facade over HTTPX's ASGI transport for plain pytest tests."""

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    def post(self, url: str, *, headers: Mapping[str, str], json: object) -> _Response:
        """Issue a JSON POST request."""
        return asyncio.run(_send(self._app, url, headers=headers, json=json))


class _Route(Protocol):
    """Typed subset of a Starlette route."""

    path: str


def test_required_control_routes_exist() -> None:
    """The skeleton exposes every Phase 0 system and command intake route."""
    routes = cast(list[_Route], create_app().routes)
    paths = {route.path for route in routes}
    assert {
        "/health",
        "/readiness",
        "/runtime",
        "/commands/reconciliations",
        "/commands/strategy-activations",
        "/commands/strategy-stops",
        "/commands/kill-switch-activations",
        "/commands/kill-switch-releases",
        "/commands/backtests",
        "/commands/{command_id}",
    }.issubset(paths)


def test_command_acceptance_has_contract_headers_and_fields() -> None:
    """The accepted response is 202 and carries a relative Location."""
    client = cast(_Client, _ClientAdapter(create_app()))
    payload = {
        "reason": "Start deterministic local backtest",
        "payload": {"dataset_version": "fixture-v1", "strategy_version": "baseline-v1", "seed": 7},
    }

    response = client.post(
        "/commands/backtests",
        headers={"Idempotency-Key": "local-backtest-01"},
        json=payload,
    )

    assert response.status_code == HTTP_ACCEPTED
    assert response.headers["Location"].startswith("/commands/")
    body = cast(dict[str, object], response.json())
    assert body["status"] == "ACCEPTED"
