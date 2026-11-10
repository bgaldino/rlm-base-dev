#!/usr/bin/env python3
"""Keep the private artifacts tree private, and keep public citations into it shaped right.

`.agents/artifacts/` is a separate PRIVATE repository that this one gitignores
(`.cursor/rules/analysis-artifacts.mdc`). Tracked files may cite paths inside it, but a fresh
clone and CI never have the tree, so citations can rot unseen: of 16 paths cited in Nov 2026,
13 no longer resolved, and the manifest audit (which walks one section) saw one of them.

Three checks, in order:

(a) Leak guard — GATING. No tracked path may start with `.agents/artifacts` (sibling backups such
    as `.agents/artifacts.old/` included, which `.gitignore` does not cover) or contain
    `-core-code-`.
(b) Shape. Every `.agents/artifacts/<x>` literal in tracked text must be the bare directory, a
    template or glob, or start with a private tier (PRIVATE_TIERS). A top-level-shaped citation
    is a warning until SHAPE_GATING is switched on, once the citations are rewritten (todo 358,
    PR-B).
(c) Resolution, only when the private clone is present. Each concrete citation must exist, or
    resolve through the private tree's MOVED.tsv. Warnings for now, like (b). With the clone
    absent, the count of shape-checked citations is printed: never a silent skip.

`tests/` is not scanned for (b)/(c): fixtures there cite misplaced paths on purpose.

Exit 0 when (a) passes (and, once gating, (b)); 1 otherwise. Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = ".agents/artifacts"

# First path segment a citation into the private tree may start with. The private repository's
# README and tools/check_layout.py are authoritative for its layout; this is the public subset.
PRIVATE_TIERS = ("todos", "topics", "archive", "memory", "reports", "inbox", "todo-audit", "tools")

SHAPE_GATING = False  # todo 358 PR-B turns this on after rewriting the citations below it

# Files whose citations are deliberate examples of a wrong path, with the reason.
EXEMPT = {
    ".cursor/rules/analysis-artifacts.mdc": "shows a top-level path as the ❌ example",
}

LITERAL = re.compile(r"\.agents/artifacts(?![\w.-])(/[^\s`'\"()\[\]<>|,;]*)?")


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def classify(rel: str) -> str:
    """'bare', 'template', 'tier' or 'top-level' for a path that may start with `.agents/artifacts`."""
    rest = rel[len(ROOT):] if rel.startswith(ROOT) else rel
    rest = rest.strip("/").rstrip(".:")
    if not rest:
        return "bare"
    if any(c in rest for c in "{}*$<>"):
        return "template"
    return "tier" if rest.split("/", 1)[0] in PRIVATE_TIERS else "top-level"


def moved_rows(tree: Path) -> list[tuple[str, str]]:
    path = tree / "MOVED.tsv"
    rows = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
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
        if (tree / cur).exists():
            return cur
    return None


def citations(paths: list[str]):
    """(file, line number, literal) for every private-tree literal outside tests/ and EXEMPT."""
    for rel in paths:
        if rel.startswith("tests/") or rel in EXEMPT:
            continue
        full = REPO / rel
        try:
            if full.is_symlink() or not full.is_file() or full.stat().st_size > 2_000_000:
                continue
            text = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if ROOT not in text:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in LITERAL.finditer(line):
                yield rel, n, m.group(0).rstrip(".:")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="print problems and the summary only")
    ap.parse_args(argv)
    paths = tracked()
    errors: list[str] = []
    warnings: list[str] = []

    for p in paths:  # (a)
        if p.startswith(ROOT) or "-core-code-" in p:
            errors.append(f"{p}: private content is tracked in the public repo; remove it "
                          f"(git rm --cached) and keep it in the private tree")

    tree = REPO / ROOT
    present = tree.is_dir()
    rows = moved_rows(tree) if present else []
    shaped = 0
    for rel, n, lit in citations(paths):  # (b) and (c)
        kind = classify(lit)
        if kind in ("bare", "template"):
            continue
        shaped += 1
        rest = lit[len(ROOT):].strip("/")
        if kind == "top-level":
            msg = (f"{rel}:{n}: {lit} cites the private tree's top level; cite a path under "
                   f"{', '.join(PRIVATE_TIERS[:4])}, …")
            (errors if SHAPE_GATING else warnings).append(msg)
        if present and not (tree / rest).exists():
            new = resolve_moved(tree, rest, rows)
            if new:
                warnings.append(f"{rel}:{n}: {lit} moved; rewrite to {ROOT}/{new}")
            else:
                warnings.append(f"{rel}:{n}: {lit} does not exist in the private tree "
                                f"(python {ROOT}/tools/where.py {rest})")

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
