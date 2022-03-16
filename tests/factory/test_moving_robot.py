"""Test robot moving"""
# pylint: disable=missing-docstring
from robotsline import commands, handlers, models


def test_a_robot_can_be_moved(robotic_factory):
    # Given an idle robot at the cafeteria
    factory = robotic_factory()
    robot = models.Robot(1, location=models.Location.CAFETERIA)
    factory.robots.append(robot)

    # When I ask her to move to foo_mine
    move_robot = commands.MoveRobot(robot_id=robot.id_, destination="Foo Mine")
    handlers.execute(move_robot, on_factory=factory)

    # Then robot is moving for 5 seconds
    assert robot.status == "Moving"
    assert robot.state.countdown == 5


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


def test_after_a_move_robot_is_idling_at_destination(robotic_factory):
    # Given an idle robot at the cafeteria
    factory = robotic_factory()
    robot = models.Robot(1, location=models.Location.CAFETERIA)
    factory.robots.append(robot)

    # When I ask her to move to foo mine and I wait 5 rounds
    move_robot = commands.MoveRobot(robot_id=robot.id_, destination="Foo Mine")
    handlers.execute(move_robot, on_factory=factory)
    wait_5_seconds = commands.Wait(seconds=5)
    handlers.execute(wait_5_seconds, on_factory=factory)

    # Then robot is idling at foo mine
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.FOO_MINE
