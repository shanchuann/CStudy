# CStudy CLI

CStudy now has one portable command core. Windows, Linux, and macOS use the
same `cstudy.py`; `cstudy.ps1` and `cstudy.sh` only locate Python and forward
arguments.

## Commands

```text
cstudy list                 # add --json for automation
cstudy progress             # compact progress and current exercise
cstudy curriculum           # show the book-driven learning path (--json supported)
cstudy check                 # grade every exercise
cstudy verify                # alias for check
cstudy run 00-introduction/compile-run               # grade one exercise
cstudy watch                # watch the first unfinished exercise and auto-advance
cstudy watch 00-introduction/compile-run             # watch a selected exercise
cstudy validate              # validate exercise files
cstudy validate --compile   # also compile every exercise without running tests
cstudy validate --json      # emit a machine-readable validation report
cstudy doctor                # check compiler, Python, API, and题库 readiness
cstudy reset                 # restore Ques.c.bak and clear progress
cstudy check --json          # machine-readable result for CI
cstudy hint 00-introduction/compile-run              # optional API hint
cstudy ai 00-introduction/compile-run --hint-only    # optional API-based learning help
```

An empty invocation opens the interactive learning console. It shows progress
and the current exercise, accepts `watch`, `list`, `progress`, `verify`,
`hint`, `next`, `edit`, `skip`, `reset`, and `quit`, and uses the same Python
implementation on all three supported platforms. `watch` can be used without
an exercise id: it selects the first unfinished exercise, monitors saves, and
automatically advances after a pass.

An exercise is any directory under `Exercises/` containing `Ques.c` (or one C
source file) and `Test.txt`, so future chapter/exercise layouts are supported.

The grader uses `gcc` or `clang`, C11, `-Wall -Wextra -O2`, a temporary build
directory, exact output comparison after line-ending normalization, and a
two-second timeout per test case. Successful exercises are recorded in
`.cstudy/state.json` and retain compatibility with `done.flag`. Skipped
exercises are recorded separately and advance navigation while remaining
available through `run`.

## AI API

Set `CSTUDY_API_KEY` or `OPENAI_API_KEY` before using `cstudy ai`. The default
endpoint is `https://api.openai.com/v1`; set `CSTUDY_API_BASE` for an
OpenAI-compatible gateway, `CSTUDY_AI_MODEL` for the model name, and
`CSTUDY_API_MODE=responses` when the gateway exposes the Responses API instead
of Chat Completions. Requests are time-limited and never write AI output into
`Ques.c` automatically.

The current `scripts/cstudy.ps1` and `scripts/cstudy.sh` remain available for
legacy workflows. The new root-level entry points are the canonical CLI while
the migration is completed.
