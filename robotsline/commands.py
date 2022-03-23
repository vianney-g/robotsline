"""Set of commands for robot factory app"""
import dataclasses
from typing import NewType

Command = NewType("Command", object)


@dataclasses.dataclass(frozen=True)
class MoveRobot:
    """Ask a robot to move"""

    robot_id: int
    destination: str


@dataclasses.dataclass(frozen=True)
class Mine:
    """Ask a robot to mine"""

    robot_id: int
    material: str

    @classmethod
    def Foo(cls, robot_id: int) -> "Mine":
        """Binded factory to mine foo"""
        return cls(robot_id=robot_id, material="foo")

    @classmethod
    def Bar(cls, robot_id: int) -> "Mine":
        """Binded factory to mine bar"""
        return cls(robot_id=robot_id, material="bar")


@dataclasses.dataclass(frozen=True)
class Assemble:
    """Ask a robot to assemble"""

    robot_id: int


@dataclasses.dataclass(frozen=True)
class Wait:
    """Wait a given number of seconds"""

    seconds: int


@dataclasses.dataclass(frozen=True)
class SellFoobars:
    """Sell some foobars"""

    robot_id: int


@dataclasses.dataclass(frozen=True)
class BuyRobot:
    """Get a new buddy 🤖"""

    robot_id: int
