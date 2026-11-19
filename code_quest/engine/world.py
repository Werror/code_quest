"""The real game world: where the hero is and which coins are left.

No drawing and no pygame in here, so it is easy to test.
"""


class World:
    def __init__(self, level):
        self.level = level
        self.reset()

    def reset(self):
        self.hero = list(self.level.start)
        self.coins = set(self.level.coins)
        self.collected = 0

    def try_move(self, dx, dy):
        """Step one tile. Returns False (and stays put) if a tree is in the way."""
        nx, ny = self.hero[0] + dx, self.hero[1] + dy
        if self.level.is_wall(nx, ny):
            return False
        self.hero[:] = [nx, ny]
        return True

    def pick_up_coin(self):
        """If the hero stands on a coin, take it. Returns True if a coin was taken."""
        here = tuple(self.hero)
        if here in self.coins:
            self.coins.remove(here)
            self.collected += 1
            return True
        return False

    def at_goal(self):
        return tuple(self.hero) == self.level.goal
