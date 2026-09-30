import json
import contextlib
import io
import os
import threading
import tempfile
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

import cstudy


class TestParsing(unittest.TestCase):
    def test_multiple_cases_and_blank_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Test.txt"
            path.write_text("ARGS: one two\nINPUT:\n\nOUTPUT:\nhello\n---\nINPUT:\na b\nOUTPUT:\nc\n", encoding="utf-8")
            cases = cstudy.parse_tests(path)
        self.assertEqual(len(cases), 2)
        self.assertEqual(cases[0].input, "")
        self.assertEqual(cases[0].expected, "hello")
        self.assertEqual(cases[0].args, ["one", "two"])
        self.assertEqual(cases[1].input, "a b")

    def test_line_endings_only_are_normalized(self):
        self.assertEqual(cstudy.normalize("a\r\nb\r\n"), "a\nb")
        self.assertNotEqual(cstudy.normalize("a  \n"), "a")


class TestRepository(unittest.TestCase):
    def test_current_exercises_are_valid(self):
        self.assertGreaterEqual(len(cstudy.discover()), 3)
        for directory in cstudy.discover():
            source, tests = cstudy.exercise_files(directory)
            self.assertIsNotNone(source)
            self.assertIsNotNone(tests)
            self.assertTrue(cstudy.parse_tests(tests))
            self.assertTrue((directory / "metadata.json").exists())

    def test_metadata_is_json_serializable(self):
        for directory in cstudy.discover():
            json.dumps(cstudy.metadata(directory), ensure_ascii=False)

    def test_doctor_reports_ready_core(self):
        result = cstudy.command_doctor(type("Args", (), {"json": True})())
        self.assertEqual(result, 0)

    def test_disabled_exercise_is_hidden_from_default_discovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); directory = root / "Exercises" / "disabled"; directory.mkdir(parents=True)
            (directory / "Ques.c").write_text("int main(void){return 0;}\n", encoding="utf-8")
            (directory / "Test.txt").write_text("INPUT:\nOUTPUT:\n", encoding="utf-8")
            (directory / "description.md").write_text("# Disabled\n", encoding="utf-8")
            (directory / "Ques.c.bak").write_text("int main(void){return 0;}\n", encoding="utf-8")
            (directory / "metadata.json").write_text('{"status":"disabled"}', encoding="utf-8")
            old = cstudy.EXERCISES; cstudy.EXERCISES = root / "Exercises"
            try:
                self.assertEqual(cstudy.discover(), [])
                self.assertEqual(len(cstudy.discover(include_disabled=True)), 1)
            finally:
                cstudy.EXERCISES = old

    def test_curriculum_maps_every_chapter_to_existing_exercises(self):
        curriculum = cstudy.load_json(cstudy.CURRICULUM, {"chapters": []})["chapters"]
        mapping = cstudy.load_json(cstudy.EXERCISE_MAP, {})
        self.assertEqual(len(curriculum), 29)
        for chapter in curriculum:
            paths = mapping.get(chapter["id"], [])
            self.assertTrue(paths, chapter["id"])
            for path in paths:
                self.assertTrue((cstudy.EXERCISES / path).is_dir(), path)

    def test_introduction_is_the_migrated_first_exercise(self):
        exercises = cstudy.discover()
        self.assertEqual(cstudy.exercise_id(exercises[0]), "00-introduction/compile-run")
        self.assertFalse((cstudy.EXERCISES / "ex0").exists())

    def test_unified_interaction_aliases_parse(self):
        parser = cstudy.build_parser()
        self.assertEqual(parser.parse_args(["verify", "00-introduction/compile-run"]).command, "verify")
        self.assertEqual(parser.parse_args(["progress"]).command, "progress")
        self.assertEqual(parser.parse_args(["hint", "00-introduction/compile-run"]).command, "hint")
        watch = parser.parse_args(["watch"])
        self.assertIsNone(watch.exercise)
        self.assertTrue(watch.auto_next)
        self.assertTrue(parser.parse_args(["ai", "--setup"]).setup)

    def test_list_and_curriculum_json_are_machine_readable(self):
        list_output = io.StringIO()
        with contextlib.redirect_stdout(list_output):
            self.assertEqual(cstudy.command_list(type("Args", (), {"all": False, "json": True})()), 0)
        listing = json.loads(list_output.getvalue())
        self.assertEqual(listing["total"], len(cstudy.discover()))
        curriculum_output = io.StringIO()
        with contextlib.redirect_stdout(curriculum_output):
            self.assertEqual(cstudy.command_curriculum(type("Args", (), {"json": True})()), 0)
        self.assertEqual(len(json.loads(curriculum_output.getvalue())["chapters"]), 29)

    def test_compile_validation_covers_current_sources(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = cstudy.command_validate(type("Args", (), {"compile": True, "compile_timeout": 10.0})())
        self.assertEqual(result, 0, output.getvalue())
        self.assertIn("0 invalid", output.getvalue())

    def test_validate_json_is_machine_readable(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = cstudy.command_validate(type("Args", (), {"compile": False, "compile_timeout": 10.0, "json": True})())
        self.assertEqual(result, 0)
        report = json.loads(output.getvalue())
        self.assertTrue(report["valid"])
        self.assertEqual(report["exercise_count"], 33)


class TestGrading(unittest.TestCase):
    def make_exercise(self, root, name, source, test):
        directory = root / "Exercises" / name
        directory.mkdir(parents=True)
        (directory / "Ques.c").write_text(source, encoding="utf-8")
        (directory / "Ques.c.bak").write_text(source, encoding="utf-8")
        (directory / "description.md").write_text("# Test\n", encoding="utf-8")
        (directory / "metadata.json").write_text('{"title":"Test","order":1}', encoding="utf-8")
        (directory / "Test.txt").write_text(test, encoding="utf-8")
        return directory

    def grade_in_temp(self, name, source, test, timeout=1.0):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = self.make_exercise(root, name, source, test)
            old = cstudy.EXERCISES
            cstudy.EXERCISES = root / "Exercises"
            try:
                return cstudy.grade(directory, timeout, timeout + 1.0, 4096)
            finally:
                cstudy.EXERCISES = old

    def test_pass_and_output_mismatch(self):
        source = '#include <stdio.h>\nint main(void){puts("ok");}\n'
        result = self.grade_in_temp("中文路径", source, "INPUT:\nOUTPUT:\nok\n")
        self.assertEqual(result["status"], "passed")
        result = self.grade_in_temp("mismatch", source, "INPUT:\nOUTPUT:\nwrong\n")
        self.assertEqual(result["status"], "output_mismatch")

    def test_completion_marker_blocks_done_until_removed(self):
        source = '#include <stdio.h>\nint main(void){puts("ok");}\n// Done\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); directory = self.make_exercise(root, "marker", source, "INPUT:\nOUTPUT:\nok\n")
            old = cstudy.EXERCISES; cstudy.EXERCISES = root / "Exercises"
            try:
                result = cstudy.grade(directory, 1.0, 2.0, 4096)
                self.assertEqual(result["status"], "incomplete_marker")
                self.assertFalse(cstudy.is_done(directory, {"exercises": {}}))
                directory.joinpath("Ques.c").write_text(source.replace("// Done", ""), encoding="utf-8")
                result = cstudy.grade(directory, 1.0, 2.0, 4096)
                self.assertEqual(result["status"], "passed")
            finally:
                cstudy.EXERCISES = old

    def test_compile_and_runtime_errors(self):
        result = self.grade_in_temp("compile", "int main(void) {", "INPUT:\nOUTPUT:\n")
        self.assertEqual(result["status"], "compile_error")
        source = '#include <stdlib.h>\nint main(void){return EXIT_FAILURE;}\n'
        result = self.grade_in_temp("runtime", source, "INPUT:\nOUTPUT:\n")
        self.assertEqual(result["status"], "runtime_error")

    def test_timeout_terminates_process(self):
        source = 'int main(void){for(;;){} return 0;}\n'
        result = self.grade_in_temp("timeout", source, "INPUT:\nOUTPUT:\n", timeout=.1)
        self.assertEqual(result["status"], "timeout")

    def test_output_limit_terminates_process(self):
        source = '#include <stdio.h>\nint main(void){for(;;)puts("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");}\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = self.make_exercise(root, "output-limit", source, "INPUT:\nOUTPUT:\n")
            old = cstudy.EXERCISES
            cstudy.EXERCISES = root / "Exercises"
            try:
                result = cstudy.grade(directory, .5, 1.0, 256)
            finally:
                cstudy.EXERCISES = old
        self.assertEqual(result["status"], "output_limit")

    def test_multiple_source_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); directory = self.make_exercise(root, "multi", '#include <stdio.h>\nint value(void);\nint main(void){printf("%d\\n", value());}\n', "INPUT:\nOUTPUT:\n42\n")
            (directory / "helper.c").write_text("int value(void){return 42;}\n", encoding="utf-8")
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            metadata["sources"] = ["Ques.c", "helper.c"]
            (directory / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            old = cstudy.EXERCISES; cstudy.EXERCISES = root / "Exercises"
            try:
                result = cstudy.grade(directory, 1.0, 2.0, 4096)
            finally:
                cstudy.EXERCISES = old
        self.assertEqual(result["status"], "passed")

    def test_command_line_arguments(self):
        source = '#include <stdio.h>\nint main(int argc,char **argv){for(int i=1;i<argc;i++)printf("%s%s",i>1?" ":"",argv[i]); puts("");}\n'
        result = self.grade_in_temp("args", source, "ARGS: one two\nINPUT:\nOUTPUT:\none two\n")
        self.assertEqual(result["status"], "passed")

    def test_watch_auto_next_switches_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.make_exercise(root, "01-first", '#include <stdio.h>\nint main(void){puts("bad");}\n', "INPUT:\nOUTPUT:\nok\n")
            self.make_exercise(root, "02-second", '#include <stdio.h>\nint main(void){puts("ok");}\n', "INPUT:\nOUTPUT:\nok\n")
            old_values = (cstudy.EXERCISES, cstudy.STATE_DIR, cstudy.STATE_FILE, cstudy.LOG_DIR)
            cstudy.EXERCISES = root / "Exercises"
            cstudy.STATE_DIR = root / ".cstudy"
            cstudy.STATE_FILE = cstudy.STATE_DIR / "state.json"
            cstudy.LOG_DIR = cstudy.STATE_DIR / "logs"
            output = io.StringIO()
            args = type("Args", (), {"exercise": "01-first", "timeout": .5, "total_timeout": 2.0,
                                      "interval": .02, "auto_next": True, "once": True,
                                      "json": False, "quiet": False})()
            thread = threading.Thread(target=lambda: None)
            try:
                thread = threading.Thread(target=lambda: cstudy.command_watch(args))
                with contextlib.redirect_stdout(output):
                    thread.start(); time.sleep(.08)
                    (first / "Ques.c").write_text('#include <stdio.h>\nint main(void){puts("ok");}\n', encoding="utf-8")
                    thread.join(timeout=5)
                self.assertFalse(thread.is_alive())
            finally:
                cstudy.EXERCISES, cstudy.STATE_DIR, cstudy.STATE_FILE, cstudy.LOG_DIR = old_values
            self.assertIn("watching next: 02-second", output.getvalue())


class TestApiAssistant(unittest.TestCase):
    def test_saved_provider_key_precedes_openai_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            old_config = cstudy.CONFIG_FILE; old = dict(os.environ)
            cstudy.CONFIG_FILE = Path(temp) / "config.json"
            cstudy.CONFIG_FILE.write_text(json.dumps({"ai_api_key": "provider-key"}), encoding="utf-8")
            try:
                os.environ.pop("CSTUDY_API_KEY", None)
                os.environ["OPENAI_API_KEY"] = "fallback-key"
                self.assertEqual(cstudy.ai_configuration()["api_key"], "provider-key")
            finally:
                cstudy.CONFIG_FILE = old_config
                os.environ.clear(); os.environ.update(old)

    def test_missing_api_key_is_actionable(self):
        old = dict(os.environ)
        with tempfile.TemporaryDirectory() as temp:
            old_config = cstudy.CONFIG_FILE
            try:
                cstudy.CONFIG_FILE = Path(temp) / "config.json"
                os.environ.pop("CSTUDY_API_KEY", None)
                os.environ.pop("OPENAI_API_KEY", None)
                result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 1.0})())
            finally:
                cstudy.CONFIG_FILE = old_config
                os.environ.clear(); os.environ.update(old)
        self.assertEqual(result, 4)

    def test_setup_saves_deepseek_configuration(self):
        with tempfile.TemporaryDirectory() as temp:
            old_values = (cstudy.STATE_DIR, cstudy.CONFIG_FILE)
            cstudy.STATE_DIR = Path(temp) / ".cstudy"
            cstudy.CONFIG_FILE = cstudy.STATE_DIR / "config.json"
            answers = iter(["https://api.deepseek.com"])
            try:
                with mock.patch.object(cstudy.sys.stdin, "isatty", return_value=True), \
                     mock.patch.object(cstudy.sys.stdout, "isatty", return_value=True), \
                     mock.patch.object(cstudy, "read_line", side_effect=lambda *_: next(answers)), \
                     mock.patch.object(cstudy.getpass, "getpass", return_value="secret-key"):
                    self.assertTrue(cstudy.configure_ai())
                saved = cstudy.load_json(cstudy.CONFIG_FILE, {})
            finally:
                cstudy.STATE_DIR, cstudy.CONFIG_FILE = old_values
        self.assertEqual(saved["ai_provider"], "DeepSeek")
        self.assertEqual(saved["ai_api_base"], "https://api.deepseek.com")
        self.assertEqual(saved["ai_model"], "deepseek-flash")
        self.assertEqual(saved["ai_api_mode"], "chat")
        self.assertEqual(saved["ai_api_key"], "secret-key")

    def test_unknown_provider_discovers_chat_model(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                response = json.dumps({"data": [
                    {"id": "text-embedding-3-small"}, {"id": "example-chat"}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            model = cstudy.discover_compatible_model(f"http://127.0.0.1:{server.server_port}/v1", "key")
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)
        self.assertEqual(model, "example-chat")

    def test_deepseek_responses_mode_is_actionable(self):
        old = dict(os.environ); errors = io.StringIO()
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = "https://api.deepseek.com"
            os.environ["CSTUDY_API_MODE"] = "responses"
            with contextlib.redirect_stderr(errors):
                result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 1.0})())
        finally:
            os.environ.clear(); os.environ.update(old)
        self.assertEqual(result, 4)
        self.assertIn("uses chat mode", errors.getvalue())
        self.assertIn("/chat/completions", errors.getvalue())

    def test_http_error_includes_service_message(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                response = json.dumps({"error": {"message": "invalid model"}}).encode()
                self.send_response(400, "Bad Request")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        old = dict(os.environ); errors = io.StringIO()
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = f"http://127.0.0.1:{server.server_port}/v1"
            with contextlib.redirect_stderr(errors):
                result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 3.0})())
        finally:
            os.environ.clear(); os.environ.update(old)
            server.shutdown(); server.server_close(); thread.join(timeout=2)
        self.assertEqual(result, 4)
        self.assertIn("HTTP 400", errors.getvalue())
        self.assertIn("invalid model", errors.getvalue())

    def test_invalid_api_base_is_reported_without_traceback(self):
        old = dict(os.environ); errors = io.StringIO()
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = "not-a-url"
            with contextlib.redirect_stderr(errors):
                result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 1.0})())
        finally:
            os.environ.clear(); os.environ.update(old)
        self.assertEqual(result, 4)
        self.assertIn("AI API connection failed", errors.getvalue())

    def test_openai_compatible_chat_completion(self):
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["path"] = self.path
                received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                response = json.dumps({"choices": [{"message": {"content": "hint"}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        old = dict(os.environ)
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = f"http://127.0.0.1:{server.server_port}/v1"
            os.environ["CSTUDY_API_MODE"] = "chat"
            result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 3.0})())
        finally:
            os.environ.clear(); os.environ.update(old)
            server.shutdown(); server.server_close(); thread.join(timeout=2)
        self.assertEqual(result, 0)
        self.assertEqual(received["path"], "/v1/chat/completions")
        self.assertEqual(received["body"]["messages"][0]["role"], "user")

    def test_responses_api_mode(self):
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["path"] = self.path
                received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                response = json.dumps({"output_text": "response hint"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        old = dict(os.environ)
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = f"http://127.0.0.1:{server.server_port}/v1"
            os.environ["CSTUDY_API_MODE"] = "responses"
            result = cstudy.command_ai(type("Args", (), {"exercise": "00-introduction/compile-run", "hint_only": True, "ai_timeout": 3.0})())
        finally:
            os.environ.clear(); os.environ.update(old)
            server.shutdown(); server.server_close(); thread.join(timeout=2)
        self.assertEqual(result, 0)
        self.assertEqual(received["path"], "/v1/responses")
        self.assertEqual(received["body"]["input"][0]["role"], "user")


class TtyBuffer(io.StringIO):
    """Captured output that claims to be a terminal, so rendering paths run."""

    def isatty(self):
        return True


class TestConsoleUx(unittest.TestCase):
    def test_plain_rendering_has_no_escape_codes(self):
        rendered = cstudy.console_ux.render_markdown("# Title\n\n- a\n- b\n", width=40, ansi=False)
        self.assertNotIn("\x1b", rendered)
        self.assertIn("Title", rendered)

    def test_wrapped_lines_stay_within_width(self):
        rendered = cstudy.console_ux.render_markdown("\u4e2d\u6587" * 60, width=40, ansi=False)
        for line in rendered.split("\n"):
            self.assertLessEqual(cstudy.console_ux.visible_width(line), 40)

    def test_payload_shapes_for_both_modes(self):
        chat = cstudy.build_ai_payload("m", "chat", [{"role": "user", "content": "hi"}])
        self.assertEqual(chat["messages"][0], {"role": "user", "content": "hi"})
        responses = cstudy.build_ai_payload("m", "responses", [{"role": "user", "content": "hi"}])
        self.assertEqual(responses["input"][0]["content"][0]["type"], "input_text")


class ScriptedReader:
    """Stand-in for InputReader: releases one scripted event per poll."""

    events = []

    def __init__(self, read_key=None, editor=None):
        self.pending = list(type(self).events)
        self.editor = editor if editor is not None else cstudy.console_ux.LineEditor()
        self.failed = False

    def start(self):
        return

    def poll(self):
        return [self.pending.pop(0)] if self.pending else []

    def stop(self):
        return


class TestLineEditor(unittest.TestCase):
    def test_typing_backspace_and_submit(self):
        editor = cstudy.console_ux.LineEditor()
        for char in "abc":
            self.assertEqual(editor.feed(char), ("redraw", ""))
        self.assertEqual(editor.feed("\x7f"), ("redraw", ""))
        editor.feed("d")
        self.assertEqual(editor.feed("\r"), ("submit", "abd"))
        self.assertEqual(editor.buffer, "")

    def test_escape_cancels_and_ctrl_c_interrupts(self):
        editor = cstudy.console_ux.LineEditor()
        editor.feed("x")
        self.assertEqual(editor.feed("ESC"), ("cancel", ""))
        self.assertEqual(editor.buffer, "")
        self.assertEqual(editor.feed("CTRL-C"), ("interrupt", ""))

    def test_caret_moves_and_inserts_in_the_middle(self):
        editor = cstudy.console_ux.LineEditor()
        for char in "ac":
            editor.feed(char)
        editor.feed("LEFT")
        self.assertEqual(editor.caret, 1)
        editor.feed("b")
        self.assertEqual(editor.buffer, "abc")
        self.assertEqual(editor.caret, 2)
        editor.feed("HOME")
        self.assertEqual(editor.caret, 0)
        editor.feed("DELETE")
        self.assertEqual(editor.buffer, "bc")
        editor.feed("END")
        self.assertEqual(editor.caret, 2)

    def test_backspace_deletes_before_the_caret(self):
        editor = cstudy.console_ux.LineEditor()
        for char in "abc":
            editor.feed(char)
        editor.feed("LEFT")
        editor.feed("\x7f")
        self.assertEqual(editor.buffer, "ac")
        self.assertEqual(editor.caret, 1)

    def test_slash_opens_and_arrows_select(self):
        editor = cstudy.console_ux.LineEditor(commands=cstudy.CHAT_COMMANDS)
        editor.feed("/")
        self.assertTrue(editor.menu_open)
        self.assertEqual(len(editor.matches()), len(cstudy.CHAT_COMMANDS))
        editor.feed("m")
        self.assertEqual([item[0] for item in editor.matches()], ["/model"])
        self.assertEqual(editor.feed("\r"), ("redraw", ""))   # /model takes an argument
        self.assertEqual(editor.buffer, "/model ")
        self.assertFalse(editor.menu_open)                    # the space closes the menu
        self.assertEqual(editor.caret, len("/model "))

    def test_menu_selection_stops_at_both_ends(self):
        editor = cstudy.console_ux.LineEditor(commands=[("/a", "a", False), ("/b", "b", False)])
        editor.feed("/")
        editor.feed("UP")
        self.assertEqual(editor.menu_index, 0)
        for _ in range(3):
            editor.feed("DOWN")
        self.assertEqual(editor.menu_index, 1)

    def test_enter_runs_a_no_argument_command(self):
        editor = cstudy.console_ux.LineEditor(commands=[("/exit", "leave", False)])
        editor.feed("/")
        self.assertEqual(editor.feed("\r"), ("submit", "/exit"))
        self.assertEqual(editor.buffer, "")

    def test_tab_completes_without_running(self):
        editor = cstudy.console_ux.LineEditor(commands=[("/exit", "leave", False)])
        editor.feed("/")
        self.assertEqual(editor.feed("\t"), ("redraw", ""))
        self.assertEqual(editor.buffer, "/exit")

    def test_escape_closes_the_menu_before_interrupting(self):
        editor = cstudy.console_ux.LineEditor(commands=[("/exit", "leave", False)])
        editor.feed("/")
        self.assertEqual(editor.feed("ESC"), ("redraw", ""))
        self.assertEqual(editor.buffer, "")
        self.assertEqual(editor.feed("ESC"), ("cancel", ""))

    def test_history_stops_at_both_ends(self):
        editor = cstudy.console_ux.LineEditor()
        for char in "one":
            editor.feed(char)
        editor.feed("\r")
        editor.feed("UP")
        self.assertEqual(editor.buffer, "one")
        editor.feed("UP")
        self.assertEqual(editor.buffer, "one")
        editor.feed("DOWN")
        self.assertEqual(editor.buffer, "")
        editor.feed("DOWN")
        self.assertEqual(editor.buffer, "")

    def test_ctrl_u_and_history_recall(self):
        editor = cstudy.console_ux.LineEditor()
        for char in "first":
            editor.feed(char)
        editor.feed("\r")
        self.assertEqual(editor.feed("UP"), ("redraw", ""))
        self.assertEqual(editor.buffer, "first")
        editor.feed("DOWN")
        self.assertEqual(editor.buffer, "")
        for char in "junk":
            editor.feed(char)
        editor.feed("\x15")
        self.assertEqual(editor.buffer, "")


class TestLiveConsole(unittest.TestCase):
    def test_status_and_input_rows_stay_pinned(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("Thinking (1.0s)", "abc", caret=3)
        console.print_above("answer line")
        console.update("Receiving", "abcd", caret=4)
        console.close()
        written = stream.getvalue()
        self.assertIn("\x1b[?25h", written)
        self.assertIn("Thinking (1.0s)", written)
        self.assertIn("> abc", written)
        self.assertIn("answer line", written)
        # the answer lands above the region, and the region is redrawn after it
        self.assertLess(written.index("answer line"), written.rindex("> abcd"))
        # clearing the region walks the cursor back up instead of leaving rows behind
        self.assertIn("\x1b[1A", written)

    def test_menu_rows_are_drawn_above_the_status_row(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("status", "/h", caret=2,
                       menu=["/help  show this help", "/hint  ask for a hint"])
        written = cstudy.console_ux.ANSI_RE.sub("", stream.getvalue())
        self.assertLess(written.index("/help"), written.index("status"))
        self.assertLess(written.index("status"), written.index("> /h"))

    def test_long_input_is_clipped_to_one_row(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "x" * 500, caret=500)
        row, column = console._input_row()
        self.assertLessEqual(cstudy.console_ux.visible_width(row),
                             cstudy.console_ux.terminal_width(2))
        self.assertLessEqual(column, cstudy.console_ux.visible_width(row))

    def test_idle_updates_do_not_write(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "abc", caret=3)
        before = len(stream.getvalue())
        for _ in range(20):
            console.update("", "abc", caret=3)
        self.assertEqual(len(stream.getvalue()), before)

    def test_changed_status_still_redraws(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("a", "x", caret=1)
        before = len(stream.getvalue())
        console.update("b", "x", caret=1)
        self.assertGreater(len(stream.getvalue()), before)

    def test_caret_is_placed_inside_the_input_row(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "abc", caret=1)
        row, column = console._input_row()
        self.assertEqual(row, "> abc")
        self.assertEqual(column, 3)
        self.assertIn("\x1b[?25h", stream.getvalue())

    def test_caret_counts_wide_characters_as_two_cells(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "\u4e2d\u6587ab", caret=2)
        _, column = console._input_row()
        self.assertEqual(column, 2 + 4)

    def test_cursor_is_hidden_again_when_the_caller_hid_it(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream,
                                                restore_hidden_cursor=True)
        console.update("", "hi", caret=2)
        console.close()
        self.assertTrue(stream.getvalue().endswith("\x1b[?25l"))

    def test_visible_cursor_is_left_visible(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "hi", caret=2)
        console.close()
        self.assertNotIn("\x1b[?25l", stream.getvalue())


class TestChatStatusLine(unittest.TestCase):
    def test_never_previews_streamed_text(self):
        line = cstudy.chat_status_line(1.25, "Receiving", 42, animate=True)
        self.assertIn("Receiving", cstudy.console_ux.ANSI_RE.sub("", line))
        self.assertNotIn("\u2502", line)

    def test_calm_mode_holds_the_row_still(self):
        first = cstudy.chat_status_line(1.0, "Thinking", 5, animate=False)
        second = cstudy.chat_status_line(9.9, "Thinking", 500, animate=False)
        self.assertEqual(first, second)          # no moving timer, no moving counter
        self.assertIn("\u273b", first)

    def test_animated_mode_reports_progress(self):
        line = cstudy.console_ux.ANSI_RE.sub("", cstudy.chat_status_line(2.5, "Thinking", 7))
        self.assertIn("2.5s", line)
        self.assertIn("7 tok", line)


class TestAlternateScreen(unittest.TestCase):
    def test_leave_and_enter_are_idempotent(self):
        old = cstudy._ALTERNATE_SCREEN
        output = TtyBuffer()
        try:
            cstudy._ALTERNATE_SCREEN = True
            with contextlib.redirect_stdout(output):
                cstudy.leave_alternate_screen()
                self.assertFalse(cstudy._ALTERNATE_SCREEN)
                cstudy.leave_alternate_screen()      # already in the normal buffer
                cstudy.enter_alternate_screen()
                self.assertTrue(cstudy._ALTERNATE_SCREEN)
                cstudy.enter_alternate_screen()      # already in the private buffer
        finally:
            cstudy._ALTERNATE_SCREEN = old
        written = output.getvalue()
        self.assertEqual(written.count("\x1b[?1049l"), 1)
        self.assertEqual(written.count("\x1b[?1049h"), 1)
        self.assertIn("\x1b[?25h", written)


class TestInputReader(unittest.TestCase):
    def test_keys_drive_the_completion_menu(self):
        keys = ["/", "h", "DOWN", "\r"]

        def read_key(timeout=0.1):
            if keys:
                return keys.pop(0)
            time.sleep(timeout)
            return None

        editor = cstudy.console_ux.LineEditor(commands=cstudy.CHAT_COMMANDS)
        reader = cstudy.console_ux.InputReader(read_key, editor)
        reader.start()
        events = []
        try:
            for _ in range(100):
                events.extend(reader.poll())
                if any(action == "submit" for action, _ in events):
                    break
                time.sleep(0.02)
        finally:
            reader.stop()
        self.assertIn(("submit", "/hint"), events)


class TestChatSlashFeedback(unittest.TestCase):
    def drive(self, keys):
        """Run the real chat loop with scripted keystrokes; no network is used."""
        state = {"keys": list(keys), "last": 0.0}

        def read_key(timeout=0.05):
            if state["keys"] and time.monotonic() - state["last"] > 0.05:
                state["last"] = time.monotonic()
                return state["keys"].pop(0)
            time.sleep(timeout)
            return None

        reader = cstudy.console_ux.InputReader(
            read_key, cstudy.console_ux.LineEditor(commands=cstudy.CHAT_COMMANDS))
        output = TtyBuffer()
        old = dict(os.environ)
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = "http://127.0.0.1:9/v1"
            os.environ["CSTUDY_API_MODE"] = "chat"
            with mock.patch.object(cstudy, "interactive_terminal", return_value=True), \
                 mock.patch.object(cstudy.console_ux, "InputReader", lambda *a, **k: reader), \
                 contextlib.redirect_stdout(output):
                code = cstudy.chat_session(cstudy.find_exercise("00-introduction/compile-run"),
                                           timeout=1.0)
        finally:
            os.environ.clear(); os.environ.update(old)
        return code, cstudy.console_ux.ANSI_RE.sub("", output.getvalue())

    def test_enter_runs_the_highlighted_command_and_echoes_it(self):
        code, plain = self.drive(["/", "\r", "/", "e", "x", "i", "t", "\r"])
        self.assertEqual(code, 0)
        self.assertIn("\u203a /help", plain)                       # what was submitted
        self.assertLess(plain.index("\u203a /help"),
                        plain.index("Commands (type / for completion)"))
        self.assertNotIn("unknown command", plain)
        self.assertIn("\u203a /exit", plain)
        self.assertTrue(plain.rstrip().endswith("bye"))

    def test_menu_explains_its_own_keys(self):
        code, plain = self.drive(["/", "ESC", "/", "e", "x", "i", "t", "\r"])
        self.assertEqual(code, 0)
        self.assertIn("Enter run", plain)          # the menu hint while it is open
        self.assertNotIn("nothing to interrupt", plain)


class TestMenuRows(unittest.TestCase):
    def test_filters_and_marks_the_selection(self):
        rows = cstudy.console_ux.menu_rows(cstudy.CHAT_COMMANDS, "/h", 1, 60)
        plain = [cstudy.console_ux.ANSI_RE.sub("", row) for row in rows]
        self.assertEqual(len(rows), 2)
        self.assertIn("/help", plain[0])
        self.assertTrue(plain[1].startswith("\u276f /hint"), plain[1])

    def test_no_menu_after_a_space(self):
        self.assertEqual(cstudy.console_ux.menu_rows(cstudy.CHAT_COMMANDS, "/model ", 0, 60), [])

    def test_window_keeps_the_selection_visible(self):
        rows = cstudy.console_ux.menu_rows(cstudy.CHAT_COMMANDS, "/", 9, 60, limit=4)
        self.assertEqual(len(rows), 4)
        self.assertTrue(any(cstudy.console_ux.ANSI_RE.sub("", row).startswith("\u276f /exit")
                            for row in rows))


class TestStreamingBlock(unittest.TestCase):
    def test_emits_wrapped_lines_above_the_region(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "", caret=0)
        block = cstudy.console_ux.StreamingBlock(console, style="dim", prefix="  ", width=20)
        block.feed("hello world this is a long thought that wraps")
        block.flush()
        written = cstudy.console_ux.ANSI_RE.sub("", stream.getvalue())
        self.assertIn("hello world this", written)
        self.assertIn("wraps", written)
        self.assertLess(written.index("hello world this"), written.index("wraps"))

    def test_keeps_the_unfinished_tail_buffered(self):
        stream = TtyBuffer()
        console = cstudy.console_ux.LiveConsole(prompt="> ", stream=stream)
        console.update("", "", caret=0)
        block = cstudy.console_ux.StreamingBlock(console, style="dim", width=20)
        block.feed("short line\npartial")
        self.assertIn("short line", stream.getvalue())
        self.assertNotIn("partial", stream.getvalue())
        block.flush()
        self.assertIn("partial", stream.getvalue())


class TestStreamingAssistant(unittest.TestCase):
    def setUp(self):
        self.servers = []

    def tearDown(self):
        for server, thread in self.servers:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def start(self, handler):
        server = HTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.servers.append((server, thread))
        return f"http://127.0.0.1:{server.server_port}/v1"

    def test_streaming_chat_completion_parses_sse(self):
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for piece in ("Hel", "lo"):
                    event = {"choices": [{"delta": {"content": piece}}]}
                    self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                self.wfile.write(b"data: [DONE]\n\n")

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        deltas = []
        text = cstudy.ai_request(base, "key", "model", "chat", [{"role": "user", "content": "hi"}],
                                 3.0, stream=True, on_delta=deltas.append)
        self.assertEqual(text, "Hello")
        self.assertEqual(deltas, ["Hel", "lo"])
        self.assertTrue(received["body"]["stream"])

    def test_stream_falls_back_to_plain_json(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                response = json.dumps({"choices": [{"message": {"content": "plain"}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        text = cstudy.ai_request(base, "key", "model", "chat", [{"role": "user", "content": "hi"}],
                                 3.0, stream=True)
        self.assertEqual(text, "plain")

    def test_chat_session_queues_while_busy_and_renders_markdown(self):
        bodies = []
        first_done = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                bodies.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for piece in ("## Fix\n\n", "use &age"):
                    event = {"choices": [{"delta": {"content": piece}}]}
                    self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                self.wfile.write(b"data: [DONE]\n\n")
                first_done.set()

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        old = dict(os.environ)
        answers = iter(["second question", "/exit"])
        output = TtyBuffer()

        def next_line(*_):
            # wait for the running turn so the next message is queued, like a user
            if not first_done.is_set():
                first_done.wait(5)
            return next(answers)

        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = base
            os.environ["CSTUDY_API_MODE"] = "chat"
            with mock.patch.object(cstudy, "interactive_terminal", return_value=False), \
                 mock.patch.object(cstudy, "read_line", side_effect=next_line), \
                 contextlib.redirect_stdout(output):
                code = cstudy.chat_session(cstudy.find_exercise("00-introduction/compile-run"),
                                           timeout=5.0, opening="first question")
        finally:
            os.environ.clear(); os.environ.update(old)
        for _ in range(100):
            if len(bodies) >= 2:
                break
            time.sleep(0.05)
        self.assertEqual(code, 0)
        self.assertEqual(len(bodies), 2)
        self.assertEqual([message["role"] for message in bodies[0]["messages"]], ["system", "user"])
        self.assertEqual([message["role"] for message in bodies[1]["messages"]],
                         ["system", "user", "assistant", "user"])
        self.assertIn("Fix", output.getvalue())

    def test_reasoning_deltas_are_reported(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                events = [{"choices": [{"delta": {"reasoning_content": "checking scanf"}}]},
                          {"choices": [{"delta": {"content": "## Fix"}}]}]
                for event in events:
                    self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                self.wfile.write(b"data: [DONE]\n\n")

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        thoughts, deltas = [], []
        text = cstudy.ai_request(base, "key", "model", "chat", [{"role": "user", "content": "hi"}],
                                 3.0, stream=True, on_delta=deltas.append,
                                 on_reasoning=thoughts.append)
        self.assertEqual(text, "## Fix")
        self.assertEqual(thoughts, ["checking scanf"])
        self.assertEqual(deltas, ["## Fix"])

    def test_cancel_aborts_a_stream(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                try:
                    for index in range(50):
                        event = {"choices": [{"delta": {"content": "chunk%d " % index}}]}
                        self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                        self.wfile.flush()
                        time.sleep(0.02)
                    self.wfile.write(b"data: [DONE]\n\n")
                except OSError:
                    pass

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        cancel = threading.Event()
        seen = []

        def first_delta(piece):
            seen.append(piece)
            cancel.set()

        with self.assertRaises(cstudy.AiCancelled):
            cstudy.ai_request(base, "key", "model", "chat", [{"role": "user", "content": "hi"}],
                              3.0, stream=True, on_delta=first_delta, cancel=cancel)
        self.assertTrue(seen)

    def test_chat_interrupt_discards_the_turn(self):
        bodies = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                bodies.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                try:
                    for index in range(40):
                        event = {"choices": [{"delta": {"content": "chunk%d " % index}}]}
                        self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                        self.wfile.flush()
                        time.sleep(0.05)
                    self.wfile.write(b"data: [DONE]\n\n")
                except OSError:
                    pass

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        old = dict(os.environ)
        output = TtyBuffer()
        ScriptedReader.events = [("submit", "go"), ("cancel", ""), ("exit", "")]
        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = base
            os.environ["CSTUDY_API_MODE"] = "chat"
            with mock.patch.object(cstudy, "interactive_terminal", return_value=True), \
                 mock.patch.object(cstudy.console_ux, "InputReader", ScriptedReader), \
                 contextlib.redirect_stdout(output):
                code = cstudy.chat_session(cstudy.find_exercise("00-introduction/compile-run"),
                                           timeout=5.0)
        finally:
            os.environ.clear(); os.environ.update(old)
        self.assertEqual(code, 0)
        self.assertEqual(len(bodies), 1)
        self.assertIn("interrupted", output.getvalue())


    def test_chat_session_reports_reasoning(self):
        first_done = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                events = [{"choices": [{"delta": {"reasoning_content": "weighing options"}}]},
                          {"choices": [{"delta": {"content": "## Answer"}}]}]
                for event in events:
                    self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                self.wfile.write(b"data: [DONE]\n\n")
                first_done.set()

            def log_message(self, *_):
                pass

        base = self.start(Handler)
        old = dict(os.environ)
        output = TtyBuffer()
        answers = iter(["hello", "/exit"])

        def next_line(*_):
            line = next(answers)
            if line == "/exit":
                for _ in range(200):
                    if "thought for" in output.getvalue():
                        break
                    time.sleep(0.05)
            return line

        try:
            os.environ["CSTUDY_API_KEY"] = "test-key"
            os.environ["CSTUDY_API_BASE"] = base
            os.environ["CSTUDY_API_MODE"] = "chat"
            with mock.patch.object(cstudy, "interactive_terminal", return_value=False), \
                 mock.patch.object(cstudy, "read_line", side_effect=next_line), \
                 contextlib.redirect_stdout(output):
                code = cstudy.chat_session(cstudy.find_exercise("00-introduction/compile-run"),
                                           timeout=5.0)
        finally:
            os.environ.clear(); os.environ.update(old)
        self.assertEqual(code, 0)
        self.assertIn("thought for", output.getvalue())
        self.assertIn("Answer", output.getvalue())
        # the reasoning itself accumulates in the transcript, not on one line
        self.assertIn("weighing options", output.getvalue())


if __name__ == "__main__":
    unittest.main()

