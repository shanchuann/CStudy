<p align="center">
  <img src="https://files.seeusercontent.com/2026/09/30/Q5nx/pasted-image-1790749599249.webp" alt="CStudy terminal preview" width="100%">
</p>

<h1 align="center">CStudy</h1>

<p align="center">
  跨平台、脚本驱动的 C 语言交互式学习平台
</p>

<p align="center">
  <a href="https://github.com/shanchuann/CStudy/actions/workflows/ci.yml"><img src="https://github.com/shanchuann/CStudy/actions/workflows/ci.yml/badge.svg" alt="CStudy CI"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/C-C11-A8B9CC?logo=c&logoColor=black" alt="C11">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-4B5563" alt="Windows Linux macOS">
  <a href="LICENSE.txt"><img src="https://img.shields.io/badge/license-MIT-16A34A" alt="MIT License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/CLI-interactive-0EA5E9" alt="Interactive CLI">
  <img src="https://img.shields.io/badge/judge-multi--case-F97316" alt="Multi-case judge">
  <img src="https://img.shields.io/badge/AI-optional-8B5CF6" alt="Optional AI">
  <img src="https://img.shields.io/badge/exercises-33-DC2626" alt="33 exercises">
</p>

CStudy 将题目描述、源码编辑、自动编译、测试判定、完成进度和可选 AI 提示整合在同一个终端学习流程中。保存 `Ques.c` 后即可自动重新判题；通过当前练习后，流程会继续前往下一题。

> Windows 使用 `cstudy.ps1`，Linux/macOS 使用 `cstudy.sh`。三个入口共享同一套 Python 核心、题目状态和判题逻辑。

## 导航

- [快速开始](#快速开始)
- [交互界面](#交互界面)
- [命令索引](#命令索引)
- [判题与完成机制](#判题与完成机制)
- [AI 辅助](#ai-辅助)
- [题目结构](#题目结构)
- [测试用例格式](#测试用例格式)
- [项目结构](#项目结构)
- [开发与验证](#开发与验证)
- [常见问题](#常见问题)

## 核心能力

| 能力 | 说明 |
| --- | --- |
| 实时学习 | 监听当前 `Ques.c`，保存后自动编译和运行测试 |
| 多用例判题 | 区分编译错误、运行错误、超时、输出超限和结果不匹配 |
| 学习进度 | 记录当前题目、完成状态、跳过状态和最近一次判题结果 |
| 交互列表 | 支持方向键移动、筛选、搜索并切换当前练习 |
| 跨平台 | 支持 Windows PowerShell、Linux/WSL 和 macOS |
| AI 提示 | 支持 OpenAI、DeepSeek、GLM 及其他 OpenAI-compatible 服务 |
| 终端对话 | AI 多轮对话、加载动画、流式接收与 Markdown 渲染 |
| 结构化输出 | 支持 `--json`，便于脚本、测试和 CI 使用 |
| 动态题库 | 新练习通过目录和 `metadata.json` 自动加入，无需修改主程序 |

## 快速开始

### 环境要求

| 依赖 | 要求 |
| --- | --- |
| Python | 3.9 或更高版本 |
| C 编译器 | `gcc` 或 `clang` |
| Windows | 推荐 PowerShell 7 |
| Linux/macOS | Bash 或兼容 Shell |

### Windows

```powershell
git clone https://github.com/shanchuann/CStudy.git
cd CStudy
.\cstudy.ps1
```

### Linux / macOS / WSL

```bash
git clone https://github.com/shanchuann/CStudy.git
cd CStudy
bash ./cstudy.sh
```

直接启动会恢复上次进度，选择第一个未完成练习，打开源码并进入实时判题界面。只想查看环境状态时运行：

```powershell
.\cstudy.ps1 doctor
```

```bash
bash ./cstudy.sh doctor
```

## 交互界面

### 学习界面

| 按键 | 操作 |
| --- | --- |
| `n` | 当前题通过后进入下一题 |
| `r` | 立即重新编译并判题 |
| `h` | 显示或隐藏题目提示 |
| `a` | 打开 AI 对话，进入时自动请求一次提示 |
| `l` | 打开练习列表 |
| `x` | 重置当前练习 |
| `q` | 退出并保留进度 |

### 练习列表

| 按键 | 操作 |
| --- | --- |
| `↑` / `↓` 或 `k` / `j` | 移动选择项 |
| `Enter` | 切换到选中的练习 |
| `d` | 筛选已完成练习 |
| `p` | 筛选未完成练习 |
| `s` 或 `/` | 搜索练习 |
| `g` / `G` | 跳到列表开头或末尾 |
| `q` | 返回学习界面 |

编辑器可通过 `--edit-cmd "code"`、`CSTUDY_EDIT_CMD`、`EDITOR` 或 `VISUAL` 配置。不希望自动打开编辑器时使用 `watch --no-editor`。

## 命令索引

| 命令 | 用途 |
| --- | --- |
| `cstudy list` | 显示题目与完成状态 |
| `cstudy progress` | `list` 的进度别名 |
| `cstudy curriculum` | 查看课程章节映射 |
| `cstudy run <id>` | 编译并判定指定练习 |
| `cstudy check` | 检查练习 |
| `cstudy watch [id]` | 进入实时学习流程 |
| `cstudy next` | 前往下一题 |
| `cstudy prev <id>` | 前往上一题 |
| `cstudy edit <id>` | 使用配置的编辑器打开题目 |
| `cstudy hint <id>` | 获取题目提示 |
| `cstudy skip <id>` | 跳过并记录题目状态 |
| `cstudy status [id]` | 查看当前或指定题目状态 |
| `cstudy reset` | 恢复题目初始代码并重置进度 |
| `cstudy validate --compile` | 校验并编译整个题库 |
| `cstudy doctor --json` | 输出环境诊断信息 |
| `cstudy ai --setup` | 配置 AI 服务 |
| `cstudy ai <id> --hint-only` | 获取提示，不直接给出完整答案 |
| `cstudy chat [id]` | 进入 AI 多轮对话；`--no-stream` 关闭流式接收，`--raw` 输出原始 Markdown |

机器可读模式示例：

```bash
bash ./cstudy.sh check --json
bash ./cstudy.sh validate --json
```

## 判题与完成机制

判题器使用 C11 模式编译源码：

```text
gcc -std=c11 -Wall -Wextra -O2
```

编译、运行和输出比较均在临时目录进行。每个用例有独立超时，每道题有总运行时限，并限制最大输出量。行尾会被统一，但行内空格不会被随意删除。

| 状态 | 含义 |
| --- | --- |
| `PASS` | 编译成功且所有测试用例通过 |
| `WARNING` | 测试通过，但仍保留 `// Done` 完成标记 |
| `compile_error` | C 源码编译失败 |
| `runtime_error` | 程序异常退出 |
| `timeout` | 程序运行超时 |
| `output_limit` | 程序输出超过限制 |
| `output_mismatch` | 实际输出与预期结果不一致 |

每道未完成练习的 `Ques.c` 中带有 `// Done` 标记。代码通过全部测试后，还需要删除该标记并再次保存，练习才会记录为完成并自动进入下一题。

进度保存在 `.cstudy/state.json`，判题日志保存在 `.cstudy/logs/`。这些文件均为本地状态，不进入 Git。

> CStudy 提供本地轻量运行隔离和进程资源控制，但不等同于容器或虚拟机级安全沙箱。请只运行可信练习代码。

## AI 辅助

AI 是可选功能，不参与判题结果。未配置或服务不可用时，练习、判题、进度和 CI 功能仍可正常使用。

### 自动配置

```powershell
.\cstudy.ps1 ai --setup
```

```bash
bash ./cstudy.sh ai --setup
```

向导只要求填写：

1. API Base
2. API Key

CStudy 会自动识别服务、选择模型和接口模式。对于其他 OpenAI-compatible 服务，会调用 `<API Base>/models` 自动选择对话模型。

| 服务 | API Base | 自动模型 | 接口 |
| --- | --- | --- | --- |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | Chat Completions |
| DeepSeek | `https://api.deepseek.com` | `deepseek-flash` | Chat Completions |
| GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | Chat Completions |
| 其他兼容服务 | 用户填写 | 通过 `/models` 发现 | Chat Completions |

配置保存在 `.cstudy/config.json`。该目录已被 Git 忽略，但 API Key 仍以明文保存在本机，请勿分享配置文件、终端日志或包含密钥的截图。

### 环境变量

`CSTUDY_*` 环境变量优先于本地配置，适合 CI 或临时切换服务：

```powershell
$env:CSTUDY_API_KEY = "your-key"
$env:CSTUDY_API_BASE = "https://api.deepseek.com"
$env:CSTUDY_AI_MODEL = "deepseek-flash"
.\cstudy.ps1 ai 01-basics/hello --hint-only
```

可用变量：

| 变量 | 说明 |
| --- | --- |
| `CSTUDY_API_KEY` | 显式覆盖当前 API Key |
| `CSTUDY_API_BASE` | API 基础地址 |
| `CSTUDY_AI_MODEL` | 模型名称 |
| `CSTUDY_API_MODE` | `chat` 或 `responses` |
| `OPENAI_API_KEY` | 未配置服务时的兼容兜底 |

密钥优先级为 `CSTUDY_API_KEY` → 本地 AI 配置 → `OPENAI_API_KEY`。

### AI 请求内容

CStudy 会发送当前题目描述、源码、测试用例和最近一次判题结果。AI 只输出分析、提示或参考解，不会自动覆盖 `Ques.c`。

### 终端对话与渲染

`cstudy chat [id]`，或学习界面中的 `a` 键，会进入多轮对话：请求期间显示加载动画（转圈、已用时间、已接收 token 数和思考/回答的实时预览），回答结束后按终端宽度渲染 Markdown（标题、列表、表格、带语法高亮的代码块）。

请求进行时**输入不会被阻塞**：底部固定区域，输入行始终可编辑，**光标停在插入位置**。状态行**不显示流式文本**（思考/回答的文字只在上方累加）：等待首个 token、以及回答生成（屏幕上没有其他东西在动）时显示转圈 + 耗时 + token 计数；而思考行正在屏幕上滚动时，状态行完全静止为 `✻ Thinking`，不去和你的滚动抢焦点。（即使学习界面隐藏了光标也会重新显示）。回车把消息排队，当前回答结束后自动发送；`Esc` 中断当前请求；`Ctrl+C` 退出。编辑键：`←`/`→` 移动光标、`Home`/`End`、`Backspace`/`Delete`、`Ctrl+U`/`Ctrl+K`/`Ctrl+W`、`↑`/`↓` 调历史。

在学习界面按 `a` 进入对话时会**暂时退出全屏界面**，回到普通终端缓冲区——因为全屏界面用的是没有回滚历史的备用缓冲区，在那里滚轮/PageUp 不会有任何反应。对话结束后自动切回学习界面。

输入 `/` 会弹出命令补全列表（输入行上方列出候选与说明），此时状态行提示 `↑↓ select · Enter run · Tab complete · Esc close`：`↑`/`↓` 移动高亮并在两端停住，`Enter` 直接执行无参数命令（如 `/hint`），带参数命令（`/model`、`/save`）会补全并等你输入参数，`Tab` 只补全不执行，`Esc` 先关闭菜单、再按一次才中断请求。

每次提交都会**回显到对话记录**（`› /help`），所以命令是否执行、执行了哪一条一目了然；空闲时按 `Esc` 不会有任何输出（没有请求可中断就不提示）。使用 `deepseek-reasoner` 等推理模型时，思考过程会**逐行向上累加到控制台**（不再挤在一行里滚动），回答完成后补一行 `✻ thought for Ns` 小结；用 `/thinking` 关闭或重新开启思考输出，用 `/model <名称>` 临时切换模型。

空闲时控制台**不写任何字节**（只有内容变化才重绘），所以可以随时向上滚动回看历史，不会被拉回底部；历史输入 `↑`/`↓` 和练习列表 `j`/`k` 到两端就停住，不会环绕跳转。

| 对话命令 | 说明 |
| --- | --- |
| `/hint` | 让 AI 分析当前代码并给出提示 |
| `/code` | 重新载入 `Ques.c` 和最近判题结果 |
| `/model <名称>` | 切换模型（例如 `deepseek-reasoner`） |
| `/thinking` | 展开或收起完整思考内容 |
| `/clear` | 清空本轮对话上下文 |
| `/raw` | 切换为原始 Markdown 输出 |
| `/stream` | 切换流式接收 |
| `/save <文件>` | 把上一条回答保存为文件 |
| `/exit` | 退出对话 |

渲染只在交互式终端启用：输出被重定向或设置了 `NO_COLOR` 时自动退化为纯文本，CI 日志和管道输出保持干净；`cstudy ai` 在非交互环境下原样输出，便于脚本处理。

## 题目结构

推荐使用章节化目录：

```text
Exercises/01-basics/hello/
├── description.md   # 题目描述与学习目标
├── Ques.c           # 学习者作答文件
├── Ques.c.bak       # 初始代码备份
├── Test.txt         # 测试用例
└── metadata.json    # 题目元数据
```

`metadata.json` 支持以下字段：

| 字段 | 说明 |
| --- | --- |
| `title` | 题目标题 |
| `difficulty` | 难度 |
| `tags` | 标签数组 |
| `order` | 固定排序值 |
| `status` | `active`、`hidden` 或 `disabled` |
| `sources` | 多源文件练习的源码列表 |

## 测试用例格式

`Test.txt` 使用 `INPUT`、`OUTPUT` 和 `---` 定义多组用例：

```text
INPUT:
<标准输入，可多行>
OUTPUT:
<预期输出，可多行>
---
INPUT:
<下一组输入>
OUTPUT:
<下一组输出>
```

命令行参数题可在 `INPUT:` 前加入：

```text
ARGS: one two
INPUT:
OUTPUT:
one two
```

参数会按 Shell 规则解析，并传给 `main(int argc, char **argv)`。

## 项目结构

```text
CStudy/
├── cstudy.py              # 跨平台 CLI、判题器和交互界面
├── console_ux.py          # 终端动画与 Markdown 渲染（仅标准库）
├── cstudy.ps1             # Windows 入口
├── cstudy.sh              # Linux/macOS/WSL 入口
├── Exercises/             # 练习题库
├── book/                  # 章节清单与题目映射
├── tests/                 # 单元与集成测试
├── docs/                  # 开发和项目文档
├── AIserver/              # AI 配置兼容提示
└── .github/workflows/     # 三平台 CI
```

## 开发与验证

运行全部单元测试：

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

校验题目元数据、测试格式与源码编译：

```bash
python cstudy.py validate --compile
```

CI 在 Windows、Linux 和 macOS 上分别执行完整单元测试与 CLI smoke tests，并且不会启动阻塞式交互界面。

## 常见问题

<details>
<summary><strong>保存代码后没有通过</strong></summary>

查看界面中的编译错误、实际输出和预期输出。输出比较只统一行尾，不会忽略多余空格。测试全部通过后还需要删除源码中的 `// Done`。
</details>

<details>
<summary><strong>没有自动打开编辑器</strong></summary>

设置 `CSTUDY_EDIT_CMD`、`EDITOR` 或 `VISUAL`，也可以向 `watch` 传入 `--edit-cmd "code"`。
</details>

<details>
<summary><strong>AI 返回 401 或 403</strong></summary>

检查密钥是否有效、账号是否有权访问模型，以及是否存在覆盖本地配置的 `CSTUDY_API_KEY`。运行 `cstudy doctor --json` 可查看当前 API Base 和模型，但不会输出密钥。
</details>

<details>
<summary><strong>AI 返回 404</strong></summary>

API Base 应填写版本根地址，不要包含 `/chat/completions` 或 `/responses`。DeepSeek 使用 `https://api.deepseek.com`。
</details>

<details>
<summary><strong>AI 请求超时或触发限流</strong></summary>

检查网络、代理、服务余额和速率限制。可使用 `--ai-timeout` 调整等待时间。
</details>

## License

本项目采用 [MIT License](LICENSE.txt)，可用于学习、修改与分发。
