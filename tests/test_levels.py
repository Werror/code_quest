"""The starter code is the first thing a player sees, so it must be safe to run."""
from code_quest.levels import LEVELS
from code_quest.levels.level_01 import LEVEL_01
from code_quest.levels.level_02 import LEVEL_02
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
    assert set(LEVEL_01.coins) <= seen
    assert len(LEVEL_01.coins) == 3


def test_every_level_is_a_rectangle_and_can_be_finished_on_foot():
    from collections import deque
    for level in LEVELS:
        assert len({len(r) for r in level.rows}) == 1, level.name
        seen, queue = {level.start}, deque([level.start])
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and not level.is_wall(nx, ny):
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        assert level.goal in seen, level.name
        assert set(level.coins) <= seen, level.name


def test_level_1_has_only_normal_coins():
    assert set(LEVEL_01.coins.values()) == {"normal"}
    assert LEVEL_01.total_gold() == 3
    assert LEVEL_01.passes_color is False


def test_level_2_has_all_three_coin_colors_worth_23_gold():
    colors = sorted(LEVEL_02.coins.values())
    assert colors == ["normal"] * 3 + ["red"] * 2 + ["sapphire"]
    assert LEVEL_02.coin_values == {"normal": 1, "red": 5, "sapphire": 10}
    assert LEVEL_02.total_gold() == 23
    assert LEVEL_02.passes_color is True


def test_level_2_starter_code_is_a_safe_stub_that_takes_a_color():
    code = LEVEL_02.starter_code
    assert "def add_coin(self, color)" in code
    session = CoinSession(code, pass_color=True)
    assert session.setup_error is None
    for color in LEVEL_02.coin_values:
        result = session.pick_up_coin(color)
        assert result.error is None and result.gold == 0


def test_every_level_has_an_intro_and_starter_lines_that_fit():
    for level in LEVELS:
        assert level.intro
        assert all(len(line) <= 35 for line in level.starter_code.split("\n")), level.name
