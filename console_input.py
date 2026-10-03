"""Interactive console primitives: spinners, line editing and pinned regions.

Depends on console_render for colours and widths; nothing here is imported by
console_render, so the dependency direction stays one-way.
"""
from __future__ import annotations

import queue
import sys
import threading
import time
from typing import List, Optional, Tuple

from console_render import (clip_tail, paint, supports_ansi, terminal_width, visible_width,
                            wrap_text)

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
