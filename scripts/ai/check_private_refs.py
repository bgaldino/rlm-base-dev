#!/usr/bin/env python3
"""Keep public citations into the private artifacts tree shaped right, and resolvable.

`.agents/artifacts/` is a separate PRIVATE repository that this one gitignores
(`.cursor/rules/analysis-artifacts.mdc`). Tracked files may cite paths inside it, but a fresh
clone and CI never have the tree, so citations can rot unseen: of 16 paths cited in Nov 2026,
13 no longer resolved, and the manifest audit (which walks one section) saw one of them.

Keeping the tree itself out of commits is `.gitignore`'s job, and the always-run
`dockerignore` check fails a tracked file it ignores. Two checks here:

(a) Shape. Every `.agents/artifacts/<x>` literal in tracked text must be the bare directory, a
    template or glob, or start with a private tier (PRIVATE_TIERS). A top-level-shaped citation
    is a warning until SHAPE_GATING is switched on, once the citations are rewritten (todo 358,
    PR-B).
(b) Resolution, only when the private clone is present. Each concrete citation must exist, or
    resolve through the private tree's MOVED.tsv. Warnings for now, like (a). With the clone
    absent, the count of shape-checked citations is printed: never a silent skip.

`tests/` is not scanned: fixtures there cite misplaced paths on purpose.

Exit 0 unless (a) is gating and fails (1); 2 when the check cannot run (git fails), so a tool
error never reads as a verdict. Stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = ".agents/artifacts"

# First path segment a citation into the private tree may start with: its tiers, then the root
# files its top level also allows. The private repository's README and tools/check_layout.py are
# authoritative; tests/test_check_private_refs.py keeps this equal to the guard hook's
# ARTIFACTS_ROOT, the other public copy.
PRIVATE_TIERS = ("todos", "topics", "archive", "memory", "reports", "inbox", "todo-audit", "tools",
                 "README.md", "MOVED.tsv", ".gitignore", ".ignore", ".githooks")

SHAPE_GATING = False  # todo 358 PR-B turns this on after rewriting the citations below it

PLACEHOLDER = re.compile(r"\{[^}]*\}|\$\{?\w+\}?|\*+")

# Files whose citations are deliberate examples of a wrong path, with the reason.
EXEMPT = {
    ".cursor/rules/analysis-artifacts.mdc": "shows a top-level path as the ❌ example",
}

# A path ends at whitespace, quoting or bracketing punctuation (typographic dashes and quotes
# included), or a URL anchor/query. A `*` stays in it: a glob is a template, not a path.
LITERAL = re.compile(r"\.agents/artifacts(?![\w.-])(/[^\s`'\"()\[\]<>|,;#?\u2013\u2014\u2018\u2019\u201c\u201d\u2026]*)?")
# What follows a path in prose but is not part of it: a `:12`, `:12:3` or `:12-20` location,
# then sentence punctuation or `_italics_`.
TRAILER = re.compile(r"(?::\d+(?:-\d+)?){0,2}[.:_]*$")
# Closing emphasis (`**path**`): trailing stars, unless they end a glob segment (`x/**`, `x-*`).
EMPHASIS = re.compile(r"(?<![/*-])\*+$")


def citing() -> list[str]:
    """Tracked text files that mention the private tree, found by one native `git grep` pass
    rather than by reading every tracked file. Exit 1 means no match; anything else raises.
    --no-color: with `color.ui=always` configured, file names come back wrapped in escape
    codes, match no tracked file, and every citation would be skipped."""
    proc = subprocess.run(["git", "grep", "--no-color", "-lIzF", ROOT], cwd=REPO,
                          capture_output=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip() or "git grep failed")
    return [p for p in proc.stdout.decode("utf-8", "replace").split("\0") if p]


def classify(rel: str) -> str:
    """'bare', 'template', 'tier' or 'top-level' for a citation, which starts with `.agents/artifacts`."""
    rest = rel[len(ROOT):].strip("/")
    if not rest:
        return "bare"
    first = rest.split("/", 1)[0]
    if first in PRIVATE_TIERS:
        return "tier"
    # Only a first segment that IS a placeholder (`{tier}`, `$DIR`, `**`) makes a template; a
    # concrete top-level name with a placeholder inside it (`x-{release}.md`) is still a
    # top-level citation.
    return "template" if PLACEHOLDER.fullmatch(first) else "top-level"


def clone_present(tree: Path) -> bool:
    """Whether `tree` is the private clone: a directory with a `.git` of its own, as the guard
    hook (rule 4) has it. A plain folder there is a stand-in, not the private tree."""
    return tree.is_dir() and os.path.exists(tree / ".git")


def exists_in(tree: Path, rest: str) -> bool:
    """Whether `rest` exists under `tree`; os.path.exists() answers False rather than raising
    for a path the OS rejects (a name past NAME_MAX, a NUL), which a citation in prose can be."""
    return os.path.exists(tree / rest)


def moved_rows(tree: Path) -> list[tuple[str, str]]:
    """MOVED.tsv's (old prefix, new prefix) rows, longest first; none if it cannot be read.
    errors="replace": a stray non-UTF-8 byte spoils that row's match, not the whole run."""
    try:
        text = (tree / "MOVED.tsv").read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return []
    rows = []
    for line in text.splitlines():
        cols = line.split("\t")
        if len(cols) == 4 and not line.startswith(("#", "old_prefix\t")):
            rows.append((cols[0].rstrip("/"), cols[1].rstrip("/")))
    return sorted(rows, key=lambda r: -len(r[0]))


def resolve_moved(tree: Path, rest: str, rows: list[tuple[str, str]] | None = None) -> str | None:
    """Where a missing path inside the private tree moved to, by MOVED.tsv prefix rows."""
    rows = moved_rows(tree) if rows is None else rows
    cur = rest.strip("/")
    for _ in range(10):
        hit = next(((o, n) for o, n in rows if cur == o or cur.startswith(o + "/")), None)
        if not hit:
            return None
        cur = hit[1] + cur[len(hit[0]):]
        if exists_in(tree, cur):
            return cur
    return None


def citations(paths: list[str]):
    """(file, line number, literal) for every private-tree literal outside tests/ and EXEMPT."""
    for rel in paths:
        if rel.startswith("tests/") or rel in EXEMPT:
            continue
        full = REPO / rel
        try:
            if full.is_symlink() or not full.is_file():
                continue
            # Bytes, decoded with errors="replace": git grep -I already judged it text, one
            # stray byte must not hide every citation, and no newline translation may move a
            # line number off git's (read_text() would turn a lone \r into a line break).
            text = full.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        # split("\n"), not splitlines(): splitlines() also breaks at \r, \f, \v, \x1c-\x1e,
        # \x85 and U+2028/9.
        for n, line in enumerate(text.split("\n"), 1):
            for m in LITERAL.finditer(line):
                lit = TRAILER.sub("", m.group(0))
                yield rel, n, TRAILER.sub("", EMPHASIS.sub("", lit))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    try:
        return _check()
    except (subprocess.CalledProcessError, RuntimeError, OSError) as exc:
        print(f"check_private_refs: cannot run: {exc}", file=sys.stderr)
        return 2


def _check() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    tree = REPO / ROOT
    present = clone_present(tree)
    rows = moved_rows(tree) if present else []
    shaped = 0
    for rel, n, lit in citations(citing()):  # (a) and (b)
        kind = classify(lit)
        if kind in ("bare", "template"):
            continue
        shaped += 1
        rest = lit[len(ROOT):].strip("/")
        if kind == "top-level":
            msg = (f"{rel}:{n}: {lit} cites the private tree's top level; cite a path under "
                   f"{', '.join(PRIVATE_TIERS[:4])}, …")
            (errors if SHAPE_GATING else warnings).append(msg)
        if present and not PLACEHOLDER.search(rest) and not exists_in(tree, rest):
            new = resolve_moved(tree, rest, rows)
            if new:
                warnings.append(f"{rel}:{n}: {lit} moved; rewrite to {ROOT}/{new}")
            else:
                warnings.append(f"{rel}:{n}: {lit} is not at that path and MOVED.tsv has no "
                                f"row for it; find it with python {ROOT}/tools/where.py {rest}")

    for w in warnings:
        print(f"  [WARN ] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    where = ("resolved against the private tree" if present
             else "shape-checked, not resolved (private tree absent)")
    print(f"check_private_refs: {shaped} citation(s) {where}; "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
