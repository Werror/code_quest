"""The commands the player is allowed to use.

They work on a *simulated* hero and only record events. Nothing here touches
the screen. That is the command-queue rule.
"""
from ..config import MAX_ACTIONS

DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def make_api(level, events):
    """Return the dict of commands the player's code can call."""
    state = {"x": level.start[0], "y": level.start[1], "coins": set(level.coins)}

    def check_limit():
        if len(events) > MAX_ACTIONS:
            raise RuntimeError("Too many actions! Is a loop never ending?")

    def move(dx, dy, n=1):
        for _ in range(int(n)):
            nx, ny = state["x"] + dx, state["y"] + dy
            if level.is_wall(nx, ny):
                events.append(("bump", state["x"], state["y"]))
                check_limit()
                return
            state["x"], state["y"] = nx, ny
            events.append(("move", nx, ny))
            if (nx, ny) in state["coins"]:
                state["coins"].remove((nx, ny))
                events.append(("coin", nx, ny))
            check_limit()

    def wall_ahead(direction):
        if direction not in DIRECTIONS:
            raise ValueError("wall_ahead needs 'up', 'down', 'left' or 'right'")
        dx, dy = DIRECTIONS[direction]
        return level.is_wall(state["x"] + dx, state["y"] + dy)

    def say(*things):
        events.append(("say", " ".join(str(t) for t in things)))
        check_limit()

    return {
        "move_up": lambda n=1: move(0, -1, n),
        "move_down": lambda n=1: move(0, 1, n),
        "move_left": lambda n=1: move(-1, 0, n),
        "move_right": lambda n=1: move(1, 0, n),
        "wall_ahead": wall_ahead,
        "say": say,
        "print": say,
    }
