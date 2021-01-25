from __future__ import annotations

import asyncio
import logging
from random import sample

from discord.ext import commands

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

    def __init__(self, x: int = 10, y: int = 10, bombs: int = 8):
        self.guesses = 0
        # self.test = True
        self.started = False
        self.x = x
        self.y = y
        self.bombs = bombs
        self.gameover = False

        self.buttons = []
        for x_coord in range(x):
            row = []
            for y_coord in range(y):
                row.append(Tile(self, x_coord, y_coord))
            self.buttons.append(row)

    def start(self, x: int, y: int) -> None:
        """Start a new minesweeper game."""
        button_numbers = {n for n in range(self.x * self.y)}
        button_numbers.remove(y * self.x + x)

        bomb_numbers = set(sample(button_numbers, self.bombs))
        self.bombPositions = []
        for bomb_number in bomb_numbers:
            bomb_x = bomb_number % self.x
            bomb_y = bomb_number // self.x
            self.buttons[bomb_x][bomb_y].bomb()
            self.bombPositions.append((bomb_x, bomb_y))

        for bomb_x, bomb_y in self.bombPositions:
            for tile in self.buttons[bomb_x][bomb_y].get_adjacent():
                if not tile.isBomb:
                    tile.reveal_image_state += 1

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
        self.tile_image_state = 0
        self.reveal_image_state = 0
        self.gameboard = gameboard

    def left_click(self) -> None:
        """Simulate a left click by the user."""
        if self.gameboard.gameover:
            return  # the game is over
        elif self.tile_image_state != 0:
            return  # flag or ?
        elif not self.gameboard.started:  # start the game
            self.gameboard.started = True
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
        """Get the adjacent tiles."""  # what did you think? it's literally the
        # name of the function.
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
            xp = self.x + dx
            yp = self.y + dy
            if not (
                xp < 0 or xp >= self.gameboard.x or yp < 0 or yp >= self.gameboard.y
            ):
                adjacent.append(self.gameboard.buttons[xp][yp])
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
    """Not status commands for the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # discord.ext.commands.Bot.__init__(self, cmd_pre)
        self.games = {}

    @commands.group(invoke_without_command=True, name="minesweeper", aliases=("ms",))
    async def minesweeper_group(self, ctx: commands.Context) -> None:
        """Commands for playing minesweeper."""
        await ctx.send_help(ctx.command)

    @minesweeper_group.command(name="spoilers-game")
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
            ctx.send("I am not smart enough for that.")
        else:
            game = GameBoard(x_distance, y_distance, bombs)
            game.buttons[0][0].left_click()
            await ctx.send(game.to_covered_message())

    @minesweeper_group.command(name="new-game")
    async def new_game(
        self,
        ctx: commands.Context,
        bombs: int = 10,
        x_distance: int = 8,
        y_distance: int = 8,
    ) -> None:
        """Make new game."""  # what did you think?
        self.games[str(ctx.message.author)] = GameBoard(x_distance, y_distance, bombs)
        await ctx.send(self.games[str(ctx.message.author)].to_message())

    @minesweeper_group.command(name="click")
    async def click(
        self, ctx: commands.Context, x_position: int, y_position: int
    ) -> None:
        """Click a square."""
        log.trace(f"click at: {x_position}, {y_position}")
        x_position -= 1
        y_position -= 1
        if str(ctx.message.author) not in self.games:
            # say something
            await ctx.send("you don't have a game.")
            return
        await ctx.message.add_reaction("⛏️")
        await ctx.message.add_reaction("❓")
        await ctx.message.add_reaction("🚩")
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
            await ctx.send("Game timed out")
            del self.games[str(ctx.message.author)]
        else:
            log.trace(f"Got reaction: {reaction.emoji}")
            if str(reaction.emoji) == "⛏️":
                self.games[str(ctx.message.author)].buttons[x_position][
                    y_position
                ].left_click()
                log.trace("Digging")
                if self.games[str(ctx.message.author)].gameover:
                    await ctx.send("Game over. who knows why?")
                    await ctx.send(self.games[str(ctx.message.author)].to_message())
                    del self.games[str(ctx.message.author)]
                    return
            elif str(reaction) == "❓":
                self.games[str(ctx.message.author)].buttons[x_position][
                    y_position
                ].right_click(2)
            elif str(reaction) == "🚩":
                self.games[str(ctx.message.author)].buttons[x_position][
                    y_position
                ].right_click(1)
            elif str(reaction) == "🧼":
                self.games[str(ctx.message.author)].buttons[x_position][
                    y_position
                ].right_click(0)

            await ctx.send(self.games[str(ctx.message.author)].to_message())


def setup(bot: commands.Bot) -> None:
    """Add the Minesweeper cog."""
    bot.add_cog(Minesweeper(bot))
