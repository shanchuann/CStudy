# Changelog

## 0.3.0

- Added `cstudy chat` (alias `ask`) for multi-turn AI conversation about the current exercise, with `/hint`, `/code`, `/clear`, `/raw`, `/stream`, `/save`, and `/exit`.
- Added animated request feedback: spinner, elapsed time, and a live streaming preview, followed by a rendered Markdown answer.
- Added `console_ux.py`: a standard-library Markdown renderer (headings, lists, tables, C syntax highlighting) and animation helpers with ANSI- and CJK-aware wrapping.
- The learning interface renders `description.md` as Markdown, and the `a` key now opens the chat session.
- AI requests support streaming with an automatic fallback when a gateway ignores `stream: true`; redirected output and `NO_COLOR` remain plain text.
- The pinned status row no longer previews streamed text; it shows only the spinner, elapsed time and token count while waiting or receiving, and goes completely still (`✻ Thinking`) while the thinking transcript is scrolling on its own.
- The `a` key now leaves the alternate screen for the duration of the chat, so the conversation lands in the normal buffer where mouse-wheel and PageUp scrolling actually work (the alternate screen keeps no history).
- Submitted input is echoed into the transcript (`› /help`), the status row explains the menu keys while it is open, and Esc stays silent when there is no request to interrupt.
- Typing `/` opens a slash-command completion menu above the input row; Up/Down move the highlight and stop at both ends, Enter runs argument-free commands or completes the ones that take an argument, Tab completes without running, and Esc closes the menu before interrupting.
- The input line shows a real caret: the terminal cursor is parked at the insertion point (and re-shown when a host such as the alternate screen had hidden it), with Left/Right, Home/End, Delete, Ctrl+U/K/W editing and history recall.
- Input is no longer blocked while a request runs: a background key reader and a pinned status/input region let you keep typing, queue messages with Enter, interrupt with `Esc`, and leave with `Ctrl+C`.
- Reasoning is surfaced: `reasoning_content` and Responses reasoning summaries accumulate line by line in the transcript (with a `✻ Thinking` header and a closing summary), `/thinking` toggles it, and `/model` switches models.
- The console writes nothing while idle, so scrolling back through the transcript is no longer yanked to the bottom; history and list navigation stop at both ends instead of wrapping.
- In-flight requests can be cancelled (the response is closed), and transient connection failures are retried once with an actionable message.

## 0.2.0

- Added one portable Python CLI for Windows, Linux, and macOS.
- Added metadata-aware recursive exercise discovery and book curriculum catalog.
- Reworked grading with C11 warnings, temporary build directories, process termination, per-case and total timeouts, output limits, JSON results, state, and JSONL logs.
- Added `next`, `prev`, `edit`, `skip`, `status`, `watch`, `validate`, and optional API assistance.
- Added 9 book-aligned starter exercises and cross-platform non-interactive CI tests.
