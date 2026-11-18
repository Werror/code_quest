"""A Level is just data: a map, a starting spot, a goal, coins and starter code."""


class Level:
    def __init__(self, name, rows, starter_code):
        self.name = name
        self.rows = rows
        self.starter_code = starter_code
        self.height = len(rows)
        self.width = len(rows[0])
        self.start = self._find_tiles("P")[0]
        self.goal = self._find_tiles("G")[0]
        self.coins = frozenset(self._find_tiles("C"))

    def _find_tiles(self, ch):
        return [(x, y) for y, row in enumerate(self.rows)
                for x, c in enumerate(row) if c == ch]

    def is_wall(self, x, y):
        """Anything outside the map counts as a wall too."""
        return not (0 <= x < self.width and 0 <= y < self.height) or self.rows[y][x] == "#"
