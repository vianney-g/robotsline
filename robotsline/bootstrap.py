from . import commands, handlers, models
from .settings import Settings


class Game:
    def __init__(self, settings: Settings = Settings()):
        self.factory = models.RoboticFactory.from_settings(settings)

    def execute(self, command: commands.Command) -> None:
        handlers.execute(command, on_factory=self.factory)
