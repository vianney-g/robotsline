"""Cli interface"""
import logging
from io import StringIO
from typing import Iterable

from robotsline import bootstrap, commands
from robotsline.cli.interactive_adapter import get_director
from robotsline.cli.screen import Cli

GameDirector = Iterable[tuple[commands.Command, str]]


_locations = [
    "cafeteria",
    "foo mine",
    "bar mine",
    "assembly line",
    "material store",
    "robots store",
    "on my way",
]

_logs = StringIO()
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    handlers=[logging.StreamHandler(_logs)],
)

_game = bootstrap.Game()
_gui = Cli(_game.factory.stock, _locations, _logs)

director: GameDirector = get_director(_game, _gui)
for cmd, instructions in director:
    _game.execute(cmd)
    _gui.redraw(instructions)
