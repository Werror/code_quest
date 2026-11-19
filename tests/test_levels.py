"""The starter code is the first thing a player sees, so it must be safe to run."""
from code_quest.levels.level_01 import LEVEL_01
from code_quest.runner.runner import run_coin_code


def test_starter_code_runs_without_error_and_changes_nothing():
    result = run_coin_code(LEVEL_01.starter_code, 0)
    assert result.error is None
    assert result.wallet == 0


def test_starter_code_explains_input_and_output():
    assert "INPUT" in LEVEL_01.starter_code
    assert "OUTPUT" in LEVEL_01.starter_code


def test_starter_lines_fit_in_the_code_box():
    # The code panel shows about 35 characters before the text is cut off.
    for line in LEVEL_01.starter_code.split("\n"):
        assert len(line) <= 35, line
