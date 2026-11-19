import builtins
import sys

from ..config import MAX_LINES_RUN
from .api import make_api
from .errors import friendly_error, friendly_syntax_error

SAFE_BUILTIN_NAMES = ("range", "len", "int", "str", "min", "max", "abs", "bool", "list", "object")


class CodeProblem(Exception):
    """Something is missing from the player's code. The message is already friendly."""


class RunResult:
    def __init__(self, gold):
        self.events = []      # ("say", text) and, if all went well, ("gold", number)
        self.error = None     # friendly error string or None
        self.gold = gold      # the gold after the code ran (unchanged if there was an error)


def _check_gold(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise CodeProblem(f"wallet.gold should be a whole number, but it is {value!r}")


class CoinSession:
    """The player's `Wallet` object, kept alive from coin to coin.

    Creating a session runs the player's code once (that defines `class Wallet`)
    and makes one Wallet. Each coin then calls wallet.add_coin(). Everything
    the player's code does is only *recorded* as events; the game plays them
    back afterwards (the command-queue rule).

    NOTE: restricted builtins stop accidents, not determined hackers.
    Fine for a classroom/home game; use a subprocess sandbox if you ever
    run other people's code on a server.
    """

    def __init__(self, source, pass_color=False):
        """pass_color: call add_coin(color) instead of add_coin()."""
        self._pass_color = pass_color
        self._events = []
        safe_builtins = {name: getattr(builtins, name) for name in SAFE_BUILTIN_NAMES}
        safe_builtins["__build_class__"] = builtins.__build_class__   # lets `class` work
        self._env = {"__builtins__": safe_builtins, "__name__": "player_code", **make_api(self._events)}
        self.wallet = None
        self.gold = 0
        self.setup_error = self._guarded(lambda: self._setup(source))

    def _setup(self, source):
        exec(compile(source, "<hero>", "exec"), self._env)
        wallet_class = self._env.get("Wallet")
        if not isinstance(wallet_class, type):
            raise CodeProblem("I can't find your `class Wallet`. Did you delete it?")
        self.wallet = wallet_class()
        if not callable(getattr(self.wallet, "add_coin", None)):
            raise CodeProblem("Your Wallet needs a method called add_coin(self).")
        _check_gold(getattr(self.wallet, "gold", None))
        self.gold = self.wallet.gold

    def _guarded(self, action):
        """Run action() with a line limit. Returns a friendly error string or None."""
        count = 0

        def tracer(frame, event, arg):
            nonlocal count
            if frame.f_code.co_filename != "<hero>":
                return None
            if event == "line":
                count += 1
                if count > MAX_LINES_RUN:
                    raise TimeoutError("Your code ran for too long. Is a loop never ending?")
            return tracer

        try:
            sys.settrace(tracer)
            try:
                action()
            finally:
                sys.settrace(None)
        except CodeProblem as e:
            return str(e)
        except SyntaxError as e:
            return friendly_syntax_error(e)
        except Exception as e:  # noqa: BLE001 - we want to show every error nicely
            return friendly_error(e)
        return None

    def pick_up_coin(self, color="normal"):
        """Call wallet.add_coin() once (with the coin's color, if the level wants it) and record what happened."""
        result = RunResult(self.gold)
        if self.setup_error:
            result.error = self.setup_error
            return result
        del self._events[:]

        def add_coin_and_check():
            if self._pass_color:
                self.wallet.add_coin(color)
            else:
                self.wallet.add_coin()
            _check_gold(getattr(self.wallet, "gold", None))

        result.error = self._guarded(add_coin_and_check)
        result.events = list(self._events)
        if result.error is None:
            self.gold = self.wallet.gold
            result.gold = self.gold
            result.events.append(("gold", self.gold))
        return result
