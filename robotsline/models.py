"""Domain models for a robotic factory"""
import enum


class Factory:
    """Outstanding Robotic factory 🏭"""

    def __init__(self, nb_robots: int) -> None:
        self.robots = [Robot() for _ in range(nb_robots)]


class RobotState(enum.Enum):
    """Robot occupation"""

    IDLE = "idle"


class Robot:
    """Robot of my factory 🤖"""

    def __init__(self):
        self.state: RobotState = RobotState.IDLE
