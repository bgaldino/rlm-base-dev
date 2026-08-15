#!/usr/bin/env python3
"""Fail a branch that carries commits which are already upstream.

A PR branch cut from a *composed* integration branch -- one built by stacking
several in-flight fixes together to test them as a set -- silently inherits
those other fixes. Its diff then shows files it does not own, and worse, it
shows them in whatever **pre-review** state they were in when the composition
was made. Merging it walks back review fixes that already landed.

#264-56 is the concrete case: `fix/264-agents-authoring-bundle` was rebuilt once
to strip five inherited commits, then re-accumulated the same five from a later
rebase onto the stale composition, and was three days from merging a second time
with them. It carried 8 commits where the PR owned 3.

The detector is `git cherry`, whose whole job is patch-id equivalence:

    -  this commit's content is already upstream  -> the branch does not own it
    +  this commit is genuinely new               -> fine

That distinction is exactly right here and is why this is a wrapper rather than
a hand-rolled diff. Two weaker checks were tried first and both fail:

* `git merge-base --is-ancestor` is **not** a detector. Foreign commits are not
  ancestors of the base -- but neither is any legitimate new commit, so it
  cannot separate them. (The 264 plan named this one before it was tested.)
* Matching commit *subjects* against the base works on this case but breaks the
  moment a subject is reworded, and misses a foreign commit whose twin has not
  merged yet.

Verified against the real #264-56 history: with the base as it stood the moment
that PR was about to merge, this flags exactly the five inherited commits and
passes the three it owns; against the rebuilt branch, it passes all three.

Exit status: 0 clean, 1 foreign commits found, 2 usage/git error.

Examples:
    python scripts/ai/check_branch_scope.py                    # HEAD vs origin/264
    python scripts/ai/check_branch_scope.py --base origin/main
    python scripts/ai/check_branch_scope.py --pr 370           # resolve both via gh
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

DEFAULT_BASE = "origin/264"


def _run(args, check=True):
    proc = subprocess.run(args, capture_output=True, text=True)
    if check and proc.returncode != 0:
        sys.stderr.write(f"error: {' '.join(args)}\n{proc.stderr.strip()}\n")
        sys.exit(2)
    return proc.stdout.strip()


def _subject(sha):
    return _run(["git", "log", "-1", "--format=%s", sha])


def _pr_refs(pr, repo):
    """Resolve (base, head) for a PR via gh, as local-resolvable refs."""
    cmd = ["gh", "pr", "view", str(pr), "--json", "baseRefName,headRefName,headRefOid"]
    if repo:
        cmd += ["--repo", repo]
    data = json.loads(_run(cmd))
    # The base is compared as it exists on the remote, not as a stale local copy:
    # a local `264` that is behind will hide inherited commits that have since
    # merged, which is the very thing being looked for.
    return f"origin/{data['baseRefName']}", data["headRefOid"]


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Fail a branch carrying commits whose content is already upstream.")
    ap.add_argument("--base", help=f"upstream ref to compare against (default {DEFAULT_BASE})")
    ap.add_argument("--head", help="branch/commit to check (default HEAD)")
    ap.add_argument("--pr", type=int, help="resolve base and head from this PR via gh")
    ap.add_argument("--repo", help="owner/name for --pr (default: current checkout)")
    ap.add_argument("--fetch", action="store_true",
                    help="git fetch the base's remote first, so the comparison is current")
    args = ap.parse_args(argv)

    if args.pr and (args.base or args.head):
        ap.error("--pr resolves base and head; do not pass them too")

    if args.pr:
        base, head = _pr_refs(args.pr, args.repo)
    else:
        base, head = args.base or DEFAULT_BASE, args.head or "HEAD"

    if args.fetch and "/" in base:
        _run(["git", "fetch", base.split("/", 1)[0]])

    for ref in (base, head):
        _run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])

    own, foreign = [], []
    for line in _run(["git", "cherry", base, head]).splitlines():
        mark, _, sha = line.partition(" ")
        (foreign if mark == "-" else own).append(sha.strip())

    label = f"{head} vs {base}"
    if not own and not foreign:
        print(f"clean: {label} — no commits ahead of base")
        return 0

    for sha in own:
        print(f"  own      {sha[:8]}  {_subject(sha)}")
    for sha in foreign:
        print(f"  FOREIGN  {sha[:8]}  {_subject(sha)}")

    if not foreign:
        print(f"\nclean: {label} — all {len(own)} commit(s) are the branch's own")
        return 0

    print(f"\n{len(foreign)} of {len(own) + len(foreign)} commit(s) on {label} are "
          "already upstream, so this branch does not own them.")
    print("Its diff will show files belonging to other changes, in whatever state "
          "they were in when they were inherited — merging it can revert review "
          "fixes that already landed.")
    print(f"Rebuild it: branch fresh from {base} and cherry-pick only the commits "
          "listed as `own` above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
