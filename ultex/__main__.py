"""
A rewrite of the Ultex Discord bot using Hikari
due to the discontinuation of Discord.py
"""

import aiohttp
import hikari
import os

from ultex.bot import Bot

if __name__ == "__main__":
    bot = Bot(
        token=os.environ["TOKEN"],
        default_enabled_guilds=int(os.environ["TEST_GUILD_ID"]),
        help_slash_command=True,
        intents=hikari.Intents.ALL,
        prefix=os.environ["PREFIX"],
        excluded_extensions=["music"]
    )

    # ---------- Listener Functions ----------

    @bot.listen()
    async def on_starting(event: hikari.StartingEvent) -> None:
        """ Listener function for when the bot starts up """
        bot.d.aio_session = aiohttp.ClientSession()


    @bot.listen()
    async def on_stopping(event: hikari.StoppingEvent) -> None:
        """ Listerner function for when the bot shuts down """
        await bot.d.aio_session.close()

    # Use uvloop instead of asyncio if not being run on windows
    if os.name != "win32":
        import uvloop
        uvloop.install()

    bot.run()
