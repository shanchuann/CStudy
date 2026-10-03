"""Conversation vocabulary and presentation for cstudy chat.

Pure helpers only: the slash-command table, help text, system-prompt assembly
and the pinned status row. The session loop itself stays in cstudy.py because it
coordinates keyboard input, network requests and saved progress.
"""
from __future__ import annotations

import json

import console_ux

COMMANDS = [
    ("/help", "\u663e\u793a\u8fd9\u4efd\u5e2e\u52a9", False),
    ("/hint", "\u9488\u5bf9\u5f53\u524d\u7ec3\u4e60\u8bf7\u6c42\u63d0\u793a", False),
    ("/code", "\u91cd\u65b0\u8f7d\u5165 Ques.c \u4e0e\u6700\u8fd1\u5224\u5b9a\u7ed3\u679c", False),
    ("/clear", "\u6e05\u7a7a\u672c\u8f6e\u5bf9\u8bdd\u4e0a\u4e0b\u6587", False),
    ("/model", "\u5207\u6362\u6a21\u578b\uff08\u5982 deepseek-reasoner\uff09", True),
    ("/thinking", "\u5c55\u5f00\u6216\u6536\u8d77\u601d\u8003\u5185\u5bb9", False),
    ("/raw", "\u5207\u6362\u539f\u59cb Markdown \u8f93\u51fa", False),
    ("/stream", "\u5207\u6362\u6d41\u5f0f\u63a5\u6536", False),
    ("/save", "\u628a\u4e0a\u4e00\u6761\u56de\u7b54\u4fdd\u5b58\u5230\u6587\u4ef6", True),
    ("/exit", "\u9000\u51fa\u5bf9\u8bdd", False),
]

HELP = ("\u547d\u4ee4\uff08\u8f93\u5165 / \u53ef\u8865\u5168\uff09\uff1a\n"
        + "\n".join("  %-10s %s" % (name, description) for name, description, _ in COMMANDS)
        + "\n\n\u8bf7\u6c42\u8fdb\u884c\u65f6\uff1aEnter \u6392\u961f\u53d1\u9001\u3001Esc \u4e2d\u65ad\u3001Ctrl+C \u9000\u51fa\u3002"
        + "\n\u7f16\u8f91\u952e\uff1a\u2190/\u2192\u3001Home/End\u3001Backspace\u3001Delete\u3001Ctrl+U/K/W\u3002"
        + "\n\u8f93\u5165 / \u65f6 \u2191\u2193 \u9009\u62e9\u547d\u4ee4\uff0c\u5176\u4f59\u60c5\u51b5 \u2191\u2193 \u8c03\u5386\u53f2\u3002")

SYSTEM_PROMPT = """You are CStudy's C language tutor inside a terminal.
Reply in the same language as the student's question.
Prefer short Markdown: headings, bullet lists, and fenced C code blocks.
Explain the cause before showing code, and never claim code was tested.
Never modify files; the student applies the changes themselves."""

HINT_REQUEST = ("Analyse my current code against the exercise description and tests, then give hints and "
                "debugging questions without revealing the complete solution.")


def system_prompt(exercise: str, title: str, description: str, source: str,
                  tests: str, previous: dict) -> str:
    """Conversation context: the exercise, the student's code, and the last result.

    Callers pass raw text; the truncation limits live here so every entry point
    (one-shot ai, chat opener, /code reload) sends the same context size.
    """
    parts = [SYSTEM_PROMPT, f"Exercise: {exercise} - {title}"]
    if description:
        parts.append("Exercise description:\n" + description[:5000])
    if source:
        parts.append("Current Ques.c:\n" + source[:10000])
    if tests:
        parts.append("Tests:\n" + tests[:5000])
    if previous:
        parts.append("Latest grading result:\n" + json.dumps(previous, ensure_ascii=False)[:3000])
    return "\n\n".join(parts)


def status_line(elapsed: float, label: str, tokens: int, animate: bool = True) -> str:
    """Compose the pinned status row: marker, phase, counters.

    Streamed text belongs to the transcript, so this row never previews it: a
    sliding preview reads as noise and forces a repaint on every token, which
    fights the user's scrolling.
    """
    if not animate:
        # The transcript is visibly moving on its own, so this row stays
        # completely still: any repaint here would fight the user's scrolling
        # while adding nothing they cannot already see.
        return "%s %s" % (console_ux.paint("\u273b", "dim"), label)
    marker = console_ux.paint(console_ux.spinner_frame(elapsed), "cyan")
    return "%s %s %s" % (marker, label,
                         console_ux.paint("(%.1fs \u00b7 %d tok)" % (elapsed, tokens), "dim"))
