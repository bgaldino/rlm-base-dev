#!/usr/bin/env python3
"""Fail when instructions or tooling name a branch by release number.

Branches are named by role (README → Branch Information): `main` is the current line,
`preview/<n>` the next release before cutover, `release/<n>` an earlier line. There are
three releases a year, so a branch named by number in an instruction or a tool default
goes stale within months. A tool that defaulted to a numbered branch quietly compared
every branch against a retired line after the cutover.

What fails, on any line of a tracked instruction or tooling file:

* `ref`: a release number used as a git ref: `origin/NNN`, `refs/heads/NNN`,
  `--base NNN`, for any remote this repo has.
* `branch`: a bare backticked release number (`` `NNN` ``) right next to branch wording:
  "branch (`NNN`", "`NNN` branch", "merged into `NNN`", "commit to `NNN`", "a branch named
  `NNN`", "`main`, `NNN`", "`NNN` → `main`" (via `main`). Only the 12 characters either
  side count, so a backticked ID prefix or HTTP code elsewhere on a line about branches
  doesn't.

What passes: `release/<n>` and `preview/<n>` by name (that is the pattern), product
release numbers in prose ("a live NNN org", `salesforce_release_active`), paths such as
`docs/salesforce/NNN/`, and
other three-digit values such as ID prefixes or HTTP codes, which aren't backticked next
to a branch word. The one place that maps releases to branches is the README's Branch
Information section, which is out of scope. A line that must keep a number, such as a
record of what happened at a past commit, can carry the marker `release-ref: allow`.

Usage:
    python scripts/ai/check_release_refs.py            # scan the tracked scope
    python scripts/ai/check_release_refs.py FILE...    # scan these files only

Exit codes: 0 = clean · 1 = findings · 2 = tool error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCOPE = ("AGENTS.md", "CONTRIBUTING.md", "REVIEW.md", ".agents/", ".claude/", ".cursor/",
         ".github/", "scripts/", "tasks/", "docs/guides/", "docs/references/")
SUFFIXES = (".md", ".mdc", ".py", ".yml", ".yaml", ".json", ".sh", ".toml", ".txt")
ALLOW = "release-ref: allow"

# Remotes this repo uses, plus whatever `git remote` lists at run time. Only a remote name
# makes `<name>/NNN` a ref; `docs/salesforce/NNN/` and `366/365` are paths and arithmetic.
KNOWN_REMOTES = ("origin", "upstream", "labs", "emu")
BARE = re.compile(r"`\d{3}`")
NEAR = 12
BRANCH_NEAR = re.compile(r"\bbranch(?:es)?\b|\b(?:named|called)\s|"
                         r"\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in)?to\b|"
                         r"`main`|`(?:release|preview)/")


def near_branch(line: str) -> bool:
    for match in BARE.finditer(line):
        window = line[max(0, match.start() - NEAR):match.end() + NEAR]
        if BRANCH_NEAR.search(window):
            return True
    return False


def ref_pattern(remotes) -> re.Pattern:
    names = "|".join(sorted({re.escape(r) for r in remotes}))
    return re.compile(rf"(?<![\w./-])(?:{names})/\d{{3}}\b|refs/heads/\d{{3}}\b"
                      rf"|--base[ =](?:(?:{names})/)?\d{{3}}\b")


def remotes() -> set:
    out = subprocess.run(["git", "-C", str(REPO), "remote"], capture_output=True, text=True)
    return set(KNOWN_REMOTES) | set(out.stdout.split())


def findings(text: str, ref: re.Pattern):
    for number, line in enumerate(text.splitlines(), 1):
        if ALLOW in line:
            continue
        if ref.search(line):
            yield number, "ref", line.strip()
        elif near_branch(line):
            yield number, "branch", line.strip()


def tracked_scope() -> list[Path]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "--", *SCOPE],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git ls-files failed")
    return [REPO / name for name in out.stdout.split("\0")
            if name.endswith(SUFFIXES) and not (REPO / name).is_symlink()]


def main(argv: list[str]) -> int:
    try:
        paths = [Path(a).resolve() for a in argv] if argv else tracked_scope()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    total, ref = 0, ref_pattern(remotes())
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        for number, rule, line in findings(text, ref):
            total += 1
            rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            print(f"{rel}:{number}: [{rule}] {line[:160]}")
    print(f"\n{len(paths)} files scanned, {total} release-numbered branch reference(s).")
    if total:
        print("Name branches by role instead: main, preview/<n>, release/<n>, or 'the PR's "
              "base'. See README → Branch Information.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
