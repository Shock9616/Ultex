"""
Main bot file that controls the bot itself, its settings,
and the plugins that are loaded on startup
"""

import hikari
import lightbulb
import logging

from pathlib import Path
from typing import Optional


class Bot(lightbulb.BotApp):
    def __init__(self,
                 token: str,
                 default_enabled_guilds: int,
                 help_slash_command: bool,
                 intents: hikari.Intents,
                 prefix: str,
                 excluded_extensions: Optional[list[str]]=None):
        super().__init__(
            token=token,
            default_enabled_guilds=default_enabled_guilds,
            help_slash_command=help_slash_command,
            intents=intents,
            prefix=prefix)
        self.excluded_extensions: list[str] = [] if excluded_extensions is None else excluded_extensions
        self._extensions: list[str] = [p.stem for p in Path(".").glob("./ultex/extensions/*.py")]
        self._LOGGER = logging.getLogger("lightbulb.app")

    def setup(self):
        """
        Set up the bot before running
        Ex. loading extensions
        """
        for ext in self._extensions:
            if ext not in self.excluded_extensions:
                self.load_extensions(f"ultex.extensions.{ext}")
            else:
                self._LOGGER.info(f"Extension excluded 'ultex.extensions.{ext}'")

    def run(self):
        self.setup()
        super().run()
