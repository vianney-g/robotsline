# pylint:disable=missing-docstring
import pytest

from robotsline import commands, exceptions, handlers, models


def test_game_is_over_when_30_robots_is_in():
    # Given I have 29 robots in a factory
    robots = [models.Robot(robot_id) for robot_id in range(30)]
    stock = models.Stock(robots)
    factory = models.RoboticFactory(stock)

    # When I try to run a new round
    # Then game is over
    with pytest.raises(exceptions.GameOver):
        handlers.execute(commands.Wait(seconds=1), on_factory=factory)
