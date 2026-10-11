#!/usr/bin/env python3
"""Fail when instructions or tooling name a branch by release number.

Branches are named by role (README → Branch Information): `main` is the current line,
`preview/<n>` the next release before cutover, `release/<n>` an earlier line. There are
three releases a year, so a branch named by number in an instruction or a tool default
goes stale within months. A tool that defaulted to a numbered branch quietly compared
every branch against a retired line after the cutover.

What fails, on any line of any tracked text file (is_text; EXCLUDE is the exception list):

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
  with a trailing backslash, a list, tuple or set opened on the setting's line and closed lines
  later, or a YAML block sequence (`branches:` then `- NNN`) is read as one line and reported at
  its first.

What passes: `release/<n>` and `preview/<n>` by name (that is the pattern), product
release numbers in prose ("a live NNN org", `salesforce_release_active`), paths such as
`docs/salesforce/NNN/`, and
other three-digit values such as ID prefixes or HTTP codes, which aren't backticked next
to a branch word. The one place that maps releases to branches is the README's Branch
Information section, and it does so by role name (`release/<n>`), so it passes too. The
captured Help, dev-guide and release-note corpora under `docs/salesforce/<n>/` are
Salesforce's text, not instructions, and are out of scope (CAPTURED); the release-root files
beside them are scanned. A line that must keep a number, such as a record of
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
# Every tracked text file, wherever it lives and whatever it is called: a list of directories,
# then of suffixes, went stale one review round at a time (README, docs/, tests/, root
# configs, docker/, launchers, .html, .js ...). Text means UTF-8 with no NUL byte in the
# first 8 KB (is_text); anything else is binary and skipped.
TEXT_PROBE = 8192
# Captured Help text, and this checker's own fixtures, which spell numbered branches on purpose.
# Captured Help, dev-guide and release-note corpora are Salesforce's text, not ours; the
# release-root files beside them (feature-index.md, notes) are maintained here and scanned.
CAPTURED = re.compile(r"^docs/salesforce/[^/]+/(?:help|dev-guide|dev-guide-industries|"
                      r"release-notes)/")
EXCLUDE = ("tests/test_check_release_refs.py",)  # this checker's own fixtures
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
    rf"|{N}\s*(?:→|->)\s*`?(?:main\b|preview/|release/)"
    rf"|(?:\bmain|\b(?:preview|release)/[\w.<>-]+)`?\s*(?:→|->)\s*{N}"
    # A release mapped onto a role branch: "NNN is now on `main`", "`main` now carries
    # Release NNN". README → Branch Information is the one place that does this, by marker.
    rf"|\b(?:Release\s+)?{N}\b[^.\n]{{0,40}}?\b(?:is\s+)?(?:now\s+)?on\s+`(?:main|preview/|release/)"
    rf"|`(?:main|preview/[^`]*|release/[^`]*)`\s+(?:now\s+)?(?:carries|holds|tracks|is)\s+"
    rf"(?:the\s+)?(?:Salesforce\s+)?Release\s+{N}"
    # A branch labelled with a release: "This branch: Release NNN", "the branch is NNN".
    rf"|\bbranch\b[*:\s]+(?:is\s+|carries\s+)?(?:(?:Salesforce\s+)?Release\s+)?{N}",
    re.IGNORECASE)


# Any git subcommand, then the rest of that simple command. Not an allowlist of verbs: a list
# went stale one review round at a time (clone, format-patch, archive, blame, tag, config).
# A bare three-digit argument is a ref unless an option's name says it's a measure.
GIT_BRANCH_CMD = re.compile(
    # Global options before the subcommand: the ones that take a separate value, then any
    # other long option (`--no-pager`, `--config-env=k=v`, ...) rather than a list of them.
    r"\bgit\s+(?:(?:-[Cc]\s+\S+|--(?:git-dir|work-tree|namespace|exec-path|config-env)\s+\S+|"
    r"--[\w-]+(?:=\S+)?|-[pP])\s+)*([a-z][\w-]*)\b([^\n#|;&`]*)")
# Short flags whose next token is a count, not a ref. Long flags are judged by their words.
COUNT_FLAGS = {"-n", "-U", "-L"}
# Words in a long option that make its value a ref (`--branch=`, `--onto`, `--set-upstream-to`).
REF_FLAG_WORDS = {"branch", "base", "head", "ref", "onto", "into", "upstream", "target", "to",
                  "from"}
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
CALL = re.compile(r"[A-Za-z_][\w.]*\((.*)\)")
QUOTED_NUMBER = re.compile(r"[\"']\d{3}[\"']")
SCALAR = re.compile(r"[\"']?\d{3}[\"']?(?![\w.-])")
ELEMENT = re.compile(r"(?<![\w./-])[\"']?\d{3}[\"']?(?![\w./-])")


def identifier_words(name: str) -> set:
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", name)}


def branch_setting(line: str, first_len: int = 0, long_line: bool = False) -> bool:
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
        # A default wrapped in a call: `DEFAULT_BASE = os.getenv("BASE", "NNN")`. Only a quoted
        # literal counts, so `limit(300)`-style arguments stay numbers.
        call = None if long_line else CALL.match(value)
        if call and QUOTED_NUMBER.search(call.group(1)):
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


def measure_flag(flag: str) -> bool:
    """A flag whose value is a number: a short count flag, or a long one whose name has a
    measurement word and no ref word (`--max-count`, `--stat-width`, `--depth`, `--prune`)."""
    if flag in COUNT_FLAGS:
        return True
    if not flag.startswith("--"):
        return False
    words = set(flag.lstrip("-").lower().split("-"))
    return bool(words & (MEASURES | {"prune", "deepen", "skip", "unified", "abbrev", "context"})) \
        and not words & REF_FLAG_WORDS


def numbered_branch_in_code(line: str, first_len: int = 0, long_line: bool = False) -> bool:
    for match in GIT_BRANCH_CMD.finditer(line):
        verb, tokens = match.group(1), match.group(2).split()
        if verb == "config":
            # `git config branch.<b>.gh-merge-base NNN`: a ref only under a branch-ish key.
            key = next((t for t in tokens if not t.startswith("-")), "")
            words = {w for w in re.split(r"[.\-_]", key.lower()) if w}
            if not words & (BRANCH_WORDS | {"merge", "remote"}) or words & MEASURES:
                continue
            tokens = tokens[tokens.index(key) + 1:] if key else []
        for i, token in enumerate(tokens):
            if i and measure_flag(tokens[i - 1]):
                continue
            if re.fullmatch(r"-[bBcC][\"']?\d{3}[\"']?", token):
                return True  # `clone -b264`, `checkout -B264`, `switch -c264`: attached value
            if token.startswith("-"):
                # `--branch=NNN` is a ref; `--stat-width=NNN` is a measure.
                flag, _, token = token.partition("=")
                if not token or measure_flag(flag) or flag.startswith("--") and not \
                        set(flag.lstrip("-").lower().split("-")) & REF_FLAG_WORDS:
                    continue
            if any(re.fullmatch(r"\d{3}", part) for part in ref_parts(token)):
                return True
    if shell_default(line):
        return True
    return branch_setting(line, first_len, long_line)


# A CLI option declared with a numbered default: `add_argument("--base", default="NNN")`,
# `click.option("--head", default="NNN")`. Read over the whole call, which often wraps.
OPTION_CALL = re.compile(r"\b(?:add_argument|option)\(")
OPTION_DEFAULT = re.compile(r"[\"'](--?[\w-]+)[\"'][^)]*?\bdefault\s*=\s*"
                            # a literal, or a call holding a quoted one (`os.getenv("B", "NNN")`)
                            r"(?:[\"']?\d{3}[\"']?(?![\w.])|[\w.]+\([^)]*?[\"']\d{3}[\"'])")


def option_default(lines: list, i: int) -> bool:
    if not OPTION_CALL.search(lines[i]):
        return False
    call, depth = "", 0
    for line in lines[i:i + LOGICAL_MAX]:
        call += " " + line.strip()
        depth += line.count("(") - line.count(")")
        if depth <= 0:
            break
    for match in OPTION_DEFAULT.finditer(call):
        words = set(match.group(1).lstrip("-").lower().split("-"))
        if words & REF_FLAG_WORDS and not words & MEASURES:
            return True
    return False


# A shell parameter default for a branch-named variable: `${BASE_BRANCH:-NNN}`.
SHELL_DEFAULT = re.compile(r"\$\{([A-Za-z_]\w*):?[-=]\s*[\"']?\d{3}[\"']?\}")


def shell_default(line: str) -> bool:
    for match in SHELL_DEFAULT.finditer(line):
        words = identifier_words(match.group(1))
        if words & BRANCH_WORDS and not words & MEASURES:
            return True
    return False


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
                      rf"|--(?:base|head)(?:=|\s+)[\"']?(?:[\w.-]+:)?(?:(?:{names})/)?\d{{3}}\b"
                      # gh's short aliases, only after `gh pr` (`grep -B 100` is context).
                      rf"|\bgh\s+pr\s+[^\n|;&]*?\s-[BH](?:=|\s*)[\"']?(?:[\w.-]+:)?\d{{3}}\b")


def remotes() -> set:
    out = subprocess.run(["git", "-C", str(REPO), "remote"], capture_output=True, text=True)
    return set(KNOWN_REMOTES) | set(out.stdout.split())


# A setting whose list, tuple or set opens on this line and doesn't close on it.
OPEN_SETTING = re.compile(r"[:=]\s*([\[({])")
CLOSER = {"[": "]", "(": ")", "{": "}"}
LOGICAL_MAX = 50


# A YAML key with no inline value (`branches:`), whose value is the block sequence below it.
YAML_KEY = re.compile(r"^(\s*)(?:-\s+)?[\"']?[A-Za-z_][\w-]*[\"']?\s*:\s*(?:#.*)?$")
YAML_ITEM = re.compile(r"^(\s*)-\s+(.*?)\s*(?:#.*)?$")


def yaml_block(lines: list, i: int):
    """`key:` then `- item` lines (indented deeper, or at the key's own indent, which YAML
    allows for a sequence) as one flow line, `key: [item, item]`. None if not that shape."""
    key = YAML_KEY.match(lines[i])
    if not key:
        return None
    indent, items = len(key.group(1)), []
    for line in lines[i + 1:i + 1 + LOGICAL_MAX]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = YAML_ITEM.match(line)
        if not item or len(item.group(1)) < indent:
            break
        if ALLOW not in line:  # the marker exempts the item it's on
            items.append(item.group(2))
    return f"{lines[i].split('#')[0].rstrip()} [{', '.join(items)}]" if items else None


def logical_line(lines: list, i: int) -> str:
    """Line i joined with what continues it: trailing-backslash lines, then the rest of a list
    or tuple opened at the end of a setting, or a YAML block sequence under a bare key. Code
    rules read this; prose rules read the line."""
    block = yaml_block(lines, i)
    if block:
        return block
    joined, j = lines[i], i
    while joined.rstrip().endswith("\\") and j + 1 < len(lines) and j - i < LOGICAL_MAX:
        j += 1
        joined = joined.rstrip()[:-1] + " " + allowed_out(lines[j])
    opened = OPEN_SETTING.search(joined)
    close = CLOSER[opened.group(1)] if opened else None
    if opened and close not in joined[opened.end(1):].split("#")[0]:
        while j + 1 < len(lines) and j - i < LOGICAL_MAX:
            j += 1
            joined += " " + allowed_out(lines[j])
            if close in lines[j]:
                break
    return joined


def allowed_out(line: str) -> str:
    """A joined continuation line, or nothing if it carries the allow marker, so the marker
    works on the line that keeps the number rather than only on the block's opener."""
    return "" if ALLOW in line else line.strip()


# Every rule needs a three-digit run, on the line or, for a block, on a later line its opener
# joins. These two let the scan skip the rest: it reads every tracked text file, ~10 MB.
DIGITS = re.compile(r"\d{3}")
# Longer than any hand-written line: minified or generated code (vendored static resources),
# where a call-wrapped quoted number is noise, not a branch someone wrote. Only that heuristic
# is switched off on such a line; exact refs and direct settings are still checked.
MAX_LINE = 2000
OPENER = re.compile(r"\\\s*$|[:=]\s*[\[({]|:\s*(?:#.*)?$|\b(?:add_argument|option)\(")


def findings(text: str, ref: re.Pattern):
    if not DIGITS.search(text):
        return
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        has_number = DIGITS.search(line)
        if not has_number and not OPENER.search(line) or ALLOW in line:
            continue
        if has_number and ref.search(line):
            yield number, "ref", line.strip()
        elif line.rstrip().endswith("\\") and ref.search(logical_line(lines, number - 1)):
            yield number, "ref", line.strip()
        elif has_number and near_branch(line):
            yield number, "branch", line.strip()
        elif numbered_branch_in_code(logical_line(lines, number - 1), len(line),
                                     len(line) > MAX_LINE) or option_default(lines, number - 1):
            yield number, "code", line.strip()


def tracked_scope() -> list[Path]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git ls-files failed")
    return [REPO / name for name in out.stdout.split("\0")
            if name and not name.startswith(EXCLUDE) and not CAPTURED.match(name)
            and not (REPO / name).is_symlink()
            and is_text(REPO / name)]


def is_text(path: Path) -> bool:
    if not path.is_file():
        return False
    with open(path, "rb") as handle:
        head = handle.read(TEXT_PROBE)
    if b"\0" in head:
        return False
    try:
        head.decode("utf-8")
    except UnicodeDecodeError as exc:
        # A multi-byte character cut at the probe boundary is still text.
        return exc.start >= len(head) - 3
    return True


def main(argv: list[str]) -> int:
    try:
        paths = [Path(a).resolve() for a in argv] if argv else tracked_scope()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    total, ref = 0, ref_pattern(remotes())
    for path in paths:
        try:
            # Classified as text by its head; a stray invalid byte further in isn't a tool error.
            text = path.read_text(encoding="utf-8", errors="replace")
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
