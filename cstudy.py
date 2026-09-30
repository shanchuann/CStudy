#!/usr/bin/env python3
"""Portable CStudy CLI shared by Windows, Linux, and macOS."""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import shutil
import signal
import shlex
import subprocess
import sys
import tempfile
import threading
import time
import platform
import queue
import contextlib
import select
import textwrap
from urllib.parse import quote, urlparse
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import resource
except ImportError:  # Windows
    resource = None

try:
    import termios
    import tty
except ImportError:  # Windows
    termios = None
    tty = None

# Terminal presentation (animation and Markdown rendering) lives in a sibling
# module so this file stays focused on the learning workflow.
_ROOT_PATH = str(Path(__file__).resolve().parent)
if _ROOT_PATH not in sys.path:
    sys.path.insert(0, _ROOT_PATH)
import console_ux

ROOT = Path(__file__).resolve().parent
EXERCISES = ROOT / "Exercises"
CURRICULUM = ROOT / "book" / "curriculum.json"
EXERCISE_MAP = ROOT / "book" / "exercise-map.json"
STATE_DIR = ROOT / ".cstudy"
STATE_FILE = STATE_DIR / "state.json"
CONFIG_FILE = STATE_DIR / "config.json"
LOG_DIR = STATE_DIR / "logs"
VERSION = "0.3.0"
EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2
_ALTERNATE_SCREEN = False
COMPLETION_MARKERS = ("// Done", "//DONE", "// I AM NOT DONE")
ANSI = {"reset": "\x1b[0m", "bold": "\x1b[1m", "green": "\x1b[32m", "red": "\x1b[31m", "yellow": "\x1b[33m", "cyan": "\x1b[36m", "dim": "\x1b[2m"}
AI_PROVIDERS = {
    "api.openai.com": ("OpenAI", "gpt-4o-mini", "chat"),
    "api.deepseek.com": ("DeepSeek", "deepseek-flash", "chat"),
    "open.bigmodel.cn": ("GLM", "glm-4-flash", "chat"),
}


def paint(value: str, colour: str) -> str:
    """Colourise one token; delegates so the CLI has a single colour table."""
    return console_ux.paint(value, colour)


@dataclass
class TestCase:
    input: str
    expected: str
    args: list[str] | None = None


@dataclass
class CaseResult:
    passed: bool
    input: str
    expected: str
    actual: str
    stderr: str
    duration_ms: int
    exit_code: int
    error: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def parse_tests(path: Path) -> list[TestCase]:
    lines = read_text(path).splitlines()
    cases: list[TestCase] = []
    inputs: list[str] = []
    outputs: list[str] = []
    arguments: list[str] = []
    mode: Optional[str] = None
    seen_case = False

    def flush() -> None:
        nonlocal inputs, outputs, arguments, mode, seen_case
        if seen_case:
            cases.append(TestCase("\n".join(inputs), "\n".join(outputs), arguments.copy()))
        inputs, outputs, arguments, mode, seen_case = [], [], [], None, False

    for raw in lines:
        marker = raw.strip()
        if marker == "INPUT:":
            if seen_case and (inputs or outputs):
                flush()
            mode, seen_case = "input", True
        elif marker == "OUTPUT:":
            mode, seen_case = "output", True
        elif marker.startswith("ARGS:"):
            arguments = shlex.split(raw.partition(":")[2].strip())
            seen_case = True
        elif marker == "---":
            flush()
        elif mode == "input":
            inputs.append(raw)
        elif mode == "output":
            outputs.append(raw)
    flush()
    return cases


def load_json(path: Path, default: dict) -> dict:
    try:
        value = json.loads(read_text(path))
        return value if isinstance(value, dict) else default.copy()
    except (OSError, json.JSONDecodeError):
        return default.copy()


def current_state() -> dict:
    state = load_json(STATE_FILE, {"version": 1, "exercises": {}, "current": None})
    state.setdefault("version", 1); state.setdefault("current", None)
    exercises = state.setdefault("exercises", {})
    if isinstance(exercises, dict):
        known = {exercise_id(item) for item in discover(include_hidden=True, include_disabled=True)}
        stale = set(exercises) - known
        if stale:
            for identifier in stale: exercises.pop(identifier, None)
            if state.get("current") in stale: state["current"] = None
            save_state(state)
    return state


def save_state(value: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def current_exercise_from_state(state: dict, exercises: Optional[list[Path]] = None) -> Optional[Path]:
    """Resolve the saved exercise, falling back to the first unfinished item."""
    exercises = exercises if exercises is not None else discover()
    identifier = state.get("current")
    if identifier:
        selected = next((item for item in exercises if exercise_id(item) == identifier), None)
        if selected is not None and not is_done(selected, state):
            return selected
    return next((item for item in exercises if not is_done(item, state)), None)


def set_current_exercise(directory: Optional[Path], state: Optional[dict] = None) -> dict:
    state = state if state is not None else current_state()
    state["current"] = exercise_id(directory) if directory is not None else None
    save_state(state)
    return state


def settings() -> dict:
    defaults = {"auto_next": False, "timeout_seconds": 2.0, "total_timeout_seconds": 10.0,
                "max_output_bytes": 1024 * 1024, "ai_model": "gpt-4o-mini",
                "ai_api_base": "https://api.openai.com/v1", "ai_api_mode": "chat"}
    value = load_json(CONFIG_FILE, defaults)
    for key, default in defaults.items():
        value.setdefault(key, default)
    return value


def save_settings(value: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        CONFIG_FILE.chmod(0o600)
    except OSError:
        pass


def ai_configuration() -> dict[str, str]:
    cfg = settings()
    return {
        "api_key": os.environ.get("CSTUDY_API_KEY") or str(cfg.get("ai_api_key", "")) or os.environ.get("OPENAI_API_KEY", ""),
        "api_base": os.environ.get("CSTUDY_API_BASE") or str(cfg.get("ai_api_base", "https://api.openai.com/v1")),
        "model": os.environ.get("CSTUDY_AI_MODEL") or str(cfg.get("ai_model", "gpt-4o-mini")),
        "mode": (os.environ.get("CSTUDY_API_MODE") or str(cfg.get("ai_api_mode", "chat"))).lower(),
    }


def print_ai_setup_help() -> None:
    print("AI is not configured. Run `cstudy ai --setup` to configure it interactively.", file=sys.stderr)
    print("You can also set CSTUDY_API_KEY, CSTUDY_API_BASE, and CSTUDY_AI_MODEL.", file=sys.stderr)
    print("Supported presets: OpenAI, DeepSeek, GLM, and other OpenAI-compatible APIs.", file=sys.stderr)


def discover_compatible_model(base_url: str, api_key: str) -> Optional[str]:
    endpoint = base_url.rstrip("/") + "/models"
    request = urllib.request.Request(endpoint, headers={"Authorization": "Bearer " + api_key,
                                                        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15.0) as response:
            body = json.loads(response.read().decode("utf-8"))
        identifiers = [str(item.get("id", "")) for item in body.get("data", [])
                       if isinstance(item, dict) and item.get("id")]
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"Could not discover models from {endpoint}: {getattr(exc, 'reason', exc)}", file=sys.stderr)
        return None
    excluded = ("embedding", "rerank", "image", "audio", "whisper", "tts")
    candidates = [item for item in identifiers if not any(word in item.lower() for word in excluded)]
    if not candidates:
        print(f"No conversational model was returned by {endpoint}.", file=sys.stderr)
        return None
    preferred = ("chat", "instruct", "flash", "turbo", "plus", "gpt", "glm", "deepseek")
    return max(candidates, key=lambda item: max((len(preferred) - index
                                                for index, word in enumerate(preferred)
                                                if word in item.lower()), default=0))


def configure_ai() -> bool:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print_ai_setup_help()
        return False
    print(paint("CStudy AI setup", "cyan"))
    default_base = str(settings().get("ai_api_base", "https://api.openai.com/v1"))
    base_url = read_line(f"API base [{default_base}]: ") or default_base
    if not base_url.startswith(("http://", "https://")):
        print("AI setup failed: API base must start with http:// or https://.", file=sys.stderr)
        return False
    base_url = base_url.rstrip("/")
    with cooked_terminal():
        api_key = getpass.getpass("API key (saved only in .cstudy/config.json): ").strip()
    if not api_key:
        print("AI setup cancelled: API key cannot be empty.", file=sys.stderr)
        return False
    host = (urlparse(base_url).hostname or "").lower()
    known = AI_PROVIDERS.get(host)
    if known:
        provider, model, requested_mode = known
    else:
        provider, requested_mode = host or "Custom", "chat"
        model = discover_compatible_model(base_url, api_key)
        if not model:
            print("AI setup failed: CStudy could not select a compatible chat model.", file=sys.stderr)
            return False
    cfg = settings()
    cfg.update({"ai_provider": provider, "ai_api_base": base_url,
                "ai_model": model, "ai_api_mode": requested_mode, "ai_api_key": api_key})
    save_settings(cfg)
    print(paint(f"AI configured: {provider} / {model}", "green"))
    print("The key is stored locally in the ignored .cstudy/config.json file.")
    return True


def exercise_id(directory: Path) -> str:
    return directory.relative_to(EXERCISES).as_posix()


def exercise_files(directory: Path) -> tuple[Optional[Path], Optional[Path]]:
    source = directory / "Ques.c"
    if not source.exists():
        source = next(iter(sorted(directory.glob("*.c"))), None)
    tests = directory / "Test.txt"
    return source, tests if tests.exists() else None


def has_completion_marker(directory: Path) -> bool:
    source, _ = exercise_files(directory)
    if source is None or not source.exists():
        return False
    return any(marker in read_text(source) for marker in COMPLETION_MARKERS)


def metadata(directory: Path) -> dict:
    value = load_json(directory / "metadata.json", {})
    title = value.get("title") or value.get("name")
    if not title:
        description = directory / "description.md"
        title = next((line[1:].strip() for line in read_text(description).splitlines()
                      if line.startswith("#")), directory.name) if description.exists() else directory.name
    value.update({"id": exercise_id(directory), "title": title,
                  "difficulty": value.get("difficulty", "unspecified"),
                  "tags": value.get("tags", []), "order": value.get("order", 0),
                  "status": value.get("status", "active")})
    return value


def discover(include_hidden: bool = False, include_disabled: bool = False) -> list[Path]:
    if not EXERCISES.exists():
        return []
    found = []
    for directory in EXERCISES.rglob("*"):
        if not directory.is_dir() or exercise_files(directory)[0] is None:
            continue
        meta = metadata(directory)
        if (meta["status"] == "disabled" and not include_disabled) or (meta["status"] == "hidden" and not include_hidden):
            continue
        found.append(directory)
    def sort_key(path: Path) -> tuple[int, int, str]:
        # The directory chapter number is the primary curriculum order. The
        # metadata order remains the stable tie-breaker for multiple exercises
        # in one chapter (for example 01-basics/hello before age).
        prefix = path.relative_to(EXERCISES).parts[0].split("-", 1)[0]
        try:
            chapter = int(prefix)
        except ValueError:
            chapter = 10**9
        return chapter, int(metadata(path).get("order", 0) or 0), exercise_id(path).lower()
    return sorted(found, key=sort_key)


def find_exercise(value: str) -> Optional[Path]:
    candidates = discover(include_hidden=True)
    exact = [p for p in candidates if exercise_id(p) == value or p.name == value]
    if value.isdigit() and 1 <= int(value) <= len(candidates):
        return candidates[int(value) - 1]
    return exact[0] if exact else None


def is_done(directory: Path, state: dict) -> bool:
    if has_completion_marker(directory):
        return False
    item = state.get("exercises", {}).get(exercise_id(directory), {})
    if item:
        return item.get("status") in {"passed", "skipped"}
    return (directory / "done.flag").exists()


def progress_status(directory: Path, state: dict) -> str:
    if has_completion_marker(directory):
        return "incomplete"
    item = state.get("exercises", {}).get(exercise_id(directory), {})
    status = item.get("status") if item else None
    if status in {"passed", "skipped"}:
        return status
    return "todo"


def compiler() -> Optional[str]:
    configured = os.environ.get("CC")
    for candidate in ([configured] if configured else []) + ["gcc", "clang"]:
        if candidate and shutil.which(candidate):
            return candidate
    return None


def terminate(process: subprocess.Popen[str]) -> None:
    try:
        if os.name == "nt":
            # /T terminates descendants as well as the direct child.
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            if process.poll() is None:
                process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except (OSError, ValueError):
        try:
            process.kill()
        except OSError:
            pass


def run_case(binary: Path, case: TestCase, timeout: float, max_output: int, cwd: Path) -> CaseResult:
    started = time.monotonic()
    stdout_path, stderr_path = cwd / "stdout.txt", cwd / "stderr.txt"
    with stdout_path.open("w+b") as stdout_file, stderr_path.open("w+b") as stderr_file:
        kwargs: dict[str, Any] = {"cwd": cwd, "stdin": subprocess.PIPE, "stdout": stdout_file,
                                  "stderr": stderr_file, "text": True}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
            # resource.preexec_fn is unreliable on macOS (and can fail after
            # fork in hosted CI). Keep process groups everywhere, and apply
            # POSIX limits only on Linux where the runner is stable.
            if resource is not None and sys.platform.startswith("linux"):
                cpu_limit = max(1, int(timeout) + 1)
                def apply_limits() -> None:
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
                    address_limit = getattr(resource, "RLIMIT_AS", None)
                    if address_limit is not None:
                        resource.setrlimit(address_limit, (512 * 1024 * 1024, 512 * 1024 * 1024))
                kwargs["preexec_fn"] = apply_limits
        try:
            process = subprocess.Popen([str(binary), *(case.args or [])], **kwargs)
        except (OSError, subprocess.SubprocessError) as exc:
            return CaseResult(False, case.input, case.expected, "", str(exc),
                              int((time.monotonic() - started) * 1000), -1, "runtime_error")
        assert process.stdin is not None
        process.stdin.write(case.input + ("\n" if case.input else ""))
        process.stdin.close()
        error = ""
        while process.poll() is None:
            elapsed = time.monotonic() - started
            if stdout_path.stat().st_size + stderr_path.stat().st_size > max_output:
                error = "output_limit"
                terminate(process)
                break
            if elapsed >= timeout:
                error = "timeout"
                terminate(process)
                break
            time.sleep(0.01)
        process.wait()
        stdout_file.flush(); stderr_file.flush()
    output = stdout_path.read_bytes()[:max_output].decode("utf-8", "replace")
    errors = stderr_path.read_bytes()[:max_output].decode("utf-8", "replace")
    if not error and process.returncode != 0:
        error = "runtime_error"
    actual, expected = normalize(output), normalize(case.expected)
    return CaseResult(not error and actual == expected, case.input, case.expected, actual, errors,
                      int((time.monotonic() - started) * 1000), process.returncode, error)


def grade(directory: Path, timeout: float, total_timeout: float, max_output: int) -> dict:
    started = time.monotonic()
    source, test_file = exercise_files(directory)
    result: dict[str, Any] = {"exercise": exercise_id(directory), "title": metadata(directory)["title"],
                              "status": "error", "compile": {}, "cases": [], "duration_ms": 0}
    if source is None or test_file is None:
        result.update(status="invalid", error="missing Ques.c or Test.txt")
        return result
    cc = compiler()
    if not cc:
        result.update(status="environment_error", error="no gcc or clang compiler found")
        return result
    cases = parse_tests(test_file)
    if not cases:
        result.update(status="invalid", error="Test.txt contains no INPUT/OUTPUT cases")
        return result
    with tempfile.TemporaryDirectory(prefix="cstudy-") as temp_name:
        temp = Path(temp_name)
        source_names = metadata(directory).get("sources", ["Ques.c"])
        if not isinstance(source_names, list) or not source_names:
            source_names = ["Ques.c"]
        compile_sources = []
        for name in source_names:
            original = (directory / str(name)).resolve()
            try:
                original.relative_to(directory.resolve())
            except ValueError:
                result.update(status="invalid", error=f"source outside exercise: {name}")
                result["duration_ms"] = int((time.monotonic() - started) * 1000)
                return result
            if not original.is_file():
                result.update(status="invalid", error=f"missing source: {name}")
                result["duration_ms"] = int((time.monotonic() - started) * 1000)
                return result
            target = temp / Path(name).name
            shutil.copyfile(original, target)
            compile_sources.append(target.name)
        binary = temp / ("solution.exe" if os.name == "nt" else "solution")
        command = [cc, "-std=c11", "-Wall", "-Wextra", "-O2", *compile_sources, "-o", str(binary)]
        try:
            # The exercise budget applies to the user's program, not compiler
            # startup.  Hosted runners can spend several seconds launching
            # gcc/clang on cold hosted runners, so keep a bounded minimum
            # compile window on every platform.
            compile_timeout = max(total_timeout, 30.0)
            compiled = subprocess.run(command, cwd=temp, text=True, capture_output=True, timeout=compile_timeout)
        except subprocess.TimeoutExpired as exc:
            result.update(status="compile_timeout", error="compiler timeout")
            result["compile"] = {"command": command, "return_code": -signal.SIGTERM,
                                  "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
            result["duration_ms"] = int((time.monotonic() - started) * 1000)
            return result
        result["compile"] = {"command": command, "return_code": compiled.returncode,
                             "stdout": compiled.stdout, "stderr": compiled.stderr}
        if compiled.returncode != 0:
            result["status"] = "compile_error"
        else:
            run_started = time.monotonic()
            for case in cases:
                remaining = total_timeout - (time.monotonic() - run_started)
                if remaining <= 0:
                    result["cases"].append(asdict(CaseResult(False, case.input, case.expected, "", "", 0,
                                                              -signal.SIGTERM, "total_timeout")))
                else:
                    result["cases"].append(asdict(run_case(binary, case, min(timeout, remaining), max_output, temp)))
            errors = {case["error"] for case in result["cases"] if case["error"]}
            if result["cases"] and all(case["passed"] for case in result["cases"]):
                result["status"] = "incomplete_marker" if has_completion_marker(directory) else "passed"
                if result["status"] == "incomplete_marker":
                    result["error"] = "remove the // Done marker after completing the exercise"
            elif errors & {"timeout", "total_timeout"}:
                result["status"] = "timeout"
            elif "output_limit" in errors:
                result["status"] = "output_limit"
            elif "runtime_error" in errors:
                result["status"] = "runtime_error"
            else:
                result["status"] = "output_mismatch"
    result["duration_ms"] = int((time.monotonic() - started) * 1000)
    return result


def compile_only(directory: Path, timeout: float) -> dict:
    """Compile an exercise without running its tests, for repository/CI checks."""
    started = time.monotonic()
    cc = compiler()
    if not cc:
        return {"status": "environment_error", "error": "no gcc or clang compiler found"}
    source_names = metadata(directory).get("sources", ["Ques.c"])
    if not isinstance(source_names, list) or not source_names:
        return {"status": "invalid", "error": "metadata sources must be a non-empty list"}
    with tempfile.TemporaryDirectory(prefix="cstudy-compile-") as temp_name:
        temp = Path(temp_name); names = []
        for name in source_names:
            original = (directory / str(name)).resolve()
            try:
                original.relative_to(directory.resolve())
            except ValueError:
                return {"status": "invalid", "error": f"source outside exercise: {name}"}
            if not original.is_file():
                return {"status": "invalid", "error": f"missing source: {name}"}
            target = temp / Path(name).name
            shutil.copyfile(original, target); names.append(target.name)
        binary = temp / ("solution.exe" if os.name == "nt" else "solution")
        command = [cc, "-std=c11", "-Wall", "-Wextra", "-O2", *names, "-o", str(binary)]
        try:
            completed = subprocess.run(command, cwd=temp, text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "compile_timeout", "command": command,
                    "duration_ms": int((time.monotonic() - started) * 1000)}
        return {"status": "passed" if completed.returncode == 0 else "compile_error",
                "command": command, "return_code": completed.returncode,
                "stderr": completed.stderr, "duration_ms": int((time.monotonic() - started) * 1000)}


def log_result(result: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (LOG_DIR / f"{time.strftime('%Y%m%d')}.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"timestamp": time.time(), **result}, ensure_ascii=False) + "\n")


def print_result(result: dict, json_mode: bool = False, quiet: bool = False) -> None:
    if json_mode:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if quiet:
        return
    print(f"{result['exercise']}: {result['status']} ({result.get('duration_ms', 0)} ms)")
    if result.get("error"):
        print(f"  {result['error']}")
    if result["status"] == "compile_error":
        print(result["compile"].get("stderr", "").rstrip())
    for number, case in enumerate(result.get("cases", []), 1):
        print(f"  case {number}: {'PASS' if case['passed'] else 'FAIL'} ({case['duration_ms']} ms)")
        if not case["passed"]:
            if case.get("error"): print(f"    error: {case['error']}")
            print(f"    expected: {case['expected']!r}")
            print(f"    actual:   {case['actual']!r}")


def record(directory: Path, result: dict, state: dict) -> None:
    source, _ = exercise_files(directory)
    item = state.setdefault("exercises", {}).setdefault(exercise_id(directory), {})
    item.update({"status": result["status"], "last_result": result,
                 "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest() if source else ""})
    state["current"] = exercise_id(directory)
    if result["status"] == "passed" and not has_completion_marker(directory):
        (directory / "done.flag").write_text("done\n", encoding="utf-8")
    elif (directory / "done.flag").exists():
        (directory / "done.flag").unlink()


def command_list(args: argparse.Namespace) -> int:
    current = current_state(); exercises = discover(include_hidden=args.all, include_disabled=args.all)
    if args.json:
        print(json.dumps({"exercises": [{"number": index, "id": exercise_id(directory),
                                          "title": metadata(directory)["title"],
                                          "difficulty": metadata(directory)["difficulty"],
                                          "status": progress_status(directory, current)}
                                         for index, directory in enumerate(exercises, 1)],
                         "completed": sum(is_done(p, current) for p in exercises),
                         "total": len(exercises)}, ensure_ascii=False, indent=2))
        return EXIT_OK
    for index, directory in enumerate(exercises, 1):
        meta = metadata(directory); mark = progress_status(directory, current)
        print(f"{index:>3}. [{mark:4}] {exercise_id(directory):<28} {meta['title']} [{meta['difficulty']}]")
    print(f"progress: {sum(is_done(p, current) for p in exercises)}/{len(exercises)}")
    return EXIT_OK


def command_progress(args: argparse.Namespace) -> int:
    """Display the compact learning progress used by the interactive loop."""
    state = current_state(); exercises = discover(include_hidden=getattr(args, "all", False))
    completed = sum(is_done(item, state) for item in exercises)
    current = next((item for item in exercises if not is_done(item, state)), None)
    if getattr(args, "json", False):
        print(json.dumps({"completed": completed, "total": len(exercises),
                          "current": (exercise_id(current) if current else None),
                          "title": (metadata(current)["title"] if current else None)},
                         ensure_ascii=False, indent=2))
        return EXIT_OK
    print(f"progress: {completed}/{len(exercises)}")
    if current:
        print(f"current: {exercise_id(current)} - {metadata(current)['title']}")
    else:
        print("current: all exercises completed")
    return EXIT_OK


def target_list(args: argparse.Namespace) -> list[Path]:
    if getattr(args, "exercise", None):
        target = find_exercise(args.exercise)
        if target is None: raise ValueError(f"exercise not found: {args.exercise}")
        return [target]
    return discover()


def command_check(args: argparse.Namespace) -> int:
    current = current_state(); cfg = settings()
    try: targets = target_list(args)
    except ValueError as exc: print(str(exc), file=sys.stderr); return EXIT_USAGE
    failures = 0; results: list[dict] = []
    for directory in targets:
        result = grade(directory, args.timeout or float(cfg["timeout_seconds"]),
                       args.total_timeout or float(cfg["total_timeout_seconds"]), int(cfg["max_output_bytes"]))
        log_result(result); record(directory, result, current); results.append(result)
        if not args.json:
            print_result(result, False, args.quiet)
        failures += result["status"] != "passed"
    save_state(current)
    if args.json:
        print(json.dumps({"results": results,
                          "passed": sum(item["status"] == "passed" for item in results),
                          "failed": sum(item["status"] != "passed" for item in results),
                          "total": len(results)}, ensure_ascii=False, indent=2))
    return EXIT_FAILED if failures else EXIT_OK


def command_validate(args: argparse.Namespace) -> int:
    invalid = 0; issues: list[str] = []; seen: set[str] = set(); orders: set[int] = set(); all_items = discover(include_hidden=True, include_disabled=True)
    def issue(message: str) -> None:
        nonlocal invalid
        invalid += 1; issues.append(message)
        if not getattr(args, "json", False): print(message)
    for directory in all_items:
        identifier = exercise_id(directory)
        if identifier in seen: issue(f"invalid: duplicate id {identifier}")
        seen.add(identifier); source, tests = exercise_files(directory)
        if source is None or tests is None or not parse_tests(tests): issue(f"invalid: {identifier} source/Test.txt")
        if not (directory / "description.md").exists(): issue(f"invalid: {identifier} description.md")
        if not (directory / "Ques.c.bak").exists(): issue(f"invalid: {identifier} Ques.c.bak")
        meta_path = directory / "metadata.json"
        if not meta_path.exists():
            issue(f"invalid: {identifier} metadata.json")
        else:
            try:
                value = json.loads(read_text(meta_path))
            except (OSError, json.JSONDecodeError):
                value = None
            if (not isinstance(value, dict) or not isinstance(value.get("tags", []), list)
                    or not isinstance(value.get("order", 0), int)
                    or value.get("status", "active") not in {"active", "hidden", "disabled"}):
                issue(f"invalid: {identifier} metadata.json")
            elif value.get("order", 0) and value["order"] in orders:
                issue(f"invalid: duplicate order {value['order']}")
            elif value.get("order", 0):
                orders.add(value["order"])
            if isinstance(value, dict) and "sources" in value:
                sources = value["sources"]
                source_error = not isinstance(sources, list) or not sources
                if not source_error:
                    for item in sources:
                        candidate = (directory / str(item)).resolve()
                        try:
                            candidate.relative_to(directory.resolve())
                        except ValueError:
                            source_error = True
                            break
                        if not candidate.is_file():
                            source_error = True
                            break
                if source_error:
                    issue(f"invalid: {identifier} metadata.json sources")
    curriculum = load_json(CURRICULUM, {"chapters": []}).get("chapters", [])
    exercise_map = load_json(EXERCISE_MAP, {})
    for chapter in curriculum:
        mapped = exercise_map.get(chapter["id"], [])
        if not mapped:
            issue(f"invalid: curriculum chapter has no exercises: {chapter['id']}")
        for identifier in mapped:
            if not (EXERCISES / identifier).is_dir():
                issue(f"invalid: curriculum exercise missing: {identifier}")
    if getattr(args, "compile", False):
        for directory in all_items:
            compiled = compile_only(directory, float(getattr(args, "compile_timeout", 10.0)))
            if compiled["status"] != "passed":
                issue(f"invalid: {exercise_id(directory)} {compiled['status']}: {compiled.get('error', compiled.get('stderr', '')).strip()}")
    if getattr(args, "json", False):
        print(json.dumps({"valid": invalid == 0, "issues": issues,
                          "exercise_count": len(all_items),
                          "compiled": bool(getattr(args, "compile", False))}, ensure_ascii=False, indent=2))
    else:
        print(f"validated: {len(seen) - invalid} ok, {invalid} invalid")
    return EXIT_FAILED if invalid else EXIT_OK


def command_reset(args: argparse.Namespace) -> int:
    for directory in discover(include_hidden=True, include_disabled=True):
        flag = directory / "done.flag"
        if flag.exists(): flag.unlink()
        backup, source = directory / "Ques.c.bak", directory / "Ques.c"
        if backup.exists() and source.exists(): shutil.copyfile(backup, source)
    save_state({"version": 1, "current": None, "exercises": {}}); print("CStudy progress reset."); return EXIT_OK


def adjacent(directory: Path, step: int) -> Optional[Path]:
    items = discover(include_hidden=True)
    try:
        index = items.index(directory) + step
        return items[index] if 0 <= index < len(items) else None
    except ValueError: return None


def command_next(args: argparse.Namespace) -> int:
    current = current_state(); exercise = getattr(args, "exercise", None)
    target = find_exercise(exercise) if exercise else next((p for p in discover() if not is_done(p, current)), None)
    if target is None: print("all exercises completed"); return EXIT_OK
    set_current_exercise(target, current)
    print(f"next: {exercise_id(target)} - {metadata(target)['title']}"); return EXIT_OK


def command_move(args: argparse.Namespace, step: int) -> int:
    target = find_exercise(args.exercise)
    if target is None: print(f"exercise not found: {args.exercise}", file=sys.stderr); return EXIT_USAGE
    other = adjacent(target, step)
    if other is None: print("no adjacent exercise")
    else:
        set_current_exercise(other)
        print(f"{exercise_id(other)} - {metadata(other)['title']}")
    return EXIT_OK


def command_skip(args: argparse.Namespace) -> int:
    target = find_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    current = current_state(); current.setdefault("exercises", {}).setdefault(exercise_id(target), {})["status"] = "skipped"
    next_target = next((item for item in discover() if not is_done(item, current) and item != target), None)
    current["current"] = exercise_id(next_target) if next_target else exercise_id(target)
    save_state(current); print(f"skipped: {exercise_id(target)}"); return EXIT_OK


def command_status(args: argparse.Namespace) -> int:
    if not args.exercise: return command_list(argparse.Namespace(all=False))
    target = find_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    print(json.dumps(current_state().get("exercises", {}).get(exercise_id(target), {}), ensure_ascii=False, indent=2)); return EXIT_OK


def command_edit(args: argparse.Namespace) -> int:
    target = find_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    source, _ = exercise_files(target)
    if source is None: return EXIT_USAGE
    if not open_editor(source, args):
        if os.name == "nt": os.startfile(str(source))  # type: ignore[attr-defined]
        else: subprocess.Popen(["vi", str(source)])
    print(source); return EXIT_OK


def hyperlink(path: Path, label: Optional[str] = None) -> str:
    visible = label or str(path)
    uri = quote(str(path.resolve()).replace(os.sep, "/"), safe="/:")
    return f"\x1b]8;;file://{uri}\x1b\\{visible}\x1b]8;;\x1b\\"


def open_editor(target: Path, args: argparse.Namespace) -> bool:
    if getattr(args, "no_editor", False): return False
    command = getattr(args, "edit_cmd", None) or os.environ.get("CSTUDY_EDIT_CMD") or os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not command and os.name == "nt" and shutil.which("code"): command = "code"
    if not command: return False
    try:
        subprocess.Popen(shlex.split(command) + [str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, ValueError): return False


def interactive_terminal() -> bool:
    """True when both standard streams are attached to a terminal."""
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except (AttributeError, ValueError):
        return False


@contextlib.contextmanager
def raw_terminal():
    if os.name == "nt" or termios is None or tty is None or not sys.stdin.isatty():
        yield; return
    try:
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    except (OSError, termios.error):
        yield
        return
    try:
        tty.setcbreak(fd); yield
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (OSError, termios.error):
            pass


def read_key(timeout: float = 0.1) -> Optional[str]:
    if os.name == "nt":
        import msvcrt
        try:
            if not msvcrt.kbhit(): time.sleep(timeout); return None
            key = msvcrt.getwch()
        except (OSError, ValueError) as exc:
            raise RuntimeError("Windows console input is unavailable") from exc
        if key in {"\x00", "\xe0"}:
            try:
                code = msvcrt.getwch()
            except (OSError, ValueError):
                return None
            return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT",
                    "G": "HOME", "O": "END", "S": "DELETE"}.get(code, "")
        if key == "\x1b":
            # Windows Terminal and some IDE consoles report ANSI arrows.
            sequence = ""
            deadline = time.monotonic() + 0.03
            while msvcrt.kbhit() and time.monotonic() < deadline:
                sequence += msvcrt.getwch()
            return {"[A": "UP", "[B": "DOWN", "[C": "RIGHT", "[D": "LEFT",
                    "[H": "HOME", "[F": "END", "[3~": "DELETE"}.get(sequence, "ESC")
        return "CTRL-C" if key == "\x03" else key
    if not sys.stdin.isatty(): time.sleep(timeout); return None
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready: return None
    key = sys.stdin.read(1)
    if key == "\x03": return "CTRL-C"
    if key == "\x1b":
        sequence = ""
        for _ in range(3):
            more, _, _ = select.select([sys.stdin], [], [], 0.01)
            if not more: break
            sequence += sys.stdin.read(1)
        return {"[A": "UP", "[B": "DOWN", "[C": "RIGHT", "[D": "LEFT",
                "[H": "HOME", "[F": "END", "[3~": "DELETE"}.get(sequence, "ESC")
    return key


@contextlib.contextmanager
def cooked_terminal():
    """Temporarily restore line input for search prompts."""
    if os.name == "nt" or termios is None or not sys.stdin.isatty():
        yield
        return
    try:
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    except (OSError, termios.error):
        yield
        return
    try:
        cooked = old[:]
        cooked[3] |= termios.ICANON | termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, cooked)
        yield
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (OSError, termios.error):
            pass


def read_line(prompt: str = "") -> str:
    with cooked_terminal():
        return input(prompt).strip()


def progress_bar(state: dict, exercises: Optional[list[Path]] = None, width: int = 30) -> str:
    exercises = exercises if exercises is not None else discover(); total = len(exercises)
    completed = sum(is_done(item, state) for item in exercises); filled = int(width * completed / total) if total else width
    return f"Progress: [{'#' * filled}{'-' * (width - filled)}] {completed}/{total}"


def clear_screen() -> None:
    if os.name == "nt":
        # PowerShell hosts may not have virtual-terminal sequences enabled,
        # including while the alternate screen buffer is active.
        os.system("cls")
    else:
        print("\x1b[2J\x1b[H\x1b[0J", end="", flush=True)


@contextlib.contextmanager
def alternate_screen():
    """Use a private terminal buffer so interactive frames never enter scrollback."""
    global _ALTERNATE_SCREEN
    _ALTERNATE_SCREEN = True
    print("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H", end="", flush=True)
    try:
        yield
    finally:
        print("\x1b[?25h\x1b[?1049l", end="", flush=True)
        _ALTERNATE_SCREEN = False


def leave_alternate_screen() -> None:
    """Return to the normal buffer, which is the only one with scrollback.

    The alternate screen is a private buffer that keeps no history, so a
    transcript printed there cannot be scrolled back through.
    """
    global _ALTERNATE_SCREEN
    if not _ALTERNATE_SCREEN:
        return
    print("\x1b[?25h\x1b[?1049l", end="", flush=True)
    _ALTERNATE_SCREEN = False


def enter_alternate_screen() -> None:
    """Re-enter the private buffer used by the interactive watch screen."""
    global _ALTERNATE_SCREEN
    if _ALTERNATE_SCREEN:
        return
    print("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H", end="", flush=True)
    _ALTERNATE_SCREEN = True


def render_watch_screen(target: Path, result: Optional[dict], hint: bool = False) -> None:
    state = current_state(); exercises = discover()
    width = max(18, min(48, shutil.get_terminal_size((80, 24)).columns - 30))
    clear_screen()
    print(paint(f"CStudy {VERSION}  |  C language exercises", "cyan"))
    print(paint(progress_bar(state, exercises, width), "bold"))
    print(f"\nCurrent: {paint(exercise_id(target), 'bold')}  {metadata(target)['title']} [{progress_status(target, state)}]")
    source, _ = exercise_files(target)
    if source: print(f"File: {hyperlink(source)}")
    description = target / "description.md"
    if description.exists():
        print(paint("\nDescription:", "cyan"))
        print(console_ux.render_markdown(read_text(description), width=console_ux.terminal_width()))
    if result:
        status = result.get("status", "pending")
        label, colour = ("PASS", "green") if status == "passed" else (("WARNING", "yellow") if status == "incomplete_marker" else ("ERROR", "red"))
        cases = result.get("cases", []); passed_cases = sum(case.get("passed", False) for case in cases)
        print(f"\n{paint(label, colour)} {status} ({result.get('duration_ms', 0)} ms)  {passed_cases}/{len(cases)} cases passed")
        if result.get("error"): print(paint(str(result["error"]), "yellow"))
        compile_stderr = result.get("compile", {}).get("stderr", "")
        if compile_stderr: print(paint(compile_stderr.rstrip(), "yellow"))
        for index, case in enumerate(result.get("cases", []), 1):
            actual = case.get("actual", "")
            print(f"\n{paint(f'Case {index}: PASS' if case.get('passed') else f'Case {index}: ERROR', 'green' if case.get('passed') else 'red')}")
            if actual or result.get("status") == "passed":
                print("Output:")
                print(actual if actual else "<empty>")
            if case.get("stderr"):
                print(paint("Warning (stderr):", "yellow"))
                print(case["stderr"].rstrip())
            if not case.get("passed"):
                print("Expected:")
                print(case.get("expected", "") or "<empty>")
    if hint:
        print(paint("\nHint:", "yellow"))
        if description.exists():
            print(console_ux.render_markdown(read_text(description), width=console_ux.terminal_width()))
        _, test_file = exercise_files(target)
        if test_file:
            cases = parse_tests(test_file)
            if cases:
                print(paint("Example input/output:", "yellow"))
                print(f"input: {cases[0].input or '<empty>'}")
                print(f"expected: {cases[0].expected or '<empty>'}")
    print("\n[n] next  [r] run  [h] hint  [a] AI chat  [l] list  [x] reset  [q] quit")


def list_tui() -> Optional[Path]:
    exercises = discover(include_hidden=True); state = current_state(); mode = "all"; query = ""
    current_id = state.get("current")
    selected = next((index for index, item in enumerate(exercises) if exercise_id(item) == current_id), 0)
    def visible():
        return [p for p in exercises if (mode == "all" or (mode == "done" and is_done(p, state)) or (mode == "pending" and not is_done(p, state))) and (not query or query.lower() in (exercise_id(p) + " " + metadata(p)["title"]).lower())]
    dirty = True
    with raw_terminal():
        while True:
            items = visible(); selected = min(selected, max(0, len(items) - 1))
            if dirty:
                clear_screen()
                print("CStudy exercises  (j/k move, d/p filter, s search, Enter select, q back)\n")
                height = max(5, shutil.get_terminal_size((80, 24)).lines - 6)
                start = max(0, min(selected - height // 2, len(items) - height))
                end = min(len(items), start + height)
                if start > 0: print(paint("... more above ...", "dim"))
                for index, item in enumerate(items[start:end], start):
                    mark = "DONE" if is_done(item, state) else "    "; cursor = ">" if index == selected else " "
                    print(f"{cursor} {index + 1:>2}. [{mark}] {exercise_id(item)} - {metadata(item)['title']}")
                if end < len(items): print(paint("... more below ...", "dim"))
                dirty = False
            key = read_key()
            if key in {"q", "ESC", "CTRL-C"}: return None
            if key in {"j", "DOWN"}: selected = min(selected + 1, max(0, len(items) - 1)); dirty = True
            elif key in {"k", "UP"}: selected = max(0, selected - 1); dirty = True
            elif key == "g": selected = 0; dirty = True
            elif key in {"G", "END"}: selected = max(0, len(items) - 1); dirty = True
            elif key == "d": mode = "done" if mode != "done" else "all"; selected = 0; dirty = True
            elif key == "p": mode = "pending" if mode != "pending" else "all"; selected = 0; dirty = True
            elif key in {"s", "/"}:
                query = read_line("\nSearch: "); selected = 0; dirty = True
            elif key == "r" and items:
                item = items[selected]; backup = item / "Ques.c.bak"; source = item / "Ques.c"
                if backup.exists(): shutil.copyfile(backup, source)
                state.setdefault("exercises", {}).pop(exercise_id(item), None); save_state(state); dirty = True
            elif key in {"c", "\r", "\n", "ENTER"} and items:
                set_current_exercise(items[selected], state); return items[selected]


def watch_tui(args: argparse.Namespace, target: Path) -> int:
    state = current_state(); set_current_exercise(target, state); source, _ = exercise_files(target); assert source
    result: dict = {}; hint = False; previous = 0

    def run_current() -> None:
        nonlocal result, previous
        result = grade(target, args.timeout, args.total_timeout, int(settings()["max_output_bytes"]))
        log_result(result); current = current_state(); record(target, result, current); save_state(current)
        previous = source.stat().st_mtime_ns

    def move_next() -> bool:
        nonlocal target, source
        if result.get("status") != "passed":
            return False
        next_target = next((item for item in discover() if not is_done(item, current_state()) and item != target), None)
        if next_target is None:
            return False
        target = next_target; source, _ = exercise_files(target); assert source
        set_current_exercise(target); open_editor(source, args); run_current()
        return True

    run_current(); open_editor(source, args); move_next()
    try:
        with alternate_screen(), raw_terminal():
            dirty = True
            while True:
                if dirty:
                    render_watch_screen(target, result, hint); dirty = False
                key = read_key(getattr(args, "interval", .1))
                if key in {"q", "CTRL-C"}:
                    clear_screen(); print("CStudy stopped."); return EXIT_OK
                if key == "r":
                    run_current(); dirty = True
                    if move_next(): dirty = True
                elif key == "h":
                    hint = not hint; dirty = True
                elif key == "a":
                    # The alternate screen keeps no history, so run the chat in
                    # the normal buffer where the transcript can be scrolled back.
                    leave_alternate_screen()
                    code = chat_session(target, timeout=float(getattr(args, "ai_timeout", 60.0)),
                                        opening=HINT_REQUEST)
                    if code != EXIT_OK:
                        read_line("\nPress Enter to return...")
                    enter_alternate_screen()
                    dirty = True
                elif key == "l":
                    chosen = list_tui()
                    if chosen:
                        target = chosen; source, _ = exercise_files(target); assert source; set_current_exercise(target); open_editor(source, args)
                        run_current(); dirty = True
                        if move_next(): dirty = True
                elif key == "n" and result.get("status") == "passed":
                    if move_next(): dirty = True
                elif key == "x":
                    answer = read_line("\nReset this exercise? [y/N] ")
                    if answer.lower() == "y":
                        backup = target / "Ques.c.bak"
                        if backup.exists(): shutil.copyfile(backup, source)
                        current = current_state(); current.setdefault("exercises", {}).pop(exercise_id(target), None); save_state(current)
                        run_current(); dirty = True
                if source.stat().st_mtime_ns != previous or key in {"r", "n", "x"}:
                    run_current(); dirty = True
                    if result.get("status") == "passed" and move_next(): dirty = True
    except KeyboardInterrupt:
        clear_screen(); print("CStudy stopped."); return EXIT_OK


def command_watch(args: argparse.Namespace) -> int:
    target = find_exercise(args.exercise) if args.exercise else None
    if target is None and not args.exercise:
        state = current_state()
        target = next((item for item in discover() if not is_done(item, state)), None)
    if target is None:
        print(f"exercise not found: {args.exercise}", file=sys.stderr); return EXIT_USAGE
    if sys.stdin.isatty() and sys.stdout.isatty() and not getattr(args, "once", False):
        try:
            return watch_tui(args, target)
        except (OSError, RuntimeError):
            # Some IDE terminals report isatty() but do not expose a keyboard
            # console. Fall through to the portable polling watcher.
            print("Interactive keyboard input is unavailable; using polling watch mode.", file=sys.stderr)
    source, _ = exercise_files(target); assert source
    print_progress = getattr(args, "progress", True)
    print(f"watching {exercise_id(target)} - {metadata(target)['title']}; press Ctrl+C to stop")
    if print_progress:
        command_progress(argparse.Namespace(all=False))
    previous = source.stat().st_mtime_ns
    try:
        while True:
            time.sleep(args.interval); current_mtime = source.stat().st_mtime_ns
            if current_mtime == previous: continue
            previous = current_mtime; cfg = settings()
            result = grade(target, args.timeout, args.total_timeout, int(cfg["max_output_bytes"]))
            log_result(result); current = current_state(); record(target, result, current); save_state(current)
            print_result(result, args.json, args.quiet)
            if not args.quiet and result["status"] != "passed":
                print("edit the source, save it, and the check will run again")
            if result["status"] == "passed" and args.auto_next:
                other = adjacent(target, 1)
                if other:
                    target = other
                    source, _ = exercise_files(target)
                    assert source
                    previous = source.stat().st_mtime_ns
                    print(f"watching next: {exercise_id(target)} - {metadata(target)['title']}")
                    if print_progress:
                        command_progress(argparse.Namespace(all=False))
                if args.once or other is None: return EXIT_OK
            elif args.once:
                return EXIT_OK
    except KeyboardInterrupt: print("\nstopped")
    return EXIT_OK


def command_curriculum(args: argparse.Namespace) -> int:
    catalog = load_json(CURRICULUM, {"chapters": []}); mapping = load_json(EXERCISE_MAP, {})
    if args.json:
        print(json.dumps({"book": catalog.get("book", "CStudy"),
                          "chapters": [{"number": index, "id": chapter["id"],
                                         "title": chapter["title"],
                                         "exercises": mapping.get(chapter["id"], [])}
                                        for index, chapter in enumerate(catalog.get("chapters", []), 1)]},
                         ensure_ascii=False, indent=2))
        return EXIT_OK
    print(f"{catalog.get('book', 'CStudy')} curriculum")
    for index, chapter in enumerate(catalog.get("chapters", []), 1):
        exercises = mapping.get(chapter["id"], [])
        print(f"{index:>2}. {chapter['title']} ({chapter['id']}) - {len(exercises)} exercise(s)")
    return EXIT_OK


def command_doctor(args: argparse.Namespace) -> int:
    exercises = discover(include_hidden=True, include_disabled=True)
    ai_cfg = ai_configuration()
    invalid = []
    for directory in exercises:
        source, tests = exercise_files(directory)
        if source is None or tests is None or not (directory / "description.md").exists() or not (directory / "Ques.c.bak").exists():
            invalid.append(exercise_id(directory))
    report = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "compiler": compiler() or "",
        "exercise_count": len(exercises),
        "invalid_exercises": invalid,
        "api_configured": bool(ai_cfg["api_key"]),
        "api_base": ai_cfg["api_base"],
        "ai_model": ai_cfg["model"],
        "status": "ready" if compiler() and exercises and not invalid else "not_ready",
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for key, value in report.items(): print(f"{key}: {value}")
        if not report["api_configured"]:
            print("note: API AI is optional; run `cstudy ai --setup` to configure it")
    return EXIT_OK if report["status"] == "ready" else EXIT_FAILED


def extract_ai_content(body: dict, api_mode: str) -> str:
    if api_mode == "responses":
        content = body.get("output_text")
        if isinstance(content, str) and content:
            return content
        fragments = []
        for item in body.get("output", []):
            for part in item.get("content", []):
                if isinstance(part.get("text"), str):
                    fragments.append(part["text"])
        return "".join(fragments)
    content = body["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return ""


def api_error_message(raw: bytes) -> str:
    text = raw.decode("utf-8", "replace").strip()
    if not text:
        return ""
    try:
        body = json.loads(text)
        error = body.get("error", body) if isinstance(body, dict) else body
        if isinstance(error, dict):
            return str(error.get("message") or error.get("detail") or error.get("code") or text)
        return str(error)
    except json.JSONDecodeError:
        return text[:1000]


class AiRequestError(Exception):
    """One failed AI request, carrying ready-to-print error lines."""

    def __init__(self, lines: list[str], code: int = 4) -> None:
        super().__init__(lines[0] if lines else "AI request failed")
        self.lines = lines
        self.code = code


def build_ai_payload(model: str, api_mode: str, messages: list[dict]) -> dict:
    """Translate a role/content conversation into the provider's request shape."""
    if api_mode == "responses":
        return {"model": model, "input": [
            {"role": message["role"],
             "content": [{"type": "output_text" if message["role"] == "assistant" else "input_text",
                          "text": message["content"]}]}
            for message in messages]}
    return {"model": model, "messages": messages}


def ai_endpoint(api_mode: str) -> str:
    return "/responses" if api_mode == "responses" else "/chat/completions"


class AiCancelled(Exception):
    """Raised when the user interrupts an in-flight request."""


def extract_reasoning(body: dict, api_mode: str) -> str:
    """Reasoning text that some providers return next to the answer."""
    if api_mode == "responses":
        return ""
    try:
        message = body["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return ""
    for key in ("reasoning_content", "reasoning"):
        value = message.get(key)
        if isinstance(value, str):
            return value
    return ""


def read_ai_stream(response, api_mode: str, on_delta=None, on_reasoning=None, cancel=None) -> str:
    """Read an SSE event stream, tolerating a gateway that ignores stream=true.

    Reasoning deltas (DeepSeek reasoning_content, Responses reasoning summaries)
    go to on_reasoning so the caller can show the thinking process.
    """
    def interrupted() -> None:
        if cancel is not None and cancel.is_set():
            raise AiCancelled()

    first = ""
    for raw in response:
        interrupted()
        candidate = raw.decode("utf-8", "replace").strip()
        if candidate:
            first = candidate
            break
    if not first:
        raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
    if not first.startswith("data:"):
        # The endpoint answered with one JSON document instead of an event stream.
        body = json.loads((first + "\n" + response.read().decode("utf-8", "replace")).strip())
        reasoning = extract_reasoning(body, api_mode)
        if reasoning and on_reasoning:
            on_reasoning(reasoning)
        content = extract_ai_content(body, api_mode)
        if not content:
            raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
        if on_delta:
            on_delta(content)
        return content
    collected: list[str] = []

    def consume(line: str) -> bool:
        line = line.strip()
        if not line or line.startswith(":") or not line.startswith("data:"):
            return False
        data = line[5:].strip()
        if data == "[DONE]":
            return True
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            return False
        kind = chunk.get("type")
        if kind == "response.reasoning_summary_text.delta":
            piece = chunk.get("delta")
            if piece and on_reasoning:
                on_reasoning(piece)
            return False
        if kind == "response.output_text.delta":
            piece = chunk.get("delta")
            if piece:
                collected.append(piece)
                if on_delta:
                    on_delta(piece)
            return False
        for choice in chunk.get("choices", []):
            delta = choice.get("delta") or {}
            thought = delta.get("reasoning_content") or delta.get("reasoning")
            if thought and on_reasoning:
                on_reasoning(thought)
            piece = delta.get("content")
            if piece:
                collected.append(piece)
                if on_delta:
                    on_delta(piece)
        return False

    if consume(first):
        return "".join(collected)
    for raw in response:
        interrupted()
        if consume(raw.decode("utf-8", "replace")):
            break
    content = "".join(collected)
    if not content:
        raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
    return content


def ai_request_once(base_url: str, api_key: str, model: str, api_mode: str, messages: list[dict],
                    timeout: float, stream: bool, on_delta, on_reasoning, cancel, on_open) -> str:
    endpoint = ai_endpoint(api_mode)
    payload_value = build_ai_payload(model, api_mode, messages)
    if stream:
        payload_value["stream"] = True
    payload = json.dumps(payload_value, ensure_ascii=False).encode("utf-8")
    url = base_url + endpoint
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    if stream:
        headers["Accept"] = "text/event-stream"
    try:
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if on_open:
                on_open(response)
            if stream:
                return read_ai_stream(response, api_mode, on_delta, on_reasoning, cancel)
            body = json.loads(response.read().decode("utf-8"))
            reasoning = extract_reasoning(body, api_mode)
            if reasoning and on_reasoning:
                on_reasoning(reasoning)
            content = extract_ai_content(body, api_mode)
            if not content:
                raise KeyError("empty response content")
            return content
    except (AiRequestError, AiCancelled):
        raise
    except json.JSONDecodeError as exc:
        raise AiRequestError([f"AI API returned invalid JSON: {exc}"]) from exc
    except urllib.error.HTTPError as exc:
        detail = api_error_message(exc.read())
        lines = [f"AI API error: HTTP {exc.code} {exc.reason}"]
        if detail:
            lines.append(f"Service message: {detail}")
        lines.append(f"Endpoint: {url}")
        if exc.code in {401, 403}:
            lines.append("Check the API key and whether it can access the selected model.")
        elif exc.code == 404:
            lines.append("Check CSTUDY_API_BASE, API mode, and the provider's compatible endpoint.")
        elif exc.code == 429:
            lines.append("The service rate limit or account quota was exceeded.")
        raise AiRequestError(lines) from exc
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        if cancel is not None and cancel.is_set():
            raise AiCancelled() from exc
        reason = getattr(exc, "reason", exc)
        raise AiRequestError([f"AI API connection failed: {reason}", f"Endpoint: {url}",
                              "Check the network or proxy, then retry."]) from exc
    except (KeyError, IndexError, TypeError) as exc:
        raise AiRequestError([f"AI API returned an unsupported response format: {exc}"]) from exc


def ai_request(base_url: str, api_key: str, model: str, api_mode: str, messages: list[dict],
               timeout: float, stream: bool = False, on_delta=None, on_reasoning=None,
               cancel=None, on_open=None, retries: int = 0) -> str:
    """Send one conversation turn and return the assistant text.

    Raises AiRequestError with printable lines instead of leaking tracebacks, and
    AiCancelled when cancel is set (interrupting a stream or closing it).
    """
    attempts = max(1, retries + 1)
    for attempt in range(attempts):
        try:
            return ai_request_once(base_url, api_key, model, api_mode, messages, timeout,
                                   stream, on_delta, on_reasoning, cancel, on_open)
        except AiCancelled:
            raise
        except AiRequestError as exc:
            transient = any("connection failed" in line for line in exc.lines)
            if attempt + 1 < attempts and transient:
                time.sleep(0.4)
                continue
            raise
    raise AiRequestError(["AI API request failed"])


def exercise_prompt(target: Path, hint_only: bool = False) -> str:
    """Build the one-shot prompt used by the ai command and the chat opener."""
    source, tests = exercise_files(target)
    previous = current_state().get("exercises", {}).get(exercise_id(target), {}).get("last_result", {})
    mode = ("Give hints and debugging questions without revealing the complete solution."
            if hint_only else "Explain the error and provide a complete compilable reference solution, but do not modify files.")
    return ("You are a C language learning assistant. " + mode + "\n"
            "Exercise description:\n" + read_text(target / "description.md")[:5000] + "\n"
            "Current code:\n" + read_text(source)[:10000] + "\n"
            "Tests:\n" + read_text(tests)[:5000] + "\n"
            "Latest grading result:\n" + json.dumps(previous, ensure_ascii=False)[:5000])


def print_ai_answer(content: str, raw: bool = False) -> None:
    """Render the answer as Markdown on a terminal; keep redirected output verbatim."""
    text = content.rstrip()
    if raw or not sys.stdout.isatty():
        print(text)
        return
    print(console_ux.render_markdown(text, width=console_ux.terminal_width()))


def command_ai(args: argparse.Namespace) -> int:
    if getattr(args, "setup", False):
        return EXIT_OK if configure_ai() else 4
    target_name = getattr(args, "exercise", None)
    if not target_name:
        print("AI is optional and uses an OpenAI-compatible API.")
        print("usage: cstudy ai <exercise> [--hint-only] | cstudy ai --setup")
        return EXIT_OK
    target = find_exercise(target_name)
    if target is None:
        print(f"exercise not found: {target_name}", file=sys.stderr)
        return EXIT_USAGE
    ai_cfg = ai_configuration()
    if not ai_cfg["api_key"]:
        print_ai_setup_help()
        if not (sys.stdin.isatty() and sys.stdout.isatty()) or not configure_ai():
            return 4
        ai_cfg = ai_configuration()
    api_key = ai_cfg["api_key"]
    base_url = ai_cfg["api_base"].rstrip("/")
    model = ai_cfg["model"]
    if "api.deepseek.com" in base_url.lower() and ai_cfg["mode"] == "responses":
        print("DeepSeek configuration error: its OpenAI-compatible API uses chat mode.", file=sys.stderr)
        print("Set ai_api_mode to chat, or run `cstudy ai --setup` and choose DeepSeek.", file=sys.stderr)
        print(f"Expected endpoint: {base_url}/chat/completions", file=sys.stderr)
        return 4
    source, tests = exercise_files(target)
    if source is None or tests is None:
        return EXIT_USAGE
    previous = current_state().get("exercises", {}).get(exercise_id(target), {}).get("last_result", {})
    prompt = exercise_prompt(target, getattr(args, "hint_only", False))
    timeout = getattr(args, "ai_timeout", 30.0)
    try:
        with console_ux.Status("Requesting AI") as status:
            content = ai_request(base_url, api_key, model, ai_cfg["mode"],
                                 [{"role": "user", "content": prompt}], timeout)
            status.stop(paint("✓ Answer ready", "green"))
    except AiRequestError as exc:
        for line in exc.lines:
            print(line, file=sys.stderr)
        return exc.code
    print_ai_answer(content, raw=getattr(args, "raw", False))
    return EXIT_OK


CHAT_COMMANDS = [
    ("/help", "show this help", False),
    ("/hint", "ask for a hint about the current exercise", False),
    ("/code", "reload Ques.c and the latest grading result", False),
    ("/clear", "forget the conversation so far", False),
    ("/model", "switch model (e.g. deepseek-reasoner)", True),
    ("/thinking", "toggle the thinking transcript", False),
    ("/raw", "toggle raw Markdown output", False),
    ("/stream", "toggle token streaming", False),
    ("/save", "write the last answer to a file", True),
    ("/exit", "leave chat", False),
]

CHAT_HELP = ("Commands (type / for completion):\n"
             + "\n".join("  %-10s %s" % (name, description) for name, description, _ in CHAT_COMMANDS)
             + "\n\nWhile a request runs: Enter queues the message, Esc interrupts, Ctrl+C exits."
             + "\nEditing: Left/Right, Home/End, Backspace, Delete, Ctrl+U/K/W."
             + "\nUp/Down pick a command while typing /, otherwise they recall history.")

CHAT_SYSTEM_PROMPT = """You are CStudy's C language tutor inside a terminal.
Reply in the same language as the student's question.
Prefer short Markdown: headings, bullet lists, and fenced C code blocks.
Explain the cause before showing code, and never claim code was tested.
Never modify files; the student applies the changes themselves."""

HINT_REQUEST = ("Analyse my current code against the exercise description and tests, then give hints and "
                "debugging questions without revealing the complete solution.")


def chat_system_prompt(target: Path) -> str:
    """Conversation context: the exercise, the student's code, and the last result."""
    source, tests = exercise_files(target)
    previous = current_state().get("exercises", {}).get(exercise_id(target), {}).get("last_result", {})
    parts = [CHAT_SYSTEM_PROMPT,
             f"Exercise: {exercise_id(target)} - {metadata(target)['title']}"]
    description = target / "description.md"
    if description.exists():
        parts.append("Exercise description:\n" + read_text(description)[:5000])
    if source is not None:
        parts.append("Current Ques.c:\n" + read_text(source)[:10000])
    if tests is not None:
        parts.append("Tests:\n" + read_text(tests)[:5000])
    if previous:
        parts.append("Latest grading result:\n" + json.dumps(previous, ensure_ascii=False)[:3000])
    return "\n\n".join(parts)


def chat_status_line(elapsed: float, label: str, tokens: int, animate: bool = True) -> str:
    """Compose the pinned status row: marker, phase, counters.

    Streamed text belongs to the transcript, so this row never previews it: a
    sliding preview reads as noise and forces a repaint on every token, which
    fights the user's scrolling.
    """
    if not animate:
        # The transcript is visibly moving on its own, so this row stays
        # completely still: any repaint here would fight the user's scrolling
        # while adding nothing they cannot already see.
        return "%s %s" % (console_ux.paint("\u273b", "dim"), label)
    marker = console_ux.paint(console_ux.spinner_frame(elapsed), "cyan")
    return "%s %s %s" % (marker, label,
                         console_ux.paint("(%.1fs \u00b7 %d tok)" % (elapsed, tokens), "dim"))


def chat_session(target: Path, timeout: float = 60.0, stream: bool = True,
                 raw: bool = False, opening: Optional[str] = None) -> int:
    """Multi-turn console conversation; the input line stays live while work runs."""
    ai_cfg = ai_configuration()
    if not ai_cfg["api_key"]:
        print_ai_setup_help()
        if not (sys.stdin.isatty() and sys.stdout.isatty()) or not configure_ai():
            return 4
        ai_cfg = ai_configuration()
    api_key = ai_cfg["api_key"]
    base_url = ai_cfg["api_base"].rstrip("/")
    model = ai_cfg["model"]
    api_mode = ai_cfg["mode"]
    if "api.deepseek.com" in base_url.lower() and api_mode == "responses":
        print("DeepSeek configuration error: its OpenAI-compatible API uses chat mode.", file=sys.stderr)
        print("Set ai_api_mode to chat, or run the AI setup and choose DeepSeek.", file=sys.stderr)
        print(f"Expected endpoint: {base_url}/chat/completions", file=sys.stderr)
        return 4

    messages: list[dict] = [{"role": "system", "content": chat_system_prompt(target)}]
    width = console_ux.terminal_width()
    print(console_ux.paint(f"Chat: {exercise_id(target)} - {metadata(target)['title']}", "bold", "cyan"))
    print(console_ux.paint("Enter queues while busy, Esc interrupts, /help lists commands.", "dim"))

    interactive = interactive_terminal()
    reader: Optional[console_ux.InputReader] = None
    console: Any
    if interactive:
        reader = console_ux.InputReader(read_key, console_ux.LineEditor(commands=CHAT_COMMANDS))
        console = console_ux.LiveConsole(hint="Enter queues \u00b7 Esc interrupts \u00b7 /help",
                                         restore_hidden_cursor=_ALTERNATE_SCREEN)
        reader.start()
    else:
        console = console_ux.PlainConsole()

    work: "queue.Queue[tuple]" = queue.Queue()
    pending: list[str] = [opening] if opening else []
    active = False
    cancel_event: Optional[threading.Event] = None
    response_slot: dict = {}
    started = 0.0
    tokens = 0
    answer = ""
    reasoning = ""
    last_answer = ""
    stream_on = stream
    show_thinking = True
    thinking: Optional[console_ux.StreamingBlock] = None
    last_transcript = 0.0
    worker: Optional[threading.Thread] = None

    def start_request(question: str) -> None:
        nonlocal active, cancel_event, started, tokens, answer, reasoning, worker, thinking
        thinking = None
        messages.append({"role": "user", "content": question})
        cancel_event = threading.Event()
        started = time.monotonic()
        tokens = 0
        answer = ""
        reasoning = ""
        response_slot.clear()
        active = True
        console.note("Thinking...")
        current_model, current_mode = model, api_mode

        def on_delta(piece: str) -> None:
            work.put(("delta", piece))

        def on_reasoning(piece: str) -> None:
            work.put(("reasoning", piece))

        def on_open(response) -> None:
            response_slot["response"] = response

        def run() -> None:
            try:
                text = ai_request(base_url, api_key, current_model, current_mode, list(messages),
                                  timeout, stream=stream_on, on_delta=on_delta,
                                  on_reasoning=on_reasoning, cancel=cancel_event,
                                  on_open=on_open, retries=1)
                work.put(("done", text))
            except AiCancelled:
                work.put(("cancelled", ""))
            except AiRequestError as exc:
                work.put(("error", exc.lines))

        worker = threading.Thread(target=run, daemon=True)
        worker.start()

    def interrupt() -> None:
        if not active:
            # nothing is running: stay quiet (Esc already closed any menu)
            return
        if cancel_event is not None:
            cancel_event.set()
        response = response_slot.get("response")
        if response is not None:
            try:
                response.close()
            except OSError:
                pass
        console.print_above(console_ux.paint("\u2717 interrupted", "yellow"))

    def handle_command(line: str) -> Optional[str]:
        nonlocal raw, stream_on, show_thinking, model, thinking
        command, _, argument = line.partition(" ")
        command = command.lower()
        if command in {"/exit", "/quit", "/q"}:
            return "exit"
        if command in {"/help", "/?"}:
            console.print_above(CHAT_HELP)
        elif command == "/hint":
            pending.append(HINT_REQUEST)
        elif command == "/clear":
            del messages[1:]
            console.print_above("context cleared")
        elif command in {"/code", "/result"}:
            messages[0] = {"role": "system", "content": chat_system_prompt(target)}
            console.print_above("context reloaded")
        elif command == "/thinking":
            show_thinking = not show_thinking
            if not show_thinking and thinking is not None:
                thinking.flush()
                thinking = None
            console.print_above("thinking streams into the transcript" if show_thinking
                                else "thinking summary only")
        elif command == "/model":
            if argument.strip():
                model = argument.strip()
            console.print_above("model: " + model)
        elif command == "/raw":
            raw = not raw
            console.print_above("raw Markdown" if raw else "rendered Markdown")
        elif command == "/stream":
            stream_on = not stream_on
            console.print_above("streaming" if stream_on else "non-streaming")
        elif command == "/save":
            name = argument.strip() or "ai-answer.md"
            try:
                (ROOT / name).write_text(last_answer, encoding="utf-8")
                console.print_above(f"saved to {name}")
            except OSError as exc:
                console.print_above(f"cannot save {name}: {exc}")
        else:
            console.print_above(f"unknown command: {command} (try /help)")
        return None

    def plain_events() -> list[tuple]:
        try:
            line = read_line(console_ux.paint("\n\u203a ", "cyan"))
        except (EOFError, KeyboardInterrupt):
            return [("exit", "")]
        return [("submit", line)] if line else []

    def drain_work() -> None:
        """Apply everything the worker produced; safe to call before leaving."""
        nonlocal active, last_answer, answer, tokens, reasoning, thinking, last_transcript
        while True:
            try:
                kind, payload = work.get_nowait()
            except queue.Empty:
                break
            if kind == "delta":
                answer += payload
                tokens += 1
                if thinking is not None:
                    # the answer starts: close the thinking block above it
                    thinking.flush()
                    thinking = None
            elif kind == "reasoning":
                reasoning += payload
                tokens += 1
                if show_thinking:
                    if thinking is None:
                        console.print_above(console_ux.paint("\u273b Thinking", "dim"))
                        thinking = console_ux.StreamingBlock(console, style="dim", prefix="  ")
                    thinking.feed(payload)
                    last_transcript = time.monotonic()
            elif kind == "done":
                active = False
                last_answer = payload
                messages.append({"role": "assistant", "content": payload})
                if thinking is not None:
                    thinking.flush()
                    thinking = None
                if reasoning:
                    elapsed = time.monotonic() - started
                    hint = "/thinking hides it" if show_thinking else "/thinking to show"
                    console.print_above(console_ux.paint(
                        "\u273b thought for %.1fs (%d chars) \u00b7 %s"
                        % (elapsed, len(reasoning), hint), "dim"))
                console.print_above("")
                if raw or not sys.stdout.isatty():
                    console.print_above(payload.rstrip())
                else:
                    console.print_above(console_ux.render_markdown(payload.rstrip(), width=width))
            elif kind == "cancelled":
                active = False
                messages.pop()
                if thinking is not None:
                    thinking.flush()
                    thinking = None
                console.print_above(console_ux.paint("interrupted; the turn was discarded", "yellow"))
            elif kind == "error":
                active = False
                messages.pop()
                if thinking is not None:
                    thinking.flush()
                    thinking = None
                for text in payload:
                    console.print_above(console_ux.paint(text, "red"))

    try:
        while True:
            # 1. drain streamed output and finish the turn
            drain_work()

            # 2. a queued message starts as soon as the previous turn finishes
            if not active and pending:
                start_request(pending.pop(0))

            # 3. fall back to line input if raw keys are unavailable
            if reader is not None and reader.failed:
                reader.stop()
                reader = None
                console.close()
                console = console_ux.PlainConsole()
                console.print_above(console_ux.paint("keyboard input unavailable; using line input", "yellow"))

            # 4. collect input without blocking the stream
            events = reader.poll() if reader is not None else plain_events()
            leaving = False
            for action, text in events:
                if action == "submit":
                    line = text.strip()
                    if not line:
                        continue
                    # echo the submitted line: without it a command that prints
                    # its own help looks like nothing happened
                    console.print_above(console_ux.paint("\u203a " + line, "cyan"))
                    if line.lower() in {"exit", "quit"}:
                        leaving = True
                        break
                    if line.startswith("/"):
                        if handle_command(line) == "exit":
                            leaving = True
                            break
                        continue
                    pending.append(line)
                    if active:
                        console.print_above(console_ux.paint("\u23ce queued for the next turn", "dim"))
                elif action == "cancel":
                    interrupt()
                elif action == "interrupt":
                    if active:
                        interrupt()
                    else:
                        leaving = True
                        break
                elif action == "exit":
                    leaving = True
                    break
            if leaving:
                drain_work()
                if active:
                    interrupt()
                    if worker is not None:
                        worker.join(timeout=1.0)
                    drain_work()
                console.close()
                print("bye")
                return EXIT_OK

            # 5. redraw the pinned region
            if active:
                label = "Receiving" if answer else "Thinking"
                # animate only while nothing else on screen is moving; otherwise
                # hold the row still so it does not repaint on every token
                calm = show_thinking and (time.monotonic() - last_transcript) < 0.6
                status = chat_status_line(time.monotonic() - started, label, tokens,
                                          animate=not calm)
            else:
                status = ""
            if reader is not None:
                editor = reader.editor
                menu = (console_ux.menu_rows(CHAT_COMMANDS, editor.buffer, editor.menu_index, width)
                        if editor.menu_open else [])
                if menu and not status:
                    status = console_ux.paint(
                        "\u2191\u2193 select \u00b7 Enter run \u00b7 Tab complete \u00b7 Esc close", "dim")
                console.update(status, editor.buffer, editor.caret, menu)
            else:
                console.update(status)
            time.sleep(0.05)
    finally:
        if reader is not None:
            reader.stop()
        console.close()


def command_chat(args: argparse.Namespace) -> int:
    target = find_exercise(args.exercise) if getattr(args, "exercise", None) else None
    if target is None:
        target = current_exercise_from_state(current_state(), discover())
    if target is None:
        print("no exercise selected; use cstudy list or cstudy chat <exercise>", file=sys.stderr)
        return EXIT_USAGE
    if not interactive_terminal():
        print("cstudy chat needs an interactive terminal; use cstudy ai <exercise> instead.", file=sys.stderr)
        return EXIT_USAGE
    return chat_session(target, timeout=getattr(args, "ai_timeout", 60.0),
                        stream=getattr(args, "stream", True), raw=getattr(args, "raw", False))


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False); common.add_argument("--json", action="store_true"); common.add_argument("--quiet", action="store_true")
    root = argparse.ArgumentParser(prog="cstudy", description="Interactive C learning CLI"); root.add_argument("--version", action="version", version=f"CStudy {VERSION}")
    sub = root.add_subparsers(dest="command")
    listing = sub.add_parser("list", aliases=["progress"], parents=[common]); listing.add_argument("--all", action="store_true")
    sub.add_parser("curriculum", parents=[common])
    check = sub.add_parser("check", aliases=["run", "verify"], parents=[common]); check.add_argument("exercise", nargs="?"); check.add_argument("--timeout", type=float); check.add_argument("--total-timeout", type=float)
    watch = sub.add_parser("watch", parents=[common]); watch.add_argument("exercise", nargs="?"); watch.add_argument("--timeout", type=float, default=2.0); watch.add_argument("--total-timeout", type=float, default=10.0); watch.add_argument("--interval", type=float, default=.1); watch.add_argument("--auto-next", dest="auto_next", action="store_true", default=True); watch.add_argument("--no-auto-next", dest="auto_next", action="store_false"); watch.add_argument("--once", action="store_true"); watch.add_argument("--no-editor", action="store_true"); watch.add_argument("--edit-cmd")
    validate_parser = sub.add_parser("validate", parents=[common]); validate_parser.add_argument("--compile", action="store_true"); validate_parser.add_argument("--compile-timeout", type=float, default=10.0)
    sub.add_parser("reset", parents=[common]); sub.add_parser("doctor", parents=[common])
    next_parser = sub.add_parser("next", parents=[common]); next_parser.add_argument("exercise", nargs="?")
    status_parser = sub.add_parser("status", parents=[common]); status_parser.add_argument("exercise", nargs="?")
    ai_parser = sub.add_parser("ai", aliases=["hint"], parents=[common]); ai_parser.add_argument("exercise", nargs="?"); ai_parser.add_argument("--hint-only", action="store_true"); ai_parser.add_argument("--ai-timeout", type=float, default=30.0); ai_parser.add_argument("--setup", action="store_true"); ai_parser.add_argument("--raw", action="store_true")
    chat_parser = sub.add_parser("chat", aliases=["ask"], parents=[common]); chat_parser.add_argument("exercise", nargs="?"); chat_parser.add_argument("--ai-timeout", type=float, default=60.0); chat_parser.add_argument("--no-stream", dest="stream", action="store_false", default=True); chat_parser.add_argument("--raw", action="store_true")
    for name in ("prev", "edit", "skip"):
        item = sub.add_parser(name, parents=[common]); item.add_argument("exercise")
    return root


def main() -> int:
    console_ux.enable_windows_vt()
    args = build_parser().parse_args()
    if not args.command:
        exercises = discover(); state = current_state(); target = current_exercise_from_state(state, exercises)
        if target is None:
            print("All exercises completed.")
            return EXIT_OK
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            return command_progress(argparse.Namespace(all=False, json=False))
        defaults = argparse.Namespace(exercise=exercise_id(target), timeout=2.0, total_timeout=10.0,
                                      interval=.1, auto_next=False, once=False, json=False, quiet=False,
                                      progress=True, no_editor=False, edit_cmd=None)
        return command_watch(defaults)
    if args.command in {"list", "progress"}: return command_list(args) if args.command == "list" else command_progress(args)
    if args.command == "curriculum": return command_curriculum(args)
    if args.command in {"check", "run", "verify"}: return command_check(args)
    if args.command == "watch": return command_watch(args)
    if args.command == "validate": return command_validate(args)
    if args.command == "reset": return command_reset(args)
    if args.command == "doctor": return command_doctor(args)
    if args.command == "next": return command_next(args)
    if args.command == "prev": return command_move(args, -1)
    if args.command == "edit": return command_edit(args)
    if args.command == "skip": return command_skip(args)
    if args.command == "status": return command_status(args)
    if args.command in {"ai", "hint"}:
        if args.command == "hint": args.hint_only = True
        return command_ai(args)
    if args.command in {"chat", "ask"}:
        return command_chat(args)
    return EXIT_USAGE


if __name__ == "__main__": raise SystemExit(main())

