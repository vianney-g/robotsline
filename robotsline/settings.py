"""Some constants"""
import dataclasses
from decimal import Decimal


@dataclasses.dataclass
class Settings:
    """Bundle of settings"""

    initial_robots_nb: int = 2
    assembly_success_rate: float = 0.6
    mining_bar_range_time: tuple[int, int] = (1, 2)
    foobars_selling_range: tuple[int, int] = (1, 5)
    robot_cost: tuple[int, int] = (3, 6)  # (money; foos)
    limit_of_robots_for_game_over: int = 30
