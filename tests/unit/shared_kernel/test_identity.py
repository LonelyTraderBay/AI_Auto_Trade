"""Unit tests for UUIDv7 identity primitives."""

from typing import cast
from uuid import RFC_4122

import pytest

from ai_auto_trade.shared_kernel.identity import UUID_V7_VERSION, generate_uuid7, parse_uuid7

TEST_TIMESTAMP_MILLISECONDS = 1_700_000_000_123


def test_generate_uuid7_has_expected_version_variant_and_timestamp() -> None:
    """Generated UUIDs contain the requested millisecond timestamp."""
    value = generate_uuid7(TEST_TIMESTAMP_MILLISECONDS)

    assert value.version == UUID_V7_VERSION
    assert value.variant == RFC_4122
    assert (value.int >> 80) == TEST_TIMESTAMP_MILLISECONDS
    assert parse_uuid7(str(value)) == value


def test_parse_uuid7_rejects_noncanonical_or_wrong_version() -> None:
    """UUID parsing rejects uppercase, UUID4 and malformed values."""
    with pytest.raises(ValueError, match="canonical"):
        parse_uuid7("0190f000-0000-7000-8000-000000000010".upper())
    with pytest.raises(ValueError, match="UUIDv7"):
        parse_uuid7("0190f000-0000-4000-8000-000000000010")
    with pytest.raises(ValueError, match="canonical"):
        parse_uuid7("not-a-uuid")


def test_generate_uuid7_rejects_out_of_range_timestamp() -> None:
    """UUIDv7 timestamp field rejects values outside 48 bits."""
    with pytest.raises(ValueError, match="range"):
        generate_uuid7(1 << 48)


def test_generate_uuid7_rejects_non_integer_timestamp() -> None:
    """UUIDv7 timestamp override rejects non-integer values."""
    with pytest.raises(ValueError, match="integer"):
        generate_uuid7(cast(int, "1700000000123"))
