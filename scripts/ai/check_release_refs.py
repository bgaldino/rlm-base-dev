#!/usr/bin/env python3
"""Flag instructions and tool defaults that name a branch by release number.

Branches are named by role (README → Branch Information): `main` is the current line,
`preview/<n>` the next release before cutover, `release/<n>` an earlier line, and work happens
on `feat/*`, `fix/*`, `chore/*`, `docs/*`. A bare numbered branch such as `264` is what goes
stale: there are three releases a year, and a tool that defaulted to one quietly compared every
branch against a retired line after the cutover.

This is a best-effort lint for the mistakes people actually make. Enforcement is on the
server: a branch ruleset blocks creating a branch whose whole name is three digits, so a
stale reference fails loudly instead of resolving. The lint doesn't try to parse every git,
shell or language spelling; see "Not covered" below.

What fails, on any line of any tracked text file:

* `ref`: a numbered branch spelled as a ref: `<remote>/NNN` (any remote this clone has, or
  origin/upstream/labs/emu), `refs/heads/NNN`, `refs/remotes/<remote>/NNN`, `--base NNN`,
  `--head NNN` (with `=` or a space, optionally quoted or remote-qualified).
* `git`: a branch-taking git command with a bare number as an argument:
  `git checkout NNN`, `git switch NNN`, `git push origin NNN`, `git merge NNN`,
  `git diff NNN..HEAD`, `git log main..NNN`, `git worktree add <path> NNN`. Values of count,
  search and date flags (`-n 100`, `--depth 100`, `--grep 404`) and quoted messages with a
  space in them (`-m "fix 264 build"`) don't count.
* `setting`: a branch-named setting given a numbered value, directly or in a one-line list:
  `DEFAULT_BASE = "NNN"`, `base: NNN`, `PROTECTED = ("main", "NNN")`,
  `branches: [main, NNN]`, or a YAML block list under such a key (`branches:` then
  `- NNN`). A name is branch-named when it contains base, branch, head, ref, target or
  protected, and no measurement word (`timeout_base`, `head_count`).
* `prose`: a number next to branch wording, backticked, quoted or bare:
  "the `NNN` branch", "branch NNN", "merged into `NNN`", "from NNN to main", "NNN → main".

A number counts only as a whole branch name. `264-dev`, `264.x`, `release/264`,
`preview/266`, `feat/264-fix` and `archive/264` (the tags retired branches were archived as)
all pass. So do product release numbers in prose ("a live 264 org",
`salesforce_release_active`), paths (`docs/salesforce/264/`), ID prefixes and HTTP codes.

README → Branch Information is the one place that maps releases to branches; its mapping line
carries the marker `release-ref: allow`. Any line that must keep a number, such as a dated
history entry, can carry the same marker. It exempts that line only.

Not covered, by design (the server ruleset is the backstop): shell parameter expansion,
command substitution and aliases; git global options and per-subcommand option arity; argv
lists in code; multi-line expressions other than YAML block lists; and prose wrapped across
lines. The Salesforce Help, dev-guide and release-note corpora under `docs/salesforce/<n>/`
are captured text, not instructions, and aren't scanned (maintainers' `*.notes.md` there are).

Usage:
    python scripts/ai/check_release_refs.py            # scan every tracked text file
    python scripts/ai/check_release_refs.py FILE...    # scan these files only

Exit codes: 0 = clean · 1 = findings · 2 = tool error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOW = "release-ref: allow"
EXCLUDE = frozenset({"tests/test_check_release_refs.py"})  # exact paths: its own fixtures
CAPTURED = re.compile(r"^docs/salesforce/[^/]+/(?:help|dev-guide|dev-guide-industries|"
                      r"release-notes)/")
TEXT_PROBE = 8192
KNOWN_REMOTES = ("origin", "upstream", "labs", "emu")
# Never remote names here: a remote called `release` must not make `release/NNN` a ref.
ROLE_PREFIXES = {"release", "preview", "feat", "fix", "chore", "docs", "archive"}

# A three-digit number that is a whole branch name: not followed by a name character, `-`,
# `/`, or a `.` that continues the name (`264.x`); a sentence's full stop still ends it.
NUM_END = r"\d{3}(?![\w/-]|\.\w)"
NUM = rf"(?<![\w./$-]){NUM_END}"
QUOTE = r"[`\"']?"
QNUM = rf"{QUOTE}{NUM}{QUOTE}"


def ref_pattern(remotes) -> re.Pattern:
    names = "|".join(sorted(re.escape(r) for r in set(remotes) - ROLE_PREFIXES))
    return re.compile(rf"(?<![\w./-])(?:{names})/{NUM_END}"
                      rf"|(?<![\w./-])refs/(?:heads|remotes/[\w.-]+)/{NUM_END}"
                      rf"|--(?:base|head)(?:=|\s+){QUOTE}(?:(?:{names})/)?{NUM_END}")


GIT_VERBS = ("checkout", "switch", "push", "pull", "fetch", "merge", "rebase", "branch",
             "reset", "diff", "log", "show", "rev-parse", "merge-base", "cherry-pick", "tag",
             "worktree", "rev-list", "format-patch")
GIT = re.compile(rf"(?<![\w.-])git\s+(?:{'|'.join(GIT_VERBS)})\b([^\n|;&#`]*)")
# Flags whose next token is a value, not a revision: counts, and the search and date filters.
VALUE_FLAGS = {"-n", "--max-count", "-U", "--unified", "--depth", "--deepen", "--skip", "-m",
               "--message", "--grep", "--author", "--committer", "--since", "--until", "-S",
               "-G"}
SENTENCE_END = re.compile(r"[,;!?)]+$|(?<!\.)\.$")
# A quoted string with a space in it is a message or a pattern, never a branch name.
QUOTED_PHRASE = re.compile(r"\"[^\"]*\s[^\"]*\"|'[^']*\s[^']*'")

# `:=`, `::=` and `:::=` are Make's immediate assignments; `!=` is left out (a comparison).
SETTING = re.compile(r"(?<![\w-])([A-Za-z_][\w-]*)[\"']?\s*(?::{1,3}=|[?+]?=(?!=)|:)\s*")
BRANCH_WORDS = {"base", "bases", "branch", "branches", "head", "heads", "ref", "refs",
                "target", "targets", "protected"}
MEASURES = {"timeout", "count", "size", "port", "limit", "max", "min", "len", "length", "num",
            "delay", "retries", "seconds", "ms", "width", "height", "depth", "index",
            "version", "rate", "ttl", "price", "amount", "total", "percent"}
# The number must be the whole value (`base: NNN`), not the start of one (`Target: NNN ms`).
SCALAR = re.compile(rf"{QUOTE}\d{{3}}{QUOTE}(?=\s*(?:[,;)\]}}#]|\.(?!\w)|$))")
# A whole list element: bounded by the brackets, a comma or a space.
ELEMENT = re.compile(rf"(?:^|[\s,])({QUOTE})\d{{3}}\1(?=\s*(?:,|$))")
YAML_KEY = re.compile(r"^(\s*)(?:-\s+)?[\"']?([A-Za-z_][\w-]*)[\"']?\s*:\s*(?:#.*)?$")
YAML_ITEM = re.compile(r"^(\s*)-\s+(.*?)\s*(?:#.*)?$")

PROSE = re.compile(
    rf"{QUOTE}{NUM}{QUOTE}\s+branch(?:es)?\b"
    rf"|(?P<q>[`\"']){NUM}(?P=q)\s+(?:[\w-]+\s+){{1,2}}branch(?:es)?\b"
    rf"|\bbranch(?:es)?\s+(?:(?:named|called)\s+)?{QNUM}"
    rf"|\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in|on)?to\s+{QNUM}"
    rf"|\b(?:merg(?:e|ed|ing)|rebas(?:e|ed|ing))\s+{QNUM}\s+(?:in|on)?to\b"
    rf"|\bfrom\s+{QNUM}\s+(?:in|on)?to\s+`?(?:main|release/|preview/)"
    rf"|{QNUM}\s*(?:→|->)\s*`?main\b|\bmain`?\s*(?:→|->)\s*{QNUM}",
    re.IGNORECASE)


def words(name: str) -> set:
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", name)}


def branch_named(name: str) -> bool:
    found = words(name)
    return bool(found & BRANCH_WORDS) and not found & MEASURES


def numbered_setting(line: str) -> bool:
    for match in SETTING.finditer(line):
        if not branch_named(match.group(1)):
            continue
        value = line[match.end():]
        if SCALAR.match(value.rstrip()):
            return True
        if value and value[0] in "[(":
            close = "]" if value[0] == "[" else ")"
            if close in value and any(ELEMENT.fullmatch(" " + item.strip())
                                      for item in value[1:value.index(close)].split(",")):
                return True
    return False


def numbered_git(line: str) -> bool:
    for match in GIT.finditer(line):
        tokens = QUOTED_PHRASE.sub(" ", match.group(1)).split()
        for i, token in enumerate(tokens):
            if token == "--":
                break  # everything after it is a path
            if i and tokens[i - 1] in VALUE_FLAGS:
                continue
            # Sentence punctuation isn't part of the name (`git checkout NNN.`). A range
            # (`a..b`) or refspec (`a:b`) names each side; `^`/`~N` suffixes don't change it.
            token = SENTENCE_END.sub("", token).strip("\"'")
            for part in re.split(r"\.\.\.?|:", token.lstrip("+^")):
                if re.fullmatch(r"\d{3}", re.sub(r"[\^~]\d*$", "", part)):
                    return True
    return False


def yaml_items_under(lines: list, i: int):
    """Line numbers of `- NNN` items in the block list under a branch-named key (`branches:`)."""
    head = lines[i].split("#")[0].rstrip()
    key = YAML_KEY.match(head)
    if not key or not branch_named(key.group(2)):
        return
    # The list belongs to the key's own column, which for `- branches:` is past the dash: a
    # sibling item at the dash's indent has left the block.
    column = key.start(2) - (head[key.start(2) - 1] in "\"'")
    direct = None  # the first item's indent; deeper lines belong to an item, not the list
    for j in range(i + 1, len(lines)):
        line = lines[j]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        item = YAML_ITEM.match(line)
        if direct is None:
            if not item or indent < column:
                return
            direct = indent
        if indent > direct:
            continue
        if not item or indent < direct:
            return
        if ALLOW not in line and SCALAR.fullmatch(item.group(2)):
            yield j + 1


# Every rule needs a three-digit run, and every prose form a branch-ish word; checking for
# them first keeps the scan of every tracked text file to a few seconds.
DIGITS = re.compile(r"\d{3}")
PROSE_KEY = re.compile(r"branch|merge|push|commit|rebase|from|main|→|->", re.IGNORECASE)


def findings(text: str, ref: re.Pattern):
    if not DIGITS.search(text):
        return
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        # A YAML block list puts the number on a later line; report the item, not the key. A
        # marker on the key doesn't cover its items.
        for item in yaml_items_under(lines, number - 1):
            yield item, "setting", lines[item - 1].strip()
        if ALLOW in line or not DIGITS.search(line):
            continue
        if ref.search(line):
            yield number, "ref", line.strip()
        elif numbered_git(line):
            yield number, "git", line.strip()
        elif numbered_setting(line):
            yield number, "setting", line.strip()
        elif PROSE_KEY.search(line) and PROSE.search(line):
            yield number, "prose", line.strip()


def remotes() -> set:
    out = subprocess.run(["git", "-C", str(REPO), "remote"], capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git remote failed")
    return set(KNOWN_REMOTES) | set(out.stdout.split())


def in_scope_name(name: str) -> bool:
    return name not in EXCLUDE and (not CAPTURED.match(name) or name.endswith(".notes.md"))


def is_text(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    with open(path, "rb") as handle:
        head = handle.read(TEXT_PROBE)
    if b"\0" in head:
        return False
    try:
        head.decode("utf-8")
    except UnicodeDecodeError as exc:
        return exc.start >= len(head) - 3  # a multi-byte character cut at the probe boundary
    return True


def tracked_scope() -> list:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git ls-files failed")
    return [REPO / name for name in out.stdout.split("\0")
            if name and in_scope_name(name) and is_text(REPO / name)]


def main(argv: list) -> int:
    try:
        paths = [Path(a).resolve() for a in argv] if argv else tracked_scope()
        ref = ref_pattern(remotes())
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    total = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
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
