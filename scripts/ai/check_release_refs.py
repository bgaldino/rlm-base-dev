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
Information section; its one line mapping `main` to a release carries the allow marker. The
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
import shlex
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
EXCLUDE = frozenset({"tests/test_check_release_refs.py"})  # exact paths: its own fixtures
ALLOW = "release-ref: allow"

# Remotes this repo uses, plus whatever `git remote` lists at run time. Only a remote name
# makes `<name>/NNN` a ref; `docs/salesforce/NNN/` and `366/365` are paths and arithmetic.
KNOWN_REMOTES = ("origin", "upstream", "labs", "emu")
BARE = re.compile(r"`\d{3}`|\"\d{3}\"|'\d{3}'")  # backticked or quoted
NEAR = 12
BRANCH_NEAR = re.compile(r"\bbranch(?:es)?\b|\b(?:named|called)\s|"
                         r"\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in)?to\b|"
                         r"`main`|`(?:release|preview)/")
# One word between the number and "branch": "the `NNN` maintenance branch".
BARE_WORD_BRANCH = re.compile(r"[`\"']\d{3}[`\"']\s+(?:[\w-]+\s+){0,2}branch(?:es)?\b")
# An unquoted number, in a phrase that can only mean a branch. Kept to whole phrases because
# unquoted release numbers are everywhere in prose ("a live NNN org", "NNN GA").
N = r"(?<![\w./$-])\d{3}(?![\w./-])"
Q = r"[`\"']?"  # an optional backtick or quote around the number
UNQUOTED = re.compile(
    rf"{N}\s+(?:[\w-]+\s+){{0,2}}branch(?:es)?\b|\bbranch(?:es)?\s+(?:(?:named|called)\s+)?{N}"
    # In these, the number may also be backticked or quoted (`from \`NNN\` to main`).
    rf"|\bfrom\s+{Q}{N}{Q}\s+(?:in|on)?to\s+`?(?:main|release/|preview/)"
    rf"|\b(?:merged?|push(?:ed)?|commit(?:ted)?|rebased?)\s+(?:in|on)?to\s+{Q}{N}"
    rf"|\bretarget\w*\s+(?:[\w#`-]+\s+){{0,4}}?from\s+{Q}{N}"
    rf"|{N}{Q}\s*(?:→|->)\s*`?(?:main\b|preview/|release/)"
    rf"|(?:\bmain|\b(?:preview|release)/[\w.<>-]+)`?\s*(?:→|->)\s*{Q}{N}"
    # A release mapped onto a role branch: "NNN is now on `main`", "`main` now carries
    # Release NNN". README → Branch Information is the one place that does this, by marker.
    rf"|\b(?:Release\s+)?{N}\b[^.\n]{{0,40}}?\b(?:is\s+)?(?:now\s+)?on\s+`(?:main|preview/|release/)"
    rf"|\b(?:Release\s+)?{N}\b[^.\n]{{0,40}}?\b(?:was\s+|is\s+)?(?:promoted|moved|merged|cut|"
    rf"graduated)\s+(?:in|on)?to\s+`?(?:main\b|preview/|release/)"
    rf"|`(?:main|preview/[^`]*|release/[^`]*)`\s+(?:now\s+)?(?:carries|holds|tracks|is)\s+"
    rf"(?:the\s+)?(?:Salesforce\s+)?Release\s+{N}"
    # A role branch labelled with a release, as README's Branch Information spells it
    # ("**`main`**: Salesforce Release NNN", "`main` (Release NNN)"); that one line is marked.
    rf"|`(?:main|preview/[^`]*|release/[^`]*)`\**\s*(?:[:—–(]|-{{1,2}})\s*(?:the\s+)?"
    rf"(?:Salesforce\s+)?Release\s+{N}"
    # A branch labelled with a release: "This branch: Release NNN", "the branch is NNN".
    rf"|\bbranch\b[*:\s]+(?:is\s+|carries\s+)?(?:(?:Salesforce\s+)?Release\s+)?{N}",
    re.IGNORECASE)


# Any git subcommand, read from shell tokens: global options are skipped by shape (quoted
# values included: `-c http.extraHeader="A: b"`), and the first other token is the verb. Not
# an allowlist of verbs or options; both went stale one review round at a time.
# A bare three-digit argument is a ref unless an option's name says it's a measure.
GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path",
                     "--config-env", "--super-prefix", "--list-cmds"}


def git_invocations(line: str):
    """(verb, arguments) for each `git` command on the line."""
    for word in GIT_WORD.finditer(line):
        rest = line[word.end():].split("`", 1)[0]
        tokens = command_tokens(rest)
        k = 0
        while k < len(tokens) and tokens[k].startswith("-"):
            k += 2 if tokens[k] in GLOBAL_WITH_VALUE else 1
        if k < len(tokens) and tokens[k] in git_commands():
            yield tokens[k], tokens[k + 1:]


# `git` as a command word: not inside `git-tracking`, `.git`, `/git/`.
# `/usr/bin/git`, `"/opt/x/git"`, Windows `git.exe`; not `.git`, `git-x`.
GIT_WORD = re.compile(r"(?<![\w.-])git(?:\.exe)?[\"']?(?=\s)", re.IGNORECASE)


def git_commands() -> frozenset:
    """Every subcommand this git knows (`git --list-cmds`), so prose such as "git helpers in
    pack 167" isn't a command. Asked of git rather than listed here, so it can't go stale."""
    global _GIT_COMMANDS
    if _GIT_COMMANDS is None:
        out = subprocess.run(["git", "--list-cmds=main,others,nohelpers,alias"],
                             capture_output=True, text=True)
        names = set(out.stdout.split()) if out.returncode == 0 else set()
        # An old git without --list-cmds: the porcelain that takes refs, at least.
        _GIT_COMMANDS = frozenset(names or {
            "checkout", "switch", "push", "pull", "fetch", "merge", "rebase", "branch", "reset",
            "diff", "log", "show", "rev-parse", "rev-list", "merge-base", "cherry", "cherry-pick",
            "clone", "tag", "format-patch", "archive", "blame", "config", "worktree", "grep",
            "restore", "add", "rm", "mv", "status", "ls-files", "commit"})
    return _GIT_COMMANDS


_GIT_COMMANDS = None
# Subcommands where `--` starts pathspecs. Everywhere else it only ends option parsing.
PATHSPEC_VERBS = {"log", "diff", "show", "checkout", "reset", "restore", "blame", "grep",
                  "rev-list", "shortlog", "whatchanged", "format-patch", "difftool", "stash",
                  "add", "rm", "mv", "status", "ls-files", "clean", "commit", "annotate"}
# Subcommands whose positional operands can be revisions (from git's own synopses). For every
# other subcommand (`hash-object`, `sparse-checkout`, ...) a positional is a path, name or
# value; only the value of a ref flag (`--branch`, `-b`, `--onto`, ...) is still read as a ref.
REVISION_VERBS = {
    "checkout", "switch", "branch", "merge", "rebase", "reset", "log", "diff", "show",
    "rev-parse", "rev-list", "merge-base", "cherry", "cherry-pick", "revert", "tag", "push",
    "pull", "fetch", "format-patch", "archive", "blame", "annotate", "grep", "describe",
    "shortlog", "whatchanged", "range-diff", "name-rev", "ls-tree", "cat-file", "show-branch",
    "update-ref", "symbolic-ref", "bisect", "difftool", "request-pull", "replace",
    "commit-tree", "read-tree", "diff-tree", "show-ref", "verify-commit", "verify-tag",
    "fast-export", "for-each-ref", "stash", "notes", "restore", "worktree", "remote",
    "bundle", "config", "clone", "reflog", "cherry-pick", "merge-tree", "log-tree",
}
# Subcommands whose positional arguments are only paths (or a URL and directory); in them a
# number is a ref only as the value of a ref flag (`clone -b NNN`).
PATH_VERBS = {"add", "rm", "mv", "status", "ls-files", "clean", "commit", "init", "clone",
              "apply", "am", "check-ignore", "check-attr", "restore"}  # restore: --source=
# Subcommands whose first positional argument is a pattern, not a ref (`git grep NNN main`).
PATTERN_VERBS = {"grep"}
# `git config` options whose next token is their value, not the key.
CONFIG_VALUE_OPTS = {"-t", "--type", "-f", "--file", "--blob", "--comment", "--default"}
# `git worktree` actions whose operands are all paths (only `add` takes a commit-ish).
WORKTREE_PATH_ACTIONS = {"remove", "move", "lock", "unlock", "repair", "prune", "list"}
# Short flags whose value is a ref, per subcommand. Scoped, because the same letters are
# numbers elsewhere (`diff -B100` is a break-rewrite threshold, `apply -C100` a context count).
VERB_REF_FLAGS = {
    "checkout": {"-b", "-B"}, "switch": {"-c", "-C"}, "clone": {"-b"}, "branch": {"-u"},
    "restore": {"-s"}, "submodule": {"-b"},
}
# Options whose value is a path, message or format, not a ref, per subcommand.
VERB_VALUE_FLAGS = {
    "archive": {"-o", "--output", "--prefix", "--format", "--remote", "--add-file"},
    "symbolic-ref": {"-m"}, "update-ref": {"-m"},
    "tag": {"-m", "-F", "-u", "--message", "--file", "--local-user"},
    "notes": {"-m", "-F", "-C", "-c", "--message", "--file"},
    "bundle": {"--output"}, "format-patch": {"-o", "--output-directory", "--subject-prefix"},
    "merge": {"-m", "-F", "--message", "--file", "-s", "--strategy", "-X"},
    "stash": {"-m", "--message"}, "revert": {"-m", "--mainline"},
    "cherry-pick": {"-m", "--mainline"},
    "branch": {"--format", "--sort"},
    "push": {"-o", "--push-option", "--receive-pack", "--exec"},
    "fetch": {"-o", "--server-option", "--upload-pack"},
    "pull": {"-o", "--server-option", "--upload-pack"},
    "blame": {"--contents", "-S", "--ignore-revs-file", "--ignore-rev", "--date"},
    "for-each-ref": {"--format", "--sort", "--count"},
}
# Optional-value options (`--color[=<when>]`, `--column[=<opts>]`, `--relative[=<path>]`)
# take their value only attached with `=`, so they never consume the next token.
VERB_VALUE_FLAGS["tag"] |= {"--format", "--sort"}
# diff/log/show search and output options: a string, regex or file, never a revision.
for _verb in ("diff", "log", "show", "whatchanged", "format-patch"):
    VERB_VALUE_FLAGS.setdefault(_verb, set()).update(
        {"-S", "-G", "-O", "--output", "--grep", "--author", "--committer", "--format",
         "--pretty", "--date", "--since", "--until", "--after", "--before", "--line-prefix",
         "--src-prefix", "--dst-prefix", "--word-diff-regex", "-I", "--ignore-matching-lines",
         "-l", "--encoding", "--notes", "--show-notes"})
# Options whose value is a file, path or pattern under any subcommand that has them.
VALUE_FLAGS_ANYWHERE = {"--pathspec-from-file", "--rotate-to", "--skip-to", "--decorate-refs",
                        "--decorate-refs-exclude", "--exclude", "--exclude-per-directory",
                        "--template", "--separate-git-dir", "--reference", "--config"}
# Long options whose value is a ref though their name has no ref word.
LONG_REF_FLAGS = {"--force-with-lease", "--shallow-exclude", "--fork-point", "--merged",
                  "--no-merged", "--contains", "--no-contains", "--points-at", "--orphan",
                  "--ancestry-path", "--exclude-first-parent-only"}


def command_tokens(rest: str) -> list:
    """The arguments of one simple command, shell-quoted, ending at an unquoted `|`, `;`, `&`,
    `#` or `)` (a command substitution's close, `$(git rev-parse NNN)`). The same characters inside
    quotes (`--format="%h | %s"`) doesn't end it. Unbalanced quotes fall back to whitespace."""
    if "'" not in rest and '"' not in rest:  # the common case, and much cheaper than shlex
        return re.split(r"[#|;&)]", rest, maxsplit=1)[0].split()
    try:
        lexer = shlex.shlex(rest, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split, lexer.commenters = True, "#"
        tokens = []
        for token in lexer:
            if token and set(token) <= set(";&|()"):
                break
            tokens.append(token)
        return tokens
    except ValueError:
        return re.split(r"[#|;&)]", rest, maxsplit=1)[0].split()
# Short flags whose next token is a count, not a ref. Long flags are judged by their words.
# Per subcommand, because a short flag's arity differs (`grep -n`/`-L` take no value).
COUNT_FLAGS = {
    "-n": {"log", "rev-list", "shortlog", "show", "whatchanged", "reflog", "format-patch"},
    "-U": {"diff", "log", "show", "format-patch", "diff-tree", "diff-index", "diff-files"},
    "-L": {"log", "blame"},
    "-j": {"fetch", "pull", "clone", "submodule"},
}
# Words in a long option that make its value a ref (`--branch=`, `--onto`, `--set-upstream-to`).
REF_FLAG_WORDS = {"branch", "branches", "base", "head", "ref", "onto", "into", "upstream",
                  "target", "to", "from", "source", "remotes"}
# A branch-ish setting: an identifier with a branch word in it (`DEFAULT_BASE`, `base_ref`,
# `targetBranch`, `PROTECTED`), then `=` or `:`, then a release-shaped value: the whole value,
# or an element of a list/tuple/set. Identifiers are split into words, so `keyPrefix` is not a
# `ref`, and one that also names a measurement (`timeout_base`, `max_refs`) is not a branch.
# The separator may carry a type annotation (`DEFAULT_BRANCH: str = "NNN"`, TS `: string =`)
# or be a Make assignment (`?=`, `:=`). Not `!=`/`==`: those are comparisons.
SETTING = re.compile(r"(?<![\w-])([A-Za-z_][\w-]*)[\"']?\s*"
                     r"(?::\s*[\w.\[\]|, ]+?\s*=(?!=)|[?:+]=|(?<![!=<>+])=(?!=)|:(?!=))\s*")
BRANCH_WORDS = {"base", "bases", "branch", "branches", "ref", "refs", "protected", "target",
                "targets", "head", "heads"}
MEASURES = {"timeout", "count", "size", "port", "limit", "max", "min", "len", "length", "num",
            "delay", "retry", "retries", "seconds", "secs", "ms", "width", "height", "depth",
            "price", "amount", "quantity", "qty", "cost", "total", "percent", "score",
            "index", "idx", "version", "rate", "ttl"}
MAPPING_KEY = re.compile(r"(?:^|[{,])\s*[\"']?\d{3}[\"']?\s*:")
QUOTED_NUMBER = re.compile(r"[\"']\d{3}[\"']")
SCALAR = re.compile(r"[\"']?\d{3}[\"']?(?![\w.-])")
ELEMENT = re.compile(r"(?<![\w./-])[\"']?\d{3}[\"']?(?![\w./-])")


def identifier_words(name: str) -> set:
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", name)}


def top_level(value: str) -> str:
    """The contents of the collection `value` opens, up to its matching close, with any nested
    collection's contents dropped. Quotes are respected, so a bracket in a string doesn't count."""
    out, depth, quote = [], 0, ""
    for ch in value:
        if quote:
            if ch == quote:
                quote = ""
            if depth == 1:
                out.append(ch)
            continue
        if ch in "\"'":
            quote = ch
            if depth == 1:
                out.append(ch)
        elif ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
            if depth == 0:
                break
        elif depth == 1:
            out.append(ch)
    return "".join(out)


# `BASE_BRANCH="${1:-NNN}"`: a launcher's default for a positional argument.
SHELL_POSITIONAL = re.compile(r"[\"']?\$\{\d+:?[-=]\s*[\"']?\d{3}[\"']?\}")
KWARG = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*[\"']\d{3}[\"']")


def non_branch_kwargs_out(expression: str) -> str:
    """The expression without keyword arguments whose name isn't branch-like, so the
    `timeout="300"` in `resolve_ref(timeout="300")` isn't taken for the default branch."""
    def keep(match):
        words = identifier_words(match.group(1))
        # `default=`/`fallback=` supply the setting's own value, so they stay.
        return match.group(0) if (words & (BRANCH_WORDS | {"default", "fallback"})
                                  and not words & MEASURES) else ""
    return KWARG.sub(keep, expression)


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
        if SCALAR.match(value) or SHELL_POSITIONAL.match(value):
            return True
        # An expression rather than a literal (`os.getenv("BASE", "NNN")`,
        # `os.getenv("BASE") or "NNN"`): any quoted three-digit literal in it is the default.
        if not long_line and re.match(r"[A-Za-z_]", value) and \
                QUOTED_NUMBER.search(non_branch_kwargs_out(re.split(r"[;\n]", value, maxsplit=1)[0])):
            return True
        if value and value[0] in "[({":
            # The collection's own top level: up to its matching close, nested ones removed,
            # so `{"main": {"reviews": 2}, "NNN": {...}}` keeps the "NNN" key.
            inner = top_level(value)
            # `{…}` with `key: value` pairs is a mapping. Under a branch-named setting its
            # keys are branches (`PROTECTED = {"main": True, "NNN": True}`); its values,
            # and any nested object's fields, aren't.
            if value[0] == "{" and ":" in inner:
                if MAPPING_KEY.search(inner):
                    return True
                continue
            if ELEMENT.search(inner):
                return True
    return False


# A revision token's ref parts: split a range (`a..b`, `a...b`) or refspec (`+a:b`), then drop
# a revision suffix (`^`, `~2`, `@{1}`), so `264..HEAD` and `264:preview/266` yield `264`.
REV_SPLIT = re.compile(r"\.\.\.?|:")
REV_SUFFIX = re.compile(r"(?:\^\{[^}]*\}|\^[!@]|\^-\d*|[\^~]\d*|@\{[^}]*\})+$")  # ^{commit}, ^!, ^@, ^-


def ref_parts(token: str) -> list:
    token = token.strip("\"'")
    return [REV_SUFFIX.sub("", part.lstrip("+^")) for part in REV_SPLIT.split(token)]


def remote_tracking(token: str) -> bool:
    """`mirror/NNN` on a remote this clone may not have: `<name>/NNN` where <name> isn't a role
    prefix (`release/NNN` is the pattern) and isn't a directory here (`docs/NNN` is a path)."""
    for part in ref_parts(token):
        match = re.fullmatch(r"([\w.-]+)/(\d{3})", part)
        if match and match.group(1) not in ROLE_PREFIXES | TAG_PREFIXES \
                and not (REPO / match.group(1)).is_dir():
            return True
    return False


# Long options that take their value as the next token (`--max-count 100`). Arity is listed,
# not guessed from the name: `--count`, `--no-abbrev-commit` and `--prune` are switches, and
# the token after them is a revision. (An attached `--x=NNN` is judged by name below.)
LONG_SEPARATE_VALUE = {"--max-count", "--skip", "--depth", "--deepen", "--stat-width",
                       "--stat-count", "--stat-name-width", "--stat-graph-width", "--unified",
                       "--inter-hunk-context", "--jobs", "--max-parents", "--min-parents",
                       "--max-age", "--min-age", "--shallow-since"}


def takes_number(flag: str, verb: str = "") -> bool:
    """Whether `flag` consumes the next token as a number."""
    if flag in COUNT_FLAGS:
        return verb in COUNT_FLAGS[flag]
    return flag in LONG_SEPARATE_VALUE


# Subcommands with an action word, whose positionals' roles depend on it. Per action: from
# which positional (counting the action as 0) operands can be refs; actions not listed take
# none. Flags in `refs` carry a ref value; flags in `values` carry other data.
ACTION_VERBS = {
    # worktree add [-b <branch>] [--reason <s>] <path> [<commit-ish>]; others take paths.
    "worktree": {"from": {"add": 2}, "refs": {"-b", "-B"}, "values": {"--reason"}},
    # remote add/set-url/rename take names and URLs; set-head and set-branches take branches.
    "remote": {"from": {"set-head": 2, "set-branches": 2},
               "refs": {"-t", "-m", "--track", "--master"},
               "values": {"--mirror"}},
    # bundle create <file> <rev-list args>; verify/list-heads/unbundle take a file.
    "bundle": {"from": {"create": 2}, "refs": set(), "values": {"--version"}},
}


def action_operands(verb: str, tokens: list) -> list:
    """The tokens of an action subcommand that can be refs: ref-flag values, and positionals
    from the action's ref position on. Option data (`--reason why`) isn't positional."""
    spec = ACTION_VERBS[verb]
    taken = spec["refs"] | spec["values"]
    positional = [k for k, t in enumerate(tokens) if not t.startswith("-")
                  and not (k and tokens[k - 1] in taken)]
    action = tokens[positional[0]] if positional else ""
    keep = set(positional[spec["from"][action]:]) if action in spec["from"] else set()
    out = []
    if verb == "worktree" and action == "add" and "--orphan" in tokens and len(positional) > 1:
        out.append(tokens[positional[1]].rstrip("/").rsplit("/", 1)[-1])  # basename = new branch
    for k, t in enumerate(tokens):
        if k in keep or k and tokens[k - 1] in spec["refs"]:
            out.append(t)
        elif t[:2] in spec["refs"] and len(t) > 2 and not t.startswith("--"):
            out.append(t[2:])  # attached: `-b264`, `-t264`
        elif "=" in t and t.split("=", 1)[0] in spec["refs"]:
            out.append(t.split("=", 1)[1])  # `--track=264`
    return out


def measure_flag(flag: str, verb: str = "") -> bool:
    """A flag whose value is a number: a short count flag of this subcommand, or a long one whose
    name has a measurement word and no ref word (`--max-count`, `--stat-width`, `--prune`)."""
    if flag in COUNT_FLAGS:
        return verb in COUNT_FLAGS[flag]
    if not flag.startswith("--"):
        return False
    words = set(flag.lstrip("-").lower().split("-"))
    return bool(words & (MEASURES | {"prune", "deepen", "skip", "unified", "abbrev", "context",
                                      "jobs"})) \
        and not words & REF_FLAG_WORDS


def numbered_branch_in_code(line: str, first_len: int = 0, long_line: bool = False) -> bool:
    # Each `git` on the line, not just the first: `git fetch && git checkout NNN`.
    for verb, tokens in git_invocations(line):
        if "--" in tokens:
            # After `--`: pathspecs for the revision-and-path commands (`git log -- 264`); for
            # the rest it only ends options, so `git branch -- NNN` still names a branch.
            cut = tokens.index("--")
            tokens = tokens[:cut] if verb in PATHSPEC_VERBS else tokens[:cut] + tokens[cut + 1:]
        if verb == "config":
            # `git config branch.<b>.gh-merge-base NNN`: a ref only under a branch-ish key.
            # Skip options and the values of those that take one (`--type path`).
            key, k = "", 0
            while k < len(tokens):
                if tokens[k] in CONFIG_VALUE_OPTS:
                    k += 2
                elif tokens[k].startswith("-"):
                    k += 1
                else:
                    key = tokens[k]
                    break
            if re.fullmatch(r"branch\.\d{3}\..+", key):
                return True  # `git config branch.NNN.remote origin`: the key names the branch
            words = {w for w in re.split(r"[.\-_]", key.lower()) if w}
            if not words & (BRANCH_WORDS | {"merge", "remote"}) or words & MEASURES:
                continue
            tokens = tokens[k + 1:] if key else []
        if verb in PATTERN_VERBS:
            # Patterns are the values of `-e`, or else the first positional; either way not refs.
            if any(t == "-e" or t.startswith(("-e", "--regexp")) for t in tokens):
                tokens = [t for k, t in enumerate(tokens)
                          if not t.startswith(("-e", "--regexp"))
                          and not (k and tokens[k - 1] in ("-e", "--regexp"))]
            else:
                positional = [k for k, t in enumerate(tokens) if not t.startswith("-")]
                if positional:
                    tokens = tokens[:positional[0]] + tokens[positional[0] + 1:]
        if verb in ACTION_VERBS:
            tokens = action_operands(verb, tokens)
        ref_flags = VERB_REF_FLAGS.get(verb, set())
        for i, token in enumerate(tokens):
            if i and (takes_number(tokens[i - 1], verb)
                      or tokens[i - 1] in VERB_VALUE_FLAGS.get(verb, ())
                      or tokens[i - 1] in VALUE_FLAGS_ANYWHERE):
                continue
            if (verb in PATH_VERBS or verb not in REVISION_VERBS) and not token.startswith("-") \
                    and not (
                    i and (tokens[i - 1] in ref_flags or tokens[i - 1].startswith("--")
                           and set(tokens[i - 1].lstrip("-").split("-")) & REF_FLAG_WORDS)):
                continue  # `git add 264`: a path
            attached = re.fullmatch(r"(-[A-Za-z])[\"']?\d{3}[\"']?", token)
            if attached and attached.group(1) in ref_flags:
                return True  # `clone -b264`, `checkout -B264`, `branch -u264`: attached value
            if token.startswith("-"):
                # `--branch=NNN` is a ref; `--stat-width=NNN` is a measure.
                flag, _, token = token.partition("=")
                if not token or measure_flag(flag, verb) or flag.startswith("--") and \
                        flag not in LONG_REF_FLAGS and not \
                        set(flag.lstrip("-").lower().split("-")) & REF_FLAG_WORDS:
                    continue
            if any(re.fullmatch(r"\d{3}", part) for part in ref_parts(token)):
                return True
            if remote_tracking(token):
                return True
    if shell_default(line):
        return True
    return branch_setting(line, first_len, long_line)


# A CLI option declared with a numbered default: `add_argument("--base", default="NNN")`,
# `click.option("--head", default="NNN")`. Read over the whole call, which often wraps.
OPTION_CALL = re.compile(r"\b(?:add_argument|option)\(")
OPTION_DEFAULT = re.compile(r"[\"'](--?[\w-]+)[\"'].*?\bdefault\s*=\s*"
                            # a literal, or a call holding a quoted one (`os.getenv("B", "NNN")`)
                            r"(?:[\"']?\d{3}[\"']?(?![\w.])|[\w.]+\([^)]*?[\"']\d{3}[\"']"
                            # or a fallback within the same argument (`os.getenv("B") or "NNN"`)
                            r"|[^,]*?[\"']\d{3}[\"'])")


OPTION_NAME = re.compile(r"[\"'](--[\w-]+)[\"']")
OPTION_CHOICES = re.compile(r"\b(?:choices\s*=\s*|Choice\(\s*)[\[({]([^\])}]*)")


def option_default(lines: list, i: int) -> bool:
    if not OPTION_CALL.search(lines[i]):
        return False
    call, depth = "", 0
    for line in lines[i:i + LOGICAL_MAX]:
        call += " " + line.strip()
        depth += line.count("(") - line.count(")")
        if depth <= 0:
            break
    # Branch-ness from every long name the option declares (`"-b", "--base"`), not the first.
    words = {w for name in OPTION_NAME.findall(call) for w in name.lstrip("-").lower().split("-")}
    if not words & REF_FLAG_WORDS or words & MEASURES:
        return False
    if OPTION_DEFAULT.search(call):
        return True
    # `choices=("main", "NNN")` / `click.Choice([...])`: a numbered branch in the CLI's
    # allowed values, whatever its default.
    return any(QUOTED_NUMBER.search(choices.group(1)) for choices in OPTION_CHOICES.finditer(call))


# A shell parameter default for a branch-named variable: `${BASE_BRANCH:-NNN}`.
SHELL_DEFAULT = re.compile(r"\$\{([A-Za-z_]\w*):?[-=]\s*[\"']?\d{3}[\"']?\}")


def shell_default(line: str) -> bool:
    for match in SHELL_DEFAULT.finditer(line):
        words = identifier_words(match.group(1))
        if words & BRANCH_WORDS and not words & MEASURES:
            return True
    return False


# Every prose pattern needs one of these words; checking for them first skips the costly
# case-insensitive UNQUOTED on almost every line.
PROSE_KEY = re.compile(r"branch|named|called|merge|push|commit|rebase|retarget|main|release/|"
                       r"preview/|→|->", re.IGNORECASE)


def near_branch(line: str) -> bool:
    if not PROSE_KEY.search(line):
        return False
    if BARE_WORD_BRANCH.search(line) or UNQUOTED.search(line):
        return True
    for match in BARE.finditer(line):
        window = line[max(0, match.start() - NEAR):match.end() + NEAR]
        if BRANCH_NEAR.search(window):
            return True
    return False


# Role prefixes: a remote that happens to be called `release` or `preview` must not turn the
# role branch `release/NNN` into a numbered remote ref (refs/remotes/... stays unambiguous).
ROLE_PREFIXES = {"release", "preview", "feat", "fix", "chore", "docs"}  # README's roles
# Tag namespaces: `archive/NNN` is the tag a retired numbered branch was archived as, not a
# branch, so it names history rather than pinning a line.
TAG_PREFIXES = {"archive"}


def ref_pattern(remotes) -> re.Pattern:
    names = "|".join(sorted({re.escape(r) for r in remotes} - ROLE_PREFIXES - TAG_PREFIXES))
    return re.compile(rf"(?<![\w./-])(?:{names})/\d{{3}}\b|refs/heads/\d{{3}}\b"
                      rf"|(?<![\w./-])(?:refs/)?remotes/[\w.-]+/\d{{3}}\b"
                      rf"|--(?:base|head)(?:=|\s+)[\"']?(?:[\w.-]+:)?(?:(?:{names})/)?\d{{3}}\b"
                      # The same pair as adjacent argv items: `["...", "--base", "NNN"]`.
                      rf"|[\"']--(?:base|head)[\"']\s*,\s*[\"'](?:[\w.-]+:)?(?:(?:{names})/)?\d{{3}}[\"']"
                      # gh's short aliases, only after `gh pr` (`grep -B 100` is context).
                      rf"|\bgh[\"']?\s+pr\s+[^\n|;&]*?\s-[BH](?:=|\s*)[\"']?(?:[\w.-]+:)?\d{{3}}\b")


def remotes() -> set:
    """Fails with OSError rather than scanning with an incomplete remote list."""
    out = subprocess.run(["git", "-C", str(REPO), "remote"], capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git remote failed")
    return set(KNOWN_REMOTES) | set(out.stdout.split())


# A setting whose list, tuple or set opens on this line and doesn't close on it.
OPEN_SETTING = re.compile(r"[:=]\s*(?:[A-Za-z_][\w.]*)?([\[({])")  # incl. `= os.getenv(`
CLOSER = {"[": "]", "(": ")", "{": "}"}
LOGICAL_MAX = 50


# A YAML key with no inline value (`branches:`), whose value is the block sequence below it.
YAML_KEY = re.compile(r"^(\s*)(?:-\s+)?[\"']?[A-Za-z_][\w-]*[\"']?\s*:\s*(?:#.*)?$")
YAML_ITEM = re.compile(r"^(\s*)-\s+(.*?)\s*(?:#.*)?$")


YAML_CHILD_KEY = re.compile(r"^(\s+)[\"']?([\w./-]+)[\"']?\s*:(?:\s|$)")


def yaml_child_keys(lines: list, i: int, indent: int) -> list:
    """`protected_branches:` then `main: true` / `"NNN": true`: the mapping's own keys (its
    direct children only), which under a branch-named key are branches."""
    keys, child = [], None
    for line in lines[i + 1:i + 1 + LOGICAL_MAX]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        width = len(line) - len(line.lstrip())
        if width <= indent:
            break
        match = YAML_CHILD_KEY.match(line)
        if child is None:
            if not match:
                return []
            child = width
        if width == child and match and ALLOW not in line:
            keys.append(match.group(2))
    return keys


def yaml_block(lines: list, i: int):
    """`key:` then `- item` lines (indented deeper, or at the key's own indent, which YAML
    allows for a sequence) as one flow line, `key: [item, item]`. None if not that shape."""
    key = YAML_KEY.match(lines[i])
    if not key:
        return None
    indent, items = len(key.group(1)), []
    keys = yaml_child_keys(lines, i, indent)
    if keys:
        return f"{lines[i].split('#')[0].rstrip()} [{', '.join(keys)}]"
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
    # `const DEFAULT_BASE =` with its value on the next line.
    if joined.rstrip().endswith("=") and not joined.rstrip().endswith(("==", "!=", "<=", ">=")) \
            and j + 1 < len(lines):
        j += 1
        joined = joined.rstrip() + " " + allowed_out(lines[j])
    while joined.rstrip().endswith("\\") and j + 1 < len(lines) and j - i < LOGICAL_MAX:
        j += 1
        joined = joined.rstrip()[:-1] + " " + allowed_out(lines[j])
    opened = OPEN_SETTING.search(joined)
    if opened:
        open_ch = opened.group(1)
        close = CLOSER[open_ch]
        depth = joined[opened.start(1):].count(open_ch) - joined[opened.start(1):].count(close)
        while depth > 0 and j + 1 < len(lines) and j - i < LOGICAL_MAX:
            j += 1
            joined += " " + allowed_out(lines[j])
            depth += lines[j].count(open_ch) - lines[j].count(close)
    return joined


def allowed_out(line: str) -> str:
    """A joined continuation line, or nothing if it carries the allow marker, so the marker
    works on the line that keeps the number rather than only on the block's opener."""
    return "" if ALLOW in line else line.strip()


# Every rule needs a three-digit run, on the line or, for a block, on a later line its opener
# joins. These two let the scan skip the rest: it reads every tracked text file, ~10 MB.
DIGITS = re.compile(r"\d{3}")
# A shell parameter's default, `${1:-NNN}` / `${VAR:-NNN}`: what the command sees when the
# argument is absent, so `git checkout "${1:-NNN}"` is read as `git checkout "NNN"`.
SHELL_EXPANSION = re.compile(r"\$\{[\w@*#?]+:?[-=]\s*[\"']?(\d{3})[\"']?\}")
# Longer than any hand-written line: minified or generated code (vendored static resources),
# where a call-wrapped quoted number is noise, not a branch someone wrote. Only that heuristic
# is switched off on such a line; exact refs and direct settings are still checked.
MAX_LINE = 2000
OPENER = re.compile(r"\\\s*$|=\s*$|\[\s*$|[:=]\s*(?:[A-Za-z_][\w.]*)?[\[({]|:\s*(?:#.*)?$|"
                    r"\b(?:add_argument|option)\(|[\[(]\s*[\"'](?:[\w./-]*/)?(?:git|gh)[\"']")


# An argv list for git or gh: `subprocess.run(["git", "diff", "NNN..HEAD"])`, the usual
# Python form here. Rebuilt as the shell command it runs, then read by the same rules.
# A list or tuple whose first item is git or gh, by basename (`"/usr/bin/git"` too).
ARGV = re.compile(r"""[\[(]\s*(["'])(?:[\w./\\: -]*[/\\])?(git|gh)(?:\.exe)?\1\s*,([^\])]*)[\])]""",
                  re.IGNORECASE)
ARGV_ITEM = re.compile(r"""(["'])(.*?)\1""")
ARGV_OPEN = re.compile(r"""[\[(]\s*["'](?:[\w./\\: -]*[/\\])?(?:git|gh)(?:\.exe)?["']""",
                       re.IGNORECASE)


def expression_end(text: str, pos: int) -> int:
    """Where the list element starting at `pos` ends: the next comma or close at its depth."""
    depth, quote, k = 0, "", pos
    while k < len(text):
        ch = text[k]
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch in "[({":
            depth += 1
        elif ch in "])}":
            if depth == 0:
                return k
            depth -= 1
        elif ch == "," and depth == 0:
            return k
        k += 1
    return k


def argv_commands(text: str) -> list:
    """Each git/gh argv in `text`, read item by item (quote-aware), so a `)` or `]` inside an
    argument (`"--format=%h (%s)"`) doesn't end the list."""
    commands = []
    for opened in ARGV_OPEN.finditer(text):
        pos, items = opened.start() + 1, []
        while True:
            while pos < len(text) and text[pos] in " \t\n,":
                pos += 1
            item = ARGV_ITEM.match(text, pos)
            if item:
                items.append(item.group(2))
                pos = item.end()
                continue
            # A non-literal element (`str(repo)`): skip it to the next top-level comma and keep
            # a placeholder, so literal refs after it are still read.
            end = expression_end(text, pos)
            if end == pos:
                break  # the list's own close
            items.append("DYNAMIC")
            pos = end
        exe = re.split(r"[/\\]", items[0])[-1].lower().removesuffix(".exe") if items else ""
        if exe in ("git", "gh"):
            commands.append(exe + " " +
                            " ".join(shlex.quote(x) for x in items[1:]))
    return commands


def argv_block(lines: list, i: int) -> str:
    """A list or tuple opened on line i and closed later, joined, if it's a git/gh argv."""
    line = lines[i]
    opened = ARGV_OPEN.search(line)
    if opened:
        if closes(line[opened.start():]):
            return ""  # closed on this line: argv_commands() reads it from the logical line
    elif not line.rstrip().endswith(("[", "(")):
        return ""
    elif not ARGV_OPEN.match(line.rstrip()[-1] + " ".join(
            x.strip() for x in lines[i + 1:i + 3])):
        return ""  # a bare opener whose next lines don't start a git/gh argv
    joined = line
    for nxt in lines[i + 1:i + 1 + LOGICAL_MAX]:
        joined += " " + allowed_out(nxt)
        if closes(joined):
            break
    return joined if argv_commands(joined) else ""


def closes(text: str) -> bool:
    """Whether every bracket opened in `text` is closed, counting outside quotes only."""
    depth, quote = 0, ""
    for ch in text:
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
    return depth <= 0


def code_finding(lines: list, i: int, line: str, has_number) -> bool:
    logical = logical_line(lines, i)
    for command in argv_commands(logical) + argv_commands(argv_block(lines, i)):
        if REF.search(command) or numbered_branch_in_code(command):
            return True
    if not has_number and not DIGITS.search(logical) and not OPTION_CALL.search(line) \
            and not line.rstrip().endswith("[") and not ARGV_OPEN.search(line) \
            and not (line.rstrip().endswith("(") and i + 1 < len(lines)
                     and ARGV_OPEN.match("(" + lines[i + 1].strip())):
        return False  # an opener whose block holds no three-digit run: nothing to find
    return numbered_branch_in_code(logical, len(line), len(line) > MAX_LINE) \
        or option_default(lines, i)


REF = None  # the ref pattern of the current scan, for argv commands; set by findings()


def findings(text: str, ref: re.Pattern):
    global REF
    REF = ref
    if not DIGITS.search(text):
        return
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        has_number = DIGITS.search(line)
        following = lines[number] if number < len(lines) else ""
        if ALLOW in line:
            # The marker exempts this physical line only. If it opens a block, the block's
            # other lines are still read, with this line's own numbers masked out.
            code = re.split(r"\s#|//", line, maxsplit=1)[0].rstrip()  # the marker's comment off
            if OPENER.search(code) or ARGV_OPEN.search(code) or code.endswith(("(", "[")):
                masked = list(lines)
                masked[number - 1] = re.sub(r"\d", "x", code)
                if code_finding(masked, number - 1, masked[number - 1], None):
                    yield number, "code", line.strip()
            continue
        if not has_number and not OPENER.search(line) and not DIGITS.search(following) \
                and not (line.rstrip().endswith("(") and ARGV_OPEN.match("(" + following.strip())):
            continue
        expanded = SHELL_EXPANSION.sub(r"\1", line) if "${" in line else line
        if has_number and ref.search(expanded):
            yield number, "ref", line.strip()
        elif line.rstrip().endswith("\\") and ref.search(logical_line(lines, number - 1)):
            yield number, "ref", line.strip()
        elif ("--base" in line or "--head" in line) and following and \
                ref.search(line.rstrip() + " " + following.strip()) and not ref.search(following):
            yield number, "ref", line.strip()  # `"--base",` then `"NNN",` on the next line
        elif has_number and near_branch(line):
            yield number, "branch", line.strip()
        elif following and ALLOW not in following and len(line) < MAX_LINE and \
                (PROSE_KEY.search(line) or PROSE_KEY.search(following)) and \
                not near_branch(following) and near_branch(line.rstrip() + " " + following.lstrip()):
            # Prose wrapped across two lines: "… the `NNN`" / "branch cut …". Reported at the
            # first line, and only when neither line matches on its own.
            yield number, "branch", line.strip()
        elif code_finding(lines, number - 1, line, has_number) or expanded != line and \
                numbered_branch_in_code(expanded):
            yield number, "code", line.strip()


def tracked_scope() -> list[Path]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise OSError(out.stderr.strip() or "git ls-files failed")
    return [REPO / name for name in out.stdout.split("\0")
            if name and name not in EXCLUDE and not CAPTURED.match(name)
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
        ref = ref_pattern(remotes())  # a spawn failure is an OSError too
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    total = 0
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
