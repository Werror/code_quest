"""
Code Quest - a tiny 2D RPG where the player writes Python to move the hero.

Controls
  Type in the code box on the right.
  F5 or Ctrl+Enter : run your code
  F6               : reset the level

Install:  pip install pygame
Run:      python code_quest.py
"""
import sys
import pygame

TILE = 40
MAP = [
    "################",
    "#P.....#.......#",
    "#.####.#.#####.#",
    "#.#C...#.#...#.#",
    "#.#.####.#.C.#.#",
    "#.#......#...#.#",
    "#.########.###.#",
    "#..........#...#",
    "####.#####.#.###",
    "#C...#...#.#...#",
    "#.##...#...#.G.#",
    "################",
]
ROWS, COLS = len(MAP), len(MAP[0])
MAP_W, MAP_H = COLS * TILE, ROWS * TILE
PANEL_W, BAR_H = 440, 60
WIN_W, WIN_H = MAP_W + PANEL_W, MAP_H + BAR_H

MAX_ACTIONS = 500        # stop runaway loops that make tons of moves
MAX_LINES_RUN = 20000    # stop runaway loops like `while True: pass`
MAX_EDITOR_LINES = 18

STARTER_CODE = "# Move the hero to the G!\nmove_down(2)\n"

COLORS = {
    "bg": (24, 26, 38), "floor": (88, 140, 84), "wall": (60, 60, 78),
    "hero": (80, 160, 255), "coin": (255, 214, 64), "goal": (200, 90, 220),
    "panel": (30, 32, 46), "text": (230, 230, 240), "dim": (120, 124, 150),
    "ok": (110, 220, 140), "err": (255, 110, 110),
}


def find_tiles(ch):
    return [(x, y) for y, row in enumerate(MAP) for x, c in enumerate(row) if c == ch]


START = find_tiles("P")[0]
GOAL = find_tiles("G")[0]
COINS = set(find_tiles("C"))


def is_wall(x, y):
    return not (0 <= x < COLS and 0 <= y < ROWS) or MAP[y][x] == "#"


# ---------------------------------------------------------------------------
# Running the player's code
# ---------------------------------------------------------------------------
class RunResult:
    def __init__(self):
        self.events = []     # ("move", x, y) / ("bump", x, y) / ("coin", x, y) / ("say", text)
        self.error = None    # friendly error string or None


def run_player_code(source):
    """Run the kid's code against a *simulated* hero and record what happened.
    The game then plays those events back as an animation.

    NOTE: restricted builtins stop accidents, not determined hackers.
    Fine for a classroom/home game; use a subprocess sandbox if you ever
    run other people's code on a server.
    """
    result = RunResult()
    state = {"x": START[0], "y": START[1], "coins": set(COINS)}
    ev = result.events

    def check_limit():
        if len(ev) > MAX_ACTIONS:
            raise RuntimeError("Too many actions! Is a loop never ending?")

    def move(dx, dy, n=1):
        for _ in range(int(n)):
            nx, ny = state["x"] + dx, state["y"] + dy
            if is_wall(nx, ny):
                ev.append(("bump", state["x"], state["y"]))
                check_limit()
                return
            state["x"], state["y"] = nx, ny
            ev.append(("move", nx, ny))
            if (nx, ny) in state["coins"]:
                state["coins"].remove((nx, ny))
                ev.append(("coin", nx, ny))
            check_limit()

    def wall_ahead(direction):
        d = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        if direction not in d:
            raise ValueError("wall_ahead needs 'up', 'down', 'left' or 'right'")
        dx, dy = d[direction]
        return is_wall(state["x"] + dx, state["y"] + dy)

    def say(*things):
        ev.append(("say", " ".join(str(t) for t in things)))
        check_limit()

    api = {
        "move_up": lambda n=1: move(0, -1, n),
        "move_down": lambda n=1: move(0, 1, n),
        "move_left": lambda n=1: move(-1, 0, n),
        "move_right": lambda n=1: move(1, 0, n),
        "wall_ahead": wall_ahead,
        "say": say,
        "print": say,
    }
    safe_builtins = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n)
                     for n in ("range", "len", "int", "str", "min", "max", "abs", "bool", "list")}
    env = {"__builtins__": safe_builtins, **api}

    count = 0

    def tracer(frame, event, arg):
        nonlocal count
        if frame.f_code.co_filename != "<hero>":
            return None
        if event == "line":
            count += 1
            if count > MAX_LINES_RUN:
                raise TimeoutError("Your code ran for too long. Is a loop never ending?")
        return tracer

    try:
        code = compile(source, "<hero>", "exec")
        sys.settrace(tracer)
        try:
            exec(code, env)
        finally:
            sys.settrace(None)
    except SyntaxError as e:
        result.error = f"Typo on line {e.lineno}: {e.msg}"
    except Exception as e:  # noqa: BLE001 - we want to show every error nicely
        tb, line = e.__traceback__, None
        while tb:
            if tb.tb_frame.f_code.co_filename == "<hero>":
                line = tb.tb_lineno
            tb = tb.tb_next
        where = f" on line {line}" if line else ""
        result.error = f"{type(e).__name__}{where}: {e}"
    return result


# ---------------------------------------------------------------------------
# Code editor widget
# ---------------------------------------------------------------------------
class Editor:
    def __init__(self, text):
        self.lines = text.split("\n")
        self.row, self.col = len(self.lines) - 1, 0

    @property
    def text(self):
        return "\n".join(self.lines)

    def handle_key(self, event):
        L, r, c = self.lines, self.row, self.col
        if event.key == pygame.K_RETURN:
            if len(L) >= MAX_EDITOR_LINES:
                return
            indent = len(L[r]) - len(L[r].lstrip(" "))
            if L[r][:c].rstrip().endswith(":"):
                indent += 4
            rest = L[r][c:]
            L[r] = L[r][:c]
            L.insert(r + 1, " " * indent + rest.lstrip(" ") if rest.strip() else " " * indent)
            self.row, self.col = r + 1, indent
        elif event.key == pygame.K_BACKSPACE:
            if c > 0:
                # delete a whole 4-space indent at once if we're in leading spaces
                n = 4 if L[r][:c].strip() == "" and c >= 4 else 1
                L[r] = L[r][:c - n] + L[r][c:]
                self.col -= n
            elif r > 0:
                self.col = len(L[r - 1])
                L[r - 1] += L[r]
                del L[r]
                self.row -= 1
        elif event.key == pygame.K_DELETE:
            if c < len(L[r]):
                L[r] = L[r][:c] + L[r][c + 1:]
            elif r < len(L) - 1:
                L[r] += L[r + 1]
                del L[r + 1]
        elif event.key == pygame.K_TAB:
            L[r] = L[r][:c] + "    " + L[r][c:]
            self.col += 4
        elif event.key == pygame.K_LEFT:
            if c > 0:
                self.col -= 1
            elif r > 0:
                self.row, self.col = r - 1, len(L[r - 1])
        elif event.key == pygame.K_RIGHT:
            if c < len(L[r]):
                self.col += 1
            elif r < len(L) - 1:
                self.row, self.col = r + 1, 0
        elif event.key == pygame.K_UP and r > 0:
            self.row -= 1
            self.col = min(c, len(L[self.row]))
        elif event.key == pygame.K_DOWN and r < len(L) - 1:
            self.row += 1
            self.col = min(c, len(L[self.row]))
        elif event.key == pygame.K_HOME:
            self.col = 0
        elif event.key == pygame.K_END:
            self.col = len(L[r])
        elif event.unicode and event.unicode.isprintable():
            L[r] = L[r][:c] + event.unicode + L[r][c:]
            self.col += 1

    def draw(self, surf, font, x0, y0, blink_on):
        lh = font.get_linesize() + 2
        for i, line in enumerate(self.lines):
            y = y0 + i * lh
            surf.blit(font.render(f"{i + 1:>2}", True, COLORS["dim"]), (x0, y))
            color = COLORS["dim"] if line.lstrip().startswith("#") else COLORS["text"]
            surf.blit(font.render(line, True, color), (x0 + 34, y))
        if blink_on:
            cw = font.size("M")[0]
            cx = x0 + 34 + self.col * cw
            cy = y0 + self.row * lh
            pygame.draw.rect(surf, COLORS["text"], (cx, cy, 2, lh - 2))


# ---------------------------------------------------------------------------
# Main game
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Code Quest")
    clock = pygame.time.Clock()
    code_font = pygame.font.SysFont("consolas,menlo,dejavusansmono,monospace", 18)
    ui_font = pygame.font.SysFont("arial,helvetica,sans", 18)

    editor = Editor(STARTER_CODE)
    hero = list(START)
    coins = set(COINS)
    queue, step_timer = [], 0
    message, message_color = "Write code, then press F5 to run it!", COLORS["text"]
    collected = 0

    def reset():
        nonlocal hero, coins, queue, collected, message, message_color
        hero, coins, queue, collected = list(START), set(COINS), [], 0
        message, message_color = "Level reset. Press F5 to run your code!", COLORS["text"]

    def run():
        nonlocal hero, coins, queue, collected, message, message_color
        hero, coins, collected = list(START), set(COINS), 0
        res = run_player_code(editor.text)
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
                message, message_color = f"Coin! ({collected}/{len(COINS)})", COLORS["coin"]
            elif kind == "say":
                message, message_color = ev[1], COLORS["text"]
            elif kind == "error":
                message, message_color = ev[1], COLORS["err"]
            elif kind == "finish":
                if tuple(hero) == GOAL:
                    message = f"LEVEL COMPLETE! You collected {collected}/{len(COINS)} coins!"
                    message_color = COLORS["ok"]
                else:
                    message = "Code finished, but you're not at the G yet. Edit and try again!"
                    message_color = COLORS["text"]

        # ---- draw ----
        screen.fill(COLORS["bg"])
        for y, row in enumerate(MAP):
            for x, ch in enumerate(row):
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                pygame.draw.rect(screen, COLORS["wall"] if ch == "#" else COLORS["floor"], rect)
                pygame.draw.rect(screen, COLORS["bg"], rect, 1)
                if ch == "G":
                    pygame.draw.rect(screen, COLORS["goal"], rect.inflate(-8, -8), border_radius=6)
        for (x, y) in coins:
            pygame.draw.circle(screen, COLORS["coin"], (x * TILE + TILE // 2, y * TILE + TILE // 2), 9)
        hx, hy = hero[0] * TILE, hero[1] * TILE
        pygame.draw.rect(screen, COLORS["hero"], (hx + 7, hy + 7, TILE - 14, TILE - 14), border_radius=8)
        pygame.draw.circle(screen, (255, 255, 255), (hx + 15, hy + 17), 3)
        pygame.draw.circle(screen, (255, 255, 255), (hx + 25, hy + 17), 3)

        # code panel
        panel = pygame.Rect(MAP_W, 0, PANEL_W, WIN_H)
        pygame.draw.rect(screen, COLORS["panel"], panel)
        screen.blit(ui_font.render("Your code  (F5 = run, F6 = reset)", True, COLORS["dim"]), (MAP_W + 12, 10))
        editor.draw(screen, code_font, MAP_W + 12, 40, (pygame.time.get_ticks() // 500) % 2 == 0)

        # help
        help_lines = ["move_right(3)  move_left()  move_up()  move_down()",
                      "for i in range(4):   if wall_ahead('right'):   say('hi')"]
        for i, t in enumerate(help_lines):
            screen.blit(ui_font.render(t, True, COLORS["dim"]), (MAP_W + 12, MAP_H - 50 + i * 22))

        # message bar
        pygame.draw.rect(screen, (16, 18, 28), (0, MAP_H, WIN_W, BAR_H))
        screen.blit(ui_font.render(message, True, message_color), (14, MAP_H + 18))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
