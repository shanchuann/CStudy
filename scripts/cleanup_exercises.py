#!/usr/bin/env python3
"""Remove exercise directories that have no authoring spec.

Expected set = every spec dir under output/specs/<chapter>/<slug> plus
00-introduction/compile-run. Dry run by default.

Usage: py scripts/cleanup_exercises.py [--apply]
"""
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = ROOT / "Exercises"
SPECS = ROOT / "output" / "specs"
KEEP = {"00-introduction/compile-run"}


def main():
    apply = "--apply" in sys.argv
    expected = set(KEEP)
    for spec in SPECS.glob("*/*"):
        if (spec / "spec.json").is_file():
            expected.add(spec.relative_to(SPECS).as_posix())
    actual = set()
    for directory in EXERCISES.rglob("*"):
        if directory.is_dir() and (directory / "Ques.c").exists():
            actual.add(directory.relative_to(EXERCISES).as_posix())
    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    print("expected %d, found %d, extra %d, missing %d" % (len(expected), len(actual), len(extra), len(missing)))
    for item in missing:
        print("  MISSING " + item)
    for item in extra:
        print("  REMOVE  " + item)
    if not apply:
        print("(dry run; pass --apply to delete)")
        return 1 if missing else 0
    for item in extra:
        target = (EXERCISES / item).resolve()
        try:
            target.relative_to(EXERCISES.resolve())
        except ValueError:
            print("refusing to delete outside Exercises: " + str(target))
            return 1
        shutil.rmtree(target)
    # prune empty directories left behind
    for directory in sorted(EXERCISES.rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    print("removed %d exercise directories" % len(extra))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
