"""Terminal presentation helpers for CStudy: animation and Markdown rendering.

Standard library only (Python 3.9+), matching the rest of the project:

  * Status            - animated spinner and elapsed timer for blocking work
  * typewriter        - progressive character reveal for short messages
  * render_markdown   - Markdown to ANSI: headings, lists, tables, code, quotes
  * wrap_text         - ANSI- and CJK-aware wrapping with hanging punctuation
  * enable_windows_vt - turn on escape processing in legacy Windows consoles

Every helper degrades to plain text when the stream is not a terminal or when
NO_COLOR is set, so redirected output and CI logs stay clean.

Run it directly for a demo, or to render a file:
  python console_ux.py                       # scripted animation demo
  python console_ux.py --render FILE.md      # render a Markdown file
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import sys
import threading
import time
import unicodedata
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# terminal capabilities
# ---------------------------------------------------------------------------
ANSI_RE = re.compile("\x1b\\[[0-9;]*[A-Za-z]")
_CODES = {
    "reset": "\x1b[0m", "bold": "\x1b[1m", "dim": "\x1b[2m",
    "italic": "\x1b[3m", "underline": "\x1b[4m", "reverse": "\x1b[7m",
    "strike": "\x1b[9m",
    "red": "\x1b[31m", "green": "\x1b[32m", "yellow": "\x1b[33m",
    "blue": "\x1b[34m", "magenta": "\x1b[35m", "cyan": "\x1b[36m",
    "white": "\x1b[37m", "grey": "\x1b[90m", "bright_cyan": "\x1b[96m",
}
_FORCE_ANSI = False


def set_force(enabled: bool) -> None:
    """Force ANSI output even when the stream is not a terminal (tests, demos)."""
    global _FORCE_ANSI
    _FORCE_ANSI = enabled


def enable_windows_vt() -> None:
    """Enable ANSI escape processing in legacy Windows consoles (no-op elsewhere)."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        for std_handle in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            handle = kernel32.GetStdHandle(std_handle)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


def supports_ansi(stream=None) -> bool:
    """ANSI is emitted only for a real terminal, so redirected logs stay readable."""
    if _FORCE_ANSI:
        return True
    if os.environ.get("NO_COLOR"):
        return False
    stream = sys.stdout if stream is None else stream
    try:
        return bool(stream.isatty())
    except Exception:
        return False


def paint(value: str, *styles: str) -> str:
    if not supports_ansi(sys.stdout):
        return value
    prefix = "".join(_CODES.get(style, "") for style in styles)
    return prefix + value + _CODES["reset"] if prefix else value


# ---------------------------------------------------------------------------
# width-aware helpers (ANSI escapes and CJK glyphs have no printable width)
# ---------------------------------------------------------------------------
#: columns reserved so trailing punctuation can hang without exceeding the width
_HANG = 2

def visible_width(text: str) -> int:
    width = 0
    for char in ANSI_RE.sub("", text):
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def pad_to(text: str, width: int, align: str = "left") -> str:
    gap = max(0, width - visible_width(text))
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def terminal_width(margin: int = _HANG) -> int:
    """Usable text width for the current terminal, leaving a small margin."""
    columns = shutil.get_terminal_size((88, 24)).columns
    return max(40, min(120, columns - margin))


def _split_by_width(text: str, room: int) -> Tuple[str, str]:
    head: List[str] = []
    used = 0
    for match in re.finditer(r"\x1b\[[0-9;]*[A-Za-z]|.", text):
        piece = match.group(0)
        if piece.startswith("\x1b"):
            head.append(piece)
            continue
        size = visible_width(piece)
        if used + size > room:
            return "".join(head), text[match.start():]
        head.append(piece)
        used += size
    return "".join(head), ""


#: punctuation that must not begin a wrapped line (CJK typesetting rule)
_NO_START = "\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\uff09\u3011\u300b\u300d\u300f%,.;:?!)]}"


def _wrap_units(text: str) -> List[Tuple[str, str]]:
    """Split text into wrap units: ANSI escapes, spaces, ASCII words, single CJK glyphs.

    CJK text has no spaces, so every wide glyph is its own break opportunity;
    ASCII runs stay glued together so English words are never split.
    """
    units: List[Tuple[str, str]] = []
    buffer = ""

    def flush_buffer() -> None:
        nonlocal buffer
        if buffer:
            units.append(("word", buffer))
            buffer = ""

    for piece in re.findall(r"\x1b\[[0-9;]*[A-Za-z]|\s|.", text):
        if piece.startswith("\x1b"):
            flush_buffer()
            units.append(("ansi", piece))
        elif piece.isspace():
            flush_buffer()
            units.append(("space", " "))
        elif ord(piece) < 128:
            buffer += piece
        else:
            flush_buffer()
            units.append(("wide", piece))
    flush_buffer()
    return units


def wrap_text(text: str, width: int, hang: bool = True) -> List[str]:
    """Wrap text to a visual width.

    ANSI escapes are held back and glued to the next visible unit, so a styled
    span is never split at a line break (which would leak colour onto the rest
    of the terminal line). Set hang=False where the result is padded to an exact
    width (table cells), so no line can exceed it.
    """
    width = max(8, width)
    # reserve room for hanging punctuation so no returned line exceeds width
    limit = max(6, width - _HANG) if hang else max(6, width)
    lines: List[str] = []
    current = ""
    current_width = 0
    pending = ""
    space = False

    def flush() -> None:
        nonlocal current, current_width
        if current_width > 0:
            line = current.rstrip()
            if "\x1b[" in line and not line.endswith("\x1b[0m"):
                line += "\x1b[0m"
            lines.append(line)
        current, current_width = "", 0

    for kind, unit in _wrap_units(text):
        if kind == "ansi":
            pending += unit
            continue
        if kind == "space":
            if current_width and pending:
                # close the previous span before the gap, or the space itself
                # would inherit its style
                current += pending
                pending = ""
            space = True
            continue
        prefix, pending = pending, ""
        if space and current_width:
            current += " "
            current_width += 1
        space = False
        word = prefix + unit
        word_width = visible_width(word)
        if current_width and current_width + word_width > limit:
            if hang and kind == "wide" and unit in _NO_START and current_width + word_width <= width:
                # hanging punctuation: let a comma or closing bracket trail the
                # line it belongs to instead of starting the next one
                current += word
                flush()
                continue
            flush()
        elif hang and kind == "wide" and unit in _NO_START and current_width == 0 and lines:
            if visible_width(lines[-1]) + word_width <= width:
                lines[-1] += word
                continue
        while word_width > limit:
            room = limit - current_width
            if room <= 0:
                flush()
                continue
            head, tail = _split_by_width(word, room)
            if not head:
                flush()
                continue
            current += head
            flush()
            word, word_width = tail, visible_width(tail)
            if not word:
                break
        if word:
            current += word
            current_width += word_width
    flush()
    return lines or [""]


# ---------------------------------------------------------------------------
# animation primitives
# ---------------------------------------------------------------------------
SPINNERS = {
    "dots": "\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f",
    "line": "|/-\\",
    "arc": "\u25dc\u25e0\u25dd\u25de\u25e1\u25df",
}


class Status:
    """One-line animated status while a blocking task runs.

    Non-terminal streams get a single start line and the final line instead, so
    captured logs never fill up with carriage-return frames.
    """

    def __init__(self, label: str = "working", spinner: str = "dots",
                 interval: float = 0.08, stream=None) -> None:
        self.stream = sys.stderr if stream is None else stream
        self.frames = SPINNERS.get(spinner, SPINNERS["dots"])
        self.interval = interval
        self.label = label
        self.enabled = supports_ansi(self.stream)
        self._done = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._started = 0.0
        self._stopped = False

    def __enter__(self) -> "Status":
        self._started = time.monotonic()
        if self.enabled:
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        else:
            self.stream.write(self.label + "...\n")
            self.stream.flush()
        return self

    def _spin(self) -> None:
        index = 0
        while not self._done.is_set():
            elapsed = time.monotonic() - self._started
            frame = paint(self.frames[index % len(self.frames)], "cyan")
            line = "\r\x1b[2K" + frame + " " + self.label + " " + paint("(%4.1fs)" % elapsed, "dim")
            try:
                self.stream.write(line)
                self.stream.flush()
            except (OSError, ValueError):
                return
            index += 1
            self._done.wait(self.interval)

    def update(self, label: str) -> None:
        self.label = label

    def stop(self, final: Optional[str] = None) -> None:
        if self._stopped:
            return
        self._stopped = True
        if self._thread is not None:
            self._done.set()
            self._thread.join(timeout=1.0)
            self._thread = None
        if self.enabled:
            self.stream.write("\r\x1b[2K")
        if final:
            self.stream.write(final.rstrip("\n") + "\n")
        self.stream.flush()

    def __exit__(self, *exc_info) -> bool:
        self.stop()
        return False


def spinner_frame(elapsed: float, name: str = "dots", interval: float = 0.08) -> str:
    """One animation frame for the given elapsed time."""
    frames = SPINNERS.get(name, SPINNERS["dots"])
    return frames[int(elapsed / interval) % len(frames)]


def clip_tail(text: str, limit: int) -> str:
    """Keep the tail of a single line within limit columns (escapes dropped)."""
    plain = ANSI_RE.sub("", text).replace("\r", " ").replace("\n", " ")
    if visible_width(plain) <= limit:
        return text.replace("\r", " ").replace("\n", " ")
    kept: List[str] = []
    used = 0
    for char in reversed(plain):
        size = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if used + size > max(1, limit - 1):
            break
        kept.append(char)
        used += size
    return "\u2026" + "".join(reversed(kept))


def menu_rows(commands, query: str, selected: int, width: int, limit: int = 6) -> List[str]:
    """Render the slash-command completion list for the pinned region.

    commands is a sequence of (name, description, takes_argument).
    """
    if not query.startswith("/") or " " in query:
        return []
    matches = [item for item in commands if item[0].startswith(query)]
    if not matches:
        return []
    selected = max(0, min(selected, len(matches) - 1))
    start = 0
    if len(matches) > limit:
        start = max(0, min(selected - limit // 2, len(matches) - limit))
    name_width = max(len(item[0]) for item in matches)
    rows: List[str] = []
    for index in range(start, min(len(matches), start + limit)):
        name, description, _takes = matches[index]
        label = name.ljust(name_width) + "  " + description
        if index == selected:
            rows.append(paint("\u276f " + label, "bold", "cyan"))
        else:
            rows.append(paint("  " + label, "dim"))
    return [clip_tail(row, width) for row in rows]


class LineEditor:
    """Line editing state for a raw-mode reader (pure: never touches the terminal).

    The caret index is the insertion point, and slash commands drive a completion
    menu that the console draws above the input row.
    """

    def __init__(self, prompt: str = "\u203a ", commands=None) -> None:
        self.prompt = prompt
        self.buffer = ""
        self.caret = 0
        self.history: List[str] = []
        self.commands = list(commands or [])
        self.menu_index = 0
        self._history_index: Optional[int] = None

    def matches(self):
        """Commands matching what has been typed so far."""
        text = self.buffer
        if not text.startswith("/") or " " in text:
            return []
        return [item for item in self.commands if item[0].startswith(text)]

    @property
    def menu_open(self) -> bool:
        return bool(self.matches())

    def _selected(self):
        matches = self.matches()
        if not matches:
            return None
        self.menu_index = max(0, min(self.menu_index, len(matches) - 1))
        return matches[self.menu_index]

    def _move_menu(self, step: int) -> None:
        """Move the highlight; it stops at both ends instead of wrapping."""
        matches = self.matches()
        if not matches:
            return
        self.menu_index = max(0, min(self.menu_index + step, len(matches) - 1))

    def _complete(self) -> None:
        """Put the highlighted command in the buffer without running it."""
        selected = self._selected()
        if selected is None:
            return
        name, _description, takes_argument = selected
        self.buffer = name + (" " if takes_argument else "")
        self.caret = len(self.buffer)
        self.menu_index = 0

    def _accept(self) -> Tuple[str, str]:
        """Enter on the menu: complete it, and run commands that take no argument."""
        selected = self._selected()
        if selected is None:
            return "redraw", ""
        name, _description, takes_argument = selected
        self._complete()
        if takes_argument:
            return "redraw", ""
        self.buffer = ""
        self.caret = 0
        self.history.append(name)
        return "submit", name

    def feed(self, key: Optional[str]) -> Tuple[str, str]:
        """Consume one key and return (action, submitted line).

        Actions: "", submit, redraw, cancel, interrupt, exit.
        """
        if not key:
            return "", ""
        if key in ("UP", "DOWN"):
            if self.menu_open:
                self._move_menu(-1 if key == "UP" else 1)
                return "redraw", ""
            self._navigate(key)
            return "redraw", ""
        if key in ("TAB", "\t"):
            if self.menu_open:
                self._complete()
                return "redraw", ""
            return "", ""
        if key in ("\r", "\n", "ENTER"):
            if self.menu_open:
                return self._accept()
            line = self.buffer.strip()
            self.buffer = ""
            self.caret = 0
            self._history_index = None
            if not line:
                return "redraw", ""
            self.history.append(line)
            return "submit", line
        if key in ("\x7f", "\x08", "BACKSPACE"):
            if self.caret > 0:
                self.buffer = self.buffer[:self.caret - 1] + self.buffer[self.caret:]
                self.caret -= 1
            self.menu_index = 0
            return "redraw", ""
        if key == "DELETE":
            if self.caret < len(self.buffer):
                self.buffer = self.buffer[:self.caret] + self.buffer[self.caret + 1:]
            self.menu_index = 0
            return "redraw", ""
        if key == "LEFT":
            self.caret = max(0, self.caret - 1)
            return "redraw", ""
        if key == "RIGHT":
            self.caret = min(len(self.buffer), self.caret + 1)
            return "redraw", ""
        if key in ("HOME", "\x01"):  # Ctrl+A
            self.caret = 0
            return "redraw", ""
        if key in ("END", "\x05"):  # Ctrl+E
            self.caret = len(self.buffer)
            return "redraw", ""
        if key == "\x15":  # Ctrl+U: clear before the caret
            self.buffer = self.buffer[self.caret:]
            self.caret = 0
            self.menu_index = 0
            return "redraw", ""
        if key == "\x0b":  # Ctrl+K: clear after the caret
            self.buffer = self.buffer[:self.caret]
            self.menu_index = 0
            return "redraw", ""
        if key == "\x17":  # Ctrl+W: delete the word before the caret
            head = self.buffer[:self.caret].rstrip()
            cut = head.rfind(" ") + 1
            self.buffer = head[:cut] + self.buffer[self.caret:]
            self.caret = cut
            self.menu_index = 0
            return "redraw", ""
        if key == "ESC":
            if self.menu_open:
                # the menu closes first; a second Esc interrupts the request
                self.buffer = ""
                self.caret = 0
                self.menu_index = 0
                return "redraw", ""
            self.buffer = ""
            self.caret = 0
            return "cancel", ""
        if key == "CTRL-C":
            self.buffer = ""
            self.caret = 0
            return "interrupt", ""
        if key == "\x04":  # Ctrl+D
            return "exit", ""
        if len(key) == 1 and key >= " ":
            self.buffer = self.buffer[:self.caret] + key + self.buffer[self.caret:]
            self.caret += 1
            self.menu_index = 0
            return "redraw", ""
        return "", ""

    def _navigate(self, key: str) -> None:
        if not self.history:
            return
        if key == "UP":
            self._history_index = (len(self.history) - 1 if self._history_index is None
                                   else max(0, self._history_index - 1))
        else:
            if self._history_index is None:
                return
            self._history_index += 1
            if self._history_index >= len(self.history):
                self._history_index = None
                self.buffer = ""
                self.caret = 0
                return
        self.buffer = self.history[self._history_index]
        self.caret = len(self.buffer)


class InputReader:
    """Background key reader: the input line stays editable while work runs."""

    def __init__(self, read_key, editor: Optional[LineEditor] = None,
                 interval: float = 0.05) -> None:
        self.read_key = read_key
        self.editor = editor if editor is not None else LineEditor()
        self.interval = interval
        self.events: "queue.Queue[Tuple[str, str]]" = queue.Queue()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.failed = False

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                key = self.read_key(self.interval)
            except (OSError, RuntimeError, ValueError):
                self.failed = True
                self.events.put(("interrupt", ""))
                return
            action, line = self.editor.feed(key)
            if action:
                self.events.put((action, line))

    def poll(self) -> List[Tuple[str, str]]:
        """Return every event queued since the last call (never blocks)."""
        events: List[Tuple[str, str]] = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                return events

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None


class LiveConsole:
    """A pinned region at the bottom: optional menu rows, a status row, an input row.

    Output is printed above the region, so an answer can arrive while the user
    keeps typing. The region grows and shrinks in place; rows released by a
    shrink are blank space that later output reuses, so nothing scrolls the
    transcript on its own and the viewport is never dragged around while idle.
    """

    def __init__(self, prompt: str = "\u203a ", hint: str = "", stream=None,
                 restore_hidden_cursor: bool = False) -> None:
        self.stream = sys.stdout if stream is None else stream
        self.prompt = prompt
        self.hint = hint
        self.status = ""
        self.input = ""
        self.caret = 0
        self.menu: List[str] = []
        # True when the caller had already hidden the cursor (for example inside
        # the alternate screen buffer): hide it again when this console closes.
        self.restore_hidden_cursor = restore_hidden_cursor
        self._cursor_shown = False
        self._height = 0
        self._rendered = False
        self._width = 0
        self._lock = threading.RLock()

    def _status_row(self) -> str:
        text = self.status or (paint(self.hint, "dim") if self.hint else "")
        return clip_tail(text, terminal_width(2))

    def _input_row(self) -> Tuple[str, int]:
        """Return (row text, caret column) with the caret kept inside the window."""
        prompt_width = visible_width(self.prompt)
        room = max(8, terminal_width(2) - prompt_width)
        text = self.input
        caret = max(0, min(self.caret, len(text)))
        if visible_width(text) <= room:
            return self.prompt + text, prompt_width + visible_width(text[:caret])
        head = text[:caret]
        while head and visible_width(head) > room - 2:
            head = head[1:]
        tail = text[caret:]
        while tail and visible_width(tail) > room - 1 - visible_width(head):
            tail = tail[:-1]
        return (self.prompt + "\u2026" + head + tail,
                prompt_width + 1 + visible_width(head))

    def _rows(self) -> List[str]:
        """Rows of the region, top to bottom: completion menu, status, input."""
        rows = [clip_tail(row, terminal_width(2)) for row in self.menu]
        rows.append(self._status_row())
        rows.append(self._input_row()[0])
        return rows

    def _clear_region(self) -> None:
        """Erase the drawn region and leave the cursor on its (blank) top row."""
        parts = ["\r"]
        if self._height > 1:
            parts.append("\x1b[%dA" % (self._height - 1))
        for index in range(self._height):
            parts.append("\r\x1b[2K")
            if index < self._height - 1:
                parts.append("\n")
        if self._height > 1:
            parts.append("\x1b[%dA" % (self._height - 1))
        parts.append("\r")
        self.stream.write("".join(parts))
        self._height = 0

    def _render(self) -> None:
        self._clear_region()
        if not self._cursor_shown:
            # the caller may have hidden the cursor; make the caret visible again
            self.stream.write("\x1b[?25h")
            self._cursor_shown = True
        rows = self._rows()
        parts: List[str] = []
        for index, row in enumerate(rows):
            parts.append("\r\x1b[2K" + row)
            if index < len(rows) - 1:
                parts.append("\n")
        column = self._input_row()[1]
        parts.append("\r")
        if column > 0:
            parts.append("\x1b[%dC" % column)
        self.stream.write("".join(parts))
        self.stream.flush()
        self._height = len(rows)
        self._rendered = True

    def update(self, status: Optional[str] = None, input_text: Optional[str] = None,
               caret: Optional[int] = None, menu: Optional[List[str]] = None) -> None:
        """Redraw only when something changed.

        Writing while idle would drag the terminal viewport back to the cursor
        every tick, which makes scrolling back through the transcript impossible.
        """
        with self._lock:
            width = terminal_width(2)
            changed = not self._rendered or width != self._width
            self._width = width
            if status is not None and status != self.status:
                self.status = status
                changed = True
            if input_text is not None and input_text != self.input:
                self.input = input_text
                changed = True
            if caret is not None and caret != self.caret:
                self.caret = caret
                changed = True
            if menu is not None and menu != self.menu:
                self.menu = list(menu)
                changed = True
            if not changed:
                return
            self._render()

    def print_above(self, text: str) -> None:
        with self._lock:
            self._clear_region()
            if text:
                self.stream.write(text if text.endswith("\n") else text + "\n")
            self._render()

    def note(self, text: str) -> None:
        """The status row already reports progress, so notes are not echoed."""
        return

    def close(self) -> None:
        with self._lock:
            self._clear_region()
            if self.restore_hidden_cursor and self._cursor_shown:
                self.stream.write("\x1b[?25l")
                self._cursor_shown = False
            self.stream.flush()


class StreamingBlock:
    """Append streamed text above a console's pinned region, wrapping as it goes.

    Complete wrapped lines are emitted immediately and the unfinished tail is
    kept, so the transcript grows upward while the input line stays usable.
    """

    def __init__(self, console, style: str = "dim", prefix: str = "",
                 width: Optional[int] = None) -> None:
        self.console = console
        self.style = style
        self.prefix = prefix
        self.width = width if width else terminal_width(2)
        self.buffer = ""
        self.lines = 0

    def feed(self, piece: str) -> None:
        self.buffer += piece
        self._drain()

    def _drain(self) -> None:
        while True:
            if "\n" in self.buffer:
                head, _, self.buffer = self.buffer.partition("\n")
                self._emit(head)
                continue
            if visible_width(self.buffer) > self.width:
                rows = wrap_text(self.buffer, self.width)
                if len(rows) > 1:
                    for row in rows[:-1]:
                        self._emit(row)
                    self.buffer = rows[-1]
                    continue
            break

    def _emit(self, text: str) -> None:
        if not text.strip():
            return
        self.console.print_above(paint(self.prefix + text, self.style) if self.style else self.prefix + text)
        self.lines += 1

    def flush(self) -> str:
        """Emit the unfinished tail; returns what was still buffered."""
        self._drain()
        remainder, self.buffer = self.buffer, ""
        if remainder.strip():
            self._emit(remainder)
        return remainder


class PlainConsole:
    """Fallback console for hosts without raw keyboard input."""

    def __init__(self, stream=None) -> None:
        self.stream = sys.stdout if stream is None else stream

    def update(self, status: Optional[str] = None, input_text: Optional[str] = None,
               caret: Optional[int] = None, menu: Optional[List[str]] = None) -> None:
        return

    def print_above(self, text: str) -> None:
        if text:
            self.stream.write(text if text.endswith("\n") else text + "\n")
            self.stream.flush()

    def note(self, text: str) -> None:
        self.print_above(paint(text, "dim"))

    def close(self) -> None:
        return


def typewriter(text: str, delay: float = 0.012, stream=None,
               enabled: Optional[bool] = None,
               pause: str = ".\u3002!\uff01?\uff1f\n") -> None:
    """Reveal text character by character, pausing at sentence boundaries."""
    stream = sys.stdout if stream is None else stream
    if enabled is None:
        enabled = supports_ansi(stream) and delay > 0
    if not enabled:
        stream.write(text if text.endswith("\n") else text + "\n")
        stream.flush()
        return
    for char in text:
        stream.write(char)
        stream.flush()
        time.sleep(min(delay * (6 if char in pause else 1), 0.08))
    if not text.endswith("\n"):
        stream.write("\n")
    stream.flush()


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------
C_KEYWORDS = (
    "auto break case const continue default do else enum extern for goto if inline "
    "register restrict return sizeof static struct switch typedef union volatile while "
    "_Bool bool NULL size_t printf scanf malloc free"
).split()
C_LANGUAGES = {"", "c", "h", "cpp", "c++", "cc", "hpp", "hxx"}

_CODE_RULES = re.compile("|".join([
    r"(?P<comment>//[^\n]*|/\*.*?\*/)",
    r"(?P<string>\x22[^\x22\n]*\x22|\x27[^\x27\n]*\x27)",
    r"(?P<preproc>^[ \t]*#[ \t]*[A-Za-z_]+)",
    r"(?P<keyword>\b(?:" + "|".join(C_KEYWORDS) + r")\b)",
    r"(?P<number>\b(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?)[fFuUlL]*\b)",
    r"(?P<call>\b[A-Za-z_]\w*(?=\s*\())",
]))
_CODE_STYLES = {
    "comment": ("dim",), "string": ("green",), "preproc": ("magenta",),
    "keyword": ("cyan", "bold"), "number": ("yellow",), "call": ("bright_cyan",),
}


def _apply_c_rules(line: str, ansi: bool) -> str:
    if not ansi:
        return line

    def replace(match: re.Match) -> str:
        return paint(match.group(0), *_CODE_STYLES.get(match.lastgroup or "", ()))

    return _CODE_RULES.sub(replace, line)


def highlight_c_line(line: str, language: str, in_block: bool, ansi: bool) -> Tuple[str, bool]:
    """Colour one C source line; carries multi-line block-comment state."""
    if not ansi or language not in C_LANGUAGES:
        return line, in_block
    if in_block:
        end = line.find("*/")
        if end < 0:
            return paint(line, "dim"), True
        head = paint(line[:end + 2], "dim")
        rest, _ = highlight_c_line(line[end + 2:], language, False, ansi)
        return head + rest, False
    start = line.find("/*")
    if start >= 0 and line.find("*/", start + 2) < 0:
        return _apply_c_rules(line[:start], ansi) + paint(line[start:], "dim"), True
    return _apply_c_rules(line, ansi), False


def render_inline(text: str, ansi: bool) -> str:
    """Inline Markdown: code spans, bold, italic, strike, links, images."""
    stash: List[str] = []

    def keep(rendered: str) -> str:
        stash.append(rendered)
        return "\x00%d\x00" % (len(stash) - 1)

    def code_span(match: re.Match) -> str:
        body = match.group(1)
        return keep(paint(body, "reverse") if ansi else body)

    def link(match: re.Match) -> str:
        label, url = match.group(1), match.group(2)
        if not ansi:
            return label + " (" + url + ")"
        return paint(label, "underline") + paint(" (" + url + ")", "dim")

    text = re.sub(r"\x60([^\x60]+)\x60", code_span, text)
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: keep(paint(m.group(1), "bold")) if ansi else m.group(1), text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)",
                  lambda m: keep(paint(m.group(1), "italic")) if ansi else m.group(1), text)
    text = re.sub(r"~~(.+?)~~", lambda m: keep(paint(m.group(1), "strike")) if ansi else m.group(1), text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: keep("[\u56fe\u7247] " + (m.group(1) or "") + " " + m.group(2)), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: keep(link(m)), text)
    for index, rendered in enumerate(stash):
        text = text.replace("\x00%d\x00" % index, rendered)
    return text


def _render_code(code: List[str], language: str, ansi: bool) -> List[str]:
    while code and not code[-1].strip():
        code.pop()
    if not code:
        return []
    gutter = len(str(len(code)))
    bar = paint("\u2502", "dim") if ansi else "|"
    output: List[str] = []
    in_block = False
    for index, line in enumerate(code, 1):
        number = paint(("%*d" % (gutter, index)), "dim") if ansi else ("%*d" % (gutter, index))
        body, in_block = highlight_c_line(line.rstrip(), language, in_block, ansi)
        output.append(number + " " + bar + " " + body)
    return output


def _render_table(rows: List[str], width: int, ansi: bool) -> List[str]:
    def cells(row: str) -> List[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [cell.strip() for cell in row.split("|")]

    header = cells(rows[0])
    body = [cells(row) for row in rows[2:]] if len(rows) > 2 else []
    columns = max([len(header)] + [len(row) for row in body] + [1])
    natural: List[int] = []
    for index in range(columns):
        values = [header[index] if index < len(header) else ""]
        values += [row[index] if index < len(row) else "" for row in body]
        natural.append(max(3, max(visible_width(render_inline(value, False)) for value in values)))
    available = max(columns * 6, width - (3 * columns + 1))
    while sum(natural) > available and max(natural) > 6:
        natural[natural.index(max(natural))] -= 1

    vertical = paint("\u2502", "dim") if ansi else "|"

    def rule(left: str, middle: str, right: str) -> str:
        segment = "\u2500" * 0
        pieces = []
        for size in natural:
            piece = "\u2500" * (size + 2)
            pieces.append(paint(piece, "dim") if ansi else piece)
        joiner = paint(middle, "dim") if ansi else middle
        edges = (paint(left, "dim") if ansi else left, paint(right, "dim") if ansi else right)
        return edges[0] + joiner.join(pieces) + edges[1]

    def render_row(values: List[str], bold: bool) -> List[str]:
        wrapped: List[List[str]] = []
        for index in range(columns):
            value = values[index] if index < len(values) else ""
            rendered = render_inline(value, ansi)
            if bold:
                rendered = paint(rendered, "bold") if ansi else rendered
            wrapped.append(wrap_text(rendered, natural[index], hang=False))
        height = max(len(cell) for cell in wrapped)
        lines_out: List[str] = []
        for line_index in range(height):
            parts = []
            for index in range(columns):
                cell = wrapped[index][line_index] if line_index < len(wrapped[index]) else ""
                parts.append(pad_to(cell, natural[index]))
            lines_out.append(vertical + " " + (" " + vertical + " ").join(parts) + " " + vertical)
        return lines_out

    output = [rule("\u250c", "\u252c", "\u2510")]
    output += render_row(header, True)
    output.append(rule("\u251c", "\u253c", "\u2524"))
    for row in body:
        output += render_row(row, False)
    output.append(rule("\u2514", "\u2534", "\u2518"))
    return output


def render_markdown(text: str, width: int = 88, ansi: Optional[bool] = None) -> str:
    """Convert Markdown to styled terminal text (headings, lists, tables, code)."""
    if ansi is None:
        ansi = supports_ansi(sys.stdout)
    out: List[str] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    paragraph: List[str] = []
    index = 0

    def flush_paragraph() -> None:
        if not paragraph:
            return
        joined = " ".join(part.strip() for part in paragraph if part.strip())
        paragraph.clear()
        if joined:
            out.extend(wrap_text(render_inline(joined, ansi), width))
            out.append("")

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()

        fence = re.match(r"^\s*(\x60{3,}|~{3,})\s*([\w+#.-]*)\s*$", raw)
        if fence:
            flush_paragraph()
            marker = fence.group(1)[0]
            language = (fence.group(2) or "").lower()
            index += 1
            code: List[str] = []
            closer = re.compile(r"^\s*" + re.escape(marker) + r"{3,}\s*$")
            while index < len(lines) and not closer.match(lines[index]):
                code.append(lines[index])
                index += 1
            index += 1
            out.extend(_render_code(code, language, ansi))
            out.append("")
            continue

        heading = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", raw)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            style = ("bold", "bright_cyan") if level == 1 else (("bold", "cyan") if level == 2 else ("bold",))
            rows = wrap_text(render_inline(heading.group(2), False), width)
            for row_index, row in enumerate(rows):
                out.append(paint(row, *style) if ansi else row)
                if ansi and level == 1 and row_index == 0:
                    out.append(paint("\u2500" * min(width, max(8, visible_width(row) + 2)), "dim"))
            out.append("")
            index += 1
            continue

        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", raw):
            flush_paragraph()
            out.append(paint("\u2500" * min(width, 60), "dim") if ansi else "-" * min(width, 60))
            out.append("")
            index += 1
            continue

        if re.match(r"^\s*>", raw):
            flush_paragraph()
            quoted: List[str] = []
            while index < len(lines) and re.match(r"^\s*>", lines[index]):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[index]))
                index += 1
            body = " ".join(part.strip() for part in quoted if part.strip())
            bar = paint("\u2502 ", "dim") if ansi else "| "
            for row in wrap_text(render_inline(body, ansi), width - 2):
                out.append(bar + row)
            out.append("")
            continue

        bullet = re.match(r"^(\s*)([-*+])\s+(.*)$", raw)
        ordered = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", raw)
        if bullet or ordered:
            flush_paragraph()
            while index < len(lines):
                item_bullet = re.match(r"^(\s*)([-*+])\s+(.*)$", lines[index])
                item_ordered = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", lines[index])
                item = item_bullet or item_ordered
                if item is None:
                    break
                indent = len(item.group(1)) // 2
                if item_bullet:
                    marker = paint("\u2022", "cyan") if ansi else "-"
                else:
                    marker = paint(item.group(2) + ".", "cyan") if ansi else item.group(2) + "."
                prefix = "  " * indent + marker + " "
                hanging = " " * visible_width(prefix)
                body = render_inline(item.group(3), ansi)
                rows = wrap_text(body, max(8, width - visible_width(prefix)))
                for row_index, row in enumerate(rows):
                    out.append((prefix if row_index == 0 else hanging) + row)
                index += 1
            out.append("")
            continue

        is_table = ("|" in raw and index + 1 < len(lines)
                    and re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", lines[index + 1]))
        if is_table:
            flush_paragraph()
            rows: List[str] = []
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append(lines[index])
                index += 1
            out.extend(_render_table(rows, width, ansi))
            out.append("")
            continue

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# demo
# ---------------------------------------------------------------------------
FENCE = chr(96) * 3
TICK = chr(96)

SAMPLE = """## \u8bca\u65ad

\u7b2c 14 \u884c\u7684 @@T@@scanf@@T@@ \u5c11\u4e86\u53d6\u5730\u5740\u7b26 @@T@@&@@T@@\uff0c\u6240\u4ee5\u7a0b\u5e8f\u628a\u8f93\u5165\u5199\u8fdb\u4e86**\u672a\u521d\u59cb\u5316\u6307\u9488**\uff0c\u8fd0\u884c\u65f6\u76f4\u63a5\u5d29\u6e83\u3002

### \u4fee\u6539\u5efa\u8bae

1. \u7ed9 @@T@@scanf@@T@@ \u8865\u4e0a @@T@@&@@T@@
2. \u7528 @@T@@if (scanf(...) != 1)@@T@@ \u68c0\u67e5\u8f93\u5165\u662f\u5426\u6210\u529f
3. \u7f16\u8bd1\u65f6\u52a0 @@T@@-Wall -Wextra@@T@@ \u8ba9\u7f16\u8bd1\u5668\u66ff\u4f60\u53d1\u73b0\u540c\u7c7b\u95ee\u9898

@@FENCE@@c
#include <stdio.h>

int main(void) {
    int age = 0;
    if (scanf("%d", &age) != 1) {   /* \u8bfb\u53d6\u5931\u8d25 */
        fprintf(stderr, "input error\\n");
        return 1;
    }
    printf("age = %d\\n", age);
    return 0;
}
@@FENCE@@

> \u63d0\u793a\uff1a@@T@@&age@@T@@ \u7684\u7c7b\u578b\u662f @@T@@int *@@T@@\uff0c\u800c @@T@@age@@T@@ \u662f @@T@@int@@T@@\uff0c@@T@@scanf@@T@@ \u9700\u8981\u7684\u662f\u524d\u8005\u3002

| \u68c0\u67e5\u9879 | \u72b6\u6001 | \u8bf4\u660e |
| --- | --- | --- |
| \u7f16\u8bd1 | \u901a\u8fc7 | \u65e0 warning |
| \u7528\u4f8b 1 | \u901a\u8fc7 | \u8f93\u51fa\u4e00\u81f4 |
| \u7528\u4f8b 2 | \u5931\u8d25 | \u7f3a\u5c11\u6362\u884c |

\u53c2\u8003 [C \u6807\u51c6\u5e93\u6587\u6863](https://zh.cppreference.com/w/c/io/scanf) \u4e86\u89e3\u8fd4\u56de\u503c\u8bed\u4e49\u3002

---
""".replace("@@FENCE@@", FENCE).replace("@@T@@", TICK)


def _fake_stream(text: str, size: int = 3) -> Iterator[str]:
    for start in range(0, len(text), size):
        yield text[start:start + size]


def demo(animate: bool, width: int) -> int:
    header = "CStudy console UX demo"
    print(paint(header, "bold", "bright_cyan"))
    print(paint("\u2500" * min(width, len(header) + 6), "dim"))
    print(paint("while the request is in flight: spinner + elapsed time", "dim"))
    print()

    answer = SAMPLE
    if animate:
        received: List[str] = []
        with Status("\u6b63\u5728\u8fde\u63a5\u6a21\u578b", spinner="dots") as status:
            time.sleep(0.5)
            status.update("\u7b49\u5f85\u9996\u4e2a token")
            time.sleep(0.35)
            for chunk in _fake_stream(answer, 2):
                received.append(chunk)
                tail = "".join(received)[-38:].replace("\n", " ").replace("\r", " ")
                status.update("\u63a5\u6536\u4e2d " + tail)
                time.sleep(0.004)
            status.stop(paint("\u2713 \u56de\u7b54\u5b8c\u6210", "green"))
    else:
        received = [answer]
        print("answer received")
    print()
    print(paint("after completion: the same Markdown, rendered", "dim"))
    print()
    print(render_markdown("".join(received), width=width))
    return 0


def render_file(path: str, width: int) -> int:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read %s: %s" % (path, exc), file=sys.stderr)
        return 2
    print(render_markdown(text, width=width))
    return 0


def _configure_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _configure_encoding()
    enable_windows_vt()
    parser = argparse.ArgumentParser(
        prog="console_ux",
        description="CStudy terminal animation and Markdown rendering",
    )
    parser.add_argument("--render", metavar="FILE", help="render a Markdown file and exit")
    parser.add_argument("--width", type=int, default=0, help="wrap width (default: terminal width)")
    parser.add_argument("--anim", dest="animate", action="store_true", default=None,
                        help="force animation even when piped")
    parser.add_argument("--no-anim", dest="animate", action="store_false",
                        help="disable animation for logs and CI")
    parser.add_argument("--typewriter", action="store_true", help="also demo the typewriter helper")
    parser.add_argument("--force", action="store_true", help="force ANSI even when piped")
    args = parser.parse_args(argv)

    set_force(args.force)
    # two spare columns: hanging punctuation may overflow by one glyph
    width = args.width or max(40, min(100, shutil.get_terminal_size((88, 24)).columns - 2))
    animate = supports_ansi(sys.stdout) if args.animate is None else args.animate

    if args.typewriter:
        typewriter("\u8fd9\u662f\u9010\u5b57\u8f93\u51fa\u6548\u679c\uff1aAI \u7684\u56de\u7b54\u53ef\u4ee5\u8fb9\u5230\u8fbe\u8fb9\u663e\u793a\u3002",
                   delay=0.02, enabled=True)
        print()
    if args.render:
        return render_file(args.render, width)
    return demo(animate, width)


if __name__ == "__main__":
    raise SystemExit(main())
