"""Tests for World: walking, trees and coins (no pygame needed)."""
from code_quest.engine.world import World
from code_quest.levels.level_01 import LEVEL_01


def test_hero_starts_on_the_start_tile():
    assert tuple(World(LEVEL_01).hero) == LEVEL_01.start


def test_walking_onto_open_ground_works():
    world = World(LEVEL_01)
    assert world.try_move(0, 1) is True       # (1, 2) is path
    assert world.hero == [1, 2]


def test_trees_and_map_edges_block_the_hero():
    world = World(LEVEL_01)
    assert world.try_move(0, -1) is False     # (1, 0) is a tree
    assert world.try_move(-1, 0) is False
    assert world.hero == [1, 1]


def test_coin_is_picked_up_only_once():
    world = World(LEVEL_01)
    world.hero[:] = [3, 3]                    # a coin sits at (3, 3)
    assert world.pick_up_coin() is True
    assert world.collected == 1
    assert world.pick_up_coin() is False
    assert world.collected == 1


def test_no_coin_on_an_empty_tile():
    assert World(LEVEL_01).pick_up_coin() is False


def test_reset_puts_everything_back():
    world = World(LEVEL_01)
    world.hero[:] = [3, 3]
    world.pick_up_coin()
    world.reset()
    assert tuple(world.hero) == LEVEL_01.start
    assert world.coins == set(LEVEL_01.coins)
    assert world.collected == 0


def test_goal_is_detected():
    world = World(LEVEL_01)
    assert world.at_goal() is False
    world.hero[:] = list(LEVEL_01.goal)
    assert world.at_goal() is True
