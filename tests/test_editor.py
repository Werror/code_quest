"""Tests for the in-game code editor (typing, indenting, limits)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from code_quest.config import (CODE_FONT_NAMES, CODE_FONT_SIZE, CODE_TEXT_INDENT,  # noqa: E402
                               MAX_EDITOR_COLS, MAX_EDITOR_LINES, PANEL_W)
from code_quest.editor.editor import Editor  # noqa: E402


def press(editor, key, char=""):
    editor.handle_key(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=char, mod=0))


def type_text(editor, text):
    for ch in text:
        if ch == "\n":
            press(editor, pygame.K_RETURN, "\r")
        else:
            editor.handle_text(ch)


def test_typing_adds_characters_at_the_cursor():
    editor = Editor("")
    type_text(editor, "wallet")
    assert editor.text == "wallet"


def test_enter_after_a_colon_indents_four_spaces():
    editor = Editor("")
    type_text(editor, "if x:\nsay(1)")
    assert editor.text == "if x:\n    say(1)"


def test_enter_keeps_the_current_indent():
    editor = Editor("")
    type_text(editor, "if x:\nsay(1)\nsay(2)")
    assert editor.text.endswith("    say(1)\n    say(2)")


def test_backspace_removes_a_whole_indent_at_once():
    editor = Editor("")
    type_text(editor, "if x:\n")
    press(editor, pygame.K_BACKSPACE)
    assert editor.text == "if x:\n"


def test_tab_inserts_four_spaces():
    editor = Editor("")
    press(editor, pygame.K_TAB)
    assert editor.text == "    "


def test_a_line_cannot_get_longer_than_the_code_box():
    editor = Editor("")
    type_text(editor, "x" * (MAX_EDITOR_COLS + 10))
    assert len(editor.text) == MAX_EDITOR_COLS
    press(editor, pygame.K_TAB)
    assert len(editor.text) == MAX_EDITOR_COLS


def test_there_is_a_limit_on_the_number_of_lines():
    editor = Editor("")
    for _ in range(MAX_EDITOR_LINES + 5):
        press(editor, pygame.K_RETURN, "\r")
    assert len(editor.lines) == MAX_EDITOR_LINES


def test_arrow_keys_move_the_cursor_between_lines():
    editor = Editor("ab\ncd")          # cursor starts at the start of the last line
    press(editor, pygame.K_UP)
    assert (editor.row, editor.col) == (0, 0)
    press(editor, pygame.K_END)
    assert editor.col == 2
    press(editor, pygame.K_DOWN)
    assert (editor.row, editor.col) == (1, 2)


def test_the_longest_allowed_line_really_fits_inside_the_panel():
    pygame.font.init()
    char_width = pygame.font.SysFont(CODE_FONT_NAMES, CODE_FONT_SIZE).size("M")[0]
    assert MAX_EDITOR_COLS * char_width <= PANEL_W - CODE_TEXT_INDENT


def test_the_dictionary_line_the_sign_suggests_can_be_typed():
    editor = Editor("")
    line = "VALUES = {'normal': 1, 'red': 5, 'sapphire': 10}"
    type_text(editor, line)
    assert editor.text == line


def test_digits_and_symbols_can_be_typed():
    editor = Editor("")
    type_text(editor, "self.gold = self.gold + 10  # 5 (x) [y] {z}")
    assert editor.text == "self.gold = self.gold + 10  # 5 (x) [y] {z}"


def test_typing_in_the_middle_of_a_line_inserts_there():
    editor = Editor("wallet = 0")
    editor.col = len("wallet = ")
    editor.row = 0
    editor.handle_text("1")
    assert editor.text == "wallet = 10"


def test_several_characters_at_once_from_an_input_method_all_arrive():
    editor = Editor("")
    editor.handle_text("123")
    assert editor.text == "123"
