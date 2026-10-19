"""The Python tools must write UTF-8 whatever the host's default encoding is.

On Windows a piped stdout (which is how Claude Code runs every tool) defaults
to the ANSI code page, cp1252 on most Western installs. A tool that prints a
non-Latin company or signal name then dies with UnicodeEncodeError before the
workflow sees any output.

Each case runs the real CLI in a child process with a legacy stdout forced via
PYTHONIOENCODING, so the Linux CI job reproduces what Windows users hit. The
child must exit cleanly and its bytes must decode as UTF-8.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"

# One name per script family that cp1252 cannot encode.
CYRILLIC = "Яндекс"
CJK = "腾讯"


def run_legacy_stdout(argv, cwd=None):
    """Run a tool the way a Western-locale Windows host pipes it."""
    env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
    return subprocess.run([sys.executable, *map(str, argv)], cwd=cwd, env=env, capture_output=True)


class ToolsWriteUtf8(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)

    def assert_clean_utf8(self, proc, expect_code, *needles, stream="stdout"):
        err = proc.stderr.decode("utf-8", "replace")
        self.assertNotIn("UnicodeEncodeError", err)
        self.assertEqual(proc.returncode, expect_code, err)
        text = getattr(proc, stream).decode("utf-8")
        for needle in needles:
            self.assertIn(needle, text)
        return text

    def test_trigger_key_prints_non_latin_company_and_signal(self):
        # Firm and signal names arrive in the script of the source market;
        # the process must exit cleanly with UTF-8 output either way. A
        # mixed-script name keeps its Latin fragment in the printed key.
        proc = run_legacy_stdout([
            TOOLS / "trigger_key.py",
            "--company", CYRILLIC + " Bank", "--signal", "Программа launch",
            "--url", "https://example.com/1",
        ])
        self.assert_clean_utf8(proc, 0, "bank", "launch")

    def test_trigger_key_audit_names_non_latin_entries(self):
        # --audit prints mismatched keys; a stored non-Latin key must not
        # break the report. Point the tool at a temp repo layout by copying
        # it next to a trigger_scraper state file.
        import shutil

        repo = self.tmp / "repo"
        (repo / "tools").mkdir(parents=True)
        (repo / ".claude" / "skills" / "trigger-scout" / "trigger_scraper").mkdir(parents=True)
        shutil.copy(TOOLS / "trigger_key.py", repo / "tools" / "trigger_key.py")
        (repo / ".claude" / "skills" / "trigger-scout" / "trigger_scraper" / "seen_triggers.json").write_text(
            '{"seen": {"bogus_key": {"company": "%s", "signal": "x", "url": ""}}}' % CJK,
            encoding="utf-8",
        )
        proc = run_legacy_stdout([repo / "tools" / "trigger_key.py", "--audit"])
        self.assertNotIn(b"UnicodeEncodeError", proc.stderr)
        self.assertEqual(proc.returncode, 1)  # one mismatched key
        self.assertIn("MISMATCH", proc.stdout.decode("utf-8"))

    def test_security_guards_output_is_utf8(self):
        proc = run_legacy_stdout([TOOLS / "security_guards.py"])
        self.assert_clean_utf8(proc, 0, "security_guards: OK")

    def test_lint_skills_output_is_utf8(self):
        proc = run_legacy_stdout([TOOLS / "lint_skills.py"])
        self.assert_clean_utf8(proc, 0, "lint_skills: OK")


if __name__ == "__main__":
    unittest.main()
