"""Decides which picture goes on every tile of a level. No pygame needed.

Walking down each column of wall tiles, we plant either a tall tree (it takes
two tiles stacked on top of each other) or a single-tile tree or bush. Most of
the time we choose single tiles, so the forest is a mix with more small trees.
"""
from . import tiles as T


def _variant(x, y, choices):
    """Pick by position, so the scenery looks varied but never flickers."""
    return choices[(x * 31 + y * 17) % len(choices)]


class Scenery:
    def __init__(self, level):
        self.ground = {}    # (x, y) -> tile drawn first (grass or path)
        self.objects = {}   # (x, y) -> tile drawn on top (trees, sign)
        for x in range(level.width):
            y = 0
            while y < level.height:
                if level.is_wall(x, y):
                    y += self._plant(level, x, y)
                else:
                    self.ground[(x, y)] = _variant(x, y, [T.PATH, T.PATH, T.PATH, T.PATH_DOTS])
                    if (x, y) == level.goal:
                        self.objects[(x, y)] = T.SIGNPOST
                    y += 1

    def _plant(self, level, x, y):
        """Put a tree at the wall tile (x, y). Returns how many rows it used (1 or 2)."""
        self.ground[(x, y)] = _variant(x, y, [T.GRASS, T.GRASS, T.GRASS_TUFT, T.GRASS_FLOWERS])
        orange = (x * 7 + y * 13) % 5 == 0
        wants_tall = (x * 13 + y * 7) % 3 == 0   # about one spot in three
        if wants_tall and y + 1 < level.height and level.is_wall(x, y + 1):
            self.ground[(x, y + 1)] = _variant(x, y + 1, [T.GRASS, T.GRASS, T.GRASS_TUFT, T.GRASS_FLOWERS])
            self.objects[(x, y)] = T.TALL_ORANGE_TOP if orange else T.TALL_GREEN_TOP
            self.objects[(x, y + 1)] = T.TALL_ORANGE_BOTTOM if orange else T.TALL_GREEN_BOTTOM
            return 2
        self.objects[(x, y)] = _variant(x, y, [T.SMALL_GREEN_TREE, T.BUSH, T.SMALL_GREEN_TREE, T.SMALL_ORANGE_TREE, T.SMALL_GREEN_TREE])
        return 1
