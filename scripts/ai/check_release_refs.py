#!/usr/bin/env python3
"""Fail when instructions or tooling name a branch by release number.

Branches are named by role (README → Branch Information): `main` is the current line,
`preview/<n>` the next release before cutover, `release/<n>` an earlier line. There are
three releases a year, so a branch named by number in an instruction or a tool default
goes stale within months. A tool that defaulted to a numbered branch quietly compared
every branch against a retired line after the cutover.

What fails, on any line of a tracked text file (see SUFFIXES and BASENAMES; EXCLUDE is the
exception list):

* `ref`: a release number used as a git ref: `origin/NNN`, `refs/heads/NNN`,
  `--base NNN`, `--head NNN` (any tool's flag: `gh pr create`, `check_branch_scope.py`), for
  any remote this repo has.
* `branch`: a bare backticked release number (`` `NNN` ``) right next to branch wording:
  "branch (`NNN`", "`NNN` branch", "the `NNN` maintenance branch", "merged into `NNN`",
  "commit to `NNN`", "a branch named `NNN`", "`main`, `NNN`", "`NNN` → `main`" (via
  `main`). Only the 12 characters either side count, so a backticked ID prefix or HTTP code
  elsewhere on a line about branches doesn't. Unquoted (or inside a code span), a number
  counts only in a phrase that can't mean anything but a branch: "NNN branch", "branch
  NNN", "from NNN to main", "merged into NNN", "retarget … from NNN", "NNN → main",
  "This branch: Release NNN".
* `code`: a numbered branch in code or a command, where it is spelled without backticks or a
  remote: a branch-taking git command with a bare 3-digit argument (`git checkout NNN`,
  `git push origin NNN`, also inside a range, refspec or revision suffix: `NNN..HEAD`,
  `HEAD...NNN`, `NNN:preview/<n>`, `NNN:README.md`, `+NNN`, `NNN^`, `NNN~2`, `NNN@{1}`, for
  `show`/`rev-parse`/`rev-list`/`merge-base` too; values of count
  flags such as `-n`/`--depth` don't count), or a
  branch-ish setting given a 3-digit value directly or in a list (`DEFAULT_BASE = "NNN"`,
  `base: NNN`, `PROTECTED = ("main", "NNN")`, `branches: [main, NNN]`). A command continued
  with a trailing backslash, or a list or tuple opened on the setting's line and closed lines later,
  is read as one line and reported at its first.

What passes: `release/<n>` and `preview/<n>` by name (that is the pattern), product
release numbers in prose ("a live NNN org", `salesforce_release_active`), paths such as
`docs/salesforce/NNN/`, and
other three-digit values such as ID prefixes or HTTP codes, which aren't backticked next
to a branch word. The one place that maps releases to branches is the README's Branch
Information section, and it does so by role name (`release/<n>`), so it passes too. The
Salesforce Help snapshots under `docs/salesforce/` are captured product text, not
instructions, and are out of scope. A line that must keep a number, such as a record of
what happened at a past commit, can carry the marker `release-ref: allow`.

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
# Every tracked file of these kinds, wherever it lives: a list of directories went stale one
# review round at a time (README, docs/, tests/, root configs, docker/, orgs/, datasets/ ...).
# Metadata XML, Apex and CSV data aren't instructions or tooling and stay out.
SUFFIXES = (".md", ".mdc", ".py", ".yml", ".yaml", ".json", ".sh", ".toml", ".txt", ".robot",
            ".resource")
BASENAMES = ("Dockerfile",)
# Captured Help text, and this checker's own fixtures, which spell numbered branches on purpose.
EXCLUDE = ("docs/salesforce/", "tests/test_check_release_refs.py")
ALLOW = "release-ref: allow"

# Remotes this repo uses, plus whatever `git remote` lists at run time. Only a remote name
# makes `<name>/NNN` a ref; `docs/salesforce/NNN/` and `366/365` are paths and arithmetic.
KNOWN_REMOTES = ("origin", "upstream", "labs", "emu")
BARE = re.compile(r"`\d{3}`")
NEAR = 12
BRANCH_NEAR = re.compile(r"\bbranch(?:es)?\b|\b(?:named|called)\s|"
                         r"\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in)?to\b|"
                         r"`main`|`(?:release|preview)/")
# One word between the number and "branch": "the `NNN` maintenance branch".
BARE_WORD_BRANCH = re.compile(r"`\d{3}`\s+[\w-]+\s+branch(?:es)?\b")
# An unquoted number, in a phrase that can only mean a branch. Kept to whole phrases because
# unquoted release numbers are everywhere in prose ("a live NNN org", "NNN GA").
N = r"(?<![\w./$-])\d{3}(?![\w./-])"
UNQUOTED = re.compile(
    rf"{N}\s+(?:[\w-]+\s+)?branch(?:es)?\b|\bbranch(?:es)?\s+(?:(?:named|called)\s+)?{N}"
    rf"|\bfrom\s+{N}\s+(?:in|on)?to\s+`?(?:main|release/|preview/)"
    rf"|\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in|on)?to\s+{N}"
    rf"|\bretarget\w*\s+(?:[\w#`-]+\s+){{0,4}}?from\s+{N}"
    rf"|{N}\s*(?:→|->)\s*`?main\b|\bmain`?\s*(?:→|->)\s*{N}"
    # A branch labelled with a release: "This branch: Release NNN", "the branch is NNN".
    rf"|\bbranch\b[*:\s]+(?:is\s+|carries\s+)?(?:(?:Salesforce\s+)?Release\s+)?{N}",
    re.IGNORECASE)


# A git verb that names branches, then the rest of that simple command.
GIT_BRANCH_CMD = re.compile(
    r"\bgit\s+(?:(?:-[Cc]\s+\S+|--(?:git-dir|work-tree|namespace|exec-path)(?:[= ]\S+)?|"
    r"--no-pager|--paginate|-[pP]|--bare|--no-replace-objects|--literal-pathspecs|"
    r"--no-optional-locks)\s+)*(?:checkout|switch|push|pull|fetch|merge-base|merge|rebase|"
    r"branch|worktree\s+add|reset|diff|log|cherry|show|rev-parse|rev-list|restore)\b"
    r"([^\n#|;&`]*)")
# Flags whose next token is a count, not a ref.
COUNT_FLAGS = {"-n", "--max-count", "-U", "--unified", "--depth", "--deepen", "--skip"}
# A branch-ish setting: an identifier with a branch word in it (`DEFAULT_BASE`, `base_ref`,
# `targetBranch`, `PROTECTED`), then `=` or `:`, then a release-shaped value: the whole value,
# or an element of a list/tuple/set. Identifiers are split into words, so `keyPrefix` is not a
# `ref`, and one that also names a measurement (`timeout_base`, `max_refs`) is not a branch.
SETTING = re.compile(r"(?<![\w-])([A-Za-z_][\w-]*)[\"']?\s*[:=]\s*")
BRANCH_WORDS = {"base", "branch", "branches", "ref", "refs", "protected", "target", "targets"}
MEASURES = {"timeout", "count", "size", "port", "limit", "max", "min", "len", "length", "num",
            "delay", "retry", "retries", "seconds", "secs", "ms", "width", "height", "depth",
            "price", "amount", "quantity", "qty", "cost", "total", "percent", "score",
            "index", "idx", "version", "rate", "ttl"}
SCALAR = re.compile(r"[\"']?\d{3}[\"']?(?![\w.-])")
ELEMENT = re.compile(r"(?<![\w./-])[\"']?\d{3}[\"']?(?![\w./-])")


def identifier_words(name: str) -> set:
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", name)}


def branch_setting(line: str, first_len: int = 0) -> bool:
    """`first_len`, for a joined logical line, limits the settings read to those on its first
    physical line: the block's own nested keys (a JSON object's fields) aren't its value."""
    for match in SETTING.finditer(line):
        if first_len and match.start() >= first_len:
            break
        words = identifier_words(match.group(1))
        if not words & BRANCH_WORDS or words & MEASURES:
            continue
        value = line[match.end():]
        if SCALAR.match(value):
            return True
        if value and value[0] in "[({":
            close = {"[": "]", "(": ")", "{": "}"}[value[0]]
            inner = value[1:value.find(close) if close in value else None]
            # `{…}` with `key: value` pairs is a mapping (a JSON object), not a set of refs.
            if value[0] == "{" and ":" in inner:
                continue
            if ELEMENT.search(inner):
                return True
    return False


# A revision token's ref parts: split a range (`a..b`, `a...b`) or refspec (`+a:b`), then drop
# a revision suffix (`^`, `~2`, `@{1}`), so `264..HEAD` and `264:preview/266` yield `264`.
REV_SPLIT = re.compile(r"\.\.\.?|:")
REV_SUFFIX = re.compile(r"(?:[\^~]\d*|@\{[^}]*\})+$")


def ref_parts(token: str) -> list:
    token = token.strip("\"'")
    return [REV_SUFFIX.sub("", part.lstrip("+")) for part in REV_SPLIT.split(token)]


def numbered_branch_in_code(line: str, first_len: int = 0) -> bool:
    for match in GIT_BRANCH_CMD.finditer(line):
        tokens = match.group(1).split()
        for i, token in enumerate(tokens):
            if i and tokens[i - 1] in COUNT_FLAGS or token.startswith("-"):
                continue
            if any(re.fullmatch(r"\d{3}", part) for part in ref_parts(token)):
                return True
    return branch_setting(line, first_len)


def near_branch(line: str) -> bool:
    if BARE_WORD_BRANCH.search(line) or UNQUOTED.search(line):
        return True
    for match in BARE.finditer(line):
        window = line[max(0, match.start() - NEAR):match.end() + NEAR]
        if BRANCH_NEAR.search(window):
            return True
    return False


def ref_pattern(remotes) -> re.Pattern:
    names = "|".join(sorted({re.escape(r) for r in remotes}))
    return re.compile(rf"(?<![\w./-])(?:{names})/\d{{3}}\b|refs/heads/\d{{3}}\b"
                      rf"|--(?:base|head)[ =](?:(?:{names})/)?\d{{3}}\b")


def remotes() -> set:
    out = subprocess.run(["git", "-C", str(REPO), "remote"], capture_output=True, text=True)
    return set(KNOWN_REMOTES) | set(out.stdout.split())


# A setting whose list, tuple or set opens on this line and doesn't close on it.
OPEN_SETTING = re.compile(r"[:=]\s*([\[({])")
CLOSER = {"[": "]", "(": ")", "{": "}"}
LOGICAL_MAX = 50


def logical_line(lines: list, i: int) -> str:
    """Line i joined with what continues it: trailing-backslash lines, then the rest of a list
    or tuple opened at the end of a setting. Code rules read this; prose rules read the line."""
    joined, j = lines[i], i
    while joined.rstrip().endswith("\\") and j + 1 < len(lines) and j - i < LOGICAL_MAX:
        j += 1
        joined = joined.rstrip()[:-1] + " " + lines[j].strip()
    opened = OPEN_SETTING.search(joined)
    close = CLOSER[opened.group(1)] if opened else None
    if opened and close not in joined[opened.end(1):].split("#")[0]:
        while j + 1 < len(lines) and j - i < LOGICAL_MAX:
            j += 1
            joined += " " + lines[j].strip()
            if close in lines[j]:
                break
    return joined


def findings(text: str, ref: re.Pattern):
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if ALLOW in line:
            continue
        if ref.search(line):
            yield number, "ref", line.strip()
        elif near_branch(line):
            yield number, "branch", line.strip()
        elif numbered_branch_in_code(logical_line(lines, number - 1), len(line)):
            yield number, "code", line.strip()


def tracked_scope() -> list[Path]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git ls-files failed")
    return [REPO / name for name in out.stdout.split("\0")
            if name and (name.endswith(SUFFIXES) or name.rsplit("/", 1)[-1] in BASENAMES)
            and not name.startswith(EXCLUDE) and not (REPO / name).is_symlink()]


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
