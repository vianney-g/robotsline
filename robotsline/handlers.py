"""Execution of commands on a robotic factory"""
import functools
from typing import Any

from . import commands, models


@functools.singledispatch
def execute(command: Any, on_factory: models.RoboticFactory) -> None:
    """Default handler when command is not regstered

    :raises: RobotsLineError
    """


@execute.register
def execute(command: commands.MoveRobot, on_factory: models.RoboticFactory) -> None:
    """Move a robot"""
    robot = on_factory.get_robot(command.robot_id)
    if robot is None:
        return

    robot.move()
