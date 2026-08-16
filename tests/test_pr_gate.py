#!/usr/bin/env python3
"""Offline tests for scripts/ai/pr_gate.py — the PR gate's check selector and reporter.

The gate exists because a skipped check reads like a passing one, so these tests care most
about the ways it could go quiet: a suite no check runs, a missing dependency reported as a
skip, an advisory check silently promoted or demoted, a trigger list that selects nothing.

Run offline: python tests/test_pr_gate.py
"""

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
sel = selected_names(["robot/rlm-base/some.robot"])
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
    # Advisory output is tailed; a gating failure's is not, so it stays diagnosable.
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
    finally:
        pr_gate.REPO_ROOT = saved_root

print("\nThe CCI reference drift check watches only what the generator writes")
src = open(os.path.join(REPO, "scripts", "ai", "pr_gate.py")).read()
check("the drift scope names the three generated files",
      all(n in src for n in ("tasks-reference.md", "flows-reference.md",
                             "feature-flags.md")))
check("the drift scope no longer includes hand-authored docs/references/",
      '"docs/references/"' not in src,
      "generate_cci_reference.py writes only to .cursor/skills/cci-orchestration/")

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
# This suite runs the gate, so its probe path must not select a check that runs this suite
# (infinite nesting) or one whose dependency CI would not have installed for the outer
# selection (a MISSING-DEP failure that says nothing about the gate).
# erd-data.json selects exactly one check, which needs no package and does not run this
# suite. It replaced .claude/skill-manifest.yml, which stopped qualifying once a manifest
# edit started (correctly) selecting the PyYAML-dependent suite that audits the manifest.
PROBE_PATH = "docs/erds/erd-data.json"
probe_selection = [c for c in pr_gate.CHECKS if pr_gate.selects(c, [PROBE_PATH])]
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
      re.search(r'"git", "status", "--porcelain", "-z".*?if st\.returncode != 0:\s*\n\s*die\(',
                source, re.S) is not None)
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
EXPECTED = 99
if PASSED != EXPECTED:
    print(f"{PASSED} checks passed but {EXPECTED} were expected — update EXPECTED "
          "deliberately when adding or removing a check")
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")
