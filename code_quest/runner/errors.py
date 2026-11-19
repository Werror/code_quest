"""Turn Python errors into short, friendly messages for the player.

Python's own messages (like "invalid syntax") don't help a beginner. For the
mistakes new coders make most often we look at the line that failed and say
what is wrong and how to fix it.
"""
import re

BLOCK_WORDS = ("if", "elif", "else", "for", "while", "def", "class", "try", "except", "finally", "with")
INCREMENT = re.compile(r"^(?P<target>[\w.\[\]'\"]+)\s*(?P<op>\+\+|--)$")
LONE_EQUALS = re.compile(r"(?<![=!<>])=(?!=)")


def _without_comment(line):
    return line.split("#", 1)[0].strip()


def _explain_line(line):
    """A friendly sentence for a failed line, or None if we have no good guess."""
    code = _without_comment(line)
    step = INCREMENT.match(code)
    if step:
        change = "+= 1" if step.group("op") == "++" else "-= 1"
        return (f"Python has no `{step.group('op')}`. "
                f"Write `{step.group('target')} {change}` instead.")
    first_word = code.split(" ", 1)[0].rstrip(":") if code else ""
    if first_word in ("if", "elif", "while") and LONE_EQUALS.search(code.split(" ", 1)[1] if " " in code else ""):
        return "To compare two things, use `==` (two equals signs). A single `=` stores a value."
    if first_word in BLOCK_WORDS and not code.endswith(":"):
        return f"Did you forget the `:` at the end of this `{first_word}` line?"
    return None


def friendly_syntax_error(error):
    where = f"Typo on line {error.lineno}"
    message = (error.msg or "").lower()
    line = (error.text or "").rstrip("\n")

    explanation = _explain_line(line)
    if explanation:
        return f"{where}: {explanation}"
    if "indent" in message:
        return f"{where}: The spaces at the start of this line don't line up with the lines above it."
    if "string" in message:
        return f"{where}: A piece of text in quotes is not closed. Add the matching quote."
    if "eof" in message or "never closed" in message or "was never" in message:
        return f"{where}: Something is still open. Check that every `(`, `[` and `{{` has a closing partner."
    if line.strip():
        return f"{where}: Python can't read `{line.strip()}`. Look for a missing or extra symbol."
    return f"{where}: {error.msg}"


def _missing_self_hint(error):
    """NameError for `gold` inside a class usually means a forgotten `self.`."""
    if isinstance(error, NameError) and "name 'gold' is not defined" in str(error):
        return ". Inside the Wallet, write `self.gold`."
    return ""


def friendly_error(error):
    """Describe a runtime error, including the line of the player's code."""
    tb, line = error.__traceback__, None
    while tb:
        if tb.tb_frame.f_code.co_filename == "<hero>":
            line = tb.tb_lineno
        tb = tb.tb_next
    where = f" on line {line}" if line else ""
    return f"{type(error).__name__}{where}: {error}{_missing_self_hint(error)}"
