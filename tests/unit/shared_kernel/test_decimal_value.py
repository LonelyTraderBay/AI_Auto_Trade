"""Unit tests for finite Decimal validation."""

from decimal import Decimal
from typing import cast

import pytest

from ai_auto_trade.shared_kernel.decimal_value import parse_decimal, serialize_decimal


def test_decimal_round_trip_preserves_base_ten_representation() -> None:
    """Decimal strings serialize without exponent notation."""
    value = parse_decimal("12.3400")

    assert value == Decimal("12.3400")
    assert serialize_decimal(value) == "12.3400"
    assert serialize_decimal(parse_decimal("1E+3")) == "1000"


@pytest.mark.parametrize("value", ["", " 1", "1 ", "NaN", "Infinity", "1.1234567890123456789"])
def test_decimal_rejects_invalid_or_over_scale_values(value: str) -> None:
    """Invalid, non-finite and over-scale strings are rejected."""
    with pytest.raises(ValueError):
        parse_decimal(value)


def test_decimal_rejects_binary_float_input() -> None:
    """Financial boundaries do not accept binary float values."""
    with pytest.raises(ValueError, match="string"):
        parse_decimal(1.2)


def test_decimal_rejects_non_integer_scale_limit() -> None:
    """Scale limits must be integer policy values."""
    with pytest.raises(ValueError, match="integer"):
        parse_decimal("1.2", max_scale=cast(int, 2.0))
