# CStudy 自动化与集成

命令总览（含全部子命令、选项与交互按键）见 [README](../README.md) 的「命令索引」「判题与完成机制」「交互界面」三节。
本文只讲脚本、CI 与编辑器集成需要的部分。

## 入口

| 入口 | 平台 | 说明 |
| --- | --- | --- |
| `cstudy.ps1` | Windows | 定位 `py -3` 或 `python`，设置 UTF-8 后转发给 `cstudy.py` |
| `cstudy.sh` | Linux / macOS / WSL | 定位 `python3` 或 `python` |
| `cstudy.py` | 全平台 | 唯一核心实现，可直接用 `py cstudy.py` 调用 |
| `pipx install .` | 全平台 | 安装 `cstudy` 控制台入口；题库根按 `CSTUDY_ROOT` → 当前目录 → 模块目录 解析 |
| `scripts/cstudy.ps1`、`scripts/cstudy.sh`、`scripts/reset.ps1` | — | 兼容旧调用路径的转发脚本，行为与根目录入口一致 |
| `scripts/console_ux_demo.py` | — | 终端渲染与动画演示，转发到 `console_ux.py` |
| `scripts/book/` | — | 《C语言圣经》GitBook 维护脚本归档，依赖 `D:\Markdown` 等外部目录，与应用无关 |
| `scripts/build_exercise.py` 等 | — | 出题与题库校验工具，见 [题目编写规范](exercise-authoring.md) |

不带子命令时：stdout 是终端则进入学习界面；被重定向时只输出 `progress: x/N` 和 `current: ...`，
因此可以安全地在脚本里直接调用。

## 机器可读输出

所有查询类命令都支持 `--json`，输出为 UTF-8 编码的单个 JSON 文档：

| 命令 | 结构 |
| --- | --- |
| `list --json` | `{"exercises": [{"number","id","title","difficulty","status"}], "completed", "total"}` |
| `curriculum --json` | `{"book", "chapters": [{"number","id","title","exercises": [id, ...]}]}` |
| `check --json` | `{"results": [判题结果], "passed", "failed", "total"}` |
| `validate --json` | `{"valid", "issues", "exercise_count", "compiled"}` |
| `doctor --json` | `{"platform","python","compiler","exercise_count","invalid_exercises","api_configured","api_base","ai_model","status"}` |
| `status <题号> --json` | 该题的进度条目：状态、最近判定摘要、源码哈希、时间戳 |

单条判题结果包含 `exercise`、`title`、`status`、`compile`（编译命令、返回码、stderr）、
`cases`（每个用例的 `input`/`expected`/`actual`/`duration_ms`/`exit_code`/`error`）与 `duration_ms`。
`status` 取值：`passed`、`incomplete_marker`（用例全过但仍保留 `// Done`）、`compile_error`、
`runtime_error`、`timeout`、`total_timeout`、`output_limit`、`output_mismatch`、`invalid`、`environment_error`。

## 退出码

| 码 | 含义 |
| --- | --- |
| `0` | 成功（判题通过、校验通过） |
| `1` | 判题未通过，或题目无效 |
| `2` | 参数或题号错误 |
| `4` | 运行环境不可用，或 AI 请求失败/超时 |

## CI 与脚本示例

```bash
# 校验题库结构（并可选编译每道题的初始代码）
python cstudy.py validate --compile

# 判定当前题；--all 判定整个题库（默认并行，96 题约 6 秒）
python cstudy.py check
python cstudy.py check --all --jobs 4 --json > results.json

# 并行编译校验（默认 CPU 核数、上限 8，--jobs 1 回到串行）
python cstudy.py validate --compile --jobs 4

# 环境诊断，供流水线判断能否运行
python cstudy.py doctor --json
```

仓库自带的 CI 在 Windows、Linux、macOS 上运行单元测试与上述冒烟命令：
Linux 作业额外输出 `coverage` 报告并做全量 `validate --compile --jobs 4`，
Windows/macOS 只做结构校验（避免三平台重复编译 96 道题）；另有 lint 作业用 ruff 的 pyflakes 规则
检查未使用导入/变量与未定义名称。

编辑器集成：`watch` 读取 `.cstudy/active`（`--active-file` 可改路径）。编辑器侧把当前文件写进去即可：

```powershell
"02-basics/hello" | Set-Content .cstudy/active          # 题目 id
# 或整条路径：.../Exercises/02-basics/hello/Ques.c 也会被识别
```

## 状态与日志

| 路径 | 内容 |
| --- | --- |
| `.cstudy/state.json` | 每题只保留有界摘要（状态、耗时、用例统计、最多 3 个失败用例与最近一次判题时间），旧格式在读取时自动压缩；陈旧条目在写回时清理 |
| `.cstudy/logs/YYYYMMDD.jsonl` | 每次判题一行 JSON，超过 2 MB 轮转为 `.jsonl.1`，超过 30 天自动删除 |
| `**/done.flag` | 与状态文件并存的完成标记，兼容早期版本 |
| `.cstudy/config.json` | AI 配置（明文密钥，已被 .gitignore 忽略） |

## 判题行为

C11、`-Wall -Wextra -O2`、复制源码到临时目录编译运行、行尾归一化后精确比较（行内空格不忽略）、
单用例 2 秒（`--timeout`）、整题 10 秒（`--total-timeout`）、输出上限 1 MiB。
Unix 追加 CPU 时间与约 512 MiB 地址空间软限制；Windows 使用独立进程组，超时后 `taskkill /T` 终止进程树。
判题是本地轻量隔离，不能替代容器或操作系统级沙箱，请只运行可信代码。
