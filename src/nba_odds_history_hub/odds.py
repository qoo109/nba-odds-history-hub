"""Odds conversion helpers."""

from __future__ import annotations


def _validate_american(odds: int | float) -> float:
    value = float(odds)
    if value == 0:
        raise ValueError("American odds cannot be zero")
    if -100 < value < 100:
        raise ValueError("American odds must be <= -100 or >= +100")
    return value


def american_to_decimal(odds: int | float, *, digits: int = 6) -> float:
    """Convert American odds to decimal odds.

    Examples:
        +188 -> 2.88
        -211 -> 1.473934...
    """
    value = _validate_american(odds)
    decimal = 1 + (value / 100 if value > 0 else 100 / abs(value))
    return round(decimal, digits)


def american_to_implied_probability(
    odds: int | float, *, digits: int = 8
) -> float:
    """Return the raw implied probability as a value between 0 and 1.

    This is not de-vigged and should not be treated as fair probability.
    """
    value = _validate_american(odds)
    probability = (
        100 / (value + 100)
        if value > 0
        else abs(value) / (abs(value) + 100)
    )
    return round(probability, digits)
