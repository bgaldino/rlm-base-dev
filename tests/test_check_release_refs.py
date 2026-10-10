"""Offline fixtures for scripts/ai/check_release_refs.py.

Both directions, because a pattern that fires on paths or ID prefixes gets ignored, and one
that misses a numbered branch lets the next cutover strand a tool default again.
Stdlib only. Run with: python tests/test_check_release_refs.py
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_release_refs as crr  # noqa: E402

REF = crr.ref_pattern(crr.KNOWN_REMOTES)


def rules(line):
    return [rule for _, rule, _ in crr.findings(line, REF)]


class NumberedBranches(unittest.TestCase):
    def test_numbered_refs_and_branches_fail(self):
        for line in ("python scripts/ai/pr_gate.py --base origin/264",
                     "git diff labs/264 --stat", "--base=264", "git push origin refs/heads/264",
                     'DEFAULT_BASE = "origin/264"',
                     "never push to the active release branch (`264`)",
                     "the sync PR (`main` merged into `264`)",
                     "required on `main`, `264` and `release/*`"):
            with self.subTest(line=line):
                self.assertTrue(rules(line), line)

    def test_role_names_paths_and_other_numbers_pass(self):
        for line in ("python scripts/ai/pr_gate.py --base origin/main",
                     "cut `release/264` from `main`, merge `preview/266` into `main`",
                     "see docs/salesforce/264/help/articles/ for the snapshot",
                     "bills 450 x (366/365)", "503/503 checks passed on the branch",
                     "ContentDocument Id (`069` prefix) — not a branch",
                     "returns `200` when the PR is merged", "a live 264 org is ground truth",
                     "Bare positive int: ``364`` -> 364 days forward",
                     "int `123` -> `\"123\"`, same as a literal",
                     'salesforce_release_active: "264"',
                     "the `264` branch existed then  <!-- release-ref: allow -->"):
            with self.subTest(line=line):
                self.assertEqual(rules(line), [], line)

    def test_remotes_found_at_run_time_count(self):
        ref = crr.ref_pattern(["fork"])
        self.assertTrue(list(crr.findings("git diff fork/264", ref)))
        self.assertFalse(list(crr.findings("git diff fork/main", ref)))

    def test_a_finding_fails_the_run_and_a_clean_file_passes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bad, good = Path(tmp) / "bad.md", Path(tmp) / "good.md"
            bad.write_text("Run `git diff origin/264` first.\n")
            good.write_text("Run `git diff origin/main` first.\n")
            self.assertEqual(crr.main([str(bad)]), 1)
            self.assertEqual(crr.main([str(good)]), 0)


if __name__ == "__main__":
    unittest.main()
