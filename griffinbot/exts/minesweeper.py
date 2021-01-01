import asyncio
import logging
from random import sample

from discord.ext import commands

log = logging.getLogger(__name__)


def num_to_emoji(x: int) -> str:
    """Convet int to emoji."""
    if x < 11:
        return {
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
            10: "<:bad_ten:788818736090054707>",
        }[x]
    return f"{x}  "


class Tile:
    """the Tiles on the board."""

    def __init__(self, gameboard, x, y):
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
            self.gameboard.GG()
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
                Xp < 0 or Xp >= self.gameboard.X or Yp < 0 or Yp >= self.gameboard.Y
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


class GameBoard:
    def __init__(self, X=10, Y=10, Bombs=8):
        self.guesses = 0
        self.test = True
        self.started = False
        self.X = X
        self.Y = Y
        self.Bombs = Bombs
        self.gameover = False

        self.buttons = []
        for x in range(X):
            row = []
            for y in range(Y):
                row.append(Tile(self, x, y))
            self.buttons.append(row)

    def start(self, x, y):
        buttonnums = {N for N in range(self.X * self.Y)}
        buttonnums.remove(y * self.X + x)

        bombnumbers = set(sample(buttonnums, self.Bombs))
        self.bombPositions = []
        for bombnum in bombnumbers:
            BombX = bombnum % self.X
            BombY = bombnum // self.X
            self.buttons[BombX][BombY].bomb()
            self.bombPositions.append((BombX, BombY))

        for BombX, BombY in self.bombPositions:
            for Tile in self.buttons[BombX][BombY].getAdjacent():
                if not Tile.isBomb:
                    Tile.revealImageState += 1

    def GG(self):
        self.gameover = True

    def cleared(self):
        for row in self.buttons:
            for Tile in row:
                if (not Tile.isBomb) and Tile.covered:
                    return False
        return True

    def toCoveredMessage(self):
        msg = ""
        for row in self.buttons:
            for Tile in row:
                msg = (
                    msg
                    + "||"
                    + {
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
                    }[Tile.revealImageState]
                    + "||"
                )
            if not row == self.buttons[-1]:
                msg = msg + "\n"
        return msg

    def toMessage(self):
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


class MinesweeperGame:
    def __init__(self, minesweepersolver, X=8, Y=8, Bombs=10):

        self.X, self.Y, self.Bombs = X, Y, Bombs
        self.GB = GameBoard(self, self.X, self.Y, self.Bombs)

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
        ctx.send_help(ctx.command)

    @minesweeper_group.command(name="spoilers-game")
    async def coveredGame(
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
            await ctx.message.channel.send(game.toCoveredMessage())

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
