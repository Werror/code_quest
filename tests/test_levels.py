"""The starter code is the first thing a player sees, so it must be safe to run."""
from code_quest.levels.level_01 import LEVEL_01
from code_quest.runner.runner import CoinSession


def test_starter_code_runs_without_error_and_changes_nothing():
    session = CoinSession(LEVEL_01.starter_code)
    assert session.setup_error is None
    result = session.pick_up_coin()
    assert result.error is None
    assert result.gold == 0


def test_starter_code_has_a_wallet_object_with_stubs():
    code = LEVEL_01.starter_code
    assert "class Wallet" in code
    assert "def add_coin(self)" in code
    assert "self.gold" in code


def test_starter_lines_fit_in_the_code_box():
    # The code panel shows about 35 characters before the text is cut off.
    for line in LEVEL_01.starter_code.split("\n"):
        assert len(line) <= 35, line
