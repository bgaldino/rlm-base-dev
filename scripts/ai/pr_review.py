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
current checkout (``gh repo view``, else the ``origin`` remote URL); override with
``--repo owner/name`` to run against any repo.

Thread state and resolution use GraphQL. Where GraphQL is refused (Claude Code
cloud sessions proxy REST only), both fall back to the REST ``ccr`` routes:
``GET pulls/{n}/ccr/review_threads`` and ``POST pulls/{n}/ccr/comments/{id}/resolve``.

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


def _repo_from_origin():
    """owner/name from the `origin` remote URL, or "" if it can't be read."""
    res = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True
    )
    url = res.stdout.strip().removesuffix(".git") if res.returncode == 0 else ""
    parts = url.replace(":", "/").rstrip("/").split("/")
    return f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 and all(parts[-2:]) else ""


def resolve_repo(repo):
    if not repo:
        # `gh repo view` is GraphQL-backed, so fall back to the remote URL.
        repo = _run(
            ["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            check=False,
        ).stdout.strip() or _repo_from_origin()
        if not repo:
            raise SystemExit("Could not determine repo; pass --repo owner/name")
    parts = repo.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise SystemExit(f"--repo must be in owner/name format, got: {repo!r}")
    return repo


def _graphql_blocked(res):
    """True when GraphQL itself is refused (not a query error about the PR)."""
    text = f"{res.stdout}\n{res.stderr}".lower()
    return res.returncode != 0 and "graphql" in text and "403" in text


def _rest_list(path):
    """Every item of a paginated REST list, paged by `page=N`.

    Not `gh api --paginate`: GitHub's `next` links use `repositories/{id}/...`
    paths, which the same proxy that refuses GraphQL also refuses.
    """
    items, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        batch = _json(["api", f"{path}{sep}per_page=100&page={page}"]) or []
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def _fetch_threads_rest(repo, pr):
    """Review threads via the REST ccr route, shaped like the GraphQL nodes.

    That route carries no thread node id, author or body -- only each thread's
    comment ids -- so the first comment is looked up in the PR's review comments.
    `id` is None, which tells `cmd_handle` to resolve through REST as well.
    """
    # The ccr route returns every thread in one response (no Link header).
    threads = _json(["api", f"repos/{repo}/pulls/{pr}/ccr/review_threads"]) or []
    by_id = {c["id"]: c for c in _rest_list(f"repos/{repo}/pulls/{pr}/comments")}
    nodes = []
    for t in threads:
        ids = t.get("comment_ids") or []
        c = by_id.get(ids[0], {}) if ids else {}
        first = {
            "databaseId": ids[0] if ids else None,
            "author": {"login": (c.get("user") or {}).get("login", "?")},
            "path": c.get("path") or t.get("path"),
            "line": c.get("line") or t.get("line"),
            "originalLine": c.get("original_line"),
            "body": c.get("body", ""),
        }
        nodes.append({
            "id": None,
            "isResolved": bool(t.get("resolved")),
            "isOutdated": bool(t.get("outdated")),
            "comments": {"nodes": [first] if ids else []},
        })
    return nodes


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
        if _graphql_blocked(res):
            return _fetch_threads_rest(repo, pr)
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


def cmd_status(repo, pr, show_all, repo_arg=None):
    threads = fetch_threads(repo, pr)
    unresolved = [t for t in threads if not t["isResolved"]]
    shown = threads if show_all else unresolved
    # Carry an explicit --repo through to the copy/paste `handle` suggestion so it
    # targets the same repo, not the current checkout. (--repo is a top-level arg,
    # so it must precede the subcommand.)
    repo_flag = f"--repo {repo_arg} " if repo_arg else ""
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
                f"  → resolve: python scripts/ai/pr_review.py {repo_flag}handle {pr} "
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
    # 2. 👍 the original comment (GA reactions header). Non-fatal: a failed
    #    reaction must NOT abort the all-important resolve step below — that
    #    would leave the half-finished state (reply posted, thread open) this
    #    tool exists to prevent. Warn and continue.
    if react:
        res = _run([
            "api", "--method", "POST",
            f"repos/{owner}/{name}/pulls/comments/{comment_id}/reactions",
            "-H", "Accept: application/vnd.github+json", "-f", "content=+1",
        ], check=False)
        if res.returncode == 0:
            print("  ✓ 👍 reaction added")
        else:
            detail = (res.stderr or res.stdout or "").strip()
            print(f"  ⚠ 👍 reaction failed (continuing to resolve): {detail[:200]}")
    # 3. Resolve the thread (GraphQL, or the REST ccr route where GraphQL is
    #    refused). Match the thread whose first comment is the cited (original)
    #    review comment.
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
    if target["id"] is None:  # REST fallback: resolve by comment id, then confirm
        _run([
            "api", "--method", "POST",
            f"repos/{owner}/{name}/pulls/{pr}/ccr/comments/{comment_id}/resolve",
        ])
        ok = any(
            t["isResolved"] for t in fetch_threads(repo, pr)
            if _first(t).get("databaseId") == int(comment_id)
        )
        print("  ✓ thread resolved" if ok else "  ⚠ resolve did not take; check the thread")
        return 0 if ok else 1
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
    h.add_argument(
        "--comment", required=True, type=int,
        help="original review comment databaseId",
    )
    h.add_argument("--body", help="reply body (resolution + commit SHA, or refutation)")
    h.add_argument("--body-file", help="read reply body from a file ('-' for stdin)")
    h.add_argument("--no-react", action="store_true", help="skip the 👍 reaction")

    a = p.parse_args()
    repo = resolve_repo(a.repo)

    if a.cmd == "status":
        sys.exit(cmd_status(repo, a.pr, a.all, a.repo))
    if a.cmd == "verify":
        sys.exit(cmd_verify(repo, a.pr))
    if a.cmd == "handle":
        body = a.body
        if a.body_file:
            if a.body_file == "-":
                body = sys.stdin.read()
            else:
                with open(a.body_file, encoding="utf-8") as fh:
                    body = fh.read()
        if not body or not body.strip():
            raise SystemExit("handle requires --body or --body-file")
        sys.exit(cmd_handle(repo, a.pr, a.comment, body, react=not a.no_react))


if __name__ == "__main__":
    main()
