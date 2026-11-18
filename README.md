# Code Quest

A tiny 2D RPG where you learn Python by writing real code to move the hero
to the goal (`G`) and collect coins.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python code_quest.py
```

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Controls

- Type in the code box on the right.
- **F5** or **Ctrl+Enter**: run your code
- **F6**: reset the level

## Commands you can use

`move_right(3)`, `move_left()`, `move_up()`, `move_down()`,
`wall_ahead('right')`, `say('hi')`, plus `for` loops and `if`.
