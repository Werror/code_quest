"""Which tile is which in the art packs (count left to right, top to bottom).

Plain numbers only, so this file needs no pygame.
"""

# --- Tiny Town ---
GRASS, GRASS_TUFT, GRASS_FLOWERS = 0, 1, 2
PATH, PATH_DOTS = 25, 41
# Tall trees are two tiles stacked on top of each other: a top and a bottom (with the trunk).
TALL_ORANGE_TOP, TALL_GREEN_TOP = 3, 4
TALL_ORANGE_BOTTOM, TALL_GREEN_BOTTOM = 15, 16
BUSH = 5
SMALL_ORANGE_TREE, SMALL_GREEN_TREE = 27, 28   # fill gaps where there is no room for a tall tree
SIGNPOST, GOLD = 83, 93

# --- Tiny Dungeon ---
HERO = 85
