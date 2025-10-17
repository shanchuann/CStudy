# CStudy 系统技术说明

以下内容由GPT根据我的需求生成

## 1. 总体目标与约束

* 平台：Windows（主要用 PowerShell / .ps1 脚本作为主入口），依赖 `gcc`（MinGW/WSL/WSL2/安装路径要在 PATH 中）与 `ollama`（用于本地模型管理，若用户启用 AI）。
* 功能：练习管理（Exercises）、自动判题（Detection）、本地 AI 辅助（AIserver）、控制台交互（仿 rustlings）。
* 输出编码：控制台与文件读写均使用 UTF-8（避免中文乱码）。
* UI 风格：命令行交互，主界面每次刷新（clear + 重新打印），提供可点击的 Ques.c 路径（依赖终端/编辑器支持）。
* 用户操作模式：交互式单一进程/控制台，支持命令：`check`、`list`、`AI`、`quit`、`help me`（进入 AI 辅助），以及 `begin`（进入练习可选项）。
* 必须实现：自动触发判题（保存文件后）与手动 `CStudy check` 的批量判题。

---

## 2. 文件结构与格式规范（精确）

```text
CStudy/
├─ Exercises/
│  ├─ Chapter1/
│  │  ├─ Exercise1/
│  │  │  ├─ description.md
│  │  │  ├─ Ques.c
│  │  │  ├─ help.txt
│  │  │  ├─ Test.txt    # 测试用例（或 Test.c，用于更复杂的 harness）
│  │  │  └─ metadata.json (可选)
│  │  └─ Exercise2/
│  └─ Chapter2/
├─ Detection/
│  ├─ detect.ps1 (或 detect.py)
│  └─ utils/ (日志、模板)
├─ AIserver/
│  ├─ model/             # 存放 ollama 下载的模型（约定路径）
│  └─ ai_manager.ps1
└─ CStudy.ps1
```

### 2.1 description.md 格式（必须）

* 文件编码：UTF-8 (no BOM)
* 约定格式（Markdown）：

```markdown
# 题目名称

题目描述（多行，描述需求、约束、注意事项，输入输出说明）

## 输入
（示例与格式说明）

## 输出
（示例与格式说明）

## 示例
输入：
<示例输入>

输出：
<示例输出>

## 其它说明
（可选，算法提示、边界条件）
```

* 解析规则：名称取 `#` 标题第一行；示例输入和输出用于手动检查和 AI 上下文采集。

### 2.2 Ques.c 约定

* 必须包含注释头：题目名称、作者（可空）、编辑区标注
* 保留用户编辑区域注释格式，例如：

```c
/* =========================
   题目：两数之和
   说明：在下面的区域实现函数
   ========================= */

#include <stdio.h>

int main() {
    // --- 用户编辑区开始 ---
    
    // 请在这里填写代码
    
    // --- 用户编辑区结束 ---
    return 0;
}
```

* 推荐在文件底部加上 `// I'm finish` 注释作为完成标记（判题时检查该标记是否删除以提示“未完成注释”逻辑）。

### 2.3 Test.txt 规范（最重要）

* 采用统一的格式：多个样例由分隔符 `---` 隔开；每个样例包含 `INPUT:` 与 `OUTPUT:` 两段。
* 示例：

```text
# 样例1
INPUT:
1 2
OUTPUT:
3
---
# 样例2
INPUT:
10 20
OUTPUT:
30
```

* 解析说明：读取文件，按 `---` 切分样例；每个样例提取 `INPUT:` 到 `OUTPUT:` 的文本（包含换行），比较程序 stdout 完全一致（注意末尾换行规范）。

### 2.4 metadata.json（可选，推荐）

用于记录每题的元数据，方便批量统计/排序。

```json
{
  "name": "两数之和",
  "difficulty": "easy",
  "tags": ["math", "基础"],
  "order": 1
}
```

---

## 3. 判题模块（Detection）详解

### 3.1 功能概述

* 对每个练习目录执行：编译 → 运行若干样例 → 比对输出 → 返回结果（通过/失败/编译错误/运行时错误/超时）。
* 支持两种判题驱动：

  * 自动触发（保存文件时）
  * 命令触发（`CStudy check`：批量判题）

### 3.2 技术细节（实现步骤）

1. **准备阶段**

   * 复制 `Ques.c` 到临时目录（如 `Detection/temp/{chapter}_{exercise}/Ques.c`）以避免改动源文件。
   * 若存在 `Test.c`（自带 harness），优先使用 `Test.c`（需约定 `Test.c` 如何包含/编译 Ques.c）。
2. **编译**

   * 命令：`gcc -std=c11 -O2 -Wall -Wextra -o temp_exec Ques.c`
   * 捕获 stderr/stdout 并保存日志。
   * 如果编译失败，返回 `compile_error` 和错误信息；不要继续运行。
3. **运行**

   * 对每个样例：

     * 将 `INPUT` 写入到临时 stdin 文件。
     * 执行：`./temp_exec < tmp_input` 并捕获 stdout/stderr。
     * 设置运行超时（建议：2 秒/样例或可配置）。
     * 限制资源：在 Windows 上可尝试限制进程优先级和内存（如使用 Job objects 或者在 MinGW 环境下做近似处理）；若在 WSL/WSL2 下，能更好限制。
     * 捕获退出码、标准输出、标准错误、是否超时。
4. **比对**

   * 对比规则：**严格字节对字节**比对 stdout 与 `OUTPUT:` 文本（建议在比对前统一处理行尾：都替换为 `\n`，但不删除额外空白，除非题目说明允许）。
   * 若不一致：

     * 返回失败样例细节：期望输出、实际输出、样例输入、差异（显示前后若干行）。
5. **结果返回**

   * 单题返回结构化结果（JSON）：

```json
{
  "path":"Exercises/Chapter1/Exercise1",
  "compile_ok": true,
  "compile_error": "",
  "cases": [
    {
      "name":"样例1",
      "passed": true,
      "expected":"...",
      "actual":"...",
      "time_ms": 12,
      "exit_code": 0
    },
    ...
  ],
  "overall": "passed" // or "failed" / "compile_error" / "runtime_error"
}
```

### 3.3 自动触发策略（文件保存）

* 在 PowerShell 环境中可以监听文件修改（`Register-ObjectEvent` 或轮询文件 mtime）：

  * 触发条件：保存 `Ques.c` 时（mtime 更新），自动运行单题判题流程。
  * 输出：把结果打印到当前控制台，若通过询问“是否跳转到下一题？（y/n）”。

### 3.4 边界与安全

* **超时**：每个样例默认 2 秒（可配置）；整个题目总时长也可设置（例如 10 秒）。
* **内存**：不能无限制；建议对进程设置最大内存（Windows 下可能需要额外原生 API，先做软限制并记录若超出则判为 runtime_error）。
* **无限循环/阻塞**：超时处理终止子进程并标记为超时。
* **文件系统/权限**：运行程序不得访问系统关键目录（建议在 temp 工作目录执行），不能允许网络访问（若能控制网络访问，则在进行评测时禁网）。
* **日志**：每次判题记录 `Detection/logs/YYYYMMDD_HHMMSS_{exercise}.log`。

---

## 4. AIserver 模块详解（本地模型 + 提示词）

### 4.1 功能定位

* 使用 `ollama` 管理本地模型（`gpt-oss:20b` 为既定默认，但 UI 提供其它模型选择：`deepseek-coder-v2:16b`、`codellama:13b`、`codegemma:7b`）。
* 当用户在控制台输入 `help me` 时，收集上下文（`description.md` + 当前 `Ques.c`），拼接提示词发送给本地模型，返回并展示建议/修复方案。
* 提供 `CStudy AI` 命令用于管理（启用、停用、列出模型、切换、删除）。

### 4.2 模型管理流程（细化）

* 首次启动或用户选择启用 AI：

  * 提示：是否开启 AI？（y/n）
  * 若选择 y：

    * 检查 `ollama` 是否安装（`ollama --version`）；若未安装，提示用户手动安装并给出命令说明（脚本不能自动安装系统级工具）。
    * 列出推荐模型供用户选择（或默认 `gpt-oss:20b`）。
    * 下载模型：`ollama pull <model>` 或 `ollama run <model>`（根据 ollama 参数）。
    * 将模型存放在 `AIserver/model/`（或 ollama 的默认存储）；记录到 `AIserver/state.json`（已启用模型信息）。
    * 启动模型服务（如需）：`ollama run <model> --detach`（视 ollama 提供的运行方式）。
* 停用：停止模型服务（`ollama stop` 或 `ollama rm` 具体命令视 ollama 版本）。
* 切换模型：

  * 提示是否删除旧模型文件（若选择删除则运行 `ollama rm <old>` 并 `ollama pull <new>`）。
* 列表显示：`CStudy AI list` 显示本地已下载模型与运行状态。

### 4.3 AI 提示词（Prompt）模板（核心）

> 目的是给出标准化、结构化、尽量包含有助解决问题的上下文的 prompt。

#### 4.3.1 基础交互模板（给模型的完整输入）

````text
请基于以下题目描述与用户当前代码，帮助分析问题、指出错误并提供修改建议与最终可编译的代码片段。
要求：
1) 简明列出可能的错误原因（最多 5 条）。
2) 给出修复后的最小化可编译 C 代码（仅包含必要修改）。
3) 如果需要，给出优化建议与复杂度说明。
4) 输出格式使用 JSON：
{
  "analysis": "...",
  "suggested_code": "```c\n...\n```",
  "explanation": "..."
}

题目描述：
[插入 description.md 的全部文本]

用户当前代码（Ques.c）：
[插入 Ques.c 的全部文本]

测试样例（Test.txt）：
[插入 Test.txt 内容]
````

#### 4.3.2 若需要更加结构化（带辅助标签）

* 在提示词中包含 `compile_flags`（如 `-std=c11 -O2`）、`time_limit_ms`、`max_output_lines` 等参数，以便模型生成符合运行环境的代码。

### 4.4 AI 输出处理

* 接收模型返回的文本（可能包含代码块），解析 JSON 或从自由文本中提取代码段。
* 展示给用户：先显示 `analysis` 段，随后以可点击/复制的方式显示 `suggested_code`。
* 如果模型返回了可执行 patch，提供 option（y/n）让用户选择是否将该代码写回 `Ques.c`（写回前备份旧文件）。

---

## 5. 主流程与交互（状态机）

### 5.1 启动（`./CStudy` 或 `CStudy.ps1`）

* 创建一个新控制台（PowerShell `Start-Process powershell -ArgumentList "-NoExit -File CStudy.ps1"` 或 `Start-Process -FilePath "powershell"` 并传参），在新控制台中进入交互模式。
* 首次打印 ASCII 欢迎横幅（你给的那段 ASCII），随后打印欢迎语与当前练习进度条（样式仿 rustlings）：

  * 进度条格式示例：`[===*******] 3/10`（已完成/总题数）
  * 显示下一题的路径（绝对或相对路径），若支持终端点击则尽量使路径以可识别格式显示。
* 打印帮助提示：

  ```text
  命令：
    check   - 检查所有练习
    list    - 列出所有练习及状态
    AI      - 管理 AI 服务（启用/禁用/更换模型）
    help me - 获取 AI 辅助（仅在题目目录下有效）
    quit    - 退出 CStudy
  请输入命令：
  ```

### 5.2 状态机（简要）

* 主界面（等待命令） → `list` → list 界面（回车回主界面或点击路径进入单题练习）
* 主界面 → `check` → check 界面（批量判题、显示结果；回车回主界面或点击未通过题进入单题练习）
* 主界面 → `AI` → AI 管理界面（启用/禁用/切换/列出）
* 主界面 → 用户点击/输入进入单题 → 单题界面（显示 description、Ques.c 路径、自动运行判题，询问是否下一题）
* 单题保存触发自动判题（并刷新单题界面）
* 任何界面接受 `help me`（若在题目上下文中），触发 AI 辅助

### 5.3 list 子界面行为细化

* 分页或逐章打印，每题一行格式：

  ```text
  1. [题目名称] - 状态：[未完成] 路径：Exercises/Chapter1/Exercise1/Ques.c
  ```

* 可通过按 Enter 返回主界面。点击路径时：打开外部编辑器（默认用 `notepad.exe` 或由环境变量 `EDITOR` 指定）打开 `Ques.c`。

### 5.4 check 子界面行为细化

* 遍历 Exercises（支持排序：章节名、metadata.order）
* 若遇到题目包含 `NOWEB` 前缀则跳过或特殊处理（根据原文档需求）
* 每题打印：路径 → 编译结果 → 每个样例结果 → 总结。
* 最终给出汇总：未完成题目路径列表 或 恭喜完成所有题目。
* 在输出中，未通过题目路径应以可点击格式展现。

### 5.5 单题界面行为（打开 Ques.c）

* 打开编辑器后返回控制台，界面持续监听该 `Ques.c` 的保存事件；保存触发判题并在控制台显示最新结果。
* 判题通过后提示：是否跳转至下一题？（y/n）

  * y：加载同章下一个练习（若最后一题则提示已完成所有练习）。
  * n：停留当前题。

---

## 6. PowerShell 实现细节（关键点）

### 6.1 新控制台创建

* 使用 `Start-Process` 启动一个新的 PowerShell 进程并执行 `CStudy.ps1` 的交互主循环，保证主控制台不会阻塞。
* 例如：

```powershell
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "C:\path\to\CStudy.ps1"
```

### 6.2 控制台刷新与编码

* 每次界面切换使用 `Clear-Host` 清屏并重新绘制页面（清除历史输出）。
* 设置编码：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
```

* PowerShell 写文件时使用 `Out-File -Encoding utf8` 或 `Set-Content -Encoding UTF8`.

### 6.3 可点击路径

* 终端可点击性依赖于终端程序（Windows Terminal/VSCode Terminal 支持路径点击）。建议在路径前后加上尖括号或 `file://` URI：

  * `file://C:/path/to/Exercises/Chapter1/Exercise1/Ques.c`

### 6.4 进程管理（判题时启动外部程序）

* 启动 `gcc` 与可执行文件时使用 `Start-Process -NoNewWindow -Wait -FilePath` 或 `&` 调用，把 stdout/stderr 重定向到临时文件，以便解析。

### 6.5 文件监控（自动判题触发）

* 可使用 `Register-ObjectEvent` 或简单轮询（定期检查文件 `LastWriteTime`）：

```powershell
$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = "C:\path\to\Exercises\Chapter1\Exercise1"
$fsw.Filter = "Ques.c"
$fsw.EnableRaisingEvents = $true
Register-ObjectEvent $fsw Changed -Action { # 调用判题函数 }
```

---

## 7. 日志、错误处理、返回码规范

### 7.1 日志文件

* 位置：`Detection/logs/` 与 `AIserver/logs/`
* 命名：`YYYYMMDD_HHMMSS_{module}_{exercise}.log`
* 内容必须包含：时间戳、操作类型（compile/run/pull-model）、执行命令、stdout、stderr、返回码。

### 7.2 返回码约定（脚本级）

* `0`：成功（所有题目/操作成功）
* `1`：通用错误（未指定）
* `2`：编译错误
* `3`：判题失败（至少有一个样例未通过）
* `4`：运行时错误/超时
* `5`：AI 服务错误（如模型未安装）
* `100+`：内部异常（日志中应记录更详细错误）

### 7.3 控制台错误信息样式

* 编译错误示例：

```text
[Compile Error] Exercises/Chapter1/Exercise1/Ques.c
gcc: error: ...
请修复后保存以重新判题。
```

* 判题失败示例：

```text
[Failed] Exercises/Chapter1/Exercise1
样例 1:
  输入:
    1 2
  期望输出:
    3
  实际输出:
    2
```

---

## 8. 测试文件与清理规则（你的第5节要求）

* **测试时临时文件**（可执行文件、临时输入输出、临时日志）均放在 `Detection/temp/{timestamp}_{exercise}/`。
* **测试结束**：判题完成后删除该 temp 目录（除非 dev 模式开启用于调试）。生产默认清除，记录清除日志。
* **不要删除 Exercises 中的源文件或用户代码**。测试清理仅影响临时 artifacts。
* **保留日志**：日志可以长期保存，或按策略（保留 30 天）清理。

---

## 9. 给 AI 编辑器 / 代码生成器 的提示词与实现指南（Execution-ready prompts）

下面提供 **一组结构化 prompt 模板**，AI 编辑器（或自动代码生成器）收到后应能生成 PowerShell 脚本、判题脚本、以及 README 文档。

### 9.1 生成 `CStudy.ps1` 主脚本 的提示词

```text
任务：生成 Windows PowerShell 脚本 CStudy.ps1，实现交互式 CLI 的主循环，功能包括：
- 启动新控制台并进入交互界面（欢迎横幅、进度条）。
- 支持命令：check、list、AI、help me、quit。
- 支持打开 Ques.c（使用 EDITOR env 或 notepad.exe）。
- 与 Detection 模块交互（调用 detect.ps1）。
编码：PowerShell，输出编码 UTF-8。
请生成注释明确、模块化的脚本，并包含用于单元测试的示例函数。
```

### 9.2 生成 `detect.ps1`（判题脚本） 的提示词

```text
任务：生成 detect.ps1，用于对单个练习目录进行判题，输入参数为练习路径（例如 Exercises/Chapter1/Exercise1）。
要求：
- 从 Test.txt 读取多个样例（规范在 prompt 中提供）。
- 编译 Ques.c（使用 gcc -std=c11）。
- 对每个样例运行可执行程序并比较输出。
- 支持超时（2s/样例）和记录日志到 Detection/logs。
- 输出 JSON 格式结果。
```

### 9.3 生成 AI 管理脚本 `ai_manager.ps1` 的提示词

```text
任务：生成 ai_manager.ps1 管理 ollama 模型：list/pull/run/stop/delete。
要求：
- 提供函数：IsOllamaInstalled, ListModels, PullModel, RunModel, StopModel, DeleteModel。
- 与 CStudy 主流程可交互（返回状态码与 descriptive message）。
- 日志记录至 AIserver/logs。
```

### 9.4 生成 README/文档 提示词

```text
任务：生成 README.md，包含安装步骤（gcc、ollama）、如何运行 CStudy、常见问题排错、以及文件/测试格式示例。
语言：中文
```

---

## 10. 验收标准（Acceptance Criteria）与示例测试用例

### 10.1 验收标准（必须满足）

1. 主脚本 `CStudy.ps1` 能在 Windows Terminal 启动并显示欢迎横幅与进度条（UTF-8 无乱码）。
2. `CStudy list` 能列出所有题目，并显示题目状态、路径（点击可用）。
3. `CStudy check` 能遍历 Exercises 并对每题返回结构化结果（compile/run/cases）。
4. 单题页面监听 `Ques.c` 保存事件并自动触发判题；判题通过后可选择跳转下一题。
5. AI 管理界面能够检测 `ollama` 安装状态、列出模型、拉取并启动模型（若用户允许）。
6. `help me` 能把 `description.md` + `Ques.c` + `Test.txt` 组织成标准 prompt 调用本地模型并把结果格式化返回。
7. 判题过程对临时文件进行清理、生成日志并返回合适的退出码。

### 10.2 示例测试用例（手动执行）

* 测试 1：有语法错误的 Ques.c → `check` 或 自动触发 时应返回 `compile_error` 且展示 gcc 错误信息。
* 测试 2：通过编译但输出不一致 → 返回失败样例详情。
* 测试 3：超时（在 Ques.c 中写无限循环） → 返回超时的样例标记，并杀死进程。
* 测试 4：AI 管理：在无 ollama 时选择启用 AI → 脚本应提示并指示安装方法（不自动安装）。
* 测试 5：保存 Ques.c 后自动判题并在通过后提示“是否跳转下一题”。

---

## 11. 安全、资源限制与未来扩展建议

* 在判题执行层面加入更严格的沙箱（如使用 WSL/容器/虚拟化运行被测程序），避免任意代码影响宿主系统。
* 为大模型（20B 等）提供异步管理（模型下载/更新由 `CStudy AI` 命令触发，UI 显示下载进度）。
* 提供 CI 配置（GitHub Actions）以验证脚本在 Windows runner 上的可执行性（或使用 Windows Server 2019/2022 runner）。
* 支持多人共享题库（git-submodule）与版本管理（题目更新时自动提示）。
* 为提高判题灵活性，后续可支持模糊匹配（忽略行尾空格）、自定义 judge 程序（Test.c 作为 harness）。

---

## 附：关键示例（快速参考）

### Test.txt 示例（标准）

```text
INPUT:
3 4
OUTPUT:
7
---
INPUT:
10 20
OUTPUT:
30
```

### description.md 示例（标准）

```markdown
# 两数之和

给定两个整数，输出它们的和。

## 输入
一行，包含两个整数，用空格隔开。

## 输出
一行，输出两个数的和。

## 示例
输入：
3 4
输出：
7
```

### AI Prompt 简短示例（发送给模型）

```text
请基于以下题目与代码帮助修复：
题目：<description.md 内容>
代码：<Ques.c 内容>
测试样例：<Test.txt 内容>
请给出 JSON 格式响应，字段：analysis, suggested_code, explanation
```

---

## 开发者清单（Quick Implementation Checklist）

* [ ] 确认开发环境：Windows + PowerShell、gcc 可用、ollama 可选。
* [ ] 搭建目录结构（按规范）。
* [ ] 编写 `detect.ps1`（判题核心、日志、超时、返回 JSON）。
* [ ] 编写 `CStudy.ps1`（主 UI、命令解析、文件监控、调用 detect）。
* [ ] 编写 `ai_manager.ps1`（ollama 管理逻辑）。
* [ ] 编写 README、示例题目（至少 3 道题用于测试）。
* [ ] 进行端到端测试（保存触发、批量 check、AI 辅助）。
* [ ] 完成清理脚本、日志轮转、并编写部署说明。
