# Changelog

## 0.6.0

### 编译器配置

- 编译器选择改为三级：环境变量 `CC` → `.cstudy/config.json` 的 `compiler` → `PATH` 中的 `gcc` → `clang`；`CC` 支持绝对路径。
- 新增额外编译参数：`CSTUDY_CFLAGS` → 配置文件的 `cflags` → `CFLAGS`（兜底），追加在基线参数之后，因此可以覆盖基线（如 `-O0` 覆盖 `-O2`）。
- 非 Windows 平台自动追加 `-lm`：学习者直接写 `sqrt/pow/fabs` 也能通过；Windows 的 MinGW 不需要它。用户自己传了 `-lm` 时不会重复。
- 编译命令的拼装收敛到唯一入口 `compile_command()`，判题与 `validate --compile` 共用，不再各写一份。
- `doctor` 输出增强：列出所有候选编译器（命令 → 绝对路径 + 版本）、当前生效的额外参数及其来源、是否追加 `-lm`；当 `CC`/配置指向不存在的程序时给出 warning（此前是静默回退）。
- 新增 `compiler`、`cflags` 两个配置键（`.cstudy/config.json`），单测覆盖选择顺序、参数优先级、`-lm` 策略与 `doctor` 新字段。

## 0.5.0

### 性能

- `cstudy check` 默认并行判题（默认 = CPU 核数，上限 8，`--jobs N` 可调，`--jobs 1` 回到串行）：全库 96 题 **29.5 s → 6.1 s**；`validate --compile` **16.8 s → 3.6 s**。
- 修复学习界面的完成度缓存键（原先按 `id(state)` 记忆，而每帧都会新建 state，导致缓存从不命中）：单帧渲染 **9.25 ms → 4.63 ms**，每帧的 `is_done` 调用从 96 次降到 0 次（只在进度变化时计算一次）。
- 单元测试把"编译全部 96 题"改为抽样 8 题（全量编译交给 CI 的 Linux 作业），测试套件 **35.8 s → 20 s**。

### 结构

- 拆分 `console_ux.py`（1263 行）：`console_render.py`（554 行，颜色/宽度/换行/Markdown）与 `console_input.py`（542 行，spinner/行编辑/固定区域），`console_ux.py` 变成 146 行的门面并保留全部公开符号。
- 拆分 `chat_session`（298 → 129 行）：新增 `ChatState` 与 `chat_start_request` / `chat_interrupt` / `chat_handle_command` / `chat_drain_work`，全项目不再有超过 170 行的函数。
- 新增 `pyproject.toml`（含 `cstudy` 控制台入口），题库根按 `CSTUDY_ROOT` → 当前目录 → 模块目录依次解析，既可 `pipx install` 也可继续 clone 运行。
- 新增 `scripts/new_exercise.py`：一条命令生成题目骨架并自动分配 `order`。

### 交互与文案

- 学习界面文案统一为中文（进度条一行的格式按要求保持不变）。
- 新增"活动文件"识别：`watch` 读取 `.cstudy/active`（编辑器钩子写入的题目 id 或路径），比"保存时间跟随"更精确；`--active-file` 可改路径。
- 命令提示符细节：窗口改变大小时提示行会重排；状态行的跟随/命令提示到期后自动消失。

### 健壮性

- Windows 判题新增 Job Object 内存上限（512 MiB，POSIX 仍用 RLIMIT_AS），防止死循环吃光内存。
- `Test.txt` 支持转义：输入或期望输出中真的需要 `INPUT:`/`OUTPUT:`/`ARGS:`/`---` 时，前面加一个反斜杠。
- CI 的 Linux 作业增加 `coverage` 报告，并只在 Linux 全量 `--compile`（Windows/macOS 跑结构校验），三平台仍各跑单测与冒烟。

## 0.4.0

- Rebuilt the exercise catalogue around the 27 chapters of 《C语言圣经》：每章至少一道练习，共 95 道，目录前缀与课程章节号一致（Exercises/<章节号>-<主题>/<题目>/）。
- 第 28 章“下一步学习方向”和第 29 章“附件与速查”不设练习，已从 book/curriculum.json 的章节清单中移除。
- 每道题都重写了完整题面（题目描述 / 输入格式 / 输出格式 / 示例 / 知识点 / 提示）、初始代码（含 // Done）和多用例测试；测试期望输出由参考解实际运行生成，并用 cstudy 自身的判题逻辑复核。
- Exercises/00-introduction/compile-run（第 0 题）保持不变。
- 同步更新 book/exercise-map.json、README 题量徽章和单元测试中的课程规模断言。
- 修复 cstudy status（不带题号）因 Namespace 缺少 json 字段而崩溃的问题。
- 统一“题号不存在”的报错：status/edit/skip/next 不再静默失败，chat 不再静默回退到当前题；cstudy watch 在全部完成时给出明确提示。
- cstudy check 不带题号时只判定当前练习，新增 --all 判定整个题库（此前会隐式判定全部题目，耗时约 30 秒并覆盖所有进度）。
- current_state() 改为纯读取，陈旧进度改由 save_state() 清理；只读命令不再改写 .cstudy/state.json。
- state.json 只保存有界摘要（状态、耗时、用例统计与最多 3 个失败用例），旧格式在读取时自动压缩；判题日志超过 2 MB 轮转为 .jsonl.1，并清理 30 天前的日志。
- 删除无用文件与目录（AIserver/、Detection/、wsl.localhost/、根目录重复的 cstudy.config.example.json、空的集成测试、.cstudy/full-check.json）和未使用的 import。
- 学习界面改为固定布局：顶部标题/进度条/当前题常驻，底部为判定状态行与键位提示，中间是可分页的题面视口（PgUp/PgDn、↑↓、g/G），题面较长时标题行显示当前行范围。
- 判定结果改为紧凑用例表（一行一个用例，只有失败用例展开期望/实际输出），并在编译判定期间于状态行显示动画；修正按 r/n/x 会重复判题一次的问题。
- 新增 e（打开编辑器）与 s（跳过当前题）快捷键；h 改为题面/提示切换，提示只显示提示要点与第一个用例。
- 练习列表增加完成计数、难度列与自适应列宽。
- 缓存 discover/metadata/完成标记与 Markdown 渲染结果，单帧渲染从 231 ms 降到约 6 ms；清屏改用 ANSI 转义，不再在 Windows 上每帧启动 cls 进程。
- 启动时把标准输出切换为 UTF-8（带替换），重定向输出不再可能因编码失败而中断。
- 拆分模块：`ai.py` 收纳 OpenAI-compatible 请求、流式解析、错误信息与配置解析；`chat.py` 收纳对话命令表、帮助文本、系统提示与状态行。`cstudy.py` 从 2292 行降到 1967 行，公开符号（`ai_request`、`ai_configuration`、`AiCancelled`、`CHAT_COMMANDS`、`chat_status_line` 等）保持不变。
- 统一判定结果渲染：CLI 与学习界面共用 `result_label()` 与 `case_lines()`，不再各写一份标签/用例格式。
- 引入 `ruff.toml`（pyflakes 规则）并在 CI 增加 lint 作业，清掉未使用导入与两处死代码。
- 出题脚本从临时目录 `output/tools/` 收进 `scripts/`（`build_exercise.py`、`verify_exercises.py`、`generate_exercise_map.py`、`cleanup_exercises.py`），并在题目编写文档中说明用法。
- `docs/CStudy-CLI.md` 改为「自动化与集成」专文，命令表以 README 为唯一来源，避免两处漂移。
- 补充 `progress`、`next`、`prev`、`reset` 命令与学习界面布局的单元测试。
- 学习界面新增命令提示符：按 `:` 或 `/` 输入 `/hint`、`/next`、`/goto 12` 等命令后回车执行，带 Tab/↑↓ 补全；单键快捷方式保留，两套输入共用同一个分发函数，不会再各自漂移。
- 新增"跟随最近编辑的文件"：默认自动切到你最近保存的 `Ques.c`（右上角 `[跟随]`），`f` 或 `/follow` 开关，`watch --no-follow` 可禁用。
- 移除已弃用的 Spec Kit（SDD）脚手架：`.specify/`、`.github/prompts/speckit.*`、`specs/001-cstudy-interactive-c/`，以及 `.vscode/settings.json` 中对应的提示词推荐与终端自动放行配置（保留文件类型关联）。

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
