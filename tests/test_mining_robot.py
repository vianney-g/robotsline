"""Test robot mining"""
# pylint: disable=missing-docstring
import pytest

from robotsline import commands, handlers, models
from robotsline.settings import Settings


@pytest.mark.parametrize(
    "material,at_mine",
    [("foo", models.Location.FOO_MINE), ("bar", models.Location.BAR_MINE)],
)
def test_asking_a_robot_to_mine_something(material: str, at_mine: models.Location):
    # Given a robot at the mine
    robot = models.Robot(1, location=at_mine)
    stock = models.Stock([robot])
    factory = models.RoboticFactory(stock)

    # When I ask her to mine
    mine = commands.Mine(robot_id=robot.id_, material=material)
    handlers.execute(mine, on_factory=factory)

    # the robot is now mining the requested material
    assert robot.status == f"Mining {material}"


def test_asking_a_robot_to_mine_a_bad_material():
    # Given a robot in a factory
    robot = models.Robot(id_=1)
    stock = models.Stock([robot])
    factory = models.RoboticFactory(stock)

    # When I ask her to mine a strange material
    mine = commands.Mine(robot_id=robot.id_, material="💰")
    handlers.execute(mine, on_factory=factory)

    # the robot is still idling
    assert robot.status == "Idle"


@pytest.mark.parametrize(
    "wrong_material,at_mine",
    [("bar", models.Location.FOO_MINE), ("foo", models.Location.BAR_MINE)],
)
def test_asking_a_robot_to_mine_something_but_she_is_at_the_wrong_mine(
    wrong_material: str, at_mine: models.Location
):
    # Given a robot at the mine
    robot = models.Robot(1, location=at_mine)
    stock = models.Stock([robot])
    factory = models.RoboticFactory(stock)

    # When I ask her to mine the wrong material
    mine = commands.Mine(robot_id=robot.id_, material=wrong_material)
    handlers.execute(mine, on_factory=factory)

    # the robot is still idle
    assert robot.status == "Idle"


def test_mining_foo():
    # Given a robot at foo mine, and a factory with no foo stock
    robot = models.Robot(1, location=models.Location.FOO_MINE)
    stock = models.Stock([robot])

    factory = models.RoboticFactory(stock)

    # When I ask her to mine foo for 1 second
    mine = commands.Mine(robot_id=1, material="foo")
    handlers.execute(mine, on_factory=factory)
    handlers.execute(commands.Wait(seconds=1), on_factory=factory)

    # the robot is idling at the mine
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.FOO_MINE
    # And the stock of Foo increased
    assert len(stock.foos) == 1


def test_mining_bar():
    # Given a robot at bar mine, and a factory with no bar stock
    robot = models.Robot(1, location=models.Location.BAR_MINE)
    stock = models.Stock([robot])

    settings = Settings(mining_bar_range_time=(1, 1))
    factory = models.RoboticFactory(stock=stock, settings=settings)

    # When I ask her to mine bar for 1 second
    mine = commands.Mine(robot_id=1, material="bar")
    handlers.execute(mine, on_factory=factory)
    handlers.execute(commands.Wait(seconds=1), on_factory=factory)

    # the robot is idling at the mine
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.BAR_MINE
    # And the stock of bars increased
    assert len(stock.bars) == 1


def test_mining_bar_waiting_longer():
    # Given a robot at bar mine, and a factory with no bar stock
    robot = models.Robot(1, location=models.Location.BAR_MINE)
    stock = models.Stock([robot])

    # And mining bar may take a long time
    settings = Settings(mining_bar_range_time=(10, 10))
    factory = models.RoboticFactory(stock=stock, settings=settings)

    # When I ask her to mine bar for 1 second
    mine = commands.Mine(robot_id=1, material="bar")
    handlers.execute(mine, on_factory=factory)
    handlers.execute(commands.Wait(seconds=1), on_factory=factory)

    # The robot is still mining bar
    assert robot.status == "Mining bar"
    # And I need 9 seconds more to mine bar
    handlers.execute(commands.Wait(seconds=9), on_factory=factory)
    assert robot.status == "Idle"
