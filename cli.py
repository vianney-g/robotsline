"""Cli interface"""
import logging
import sys
from io import StringIO

from robotsline import bootstrap
from robotsline.cli import ia_adapter, interactive_adapter
from robotsline.cli.screen import Cli

_logs = StringIO()
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    handlers=[logging.StreamHandler(_logs)],
)


def main(interactive: bool):
    game = bootstrap.Game()
    cli = Cli(game, _logs)

    if interactive:
        director = interactive_adapter.get_director(game, cli)
        cli.interactive_run(director)
    else:
        director = ia_adapter.get_director(game)
        cli.live_run(director)


if __name__ == "__main__":
    INTERACTIVE = False
    try:
        if sys.argv[1] == "-i":
            INTERACTIVE = True
    except IndexError:
        pass
    main(INTERACTIVE)
