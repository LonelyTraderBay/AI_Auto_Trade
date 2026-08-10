"""Operations error envelope compatibility tests."""

from ai_auto_trade.shared_kernel.error import ErrorCode, ErrorEnvelope


def test_operations_error_uses_catalog_code() -> None:
    """Operations validation errors use the stable catalog code."""
    envelope = ErrorEnvelope(
        code=ErrorCode.VALIDATION_FAILED,
        message="Configuration is invalid",
        details={"field": "run_mode"},
        correlation_id="0190f000-0000-7000-8000-000000000020",
        retryable=False,
        remediation_hint="Correct the configuration and retry validation",
    )

    assert envelope.to_dict()["code"] == "VALIDATION_FAILED"
