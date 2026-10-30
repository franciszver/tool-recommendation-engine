import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo.py"


def run_demo(*args, stdin=""):
    return subprocess.run(
        [sys.executable, str(DEMO), *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=30,
    )


class ScriptedDemoTests(unittest.TestCase):
    def test_scripted_demo_exits_zero_and_shows_each_scene(self):
        result = run_demo()
        self.assertEqual(result.returncode, 0, result.stderr)
        for heading in (
            "Scene 1",
            "Scene 2",
            "Scene 3",
            "Scene 4",
            "Scene 5",
            "Scene 6",
            "Scene 7",
        ):
            self.assertIn(heading, result.stdout)
        self.assertIn("All demo checks passed", result.stdout)

    def test_scripted_demo_shows_scores(self):
        result = run_demo()
        self.assertRegex(result.stdout, r"\d\.\d{4}")


class InteractiveDemoTests(unittest.TestCase):
    def test_interactive_session(self):
        script = "\n".join(
            [
                "tool jira create a bug ticket",
                "tool email send an email",
                "msg alice file a bug ticket",
                "rec alice 3",
                "show alice",
                "quit",
            ]
        )
        result = run_demo("--interactive", stdin=script + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        rec_lines = [
            line
            for line in result.stdout.splitlines()
            if line.startswith("recommendations for alice")
        ]
        self.assertEqual(len(rec_lines), 1, result.stdout)
        self.assertIn("jira", rec_lines[0])
        self.assertNotIn("email", rec_lines[0])

    def test_interactive_reports_bad_command_and_continues(self):
        result = run_demo("--interactive", stdin="bogus\nquit\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Unknown command", result.stdout)

    def test_interactive_ends_on_eof(self):
        result = run_demo("--interactive", stdin="")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
