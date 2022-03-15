"""Domain specific exceptions"""


class DomainError(Exception):
    """Base class for domain specific errors"""


class InvalidTransition(DomainError):
    """Cannot change robot state"""


class NotEnoughMaterial(DomainError):
    """Not enough material to build foobar"""


class UnknownLocation(DomainError):
    """We don't know where you are 🤷"""
