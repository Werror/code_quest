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


def test_the_map_is_a_proper_rectangle_with_one_start_and_one_goal():
    rows = LEVEL_01.rows
    assert len({len(r) for r in rows}) == 1
    text = "".join(rows)
    assert text.count("P") == 1 and text.count("G") == 1


def test_every_coin_and_the_goal_can_be_reached_on_foot():
    from collections import deque
    seen, queue = {LEVEL_01.start}, deque([LEVEL_01.start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and not LEVEL_01.is_wall(nx, ny):
                seen.add((nx, ny))
                queue.append((nx, ny))
    assert LEVEL_01.goal in seen
    assert LEVEL_01.coins <= seen
    assert len(LEVEL_01.coins) == 3
