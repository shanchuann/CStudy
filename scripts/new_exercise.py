#!/usr/bin/env python3
"""Scaffold a new exercise spec under output/specs/<chapter>/<slug>.

Usage:
  py scripts/new_exercise.py 08-arrays/rotate-k --title "三次翻转循环左移" \
      [--order 806] [--difficulty medium] [--tags arrays,reverse]

Writes spec.json / statement.md / starter.c / solution.c with TODO placeholders.
Fill them in, then run scripts/build_exercise.py to generate the delivered files
and scripts/verify_exercises.py to check the reference solution.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "output" / "specs"


def next_order(chapter: str) -> int:
    """First free order inside the chapter's number range (chapter * 100 + n)."""
    prefix = chapter.split("-", 1)[0]
    try:
        base = int(prefix) * 100
    except ValueError:
        base = 9000
    used = set()
    for spec in SPECS.glob("*/*/spec.json"):
        try:
            used.add(int(json.loads(spec.read_text(encoding="utf-8")).get("order", 0) or 0))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
    for candidate in range(base + 1, base + 100):
        if candidate not in used:
            return candidate
    return base + 100


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new CStudy exercise spec")
    parser.add_argument("path", help="chapter-dir/slug, e.g. 08-arrays/rotate-k")
    parser.add_argument("--title", required=True, help="exercise title shown in the UI")
    parser.add_argument("--order", type=int, help="sort order (default: first free in the chapter)")
    parser.add_argument("--difficulty", default="medium", choices=["intro", "easy", "medium", "hard"])
    parser.add_argument("--tags", default="", help="comma separated tags")
    args = parser.parse_args()

    parts = args.path.strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        print("path must look like <chapter-dir>/<slug>")
        return 2
    chapter, slug = parts
    target = SPECS / chapter / slug
    if target.exists():
        print(f"spec already exists: {target.relative_to(ROOT)}")
        return 1
    target.mkdir(parents=True)

    order = args.order or next_order(chapter)
    tags = [item.strip() for item in args.tags.split(",") if item.strip()]
    spec = {
        "dir": f"{chapter}/{slug}",
        "title": args.title,
        "difficulty": args.difficulty,
        "tags": tags or ["basics"],
        "order": order,
        "knowledge": ["TODO: 本章知识点一", "TODO: 本章知识点二"],
        "hints": ["TODO: 给学习者的一条提示"],
        "cases": [{"input": "TODO"}, {"input": "TODO"}],
        "examples": [0],
        "starter_files": {"Ques.c": "starter.c"},
        "solution_files": {"Ques.c": "solution.c"},
    }
    (target / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (target / "statement.md").write_text(
        "## 题目描述\n\nTODO：用两三句话说明要做什么，并点明对应的教材知识点。\n\n"
        "## 输入格式\n\nTODO\n\n## 输出格式\n\nTODO\n", encoding="utf-8", newline="\n")
    (target / "starter.c").write_text(
        "#include <stdio.h>\n\nint main(void) {\n    /* TODO: 在这里完成题目要求 */\n    return 0;\n}\n\n// Done\n",
        encoding="utf-8", newline="\n")
    (target / "solution.c").write_text(
        "#include <stdio.h>\n\nint main(void) {\n    /* TODO: 参考解 */\n    return 0;\n}\n", encoding="utf-8", newline="\n")

    relative = target.relative_to(ROOT)
    print(f"created {relative} (order {order})")
    print("next:")
    print(f"  1. 填写 {relative}/statement.md、starter.c、solution.c 与 spec.json 的 cases")
    print(f"  2. py scripts/build_exercise.py {relative}")
    print(f"  3. py scripts/verify_exercises.py {chapter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
