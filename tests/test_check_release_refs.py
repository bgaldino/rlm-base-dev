"""Offline fixtures for scripts/ai/check_release_refs.py.

Both directions, because a pattern that fires on paths or valid names gets ignored, and one
that misses a numbered branch lets the next cutover strand a tool default again. The checker
is a best-effort lint with a documented contract; these pin that contract, not every
spelling git or a shell accepts (the server ruleset is the backstop for those).
Stdlib only. Run with: python tests/test_check_release_refs.py
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_release_refs as crr  # noqa: E402

REF = crr.ref_pattern(crr.KNOWN_REMOTES)


def rules(text):
    return [rule for _, rule, _ in crr.findings(text, REF)]


class Contract(unittest.TestCase):
    def assert_flagged(self, rule, cases):
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(rules(text), [rule], text)

    def assert_clean(self, cases):
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(rules(text), [], text)

    def test_numbered_refs_fail(self):
        self.assert_flagged("ref", (
            "python scripts/ai/pr_gate.py --base origin/264", "git diff labs/264 --stat",
            "--base=264", "--head '264'", "git push origin refs/heads/264",
            "git log refs/remotes/origin/264", 'DEFAULT_BASE = "origin/264"',
            "gh pr create --base 264", "see origin/264."))

    def test_numbered_branches_in_git_commands_fail(self):
        self.assert_flagged("git", (
            "git checkout 264", "git switch 262", "git push origin 264", "git merge 264",
            "git rebase 264", "git diff 264..HEAD", "git log main...264",
            "git push origin 264:preview/266", "git worktree add ../wt 264",
            "git log 264~3", "git rev-list 264..HEAD", "Run git checkout 264.",
            "Run git merge 264, then continue", "(or git switch '264')"))

    def test_numbered_branch_settings_fail(self):
        self.assert_flagged("setting", (
            'DEFAULT_BASE = "264"', "base: 264", 'PROTECTED = ("main", "264")',
            "branches: [main, 264]", 'targetBranch: "264"', '"active_work_branch": "264",',
            "BASE_BRANCH ?= 264", "BASE_BRANCH ::= 264", "BASE_BRANCH := 264", "branches:\n  - main\n  - 264",
            "on:\n  push:\n    branches:\n      - 264", "base = 264.", 'targets: ["main", "264"]'))

    def test_numbered_branches_in_prose_fail(self):
        self.assert_flagged("prose", (
            "never push to the active release branch `264` directly",
            "the `262` maintenance branch", "the 264 branch is in sync", "branch 264",
            "merged into `264`", "from 264 to main", "264 → main", "main -> `264`",
            "it was merged into 264.", "merge 264 into main", "rebasing `262` onto main"))

    def test_valid_names_and_other_numbers_pass(self):
        # Role prefixes and suffixed names are the pattern, not a violation.
        self.assert_clean((
            "git checkout release/264", "git push origin release/264",
            "cut `release/264` from `main`, merge `preview/266` into `main`",
            "git diff origin/264-dev", "git checkout 264-dev", "git checkout feat/264-fix",
            "--base origin/264-dev", "the `264-dev` branch", "git log remotes/origin/264.x",
            "git show archive/264", 'DEFAULT_BASE = "264-dev"', "branches: [main, 264-dev]"))
        # Product release numbers, paths, counts, IDs, codes and measurements.
        self.assert_clean((
            "a live 264 org is ground truth", "Release 264 (Winter '27) is the GA line",
            'salesforce_release_active: "264"', "see docs/salesforce/264/help/ for it",
            "git log -n 100", "git log HEAD~100", "git diff -U 200 main",
            "git fetch --depth 100", "bills 450 x (366/365)", "returns `200` when merged",
            "ContentDocument Id (`069` prefix)", 'api_version: "64.0"',
            "timeout_base = 300", "head_count = 100", 'branch:"262-patch"',
            '"keyPrefix": "001",', "if base_ref == 264:", "x = 264"))
        # Messages, search patterns, labels and counts that sit near branch words.
        self.assert_clean((
            'git log --grep "404 error"', "git diff -- 264", "git checkout main -- 264", "git log -S 123", 'git commit -m "fix 264 build"',
            "git log --since 100", "see the 500 open branches", "a 264 org build branch",
            "Target: 200 ms", "Protected: 300 files", 'branches: ["see 123 items"]',
            "targets: [x 100 y]"))

    def test_a_block_list_finding_names_the_item_line(self):
        self.assertEqual([(n, r) for n, r, _ in crr.findings("branches:\n  - main\n  - 264", REF)],
                         [(3, "setting")])

    def test_a_block_list_ends_at_its_dedent_however_long(self):
        long_list = "branches:\n" + "  - main\n" * 60 + "  - 264"
        self.assertEqual(rules(long_list), ["setting"])
        self.assertEqual(rules("rules:\n  - branches:\n      - main\n  - 264"), [])
        self.assertEqual(rules("rules:\n  - branches:\n    - main\n    - 264"), ["setting"])
        self.assertEqual(rules("branches:\n- main\n- 264"), ["setting"])
        self.assertEqual(rules("branches:\n  - ports:\n      - 264"), [])
        self.assertEqual(rules("branches:\n  - name: main\n    ports:\n      - 264\n  - 262"),
                         ["setting"])
        self.assertEqual(rules("branches:\n- main\nports:\n- 264"), [])

    def test_the_allow_marker_exempts_its_line_only(self):
        self.assert_clean(("the `264` branch existed then  <!-- release-ref: allow -->",
                           "branches:\n  - main\n  - 264 # release-ref: allow"))
        self.assert_flagged("setting", ("branches:  # release-ref: allow\n  - main\n  - 264",))

    def test_a_remote_named_like_a_role_does_not_make_role_branches_refs(self):
        ref = crr.ref_pattern(["release", "preview", "origin"])
        self.assertFalse(list(crr.findings("cut `release/264` from `main`", ref)))
        self.assertTrue(list(crr.findings("git diff origin/264", ref)))

    def test_remotes_found_at_run_time_count(self):
        ref = crr.ref_pattern(["fork"])
        self.assertTrue(list(crr.findings("git diff fork/264", ref)))
        self.assertFalse(list(crr.findings("git diff fork/main", ref)))


class Scope(unittest.TestCase):
    def test_every_tracked_text_file_is_scanned_except_captured_corpora(self):
        scanned = {p.relative_to(REPO).as_posix() for p in crr.tracked_scope()}
        self.assertIn("README.md", scanned)
        self.assertIn("cumulusci.yml", scanned)
        roots = {p.split("/", 1)[0] for p in scanned}
        self.assertLessEqual({"docker", "orgs", "datasets", "docs", "scripts", "tests"}, roots)
        self.assertFalse([p for p in scanned if crr.CAPTURED.match(p)])

    def test_maintainer_notes_inside_a_corpus_are_scanned(self):
        corpus = "docs/sales" + "force/264/help/articles/"
        self.assertTrue(crr.in_scope_name(corpus + "pricing.notes.md"))
        self.assertFalse(crr.in_scope_name(corpus + "pricing.md"))

    def test_the_exclusion_is_exact(self):
        self.assertFalse(crr.in_scope_name("tests/test_check_release_refs.py"))
        self.assertTrue(crr.in_scope_name("tests/test_check_release_refs.py.snapshot"))

    def test_the_gate_runs_it_on_every_change(self):
        import pr_gate
        check = next(c for c in pr_gate.CHECKS if c["name"] == "release_refs")
        self.assertTrue(check.get("always"))
        self.assertTrue(pr_gate.selects(check, ["any/unlisted/file.md"]))


class ExitCodes(unittest.TestCase):
    def test_a_finding_fails_the_run_and_a_clean_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad, good = Path(tmp) / "bad.md", Path(tmp) / "good.md"
            bad.write_text("Run `git diff origin/264` first.\n")
            good.write_text("Run `git diff origin/main` first.\n")
            self.assertEqual(crr.main([str(bad)]), 1)
            self.assertEqual(crr.main([str(good)]), 0)

    def test_a_failing_git_remote_is_a_tool_error(self):
        failed = subprocess.CompletedProcess([], 128, "", "fatal: not a git repository")
        with mock.patch.object(crr.subprocess, "run", return_value=failed):
            with self.assertRaises(OSError):
                crr.remotes()
        with mock.patch.object(crr, "remotes", side_effect=OSError("spawn failed")), \
                mock.patch.object(crr, "tracked_scope", return_value=[]):
            self.assertEqual(crr.main([]), 2)


if __name__ == "__main__":
    unittest.main()
