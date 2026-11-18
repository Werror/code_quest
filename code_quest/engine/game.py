"""The main game loop: read keys, play back recorded events, draw."""
import math

import pygame

from ..config import COLORS, STEP_MS, TYPE_CHARS_PER_SEC
from ..editor.editor import Editor
from ..levels.level_01 import LEVEL_01
from ..runner.runner import run_player_code
from . import renderer
from .sprites import Sprites


def main(level=LEVEL_01):
    pygame.init()
    screen = pygame.display.set_mode(renderer.window_size(level))
    pygame.display.set_caption("Code Quest")
    clock = pygame.time.Clock()
    code_font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", 18)
    ui_font = pygame.font.SysFont("arial,helvetica,sans", 18)

    sprites = Sprites()
    editor = Editor(level.starter_code)
    hero = list(level.start)
    hero_before = list(level.start)   # where the hero was one step ago (for smooth walking)
    facing = "down"
    coins = set(level.coins)
    queue, step_timer = [], 0
    shown_message, typed = "", 0.0   # for the typewriter effect in the dialogue box
    message, message_color = "Write code, then press F5 to run it!", COLORS["text"]
    collected = 0

    def reset():
        nonlocal hero, hero_before, facing, coins, queue, collected, message, message_color
        hero, coins, queue, collected = list(level.start), set(level.coins), [], 0
        hero_before, facing = list(hero), "down"
        message, message_color = "Level reset. Press F5 to run your code!", COLORS["text"]

    def run():
        nonlocal hero, hero_before, facing, coins, queue, collected, message, message_color
        hero, coins, collected = list(level.start), set(level.coins), 0
        hero_before, facing = list(hero), "down"
        res = run_player_code(editor.text, level)
        queue = list(res.events)
        if res.error:
            queue.append(("error", res.error))
        else:
            queue.append(("finish",))
        message, message_color = "Running...", COLORS["text"]

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5 or (
                    event.key == pygame.K_RETURN and event.mod & pygame.KMOD_CTRL
                ):
                    run()
                elif event.key == pygame.K_F6:
                    reset()
                else:
                    editor.handle_key(event)

        # play back one event every STEP_MS
        step_timer += dt
        if queue and step_timer >= STEP_MS:
            step_timer = 0
            ev = queue.pop(0)
            kind = ev[0]
            hero_before = list(hero)  # every event starts a new step from where the hero is now
            if kind == "move":
                hero[:] = [ev[1], ev[2]]
                dx, dy = hero[0] - hero_before[0], hero[1] - hero_before[1]
                facing = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}[(dx, dy)]
            elif kind == "bump":
                message, message_color = "Ouch! You bumped into a wall.", COLORS["err"]
            elif kind == "coin":
                coins.discard((ev[1], ev[2]))
                collected += 1
                message, message_color = f"Coin! ({collected}/{len(level.coins)})", COLORS["coin"]
            elif kind == "say":
                message, message_color = ev[1], COLORS["text"]
            elif kind == "error":
                message, message_color = ev[1], COLORS["err"]
            elif kind == "finish":
                if tuple(hero) == level.goal:
                    message = f"LEVEL COMPLETE! You collected {collected}/{len(level.coins)} coins!"
                    message_color = COLORS["ok"]
                else:
                    message = "Code finished, but you're not at the sign yet. Edit and try again!"
                    message_color = COLORS["text"]

        # typewriter effect: start again whenever the message changes
        if message != shown_message:
            shown_message, typed = message, 0.0
        typed += dt * TYPE_CHARS_PER_SEC / 1000

        screen.fill(COLORS["bg"])
        renderer.draw_map(screen, level, coins, sprites)
        # slide from the old tile to the new one, with a little hop on each step
        progress = min(1.0, step_timer / STEP_MS)
        pos = (hero_before[0] + (hero[0] - hero_before[0]) * progress,
               hero_before[1] + (hero[1] - hero_before[1]) * progress)
        moving = hero != hero_before and progress < 1.0
        hop = round(abs(math.sin(progress * math.pi)) * 6) if moving else 0
        renderer.draw_hero(screen, sprites, pos, facing, hop)
        renderer.draw_panel(screen, level, editor, code_font, ui_font)
        renderer.draw_dialogue(screen, level, ui_font, message[:int(typed)], message_color)
        pygame.display.flip()

    pygame.quit()
