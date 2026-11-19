"""A Level is just data: a map, a starting spot, a goal, coins and starter code."""

# Letters on the map that stand for coins, and which color each one is.
COIN_LETTERS = {"C": "normal", "R": "red", "S": "sapphire"}

# What each color is worth. The player's code has to work this out; the game
# only uses these numbers to check that the player's wallet is right.
COIN_VALUES = {"normal": 1, "red": 5, "sapphire": 10}


class Level:
    def __init__(self, name, intro, rows, starter_code, passes_color=False):
        """passes_color: if True the game calls add_coin(color), otherwise add_coin()."""
        self.name = name
        self.intro = intro
        self.rows = rows
        self.starter_code = starter_code
        self.passes_color = passes_color
        self.height = len(rows)
        self.width = len(rows[0])
        self.start = self._find_tiles("P")[0]
        self.goal = self._find_tiles("G")[0]
        self.coins = {pos: color for letter, color in COIN_LETTERS.items()
                      for pos in self._find_tiles(letter)}          # (x, y) -> color
        self.coin_values = {color: COIN_VALUES[color] for color in set(self.coins.values())}

    def _find_tiles(self, ch):
        return [(x, y) for y, row in enumerate(self.rows)
                for x, c in enumerate(row) if c == ch]

    def is_wall(self, x, y):
        """Anything outside the map counts as a wall too."""
        return not (0 <= x < self.width and 0 <= y < self.height) or self.rows[y][x] == "#"

    def total_gold(self):
        """How much gold a perfect wallet has after every coin is collected."""
        return sum(self.coin_values[color] for color in self.coins.values())
