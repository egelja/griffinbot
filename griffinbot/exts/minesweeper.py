from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from random import sample

import discord
from discord.ext import commands, tasks

from griffinbot.constants import Bot, Emoji

log = logging.getLogger(__name__)


def num_to_emoji(x: int) -> str:
    """Convet int to emoji."""
    if x < 11:
        return {
            -1: "💣",
            0: "🟦",
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "<:bad_ten:798295802866040862>",
        }[x]
    return f"{x}  "


class GameBoard:
    """Represents a Minesweeper game board."""

    def __init__(self, x_bombs: int = 10, y_bombs: int = 10, num_bombs: int = 8):
        self.guesses = 0
        self.started = False
        self.x_bombs = x_bombs
        self.y_bombs = y_bombs
        self.bombs = num_bombs
        self.gameover = False
        self.updated = datetime.now()

        self.buttons = []
        for x_coord in range(x_bombs):
            row = []
            for y_coord in range(y_bombs):
                row.append(Tile(self, x_coord, y_coord))
            self.buttons.append(row)

    def start(self, x: int, y: int) -> None:
        """Start a new minesweeper game."""
        button_numbers = {n for n in range(self.x_bombs * self.y_bombs)}
        button_numbers.remove(y * self.x_bombs + x)

        bomb_numbers = set(sample(button_numbers, self.bombs))
        self.bombPositions = []
        for bomb_number in bomb_numbers:
            bomb_x = bomb_number % self.x_bombs
            bomb_y = bomb_number // self.x_bombs
            self.buttons[bomb_x][bomb_y].bomb()
            self.bombPositions.append((bomb_x, bomb_y))

        for bomb_x, bomb_y in self.bombPositions:
            for tile in self.buttons[bomb_x][bomb_y].get_adjacent():
                if not tile.isBomb:
                    tile.reveal_image_state += 1

        # Mark the game as started
        self.started = True

    def game_over(self) -> None:
        """Game over."""
        self.gameover = True

    def cleared(self) -> bool:
        """Check if the player has cleared the gameboard of mines."""
        for row in self.buttons:
            for tile in row:
                if (not tile.isBomb) and tile.covered:
                    return False
        return True

    def stale(self) -> bool:
        """Check if the game is stale."""
        if (datetime.now() - self.updated).total_seconds() > 120:
            log.trace("Stale")
            return True
        log.trace("Not stale")
        return False

    def update(self) -> None:
        """Update the game board to keep it from going stale."""
        self.updated = datetime.now()

    def to_covered_message(self) -> str:
        """Return the board as a covered (spoilers) message."""
        msg = ""
        for row in self.buttons:
            for tile in row:
                msg = msg + "||" + num_to_emoji(tile.reveal_image_state) + "||"
            if not row == self.buttons[-1]:
                msg = msg + "\n"
        return msg

    def to_message(self) -> str:
        """Return the board as a emoji message."""
        msg = ":blue_square:"
        x = 1
        while x <= len(self.buttons[0]):
            msg = msg + num_to_emoji(x)
            x += 1
        x = 1
        msg = msg + "\n"
        for row in self.buttons:
            msg = msg + num_to_emoji(x)
            x += 1
            for tile in row:
                msg = msg + tile.to_emoji()
            if not row == self.buttons[-1]:
                msg = msg + "\n"
        return msg


class Tile:
    """the Tiles on the board."""

    def __init__(self, gameboard: GameBoard, x: int, y: int):
        self.covered = True
        self.isBomb = False
        self.x = x
        self.y = y
        self.tile_image_state = 0  # Shown when covered: 0 = 🟦, 1 = 🚩, 2 = ❓
        self.reveal_image_state = 0  # Shown when revealed: num bombs or -1 if bomb
        self.gameboard = gameboard

    def left_click(self) -> None:
        """Simulate a left click by the user."""
        if self.gameboard.gameover:
            return  # the game is over
        elif self.tile_image_state != 0:
            return  # flag or ?
        elif not self.gameboard.started:  # start the game
            self.gameboard.start(
                self.x,
                self.y,
            )
            self.reveal()
        elif self.isBomb:  # game over
            self.gameboard.game_over()
            return
        else:  # all good
            self.reveal()

        if self.gameboard.cleared():
            self.gameboard.gameover = True

    def reveal(self) -> None:
        """Reveal the tile."""
        self.covered = False
        if self.reveal_image_state == 0:
            for tile in self.get_adjacent():
                if tile.covered and tile.tile_image_state == 0:
                    tile.reveal()

    def right_click(self, image_state: int) -> None:
        """Right click the tile."""
        if self.gameboard.gameover:
            return
        self.tile_image_state = image_state

    def bomb(self) -> None:
        """Change the tile to a bomb."""
        self.isBomb = True
        self.reveal_image_state = -1

    def get_adjacent(self) -> list[Tile]:
        """Get the adjacent tiles."""
        adjacent = []
        for dx, dy in (
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
        ):
            x_pos = self.x + dx
            y_pos = self.y + dy
            if not (
                x_pos < 0
                or x_pos >= self.gameboard.x_bombs
                or y_pos < 0
                or y_pos >= self.gameboard.y_bombs
            ):
                adjacent.append(self.gameboard.buttons[x_pos][y_pos])
        return adjacent

    def to_emoji(self) -> str:
        """Convert the tile to emoji."""
        if self.gameboard.gameover:
            if self.covered:
                if self.isBomb:
                    return ":bomb:"
                elif self.tile_image_state == 1:
                    return ":flag_black:"
                return {0: "⬜", 1: "🚩", 2: "❓"}[self.tile_image_state]
            else:
                return num_to_emoji(self.reveal_image_state)
        else:
            if self.covered:
                return {0: "⬜", 1: "🚩", 2: "❓"}[self.tile_image_state]
            else:
                return num_to_emoji(self.reveal_image_state)


class Minesweeper(commands.Cog):
    """Minesweeper Game."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._games = {}
        self.clear_stale_games.start()

    def cog_unload(self) -> None:
        """Clean up while unloading the cog."""
        self.clear_stale_games.cancel()
        return super().cog_unload()

    @tasks.loop(minutes=1.0)
    async def clear_stale_games(self) -> None:
        """Clear stale games from the bot."""
        stale_games = []

        for game_id, game in self._games.items():
            if game.stale():
                stale_games.append(game_id)

        for game_id in stale_games:
            del self._games[game_id]

        log.info(f"{len(stale_games)} stale Minesweeper games removed")

    @commands.group(invoke_without_command=True, name="minesweeper", aliases=("ms",))
    async def minesweeper_group(self, ctx: commands.Context) -> None:
        """Commands for playing minesweeper."""
        await ctx.send_help(ctx.command)

    @minesweeper_group.command(name="spoilers-game", aliases=("s-g", "sg"))
    async def spoilers_game(
        self,
        ctx: commands.Context,
        bombs: int = 10,
        x_distance: int = 8,
        y_distance: int = 8,
        solvable: bool = False,
    ) -> None:
        """Send a spoilers minesweeper board."""
        if solvable:
            ctx.send(f"{Emoji.no} I am not smart enough for that.")
        else:
            game = GameBoard(x_distance, y_distance, bombs)
            game.buttons[0][0].left_click()
            await ctx.send(
                embed=discord.Embed(
                    title="Spoilers Minesweeper",
                    description=game.to_covered_message(),
                    color=discord.Color.gold(),
                    timestamp=datetime.now().astimezone(),
                ),
            )

    @minesweeper_group.command(name="new-game", aliases=("n-g", "ng"))
    async def new_game(
        self,
        ctx: commands.Context,
        bombs: int = 10,
        x_distance: int = 8,
        y_distance: int = 8,
    ) -> None:
        """Make new game."""
        log.info(f"{ctx.author} started a new Minesweeper game")
        game = GameBoard(x_distance, y_distance, bombs)
        self._games[str(ctx.message.author)] = game
        await ctx.send(
            embed=discord.Embed(
                title="Minesweeper",
                description=game.to_message(),
                color=discord.Color.gold(),
                timestamp=datetime.now().astimezone(),
            ),
        )

    @minesweeper_group.command(name="quit-game", aliases=("quit", "q"))
    async def quit_game(self, ctx: commands.Context) -> None:
        """Quit a Minesweeper game."""
        del self._games[str(ctx.message.author)]
        log.info(f"{ctx.author} quit their Minesweeper game")
        await ctx.send(f"{Emoji.ok} Successfully quit Minesweeper game.")

    @minesweeper_group.command(name="click", aliases=("c",))
    async def click(
        self, ctx: commands.Context, x_position: int, y_position: int
    ) -> None:
        """Click a square.

        The bot will add 5 emojis to your message:
            - ⛏️ means to break the square
            - 🚩 means to flag the square
            - ❓ means to mark the square as unknown
            - 🧼 means to clear the square
            - 🚫 means to cancel clicking
        """
        log.trace(f"Click at: {x_position}, {y_position}")
        # These have to be switched...
        x_temp = x_position
        x_position = y_position - 1
        y_position = x_temp - 1

        if str(ctx.message.author) not in self._games:
            # say something
            await ctx.send(
                f"{Emoji.no} You don't have a game, or your previous game went stale. "
                + f"Run `{Bot.prefix}ms new-game` to start a new game."
            )
            return

        # Update the game to keep it from going stale
        self._games[str(ctx.message.author)].update()

        # Add click reactions
        await ctx.message.add_reaction("⛏️")
        await ctx.message.add_reaction("🚩")
        await ctx.message.add_reaction("❓")
        await ctx.message.add_reaction("🧼")
        await ctx.message.add_reaction("🚫")

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add",
                timeout=120.0,
                check=lambda r, u: r.message == ctx.message
                and u == ctx.message.author
                and str(r.emoji) in {"⛏️", "❓", "🚩", "🧼", "🚫"},
            )
        except asyncio.TimeoutError:
            await ctx.send(f"{Emoji.warning} Game timed out")
            del self._games[str(ctx.message.author)]
        else:
            game = self._games[str(ctx.message.author)]

            log.trace(f"Got reaction: {reaction.emoji}")
            if str(reaction.emoji) == "⛏️":
                game.buttons[x_position][y_position].left_click()
                log.trace("Digging")
                if game.gameover:
                    if game.cleared():
                        await ctx.send(":tada: You won!")
                        await ctx.send(
                            embed=discord.Embed(
                                title="Minesweeper",
                                description=game.to_message(),
                                color=discord.Color.green(),
                                timestamp=datetime.now().astimezone(),
                            ),
                        )
                    else:
                        await ctx.send(":pensive: Game over.")
                        await ctx.send(
                            embed=discord.Embed(
                                title="Minesweeper",
                                description=game.to_message(),
                                color=discord.Color.red(),
                                timestamp=datetime.now().astimezone(),
                            ),
                        )

                    # Clean up
                    del self._games[str(ctx.message.author)]
                    return
            elif str(reaction) == "❓":
                game.buttons[x_position][y_position].right_click(2)
            elif str(reaction) == "🚩":
                game.buttons[x_position][y_position].right_click(1)
            elif str(reaction) == "🧼":
                game.buttons[x_position][y_position].right_click(0)

            await ctx.send(
                embed=discord.Embed(
                    title="Minesweeper",
                    description=game.to_message(),
                    color=discord.Color.gold(),
                    timestamp=datetime.now().astimezone(),
                ),
            )


def setup(bot: commands.Bot) -> None:
    """Add the Minesweeper cog."""
    bot.add_cog(Minesweeper(bot))
