"""Tests for run_player_code(): the part of Code Quest that runs the kid's code.

Map facts used below (x, y), with (0, 0) at the top-left:
  - The hero starts at (1, 1).
  - (1, 0) is a wall (above the hero) and (1, 2) is floor (below the hero).
  - Row 1 is open from x=1 to x=6, and (7, 1) is a wall.
  - There is a coin at (3, 3).
"""
from code_quest.config import MAX_ACTIONS
from code_quest.levels.level_01 import LEVEL_01
from code_quest.runner.runner import run_player_code as _run

START = LEVEL_01.start


def run_player_code(source):
    return _run(source, LEVEL_01)


def moves(result):
    return [e for e in result.events if e[0] == "move"]


# --- normal moves -----------------------------------------------------------
def test_move_right_records_one_event_per_step():
    result = run_player_code("move_right(3)")
    assert result.error is None
    assert result.events == [("move", 2, 1), ("move", 3, 1), ("move", 4, 1)]


def test_move_defaults_to_one_step():
    result = run_player_code("move_down()")
    assert result.events == [("move", 1, 2)]


def test_starter_code_runs_without_error():
    result = run_player_code("# Move the hero to the G!\nmove_down(2)\n")
    assert result.error is None
    assert moves(result)[-1] == ("move", 1, 3)


def test_empty_code_does_nothing():
    result = run_player_code("")
    assert result.error is None
    assert result.events == []


def test_say_and_print_are_recorded():
    result = run_player_code("say('hi', 5)\nprint('there')")
    assert result.events == [("say", "hi 5"), ("say", "there")]


# --- walls ------------------------------------------------------------------
def test_walking_into_a_wall_bumps():
    result = run_player_code("move_up()")
    assert result.error is None
    assert result.events == [("bump", START[0], START[1])]


def test_bump_stops_the_rest_of_that_move():
    # Row 1 ends at x=6, so only 5 of the 10 steps can happen.
    result = run_player_code("move_right(10)")
    assert len(moves(result)) == 5
    assert result.events[-1] == ("bump", 6, 1)


# --- coins ------------------------------------------------------------------
def test_coin_is_picked_up_once():
    result = run_player_code("move_right(5)\nmove_down(2)\nmove_left(3)")
    assert result.error is None
    assert result.events.count(("coin", 3, 3)) == 1
    # The coin event comes right after stepping onto the coin tile.
    i = result.events.index(("coin", 3, 3))
    assert result.events[i - 1] == ("move", 3, 3)


def test_walking_over_a_coin_twice_gives_only_one_coin():
    result = run_player_code(
        "move_right(5)\nmove_down(2)\nmove_left(3)\nmove_right(1)\nmove_left(1)"
    )
    assert [e for e in result.events if e[0] == "coin"] == [("coin", 3, 3)]


# --- loops and if -----------------------------------------------------------
def test_for_loop_repeats_moves():
    result = run_player_code("for i in range(3):\n    move_right()")
    assert result.error is None
    assert [(e[1], e[2]) for e in moves(result)] == [(2, 1), (3, 1), (4, 1)]


def test_wall_ahead_sees_walls_and_floor():
    result = run_player_code(
        "if wall_ahead('up'):\n    say('wall up')\n"
        "if wall_ahead('down'):\n    say('wall down')\n"
        "else:\n    say('clear down')"
    )
    assert result.error is None
    assert result.events == [("say", "wall up"), ("say", "clear down")]


def test_if_wall_ahead_inside_a_loop():
    code = (
        "for i in range(8):\n"
        "    if wall_ahead('right'):\n"
        "        say('wall!')\n"
        "    else:\n"
        "        move_right()\n"
    )
    result = run_player_code(code)
    assert result.error is None
    assert moves(result)[-1] == ("move", 6, 1)
    assert result.events.count(("say", "wall!")) == 3  # 8 turns - 5 moves


def test_wall_ahead_rejects_a_bad_direction():
    result = run_player_code("wall_ahead('sideways')")
    assert result.error.startswith("ValueError on line 1")
    assert "'up', 'down', 'left' or 'right'" in result.error


# --- friendly errors --------------------------------------------------------
def test_syntax_error_is_friendly():
    result = run_player_code("move_right(")
    assert result.error is not None
    assert result.error.startswith("Typo on line 1")
    assert "Traceback" not in result.error


def test_syntax_error_runs_nothing():
    result = run_player_code("move_right(2)\nmove_down(")
    assert result.events == []


def test_name_error_for_unknown_command():
    result = run_player_code("move_right(1)\njump()")
    assert result.error.startswith("NameError on line 2")
    assert "jump" in result.error
    # Moves made before the mistake are still recorded.
    assert result.events == [("move", 2, 1)]


def test_import_is_blocked():
    result = run_player_code("import os")
    assert result.error is not None
    assert result.error.startswith("ImportError on line 1")


def test_dangerous_builtins_are_missing():
    for code in ("open('x.txt')", "exec('1')", "eval('1')", "__import__('os')"):
        result = run_player_code(code)
        assert result.error is not None, code


# --- runaway code -----------------------------------------------------------
def test_infinite_loop_is_stopped():
    result = run_player_code("while True: pass")
    assert result.error is not None
    assert result.error.startswith("TimeoutError")
    assert "never ending" in result.error


def test_endless_moving_is_stopped_by_action_limit():
    result = run_player_code("while True:\n    move_right()\n    move_left()")
    assert result.error is not None
    assert "Too many actions" in result.error
    assert len(result.events) <= MAX_ACTIONS + 1


def test_tracing_is_switched_off_after_a_run():
    import sys

    run_player_code("while True: pass")
    assert sys.gettrace() is None
