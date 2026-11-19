"""The game itself: one Game object that owns the window, the current level and
everything that changes while you play.

Two modes:
  "edit" - the arrow keys move the text cursor in the code box.
  "play" - the arrow keys walk the hero. F5 starts it, Esc goes back to editing.

When the hero picks up a coin, we call add_coin() on the player's own Wallet
object. It only records events; update() plays them back one at a time.
"""
import math

import pygame

from ..config import CODE_FONT_NAMES, CODE_FONT_SIZE, COLORS, EVENT_MS, STEP_MS, TYPE_CHARS_PER_SEC
from ..editor.editor import Editor
from ..levels import LEVELS
from ..runner.review import CoinLog, review_code
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


class Game:
    def __init__(self, levels=LEVELS):
        pygame.init()
        self.screen = pygame.display.set_mode(renderer.window_size())
        self.clock = pygame.time.Clock()
        self.code_font = pygame.font.SysFont(CODE_FONT_NAMES, CODE_FONT_SIZE)
        self.ui_font = pygame.font.SysFont("arial,helvetica,sans", 18)
        self.sprites = Sprites()
        self.levels = levels
        self.running = True
        self.load_level(0)

    # ------------------------------------------------------------------ levels
    def load_level(self, index):
        self.level_index = index
        self.level = self.levels[index]
        pygame.display.set_caption(f"Code Quest - {self.level.name}")
        self.world = World(self.level)
        self.scenery = Scenery(self.level)
        self.editor = Editor(self.level.starter_code)
        self.mode = "edit"
        self.loaded_code = ""        # the code that was running when F5 was pressed
        self.reset_world(self.level.intro)

    def has_next_level(self):
        return self.level_index + 1 < len(self.levels)

    def reset_world(self, text):
        """Put the hero, coins and gold back to the start (the player's code stays)."""
        self.world.reset()
        # a brand new Wallet() for the player's code
        self.session = (CoinSession(self.loaded_code, self.level.passes_color)
                        if self.loaded_code else None)
        self.gold = 0                       # the number in the GOLD box
        self.hero_before = list(self.world.hero)   # where the hero was one step ago (smooth walking)
        self.facing = "down"
        self.moving, self.walk_timer, self.arriving = False, 0, False
        self.held = []                      # arrow keys currently held down, most recent last
        self.queue, self.event_timer = [], 0   # events recorded from the player's code
        self.coin_log = []                  # what the Wallet did for each coin (for the sign)
        self.level_done = False
        self.pages, self.page_index, self.reading, self.review_passed = [], 0, False, False
        self.shown_message, self.typed = "", 0.0   # for the typewriter effect
        self.say(text)

    def say(self, text, color=None):
        self.message = text
        self.message_color = color or COLORS["text"]

    # ---------------------------------------------------------------- starting
    def start_game(self):
        """F5: try the code with a pretend coin of every color, and if it works, start playing."""
        trial = CoinSession(self.editor.text, self.level.passes_color)
        error = trial.setup_error
        if not error:
            for color in self.level.coin_values:
                error = trial.pick_up_coin(color).error
                if error:
                    break
        if error:
            self.say(error, COLORS["err"])
            return
        self.loaded_code = self.editor.text
        self.mode = "play"
        self.reset_world("Game started! Walk with the arrow keys. (Esc = edit your code)")

    # ------------------------------------------------------------ game events
    def handle_arrival(self):
        """The hero just finished walking onto a new tile."""
        color = self.world.pick_up_coin()
        if color:
            self.queue.append(("coin", color))
            result = self.session.pick_up_coin(color)   # only simulates, changes nothing real
            self.coin_log.append(CoinLog(color, self.level.coin_values[color],
                                         result.gold - self.gold, result.error))
            self.queue.extend(result.events)
            if result.error:
                self.queue.append(("error", result.error))
            elif result.gold == self.gold:
                self.queue.append(("hint", "Hmm, your gold did not change. Did add_coin() change self.gold?"))
        if self.world.at_goal():
            self.queue.append(("finish",))
        self.event_timer = EVENT_MS   # show the first message straight away

    def play_event(self, ev):
        """Show one thing the player's code (or the game) recorded."""
        kind = ev[0]
        if kind == "coin":
            self.say(f"You picked up a {ev[1]} coin!", COLORS["coin"])
        elif kind == "gold":
            self.gold = ev[1]
            self.say(f"Your wallet now has {self.gold} gold.", COLORS["coin"])
        elif kind == "say":
            self.say(ev[1])
        elif kind in ("error", "hint"):
            self.say(ev[1], COLORS["err"])
        elif kind == "finish":
            self.read_the_sign()

    def read_the_sign(self):
        review = review_code(self.level, self.loaded_code, self.coin_log,
                             self.world.collected, self.has_next_level())
        self.pages, self.page_index, self.reading = review.pages, 0, True
        self.review_passed = review.passed
        self.show_page()

    def show_page(self):
        good = self.review_passed and self.page_index == 0
        self.say(self.pages[self.page_index], COLORS["ok"] if good else COLORS["text"])

    def advance_page(self):
        if self.typed < len(self.message):      # first press: show the whole page at once
            self.typed = len(self.message)
        elif self.page_index + 1 < len(self.pages):
            self.page_index += 1
            self.show_page()
        else:
            self.reading = False
            self.level_done = self.review_passed

    # ------------------------------------------------------------------- input
    def handle_keydown(self, event):
        if event.key == pygame.K_F5 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_CTRL):
            self.start_game()
        elif event.key == pygame.K_F6:
            self.reset_world("Level reset. Press F5 to start the game!" if self.mode == "edit"
                             else "Level reset. Walk with the arrow keys!")
        elif self.mode == "edit":
            self.editor.handle_key(event)
        elif event.key == pygame.K_ESCAPE:
            self.mode = "edit"
            self.held.clear()
            self.reading = False
            self.say("Editing. Press F5 to start again with your new code.")
        elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and self.reading:
            self.advance_page()
        elif event.key == pygame.K_n and self.level_done and self.has_next_level():
            self.load_level(self.level_index + 1)
        elif event.key in ARROWS:
            self.held.append(event.key)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYUP:
            if event.key in self.held:
                self.held.remove(event.key)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)

    # ------------------------------------------------------------------ update
    def update(self, dt):
        # walking: finish the current step, or start a new one if an arrow is held
        if self.moving:
            self.walk_timer += dt
            if self.walk_timer >= STEP_MS:
                self.moving = False
                if self.arriving:
                    self.arriving = False
                    self.handle_arrival()
        can_walk = (self.mode == "play" and not self.moving and not self.queue
                    and not self.reading and not self.level_done)
        if can_walk and self.held:
            dx, dy, self.facing = ARROWS[self.held[-1]]
            self.hero_before = list(self.world.hero)
            if self.world.try_move(dx, dy):
                self.moving, self.walk_timer, self.arriving = True, 0, True
            else:
                self.held.clear()   # one bump per key press, not one per frame
                self.say("Ouch! A tree is in the way.", COLORS["err"])

        # play back one recorded event at a time
        self.event_timer += dt
        if self.queue and self.event_timer >= EVENT_MS:
            self.event_timer = 0
            self.play_event(self.queue.pop(0))

        # typewriter effect: start again whenever the message changes
        if self.message != self.shown_message:
            self.shown_message, self.typed = self.message, 0.0
        self.typed += dt * TYPE_CHARS_PER_SEC / 1000

    # -------------------------------------------------------------------- draw
    def draw(self):
        self.screen.fill(COLORS["bg"])
        # slide from the old tile to the new one, with a little hop on each step
        progress = min(1.0, self.walk_timer / STEP_MS) if self.moving else 1.0
        hero, before = self.world.hero, self.hero_before
        pos = (before[0] + (hero[0] - before[0]) * progress,
               before[1] + (hero[1] - before[1]) * progress)
        hop = round(abs(math.sin(progress * math.pi)) * 6) if self.moving else 0
        cam = camera_origin(pos, self.level.width, self.level.height)
        renderer.draw_map(self.screen, self.level, self.scenery, self.world.coins, self.sprites, cam)
        renderer.draw_hero(self.screen, self.sprites, pos, self.facing, hop, cam)
        renderer.draw_status(self.screen, self.ui_font, self.gold)
        renderer.draw_panel(self.screen, self.editor, self.code_font, self.ui_font, self.mode)
        page_done = self.reading and self.typed >= len(self.message)
        renderer.draw_dialogue(self.screen, self.ui_font, self.message[:int(self.typed)],
                               self.message_color, more=page_done)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.quit()


def main(levels=LEVELS):
    Game(levels).run()
