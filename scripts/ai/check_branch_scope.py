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

2. **Shares history with another open PR beyond the base** -- if this head and
   another open PR's head join at a commit the base does not have, that shared
   part is unmerged work belonging to some other PR, and so is invisible to
   signal 1. Found the hard way: while writing this check, the branch for its own
   companion fix was cut from the check's branch, and signal 1 reported clean.
   Needs `--pr`, since it is the PR list that says which branches are in flight.

   Not simple ancestry, which was the first version: that only catches a parent
   which has not *moved* since the branch was cut. Cut at the parent's B, let the
   parent advance to C, and C is no longer an ancestor even though B is still
   inherited and still unmerged -- and `git cherry` cannot see B either, since it
   is not upstream, so both signals reported clean on the shape signal 2 exists for.

   **A shared join is symmetric, so it cannot by itself say who inherited from
   whom**, and four exclusions keep the signal from reporting the wrong branch.
   Every one was a false positive before it was a guard:

   - **Contained in the base.** The release integration PR (`264` -> `main`) has
     the base branch itself as its head, so without this every branch merely *up
     to date* with base was reported -- and being behind base read cleaner than
     being current with it.
   - **A fork's head.** Not in this checkout, and the `<remote>/<branch>` fallback
     would resolve a fork PR on a branch named `264` or `main` to *our* branch of
     that name.
   - **A PR that targets this branch.** That is the declaration of a child stack:
     they are building on us. GitHub records it in `baseRefName`, which is worth
     using precisely because history cannot distinguish it -- a child cut from our
     B while we advanced to C produces the identical graph to a parent we cut from
     at B, and without this the *parent* was told to rebuild over its own work.
   - **A descendant of this head.** The unmoved form of the same case.

   Where none of those apply and the histories have merely diverged, direction is
   genuinely not derivable, and both the output and the remedy say so rather than
   asserting inheritance. Signal 1 still covers every skipped branch.

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

Verified by `tests/test_branch_scope.py` (74 checks) against throwaway repos, not
against this checkout's branches -- the #264-56 branches have since been rebuilt
and merged, so a test reading real history would rot. It reproduces the #264-56
shape (5 inherited + 3 own, reported 5 of 8), the rebase that fixes it, a
reworded inherited commit, a genuinely-merged parent (correctly *not* a finding),
a stale base (which reports clean, so the pre-comparison fetch is load-bearing),
a *failing* fetch (which must exit 2 rather than compare the stale ref it just
failed to refresh -- a guard that fails open is decoration), and the exit-code
contract. Signal 2 is driven end to end through `--pr` with a
stubbed `gh`, which is what pins the exclusions above; an earlier version tested
only `_is_ancestor` in isolation, and deleting the signal outright left the suite
green. Each of these mutations now fails it: emptying the `others` loop,
inverting the ancestor test at the call site or inside it, dropping `stacked`
from the failure condition, disabling the containment or fork guard, and either
removing the fetch or letting it fail silently.

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

    Exit status is the answer here, so this cannot go through _run's check=True
    path. But only 0 and 1 are answers -- anything else (128 for an unknown
    object, say) is git failing, and reading that as "not an ancestor" would let a
    broken invocation *suppress* a STACKED finding and return a clean 0. That
    inverts the tool's contract: errors are exit 2, never a verdict.
    """
    try:
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            capture_output=True, text=True)
    except OSError as exc:
        raise ToolError(f"could not run 'git': {exc}") from exc
    if proc.returncode not in (0, 1):
        raise ToolError(
            f"git merge-base --is-ancestor {ancestor} {descendant} exited "
            f"{proc.returncode}\n{proc.stderr.strip()}")
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
    others, pr = [], None

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
        list_args = ["pr", "list", "--state", "open", "--limit", "200", "--json",
                     "number,baseRefName,headRefName,headRefOid,title,isCrossRepository"]
        if args.repo:
            list_args += ["--repo", args.repo]
        others = [p for p in _gh_json(list_args) if p["number"] != pr_number]
    else:
        base, head = args.base or DEFAULT_BASE, args.head or "HEAD"

    # Fetch before comparing. A base that is behind the remote hides exactly what
    # is being looked for: an inherited commit that has since merged still looks
    # new against a stale copy, so the check would report clean. #264-55's first
    # fix attempt refuted a correct review finding for this reason.
    #
    # Fail closed. This fetch is the guard, so swallowing its exit status would
    # reinstate the very false negative it exists to prevent: offline, or with a
    # dead credential, the comparison would silently run against whatever the
    # remote-tracking ref last happened to hold and could report clean. A failure
    # here is a tool error (exit 2), never a verdict about the branch. Skipping is
    # available, but only by asking for it with --no-fetch.
    if not args.no_fetch and "/" in base:
        candidate = base.split("/", 1)[0]
        # A slash does not prove a remote: `--base release/262` is a local branch
        # whose first segment is not a remote, and fetching 'release' would fail
        # for a reason that says nothing about staleness.
        if candidate in _run(["git", "remote"]).split():
            try:
                _run(["git", "fetch", "--quiet", candidate])
            except ToolError as exc:
                raise ToolError(
                    f"could not fetch {candidate!r}, so {base} may be stale and this "
                    f"check cannot be trusted:\n{exc}\n"
                    f"Fix the remote, or pass --no-fetch to compare against the local "
                    f"copy knowingly.") from exc

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
        if other.get("baseRefName") and pr and other["baseRefName"] == pr["headRefName"]:
            # They target *this* branch, which is how a child stack is declared. Use
            # the declaration, because the history cannot be read for direction: a
            # child cut from our B while we advanced to C is graph-identical to a
            # parent we cut from at B. Without this the parent PR fails its own gate
            # the moment it takes a review fix after a child was cut from it — and
            # `AGENTS.md` says PRs are routinely stacked here, so that is the common
            # shape, not a corner. Signal 1 still covers their branch.
            continue
        # Not "is the other head an ancestor of mine" -- that only catches a parent
        # which has not moved since the branch was cut. Cut at the parent's commit B,
        # let the parent advance to C, and C is no longer an ancestor even though B
        # is still inherited and still unmerged; `git cherry` cannot see B either,
        # because it is not upstream. Both signals would report clean.
        #
        # Ask instead where the two histories join. If they share anything the base
        # does not, that shared part is unmerged work belonging to another PR -- and
        # it subsumes the unmoved-parent case (there the join *is* the other head).
        #
        # `--all`, because criss-crossed history has more than one merge base and
        # plain `merge-base` returns an arbitrary one: if that one happens to be
        # inside base and another does not, the finding disappears. check=False
        # because unrelated histories exit 1 with no output, which is an answer
        # ("nothing shared"), not a failure -- and treating it as one turned a
        # single open PR with orphan history into a hard exit 2 for every branch.
        bases = [b for b in _run(["git", "merge-base", "--all", ref, head],
                                 check=False).split() if b]
        outside = [b for b in bases if not _is_ancestor(b, base)]
        if not outside:
            continue
        join = outside[0]
        # merge-base is symmetric, and that cuts the wrong way for a *child*: if
        # another PR was cut from this one, the join is this branch's own head, and
        # reporting it would tell the parent to rebuild over work it authored. The
        # containment tests below are what recover direction from a symmetric join.
        if _is_ancestor(head, ref):
            continue  # the other PR is downstream of us; their problem, not ours
        stacked.append((other, join, _is_ancestor(ref, head)))

    label = f"{head[:12] if len(head) == 40 else head} vs {base}"
    total = len(own) + len(foreign)

    for sha in own:
        print(f"  own      {sha[:8]}  {_subject(sha)}")
    for sha in foreign:
        print(f"  FOREIGN  {sha[:8]}  {_subject(sha)}")
    for other, join, contained in stacked:
        # "in full" is a containment fact; the diverged case is deliberately not
        # phrased as inheritance, because a symmetric join cannot establish who took
        # what from whom -- only that the two share commits the base does not have.
        shares = "in full" if contained else f"from {join[:8]} on (shared, direction " \
            "not determinable from history alone)"
        print(f"  STACKED  on open PR #{other['number']} ({other['headRefName']}) "
              f"{shares}: {other['title']}")

    if not foreign and not stacked:
        # Deliberately states what was *checked*, not that the branch is clean in
        # some absolute sense. Neither signal can see an inherited commit whose
        # upstream counterpart was amended or squash-combined before merging: its
        # content differs, so there is no patch to match, and its PR is closed so
        # it is not in the open list either. Saying "all N are the branch's own"
        # promises more than patch-id can deliver.
        if total:
            print(f"\nclean: {label} — none of the {total} non-merge commit(s) are "
                  "upstream, and no open PR shares history beyond base")
        else:
            print(f"clean: {label} — no commits ahead of base")
        return 0

    print()
    if foreign:
        # `git cherry` compares non-merge commits only, so this count is of those.
        print(f"{len(foreign)} of {total} non-merge commit(s) on {label} are already "
              "upstream, so this branch does not own them.")
    contains = [s for s in stacked if s[2]]
    diverged = [s for s in stacked if not s[2]]
    if contains:
        print(f"This branch contains {len(contains)} other open PR(s) in full. Those commits "
              f"have not merged anywhere yet, so they are invisible to the upstream check "
              "above — but they are still not this PR's to carry, and reviewing this diff "
              "means reviewing theirs.")
    if diverged:
        # Deliberately not phrased as a finding against this branch, and given no
        # remedy. The join is symmetric and the child-stack declaration has already
        # been excluded, so what is left cannot be attributed from history: telling a
        # branch to rebuild over commits that may be its own is how a gate earns a
        # reputation for crying wolf, which is worse than not having it.
        print(f"This branch shares commits with {len(diverged)} other open PR(s) that "
              f"{base} does not have, joining where each line above says. Direction is not "
              "derivable from the history — if those commits are yours and the other PR was "
              "cut from this one, there is nothing to fix here; check its base branch.")
    if foreign or contains:
        print("Its diff will show files belonging to other changes, in whatever state they "
              "were in when they were inherited — merging it can revert review fixes that "
              "already landed.")
        print(f"Rebuild it: branch fresh from {base} and cherry-pick only the commits listed "
              "as `own` above. If the extra commits came from a parent PR that has since "
              "merged, a plain rebase onto the updated base drops them.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
