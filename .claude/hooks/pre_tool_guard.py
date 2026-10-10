#!/usr/bin/env python3
"""PreToolUse guard: refuse, before it happens, what AGENTS.md says an agent must not do.

These rules are enforced here because by the time a gate sees the diff the damage is done
(a push to a protected branch) or the context is gone (which edit flipped an operation).
They bind Claude Code only. The required CI check is the layer every tool hits, so a rule
that can be checked from a diff belongs in `scripts/ai/pr_gate.py` as well.

1. Push target (DO NOT 8). A push whose destination is `main`, a `preview/*` or a
   `release/*` branch is denied, however it is spelled: `git push origin HEAD:main`, a bare `git push` whose
   upstream is `main`, `git -C <dir> push`, `--mirror`/`--all`. Release lines are matched
   by prefix, never by number, so nothing here changes from one release to the next. The
   `Bash(git push origin main …)` deny rules in settings.json only catch the literal spelling. A force push to any
   other branch asks the person, because rewriting a branch that other PRs stack on needs
   their approval.
2. SFDMU destructive operation (CRITICAL rule). An edit that adds `"deleteOldData": true` or
   flips `"operation": "Upsert"` to `"Insert"` in a `datasets/` plan asks the person. The
   agent cannot approve it for itself.
3. Kill switch. While `.loop/STOP` exists in the main checkout, every tool call by a loop
   agent (`LOOP_ROLE` set) is refused. Interactive sessions are not affected.

Not covered, by design: commands hidden in `$(...)`, `bash -c` or `eval`. The server-side
ruleset is the backstop there.

Stdlib only, Python 3.9-safe: it runs under whatever `python3` the shell provides.
Exit 0 = allow (or a JSON `ask` decision on stdout) · exit 2 = deny, reason on stderr.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

PROTECTED = ("main",)
PROTECTED_PREFIXES = ("preview/", "release/")
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&"}
# git's global options that take a separate argument, so `git -C dir push` is still a push.
GIT_GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
# `git push` options that take a separate argument, so their value is not read as a remote.
PUSH_WITH_ARG = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
FORCE_FLAGS = ("-f", "--force", "--force-with-lease", "--force-if-includes")
EVERYTHING_FLAGS = ("--mirror", "--all", "--branches")

DELETE_OLD_DATA = re.compile(r'"deleteOldData"\s*:\s*true')
OP_INSERT = re.compile(r'"operation"\s*:\s*"Insert"')
OP_UPSERT = re.compile(r'"operation"\s*:\s*"Upsert"')


def is_protected(ref: str) -> bool:
    name = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    return name in PROTECTED or name.startswith(PROTECTED_PREFIXES)


def git(cwd: str, *args: str) -> Optional[str]:
    try:
        out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                             timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def simple_commands(command: str) -> Iterator[List[str]]:
    """Each simple command in a shell line, as argv. Unparseable text yields nothing."""
    for line in command.splitlines():
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            continue
        argv: List[str] = []
        for token in tokens + [";"]:
            if token in SEPARATORS:
                if argv:
                    yield argv
                argv = []
            else:
                argv.append(token)


def git_push_args(argv: List[str], cwd: str) -> Optional[Tuple[str, List[str]]]:
    """(directory, push arguments) if argv is a `git push`, else None."""
    while argv and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0]) or argv[0] == "env"):
        argv = argv[1:]
    if not argv or os.path.basename(argv[0]) != "git":
        return None
    i, directory = 1, cwd
    while i < len(argv) and argv[i].startswith("-"):
        if argv[i] in GIT_GLOBAL_WITH_ARG and i + 1 < len(argv):
            if argv[i] == "-C":
                directory = os.path.join(directory, argv[i + 1])
            i += 2
        else:
            i += 1
    if i >= len(argv) or argv[i] != "push":
        return None
    return directory, argv[i + 1:]


def push_decision(directory: str, args: List[str]) -> Tuple[str, str]:
    """('deny' | 'ask' | 'allow', reason) for one `git push`."""
    force, positional, i = False, [], 0
    while i < len(args):
        arg = args[i]
        if arg in EVERYTHING_FLAGS:
            return "deny", f"`git push {arg}` updates protected branches too"
        if arg.startswith(FORCE_FLAGS):
            force = True
        elif arg in PUSH_WITH_ARG:
            i += 1
        elif arg in ("-d", "--delete"):
            pass
        elif not arg.startswith("-"):
            positional.append(arg)
        i += 1
    refspecs = positional[1:]
    targets: List[str] = []
    if refspecs:
        for spec in refspecs:
            if spec.startswith("+"):
                force, spec = True, spec[1:]
            if spec == ":":
                return "deny", "the `:` refspec pushes every matching branch, including protected ones"
            src, _, dst = spec.partition(":")
            if not dst and src in ("HEAD", "@"):
                dst = git(directory, "rev-parse", "--abbrev-ref", "HEAD") or src
            targets.append(dst or src)
    else:
        # A bare push goes to @{push} (the same-named branch or the upstream, by push.default),
        # so check both @{push} and @{upstream}: `git -c push.default=upstream push` reaches
        # the upstream even where the plain config makes @{push} unresolvable. A feature
        # branch that tracks main is refused here; plain git would refuse that push anyway.
        # Both are `<remote>/<branch>`, the only form with a remote prefix to strip, since a
        # preview/* or release/* branch name has a slash of its own.
        for spec in ("@{push}", "@{upstream}"):
            where = git(directory, "rev-parse", "--abbrev-ref", "--symbolic-full-name", spec)
            if where and "/" in where:
                targets.append(where.split("/", 1)[1])
        current = git(directory, "rev-parse", "--abbrev-ref", "HEAD")
        if current and current != "HEAD":
            targets.append(current)
    hit = [t for t in targets if is_protected(t)]
    if hit:
        return "deny", (f"this push updates {', '.join(sorted(set(hit)))}. AGENTS.md DO NOT 8: "
                        "changes reach main, preview/* and release/* only through a pull request")
    if force:
        return "ask", ("force push rewrites a branch other PRs may be stacked on "
                       "(AGENTS.md DO NOT 8); a person must approve it")
    return "allow", ""


def text_change(tool: str, tool_input: dict) -> Optional[Tuple[str, str, str]]:
    """(path, text before, text after) for a file edit, else None."""
    path = tool_input.get("file_path") or ""
    if tool == "Write":
        try:
            before = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            before = ""
        return path, before, tool_input.get("content") or ""
    if tool == "Edit":
        return path, tool_input.get("old_string") or "", tool_input.get("new_string") or ""
    if tool == "MultiEdit":
        edits = tool_input.get("edits") or []
        return (path, "".join(e.get("old_string") or "" for e in edits),
                "".join(e.get("new_string") or "" for e in edits))
    return None


def sfdmu_decision(path: str, before: str, after: str) -> Tuple[str, str]:
    if "datasets/" not in path.replace(os.sep, "/") or not path.endswith(".json"):
        return "allow", ""
    count = lambda rx, s: len(rx.findall(s))  # noqa: E731
    if count(DELETE_OLD_DATA, after) > count(DELETE_OLD_DATA, before):
        return "ask", ('this edit adds "deleteOldData": true, which deletes every existing '
                       "record before inserting. AGENTS.md CRITICAL rule: explain why Upsert "
                       "cannot work and get explicit approval")
    if (count(OP_INSERT, after) > count(OP_INSERT, before)
            and count(OP_UPSERT, after) < count(OP_UPSERT, before)):
        return "ask", ("this edit flips an Upsert operation to Insert. AGENTS.md CRITICAL rule: "
                       "on SFDMU 5.6.4+ Upsert works; explicit approval is required")
    return "allow", ""


def kill_switch(cwd: str) -> bool:
    if not os.environ.get("LOOP_ROLE"):
        return False
    common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return bool(common) and (Path(common).parent / ".loop" / "STOP").exists()


def respond(decision: str, reason: str) -> int:
    if decision == "deny":
        print(f"Blocked: {reason}.", file=sys.stderr)
        return 2
    if decision == "ask":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }}))
    return 0


def decide(event: dict) -> Tuple[str, str]:
    tool = event.get("tool_name") or ""
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if kill_switch(cwd):
        return "deny", ("the loop's kill switch is on (.loop/STOP). Make no more tool calls; "
                        "say where you got to and stop")
    if tool == "Bash":
        worst = ("allow", "")
        for argv in simple_commands(tool_input.get("command") or ""):
            push = git_push_args(argv, cwd)
            if push:
                decision = push_decision(*push)
                if decision[0] == "deny":
                    return decision
                if decision[0] == "ask":
                    worst = decision
        return worst
    change = text_change(tool, tool_input)
    if change:
        return sfdmu_decision(*change)
    return "allow", ""


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    return respond(*decide(event))


if __name__ == "__main__":
    sys.exit(main())
