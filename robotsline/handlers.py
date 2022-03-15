"""Execution of commands on a robotic factory"""
import functools
from typing import Any

from . import commands, models, exceptions


@functools.singledispatch
def execute(command: Any, on_factory: models.RoboticFactory) -> None:
    """Default handler when command is not regstered

    :raises: RobotsLineError
    """


@execute.register
def move(command: commands.MoveRobot, on_factory: models.RoboticFactory) -> None:
    """Move a robot"""
    robot = on_factory.get_robot(command.robot_id)
    if robot is None:
        return

    robot.move()


@execute.register
def mine(command: commands.Mine, on_factory: models.RoboticFactory) -> None:
    """Ask a robot to mine"""
    robot = on_factory.get_robot(command.robot_id)
    if robot is None:
        return

    try:
        material = models.Material(command.material)
    except ValueError as unknown_material:
        raise exceptions.UnknownMaterial from unknown_material


    robot.mine(material)
