"""Domain models for a robotic factory"""
import abc
import dataclasses
import enum
import logging
import random
import uuid
from itertools import count
from typing import Counter, Iterable, Iterator, Literal, NewType, Optional, Protocol

from . import exceptions, settings

logger = logging.getLogger(__name__)

Seconds = NewType("Seconds", int)


class Location(enum.Enum):
    """Where robots can go"""

    CAFETERIA = "cafeteria"
    ON_MY_WAY = "on my way..."
    FOO_MINE = "foo mine"
    BAR_MINE = "bar mine"
    ASSEMBLY_LINE = "assembly line"
    MATERIAL_STORE = "material store"
    ROBOTS_STORE = "robots store"

    @classmethod
    def by_name(cls, name: str) -> "Location":
        """Get location by name or raise UnknownLocation"""
        try:
            return cls(name)
        except ValueError as bad_location:
            raise exceptions.UnknownLocation(name) from bad_location


@dataclasses.dataclass
class Material:
    name: str
    where_to_find_it: Location
    mining_time: Seconds

    @classmethod
    def from_name(cls, material_name) -> "Material":
        """New material from name"""
        if material_name.lower() == "foo":
            return Material(
                name="foo",
                where_to_find_it=Location.FOO_MINE,
                mining_time=Seconds(1),
            )
        if material_name.lower() == "bar":
            return Material(
                name="bar",
                where_to_find_it=Location.BAR_MINE,
                mining_time=Seconds(1),
            )
        raise exceptions.UnknownMaterial(material_name)


Foobar = uuid.UUID


class Stock:
    """Material stock"""

    def __init__(
        self, foos_nb=0, bars_nb=0, foobars: Optional[list[Foobar]] = None
    ) -> None:
        self.materials = Counter(foo=foos_nb, bar=bars_nb)
        if foobars is None:
            foobars = []
        self.foobars: list[Foobar] = foobars

    @property
    def foos(self) -> int:
        """Get nb of foos in stock"""
        return self.materials["foo"]

    @property
    def bars(self) -> int:
        """Get nb of bars in stock"""
        return self.materials["bar"]

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
        self.materials["foo"] -= 1
        self.materials["bar"] -= 1

    def end_assembling_success(self):
        """A new Foobar is built 😂"""
        foobar = uuid.uuid4()
        self.foobars.append(foobar)

    def end_assembling_failure(self):
        """Oh no!! 😥"""
        # we still saved a bar...
        self.materials["bar"] += 1

    def new_material(self, material: Material):
        """Add a new material in stock"""
        self.materials[material.name] += 1


class RobotState(abc.ABC):
    """Abstract robot state"""

    def __init__(self, robot: "Robot", countdown: Seconds, location: Location) -> None:
        self.robot = robot
        self.countdown = countdown
        self.location = location

    def __str__(self) -> str:
        return self.__class__.__name__

    def idle(self, location: Location) -> None:
        """Set robot to idle state"""
        self.robot.state = Idle(self.robot, location)

    def move(self, destination: Location) -> None:
        """Try to move the robot"""
        raise exceptions.InvalidTransition(f"Cannot move robot {self.robot}")

    def mine(self, material: Material, stock: Stock) -> None:
        """Try to send the robot to mine"""
        raise exceptions.InvalidTransition(f"Cannot send robot {self.robot} to mine.")

    def assemble(self, stock: Stock, assembly_success_rate: float) -> None:
        """Try to send the robot to assembly line"""
        raise exceptions.InvalidTransition(
            f"Cannot send robot {self.robot} to assembly line."
        )

    def haunt(self):
        """Try to make the robot haunting"""
        if self.robot:
            raise exceptions.InvalidTransition("Robot is not a ghost")
        self.robot.state = Haunting(self.robot)

    def terminate(self) -> None:
        """Task is done"""

    def run_round(self) -> None:
        """A second of time..."""
        self.countdown -= Seconds(1)
        if self.countdown == Seconds(0):
            self.terminate()


class Haunting(RobotState):
    """👻"""

    def __init__(self, robot: "Robot"):
        location = Location.ON_MY_WAY
        countdown = Seconds(999_999_999)
        super().__init__(robot, countdown, location)


class Moving(RobotState):
    """Robot is 🚶"""

    DURATION: Seconds = Seconds(5)

    def __init__(self, robot: "Robot", destination: Location):
        super().__init__(robot, self.DURATION, Location.ON_MY_WAY)
        self.destination = destination

    def terminate(self) -> None:
        self.robot.state = Idle(self.robot, location=self.destination)


class Mining(RobotState):
    """Robot is ⛏"""

    def __init__(self, robot: "Robot", material: Material, stock: Stock) -> None:
        super().__init__(
            robot,
            countdown=material.mining_time,
            location=material.where_to_find_it,
        )
        self.material = material
        self.stock = stock

    def __str__(self) -> str:
        return f"Mining {self.material.name} at {self.location.value.title()}"

    def terminate(self) -> None:
        self.stock.new_material(self.material)
        self.robot.state = Idle(self.robot, self.location)


class Assembling(RobotState):
    """Robot is assembling"""

    LOCATION = Location.ASSEMBLY_LINE

    def __init__(
        self, robot: "Robot", stock: Stock, assembly_success_rate: float
    ) -> None:
        super().__init__(robot, countdown=Seconds(2), location=self.LOCATION)
        self.stock = stock
        self.assembly_success_rate = assembly_success_rate

    def __str__(self) -> str:
        return "Assembling a foobar..."

    def terminate(self) -> None:
        if random.random() <= self.assembly_success_rate:
            self.stock.end_assembling_success()
        else:
            self.stock.end_assembling_failure()
        self.robot.state = Idle(self.robot, location=self.location)


class Idle(RobotState):
    """Robot is sleeping 😴"""

    def __init__(self, robot: "Robot", location: Location) -> None:
        super().__init__(robot, countdown=Seconds(0), location=location)

    def move(self, destination: Location):
        self.robot.state = Moving(self.robot, destination)

    def mine(self, material: Material, stock: Stock):
        if self.location is material.where_to_find_it:
            self.robot.state = Mining(self.robot, material, stock)
        raise exceptions.InvalidTransition(
            f"Move to {material.where_to_find_it} before mining {material}"
        )

    def assemble(self, stock: Stock, assembly_success_rate: float):
        if not self.location is Assembling.LOCATION:
            raise exceptions.InvalidTransition(f"Move to {Assembling.location} first")
        try:
            stock.start_assembling()
        except exceptions.NotEnoughMaterial as missing_materials:
            raise exceptions.InvalidTransition from missing_materials

        self.robot.state = Assembling(
            self.robot,
            stock=stock,
            assembly_success_rate=assembly_success_rate,
        )


RobotId = int | Literal["Ghost"]
RobotIdGenerator = Iterator[RobotId]


class Robot:
    """Robot in a factory 🤖.
    Beware a ghost may be haunting the factory
    """

    def __init__(self, id_: RobotId, location: Location = Location.CAFETERIA):
        self.id_ = id_
        self.state: RobotState = Idle(self, location)

    def run_round(self) -> None:
        self.state.run_round()

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


def robots_generator() -> Iterable[Robot]:
    """Generate some robots whose ids starting with 1"""
    counter = count(start=1)
    while True:
        yield Robot.from_id_generator(counter)


class RoboticFactory:
    """Outstanding Robotic factory 🏭"""

    def __init__(
        self,
        robots: list[Robot],
        stock: Optional[Stock] = None,
        assembly_success_rate: float = settings.ASSEMBLY_SUCCESS_RATE,
    ) -> None:
        if stock is None:
            stock = Stock()

        self.robots = robots
        self.stock: Stock = stock
        self.seconds_left = Seconds(0)
        self.assembly_success_rate = assembly_success_rate

    def get_robot(self, robot_id: int) -> Robot:
        """Get the robot with the given id"""
        for robot in self.robots:
            if robot.id_ == robot_id:
                return robot
        logger.error("Robot %s not found", robot_id)
        return Robot.ghost()

    def move(self, robot_id: int, destination: str) -> None:
        """Say robot to move"""
        true_destination = Location.by_name(destination.lower())
        robot = self.get_robot(robot_id)
        robot.state.move(true_destination)

    def mine(self, robot_id: int, material: str) -> None:
        """Say robot to move"""
        robot = self.get_robot(robot_id)
        robot.state.mine(Material.from_name(material), self.stock)

    def assemble(self, robot_id: int) -> None:
        """Say robot to assemble foobar"""
        robot = self.get_robot(robot_id)
        robot.state.assemble(self.stock, self.assembly_success_rate)

    def run_round(self) -> None:
        """Run a given round"""
        for robot in self.robots:
            robot.run_round()
        self.seconds_left += 1

    def wait(self, seconds: int) -> None:
        """Simulate some seconds in the factory"""
        for _ in range(seconds):
            self.run_round()
