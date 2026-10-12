#!/usr/bin/env python3
"""PreToolUse guard: refuse, before it happens, what AGENTS.md says an agent must not do.

These rules are enforced here because by the time a gate sees the diff the damage is done
(a push to a protected branch) or the context is gone (which edit flipped an operation).
They bind Claude Code only. The required CI check is the layer every tool hits, so a rule
that can be checked from a diff belongs in `scripts/ai/pr_gate.py` as well.

1. Push target (DO NOT 8). A push whose destination is `main`, a `preview/*` or a
   `release/*` branch is denied, however it is spelled: an explicit refspec
   (`HEAD:main`), a bare `git push` whose upstream is `main`, a configured
   `remote.<name>.push` refspec (from the repo config or the command's own `-c`), a git
   alias that expands to `push`, `git -C <dir> push`, `--mirror`/`--all`, a push behind a
   command wrapper (a command starting with `env`, `sudo`, `time`, `timeout`, `nohup`,
   `nice` and the others in WRAPPERS, whatever their options), or split across lines with a
   trailing backslash. Release lines are
   matched by prefix, never by number. A push the guard cannot resolve to concrete
   destinations is denied rather than guessed at: wildcard refspecs, `--config-env`, `GIT_*`
   environment overrides, and shell aliases that run `push`. The `Bash(git push origin …)`
   deny rules in settings.json only catch the literal spelling.
   Adapter policy, not a DO NOT 8 rule: a force push to any other branch asks the person.
2. SFDMU destructive operation (CRITICAL rule). An edit to a `datasets/` plan that makes any
   object newly destructive asks the person: `deleteOldData` turning on, or an `Upsert`
   object becoming `Insert`. Objects are compared one by one, keyed by the object their
   query reads (`scripts/sfdmu_export.py`'s parsers), so moving `deleteOldData` from one
   object to another, or swapping Upsert and Insert between two objects, still asks. The
   agent cannot approve it for itself.
3. Stop files, for loop agents only (`LOOP_ROLE` set; interactive sessions are not affected):
   `$LOOP_RUN_DIR/STOP` refuses every tool call of that one run (a remote cancel of one run);
   `<main checkout>/.loop/STOP` refuses every loop agent on the workstation (`make stop`).
   Either takes effect at the agent's next tool call; neither aborts a tool already running.

What this guard does not catch, and what backs it up:
- Commands hidden in `$(...)`, `bash -c`, `eval`, `env -S '…'`, `xargs` or `find -exec`, a
  wrapper not in WRAPPERS, and pushes by any non-git program.
- State a compound command changes before its push runs: `git checkout main && git push` and
  `cd elsewhere && git push` are resolved against the branch and directory the command
  started in. An explicit destination (`git push origin main`) is caught either way.
- Aliases more than one level deep (an alias whose expansion is another alias).
  For all of these the server is the backstop: the "Approvals" branch ruleset on `main`,
  `preview/*` and `release/*` requires a PR and blocks force-pushes and deletion, and its
  admin bypass applies to pull-request merges only, so a direct push with the owner's
  credentials is rejected. This guard refuses it earlier and says why.
- SFDMU edits made through Bash (`sed -i`, a script) rather than Edit/Write. No diff-level
  check for destructive operations exists in `pr_gate.py` yet; adding one is planned with the
  defect registry work, and until then a person reviewing the diff is the only backstop.

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
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

PROTECTED = ("main",)
PROTECTED_PREFIXES = ("preview/", "release/")
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&"}
# git's global options that take a separate argument, so `git -C dir push` is still a push.
GIT_GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
# Global options replayed into every resolution call, so `-c remote.origin.push=…` and
# `--git-dir` mean to the guard what they mean to the push.
GIT_GLOBAL_REPLAYED = {"-c", "--git-dir", "--work-tree", "--namespace"}
# `git push` options that take a separate argument, so their value is not read as a remote.
PUSH_WITH_ARG = {"-o", "--push-option", "--receive-pack", "--exec"}
FORCE_LONG = ("--force", "--force-with-lease", "--force-if-includes")
# `-f` alone or clustered with `git push`'s other no-value short flags (`-uf`, `-fu`).
FORCE_SHORT = re.compile(r"-[46dnquv]*f[46dnquv]*")
# Programs that run another command after their own options and values. Rather than model
# each one's options, the push is read from the first `git` after the wrapper.
WRAPPERS = {"env", "command", "builtin", "exec", "sudo", "doas", "time", "timeout", "nohup",
            "nice", "ionice", "stdbuf", "setsid", "chronic", "caffeinate", "arch", "unbuffer"}
EVERYTHING_FLAGS = ("--mirror", "--all", "--branches")
ENV_ASSIGNMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")

DELETE_OLD_DATA = re.compile(r'"deleteOldData"\s*:\s*true')
OP_INSERT = re.compile(r'"operation"\s*:\s*"Insert"')
OP_UPSERT = re.compile(r'"operation"\s*:\s*"Upsert"')
CHECKOUT = Path(__file__).resolve().parents[2]  # the checkout this hook ships in


def is_protected(ref: str) -> bool:
    name = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    return name in PROTECTED or name.startswith(PROTECTED_PREFIXES)


def git(cwd: str, *args: str, opts: Sequence[str] = ()) -> Optional[str]:
    try:
        out = subprocess.run(["git", *opts, "-C", cwd, *args], capture_output=True, text=True,
                             timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def simple_commands(command: str) -> Iterator[List[str]]:
    """Each simple command in a shell line, as argv. Unparseable text yields nothing."""
    # Each line as written and with `\`-continued lines rejoined: the shell may read it
    # either way (an escaped `\\`, a backslash in a comment), so both are checked.
    joined = re.sub(r"\\\r?\n", " ", command)
    lines = command.splitlines() + ([] if joined == command else joined.splitlines())
    for line in lines:
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


class Push:
    """One `git push`, with what is needed to resolve where it goes."""

    def __init__(self, directory: str, args: List[str], opts: List[str], env: Dict[str, str],
                 unresolvable: str = "") -> None:
        self.directory, self.args, self.opts, self.env = directory, args, opts, env
        self.unresolvable = unresolvable


def git_push(argv: List[str], cwd: str) -> Optional[Push]:
    """A Push if argv runs `git push` directly or through an alias, else None."""
    env: Dict[str, str] = {}
    while argv and ENV_ASSIGNMENT.match(argv[0]):
        name, _, value = argv[0].partition("=")
        env[name] = value
        argv = argv[1:]
    if argv and os.path.basename(argv[0]) in WRAPPERS:
        at = next((i for i, w in enumerate(argv) if os.path.basename(w) == "git"), None)
        if at is None:
            return None
        env.update(w.partition("=")[::2] for w in argv[1:at] if ENV_ASSIGNMENT.match(w))
        argv = argv[at:]
    if not argv or os.path.basename(argv[0]) != "git":
        return None
    i, directory, opts, config_env = 1, cwd, [], False
    while i < len(argv) and argv[i].startswith("-"):
        flag = argv[i]
        if flag in GIT_GLOBAL_WITH_ARG and i + 1 < len(argv):
            if flag == "-C":
                directory = os.path.join(directory, argv[i + 1])
            elif flag in GIT_GLOBAL_REPLAYED:
                opts += [flag, argv[i + 1]]
            else:
                config_env = True
            i += 2
        else:
            if flag.startswith("--config-env"):
                config_env = True
            elif flag.split("=", 1)[0] in GIT_GLOBAL_REPLAYED:
                opts.append(flag)
            i += 1
    if i >= len(argv):
        return None
    sub, rest = argv[i], argv[i + 1:]
    if sub != "push":
        alias = git(directory, "config", "--get", f"alias.{sub}", opts=opts)
        if alias is None:
            return None
        if alias.startswith("!"):
            if re.search(r"\bpush\b", alias):
                return Push(directory, [], opts, env,
                            f"the shell alias `{sub}` runs a push the guard cannot resolve")
            return None
        try:
            expansion = shlex.split(alias)
        except ValueError:
            return None
        if not expansion or expansion[0] != "push":
            return None
        rest = expansion[1:] + rest
    unresolvable = ""
    if config_env:
        unresolvable = "`--config-env` takes push configuration from the environment"
    elif any(name.startswith("GIT_") for name in env):
        unresolvable = "`GIT_*` environment overrides change where git pushes"
    return Push(directory, rest, opts, env, unresolvable)


def strip_remote(ref: str) -> str:
    """`origin/release/x` → `release/x`: only the first segment is the remote."""
    return ref.split("/", 1)[1] if "/" in ref else ref


def push_decision(push: Push) -> Tuple[str, str]:
    """('deny' | 'ask' | 'allow', reason) for one `git push`."""
    if push.unresolvable:
        return "deny", f"{push.unresolvable}, so this push is refused rather than guessed at"
    d, opts = push.directory, push.opts
    force, positional, remote_flag, i = False, [], None, 0
    while i < len(push.args):
        arg = push.args[i]
        if arg in EVERYTHING_FLAGS:
            return "deny", f"`git push {arg}` updates protected branches too"
        name = arg.split("=", 1)[0]
        # git takes any unambiguous prefix of a long option: `--forc` is `--force`.
        if FORCE_SHORT.fullmatch(arg) or (name.startswith("--forc")
                                          and any(f.startswith(name) for f in FORCE_LONG)):
            force = True
        elif arg == "--repo" and i + 1 < len(push.args):
            remote_flag = push.args[i + 1]
            i += 1
        elif arg.startswith("--repo="):
            remote_flag = arg.split("=", 1)[1]
        elif arg in PUSH_WITH_ARG:
            i += 1
        elif not arg.startswith("-"):
            positional.append(arg)
        i += 1
    current = git(d, "rev-parse", "--abbrev-ref", "HEAD", opts=opts)
    remote = (positional[0] if positional else remote_flag
              or (current and git(d, "config", "--get", f"branch.{current}.pushRemote", opts=opts))
              or git(d, "config", "--get", "remote.pushDefault", opts=opts)
              or (current and git(d, "config", "--get", f"branch.{current}.remote", opts=opts))
              or "origin")
    refspecs = positional[1:]
    configured = False
    if not refspecs:
        # With no refspec on the command line, git uses `remote.<remote>.push` if set (from
        # the repo config or this command's `-c`), and only otherwise push.default.
        listed = git(d, "config", "--get-all", f"remote.{remote}.push", opts=opts)
        if listed:
            refspecs, configured = listed.splitlines(), True
    targets: List[str] = []
    if refspecs:
        for spec in refspecs:
            if spec.startswith("+"):
                force, spec = True, spec[1:]
            if spec == ":":
                return "deny", "the `:` refspec pushes every matching branch, including protected ones"
            if "*" in spec:
                return "deny", f"the wildcard refspec `{spec}` can't be resolved to concrete branches"
            src, _, dst = spec.partition(":")
            if not dst and src in ("HEAD", "@"):
                dst = current or src
            targets.append(dst or src)
    else:
        # A bare push goes to @{push} (the same-named branch or the upstream, by push.default),
        # so check both @{push} and @{upstream}: `git -c push.default=upstream push` reaches
        # the upstream even where the plain config makes @{push} unresolvable. A feature
        # branch that tracks main is refused here; plain git would refuse that push anyway.
        for spec in ("@{push}", "@{upstream}"):
            where = git(d, "rev-parse", "--abbrev-ref", "--symbolic-full-name", spec, opts=opts)
            if where and "/" in where:
                targets.append(strip_remote(where))
        if current and current != "HEAD":
            targets.append(current)
    hit = [t for t in targets if is_protected(t)]
    if hit:
        how = f" (via the configured remote.{remote}.push refspec)" if configured else ""
        return "deny", (f"this push updates {', '.join(sorted(set(hit)))}{how}. AGENTS.md DO NOT "
                        "8: changes reach main, preview/* and release/* only through a pull request")
    if force:
        return "ask", ("force push rewrites a branch other PRs may be stacked on; this adapter "
                       "asks a person first (adapter policy, not a DO NOT 8 rule)")
    return "allow", ""


def text_change(tool: str, tool_input: dict) -> Optional[Tuple[str, str, Optional[str], str, str]]:
    """(path, whole file before, whole file after or None, snippet before, snippet after)."""
    path = tool_input.get("file_path") or ""
    if tool not in ("Write", "Edit", "MultiEdit"):
        return None
    try:
        before = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        before = ""
    if tool == "Write":
        after = tool_input.get("content") or ""
        return path, before, after, before, after
    edits = [tool_input] if tool == "Edit" else (tool_input.get("edits") or [])
    after: Optional[str] = before
    for edit in edits:
        old, new = edit.get("old_string") or "", edit.get("new_string") or ""
        if after is None or not old or old not in after:
            after = None  # the edit can't be replayed here; fall back to the snippets
            continue
        after = after.replace(old, new) if edit.get("replace_all") else after.replace(old, new, 1)
    return (path, before, after, "".join(e.get("old_string") or "" for e in edits),
            "".join(e.get("new_string") or "" for e in edits))


def destructive_objects(text: str) -> Optional[Dict[Tuple[str, int], Tuple[bool, Optional[str]]]]:
    """{(object, nth occurrence): (deleteOldData on, operation)} for an SFDMU plan, or None."""
    sys.path.insert(0, str(CHECKOUT / "scripts"))
    try:
        import sfdmu_export as sfdmu  # noqa: PLC0415  (the checkout's own parsers)
    except Exception:  # noqa: BLE001  any failure falls back to the text comparison, which asks
        return None
    finally:
        if str(CHECKOUT / "scripts") in sys.path:
            sys.path.remove(str(CHECKOUT / "scripts"))
    try:
        return _objects(sfdmu, json.loads(text))
    except Exception:  # noqa: BLE001  a plan shape the parsers choke on: same fallback
        return None


def _objects(sfdmu, plan) -> Optional[Dict[Tuple[str, int], Tuple[bool, Optional[str]]]]:
    if not isinstance(plan, dict):
        return None
    seen: Dict[str, int] = {}
    out: Dict[Tuple[str, int], Tuple[bool, Optional[str]]] = {}
    for object_set in sfdmu.normalize_object_sets(plan):
        objects = object_set.get("objects") if isinstance(object_set, dict) else None
        for obj in objects if isinstance(objects, list) else []:
            if not isinstance(obj, dict):
                continue
            name = sfdmu.extract_object_name(obj.get("query")) or "?"
            nth = seen[name] = seen.get(name, -1) + 1
            out[(name, nth)] = (sfdmu.is_js_truthy(obj.get("deleteOldData")),
                                sfdmu.resolve_operation(obj.get("operation")))
    return out


def sfdmu_decision(path: str, before: str, after: Optional[str], old: str,
                   new: str) -> Tuple[str, str]:
    if "datasets/" not in path.replace(os.sep, "/") or not path.endswith(".json"):
        return "allow", ""
    was = destructive_objects(before) if before else {}
    now = destructive_objects(after) if after is not None else None
    # A document that parses but declares no objects isn't a plan the parsers understand, so
    # it gets the conservative text comparison below rather than a vacuous "nothing changed".
    if was is not None and now:
        prior = lambda key: was.get(key, (False, None))  # noqa: E731
        newly_deleting = [k[0] for k, (deletes, _) in now.items()
                          if deletes and not prior(k)[0]]
        flipped = [k[0] for k, (_, op) in now.items()
                   if op == "insert" and prior(k)[1] == "upsert"]
        if newly_deleting:
            return "ask", (f'this edit turns on "deleteOldData" for {", ".join(newly_deleting)}, '
                           "which deletes every existing record before inserting. AGENTS.md "
                           "CRITICAL rule: explain why Upsert cannot work and get explicit "
                           "approval")
        if flipped:
            return "ask", (f"this edit flips {', '.join(flipped)} from Upsert to Insert. "
                           "AGENTS.md CRITICAL rule: on SFDMU 5.6.4+ Upsert works; explicit "
                           "approval is required")
        return "allow", ""
    # The plan doesn't parse (mid-edit), has no objects, or the edit can't be replayed: compare
    # the edited text itself, and ask whenever it adds a destructive marker or an Insert where
    # an Upsert was.
    count = lambda rx, s: len(rx.findall(s))  # noqa: E731
    if count(DELETE_OLD_DATA, new) > count(DELETE_OLD_DATA, old) or (
            count(OP_INSERT, new) > count(OP_INSERT, old) and count(OP_UPSERT, old)):
        return "ask", ("this SFDMU plan edit can't be compared object by object (the plan "
                       "doesn't parse, or the edit can't be replayed), and it adds deleteOldData "
                       "or an Insert where an Upsert was. AGENTS.md CRITICAL rule: explicit "
                       "approval is required")
    return "allow", ""


def stop_file(cwd: str) -> Optional[str]:
    """Why a loop agent must stop now, or None. Interactive sessions never stop here."""
    if not os.environ.get("LOOP_ROLE"):
        return None
    run_dir = os.environ.get("LOOP_RUN_DIR")
    if run_dir and (Path(run_dir) / "STOP").exists():
        return f"this run's stop file is set ({run_dir}/STOP): a cancel was requested for this run"
    common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common and (Path(common).parent / ".loop" / "STOP").exists():
        return "the workstation's kill switch is on (.loop/STOP)"
    return None


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
    stop = stop_file(cwd)
    if stop:
        return "deny", f"{stop}. Make no more tool calls; say where you got to and stop"
    if tool == "Bash":
        worst = ("allow", "")
        for argv in simple_commands(tool_input.get("command") or ""):
            push = git_push(argv, cwd)
            if push:
                decision = push_decision(push)
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
