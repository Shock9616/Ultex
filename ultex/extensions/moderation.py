"""
An extension which provides some moderation capabilities such
as automatically censoring bad language and limiting spam
"""

import lightbulb

plugin = lightbulb.Plugin("Moderation", "Boring moderation stuff")


def placeholder():
    """ This function is a placeholder
    for future moderation code """
    pass


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plubins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
