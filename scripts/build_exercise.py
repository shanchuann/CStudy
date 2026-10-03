#!/usr/bin/env python3
"""Build one CStudy exercise from an authoring spec directory.

Usage:  py scripts/build_exercise.py output/specs/<chapter>/<slug>

Spec directory files:
  spec.json     metadata + cases
  statement.md  problem statement (no level-1 heading)
  starter.c     initial Ques.c content (must contain "// Done")
  solution.c    reference solution (used to generate expected outputs)
  other .c/.h   extra files for multi-file exercises

spec.json fields:
  dir, title, difficulty, tags, order, cases  (required)
  knowledge[], hints[], examples[], sources[] optional
  starter_files / solution_files: {name: relative-file}
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = ROOT / "Exercises"
#: Authoring scratch (gitignored): specs hold reference solutions, so they never
#: ship in the repository; refs are the solutions copied out for verification.
REFS = ROOT / "output" / "refs"
CC = os.environ.get("CC", "gcc")
FENCE = chr(96) * 3
MARKERS = ("INPUT:", "OUTPUT:", "ARGS:", "---")


def norm(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def compile_files(files, work):
    work.mkdir(parents=True, exist_ok=True)
    names = []
    for name, src in files.items():
        src = Path(src)
        if not src.is_file():
            fail("missing source file: " + str(src))
        shutil.copyfile(src, work / name)
        names.append(name)
    exe = work / ("prog.exe" if os.name == "nt" else "prog")
    cmd = [CC, "-std=c11", "-Wall", "-Wextra", "-O2", *names, "-o", str(exe)]
    proc = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True)
    return proc, exe


def run_case(exe, case, work):
    inp = case.get("input", "") or ""
    args = [str(a) for a in case.get("args", [])]
    return subprocess.run([str(exe), *args], cwd=str(work),
                          input=(inp + "\n") if inp else "",
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=30)


def render_case(case, expected):
    lines = []
    if case.get("args"):
        lines.append("ARGS: " + " ".join(str(a) for a in case["args"]))
    lines.append("INPUT:")
    if case.get("input", ""):
        lines.extend(case["input"].split("\n"))
    lines.append("OUTPUT:")
    if expected:
        lines.extend(expected.split("\n"))
    return "\n".join(lines)


def fence(text):
    return FENCE + "text\n" + text + "\n" + FENCE


def main():
    if len(sys.argv) != 2:
        fail("usage: build_exercise.py <spec-dir>")
    spec_dir = Path(sys.argv[1]).resolve()
    spec = json.loads((spec_dir / "spec.json").read_text(encoding="utf-8"))
    for key in ("dir", "title", "difficulty", "tags", "order", "cases"):
        if key not in spec:
            fail("spec.json missing field: " + key)
    cases = spec["cases"]
    if not cases:
        fail("spec.json has no cases")
    for i, case in enumerate(cases):
        for line in (case.get("input", "") or "").split("\n"):
            if line.strip() in MARKERS:
                fail("case %d input line collides with Test.txt marker: %r" % (i, line))
        if case.get("input", "").endswith("\n"):
            fail("case %d input must not end with a newline" % i)

    statement = (spec_dir / "statement.md").read_text(encoding="utf-8").strip()
    if statement.startswith("# "):
        statement = statement.split("\n", 1)[1].strip()
    starter_files = {name: str((spec_dir / src).resolve())
                     for name, src in (spec.get("starter_files") or {"Ques.c": "starter.c"}).items()}
    solution_files = {name: str((spec_dir / src).resolve())
                      for name, src in (spec.get("solution_files") or {"Ques.c": "solution.c"}).items()}
    target = EXERCISES / spec["dir"]
    target.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cstudy-build-") as tmp_name:
        tmp = Path(tmp_name)
        sol_proc, sol_exe = compile_files(solution_files, tmp / "sol")
        if sol_proc.returncode != 0:
            fail("solution does not compile:\n" + (sol_proc.stderr or sol_proc.stdout))
        if sol_proc.stderr.strip():
            print("note: solution compiler warnings:\n" + sol_proc.stderr.strip())
        expected = []
        for i, case in enumerate(cases):
            proc = run_case(sol_exe, case, tmp / "sol")
            if proc.returncode != 0:
                fail("solution failed on case %d (exit %s):\n%s" % (i, proc.returncode, proc.stderr))
            out = norm(proc.stdout)
            for line in out.split("\n"):
                if line.strip() in MARKERS:
                    fail("case %d expected output line collides with Test.txt marker: %r" % (i, line))
            expected.append(out)

        start_proc, start_exe = compile_files(starter_files, tmp / "starter")
        if start_proc.returncode != 0:
            fail("starter does not compile:\n" + (start_proc.stderr or start_proc.stdout))
        if start_proc.stderr.strip():
            print("note: starter compiler warnings:\n" + start_proc.stderr.strip())
        passed = 0
        for i, case in enumerate(cases):
            proc = run_case(start_exe, case, tmp / "starter")
            if proc.returncode == 0 and norm(proc.stdout) == expected[i]:
                passed += 1
        if passed == len(cases):
            fail("starter already passes every case; the exercise would be trivial")

    # Test.txt
    blocks = [render_case(case, exp) for case, exp in zip(cases, expected)]
    (target / "Test.txt").write_text("\n---\n".join(blocks) + "\n", encoding="utf-8", newline="\n")

    # description.md
    example_index = spec.get("examples") or list(range(min(2, len(cases))))
    parts = ["# " + spec["title"], "", statement, "", "## 示例"]
    for n, idx in enumerate(example_index, 1):
        case, exp = cases[idx], expected[idx]
        parts.append("")
        parts.append("**示例 %d**" % n)
        parts.append("")
        if case.get("args"):
            parts.append("命令行参数：")
            parts.append("")
            parts.append(fence(" ".join(str(a) for a in case["args"])))
            parts.append("")
        if case.get("input", ""):
            parts.append("输入：")
            parts.append("")
            parts.append(fence(case["input"]))
            parts.append("")
        parts.append("输出：")
        parts.append("")
        parts.append(fence(exp))
    if spec.get("knowledge"):
        parts += ["", "## 知识点", ""] + ["- " + item for item in spec["knowledge"]]
    if spec.get("hints"):
        parts += ["", "## 提示", ""] + ["- " + item for item in spec["hints"]]
    parts.append("")
    (target / "description.md").write_text("\n".join(parts), encoding="utf-8", newline="\n")

    # Ques.c + Ques.c.bak
    ques = (spec_dir / starter_files["Ques.c"]).read_text(encoding="utf-8")
    if "// Done" not in ques:
        ques = ques.rstrip() + "\n\n// Done\n"
    (target / "Ques.c").write_text(ques, encoding="utf-8", newline="\n")
    (target / "Ques.c.bak").write_text(ques, encoding="utf-8", newline="\n")
    for name, src in starter_files.items():
        if name != "Ques.c":
            shutil.copyfile(src, target / name)

    # metadata.json
    meta = {"title": spec["title"], "difficulty": spec["difficulty"],
            "tags": spec["tags"], "order": spec["order"], "status": "active"}
    sources = spec.get("sources") or list(starter_files.keys())
    if len(sources) > 1:
        meta["sources"] = sources
    (target / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # reference copy for central verification
    ref_dir = REFS / spec["dir"].replace("/", "__")
    if ref_dir.exists():
        shutil.rmtree(ref_dir)
    ref_dir.mkdir(parents=True, exist_ok=True)
    for name, src in solution_files.items():
        shutil.copyfile(src, ref_dir / name)

    print("built %s (%d cases)" % (spec["dir"], len(cases)))


if __name__ == "__main__":
    main()
