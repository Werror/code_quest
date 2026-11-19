"""The camera follows the hero but never shows past the edge of the map."""
from code_quest.config import TILE, VIEW_COLS, VIEW_ROWS
from code_quest.engine.camera import camera_origin


def test_camera_stops_at_the_top_left_corner():
    assert camera_origin((0, 0), 32, 23) == (0, 0)
    assert camera_origin((2, 2), 32, 23) == (0, 0)


def test_camera_centers_on_the_hero_in_the_middle_of_the_map():
    x, y = camera_origin((16, 11), 32, 23)
    assert x == 16 * TILE + TILE // 2 - VIEW_COLS * TILE // 2
    assert y == 11 * TILE + TILE // 2 - VIEW_ROWS * TILE // 2


def test_camera_stops_at_the_bottom_right_corner():
    assert camera_origin((31, 22), 32, 23) == ((32 - VIEW_COLS) * TILE, (23 - VIEW_ROWS) * TILE)


def test_a_map_smaller_than_the_window_never_scrolls():
    assert camera_origin((5, 5), 10, 8) == (0, 0)
