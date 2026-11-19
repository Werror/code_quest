"""Decides which picture goes on every tile of a level. No pygame needed.

Trees are two tiles tall, so we pair up the wall tiles in each column from the
top down: each pair becomes one tall tree. A wall tile left over on its own
gets a small tree or a bush instead.
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
        if y + 1 < level.height and level.is_wall(x, y + 1):
            self.ground[(x, y + 1)] = _variant(x, y + 1, [T.GRASS, T.GRASS, T.GRASS_TUFT, T.GRASS_FLOWERS])
            self.objects[(x, y)] = T.TALL_ORANGE_TOP if orange else T.TALL_GREEN_TOP
            self.objects[(x, y + 1)] = T.TALL_ORANGE_BOTTOM if orange else T.TALL_GREEN_BOTTOM
            return 2
        self.objects[(x, y)] = _variant(x, y, [T.SMALL_GREEN_TREE, T.BUSH, T.SMALL_GREEN_TREE, T.SMALL_ORANGE_TREE])
        return 1
