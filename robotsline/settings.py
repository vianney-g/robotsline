"""Some constants"""
import dataclasses


@dataclasses.dataclass
class Settings:
    """Bundle of settings"""
    assembly_success_rate: float = 0.6
