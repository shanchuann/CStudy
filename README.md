# CStudy - 跨平台、脚本驱动的 C 语言学习平台

> 当前推荐入口是根目录的 `cstudy.py`，Windows 使用 `cstudy.ps1`，Linux/macOS 使用 `cstudy.sh`。三端共享同一套题目发现、判题、状态和日志实现。

## 统一 CLI

```text
cstudy list
cstudy progress
cstudy curriculum
cstudy verify
cstudy run 00-introduction/compile-run
cstudy check --json
cstudy watch 00-introduction/compile-run
cstudy next
cstudy prev 00-introduction/compile-run
cstudy edit 00-introduction/compile-run
cstudy skip 00-introduction/compile-run
cstudy status 00-introduction/compile-run
cstudy validate
cstudy doctor
cstudy reset
cstudy ai 00-introduction/compile-run --hint-only
```

直接运行 `cstudy.ps1`、`cstudy.sh` 或 `cstudy.py` 会进入实时学习界面，自动选择第一个未完成题目并执行判题。保存 `Ques.c` 后自动重判，当前源码路径带有终端可点击链接。界面按键为：`n` 下一题（当前题通过后）、`r` 重跑、`h` 提示、`a` 请求 AI 提示、`l` 题目列表、`x` 重置当前题、`q` 退出。列表中可用 `j/k` 或方向键移动，`d/p` 筛选已完成/未完成，`s` 搜索，回车切换当前题目。

编辑器可通过 `--edit-cmd "code"`、`CSTUDY_EDIT_CMD`、`EDITOR` 或 `VISUAL` 配置；不希望自动打开编辑器时使用 `cstudy watch --no-editor`。

判题使用 `gcc` 或 `clang` 的 C11 模式，默认启用 `-Wall -Wextra -O2`。每个测试用例有独立超时，每道题有总超时，程序在临时目录运行，结果写入 `.cstudy/logs/`，进度写入 `.cstudy/state.json`。这是本地轻量运行隔离，不等同于容器级安全沙箱。

每道未完成题目的 `Ques.c` 末尾带有 `// Done` 标记。测试通过后，需要删除该标记并重新运行判题，题目才会记录为完成，`n` 才能进入下一题。这让代码测试结果和学习者的明确完成动作同时生效。

题目目录支持扁平和章节结构，推荐格式如下：

```text
Exercises/01-basics/hello/
├── description.md
├── Ques.c
├── Ques.c.bak
├── Test.txt
└── metadata.json
```

`metadata.json` 支持 `title`、`difficulty`、`tags`、`order` 和 `status`（`active`、`hidden`、`disabled`）。课程章节清单见 `book/curriculum.json`，内容对应《C语言圣经》GitBook。

CI 使用非交互命令和 Python `unittest`，不会启动阻塞式控制台。

CStudy 是一个跨平台、脚本驱动的 C 语言学习平台。三个入口共享同一套 Python 核心。

## 特色功能

- 跨平台 CLI：根目录 `cstudy.ps1`、`cstudy.sh` 和 `cstudy.py`
- 动态题库：`Exercises/` 下每题一个目录（第 0 题为 `00-introduction/compile-run/`），含 `Ques.c`、`description.md`、`Test.txt`
- 自动判题：解析 `Test.txt` 的 INPUT/OUTPUT/--- 分组并比对运行结果
- 仓库验证：`validate --compile` 会在不运行测试的情况下编译全部题目，适合 CI
- 进度展示：在主界面显示整体进度并自动聚焦第一个未完成题
- AI 辅助：通过 OpenAI-compatible API 生成提示、分析和参考解
- 一键重置：清理完成标记并从 `Ques.c.bak` 恢复初始代码

## 目录结构

```text
CStudy/
├─ scripts/                # 辅助脚本（主 CLI 在根目录）
├─ Exercises/              # 练习目录（每题一个子目录）
│  └─ 00-introduction/compile-run/
│     ├─ Ques.c            # 作答文件
│     ├─ Ques.c.bak        # 初始备份
│     ├─ description.md    # 题目描述
│     └─ Test.txt          # 测试用例（INPUT/OUTPUT/---）
├─ AIserver/
│  └─ ai_server_stub.sh    # API 配置提示（核心请求在 cstudy.py）
├─ docs/
│  └─ PROJECT_DESCRIPTION.md# 简明项目描述
└─ ...
```

## 快速开始（PowerShell / Windows）

1. 打开 PowerShell，进入项目根目录
2. 运行主脚本

   ```powershell
   cstudy.ps1
   ```

3. 使用 AI 前设置 API 环境变量：
   - `CSTUDY_API_KEY` 或 `OPENAI_API_KEY`
   - 可选 `CSTUDY_API_BASE`（默认 `https://api.openai.com/v1`）
   - 可选 `CSTUDY_AI_MODEL`（默认 `gpt-4o-mini`）

### AI 入口

在实时学习界面按 `a`，CStudy 会把当前题目的描述、源码、测试用例和最近一次判题结果发送给配置的 OpenAI-compatible API，并显示针对当前题目的提示。按 Enter 返回学习界面。

也可以直接从命令行调用：

```powershell
# 当前题目给出提示，不修改 Ques.c
.\cstudy.ps1 ai 01-basics/hello --hint-only

# 获取错误分析和参考实现建议
.\cstudy.ps1 ai 01-basics/hello
```

Linux/macOS 使用：

```bash
./cstudy.sh ai 01-basics/hello --hint-only
```

AI 是可选功能；未配置 API key 时，判题、watch、list 等核心功能仍然可用。

## 命令说明

- check：检测全部练习
- run <id>：检测指定练习
- list：显示题目列表与完成情况
- ai：调用配置的 API 获取学习辅助
- reset：清理完成标记并用 `Ques.c.bak` 还原 `Ques.c`
- quit：退出系统

## 测试用例规范（Test.txt）

使用以下分节格式，可以定义多组用例：

```text
INPUT:
<标准输入（可多行）>
OUTPUT:
<期望输出（可多行）>
---
```

命令行参数题可以在 `INPUT:` 前增加一行，例如 `ARGS: one two`；参数会按 shell 规则解析并传给 `main(int argc, char **argv)`。

判题器将依次编译运行并严格按行比对输出。

## API AI 辅助

- `cstudy ai 00-introduction/compile-run` 会将题目描述、当前代码、测试用例和最近一次判题结果发送到 API
- `cstudy ai 00-introduction/compile-run --hint-only` 只请求提示和调试问题，不直接给出完整答案
- API 失败、超时或返回格式异常时只输出错误，不修改题目文件

## 重置与备份

- 每个练习目录可维护 `Ques.c.bak` 作为初始备份
- 执行 `reset`：
  - 删除所有 `done.flag`
  - 用 `Ques.c.bak` 覆盖 `Ques.c`（若存在）
  - 清理残留 `.exe`

## 常见问题

- 判题失败但无输出：检查是否存在 `Test.txt` 且格式正确；确认代码能成功编译
- AI 无响应：检查 `CSTUDY_API_BASE`、API key、模型名和网络连接
- 未显示“运行结果”：若 `Test.txt` 无 INPUT 段，则直接运行程序的默认输出

## 许可证

本项目基于 MIT 许可证开源，允许个人或商业场景下的使用、修改与分发，详见LICENSE.txt文件。

