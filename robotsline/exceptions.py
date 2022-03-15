"""Domain specific exceptions"""


class InvalidTransition(Exception):
    """Cannot change robot state"""

class NotEnoughMaterial(Exception):
    """Not enough material to build foobar"""
