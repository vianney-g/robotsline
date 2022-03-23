from datetime import timedelta
from io import StringIO
from typing import Iterable

from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import TextType

from robotsline import exceptions
from robotsline.bootstrap import Game
from robotsline.commands import Command
from robotsline.models import Robot, Stock

GameDirector = Iterable[tuple[Command, str]]


class Cli:
    """Gui representation of a stock"""

    def __init__(self, game: Game, logs: StringIO):
        self.console = Console()
        self.game = game

        self.locations = [
            "cafeteria",
            "foo mine",
            "bar mine",
            "assembly line",
            "material store",
            "robots store",
            "on my way",
        ]
        self.logs = logs

    @property
    def stock(self) -> Stock:
        return self.game.factory.stock

    @staticmethod
    def _robots_at_location(robots: list[Robot], location: str) -> Columns:
        def robot_to_panel(robot):
            return Panel(
                f"🤖 {robot.id_} [b]{robot.status}",
                style="Green" if robot.status == "Idle" else "Red",
            )

        robots_panels = [robot_to_panel(robot) for robot in robots]
        if not robots_panels:
            robots_panels = [Panel("👻 Nothing here 👻", style="White")]
        return Columns(robots_panels, title=f"[b]{location.upper()}")

    def _location(self, location: str) -> Panel:
        robots = [robot for robot in self.stock.robots if robot.location == location]
        return Panel(
            self._robots_at_location(robots, location=location),
            style="Black" if location == "on my way" else "Purple",
            width=30,
        )

    def _locations(self) -> Columns:
        locations_views = [self._location(location) for location in self.locations]
        return Columns(locations_views, title="[b]LOCATIONS", expand=False, equal=True)

    def _resources(self) -> Layout:
        timeleft = "{:0>8}".format(
            str(timedelta(seconds=self.game.factory.seconds_left))
        )
        resources = [
            f"[b]FOOS:[/b] {len(self.stock.foos)}",
            f"[b]BARS:[/b] {len(self.stock.bars)}",
            f"[b]FOOBARS:[/b] {len(self.stock.foobars)}",
            f"[b]💰[/b] ${self.stock.money}",
            f"[b]🤖[/b] {len(self.stock.robots)}",
            f"[b]⏲[/b] {timeleft}",
        ]
        columns = Columns(resources, title="[b]RESOURCES", expand=True)
        return Layout(columns, size=2)

    @staticmethod
    def _instructions(instructions: TextType) -> Panel:
        return Panel(instructions, title="[b]ℹ️ INSTRUCTIONS")

    def _logs(self) -> Panel:
        last_logs = self.logs.getvalue().splitlines()[-6:]
        displayed_logs = "\n".join(last_logs)
        return Panel(f"[b red]{displayed_logs}", title="[b]💻 LOGS")

    def _main_layout(self) -> Layout:
        main_layout = Layout()
        main_layout.split_column(
            self._resources(), self._locations(), Layout(name="events", size=10)
        )
        main_layout["events"].split_row(
            Layout(name="instructions"), Layout(self._logs(), name="logs")
        )
        return main_layout

    def main_layout(self, instructions: TextType) -> Layout:
        """Build the entire screen"""
        layout = self._main_layout()
        layout["instructions"].update(self._instructions(instructions))
        layout["logs"].update(self._logs())
        return layout

    def refresh(self, instructions: TextType):
        """Manually refresh the screen"""
        self.console.print(self.main_layout(instructions))

    def live_run(self, director: GameDirector):
        """Run game in auto refresh mode"""
        with Live(self.main_layout("")) as live:
            for cmd, instructions in director:
                try:
                    self.game.execute(cmd)
                except exceptions.GameOver:
                    self.console.print("End of game!")
                    return
                live.update(self.main_layout(instructions))

    def interactive_run(self, director: GameDirector):
        """Run game in interactive mode"""
        for cmd, instructions in director:
            self.refresh(instructions)
            try:
                self.game.execute(cmd)
            except exceptions.GameOver:
                self.console.print("End of game!")
                return
