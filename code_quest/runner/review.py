"""The sign's advice: what went wrong, or how the code could be better.

Two sources of advice:
  - what the code *did*: the gold added for each coin that was picked up
  - what the code *looks like*: a look at the code itself (using `ast`)

No pygame in here.
"""
import ast
from collections import namedtuple

# One entry per coin picked up: its color, what it should add, what the wallet
# really went up by, and the error (if the code crashed).
CoinLog = namedtuple("CoinLog", "color expected delta error")

MAX_TIPS = 3


class Review:
    def __init__(self, passed, pages):
        self.passed = passed   # True if the Wallet is right and every coin was found
        self.pages = pages     # what the sign says, one text box at a time


def _coin_name(level, color):
    """'coin' when all coins are alike, otherwise 'red coin' etc."""
    return "coin" if len(level.coin_values) == 1 else f"{color} coin"


def _problems(level, coin_log):
    """One sentence for each kind of coin that the Wallet got wrong."""
    problems, seen = [], set()
    for entry in coin_log:
        if entry.color in seen:
            continue
        name = _coin_name(level, entry.color)
        if entry.error:
            problems.append(f"When a {name} was picked up, your code crashed: {entry.error}")
        elif entry.delta != entry.expected:
            if entry.delta == 0:
                problems.append(f"A {name} should add {entry.expected} gold, but your gold did not change.")
            else:
                problems.append(f"A {name} should add {entry.expected} gold, but your gold went up by {entry.delta}.")
        else:
            continue
        seen.add(entry.color)
    return problems


def _find_add_coin(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Wallet":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "add_coin":
                    return item
    return None


def _is_self_gold(node):
    return (isinstance(node, ast.Attribute) and node.attr == "gold"
            and isinstance(node.value, ast.Name) and node.value.id == "self")


def code_tips(level, source):
    """Ideas for making working code nicer. Most important first."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    add_coin = _find_add_coin(tree)
    if add_coin is None:
        return []
    inside = list(ast.walk(add_coin))
    tips = []

    if any(isinstance(n, ast.Pass) for n in inside):
        tips.append("There is still a `pass` line in add_coin(). It does nothing now, so you can delete it.")

    for n in inside:   # self.gold = self.gold + 1   ->   self.gold += 1
        if (isinstance(n, ast.Assign) and len(n.targets) == 1 and _is_self_gold(n.targets[0])
                and isinstance(n.value, ast.BinOp) and isinstance(n.value.op, ast.Add)
                and _is_self_gold(n.value.left)):
            tips.append("`self.gold = self.gold + 1` can be written shorter as `self.gold += 1`.")
            break

    if level.passes_color:
        top_ifs = [n for n in add_coin.body if isinstance(n, ast.If)]
        has_dict = any(isinstance(n, ast.Dict) for n in ast.walk(tree))
        if len(top_ifs) >= 2 and not any(i.orelse for i in top_ifs):
            tips.append("You used several separate `if`s. Joining them with `elif` is clearer, "
                        "and Python stops checking once one matches.")
        if has_dict:
            tips.append("Nice, you used a dictionary. Adding a new coin color is just one new line!")
        elif top_ifs:
            tips.append("Idea: a dictionary like VALUES = {'normal': 1, 'red': 5, 'sapphire': 10} "
                        "would let you look up the gold with VALUES[color] in one line.")
            chain = top_ifs[-1]
            while chain.orelse and len(chain.orelse) == 1 and isinstance(chain.orelse[0], ast.If):
                chain = chain.orelse[0]
            if not chain.orelse:
                tips.append("What if a new color shows up? An `else:` at the end can decide what to do.")
    return tips[:MAX_TIPS]


def review_code(level, source, coin_log, collected, next_level_exists):
    """Build the sign's pages after the hero reaches it."""
    remaining = len(level.coins) - collected
    problems = _problems(level, coin_log)

    if remaining:
        pages = [f"The sign reads: 'Not so fast, hero! {remaining} coin(s) are still hiding in the forest.'"]
        if problems:
            pages.append("'Also, your Wallet has a problem.' " + problems[0])
        pages.append("'Go find the rest of the coins, then come back to me.'")
        return Review(False, pages)

    if problems:
        pages = ["The sign reads: 'Your Wallet is not quite right yet.'"]
        pages += [f"'{p}'" for p in problems[:3]]
        pages.append("'Press Esc to fix your code, then F5 to try again.'")
        return Review(False, pages)

    pages = [f"LEVEL COMPLETE! Your Wallet counted {level.total_gold()} gold. Great work!"]
    tips = code_tips(level, source)
    if tips:
        pages.append("The sign reads: 'Your code works! Here is how it could be even better.'")
        pages += [f"Tip {i}: {t}" for i, t in enumerate(tips, 1)]
    else:
        pages.append("The sign reads: 'I cannot find anything to improve. Beautiful code!'")
    pages.append("Press N for the next level." if next_level_exists
                 else "You finished every level so far. Well done, coder!")
    return Review(True, pages)
