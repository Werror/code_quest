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

## Architecture (currently all in `code_quest.py`)
- **Game loop (pygame):** tile map on the left, code editor on the right.
  F5 / Ctrl+Enter runs the code, F6 resets the level.
- **`run_player_code(source)`:** runs the player's code against a *simulated*
  hero and records events: `("move", x, y)`, `("bump", x, y)`,
  `("coin", x, y)`, `("say", text)`. Returns a `RunResult` with `.events`
  and `.error` (a friendly string or `None`).
- **Playback:** the game animates the recorded events one at a time
  (one every 180 ms), then shows an `error` or `finish` message.
- **`Editor` widget:** a small hand-written text editor (auto-indent after
  `:`, 4-space tab/backspace, line limit).
- **Player API:** `move_up/down/left/right(n)`, `wall_ahead(direction)`,
  `say()` (`print` is an alias).
- **Safety:** restricted builtins, a `sys.settrace` line limit
  (`MAX_LINES_RUN`) and an action limit (`MAX_ACTIONS`) stop infinite loops.
  Restricted builtins stop accidents, not determined attackers; use a
  subprocess sandbox if this ever runs untrusted code on a server.

## The command-queue rule (core design, keep it)
Player code **never** touches the real hero or the screen. It only runs
against a simulated hero and appends events to a list. The game loop plays
those events back afterwards. New features (doors, NPCs, combat...) must
follow this: simulate during the run, record events, animate later.

## Working rules
- Small commits with clear messages.
- Don't add new gameplay features until the owner asks.
- Don't refactor the folder structure until the owner approves a plan.
- Ideas for later (not yet): multiple levels each teaching one concept
  (moves, loops, if, variables, functions), NPCs and doors, sprite art, combat.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run: `python code_quest.py`
- Test: `pytest`
