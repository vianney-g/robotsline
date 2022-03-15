"""Set of commands for robot factory app"""
import dataclasses
from typing import NewType

Command = NewType("Command", object)


@dataclasses.dataclass(frozen=True)
class MoveRobot:
    """Ask a robot to move"""

    robot_id: int


@dataclasses.dataclass(frozen=True)
class Mine:
    """Ask a robot to mine"""

    robot_id: int
    material: str
