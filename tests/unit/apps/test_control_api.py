"""Unit tests for the local-only control API skeleton."""

import asyncio
from collections.abc import Mapping
from typing import Protocol, cast

import httpx
from fastapi import FastAPI

from ai_auto_trade.apps.control_api.app import create_app

UUIDS = {
    "account": "0190f000-0000-7000-8000-000000000003",
    "instrument": "0190f000-0000-7000-8000-000000000008",
    "strategy": "0190f000-0000-7000-8000-000000000009",
    "deployment": "0190f000-0000-7000-8000-000000000001",
    "kill_switch": "0190f000-0000-7000-8000-00000000000a",
}
HTTP_OK = 200
HTTP_ACCEPTED = 202
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404


class _Response(Protocol):
    """Typed subset of the test client's response object."""

    status_code: int
    headers: Mapping[str, str]
    text: str

    def json(self) -> object:
        """Return a decoded response payload."""
        ...


class _Client(Protocol):
    """Typed subset of the test client used by these tests."""

    def get(self, url: str) -> _Response:
        """Issue a GET request."""
        ...

    def post(self, url: str, *, headers: Mapping[str, str], json: object) -> _Response:
        """Issue a JSON POST request."""
        ...


async def _send(
    app: FastAPI,
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    json: object | None = None,
) -> _Response:
    """Send one request through the ASGI app without a deprecated test client."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.request(method, url, headers=headers, json=json)
    return cast(_Response, response)


class _ClientAdapter:
    """Synchronous facade over HTTPX's ASGI transport for plain pytest tests."""

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    def get(self, url: str) -> _Response:
        """Issue a GET request."""
        return asyncio.run(_send(self._app, "GET", url))

    def post(self, url: str, *, headers: Mapping[str, str], json: object) -> _Response:
        """Issue a JSON POST request."""
        return asyncio.run(_send(self._app, "POST", url, headers=headers, json=json))


def test_health_readiness_and_runtime_are_sanitized() -> None:
    """System read routes return contract-shaped local safe state."""
    client = cast(_Client, _ClientAdapter(create_app()))

    health = client.get("/health")
    readiness = client.get("/readiness")
    runtime = client.get("/runtime")

    assert health.status_code == HTTP_OK
    assert cast(dict[str, object], health.json())["status"] == "OK"
    assert readiness.status_code == HTTP_OK
    readiness_body = cast(dict[str, object], readiness.json())
    assert readiness_body == {
        "ready": True,
        "safe_state": "READY",
        "blocking_reasons": [],
        "observed_at": readiness_body["observed_at"],
    }
    assert runtime.status_code == HTTP_OK
    runtime_body = cast(dict[str, object], runtime.json())
    assert runtime_body["environment"] == "local"
    assert runtime_body["execution_target"] == "INTERNAL_SIMULATOR"
    assert "secret" not in runtime.text.lower()


def test_command_stub_returns_accepted_and_location() -> None:
    """A valid command request creates only an in-memory accepted projection."""
    client = cast(_Client, _ClientAdapter(create_app()))
    payload = {
        "reason": "Validate the local reconciliation projection",
        "payload": {
            "scope": {
                "scope_type": "ACCOUNT",
                "account_id": UUIDS["account"],
                "instrument_id": None,
                "strategy_instance_id": None,
            },
            "evidence_cutoff_at": "2026-08-11T00:30:47Z",
        },
    }

    response = client.post(
        "/commands/reconciliations",
        headers={"Idempotency-Key": "local-reconcile-01"},
        json=payload,
    )

    assert response.status_code == HTTP_ACCEPTED
    body = cast(dict[str, object], response.json())
    assert body["status"] == "ACCEPTED"
    assert response.headers["Location"] == body["location"]
    status = client.get(cast(str, body["location"]))
    assert status.status_code == HTTP_OK
    assert cast(dict[str, object], status.json())["status"] == "ACCEPTED"


def test_validation_failure_uses_error_envelope_without_input_echo() -> None:
    """Framework validation errors do not expose raw input or stack traces."""
    client = cast(_Client, _ClientAdapter(create_app()))

    response = client.post(
        "/commands/reconciliations",
        headers={"Idempotency-Key": "local-reconcile-02"},
        json={"reason": "contains token material", "payload": {}},
    )

    assert response.status_code == HTTP_BAD_REQUEST
    body = cast(dict[str, object], response.json())
    assert body["code"] == "VALIDATION_FAILED"
    assert body["details"] == {}
    assert "token material" not in response.text


def test_unknown_route_uses_error_envelope() -> None:
    """Framework 404 responses use the stable error contract."""
    client = cast(_Client, _ClientAdapter(create_app()))

    response = client.get("/not-a-route")

    assert response.status_code == HTTP_NOT_FOUND
    body = cast(dict[str, object], response.json())
    assert body["code"] == "RESOURCE_NOT_FOUND"
