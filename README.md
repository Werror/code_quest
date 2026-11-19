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
python main.py
```

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## How to play

1. In the code box, finish the `Wallet` object. In level 1, make `add_coin()` add 1 to `self.gold`.
2. Press **F5**. If your code has a mistake, the game tells you. If not, the game starts.
3. Walk with the **arrow keys**. Pick up the coins, then reach the sign.
   Each coin calls your `wallet.add_coin()`, and the GOLD box shows `wallet.gold`.

| Key | What it does |
| --- | --- |
| F5 (or Ctrl+Enter) | Check your code and start the game |
| Arrow keys | Walk (while playing) or move the text cursor (while editing) |
| Esc | Stop playing and go back to editing |
| F6 | Reset the level |

## Activate the virtual environment first

Each new terminal needs `source .venv/bin/activate` before `python main.py`.
