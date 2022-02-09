"""
The main entry point for the program.
"""

import os
import hikari
import lightbulb

bot = lightbulb.BotApp(
    token=os.environ["TOKEN"],
    default_enabled_guilds=int(os.environ["TEST_GUILD_ID"]),
    help_slash_command=True,
    intents=hikari.Intents.ALL,
    prefix="!",
)

bot.load_extensions_from("./ultex/extensions")


def run() -> None:
    if os.name != "win32":
        import uvloop
        uvloop.install()

    bot.run()
