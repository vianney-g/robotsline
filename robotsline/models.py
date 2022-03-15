"""Domain models for a robotic factory"""
import abc
import enum
from itertools import count
from typing import Iterable, Iterator, Optional

from . import exceptions


class Material(enum.Enum):
    """Valid materials"""

    FOO = "foo"
    BAR = "bar"


class RobotState(abc.ABC):
    """Abstract robot state"""

    def __init__(self, robot: "Robot") -> None:
        self.robot = robot

    def __str__(self) -> str:
        return self.__class__.__name__

    def move(self):
        """Try to move the robot"""
        raise exceptions.InvalidTransition(f"Cannot move robot {self.robot}")

    def mine(self, material: Material):
        """Try to send the robot to mine"""
        raise exceptions.InvalidTransition(f"Cannot send robot {self.robot}.")


class Moving(RobotState):
    """Robot is 🚶"""

    def move(self):
        pass


class Mining(RobotState):
    """Robot is ⛏"""

    def __init__(self, robot: "Robot", material: Material) -> None:
        super().__init__(robot)
        self.material = material

    def __str__(self) -> str:
        return f"Mining {self.material.value}"

    def mine(self, material: Material):
        pass


class Idle(RobotState):
    """Robot is sleeping 😴"""

    def move(self):
        self.robot.state = Moving(self.robot)

    def mine(self, material: Material):
        self.robot.state = Mining(self.robot, material)


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

    def mine(self, material: Material) -> None:
        """Send robot to mine"""
        self.state.mine(material)


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
