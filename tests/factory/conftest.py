"""Fixtures for the robotic factory"""

from decimal import Decimal
from typing import Callable, Optional

import pytest

from robotsline.models import Bar, Foo, Foobar, Robot, Stock
from robotsline.settings import Settings


@pytest.fixture
def stock_factory() -> Callable[[...], Stock]:
    def _factory(
        robots: list[Robot],
        foos_nb: int = 0,
        bars_nb: int = 0,
        money: Decimal = Decimal("0.00"),
        foobars: Optional[list[Foobar]] = None,
    ):
        if foobars is None:
            foobars = []
        foos = [Foo() for _ in range(foos_nb)]
        bars = [Bar(1) for _ in range(bars_nb)]
        return Stock(robots=robots, foos=foos, bars=bars, money=money, foobars=foobars)

    return _factory
