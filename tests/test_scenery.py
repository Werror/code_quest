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


def assert_no_half_trees(scenery):
    for (x, y), tile in scenery.objects.items():
        if tile in TOPS:
            assert scenery.objects.get((x, y + 1)) == TOPS[tile], f"tree top at {(x, y)} has no matching bottom"
        if tile in BOTTOMS:
            top = scenery.objects.get((x, y - 1))
            assert top in TOPS and TOPS[top] == tile, f"tree bottom at {(x, y)} has no top"


def test_tall_trees_are_always_complete_two_tile_trees():
    assert_no_half_trees(Scenery(LEVEL_01))


def test_the_forest_has_both_kinds_but_more_single_tile_trees():
    tiles = list(Scenery(LEVEL_01).objects.values())
    tall_trees = sum(t in TOPS for t in tiles)
    single_trees = sum(t in SMALL for t in tiles)
    assert tall_trees >= 10
    assert single_trees > tall_trees


def test_the_goal_gets_a_signpost_on_a_path():
    scenery = Scenery(LEVEL_01)
    assert scenery.objects[LEVEL_01.goal] == T.SIGNPOST
    assert scenery.ground[LEVEL_01.goal] in (T.PATH, T.PATH_DOTS)


def test_a_column_of_five_trees_never_leaves_half_a_tall_tree():
    from code_quest.levels.level import Level
    level = Level("t", "", ["###", "#P#", "#G#", "#C#", "###"], "")   # column 0 is five walls tall
    scenery = Scenery(level)
    assert all((0, y) in scenery.objects for y in range(5))
    assert_no_half_trees(scenery)
