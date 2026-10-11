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
                     "required on `main`, `264` and `release/*`",
                     "Prior GA reference (the `262` maintenance branch)",
                     # Unquoted, in phrases that can only mean a branch.
                     "Retarget a green PR from 264 to main and no event fires",
                     "the 264 branch is in sync", "the 262 maintenance branch",
                     "check out branch 264", "it was merged into 264 first",
                     "retarget #285 from 264", "sync 264 → main by PR"):
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
                     "the `264` branch existed then  <!-- release-ref: allow -->",
                     # Unquoted release numbers in ordinary prose stay quiet.
                     "Release 264 (Winter '27) is the GA line",
                     "an upgraded 262 org keeps settings a fresh 264 org lacks",
                     "262 is the prior GA reference; 260 extracts remain",
                     "every scratch org it creates is a 264 org regardless of branch",
                     "from 260 to 262 the schema grew", "the release/264 branch",
                     "merged into main in 264"):
            with self.subTest(line=line):
                self.assertEqual(rules(line), [], line)

    def test_numbered_branches_in_code_fail(self):
        # Spelled without backticks or a remote, these passed the first two rules; the two
        # config lines are the ones this repo actually carried (agent context and manifest).
        for line in ('DEFAULT_BASE = "264"', "git checkout 264", "base: 264",
                     'PROTECTED = ("main", "264")', "git switch 262", "git push origin 264",
                     "branches: [main, 264]", 'targetBranch: "264"',
                     '"active_work_branch": "264",', 'branch_active: "264"'):
            with self.subTest(line=line):
                self.assertEqual(rules(line), ["code"], line)

    def test_numbers_in_code_that_are_not_branches_pass(self):
        # Counts, measurements, paths, IDs and other repos' branch names found while
        # calibrating against this repo (keyPrefix appears 36 times in the ERD snapshots).
        for line in ("git log -n 100", "git log HEAD~100", "git diff -U 200 main",
                     "timeout_base = 300", "branch_count = 3", 'ref = "main"',
                     "base: origin/main", "git checkout release/264", "max_refs = [1, 2]",
                     '"keyPrefix": "001",', 'branch:"262-patch"',
                     'salesforce_release_active: "264"', 'api_version: "64.0"'):
            with self.subTest(line=line):
                self.assertEqual(rules(line), [], line)

    def test_the_gate_selects_on_exactly_the_scanned_scope(self):
        # The gate mirrors SCOPE in its triggers; a scope entry missing there means a change
        # to that file never runs the check that audits it.
        import pr_gate
        check = next(c for c in pr_gate.CHECKS if c["name"] == "release_refs")
        self.assertEqual(sorted(check["triggers"]), sorted(crr.SCOPE))

    def test_readme_and_current_docs_are_scanned_and_help_snapshots_are_not(self):
        scanned = {p.relative_to(REPO).as_posix() for p in crr.tracked_scope()}
        self.assertIn("README.md", scanned)
        docs = [p for p in scanned if p.startswith("docs")]
        self.assertTrue([p for p in docs if "/" in p and p.count("/") == 1], "docs root unscanned")
        self.assertFalse([p for p in docs if p.startswith(crr.EXCLUDE)])

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
