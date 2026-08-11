"""Injectable seeded randomness for deterministic simulator behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Protocol


class RandomSource(Protocol):
    """Provide deterministic bounded randomness to domain callers."""

    def randbelow(self, upper_bound: int) -> int:
        """Return a value in the half-open interval [0, upper_bound)."""
        ...


@dataclass(slots=True)
class SeededRandomSource:
    """Use an isolated pseudo-random generator with a recorded seed."""

    seed: int
    _generator: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the isolated generator."""
        self._generator = Random(self.seed)

    def randbelow(self, upper_bound: int) -> int:
        """Return a deterministic bounded value.

        Args:
            upper_bound: Exclusive positive upper bound.

        Returns:
            Deterministic pseudo-random integer.

        Raises:
            ValueError: If the upper bound is not positive.
        """
        if type(upper_bound) is not int or upper_bound <= 0:
            raise ValueError("upper_bound must be a positive integer")
        return self._generator.randrange(upper_bound)
