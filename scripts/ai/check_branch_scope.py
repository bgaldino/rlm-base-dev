#!/usr/bin/env python3
"""Fail a branch that carries commits it does not own.

A PR branch cut from a *composed* integration branch -- one built by stacking
several in-flight fixes together to test them as a set -- silently inherits
those other fixes. Its diff then shows files it does not own, and worse, it
shows them in whatever **pre-review** state they were in when the composition
was made. Merging it walks back review fixes that already landed.

#264-56 is the concrete case: `fix/264-agents-authoring-bundle` was rebuilt once
to strip five inherited commits, then re-accumulated the same five from a later
rebase onto the stale composition, and was a day from merging a second time with
them. It carried 8 commits where the PR owned 3.

Two independent signals, because the inherited work may or may not have merged
yet and each signal is blind to one of those cases:

1. **Already upstream** -- `git cherry`, i.e. patch-id equivalence: `-` means
   this commit's content is in the base already, so the branch does not own it.
   This is the #264-56 signal, and it only works once the other PRs have merged.

2. **Contains another open PR's branch** -- if another open PR's head is an
   *ancestor* of this head, this branch is built on top of that PR, whose commits
   have not merged anywhere yet and so are invisible to signal 1. Found the hard
   way: while writing this check, the branch for its own companion fix was cut
   from the check's branch, and signal 1 reported clean. Needs `--pr`, since it
   is the PR list that says which branches are in flight.

   Two exclusions keep signal 2 honest, and both were false positives before they
   were guards. A head **already contained in the base** is skipped: the release
   integration PR (`264` -> `main`) has the base branch itself as its head, so
   without that guard every branch merely *up to date* with base was reported, and
   being behind base read cleaner than being current with it. A **fork's** head is
   skipped too, because it is not in this checkout and the `<remote>/<branch>`
   fallback would resolve a fork PR on a branch named `264` or `main` to *our*
   branch of that name. Signal 1 still covers both branches.

**What a clean result does and does not prove.** `git cherry`'s `+` means "no
patch-equivalent commit found upstream" -- which is not the same as "this branch
owns it", and the output says so rather than claiming otherwise. The residual gap
is narrow but real: an inherited commit whose upstream counterpart was **amended
or squash-combined** before merging has different content, so signal 1 finds no
match, and its PR is closed, so signal 2 does not list it. Both signals are blind
to that case. It did not arise in #264-56 (all five inherited commits were
patch-identical to their merged versions, which is why `git cherry` marked exactly
those five), and the case that *did* bite -- a stack on an unmerged PR -- is what
signal 2 covers. Treat a clean result as "neither known contamination shape is
present", not as proof of authorship; the diff review still has to happen.

A note on what does *not* work, so neither gets substituted:
`git merge-base --is-ancestor <commit> <base>` is not a detector. Inherited
commits are not ancestors of the base -- but neither is any legitimate new
commit, so it cannot separate them. (The 264 plan named this one before it was
tested against the history.) Matching commit *subjects* against the base works
on #264-56 but breaks on any reworded subject.

Exit status: 0 clean, 1 commits not owned by the branch, 2 usage/tool error. A
missing `git`/`gh` gives 2, never 1, so a gate keyed on the status cannot call a
branch dirty because a tool is absent.

Verified by `tests/test_branch_scope.py` (46 checks) against throwaway repos, not
against this checkout's branches -- the #264-56 branches have since been rebuilt
and merged, so a test reading real history would rot. It reproduces the #264-56
shape (5 inherited + 3 own, reported 5 of 8), the rebase that fixes it, a
reworded inherited commit, a genuinely-merged parent (correctly *not* a finding),
a stale base (which reports clean, so the pre-comparison fetch is load-bearing),
and the exit-code contract. Signal 2 is driven end to end through `--pr` with a
stubbed `gh`, which is what pins the exclusions above; an earlier version tested
only `_is_ancestor` in isolation, and deleting the signal outright left the suite
green. Each of these mutations now fails it: emptying the `others` loop,
inverting the ancestor test at the call site or inside it, dropping `stacked`
from the failure condition, and disabling the fetch, containment or fork guard.

Examples:
    python scripts/ai/check_branch_scope.py --pr 370       # both signals
    python scripts/ai/check_branch_scope.py                # HEAD vs origin/264
    python scripts/ai/check_branch_scope.py --base origin/main --head my-branch
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

DEFAULT_BASE = "origin/264"


class ToolError(Exception):
    """A git/gh invocation failed -- distinct from a finding about the branch."""


def _run(args, check=True):
    try:
        proc = subprocess.run(args, capture_output=True, text=True)
    except OSError as exc:
        # A missing `git`/`gh` must not exit 1: that is the code reserved for
        # "this branch carries foreign commits", and a gate keyed on exit status
        # would report the branch dirty because a tool is absent.
        raise ToolError(f"could not run {args[0]!r}: {exc}") from exc
    if check and proc.returncode != 0:
        raise ToolError(f"{' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def _subject(sha):
    return _run(["git", "log", "-1", "--format=%s", sha])


def _is_ancestor(ancestor, descendant):
    """True if `ancestor` is reachable from `descendant`.

    Exit status is the answer here (0 yes, 1 no), so this cannot go through _run's
    check=True path, and a non-zero status must not be read as a tool failure.
    """
    try:
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            capture_output=True, text=True)
    except OSError as exc:
        raise ToolError(f"could not run 'git': {exc}") from exc
    return proc.returncode == 0


def _resolves(ref):
    try:
        _run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"])
        return True
    except ToolError:
        return False


def _remote_for(repo):
    """Return the remote whose URL names `repo` (owner/name), else 'origin'.

    This checkout has more than one remote (a fork and the internal mirror), so
    assuming `origin` when `--repo` points elsewhere would compare against a
    different repository and produce a confident wrong answer.
    """
    if not repo:
        return "origin"
    owner, _, name = repo.partition("/")
    if not owner or not name:
        raise ToolError(f"--repo must be owner/name, got {repo!r}")
    for remote in _run(["git", "remote"]).splitlines():
        url = _run(["git", "remote", "get-url", remote.strip()], check=False)
        if not url:
            continue
        # Match `owner/name` as a unit at the end of the URL, not as two
        # independent substrings: `--repo bgaldino/rlm-base` would otherwise match
        # the `rlm-base-dev` remote and compare against a different repository.
        # Both URL shapes end the same way — `.../owner/name` and `:owner/name`.
        tail = url.strip().removesuffix(".git").replace(":", "/")
        if tail.endswith(f"/{owner}/{name}"):
            return remote.strip()
    raise ToolError(
        f"no git remote matches --repo {repo}; add one or pass --base/--head explicitly")


def _gh_json(args):
    return json.loads(_run(["gh"] + args))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Fail a branch carrying commits it does not own.")
    ap.add_argument("--base", help=f"upstream ref to compare against (default {DEFAULT_BASE})")
    ap.add_argument("--head", help="branch/commit to check (default HEAD)")
    ap.add_argument("--pr", type=int, help="resolve base and head from this PR via gh, "
                                          "and also check for stacking on other open PRs")
    ap.add_argument("--repo", help="owner/name for --pr (default: current checkout)")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip the fetch; only safe if the base was just updated")
    args = ap.parse_args(argv)

    try:
        return _check(args, ap)
    except ToolError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


def _check(args, ap):
    # `is not None`: --pr 0 is falsy, and silently taking the manual path for it
    # would skip both the mutual-exclusion error and PR resolution.
    if args.pr is not None and (args.base or args.head):
        ap.error("--pr resolves base and head; do not pass them too")
    if args.repo and args.pr is None:
        ap.error("--repo only applies to --pr")

    remote, pr_number = "origin", args.pr
    others = []

    if pr_number is not None:
        remote = _remote_for(args.repo)
        gh_args = ["pr", "view", str(pr_number), "--json",
                   "baseRefName,headRefName,headRefOid,headRepositoryOwner,isCrossRepository"]
        if args.repo:
            gh_args += ["--repo", args.repo]
        pr = _gh_json(gh_args)
        base, head = f"{remote}/{pr['baseRefName']}", pr["headRefOid"]
        if pr.get("isCrossRepository"):
            raise ToolError(
                f"PR #{pr_number} comes from a fork "
                f"({pr.get('headRepositoryOwner', {}).get('login', '?')}); its head is not in "
                f"this checkout. Fetch it first:\n"
                f"  git fetch {remote} pull/{pr_number}/head:pr-{pr_number}\n"
                f"then re-run with --base {base} --head pr-{pr_number}")
        list_args = ["pr", "list", "--state", "open", "--limit", "200",
                     "--json", "number,headRefName,headRefOid,title,isCrossRepository"]
        if args.repo:
            list_args += ["--repo", args.repo]
        others = [p for p in _gh_json(list_args) if p["number"] != pr_number]
    else:
        base, head = args.base or DEFAULT_BASE, args.head or "HEAD"

    # Fetch before comparing. A base that is behind the remote hides exactly what
    # is being looked for: an inherited commit that has since merged still looks
    # new against a stale copy, so the check would report clean. #264-55's first
    # fix attempt refuted a correct review finding for this reason.
    if not args.no_fetch and "/" in base:
        _run(["git", "fetch", "--quiet", base.split("/", 1)[0]], check=False)

    for ref in (base, head):
        if not _resolves(ref):
            raise ToolError(f"{ref} does not resolve in this checkout")

    own, foreign = [], []
    for line in _run(["git", "cherry", base, head]).splitlines():
        mark, _, sha = line.partition(" ")
        (foreign if mark == "-" else own).append(sha.strip())

    stacked = []
    for other in others:
        if other.get("isCrossRepository"):
            # A fork's head is not in this checkout, and `<remote>/<headRefName>`
            # would silently resolve to *our* branch of that name — so a fork PR on
            # a branch called `264` or `main` would be compared against the wrong
            # commits entirely. Signal 1 still covers this branch.
            continue
        ref = other["headRefOid"] if _resolves(other["headRefOid"]) \
            else f"{remote}/{other['headRefName']}"
        if not _resolves(ref):
            continue  # not fetched — signal 1 still applies
        if _is_ancestor(ref, base):
            # Already contained in the base, so containing it says nothing about
            # this branch. Load-bearing for one case in particular: the release
            # integration PR (`264` -> `main`) has the *base branch itself* as its
            # head, which is an ancestor of every branch that is up to date with
            # base. Without this, opening that PR fails every other branch in the
            # repo, and being *behind* base would read cleaner than being current
            # with it — a gate nobody would keep using.
            continue
        if _is_ancestor(ref, head):
            stacked.append(other)

    label = f"{head[:12] if len(head) == 40 else head} vs {base}"
    total = len(own) + len(foreign)

    for sha in own:
        print(f"  own      {sha[:8]}  {_subject(sha)}")
    for sha in foreign:
        print(f"  FOREIGN  {sha[:8]}  {_subject(sha)}")
    for other in stacked:
        print(f"  STACKED  on open PR #{other['number']} ({other['headRefName']}): "
              f"{other['title']}")

    if not foreign and not stacked:
        # Deliberately states what was *checked*, not that the branch is clean in
        # some absolute sense. Neither signal can see an inherited commit whose
        # upstream counterpart was amended or squash-combined before merging: its
        # content differs, so there is no patch to match, and its PR is closed so
        # it is not in the open list either. Saying "all N are the branch's own"
        # promises more than patch-id can deliver.
        if total:
            print(f"\nclean: {label} — none of the {total} non-merge commit(s) are "
                  "upstream, and no open PR is contained")
        else:
            print(f"clean: {label} — no commits ahead of base")
        return 0

    print()
    if foreign:
        # `git cherry` compares non-merge commits only, so this count is of those.
        print(f"{len(foreign)} of {total} non-merge commit(s) on {label} are already "
              "upstream, so this branch does not own them.")
    if stacked:
        print(f"This branch contains {len(stacked)} other open PR(s) in full. Those commits "
              "have not merged anywhere yet, so they are invisible to the upstream check "
              "above — but they are still not this PR's to carry, and reviewing this diff "
              "means reviewing theirs.")
    print("Its diff will show files belonging to other changes, in whatever state they were "
          "in when they were inherited — merging it can revert review fixes that already "
          "landed.")
    print(f"Rebuild it: branch fresh from {base} and cherry-pick only the commits listed as "
          "`own` above. If the extra commits came from a parent PR that has since merged, a "
          "plain rebase onto the updated base drops them.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
