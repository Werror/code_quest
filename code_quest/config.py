"""Settings shared by the whole game: sizes, limits and colors."""

TILE = 40
PANEL_W, BAR_H = 440, 60

MAX_ACTIONS = 500        # stop runaway loops that make tons of moves
MAX_LINES_RUN = 20000    # stop runaway loops like `while True: pass`
MAX_EDITOR_LINES = 18

COLORS = {
    "bg": (24, 26, 38), "floor": (88, 140, 84), "wall": (60, 60, 78),
    "hero": (80, 160, 255), "coin": (255, 214, 64), "goal": (200, 90, 220),
    "panel": (30, 32, 46), "text": (230, 230, 240), "dim": (120, 124, 150),
    "ok": (110, 220, 140), "err": (255, 110, 110),
}
