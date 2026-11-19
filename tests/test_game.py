"""End-to-end test: drive the real Game object with key presses, no window needed."""
import os
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402  (must come after the environment variables)

from code_quest.config import EVENT_MS, STEP_MS  # noqa: E402
from code_quest.engine.game import Game  # noqa: E402
from code_quest.levels import LEVELS  # noqa: E402

DIRECTIONS = {(1, 0): pygame.K_RIGHT, (-1, 0): pygame.K_LEFT, (0, 1): pygame.K_DOWN, (0, -1): pygame.K_UP}

LEVEL_1_CODE = (
    "class Wallet:\n    def __init__(self):\n        self.gold = 0\n"
    "    def add_coin(self):\n        self.gold += 1\n"
)
LEVEL_2_CODE = (
    "VALUES = {'normal': 1, 'red': 5, 'sapphire': 10}\n"
    "class Wallet:\n    def __init__(self):\n        self.gold = 0\n"
    "    def add_coin(self, color):\n        self.gold += VALUES[color]\n"
)


def key_down(key, mod=0):
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode="", mod=mod)


def route(level, start, target):
    """The tiles to walk through to get from start to target."""
    came_from, queue = {start: None}, deque([start])
    while queue:
        here = queue.popleft()
        for dx, dy in DIRECTIONS:
            nxt = (here[0] + dx, here[1] + dy)
            if nxt not in came_from and not level.is_wall(*nxt):
                came_from[nxt] = here
                queue.append(nxt)
    steps, tile = [], target
    while came_from[tile]:
        steps.append(tile)
        tile = came_from[tile]
    return steps[::-1]


def walk_to(game, target):
    for tile in route(game.level, tuple(game.world.hero), target):
        here = tuple(game.world.hero)
        key = DIRECTIONS[(tile[0] - here[0], tile[1] - here[1])]
        game.handle_event(key_down(key))
        game.update(16)                                    # the step starts
        game.handle_event(pygame.event.Event(pygame.KEYUP, key=key))
        game.update(STEP_MS + 1)                           # the step ends: coin / sign handling
        while game.queue:
            game.update(EVENT_MS + 1)                      # play the recorded messages


def read_the_sign(game):
    pages = []
    while game.reading:
        game.update(5000)                                  # let the typewriter finish
        pages.append(game.message)
        game.handle_event(key_down(pygame.K_SPACE))
    return pages


def play_level(game, code):
    game.editor.lines = code.split("\n")
    game.handle_event(key_down(pygame.K_F5))
    assert game.mode == "play"
    targets = sorted(game.level.coins, key=lambda c: len(route(game.level, game.level.start, c)))
    for target in targets + [game.level.goal]:
        walk_to(game, target)
    return read_the_sign(game)


def test_play_level_1_then_level_2_with_colored_coins():
    game = Game(LEVELS)
    assert game.level.name == "Level 1"

    pages = play_level(game, LEVEL_1_CODE)
    assert game.gold == 3
    assert game.level_done
    assert pages[0].startswith("LEVEL COMPLETE")
    assert pages[-1] == "Press N for the next level."

    game.handle_event(key_down(pygame.K_n))
    assert game.level.name == "Level 2"
    assert game.mode == "edit"
    assert "def add_coin(self, color)" in game.editor.text

    pages = play_level(game, LEVEL_2_CODE)
    assert game.gold == 23                                 # 3 normal + 2 red + 1 sapphire
    assert game.level_done
    assert any("Nice, you used a dictionary" in page for page in pages)
    assert "finished every level" in pages[-1]
    pygame.quit()


def test_wrong_level_2_code_makes_the_sign_explain_the_mistake():
    game = Game(LEVELS)
    game.load_level(1)
    pages = play_level(game, LEVEL_2_CODE.replace("VALUES[color]", "1"))
    assert game.gold == 6                                  # every coin counted as 1
    assert not game.level_done
    assert any("red coin should add 5" in page for page in pages)
    assert "Esc" in pages[-1]
    pygame.quit()


def test_a_typo_is_caught_by_f5_and_the_game_does_not_start():
    game = Game(LEVELS)
    game.editor.lines = ["class Wallet:", "    def __init__(self)", "        self.gold = 0"]
    game.handle_event(key_down(pygame.K_F5))
    assert game.mode == "edit"
    assert game.message.startswith("Typo on line 2")
    pygame.quit()


def test_arrow_keys_move_the_cursor_while_editing_and_the_hero_while_playing():
    game = Game(LEVELS)
    start = list(game.world.hero)
    game.handle_event(key_down(pygame.K_DOWN))
    game.update(16)
    assert game.world.hero == start                        # editing: the hero stays put
    game.handle_event(key_down(pygame.K_F5))               # the stub is valid, so the game starts
    assert game.mode == "play"
    game.handle_event(key_down(pygame.K_DOWN))
    game.update(16)
    assert game.world.hero == [start[0], start[1] + 1]
    pygame.quit()
