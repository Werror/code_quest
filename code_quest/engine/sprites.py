"""Loads the pixel art and scales it up.

The art packs are 16x16 pixel tiles in one big picture (a "tilemap"). We cut it
into tiles and make each one SCALE times bigger. We scale with
pygame.transform.scale (not smoothscale) so the pixels stay crisp, not blurry.
"""
import colorsys
from pathlib import Path

import pygame

from ..config import SCALE, SRC_TILE
from . import tiles as T

ASSETS = Path(__file__).resolve().parents[2] / "assets"
SHEET_COLUMNS, SHEET_ROWS = 12, 11


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


# Hue (0 to 1 around the color wheel) for each coin color. Normal coins keep the original gold.
COIN_HUES = {"red": 0.0, "sapphire": 0.6}


def _recolor(tile, hue):
    """Copy of a tile with its colorful pixels turned to a new hue (greys and whites stay)."""
    out = tile.copy()
    for x in range(out.get_width()):
        for y in range(out.get_height()):
            r, g, b, a = out.get_at((x, y))
            if a == 0:
                continue
            _, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if saturation < 0.25:
                continue
            r, g, b = colorsys.hsv_to_rgb(hue, min(1.0, saturation * 1.15), value)
            out.set_at((x, y), (round(r * 255), round(g * 255), round(b * 255), a))
    return out


class Sprites:
    """Call this after pygame.display.set_mode(), because loading needs a window."""

    def __init__(self):
        self._town = _load_sheet("tiny-town")
        self._dungeon = _load_sheet("tiny-dungeon")
        gold = self._town[T.GOLD]
        self._coins = {"normal": gold, **{color: _recolor(gold, hue) for color, hue in COIN_HUES.items()}}

    def town(self, number):
        return self._town[number]

    def dungeon(self, number):
        return self._dungeon[number]

    def coin(self, color):
        return self._coins[color]
