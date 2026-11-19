"""The real game world: where the hero is and which coins are left.

No drawing and no pygame in here, so it is easy to test.
"""


class World:
    def __init__(self, level):
        self.level = level
        self.reset()

    def reset(self):
        self.hero = list(self.level.start)
        self.coins = dict(self.level.coins)   # (x, y) -> color, coins still on the ground
        self.collected = 0

    def try_move(self, dx, dy):
        """Step one tile. Returns False (and stays put) if a tree is in the way."""
        nx, ny = self.hero[0] + dx, self.hero[1] + dy
        if self.level.is_wall(nx, ny):
            return False
        self.hero[:] = [nx, ny]
        return True

    def pick_up_coin(self):
        """If the hero stands on a coin, take it. Returns its color, or None if there is no coin."""
        color = self.coins.pop(tuple(self.hero), None)
        if color is not None:
            self.collected += 1
        return color

    def at_goal(self):
        return tuple(self.hero) == self.level.goal
