"""Domain specific exceptions"""


class InvalidTransition(Exception):
    """Cannot change robot state"""


class UnknownMaterial(Exception):
    """Mining material not dealt by our factory"""
