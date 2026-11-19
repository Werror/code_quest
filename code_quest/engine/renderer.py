"""All the drawing. Nothing in here changes the game, it only paints it."""
import pygame

from ..config import BAR_H, COLORS, PANEL_W, TILE
from . import sprites as S


def window_size(level):
    return level.width * TILE + PANEL_W, level.height * TILE + BAR_H


def _pick(x, y, choices):
    """Pick a variant by position, so the scenery looks varied but never flickers."""
    return choices[(x * 31 + y * 17) % len(choices)]


def draw_map(screen, level, coins, sprites):
    for y, row in enumerate(level.rows):
        for x, ch in enumerate(row):
            pos = (x * TILE, y * TILE)
            if ch == "#":
                screen.blit(sprites.town(_pick(x, y, [S.GRASS, S.GRASS, S.GRASS_TUFT, S.GRASS_FLOWERS])), pos)
                screen.blit(sprites.town(_pick(x, y, [S.ROUND_TREE, S.PINE_TREE, S.ROUND_TREE, S.BUSH])), pos)
            else:
                screen.blit(sprites.town(_pick(x, y, [S.PATH, S.PATH, S.PATH, S.PATH_DOTS])), pos)
                if ch == "G":
                    screen.blit(sprites.town(S.SIGNPOST), pos)
    for (x, y) in coins:
        screen.blit(sprites.town(S.GOLD), (x * TILE, y * TILE))


def draw_hero(screen, sprites, pos, facing, hop):
    """pos is the hero's tile (can be between tiles while walking)."""
    image = sprites.dungeon(S.HERO)
    if facing == "left":
        image = pygame.transform.flip(image, True, False)
    screen.blit(image, (round(pos[0] * TILE), round(pos[1] * TILE) - hop))


def draw_status(screen, font, wallet):
    """The little GOLD box in the top-left corner, like an old RPG."""
    box = pygame.Rect(8, 8, 150, 38)
    pygame.draw.rect(screen, (14, 22, 90), box, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box, 3, border_radius=6)
    screen.blit(font.render(f"GOLD: {wallet}", True, COLORS["coin"]), (box.x + 14, box.y + 8))


def draw_panel(screen, level, editor, code_font, ui_font, mode):
    map_w, map_h = level.width * TILE, level.height * TILE
    _, win_h = window_size(level)
    panel = pygame.Rect(map_w, 0, PANEL_W, win_h)
    pygame.draw.rect(screen, COLORS["panel"], panel)
    editing = mode == "edit"
    if editing:
        pygame.draw.rect(screen, COLORS["ok"], panel, 3)   # green frame = you are typing here
    title = "Coin code: type here, F5 = start" if editing else "Playing! Esc = edit your code"
    screen.blit(ui_font.render(title, True, COLORS["ok"] if editing else COLORS["dim"]), (map_w + 12, 10))
    blink_on = editing and (pygame.time.get_ticks() // 500) % 2 == 0
    editor.draw(screen, code_font, map_w + 12, 40, blink_on)

    help_lines = ["Use the variable: wallet",
                  "say('hi') shows a message",
                  "Arrows = walk   F5 = start   F6 = reset"]
    for i, t in enumerate(help_lines):
        screen.blit(ui_font.render(t, True, COLORS["dim"]), (map_w + 12, map_h - 72 + i * 22))


def _wrap(text, font, max_width):
    """Split text into lines that fit inside max_width pixels."""
    lines, line = [], ""
    for word in text.split(" "):
        trial = f"{line} {word}".strip()
        if line and font.size(trial)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    lines.append(line)
    return lines


def draw_dialogue(screen, level, font, text, color):
    """A Dragon Quest style text window: navy box, white double border."""
    win_w, _ = window_size(level)
    map_h = level.height * TILE
    pygame.draw.rect(screen, COLORS["bg"], (0, map_h, win_w, BAR_H))   # clear behind the box
    box = pygame.Rect(8, map_h + 8, win_w - 16, BAR_H - 16)
    pygame.draw.rect(screen, (14, 22, 90), box, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box, 3, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box.inflate(-10, -10), 1, border_radius=4)
    line_h = font.get_linesize()
    for i, line in enumerate(_wrap(text, font, box.width - 40)[:3]):
        screen.blit(font.render(line, True, color), (box.x + 20, box.y + 12 + i * line_h))
