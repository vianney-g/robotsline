"""Test the robotic factory"""
# pylint: disable=missing-docstring,redefined-outer-name
from typing import Callable

import pytest

from robotsline import commands, handlers, models


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


def test_new_robots_are_idling(robotic_factory):
    # Given a factory with 2 robots
    factory = robotic_factory(2)
    robot_1, robot_2 = factory.robots
    # The two robots are in IDLE state

    assert robot_1.status == "Idle"
    assert robot_2.status == "Idle"


def test_a_robot_can_be_moved(robotic_factory):
    # Given a robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]

    # When I ask it to be moved
    move_robot = commands.MoveRobot(robot_id=robot.id_)
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is moving
    assert robot.status == "Moving"


def test_moving_a_moving_robot_is_idempotent(robotic_factory):
    # Given a robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]
    robot.move()

    # When I ask it to be moved
    move_robot = commands.MoveRobot(robot_id=robot.id_)
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is still moving
    assert robot.status == "Moving"
