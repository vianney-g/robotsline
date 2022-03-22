"""Human cli"""
from typing import Any, Iterable, Type

from rich.prompt import IntPrompt, Prompt

from .. import bootstrap, commands
from . import screen


class _InteractiveDirector:

    interactive_commands = [
        commands.MoveRobot,
        commands.Mine,
        commands.Assemble,
        commands.Wait,
        commands.SellFoobars,
        commands.BuyRobot,
    ]

    def __init__(self, game: bootstrap.Game, gui: screen.Cli):
        self.game = game
        self.gui = gui

    def commands_gen(self) -> Iterable[tuple[commands.Command, str]]:
        while True:
            cmd_id = self._ask_command_id()
            yield self._build_cmd(cmd_id)

    def _build_cmd(self, cmd_id: int):
        cmd_type = self.interactive_commands[cmd_id]
        cmd_params = cmd_type.__annotations__
        kwargs = {}
        for arg_name, arg_type in cmd_params.items():
            self.gui.redraw(f"Enter a valid {arg_type.__name__} for {arg_name}")
            kwargs[arg_name] = self._ask(arg_type)
        instance = cmd_type(**kwargs)
        return instance, ""

    def _ask(self, arg_type: type, **kwargs) -> Any:
        prompts = {int: IntPrompt, str: Prompt}
        prompt = prompts.get(arg_type, Prompt)
        return prompt.ask("", console=self.gui.console, **kwargs)

    def _ask_command_id(self) -> int:
        choices = range(1, len(self.interactive_commands) + 1)
        instructions = "\n".join(
            self._cmd_instruction(choice, cmd)
            for choice, cmd in zip(choices, self.interactive_commands)
        )
        self.gui.redraw(instructions)
        choice = IntPrompt.ask(
            "", choices=[str(c) for c in choices], console=self.gui.console
        )
        return choice - 1

    def _cmd_instruction(self, entry: int, cmd: Type[commands.Command]) -> str:
        return f"[b]{entry}:[/b] {cmd.__doc__}"


def get_director(
    game: bootstrap.Game, gui: screen.Cli
) -> Iterable[tuple[commands.Command, str]]:
    return _InteractiveDirector(game, gui).commands_gen()
