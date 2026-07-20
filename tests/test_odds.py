import pytest

from nba_odds_history_hub.odds import (
    american_to_decimal,
    american_to_implied_probability,
)


def test_positive_american_to_decimal() -> None:
    assert american_to_decimal(188) == 2.88


def test_negative_american_to_decimal() -> None:
    assert american_to_decimal(-211) == 1.473934


def test_positive_implied_probability() -> None:
    assert american_to_implied_probability(188) == 0.34722222


def test_negative_implied_probability() -> None:
    assert american_to_implied_probability(-211) == 0.67845659


@pytest.mark.parametrize("value", [0, 50, -50])
def test_invalid_american_odds(value: int) -> None:
    with pytest.raises(ValueError):
        american_to_decimal(value)
