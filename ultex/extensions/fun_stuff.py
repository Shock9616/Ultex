"""
An extension that contains some fun commands like jokes
"""

import lightbulb
import random


plugin = lightbulb.Plugin("Fun Stuff", "Fun commands just for fun!")


# ---------- Command Functions ----------

# ----- Joke Command -----
@plugin.command()
@lightbulb.command("joke", "Tell a really bad joke", aliases=["dadjoke"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def joke_command(ctx: lightbulb.Context) -> None:
    """ Send a really bad joke """
    with open("data/jokes.txt", "r") as file:
        jokes = file.read().splitlines()
        joke = random.choice(jokes)
        await ctx.respond(f"{joke}")


# --------- Plugin Load and Unload Functions ----------


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)
