"""Domain models for a robotic factory"""
import abc
from itertools import count
from typing import Callable, Iterable, Iterator, Optional

from . import exceptions


class RobotState(abc.ABC):
    """Abstract robot state"""

    def __init__(self, robot: "Robot") -> None:
        self.robot = robot

    def __str__(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def move(self):
        """Try to move the robot"""
        raise exceptions.InvalidTransition(f"Cannot move from state {self}")


class Moving(RobotState):
    """Robot is 🚶"""

    def move(self):
        pass


class Idle(RobotState):
    """Robot doing nothing 😴"""

    def move(self):
        self.robot.state = Moving(self.robot)


RobotId = int
RobotIdGenerator = Iterator[RobotId]


class Robot:
    """Robot in a factory 🤖"""

    def __init__(self, id_: RobotId):
        self.id_ = id_
        self.state: RobotState = Idle(self)

    @property
    def status(self) -> str:
        """Return robot state as string"""
        return str(self.state)

    @classmethod
    def from_id_generator(cls, id_generator: RobotIdGenerator) -> "Robot":
        return cls(next(id_generator))

    def move(self) -> None:
        """Move the robot"""
        self.state.move()


def robots_generator() -> Iterable[Robot]:
    """Generate some robots whose ids starting with 1"""
    counter = count(start=1)
    while True:
        yield Robot.from_id_generator(counter)


class RoboticFactory:
    """Outstanding Robotic factory 🏭"""

    def __init__(self, robots: list[Robot]) -> None:
        self.robots = robots

    def get_robot(self, robot_id: int) -> Optional[Robot]:
        """Get the robot with the given id"""
        for robot in self.robots:
            if robot.id_ == robot_id:
                return robot
        return None
