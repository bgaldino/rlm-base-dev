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
                     "gh pr create --head alice:264", "gh pr create -B=264",
                     "git checkout refs/remotes/origin/264", "git push origin -- 264",
                     "git restore -s 264 -- file.txt", "git restore -s264 file.txt",
                     "git config --type path branch.foo.gh-merge-base 264",
                     "git grep -eTODO 264", "git grep --regexp=TODO 264",
                     "git worktree add ../wt 264", "git worktree add -b feat ../wt 264",
                     "git grep -e TODO -L 264", "git grep -n TODO 264",
                     "/usr/bin/git checkout 264", "git log ^264 main", "git rev-list main ^264",
                     'parser.add_argument("--base", default=os.getenv("BASE") or "264")',
                     "the `264` active maintenance branch", "the 262 old maintenance branch",
                     "git worktree add -b 264 ../wt main",
                     'ap.add_argument("--base", choices=("main", "264"), default="264")',
                     'subprocess.run(["git", "diff", "264..HEAD"])',
                     "run(['git', 'checkout', '264'], check=True)",
                     'subprocess.run(["gh", "pr", "create", "--base", "264"])',
                     'the "264" branch is retired', "the '264' branch is retired",
                     "gh pr create -H=alice:264", "sync 264 -> preview/266",
                     "264 → release/262 backport", "preview/266 -> 264",
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
                     "git --config-env=http.extraHeader=HEADER checkout 264",
                     "git --exec-path=/x --no-replace-objects log 264",
                     'parser.add_argument("--base", default="264")',
                     "@click.option('--head', default='264', help='PR head')",
                     'parser.add_argument("--base", default=os.getenv("BASE", "264"))',
                     "click.option('--head', default=os.environ.get('HEAD_REF', '262'))",
                     "git clone -b264 https://example.com/r.git", "git checkout -B264",
                     "git switch -c264",
                     'git log --format="%h | %s" 264', "git log --format='# %h' 264",
                     'DEFAULT_BASE = os.getenv("BASE") or "264"',
                     "base_ref = env.get('BASE_REF') if env else '262'",
                     'PROTECTED_BRANCHES = {"main": True, "264": True}',
                     "git fetch origin && git checkout 264", "git status; git switch 264",
                     "git grep TODO 264", "git restore --source=264 README.md",
                     'git -c http.extraHeader="Authorization: Bearer x" checkout 264',
                     "git --config-env 'http.extraHeader=TOKEN' checkout 264",
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

    def test_a_wrapped_call_default_and_wrapped_prose_fail_at_their_first_line(self):
        for text in ('DEFAULT_BASE = os.getenv(\n    "BASE", "264"\n)',
                     'protected_branches:\n  main: true\n  "264": true',
                     'PROTECTED_BRANCHES = {\n  "main": {"reviews": 2},\n  "264": {"reviews": 2},\n}',
                     'subprocess.run([\n    "git",\n    "checkout",\n    "264",\n])',

                     'const DEFAULT_BASE =\n  "264";',
                     "Created with the `264`\nbranch cut so the directory exists.",
                     "the sync PR merged\ninto `264` first."):
            with self.subTest(text=text):
                self.assertEqual([n for n, _, _ in crr.findings(text, REF)], [1])
        # An argv list opened on its own line: reported where the list opens.
        argv = 'subprocess.run(\n    [\n        "gh", "pr", "create",\n        "--base", "264",\n    ]\n)'
        self.assertEqual([n for n, _, _ in crr.findings(argv, REF)], [2])
        for text in ('timeout = os.getenv(\n    "T", "300"\n)',
                     "protected_branches:\n  main:\n    reviews: 264",
                     'PROTECTED = {\n  "main": {"100": 2},\n}',
                     "settings:\n  264: true",
                     "Release 264 shipped.\nThe branch is `main`.",
                     "a live 264 org\nbuilt from `main`"):
            with self.subTest(text=text):
                self.assertEqual(list(crr.findings(text, REF)), [])

    def test_a_wrapped_option_declaration_fails_at_its_call(self):
        text = 'ap.add_argument(\n    "--base",\n    default="264",\n    help="base ref",\n)'
        self.assertEqual([(n, r) for n, r, _ in crr.findings(text, REF)], [(1, "code")])

    def test_multiline_values_that_are_not_branches_pass(self):
        for text in ("git log -n \\\n  100", 'PROTECTED = (\n  "main",\n)\nx = 264',
                     'targets = [  # roles\n  "main",\n]\nport = (\n  264,\n)',
                     "git diff \\\n  HEAD~100",
                     # The allow marker works on the line that keeps the number.
                     "branches:\n  - main\n  - 264 # release-ref: allow",
                     "PROTECTED = (\n  \"main\",\n  \"264\",  # release-ref: allow\n)",
                     "git checkout \\\n  264  # release-ref: allow", 'refs = {"main": 1}\nport = 264',
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
                     'ap.add_argument("--timeout", default=300)',
                     'ap.add_argument("--base", default="main")', "git --version 264",
                     'ap.add_argument("--base", default=os.getenv("BASE", "main"))',
                     'ap.add_argument("--timeout", default=int(os.getenv("T", "300")))',
                     "git log -n100", "cut `release/264` from `main` -> `preview/266`",
                     "git grep 264", "git grep -n 264 -- docs", "git restore 264",
                     'PROTECTED = {"main": {"reviews": 2, "timeout": 300}}',
                     "git status && echo 264", "git log -- 264", "git checkout -- 264",
                     "git diff main -- docs/264", 'x = "264"', "if a == \n  264:",
                     'the "200" status code', "'069' prefix",
                     "# The shared git-tracking helpers (scripts/repo_paths.py, pack 167)",
                     "use git to compare 264 snapshots", "cd .git && ls 264",
                     "git grep -e 264", "git grep -e 264 -e 262 main", "git grep -e264",
                     "git worktree remove 264", "git worktree move old 264",
                     "git worktree add -b topic 264 main", "git blame -L 100 f.py",
                     "git archive -o 264 HEAD", "git tag -m 264 v1", "ls /srv/git/264",
                     "cd repo.git 264",
                     "git log -n 100 main", "git diff -U 200 main",
                     "a live 264 org built off this branch",
                     "git worktree add 264", "git config --type int core.bigFileThreshold 512",
                     'ap.add_argument("--base", choices=("main", "x"), default="main")',
                     'subprocess.run(["git", "log", "-n", "100"])',
                     'subprocess.run(["git", "add", "264"])', 'run(["gh", "pr", "view", "264"])',
                     # Pathspec-only subcommands: the number is a path.
                     "git add 264", "git rm 264", "git status 264", "git ls-files 264",
                     "git clone https://example.com/r.git 264", "git commit -m 264",
                     'git log --format="%h | 264"', "git log main | head -264",
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
        self.assertFalse([p for p in docs if p.startswith(crr.EXCLUDE) or crr.CAPTURED.match(p)])
        # Release-root docs beside the captured corpora are maintained here, so they're scanned.
        self.assertTrue([p for p in docs if p.endswith("feature-index.md") and
                         p.startswith("docs/sales")])

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
