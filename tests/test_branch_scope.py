#!/usr/bin/env python3
"""Offline tests for scripts/ai/check_branch_scope.py.

Runs against throwaway repos built in a temp dir, so no org, no network, and no
dependence on this checkout's branches -- the #264-56 branches have been rebuilt
and merged, so a test reading real history would rot immediately.

The shapes below are the ones that matter, and each maps to a thing that actually
happened rather than to a line of the script:

  clean            a branch cut from base with its own commits
  #264-56          a branch cut from a composed integration branch, whose extra
                   commits have since merged into base (patch-id detectable)
  rebase fix       the same branch after rebasing onto the updated base
  reworded         an inherited commit whose subject was edited -- the case that
                   rules out subject matching
  cherry-picked    the same content committed twice, which is what patch-id is for
  empty            a branch with no commits ahead of base
  stacked          a branch built on an unmerged branch, invisible to patch-id

Also asserts the exit-code contract, because a gate keys on it: 0 clean,
1 findings, 2 tool/usage error. A missing tool must not read as a dirty branch.

Usage: python tests/test_branch_scope.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "ai" / "check_branch_scope.py"

_passed = 0
_failed: list[str] = []


def check(name, condition, detail=""):
    global _passed
    if condition:
        _passed += 1
        print(f"  [PASS] {name}")
    else:
        _failed.append(f"{name}: {detail}")
        print(f"  [FAIL] {name}  {detail}")


def git(cwd, *args, check_rc=True):
    proc = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    if check_rc and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}:\n{proc.stderr}")
    return proc.stdout.strip()


def commit(cwd, path, body, message):
    (Path(cwd) / path).parent.mkdir(parents=True, exist_ok=True)
    (Path(cwd) / path).write_text(body)
    git(cwd, "add", path)
    git(cwd, "commit", "--quiet", "-m", message)
    return git(cwd, "rev-parse", "HEAD")


def new_repo(root, name):
    cwd = Path(root) / name
    cwd.mkdir()
    git(cwd, "init", "--quiet", "-b", "base")
    git(cwd, "config", "user.email", "t@example.com")
    git(cwd, "config", "user.name", "test")
    commit(cwd, "seed.txt", "seed\n", "seed")
    return cwd


def run_check(cwd, *args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--no-fetch"] + list(args),
        cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def test_clean_branch(root):
    print("\nA branch that owns everything on it")
    cwd = new_repo(root, "clean")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    commit(cwd, "a.txt", "a\n", "own commit one")
    commit(cwd, "b.txt", "b\n", "own commit two")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("clean branch exits 0", rc == 0, f"rc={rc}\n{out}")
    check("clean branch counts its own commits", "all 2 non-merge commit(s)" in out, out)
    check("clean branch reports no foreign", "FOREIGN" not in out, out)


def build_264_56(root, name):
    """The #264-56 shape: branch cut from a composition, extras later merged.

    The extras must land on base as *new* SHAs, which is what a squash or rebase
    merge does (and what this repo's PRs do). A true merge of the composition
    would make them literal ancestors of base -- see test_true_merge, where there
    is correctly nothing to report. Base must also have moved on first, or the
    replayed commits keep their original SHAs and the case collapses.
    """
    cwd = new_repo(root, name)
    git(cwd, "checkout", "--quiet", "-b", "verify-composed")
    inherited = [commit(cwd, f"other{i}.txt", f"other{i}\n", f"fix other thing {i}")
                 for i in range(1, 6)]
    git(cwd, "checkout", "--quiet", "-b", "feature")
    own = [commit(cwd, f"mine{i}.txt", f"mine{i}\n", f"my real change {i}")
           for i in range(1, 4)]
    git(cwd, "checkout", "--quiet", "base")
    commit(cwd, "unrelated.txt", "moved on\n", "base moves on independently")
    git(cwd, "cherry-pick", *inherited)
    return cwd, inherited, own


def test_264_56_shape(root):
    print("\n#264-56: cut from a composed branch, the extras have since merged")
    cwd, inherited, own = build_264_56(root, "composed")

    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("composed branch exits 1", rc == 1, f"rc={rc}\n{out}")
    check("names all five inherited commits",
          all(sha[:8] in out for sha in inherited), out)
    check("marks the five FOREIGN", out.count("FOREIGN") == 5, out)
    check("keeps the branch's own three", out.count("own      ") == 3, out)
    check("reports 5 of 8", "5 of 8 non-merge commit(s)" in out, out)
    check("says the diff can revert landed fixes", "revert review fixes" in out, out)
    check("tells you how to rebuild", "cherry-pick only the commits listed" in out, out)
    check("own commits are not marked foreign",
          not any(f"FOREIGN  {sha[:8]}" in out for sha in own), out)

    print("\n  ...and the fix for it (rebase onto the updated base) reads clean")
    git(cwd, "checkout", "--quiet", "feature")
    git(cwd, "rebase", "--quiet", "base")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("rebased branch exits 0", rc == 0, f"rc={rc}\n{out}")
    check("rebased branch has only its own three",
          "all 3 non-merge commit(s)" in out, out)


def test_true_merge_is_not_a_finding(root):
    print("\nA composition that TRULY merged into base is not a finding")
    cwd = new_repo(root, "truemerge")
    git(cwd, "checkout", "--quiet", "-b", "composed")
    for i in range(1, 4):
        commit(cwd, f"other{i}.txt", f"other{i}\n", f"other {i}")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    commit(cwd, "mine.txt", "mine\n", "my change")
    git(cwd, "checkout", "--quiet", "base")
    git(cwd, "merge", "--quiet", "--no-ff", "-m", "merge the composition", "composed")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    # The inherited commits are literal ancestors of base now, so they are not in
    # the branch's diff and there is nothing to strip. Flagging here would be a
    # false positive on every branch cut from a merged parent.
    check("true-merged parent leaves nothing to report", rc == 0, f"rc={rc}\n{out}")
    check("only the branch's own commit is counted",
          "all 1 non-merge commit(s)" in out, out)


def test_reworded_subject(root):
    print("\nAn inherited commit with an edited subject (rules out subject matching)")
    cwd = new_repo(root, "reworded")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    # Same content as the upstream commit below, deliberately different words.
    inherited = commit(cwd, "other.txt", "other\n", "totally different words")
    commit(cwd, "mine.txt", "mine\n", "my change")
    git(cwd, "checkout", "--quiet", "base")
    commit(cwd, "unrelated.txt", "moved on\n", "base moves on")
    commit(cwd, "other.txt", "other\n", "fix: the original subject line")

    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("reword does not hide the inherited commit", rc == 1, f"rc={rc}\n{out}")
    check("the reworded commit is the one flagged",
          f"FOREIGN  {inherited[:8]}" in out, out)
    check("its own commit is still its own", out.count("own      ") == 1, out)
    # Guard the guard: nothing in base's history shares this branch's subject, so a
    # subject-matching implementation would pass this branch clean.
    subjects = git(cwd, "log", "--format=%s", "base").splitlines()
    check("subject matching could not have found it",
          "totally different words" not in subjects, subjects)


def test_cherry_picked_content(root):
    print("\nThe same content committed twice (what patch-id is for)")
    cwd = new_repo(root, "picked")
    git(cwd, "checkout", "--quiet", "-b", "upstream")
    sha = commit(cwd, "shared.txt", "shared content\n", "add shared thing")
    git(cwd, "checkout", "--quiet", "base")
    commit(cwd, "unrelated.txt", "moved on\n", "base moves on")
    git(cwd, "cherry-pick", sha)
    git(cwd, "checkout", "--quiet", "-b", "feature", "upstream")
    commit(cwd, "mine.txt", "mine\n", "my change")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("duplicate content is foreign even with a different sha", rc == 1, f"rc={rc}\n{out}")
    check("the duplicate is the one flagged", out.count("FOREIGN") == 1, out)
    check("the copy on base really has a different sha",
          git(cwd, "rev-parse", "base") != sha, "cherry-pick collapsed to the same sha")


def test_empty_branch(root):
    print("\nA branch with nothing ahead of base")
    cwd = new_repo(root, "empty")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("empty branch exits 0", rc == 0, f"rc={rc}\n{out}")
    check("empty branch says so", "no commits ahead of base" in out, out)


def test_stacked_on_unmerged(root):
    print("\nStacked on an UNMERGED branch — the case patch-id cannot see")
    cwd = new_repo(root, "stacked")
    git(cwd, "checkout", "--quiet", "-b", "parent-pr")
    parent = commit(cwd, "parent.txt", "parent\n", "the parent PR's commit")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    commit(cwd, "mine.txt", "mine\n", "my change")

    # Signal 1 alone cannot see this: nothing has merged, so no patch is upstream.
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("patch-id alone reports clean (documented blind spot)", rc == 0, f"rc={rc}\n{out}")

    # Signal 2 is what catches it: the parent's head is an ancestor of ours.
    sys.path.insert(0, str(SCRIPT.parent))
    os.chdir(cwd)
    import importlib
    mod = importlib.import_module("check_branch_scope")
    importlib.reload(mod)
    check("ancestor test sees the parent branch",
          mod._is_ancestor(parent, "feature"), "parent should be an ancestor of feature")
    check("ancestor test is directional, not symmetric",
          not mod._is_ancestor("feature", parent), "feature must not be an ancestor of parent")
    unrelated = git(cwd, "rev-parse", "base")
    check("base is an ancestor of both (so ancestry alone is not the finding)",
          mod._is_ancestor(unrelated, "feature"),
          "base must be an ancestor — the finding comes from the open-PR list, not ancestry")
    os.chdir(REPO)


def test_exit_code_contract(root):
    print("\nExit codes: 2 is for tool/usage errors, never 1")
    cwd = new_repo(root, "codes")
    rc, out = run_check(cwd, "--base", "base", "--head", "no-such-branch")
    check("unresolvable head exits 2, not 1", rc == 2, f"rc={rc}\n{out}")
    check("unresolvable head says which ref", "no-such-branch does not resolve" in out, out)
    rc, out = run_check(cwd, "--base", "nope/nope", "--head", "base")
    check("unresolvable base exits 2", rc == 2, f"rc={rc}\n{out}")

    # These assert the *reason*, not just the status. Every wrong-argument path
    # also exits 2 by way of a gh failure, so a status-only assertion passes even
    # when the guard it is meant to cover has been removed.
    proc = subprocess.run([sys.executable, str(SCRIPT), "--pr", "1", "--base", "x"],
                          cwd=cwd, capture_output=True, text=True)
    check("--pr with --base is rejected as a usage error",
          proc.returncode == 2 and "--pr resolves base and head" in proc.stderr,
          f"rc={proc.returncode}\n{proc.stderr}")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--repo", "a/b"],
                          cwd=cwd, capture_output=True, text=True)
    check("--repo without --pr is rejected as a usage error",
          proc.returncode == 2 and "--repo only applies to --pr" in proc.stderr,
          f"rc={proc.returncode}\n{proc.stderr}")
    # --pr 0 is falsy: it must reach PR handling, not fall through to the manual
    # path, so it has to hit the same mutual-exclusion error as any other number.
    proc = subprocess.run([sys.executable, str(SCRIPT), "--pr", "0", "--head", "base"],
                          cwd=cwd, capture_output=True, text=True)
    check("--pr 0 is treated as a PR, not as absent",
          proc.returncode == 2 and "--pr resolves base and head" in proc.stderr,
          f"rc={proc.returncode}\n{proc.stderr}")

    # A missing tool must not masquerade as a dirty branch.
    env = dict(os.environ, PATH="/nonexistent")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--no-fetch",
                           "--base", "base", "--head", "base"],
                          cwd=cwd, capture_output=True, text=True, env=env)
    check("missing git exits 2, not 1", proc.returncode == 2,
          f"rc={proc.returncode}\n{proc.stdout}{proc.stderr}")


def main():
    if not SCRIPT.exists():
        print(f"error: {SCRIPT} not found")
        return 2
    print("=" * 100)
    print("check_branch_scope.py — branch ownership detection (#264-56)")
    print("=" * 100)
    with tempfile.TemporaryDirectory() as root:
        test_clean_branch(root)
        test_264_56_shape(root)
        test_true_merge_is_not_a_finding(root)
        test_reworded_subject(root)
        test_cherry_picked_content(root)
        test_empty_branch(root)
        test_stacked_on_unmerged(root)
        test_exit_code_contract(root)
    print("\n" + "=" * 100)
    total = _passed + len(_failed)
    if _failed:
        print(f"{_passed}/{total} checks passed — {len(_failed)} FAILED")
        for failure in _failed:
            print(f"  - {failure}")
        return 1
    print(f"{_passed}/{total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
