import time
from itertools import cycle
from typing import Iterable, Iterator

from .. import bootstrap, commands, models


def _idle_robots(stock: models.Stock) -> Iterator[models.Robot]:
    return (robot for robot in stock.robots if robot.status == "Idle")


def _get_idle_robot_at(stock: models.Stock, location: models.Location) -> models.Robot:
    idle_robots = (
        robot for robot in _idle_robots(stock) if robot.state.location is location
    )
    return next(idle_robots, models.Robot.ghost())


def _move_idle_robot_to(
    stock: models.Stock, destination: models.Location
) -> Iterable[commands.Command]:
    robot = next(_idle_robots(stock), models.Robot.ghost())
    if robot:
        yield commands.MoveRobot(robot_id=robot.id_, destination=destination.value)


def _extract_foo(stock: models.Stock) -> Iterable[commands.Command]:
    extractor = _get_idle_robot_at(stock, models.Location.FOO_MINE)
    if extractor:
        yield commands.Mine(robot_id=extractor.id_, material="foo")
    else:
        yield from _move_idle_robot_to(stock, models.Location.FOO_MINE)


def _extract_bar(stock: models.Stock) -> Iterable[commands.Command]:
    extractor = _get_idle_robot_at(stock, models.Location.BAR_MINE)
    if extractor:
        yield commands.Mine(robot_id=extractor.id_, material="bar")
    else:
        yield from _move_idle_robot_to(stock, models.Location.BAR_MINE)


def _assemble_foobars(stock: models.Stock) -> Iterable[commands.Command]:
    if stock.has_enough_material():
        assembler = _get_idle_robot_at(stock, models.Location.ASSEMBLY_LINE)
        if assembler:
            yield commands.Assemble(robot_id=assembler.id_)
        else:
            yield from _move_idle_robot_to(stock, models.Location.ASSEMBLY_LINE)
    else:
        if not stock.foos:
            yield from _extract_foo(stock)
        if not stock.bars:
            yield from _extract_bar(stock)


def _sell_materials(stock: models.Stock) -> Iterable[commands.Command]:
    if stock.foobars:
        seller = _get_idle_robot_at(stock, models.Location.MATERIAL_STORE)
        if seller:
            yield commands.SellFoobars(robot_id=seller.id_)
        else:
            yield from _move_idle_robot_to(stock, models.Location.MATERIAL_STORE)
    else:
        yield from _assemble_foobars(stock)


def _purchase_robot(
    stock: models.Stock, settings: models.Settings
) -> Iterable[commands.Command]:
    required_money, required_foos = settings.robot_cost
    if stock.can_buy_robot(required_money, required_foos):
        buyer = _get_idle_robot_at(stock, models.Location.ROBOTS_STORE)
        if buyer:
            yield commands.BuyRobot(robot_id=buyer.id_)
        else:
            yield from _move_idle_robot_to(stock, models.Location.ROBOTS_STORE)
    else:
        if required_money > stock.money:
            yield from _sell_materials(stock)
        if required_foos > len(stock.foos):
            yield from _extract_foo(stock)


def _ia_director(
    stock: models.Stock, settings: models.Settings
) -> Iterable[commands.Command]:
    while True:
        if len(stock.robots) < 5:
            yield from _low_robots_strategy(stock, settings)
        else:
            yield from _high_robots_strategy(stock, settings)
        yield commands.Wait(seconds=1)


def _low_robots_strategy(
    stock: models.Stock, settings: models.Settings
) -> Iterable[commands.Command]:
    """Naive strategy is to give priority of robots purchase."""
    yield from _purchase_robot(stock, settings)
    while next(_idle_robots(stock), False):
        yield from _extract_foo(stock)
        yield from _extract_bar(stock)


def _high_robots_strategy(
    stock: models.Stock, settings: models.Settings
) -> Iterable[commands.Command]:
    """We place a robot on strategic places to minimize movement"""
    locations_activity = {
        models.Location.FOO_MINE: commands.Mine.Foo,
        models.Location.BAR_MINE: commands.Mine.Bar,
        models.Location.ASSEMBLY_LINE: commands.Assemble,
        models.Location.MATERIAL_STORE: commands.SellFoobars,
    }
    # Just 1 seller is needed
    seller, robot_store = stock.robots[0], models.Location.ROBOTS_STORE
    if seller.state.location is not robot_store:
        yield commands.MoveRobot(robot_id=seller.id_, destination=robot_store.value)
    yield commands.BuyRobot(robot_id=seller.id_)

    for robot, location in zip(stock.robots[1:], cycle(locations_activity)):
        if robot.state.location is not location and robot.status == "Idle":
            yield commands.MoveRobot(robot_id=robot.id_, destination=location.value)
    for robot in stock.robots:
        if robot.state.location in locations_activity:
            yield locations_activity[robot.state.location](robot_id=robot.id_)


def get_director(game: bootstrap.Game) -> Iterable[tuple[commands.Command, str]]:
    for cmd in _ia_director(game.factory.stock, game.factory.settings):
        yield cmd, str(cmd)
        time.sleep(0.1)
