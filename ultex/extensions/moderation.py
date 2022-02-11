"""
An extension which provides some moderation capabilities such
as automatically censoring bad language and limiting spam
"""

import time
import json
import hikari
import lightbulb

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
                with open("data/users.json", "r+") as file:
                    users = json.load(file)

                    if f"{user}" in users.keys():
                        if "swears" in users[f"{user}"].keys():
                            if users[f"{user}"]["swears"] < 10:
                                users[f"{user}"]["swears"] += 1
                                swear_count = users[f"{user}"]["swears"]
                                response = await event.message.respond(
                                    f"Hey {user}! No swearing on my Christian "
                                    "discord server! You have "
                                    f"{10 - swear_count} violations left until"
                                    " you will be banned.")
                                time.sleep(5)
                                await response.delete()
                            else:
                                await event.app.rest.ban_user(
                                    user=user.id,
                                    guild=event.get_guild(),
                                    reason="Excessive bad language")
                        else:
                            users[f"{user}"]["swears"] = 1
                            swear_count = users[f"{user}"]["swears"]
                            response = await event.message.respond(
                                f"Hey {user}! No swearing on my Christian "
                                f"discord server! You have {10 - swear_count} "
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
                            f"Hey {user}! No swearing on my Christian discord "
                            f"swerver! You have {10 - swear_count} violations "
                            "left until you will be banned.")
                        time.sleep(5)
                        await response.delete()
                        users[f"{user}"]["xp"] = -20

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
