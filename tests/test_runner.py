"""Tests for run_coin_code(): the part that runs the player's coin code.

The code runs once per coin, with `wallet` already set to the current amount.
"""
import sys

from code_quest.config import MAX_ACTIONS
from code_quest.runner.runner import run_coin_code


# --- the wallet exercise ----------------------------------------------------
def test_wallet_plus_one():
    result = run_coin_code("wallet = wallet + 1", 0)
    assert result.error is None
    assert result.wallet == 1
    assert result.events == [("wallet", 1)]


def test_wallet_builds_on_what_it_already_has():
    assert run_coin_code("wallet = wallet + 1", 4).wallet == 5


def test_plus_equals_works_too():
    assert run_coin_code("wallet += 5", 2).wallet == 7


def test_code_that_does_nothing_leaves_wallet_alone():
    result = run_coin_code("# no code yet\n\n", 3)
    assert result.error is None
    assert result.wallet == 3


def test_wallet_can_be_set_directly():
    assert run_coin_code("wallet = 10", 0).wallet == 10


def test_wallet_must_be_a_whole_number():
    for code in ("wallet = 'lots'", "wallet = 1.5", "wallet = True", "del wallet"):
        result = run_coin_code(code, 0)
        assert result.error is not None, code
        assert "whole number" in result.error
        assert result.wallet == 0


# --- say --------------------------------------------------------------------
def test_say_and_print_are_recorded_before_the_wallet():
    result = run_coin_code("say('Ka-ching!', 5)\nprint('yay')\nwallet = wallet + 1", 0)
    assert result.events == [("say", "Ka-ching! 5"), ("say", "yay"), ("wallet", 1)]


# --- loops and ifs still work inside coin code -------------------------------
def test_if_and_for_work():
    code = "for i in range(3):\n    wallet = wallet + 1\nif wallet > 2:\n    say('rich!')"
    result = run_coin_code(code, 0)
    assert result.wallet == 3
    assert ("say", "rich!") in result.events


# --- friendly errors --------------------------------------------------------
def test_syntax_error_is_friendly():
    result = run_coin_code("wallet = wallet +", 0)
    assert result.error.startswith("Typo on line 1")
    assert "Traceback" not in result.error
    assert result.wallet == 0


def test_name_error_for_unknown_name():
    result = run_coin_code("wallet = walet + 1", 0)
    assert result.error.startswith("NameError on line 1")
    assert "walet" in result.error
    assert result.wallet == 0


def test_error_keeps_the_old_wallet():
    result = run_coin_code("wallet = wallet + 100\nboom()", 7)
    assert result.error is not None
    assert result.wallet == 7


def test_import_is_blocked():
    result = run_coin_code("import os", 0)
    assert result.error.startswith("ImportError on line 1")


def test_dangerous_builtins_are_missing():
    for code in ("open('x.txt')", "exec('1')", "eval('1')", "__import__('os')"):
        assert run_coin_code(code, 0).error is not None, code


# --- runaway code -----------------------------------------------------------
def test_infinite_loop_is_stopped():
    result = run_coin_code("while True: pass", 0)
    assert result.error.startswith("TimeoutError")
    assert "never ending" in result.error


def test_endless_messages_are_stopped():
    result = run_coin_code("while True:\n    say('hi')", 0)
    assert "Too many messages" in result.error
    assert len(result.events) <= MAX_ACTIONS + 1


def test_tracing_is_switched_off_after_a_run():
    run_coin_code("while True: pass", 0)
    assert sys.gettrace() is None
