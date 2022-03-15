"""Test the robot default state"""
# pylint: disable=missing-docstring

from robotsline import models


def test_new_robots_are_idling(robotic_factory):
    # Given a factory with a robot
    factory = robotic_factory(1)
    robot_1 = factory.robots[0]

    # The robot is in IDLE state at the cafeteria
    assert robot_1.status == "Idle"
    assert robot_1.state.location == models.Location.CAFETERIA
