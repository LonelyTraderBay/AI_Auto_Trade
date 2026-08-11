"""Unit tests for injectable UTC clocks."""

from datetime import UTC, datetime

import pytest

from ai_auto_trade.shared_kernel.clock import FixedClock, SystemClock


def test_system_clock_returns_utc_timestamp() -> None:
    """System clock returns an aware UTC timestamp."""
    now = SystemClock().now()

    assert now.tzinfo is UTC


def test_fixed_clock_returns_unchanged_timestamp() -> None:
    """Fixed clock returns the exact configured timestamp."""
    expected = datetime(2026, 8, 12, 0, 0, tzinfo=UTC)

    assert FixedClock(expected).now() == expected


def test_fixed_clock_rejects_naive_timestamp() -> None:
    """Fixed clock rejects timestamps without UTC timezone information."""
    with pytest.raises(ValueError, match="UTC"):
        FixedClock(datetime(2026, 8, 12, 0, 0))
