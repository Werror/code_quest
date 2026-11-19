"""Friendly messages for the mistakes beginners make most."""
from code_quest.runner.runner import CoinSession

HEAD = "class Wallet:\n    def __init__(self):\n        self.gold = 0\n\n    def add_coin(self):\n"


def error_for(snippet):
    """The message the player sees if `snippet` is the body of add_coin() (it starts on line 6)."""
    code = HEAD + "\n".join("        " + line for line in snippet.split("\n")) + "\n"
    return CoinSession(code).setup_error


def test_plus_plus_explains_that_python_has_no_plus_plus():
    message = error_for("self.gold++")
    assert message.startswith("Typo on line 6")
    assert "no `++`" in message
    assert "`self.gold += 1`" in message


def test_minus_minus_suggests_minus_equals():
    assert "`self.gold -= 1`" in error_for("self.gold--")


def test_plus_plus_with_a_trailing_comment_is_still_recognised():
    assert "`self.gold += 1`" in error_for("self.gold++   # add one")


def test_forgotten_colon_is_pointed_out():
    message = error_for("if self.gold == 1\n    pass")
    assert "forget the `:`" in message and "`if`" in message


def test_single_equals_in_a_condition_suggests_double_equals():
    message = error_for("if self.gold = 1:\n    pass")
    assert "`==`" in message


def test_unclosed_bracket_is_explained():
    assert "closing partner" in error_for("x = (1 + 2")


def test_unclosed_quote_is_explained():
    assert "quotes is not closed" in error_for("say('hi)")


def test_bad_indentation_is_explained():
    code = "class Wallet:\n    def __init__(self):\n        self.gold = 0\n  def add_coin(self):\n        pass\n"
    assert "spaces at the start" in CoinSession(code).setup_error


def test_other_syntax_mistakes_show_the_line_that_failed():
    message = error_for("self.gold = 5 5")
    assert message.startswith("Typo on line 6")
    assert "self.gold = 5 5" in message


def test_messages_never_contain_a_traceback_or_raw_python_jargon():
    for snippet in ("self.gold++", "if x == 1", "x = (", "self.gold = 5 5"):
        message = error_for(snippet)
        assert "Traceback" not in message
        assert "invalid syntax" not in message
        assert "EOF" not in message


def test_forgetting_self_before_gold_gets_a_hint():
    code = HEAD + "        self.gold = gold + 1\n"
    result = CoinSession(code).pick_up_coin()
    assert result.error.startswith("NameError on line 6")
    assert "self.gold" in result.error
