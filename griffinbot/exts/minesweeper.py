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
            for tile in self.buttons[bomb_x][bomb_y].getAdjacent():
                if not tile.isBomb:
                    tile.revealImageState += 1

    def game_over(self) -> None:
        """Game over."""
        self.gameover = True

    def cleared(self) -> bool:
        """Check if the player has cleared the gameboard of mines."""
        for row in self.buttons:
            for Tile in row:
                if (not Tile.isBomb) and Tile.covered:
                    return False
        return True

    def to_covered_message(self):
        """Return the board as a covered (spoilers) message."""
        msg = ""
        for row in self.buttons:
            for tile in row:
                msg = msg + "||" + num_to_emoji(tile.revealImageState) + "||"
            if not row == self.buttons[-1]:
                msg = msg + "\n"
        return msg

    def to_message(self):
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
            for Tile in row:
                msg = msg + Tile.toemoji()
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
        self.TileImageState = 0
        self.revealImageState = 0
        self.gameboard = gameboard

    def left_click(self) -> None:
        """Simulate a left click by the user."""
        if self.gameboard.gameover:
            return  # the game is over
        elif self.TileImageState != 0:
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
        if self.revealImageState == 0:
            for tile in self.getAdjacent():
                if tile.covered and tile.TileImageState == 0:
                    tile.reveal()

    def Rclick(self, imgstate):
        if self.gameboard.gameover:
            return
        self.TileImageState = imgstate

    def bomb(self):
        self.isBomb = True
        self.revealImageState = -1

    def getAdjacent(self):
        adjacents = []
        for Dx, Dy in (
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
        ):
            Xp = self.x + Dx
            Yp = self.y + Dy
            if not (
                Xp < 0 or Xp >= self.gameboard.x or Yp < 0 or Yp >= self.gameboard.y
            ):
                adjacents.append(self.gameboard.buttons[Xp][Yp])
        return adjacents

    def toemoji(self):
        if self.gameboard.gameover:
            if self.covered:
                if self.isBomb:
                    return ":bomb:"
                elif self.TileImageState == 1:
                    return ":flag_black:"
                return {0: "⬜", 1: "🚩", 2: "❓"}[self.TileImageState]
            else:
                return num_to_emoji(self.revealImageState)
        else:
            if self.covered:
                return {0: "⬜", 1: "🚩", 2: "❓"}[self.TileImageState]
            else:
                return num_to_emoji(self.revealImageState)


class MinesweeperGame:
    def __init__(self, minesweepersolver, X=8, Y=8, Bombs=10):

        self.X, self.Y, self.Bombs = X, Y, Bombs
        self.GB = GameBoard(self.X, self.Y, self.Bombs)

    #     self.Solver = minesweepersolver

    # def run(self):
    #     self.Solver(self.GB)
    #     covered = 0
    #     for row in self.GB.buttons:
    #         for Tile in row:
    #             if not Tile.isBomb and Tile.covered:
    #                 covered += 1
    #     return (covered, self.GB.guesses)


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
    async def coveredGame(
        self,
        ctx: commands.Context,
        bombs: int = 10,
        xdistance: int = 8,
        ydistance: int = 8,
        solvable: bool = False,
    ):
        """Sends a spoilers minesweeper board"""

        if solvable:
            ctx.message.channel.send("I am not smart enough for that.")
        else:
            game = GameBoard(xdistance, ydistance, bombs)
            game.buttons[0][0].left_click()
            await ctx.message.channel.send(game.to_covered_message())

    @minesweeper_group.command(name="new-game", help="Starts a game.")
    async def NewGame(
        self, ctx, bombs: int = 10, xdistance: int = 8, ydistance: int = 8
    ):
        self.games[str(ctx.message.author)] = GameBoard(xdistance, ydistance, bombs)
        await ctx.message.channel.send(self.games[str(ctx.message.author)].toMessage())

    @minesweeper_group.command(name="click", help="Click a square.")
    async def Click(self, ctx, xPosition: int, yPosition: int):
        # if (xPosition): pass
        xPosition -= 1
        yPosition -= 1
        print(f"click at: {xPosition}, {yPosition}")
        if str(ctx.message.author) not in self.games:
            # say something
            await ctx.message.channel.send("you don't have a game.")
            return
        await ctx.message.add_reaction("⛏️")
        await ctx.message.add_reaction("❓")
        await ctx.message.add_reaction("🚩")
        await ctx.message.add_reaction("🧼")
        await ctx.message.add_reaction("🚫")
        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add",
                timeout=600.0,
                check=lambda r, u: self.check(ctx.message.author, ctx.message, r, u),
            )
        except asyncio.TimeoutError:
            await ctx.message.channel.send("game timed out")
            del self.games[str(ctx.message.author)]
        else:
            print(f"got reaction: {reaction.emoji}")
            print(str(reaction.emoji))
            if str(reaction.emoji) == "⛏️":
                self.games[str(ctx.message.author)].buttons[xPosition][
                    yPosition
                ].left_click()
                print("digging")
                if self.games[str(ctx.message.author)].gameover:
                    await ctx.message.channel.send("Game over. who knows why?")
                    await ctx.message.channel.send(
                        self.games[str(ctx.message.author)].toMessage()
                    )
                    del self.games[str(ctx.message.author)]
            elif str(reaction) == "❓":
                self.games[str(ctx.message.author)].buttons[xPosition][
                    yPosition
                ].Rclick(2)
            elif str(reaction) == "🚩":
                self.games[str(ctx.message.author)].buttons[xPosition][
                    yPosition
                ].Rclick(1)
            elif str(reaction) == "🧼":
                self.games[str(ctx.message.author)].buttons[xPosition][
                    yPosition
                ].Rclick(0)

            await ctx.message.channel.send(
                self.games[str(ctx.message.author)].toMessage()
            )

    @staticmethod
    def check(player, message, reaction, user):
        return (
            reaction.message == message
            and user == player
            and str(reaction.emoji) in {"⛏️", "❓", "🚩", "🧼", "🚫"}
        )


def setup(bot: commands.Bot) -> None:
    """Add the status cog."""
    bot.add_cog(Minesweeper(bot))
