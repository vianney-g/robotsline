"""Test buying robot"""
# pylint: disable=missing-docstring
import pytest

from robotsline import commands, handlers, models


@pytest.mark.parametrize(
    "wrong_place",
    [
        location
        for location in models.Location
        if location is not models.Location.ROBOTS_STORE
    ],
)
def test_buying_at_the_wrong_place(wrong_place: models.Location):
    # Given a factory with some money and foos
    # And a robot not in the robot store
    robot = models.Robot(id_=1, location=wrong_place)
    stock = models.Stock([robot], money=models.Decimal("10.00"), foos_nb=6)
    factory = models.RoboticFactory(stock=stock)

    # When I ask her to buy a Robot
    buy = commands.BuyRobot(robot_id=robot.id_)
    handlers.execute(buy, on_factory=factory)

    # Then number of robots did not change
    assert stock.robots == [robot]
    # and robot is idle
    assert robot.status == "Idle"


def test_buying_a_robot_costs_money_and_foos():
    # Given a factory with some money and foos
    # And a robot in the robot store
    robot = models.Robot(id_=1, location=models.Location.ROBOTS_STORE)
    stock = models.Stock([robot], money=models.Decimal("10.00"), foos_nb=6)
    factory = models.RoboticFactory(stock=stock)

    # When I ask her to buy a Robot
    buy = commands.BuyRobot(robot_id=robot.id_)
    handlers.execute(buy, on_factory=factory)

    # Then we've got one robot more
    assert len(stock.robots) == 2
    # and robot is idle
    assert robot.status == "Idle"
    # and we've got 6 foos and 3€ less
    assert stock.money == 7
    assert stock.foos == 0


@pytest.mark.parametrize(
    "money,foos",
    [
        (0, 0),
        (10, 2),  # not enough foos
        (2, 10),  # not enough money
    ],
)
def test_buying_a_robot_but_not_enough_resources(money: int, foos: int):
    # Given a factory with not enough money and/or foos
    # And a robot in the robot store
    robot = models.Robot(id_=1, location=models.Location.ROBOTS_STORE)
    stock = models.Stock([robot], money=models.Decimal(money), foos_nb=foos)
    factory = models.RoboticFactory(stock=stock)

    # When I ask her to buy a Robot
    buy = commands.BuyRobot(robot_id=robot.id_)
    handlers.execute(buy, on_factory=factory)

    # Then we have no new robot
    assert len(stock.robots) == 1
    # and robot is idle
    assert robot.status == "Idle"
    # and stock didn't changed
    assert stock.money == money
    assert stock.foos == foos
