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
                     "python scripts/ai/check_branch_scope.py --head 264",
                     "gh pr create --head 264 --base main", "--head=origin/264",
                     'gh pr create --base "264"', "check_branch_scope.py --head '264'",
                     "gh pr create --base  264", "check_branch_scope.py --head\t264",
                     "git clone --branch 264 https://example.com/r.git",
                     "gh pr create -B 264", "gh pr create -H 264 -B main",
                     "gh pr create --head alice:264",
                     "release 264 is now on `main`", "`main` now carries Release 264",
                     "Foundations' skill (shipped in Release 262, now on `main`)",
                     # Exact refs stay checked on a long (minified-looking) line.
                     "x" * 2100 + " git diff origin/264", '"active_work_branch":"264",' + "x" * 2100,
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
                     "retarget #285 from 264", "sync 264 → main by PR",
                     "| The deep pre-merge audit of a branch before `264 → main` | Yes |",
                     "**This branch:** Release 264 (Winter '27), API v68.0.",
                     "the branch is 262 until cutover"):
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
                     "merged into main in 264", "branch protection: 3 rules",
                     "**This branch:** the current line; see Branch Information",
                     "verify against a live 264 org built from `main`",
                     "shipped in Release 262"):
            with self.subTest(line=line):
                self.assertEqual(rules(line), [], line)

    def test_numbered_branches_in_code_fail(self):
        # Spelled without backticks or a remote, these passed the first two rules; the two
        # config lines are the ones this repo actually carried (agent context and manifest).
        for line in ('DEFAULT_BASE = "264"', "git checkout 264", "base: 264",
                     'PROTECTED = ("main", "264")', "git switch 262", "git push origin 264",
                     "branches: [main, 264]", 'targetBranch: "264"',
                     '"active_work_branch": "264",', 'branch_active: "264"',
                     # Inside revision syntax: ranges, refspecs, suffixes.
                     "git diff 264..HEAD", "git log main...264", "git push origin 264:preview/266",
                     "git push origin +264", "git diff 264^", "git log 264~3 -1",
                     "git checkout 264@{1}", "git push origin :264", "git diff 264...HEAD",
                     "git log 264..main", "git show 264:README.md", "git rev-parse 264",
                     "git merge-base main 264", "git --no-pager log 264",
                     "git --paginate show 264:README.md", "git -P diff 264",
                     "git --git-dir=.git --work-tree . checkout 264",
                     "git clone -b 264 https://example.com/r.git",
                     "git clone --branch=264 https://example.com/r.git",
                     'DEFAULT_BASE = os.getenv("BASE", "264")',
                     "git config branch.feature.gh-merge-base 264", "git format-patch 264..HEAD",
                     "git archive 264", "git blame 264 -- README.md", "git tag v1 264",
                     'BASE_BRANCH="${BASE_BRANCH:-264}"', "git log ${TARGET_REF:-264}",
                     "base_ref = env.get('BASE_REF', '262')"):
            with self.subTest(line=line):
                self.assertEqual(rules(line), ["code"], line)

    def test_numbered_branches_across_lines_fail_at_their_first_line(self):
        for text in ('PROTECTED = (\n    "main",\n    "264",\n)', "git checkout \\\n  264",
                     "branches: [\n  main,\n  264\n]", "git push origin \\\n  main \\\n  264",
                     "branches: [main,\n  264\n]", 'PROTECTED = {"main",\n  "264"\n}',
                     'PROTECTED = {\n  "main",\n  "264",\n}',
                     "branches:\n  - main\n  - 264", "branches:\n- main\n- '264'",
                     # Comments and blank lines inside the sequence don't end it.
                     "branches:\n  # migration\n  - main\n  - 264",
                     "branches:\n\n  - main\n\n  - 264"):
            with self.subTest(text=text):
                self.assertEqual([(n, r) for n, r, _ in crr.findings(text, REF)], [(1, "code")])
        # A --base/--head value continued onto the next line: a ref, at the command's line.
        for text in ("python scripts/ai/pr_gate.py --base \\\n  264",
                     "gh pr create --head \\\n  264 --base main"):
            with self.subTest(text=text):
                self.assertEqual([(n, r) for n, r, _ in crr.findings(text, REF)], [(1, "ref")])
        # A GitHub Actions branch filter: reported at its `branches:` line.
        workflow = "on:\n  push:\n    branches:\n      - main\n      - 264\n"
        self.assertEqual([(n, r) for n, r, _ in crr.findings(workflow, REF)], [(3, "code")])

    def test_multiline_values_that_are_not_branches_pass(self):
        for text in ("git log -n \\\n  100", 'PROTECTED = (\n  "main",\n)\nx = 264',
                     'targets = [  # roles\n  "main",\n]\nport = (\n  264,\n)',
                     "git diff \\\n  HEAD~100", 'refs = {"main": 1}\nport = 264',
                     'base: {\n  "name": "main"\n}\ntimeout = 300',
                     # YAML: the sequence ends at a shallower line, and a non-branch key's
                     # items don't count.
                     "branches:\n  - main\nport: 264", "items:\n  - 264\n  - 265",
                     "branches:\n  - main\n  - release/264\n  - preview/266",
                     # The ERD schema's shape: a branch word in a key whose value is an object.
                     '"GrantBindingTargetType": {\n  "length": 255,\n  "type": "picklist"\n}'):
            with self.subTest(text=text):
                self.assertEqual(list(crr.findings(text, REF)), [])

    def test_numbers_in_code_that_are_not_branches_pass(self):
        # Counts, measurements, paths, IDs and other repos' branch names found while
        # calibrating against this repo (keyPrefix appears 36 times in the ERD snapshots).
        for line in ("git log -n 100", "git log HEAD~100", "git diff -U 200 main",
                     "git log HEAD~100..HEAD", "git diff main...feat/x", "git log --depth=100",
                     "git push origin main:release/264", "git diff HEAD@{100}",
                     "git show HEAD:README.md", "git rev-list --count HEAD",
                     "git --no-pager log -n 100", "input.targetPrice = 150;",
                     'DEFAULT_BASE = os.getenv("BASE", "main")', "base_timeout = int('300')",
                     "git diff --stat-width=264 main", "git diff --stat-width 264 main",
                     "git gc --prune=100", "git log --abbrev=100", "git blame -L 100,200 f.py",
                     "git config core.bigFileThreshold 512", "git config http.postBuffer 524",
                     'TIMEOUT="${TIMEOUT:-300}"', "rg -B 100 pattern", "grep -H 200 x",
                     # A call-wrapped quoted number on a minified line is noise.
                     "x" * 2100 + ' base=fn("264")',
                     "git clone --depth=100 https://example.com/r.git",
                     "timeout_base = 300", "branch_count = 3", 'ref = "main"',
                     "base: origin/main", "git checkout release/264", "max_refs = [1, 2]",
                     '"keyPrefix": "001",', 'branch:"262-patch"',
                     'salesforce_release_active: "264"', 'api_version: "64.0"'):
            with self.subTest(line=line):
                self.assertEqual(rules(line), [], line)

    def test_the_gate_runs_it_on_every_change(self):
        # The scope is every tracked text file, so no trigger list can mirror it; the gate
        # has to run it unconditionally, or a change to an unlisted file skips the check.
        import pr_gate
        check = next(c for c in pr_gate.CHECKS if c["name"] == "release_refs")
        self.assertTrue(check.get("always"))
        self.assertTrue(pr_gate.selects(check, ["any/unlisted/file.md"]))

    def test_readme_and_current_docs_are_scanned_and_help_snapshots_are_not(self):
        scanned = {p.relative_to(REPO).as_posix() for p in crr.tracked_scope()}
        self.assertIn("README.md", scanned)
        self.assertIn("cumulusci.yml", scanned)
        # Directories a path list used to miss, named by top-level segment rather than by
        # path so this test doesn't read files it can't select (test_pr_gate's read rule).
        roots = {p.split("/", 1)[0] for p in scanned}
        self.assertLessEqual({"docker", "orgs", "datasets", "postman", "robot"}, roots)
        names = {p.rsplit("/", 1)[-1] for p in scanned}
        # Any text format, not an allowlist of suffixes: HTML docs and JS/MJS tooling too.
        suffixes = {p.rsplit(".", 1)[-1] for p in names if "." in p}
        self.assertLessEqual({"html", "js", "mjs", "md", "yml", "py"}, suffixes)
        self.assertIn("Dockerfile", names)
        # Extensionless launchers, found by their shebang (this repo has at least three).
        launchers = [p for p in scanned if "." not in p.rsplit("/", 1)[-1]
                     and p.rsplit("/", 1)[-1] != "Dockerfile"]
        self.assertGreaterEqual(len(launchers), 3, launchers)
        self.assertTrue([p for p in scanned if p.endswith(".robot")])
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
