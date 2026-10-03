#!/usr/bin/env python3
"""Regenerate book/exercise-map.json from book/curriculum.json and Exercises/.

Usage: py scripts/generate_exercise_map.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = ROOT / "Exercises"
CURRICULUM = ROOT / "book" / "curriculum.json"
EXERCISE_MAP = ROOT / "book" / "exercise-map.json"


def prefix_for(number):
    return "00" if number == 1 else "%02d" % number


def exercise_id(directory):
    return directory.relative_to(EXERCISES).as_posix()


def main():
    curriculum = json.loads(CURRICULUM.read_text(encoding="utf-8"))
    chapters = curriculum.get("chapters", [])
    by_prefix = {}
    for directory in sorted(EXERCISES.rglob("*")):
        if not directory.is_dir() or not (directory / "Ques.c").exists():
            continue
        prefix = exercise_id(directory).split("-", 1)[0]
        by_prefix.setdefault(prefix, []).append(directory)

    mapping = {}
    problems = []
    for number, chapter in enumerate(chapters, 1):
        prefix = prefix_for(number)
        items = by_prefix.get(prefix, [])
        if not items:
            problems.append("chapter %s (%s) has no exercises with prefix %s"
                            % (chapter["id"], chapter["title"], prefix))
            continue
        def order_of(path):
            try:
                value = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
                return int(value.get("order", 0) or 0)
            except Exception:
                return 0
        items = sorted(items, key=lambda p: (order_of(p), exercise_id(p)))
        mapping[chapter["id"]] = [exercise_id(p) for p in items]

    if problems:
        for item in problems:
            print("ERROR: " + item)
        return 1

    lines = ["{"]
    keys = list(mapping.keys())
    for index, key in enumerate(keys):
        value = json.dumps(mapping[key], ensure_ascii=False)
        comma = "," if index < len(keys) - 1 else ""
        lines.append('  %s: %s%s' % (json.dumps(key, ensure_ascii=False), value, comma))
    lines.append("}")
    EXERCISE_MAP.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    total = sum(len(v) for v in mapping.values())
    print("wrote %s: %d chapters, %d exercises" % (EXERCISE_MAP.relative_to(ROOT), len(mapping), total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
