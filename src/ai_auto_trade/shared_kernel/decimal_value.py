"""Finite Decimal value validation for financial domain boundaries."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

MAX_FINANCIAL_SCALE = 18


def parse_decimal(value: object, *, max_scale: int = MAX_FINANCIAL_SCALE) -> Decimal:
    """Parse a finite decimal string without accepting binary floats.

    Args:
        value: Decimal string in canonical JSON/API form.
        max_scale: Maximum number of fractional digits.

    Returns:
        A finite Decimal value.

    Raises:
        ValueError: If the value is malformed, non-finite or over scale.
    """
    _validate_scale_limit(max_scale)
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("value must be a non-empty decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("value must be a valid decimal string") from exc
    _validate_decimal(parsed, max_scale)
    return parsed


def serialize_decimal(value: Decimal, *, max_scale: int = MAX_FINANCIAL_SCALE) -> str:
    """Serialize a finite Decimal without exponent notation.

    Args:
        value: Decimal value to serialize.
        max_scale: Maximum number of fractional digits.

    Returns:
        A base-10 string suitable for JSON/API transport.

    Raises:
        ValueError: If the value is non-finite or over scale.
    """
    _validate_scale_limit(max_scale)
    _validate_decimal(value, max_scale)
    return format(value, "f")


def _validate_scale_limit(max_scale: int) -> None:
    """Validate a caller-provided scale limit."""
    if type(max_scale) is not int or not 0 <= max_scale <= MAX_FINANCIAL_SCALE:
        raise ValueError("max_scale must be an integer from 0 to 18")


def _validate_decimal(value: Decimal, max_scale: int) -> None:
    """Validate finiteness and fractional scale."""
    if not value.is_finite():
        raise ValueError("value must be finite")
    exponent = value.as_tuple().exponent
    scale = -exponent if isinstance(exponent, int) and exponent < 0 else 0
    if scale > max_scale:
        raise ValueError("value exceeds maximum decimal scale")
