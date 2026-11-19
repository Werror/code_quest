"""Where the camera looks. The map is bigger than the window, so the camera
follows the hero and stops at the edges of the map. No pygame needed."""
from ..config import TILE, VIEW_H, VIEW_W


def _clamp(value, low, high):
    return max(low, min(value, high))


def camera_origin(hero_pos, level_cols, level_rows):
    """Top-left corner of the view, in pixels, with the hero in the middle."""
    x = hero_pos[0] * TILE + TILE / 2 - VIEW_W / 2
    y = hero_pos[1] * TILE + TILE / 2 - VIEW_H / 2
    max_x = max(0, level_cols * TILE - VIEW_W)
    max_y = max(0, level_rows * TILE - VIEW_H)
    return round(_clamp(x, 0, max_x)), round(_clamp(y, 0, max_y))
