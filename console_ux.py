"""Terminal presentation facade: re-exports console_render and console_input.

Kept as the single import site for cstudy.py and for the demo CLI, so callers
(and tests) can keep using console_ux.paint, console_ux.LineEditor, and so on.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from typing import Iterator, List, Optional

from console_input import (InputReader, LineEditor, LiveConsole, PlainConsole, SPINNERS, Status,
                           StreamingBlock, menu_rows, spinner_frame)
from console_render import (ANSI_RE, _CODES, _FORCE_ANSI, clip_tail, clip_visible, enable_windows_vt,
                            highlight_c_line, pad_to, paint, render_file, render_inline, render_markdown,
                            set_force, supports_ansi, terminal_width, typewriter, visible_width, wrap_text)

__all__ = [
    # console_render
    "ANSI_RE", "_CODES", "_FORCE_ANSI", "clip_tail", "clip_visible", "enable_windows_vt",
    "highlight_c_line", "pad_to", "paint", "render_file", "render_inline", "render_markdown",
    "set_force", "supports_ansi", "terminal_width", "typewriter", "visible_width", "wrap_text",
    # console_input
    "InputReader", "LineEditor", "LiveConsole", "PlainConsole", "SPINNERS", "Status",
    "StreamingBlock", "menu_rows", "spinner_frame",
    # this module
    "FENCE", "TICK", "SAMPLE", "configure_encoding", "demo", "main",
]

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

def configure_encoding() -> None:
    """Use UTF-8 with replacement so redirected output never raises."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

_configure_encoding = configure_encoding

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
