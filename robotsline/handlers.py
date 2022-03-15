"""Execution of commands on a robotic factory"""
import functools
import logging
from typing import Any

from . import commands, exceptions, models

logger = logging.getLogger(__name__)


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

    try:
        robot.move()
    except exceptions.InvalidTransition as cannot_move:
        logger.error(cannot_move)


@execute.register
def mine(command: commands.Mine, on_factory: models.RoboticFactory) -> None:
    """Ask a robot to mine"""
    robot = on_factory.get_robot(command.robot_id)
    if robot is None:
        return

    try:
        material = models.Material(command.material)
    except ValueError as unknown_material:
        logger.error(unknown_material)
        return

    try:
        robot.mine(material)
    except exceptions.InvalidTransition as cannot_mine:
        logger.error(cannot_mine)


@execute.register
def assemble(command: commands.Assemble, on_factory: models.RoboticFactory) -> None:
    """Ask a robot to mine"""
    on_factory.assemble(robot_id=command.robot_id)
