"""All the drawing. Nothing in here changes the game, it only paints it."""
import pygame

from ..config import BAR_H, COLORS, PANEL_W, TILE, VIEW_H, VIEW_W
from . import tiles as T


def window_size():
    return VIEW_W + PANEL_W, VIEW_H + BAR_H


def draw_map(screen, level, scenery, coins, sprites, cam):
    """Draw the part of the map the camera can see. cam is the view's top-left in pixels."""
    screen.set_clip(pygame.Rect(0, 0, VIEW_W, VIEW_H))   # never paint over the code panel
    first_x, first_y = cam[0] // TILE, cam[1] // TILE
    for y in range(first_y, min(level.height, first_y + VIEW_H // TILE + 2)):
        for x in range(first_x, min(level.width, first_x + VIEW_W // TILE + 2)):
            pos = (x * TILE - cam[0], y * TILE - cam[1])
            screen.blit(sprites.town(scenery.ground[(x, y)]), pos)
            if (x, y) in scenery.objects:
                screen.blit(sprites.town(scenery.objects[(x, y)]), pos)
    for (x, y), color in coins.items():
        screen.blit(sprites.coin(color), (x * TILE - cam[0], y * TILE - cam[1]))
    screen.set_clip(None)


def draw_hero(screen, sprites, pos, facing, hop, cam):
    """pos is the hero's tile (can be between tiles while walking)."""
    image = sprites.dungeon(T.HERO)
    if facing == "left":
        image = pygame.transform.flip(image, True, False)
    screen.blit(image, (round(pos[0] * TILE) - cam[0], round(pos[1] * TILE) - cam[1] - hop))


def draw_status(screen, font, gold):
    """The little GOLD box in the top-left corner, like an old RPG."""
    box = pygame.Rect(8, 8, 150, 38)
    pygame.draw.rect(screen, (14, 22, 90), box, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box, 3, border_radius=6)
    screen.blit(font.render(f"GOLD: {gold}", True, COLORS["coin"]), (box.x + 14, box.y + 8))


def draw_panel(screen, editor, code_font, ui_font, mode):
    panel = pygame.Rect(VIEW_W, 0, PANEL_W, VIEW_H + BAR_H)
    pygame.draw.rect(screen, COLORS["panel"], panel)
    editing = mode == "edit"
    if editing:
        pygame.draw.rect(screen, COLORS["ok"], panel, 3)   # green frame = you are typing here
    title = "Coin code: type here, F5 = start" if editing else "Playing! Esc = edit your code"
    screen.blit(ui_font.render(title, True, COLORS["ok"] if editing else COLORS["dim"]), (VIEW_W + 12, 10))
    blink_on = editing and (pygame.time.get_ticks() // 500) % 2 == 0
    editor.draw(screen, code_font, VIEW_W + 12, 40, blink_on)

    help_lines = ["Fill in add_coin() in your Wallet",
                  "say('hi') shows a message",
                  "Arrows = walk   F5 = start   F6 = reset"]
    for i, t in enumerate(help_lines):
        screen.blit(ui_font.render(t, True, COLORS["dim"]), (VIEW_W + 12, VIEW_H - 72 + i * 22))


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


def draw_dialogue(screen, font, text, color, more=False):
    """A Dragon Quest style text window: navy box, white double border."""
    win_w, _ = window_size()
    pygame.draw.rect(screen, COLORS["bg"], (0, VIEW_H, win_w, BAR_H))   # clear behind the box
    box = pygame.Rect(8, VIEW_H + 8, win_w - 16, BAR_H - 16)
    pygame.draw.rect(screen, (14, 22, 90), box, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box, 3, border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), box.inflate(-10, -10), 1, border_radius=4)
    line_h = font.get_linesize()
    for i, line in enumerate(_wrap(text, font, box.width - 40)[:3]):
        screen.blit(font.render(line, True, color), (box.x + 20, box.y + 12 + i * line_h))
    if more:   # a little arrow: "press Space for the next page"
        tip = pygame.Rect(box.right - 40, box.bottom - 26, 20, 12)
        pygame.draw.polygon(screen, (255, 255, 255), [tip.topleft, tip.topright, (tip.centerx, tip.bottom)])
