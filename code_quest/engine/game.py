"""The main game loop.

Two modes:
  "edit" - the arrow keys move the text cursor in the code box.
  "play" - the arrow keys walk the hero. F5 starts it, Esc goes back to editing.

When the hero picks up a coin, we call add_coin() on the player's own Wallet
object. It only records events; the loop plays them back one at a time.
"""
import math

import pygame

from ..config import COLORS, EVENT_MS, STEP_MS, TYPE_CHARS_PER_SEC
from ..editor.editor import Editor
from ..levels.level_01 import LEVEL_01
from ..runner.runner import CoinSession
from . import renderer
from .camera import camera_origin
from .scenery import Scenery
from .sprites import Sprites
from .world import World

ARROWS = {
    pygame.K_UP: (0, -1, "up"), pygame.K_DOWN: (0, 1, "down"),
    pygame.K_LEFT: (-1, 0, "left"), pygame.K_RIGHT: (1, 0, "right"),
}


def main(level=LEVEL_01):
    pygame.init()
    screen = pygame.display.set_mode(renderer.window_size())
    pygame.display.set_caption("Code Quest")
    clock = pygame.time.Clock()
    code_font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", 18)
    ui_font = pygame.font.SysFont("arial,helvetica,sans", 18)

    sprites = Sprites()
    world = World(level)
    scenery = Scenery(level)
    editor = Editor(level.starter_code)

    mode = "edit"
    loaded_code = ""              # the code that was running when F5 was pressed
    session = None                # holds the player's Wallet object while playing
    gold = 0                      # the gold shown in the GOLD box
    hero_before = list(world.hero)  # where the hero was one step ago (for smooth walking)
    facing = "down"
    moving, walk_timer, arriving = False, 0, False
    held = []                     # arrow keys currently held down, most recent last
    queue, event_timer = [], 0    # events recorded from the player's code, played back slowly
    level_done = False
    shown_message, typed = "", 0.0  # for the typewriter effect in the dialogue box
    message, message_color = "Write your coin code, then press F5 to start the game!", COLORS["text"]

    def reset_world(text):
        nonlocal session, gold, hero_before, facing, moving, arriving, queue, level_done, message, message_color
        world.reset()
        session = CoinSession(loaded_code) if loaded_code else None   # a brand new Wallet()
        gold, hero_before, facing = 0, list(world.hero), "down"
        moving, arriving, queue, level_done = False, False, [], False
        held.clear()
        message, message_color = text, COLORS["text"]

    def start_game():
        """F5: test the code once, and if it works, start playing with it."""
        nonlocal mode, loaded_code, message, message_color
        trial = CoinSession(editor.text)
        error = trial.setup_error or trial.pick_up_coin().error   # try one pretend coin
        if error:
            message, message_color = error, COLORS["err"]
            return
        loaded_code = editor.text
        mode = "play"
        reset_world("Game started! Walk with the arrow keys. (Esc = edit your code)")

    def handle_arrival():
        """The hero just finished walking onto a new tile."""
        nonlocal queue, event_timer
        if world.pick_up_coin():
            queue.append(("coin",))
            result = session.pick_up_coin()   # only simulates, changes nothing real
            queue.extend(result.events)
            if result.error:
                queue.append(("error", result.error))
            elif result.gold == gold:
                queue.append(("hint", "Hmm, your gold did not change. Did add_coin() change self.gold?"))
        if world.at_goal():
            queue.append(("finish",))
        event_timer = EVENT_MS   # show the first message straight away

    def play_event(ev):
        nonlocal gold, level_done, message, message_color
        kind = ev[0]
        if kind == "coin":
            message, message_color = "You picked up a coin!", COLORS["coin"]
        elif kind == "gold":
            gold = ev[1]
            message, message_color = f"Your wallet now has {gold} gold.", COLORS["coin"]
        elif kind == "say":
            message, message_color = ev[1], COLORS["text"]
        elif kind in ("error", "hint"):
            message, message_color = ev[1], COLORS["err"]
        elif kind == "finish":
            total, got = len(level.coins), world.collected
            if got < total:
                message = f"You found the sign, but {total - got} coin(s) are still out there. Go get them!"
                message_color = COLORS["text"]
            elif gold != got:
                message = (f"You picked up {got} coins but your wallet has {gold}. "
                           "Check your add_coin code (Esc), then press F5!")
                message_color = COLORS["err"]
            else:
                message = f"LEVEL COMPLETE! Your Wallet works: {gold} gold!"
                message_color = COLORS["ok"]
                level_done = True

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                if event.key in held:
                    held.remove(event.key)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5 or (
                    event.key == pygame.K_RETURN and event.mod & pygame.KMOD_CTRL
                ):
                    start_game()
                elif event.key == pygame.K_F6:
                    reset_world("Level reset. Press F5 to start the game!" if mode == "edit"
                                else "Level reset. Walk with the arrow keys!")
                elif mode == "edit":
                    editor.handle_key(event)
                elif event.key == pygame.K_ESCAPE:
                    mode = "edit"
                    held.clear()
                    message, message_color = "Editing. Press F5 to start again with your new code.", COLORS["text"]
                elif event.key in ARROWS:
                    held.append(event.key)

        # walking: finish the current step, or start a new one if an arrow is held
        if moving:
            walk_timer += dt
            if walk_timer >= STEP_MS:
                moving = False
                if arriving:
                    arriving = False
                    handle_arrival()
        if mode == "play" and not moving and not queue and not level_done and held:
            dx, dy, facing = ARROWS[held[-1]]
            hero_before = list(world.hero)
            if world.try_move(dx, dy):
                moving, walk_timer, arriving = True, 0, True
            else:
                held.clear()   # one bump per key press, not one per frame
                message, message_color = "Ouch! A tree is in the way.", COLORS["err"]

        # play back one recorded event at a time
        event_timer += dt
        if queue and event_timer >= EVENT_MS:
            event_timer = 0
            play_event(queue.pop(0))

        # typewriter effect: start again whenever the message changes
        if message != shown_message:
            shown_message, typed = message, 0.0
        typed += dt * TYPE_CHARS_PER_SEC / 1000

        screen.fill(COLORS["bg"])
        # slide from the old tile to the new one, with a little hop on each step
        progress = min(1.0, walk_timer / STEP_MS) if moving else 1.0
        pos = (hero_before[0] + (world.hero[0] - hero_before[0]) * progress,
               hero_before[1] + (world.hero[1] - hero_before[1]) * progress)
        hop = round(abs(math.sin(progress * math.pi)) * 6) if moving else 0
        cam = camera_origin(pos, level.width, level.height)
        renderer.draw_map(screen, level, scenery, world.coins, sprites, cam)
        renderer.draw_hero(screen, sprites, pos, facing, hop, cam)
        renderer.draw_status(screen, ui_font, gold)
        renderer.draw_panel(screen, editor, code_font, ui_font, mode)
        renderer.draw_dialogue(screen, ui_font, message[:int(typed)], message_color)
        pygame.display.flip()

    pygame.quit()
