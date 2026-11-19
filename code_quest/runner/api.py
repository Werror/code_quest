"""The commands the player's code is allowed to call.

They only record events. Nothing here touches the screen. That is the
command-queue rule: the player's code never changes the real game, it just
writes down what should happen and the game plays it back afterwards.
"""
from ..config import MAX_ACTIONS


def make_api(events):
    """Return the dict of commands the player's code can call."""

    def say(*things):
        events.append(("say", " ".join(str(t) for t in things)))
        if len(events) > MAX_ACTIONS:
            raise RuntimeError("Too many messages! Is a loop never ending?")

    return {"say": say, "print": say}
