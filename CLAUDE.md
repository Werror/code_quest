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

## Architecture
```
main.py                     entry point
code_quest/
  config.py                 sizes, limits, colors
  engine/game.py            main loop + playback of recorded events
  engine/renderer.py        all drawing (never changes game state)
  runner/runner.py          run_player_code(source, level) -> RunResult
  runner/api.py             the player's commands (move_*, wall_ahead, say)
  runner/errors.py          Python errors -> friendly messages
  editor/editor.py          the in-game code editor widget
  levels/level.py           Level class (map, start, goal, coins, starter code)
  levels/level_01.py        level data
tests/test_runner.py
```
- **Run:** the player's code runs against a *simulated* hero and records
  events: `("move", x, y)`, `("bump", x, y)`, `("coin", x, y)`,
  `("say", text)`. `RunResult` has `.events` and `.error` (friendly string or `None`).
- **Playback:** the game animates the events one at a time (one every 180 ms),
  then shows an `error` or `finish` message.
- **`runner/` must never import pygame.** Keeps the command-queue rule honest
  and the tests fast.
- **Levels are data.** Runner and engine receive a `Level`; no global map.
- **Safety:** restricted builtins, a `sys.settrace` line limit and an action
  limit stop infinite loops. They stop accidents, not determined attackers.

## The command-queue rule (core design, keep it)
Player code **never** touches the real hero or the screen. It only runs
against a simulated hero and appends events to a list. The game loop plays
those events back afterwards. New features (doors, NPCs, combat...) must
follow this: simulate during the run, record events, animate later.

## Working rules
- Small commits with clear messages.
- Don't add new gameplay features until the owner asks.
- Ideas for later (not yet): multiple levels each teaching one concept
  (moves, loops, if, variables, functions), NPCs and doors, sprite art, combat.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run: `python main.py`
- Test: `pytest`
