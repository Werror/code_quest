"""All the drawing. Nothing in here changes the game, it only paints it."""
import pygame

from ..config import BAR_H, COLORS, PANEL_W, TILE


def window_size(level):
    return level.width * TILE + PANEL_W, level.height * TILE + BAR_H


def draw_map(screen, level, coins):
    for y, row in enumerate(level.rows):
        for x, ch in enumerate(row):
            rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
            pygame.draw.rect(screen, COLORS["wall"] if ch == "#" else COLORS["floor"], rect)
            pygame.draw.rect(screen, COLORS["bg"], rect, 1)
            if ch == "G":
                pygame.draw.rect(screen, COLORS["goal"], rect.inflate(-8, -8), border_radius=6)
    for (x, y) in coins:
        pygame.draw.circle(screen, COLORS["coin"], (x * TILE + TILE // 2, y * TILE + TILE // 2), 9)


def draw_hero(screen, hero):
    hx, hy = hero[0] * TILE, hero[1] * TILE
    pygame.draw.rect(screen, COLORS["hero"], (hx + 7, hy + 7, TILE - 14, TILE - 14), border_radius=8)
    pygame.draw.circle(screen, (255, 255, 255), (hx + 15, hy + 17), 3)
    pygame.draw.circle(screen, (255, 255, 255), (hx + 25, hy + 17), 3)


def draw_panel(screen, level, editor, code_font, ui_font):
    map_w, map_h = level.width * TILE, level.height * TILE
    _, win_h = window_size(level)
    pygame.draw.rect(screen, COLORS["panel"], pygame.Rect(map_w, 0, PANEL_W, win_h))
    screen.blit(ui_font.render("Your code  (F5 = run, F6 = reset)", True, COLORS["dim"]), (map_w + 12, 10))
    blink_on = (pygame.time.get_ticks() // 500) % 2 == 0
    editor.draw(screen, code_font, map_w + 12, 40, blink_on)

    help_lines = ["move_right(3)  move_left()  move_up()  move_down()",
                  "for i in range(4):   if wall_ahead('right'):   say('hi')"]
    for i, t in enumerate(help_lines):
        screen.blit(ui_font.render(t, True, COLORS["dim"]), (map_w + 12, map_h - 50 + i * 22))


def draw_message_bar(screen, level, ui_font, message, color):
    win_w, _ = window_size(level)
    map_h = level.height * TILE
    pygame.draw.rect(screen, (16, 18, 28), (0, map_h, win_w, BAR_H))
    screen.blit(ui_font.render(message, True, color), (14, map_h + 18))
