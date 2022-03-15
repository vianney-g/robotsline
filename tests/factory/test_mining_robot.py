"""Test robot mining"""
# pylint: disable=missing-docstring
import pytest

from robotsline import commands, handlers, models


@pytest.mark.parametrize(
    "material,at_mine",
    [("foo", models.Location.FOO_MINE), ("bar", models.Location.BAR_MINE)],
)
def test_asking_a_robot_to_mine_something(
    robotic_factory, material: str, at_mine: models.Location
):
    # Given a robot at the mine
    factory = robotic_factory()
    robot = models.Robot(1, location=at_mine)
    factory.robots.append(robot)

    # When I ask it to mine
    mine = commands.Mine(robot_id=robot.id_, material=material)
    handlers.execute(mine, on_factory=factory)

    # the robot is now mining the requested material
    assert robot.status == f"Mining {material} at {at_mine.value.title()}"


def test_asking_a_robot_to_mine_a_bad_material(robotic_factory):
    # Given a robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]

    # When I ask it to mine a strange material
    mine = commands.Mine(robot_id=robot.id_, material="💰")
    handlers.execute(mine, on_factory=factory)

    # the robot is still idling
    assert robot.status == "Idle"


@pytest.mark.parametrize(
    "wrong_material,at_mine",
    [("bar", models.Location.BAR_MINE), ("foo", models.Location.FOO_MINE)],
)
def test_asking_a_robot_to_mine_something_but_she_is_at_the_wrong_mine(
    robotic_factory, wrong_material: str, at_mine: models.Location
):
    # Given a robot at the mine
    factory = robotic_factory()
    robot = models.Robot(1, location=at_mine)

    # When I ask it to mine the wrong material
    mine = commands.Mine(robot_id=robot.id_, material=wrong_material)
    handlers.execute(mine, on_factory=factory)

    # the robot is still idle
    assert robot.status == "Idle"
