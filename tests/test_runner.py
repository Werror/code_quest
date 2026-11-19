"""Tests for CoinSession: the player's Wallet object and how coins call it.

The player writes `class Wallet` with add_coin(). The game makes one Wallet and
calls add_coin() each time a coin is picked up.
"""
import sys

from code_quest.config import MAX_ACTIONS
from code_quest.runner.runner import CoinSession


def wallet_code(add_coin_body, init_body="self.gold = 0"):
    """Build a small Wallet class so each test only shows what it cares about."""
    indent = "        "
    body = "\n".join(indent + line for line in add_coin_body.split("\n"))
    return f"class Wallet:\n    def __init__(self):\n{indent}{init_body}\n    def add_coin(self):\n{body}\n"


PLUS_ONE = wallet_code("self.gold = self.gold + 1")


# --- the wallet exercise ----------------------------------------------------
def test_add_coin_plus_one():
    result = CoinSession(PLUS_ONE).pick_up_coin()
    assert result.error is None
    assert result.gold == 1
    assert result.events == [("gold", 1)]


def test_the_wallet_object_remembers_gold_between_coins():
    session = CoinSession(PLUS_ONE)
    assert [session.pick_up_coin().gold for _ in range(3)] == [1, 2, 3]


def test_each_session_has_its_own_wallet():
    first, second = CoinSession(PLUS_ONE), CoinSession(PLUS_ONE)
    first.pick_up_coin()
    first.pick_up_coin()
    assert second.pick_up_coin().gold == 1


def test_init_can_start_with_gold():
    session = CoinSession(wallet_code("self.gold += 1", init_body="self.gold = 10"))
    assert session.gold == 10
    assert session.pick_up_coin().gold == 11


def test_plus_equals_works_too():
    assert CoinSession(wallet_code("self.gold += 5")).pick_up_coin().gold == 5


def test_stub_that_does_nothing_leaves_gold_alone():
    result = CoinSession(wallet_code("pass")).pick_up_coin()
    assert result.error is None
    assert result.gold == 0


def test_gold_must_be_a_whole_number():
    for value in ("'lots'", "1.5", "True", "None"):
        result = CoinSession(wallet_code(f"self.gold = {value}")).pick_up_coin()
        assert "whole number" in result.error, value
        assert result.gold == 0


def test_gold_must_be_a_whole_number_from_the_start_too():
    session = CoinSession(wallet_code("pass", init_body="self.gold = 'lots'"))
    assert "whole number" in session.setup_error


# --- the object has to be there -----------------------------------------------
def test_missing_wallet_class_is_explained():
    session = CoinSession("x = 1")
    assert "class Wallet" in session.setup_error
    assert session.pick_up_coin().error == session.setup_error


def test_missing_add_coin_is_explained():
    session = CoinSession("class Wallet:\n    def __init__(self):\n        self.gold = 0\n")
    assert "add_coin" in session.setup_error


def test_missing_gold_is_explained():
    session = CoinSession("class Wallet:\n    def add_coin(self):\n        pass\n")
    assert "whole number" in session.setup_error


# --- say --------------------------------------------------------------------
def test_say_and_print_are_recorded_before_the_gold():
    code = wallet_code("say('Ka-ching!', 5)\nprint('yay')\nself.gold += 1")
    result = CoinSession(code).pick_up_coin()
    assert result.events == [("say", "Ka-ching! 5"), ("say", "yay"), ("gold", 1)]


def test_events_do_not_pile_up_between_coins():
    session = CoinSession(wallet_code("say('hi')\nself.gold += 1"))
    session.pick_up_coin()
    assert session.pick_up_coin().events == [("say", "hi"), ("gold", 2)]


# --- if and for still work inside add_coin ------------------------------------
def test_if_and_for_work():
    code = wallet_code("for i in range(3):\n    self.gold = self.gold + 1\nif self.gold > 2:\n    say('rich!')")
    result = CoinSession(code).pick_up_coin()
    assert result.gold == 3
    assert ("say", "rich!") in result.events


# --- friendly errors --------------------------------------------------------
def test_syntax_error_is_friendly():
    session = CoinSession("class Wallet:\n    def __init__(self)\n        self.gold = 0\n")
    assert session.setup_error.startswith("Typo on line 2")
    assert "Traceback" not in session.setup_error


def test_mistake_inside_add_coin_names_the_line():
    result = CoinSession(wallet_code("self.gold = self.gld + 1")).pick_up_coin()
    assert result.error.startswith("AttributeError on line 5")
    assert "gld" in result.error


def test_name_error_for_unknown_name():
    result = CoinSession(wallet_code("self.gold = golt + 1")).pick_up_coin()
    assert result.error.startswith("NameError on line 5")
    assert result.gold == 0


def test_error_keeps_the_old_gold_in_the_result():
    session = CoinSession(wallet_code("self.gold += 1\nif self.gold == 2:\n    boom()"))
    assert session.pick_up_coin().gold == 1
    result = session.pick_up_coin()
    assert result.error is not None
    assert result.gold == 1


def test_import_is_blocked():
    session = CoinSession("import os\n" + PLUS_ONE)
    assert session.setup_error.startswith("ImportError on line 1")


def test_dangerous_builtins_are_missing():
    for body in ("open('x.txt')", "exec('1')", "eval('1')", "__import__('os')"):
        assert CoinSession(wallet_code(body)).pick_up_coin().error is not None, body


# --- runaway code -----------------------------------------------------------
def test_infinite_loop_in_add_coin_is_stopped():
    result = CoinSession(wallet_code("while True: pass")).pick_up_coin()
    assert result.error.startswith("TimeoutError")
    assert "never ending" in result.error


def test_infinite_loop_outside_the_class_is_stopped():
    session = CoinSession("while True: pass\n" + PLUS_ONE)
    assert session.setup_error.startswith("TimeoutError")


def test_endless_messages_are_stopped():
    result = CoinSession(wallet_code("while True:\n    say('hi')")).pick_up_coin()
    assert "Too many messages" in result.error
    assert len(result.events) <= MAX_ACTIONS + 1


def test_tracing_is_switched_off_after_a_run():
    CoinSession(wallet_code("while True: pass")).pick_up_coin()
    assert sys.gettrace() is None
