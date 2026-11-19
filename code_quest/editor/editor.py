import pygame

from ..config import COLORS, MAX_EDITOR_COLS, MAX_EDITOR_LINES


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
            if len(L[r]) + 4 <= MAX_EDITOR_COLS:
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

    def handle_text(self, text):
        """Typed characters (letters, digits, symbols). They arrive from pygame's
        TEXTINPUT event, which works with every keyboard layout and input method."""
        for ch in text:
            line = self.lines[self.row]
            if ch.isprintable() and len(line) < MAX_EDITOR_COLS:   # no room left: ignore the key
                self.lines[self.row] = line[:self.col] + ch + line[self.col:]
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
