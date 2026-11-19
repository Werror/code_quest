"""Tests for the sign's advice (runner/review.py)."""
from code_quest.levels import LEVELS
from code_quest.runner.review import CoinLog, code_tips, review_code
from code_quest.runner.runner import CoinSession

LEVEL_1, LEVEL_2 = LEVELS

LONG_FORM = "class Wallet:\n    def __init__(self):\n        self.gold = 0\n    def add_coin(self):\n        self.gold = self.gold + 1\n"
SHORT_FORM = LONG_FORM.replace("self.gold = self.gold + 1", "self.gold += 1")
LEFT_PASS = SHORT_FORM + "        pass\n"

HEAD = "class Wallet:\n    def __init__(self):\n        self.gold = 0\n    def add_coin(self, color):\n"
IF_ELIF = HEAD + (
    "        if color == 'normal':\n            self.gold += 1\n"
    "        elif color == 'red':\n            self.gold += 5\n"
    "        elif color == 'sapphire':\n            self.gold += 10\n")
IF_ELIF_ELSE = IF_ELIF + "        else:\n            self.gold += 0\n"
SEPARATE_IFS = HEAD + (
    "        if color == 'normal':\n            self.gold += 1\n"
    "        if color == 'red':\n            self.gold += 5\n"
    "        if color == 'sapphire':\n            self.gold += 10\n")
WITH_DICT = HEAD.replace("class Wallet:", "VALUES = {'normal': 1, 'red': 5, 'sapphire': 10}\nclass Wallet:") + "        self.gold += VALUES[color]\n"
ALWAYS_ONE = HEAD + "        self.gold += 1\n"

ALL_COLORS = ["normal", "normal", "normal", "red", "red", "sapphire"]


def play(level, code, colors):
    """Pretend the hero picked up these coins in order, and record what the Wallet did."""
    session = CoinSession(code, level.passes_color)
    log, gold = [], 0
    for color in colors:
        result = session.pick_up_coin(color)
        log.append(CoinLog(color, level.coin_values[color], result.gold - gold, result.error))
        gold = result.gold
    return log


def review(level, code, colors, collected=None, next_exists=True):
    collected = len(colors) if collected is None else collected
    return review_code(level, code, play(level, code, colors), collected, next_exists)


# --- passing ----------------------------------------------------------------
def test_working_code_passes_and_celebrates_first():
    result = review(LEVEL_1, SHORT_FORM, ["normal"] * 3)
    assert result.passed
    assert result.pages[0].startswith("LEVEL COMPLETE")
    assert "3 gold" in result.pages[0]


def test_perfect_level_1_code_gets_praise_not_tips():
    result = review(LEVEL_1, SHORT_FORM, ["normal"] * 3)
    assert any("Beautiful code" in page for page in result.pages)
    assert not any(page.startswith("Tip") for page in result.pages)


def test_last_page_points_to_the_next_level_or_the_end():
    assert review(LEVEL_1, SHORT_FORM, ["normal"] * 3, next_exists=True).pages[-1] == "Press N for the next level."
    assert "finished every level" in review(LEVEL_1, SHORT_FORM, ["normal"] * 3, next_exists=False).pages[-1]


# --- tips from reading the code ---------------------------------------------
def test_tip_to_shorten_gold_plus_one():
    assert any("self.gold += 1" in t for t in code_tips(LEVEL_1, LONG_FORM))
    assert not any("self.gold += 1" in t for t in code_tips(LEVEL_1, SHORT_FORM))


def test_tip_to_delete_a_leftover_pass():
    assert any("`pass`" in t for t in code_tips(LEVEL_1, LEFT_PASS))
    assert not any("`pass`" in t for t in code_tips(LEVEL_1, SHORT_FORM))


def test_tip_to_use_elif_for_separate_ifs():
    assert any("elif" in t for t in code_tips(LEVEL_2, SEPARATE_IFS))
    assert not any("separate" in t for t in code_tips(LEVEL_2, IF_ELIF))


def test_if_chain_without_else_gets_a_dictionary_idea_and_an_else_tip():
    tips = " ".join(code_tips(LEVEL_2, IF_ELIF))
    assert "dictionary" in tips
    assert "else:" in tips


def test_an_else_branch_removes_the_else_tip():
    assert "else:" not in " ".join(code_tips(LEVEL_2, IF_ELIF_ELSE))


def test_using_a_dictionary_is_praised():
    tips = code_tips(LEVEL_2, WITH_DICT)
    assert any("Nice, you used a dictionary" in t for t in tips)
    assert not any("Idea" in t for t in tips)


def test_never_more_than_three_tips():
    messy = SEPARATE_IFS + "        pass\n"
    assert len(code_tips(LEVEL_2, messy)) <= 3


def test_tips_are_shown_as_numbered_pages():
    result = review(LEVEL_2, IF_ELIF, ALL_COLORS)
    assert result.passed
    assert result.pages[2].startswith("Tip 1:")


# --- wrong code ---------------------------------------------------------------
def test_wallet_that_adds_one_for_every_color_fails_and_says_why():
    result = review(LEVEL_2, ALWAYS_ONE, ALL_COLORS)
    assert not result.passed
    text = " ".join(result.pages)
    assert "red coin should add 5 gold, but your gold went up by 1" in text
    assert "sapphire coin should add 10" in text
    assert "Esc" in result.pages[-1]


def test_level_1_wording_says_coin_not_normal_coin():
    code = LONG_FORM.replace("+ 1", "+ 2")
    text = " ".join(review(LEVEL_1, code, ["normal"] * 3).pages)
    assert "A coin should add 1 gold, but your gold went up by 2" in text


def test_a_wallet_that_never_changes_is_called_out():
    code = LONG_FORM.replace("self.gold = self.gold + 1", "pass")
    text = " ".join(review(LEVEL_1, code, ["normal"] * 3).pages)
    assert "did not change" in text


def test_a_crashing_wallet_shows_the_error():
    code = LONG_FORM.replace("self.gold + 1", "self.gld + 1")
    result = review(LEVEL_1, code, ["normal"] * 3)
    assert not result.passed
    assert "crashed" in " ".join(result.pages)
    assert "gld" in " ".join(result.pages)


def test_each_wrong_coin_color_is_mentioned_once():
    text = " ".join(review(LEVEL_2, ALWAYS_ONE, ALL_COLORS).pages)
    assert text.count("red coin should add") == 1


# --- not finished yet ---------------------------------------------------------
def test_missing_coins_are_counted_and_level_is_not_complete():
    result = review(LEVEL_1, SHORT_FORM, ["normal"], collected=1)
    assert not result.passed
    assert "2 coin(s) are still hiding" in result.pages[0]


def test_missing_coins_still_mention_a_wallet_problem():
    result = review(LEVEL_2, ALWAYS_ONE, ["red"], collected=1)
    assert not result.passed
    assert any("red coin should add 5" in page for page in result.pages)
