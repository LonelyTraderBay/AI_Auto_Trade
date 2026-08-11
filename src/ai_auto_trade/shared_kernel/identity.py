"""UUIDv7 identity primitives for internal identifiers."""

from __future__ import annotations

import os
import time
from uuid import UUID

UUID_V7_VERSION = 7
_MAX_TIMESTAMP_MILLISECONDS = (1 << 48) - 1
_MAX_RANDOM_A = (1 << 12) - 1
_MAX_RANDOM_B = (1 << 62) - 1


def generate_uuid7(timestamp_milliseconds: int | None = None) -> UUID:
    """Generate an RFC 9562 UUIDv7 using a Unix millisecond timestamp.

    Args:
        timestamp_milliseconds: Optional timestamp override for deterministic tests.

    Returns:
        A UUIDv7 value with RFC 4122 variant bits.

    Raises:
        ValueError: If the timestamp cannot be represented by UUIDv7.
    """
    timestamp = _resolve_timestamp(timestamp_milliseconds)
    entropy = int.from_bytes(os.urandom(10), byteorder="big")
    random_a = (entropy >> 68) & _MAX_RANDOM_A
    random_b = entropy & _MAX_RANDOM_B
    value = (timestamp << 80) | (UUID_V7_VERSION << 76) | (random_a << 64)
    value |= 0b10 << 62
    value |= random_b
    return UUID(int=value)


def parse_uuid7(value: str) -> UUID:
    """Parse a canonical lowercase UUIDv7 string.

    Args:
        value: Canonical UUID string.

    Returns:
        Parsed UUIDv7 value.

    Raises:
        ValueError: If the value is not canonical UUIDv7.
    """
    try:
        parsed = UUID(value)
    except (AttributeError, ValueError, TypeError) as exc:
        raise ValueError("value must be a canonical UUIDv7") from exc
    if parsed.version != UUID_V7_VERSION or parsed.variant != "specified in RFC 4122":
        raise ValueError("value must be a canonical UUIDv7")
    if str(parsed) != value:
        raise ValueError("value must be a canonical lowercase UUIDv7")
    return parsed


def _resolve_timestamp(timestamp_milliseconds: int | None) -> int:
    """Resolve and validate the UUIDv7 timestamp field."""
    timestamp = (
        time.time_ns() // 1_000_000 if timestamp_milliseconds is None else timestamp_milliseconds
    )
    if type(timestamp) is not int:
        raise ValueError("timestamp_milliseconds must be an integer")
    if timestamp < 0 or timestamp > _MAX_TIMESTAMP_MILLISECONDS:
        raise ValueError("timestamp_milliseconds is outside UUIDv7 range")
    return timestamp
