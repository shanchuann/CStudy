#!/usr/bin/env python3
"""Verify every exercise against its reference solution.

Uses cstudy's own Test.txt parser and output comparison, so a passing run means
the official judge would accept the reference solution too.

Usage: py scripts/verify_exercises.py [chapter-prefix ...]
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cstudy

EXERCISES = ROOT / "Exercises"
REFS = ROOT / "output" / "refs"
CC = os.environ.get("CC", "gcc")
SKIP = {"00-introduction/compile-run"}


def build(sources, work):
    work.mkdir(parents=True, exist_ok=True)
    names = []
    for path in sources:
        path = Path(path)
        shutil.copyfile(path, work / path.name)
        if path.suffix == ".c":
            names.append(path.name)
    exe = work / ("prog.exe" if os.name == "nt" else "prog")
    cmd = [CC, "-std=c11", "-Wall", "-Wextra", "-O2", *names, "-o", str(exe)]
    return subprocess.run(cmd, cwd=str(work), capture_output=True, text=True), exe


def run(exe, case, work):
    return subprocess.run([str(exe), *case.args], cwd=str(work),
                          input=(case.input + "\n") if case.input else "",
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=30)


def main():
    filters = sys.argv[1:]
    problems = []
    checked = 0
    orders = {}
    for directory in sorted(EXERCISES.rglob("*")):
        if not directory.is_dir() or not (directory / "Ques.c").exists():
            continue
        rel = directory.relative_to(EXERCISES).as_posix()
        if rel in SKIP or (filters and not any(rel.startswith(f) for f in filters)):
            continue
        checked += 1
        meta = cstudy.metadata(directory)
        order = meta.get("order", 0)
        if not isinstance(order, int) or order == 0:
            problems.append("%s: order must be a non-zero integer" % rel)
        elif order in orders:
            problems.append("%s: duplicate order %s (also %s)" % (rel, order, orders[order]))
        else:
            orders[order] = rel
        ques = directory / "Ques.c"
        bak = directory / "Ques.c.bak"
        if not bak.exists():
            problems.append("%s: missing Ques.c.bak" % rel)
        elif bak.read_bytes() != ques.read_bytes():
            problems.append("%s: Ques.c.bak differs from Ques.c" % rel)
        if "// Done" not in ques.read_text(encoding="utf-8"):
            problems.append("%s: Ques.c has no // Done marker" % rel)
        desc = directory / "description.md"
        text = desc.read_text(encoding="utf-8") if desc.exists() else ""
        for section in ("## 示例", "## 知识点", "## 提示"):
            if section not in text:
                problems.append("%s: description.md missing %s" % (rel, section))
        for name in ("metadata.json", "Test.txt"):
            if not (directory / name).exists():
                problems.append("%s: missing %s" % (rel, name))
        tests = directory / "Test.txt"
        if not tests.exists():
            continue
        cases = cstudy.parse_tests(tests)
        if not cases:
            problems.append("%s: Test.txt has no cases" % rel)
            continue
        ref_dir = REFS / rel.replace("/", "__")
        if not ref_dir.is_dir():
            problems.append("%s: no reference solution" % rel)
            continue
        with tempfile.TemporaryDirectory(prefix="cstudy-verify-") as tmp_name:
            tmp = Path(tmp_name)
            ref_sources = sorted(p for p in ref_dir.iterdir() if p.suffix in (".c", ".h"))
            proc, exe = build(ref_sources, tmp / "ref")
            if proc.returncode != 0:
                problems.append("%s: reference does not compile: %s" % (rel, proc.stderr.strip()[:300]))
                continue
            for i, case in enumerate(cases):
                result = run(exe, case, tmp / "ref")
                actual = cstudy.normalize(result.stdout)
                if result.returncode != 0:
                    problems.append("%s: case %d reference exit %s" % (rel, i, result.returncode))
                elif actual != cstudy.normalize(case.expected):
                    problems.append("%s: case %d mismatch\n  expected=%r\n  actual  =%r"
                                    % (rel, i, cstudy.normalize(case.expected), actual))
            src_names = meta.get("sources") or ["Ques.c"]
            start_sources = [directory / str(n) for n in src_names]
            proc2, exe2 = build(start_sources, tmp / "starter")
            if proc2.returncode != 0:
                problems.append("%s: starter does not compile: %s" % (rel, proc2.stderr.strip()[:300]))
                continue
            solved = 0
            for case in cases:
                result = run(exe2, case, tmp / "starter")
                if result.returncode == 0 and cstudy.normalize(result.stdout) == cstudy.normalize(case.expected):
                    solved += 1
            if solved == len(cases):
                problems.append("%s: starter already passes every case" % rel)
    print("checked %d exercises, %d problems" % (checked, len(problems)))
    for item in problems:
        print(" - " + item)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
