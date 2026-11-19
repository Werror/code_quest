# Code Quest

A 2D RPG for **12-year-olds** where the player learns Python by typing real
code into an in-game editor. The hero walks around a tile map; the player's
code tells the hero what to do.

## Audience rules
- Every message the player sees must be **friendly and plain-language**
  (no raw tracebacks, no jargon without explanation).
- Code should be **readable**: simple names, short functions, comments that
  explain *why*. The project owner is learning as they go, so explain changes
  in plain language.

## How the game plays
- The player walks the hero with the **arrow keys**. There are two modes:
  **edit** (arrows move the text cursor) and **play** (arrows walk the hero).
- **F5** checks the code once, and if it works, starts the game with it.
  **Esc** goes back to editing. **F6** resets the level.
- The code box holds an **object** for the item. Level 1 is the coin: the
  starter code has a stubbed `class Wallet` (with `self.gold` and an empty
  `add_coin(self)`). The game makes one `Wallet()` when F5 is pressed and calls
  `wallet.add_coin()` each time a coin is picked up. The player fills in
  `self.gold = self.gold + 1`. The GOLD box shows `wallet.gold`. Reaching the
  sign checks that the gold matches the coins taken.
- Each new item should likewise be a small class with stubbed methods, so the
  player learns object-oriented Python from the start.
- **Level 2 has colored coins.** Map letters: `C` normal (1 gold), `R` red (5),
  `S` sapphire (10). The game calls `add_coin(self, color)` with the color name;
  the *player's code* turns the color into gold (if/elif, then dictionaries).
  The game only knows the true values (`COIN_VALUES` in `levels/level.py`) to
  check the player's work.
- **The sign** (the goal) shows a multi-page message (Space = next page). If the
  Wallet is wrong it explains which coin color added the wrong amount; if it
  is right it reads the code with `ast` and gives up to 3 improvement tips
  (shorter `+=`, leftover `pass`, `elif`, dictionary, `else`). Press **N** after
  a finished level for the next one (N works as soon as the last page shows).
- **Messages:** passing messages ("Ouch!", "Coin!", `say()`) disappear after
  `MESSAGE_SECONDS` (3). Errors and the sign's pages stay until dealt with.

## Architecture
```
main.py                     entry point
code_quest/
  config.py                 sizes, speeds, limits, colors
  engine/game.py            Game class: window, levels, modes, playback of recorded events
  engine/world.py           hero position, coins, walking rules (no pygame)
  engine/renderer.py        all drawing (never changes game state)
  engine/sprites.py         loads and scales the pixel art
  engine/tiles.py           which tile number is which in the art packs
  engine/scenery.py         picks the picture for every map tile (tall trees, etc.)
  engine/camera.py          follows the hero; the map is bigger than the window
  runner/runner.py          CoinSession: holds the player's Wallet object
  runner/review.py          the sign's advice: what went wrong, tips from reading the code
  runner/api.py             commands the player's code can call (say, print)
  runner/errors.py          Python errors -> friendly messages
  editor/editor.py          the in-game code editor widget
  levels/level.py           Level class (map, start, goal, colored coins, starter code)
  levels/level_01.py, level_02.py   level data; levels/__init__.py has LEVELS (play order)
assets/                     Kenney Tiny Town + Tiny Dungeon (CC0)
tests/                      runner, review, world, scenery, camera, editor, level
                            and an end-to-end Game test (no window needed)
```
- **Trees:** `Scenery` mixes tall trees (two tiles stacked) with single-tile
  trees and bushes, mostly single. Tall trees are always drawn complete.
- **`runner/`, `world.py`, `scenery.py` and `camera.py` must never import pygame.** Keeps the
  command-queue rule honest and the tests fast.
- **Levels are data.** Engine and world receive a `Level`; no global map.
- **Safety:** restricted builtins, a `sys.settrace` line limit and a message
  limit stop infinite loops. They stop accidents, not determined attackers.

## The command-queue rule (core design, keep it)
The player's code **never** touches the real game or the screen. It runs in
its own sandbox (the player's `Wallet` object lives in a `CoinSession`) and only
appends events to a list: `("say", text)`, `("gold", number)`. The game loop
plays those events back one at a time. New items must follow this: simulate,
record events, animate later. The GOLD box only changes when the event is played.

## Working rules
- Small commits with clear messages.
- Don't add new gameplay features until the owner asks.
- The old `move_right(3)` / `wall_ahead` style commands were removed on purpose
  (arrow keys walk the hero now). They could return later as an "auto-walk" puzzle.
- Ideas for later (not yet): more levels each teaching one concept (loops,
  functions, lists), NPCs, doors and chests with their own code, combat,
  a hand-built village with houses and fences, a pixel font, friendlier
  Python error messages.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run: `python main.py`
- Test: `pytest`
