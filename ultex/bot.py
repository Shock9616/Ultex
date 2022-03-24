"""
Main bot file that controls the bot itself, its settings,
and the plugins that are loaded on startup
"""

import os
import aiohttp
import hikari
import lightbulb

bot = lightbulb.BotApp(
    token=os.environ["TOKEN"],
    default_enabled_guilds=int(os.environ["TEST_GUILD_ID"]),
    help_slash_command=True,
    intents=hikari.Intents.ALL,
    prefix=os.environ["PREFIX"],
)

bot.load_extensions_from("./ultex/extensions")


# ---------- Listener Functions ----------


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    """ Listener function for when the bot starts up """
    bot.d.aio_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    """ Listerner function for when the bot shuts down """
    await bot.d.aio_session.close()


# --------------------


def run() -> None:
    """ Run the bot. Use uvloop instead
    of asyncio if not on Windows """
    if os.name != "win32":
        import uvloop
        uvloop.install()

    bot.run()
