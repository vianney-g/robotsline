"""Test robot moving"""
# pylint: disable=missing-docstring
from robotsline import commands, handlers, models


def test_a_robot_can_be_moved(robotic_factory):
    # Given an idle robot in a factory
    factory = robotic_factory(1)
    robot = factory.robots[0]

    # When I ask it to be moved to foo_mine
    move_robot = commands.MoveRobot(robot_id=robot.id_, destination="Foo Mine")
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is moving
    assert robot.status == "Moving"


def test_a_moving_robot_cannot_be_rerouted(robotic_factory):
    # Given a robot moving at the cafeteria
    factory = robotic_factory(1)
    robot = factory.robots[0]
    robot.state.move(destination=models.Location.CAFETERIA)

    # When I ask it to be moved at the foo mine
    move_robot = commands.MoveRobot(robot_id=robot.id_, destination="Foo Mine")
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is still moving at the cafeteria
    assert robot.status == "Moving"
    assert robot.state.destination is models.Location.CAFETERIA
