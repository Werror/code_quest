"""The main game loop: read keys, play back recorded events, draw."""
import pygame

from ..config import COLORS
from ..editor.editor import Editor
from ..levels.level_01 import LEVEL_01
from ..runner.runner import run_player_code
from . import renderer


def main(level=LEVEL_01):
    pygame.init()
    screen = pygame.display.set_mode(renderer.window_size(level))
    pygame.display.set_caption("Code Quest")
    clock = pygame.time.Clock()
    code_font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", 18)
    ui_font = pygame.font.SysFont("arial,helvetica,sans", 18)

    editor = Editor(level.starter_code)
    hero = list(level.start)
    coins = set(level.coins)
    queue, step_timer = [], 0
    message, message_color = "Write code, then press F5 to run it!", COLORS["text"]
    collected = 0

    def reset():
        nonlocal hero, coins, queue, collected, message, message_color
        hero, coins, queue, collected = list(level.start), set(level.coins), [], 0
        message, message_color = "Level reset. Press F5 to run your code!", COLORS["text"]

    def run():
        nonlocal hero, coins, queue, collected, message, message_color
        hero, coins, collected = list(level.start), set(level.coins), 0
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

        # play back one event every 180 ms
        step_timer += dt
        if queue and step_timer >= 180:
            step_timer = 0
            ev = queue.pop(0)
            kind = ev[0]
            if kind == "move":
                hero[:] = [ev[1], ev[2]]
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
                    message = "Code finished, but you're not at the G yet. Edit and try again!"
                    message_color = COLORS["text"]

        screen.fill(COLORS["bg"])
        renderer.draw_map(screen, level, coins)
        renderer.draw_hero(screen, hero)
        renderer.draw_panel(screen, level, editor, code_font, ui_font)
        renderer.draw_message_bar(screen, level, ui_font, message, message_color)
        pygame.display.flip()

    pygame.quit()
