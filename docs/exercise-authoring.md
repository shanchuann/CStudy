# 题目编写规范

题目目录可以放在 `Exercises/` 任意深度。发现器要求至少存在 `Ques.c`、`Ques.c.bak`、`description.md` 和 `Test.txt`；`metadata.json` 用于排序和展示。

```json
{
  "title": "数组最大值",
  "difficulty": "medium",
  "tags": ["arrays", "loops"],
  "order": 300,
  "status": "active"
}
```

`status` 可为 `active`、`hidden` 或 `disabled`。题目排序首先使用 `order`，然后使用相对路径。测试文件由可选的 `ARGS:`、`INPUT:`、`OUTPUT:` 和 `---` 分隔，可以包含空输入、多行输入和命令行参数。

判题程序会复制源文件到临时目录，再使用 C11、`-Wall -Wextra -O2` 编译。程序 stdout/stderr 超过配置上限或超过单用例/整题时间限制时失败。当前是本地轻量隔离，不能替代容器或操作系统级沙箱。

Unix 运行器还会设置 CPU 时间和约 512 MiB 地址空间软限制；Windows 使用独立进程组，并在超时后通过 `taskkill /T` 终止子进程树。不同操作系统对资源限制的支持存在差异，判题结果仍以超时、退出码和输出限制为最终依据。

## 退出码

`0` 表示通过，`1` 表示判题失败或无效题目，`2` 表示命令参数错误，`4` 表示运行环境不可用或 AI 超时。`--json` 输出可供 CI 和编辑器集成消费的结果。
