import asyncio
import logging
import os
import subprocess
from datetime import datetime

from discord import Activity, ActivityType, Colour, Embed, Intents
from discord.ext import commands

from griffinbot.constants import BOT_ADMINS, DEBUG_MODE
from griffinbot.constants import Bot as BotConsts
from griffinbot.constants import Channels, Emoji

log = logging.getLogger("griffinbot.main")

try:
    import uvloop
except ImportError:
    log.warning(
        "Using the not-so-fast default asyncio event loop. Consider installing uvloop."
    )
    pass
else:
    log.info("Using the fast uvloop asyncio event loop")
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# Change the bot class to log adding/removing cogs:
class Bot(commands.Bot):
    """Subclass of `discord.ext.commands.Bot` with additional functionality."""

    def add_cog(self, cog) -> None:  # noqa: ANN001
        """Add a cog and log it."""
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    def remove_cog(self, name) -> None:  # noqa: ANN001
        """Remove a cog and log it."""
        super().remove_cog(name)
        log.info(f"Cog unloaded: {name}")

    async def close(self) -> None:
        """Close the bot and database session."""
        await super().close()

        # Prevents error on windows
        log.warning("Please wait, just cleaning up a bit more")
        await asyncio.get_event_loop().shutdown_asyncgens()
        await asyncio.sleep(2)


# Create bot
intents = Intents.default()
intents.typing = False
intents.members = True
bot = Bot(
    command_prefix=BotConsts.prefix,
    intents=intents,
    activity=Activity(type=ActivityType.watching, name=f"{BotConsts.prefix}help"),
)
bot.start_time = datetime.utcnow()


# Message when bot is ready
@bot.event
async def on_ready() -> None:
    """Message that the bot is ready."""
    log.info(f"Logged in as {bot.user}")

    log.trace(f"Time: {datetime.now()}")
    channel = bot.get_channel(Channels.bot_log)
    embed = Embed(
        description="Connected!",
        timestamp=datetime.now().astimezone(),
        color=Colour.green(),
    ).set_author(
        name=bot.user.display_name,
        url="https://github.com/NinoMaruszewski/griffinbot/",
        icon_url=bot.user.avatar_url_as(static_format="png"),
    )
    await channel.send(embed=embed)


# Load cogs
for file in os.listdir(os.path.join(".", "griffinbot", "exts")):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension(f"griffinbot.exts.{file[:-3]}")

# Log if debug mode is on
log.info(f"Debug: {DEBUG_MODE}")
log.trace(f"Debug env variable: {os.environ['DEBUG']}")


@commands.has_any_role(*BOT_ADMINS)
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


@commands.has_any_role(*BOT_ADMINS)
@bot.command(name="git-pull", aliases=("gitpull", "gp"))
async def git_pull(ctx: commands.Context) -> None:
    """Pull new changes."""
    log.info(f"{ctx.author} ran a git pull")
    try:
        c = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            check=True,
            encoding="utf-8",
            timeout=60,
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        log.info(f"Command error! `{str(e)}`")
        await ctx.send(
            f"{Emoji.warning} There was an error trying to execute that "
            + f"command:\n```\n{str(e)}\n```"
        )

        # Print output if available
        log.trace(f"Output: {e.stderr}")
        if (
            isinstance(e, (subprocess.TimeoutExpired, subprocess.SubprocessError))
            and e.stderr
        ):
            await ctx.send(f"Command output:\n```\n{e.stderr}\n```")
    else:
        # Command worked
        await ctx.send(f"{Emoji.green_check} Command executed successfully.")
        if c.stdout:
            await ctx.send(f"Command output:\n```\n{c.stdout}\n```")


bot.run(BotConsts.bot_token)
