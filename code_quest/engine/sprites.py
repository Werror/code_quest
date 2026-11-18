"""Loads the pixel art and scales it up.

The art packs are 16x16 pixel tiles in one big picture (a "tilemap"). We cut it
into tiles and make each one SCALE times bigger. We scale with
pygame.transform.scale (not smoothscale) so the pixels stay crisp, not blurry.
"""
from pathlib import Path

import pygame

from ..config import SCALE, SRC_TILE

ASSETS = Path(__file__).resolve().parents[2] / "assets"
SHEET_COLUMNS, SHEET_ROWS = 12, 11

# Tile numbers inside the Tiny Town pack (count left to right, top to bottom).
GRASS, GRASS_TUFT, GRASS_FLOWERS = 0, 1, 2
PINE_TREE, ROUND_TREE, BUSH = 4, 16, 5
PATH, PATH_DOTS = 25, 41
SIGNPOST, GOLD = 83, 93

# Tile numbers inside the Tiny Dungeon pack.
HERO = 85


def _load_sheet(pack):
    """Return a list with every tile of a pack, already scaled up."""
    path = ASSETS / pack / "Tilemap" / "tilemap_packed.png"
    sheet = pygame.image.load(str(path)).convert_alpha()
    size = SRC_TILE * SCALE
    tiles = []
    for row in range(SHEET_ROWS):
        for col in range(SHEET_COLUMNS):
            rect = (col * SRC_TILE, row * SRC_TILE, SRC_TILE, SRC_TILE)
            tiles.append(pygame.transform.scale(sheet.subsurface(rect), (size, size)))
    return tiles


class Sprites:
    """Call this after pygame.display.set_mode(), because loading needs a window."""

    def __init__(self):
        self._town = _load_sheet("tiny-town")
        self._dungeon = _load_sheet("tiny-dungeon")

    def town(self, number):
        return self._town[number]

    def dungeon(self, number):
        return self._dungeon[number]
