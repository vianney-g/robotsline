"""Test robot mining"""
# pylint: disable=missing-docstring
import pytest

from robotsline import commands, handlers, models


@pytest.mark.parametrize(
    "wrong_place",
    [
        location
        for location in models.Location
        if location is not models.Location.MATERIAL_STORE
    ],
)
def test_selling_at_the_wrong_place(wrong_place: models.Location):
    # Given a factory with enough stock
    # And a robot not in the material store
    robot = models.Robot(id_=1, location=wrong_place)
    foobar = models.Foobar()
    stock = models.Stock(foobars=[foobar])
    factory = models.RoboticFactory(robots=[robot], stock=stock)

    # When I ask her to sell a foobar and wait 10s
    sell = commands.SellFoobars(robot_id=robot.id_)
    handlers.execute(sell, on_factory=factory)

    # Then stock didn't change
    assert stock.foobars == [foobar]
    # and moneybag either
    assert stock.money == 0
    # and robot is idle
    assert robot.status == "Idle"


@pytest.mark.parametrize(
    "initial_stock,final_money,final_stock",
    [
        (1, 1, 0),
        (5, 5, 0),
        (10, 5, 5),  # max 5 foobars by sell
        (0, 0, 0),
    ],
)
def test_selling_foobars_gave_me_money(
    initial_stock: int, final_money: int, final_stock: int
):
    # Given a factory with some stock
    # And a robot not in the material store
    robot = models.Robot(id_=1, location=models.Location.MATERIAL_STORE)
    foobars = [models.Foobar() for _ in range(initial_stock)]
    stock = models.Stock(foobars=foobars)
    factory = models.RoboticFactory(robots=[robot], stock=stock)

    # When I ask her to sell some foobars
    assemble = commands.SellFoobars(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # Then stock did changed because foobar is being sold
    assert len(stock.foobars) == final_stock
    # But moneybag didn't, as it's not yet sold
    assert stock.money == 0

    # When I wait 10s
    handlers.execute(commands.Wait(seconds=10), on_factory=factory)
    # Then I earned the money
    assert stock.money == final_money
