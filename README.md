# CStudy - 脚本驱动的 C 语言学习平台

CStudy 是一个跨平台、脚本驱动、类 rustlings 的 C 语言学习平台。它通过命令行提供题目列表、自动判题、AI 辅助、进度展示与一键重置等功能，支持 Windows PowerShell/WSL 及 Bash。
> 注：powershell版本为正常使用版本，bash版本是由spec-kit开发的原始版本,开发过程已上传至[个人网站](https://www.shanchuann.cn/2025/10/18/spec-kit/)

## 特色功能

- 跨平台 CLI：PowerShell 主体验（`scripts/cstudy.ps1`），附带 Bash 版本（`scripts/cstudy.sh`）
- 动态题库：`Exercises/` 下每题一个目录（如 `ex1/`），含 `Ques.c`、`description.md`、`Test.txt`
- 自动判题：解析 `Test.txt` 的 INPUT/OUTPUT/--- 分组并比对运行结果
- 进度展示：在主界面显示整体进度并自动聚焦第一个未完成题
- AI 辅助：集成本地 `ollama` 模型，一键“help me”生成参考解
- 模型管理：在 CLI 内进行 list / download / switch / remove，默认模型持久化
- 一键重置：清理完成标记并从 `Ques.c.bak` 恢复初始代码

## 目录结构

```text
CStudy/
├─ scripts/                # CLI 与通用脚本
│  ├─ cstudy.ps1           # PowerShell 主入口
│  ├─ cstudy.sh            # Bash 入口
│  ├─ reset.ps1            # 重置工具（还原 Ques.c）
│  └─ common/
│     ├─ judge.ps1         # 判题
│     ├─ list_exercises.ps1# 列出题目
│     ├─ ai_helper.ps1     # AI 辅助（调用 ollama）
│     └─ ...
├─ Exercises/              # 练习目录（每题一个子目录）
│  └─ ex1/
│     ├─ Ques.c            # 作答文件
│     ├─ Ques.c.bak        # 初始备份
│     ├─ description.md    # 题目描述
│     └─ Test.txt          # 测试用例（INPUT/OUTPUT/---）
├─ AIserver/
│  ├─ ai_enabled.txt       # AI 开关配置
│  └─ model/
│     └─ default-model.txt # 默认模型名称
├─ docs/
│  └─ PROJECT_DESCRIPTION.md# 简明项目描述
└─ ...
```

## 快速开始（PowerShell / Windows）

1. 打开 PowerShell，进入项目根目录
2. 运行主脚本

   ```powershell
   scripts/cstudy.ps1
   ```

3. 首次使用可选择是否启用 AI：
   - 启用：确保本机已安装 `ollama`(访问官网：<https://ollama.com/download>)
   - 默认模型文件位于 `AIserver/model/default-model.txt`

## 命令说明

- check：检测当前界面所示的练习
- check all：检测所有练习
- list：显示题目列表与完成情况
- AI：打开 AI 模型管理（list / download / switch / remove）
- help me：选择练习后调用本地模型生成参考代码
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

判题器将依次编译运行并严格按行比对输出。

## AI 辅助

- 依赖本地 `ollama`，模型名称保存在 `AIserver/model/default-model.txt`
- `help me` 会将题目描述、当前代码与测试用例构造成 Prompt，只要求输出 `<<CODE>>...<<END>>` 之间的 C 代码
- 若模型输出为空或异常，脚本会给出提示，建议切换至 `codegemma:2b`、`qwen2.5-coder:7b` 或 `deepseek-coder:6.7b`

## 重置与备份

- 每个练习目录可维护 `Ques.c.bak` 作为初始备份
- 执行 `reset`：
  - 删除所有 `done.flag`
  - 用 `Ques.c.bak` 覆盖 `Ques.c`（若存在）
  - 清理残留 `.exe`

## 常见问题

- 判题失败但无输出：检查是否存在 `Test.txt` 且格式正确；确认代码能成功编译
- AI 无响应或输出不完整：优先选择体量较小的本地模型；或在 AI 菜单 `download` 拉取合适模型
- 未显示“运行结果”：若 `Test.txt` 无 INPUT 段，则直接运行程序的默认输出

## 许可证

本项目基于 MIT 许可证开源，允许个人或商业场景下的使用、修改与分发，详见LICENSE.txt文件。

