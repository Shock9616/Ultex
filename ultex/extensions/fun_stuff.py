"""
An extension that contains some fun commands like jokes
"""

import random
import lightbulb


plugin = lightbulb.Plugin("Fun Stuff", "Utility commands just for utility!")


@plugin.command()
@lightbulb.command("joke", "Tell a really bad joke", aliases=["dadjoke"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def joke(ctx: lightbulb.Context) -> None:
    """ Send a really bad joke """
    with open("data/jokes.txt", "r") as file:
        jokes = file.read().splitlines()
        joke = random.choice(jokes)
        await ctx.respond(f"{joke}")


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plubins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
