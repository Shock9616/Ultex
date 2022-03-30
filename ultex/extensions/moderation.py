"""
An extension which provides some moderation capabilities such
as automatically censoring bad language and limiting spam
"""

import time
import json
import hikari
import lightbulb
import datetime as dt
from typing import Optional

plugin = lightbulb.Plugin("Moderation", "Boring moderation stuff")


# ---------- Listener Functions ----------

# ----- Auto-censoring Listener -----
@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message_create(event: hikari.GuildMessageCreateEvent) -> None:
    """ Listen for messages and censor/warn
    the author if they use bad language """
    if event.is_bot or not event.content:
        return

    words = event.content.lower().split()
    user = event.message.author
    with open("data/bad_language.txt", "r") as file:
        bad_words = file.read().splitlines()

    for word in words:
        if word in bad_words:
            await event.message.delete()
            with open("data/users.json", "r") as file:
                users = json.load(file)

            if f"{user}" in users.keys():
                if "swears" in users[f"{user}"].keys():
                    if users[f"{user}"]["swears"] < 10:
                        users[f"{user}"]["swears"] += 1
                        swear_count = users[f"{user}"]["swears"]
                        response = await event.message.respond(
                            f"Hey {user}! No swearing on my Christian " +
                            "discord server! You have " +
                            f"{10 - swear_count} violations left until" +
                            " you will be banned.")
                        time.sleep(5)
                        await response.delete()
                    else:
                        await event.app.rest.ban_user(
                            user=user.id,
                            guild=event.guild_id,
                            reason="Excessive bad language")
                else:
                    users[f"{user}"]["swears"] = 1
                    swear_count = users[f"{user}"]["swears"]
                    response = await event.message.respond(
                        f"Hey {user}! No swearing on my Christian " +
                        f"discord server! You have {10 - swear_count} " +
                        "violations left until you will be banned.")
                    time.sleep(5)
                    await response.delete()

                if "xp" in users[f"{user}"].keys():
                    users[f"{user}"]["xp"] -= 20
                else:
                    users[f"{user}"]["xp"] = -20

            else:
                users[f"{user}"] = {}
                users[f"{user}"]["swears"] = 1
                swear_count = users[f"{user}"]["swears"]
                response = await event.message.respond(
                    f"Hey {user}! No swearing on my Christian discord " +
                    f"swerver! You have {10 - swear_count} violations " +
                    "left until you will be banned.")
                time.sleep(5)
                await response.delete()
                users[f"{user}"]["xp"] = -20

            with open("data/users.json", "w") as file:
                file.seek(0)
                json.dump(users, file, indent=4)
                file.truncate()


# ---------- Command Functions (All server owner only) ----------

# ----- Kick Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to kick from the guild",
                  hikari.PartialUser, required=True)
@lightbulb.option("reason", "Reason for kicking the user", str, default="")
@lightbulb.command("kick", "Kick a user from the guild")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def kick_command(ctx: lightbulb.Context) -> None:
    """ Kick a user from the guild """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        user: hikari.PartialUser = ctx.options.user
        if user is not None:
            await guild.kick(
                user=int(ctx.options.user.strip("<>!@")),
                reason=ctx.options.reason
            )
            await ctx.respond(f"Kicked user {ctx.options.user}")
        else:
            await ctx.respond("Sorry that user doesn't exist")


# ----- Ban Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to ban from the guild",
                  hikari.PartialUser, required=True)
@lightbulb.option("reason", "Reason for banning the user", str, default="")
@lightbulb.command("ban", "Ban a user from the guild")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ban_command(ctx: lightbulb.Context) -> None:
    """ Ban a user from the guild """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        user: hikari.PartialUser = ctx.options.user
        if user is not None:
            await guild.ban(
                user=int(ctx.options.user.strip("<>!@")),
                reason=ctx.options.reason
            )
            await ctx.respond(f"Banned user {ctx.options.user}")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Unban Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to unban",
                  hikari.PartialUser, required=True)
@lightbulb.command("unban", "Unban a user from the guild")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def unban_command(ctx: lightbulb.Context) -> None:
    """ Unban a user from the guild """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        user: hikari.PartialUser = ctx.options.user
        if user is not None:
            await guild.unban(
                user=int(ctx.options.user.strip("<>!@")),
            )
            await ctx.respond(f"Unbanned user {ctx.options.user}")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Mute Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("limit", "Length of time to mute the user (minutes)",
                  int, required=True)
@lightbulb.option("user", "User to mute",
                  hikari.PartialUser, required=True)
@lightbulb.command("mute", "Mute a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def mute_command(ctx: lightbulb.Context) -> None:
    """ Mute a user """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        member: Optional[hikari.PartialUser] = guild.get_member(int(ctx.options.user.strip("<>!@")))
        if member is not None:
            await member.edit(communication_disabled_until=dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes = ctx.options.limit))
            await ctx.respond(f"Muted {ctx.options.user} for {ctx.options.limit} minute(s)")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Unmute Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to unmute",
                  hikari.PartialUser, required=True)
@lightbulb.command("unmute", "Unmute a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def unmute_command(ctx: lightbulb.Context) -> None:
    """ Unmute a user """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        member: Optional[hikari.PartialUser] = guild.get_member(int(ctx.options.user.strip("<>!@")))
        if member is not None:
            await member.edit(communication_disabled_until=dt.datetime.now(dt.timezone.utc))
            await ctx.respond(f"Unmuted {ctx.options.user}")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Deafen Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to deafen",
                  hikari.PartialUser, required=True)
@lightbulb.command("deafen", "Deafen a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def deafen_command(ctx: lightbulb.Context) -> None:
    """ Deafen a user """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        member: Optional[hikari.PartialUser] = guild.get_member(int(ctx.options.user.strip("<>!@")))
        if member is not None:
            await member.edit(deaf=True)
            await ctx.respond(f"Deafened {ctx.options.user}")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Deafen Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("user", "User to undeafen",
                  hikari.PartialUser, required=True)
@lightbulb.command("undeafen", "Undeafen a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def undeafen_command(ctx: lightbulb.Context) -> None:
    """ Undeafen a user """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        member: Optional[hikari.PartialUser] = guild.get_member(int(ctx.options.user.strip("<>!@")))
        if member is not None:
            await member.edit(deaf=False)
            await ctx.respond(f"Undeafened {ctx.options.user}")
        else:
            await ctx.respond("Sorry, that user doesn't exist")


# ----- Members Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("role", "Role to list members of",
                  hikari.Role, required=True)
@lightbulb.command("members",
                   "Respond with up to 20 members of the given role")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def members_command(ctx: lightbulb.Context) -> None:
    """ Respond with up to 20 members of the given role """
    guild: Optional[hikari.Guild] = ctx.get_guild()
    if guild is not None:
        role: Optional[hikari.Role] = guild.get_role(ctx.options.role)
        if role is not None:
            role_members: list[str] = []
            for memb in guild.get_members():
                if len(role_members) > 20:
                    break

                member: Optional[hikari.Member] = guild.get_member(memb)
                if member is not None:
                    if role.id in member.role_ids:
                        role_members.append(member.display_name)
            members: str = ", ".join(role_members)
            await ctx.respond(f"Members of role '{ctx.options.role}' - {members}")

        else:
            await ctx.respond(f"Sorry, that role doesn't exist")


# ---------- Plugin Load and Unload Functions ----------


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)
