"""Test instanciation of robotic factory"""
# pylint: disable=missing-docstring
from robotsline import models


def test_i_can_bootstrap_a_factory_with_two_robots():
    # Given a factory with 2 robots
    factory = models.Factory(nb_robots=2)

    # When I ask nothing to factory
    # The two robots are in IDLE state

    robot_1, robot_2 = factory.robots
    assert robot_1.state == models.RobotState.IDLE
    assert robot_2.state == models.RobotState.IDLE
