"""Test the robots actions"""
# pylint: disable=missing-docstring,redefined-outer-name

import pytest

from robotsline import commands, handlers, models


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
    robot.state.move()

    # When I ask it to be moved
    move_robot = commands.MoveRobot(robot_id=robot.id_)
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is still moving
    assert robot.status == "Moving"


@pytest.mark.parametrize("material", ["foo", "bar"])
def test_asking_a_robot_to_mine_something(robotic_factory, material):
    # Given a robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]

    # When I ask it to mine
    mine = commands.Mine(robot_id=robot.id_, material=material)
    handlers.execute(mine, on_factory=factory)

    # the robot is now mining the requested material
    assert robot.status == f"Mining {material}"


def test_asking_a_robot_to_mine_a_bad_material(robotic_factory):
    # Given a robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]

    # When I ask it to mine a strange material
    mine = commands.Mine(robot_id=robot.id_, material="💰")
    handlers.execute(mine, on_factory=factory)

    # the robot is still idling
    assert robot.status == f"Idle"


def test_asking_a_robot_to_assemble_foo_and_bar(robotic_factory):
    # Given a robot in a factory with enough stock
    factory = robotic_factory(1)
    factory.stock.foos = 1
    factory.stock.bars = 1

    robot = factory.robots[0]

    # When I ask it to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # the robot is assembling
    assert robot.status == f"Assembling foo bar"
    # and stock is lower
    assert factory.stock.foos == 0
    assert factory.stock.bars == 0


def test_asking_a_robot_to_assemble_but_she_is_busy(robotic_factory):
    # Given a robot in a factory with enough stock, but robot is mining
    factory = robotic_factory(1)
    factory.stock.foos = 1
    factory.stock.bars = 1
    factory.stock.foobars = []
    robot = factory.robots[0]
    factory.move(robot.id_)

    # When I ask it to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # Then the robot is still moving
    assert robot.status == f"Moving"
    # And stock didn't changed
    assert factory.stock.foos == 1
    assert factory.stock.bars == 1
    # And foobar is not yet produced
    assert factory.stock.foobars == []
