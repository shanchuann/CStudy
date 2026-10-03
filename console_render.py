"""Terminal rendering: ANSI colours, CJK-aware widths, wrapping and Markdown.

This module is the presentation core. It has no input handling, so the
interactive layer (console_input) can depend on it without a cycle.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple

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

def clip_visible(text: str, width: int, ellipsis: str = "\u2026") -> str:
    """Truncate to width visible columns, preserving ANSI escape sequences."""
    if visible_width(text) <= width:
        return text
    kept: List[str] = []
    used = 0
    index = 0
    room = max(1, width - visible_width(ellipsis))
    while index < len(text):
        match = ANSI_RE.match(text, index)
        if match:
            kept.append(match.group())
            index = match.end()
            continue
        char = text[index]
        size = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if not unicodedata.combining(char):
            if used + size > room:
                break
            used += size
        kept.append(char)
        index += 1
    return "".join(kept) + ellipsis + _CODES["reset"]

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

def render_file(path: str, width: int) -> int:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read %s: %s" % (path, exc), file=sys.stderr)
        return 2
    print(render_markdown(text, width=width))
    return 0
