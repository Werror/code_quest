"""Tests for World: walking, trees and coins (no pygame needed).

They use a tiny map of their own, so changing a real level never breaks them.

    ##### x=0..4
    #P.C#   y=1   hero starts at (1, 1), a coin sits at (3, 1)
    #.#G#   y=2   the goal is at (3, 2); (2, 2) is a tree
    #####
"""
from code_quest.engine.world import World
from code_quest.levels.level import Level

TINY = Level("tiny", "", ["#####", "#P.C#", "#.#G#", "#####"], starter_code="")


def test_hero_starts_on_the_start_tile():
    assert tuple(World(TINY).hero) == (1, 1)


def test_walking_onto_open_ground_works():
    world = World(TINY)
    assert world.try_move(0, 1) is True
    assert world.hero == [1, 2]


def test_trees_and_map_edges_block_the_hero():
    world = World(TINY)
    assert world.try_move(0, -1) is False     # (1, 0) is a tree
    assert world.try_move(-1, 0) is False
    assert world.hero == [1, 1]


def test_a_tree_in_the_middle_of_the_map_blocks_too():
    world = World(TINY)
    world.hero[:] = [1, 2]
    assert world.try_move(1, 0) is False      # (2, 2) is a tree


def test_coin_is_picked_up_only_once():
    world = World(TINY)
    world.hero[:] = [3, 1]
    assert world.pick_up_coin() == "normal"
    assert world.collected == 1
    assert world.pick_up_coin() is None
    assert world.collected == 1


def test_no_coin_on_an_empty_tile():
    assert World(TINY).pick_up_coin() is None


def test_reset_puts_everything_back():
    world = World(TINY)
    world.hero[:] = [3, 1]
    world.pick_up_coin()
    world.reset()
    assert tuple(world.hero) == (1, 1)
    assert world.coins == {(3, 1): "normal"}
    assert world.collected == 0


def test_each_coin_remembers_its_color():
    level = Level("colors", "", ["#####", "#PRS#", "#..G#", "#####"], starter_code="")
    world = World(level)
    world.hero[:] = [2, 1]
    assert world.pick_up_coin() == "red"
    world.hero[:] = [3, 1]
    assert world.pick_up_coin() == "sapphire"


def test_goal_is_detected():
    world = World(TINY)
    assert world.at_goal() is False
    world.hero[:] = [3, 2]
    assert world.at_goal() is True
