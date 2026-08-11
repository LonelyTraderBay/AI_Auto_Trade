"""Unit tests for seeded randomness."""

from typing import cast

import pytest

from ai_auto_trade.shared_kernel.random_source import SeededRandomSource


def test_seeded_sources_produce_the_same_sequence() -> None:
    """Equal seeds produce equal bounded sequences."""
    first = SeededRandomSource(42)
    second = SeededRandomSource(42)

    assert [first.randbelow(100) for _ in range(5)] == [second.randbelow(100) for _ in range(5)]


@pytest.mark.parametrize("upper_bound", [0, -1])
def test_seeded_source_rejects_non_positive_bound(upper_bound: int) -> None:
    """Random source rejects invalid bounds."""
    with pytest.raises(ValueError, match="positive"):
        SeededRandomSource(1).randbelow(upper_bound)


def test_seeded_source_rejects_non_integer_bound() -> None:
    """Random source rejects non-integer bounds."""
    with pytest.raises(ValueError, match="positive integer"):
        SeededRandomSource(1).randbelow(cast(int, 10.0))
