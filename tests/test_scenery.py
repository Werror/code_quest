"""Scenery decides which picture goes on each tile (no pygame needed)."""
from code_quest.engine import tiles as T
from code_quest.engine.scenery import Scenery
from code_quest.levels.level_01 import LEVEL_01

TOPS = {T.TALL_GREEN_TOP: T.TALL_GREEN_BOTTOM, T.TALL_ORANGE_TOP: T.TALL_ORANGE_BOTTOM}
BOTTOMS = set(TOPS.values())
SMALL = {T.SMALL_GREEN_TREE, T.SMALL_ORANGE_TREE, T.BUSH}


def all_tiles(level):
    return [(x, y) for y in range(level.height) for x in range(level.width)]


def test_every_tile_has_ground():
    scenery = Scenery(LEVEL_01)
    assert all(pos in scenery.ground for pos in all_tiles(LEVEL_01))


def test_every_wall_tile_has_a_tree_and_no_open_tile_does():
    scenery = Scenery(LEVEL_01)
    for x, y in all_tiles(LEVEL_01):
        is_tree = (x, y) in scenery.objects and scenery.objects[(x, y)] != T.SIGNPOST
        assert is_tree == LEVEL_01.is_wall(x, y), (x, y)


def test_tall_trees_are_always_complete_two_tile_trees():
    scenery = Scenery(LEVEL_01)
    for (x, y), tile in scenery.objects.items():
        if tile in TOPS:
            assert scenery.objects.get((x, y + 1)) == TOPS[tile], f"tree top at {(x, y)} has no matching bottom"
        if tile in BOTTOMS:
            top = scenery.objects.get((x, y - 1))
            assert top in TOPS and TOPS[top] == tile, f"tree bottom at {(x, y)} has no top"


def test_there_are_tall_trees_and_a_few_small_fillers():
    tiles = list(Scenery(LEVEL_01).objects.values())
    assert sum(t in TOPS for t in tiles) > 50
    assert any(t in SMALL for t in tiles)


def test_the_goal_gets_a_signpost_on_a_path():
    scenery = Scenery(LEVEL_01)
    assert scenery.objects[LEVEL_01.goal] == T.SIGNPOST
    assert scenery.ground[LEVEL_01.goal] in (T.PATH, T.PATH_DOTS)


def test_a_single_wall_tile_gets_a_small_tree_not_half_a_tall_one():
    from code_quest.levels.level import Level
    level = Level("t", ["###", "#P#", "#G#", "#C#", "###"], "")   # column x=1 has 1 open tile... plus 2 walls around
    scenery = Scenery(level)
    # Column 0 is 5 walls tall: two tall trees (rows 0-1, 2-3) and one small tree (row 4).
    assert scenery.objects[(0, 0)] in TOPS and scenery.objects[(0, 3)] in BOTTOMS
    assert scenery.objects[(0, 4)] in SMALL
