# 模块架构

面向维护者：项目分成哪几块、依赖朝哪个方向、关键流程在哪、改哪里最安全。

## 模块图

```text
                 cstudy.py            跨平台 CLI、判题器、状态与进度、学习界面与会话编排
                 ├── ai.py            OpenAI-compatible 请求、SSE 流式解析、配置解析（无业务依赖）
                 ├── chat.py          对话命令表、帮助文本、系统提示与状态行（纯展示 + 数据）
                 ├── console_render.py  颜色、CJK 宽度、换行、Markdown 渲染、代码高亮
                 └── console_input.py   spinner、行编辑器、固定区域、流式输出
                        └── console_ux.py  门面：转发上面两个模块，并保留演示 CLI
```

依赖方向是单向的：`console_input → console_render`，`ai / chat → console_ux(门面)`，
`cstudy → 其余全部`。没有反向依赖，也没有循环导入；`console_ux` 只做转发，
新增公开符号时记得同时加进它的 `__all__`。

## 关键流程

### 判题

1. `grade()` 把题目源码复制到临时目录，用 `gcc/clang -std=c11 -Wall -Wextra -O2` 编译。
2. 每个用例由 `run_case()` 在独立进程里运行：stdin 写入用例输入，stdout/stderr 落到临时文件，
   轮询进程状态以同时执行单用例超时、整题超时与输出上限；Windows 用独立进程组 + `taskkill /T`，
   Linux 额外设 `RLIMIT_CPU/RLIMIT_AS`，Windows 用 Job Object 限制 512 MiB。
3. 输出经 `normalize()` 统一行尾后与期望值精确比较（行内空格不忽略）。
4. `print_result()`（CLI，展开式）与 `result_lines()`（学习界面，紧凑式）共用
   `result_label()` 与 `case_lines()`，保证两种视图的标签与用例格式不会漂移。
5. `check --all` 通过 `grade_many()` 用线程池并行（每个判题本身是独立子进程，GIL 不阻塞），
   结果按原顺序汇总、记录。

### 状态与日志

- `.cstudy/state.json`：每题只存有界摘要（状态、耗时、用例统计、最多 3 个失败用例、时间戳），
  旧格式在读取时压缩；陈旧条目在 `save_state()` 里清理（`prune_state()`）。
- `.cstudy/logs/YYYYMMDD.jsonl`：每次判题一行 JSON，超过 2 MB 轮转成 `.jsonl.1`，超过 30 天删除。
- `current_state()` 是**纯读**，只读命令（`list/status/progress`）不会改写状态文件。

### 缓存

学习界面每帧都要知道"哪些题已完成"和"题面长什么样"，因此有三层按 mtime/TTL 记忆的缓存：
`discover()`（目录指纹 + 0.5 s TTL）、`metadata()`/`has_completion_marker()`（按文件 mtime）、
`done_set()`（按 `_STATE_REVISION`，`save_state()` 时自增）、`rendered_description()`（按文件 mtime + 宽度）。
改题库或进度后如果看到陈旧数据，调用 `invalidate_caches(discovery=True)`。

### 学习界面

`watch_tui()` 是事件循环：单键与 `:`/`/` 命令提示符都走同一个 `dispatch()`，
所以两套输入不会出现行为差异。`build_watch_frame()` 生成"固定头 + 可滚动题面视口 + 紧凑判定块 + 固定状态行/键位行"的整屏文本，
`draw_frame()` 用 `\x1b[H` 逐行覆盖并 `\x1b[J` 收尾，不清屏、不闪烁。

跟随逻辑：`.cstudy/active`（编辑器写入）优先，其次按最近修改的 `Ques.c`（`follow_target()`，0.5 s 节流）。

### AI

`ai.configuration(settings)` 合并环境变量与 `.cstudy/config.json`；`ai.request()` 负责一次请求
（含流式与重试），错误统一抛 `AiRequestError`（携带可打印的行）；`chat.py` 提供命令表、系统提示与状态行；
`cstudy.chat_session()` 只负责"按键 → 状态 → 重绘"的编排，状态放在 `ChatState`。

## 扩展点

| 想做什么 | 改哪里 |
| --- | --- |
| 加一道题 | `scripts/new_exercise.py` 生成骨架 → `scripts/build_exercise.py` 构建 → `scripts/verify_exercises.py` 校验 |
| 加一个子命令 | `build_parser()` 注册 + `command_xxx()` 实现 + `main()` 分发；顺手补单测 |
| 加一个界面按键/命令 | `WATCH_ALIASES` / `WATCH_COMMANDS` + `watch_tui.dispatch()` |
| 换渲染样式 | `console_render.py`（颜色、宽度、Markdown） |
| 调判题限制 | `run_case()` 的超时/输出上限/内存限制，或 `.cstudy/config.json` |
| 加 AI 供应商 | `ai.py` 的 `endpoint()/build_payload()/extract_content()` 与 `configure_ai()` 的预设 |

## CI

`.github/workflows/ci.yml` 有五个作业：`lint`（ruff 的 pyflakes 规则）、
`test-linux`（coverage + 全量 `validate --compile --jobs 4` + 冒烟 + 题库一致性）、
`test-windows` / `test-macos`（单测 + 结构校验 + 冒烟）、
`package`（构建 wheel、装进干净 venv、验证控制台入口与题库根解析）。
