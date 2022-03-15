"""Fixtures for the robotic factory"""
# pylint: disable=missing-docstring,redefined-outer-name
from typing import Callable

import pytest

from robotsline import models


@pytest.fixture
def robot() -> Callable[[], models.Robot]:
    robots_generator = models.robots_generator()

    def build_robot() -> models.Robot:
        return next(robots_generator)

    return build_robot


@pytest.fixture
def robotic_factory(robot) -> Callable[[int], models.RoboticFactory]:
    def _factory(robots_nb: int) -> models.RoboticFactory:
        robots = [robot() for _ in range(robots_nb)]
        return models.RoboticFactory(robots)

    return _factory
