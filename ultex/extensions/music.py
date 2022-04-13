"""
An extension that adds functionality for
playing music in a user's voice channel
"""

import datetime as dt
import logging
import os
import random  # TODO: Add shuffle command

from typing import Optional

import hikari
import lightbulb

import lavasnek_rs

plugin = lightbulb.Plugin("Music")

TOKEN = os.environ["TOKEN"]
LAVALINK_PASSWORD = os.environ["LAVALINK_PASSWORD"]
PREFIX = os.environ["PREFIX"]
HIKARI_VOICE = True


class EventHandler:
    """ Events from the Lavalink server """

    async def track_start(self,
                          _: lavasnek_rs.Lavalink,
                          event: lavasnek_rs.TrackStart) -> None:
        logging.info("Track started on guild: %s", event.guild_id)

    async def track_finish(self,
                           _: lavasnek_rs.Lavalink,
                           event: lavasnek_rs.TrackFinish) -> None:
        logging.info("Track finished on guild: %s", event.guild_id)

    async def track_exception(self,
                              lavalink: lavasnek_rs.Lavalink,
                              event: lavasnek_rs.TrackException) -> None:
        logging.warning("Track exception event happened on guild: %d", event.guild_id)

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not node:
            return

        if skip and not node.queue and not node.now_playing:
            await lavalink.stop(event.guild_id)


# ---------- Private Functions ----------


async def _join(ctx: lightbulb.Context) -> Optional[hikari.Snowflake]:
    assert ctx.guild_id is not None

    states = plugin.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]

    if not voice_state:
        await ctx.respond("Connect to a voice channel first.")
        return None

    channel_id = voice_state[0].channel_id

    if HIKARI_VOICE:
        assert ctx.guild_id is not None

        await plugin.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=False)
        connection_info = await plugin.bot.d.lavalink.wait_for_full_connection_info_insert(ctx.guild_id)

    else:
        try:
            connection_info = await plugin.bot.d.lavalink.join(ctx.guild_id, channel_id)
        except TimeoutError:
            await ctx.respond(
                "I was unable to connect to the voice channel, maybe missing permissions? or some internal issue."
            )
            return None

    await plugin.bot.d.lavalink.create_session(connection_info)

    return channel_id


@plugin.listener(hikari.ShardReadyEvent)
async def start_lavalink(event: hikari.ShardReadyEvent) -> None:
    """ Event that triggers when the hikari gateway is ready """

    builder = (
        # TOKEN can be an empty string if not using lavasnek's discord gateway
        lavasnek_rs.LavalinkBuilder(event.my_user.id, TOKEN)
    )

    if HIKARI_VOICE:
        builder.set_start_gateway(False)

    lava_client = await builder.build(EventHandler())

    plugin.bot.d.lavalink = lava_client


# ---------- Command Functions ----------


# ----- Join Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("join",
                   "Joins the voice channel you are in.",
                   aliases=["connect"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join_command(ctx: lightbulb.Context) -> None:
    """ Joins the voice channel you are in """
    channel_id = await _join(ctx)

    if channel_id:
        await ctx.respond(f"Joined <#{channel_id}>")


# ----- Leave Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("leave",
                   "Leaves the current voice channel and clears the queue.",
                   aliases=["disconnect"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def leave_command(ctx: lightbulb.Context) -> None:
    """ Leaves the voice channel the bot is in, clearing the queue """

    await plugin.bot.d.lavalink.destroy(ctx.guild_id)

    if HIKARI_VOICE:
        if ctx.guild_id is not None:
            await plugin.bot.update_voice_state(ctx.guild_id, None)
            await plugin.bot.d.lavalink.wait_for_connection_info_remove(ctx.guild_id)
    else:
        await plugin.bot.d.lavalink.leave(ctx.guild_id)

    await plugin.bot.d.lavalink.remove_guild_node(ctx.guild_id)
    await plugin.bot.d.lavalink.remove_guild_from_loops(ctx.guild_id)

    await ctx.respond("Left voice channel")


# ----- Play Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("song",
                  "The song to search for.",
                  modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("play",
                   "Searches on youtube, or adds the URL to the queue.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def play_command(ctx: lightbulb.Context) -> None:
    """ Searches the query on youtube, or adds the URL to the queue """

    song = ctx.options.song

    if not song:
        await ctx.respond("Please specify a query.")
        return None

    con = plugin.bot.d.lavalink.get_guild_gateway_connection_info(ctx.guild_id)
    # Join the user's voice channel if the bot is not in one
    if not con:
        await _join(ctx)

    # Search for the song, auto_search will get the track from a url if
    # possible, otherwise it will search the query on youtube
    query_information = await plugin.bot.d.lavalink.auto_search_tracks(song)

    if not query_information.tracks:  # tracks is empty
        await ctx.respond("Could not find any video of the search query.")
        return

    try:
        # `.requester()` To set who requested the track, so you can show it on now-playing or queue
        # `.queue()` To add the track to the queue rather than starting to play the track now
        await plugin.bot.d.lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(ctx.author.id).queue()
    except lavasnek_rs.NoSessionPresent:
        await ctx.respond(f"Use `{PREFIX}join` first")
        return

    await ctx.respond(f"Added to queue: {query_information.tracks[0].info.title}")


# ----- Stop Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("stop", "Stops the current song (skip to continue).")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop_command(ctx: lightbulb.Context) -> None:
    """ Stops the current song (skip to continue) """

    await plugin.bot.d.lavalink.stop(ctx.guild_id)
    await ctx.respond("Stopped playing")


# ----- Skip Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("skip", "Skips the current song.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def skip_command(ctx: lightbulb.Context) -> None:
    """ Skips the current song """

    skip = await plugin.bot.d.lavalink.skip(ctx.guild_id)
    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)

    if not skip:
        await ctx.respond("Nothing to skip")
    else:
        # If the queue is empty, the next track won't
        # start playing (because there isn't one),
        # so we stop the player
        if not node.queue and not node.now_playing:
            await plugin.bot.d.lavalink.stop(ctx.guild_id)

        await ctx.respond(f"Skipped: {skip.track.info.title}")


# ----- Pause Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pause", "Pauses the current song.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause_command(ctx: lightbulb.Context) -> None:
    """ Pauses the current song """

    await plugin.bot.d.lavalink.pause(ctx.guild_id)
    await ctx.respond("Paused player")


# ----- Resume Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("resume", "Resumes playing the current song.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def resume_command(ctx: lightbulb.Context) -> None:
    """ Resumes playing the current song """

    await plugin.bot.d.lavalink.resume(ctx.guild_id)
    await ctx.respond("Resumed player")


# ----- Shuffle Command -----
@plugin.command()
@lightbulb.command("shuffle", "Shuffles the tracks left in the queue.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def shuffle_command(ctx: lightbulb.Context) -> None:
    """ Shuffles the tracks left in the queue """
    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)
    queue = node.queue()

    if not node or not queue:
        await ctx.respond("Nothing is playing at the moment.")
        return

    queue = random.shuffle(queue)

    node.set_data(queue)

    await ctx.respond("Shuffled queue")


# ----- Now Playing Command -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("nowplaying",
                   "Gets the song that's currently playing.",
                   aliases=["np"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def now_playing_command(ctx: lightbulb.Context) -> None:
    """ Gets the song that's currently playing """

    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)

    if not node:
        await ctx.respond("Nothing is playing at the moment.")
        return

    embed = hikari.Embed(
        title="Now Playing",
        description=getattr(node.now_playing.track.info, "title", "No tracks are currently playing"),
        colour=ctx.author.accent_color,
        timestamp=dt.datetime.now(dt.timezone.utc)
    )
    embed.set_footer(text=f"Requested by {ctx.author.username}", icon=ctx.author.avatar_url)

    await ctx.respond("", embed=embed)


# ----- Up Next Commaand -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("upnext",
                   "Shows the next 5 songs in the queue",
                   aliases=["queue"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def up_next_command(ctx: lightbulb.Context) -> None:
    """ Gets the current and next 5 songes in the queue """
    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)

    if not node:
        await ctx.respond("Nothing is playing at the moment.")
        return

    embed = hikari.Embed(
        title="Now Playing",
        description=getattr(node.now_playing.track.info, "title", "No tracks are currently playing"),
        colour=ctx.author.accent_color,
        timestamp=dt.datetime.now(dt.timezone.utc)
    )
    embed.set_footer(text=f"Requested by {ctx.author.username}", icon=ctx.author.avatar_url)
    embed.set_author(name="Queue")
    embed.add_field(
        name="Up Next",
        value="\n".join(queue.track.info.title for queue in node.queue[1:6]),
        inline=False
    )

    await ctx.respond("", embed=embed)


# ----- Data Command (Server owner only) -----
@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("args",
                  "The arguments to write to the node data.",
                  required=False,
                  modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("data", "Load or read data from the node.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def data_command(ctx: lightbulb.Context) -> None:
    """
    Load or read data from the node

    If just `data` is ran, it will show the current data,
    but if `data <key> <value>` is ran, it will insert that
    data to the node and display it
    """

    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)

    if not node:
        await ctx.respond("No node found.")
        return None

    if args := ctx.options.args:
        args = args.split(" ")

        if len(args) == 1:
            node.set_data({args[0]: args[0]})
        else:
            node.set_data({args[0]: args[1]})
    await ctx.respond(node.get_data())


# ---------- Listener Functions ----------


if HIKARI_VOICE:

    @plugin.listener(hikari.VoiceStateUpdateEvent)
    async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
        plugin.bot.d.lavalink.raw_handle_event_voice_state_update(
            event.state.guild_id,
            event.state.user_id,
            event.state.session_id,
            event.state.channel_id,
        )

    @plugin.listener(hikari.VoiceServerUpdateEvent)
    async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
        await plugin.bot.d.lavalink.raw_handle_event_voice_server_update(event.guild_id, event.endpoint, event.token)


# --------- Plugin Load and Unload Functions ----------


def load(bot: lightbulb.BotApp) -> None:
    """ Load commands and plugins to the bot """
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    """ Unload commands and plugins from the bot """
    bot.remove_plugin(plugin)

