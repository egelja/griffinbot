import logging
import os
from datetime import datetime

import discord
from discord.ext import commands

from griffinbot import constants

log = logging.getLogger(__name__)


# Change the bot class to log adding/removing cogs:
class CogLoggingBot(commands.Bot):
    """Subclass of `discord.ext.commands.Bot` to log adding and removing cogs."""

    def add_cog(self, cog) -> None:  # noqa: ANN001
        """Add a cog and log it."""
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    def remove_cog(self, name) -> None:  # noqa: ANN001
        """Remove a cog and log it."""
        super().remove_cog(name)
        log.info(f"Cog unloaded: {name}")


# Create bot
intents = discord.Intents.default()
intents.typing = False
intents.members = True
bot = CogLoggingBot(
    command_prefix=constants.Bot.prefix,
    intents=intents,
    activity=discord.Activity(
        type=discord.ActivityType.watching, name=f"{constants.Bot.prefix}help"
    ),
)
bot.start_time = datetime.utcnow()


# Message when bot is ready
@bot.event
async def on_ready() -> None:
    """Message that the bot is ready."""
    log.info(f"Logged in as {bot.user}")

    channel = bot.get_channel(constants.Channels.bot_log)
    await channel.send(f"{constants.Emoji.green_check} Connected!")


# Load cogs
for file in os.listdir(os.path.join(".", "griffinbot", "exts")):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension(f"griffinbot.exts.{file[:-3]}")


@bot.command()
async def reload(ctx: commands.Context, cog: str) -> None:
    """Reload a cog."""
    try:
        bot.unload_extension(cog)
        bot.load_extension(cog)
    except commands.ExtensionNotLoaded:
        await ctx.send(f"Could not find the extension `{cog}`!")
    else:
        await ctx.send(f"Cog `{cog}` successfully reloaded!")


bot.run(constants.Bot.bot_token)
