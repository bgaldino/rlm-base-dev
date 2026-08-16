#!/usr/bin/env python3
"""Run the mechanical checks a change actually needs, and report the status of every one.

Nothing mechanical ran on a pull request here unless it touched agent tooling: the only
`pull_request` workflow was path-filtered to `AGENTS.md`, `.cursor/**`, `.agents/**` and
`scripts/ai/**`. A PR changing `tasks/`, `tests/`, `datasets/`, `templates/`,
`force-app/`, `unpackaged/`, `robot/` or `cumulusci.yml` got **no** automated check —
not the offline suites, not the dataset validators, not the doc-step or ERD-count gates.
Every one of those was enforced only by an agent reading a checklist, which is the
enforcement that failed in #264-27, #264-55 and #264-56: all three found by hand, late.

**Why a driver instead of `paths:` filters and `if:` conditions in the workflow.** A path
filter makes the job *skip*, and a skipped job is not a failed job — it cannot serve as a
required status check, and in a PR summary it reads exactly like a pass. Same for a skipped
step. So selection happens here, in one job that always runs, and every check is reported
with an explicit status. A check that did not run says so on its own line.

Three statuses that are easy to conflate and must not be:

* `SKIPPED` — not selected, because nothing the check covers changed. Benign, but printed.
* `MISSING-DEP` — selected, but its interpreter or a package is absent. **This fails the
  gate.** Treating it as a skip is how a broken install silently turns a gate green; the
  same absence hole that let a documentation check pass by finding nothing to check.
* `ADVISORY` — runs, reports, and never fails the gate. Exactly one check is advisory:
  `validate_sfdmu_v5_datasets.py` exits non-zero on a clean tree today, on two known
  false positives (pack 123). A check that always fails gets ignored, and an ignored
  check is worse than an absent one — so it is labelled, with the reason, until 123 lands.

Exit codes follow `check_branch_scope.py`, so a tool error is never read as a verdict:
0 = every selected gating check passed · 1 = at least one failed · 2 = usage or tool error.

Usage:
    python scripts/ai/pr_gate.py --base origin/264        # select from the diff vs a ref
    python scripts/ai/pr_gate.py --changed-files-from f   # one path per line (tests, CI)
    python scripts/ai/pr_gate.py --all                    # ignore selection, run everything
    python scripts/ai/pr_gate.py --list                   # print the matrix, run nothing
    python scripts/ai/pr_gate.py --requirements --base X  # extra pip deps the selection needs
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Package -> the import that proves it is USABLE, not merely present. `cumulusci` maps to
# `cumulusci.core.tasks` because the top-level package imports on a install that cannot run
# a task: `cumulusci.core.tasks` -> `cumulusci.core.config` -> `fs` -> `pkg_resources`, which
# Python 3.12+ venvs do not ship unless setuptools is installed (`prepare-rlm-org.yml` pins
# `setuptools>=75.4,<77` ahead of CumulusCI for exactly this reason). Probed with a real
# import rather than `find_spec`, which answers "is there a file to import" and so calls such
# an install fine — the failure then surfaces as two unrelated-looking suite failures instead
# of one blocked dependency. `analyze_agent_tooling.py` also needs Python 3.10+
# (`sys.stdlib_module_names`); on 3.9 it reported `json, os, re` as non-stdlib, so the version
# is checked as a dependency rather than assumed.
DEPS = {
    "PyYAML": "yaml",
    "cumulusci": "cumulusci.core.tasks",
    "pytest": "pytest",
    "textual": "textual",
    "requests": "requests",
}

# What `--requirements` emits, so CI installs only what the selection needs. CumulusCI is
# pinned to the version `prepare-rlm-org.yml` installs: two workflows resolving different
# CumulusCI versions would let a flow-citation check pass here and fail there.
PINS = {"cumulusci": "cumulusci==4.8.1"}

# Lines of an advisory check's output to keep — the FIRST lines, not the last: the SFDMU
# validator puts its summary and its Critical counts at the top and then lists every passing
# plan, so tailing kept a wall of passes and elided the only thing the reader needs.
# Gating failures are never truncated.
ADVISORY_HEAD = 20

# Per-check wall-clock ceiling. Generous: the slowest real check is ~8s.
CHECK_TIMEOUT = 900

# name, command, path prefixes that select it, extra pip deps, gating, note.
# `suffixes` is for a check that reads the whole repo rather than a subtree: prefixes cannot
# express "every .md file", and pretending otherwise is how a check ends up unable to select
# on the very files it audits.
CHECKS = [
    dict(
        name="agent_tooling",
        cmd=["python", "scripts/ai/analyze_agent_tooling.py", "check"],
        triggers=["AGENTS.md", "REVIEW.md", ".github/copilot-instructions.md",
                  ".claude/skill-manifest.yml", ".cursor/", ".agents/", "scripts/ai/"],
        deps=[], min_python=(3, 10), gating=True,
    ),
    dict(
        name="skill_manifest",
        cmd=["python", "scripts/ai/skill_manifest.py", "--check"],
        triggers=[".cursor/skills/", ".claude/skill-manifest.yml",
                  "scripts/ai/skill_manifest.py"],
        deps=[], gating=True,
    ),
    dict(
        name="plan_readme_consistency",
        cmd=["python", "scripts/ai/check_plan_readme_consistency.py"],
        triggers=["datasets/sfdmu/"],
        deps=[], gating=True,
    ),
    dict(
        name="erd_doc_counts",
        cmd=["python", "tests/test_erd_doc_counts.py"],
        # Exactly the files the suite reads (its TRIPLE_SITES, docs/erds/*, domains/*.md).
        # doc-consistency/ was here and the suite never reads it — over-selection is matrix
        # drift in a matrix whose job is preventing drift.
        triggers=["docs/erds/", ".cursor/skills/revenue-cloud-data-model/",
                  ".cursor/skills/schema-validation/",
                  "scripts/ai/README.md", "tests/test_erd_doc_counts.py"],
        deps=[], gating=True,
    ),
    dict(
        name="branch_scope",
        cmd=["python", "tests/test_branch_scope.py"],
        triggers=["scripts/ai/check_branch_scope.py", "tests/test_branch_scope.py"],
        deps=[], gating=True,
    ),
    dict(
        name="doc_build_steps",
        cmd=["python", "tests/test_doc_build_steps.py"],
        # The suite walks every .md in the repo, so any .md must be able to select it.
        # With prefixes alone, live `step N of <flow>` citations in the root README and in
        # seven datasets/**/README.md files could be edited with this check skipped —
        # cumulusci.yml covered renumbering, but not writing a new wrong citation.
        triggers=["cumulusci.yml", "tests/test_doc_build_steps.py"],
        suffixes=[".md"],
        deps=["cumulusci"], gating=True,
    ),
    dict(
        name="cci_reference_drift",
        cmd=None,  # regenerate, then require a clean tree — see run_cci_reference_drift
        triggers=["cumulusci.yml", "scripts/ai/generate_cci_reference.py"],
        deps=["PyYAML"], gating=True,
    ),
    dict(
        name="stdlib_offline_suites",
        cmd=None,  # expanded at runtime — see stdlib_suites()
        triggers=["tasks/", "scripts/", "tests/", "datasets/", "cumulusci.yml",
                  "force-app/", "unpackaged/"],
        deps=[], gating=True,
    ),
    dict(
        name="yaml_offline_suites",
        cmd=["python", "tests/test_decision_table_tasks.py",
             "tests/test_fulfillment_scope_tolerance.py",
             "tests/test_skill_manifest_audit.py"],  # run in sequence
        triggers=["tasks/", "cumulusci.yml", "scripts/ai/skill_manifest.py",
                  ".claude/skill-manifest.yml",
                  "tests/test_decision_table_tasks.py",
                  "tests/test_fulfillment_scope_tolerance.py",
                  "tests/test_skill_manifest_audit.py"],
        deps=["PyYAML"], gating=True,
    ),
    dict(
        name="docgen_suite",
        # The one pytest-style suite in tests/: pytest collects it and it has no __main__
        # block, so `python tests/test_docgen_helpers.py` exits 0 having run zero tests
        # once pytest is installed (and ModuleNotFoundError before that). A silent green,
        # so it is invoked through pytest, not the repo's usual `python tests/<name>.py`.
        cmd=["python", "-m", "pytest", "-q", "tests/test_docgen_helpers.py"],
        triggers=["scripts/docgen/", "tests/test_docgen_helpers.py"],
        deps=["pytest"], gating=True,
    ),
    dict(
        # 30 pytest suites under tests/build_harness/ and tests/txn_data_harness/ that no
        # check ran and no report mentioned, because discovery used a non-recursive listing.
        # 512 pass; build_harness needs 3.11+ for enum.StrEnum. Running them found a real
        # 264 regression: test_cli.py still asserted api-version 67.0 after commit 66f193f9
        # bumped the harness to 68.0 — a stale assertion nothing had executed since.
        name="harness_suites",
        cmd=["python", "-m", "pytest", "-q",
             "tests/build_harness", "tests/txn_data_harness"],
        triggers=["scripts/build_harness/", "scripts/txn_data_harness/",
                  "tests/build_harness/", "tests/txn_data_harness/"],
        deps=["pytest", "PyYAML", "textual", "requests"], min_python=(3, 11), gating=True,
    ),
    dict(
        # Kept out of stdlib_offline_suites on purpose: this suite invokes pr_gate.py as a
        # subprocess, so running it from inside a check that a `tests/` change selects
        # would nest the gate inside itself. Its own probe paths select only checks that
        # do not run it, which bounds the nesting at one level.
        name="pr_gate_suite",
        cmd=["python", "tests/test_pr_gate.py"],
        triggers=["scripts/ai/pr_gate.py", "tests/test_pr_gate.py"],
        deps=[], gating=True,
    ),
    dict(
        name="sfdmu_datasets",
        cmd=["python", "scripts/validate_sfdmu_v5_datasets.py"],
        triggers=["datasets/"],
        deps=[], gating=False,
        note="advisory until pack 123: 2 Criticals on a clean tree are validator "
             "false positives (Readonly CSV demand, objectset_source layout)",
    ),
]

# Suites that need nothing but the standard library, run as one check. Enumerated rather
# than globbed: a new suite with an unmet dependency would otherwise join a stdlib check
# and fail it for a reason that has nothing to do with the change. `unlisted_suites()`
# reports anything in tests/ that no check claims, so adding one is not silently ignored.
STDLIB_SUITES = [
    "tests/test_agents_common.py",
    "tests/test_context_apply.py",
    "tests/test_context_delete.py",
    "tests/test_context_payload.py",
    "tests/test_context_plan_validator.py",
    "tests/test_context_runtime.py",
    "tests/test_decision_tables_client.py",
    "tests/test_decision_tables_toolkit.py",
    "tests/test_expression_set_schema.py",
    "tests/test_expression_sets_toolkit.py",
    "tests/test_fix_scratch_identity.py",
    "tests/test_qb_multicurrency_data.py",
    "tests/test_rlm_apex_file.py",
    "tests/test_rlm_cml_import_failure.py",
    "tests/test_snapshot_dev_guide.py",
]

CLAIMED_SUITES = set(STDLIB_SUITES) | {
    "tests/test_decision_table_tasks.py",
    "tests/test_fulfillment_scope_tolerance.py",
    "tests/test_skill_manifest_audit.py",
    "tests/test_doc_build_steps.py",
    "tests/test_docgen_helpers.py",
    "tests/test_pr_gate.py",
    # Run as whole directories by harness_suites rather than file by file.
    "tests/build_harness/",
    "tests/txn_data_harness/",
    # Its own check; also a member of no bulk list, so it is not run twice.
    "tests/test_branch_scope.py",
    "tests/test_erd_doc_counts.py",
}

# Suites deliberately outside the gate, each with the reason. Separate from CLAIMED_SUITES so
# "nothing runs it" and "we decided not to run it" cannot be confused, and so neither can
# happen silently: discovery reports anything in tests/ that appears in neither.
EXCLUDED_SUITES = {
    "tests/test-cleanup.sh": "integration script — requires a live org",
    "tests/test-prepare-rlm-org.sh": "integration script — requires a live org",
}


def die(msg):
    print(f"pr_gate: {msg}", file=sys.stderr)
    sys.exit(2)


def unlisted_suites():
    """Suites under tests/ that no check runs and no exclusion covers.

    Walks, rather than listing one directory: a flat listing missed the 30 suites in
    tests/build_harness/ and tests/txn_data_harness/ entirely, so the report said "none
    unclaimed" while editing one of them ran seventeen unrelated suites and passed. Shell
    suites are discovered too — they were previously skipped by the `.py` filter, which
    means the right outcome (not gating an org-requiring script) happened by accident
    instead of by declaration.
    """
    tests_dir = os.path.join(REPO_ROOT, "tests")
    if not os.path.isdir(tests_dir):
        # An absent tests/ is not an empty tests/; saying "none unclaimed" here would be
        # the same lie this function exists to catch.
        return ["tests/ is missing entirely"]
    found = set()
    for root, dirs, names in os.walk(tests_dir):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
        for name in names:
            if not (name.startswith("test_") or name.startswith("test-")):
                continue
            if not name.endswith((".py", ".sh")):
                continue
            found.add(os.path.relpath(os.path.join(root, name), REPO_ROOT))
    claimed_dirs = tuple(c for c in CLAIMED_SUITES if c.endswith("/"))
    return sorted(f for f in found
                  if f not in CLAIMED_SUITES
                  and f not in EXCLUDED_SUITES
                  and not f.startswith(claimed_dirs))


def changed_files(base):
    """Paths changed against `base`, via the merge base so unrelated base commits do not
    enlarge the selection (the mistake `check_branch_scope.py` documents)."""
    try:
        # Three dots, not two: `base...HEAD` diffs from the merge base, so commits that
        # landed on the base after this branch diverged do not enter the selection.
        # --no-renames, because git's rename detection reports only the destination — so
        # moving a plan README *out* of datasets/sfdmu/ would not select the check that
        # notices the plan lost its README. -z, because git quotes and escapes non-ASCII
        # paths ("docs/caf\303\251.md"), and a leading quote matches no trigger prefix.
        out = subprocess.run(["git", "diff", "--no-renames", "-z", "--name-only",
                              f"{base}...HEAD"],
                             cwd=REPO_ROOT, capture_output=True, text=True)
        if out.returncode != 0:
            die(f"git diff against {base!r} failed: {out.stderr.strip()}")
        files = [p for p in out.stdout.split("\0") if p]
        # Uncommitted work counts too, so running this locally before a commit is honest.
        st = subprocess.run(["git", "status", "--porcelain", "-z"], cwd=REPO_ROOT,
                            capture_output=True, text=True)
        # Checked, not assumed: a failed `git status` returns empty stdout, which is
        # indistinguishable from a clean tree — so an unreadable index would silently
        # drop every uncommitted path from the selection and still exit 0.
        if st.returncode != 0:
            die(f"git status failed: {st.stderr.strip()}")
        # -z separates entries with NUL and, for a rename, emits "XY new\0old\0" — both
        # halves are wanted here, so every non-status token is taken as a path.
        for entry in st.stdout.split("\0"):
            if not entry:
                continue
            files.append(entry[3:] if len(entry) > 3 and entry[2] == " " else entry)
        return sorted(set(files))
    except FileNotFoundError:
        die("git not found on PATH")


def selects(check, files):
    if any(f.startswith(t) for t in check["triggers"] for f in files):
        return True
    return any(f.endswith(s) for s in check.get("suffixes", ()) for f in files)


def missing_deps(check):
    missing = [pkg for pkg in check["deps"]
               if not have_module(DEPS.get(pkg, pkg))]
    need = check.get("min_python")
    if need and sys.version_info[:2] < need:
        missing.append(f"python>={'.'.join(str(n) for n in need)}"
                       f" (running {sys.version_info.major}.{sys.version_info.minor})")
    return missing


_IMPORTABLE = {}


def have_module(name):
    """True when `import name` actually succeeds, in a child so nothing leaks in here."""
    if name not in _IMPORTABLE:
        try:
            proc = subprocess.run([sys.executable, "-c", f"import {name}"],
                                  capture_output=True, timeout=120)
            _IMPORTABLE[name] = proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            _IMPORTABLE[name] = False
    return _IMPORTABLE[name]


def run(cmd):
    """Run one command from the repo root, streaming nothing but returning everything."""
    argv = list(cmd)
    if argv and argv[0] == "python":
        argv[0] = sys.executable
    started = time.time()
    try:
        # Bounded, so one hung check cannot burn the whole CI job's budget with no output.
        proc = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True,
                              timeout=CHECK_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 1, (f"timed out after {CHECK_TIMEOUT}s: {' '.join(argv)}"), time.time() - started
    return proc.returncode, proc.stdout + proc.stderr, time.time() - started


def run_cci_reference_drift():
    """Regenerate the CCI reference and require the tree to come back clean.

    The generator is the check: it exits 0 whether or not it rewrote anything, so the
    verdict is the git diff afterwards, scoped to what it writes.
    """
    code, out, secs = run(["python", "scripts/ai/generate_cci_reference.py"])
    if code != 0:
        return code, out, secs
    # Scoped to exactly the three files the generator writes. It was scoped to
    # docs/references/ as well, which it never writes and which is hand-authored — so any
    # unrelated edit there failed the check with "commit the regenerated result".
    generated = [f".cursor/skills/cci-orchestration/{name}"
                 for name in ("tasks-reference.md", "flows-reference.md",
                              "feature-flags.md")]
    diff = subprocess.run(["git", "status", "--porcelain", "--", *generated],
                          cwd=REPO_ROOT, capture_output=True, text=True)
    # Here the empty-output-means-clean trap is worse than in changed_files: this git status
    # *is* the verdict, so a failed one reads as "no drift" and passes the check.
    if diff.returncode != 0:
        return 1, (out + "\ngit status failed, so drift could not be determined:\n"
                   + diff.stderr), secs
    if diff.stdout.strip():
        return 1, (out + "\nRegenerating changed committed files — commit the result:\n"
                   + diff.stdout), secs
    return 0, out + "\nno drift", secs


def resolve(check):
    if check["name"] == "cci_reference_drift":
        return run_cci_reference_drift
    if check["name"] == "stdlib_offline_suites":
        return lambda: run_sequence([["python", s] for s in STDLIB_SUITES])
    if check["name"] == "yaml_offline_suites":
        return lambda: run_sequence([["python", s] for s in check["cmd"][1:]])
    if check["cmd"] is None:
        # A runtime-expanded check whose branch above was never added would otherwise reach
        # run(None) and raise, aborting the loop before any result printed — and exit 1,
        # reading as a gating failure rather than the tool error it is.
        die(f"{check['name']} has cmd=None and resolve() has no branch for it")
    return lambda: run(check["cmd"])


def run_sequence(cmds):
    """Run every command even after one fails, so a single failure does not hide the rest."""
    worst, chunks, total = 0, [], 0.0
    for cmd in cmds:
        code, out, secs = run(cmd)
        total += secs
        worst = worst or code
        chunks.append(f"$ {' '.join(cmd)}  -> exit {code} ({secs:.1f}s)\n{out}")
    return worst, "\n".join(chunks), total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", help="git ref to diff against (e.g. origin/264)")
    ap.add_argument("--changed-files-from", help="file with one changed path per line")
    ap.add_argument("--all", action="store_true", help="run every check regardless of paths")
    ap.add_argument("--list", action="store_true", help="print the matrix and exit")
    ap.add_argument("--requirements", action="store_true",
                    help="print pip deps the selection needs, one per line, then exit")
    args = ap.parse_args()

    if args.list:
        print(f"{'check':26} {'gating':7} {'deps':34} triggers")
        for c in CHECKS:
            selectors = list(c["triggers"]) + [f"*{s}" for s in c.get("suffixes", ())]
            print(f"{c['name']:26} {str(c['gating']):7} "
                  f"{','.join(c['deps']) or '-':34} {', '.join(selectors)}")
        print("\nexcluded from the gate, deliberately:")
        for path, reason in sorted(EXCLUDED_SUITES.items()):
            print(f"  {path:40} {reason}")
        orphans = unlisted_suites()
        print(f"\nsuites no check runs and no exclusion covers: {orphans or 'none'}")
        return 0

    if sum(bool(x) for x in (args.base, args.changed_files_from, args.all)) != 1:
        die("pass exactly one of --base, --changed-files-from, --all")

    if args.all:
        files, selected = None, list(CHECKS)
    else:
        if args.changed_files_from:
            try:
                with open(args.changed_files_from) as f:
                    files = [ln.strip() for ln in f if ln.strip()]
            except OSError as exc:
                die(f"cannot read {args.changed_files_from}: {exc}")
        else:
            files = changed_files(args.base)
        selected = [c for c in CHECKS if selects(c, files)]

    if args.requirements:
        for pkg in sorted({d for c in selected for d in c["deps"]}):
            print(PINS.get(pkg, pkg))
        return 0

    orphans = unlisted_suites()
    if files is not None:
        print(f"{len(files)} changed path(s) vs {args.base or 'file'}; "
              f"{len(selected)} of {len(CHECKS)} checks selected\n")

    results, failures, advisory_failures = [], [], []
    for check in CHECKS:
        if check not in selected:
            results.append((check, "SKIPPED", "", 0.0))
            continue
        missing = missing_deps(check)
        if missing:
            # Gating: a missing dependency is a failure, not a skip. Otherwise a broken
            # install is indistinguishable from a change that needed no checking.
            status = "MISSING-DEP" if check["gating"] else "ADVISORY-DEP"
            results.append((check, status, f"missing: {', '.join(missing)}", 0.0))
            if check["gating"]:
                failures.append(check["name"])
            continue
        code, out, secs = resolve(check)()
        if code == 0:
            results.append((check, "PASS", "", secs))
        elif check["gating"]:
            results.append((check, "FAIL", out, secs))
            failures.append(check["name"])
        else:
            results.append((check, "ADVISORY", out, secs))
            advisory_failures.append(check["name"])

    width = max(len(c["name"]) for c in CHECKS)
    print("=" * 78)
    for check, status, _, secs in results:
        timing = f"{secs:5.1f}s" if secs else "      "
        note = "" if status != "SKIPPED" else "  (nothing it covers changed)"
        if status in ("ADVISORY", "ADVISORY-DEP"):
            note = f"  ({check['note']})"
        print(f"[{status:11}] {check['name']:{width}} {timing}{note}")
    print("=" * 78)

    for check, status, out, _ in results:
        # Every non-passing check gets a section, including one that failed silently:
        # "[FAIL]" with no detail anywhere is indistinguishable from a reporting bug.
        if status in ("FAIL", "MISSING-DEP", "ADVISORY", "ADVISORY-DEP"):
            body = out.rstrip() or "(the check produced no output)"
            # A gating failure is echoed whole — it has to be diagnosable from the log
            # alone. An advisory one is informational, and the SFDMU validator prints a
            # ~100-line report every run, so it is tailed rather than allowed to bury
            # the failures above it.
            if not check["gating"]:
                lines = body.split("\n")
                if len(lines) > ADVISORY_HEAD:
                    body = ("\n".join(lines[:ADVISORY_HEAD])
                            + f"\n({len(lines) - ADVISORY_HEAD} later line(s) elided; run "
                              f"the check directly for the full report)")
            print(f"\n----- {check['name']} ({status}) -----\n{body}")

    if orphans:
        print(f"\n[FAIL       ] suites no check runs: {', '.join(orphans)}\n"
              "              add each to a check in CHECKS, or to CLAIMED_SUITES with a "
              "reason — an unrun suite is not a passing suite")
        failures.append("unlisted_suites")

    # Every check appears in exactly one bucket and the buckets sum to len(CHECKS).
    # MISSING-DEP previously fell out of both counts, so a reader reconciling "11 executed,
    # 0 skipped" against 12 checks found one unaccounted for — the shape this file exists
    # to eliminate.
    executed = sum(1 for _, s, _, _ in results if s in ("PASS", "FAIL", "ADVISORY"))
    skipped = sum(1 for _, s, _, _ in results if s == "SKIPPED")
    blocked = sum(1 for _, s, _, _ in results if s in ("MISSING-DEP", "ADVISORY-DEP"))
    assert executed + skipped + blocked == len(CHECKS), "a check fell out of the summary"
    print(f"\n{len(CHECKS)} checks: {executed} executed, {skipped} skipped, "
          f"{blocked} blocked on a missing dependency, {len(failures)} failed"
          + (f", {len(advisory_failures)} advisory failure(s): "
             f"{', '.join(advisory_failures)}" if advisory_failures else ""))

    if failures:
        print(f"\nFAILED: {', '.join(failures)}")
        return 1
    print("\nAll selected gating checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
