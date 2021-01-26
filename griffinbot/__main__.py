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

    log.trace(f"Time: {datetime.now()}")
    channel = bot.get_channel(constants.Channels.bot_log)
    embed = discord.Embed(
        description="Connected!",
        timestamp=datetime.now().astimezone(),
        color=discord.Colour.green(),
    ).set_author(
        name=bot.user.display_name,
        url="https://github.com/NinoMaruszewski/griffinbot/",
        icon_url=bot.user.avatar_url_as(format="png"),
    )
    await channel.send(embed=embed)


# Load cogs
for file in os.listdir(os.path.join(".", "griffinbot", "exts")):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension(f"griffinbot.exts.{file[:-3]}")

# Log if debug mode is on
log.info(f"Debug: {constants.DEBUG_MODE}")
log.trace(f"Debug env variable: {os.environ['DEBUG']}")


@commands.has_any_role(*constants.BOT_ADMINS)
@bot.command(aliases=("r",))
async def reload(ctx: commands.Context, cog: str) -> None:
    """Reload a cog."""
    try:
        bot.reload_extension(cog) if "griffinbot" in cog else bot.reload_extension(
            f"griffinbot.exts.{cog}"
        )
    except commands.ExtensionNotLoaded:
        await ctx.send(f"Could not find the extension `{cog}`!")
    else:
        await ctx.send(f"Cog `{cog}` successfully reloaded!")


bot.run(constants.Bot.bot_token)
