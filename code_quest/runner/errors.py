"""Turn Python errors into short messages for the player."""


def friendly_syntax_error(error):
    return f"Typo on line {error.lineno}: {error.msg}"


def friendly_error(error):
    """Describe a runtime error, including the line of the player's code."""
    tb, line = error.__traceback__, None
    while tb:
        if tb.tb_frame.f_code.co_filename == "<hero>":
            line = tb.tb_lineno
        tb = tb.tb_next
    where = f" on line {line}" if line else ""
    return f"{type(error).__name__}{where}: {error}"
