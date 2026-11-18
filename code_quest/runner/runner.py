import builtins
import sys

from ..config import MAX_LINES_RUN
from .api import make_api
from .errors import friendly_error, friendly_syntax_error

SAFE_BUILTIN_NAMES = ("range", "len", "int", "str", "min", "max", "abs", "bool", "list")


class RunResult:
    def __init__(self):
        self.events = []     # ("move", x, y) / ("bump", x, y) / ("coin", x, y) / ("say", text)
        self.error = None    # friendly error string or None


def run_player_code(source, level):
    """Run the kid's code against a *simulated* hero and record what happened.
    The game then plays those events back as an animation.

    NOTE: restricted builtins stop accidents, not determined hackers.
    Fine for a classroom/home game; use a subprocess sandbox if you ever
    run other people's code on a server.
    """
    result = RunResult()
    safe_builtins = {name: getattr(builtins, name) for name in SAFE_BUILTIN_NAMES}
    env = {"__builtins__": safe_builtins, **make_api(level, result.events)}

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
    except Exception as e:  # noqa: BLE001 - we want to show every error nicely
        result.error = friendly_error(e)
    return result
