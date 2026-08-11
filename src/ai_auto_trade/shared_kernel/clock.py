"""Injectable UTC clocks for deterministic domain and simulator code."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Provide timezone-aware UTC timestamps."""

    def now(self) -> datetime:
        """Return the current UTC timestamp."""
        ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """Read the system clock as UTC."""

    def now(self) -> datetime:
        """Return the current timezone-aware UTC timestamp."""
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class FixedClock:
    """Return a fixed UTC timestamp for deterministic tests and replay."""

    current: datetime

    def __post_init__(self) -> None:
        """Reject naive or non-UTC timestamps."""
        if self.current.tzinfo != UTC:
            raise ValueError("current must be timezone-aware UTC")

    def now(self) -> datetime:
        """Return the configured fixed timestamp."""
        return self.current
