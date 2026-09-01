#!/usr/bin/env python3
"""Does the discovery layer actually distinguish a tracked README-less plan (must be
reported) from an untracked/gitignored scratch plan (advisory only)?

Comment 3901323028 (PR #406, round-21 hosted review, pack 147): this is the PR's
headline fix — `find_plan_dirs()` discovering on export.json alone, and
`tracked_plan_dirs()`/`tracked_paths()` gating the *required* half of that on git
tracked-ness — yet no test exercised any of it. `tests/test_check_plan_readme_consistency.py`
only covers `check_plan()`'s README-content parsing, always against a synthetic plan
that already has a README. Reintroducing the old "export.json + README.md" discovery
condition, or dropping the tracked-ness gate, would leave that suite green.

Builds an isolated, hermetic git repo under a tempdir (same pattern as
tests/test_branch_scope.py) rather than touching this checkout's own git state, and
monkeypatches the loaded module's REPO_ROOT/SFDMU_ROOT globals to point into it —
every function under test reads those as module globals at call time, not as
values baked into a closure, so this is sufficient.

Run: `python tests/test_check_plan_readme_discovery.py` (offline, no org; spawns git
in a throwaway tempdir, no network).
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "scripts" / "ai" / "check_plan_readme_consistency.py"

GIT_ENV = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
GIT_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
               GIT_CONFIG_NOSYSTEM="1")


def git(cwd, *args):
    proc = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, env=GIT_ENV)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}:\n{proc.stderr}")
    return proc.stdout.strip()


def load_checker():
    spec = importlib.util.spec_from_file_location("plan_readme_checker_discovery", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _new_synthetic_repo(root):
    """A repo shaped like this one, enough for find_plan_dirs/tracked_plan_dirs:
    <root>/datasets/sfdmu/{tracked-no-readme, tracked-with-readme, untracked-scratch}/export.json
    plus a .gitignore excluding the scratch dir, mirroring datasets/sfdmu/test/**."""
    sfdmu = pathlib.Path(root) / "datasets" / "sfdmu"

    tracked_no_readme = sfdmu / "tracked-no-readme"
    tracked_no_readme.mkdir(parents=True)
    (tracked_no_readme / "export.json").write_text(json.dumps({"objectSets": []}))

    tracked_with_readme = sfdmu / "tracked-with-readme"
    tracked_with_readme.mkdir(parents=True)
    (tracked_with_readme / "export.json").write_text(json.dumps({"objectSets": []}))
    (tracked_with_readme / "README.md").write_text("# Doc\n")

    untracked_scratch = sfdmu / "untracked-scratch"
    untracked_scratch.mkdir(parents=True)
    (untracked_scratch / "export.json").write_text(json.dumps({"objectSets": []}))

    (pathlib.Path(root) / ".gitignore").write_text("datasets/sfdmu/untracked-scratch/**\n")

    git(root, "init", "--quiet", "-b", "base")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "test")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "core.hooksPath", os.devnull)
    git(root, "add", ".gitignore",
        str(tracked_no_readme.relative_to(root)), str(tracked_with_readme.relative_to(root)))
    git(root, "commit", "--quiet", "-m", "seed")

    return tracked_no_readme, tracked_with_readme, untracked_scratch


def _case_walk_finds_readme_less_and_untracked_alike():
    """find_plan_dirs([]) (the bare-walk path) is git-tracked-ness-BLIND — it must
    surface every export.json dir, tracked or not; narrowing to "must have a README"
    happens one layer up, in main()'s tracked-vs-not split."""
    with tempfile.TemporaryDirectory() as td:
        mod = load_checker()
        no_readme_dir, with_readme_dir, untracked_dir = _new_synthetic_repo(td)
        mod.REPO_ROOT = td
        mod.SFDMU_ROOT = str(pathlib.Path(td) / "datasets" / "sfdmu")

        with_readme, no_readme = mod.find_plan_dirs([])
        return (sorted(with_readme), sorted(no_readme))


def _case_tracked_plan_dirs_excludes_gitignored_scratch():
    with tempfile.TemporaryDirectory() as td:
        mod = load_checker()
        no_readme_dir, with_readme_dir, untracked_dir = _new_synthetic_repo(td)
        mod.REPO_ROOT = td
        mod.SFDMU_ROOT = str(pathlib.Path(td) / "datasets" / "sfdmu")

        _with_readme, no_readme = mod.find_plan_dirs([])
        tracked = mod.tracked_plan_dirs(no_readme)
        return sorted(tracked)


def _case_explicit_target_outside_repo_reports_cleanly():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
        mod = load_checker()
        _new_synthetic_repo(td)
        mod.REPO_ROOT = td
        mod.SFDMU_ROOT = str(pathlib.Path(td) / "datasets" / "sfdmu")

        outside_plan = pathlib.Path(outside) / "not-in-repo"
        outside_plan.mkdir()
        (outside_plan / "export.json").write_text(json.dumps({"objectSets": []}))
        with_readme, no_readme = mod.find_plan_dirs([str(outside_plan)])
        return with_readme, no_readme


def main() -> int:
    failures = []
    print("=" * 100)
    print("-- find_plan_dirs([]) discovers on export.json alone, tracked-ness blind")

    with_readme, no_readme = _case_walk_finds_readme_less_and_untracked_alike()
    checks = [
        ("a plan with a README is reported in with_readme",
         any(p.endswith("tracked-with-readme") for p in with_readme)),
        ("a tracked plan with NO README is reported in no_readme, not silently skipped",
         any(p.endswith("tracked-no-readme") for p in no_readme)),
        ("an untracked/gitignored scratch plan with no README is ALSO surfaced by the bare "
         "walk (tracked-ness is not this function's job)",
         any(p.endswith("untracked-scratch") for p in no_readme)),
    ]
    for label, ok in checks:
        if not ok:
            failures.append(label)
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

    print("-- tracked_plan_dirs() narrows no_readme to git-tracked plans only")
    tracked = _case_tracked_plan_dirs_excludes_gitignored_scratch()
    checks = [
        ("the tracked README-less plan survives the filter (still owed a README)",
         any(p.endswith("tracked-no-readme") for p in tracked)),
        ("the gitignored scratch plan is filtered OUT (advisory only, not required)",
         not any(p.endswith("untracked-scratch") for p in tracked)),
    ]
    for label, ok in checks:
        if not ok:
            failures.append(label)
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

    print("-- an explicit target outside REPO_ROOT is skipped cleanly, not a raw git crash")
    with_readme_out, no_readme_out = _case_explicit_target_outside_repo_reports_cleanly()
    ok = with_readme_out == [] and no_readme_out == []
    if not ok:
        failures.append("outside-repo target reported cleanly with no dirs")
    print(f"  [{'PASS' if ok else 'FAIL'}] outside-repo target reported cleanly with no dirs")

    print("=" * 100)
    total = 3 + 2 + 1
    if failures:
        for label in failures:
            print(f"FAILED: {label}")
        print(f"\n{total - len(failures)}/{total} checks passed")
        return 1
    print(f"{total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
