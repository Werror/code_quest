"""Settings shared by the whole game: sizes, limits and colors."""

SRC_TILE = 16            # size of one tile in the art files, in pixels
SCALE = 3                # how many times bigger we draw the pixels
TILE = SRC_TILE * SCALE  # size of one tile on screen
STEP_MS = 160            # how long the hero takes to walk one tile
MESSAGE_SECONDS = 3      # how long a passing message ("Ouch!", "Coin!"...) stays in the text box
EVENT_MS = 600           # how long each message from the player's code stays on screen
VIEW_COLS, VIEW_ROWS = 16, 12   # how many tiles you can see at once (the camera follows the hero)
VIEW_W, VIEW_H = VIEW_COLS * TILE, VIEW_ROWS * TILE
PANEL_W, BAR_H = 560, 96
TYPE_CHARS_PER_SEC = 60  # speed of the dialogue box typewriter effect

MAX_ACTIONS = 500        # stop runaway loops that make tons of moves
MAX_LINES_RUN = 20000    # stop runaway loops like `while True: pass`
MAX_EDITOR_LINES = 20
MAX_EDITOR_COLS = 50     # longest line the code box accepts, so text never runs off the panel
CODE_FONT_NAMES, CODE_FONT_SIZE = "consolas,menlo,dejavusansmono,monospace", 16
CODE_TEXT_INDENT = 46    # space the panel keeps left of the code text (margin + line numbers)

COLORS = {
    "bg": (24, 26, 38), "floor": (88, 140, 84), "wall": (60, 60, 78),
    "hero": (80, 160, 255), "coin": (255, 214, 64), "goal": (200, 90, 220),
    "panel": (30, 32, 46), "text": (230, 230, 240), "dim": (120, 124, 150),
    "ok": (110, 220, 140), "err": (255, 110, 110),
}
