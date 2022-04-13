"""
An extension which provides an xp system based on users' messages
"""

import datetime as dt
import json

import hikari
import lightbulb

plugin = lightbulb.Plugin("Leveling", "XP leveling system")


# ---------- Command Functions ----------

# ----- XP/Level Command -----
@plugin.command()
@lightbulb.command("xp", "Send an embed with the command author's xp value",
                   aliases=["level"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def xp_command(ctx: lightbulb.Context) -> None:
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


# ----- Leaderboard Command -----
@plugin.command()
@lightbulb.command("leaderboard",
                  "Send an embed with the leaderboard and the author's rank")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def leaderboard_command(ctx: lightbulb.Context) -> None:
    """ Respond with an embed with the top 3 people
    on the leaderboard, and the author's rank """
    author = ctx.author
    top_users = [["", 0], ["", 0], ["", 0]]

    with open("data/users.json", "r") as file:
        users = json.load(file)

    for user in users:
        if users[f"{user}"]["xp"] > top_users[0][1]:
            top_users.insert(0, [user, users[f"{user}"]["xp"]])
            top_users.pop()
        elif users[f"{user}"]["xp"] > top_users[1][1]:
            top_users.insert(1, [user, users[f"{user}"]["xp"]])
            top_users.pop()
        elif users[f"{user}"]["xp"] > top_users[2][1]:
            top_users.insert(2, [user, users[f"{user}"]["xp"]])
            top_users.pop()

        print(top_users)

    embed = hikari.Embed(
        title=f"Server XP Leaderboard",
        colour=ctx.author.accent_colour,
        timestamp=dt.datetime.now(dt.timezone.utc)
    )

    embed.add_field(name=f"1. {top_users[0][0]} - XP: {top_users[0][1]}",
                    value=(f"2. {top_users[1][0]} - XP: {top_users[1][1]}\n" +
                           f"3. {top_users[2][0]} - XP: {top_users[2][1]}\n" +
                           "-------------------------------"),
                    inline=False)

    author_rank: int = 1
    author_xp: float = users[f"{author}"]["xp"]

    for user in users:
        if users[f"{user}"]["xp"] > users[f"{author}"]["xp"]:
            author_rank += 1

    embed.add_field(name=f"{author_rank}. {author} - XP: {author_xp}",
                    value="-------------------------------",
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
            old_level = 1
            users[f"{event.message.author}"] = {}
            users[f"{event.message.author}"]["xp"] = 10

        new_level = int(users[f"{event.message.author}"]["xp"] // 100) + 1
        if new_level > old_level:
            await event.message.respond((f"GG {event.message.author.username}!",
                                        "You have advanced to Level ",
                                        f"{new_level}!"))

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
