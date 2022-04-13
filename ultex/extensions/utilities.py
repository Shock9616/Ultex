"""
An extension that contains more utilitarian commands
such as random number generation or invite link sharing
"""

import datetime as dt
import os
import random
import smtplib

from email.mime.text import MIMEText as text

import hikari
import lightbulb
import wikipedia
import wolframalpha

plugin = lightbulb.Plugin("Utilities", "Exactly what it sounds like :)")


# ---------- Command functions ----------

# ----- Invite Command -----
@plugin.command()
@lightbulb.option("recipients", "List of people to invite", str, required=True)
@lightbulb.command("invite",
                   "Send an invite code to the specified email address(es)")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def invite_command(ctx: lightbulb.Context) -> None:
    """ Generate an invite code and send it
    to the specified email address(es) """

    recipients = list(ctx.options.recipients.split(" "))

    if len(recipients) > 1:
        response = "Sending invite email to "
        for i in range(len(recipients)):
            if i == len(recipients) - 1:
                response = response + "and " + recipients[i]
            else:
                response = response + recipients[i] + ", "
    else:
        response = "Sending invite email to " + recipients[0]

    await ctx.respond(response)

    ADDRESS = os.environ["BOT_EMAIL_ADDRESS"]
    PASSWORD = os.environ["BOT_EMAIL_PASSWD"]
    channel = ctx.get_channel()
    if not isinstance(channel, hikari.Snowflake) and channel is not None:
        link = await ctx.app.rest.create_invite(channel.id,
                                                max_uses=len(recipients))
    else:
        return

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(ADDRESS, PASSWORD)

    if ctx.get_guild() is not None:
        msg = text(str(f"Greetings earthling!\n\n{str(ctx.author)} has invited " +
                       f"you to join the {str(ctx.get_guild())} discord " +
                       "server.\nClick the link below to accept the invitation.\n" +
                       f"{str(link)}\n\nHope to talk to you soon!\n" +
                       f"{str(ctx.get_guild())}."))
        msg["Subject"] = f"Invite to {str(ctx.get_guild())}"
        msg["From"] = ADDRESS

        for recipient in recipients:
            msg["To"] = recipient
            server.sendmail(ADDRESS, recipient, msg.as_string())

        server.quit()

        await ctx.edit_last_response(response.replace("Sending", "Sent"))


# ----- Rand Command -----
@plugin.command()
@lightbulb.option("upper", "Upper bound", int, default=10)
@lightbulb.option("lower", "Lower bound", int, default=0)
@lightbulb.command("rand", "Generate a random number", aliases=["random"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def rand_command(ctx: lightbulb.Context) -> None:
    """ Generate a random number using the
    given bounds in lightbulb.Context """

    rand = random.randint(ctx.options.lower, ctx.options.upper)
    await ctx.respond(f"Your random number is {rand}")


# ----- Search Command -----
@plugin.command()
@lightbulb.option("query", "Search query", str)
@lightbulb.command("search", "Generate a random number")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def search_command(ctx: lightbulb.Context) -> None:
    """ Search for literally everything
    The bot isn't always correct but it will certainly try its best to be """
    query = ctx.options.query
    await ctx.respond(f"Searching for: {query}...")
    wolf = wolframalpha.Client(os.environ["WOLFRAMALPHA_KEY"])

    try:
        res = wolf.query(query)
        answer = next(res.results).text
    except (StopIteration, AttributeError):
        try:
            answer = wikipedia.summary(query, sentences=2)
        except wikipedia.exceptions.PageError:
            await ctx.respond("Sorry, there were no search results for your query.")
            return

    embed = hikari.Embed(
        title=query,
        colour=ctx.author.accent_colour,
        timestamp=dt.datetime.now(dt.timezone.utc)
    )

    embed.set_footer(text=f"Requested by {ctx.author.username}",
                     icon=ctx.author.avatar_url)
    embed.add_field(name="Search Results",
                    value=answer,
                    inline=False)

    await ctx.edit_last_response("", embed=embed)


# --------- Plugin Load and Unload Functions ----------


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)
