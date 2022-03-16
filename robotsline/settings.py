"""Some constants"""
import dataclasses


@dataclasses.dataclass
class Settings:
    """Bundle of settings"""

    assembly_success_rate: float = 0.6
    mining_bar_range_time: tuple[int, int] = (1, 2)
