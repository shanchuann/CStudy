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
from concurrent.futures import ThreadPoolExecutor
import queue
import contextlib
import select
from urllib.parse import quote, urlparse
from dataclasses import asdict, dataclass, field
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
from ai import (AiCancelled, AiRequestError, configuration as resolve_ai_configuration,
                discover_compatible_model, print_answer as print_ai_answer,
                print_setup_help as print_ai_setup_help, request as ai_request)
from chat import COMMANDS as CHAT_COMMANDS, HELP as CHAT_HELP, HINT_REQUEST
from chat import status_line as chat_status_line, system_prompt as build_chat_system_prompt

def resolve_root() -> Path:
    """Locate the exercise catalogue.

    Order: $CSTUDY_ROOT, then the current directory (if it holds Exercises/),
    then the directory this module lives in. The first two make an installed
    copy usable from anywhere, the last keeps `python cstudy.py` working from
    a clone.
    """
    override = os.environ.get("CSTUDY_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    module_dir = Path(__file__).resolve().parent
    for candidate in (Path.cwd(), module_dir):
        try:
            if (candidate / "Exercises").is_dir(): return candidate
        except OSError:
            continue
    return module_dir


ROOT = resolve_root()
EXERCISES = ROOT / "Exercises"
CURRICULUM = ROOT / "book" / "curriculum.json"
EXERCISE_MAP = ROOT / "book" / "exercise-map.json"
STATE_DIR = ROOT / ".cstudy"
STATE_FILE = STATE_DIR / "state.json"
CONFIG_FILE = STATE_DIR / "config.json"
LOG_DIR = STATE_DIR / "logs"
VERSION = "0.6.0"
MAX_LOG_BYTES = 2 * 1024 * 1024
LOG_RETENTION_DAYS = 30
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


def unescape_marker(raw: str) -> str:
    """Undo the \\ escape used for data lines that look like a Test.txt marker.

    A test whose input or expected output really is "INPUT:" (or OUTPUT:/ARGS:/
    ---) is written with one leading backslash; every other line is untouched.
    """
    if raw.startswith("\\") and raw[1:].strip() in {"INPUT:", "OUTPUT:", "ARGS:", "---"}:
        return raw[1:]
    return raw


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
            inputs.append(unescape_marker(raw))
        elif mode == "output":
            outputs.append(unescape_marker(raw))
    flush()
    return cases


def load_json(path: Path, default: dict) -> dict:
    try:
        value = json.loads(read_text(path))
        return value if isinstance(value, dict) else default.copy()
    except (OSError, json.JSONDecodeError):
        return default.copy()


def current_state() -> dict:
    """Read saved progress.

    This is a pure read: pruning happens in save_state, so read-only commands
    (list, status, progress) never rewrite the state file.
    """
    state = load_json(STATE_FILE, {"version": 1, "exercises": {}, "current": None})
    state.setdefault("version", 1); state.setdefault("current", None)
    exercises = state.setdefault("exercises", {})
    if isinstance(exercises, dict):
        for item in exercises.values():
            if isinstance(item, dict): compact_entry(item)
    return state


def compact_entry(item: dict) -> dict:
    """Downgrade a legacy full grading result to the bounded summary form."""
    previous = item.get("last_result")
    if isinstance(previous, dict) and isinstance(previous.get("cases"), list):
        item["last_result"] = result_summary(previous)
    return item


def prune_state(state: dict) -> dict:
    """Drop progress for exercises that no longer exist.

    A failed discovery (empty result) never wipes existing progress.
    """
    known = {exercise_id(item) for item in discover(include_hidden=True, include_disabled=True)}
    exercises = state.get("exercises")
    if not known or not isinstance(exercises, dict):
        return state
    stale = set(exercises) - known
    for identifier in stale: exercises.pop(identifier, None)
    if state.get("current") in stale: state["current"] = None
    return state


def save_state(value: dict) -> None:
    prune_state(value)
    invalidate_caches()
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
                "max_output_bytes": 1024 * 1024, "compiler": "", "cflags": "",
                "ai_model": "gpt-4o-mini",
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
    """Effective AI configuration: environment variables win over saved settings."""
    return resolve_ai_configuration(settings())


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


#: Interactive frames redraw on every keystroke. These caches key on file
#: mtimes so one frame does not re-read 96 metadata.json and Ques.c files.
_METADATA_CACHE: dict[tuple, dict] = {}
_MARKER_CACHE: dict[tuple, bool] = {}
_DISCOVERY_CACHE: dict[tuple, tuple[float, tuple, list[Path]]] = {}
_DONE_CACHE: dict[tuple, tuple[float, set[str]]] = {}
_CACHE_LIMIT = 512
_DISCOVERY_TTL = 0.5
_DONE_TTL = 0.5
#: Bumped by invalidate_caches(); save_state() calls it, so any progress change
#: invalidates the done-set memo without relying on dict identity.
_STATE_REVISION = 0


def invalidate_caches(discovery: bool = False) -> None:
    """Drop memoized progress, and optionally the whole exercise tree."""
    global _STATE_REVISION
    _STATE_REVISION += 1
    _DONE_CACHE.clear()
    if discovery:
        _DISCOVERY_CACHE.clear()
        _METADATA_CACHE.clear()
        _MARKER_CACHE.clear()


def done_set(state: dict, exercises: list[Path]) -> set[str]:
    """Ids of finished exercises.

    is_done stats every source file and marker, so memoize briefly and let
    save_state invalidate the memo whenever progress changes.
    """
    key = (str(EXERCISES), _STATE_REVISION, len(exercises))
    now = time.monotonic()
    cached = _DONE_CACHE.get(key)
    if cached is not None and now - cached[0] < _DONE_TTL:
        return cached[1]
    done = {exercise_id(item) for item in exercises if is_done(item, state)}
    _DONE_CACHE.clear()
    _DONE_CACHE[key] = (now, done)
    return done


def exercises_signature() -> tuple:
    """Cheap fingerprint of the exercise tree: directory mtimes only."""
    if not EXERCISES.exists():
        return ()
    signature = []
    for current, dirs, _files in os.walk(EXERCISES):
        dirs.sort()
        try:
            signature.append((current, os.stat(current).st_mtime_ns))
        except OSError:
            pass
    return tuple(signature)


def has_completion_marker(directory: Path) -> bool:
    source, _ = exercise_files(directory)
    if source is None or not source.exists():
        return False
    try:
        stamp = source.stat().st_mtime_ns
    except OSError:
        stamp = None
    key = (str(source), stamp)
    if key in _MARKER_CACHE:
        return _MARKER_CACHE[key]
    value = any(marker in read_text(source) for marker in COMPLETION_MARKERS)
    if len(_MARKER_CACHE) >= _CACHE_LIMIT: _MARKER_CACHE.clear()
    _MARKER_CACHE[key] = value
    return value


def metadata(directory: Path) -> dict:
    meta_path = directory / "metadata.json"
    description = directory / "description.md"
    try: stamp = meta_path.stat().st_mtime_ns
    except OSError: stamp = None
    try: description_stamp = description.stat().st_mtime_ns
    except OSError: description_stamp = None
    key = (str(directory), stamp, description_stamp)
    cached = _METADATA_CACHE.get(key)
    if cached is not None:
        return dict(cached)
    value = load_json(meta_path, {})
    title = value.get("title") or value.get("name")
    if not title:
        title = next((line[1:].strip() for line in read_text(description).splitlines()
                      if line.startswith("#")), directory.name) if description.exists() else directory.name
    value.update({"id": exercise_id(directory), "title": title,
                  "difficulty": value.get("difficulty", "unspecified"),
                  "tags": value.get("tags", []), "order": value.get("order", 0),
                  "status": value.get("status", "active")})
    if len(_METADATA_CACHE) >= _CACHE_LIMIT: _METADATA_CACHE.clear()
    _METADATA_CACHE[key] = value
    return dict(value)


def discover(include_hidden: bool = False, include_disabled: bool = False) -> list[Path]:
    if not EXERCISES.exists():
        return []
    cache_key = (str(EXERCISES), include_hidden, include_disabled)
    now = time.monotonic()
    cached = _DISCOVERY_CACHE.get(cache_key)
    if cached is not None and now - cached[0] < _DISCOVERY_TTL:
        return list(cached[2])
    signature = exercises_signature()
    if cached is not None and cached[1] == signature:
        _DISCOVERY_CACHE[cache_key] = (now, signature, cached[2])
        return list(cached[2])
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
        # in one chapter (for example 02-basics/hello before dec-to-bin).
        prefix = path.relative_to(EXERCISES).parts[0].split("-", 1)[0]
        try:
            chapter = int(prefix)
        except ValueError:
            chapter = 10**9
        return chapter, int(metadata(path).get("order", 0) or 0), exercise_id(path).lower()
    ordered = sorted(found, key=sort_key)
    _DISCOVERY_CACHE[cache_key] = (now, signature, ordered)
    return list(ordered)


def find_exercise(value: str) -> Optional[Path]:
    candidates = discover(include_hidden=True)
    exact = [p for p in candidates if exercise_id(p) == value or p.name == value]
    if value.isdigit() and 1 <= int(value) <= len(candidates):
        return candidates[int(value) - 1]
    return exact[0] if exact else None


def require_exercise(value: str) -> Optional[Path]:
    """Resolve a user-supplied exercise id, reporting one consistent error."""
    target = find_exercise(value)
    if target is None:
        print(f"exercise not found: {value}", file=sys.stderr)
    return target


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


def compiler_setting() -> tuple[str, str]:
    """(configured compiler, where it came from): $CC wins over the config file."""
    environment = os.environ.get("CC", "").strip()
    if environment:
        return environment, "CC"
    from_config = str(settings().get("compiler", "") or "").strip()
    if from_config:
        return from_config, "config"
    return "", ""


def compiler_candidates() -> list[str]:
    """Compiler commands to try, in priority order."""
    configured, _source = compiler_setting()
    return ([configured] if configured else []) + ["gcc", "clang"]


def compiler() -> Optional[str]:
    """The compiler that grading will use, or None when none is installed."""
    for candidate in compiler_candidates():
        if candidate and shutil.which(candidate):
            return candidate
    return None


def compiler_version(command: str) -> str:
    """First line of <compiler> --version, best effort."""
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    lines = ((result.stdout or "") + (result.stderr or "")).strip().splitlines()
    return lines[0][:120] if lines else ""


def compiler_report() -> dict:
    """What doctor needs to explain the compiler situation."""
    configured, source = compiler_setting()
    found = []
    for candidate in compiler_candidates():
        path = shutil.which(candidate)
        if not path or any(item["path"] == path for item in found):
            continue
        found.append({"command": candidate, "path": path, "version": compiler_version(path)})
    effective = found[0] if found else {}
    warning = ""
    if configured and not shutil.which(configured):
        warning = (f"configured compiler not found: {configured} (from {source}); "
                   "falling back to gcc/clang")
    return {"effective": effective.get("command", ""), "path": effective.get("path", ""),
            "configured": configured, "configured_source": source,
            "candidates": found, "warning": warning}


def _split_flags(value: str) -> list[str]:
    try:
        return shlex.split(value)
    except ValueError:
        return value.split()


def compile_flags() -> tuple[list[str], str]:
    """Extra flags appended after the baseline ones, and where they came from."""
    environment = os.environ.get("CSTUDY_CFLAGS", "").strip()
    if environment:
        return _split_flags(environment), "CSTUDY_CFLAGS"
    from_config = str(settings().get("cflags", "") or "").strip()
    if from_config:
        return _split_flags(from_config), "config"
    fallback = os.environ.get("CFLAGS", "").strip()
    if fallback:
        return _split_flags(fallback), "CFLAGS"
    return [], ""


def compile_command(cc: str, sources: list[str], output: str) -> list[str]:
    """The single place that decides how an exercise is compiled.

    Baseline flags first, then user flags (so they can override the baseline),
    then -lm on the platforms that need it, then the output path.
    """
    extra, _source = compile_flags()
    command = [cc, "-std=c11", "-Wall", "-Wextra", "-O2", *sources, *extra]
    if os.name != "nt" and "-lm" not in extra:
        command.append("-lm")
    return command + ["-o", output]


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


#: Guard rail for runaway exercises on Windows, where there is no RLIMIT_AS.
WINDOWS_MEMORY_LIMIT = 512 * 1024 * 1024


def limit_process_memory(process: subprocess.Popen) -> Any:
    """Best-effort memory cap for one graded process on Windows.

    POSIX gets RLIMIT_AS in run_case; Windows has no equivalent call, so the child
    is assigned to a Job Object carrying a process memory limit plus
    kill-on-close. The assignment happens right after spawn, so a process could
    allocate inside that tiny window: this is a guard rail, not a sandbox.
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class BasicLimit(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.POINTER(ctypes.c_ulong)),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class ExtendedLimit(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimit), ("IoInfo", IoCounters),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        handle = getattr(process, "_handle", None)
        if not handle:
            return None
        kernel32 = ctypes.windll.kernel32
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return None
        info = ExtendedLimit()
        # JOB_OBJECT_LIMIT_PROCESS_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        info.BasicLimitInformation.LimitFlags = 0x0100 | 0x2000
        info.ProcessMemoryLimit = WINDOWS_MEMORY_LIMIT
        if not kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
            kernel32.CloseHandle(job)
            return None
        if not kernel32.AssignProcessToJobObject(job, int(handle)):
            kernel32.CloseHandle(job)
            return None
        return job
    except Exception:
        return None


def release_process_memory(job: Any) -> None:
    """Close a Job Object handle created by limit_process_memory."""
    if job is None:
        return
    try:
        import ctypes
        ctypes.windll.kernel32.CloseHandle(job)
    except Exception:
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
        job = limit_process_memory(process)
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
        release_process_memory(job)
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
        command = compile_command(cc, compile_sources, str(binary))
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
        command = compile_command(cc, names, str(binary))
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
    path = LOG_DIR / f"{time.strftime('%Y%m%d')}.jsonl"
    rotate_log(path)
    prune_logs()
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"timestamp": time.time(), **result}, ensure_ascii=False) + "\n")


def rotate_log(path: Path, limit: Optional[int] = None) -> None:
    """Keep one rotated copy per day file so a log cannot grow without bound."""
    if limit is None: limit = MAX_LOG_BYTES
    try:
        if path.exists() and path.stat().st_size >= limit:
            backup = path.with_name(path.name + ".1")
            if backup.exists(): backup.unlink()
            path.rename(backup)
    except OSError:
        pass


def prune_logs(days: int = LOG_RETENTION_DAYS) -> None:
    """Delete log files older than the retention window."""
    try:
        cutoff = time.time() - days * 86400
        for item in LOG_DIR.glob("*.jsonl*"):
            if item.stat().st_mtime < cutoff: item.unlink()
    except OSError:
        pass


def result_label(status: str) -> tuple[str, str]:
    """Shared label and colour for one grading status (CLI and watch screen)."""
    if status == "passed": return "PASS", "green"
    if status == "incomplete_marker": return "WARNING", "yellow"
    return "ERROR", "red"


def case_lines(case: dict, index: int, compact: bool = False) -> list[str]:
    """Render one test case for a log (compact=False) or the watch screen."""
    duration = case.get("duration_ms", 0)
    passed = bool(case.get("passed"))
    if compact:
        if passed:
            output = str(case.get("actual", "")).replace("\n", " | ")
            return [paint(f"  PASS case {index}", "green") + f"  {output}  {duration} ms"]
        lines = [paint(f"  FAIL case {index}", "red") +
                 f"  expected {case.get('expected', '')!r} | actual {case.get('actual', '')!r}  {duration} ms"]
        if case.get("error"): lines.append("    " + str(case["error"]))
        if case.get("stderr"): lines.append(paint("    stderr: " + str(case["stderr"]).strip()[:120], "yellow"))
        return lines
    lines = [f"  \u7528\u4f8b {index}: {'PASS' if passed else 'FAIL'} ({duration} ms)"]
    if not passed:
        if case.get("error"): lines.append(f"    \u9519\u8bef: {case['error']}")
        lines.append(f"    \u671f\u671b: {case['expected']!r}")
        lines.append(f"    \u5b9e\u9645: {case['actual']!r}")
    return lines


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
        for line in case_lines(case, number): print(line)


def result_summary(result: dict, failure_limit: int = 3) -> dict:
    """Bounded view of one grading result, safe to keep in the state file."""
    cases = result.get("cases") or []
    failures = []
    for index, case in enumerate(cases, 1):
        if case.get("passed"): continue
        failures.append({"case": index,
                         "input": str(case.get("input", ""))[:200],
                         "expected": str(case.get("expected", ""))[:400],
                         "actual": str(case.get("actual", ""))[:400],
                         "error": str(case.get("error", ""))[:120]})
        if len(failures) >= failure_limit: break
    summary = {"status": result.get("status", "error"),
               "duration_ms": result.get("duration_ms", 0),
               "cases": len(cases),
               "passed": sum(1 for case in cases if case.get("passed")),
               "failures": failures}
    if result.get("error"): summary["error"] = str(result["error"])[:300]
    stderr = (result.get("compile") or {}).get("stderr", "")
    if stderr: summary["compile_stderr"] = str(stderr)[:800]
    return summary


def record(directory: Path, result: dict, state: dict) -> None:
    source, _ = exercise_files(directory)
    item = state.setdefault("exercises", {}).setdefault(exercise_id(directory), {})
    item.update({"status": result["status"], "last_result": result_summary(result),
                 "at": time.strftime("%Y-%m-%d %H:%M:%S"),
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


def default_jobs(count: int) -> int:
    """Worker count for parallel grading: CPU count capped at 8, never above the task count."""
    if count <= 1: return 1
    return max(1, min(8, count, os.cpu_count() or 1))


def grade_many(targets: list[Path], timeout: float, total_timeout: float, max_output: int,
               jobs: int = 1) -> list[dict]:
    """Grade exercises, preserving the given order.

    Each grading run is an independent compile+run in its own temporary directory,
    so a thread pool gives near-linear speedup: the waiting happens in child
    processes and the GIL is released while they run.
    """
    if jobs <= 1 or len(targets) <= 1:
        return [grade(directory, timeout, total_timeout, max_output) for directory in targets]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(lambda directory: grade(directory, timeout, total_timeout, max_output), targets))


def target_list(args: argparse.Namespace) -> list[Path]:
    if getattr(args, "exercise", None):
        target = find_exercise(args.exercise)
        if target is None: raise ValueError(f"exercise not found: {args.exercise}")
        return [target]
    if getattr(args, "all", False):
        return discover()
    target = current_exercise_from_state(current_state(), discover())
    return [target] if target else []


def command_check(args: argparse.Namespace) -> int:
    current = current_state(); cfg = settings()
    try: targets = target_list(args)
    except ValueError as exc: print(str(exc), file=sys.stderr); return EXIT_USAGE
    if not targets:
        print("all exercises completed; use cstudy check --all to grade every exercise")
        return EXIT_OK
    if not getattr(args, "exercise", None) and not getattr(args, "all", False) and not args.json and not args.quiet:
        print("checking the current exercise; use cstudy check --all to grade the whole library")
    requested = getattr(args, "jobs", None)
    jobs = default_jobs(len(targets)) if requested is None else max(1, int(requested))
    if jobs > 1 and not args.json and not args.quiet:
        print(f"grading {len(targets)} exercises with {jobs} worker(s)")
    failures = 0; results: list[dict] = []
    graded = grade_many(targets, args.timeout or float(cfg["timeout_seconds"]),
                        args.total_timeout or float(cfg["total_timeout_seconds"]),
                        int(cfg["max_output_bytes"]), jobs)
    for directory, result in zip(targets, graded):
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
        requested = getattr(args, "jobs", None)
        jobs = default_jobs(len(all_items)) if requested is None else max(1, int(requested))
        timeout = float(getattr(args, "compile_timeout", 10.0))
        if jobs <= 1 or len(all_items) <= 1:
            compiled_items = [compile_only(directory, timeout) for directory in all_items]
        else:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                compiled_items = list(pool.map(lambda directory: compile_only(directory, timeout), all_items))
        for directory, compiled in zip(all_items, compiled_items):
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
    if exercise:
        target = require_exercise(exercise)
        if target is None: return EXIT_USAGE
    else:
        target = next((p for p in discover() if not is_done(p, current)), None)
    if target is None: print("all exercises completed"); return EXIT_OK
    set_current_exercise(target, current)
    print(f"next: {exercise_id(target)} - {metadata(target)['title']}"); return EXIT_OK


def command_move(args: argparse.Namespace, step: int) -> int:
    target = require_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    other = adjacent(target, step)
    if other is None: print("no adjacent exercise")
    else:
        set_current_exercise(other)
        print(f"{exercise_id(other)} - {metadata(other)['title']}")
    return EXIT_OK


def command_skip(args: argparse.Namespace) -> int:
    target = require_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    current = current_state(); current.setdefault("exercises", {}).setdefault(exercise_id(target), {})["status"] = "skipped"
    next_target = next((item for item in discover() if not is_done(item, current) and item != target), None)
    current["current"] = exercise_id(next_target) if next_target else exercise_id(target)
    save_state(current); print(f"skipped: {exercise_id(target)}"); return EXIT_OK


def command_status(args: argparse.Namespace) -> int:
    if not args.exercise: return command_list(argparse.Namespace(all=False, json=False))
    target = require_exercise(args.exercise)
    if target is None: return EXIT_USAGE
    print(json.dumps(current_state().get("exercises", {}).get(exercise_id(target), {}), ensure_ascii=False, indent=2)); return EXIT_OK


def command_edit(args: argparse.Namespace) -> int:
    target = require_exercise(args.exercise)
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
                    "G": "HOME", "O": "END", "S": "DELETE",
                    "I": "PGUP", "Q": "PGDN"}.get(code, "")
        if key == "\x1b":
            # Windows Terminal and some IDE consoles report ANSI arrows.
            sequence = ""
            deadline = time.monotonic() + 0.03
            while msvcrt.kbhit() and time.monotonic() < deadline:
                sequence += msvcrt.getwch()
            return {"[A": "UP", "[B": "DOWN", "[C": "RIGHT", "[D": "LEFT",
                    "[H": "HOME", "[F": "END", "[3~": "DELETE",
                    "[5~": "PGUP", "[6~": "PGDN"}.get(sequence, "ESC")
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
                "[H": "HOME", "[F": "END", "[3~": "DELETE",
                "[5~": "PGUP", "[6~": "PGDN"}.get(sequence, "ESC")
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
    completed = len(done_set(state, exercises)) if total else 0; filled = int(width * completed / total) if total else width
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


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size((80, 24))
    return max(12, size.lines), max(40, size.columns)


def fit_line(text: str, width: int) -> str:
    return console_ux.pad_to(console_ux.clip_visible(text, width), width)


def draw_frame(lines: list[str], width: int) -> None:
    """Redraw in place: home, overwrite every row, erase whatever is left."""
    parts = ["\x1b[H"]
    for index, line in enumerate(lines):
        parts.append("\x1b[K" + fit_line(line, width))
        if index < len(lines) - 1: parts.append("\n")
    parts.append("\x1b[J")
    sys.stdout.write("".join(parts)); sys.stdout.flush()


_RENDER_CACHE: dict[tuple, list[str]] = {}
_VIEWPORT_HEIGHT = 10
_VIEWPORT_MAX_SCROLL = 0


def rendered_description(target: Path, width: int) -> list[str]:
    """Markdown-rendered description, cached until the file or width changes."""
    description = target / "description.md"
    if not description.exists(): return []
    try: stamp = description.stat().st_mtime_ns
    except OSError: stamp = 0
    key = (str(description), stamp, width)
    cached = _RENDER_CACHE.get(key)
    if cached is not None: return cached
    lines = console_ux.render_markdown(read_text(description), width=width).split("\n")
    if len(_RENDER_CACHE) > 16: _RENDER_CACHE.clear()
    _RENDER_CACHE[key] = lines
    return lines


def hint_block(target: Path, result: Optional[dict], width: int) -> list[str]:
    """Hint view: the description hint section plus one concrete case."""
    lines = rendered_description(target, width)
    start = next((index for index, line in enumerate(lines) if line.strip().startswith("\u63d0\u793a")), None)
    block = list(lines[start:] if start is not None else lines)
    case = next((item for item in (result or {}).get("cases", []) if not item.get("passed")), None)
    if case is None:
        _, tests = exercise_files(target)
        parsed = parse_tests(tests) if tests else []
        case = {"input": parsed[0].input, "expected": parsed[0].expected, "passed": False} if parsed else None
    if case is not None:
        def flat(value) -> str:
            text = str(value if value is not None else "")
            return text.replace("\n", " | ") or "<\u7a7a>"
        block += ["", paint("\u7b2c\u4e00\u4e2a\u7528\u4f8b\uff1a", "yellow"),
                  "  \u8f93\u5165: " + flat(case.get("input")),
                  "  \u671f\u671b: " + flat(case.get("expected"))]
        if not case.get("passed", True):
            block.append("  \u5b9e\u9645: " + flat(case.get("actual")))
    return block


def result_lines(result: Optional[dict], width: int) -> list[str]:
    """Compact grading result: one line per case, details only for failures."""
    if not result: return []
    status = result.get("status", "pending")
    label, colour = result_label(status)
    cases = result.get("cases") or []
    passed = sum(1 for case in cases if case.get("passed"))
    lines = [paint(f"{label} {status} ({result.get('duration_ms', 0)} ms)  {passed}/{len(cases)} cases passed", colour)]
    if result.get("error"): lines.append(paint(str(result["error"]), "yellow"))
    stderr = (result.get("compile") or {}).get("stderr", "")
    if stderr:
        lines.extend(paint("  " + line, "yellow") for line in stderr.rstrip().split("\n")[:3])
    for index, case in enumerate(cases, 1):
        lines.extend(case_lines(case, index, compact=True))
    return lines


def keys_line(width: int) -> str:
    full = "[n] \u4e0b\u4e00\u9898  [r] \u91cd\u8dd1  [h] \u63d0\u793a  [e] \u7f16\u8f91  [a] AI \u5bf9\u8bdd  [l] \u5217\u8868  [x] \u91cd\u7f6e  [:] \u547d\u4ee4  [q] \u9000\u51fa  [\u2191\u2193 PgUp/PgDn] \u9898\u9762"
    short = "[n] \u4e0b\u4e00\u9898  [r] \u91cd\u8dd1  [h] \u63d0\u793a  [:] \u547d\u4ee4  [q] \u9000\u51fa"
    return full if console_ux.visible_width(full) <= width else short


def last_status_line(result: Optional[dict]) -> str:
    if not result: return paint("\u5c31\u7eea \u00b7 \u6309 r \u91cd\u65b0\u5224\u5b9a", "dim")
    cases = result.get("cases") or []
    passed = sum(1 for case in cases if case.get("passed"))
    stamp = result.get("at") or time.strftime("%H:%M:%S")
    return paint(f"\u4e0a\u6b21\u5224\u5b9a {stamp}  {passed}/{len(cases)} \u7528\u4f8b\u901a\u8fc7  {result.get('duration_ms', 0)} ms", "dim")


WATCH_COMMANDS = [
    ("/help", "\u663e\u793a\u547d\u4ee4\u4e0e\u5feb\u6377\u952e", False),
    ("/hint", "\u9898\u9762/\u63d0\u793a\u5207\u6362", False),
    ("/next", "\u8df3\u5230\u4e0b\u4e00\u9053\u672a\u5b8c\u6210\u9898", False),
    ("/run", "\u7acb\u5373\u91cd\u65b0\u7f16\u8bd1\u5224\u5b9a", False),
    ("/list", "\u6253\u5f00\u7ec3\u4e60\u5217\u8868", False),
    ("/goto", "\u8df3\u5230\u6307\u5b9a\u9898\u76ee", True),
    ("/skip", "\u8df3\u8fc7\u5f53\u524d\u9898\u5e76\u524d\u8fdb", False),
    ("/reset", "\u6062\u590d\u521d\u59cb\u4ee3\u7801", False),
    ("/edit", "\u7528\u7f16\u8f91\u5668\u6253\u5f00 Ques.c", False),
    ("/ai", "\u5c31\u5f53\u524d\u9898\u5f00\u542f AI \u5bf9\u8bdd", False),
    ("/follow", "\u5f00\u5173\u201c\u8ddf\u968f\u6700\u8fd1\u7f16\u8f91\u7684\u6587\u4ef6\u201d", False),
    ("/quit", "\u9000\u51fa\u5b66\u4e60\u754c\u9762", False),
]

#: One-letter aliases accepted in the command prompt (the plain keys use these too).
WATCH_ALIASES = {"h": "hint", "n": "next", "r": "run", "l": "list", "s": "skip",
                 "x": "reset", "e": "edit", "a": "ai", "f": "follow", "q": "quit",
                 "?": "help"}

#: Verbs the watch screen can execute; WATCH_COMMANDS must stay a subset of this.
WATCH_ACTIONS = {"help", "hint", "next", "run", "list", "goto", "skip", "reset",
                 "edit", "ai", "follow", "quit"}


def parse_watch_command(text: str) -> tuple[str, str]:
    """Split a typed command into (verb, argument), mapping aliases to verbs.

    Accepts "/hint", ":hint", "hint" and the one-letter aliases, so the prompt can
    be driven by full commands or by the same letters the single keys use.
    """
    cleaned = text.strip().lstrip(":").lstrip("/").strip()
    if not cleaned: return "", ""
    parts = cleaned.split(None, 1)
    verb = parts[0].lower()
    argument = parts[1].strip() if len(parts) > 1 else ""
    return WATCH_ALIASES.get(verb, verb), argument


def latest_modified_exercise(exercises: list[Path]) -> Optional[Path]:
    """Exercise whose source file was modified most recently (follow mode)."""
    newest: Optional[Path] = None; newest_stamp = -1
    for directory in exercises:
        source, _ = exercise_files(directory)
        if source is None: continue
        try: stamp = source.stat().st_mtime_ns
        except OSError: continue
        if stamp > newest_stamp: newest, newest_stamp = directory, stamp
    return newest


def normalise_exercise_hint(text: str) -> str:
    """Turn an editor-supplied path or id into an exercise id.

    Accepts "02-basics/hello", "Exercises/02-basics/hello", an absolute path to
    the exercise directory or to its Ques.c, and Windows separators.
    """
    cleaned = text.strip().strip('"').replace("\\", "/")
    if "/Exercises/" in cleaned:
        cleaned = cleaned.split("/Exercises/", 1)[1]
    elif cleaned.startswith("Exercises/"):
        cleaned = cleaned[len("Exercises/"):]
    for suffix in ("/Ques.c", "/Ques.c.bak"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
    return cleaned.strip("/")


def active_file_exercise(path: Path) -> Optional[Path]:
    """Exercise named by the editor hook file (default .cstudy/active)."""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    hint = normalise_exercise_hint(text)
    return find_exercise(hint) if hint else None


def follow_target(exercises: list[Path], target: Path, source: Optional[Path],
                  last_stamp: int) -> Optional[Path]:
    """Exercise whose file was edited most recently, if it is newer than ours.

    The stamp guard keeps the screen from bouncing between two files when both
    were touched recently.
    """
    candidate = latest_modified_exercise(exercises)
    if candidate is None or candidate == target:
        return None
    candidate_source, _ = exercise_files(candidate)
    try: candidate_stamp = candidate_source.stat().st_mtime_ns if candidate_source else 0
    except OSError: candidate_stamp = 0
    try: current_stamp = source.stat().st_mtime_ns if source else 0
    except OSError: current_stamp = 0
    if candidate_stamp > current_stamp and candidate_stamp != last_stamp:
        return candidate
    return None


def watch_help_lines() -> list[str]:
    """Body shown by the help command: commands first, then the key shortcuts."""
    lines = [paint("\u547d\u4ee4\uff08\u6309 : \u6216 / \u6253\u5f00\u547d\u4ee4\u63d0\u793a\u7b26\uff0c\u56de\u8f66\u6267\u884c\uff1b\u8f93\u5165 / \u53ef\u8865\u5168\uff09", "cyan"), ""]
    for name, description, takes_argument in WATCH_COMMANDS:
        lines.append("  " + name.ljust(10) + ("<arg>  " if takes_argument else "       ") + description)
    lines += ["", paint("\u5355\u952e\u5feb\u6377\u65b9\u5f0f", "cyan"), "",
              "  n \u4e0b\u4e00\u9898   r \u91cd\u65b0\u5224\u5b9a   h \u9898\u9762/\u63d0\u793a   e \u7f16\u8f91   s \u8df3\u8fc7   a AI \u5bf9\u8bdd",
              "  l \u5217\u8868   x \u91cd\u7f6e   f \u8ddf\u968f\u5f00\u5173   q \u9000\u51fa   \u2191\u2193/j k \u6eda\u52a8   PgUp/PgDn \u7ffb\u9875   g/G \u9996\u5c3e"]
    return lines


def watch_command_prompt() -> Optional[str]:
    """One-line command prompt with completion, drawn over the status row."""
    editor = console_ux.LineEditor(prompt="/", commands=WATCH_COMMANDS)
    editor.buffer = "/"; editor.caret = 1

    def draw() -> None:
        _rows, cols = terminal_size()
        status_row = max(1, _rows - 1)
        menu = (console_ux.menu_rows(WATCH_COMMANDS, editor.buffer, editor.menu_index, cols)
                if editor.buffer.startswith("/") else [])
        parts = []
        top = max(1, status_row - len(menu))
        for index, line in enumerate(menu):
            row = top + index
            if row >= status_row: break
            parts.append(f"\x1b[{row};1H\x1b[K" + fit_line(line, cols))
        parts.append(f"\x1b[{status_row};1H\x1b[K" + fit_line(":" + editor.buffer, cols))
        parts.append(f"\x1b[{status_row};{min(cols, editor.caret + 2)}H")
        sys.stdout.write("".join(parts)); sys.stdout.flush()

    draw()
    while True:
        action, submitted = editor.feed(read_key(0.1))
        if action == "submit": return submitted
        if action in {"cancel", "interrupt", "exit"}: return None
        if action: draw()


def build_watch_frame(target: Path, state: dict, exercises: list[Path], result: Optional[dict],
                      hint: bool, scroll: int, status: str, follow: bool = True,
                      show_help: bool = False) -> list[str]:
    """Fixed header, scrollable body, compact result block, fixed footer."""
    global _VIEWPORT_HEIGHT, _VIEWPORT_MAX_SCROLL
    rows, cols = terminal_size()
    bar_width = max(18, min(48, cols - 30))
    title = paint(f"CStudy {VERSION}  |  C \u8bed\u8a00\u7ec3\u4e60", "cyan")
    badge = paint("[跟随]" if follow else "[跟随:关]", "dim")
    gap = max(1, cols - console_ux.visible_width(title) - console_ux.visible_width(badge))
    header = [title + " " * gap + badge,
              paint(progress_bar(state, exercises, bar_width), "bold"),
              f"\u5f53\u524d: {paint(exercise_id(target), 'bold')}  {metadata(target)['title']} [{progress_status(target, state)}]"]
    source, _ = exercise_files(target)
    if source: header.append("\u6e90\u7801: " + hyperlink(source))

    if show_help: body = watch_help_lines()
    elif hint: body = hint_block(target, result, cols)
    else: body = rendered_description(target, cols)
    result_block = result_lines(result, cols)
    footer = [status, keys_line(cols)]
    fixed = len(header) + len(footer) + 1 + (1 if result_block else 0)
    room = max(3, rows - fixed)
    if result_block:
        result_height = min(len(result_block), max(2, room // 2))
        body_height = max(1, room - result_height)
    else:
        result_height = 0
        body_height = room

    total_body = len(body)
    max_scroll = max(0, total_body - body_height)
    scroll = max(0, min(scroll, max_scroll))
    _VIEWPORT_HEIGHT = body_height
    _VIEWPORT_MAX_SCROLL = max_scroll
    window = body[scroll:scroll + body_height]

    label = "\u5e2e\u52a9" if show_help else ("\u63d0\u793a" if hint else "\u9898\u9762")
    if max_scroll:
        span = f"{scroll + 1}-{scroll + len(window)}/{total_body} \u884c  PgUp/PgDn \u7ffb\u9875"
    else:
        span = f"{total_body} \u884c"
    lines = list(header)
    lines.append(paint("-" * max(1, cols - console_ux.visible_width(span) - 4) + f" {label} {span} ", "dim"))
    lines.extend(window + [""] * (body_height - len(window)))
    if result_height:
        lines.append(paint("-" * cols, "dim"))
        shown = result_block[:result_height]
        if len(result_block) > result_height:
            shown = shown[:-1] + [paint(f"  \u2026 \u8fd8\u6709 {len(result_block) - result_height + 1} \u884c\u7ed3\u679c", "dim")]
        lines.extend(shown + [""] * (result_height - len(shown)))
    lines.extend(footer)
    return lines[:rows]


def render_watch_screen(target: Path, result: Optional[dict], hint: bool = False, scroll: int = 0,
                        follow: bool = True, show_help: bool = False,
                        status: Optional[str] = None) -> None:
    state = current_state(); exercises = discover()
    _rows, cols = terminal_size()
    draw_frame(build_watch_frame(target, state, exercises, result, hint, scroll,
                                 status if status is not None else last_status_line(result),
                                 follow, show_help), cols)


def spin_status(stop: threading.Event, row: int, label: str) -> None:
    """Animate the pinned status row while a blocking grading run is in flight."""
    started = time.monotonic()
    while not stop.is_set():
        elapsed = time.monotonic() - started
        frame = paint(console_ux.spinner_frame(elapsed), "cyan")
        line = f"{frame} {label} ({elapsed:.1f}s)"
        try:
            _rows, cols = terminal_size()
            sys.stdout.write(f"\x1b[{max(1, row)};1H\x1b[K" + fit_line(line, cols))
            sys.stdout.flush()
        except (OSError, ValueError):
            return
        stop.wait(0.08)


def list_tui() -> Optional[Path]:
    exercises = discover(include_hidden=True); state = current_state(); mode = "all"; query = ""
    current_id = state.get("current")
    selected = next((index for index, item in enumerate(exercises) if exercise_id(item) == current_id), 0)
    def visible():
        done = done_set(state, exercises)
        return [p for p in exercises if (mode == "all" or (mode == "done" and exercise_id(p) in done) or (mode == "pending" and exercise_id(p) not in done)) and (not query or query.lower() in (exercise_id(p) + " " + metadata(p)["title"]).lower())]
    dirty = True
    with raw_terminal():
        while True:
            items = visible(); selected = min(selected, max(0, len(items) - 1))
            if dirty:
                rows, cols = terminal_size()
                done = done_set(state, exercises)
                height = max(5, rows - 4)
                start = max(0, min(selected - height // 2, len(items) - height))
                end = min(len(items), start + height)
                header = ["CStudy \u7ec3\u4e60\u5217\u8868  (j/k \u79fb\u52a8, d/p \u7b5b\u9009, s \u641c\u7d22, Enter \u9009\u62e9, q \u8fd4\u56de)",
                          paint(f"\u5df2\u5b8c\u6210 {len(done)}/{len(exercises)} \u00b7 \u7b5b\u9009={mode}" +
                                (f" \u00b7 \u641c\u7d22={query}" if query else ""), "dim")]
                body: list[str] = []
                if start > 0: body.append(paint("... more above ...", "dim"))
                id_width = min(30, max(18, cols // 2 - 6))
                for index, item in enumerate(items[start:end], start):
                    meta = metadata(item)
                    mark = "DONE" if exercise_id(item) in done else "    "
                    cursor = ">" if index == selected else " "
                    row = f"{cursor} {index + 1:>3}. [{mark}] " + console_ux.pad_to(exercise_id(item), id_width)
                    body.append(row + f" {meta['title']} [{meta['difficulty']}]")
                if end < len(items): body.append(paint("... more below ...", "dim"))
                clear_screen()
                for line in header + body: print(fit_line(line, cols))
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
    result: dict = {}; hint = False; show_help = False; scroll = 0; previous = 0
    dirty = True
    follow = not getattr(args, "no_follow", False)
    active_path = Path(getattr(args, "active_file", None) or (STATE_DIR / "active"))
    followed_stamp = 0; last_scan = 0.0
    note = ""; note_until = 0.0

    def run_current() -> None:
        nonlocal result, previous
        stop = threading.Event(); thread = None
        if sys.stdout.isatty():
            _rows, _cols = terminal_size()
            thread = threading.Thread(target=spin_status, args=(stop, _rows - 1, "\u7f16\u8bd1\u5224\u5b9a\u4e2d"), daemon=True)
            thread.start()
        try:
            result = grade(target, args.timeout, args.total_timeout, int(settings()["max_output_bytes"]))
        finally:
            stop.set()
            if thread is not None: thread.join(timeout=0.5)
        result["at"] = time.strftime("%H:%M:%S")
        log_result(result); current = current_state(); record(target, result, current); save_state(current)
        previous = source.stat().st_mtime_ns

    def select(target_path: Path, open_in_editor: bool = True) -> None:
        nonlocal target, source, scroll
        target = target_path; source, _ = exercise_files(target); assert source
        scroll = 0; set_current_exercise(target)
        if open_in_editor: open_editor(source, args)
        run_current()

    def move_next() -> bool:
        if result.get("status") != "passed":
            return False
        next_target = next((item for item in discover() if not is_done(item, current_state()) and item != target), None)
        if next_target is None:
            return False
        select(next_target)
        return True

    def set_note(text: str, seconds: float = 5.0) -> None:
        nonlocal note, note_until
        note = text; note_until = time.monotonic() + seconds

    def status_text() -> Optional[str]:
        if note and time.monotonic() < note_until: return paint(note, "yellow")
        return None

    def dispatch(verb: str, argument: str = "") -> bool:
        """Run one action; returns False when the watch screen should exit.

        Both the single keys and the typed commands go through here, so the two
        input styles can never drift apart.
        """
        nonlocal hint, show_help, dirty, follow, target
        if verb in {"quit", "exit"}: return False
        if verb == "help":
            show_help = True; dirty = True
        elif verb == "hint":
            hint = not hint; show_help = False; dirty = True
        elif verb == "next":
            if not move_next(): set_note("\u5f53\u524d\u9898\u8fd8\u6ca1\u901a\u8fc7\uff0c\u5148\u628a\u5b83\u505a\u5bf9\uff08\u6216\u7528 skip\uff09")
            dirty = True
        elif verb == "run":
            run_current(); dirty = True
            if move_next(): dirty = True
        elif verb == "list":
            chosen = list_tui()
            if chosen: select(chosen); dirty = True
        elif verb == "goto":
            if not argument:
                set_note("\u7528\u6cd5\uff1agoto <\u9898\u53f7\u6216\u7f16\u53f7>\uff0c\u4f8b\u5982 goto 12")
            else:
                found = find_exercise(argument)
                if found is None: set_note(f"\u627e\u4e0d\u5230\u9898\u76ee\uff1a{argument}")
                else: select(found); set_note(f"\u5df2\u5207\u6362\u5230 {exercise_id(found)}")
            dirty = True
        elif verb == "skip":
            current = current_state()
            current.setdefault("exercises", {}).setdefault(exercise_id(target), {})["status"] = "skipped"
            save_state(current)
            next_target = next((item for item in discover() if not is_done(item, current) and item != target), None)
            if next_target is None: set_note("\u6ca1\u6709\u5176\u4ed6\u672a\u5b8c\u6210\u9898\u4e86"); dirty = True
            else: select(next_target); set_note(f"\u5df2\u8df3\u8fc7\uff0c\u5207\u5230 {exercise_id(next_target)}"); dirty = True
        elif verb == "reset":
            answer = read_line("\nReset this exercise? [y/N] ")
            if answer.lower() == "y":
                backup = target / "Ques.c.bak"
                if backup.exists(): shutil.copyfile(backup, source)
                current = current_state(); current.setdefault("exercises", {}).pop(exercise_id(target), None); save_state(current)
                run_current(); set_note("\u5df2\u6062\u590d\u521d\u59cb\u4ee3\u7801")
            dirty = True
        elif verb == "edit":
            if not open_editor(source, args): set_note("\u6ca1\u6709\u914d\u7f6e\u7f16\u8f91\u5668\uff08\u8bbe\u7f6e CSTUDY_EDIT_CMD/EDITOR\uff09")
        elif verb == "ai":
            # The alternate screen keeps no history, so run the chat in the normal
            # buffer where the transcript can be scrolled back.
            leave_alternate_screen()
            code = chat_session(target, timeout=float(getattr(args, "ai_timeout", 60.0)), opening=HINT_REQUEST)
            if code != EXIT_OK: read_line("\nPress Enter to return...")
            enter_alternate_screen()
            dirty = True
        elif verb == "follow":
            follow = not follow
            set_note("\u8ddf\u968f\u5f00\u5173\uff1a" + ("\u5f00" if follow else "\u5173"))
            dirty = True
        else:
            set_note(f"\u672a\u77e5\u547d\u4ee4\uff1a{verb}\uff08\u8f93\u5165 help \u67e5\u770b\u5168\u90e8\uff09")
        return True

    run_current(); open_editor(source, args); move_next()
    try:
        with alternate_screen(), raw_terminal():
            while True:
                rows, cols = terminal_size()
                if dirty:
                    render_watch_screen(target, result, hint, scroll, follow, show_help, status_text())
                    dirty = False
                key = read_key(getattr(args, "interval", .1))
                exiting = False
                if key in {"q", "CTRL-C"}:
                    exiting = True
                elif key in {"PGDN", "j", "DOWN"}:
                    step = _VIEWPORT_HEIGHT if key == "PGDN" else 1
                    scroll = min(scroll + step, _VIEWPORT_MAX_SCROLL); dirty = True
                elif key in {"PGUP", "k", "UP"}:
                    step = _VIEWPORT_HEIGHT if key == "PGUP" else 1
                    scroll = max(0, scroll - step); dirty = True
                elif key in {"g", "HOME"}:
                    scroll = 0; dirty = True
                elif key in {"G", "END"}:
                    scroll = _VIEWPORT_MAX_SCROLL; dirty = True
                elif key in {":", "/"}:
                    typed = watch_command_prompt()
                    if typed:
                        verb, argument = parse_watch_command(typed)
                        if verb and not dispatch(verb, argument): exiting = True
                    dirty = True
                elif key and key in WATCH_ALIASES:
                    if not dispatch(WATCH_ALIASES[key]): exiting = True
                if exiting:
                    clear_screen(); print("CStudy stopped."); return EXIT_OK
                if source.stat().st_mtime_ns != previous:
                    run_current(); dirty = True
                    if result.get("status") == "passed" and move_next(): dirty = True
                if note and time.monotonic() >= note_until:
                    note = ""; dirty = True
                now = time.monotonic()
                if now - last_scan > 0.5:
                    last_scan = now
                    # an explicit editor hook (.cstudy/active) wins over mtime
                    chosen = active_file_exercise(active_path)
                    if chosen is None and follow:
                        chosen = follow_target(discover(), target, source, followed_stamp)
                        if chosen is not None:
                            candidate_source, _ = exercise_files(chosen)
                            try: followed_stamp = candidate_source.stat().st_mtime_ns if candidate_source else 0
                            except OSError: followed_stamp = 0
                    if chosen is not None and chosen != target:
                        select(chosen, open_in_editor=False)
                        set_note(f"\u5df2\u8ddf\u968f\u5230 {exercise_id(chosen)}")
                        dirty = True
    except KeyboardInterrupt:
        clear_screen(); print("CStudy stopped."); return EXIT_OK


def command_watch(args: argparse.Namespace) -> int:
    target = require_exercise(args.exercise) if args.exercise else None
    if args.exercise and target is None: return EXIT_USAGE
    if target is None:
        state = current_state()
        target = next((item for item in discover() if not is_done(item, state)), None)
    if target is None:
        print("all exercises completed"); return EXIT_OK
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
    compilers = compiler_report()
    extra_flags, flags_source = compile_flags()
    invalid = []
    for directory in exercises:
        source, tests = exercise_files(directory)
        if source is None or tests is None or not (directory / "description.md").exists() or not (directory / "Ques.c.bak").exists():
            invalid.append(exercise_id(directory))
    report = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "compiler": compilers["effective"],
        "compiler_path": compilers["path"],
        "compiler_configured": compilers["configured"],
        "compiler_candidates": compilers["candidates"],
        "compile_flags": extra_flags,
        "compile_flags_source": flags_source,
        "links_libm": os.name != "nt",
        "exercise_count": len(exercises),
        "invalid_exercises": invalid,
        "api_configured": bool(ai_cfg["api_key"]),
        "api_base": ai_cfg["api_base"],
        "ai_model": ai_cfg["model"],
        "status": "ready" if compilers["effective"] and exercises and not invalid else "not_ready",
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"platform: {report['platform']}")
        print(f"python: {report['python']}")
        print(f"compiler: {report['compiler'] or '(none found)'}")
        for item in report["compiler_candidates"]:
            print(f"  candidate: {item['command']} -> {item['path']}  [{item['version']}]")
        flags = " ".join(report["compile_flags"]) or "(none)"
        print(f"compile_flags: {flags}" + (f"  (from {flags_source})" if flags_source else ""))
        print(f"links_libm: {report['links_libm']}")
        print(f"exercise_count: {report['exercise_count']}")
        print(f"invalid_exercises: {report['invalid_exercises']}")
        print(f"api_configured: {report['api_configured']}")
        print(f"api_base: {report['api_base']}")
        print(f"ai_model: {report['ai_model']}")
        print(f"status: {report['status']}")
        if compilers["warning"]:
            print("warning: " + compilers["warning"])
        if not report["api_configured"]:
            print("note: API AI is optional; run `cstudy ai --setup` to configure it")
    return EXIT_OK if report["status"] == "ready" else EXIT_FAILED


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


def chat_system_prompt(target: Path) -> str:
    """Conversation context: the exercise, the student's code, and the last result."""
    source, tests = exercise_files(target)
    previous = current_state().get("exercises", {}).get(exercise_id(target), {}).get("last_result", {})
    description = target / "description.md"
    return build_chat_system_prompt(
        exercise_id(target), metadata(target)["title"],
        read_text(description) if description.exists() else "",
        read_text(source) if source is not None else "",
        read_text(tests) if tests is not None else "",
        previous)


@dataclass
class ChatState:
    """Mutable conversation state shared by the chat helpers below.

    Kept as one object so chat_session stays a readable input loop instead of a
    300-line function closing over twenty locals.
    """

    target: Path
    console: Any
    messages: list
    work: "queue.Queue[tuple]"
    pending: list
    base_url: str
    api_key: str
    model: str
    api_mode: str
    timeout: float
    width: int
    raw: bool
    stream: bool
    show_thinking: bool = True
    active: bool = False
    cancel_event: Optional[threading.Event] = None
    response_slot: dict = field(default_factory=dict)
    started: float = 0.0
    tokens: int = 0
    answer: str = ""
    reasoning: str = ""
    last_answer: str = ""
    thinking: Any = None
    last_transcript: float = 0.0
    worker: Optional[threading.Thread] = None


def chat_start_request(state: ChatState, question: str) -> None:
    """Start one assistant turn in the background; results arrive on state.work."""
    state.thinking = None
    state.messages.append({"role": "user", "content": question})
    state.cancel_event = threading.Event()
    state.started = time.monotonic()
    state.tokens = 0
    state.answer = ""
    state.reasoning = ""
    state.response_slot.clear()
    state.active = True
    state.console.note("思考中...")
    model, api_mode = state.model, state.api_mode

    def on_delta(piece: str) -> None:
        state.work.put(("delta", piece))

    def on_reasoning(piece: str) -> None:
        state.work.put(("reasoning", piece))

    def on_open(response) -> None:
        state.response_slot["response"] = response

    def run() -> None:
        try:
            text = ai_request(state.base_url, state.api_key, model, api_mode, list(state.messages),
                              state.timeout, stream=state.stream, on_delta=on_delta,
                              on_reasoning=on_reasoning, cancel=state.cancel_event,
                              on_open=on_open, retries=1)
            state.work.put(("done", text))
        except AiCancelled:
            state.work.put(("cancelled", ""))
        except AiRequestError as exc:
            state.work.put(("error", exc.lines))

    state.worker = threading.Thread(target=run, daemon=True)
    state.worker.start()


def chat_interrupt(state: ChatState) -> None:
    """Stop the in-flight turn; silent when nothing is running."""
    if not state.active:
        return
    if state.cancel_event is not None:
        state.cancel_event.set()
    response = state.response_slot.get("response")
    if response is not None:
        try:
            response.close()
        except OSError:
            pass
    state.console.print_above(console_ux.paint("✗ 已中断", "yellow"))


def chat_handle_command(state: ChatState, line: str) -> Optional[str]:
    """Handle one slash command; returns "exit" when the session should end."""
    command, _, argument = line.partition(" ")
    command = command.lower()
    console = state.console
    if command in {"/exit", "/quit", "/q"}:
        return "exit"
    if command in {"/help", "/?"}:
        console.print_above(CHAT_HELP)
    elif command == "/hint":
        state.pending.append(HINT_REQUEST)
    elif command == "/clear":
        del state.messages[1:]
        console.print_above("已清空上下文")
    elif command in {"/code", "/result"}:
        state.messages[0] = {"role": "system", "content": chat_system_prompt(state.target)}
        console.print_above("已重新载入 Ques.c 与最近判定结果")
    elif command == "/thinking":
        state.show_thinking = not state.show_thinking
        if not state.show_thinking and state.thinking is not None:
            state.thinking.flush()
            state.thinking = None
        console.print_above("思考过程写入对话" if state.show_thinking else "只保留思考小结")
    elif command == "/model":
        if argument.strip():
            state.model = argument.strip()
        console.print_above("模型: " + state.model)
    elif command == "/raw":
        state.raw = not state.raw
        console.print_above("原始 Markdown" if state.raw else "渲染后 Markdown")
    elif command == "/stream":
        state.stream = not state.stream
        console.print_above("流式接收" if state.stream else "非流式")
    elif command == "/save":
        name = argument.strip() or "ai-answer.md"
        try:
            (ROOT / name).write_text(state.last_answer, encoding="utf-8")
            console.print_above(f"已保存到 {name}")
        except OSError as exc:
            console.print_above(f"无法保存 {name}: {exc}")
    else:
        console.print_above(f"未知命令: {command}（输入 /help 查看）")
    return None


def chat_drain_work(state: ChatState) -> None:
    """Apply everything the worker produced; safe to call before leaving."""
    console = state.console
    while True:
        try:
            kind, payload = state.work.get_nowait()
        except queue.Empty:
            break
        if kind == "delta":
            state.answer += payload
            state.tokens += 1
            if state.thinking is not None:
                # the answer starts: close the thinking block above it
                state.thinking.flush()
                state.thinking = None
        elif kind == "reasoning":
            state.reasoning += payload
            state.tokens += 1
            if state.show_thinking:
                if state.thinking is None:
                    console.print_above(console_ux.paint("✻ 思考中", "dim"))
                    state.thinking = console_ux.StreamingBlock(console, style="dim", prefix="  ")
                state.thinking.feed(payload)
                state.last_transcript = time.monotonic()
        elif kind == "done":
            state.active = False
            state.last_answer = payload
            state.messages.append({"role": "assistant", "content": payload})
            if state.thinking is not None:
                state.thinking.flush()
                state.thinking = None
            if state.reasoning:
                elapsed = time.monotonic() - state.started
                hint = "/thinking 隐藏" if state.show_thinking else "/thinking 展开"
                console.print_above(console_ux.paint(
                    "✻ 思考 %.1f 秒（%d 字符） · %s" % (elapsed, len(state.reasoning), hint), "dim"))
            console.print_above("")
            if state.raw or not sys.stdout.isatty():
                console.print_above(payload.rstrip())
            else:
                console.print_above(console_ux.render_markdown(payload.rstrip(), width=state.width))
        elif kind == "cancelled":
            state.active = False
            state.messages.pop()
            if state.thinking is not None:
                state.thinking.flush()
                state.thinking = None
            console.print_above(console_ux.paint("已中断，本轮已丢弃", "yellow"))
        elif kind == "error":
            state.active = False
            state.messages.pop()
            if state.thinking is not None:
                state.thinking.flush()
                state.thinking = None
            for text in payload:
                console.print_above(console_ux.paint(text, "red"))


def chat_session(target: Path, timeout: float = 60.0, stream: bool = True,
                 raw: bool = False, opening: Optional[str] = None) -> int:
    """Multi-turn console conversation; the input line stays live while work runs."""
    ai_cfg = ai_configuration()
    if not ai_cfg["api_key"]:
        print_ai_setup_help()
        if not (sys.stdin.isatty() and sys.stdout.isatty()) or not configure_ai():
            return 4
        ai_cfg = ai_configuration()
    base_url = ai_cfg["api_base"].rstrip("/")
    api_mode = ai_cfg["mode"]
    if "api.deepseek.com" in base_url.lower() and api_mode == "responses":
        print("DeepSeek 配置错误：它的 OpenAI 兼容接口使用 chat 模式。", file=sys.stderr)
        print("请把 ai_api_mode 改为 chat，或重新运行 AI 配置并选择 DeepSeek。", file=sys.stderr)
        print(f"预期端点: {base_url}/chat/completions", file=sys.stderr)
        return 4

    width = console_ux.terminal_width()
    print(console_ux.paint(f"对话: {exercise_id(target)} - {metadata(target)['title']}", "bold", "cyan"))
    print(console_ux.paint("请求进行时 Enter 排队，Esc 中断，/help 列出命令。", "dim"))

    interactive = interactive_terminal()
    reader: Optional[console_ux.InputReader] = None
    if interactive:
        reader = console_ux.InputReader(read_key, console_ux.LineEditor(commands=CHAT_COMMANDS))
        console: Any = console_ux.LiveConsole(hint="Enter 排队 · Esc 中断 · /help",
                                              restore_hidden_cursor=_ALTERNATE_SCREEN)
        reader.start()
    else:
        console = console_ux.PlainConsole()

    state = ChatState(target=target, console=console,
                      messages=[{"role": "system", "content": chat_system_prompt(target)}],
                      work=queue.Queue(), pending=[opening] if opening else [],
                      base_url=base_url, api_key=ai_cfg["api_key"], model=ai_cfg["model"],
                      api_mode=api_mode, timeout=timeout, width=width, raw=raw, stream=stream)

    def plain_events() -> list[tuple]:
        try:
            line = read_line(console_ux.paint("\n› ", "cyan"))
        except (EOFError, KeyboardInterrupt):
            return [("exit", "")]
        return [("submit", line)] if line else []

    try:
        while True:
            # 1. drain streamed output and finish the turn
            chat_drain_work(state)

            # 2. a queued message starts as soon as the previous turn finishes
            if not state.active and state.pending:
                chat_start_request(state, state.pending.pop(0))

            # 3. fall back to line input if raw keys are unavailable
            if reader is not None and reader.failed:
                reader.stop()
                reader = None
                state.console.close()
                state.console = console_ux.PlainConsole()
                state.console.print_above(console_ux.paint("键盘输入不可用，改用行输入", "yellow"))

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
                    state.console.print_above(console_ux.paint("› " + line, "cyan"))
                    if line.lower() in {"exit", "quit"}:
                        leaving = True
                        break
                    if line.startswith("/"):
                        if chat_handle_command(state, line) == "exit":
                            leaving = True
                            break
                        continue
                    state.pending.append(line)
                    if state.active:
                        state.console.print_above(console_ux.paint("⏎ 已排队，下一轮发送", "dim"))
                elif action == "cancel":
                    chat_interrupt(state)
                elif action == "interrupt":
                    if state.active:
                        chat_interrupt(state)
                    else:
                        leaving = True
                        break
                elif action == "exit":
                    leaving = True
                    break
            if leaving:
                chat_drain_work(state)
                if state.active:
                    chat_interrupt(state)
                    if state.worker is not None:
                        state.worker.join(timeout=1.0)
                    chat_drain_work(state)
                state.console.close()
                print("bye")
                return EXIT_OK

            # 5. redraw the pinned region
            if state.active:
                label = "接收中" if state.answer else "思考中"
                # animate only while nothing else on screen is moving; otherwise
                # hold the row still so it does not repaint on every token
                calm = state.show_thinking and (time.monotonic() - state.last_transcript) < 0.6
                status = chat_status_line(time.monotonic() - state.started, label, state.tokens,
                                          animate=not calm)
            else:
                status = ""
            if reader is not None:
                editor = reader.editor
                menu = (console_ux.menu_rows(CHAT_COMMANDS, editor.buffer, editor.menu_index, width)
                        if editor.menu_open else [])
                if menu and not status:
                    status = console_ux.paint("↑↓ 选择 · Enter 执行 · Tab 补全 · Esc 关闭", "dim")
                state.console.update(status, editor.buffer, editor.caret, menu)
            else:
                state.console.update(status)
            time.sleep(0.05)
    finally:
        if reader is not None:
            reader.stop()
        state.console.close()


def command_chat(args: argparse.Namespace) -> int:
    exercise = getattr(args, "exercise", None)
    target = require_exercise(exercise) if exercise else None
    if exercise and target is None: return EXIT_USAGE
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
    check = sub.add_parser("check", aliases=["run", "verify"], parents=[common]); check.add_argument("exercise", nargs="?"); check.add_argument("--all", action="store_true"); check.add_argument("--jobs", type=int, help="parallel grading workers (default: CPU count, capped at 8)"); check.add_argument("--timeout", type=float); check.add_argument("--total-timeout", type=float)
    watch = sub.add_parser("watch", parents=[common]); watch.add_argument("exercise", nargs="?"); watch.add_argument("--timeout", type=float, default=2.0); watch.add_argument("--total-timeout", type=float, default=10.0); watch.add_argument("--interval", type=float, default=.1); watch.add_argument("--auto-next", dest="auto_next", action="store_true", default=True); watch.add_argument("--no-auto-next", dest="auto_next", action="store_false"); watch.add_argument("--once", action="store_true"); watch.add_argument("--no-editor", action="store_true"); watch.add_argument("--no-follow", dest="no_follow", action="store_true", help="do not switch to the exercise whose file you edited last"); watch.add_argument("--active-file", dest="active_file", help="editor hook file naming the open exercise (default .cstudy/active)"); watch.add_argument("--edit-cmd")
    validate_parser = sub.add_parser("validate", parents=[common]); validate_parser.add_argument("--compile", action="store_true"); validate_parser.add_argument("--jobs", type=int, help="parallel compile workers (default: CPU count, capped at 8)"); validate_parser.add_argument("--compile-timeout", type=float, default=10.0)
    sub.add_parser("reset", parents=[common]); sub.add_parser("doctor", parents=[common])
    next_parser = sub.add_parser("next", parents=[common]); next_parser.add_argument("exercise", nargs="?")
    status_parser = sub.add_parser("status", parents=[common]); status_parser.add_argument("exercise", nargs="?")
    ai_parser = sub.add_parser("ai", aliases=["hint"], parents=[common]); ai_parser.add_argument("exercise", nargs="?"); ai_parser.add_argument("--hint-only", action="store_true"); ai_parser.add_argument("--ai-timeout", type=float, default=30.0); ai_parser.add_argument("--setup", action="store_true"); ai_parser.add_argument("--raw", action="store_true")
    chat_parser = sub.add_parser("chat", aliases=["ask"], parents=[common]); chat_parser.add_argument("exercise", nargs="?"); chat_parser.add_argument("--ai-timeout", type=float, default=60.0); chat_parser.add_argument("--no-stream", dest="stream", action="store_false", default=True); chat_parser.add_argument("--raw", action="store_true")
    for name in ("prev", "edit", "skip"):
        item = sub.add_parser(name, parents=[common]); item.add_argument("exercise")
    return root


def main() -> int:
    console_ux.configure_encoding()
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
                                      progress=True, no_editor=False, no_follow=False, active_file=None, edit_cmd=None)
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

