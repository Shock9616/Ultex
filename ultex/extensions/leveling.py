"""
An extension which provides an xp system based on users' messages
"""

import json
import datetime as dt

import hikari
import lightbulb

plugin = lightbulb.Plugin("Leveling", "XP leveling system")


# ---------- Command Functions ----------

# ----- XP/Level Command -----
@plugin.command()
@lightbulb.command("xp", "Send a message with the command author's xp value",
                   aliases=["level"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def xp(ctx: lightbulb.Context) -> None:
    """ Respond with an embed with the command
    author's xp value and level """
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


# ---------- Listener Functions ----------

# ----- XP/Level Up Listener -----
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
                old_level = (
                    int(users[f"{event.message.author}"]["xp"] // 100) + 1)
                users[f"{event.message.author}"]["xp"] += round(
                    10 / old_level, 2)
            else:
                old_level = 1
                users[f"{event.message.author}"]["xp"] = 10

        else:
            users[f"{event.message.author}"] = {}
            users[f"{event.message.author}"]["xp"] = 10

        new_level = int(users[f"{event.message.author}"]["xp"] // 100) + 1
        if new_level > old_level:
            await event.message.respond(f"GG {event.message.author.username}!"
                                        "You have advanced to Level "
                                        f"{new_level}!")

        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()


# --------- Plugin Load and Unload Functions ----------


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)
