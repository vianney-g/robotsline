"""Domain models for a robotic factory"""
import abc
import enum
import logging
import uuid
from itertools import count
from typing import Iterable, Iterator, Literal

from . import exceptions

logger = logging.getLogger(__name__)


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
        raise exceptions.InvalidTransition(f"Cannot send robot {self.robot} to mine.")

    def assemble(self, stock: "Stock"):
        """Try to send the robot to assembly line"""
        raise exceptions.InvalidTransition(
            f"Cannot send robot {self.robot} to assembly line."
        )

    def haunt(self):
        """Try to make the robot haunting"""
        if self.robot:
            raise exceptions.InvalidTransition(f"Robot is not a ghost")
        self.robot.state = Haunting(self.robot)


class Haunting(RobotState):
    """👻"""


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


class Assembling(RobotState):
    """Robot is assembling"""

    def __init__(self, robot: "Robot", stock: "Stock") -> None:
        super().__init__(robot)
        self.stock = stock

    def __str__(self) -> str:
        return f"Assembling foo bar"


class Idle(RobotState):
    """Robot is sleeping 😴"""

    def move(self):
        self.robot.state = Moving(self.robot)

    def mine(self, material: Material):
        self.robot.state = Mining(self.robot, material)

    def assemble(self, stock: "Stock"):
        try:
            stock.start_assembling()
        except exceptions.NotEnoughMaterial as missing_materials:
            raise exceptions.InvalidTransition from missing_materials
        self.robot.state = Assembling(self.robot, stock=stock)


RobotId = int | Literal["Ghost"]
RobotIdGenerator = Iterator[RobotId]


class Robot:
    """Robot in a factory 🤖.
    Beware a ghost may be haunting the factory
    """

    def __init__(self, id_: RobotId):
        self.id_ = id_
        self.state: RobotState = Idle(self)

    @property
    def status(self) -> str:
        """Return robot state as string"""
        return str(self.state)

    @classmethod
    def from_id_generator(cls, id_generator: RobotIdGenerator) -> "Robot":
        """Build a new robot from a sequence"""
        return cls(next(id_generator))

    @classmethod
    def ghost(cls) -> "Robot":
        """Build a nullable robot 👻"""
        robot = cls(id_="Ghost")
        robot.state = Haunting(robot)
        return robot

    def __bool__(self) -> bool:
        return self.id_ == "Ghost"

    def move(self) -> None:
        """Move the robot"""
        self.state.move()

    def mine(self, material: Material) -> None:
        """Send robot to mine"""
        self.state.mine(material)

    def assemble(self, stock: "Stock") -> None:
        """Send robot to mine"""
        self.state.assemble(stock)


def robots_generator() -> Iterable[Robot]:
    """Generate some robots whose ids starting with 1"""
    counter = count(start=1)
    while True:
        yield Robot.from_id_generator(counter)


Foobar = uuid.UUID


class Stock:
    """Material stock"""

    def __init__(self):
        self.foos: int = 0
        self.bars: int = 0
        self.foobars: list[Foobar] = []

    def has_enough_material(self) -> bool:
        """Check if wa have enough material to build a foobar"""
        if self.foos < 1:
            logger.error("Not enough foos in stock!")
            return False
        if self.bars < 1:
            logger.error("Not enough bars in stock!")
            return False
        return True

    def start_assembling(self):
        """Begin to assemble a new foobar"""
        if not self.has_enough_material():
            raise exceptions.NotEnoughMaterial
        self.foos -= 1
        self.bars -= 1

    def end_assembling(self) -> Foobar:
        """A new Foobar is built 😂"""
        foobar = uuid.uuid4()
        self.foobars.append(foobar)
        return foobar


class RoboticFactory:
    """Outstanding Robotic factory 🏭"""

    def __init__(self, robots: list[Robot]) -> None:
        self.robots = robots
        self.stock = Stock()

    def get_robot(self, robot_id: int) -> Robot:
        """Get the robot with the given id"""
        for robot in self.robots:
            if robot.id_ == robot_id:
                return robot
        logger.error("Robot %s not found", robot_id)
        return Robot.ghost()

    def assemble(self, robot_id: int) -> None:
        """Say robot to assemble foobar"""
        robot = self.get_robot(robot_id)
        try:
            robot.assemble(self.stock)
        except exceptions.InvalidTransition:
            pass
