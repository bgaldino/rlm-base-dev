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

print("\nThe workflow that runs the gate cannot be quietly defanged")
# The gate is only as real as the job that invokes it, and every way of disabling that job
# leaves a green PR behind — which is the exact failure #264-58 exists to fix, one level up.
# So the workflow is asserted here rather than trusted to review: a `paths:` filter added in
# good faith would skip the job, and a skipped job reports success.
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
                mapping[key] = rest
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

    # An invocation that is not `--requirements`, because that one resolves dependencies and
    # its exit code is not a verdict. Two rounds of this rule were vacuous: first it tested for
    # the bare string, which survived deleting the gate step because the name remained on the
    # dependency line; then it excluded `--requirements` but still scanned every line, so
    # deleting the step and leaving `# TODO: re-enable scripts/ai/pr_gate.py` also passed. It
    # now asks the only question that matters — does the job *execute* it?
    # Being inside `run:` is not the same as being run. Two shapes clear that bar and are still
    # inert: `echo python …` prints the command, and `… || true` runs it and throws the verdict
    # away. Both were asked for by review and both survived the sweep, so the question a rule may
    # ask is narrower than "does the name appear in an executed line" — it is "is this the command,
    # and does its exit status still reach the job".
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
            elif char in ";|&":
                out, cur, i = out + [cur, char], "", i + 1
            else:
                cur, i = cur + char, i + 1
        return out + [cur]

    def parts(ln):
        """Each shell segment of a line, paired with the text that follows it."""
        pieces = tokens(ln)
        return [(pieces[i], "".join(pieces[i + 1:])) for i in range(0, len(pieces), 2)]

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
                    and not MASKED.match(tail.strip()))

    def executes(ln, script, args_required=()):
        return any(runs_segment(seg, tail, script, args_required) for seg, tail in parts(ln))

    def invocations(script, args_required=()):
        return [ln for ln in run_contents(wf) if executes(ln, script, args_required)]

    # `exit`/`return` do not mask a status, they end the shell: every command after one, on that
    # line or any later line of the step, is unreachable.
    TERMINATOR = ("exit", "return")

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
        pieces = tokens(ln)
        for i in range(0, len(pieces), 2):
            if opens(pieces[i]) and opens(pieces[i])[0] in TERMINATOR:
                return False
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

    def flow_list(scalar):
        return [w.strip().strip("'\"") for w in str(scalar).strip("[]").split(",") if w.strip()]

    # `paths:` was the filter this workflow exists to avoid, but it is not the only one that makes
    # the job skip — and a skipped job reports success. Read as keys rather than matched as text:
    # naming five forbidden filters left every other one permitted, and the quoting the rule had to
    # tolerate (`'paths':`) was a second spelling to remember. A whitelist needs neither.
    on = doc.get("on") or {}
    check("the workflow triggers on pull_request at all", "pull_request" in on, list(on))
    pr_trigger = on.get("pull_request")
    # `types` is allowed only as a superset of the default three, which cannot skip a PR that the
    # default would have run. Rejecting it outright made the rule fire on a correct edit
    # (`types: [opened, synchronize, reopened, ready_for_review]`), and a rule that fires on correct
    # code is a rule someone deletes.
    DEFAULT_TYPES = {"opened", "synchronize", "reopened"}
    filters = sorted(set(pr_trigger or {}) - {"types"})
    check("the pull_request trigger carries no filter that could skip the job and read as a pass",
          not filters, filters)
    # Unconditional, like every other rule here: writing this as `if "types" in trigger:` would make
    # the suite's own check count depend on the workflow, so adding a `types:` filter would trip the
    # count invariant — whose message asks the reader to update EXPECTED, i.e. to wave the filter
    # through. Absent `types`, the effective set *is* the default, so the same assertion holds.
    types = set(flow_list((pr_trigger or {}).get("types", ""))) or DEFAULT_TYPES
    check("the trigger's event types are a superset of the default three, so no PR is skipped",
          types >= DEFAULT_TYPES, types)

    # The job that runs the gate, found by what its steps do rather than by position. The rule this
    # replaces read "everything between `jobs:` and the first `- name:`" as a stand-in for the job,
    # so `if: false` appended after the steps list was outside the window, and a decoy job whose
    # first step preceded the real job's collapsed the window to nothing.
    def step_runs(step, script, exclude=()):
        return any(executes(ln, script) and not any(x in ln for x in exclude)
                   for ln in run_contents("        run: |\n" + str(step.get("run", ""))))

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

    def raw_shell_of(step):
        return [ln for ln
                in run_contents("        run: |\n" + str(step.get("run", ""))) if ln.strip()]

    def shell_of(step):
        return [ln.strip() for ln in raw_shell_of(step)]

    def escapes_early(step):
        """Commands at the step's own indentation that end the shell. Reachability is a property of
        the whole step, not of one line: an `exit 0` on a line of its own leaves every per-line
        assertion about the checker below it — invoked, exit code captured, fork branch guarded,
        `--no-fetch` supplied — satisfied and unreached. Nesting is what makes an exit conditional,
        so the real `exit 2` inside the retry loop's `if` and the single-line `if …; then exit …; fi`
        (which opens with `if`) are both accepted; one at the top level is not.
        """
        raw = raw_shell_of(step)
        base = min((len(ln) - len(ln.lstrip()) for ln in raw), default=0)
        return [ln.strip() for ln in raw
                if len(ln) - len(ln.lstrip()) == base
                and opens(ln.strip()) and opens(ln.strip())[0] in TERMINATOR]

    # Block keywords are not commands: `then exit 2` runs `exit`, `{ echo x` runs `echo`.
    KEYWORDS = ("then", "else", "elif", "do", "done", "fi", "esac", "!", "{", "}", "(", ")")
    # The two steps' whole vocabulary: `set`, a conditional, `echo`, `exit`, `sleep`, `git fetch`,
    # the two scripts, and four variables. Small enough to whitelist, which is why this is possible
    # here and would not be for an arbitrary step.
    HARMLESS = ("echo", "printf", "exit", "return", "sleep", ":", "true")
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
        if words[0] in HARMLESS:
            return True
        if words[0] == "set":
            return " ".join(words) in ALLOWED_SET
        if words[0] in ("if", "elif", "while", "until"):
            return words[1:2] and words[1] in ("[", "test", ":")
        if words[0] == "git":
            return words[1:2] == ["fetch"]
        if words[0] == "python":
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
                if ">" in ln or "<" in ln or re.search(r"\$\((?!\()", ln) or "`" in ln]

    def pure_echo(ln):
        """One segment, and that segment is an echo. `startswith("echo ")` was a *prefix* test, so
        `echo "disabled" && exit 0` and `echo "shim"; python() { return 0; }` both satisfied it while
        making the gate that follows either unreachable or a no-op."""
        segs = parts(ln)
        return len(segs) == 1 and segs[0][0].split()[:1] == ["echo"]

    found_gate = steps_named(gate_job, "scripts/ai/pr_gate.py",
                             exclude=("--requirements", "--list", "--help"))
    check("exactly one step runs the gate for a verdict", len(found_gate) == 1, len(found_gate))
    if len(found_gate) == 1:
        gate_step = found_gate[0]
        cmds = shell_of(gate_step)
        # Keys, exactly: `if:`/`continue-on-error:` were the two a regex looked for, but `shell:`
        # ("cat {0}" makes the runner print the script instead of executing it) and `env:`
        # (re-pointing SEL at an empty selection) neutralise the step just as completely, and no
        # enumeration of bad keys would have named them all.
        check("the gate step carries only a name and a script, so nothing can skip, tolerate or "
              "reinterpret it", sorted(gate_step) == ["name", "run"], sorted(gate_step))
        check("the gate step aborts on the first error", cmds[:1] == ["set -euo pipefail"], cmds)
        # Property, not spelling: exactly one command must *execute* the gate with its status still
        # reaching the job. Pinning the last line to one literal rejected two correct edits — a
        # re-raising handler (`|| { echo "::error::…"; exit 1; }`, which this suite separately
        # asserts is not masking) and a trailing `echo "::notice::"`, unreachable under `set -e`.
        runs_gate = [ln for ln in cmds if foreground(ln, "scripts/ai/pr_gate.py")]
        check("one command executes the gate with its verdict reaching the job",
              len(runs_gate) == 1, cmds)
        check("the gate receives the selection this workflow computed, not a literal that would "
              "make an empty diff",
              len(runs_gate) == 1
              and invoking_segment(runs_gate[0], "scripts/ai/pr_gate.py") == GATE_CMD,
              [invoking_segment(ln, "scripts/ai/pr_gate.py") for ln in runs_gate])
        check("every other command is a bare echo, which cannot swallow the verdict",
              all(pure_echo(ln) for ln in cmds[1:] if ln not in runs_gate), cmds)
        check("nothing in the gate step ends the shell before the gate runs",
              not escapes_early(gate_step), escapes_early(gate_step))
        check("every segment of the gate step runs a command the step is meant to run, so nothing "
              "beside the invocation can redefine what `python` means",
              not foreign_commands(gate_step), foreign_commands(gate_step))
        check("the gate step neither redirects nor substitutes, so it cannot rewrite the script it "
              "is about to run", not rewrites(gate_step), rewrites(gate_step))
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
    crossings = [ln.strip() for ln in run_contents(wf)
                 if "GITHUB_ENV" in ln or "GITHUB_PATH" in ln]
    check("the only value a step hands another is the selection, so nothing can re-point PATH or "
          "the interpreter out of band",
          crossings and all(ln in ALLOWED_SEL for ln in crossings), crossings)
    for label, mutant in (("a PATH re-pointed for later steps",
                           'echo "PATH=/tmp/shim:$PATH" >> "$GITHUB_ENV"'),
                          ("a directory prepended to PATH",
                           'echo "/tmp/shim" >> "$GITHUB_PATH"')):
        check(f"that rule rejects {label}", mutant not in ALLOWED_SEL)
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
        check("the inputs that decide its comparison are the real event values",
              (scope_step.get("env") or {}) == SCOPE_ENV, scope_step.get("env"))
        seq = shell_of(scope_step)
        called = [i for i, ln in enumerate(seq)
                  if foreground(ln, "scripts/ai/check_branch_scope.py")]
        check("the checker is invoked as a bare command", called, seq)
        # `--no-fetch` may ride on the invocation instead of the argument list, which is one of the
        # correct edits this suite promises to accept; nothing else may.
        check("the checker receives the argument list this step built, not literal refs",
              all(invoking_segment(seq[i], "scripts/ai/check_branch_scope.py")
                  in (SCOPE_CMD, SCOPE_CMD + " --no-fetch") for i in called),
              [invoking_segment(seq[i], "scripts/ai/check_branch_scope.py") for i in called])
        check("its real exit code is what the retry loop reads",
              all(seq[i + 1:i + 2] == ["code=$?"] for i in called), seq)
        # The fork branch is the one without --pr, so a condition that is always true sends every
        # PR down it and loses STACKED permanently while `set -- --pr` survives, unreachable, in the
        # else. Textual rules could see the flag but not which branch runs.
        check("the fork branch is taken only for a genuine cross-repository PR",
              [ln for ln in seq if ln == 'if [ "${CROSS}" = "true" ]; then'], seq)
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
        check("every segment of the branch-scope step runs a command the step is meant to run",
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

    STEP_MUTANTS = {
        "a conditional gate step": ("        run: |", "        if: false\n        run: |"),
        "a gate step that tolerates failure":
            ("        run: |", "        continue-on-error: true\n        run: |"),
        "a quoted key the old regex could not see":
            ("        run: |", '        "continue-on-error": true\n        run: |'),
        "a step whose shell prints the script instead of running it":
            ("        run: |", '        shell: "cat {0}"\n        run: |'),
        "a step env that re-points the selection":
            ("        run: |", '        env:\n          SEL: "--all --dry-run"\n        run: |'),
    }
    for label, (anchor, repl) in STEP_MUTANTS.items():
        mutant, _ = gate_step_of(wf.replace("      - name: Run the gate\n" + anchor,
                                            "      - name: Run the gate\n" + repl, 1))
        check(f"the gate-step key rule rejects {label}",
              mutant is not None and sorted(mutant) != ["name", "run"], sorted(mutant or {}))
    JOB_MUTANTS = {
        "a job that tolerates failure": "    continue-on-error: true",
        "a job that never runs": "    if: false",
        "a job default shell that swallows every step": "    defaults:\n      run:\n"
                                                        '        shell: "cat {0}"',
    }
    # Anchored on the gate job's own header rather than the first `runs-on:` in the file, so these
    # controls keep landing on the job under test if another job is ever added above it.
    GATE_HEADER = "  %s:\n    name: %s" % (gate_job_name, gate_job.get("name"))
    for label, extra in JOB_MUTANTS.items():
        _, job = gate_step_of(wf.replace(GATE_HEADER, GATE_HEADER + "\n" + extra, 1))
        check(f"the job key rule rejects {label}", sorted(set(job) - JOB_KEYS), sorted(job))
    check("the job rule sees a key appended after the steps list, which a positional window missed",
          sorted(set(gate_step_of(wf + "    if: false\n")[1]) - JOB_KEYS) == ["if"])
    check("a decoy job before the real one no longer hides it",
          sorted(set(gate_step_of(
              wf.replace("jobs:\n  gate:", "jobs:\n  noop:\n    runs-on: ubuntu-latest\n"
                         "    steps:\n      - name: nothing\n        run: echo ok\n\n  gate:", 1)
          )[1]) - JOB_KEYS) == [])
    # The parser's refusals are what make every whitelist above honest: a shape it cannot model is
    # a step whose keys are invisible, which would satisfy "only these keys" by having none.
    for bad, why in (("jobs:\n  gate:\n    steps:\n      - { name: x, run: echo hi }\n",
                      "a flow-style step"),
                     ("a: &anchor 1\nb: *anchor\n", "an anchor or alias"),
                     ("a: 1\na: 2\n", "a duplicate key"),
                     ("a:\n\t- 1\n", "a tab")):
        try:
            parse_yaml(bad)
            refused = False
        except YamlUnsupported:
            refused = True
        check(f"the reader refuses {why} rather than reading past it", refused)
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
              invoking_segment(ln, script) not in (GATE_CMD, SCOPE_CMD, SCOPE_CMD + " --no-fetch"),
              invoking_segment(ln, script))
    check("it accepts the gate as written, and a re-raising handler after it",
          invoking_segment('python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 1; }',
                           "scripts/ai/pr_gate.py") == GATE_CMD)
    check("and the checker with --no-fetch moved onto the invocation",
          invoking_segment('python scripts/ai/check_branch_scope.py "$@" --no-fetch',
                           "scripts/ai/check_branch_scope.py") == SCOPE_CMD + " --no-fetch")
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
              'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit 1; }')))
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
    restated = [ln for ln in run_contents(wf)
                if "pip install" in ln
                and "reqs" not in ln
                and not re.search(r"pip install\s+--upgrade\s+pip\s*$", ln)]
    check("every dependency install comes from --requirements rather than being restated",
          not restated, restated)
    check("the gate is asked what to install in the first place",
          [ln for ln in run_contents(wf) if "--requirements" in ln], run_contents(wf))
    for spelling in ('pip install "cumulusci~=4.8.1"', "pip install setuptools<77",
                     "pip install requests"):
        check(f"that rule catches a restated dependency: {spelling}",
              [ln for ln in run_contents(f"        run: |\n          {spelling}\n")
               if "pip install" in ln and "reqs" not in ln
               and not re.search(r"pip install\s+--upgrade\s+pip\s*$", ln)])

    # fetch-depth: 0 is load-bearing, not hygiene: on a shallow clone the merge-base diff has
    # no base to resolve against, so selection would come up empty and the gate would pass by
    # having checked nothing. Read from the step's `with:` rather than matched as a substring —
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
    JOB_USES = {"Checkout repository": "actions/checkout@v6",
                "Set up Python": "actions/setup-python@v6"}
    # `python -m pip` cannot be left open the way `git fetch` can: `pip install ${reqs} evil-shim`
    # installs whatever it is told, so the two install forms are pinned like everything else.
    PIP_FORMS = ("python -m pip install --upgrade pip", "python -m pip install ${reqs}")
    JOB_ASSIGN = ALLOWED_ASSIGN + (
        'reqs="$(python scripts/ai/pr_gate.py --requirements ${SEL})"',)
    # A redirection is how a step writes to the checkout, so its *target* is the rule. The four
    # GitHub-provided files are how steps legitimately pass values on; /dev/null is how `git rev-parse
    # --verify` stays quiet.
    REDIR_TARGETS = ('"$GITHUB_OUTPUT"', '"$GITHUB_ENV"', '"$GITHUB_PATH"', '"$GITHUB_STEP_SUMMARY"',
                     "/dev/null")

    def permitted_job(seg):
        """Wider than `permitted()` — the other two steps resolve a ref and install pins — but still a
        whitelist of forms, not of words."""
        words = [w for w in seg.split() if w != "!"]
        while words and (words[0] in KEYWORDS or words[0] in ("if", "elif", "while", "until")):
            words = words[1:]
        if not words:
            return True
        w0 = words[0]
        if w0 in HARMLESS or w0 in ("[", "test"):
            return True
        if w0 == "set":
            return " ".join(words) in ALLOWED_SET
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", w0):
            return re.sub(r"\s+", "", seg) in [re.sub(r"\s+", "", f) for f in JOB_ASSIGN]
        if w0 == "git":
            return len(words) > 1 and words[1] in ("fetch", "rev-parse")
        if w0 == "python":
            if len(words) > 1 and words[1] in SCRIPTS:
                return True
            return " ".join(w for w in words if not w.startswith(">")) in PIP_FORMS
        return False

    def redirections(step):
        # The target stops at a separator: `>/dev/null; then` redirects to /dev/null, and reading the
        # `;` as part of the path made the workflow fail its own rule.
        return [ln.strip() for ln in shell_of(step)
                for m in re.finditer(r"(?<![0-9<>])>>?\s*([^\s;&|)]+)", ln)
                if m.group(1) not in REDIR_TARGETS]

    job_steps = gate_job.get("steps") or []
    check("the job runs exactly the six steps it is built from, so a seventh cannot arrive without "
          "updating this rule", [s.get("name") for s in job_steps] == JOB_STEPS,
          [s.get("name") for s in job_steps])
    check("and uses only the two pinned actions, neither of which patches the tree",
          {s["name"]: s["uses"] for s in job_steps if "uses" in s} == JOB_USES,
          {s.get("name"): s.get("uses") for s in job_steps if "uses" in s})
    stray = [(s.get("name"), seg.strip()) for s in job_steps if "run" in s
             for ln in shell_of(s) for seg, _ in parts(ln) if not permitted_job(seg)]
    check("every command in every step is one the job exists to run, so no step can rewrite what a "
          "later one executes", not stray, stray[:4])
    redirs = [(s.get("name"), r) for s in job_steps if "run" in s for r in redirections(s)]
    check("and every redirection writes to a GitHub-provided file or /dev/null, never into the "
          "checkout", not redirs, redirs[:4])
    for label, snippet in (("a script overwritten by a redirection",
                            "echo 'import sys; sys.exit(0)' > scripts/ai/pr_gate.py"),
                           ("a script rewritten through a glob, naming nothing",
                            "sed -i.bak 's/^/#/' scripts/ai/pr_g*.py"),
                           ("a stub copied over the directory", "cp /tmp/stub.py scripts/ai/"),
                           ("a shim installed alongside the pins",
                            "python -m pip install ${reqs} evil-shim")):
        step = as_step("set -euo pipefail", snippet)
        check(f"those two rules reject {label}",
              [seg for ln in shell_of(step) for seg, _ in parts(ln) if not permitted_job(seg)]
              or redirections(step), snippet)
    check("and accept the two steps this job needs them for",
          not [seg for s in job_steps if "run" in s and s.get("name") in JOB_STEPS[2:4]
               for ln in shell_of(s) for seg, _ in parts(ln) if not permitted_job(seg)])
    check("a seventh step is visible to the step-list rule",
          [s.get("name") for s in job_steps] + ["Prepare"] != JOB_STEPS)

    # The selection's *input*, not just its spelling. SEL is pinned to `--base ${BASE}` below, and
    # BASE is whatever this step wrote: `echo "ref=HEAD"` left both permitted SEL lines untouched
    # and made the diff `HEAD...HEAD`, so the gate selected nothing and passed.
    ALLOWED_REF = ('echo "ref=" >> "$GITHUB_OUTPUT"',
                   'echo "ref=origin/${BASE_REF}" >> "$GITHUB_OUTPUT"')
    ref_lines = [ln.strip() for ln in run_contents(wf) if "ref=" in ln and "GITHUB_OUTPUT" in ln]
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
    minor = re.search(r'python-version:\s*"(\d+)\.(\d+)"', body)
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
EXPECTED = 295
if PASSED != EXPECTED:
    print(f"{PASSED} checks passed but {EXPECTED} were expected — update EXPECTED "
          "deliberately when adding or removing a check")
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")
