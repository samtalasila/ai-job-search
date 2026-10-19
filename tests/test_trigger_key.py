"""Tests for tools/trigger_key.py - the canonical seen_triggers.json key function.

The key rule is prose only in the source contract, so runs slugified
inconsistently and the state file accumulated two failure classes: keys
carrying "/", "," and "&" that break anything derived from them as paths, and
the same signal stored twice under two different truncations of a long
description. These pin the fix - a pure, deterministic function of
(company, signal, url) - and the audit that finds drift in an existing state
file.
"""
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from trigger_key import key, slug  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "trigger_key.py"


def digest(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]


class Slugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slug("VersaBank"), "versabank")

    def test_strips_punctuation_that_breaks_paths(self):
        self.assertEqual(slug("Acme Lending, Inc."), "acme-lending-inc")
        self.assertEqual(slug("Bank & Trust / Ops"), "bank-trust-ops")

    def test_non_latin_script_falls_back_to_untitled(self):
        self.assertEqual(slug("시큐리온"), "untitled")

    def test_long_text_is_truncated_with_a_digest(self):
        long = "frontier ai named in the fall risk update with substantial trailing text"
        s = slug(long)
        self.assertTrue(len(s) <= 60)
        self.assertRegex(s, r"-[0-9a-f]{8}$")


class MakeKey(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(
            key("VersaBank", "AI program launched", "https://example.com/1"),
            f"versabank--ai-program-launched--{digest('https://example.com/1')}",
        )

    def test_deterministic_across_calls(self):
        desc = "Superintendent remarks on responsible AI adoption at the regulator summit"
        self.assertEqual(key("OSFI", desc, "https://example.com/2"), key("OSFI", desc, "https://example.com/2"))

    def test_long_descriptions_never_collide_after_truncation(self):
        """The bug that produced two entries for one signal: two runs
        truncated the same long description at different points. A hash of the
        full slug inside slug() makes truncation deterministic instead of
        lossy, so near-identical long descriptions still key differently."""
        a = key("OSFI", "Frontier AI named in the fall risk update with trailing text A", "https://example.com/x")
        b = key("OSFI", "Frontier AI named in the fall risk update with trailing text B", "https://example.com/x")
        self.assertNotEqual(a, b)

    def test_distinct_urls_still_get_distinct_keys(self):
        a = key("VersaBank", "AI program launched", "https://example.com/1")
        b = key("VersaBank", "AI program launched", "https://example.com/2")
        self.assertNotEqual(a, b)

    def test_empty_company_falls_back_to_untitled(self):
        self.assertTrue(key("", "AI program launched", "https://example.com/1").startswith("untitled--"))

    def test_empty_url_hashes_stably(self):
        self.assertEqual(key("OSFI", "update", ""), key("OSFI", "update", ""))
        self.assertTrue(key("OSFI", "update", "").endswith(f"--{digest('')}"))


class KeyCLI(unittest.TestCase):
    def run_tool(self, *args):
        proc = subprocess.run(
            [sys.executable, str(TOOL), *args],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        return proc.stdout.strip()

    def test_company_signal_url_produces_a_canonical_key(self):
        k = self.run_tool("--company", "VersaBank", "--signal", "AI program launched",
                          "--url", "https://example.com/1")
        self.assertEqual(k, f"versabank--ai-program-launched--{digest('https://example.com/1')}")

    def test_cli_matches_library(self):
        company, signal, url = "OSFI", "Frontier AI in fall risk update", "https://example.com/2"
        self.assertEqual(self.run_tool("--company", company, "--signal", signal, "--url", url),
                         key(company, signal, url))

    def test_missing_signal_is_not_an_error(self):
        # The tool never requires arguments: empty inputs hash stably.
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--company", "VersaBank"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("Traceback", proc.stderr)


class AuditCLI(unittest.TestCase):
    def test_no_state_file_reports_nothing_and_exits_zero(self):
        # Fresh checkout: the repo's own state file is gitignored, so --audit
        # must exit 0. If a local state file exists (real runs), skip - it is
        # machine-local data, not a test fixture.
        from trigger_key import STATE

        if STATE.exists():
            self.skipTest("local seen_triggers.json exists; skipping no-state audit check")
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--audit"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("nothing to audit", proc.stdout)

    def test_state_resolves_to_the_skill_relative_path(self):
        # The skill writes seen-signal state to trigger_scraper/ relative to
        # its own directory; the audit must read that same file, not a
        # repo-rooted path that never exists.
        from trigger_key import STATE

        self.assertEqual(
            STATE,
            REPO / ".claude" / "skills" / "trigger-scout" / "trigger_scraper" / "seen_triggers.json",
        )


if __name__ == "__main__":
    unittest.main()
