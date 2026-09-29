# CStudy Upgrade Tasks

本任务清单对应当前实现。根目录 `cstudy.py` 是唯一核心；PowerShell、Bash
入口只负责转发，题目与测试通过 `Exercises/` 动态发现。

## 已完成

- [x] 建立 Windows、WSL/Linux、macOS 共用的 CLI 入口。
- [x] 实现 `list`、`curriculum`、`run`、`check`、`watch`、`next`、`prev`、`edit`、`skip`、`status`、`validate`、`doctor`、`reset`、`ai`。
- [x] 支持章节题库、元数据、隐藏/禁用题目、课程映射和固定排序。
- [x] 实现 C11 编译、多测试用例、临时目录、超时、输出上限、进程终止和资源限制。
- [x] 实现状态文件、结果日志、JSON 输出和非交互 CI 模式。
- [x] AI 改为可选的 OpenAI-compatible API，支持 Chat Completions 与 Responses。
- [x] 建立 29 个章节、33 道练习的课程题库；`00-introduction/compile-run` 为第 0 题。
- [x] 建立 Python 单元测试与 Windows/Linux/macOS GitHub Actions 验证。

## 维护约束

- 新题必须包含 `description.md`、`Ques.c`、`Ques.c.bak`、`Test.txt`、`metadata.json`。
- 新题加入后运行 `cstudy validate --compile`。
- 判题逻辑只在 `cstudy.py` 中维护，不再新增独立判题脚本。
- API 密钥只通过环境变量提供，不写入题目、日志或配置示例。
