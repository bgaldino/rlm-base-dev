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

import json
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


# Hermetic git. Without this the suite inherits the developer's global config and
# aborts on settings that have nothing to do with the code under test -- signed
# commits (`commit.gpgsign` with no usable key here), a global `core.hooksPath`
# whose pre-commit fails, or an exported GIT_DIR from running inside a hook. Each
# one produced a bare traceback indistinguishable from "the script regressed".
GIT_ENV = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
GIT_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
               GIT_CONFIG_NOSYSTEM="1")


def git(cwd, *args, check_rc=True):
    proc = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, env=GIT_ENV)
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
    # Belt and braces alongside GIT_ENV: a repo-local override also protects the
    # case where the env is passed through by something else.
    git(cwd, "config", "commit.gpgsign", "false")
    git(cwd, "config", "core.hooksPath", os.devnull)
    commit(cwd, "seed.txt", "seed\n", "seed")
    return cwd


def run_check(cwd, *args, extra_path=None, no_fetch=True):
    argv = [sys.executable, str(SCRIPT)] + (["--no-fetch"] if no_fetch else []) + list(args)
    env = dict(GIT_ENV)
    if extra_path:
        env["PATH"] = f"{extra_path}:{env['PATH']}"
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def stub_gh(cwd, view, listing):
    """Put a fake `gh` on PATH so the --pr path can be driven with no network.

    Returns the directory to prepend to PATH. The stub answers exactly the two
    calls the script makes -- `pr view` and `pr list` -- which is what lets the
    STACKED signal be tested end to end instead of only through _is_ancestor.
    """
    bindir = Path(cwd) / "_stubbin"
    bindir.mkdir(exist_ok=True)
    gh = bindir / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        f"if [ \"$2\" = view ]; then cat <<'J1'\n{json.dumps(view)}\nJ1\n"
        f"else cat <<'J2'\n{json.dumps(listing)}\nJ2\nfi\n")
    gh.chmod(0o755)
    return str(bindir)


def test_clean_branch(root):
    print("\nA branch that owns everything on it")
    cwd = new_repo(root, "clean")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    commit(cwd, "a.txt", "a\n", "own commit one")
    commit(cwd, "b.txt", "b\n", "own commit two")
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("clean branch exits 0", rc == 0, f"rc={rc}\n{out}")
    check("clean branch counts its own commits", "none of the 2 non-merge commit(s)" in out, out)
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
          "none of the 3 non-merge commit(s)" in out, out)


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
          "none of the 1 non-merge commit(s)" in out, out)


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
    """Drive the whole --pr path with a stubbed gh.

    An earlier version of this test called `_is_ancestor` directly, which left the
    signal itself untested: deleting the `others` loop, inverting the call site, or
    dropping `stacked` from the failure condition all kept the suite green.
    """
    print("\nStacked on an UNMERGED branch — the case patch-id cannot see")
    cwd = new_repo(root, "stacked")
    git(cwd, "checkout", "--quiet", "-b", "parent-pr")
    commit(cwd, "parent.txt", "parent\n", "the parent PR's commit")
    git(cwd, "checkout", "--quiet", "-b", "feature")
    commit(cwd, "mine.txt", "mine\n", "my change")
    git(cwd, "remote", "add", "origin", str(cwd))
    git(cwd, "update-ref", "refs/remotes/origin/base", "base")
    git(cwd, "update-ref", "refs/remotes/origin/parent-pr", "parent-pr")
    head = git(cwd, "rev-parse", "feature")
    parent_oid = git(cwd, "rev-parse", "parent-pr")

    # Signal 1 alone cannot see this: nothing has merged, so no patch is upstream.
    rc, out = run_check(cwd, "--base", "base", "--head", "feature")
    check("patch-id alone reports clean (documented blind spot)", rc == 0, f"rc={rc}\n{out}")

    mine = {"baseRefName": "base", "headRefName": "feature", "headRefOid": head,
            "headRepositoryOwner": {"login": "me"}, "isCrossRepository": False}
    parent_pr = {"number": 2, "headRefName": "parent-pr", "headRefOid": parent_oid,
                 "title": "the parent PR", "isCrossRepository": False}

    bindir = stub_gh(cwd, mine, [{"number": 1, "headRefName": "feature",
                                  "headRefOid": head, "title": "mine",
                                  "isCrossRepository": False}, parent_pr])
    rc, out = run_check(cwd, "--pr", "1", extra_path=bindir)
    check("stacking on an open PR exits 1", rc == 1, f"rc={rc}\n{out}")
    check("names the PR it is stacked on", "STACKED  on open PR #2" in out, out)
    check("explains why signal 1 missed it", "invisible to the upstream check" in out, out)
    # Both commits are listed as `own`, and correctly so: nothing has merged, so
    # patch-id has nothing to match the parent's commit against. That is the whole
    # reason the second signal exists -- the per-commit listing cannot express this
    # finding, only the PR-level one can.
    check("the parent's commit still reads as `own` under signal 1",
          out.count("own      ") == 2, out)
    check("the PR under test is not reported against itself",
          "PR #1" not in out, out)

    print("\n  ...and a branch merely UP TO DATE with base is not stacked")
    # The release-integration PR (`264` -> `main`) has the base branch itself as
    # its head. That head is an ancestor of every branch current with base, so
    # without the containment guard this fails every branch in the repo.
    integration = {"number": 3, "headRefName": "base",
                   "headRefOid": git(cwd, "rev-parse", "base"),
                   "title": "base -> main release integration",
                   "isCrossRepository": False}
    bindir = stub_gh(cwd, mine, [integration])
    rc, out = run_check(cwd, "--pr", "1", extra_path=bindir)
    check("a PR whose head is the base branch is not a finding", rc == 0, f"rc={rc}\n{out}")
    check("and it is not printed as stacked", "STACKED" not in out, out)

    print("\n  ...and a fork PR is skipped rather than resolved to our own branch")
    # `origin/parent-pr` exists locally, so an unguarded fallback would compare
    # against *our* branch of that name and report a stack that does not exist.
    fork = dict(parent_pr, number=4, headRefOid="0" * 40, isCrossRepository=True,
                title="a fork's PR on a colliding branch name")
    bindir = stub_gh(cwd, mine, [fork])
    rc, out = run_check(cwd, "--pr", "1", extra_path=bindir)
    check("a fork PR does not produce a phantom stack", rc == 0, f"rc={rc}\n{out}")

    print("\n  ...and an unrelated open PR is not a finding")
    git(cwd, "checkout", "--quiet", "-b", "unrelated", "base")
    commit(cwd, "other.txt", "other\n", "unrelated work")
    unrelated = {"number": 5, "headRefName": "unrelated",
                 "headRefOid": git(cwd, "rev-parse", "unrelated"),
                 "title": "unrelated", "isCrossRepository": False}
    git(cwd, "checkout", "--quiet", "feature")
    bindir = stub_gh(cwd, mine, [unrelated])
    rc, out = run_check(cwd, "--pr", "1", extra_path=bindir)
    check("an unrelated open PR is not reported", rc == 0, f"rc={rc}\n{out}")


def test_fetch_before_comparing(root):
    """A stale base hides the finding, so the check must fetch first.

    This is the failure the guard exists for: the inherited commits *have* merged
    upstream, but the local remote-tracking copy predates that, so patch-id finds
    nothing to match and the branch reads clean. Comparing the two modes in one
    test is what makes the guard's absence visible.
    """
    print("\nFetch before comparing — a stale base reports clean")
    upstream = new_repo(root, "upstream-origin")
    git(upstream, "checkout", "--quiet", "-b", "composed")
    inherited = [commit(upstream, f"o{i}.txt", f"o{i}\n", f"other {i}") for i in (1, 2, 3)]
    git(upstream, "checkout", "--quiet", "base")

    work = Path(root) / "clone"
    subprocess.run(["git", "clone", "--quiet", str(upstream), str(work)],
                   capture_output=True, env=GIT_ENV, check=True)
    git(work, "config", "user.email", "t@example.com")
    git(work, "config", "user.name", "test")
    git(work, "config", "commit.gpgsign", "false")
    git(work, "checkout", "--quiet", "-b", "feature", "origin/composed")
    commit(work, "mine.txt", "mine\n", "my change")

    # The five fixes land upstream as new SHAs, after base has moved on.
    commit(upstream, "moved.txt", "moved\n", "base moves on")
    git(upstream, "cherry-pick", *inherited)

    rc, out = run_check(work, "--base", "origin/base", "--head", "feature")
    check("stale base reports clean — this is the trap", rc == 0, f"rc={rc}\n{out}")
    rc, out = run_check(work, "--base", "origin/base", "--head", "feature", no_fetch=False)
    check("fetching first finds the inherited commits", rc == 1, f"rc={rc}\n{out}")
    check("and counts all three", "3 of 4 non-merge commit(s)" in out, out)


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
    # A prefix of a real remote's name must not resolve to it. `rlm-base` is a
    # prefix of `rlm-base-dev`, so substring matching would answer confidently
    # about the wrong repository.
    git(cwd, "remote", "add", "origin", "https://github.com/owner/rlm-base-dev.git")
    rc, out = run_check(cwd, "--pr", "1", "--repo", "owner/rlm-base")
    check("a prefix of a remote's repo name does not match it",
          rc == 2 and "no git remote matches" in out, f"rc={rc}\n{out}")
    rc, out = run_check(cwd, "--pr", "1", "--repo", "not-an-owner-slash-name")
    check("--repo without a slash is a usage error",
          rc == 2 and "must be owner/name" in out, f"rc={rc}\n{out}")

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
        test_fetch_before_comparing(root)
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
