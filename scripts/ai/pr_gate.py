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

# Package -> the import name that proves it is installed. `analyze_agent_tooling.py` also
# needs Python 3.10+ (`sys.stdlib_module_names`); on 3.9 it reported `json, os, re` as
# non-stdlib, so the version is checked as a dependency rather than assumed.
DEPS = {
    "PyYAML": "yaml",
    "cumulusci": "cumulusci",
    "pytest": "pytest",
}

# What `--requirements` emits, so CI installs only what the selection needs. CumulusCI is
# pinned to the version `prepare-rlm-org.yml` installs: two workflows resolving different
# CumulusCI versions would let a flow-citation check pass here and fail there.
PINS = {"cumulusci": "cumulusci==4.8.1"}

# Lines of an advisory check's output to keep. Gating failures are never truncated.
ADVISORY_TAIL = 20

# name, command, path prefixes that select it, extra pip deps, gating, note
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
        triggers=["docs/erds/", ".cursor/skills/revenue-cloud-data-model/",
                  ".cursor/skills/schema-validation/", ".cursor/skills/doc-consistency/",
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
        triggers=["cumulusci.yml", "docs/", "tests/test_doc_build_steps.py",
                  ".cursor/skills/"],
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
             "tests/test_fulfillment_scope_tolerance.py"],  # run in sequence
        triggers=["tasks/", "cumulusci.yml", "tests/test_decision_table_tasks.py",
                  "tests/test_fulfillment_scope_tolerance.py"],
        deps=["PyYAML"], gating=True,
    ),
    dict(
        name="docgen_suite",
        # The one pytest-style suite in tests/. `python tests/test_docgen_helpers.py`
        # raises ModuleNotFoundError even where pytest is installed, because it has no
        # __main__ block — so it must be invoked through pytest, not the repo's usual
        # `python tests/<name>.py`.
        cmd=["python", "-m", "pytest", "-q", "tests/test_docgen_helpers.py"],
        triggers=["scripts/docgen/", "tests/test_docgen_helpers.py"],
        deps=["pytest"], gating=True,
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
    "tests/test_branch_scope.py",
    "tests/test_context_apply.py",
    "tests/test_context_delete.py",
    "tests/test_context_payload.py",
    "tests/test_context_plan_validator.py",
    "tests/test_context_runtime.py",
    "tests/test_decision_tables_client.py",
    "tests/test_decision_tables_toolkit.py",
    "tests/test_erd_doc_counts.py",
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
    "tests/test_doc_build_steps.py",
    "tests/test_docgen_helpers.py",
    "tests/test_pr_gate.py",
}


def die(msg):
    print(f"pr_gate: {msg}", file=sys.stderr)
    sys.exit(2)


def unlisted_suites():
    """Suites in tests/ that no check runs. A new one must not join silently."""
    tests_dir = os.path.join(REPO_ROOT, "tests")
    if not os.path.isdir(tests_dir):
        return []
    found = {f"tests/{f}" for f in os.listdir(tests_dir)
             if f.startswith("test_") and f.endswith(".py")}
    return sorted(found - CLAIMED_SUITES)


def changed_files(base):
    """Paths changed against `base`, via the merge base so unrelated base commits do not
    enlarge the selection (the mistake `check_branch_scope.py` documents)."""
    try:
        # Three dots, not two: `base...HEAD` diffs from the merge base, so commits that
        # landed on the base after this branch diverged do not enter the selection. Two
        # dots would select checks for files the pull request never touched.
        out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"],
                             cwd=REPO_ROOT, capture_output=True, text=True)
        if out.returncode != 0:
            die(f"git diff against {base!r} failed: {out.stderr.strip()}")
        files = [ln.strip() for ln in out.stdout.split("\n") if ln.strip()]
        # Uncommitted work counts too, so running this locally before a commit is honest.
        st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                            capture_output=True, text=True)
        for line in st.stdout.split("\n"):
            if len(line) > 3:
                files.append(line[3:].strip().split(" -> ")[-1])
        return sorted(set(files))
    except FileNotFoundError:
        die("git not found on PATH")


def selects(check, files):
    return any(f.startswith(t) for t in check["triggers"] for f in files)


def missing_deps(check):
    missing = [pkg for pkg in check["deps"]
               if not have_module(DEPS.get(pkg, pkg))]
    need = check.get("min_python")
    if need and sys.version_info[:2] < need:
        missing.append(f"python>={'.'.join(str(n) for n in need)}"
                       f" (running {sys.version_info.major}.{sys.version_info.minor})")
    return missing


def have_module(name):
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def run(cmd):
    """Run one command from the repo root, streaming nothing but returning everything."""
    argv = list(cmd)
    if argv and argv[0] == "python":
        argv[0] = sys.executable
    started = time.time()
    proc = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr, time.time() - started


def run_cci_reference_drift():
    """Regenerate the CCI reference and require the tree to come back clean.

    The generator is the check: it exits 0 whether or not it rewrote anything, so the
    verdict is the git diff afterwards, scoped to what it writes.
    """
    code, out, secs = run(["python", "scripts/ai/generate_cci_reference.py"])
    if code != 0:
        return code, out, secs
    diff = subprocess.run(["git", "status", "--porcelain", "--",
                           ".cursor/skills/cci-orchestration/", "docs/references/"],
                          cwd=REPO_ROOT, capture_output=True, text=True)
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
        print(f"{'check':26} {'gating':7} {'deps':12} triggers")
        for c in CHECKS:
            print(f"{c['name']:26} {str(c['gating']):7} "
                  f"{','.join(c['deps']) or '-':12} {', '.join(c['triggers'])}")
        orphans = unlisted_suites()
        print(f"\nsuites no check runs: {orphans or 'none'}")
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
                if len(lines) > ADVISORY_TAIL:
                    body = (f"({len(lines) - ADVISORY_TAIL} earlier line(s) elided; run "
                            f"the check directly for the full report)\n"
                            + "\n".join(lines[-ADVISORY_TAIL:]))
            print(f"\n----- {check['name']} ({status}) -----\n{body}")

    if orphans:
        print(f"\n[FAIL       ] suites no check runs: {', '.join(orphans)}\n"
              "              add each to a check in CHECKS, or to CLAIMED_SUITES with a "
              "reason — an unrun suite is not a passing suite")
        failures.append("unlisted_suites")

    executed = sum(1 for _, s, _, _ in results if s in ("PASS", "FAIL", "ADVISORY"))
    skipped = sum(1 for _, s, _, _ in results if s == "SKIPPED")
    print(f"\n{executed} executed, {skipped} skipped, {len(failures)} failed"
          + (f", {len(advisory_failures)} advisory failure(s): "
             f"{', '.join(advisory_failures)}" if advisory_failures else ""))

    if failures:
        print(f"\nFAILED: {', '.join(failures)}")
        return 1
    print("\nAll selected gating checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
