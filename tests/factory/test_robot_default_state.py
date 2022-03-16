"""Test the robot default state"""
# pylint: disable=missing-docstring

from robotsline import models


def test_new_robots_are_idling():
    # Given a default robot
    robot = models.Robot(id_=1)

    # The robot is in IDLE state at the cafeteria
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.CAFETERIA
