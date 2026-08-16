#!/usr/bin/env python3
"""Offline tests for scripts/ai/pr_gate.py — the PR gate's check selector and reporter.

The gate exists because a skipped check reads like a passing one, so these tests care most
about the ways it could go quiet: a suite no check runs, a missing dependency reported as a
skip, an advisory check silently promoted or demoted, a trigger list that selects nothing.

Run offline: python tests/test_pr_gate.py
"""

import ast
import importlib.util
import io
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts", "ai"))

import pr_gate  # noqa: E402

PASSED = 0
FAILED = []


def check(label, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}")
    else:
        FAILED.append(label)
        print(f"  [FAIL] {label}" + (f"\n         {detail}" if detail else ""))


def run_gate(*args):
    proc = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "ai", "pr_gate.py"),
                           *args], cwd=REPO, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def selected_names(files):
    return {c["name"] for c in pr_gate.CHECKS if pr_gate.selects(c, files)}


def main_with(args):
    """Drive main() in-process so the verdict itself is asserted, not just its helpers.

    Testing `missing_deps()` and `unlisted_suites()` in isolation left both able to report a
    problem while the gate still exited 0 — the absence hole this gate exists to prevent, in
    the gate's own tests. These go through the exit code.
    """
    # pr_gate_suite triggers on tests/, so a fixture naming a tests/ path would select this
    # very suite and main() would run it as a subprocess of itself. Refused here, once, rather
    # than trusted to every future call site: an unbounded recursion in a test that runs the
    # real gate is a hang, not a failure.
    if "--changed-files-from" in args:
        listed = args[args.index("--changed-files-from") + 1]
        with open(listed) as fh:
            fixture_paths = [ln.strip() for ln in fh if ln.strip()]
        nesting = [c["name"] for c in pr_gate.CHECKS
                   if pr_gate.selects(c, fixture_paths) and c["cmd"]
                   and "tests/test_pr_gate.py" in c["cmd"]]
        assert not nesting, f"fixture {fixture_paths} would nest the gate inside {nesting}"
    saved = sys.argv
    buf = io.StringIO()
    try:
        sys.argv = ["pr_gate.py", *args]
        with redirect_stdout(buf):
            try:
                code = pr_gate.main()
            except SystemExit as exc:
                # `die()` exits rather than returning, so a tool error arrives as SystemExit.
                # Letting it escape would abort this suite mid-run and look like a crash
                # instead of the exit code under test.
                code = exc.code if isinstance(exc.code, int) else 2
    finally:
        sys.argv = saved
    return code, buf.getvalue()


def changed_list(*paths):
    fh = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    fh.write("".join(p + "\n" for p in paths))
    fh.close()
    return fh.name


print("\nSelection maps a change to the checks that cover it")
sel = selected_names(["datasets/sfdmu/qb-pricing/export.json"])
check("a data plan change selects the plan README gate",
      "plan_readme_consistency" in sel, sel)
check("a data plan change selects the SFDMU validator", "sfdmu_datasets" in sel, sel)
sel = selected_names(["docs/guides/some-guide.md"])
check("a docs change selects the build-step citation check",
      "doc_build_steps" in sel, sel)
check("a docs change does not select the data plan gate",
      "plan_readme_consistency" not in sel, sel)
sel = selected_names(["cumulusci.yml"])
check("a cumulusci.yml change selects the CCI reference drift check",
      "cci_reference_drift" in sel, sel)
sel = selected_names(["docs/erds/erd-data.json"])
check("an ERD data change selects the ERD count check", "erd_doc_counts" in sel, sel)
# Selection must still be able to come up empty, or "selected" means nothing. The probe has
# to be outside the manifest audit's roots, which are deliberately repo-wide: a manifest can
# cite a path anywhere, so robot/ (a root) no longer qualifies as an unclaimed path.
sel = selected_names(["docker/Dockerfile"])
check("a path no check claims selects nothing rather than everything", sel == set(), sel)
# A suffix selector, for the check that walks every .md in the repo. Prefix triggers left
# the root README and seven datasets/**/README.md build-step citations unable to select the
# suite that audits them.
check("the root README selects the build-step check",
      "doc_build_steps" in selected_names(["README.md"]),
      selected_names(["README.md"]))
check("a data plan README selects the build-step check",
      "doc_build_steps" in selected_names(
          ["datasets/sfdmu/qb/en-US/qb-billing/README.md"]))
check("a non-markdown file does not select it via the suffix",
      "doc_build_steps" not in selected_names(["robot/x.robot"]))
check("only the whole-repo check carries a suffix selector",
      [c["name"] for c in pr_gate.CHECKS if c.get("suffixes")] == ["doc_build_steps"],
      [c["name"] for c in pr_gate.CHECKS if c.get("suffixes")])
check("a harness change selects the harness suites",
      "harness_suites" in selected_names(["scripts/txn_data_harness/cli.py"]))
check("an empty change set selects nothing", selected_names([]) == set())
# Triggers are path prefixes, not substrings: a vendored or nested lookalike must not
# select a check that has no authority over it.
check("a trigger embedded mid-path does not select",
      "plan_readme_consistency" not in selected_names(
          ["vendor/datasets/sfdmu/export.json"]),
      selected_names(["vendor/datasets/sfdmu/export.json"]))
check("a trigger at the start does select",
      "plan_readme_consistency" in selected_names(["datasets/sfdmu/export.json"]))

print("\nEvery check is well formed")
names = [c["name"] for c in pr_gate.CHECKS]
check("check names are unique", len(names) == len(set(names)), names)
check("every check has at least one trigger",
      all(c["triggers"] for c in pr_gate.CHECKS))
check("every declared dep is one the gate knows how to detect",
      all(d in pr_gate.DEPS for c in pr_gate.CHECKS for d in c["deps"]))
check("every non-gating check explains itself",
      all(c.get("note") for c in pr_gate.CHECKS if not c["gating"]))
check("agent_tooling declares the 3.10+ floor it actually needs",
      next(c for c in pr_gate.CHECKS if c["name"] == "agent_tooling")
      .get("min_python") == (3, 10))

print("\nNo suite goes unrun, and none is claimed but absent")
check("no suite in tests/ is left unclaimed", pr_gate.unlisted_suites() == [],
      pr_gate.unlisted_suites())
missing = [s for s in pr_gate.STDLIB_SUITES if not os.path.exists(os.path.join(REPO, s))]
check("every stdlib suite the gate names exists on disk", missing == [], missing)
missing = [s for s in pr_gate.CLAIMED_SUITES if not os.path.exists(os.path.join(REPO, s))]
check("every claimed suite or directory exists on disk", missing == [], missing)
missing = [s for s in pr_gate.EXCLUDED_SUITES if not os.path.exists(os.path.join(REPO, s))]
check("every excluded suite exists on disk", missing == [], missing)
check("every exclusion states a reason",
      all(r.strip() for r in pr_gate.EXCLUDED_SUITES.values()))
check("no suite is both claimed and excluded",
      not (set(pr_gate.EXCLUDED_SUITES) & pr_gate.CLAIMED_SUITES))
check("a suite is never run twice — no dedicated check's suite is also in a bulk list",
      "tests/test_branch_scope.py" not in pr_gate.STDLIB_SUITES
      and "tests/test_erd_doc_counts.py" not in pr_gate.STDLIB_SUITES)
# Discovery must recurse. A flat listing missed 30 suites in tests/build_harness/ and
# tests/txn_data_harness/ while reporting "none unclaimed".
nested = [s for s in pr_gate.CLAIMED_SUITES if s.endswith("/")]
check("nested suite directories are claimed as directories", len(nested) >= 2, nested)
real_nested = [
    f for d in nested
    for f in os.listdir(os.path.join(REPO, d))
    if f.startswith("test_") and f.endswith(".py")
]
check("those directories really do hold suites", len(real_nested) > 20, len(real_nested))

# A new suite must fail loudly rather than join silently — verified in a temp tree, so a
# crash cannot leave a stray file in the real tests/ that then fails everyone else's gate.
with tempfile.TemporaryDirectory() as fake_repo:
    os.makedirs(os.path.join(fake_repo, "tests", "nested"))
    open(os.path.join(fake_repo, "tests", "nested", "test_probe.py"), "w").close()
    saved_root = pr_gate.REPO_ROOT
    try:
        pr_gate.REPO_ROOT = fake_repo
        found = pr_gate.unlisted_suites()
        check("an unclaimed suite in a nested directory is detected",
              found == ["tests/nested/test_probe.py"], found)
        code, out = main_with(["--changed-files-from", os.devnull])
        check("an unclaimed suite fails the gate", code == 1, code)
        check("the unclaimed suite is named in the output", "suites no check runs" in out)
        # A shell suite must be discovered too, so excluding one is a declaration.
        open(os.path.join(fake_repo, "tests", "test-probe.sh"), "w").close()
        check("a shell suite is discovered rather than missed by the .py filter",
              "tests/test-probe.sh" in pr_gate.unlisted_suites(),
              pr_gate.unlisted_suites())
        # A directory claim covers pytest-collectable .py only. A shell suite dropped into a
        # claimed directory has no runner, so being "claimed" there would be a silent skip.
        claimed_dir = sorted(c for c in pr_gate.CLAIMED_SUITES if c.endswith("/"))[0]
        os.makedirs(os.path.join(fake_repo, claimed_dir), exist_ok=True)
        open(os.path.join(fake_repo, claimed_dir, "test_inside.py"), "w").close()
        open(os.path.join(fake_repo, claimed_dir, "test-inside.sh"), "w").close()
        listed = pr_gate.unlisted_suites()
        check("a .py suite under a claimed directory is covered by the claim",
              claimed_dir + "test_inside.py" not in listed, listed)
        check("a shell suite under a claimed directory is not covered by the claim",
              claimed_dir + "test-inside.sh" in listed, listed)
    finally:
        pr_gate.REPO_ROOT = saved_root

with tempfile.TemporaryDirectory() as empty:
    saved_root = pr_gate.REPO_ROOT
    try:
        pr_gate.REPO_ROOT = empty
        check("a missing tests/ directory is reported, not read as 'none unclaimed'",
              pr_gate.unlisted_suites() != [], pr_gate.unlisted_suites())
    finally:
        pr_gate.REPO_ROOT = saved_root

print("\nA missing dependency fails a gating check instead of skipping it")
fake_gating = dict(name="probe", cmd=["python", "-c", "pass"], triggers=["x"],
                   deps=["cumulusci"], gating=True)
saved = dict(pr_gate.DEPS)
try:
    pr_gate.DEPS["cumulusci"] = "a_module_that_does_not_exist_anywhere"
    check("a gating check with an absent dep reports it as missing",
          pr_gate.missing_deps(fake_gating) == ["cumulusci"],
          pr_gate.missing_deps(fake_gating))
finally:
    pr_gate.DEPS.clear()
    pr_gate.DEPS.update(saved)
check("a satisfied dep reports nothing missing",
      pr_gate.missing_deps(dict(fake_gating, deps=[])) == [])
check("a future python floor is reported as a missing dep",
      pr_gate.missing_deps(dict(fake_gating, deps=[], min_python=(99, 0))) != [])

# ...and the verdict, not just the report: an absent dependency has to fail the gate.
saved = dict(pr_gate.DEPS)
listing = changed_list("docs/guides/some-guide.md")
try:
    pr_gate.DEPS["cumulusci"] = "a_module_that_does_not_exist_anywhere"
    code, out = main_with(["--changed-files-from", listing])
    check("an absent dependency fails the gate rather than skipping it", code == 1, code)
    check("the absent dependency is named as MISSING-DEP", "MISSING-DEP" in out)
finally:
    pr_gate.DEPS.clear()
    pr_gate.DEPS.update(saved)
    os.unlink(listing)

print("\nA check that actually fails fails the gate")
# The gate's whole purpose. Without this, reclassifying every runtime failure as advisory
# would leave the suite green — the one mutation that survived the first round.
listing = changed_list("zz_probe_path/thing.txt")
pr_gate.CHECKS.append(dict(name="zz_probe_failing",
                           cmd=["python", "-c", "import sys; sys.exit(1)"],
                           triggers=["zz_probe_path/"], deps=[], gating=True))
try:
    code, out = main_with(["--changed-files-from", listing])
    check("a failing gating check exits 1", code == 1, code)
    check("a failing gating check is labelled FAIL", "[FAIL" in out)
    check("the failing check is named in the summary", "zz_probe_failing" in out)
    check("its output is echoed for diagnosis", "zz_probe_failing (FAIL)" in out)
    check("a failure with no output says so rather than showing an empty section",
          "the check produced no output" in out)
    pr_gate.CHECKS[-1]["gating"] = False
    pr_gate.CHECKS[-1]["note"] = "probe"
    code, out = main_with(["--changed-files-from", listing])
    check("the same failure as advisory does not fail the gate", code == 0, code)
    check("but is still reported as an advisory failure", "advisory failure" in out)
    # Advisory output is truncated to its head; a gating failure's is not, so it stays
    # diagnosable from the log alone.
    noisy = ["python", "-c",
             f"print('\\n'.join(str(i) for i in range({pr_gate.ADVISORY_HEAD + 30})))"
             "; import sys; sys.exit(1)"]
    pr_gate.CHECKS[-1]["cmd"] = noisy
    code, out = main_with(["--changed-files-from", listing])
    check("a long advisory report is truncated rather than dumped whole",
          "line(s) elided" in out, out[-300:])
    # The head, not the tail: the SFDMU validator's Critical counts are at the top, and
    # tailing kept twenty lines of passing plans and elided the only useful part.
    check("truncation keeps the beginning of an advisory report", "\n0\n" in out)
    check("...and drops the end",
          f"\n{pr_gate.ADVISORY_HEAD + 29}\n" not in out)
    pr_gate.CHECKS[-1]["gating"] = True
    code, out = main_with(["--changed-files-from", listing])
    check("a gating failure is never truncated", "line(s) elided" not in out)
    check("...and shows its earliest output too", "\n0\n" in out)
finally:
    pr_gate.CHECKS.pop()
    os.unlink(listing)

print("\nA hung check is bounded and reported, not left to burn the job's budget")
listing = changed_list("zz_probe_path/thing.txt")
saved_timeout = pr_gate.CHECK_TIMEOUT
pr_gate.CHECKS.append(dict(name="zz_probe_hang",
                           cmd=["python", "-c", "import time; time.sleep(30)"],
                           triggers=["zz_probe_path/"], deps=[], gating=True))
try:
    pr_gate.CHECK_TIMEOUT = 1
    code, out = main_with(["--changed-files-from", listing])
    check("a check exceeding the timeout fails the gate", code == 1, code)
    check("the timeout is named in the output", "timed out after 1s" in out, out[-300:])
finally:
    pr_gate.CHECK_TIMEOUT = saved_timeout
    pr_gate.CHECKS.pop()
    os.unlink(listing)

print("\nThe advisory carve-out stays exactly one check, with its reason")
advisory = [c for c in pr_gate.CHECKS if not c["gating"]]
check("exactly one check is advisory", len(advisory) == 1, [c["name"] for c in advisory])
check("the advisory one is the SFDMU validator",
      advisory and advisory[0]["name"] == "sfdmu_datasets")
check("its note cites the pack that keeps it advisory",
      advisory and "123" in advisory[0]["note"], advisory[0]["note"] if advisory else "")

print("\nA failure in one command does not hide the commands after it")
code, out, _ = pr_gate.run_sequence([["python", "-c", "print('first')"],
                                     ["python", "-c", "import sys; sys.exit(3)"],
                                     ["python", "-c", "print('third')"]])
check("a sequence reports non-zero when any command fails", code != 0, code)
check("commands before the failure still ran", "first" in out)
check("commands after the failure still ran", "third" in out)

print("\nDependency pins agree with the workflow that installs them")
prepare = os.path.join(REPO, ".github", "workflows", "prepare-rlm-org.yml")
if os.path.exists(prepare):
    with open(prepare) as fh:
        body = fh.read()
    pinned = re.findall(r"cumulusci==([\d.]+)", body)
    gate_pin = re.findall(r"cumulusci==([\d.]+)", pr_gate.PINS.get("cumulusci", ""))
    check("the gate pins the same CumulusCI version prepare-rlm-org installs",
          bool(pinned) and bool(gate_pin) and pinned[0] == gate_pin[0],
          f"prepare-rlm-org={pinned}, pr_gate={gate_pin}")
else:
    check("prepare-rlm-org.yml exists to compare pins against", False, "file missing")

print("\nSelection reads the merge base, so commits landed on the base after divergence "
      "do not enlarge it")
# Hermetic: a throwaway repo, so this asserts git behaviour rather than whatever the real
# repo happens to look like. A two-dot diff here would pick up base_only.txt and select
# checks for a file the pull request never touched.
def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as repo:
    git(repo, "init", "-q", "-b", "base")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    open(os.path.join(repo, "seed.txt"), "w").write("seed\n")
    # Present on the base, so a later move reads as a deletion from it. Given a body, so
    # git's similarity detection actually fires — with a one-line file it falls back to
    # delete+add and the rename case is never exercised.
    os.makedirs(os.path.join(repo, "datasets", "sfdmu"), exist_ok=True)
    open(os.path.join(repo, "datasets", "sfdmu", "export.json"), "w").write(
        "\n".join(f'{{"object": "Obj{i}", "operation": "Upsert"}}' for i in range(40)))
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "seed")
    git(repo, "checkout", "-q", "-b", "feature")
    open(os.path.join(repo, "feature-change.md"), "w").write("feature work\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feature work")
    git(repo, "checkout", "-q", "base")
    open(os.path.join(repo, "base_only.txt"), "w").write("landed after divergence\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base moves on")
    git(repo, "checkout", "-q", "feature")

    saved_root = pr_gate.REPO_ROOT
    try:
        pr_gate.REPO_ROOT = repo
        files = pr_gate.changed_files("base")
        check("the feature's own change is selected", "feature-change.md" in files, files)
        check("a commit landed on the base after divergence is excluded",
              "base_only.txt" not in files, files)

        # A rename must report the source too. Git's default rename detection names only
        # the destination, so moving a plan README out of datasets/sfdmu/ would not select
        # the check that notices the plan lost its README.
        git(repo, "mv", "datasets/sfdmu/export.json", "moved-away.json")
        git(repo, "commit", "-qm", "move it out")
        files = pr_gate.changed_files("base")
        check("a rename reports the source path, not only the destination",
              "datasets/sfdmu/export.json" in files, files)
        check("...and the destination", "moved-away.json" in files, files)
        check("moving a file out of a directory still selects that directory's check",
              "plan_readme_consistency" in selected_names(files), selected_names(files))

        # Non-ASCII paths: git quotes and escapes them unless -z is used, and a leading
        # quote matches no prefix.
        odd = os.path.join(repo, "docs")
        os.makedirs(odd, exist_ok=True)
        open(os.path.join(odd, "café.md"), "w").write("x\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "non-ascii")
        files = pr_gate.changed_files("base")
        check("a non-ASCII path arrives unquoted and selects normally",
              any(f.endswith("café.md") for f in files), files)
        check("...and is not wrapped in quotes",
              not any(f.startswith('"') for f in files), files)

        # A wholly new, still-untracked directory. Plain `git status --porcelain` collapses
        # it to the topmost new directory ("brand-new/"), so the leaf file never reaches
        # selection: no .md suffix, no deeper prefix. The gate claims uncommitted work is
        # covered, so the collapse has to be defeated rather than documented.
        os.makedirs(os.path.join(repo, "brand-new", "guide"), exist_ok=True)
        open(os.path.join(repo, "brand-new", "guide", "page.md"), "w").write("# new\n")
        files = pr_gate.changed_files("base")
        check("a file inside a brand-new untracked directory reaches selection by full path",
              "brand-new/guide/page.md" in files, files)
        check("...and the collapsed directory entry is not what selection sees",
              "brand-new/" not in files, files)
        # The same collapse, now proved to change a verdict: this citation is wrong, and
        # doc_build_steps only sees it if the leaf path survives.
        open(os.path.join(repo, "brand-new", "guide", "page.md"), "w").write(
            "See step 99.99 of a flow that does not exist.\n")
        check("the new directory's markdown selects the build-step check",
              "doc_build_steps" in selected_names(pr_gate.changed_files("base")),
              selected_names(pr_gate.changed_files("base")))
    finally:
        pr_gate.REPO_ROOT = saved_root

print("\nEvery file a check reads can select that check")
# The absence hole one level up from a missing check: a check that runs, but not when the
# input it asserts against changes. Five of these shipped at once — a suite asserting that
# scripts/ai/README.md cites its current size while a README edit selected nothing; the
# CumulusCI pin compared against prepare-rlm-org.yml with that workflow untriggered; the
# "do not edit" generated references editable without the drift check; the manifest audit
# resolving paths repo-wide from a three-prefix trigger list; two suites reading skill and
# docs/references inputs outside their triggers. Each was invisible in the same way: the
# check passes, so nothing looks wrong. Enumerating the reads is what makes the sixth one
# fail loudly instead of joining quietly.
#
# Paths a suite names but does not depend on, so an unavoidable static-analysis false
# positive is a written decision rather than a loosened rule.
NOT_INPUTS = {
    "tests/test_pr_gate.py": {
        "datasets/sfdmu": "a path built inside a throwaway repo, not read from this one",
    },
    "tests/test_skill_manifest_audit.py": {
        # .agents/artifacts is gitignored, so it can never appear in a PR diff — nothing
        # there is selectable, which is the very asymmetry this suite exists to pin.
        ".agents/artifacts": "gitignored: cannot appear in a diff, so cannot select anything",
        ".agents/artifacts/integration-staging/pmos-integration.md": "gitignored",
    },
    "tests/test_fix_scratch_identity.py": {
        ".sf/orgs": "runtime org state, gitignored — not a repo input",
    },
    "tests/build_harness/test_tui_runner.py": {
        "orgs/ent.json": "a value in a stubbed load_cci dict, with runner.ROOT pointed at "
                         "tmp_path — never read from this repo",
    },
}


#: Names the suites use for the repository root. A single path segment counts as a read only
#: when it hangs off one of these: os.path.join(REPO, "tui-cci") is the root launcher, while
#: os.path.join(ERD_DIR, "README.md") is not the root README, and treating the two alike
#: reported both erd-count suites as reading a file they never touch.
#: Deliberately excludes a bare `root`, which the harness suites use for a tmp_path fixture
#: they write into — `root / "cumulusci.yml"` there is not this repo's cumulusci.yml.
ROOT_NAMES = {"REPO", "REPO_ROOT", "ROOT", "repo_root"}


def root_anchored(node):
    """Segments of a `REPO / "a" / "b"` chain, or () if it is not rooted at the repo."""
    segs = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not (isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)):
            return ()
        segs.insert(0, node.right.value)
        node = node.left
    return tuple(segs) if isinstance(node, ast.Name) and node.id in ROOT_NAMES else ()


def named_paths(py_file, joins_only=False):
    """Repo-relative paths a source file names, from string constants and os.path.join()."""
    try:
        tree = ast.parse(pathlib.Path(py_file).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    found = set()
    # ast.walk visits the inner nodes of a `REPO / "scripts" / "ai" / "x.py"` chain too, and
    # each one is a valid rooted path — reporting the prefixes as separate reads.
    partial = {id(n.left) for n in ast.walk(tree)
               if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and not joins_only:
            if "/" in node.value and not node.value.startswith(("/", "http")):
                found.add(node.value.strip("/"))
        elif isinstance(node, ast.BinOp):
            # repo_root / "tui-cci" — a single root-level segment carries no slash to
            # recognise it by, so this read stayed invisible: the launcher had no trigger at
            # all and the mutation proving that survived.
            segs = root_anchored(node) if id(node) not in partial else ()
            if segs:
                found.add("/".join(segs))
        elif isinstance(node, ast.Call):
            # os.path.join(REPO, "a", "b") — the segments carry no slash of their own, so
            # the constant branch above cannot see this shape.
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "join" and node.args:
                segs = [a.value for a in node.args[1:]
                        if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                rooted = (isinstance(node.args[0], ast.Name)
                          and node.args[0].id in ROOT_NAMES)
                if len(segs) == len(node.args) - 1 and segs and (len(segs) > 1 or rooted):
                    found.add("/".join(segs))
    # A lone root-level segment counts only when it names a file. `ROOT / "scripts"` is a
    # directory on its way to a longer path, not something a suite reads.
    return {p for p in found
            if "/" in p or os.path.isfile(os.path.join(REPO, p))}


def check_sources(spec):
    """The test suites a check's command executes.

    Suites only, deliberately: running a suite runs everything in it, so every path it names
    is a path it reads. A script invoked with a subcommand (`skill_manifest.py --check`)
    exercises one branch, so its other paths — a report's output file, a table another
    subcommand renders — would be false positives. Those checks get the exact, data-driven
    gates below instead of a static read of the whole file.
    """
    if spec["name"] == "stdlib_offline_suites":
        return list(pr_gate.STDLIB_SUITES)
    if spec["cmd"] is None:
        return []
    sources = []
    for arg in spec["cmd"][1:]:
        if arg.endswith(".py") and arg.startswith("tests/"):
            sources.append(arg)
        elif os.path.isdir(os.path.join(REPO, arg)):
            # A directory argument is ~30 suites plus their conftest.py. Skipping it — the
            # first version of this function did, having only matched names ending in .py —
            # left every nested harness suite outside the guarantee, which is how the root
            # `tui-cci` launcher came to be read by a test that no check selected.
            for root, _dirs, files in os.walk(os.path.join(REPO, arg)):
                sources += [os.path.relpath(os.path.join(root, f), REPO)
                            for f in files if f.endswith(".py")]
    return sources


def as_change(rel):
    """A directory named as an input stands for a change underneath it."""
    return rel + "/probe" if os.path.isdir(os.path.join(REPO, rel)) else rel


SELF = "tests/test_pr_gate.py"
unselected_reads, inspected = [], 0
for spec in pr_gate.CHECKS:
    for src in check_sources(spec):
        declared = NOT_INPUTS.get(src, {})
        # This suite is *about* selection, so nearly every path it names is a fixture — an
        # expected trigger, a probe, content written into a throwaway repo. Enumerating those
        # produced a declaration list that grew with every assertion added, which is the drift
        # this gate is supposed to prevent, not cause. Every real read here goes through
        # os.path.join(REPO, …), so that shape is the enumeration, and the check below refuses
        # a read written any other way.
        for rel in sorted(named_paths(os.path.join(REPO, src), joins_only=(src == SELF))):
            inspected += 1
            if rel in declared or not os.path.exists(os.path.join(REPO, rel)):
                continue
            if not pr_gate.selects(spec, [as_change(rel)]):
                unselected_reads.append(f"{spec['name']} reads {rel} ({src}) but is not "
                                        f"selected by it")
check("no suite reads a file that cannot select it", not unselected_reads,
      "; ".join(unselected_reads[:8]))
check("the enumeration actually inspected something", inspected > 20, inspected)
# Coverage of the enumeration itself, which the failure above cannot assert: a shape it stops
# recognising silently narrows the guarantee instead of failing. Both shapes below were blind
# spots that let a real missing trigger through — the nested suites reached only via a
# directory argument, and the root launcher named as a single rooted segment.
enumerated = {s for spec in pr_gate.CHECKS for s in check_sources(spec)}
check("the enumeration reaches suites named only by a directory argument",
      "tests/build_harness/test_tui_launcher.py" in enumerated)
check("a single root-level segment is recognised as a read",
      "tui-cci" in named_paths(os.path.join(REPO, "tests/build_harness/test_tui_launcher.py")))
# The two rooted single-segment shapes, told apart: a root *file* is a read, a root directory
# is the start of a longer path. Asserted on a synthetic source because no suite currently
# writes the directory form, so the distinction is otherwise unobservable.
shapes = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
shapes.write('a = os.path.join(REPO, "tui-cci")\nb = os.path.join(REPO, "scripts")\n')
shapes.close()
try:
    shape_reads = named_paths(shapes.name)
    check("a rooted root-file segment counts as a read", "tui-cci" in shape_reads)
    check("a rooted root-directory segment does not", "scripts" not in shape_reads, shape_reads)
finally:
    os.unlink(shapes.name)

# The convention the joins_only narrowing above depends on: a read written as
# open("docs/x.md") in this file would be invisible to the enumeration, so it is refused
# outright rather than left as a quiet exemption.
self_src = "\n".join(
    ln for ln in pathlib.Path(os.path.join(REPO, SELF)).read_text(
        encoding="utf-8").splitlines()
    if not ln.lstrip().startswith("#"))  # the comment above names the shape it forbids
bare_reads = re.findall(r'(?:open|read_text|Path)\(\s*"[^"]*/[^"]*"', self_src)
check("this suite reads repo files only through os.path.join(REPO, …)",
      not bare_reads, bare_reads)

# agent_tooling asserts these files exist, so deleting one must select it. Read back out of
# the script for the same reason as the manifest roots below: a hand-kept copy drifts.
tooling_src = pathlib.Path(
    os.path.join(REPO, "scripts", "ai", "analyze_agent_tooling.py")).read_text()
required = []
for const in ("REQUIRED_FILES", "GENERATED_CCI_REFERENCE_FILES", "BASELINE_EXTRA_FILES"):
    block = re.search(rf"^{const} = \[(.*?)\]", tooling_src, re.S | re.M)
    check(f"analyze_agent_tooling.py still declares {const}", block is not None)
    required += re.findall(r'"([^"]+)"', block.group(1) if block else "")
tooling_check = next(c for c in pr_gate.CHECKS if c["name"] == "agent_tooling")
check("the required-file list is non-trivial", len(required) > 8, len(required))
missed_required = [r for r in required if not pr_gate.selects(tooling_check, [r])]
check("every file agent_tooling asserts the presence of can select it",
      not missed_required, missed_required)

# The manifest audit resolves paths anywhere under its own declared roots, so the trigger
# list is read back out of the script rather than kept in step by hand.
manifest_src = pathlib.Path(os.path.join(REPO, "scripts", "ai", "skill_manifest.py")).read_text()
roots = re.search(r"_PATH_ROOTS = \((.*?)\)", manifest_src, re.S)
root_files = re.search(r"_ROOT_FILES = \((.*?)\)", manifest_src, re.S)
check("skill_manifest.py still declares the roots it audits",
      roots is not None and root_files is not None)
audited = [v for v in re.findall(r'"([^"]+)"', (roots.group(1) if roots else "")
                                 + (root_files.group(1) if root_files else ""))]
check("the audited root list is non-trivial", len(audited) > 15, len(audited))
manifest_check = next(c for c in pr_gate.CHECKS if c["name"] == "skill_manifest")
missed_roots = [r for r in audited
                if not pr_gate.selects(manifest_check, [r.rstrip("/") + "/probe.md"
                                                        if r.endswith("/") else r])]
check("every root the manifest audit resolves can select the manifest check",
      not missed_roots, missed_roots)

print("\nThe CCI reference drift check watches only what the generator writes")
src = open(os.path.join(REPO, "scripts", "ai", "pr_gate.py")).read()
check("the drift scope names the three generated files",
      all(n in src for n in ("tasks-reference.md", "flows-reference.md",
                             "feature-flags.md")))
# Scoped to the function, not the file: docs/references/ is a legitimate trigger elsewhere
# (a suite validates a shipped example under it), so a whole-file search would conflate the
# two and pass or fail for the wrong reason.
drift_body = src.split("def run_cci_reference_drift")[1].split("\ndef ")[0]
drift_code = "\n".join(ln for ln in drift_body.splitlines()
                       if not ln.lstrip().startswith("#"))
check("the drift scope no longer includes hand-authored docs/references/",
      "docs/references/" not in drift_code,
      "generate_cci_reference.py writes only to .cursor/skills/cci-orchestration/")
# This check adjudicates hand edits to files that carry a "do not edit" banner, so each of
# them has to be able to select it. Not reachable by the read-enumeration above: the scope
# lives inside a cmd=None runtime branch, which is exactly where an ungated input hides.
drift_check = next(c for c in pr_gate.CHECKS if c["name"] == "cci_reference_drift")
drift_scope = [f".cursor/skills/cci-orchestration/{n}"
               for n in re.findall(r'"([^"]+\.md)"', drift_code)]
check("the drift scope was parsed out of the function", len(drift_scope) == 3, drift_scope)
unselecting = [g for g in drift_scope if not pr_gate.selects(drift_check, [g])]
check("every generated file the drift check judges can select it", not unselecting,
      unselecting)

print("\nA dependency-blocked advisory check does not fail the gate")
listing = changed_list("zz_probe_path/thing.txt")
pr_gate.CHECKS.append(dict(name="zz_probe_advisory", cmd=["python", "-c", "pass"],
                           triggers=["zz_probe_path/"], deps=["pytest"], gating=False,
                           note="probe"))
saved = dict(pr_gate.DEPS)
try:
    pr_gate.DEPS["pytest"] = "a_module_that_does_not_exist_anywhere"
    code, out = main_with(["--changed-files-from", listing])
    check("an advisory check blocked on a dependency does not fail the gate", code == 0, code)
    check("it is labelled ADVISORY-DEP rather than passed over", "ADVISORY-DEP" in out)
finally:
    pr_gate.DEPS.clear()
    pr_gate.DEPS.update(saved)
    pr_gate.CHECKS.pop()
    os.unlink(listing)

print("\nA check with no command and no resolve() branch is a tool error, not a verdict")
exit_code = None
try:
    pr_gate.resolve(dict(name="zz_probe_nocmd", cmd=None, triggers=[], deps=[],
                         gating=True))
except SystemExit as exc:
    exit_code = exc.code
check("an unresolvable check exits 2, not a traceback or a gating failure",
      exit_code == 2, exit_code)
for name in ("cci_reference_drift", "stdlib_offline_suites", "yaml_offline_suites"):
    spec = next(c for c in pr_gate.CHECKS if c["name"] == name)
    check(f"{name} resolves to a runnable callable", callable(pr_gate.resolve(spec)))

print("\nCommand-line contract")
code, out = run_gate("--list")
check("--list exits 0", code == 0, code)
check("--list names every check", all(n in out for n in names))
code, out = run_gate("--base", "HEAD", "--all")
check("two selectors at once is a usage error (exit 2, never 1)", code == 2, code)
code, out = run_gate()
check("no selector is a usage error", code == 2, code)
code, out = run_gate("--requirements", "--all")
check("--requirements emits the pinned CumulusCI spec",
      "cumulusci==" in out, out.strip())
check("--requirements emits nothing unpinned for cumulusci",
      not re.search(r"^cumulusci$", out, re.M), out.strip())
# Installing exactly what --requirements prints has to leave the dependency importable.
# CumulusCI needs pkg_resources at import time, which a 3.12+ venv lacks until setuptools is
# installed — so omitting it here hands the caller a MISSING-DEP for a package it just
# installed, and pip's install order means the pin must come first.
req_lines = [ln for ln in out.splitlines() if ln.strip()]
check("--requirements pairs the CumulusCI pin with setuptools",
      any(ln.startswith("setuptools") for ln in req_lines), req_lines)
check("...and emits setuptools before CumulusCI, the order pip installs in",
      next(i for i, ln in enumerate(req_lines) if ln.startswith("setuptools"))
      < next(i for i, ln in enumerate(req_lines) if ln.startswith("cumulusci")),
      req_lines)
code, out_nocci = run_gate("--requirements", "--changed-files-from", os.devnull)
check("a selection without CumulusCI does not drag setuptools in",
      "setuptools" not in out_nocci, out_nocci.strip())

# pyproject.toml carries [tool.pytest.ini_options], so it decides what the two pytest-invoking
# checks collect. If it selected nothing, a change that broke collection would merge without
# either suite running once.
pytest_driven = {c["name"] for c in pr_gate.CHECKS
                 if c["cmd"] and "pytest" in " ".join(c["cmd"])}
selected_by_pyproject = set(selected_names(["pyproject.toml"]))
check("pyproject.toml selects every pytest-driven check",
      pytest_driven and pytest_driven <= selected_by_pyproject,
      sorted(pytest_driven - selected_by_pyproject))
# This suite runs the gate, so its probe path must not select a check that runs this suite
# (infinite nesting) or one whose dependency CI would not have installed for the outer
# selection (a MISSING-DEP failure that says nothing about the gate).
# erd-data.json selects exactly one check, which needs no package and does not run this
# suite. It replaced .claude/skill-manifest.yml, which stopped qualifying once a manifest
# edit started (correctly) selecting the PyYAML-dependent suite that audits the manifest.
PROBE_PATH = "docs/erds/erd-data.json"
probe_selection = [c for c in pr_gate.CHECKS if pr_gate.selects(c, [PROBE_PATH])]
nesting_fixture = changed_list("tests/test_branch_scope.py")
try:
    main_with(["--changed-files-from", nesting_fixture])
    refused = False
except AssertionError:
    refused = True
finally:
    os.unlink(nesting_fixture)
check("a fixture that would nest the gate inside itself is refused, not run", refused,
      "pr_gate_suite triggers on tests/, so running it on a tests/ fixture recurses")
check("the probe path selects at least one check", probe_selection != [])
check("the probe path selects no check that re-runs this suite",
      all("tests/test_pr_gate.py" not in (c["cmd"] or []) for c in probe_selection)
      # cmd=None checks expand at runtime, so the command list alone is not enough: a
      # bulk-suite check would satisfy the test above while still re-running this file.
      and "tests/test_pr_gate.py" not in pr_gate.STDLIB_SUITES
      and not any(c["name"] == "stdlib_offline_suites" for c in probe_selection),
      [c["name"] for c in probe_selection])
check("the probe path needs no installed dependency",
      all(not c["deps"] for c in probe_selection),
      {c["name"]: c["deps"] for c in probe_selection})

with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
    fh.write(PROBE_PATH + "\n")
    changed = fh.name
try:
    code, out = run_gate("--changed-files-from", changed)
    check("a changed-file list runs the checks it selects and exits 0", code == 0, out[-400:])
    check("the report prints a line for every check",
          all(re.search(rf"\] {re.escape(n)}\b", out) for n in names),
          [n for n in names if not re.search(rf"\] {re.escape(n)}\b", out)])
    check("skipped checks say why they were skipped", "nothing it covers changed" in out)
    # Every check lands in exactly one bucket and the buckets sum to the total, so a reader
    # reconciling them never finds one unaccounted for.
    buckets = re.search(r"(\d+) checks: (\d+) executed, (\d+) skipped, "
                        r"(\d+) blocked on a missing dependency, (\d+) failed", out)
    check("the summary reports every bucket separately", buckets is not None, out[-300:])
    check("the buckets account for every check",
          buckets and int(buckets.group(1)) == sum(int(buckets.group(i))
                                                  for i in (2, 3, 4)),
          buckets.groups() if buckets else None)
finally:
    os.unlink(changed)

# A dependency that is present on disk but cannot be imported must read as absent. This is
# not hypothetical: cumulusci 4.8.1 imports `fs`, which imports `pkg_resources`, which a
# Python 3.12+ venv lacks until setuptools is installed. find_spec called that install fine
# and the breakage surfaced as two unrelated-looking suite failures instead of one blocked
# dependency, so the probe has to be a real import.
with tempfile.TemporaryDirectory() as probe_dir:
    name = "zz_present_but_unimportable"
    pathlib.Path(probe_dir, name + ".py").write_text(
        "raise ModuleNotFoundError(\"No module named 'pretend_transitive_dep'\")\n")
    prior_path, prior_cache = sys.path[:], dict(pr_gate._IMPORTABLE)
    prior_env = os.environ.get("PYTHONPATH")
    sys.path.insert(0, probe_dir)
    os.environ["PYTHONPATH"] = probe_dir + os.pathsep + (prior_env or "")
    try:
        pr_gate._IMPORTABLE.clear()
        check("find_spec alone would call the broken dependency present",
              importlib.util.find_spec(name) is not None)
        check("a present-but-unimportable dependency reads as absent",
              pr_gate.have_module(name) is False)
        pr_gate._IMPORTABLE.clear()
        check("a genuinely importable dependency still reads as present",
              pr_gate.have_module("json") is True)
    finally:
        sys.path[:] = prior_path
        if prior_env is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = prior_env
        pr_gate._IMPORTABLE.clear()
        pr_gate._IMPORTABLE.update(prior_cache)

check("cumulusci is probed at the depth a task actually needs",
      pr_gate.DEPS["cumulusci"] == "cumulusci.core.tasks", pr_gate.DEPS["cumulusci"])

# A failed `git status` returns empty stdout, which reads exactly like a clean tree. In
# changed_files that would silently drop every uncommitted path from the selection; in the
# CCI-reference check, where the status IS the verdict, it would report "no drift" and pass.
# Both must fail loudly instead, so both return codes are asserted here.
source = pathlib.Path(pr_gate.__file__).read_text()
status_calls = source.count('"git", "status", "--porcelain"')
check("both git status call sites are still present", status_calls == 2, status_calls)
check("changed_files dies when git status fails",
      re.search(r'"git", "status", "--porcelain", "--untracked-files=all", "-z"'
                r'.*?if st\.returncode != 0:\s*\n\s*die\(', source, re.S) is not None)
check("the drift check fails when git status fails",
      re.search(r'"git", "status", "--porcelain", "--", \*generated.*?'
                r'if diff\.returncode != 0:\s*\n\s*return 1,', source, re.S) is not None)

broken_git = tempfile.mkdtemp()
try:
    # An unreadable repo: `git status` cannot succeed, so the gate must be a tool error
    # (exit 2) rather than a verdict computed from an empty result.
    prior_root = pr_gate.REPO_ROOT
    pr_gate.REPO_ROOT = broken_git
    try:
        code, out = main_with(["--base", "origin/264"])
        check("an unusable repo is a tool error, not a clean selection",
              code == 2, f"exit {code}: {out[-200:]}")
    finally:
        pr_gate.REPO_ROOT = prior_root
finally:
    os.rmdir(broken_git)

code, out = run_gate("--changed-files-from", os.devnull)
check("an empty change set is a clean pass, not an error", code == 0, out[-300:])
code, out = run_gate("--changed-files-from", "/no/such/file")
check("an unreadable change list is a tool error (exit 2)", code == 2, code)

print("\n" + "=" * 100)
if FAILED:
    print(f"{len(FAILED)} FAILED: {', '.join(FAILED)}")
    sys.exit(1)
# Pinned so a check that stops running is a failure rather than a smaller number nobody reads.
EXPECTED = 126
if PASSED != EXPECTED:
    print(f"{PASSED} checks passed but {EXPECTED} were expected — update EXPECTED "
          "deliberately when adding or removing a check")
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")
