# 题目编写规范

## 章节结构

题库按《C语言圣经》的章节编号组织，目录前缀与课程章节号一致：

```text
Exercises/00-introduction/compile-run/   # 第 0 题，对应第 1 章引言
Exercises/02-basics/hello/               # 第 2 章 C 语言基础
Exercises/27-student-project/gradebook/  # 第 27 章学生成绩管理系统
```

章节清单在 `book/curriculum.json`，章节到题目的映射在 `book/exercise-map.json`。
第 28 章“下一步学习方向”和第 29 章“附件与速查”不设练习，因此不出现在章节清单中。
一个章节可以有多道练习，同一章节内按 `metadata.json` 的 `order` 排序；`order` 在所有题目中必须唯一。

## 文件要求

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

## 批量生成与校验

题目的**源文件**（题面、初始代码、参考解、用例）放在 `output/specs/<章节>/<题目>/`，
它被 `.gitignore` 忽略——因为里面包含参考解，不应随仓库发布。
用 `scripts/` 下的脚本生成 `Exercises/` 里的交付文件并校验：

```bash
# 1. 由 spec 生成 description.md / Ques.c / Ques.c.bak / Test.txt / metadata.json
python scripts/build_exercise.py output/specs/02-basics/hello

# 2. 用 cstudy 自己的判题逻辑复核全部题目（参考解必须全部通过，初始代码必须至少失败一个用例）
python scripts/verify_exercises.py            # 也可只验某章：verify_exercises.py 02-basics

# 3. 由 book/curriculum.json 与 Exercises/ 重新生成章节映射
python scripts/generate_exercise_map.py

# 4. 清理没有 spec 的题目目录（默认只打印，--apply 才删除）
python scripts/cleanup_exercises.py
```

`Test.txt` 的期望输出不是手写的，而是构建脚本运行参考解后生成的，因此示例、测试与判题标准三者天然一致。
`build_exercise.py` 还会检查：参考解可编译且全部用例通过、初始代码可编译且至少一个用例失败（否则题目过于简单）。

## 新建题目

```bash
py scripts/new_exercise.py 08-arrays/rotate-k --title "三次翻转循环左移" --tags arrays,reverse
```

脚本在 `output/specs/<章节>/<题目>/` 生成 `spec.json`（自动分配该章第一个空闲 `order`）、
`statement.md`、`starter.c`、`solution.c` 骨架；填写后按上一节的两条命令构建与校验。

## Test.txt 转义

如果某个用例的**输入或期望输出**本身就是标记行（`INPUT:`、`OUTPUT:`、`ARGS:`、`---`），
在前面加一个反斜杠即可，解析时会去掉：

```text
INPUT:
\INPUT:
OUTPUT:
\OUTPUT:
```

上例的输入是字面量 `INPUT:`，期望输出是字面量 `OUTPUT:`。其余行不受影响。

## 退出码

`0` 表示通过，`1` 表示判题失败或无效题目，`2` 表示命令参数错误，`4` 表示运行环境不可用或 AI 超时。`--json` 输出可供 CI 和编辑器集成消费的结果。
