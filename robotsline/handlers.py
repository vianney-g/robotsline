"""Execution of commands on a robotic factory"""
import functools
import logging
from typing import Any, Callable

from . import commands, exceptions, models

logger = logging.getLogger(__name__)

Handler = Callable[[commands.Command], None]


@functools.singledispatch
def handler(command: Any, on_factory: models.RoboticFactory) -> None:
    """Default handler when command is not regstered

    :raises: DomainError
    """


@handler.register
def move(command: commands.MoveRobot, on_factory: models.RoboticFactory) -> None:
    """Move a robot"""
    on_factory.move(robot_id=command.robot_id)


@handler.register
def mine(command: commands.Mine, on_factory: models.RoboticFactory) -> None:
    """Ask a robot to mine"""
    try:
        material = models.Material(command.material)
    except ValueError as unknown_material:
        logger.error(unknown_material)
        return

    on_factory.mine(robot_id=command.robot_id, material=material)


@handler.register
def assemble(command: commands.Assemble, on_factory: models.RoboticFactory) -> None:
    """Ask a robot to mine"""
    on_factory.assemble(robot_id=command.robot_id)


def ignore_domain_errors(function: Handler):
    """Log domain errors but do not raise them"""

    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except exceptions.DomainError as domain_error:
            logger.error(domain_error)

    return wrapper


execute = ignore_domain_errors(handler)
