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
- The code box holds the rule for an item. Level 1 is the coin: the code runs
  each time a coin is picked up, with a variable `wallet` already set to the
  current amount. The player writes `wallet = wallet + 1`. The GOLD box shows
  the wallet. Reaching the sign checks that the wallet matches the coins taken.
- More items (doors, NPCs, chests...) will each get their own exercise.

## Architecture
```
main.py                     entry point
code_quest/
  config.py                 sizes, speeds, limits, colors
  engine/game.py            main loop, modes, playback of recorded events
  engine/world.py           hero position, coins, walking rules (no pygame)
  engine/renderer.py        all drawing (never changes game state)
  engine/sprites.py         loads and scales the pixel art
  runner/runner.py          run_coin_code(source, wallet) -> RunResult
  runner/api.py             commands the player's code can call (say, print)
  runner/errors.py          Python errors -> friendly messages
  editor/editor.py          the in-game code editor widget
  levels/level.py           Level class (map, start, goal, coins, starter code)
  levels/level_01.py        level data
assets/                     Kenney Tiny Town + Tiny Dungeon (CC0)
tests/                      test_runner.py, test_world.py
```
- **`runner/` and `world.py` must never import pygame.** Keeps the
  command-queue rule honest and the tests fast.
- **Levels are data.** Engine and world receive a `Level`; no global map.
- **Safety:** restricted builtins, a `sys.settrace` line limit and a message
  limit stop infinite loops. They stop accidents, not determined attackers.

## The command-queue rule (core design, keep it)
The player's code **never** touches the real game or the screen. It runs
against *simulated* values (e.g. a copy of the wallet) and only appends
events to a list: `("say", text)`, `("wallet", number)`. The game loop plays
those events back one at a time. New items must follow this: simulate, record
events, animate later. The real wallet only changes when the event is played.

## Working rules
- Small commits with clear messages.
- Don't add new gameplay features until the owner asks.
- The old `move_right(3)` / `wall_ahead` style commands were removed on purpose
  (arrow keys walk the hero now). They could return later as an "auto-walk" puzzle.
- Ideas for later (not yet): more levels each teaching one concept (variables,
  if, loops, functions), NPCs, doors and chests with their own code, combat,
  a bigger village with a scrolling camera, a pixel font.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run: `python main.py`
- Test: `pytest`
