#!/usr/bin/env python3
"""Automate the repo's automated-PR-review protocol.

Implements the *mechanical* half of the "Responding to Automated PR Reviews"
policy in AGENTS.md so review rounds reliably end with **zero unresolved
threads**:

* ``status``  — list review threads (unresolved by default), paginated, with the
  comment id, location, and body needed to act on each.
* ``handle``  — reply in-thread + 👍 + resolve a single thread, in one call
  (👍 by default; pass ``--no-react`` to refute a false positive without it).
* ``verify``  — confirm 0 unresolved across all pages (exit 1 if any remain).

The *judgment* half stays with the agent: verify each finding against the code,
classify it real / partial / false-positive, and sweep the whole class before
resolving (see AGENTS.md and .cursor/skills/audit-review/SKILL.md).

Tool-agnostic: shells out to the authenticated ``gh`` CLI. Repo defaults to the
current checkout (``gh repo view``); override with ``--repo owner/name`` to run
against any repo.

Examples:
    python scripts/ai/pr_review.py status 212
    python scripts/ai/pr_review.py handle 212 --comment 3369933169 \\
        --body "Fixed in abc1234 — guarded the empty case."
    python scripts/ai/pr_review.py verify 212
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

THREADS_QUERY = """query($owner:String!,$name:String!,$pr:Int!,$cursor:String){
  repository(owner:$owner,name:$name){
    pullRequest(number:$pr){
      reviewThreads(first:100, after:$cursor){
        pageInfo{ hasNextPage endCursor }
        nodes{
          id isResolved isOutdated
          comments(first:1){ nodes{ databaseId author{login} path line originalLine body } }
        }
      }
    }
  }
}"""

RESOLVE_MUTATION = (
    "mutation($tid:ID!){ resolveReviewThread(input:{threadId:$tid})"
    "{ thread{ isResolved } } }"
)


def _run(args, check=True, input_text=None):
    res = subprocess.run(
        ["gh", *args], capture_output=True, text=True, input=input_text
    )
    if check and res.returncode != 0:
        sys.stderr.write(res.stdout)
        sys.stderr.write(res.stderr)
        raise SystemExit(f"`gh {' '.join(args)}` failed (exit {res.returncode})")
    return res


def _json(args, input_text=None):
    out = _run(args, input_text=input_text).stdout.strip()
    return json.loads(out) if out else None


def resolve_repo(repo):
    if repo:
        return repo
    out = _run(
        ["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
    ).stdout.strip()
    if not out:
        raise SystemExit("Could not determine repo; pass --repo owner/name")
    return out


def fetch_threads(repo, pr):
    """Return all review-thread nodes for the PR, following pagination."""
    owner, name = repo.split("/", 1)
    cursor, nodes = None, []
    while True:
        args = [
            "api", "graphql",
            "-f", f"query={THREADS_QUERY}",
            "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"pr={pr}",
        ]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        res = _run(args, check=False)
        try:
            data = json.loads(res.stdout) if res.stdout.strip() else {}
        except json.JSONDecodeError:
            data = {}
        if data.get("errors"):
            msgs = "; ".join(e.get("message", str(e)) for e in data["errors"])
            raise SystemExit(f"GraphQL error for PR #{pr} in {repo}: {msgs}")
        pr_node = ((data.get("data") or {}).get("repository") or {}).get("pullRequest")
        if pr_node is None:  # bad repo/auth/network, or PR missing with no errors block
            detail = res.stderr.strip() or res.stdout.strip() or "unknown error"
            raise SystemExit(f"Could not read PR #{pr} in {repo}: {detail}")
        rt = pr_node["reviewThreads"]
        nodes.extend(rt["nodes"])
        if rt["pageInfo"]["hasNextPage"]:
            cursor = rt["pageInfo"]["endCursor"]
        else:
            return nodes


def _first(thread):
    nodes = thread.get("comments", {}).get("nodes", [])
    return nodes[0] if nodes else {}


def _loc(comment):
    line = comment.get("line") or comment.get("originalLine") or "?"
    return f"{comment.get('path', '?')}:{line}"


def cmd_status(repo, pr, show_all):
    threads = fetch_threads(repo, pr)
    unresolved = [t for t in threads if not t["isResolved"]]
    shown = threads if show_all else unresolved
    print(f"PR #{pr} ({repo}): {len(threads)} thread(s), {len(unresolved)} unresolved")
    if not shown:
        print("  ✅ nothing to handle" if not show_all else "  (no threads)")
        return 0
    for t in shown:
        c = _first(t)
        state = "RESOLVED" if t["isResolved"] else "OPEN"
        author = (c.get("author") or {}).get("login", "?")
        body = " ".join((c.get("body") or "").split())
        snippet = (body[:160] + "…") if len(body) > 160 else body
        print(f"\n[{state}] {author} — {_loc(c)}  (comment id {c.get('databaseId')})")
        print(f"  {snippet}")
        if not t["isResolved"]:
            print(
                f"  → resolve: python scripts/ai/pr_review.py handle {pr} "
                f"--comment {c.get('databaseId')} --body \"<fix + commit SHA>\""
            )
            print("             (👍 added by default; add --no-react to refute a false positive)")
    return 0


def cmd_verify(repo, pr):
    threads = fetch_threads(repo, pr)
    unresolved = [t for t in threads if not t["isResolved"]]
    print(f"PR #{pr} ({repo}): {len(threads)} thread(s), {len(unresolved)} unresolved")
    if unresolved:
        for t in unresolved:
            c = _first(t)
            author = (c.get("author") or {}).get("login", "?")
            print(f"  OPEN: {author} — {_loc(c)} (comment id {c.get('databaseId')})")
        print("❌ NOT clean — unresolved threads remain")
        return 1
    print("✅ 0 unresolved")
    return 0


def cmd_handle(repo, pr, comment_id, body, react):
    owner, name = repo.split("/", 1)
    # 1. Reply in-thread (resolution + commit SHA, or an evidence-backed refutation).
    _run([
        "api", "--method", "POST",
        f"repos/{owner}/{name}/pulls/{pr}/comments/{comment_id}/replies",
        "-f", f"body={body}",
    ])
    print(f"  ✓ replied in-thread on comment {comment_id}")
    # 2. 👍 the original comment (GA reactions header).
    if react:
        _run([
            "api", "--method", "POST",
            f"repos/{owner}/{name}/pulls/comments/{comment_id}/reactions",
            "-H", "Accept: application/vnd.github+json", "-f", "content=+1",
        ])
        print("  ✓ 👍 reaction added")
    # 3. Resolve the thread (REST can't — GraphQL). Match the thread whose first
    #    comment is the cited (original) review comment.
    target = next(
        (t for t in fetch_threads(repo, pr)
         if _first(t).get("databaseId") == int(comment_id)),
        None,
    )
    if target is None:
        print(
            f"  ⚠ no thread found whose first comment is {comment_id} "
            "(a reply id, or wrong PR?). Reply/react done; resolve manually."
        )
        return 1
    if target["isResolved"]:
        print("  ✓ thread already resolved")
        return 0
    data = _json([
        "api", "graphql",
        "-f", f"query={RESOLVE_MUTATION}", "-f", f"tid={target['id']}",
    ])
    ok = data["data"]["resolveReviewThread"]["thread"]["isResolved"]
    print("  ✓ thread resolved" if ok else "  ⚠ resolve returned isResolved=false")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(
        description="Automate the repo's automated-PR-review protocol (see AGENTS.md)."
    )
    p.add_argument("--repo", help="owner/name (default: current repo via gh)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="list review threads (unresolved by default)")
    s.add_argument("pr", type=int)
    s.add_argument("--all", action="store_true", help="include resolved threads")

    v = sub.add_parser("verify", help="confirm 0 unresolved (exit 1 if any remain)")
    v.add_argument("pr", type=int)

    h = sub.add_parser("handle", help="reply + 👍 + resolve one thread")
    h.add_argument("pr", type=int)
    h.add_argument("--comment", required=True, help="original review comment databaseId")
    h.add_argument("--body", help="reply body (resolution + commit SHA, or refutation)")
    h.add_argument("--body-file", help="read reply body from a file ('-' for stdin)")
    h.add_argument("--no-react", action="store_true", help="skip the 👍 reaction")

    a = p.parse_args()
    repo = resolve_repo(a.repo)

    if a.cmd == "status":
        sys.exit(cmd_status(repo, a.pr, a.all))
    if a.cmd == "verify":
        sys.exit(cmd_verify(repo, a.pr))
    if a.cmd == "handle":
        body = a.body
        if a.body_file:
            body = sys.stdin.read() if a.body_file == "-" else open(
                a.body_file, encoding="utf-8"
            ).read()
        if not body or not body.strip():
            raise SystemExit("handle requires --body or --body-file")
        sys.exit(cmd_handle(repo, a.pr, a.comment, body, react=not a.no_react))


if __name__ == "__main__":
    main()
