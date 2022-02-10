"""
An extension which provides an xp system based on users' messages
"""

import json
import datetime as dt

import hikari
import lightbulb

plugin = lightbulb.Plugin("Leveling", "XP leveling system")


@plugin.command()
@lightbulb.command("xp", "Send a message with the command author's xp value", aliases=["level"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def xp(ctx: lightbulb.Context) -> None:
    """ Send a message with the command author's xp value """
    with open("data/users.json", "r") as file:
        users = json.load(file)
        user = ctx.author
        xp = users[f"{user}"]["xp"]
        level = xp // 100

    embed = hikari.Embed(
        title=f"{user}'s XP",
        colour=ctx.author.accent_colour,
        timestamp=dt.datetime.now(dt.timezone.utc)
    )

    embed.add_field(name=f"Level: {level}",
                    value=f"XP: {xp}",
                    inline=False)

    await ctx.respond("", embed=embed)


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message_create(event: hikari.GuildMessageCreateEvent) -> None:
    """ Listen for messages and give
    XP to the users who sent them """
    if event.is_bot or not event.content:
        return

    with open("data/users.json", "r+") as file:
        users = json.load(file)

        if f"{event.message.author}" in users.keys():
            if "xp" in users[f"{event.message.author}"].keys():
                users[f"{event.message.author}"]["xp"] += 5
            else:
                users[f"{event.message.author}"]["xp"] = 5

        else:
            users[f"{event.message.author}"] = {}
            users[f"{event.message.author}"]["xp"] = 5

        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)
