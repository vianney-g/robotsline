"""Domain models for a robotic factory"""
import abc
import dataclasses
import enum
import logging
import random
import uuid
from decimal import Decimal
from itertools import count
from typing import Iterable, Iterator, Literal, NewType, Optional

from . import exceptions
from .settings import Settings

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


class Material(abc.ABC):
    """A foe or a bar"""

    name: str
    where_to_find_it: Location
    mining_time: Seconds

    def __init__(self) -> None:
        self.id_ = uuid.uuid4()

    @classmethod
    def from_name(
        cls, material_name, mining_bar_range_time: tuple[int, int]
    ) -> "Material":
        """New material from name"""
        if material_name.lower() == "foo":
            return Foo()
        if material_name.lower() == "bar":
            return Bar.from_randomness(*mining_bar_range_time)
        raise exceptions.UnknownMaterial(material_name)


class Foo(Material):
    name: str = "foo"
    where_to_find_it: Location = Location.FOO_MINE
    mining_time = Seconds(1)


class Bar(Material):
    name: str = "bar"
    where_to_find_it: Location = Location.BAR_MINE

    def __init__(self, mining_time: Seconds):
        super().__init__()
        self.mining_time = mining_time

    @classmethod
    def from_randomness(cls, mining_time_min: int, mining_time_max: int) -> "Bar":
        mining_time = Seconds(random.randint(mining_time_min, mining_time_max))
        return cls(mining_time)


@dataclasses.dataclass(frozen=True)
class Foobar:
    """The final product"""

    foo: Foo
    bar: Bar
    price: Decimal = Decimal("1.00")


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


def robots_generator() -> Iterator[Robot]:
    """Generate some robots whose ids starting with 1"""
    counter = count(start=1)
    while True:
        yield Robot.from_id_generator(counter)


@dataclasses.dataclass
class Stock:
    """Material stock"""

    robots: list[Robot]
    foos: list[Foo] = dataclasses.field(default_factory=list)
    bars: list[Bar] = dataclasses.field(default_factory=list)
    foobars: list[Foobar] = dataclasses.field(default_factory=list)
    money: Decimal = Decimal("0.00")
    _robot_generator: Iterable[Robot] = dataclasses.field(default_factory=robots_generator)

    def add_robot(self) -> None:
        """Add a free robot to the factory"""
        self.robots.append(next(self._robot_generator))

    def has_enough_material(self) -> bool:
        """Check if wa have enough material to build a foobar"""
        if len(self.foos) < 1:
            logger.error("Not enough foos in stock!")
            return False
        if len(self.bars) < 1:
            logger.error("Not enough bars in stock!")
            return False
        return True

    def start_assembling(self) -> Foobar:
        """Begin to assemble a new foobar"""
        if not self.has_enough_material():
            raise exceptions.NotEnoughMaterial
        foo, bar = self.foos.pop(), self.bars.pop()
        return Foobar(foo, bar)

    def end_assembling_success(self, foobar: Foobar):
        """A new Foobar is built 😂"""
        self.foobars.append(foobar)

    def end_assembling_failure(self, foobar: Foobar):
        """Oh no!! 😥"""
        # we still saved a bar...
        self.bars.append(foobar.bar)

    def new_material(self, material: Material):
        """Add a new material in stock"""
        match material:
            case Foo():
                self.foos.append(material)
            case Bar():
                self.bars.append(material)

    def start_selling(self, min_nb: int, max_nb: int) -> list[Foobar]:
        """Get foobars to sell"""
        sell_nb = min((max_nb, len(self.foobars)))
        if sell_nb < min_nb:
            raise exceptions.NotEnoughMaterial("Not enough foobars")
        to_sell, self.foobars = self.foobars[:sell_nb], self.foobars[sell_nb:]
        return to_sell

    def sold(self, foobars: list[Foobar]):
        logger.info("%s Foobar(s) sold", len(foobars))
        self.money += sum(foobar.price for foobar in foobars)

    def buy_robot(self, required_money: Decimal, required_foos: int):
        if required_money > self.money:
            raise exceptions.NotEnoughMaterial("Not enough money")
        if required_foos > len(self.foos):
            raise exceptions.NotEnoughMaterial("Not enough foos")
        self.money -= required_money
        for _ in range(required_foos):
            self.foos.pop()

        self.add_robot()

    def get_robot(self, robot_id: int) -> Robot:
        """Get the robot with the given id"""
        for robot in self.robots:
            if robot.id_ == robot_id:
                return robot
        logger.error("Robot %s not found", robot_id)
        return Robot.ghost()


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

    def sell(self, stock: Stock, min_nb: int, max_nb: int) -> None:
        """Try to tell the robot to sell some foobars"""
        raise exceptions.InvalidTransition("Cannot sell foobar")

    def buy(self, stock: Stock, required_money: Decimal, required_foos: int) -> None:
        """Try to buy a robot"""
        raise exceptions.InvalidTransition("Cannot buy robot")

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
            self, robot: "Robot", foobar: Foobar, stock: Stock, assembly_success_rate: float
    ) -> None:
        super().__init__(robot, countdown=Seconds(2), location=self.LOCATION)
        self.stock = stock
        self.foobar = foobar
        self.assembly_success_rate = assembly_success_rate

    def __str__(self) -> str:
        return "Assembling a foobar..."

    def terminate(self) -> None:
        if random.random() <= self.assembly_success_rate:
            self.stock.end_assembling_success(self.foobar)
        else:
            self.stock.end_assembling_failure(self.foobar)
        self.robot.state = Idle(self.robot, location=self.location)


class Sell(RobotState):
    """Robot is selling"""

    LOCATION = Location.MATERIAL_STORE

    def __init__(self, robot: "Robot", stock: Stock, foobars: list[Foobar]) -> None:
        super().__init__(robot, countdown=Seconds(10), location=self.LOCATION)
        self.stock = stock
        self.foobars = foobars

    def __str__(self) -> str:
        return f"Selling {len(self.foobars)} foobar(s)..."

    def terminate(self) -> None:
        self.stock.sold(self.foobars)
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
            raise exceptions.InvalidTransition(f"Move to {Assembling.LOCATION} first")
        try:
            foobar = stock.start_assembling()
        except exceptions.NotEnoughMaterial as missing_materials:
            raise exceptions.InvalidTransition from missing_materials

        self.robot.state = Assembling(
            self.robot,
            foobar=foobar,
            stock=stock,
            assembly_success_rate=assembly_success_rate,
        )

    def sell(self, stock: Stock, min_nb: int, max_nb: int) -> None:
        """Try to sell between min and max foobar"""
        if not self.location is Sell.LOCATION:
            raise exceptions.InvalidTransition(f"Move to {Sell.LOCATION} first")
        foobars = stock.start_selling(min_nb, max_nb)
        self.robot.state = Sell(self.robot, stock=stock, foobars=foobars)

    def buy(self, stock: Stock, required_money: Decimal, required_foos: int) -> None:
        if not self.location is Location.ROBOTS_STORE:
            raise exceptions.InvalidTransition(f"Move to {Location.ROBOTS_STORE} first")
        stock.buy_robot(required_money, required_foos)


class RoboticFactory:
    """Outstanding Robotic factory 🏭"""

    def __init__(
        self,
        stock: Optional[Stock] = None,
        settings: Settings = Settings(),
    ) -> None:

        if stock is None:
            stock = Stock([])

        self.stock: Stock = stock
        self.seconds_left = Seconds(0)
        self.settings = settings

    def move(self, robot_id: int, destination: str) -> None:
        """Say robot to move"""
        true_destination = Location.by_name(destination.lower())
        robot = self.stock.get_robot(robot_id)
        robot.state.move(true_destination)

    def mine(self, robot_id: int, material: str) -> None:
        """Say robot to move"""
        robot = self.stock.get_robot(robot_id)
        true_material = Material.from_name(
            material, self.settings.mining_bar_range_time
        )
        robot.state.mine(true_material, self.stock)

    def assemble(self, robot_id: int) -> None:
        """Say robot to assemble foobar"""
        robot = self.stock.get_robot(robot_id)
        robot.state.assemble(self.stock, self.settings.assembly_success_rate)

    def sell(self, robot_id: int) -> None:
        """Say robot to sell foobars"""
        robot = self.stock.get_robot(robot_id)
        min_nb, max_nb = self.settings.foobars_selling_range
        robot.state.sell(self.stock, min_nb, max_nb)

    def buy_robot(self, robot_id: int) -> None:
        """Say robot to buy a new buddy"""
        robot = self.stock.get_robot(robot_id)
        required_money, required_foos = self.settings.robot_cost
        robot.state.buy(self.stock, Decimal(required_money), required_foos)

    def run_round(self) -> None:
        """Run a given round"""
        for robot in self.stock.robots:
            robot.run_round()
        self.seconds_left += 1

    def wait(self, seconds: int) -> None:
        """Simulate some seconds in the factory"""
        for _ in range(seconds):
            self.run_round()
