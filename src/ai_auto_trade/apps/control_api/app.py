"""Local-only FastAPI control-plane skeleton.

This module intentionally contains no authentication implementation, database
client, venue adapter, LLM provider, or command execution path. Every command
route creates an in-memory ``ACCEPTED`` projection only.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from ai_auto_trade.shared_kernel.error import ErrorCode
from ai_auto_trade.shared_kernel.error import ErrorEnvelope as SharedErrorEnvelope

UUID_V7_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
TIMESTAMP_PATTERN = r"Z$"
MANIFEST_HASH = "sha256:" + "0" * 64
DEPLOYMENT_ID = "0190f000-0000-7000-8000-000000000001"
UUID_V7_VERSION = 7
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405

UuidV7 = Annotated[str, Field(pattern=UUID_V7_PATTERN)]
UtcTimestamp = Annotated[str, Field(pattern=TIMESTAMP_PATTERN)]
ScopeType = Literal["GLOBAL", "ACCOUNT", "INSTRUMENT", "STRATEGY"]
CommandType = Literal[
    "REQUEST_RECONCILIATION",
    "ACTIVATE_STRATEGY",
    "STOP_STRATEGY",
    "ACTIVATE_KILL_SWITCH",
    "RELEASE_KILL_SWITCH",
    "START_BACKTEST",
]


class _StrictModel(BaseModel):
    """Base model that rejects undocumented input fields."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(_StrictModel):
    """Liveness response without runtime or credential state."""

    status: Literal["OK", "DEGRADED"]
    observed_at: UtcTimestamp


class ReadinessResponse(_StrictModel):
    """Safe readiness projection for the local simulator mode."""

    ready: bool
    safe_state: Literal["READY", "BLOCKED", "FROZEN", "KILL_SWITCH_ACTIVE"]
    observed_at: UtcTimestamp
    blocking_reasons: list[str]


class RuntimeResponse(_StrictModel):
    """Sanitized runtime identity with no secret or venue state."""

    deployment_id: UuidV7
    environment: Literal["local", "ci", "paper", "testnet", "canary", "live"]
    run_mode: Literal[
        "BACKTEST",
        "REPLAY",
        "SHADOW",
        "PAPER_SIMULATOR",
        "TESTNET",
        "CANARY",
        "FULL_LIVE",
    ]
    execution_target: Literal["INTERNAL_SIMULATOR", "DISABLED", "VENUE_TESTNET", "VENUE_LIVE"]
    safe_state: Literal["READY", "BLOCKED", "FROZEN", "KILL_SWITCH_ACTIVE"]
    manifest_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    observed_at: UtcTimestamp


class CommandAcceptedResponse(_StrictModel):
    """Accepted command projection; acceptance is not execution."""

    command_id: UuidV7
    status: Literal["ACCEPTED"]
    location: str
    correlation_id: UuidV7
    accepted_at: UtcTimestamp


class CommandStatusResponse(_StrictModel):
    """In-memory command status projection."""

    command_id: UuidV7
    command_type: CommandType
    status: Literal["ACCEPTED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]
    requested_at: UtcTimestamp
    completed_at: UtcTimestamp | None
    correlation_id: UuidV7
    result_ref: str | None
    error: dict[str, object] | None


class ErrorEnvelope(_StrictModel):
    """OpenAPI-compatible safe error response model."""

    code: ErrorCode
    message: str = Field(min_length=1, max_length=1024)
    details: dict[str, object]
    correlation_id: UuidV7
    retryable: bool
    remediation_hint: str = Field(min_length=1, max_length=1024)


class ControlScope(_StrictModel):
    """Contract scope without accepting an actor identity claim."""

    scope_type: ScopeType
    account_id: UuidV7 | None
    instrument_id: UuidV7 | None
    strategy_instance_id: UuidV7 | None


class _CommandRequest(_StrictModel):
    """Shared command reason validation and secret-like input rejection."""

    reason: str = Field(min_length=1, max_length=1024)

    @field_validator("reason")
    @classmethod
    def reject_secret_like_reason(cls, value: str) -> str:
        """Reject credential-like text before it reaches an audit boundary."""
        fragments = ("secret", "password", "token", "api_key", "apikey")
        if any(fragment in value.lower() for fragment in fragments):
            raise ValueError("reason contains secret-like material")
        return value


class ReconciliationPayload(_StrictModel):
    """Reconciliation request payload shape."""

    scope: ControlScope
    evidence_cutoff_at: UtcTimestamp


class ReconciliationRequest(_CommandRequest):
    """Request model for the reconciliation stub."""

    payload: ReconciliationPayload


class StrategyCommandPayload(_StrictModel):
    """Strategy command payload shape."""

    strategy_instance_id: UuidV7
    deployment_id: UuidV7


class StrategyCommandRequest(_CommandRequest):
    """Request model shared by strategy activate/stop stubs."""

    payload: StrategyCommandPayload


class KillSwitchActivationPayload(_StrictModel):
    """Kill-switch activation payload shape."""

    scope: ControlScope
    activation_reason_code: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")


class KillSwitchActivationRequest(_CommandRequest):
    """Request model for the kill-switch activation stub."""

    payload: KillSwitchActivationPayload


class KillSwitchReleasePayload(_StrictModel):
    """Kill-switch release payload shape."""

    kill_switch_id: UuidV7
    scope: ControlScope
    verification_evidence_ref: str = Field(min_length=1, max_length=2048)


class KillSwitchReleaseRequest(_CommandRequest):
    """Request model for the kill-switch release stub."""

    payload: KillSwitchReleasePayload


class BacktestPayload(_StrictModel):
    """Backtest request payload shape."""

    dataset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    seed: int = Field(ge=0)


class BacktestRequest(_CommandRequest):
    """Request model for the deterministic backtest stub."""

    payload: BacktestPayload


class _ControlApiError(Exception):
    """Safe HTTP error carrying an already-redacted error envelope."""

    def __init__(self, status_code: int, envelope: SharedErrorEnvelope) -> None:
        super().__init__(envelope.code.value)
        self.status_code = status_code
        self.envelope = envelope


class _CommandProjection:
    """Minimal in-memory projection used only by the Phase 0 skeleton."""

    def __init__(self) -> None:
        self._records: dict[str, CommandStatusResponse] = {}

    def accept(self, command_type: CommandType, correlation_id: str) -> CommandAcceptedResponse:
        """Record acceptance without executing or persisting the command."""
        command_id = _new_uuid_v7()
        accepted_at = _utc_now()
        self._records[command_id] = CommandStatusResponse(
            command_id=command_id,
            command_type=command_type,
            status="ACCEPTED",
            requested_at=accepted_at,
            completed_at=None,
            correlation_id=correlation_id,
            result_ref=None,
            error=None,
        )
        return CommandAcceptedResponse(
            command_id=command_id,
            status="ACCEPTED",
            location=f"/commands/{command_id}",
            correlation_id=correlation_id,
            accepted_at=accepted_at,
        )

    def get(self, command_id: str) -> CommandStatusResponse:
        """Read one in-memory projection or raise a safe not-found error."""
        record = self._records.get(command_id)
        if record is None:
            raise _ControlApiError(
                HTTP_NOT_FOUND,
                _error_envelope(
                    ErrorCode.COMMAND_NOT_FOUND,
                    "Command is not available in the local projection",
                    "Review the command identifier and local process state",
                    correlation_id=_new_uuid_v7(),
                ),
            )
        return record


class _CommandHeaders:
    """Validated headers shared by ordinary command intake routes."""

    def __init__(self, idempotency_key: str, correlation_id: str | None) -> None:
        self.idempotency_key = idempotency_key
        self.correlation_id = correlation_id


class _StrategyHeaders(_CommandHeaders):
    """Command headers plus optimistic-concurrency precondition."""

    def __init__(self, idempotency_key: str, correlation_id: str | None, if_match: str) -> None:
        super().__init__(idempotency_key, correlation_id)
        self.if_match = if_match


class _ReleaseHeaders(_StrategyHeaders):
    """Kill-switch release headers including the protected proof placeholder."""

    def __init__(
        self,
        idempotency_key: str,
        correlation_id: str | None,
        if_match: str,
        reauthentication_proof: str,
    ) -> None:
        super().__init__(idempotency_key, correlation_id, if_match)
        self.reauthentication_proof = reauthentication_proof


def _command_headers(
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ],
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
) -> _CommandHeaders:
    """Parse ordinary command headers without implementing actor auth."""
    return _CommandHeaders(idempotency_key, correlation_id)


def _strategy_headers(
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ],
    if_match: Annotated[str, Header(alias="If-Match", min_length=1, max_length=256)],
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
) -> _StrategyHeaders:
    """Parse strategy command headers without implementing actor auth."""
    return _StrategyHeaders(idempotency_key, correlation_id, if_match)


def _release_headers(
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ],
    if_match: Annotated[str, Header(alias="If-Match", min_length=1, max_length=256)],
    reauthentication_proof: Annotated[
        str, Header(alias="X-Reauthentication-Proof", min_length=1, max_length=4096)
    ],
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
) -> _ReleaseHeaders:
    """Parse release headers; proof is not logged, persisted or evaluated here."""
    return _ReleaseHeaders(idempotency_key, correlation_id, if_match, reauthentication_proof)


def create_app() -> FastAPI:
    """Create the local-only control API application."""
    app = FastAPI(
        title="AI Auto Trade Control Plane API",
        version="0.1.0-local",
        description=(
            "Phase 0 local-only skeleton. Authentication is a no-op stub; "
            "no route executes commands or contacts external services."
        ),
        responses={
            400: {"model": ErrorEnvelope},
            401: {"model": ErrorEnvelope},
            403: {"model": ErrorEnvelope},
            404: {"model": ErrorEnvelope},
            405: {"model": ErrorEnvelope},
            409: {"model": ErrorEnvelope},
            412: {"model": ErrorEnvelope},
            423: {"model": ErrorEnvelope},
            500: {"model": ErrorEnvelope},
            503: {"model": ErrorEnvelope},
        },
    )
    projection = _CommandProjection()
    _register_error_handlers(app)
    _register_system_routes(app)
    _register_command_routes(app, projection)
    return app


def _register_error_handlers(app: FastAPI) -> None:
    """Register stable error-envelope handlers at the composition root."""

    async def control_api_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a safe error envelope for known API errors."""
        del request
        if not isinstance(exc, _ControlApiError):
            envelope = _error_envelope(
                ErrorCode.INTERNAL_ERROR,
                "Internal control API error",
                "Use the correlation identifier and review local logs",
                correlation_id=_new_uuid_v7(),
            )
            return JSONResponse(status_code=500, content=envelope.to_dict())
        return JSONResponse(status_code=exc.status_code, content=exc.envelope.to_dict())

    async def request_validation_handler(request: Request, exc: Exception) -> JSONResponse:
        """Map framework validation failures to the stable error contract."""
        del request, exc
        envelope = _error_envelope(
            ErrorCode.VALIDATION_FAILED,
            "Request validation failed",
            "Correct the request fields and try again",
            correlation_id=_new_uuid_v7(),
        )
        return JSONResponse(status_code=400, content=envelope.to_dict())

    app.add_exception_handler(_ControlApiError, control_api_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)

    async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Map framework HTTP errors to a redacted stable envelope."""
        del request
        if not isinstance(exc, StarletteHTTPException):
            envelope = _error_envelope(
                ErrorCode.INTERNAL_ERROR,
                "Internal control API error",
                "Use the correlation identifier and review local logs",
                correlation_id=_new_uuid_v7(),
            )
            return JSONResponse(status_code=500, content=envelope.to_dict())
        code_by_status = {
            HTTP_BAD_REQUEST: ErrorCode.VALIDATION_FAILED,
            HTTP_METHOD_NOT_ALLOWED: ErrorCode.VALIDATION_FAILED,
            HTTP_NOT_FOUND: ErrorCode.RESOURCE_NOT_FOUND,
        }
        envelope = _error_envelope(
            code_by_status.get(exc.status_code, ErrorCode.INTERNAL_ERROR),
            "Control API request could not be completed",
            "Review the route and request, then try again",
            correlation_id=_new_uuid_v7(),
        )
        return JSONResponse(status_code=exc.status_code, content=envelope.to_dict())

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)


def _register_system_routes(app: FastAPI) -> None:
    """Register health, readiness and sanitized runtime routes."""

    async def health() -> HealthResponse:
        """Return liveness without exposing runtime or credential state."""
        return HealthResponse(status="OK", observed_at=_utc_now())

    async def readiness() -> ReadinessResponse:
        """Return safe local simulator readiness."""
        return ReadinessResponse(
            ready=True,
            safe_state="READY",
            observed_at=_utc_now(),
            blocking_reasons=[],
        )

    async def runtime(
        correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
    ) -> RuntimeResponse:
        """Return sanitized local runtime identity; auth is intentionally a stub."""
        _resolve_correlation_id(correlation_id)
        return RuntimeResponse(
            deployment_id=DEPLOYMENT_ID,
            environment="local",
            run_mode="BACKTEST",
            execution_target="INTERNAL_SIMULATOR",
            safe_state="READY",
            manifest_hash=MANIFEST_HASH,
            observed_at=_utc_now(),
        )

    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    app.add_api_route("/readiness", readiness, methods=["GET"], response_model=ReadinessResponse)
    app.add_api_route("/runtime", runtime, methods=["GET"], response_model=RuntimeResponse)


def _register_command_routes(app: FastAPI, projection: _CommandProjection) -> None:
    """Register command status and no-execution command intake routes."""

    async def command_status(command_id: str) -> CommandStatusResponse:
        """Read an accepted command from the in-memory projection."""
        if not _is_uuid_v7(command_id):
            raise _ControlApiError(
                HTTP_BAD_REQUEST,
                _error_envelope(
                    ErrorCode.VALIDATION_FAILED,
                    "Command identifier is invalid",
                    "Provide a canonical UUIDv7 command identifier",
                    correlation_id=_new_uuid_v7(),
                ),
            )
        return projection.get(command_id)

    async def request_reconciliation(
        request: ReconciliationRequest,
        response: Response,
        headers: Annotated[_CommandHeaders, Depends(_command_headers)],
    ) -> CommandAcceptedResponse:
        """Accept reconciliation intent without executing it."""
        del request
        return _accept(projection, response, "REQUEST_RECONCILIATION", headers.correlation_id)

    async def activate_strategy(
        request: StrategyCommandRequest,
        response: Response,
        headers: Annotated[_StrategyHeaders, Depends(_strategy_headers)],
    ) -> CommandAcceptedResponse:
        """Accept strategy activation intent without executing it."""
        del request
        return _accept(projection, response, "ACTIVATE_STRATEGY", headers.correlation_id)

    async def stop_strategy(
        request: StrategyCommandRequest,
        response: Response,
        headers: Annotated[_StrategyHeaders, Depends(_strategy_headers)],
    ) -> CommandAcceptedResponse:
        """Accept strategy stop intent without executing it."""
        del request
        return _accept(projection, response, "STOP_STRATEGY", headers.correlation_id)

    async def activate_kill_switch(
        request: KillSwitchActivationRequest,
        response: Response,
        headers: Annotated[_CommandHeaders, Depends(_command_headers)],
    ) -> CommandAcceptedResponse:
        """Accept kill-switch activation intent without executing it."""
        del request
        return _accept(projection, response, "ACTIVATE_KILL_SWITCH", headers.correlation_id)

    async def release_kill_switch(
        request: KillSwitchReleaseRequest,
        response: Response,
        headers: Annotated[_ReleaseHeaders, Depends(_release_headers)],
    ) -> CommandAcceptedResponse:
        """Accept release intent without implementing authentication or release."""
        del request
        return _accept(projection, response, "RELEASE_KILL_SWITCH", headers.correlation_id)

    async def start_backtest(
        request: BacktestRequest,
        response: Response,
        headers: Annotated[_CommandHeaders, Depends(_command_headers)],
    ) -> CommandAcceptedResponse:
        """Accept backtest intent without starting a worker."""
        del request
        return _accept(projection, response, "START_BACKTEST", headers.correlation_id)

    app.add_api_route(
        "/commands/{command_id}",
        command_status,
        methods=["GET"],
        response_model=CommandStatusResponse,
    )
    command_routes: tuple[tuple[str, Callable[..., object]], ...] = (
        ("/commands/reconciliations", request_reconciliation),
        ("/commands/strategy-activations", activate_strategy),
        ("/commands/strategy-stops", stop_strategy),
        ("/commands/kill-switch-activations", activate_kill_switch),
        ("/commands/kill-switch-releases", release_kill_switch),
        ("/commands/backtests", start_backtest),
    )
    for path, endpoint in command_routes:
        app.add_api_route(
            path,
            endpoint,
            methods=["POST"],
            status_code=202,
            response_model=CommandAcceptedResponse,
        )


def _accept(
    projection: _CommandProjection,
    response: Response,
    command_type: CommandType,
    correlation_id: str | None,
) -> CommandAcceptedResponse:
    """Validate correlation ID and create a safe accepted projection."""
    accepted = projection.accept(command_type, _resolve_correlation_id(correlation_id))
    response.headers["Location"] = accepted.location
    return accepted


def _error_envelope(
    code: ErrorCode,
    message: str,
    remediation_hint: str,
    correlation_id: str,
) -> SharedErrorEnvelope:
    """Build a safe envelope without raw request or exception data."""
    return SharedErrorEnvelope(
        code=code,
        message=message,
        details={},
        correlation_id=correlation_id,
        retryable=False,
        remediation_hint=remediation_hint,
    )


def _resolve_correlation_id(value: str | None) -> str:
    """Use a supplied UUIDv7 or generate one for the local request."""
    if value is None:
        return _new_uuid_v7()
    if not _is_uuid_v7(value):
        raise _ControlApiError(
            HTTP_BAD_REQUEST,
            _error_envelope(
                ErrorCode.VALIDATION_FAILED,
                "Correlation identifier is invalid",
                "Provide a canonical UUIDv7 correlation identifier",
                correlation_id=_new_uuid_v7(),
            ),
        )
    return value


def _is_uuid_v7(value: str) -> bool:
    """Validate canonical UUIDv7 text without a third-party dependency."""
    try:
        parsed = UUID(value)
    except ValueError:
        return False
    return parsed.version == UUID_V7_VERSION and str(parsed) == value


def _new_uuid_v7() -> str:
    """Create a UUIDv7-shaped identifier for local command correlation."""
    timestamp_ms = int(datetime.now(UTC).timestamp() * 1000) & ((1 << 48) - 1)
    random_bits = uuid4().int & ((1 << 80) - 1)
    value = (timestamp_ms << 80) | random_bits
    value = (value & ~(0xF << 76)) | (7 << 76)
    value = (value & ~(0x3 << 62)) | (0x2 << 62)
    return str(UUID(int=value))


def _utc_now() -> str:
    """Return canonical UTC timestamp text."""
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


app = create_app()
