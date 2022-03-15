"""Domain specific exceptions"""


class DomainError(Exception):
    """Base class for domain specific errors"""


class InvalidTransition(DomainError):
    """Cannot change robot state"""


class NotEnoughMaterial(DomainError):
    """Not enough material to build foobar"""
