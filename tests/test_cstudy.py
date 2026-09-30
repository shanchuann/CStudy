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
            answers = iter(["2", "", ""])
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


if __name__ == "__main__":
    unittest.main()

