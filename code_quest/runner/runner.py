import builtins
import sys

from ..config import MAX_LINES_RUN
from .api import make_api
from .errors import friendly_error, friendly_syntax_error

SAFE_BUILTIN_NAMES = ("range", "len", "int", "str", "min", "max", "abs", "bool", "list")


class RunResult:
    def __init__(self, wallet):
        self.events = []     # ("say", text) and, if all went well, ("wallet", number)
        self.error = None    # friendly error string or None
        self.wallet = wallet  # the wallet after the code ran (unchanged if there was an error)


def run_coin_code(source, wallet):
    """Run the player's coin code once, as if one coin was just picked up.

    The code starts with a variable called `wallet` already set to the current
    amount. Whatever `wallet` is when the code finishes is the new amount. We
    only record what happened; the game plays it back afterwards.

    NOTE: restricted builtins stop accidents, not determined hackers.
    Fine for a classroom/home game; use a subprocess sandbox if you ever
    run other people's code on a server.
    """
    result = RunResult(wallet)
    safe_builtins = {name: getattr(builtins, name) for name in SAFE_BUILTIN_NAMES}
    env = {"__builtins__": safe_builtins, "wallet": wallet, **make_api(result.events)}

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
        code = compile(source, "<hero>", "exec")
        sys.settrace(tracer)
        try:
            exec(code, env)
        finally:
            sys.settrace(None)
    except SyntaxError as e:
        result.error = friendly_syntax_error(e)
        return result
    except Exception as e:  # noqa: BLE001 - we want to show every error nicely
        result.error = friendly_error(e)
        return result

    new_wallet = env.get("wallet")
    if isinstance(new_wallet, bool) or not isinstance(new_wallet, int):
        result.error = f"Your wallet should be a whole number, but it is {new_wallet!r}"
        return result
    result.wallet = new_wallet
    result.events.append(("wallet", new_wallet))
    return result
