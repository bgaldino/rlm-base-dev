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
   alias that expands to `push` (also through leading global options or another
   alias), `git -C <dir> push`, `--mirror`/`--all`, a push behind command wrappers (`env`,
   `sudo`, `time`, `timeout`, `nohup`, `nice` and the others in WRAPPERS, nested or not,
   and resolved in the directory a single `env -C` or `sudo -D` names), or
   split across lines with a trailing backslash. Long options are read the way the tool
   reads them, abbreviations included (`--mir`, `env --chd=`). Release lines are matched by
   prefix, never by number. A push the guard cannot resolve to concrete
   destinations is denied rather than guessed at: wildcard refspecs, `--config-env`, `GIT_*`,
   `HOME` or `XDG_CONFIG_HOME` overrides (they choose which config git reads), and shell
   aliases that run `push`. Redirections (`2>&1`, `>log`, before or after the command) are
   not arguments. The `Bash(git push origin …)`
   deny rules in settings.json only catch the literal spelling.
   A leading `cd <dir> &&` is followed. The private artifacts repo (`rlm-base-artifacts`,
   cloned at `.agents/artifacts`) takes direct commits on its `main` by design, so a push
   whose remote is that repository isn't refused for its target (a force push or a deletion
   of `main`, `preview/*` or `release/*` there asks); every other repository is.
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
  wrapper not in WRAPPERS, and pushes by any non-git program. Wrapper option *values*
  aren't parsed per wrapper, so a value that names a wrapper (`env -u sudo -C dir`) or a
  repeated chdir (`env -C a -C ../b`, where the last one wins) can resolve the wrong
  directory.
- A branch change a compound command makes before its push runs: `git checkout main &&
  git push` is resolved against the branch the command started on. (Directory changes are
  covered: a leading `cd <dir> &&` is followed, and a push in a command that changes
  directory any other way is refused as unresolvable.) An explicit destination (`git push origin main`) is caught either way.
- A brace group after a leading `cd`: `cd <dir> && { a; b; git push; }` also checks the
  starting directory, because the `;` inside is read as one that could run after a failed
  `cd`. That errs toward refusing; spell it with `&&` throughout, or `git -C <dir>`.
- For both push cases above the server is the backstop: the "Approvals" branch ruleset on
  `main`, `preview/*` and `release/*` requires a PR and blocks force-pushes and deletion,
  and its admin bypass applies to pull-request merges only, so a direct push with the
  owner's credentials is rejected. This guard refuses it earlier and says why.
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
# The one repository whose protected-looking branches are pushed to directly by design: the
# private artifacts repo (`.agents/artifacts`, the todo tracker) takes commits on its `main`.
# Matched on the push URL's host *and* path (see is_artifacts_url), so every other repository,
# on any host or local path, stays protected by default. GitHub names are case-insensitive.
ARTIFACTS_HOST = "github.com"
ARTIFACTS_PATH = re.compile(r"/?bgaldino/rlm-base-artifacts(?:\.git)?/?", re.IGNORECASE)
URL_FORMS = (
    re.compile(r"https://(?:[^@/]+@)?(?P<host>[^/:@]+)/(?P<path>.+)"),
    re.compile(r"ssh://(?:[^@/]+@)?(?P<host>[^/:@]+)(?::\d+)?/(?P<path>.+)"),
    re.compile(r"(?:[^@/:]+@)?(?P<host>[^/:@]+):(?P<path>[^/].*)"),  # scp-like, git@host:path
)
SAFE_HOST = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PROTECTED_PREFIXES = ("preview/", "release/")
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&"}
# git's global options that take a separate argument, so `git -C dir push` is still a push.
GIT_GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
# Global options replayed into every resolution call, so `-c remote.origin.push=…` and
# `--git-dir` mean to the guard what they mean to the push.
GIT_GLOBAL_REPLAYED = {"-c", "--git-dir", "--work-tree", "--namespace"}
# `git push` options that take a separate argument, so their value is not read as a remote.
PUSH_WITH_ARG = {"-o", "--push-option", "--receive-pack", "--exec", "--recurse-submodules"}
FORCE_LONG = ("--force", "--force-with-lease", "--force-if-includes")
# A cluster of `git push`'s short flags: no-value ones, optionally ending in `-o` (whose value
# is glued on, or is the next word). `-f` in it is a force: `-uf`, `-fu`, `-fo ci.skip`.
SHORT_CLUSTER = re.compile(r"-([46dfnquv]*)(?:o(.*))?")
# A redirection and its target (`2>&1`, `>log`, `&>>log`, `<in`); heredocs (`<<`) are left
# for code_lines. Stripping can unbalance a quote (`-m "a > b"`), so each line is read both
# with and without them.
REDIRECT = re.compile(r"(?:(?<=\s)|^)(?:\d+|&)?(?:>\||>>?|<(?!<)|<&)"
                      r"(?:&?\d+-?|-|\s*(?:'[^']*'|\"[^\"]*\"|[^\s;&|<>()]+))?")
# A heredoc's body is data, not commands (`cat > notes.md <<'EOF'`); `<<<` is a here-string.
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")
# Programs that run another command after their own options and values. Rather than model
# each one's options, the push is read from the first `git` after the wrapper.
WRAPPERS = {"env", "command", "builtin", "exec", "sudo", "doas", "time", "timeout", "nohup",
            "nice", "ionice", "stdbuf", "setsid", "chronic", "caffeinate", "arch", "unbuffer"}
# Wrapper options that run the command in another directory (`env -C`, `sudo -D`), and each
# wrapper's long options, so an abbreviation (`env --chd=…`) resolves as the tool would.
CHDIR = {"env": "-C", "sudo": "-D"}
WRAPPER_LONG = {
    "env": ("--ignore-environment", "--null", "--unset", "--chdir", "--split-string",
            "--block-signal", "--default-signal", "--ignore-signal", "--list-signal-handling",
            "--debug", "--help", "--version"),
    "sudo": ("--askpass", "--background", "--bell", "--chdir", "--chroot", "--close-from",
             "--command-timeout", "--edit", "--group", "--help", "--host", "--list", "--login",
             "--non-interactive", "--other-user", "--preserve-env", "--preserve-groups",
             "--prompt", "--remove-timestamp", "--reset-timestamp", "--role", "--set-home",
             "--shell", "--stdin", "--type", "--user", "--validate", "--version"),
}
# `git push`'s long options (`git push -h`), so an abbreviation git accepts (`--receive`,
# `--mir`) is read as the option it names.
_NEGATABLE = ("all", "atomic", "branches", "delete", "dry-run", "exec", "follow-tags", "force",
              "force-if-includes", "force-with-lease", "mirror", "porcelain", "progress", "prune",
              "push-option", "quiet", "receive-pack", "recurse-submodules", "repo",
              "set-upstream", "signed", "tags", "thin", "verbose")
PUSH_LONG = tuple(f"--{n}" for n in _NEGATABLE) + tuple(f"--no-{n}" for n in _NEGATABLE) + (
    "--ipv4", "--ipv6", "--verify", "--no-verify")
EVERYTHING_FLAGS = ("--mirror", "--all", "--branches")
# Shell reserved words that can precede a simple command (`! git push`, `if git push …; then`).
SHELL_PREFIX = {"!", "{", "}", "if", "then", "elif", "else", "do", "while", "until", "fi", "done"}
CONFIG_LOCATION = {"HOME", "XDG_CONFIG_HOME"}  # where git finds its global configuration
ENV_ASSIGNMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")

DELETE_OLD_DATA = re.compile(r'"deleteOldData"\s*:\s*true')
OP_INSERT = re.compile(r'"operation"\s*:\s*"Insert"')
OP_UPSERT = re.compile(r'"operation"\s*:\s*"Upsert"')
CHECKOUT = Path(__file__).resolve().parents[2]  # the checkout this hook ships in


def ssh_hostname(alias: str) -> Optional[str]:
    """The host an SSH alias connects to (`github.com-me` -> `github.com`), per `ssh -G`."""
    if not SAFE_HOST.fullmatch(alias):  # never let a host be read as an ssh option
        return None
    try:
        out = subprocess.run(["ssh", "-G", alias], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    for line in out.stdout.splitlines() if out.returncode == 0 else []:
        key, _, value = line.partition(" ")
        if key == "hostname":
            return value.strip().lower()
    return None


def is_artifacts_url(url: str) -> bool:
    """Whether a push URL is the private artifacts repo on GitHub: https://github.com/…, or SSH
    to github.com directly or through an alias that resolves to it."""
    for form in URL_FORMS:
        found = form.fullmatch(url)
        if found:
            break
    else:
        return False  # a local path or another scheme is never the artifacts repo
    if not ARTIFACTS_PATH.fullmatch(found.group("path")):
        return False
    host = found.group("host").lower()
    if host == ARTIFACTS_HOST:
        return True
    return not url.startswith("https://") and ssh_hostname(host) == ARTIFACTS_HOST


def is_protected(ref: str) -> bool:
    """git resolves a push destination by trying `refs/<dst>` and `refs/heads/<dst>`, so
    `main`, `heads/main` and `refs/heads/main` all name the same branch."""
    name = ref
    for prefix in ("refs/", "heads/"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name in PROTECTED or name.startswith(PROTECTED_PREFIXES)


def git(cwd: str, *args: str, opts: Sequence[str] = ()) -> Optional[str]:
    try:
        out = subprocess.run(["git", *opts, "-C", cwd, *args], capture_output=True, text=True,
                             timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def code_lines(lines: List[str]) -> Iterator[str]:
    """The lines that are commands, skipping heredoc bodies."""
    end = None
    for line in lines:
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        yield line
        heredoc = HEREDOC.search(line)
        if heredoc:
            end = heredoc.group(2)


def _argvs(text: str, whole: bool) -> Iterator[List[str]]:
    """Split one text into simple commands. `whole` lexes it as one script, so a quoted string
    may span lines (`-m "title⏎⏎body" && git push`) and a newline outside quotes separates
    commands; otherwise it is one line. Unparseable text yields nothing."""
    if whole:
        lexer = shlex.shlex(text, posix=True, punctuation_chars="();<>|&\n")
        lexer.whitespace = " \t\r"
    else:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return
    argv: List[str] = []
    for token in tokens + [";"]:
        # Punctuation arrives grouped (`&&\n`, `);`); a redirection (`>`, `2>&`) stays with its
        # command, anything else ends it.
        redirection = set(token) <= set("<>&") and bool(set(token) & set("<>"))
        if token in SEPARATORS or (whole and is_punctuation(token) and not redirection):
            if argv:
                yield argv
            argv = []
        else:
            argv.append(token)


def simple_commands(command: str) -> Iterator[List[str]]:
    """Each simple command in a shell command, as argv, read every way the shell might: the
    whole script (quotes spanning lines), each line as written, and each line with
    backslash-continued lines rejoined (an escaped backslash, a backslash in a comment) and
    with redirections removed. A push found in any reading counts."""
    code = list(code_lines(command.splitlines()))
    joined = re.sub(r"\\\r?\n", "", command)  # bash deletes a continuation: `c\⏎d` is `cd`
    lines = list(code)
    if joined != command:
        lines += code_lines(joined.splitlines())
    lines += [stripped for stripped in (REDIRECT.sub(" ", line) for line in lines)
              if stripped not in lines]
    script = "\n".join(code)
    for text in dict.fromkeys([script, REDIRECT.sub(" ", script)]):
        yield from _argvs(text, whole=True)
    for line in lines:
        yield from _argvs(line, whole=False)


class Push:
    """One `git push`, with what is needed to resolve where it goes."""

    def __init__(self, directory: str, args: List[str], opts: List[str], env: Dict[str, str],
                 unresolvable: str = "") -> None:
        self.directory, self.args, self.opts, self.env = directory, args, opts, env
        self.unresolvable = unresolvable


def git_push(argv: List[str], cwd: str, env: Optional[Dict[str, str]] = None,
             depth: int = 0) -> Optional[Push]:
    """A Push if argv runs `git push` directly or through an alias, else None."""
    env = dict(env or {})
    while argv and argv[0] in SHELL_PREFIX:
        argv = argv[1:]
    while argv and ENV_ASSIGNMENT.match(argv[0]):
        name, _, value = argv[0].partition("=")
        env[name] = value
        argv = argv[1:]
    if argv and os.path.basename(argv[0]) in WRAPPERS:
        # The first `git` that reads as a push: an option value can be `git` too
        # (`sudo -u git git push`, `env -C /srv/git git push`).
        for at in range(1, len(argv)):
            if os.path.basename(argv[at]) in ("git", "git-push"):
                inner = dict(env, **dict(w.partition("=")[::2] for w in argv[1:at]
                                         if ENV_ASSIGNMENT.match(w)))
                # Wrappers nest (`timeout 60 env -C dir git push`): each option is read as
                # the innermost wrapper before it reads it.
                directory, wrapper = cwd, os.path.basename(argv[0])
                for j, word in enumerate(argv[1:at], 1):
                    if os.path.basename(word) in WRAPPERS:
                        wrapper = os.path.basename(word)
                        continue
                    flag, eq, value = word.partition("=")
                    flag = long_option(flag, WRAPPER_LONG.get(wrapper, ()))
                    short = CHDIR.get(wrapper)
                    if short and word.startswith(short) and len(word) > len(short):
                        directory = os.path.join(directory, word[len(short):])  # `-Cdir`
                    elif flag in (short, "--chdir") and short:
                        if eq:
                            directory = os.path.join(directory, value)
                        elif j + 1 < at:
                            directory = os.path.join(directory, argv[j + 1])
                push = git_push(argv[at:], directory, inner)
                if push:
                    return push
        return None
    if argv and os.path.basename(argv[0]) == "git-push":
        argv = ["git", "push"] + argv[1:]  # git's exec-path entry point, `git-push`, run directly
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
        # An alias can start with global options (`-c remote.origin.push=… push`) or name
        # another alias, so its expansion is read like a command line of its own. git itself
        # refuses alias loops; the depth bound only stops this guard looping on one.
        if not expansion or depth >= 10:
            return None
        return git_push(argv[:i] + expansion + rest, cwd, env, depth + 1)
    unresolvable = ""
    if config_env:
        unresolvable = "`--config-env` takes push configuration from the environment"
    elif any(name.startswith("GIT_") or name in CONFIG_LOCATION for name in env):
        unresolvable = ("`GIT_*`, `HOME` or `XDG_CONFIG_HOME` overrides change which "
                        "configuration, and so which destination, git uses")
    return Push(directory, rest, opts, env, unresolvable)


def long_option(name: str, options: Sequence[str]) -> str:
    """The long option `name` (before any `=`) abbreviates, as getopt and git resolve it: an
    exact name, else the one option it is a prefix of. An ambiguous prefix every candidate of
    which forces (`--forc`) is `--force`; any other is returned unchanged."""
    if name in options or not name.startswith("--") or name == "--":
        return name
    matches = [o for o in options if o.startswith(name)]
    if len(matches) == 1:
        return matches[0]
    if matches and all(m in FORCE_LONG for m in matches):
        return "--force"
    return name


def strip_remote(ref: str) -> str:
    """`origin/release/x` → `release/x`: only the first segment is the remote."""
    return ref.split("/", 1)[1] if "/" in ref else ref


def push_decision(push: Push) -> Tuple[str, str]:
    """('deny' | 'ask' | 'allow', reason) for one `git push`."""
    if push.unresolvable:
        return "deny", f"{push.unresolvable}, so this push is refused rather than guessed at"
    d, opts = push.directory, push.opts
    force, tags, delete, positional, remote_flag, i = False, False, False, [], None, 0
    while i < len(push.args):
        arg = push.args[i]
        if arg == "--":  # everything after it is the repository and refspecs, never an option
            positional += push.args[i + 1:]
            break
        name, eq, value = arg.partition("=")
        name = long_option(name, PUSH_LONG)
        if name in EVERYTHING_FLAGS:
            return "deny", f"`git push {arg}` updates protected branches too"
        cluster = SHORT_CLUSTER.fullmatch(arg)
        if cluster and arg != "-":
            force = force or "f" in cluster.group(1)
            delete = delete or "d" in cluster.group(1)
            if cluster.group(2) == "":  # `-o value` / `-fo value`: skip the value
                i += 1
        elif name in FORCE_LONG:
            force = True
        elif name in ("--delete", "--no-delete"):
            delete = name == "--delete"
        elif name in ("--tags", "--no-tags"):
            tags = name == "--tags"  # the last one wins
        elif name == "--repo":
            if eq:
                remote_flag = value
            elif i + 1 < len(push.args):
                remote_flag = push.args[i + 1]
                i += 1
        elif name in PUSH_WITH_ARG and not eq:
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
    # `--tags` is itself a refspec (refs/tags/*): with no other on the command line, git
    # pushes only tags and uses neither remote.<name>.push nor push.default.
    tags_only = tags and not refspecs
    if not refspecs and not tags_only:
        # With no refspec on the command line, git uses `remote.<remote>.push` if set (from
        # the repo config or this command's `-c`), and only otherwise push.default.
        listed = git(d, "config", "--get-all", f"remote.{remote}.push", opts=opts)
        if listed:
            refspecs, configured = listed.splitlines(), True
    targets: List[str] = []
    deletions: List[str] = []  # `:dst` refspecs, or every target under --delete
    if refspecs:
        for spec in refspecs:
            if spec.startswith("+"):
                force, spec = True, spec[1:]
            if spec == ":":
                return "deny", "the `:` refspec pushes every matching branch, including protected ones"
            if "*" in spec:
                return "deny", f"the wildcard refspec `{spec}` can't be resolved to concrete branches"
            src, _, dst = spec.partition(":")
            if not src and dst:
                deletions.append(dst)
            if not dst and src in ("HEAD", "@"):
                dst = current or src
            targets.append(dst or src)
    elif not tags_only:
        # A bare push goes to @{push} (the same-named branch or the upstream, by push.default),
        # so check both @{push} and @{upstream}: `git -c push.default=upstream push` reaches
        # the upstream even where the plain config makes @{push} unresolvable. A feature
        # branch that tracks main is refused here; plain git would refuse that push anyway.
        if (git(d, "config", "--get", "push.default", opts=opts) or "").lower() == "matching":
            return "deny", ("push.default=matching pushes every branch that exists on both "
                            "ends, protected ones included")
        for spec in ("@{push}", "@{upstream}"):
            where = git(d, "rev-parse", "--abbrev-ref", "--symbolic-full-name", spec, opts=opts)
            if where and "/" in where:
                targets.append(strip_remote(where))
        if current and current != "HEAD":
            targets.append(current)
    # Exempt only a configured remote, every one of whose push URLs (after insteadOf and
    # pushInsteadOf rewriting) is the artifacts repo; a raw URL or path is never exempt.
    urls = (git(d, "remote", "get-url", "--push", "--all", remote, opts=opts) or "").split()
    exempt = bool(urls) and all(is_artifacts_url(u) for u in urls)
    hit = [] if exempt else [t for t in targets if is_protected(t)]
    if delete:
        deletions += targets
    gone = sorted({t for t in deletions if is_protected(t)})
    if exempt and gone:
        # The exemption is for direct commits; deleting a protected-looking branch there asks,
        # like a force push.
        return "ask", (f"this deletes {', '.join(gone)} in the artifacts repo; deleting a "
                       "branch asks a person first (adapter policy)")
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


LITERAL_PATH = re.compile(r"[A-Za-z0-9._/-]+")  # a cd target the guard follows (see below)
# Another change of directory after a leading `cd <dir> &&` (see command_directories).
MOVES = {"cd", "pushd", "popd"}


def unconditional(token: str) -> bool:
    """Whether a lexer token (punctuation arrives grouped, e.g. `);`) holds a separator that runs
    what follows even if an earlier `cd` failed: `;`, `||`, a newline, or a lone `&`."""
    if not token or not set(token) <= set("();<>|&\n"):
        return False
    if ";" in token or "||" in token or "\n" in token:
        return True
    return "&" in token.replace("&&", "").replace(">&", "").replace("&>", "")


PUNCTUATION = set("();<>|&\n")


def is_punctuation(token: str) -> bool:
    return bool(token) and set(token) <= PUNCTUATION


def lexed_commands(tokens: List[str]) -> List[List[str]]:
    """The words of each simple command in a token list (punctuation arrives grouped). A
    redirection (`<`, `>`, `<<<`, `2>&`) belongs to its command, and its operand (`< cd`) is
    not a word of it."""
    out, words, operand = [], [], False
    for token in tokens + [";"]:
        if is_punctuation(token) and set(token) <= set("<>&") and set(token) & set("<>"):
            if words and words[-1].isdigit():  # `2>` arrives as `2`, `>`: the fd isn't a word
                words.pop()
            operand = True
        elif is_punctuation(token):
            if words:
                out.append(words)
            words, operand = [], False
        elif operand:
            operand = False
        else:
            words.append(token)
    return out


def command_directories(command: str, cwd: str) -> Optional[List[str]]:
    """command_directories for every way the shell may read the command: as written, and with
    backslash-newline continuations deleted (`c\⏎d` is `cd`). An escaped backslash before a
    newline is not a continuation, so both readings are taken; None if either is."""
    readings = dict.fromkeys([command, re.sub(r"\\\r?\n", "", command)])
    found: List[str] = []
    for text in readings:
        dirs = _command_directories(text, cwd)
        if dirs is None:
            return None
        found += [d for d in dirs if d not in found]
    return found


def _command_directories(command: str, cwd: str) -> Optional[List[str]]:
    """The directories this command's pushes may run in. A leading `cd <dir> &&`, or
    `(cd <dir> && …)`, moves them (`cd .agents/artifacts && git push`), and the starting
    directory is checked too when anything after it can run if the `cd` failed, or follows
    the subshell. None when where a push runs can't be resolved: a target the shell would
    resolve differently (anything but a literal path of letters, digits and `._/-`; `CDPATH`;
    a missing directory), or any other
    change of directory (`cd a; git push`, `x && cd a`, `cd a && cd b`, `time cd a`). Any
    standalone `cd`/`pushd`/`popd` word counts, other than a redirection's operand."""
    # Heredoc bodies are data (a commit message may mention `cd`), as in simple_commands.
    command = "\n".join(code_lines(command.splitlines()))
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace, lexer.whitespace_split = " \t\r", True
    try:
        tokens = list(lexer)
    except ValueError:
        return [cwd]
    # Any standalone cd/pushd/popd word counts, wherever it sits: telling the command word from
    # its prefixes (`time`, `command -p`, `{fd}>`, `exec`, …) is open-ended, and missing one lets
    # a push through. Only a redirection's operand (`< cd`) is skipped. `echo cd && git push`
    # is refused as a result, which errs toward refusing.
    moves = [w for argv in lexed_commands(tokens) for w in argv if w in MOVES]
    if not moves:
        return [cwd]
    # The one form followed: a leading `cd [-L|-P|-e|-@]… [--] <dir> &&`, optionally in `( )`.
    i = 1 if tokens[:1] == ["("] else 0
    if len(moves) > 1 or tokens[i:i + 1] != ["cd"]:
        return None
    j, physical = i + 1, None  # None: no -L/-P given, so the shell's own default applies
    while j < len(tokens) and re.fullmatch(r"-[LPe@]+", tokens[j]):
        modes = [c for c in tokens[j] if c in "LP"]
        if modes:
            physical = modes[-1] == "P"  # the last of -L / -P wins
        j += 1
    if j < len(tokens) and tokens[j] == "--":
        j += 1
    if len(tokens) < j + 2 or tokens[j + 1] != "&&":
        return None
    raw = tokens[j]
    # `cd -L` cancels `..` against the path as typed (`link/..` is where you started), before
    # any symlink is followed; normpath does the same. Under `-P`, or with no option (the
    # shell may run with `set -o physical`, e.g. inherited through SHELLOPTS), `..` applies
    # after symlinks, which the guard doesn't model, so a `..` is followed only under `-L`.
    if physical is not False and ".." in raw.split("/"):
        return None
    target = os.path.normpath(os.path.join(cwd, raw))
    # Followed only when the target is a plain literal path. The lexer has dropped the quoting
    # that decides how the shell expands a word (`~` vs `'~'`, `[x]`, `$VAR`, `{a,b}`, `!`,
    # escapes), so rather than list what the shell might expand, anything outside letters,
    # digits and `._/-` is refused. CDPATH would also redirect a relative name.
    if (not LITERAL_PATH.fullmatch(raw) or raw.startswith("-") or not os.path.isdir(target)
            or (os.environ.get("CDPATH") and not raw.startswith(("/", "./", "../")))):
        return None
    rest = tokens[j + 2:]
    # In `(cd dir && …) && git push` the cd is the subshell's alone: a push after the matching
    # `)` runs back in the starting directory. (A redirection or `| tail` there doesn't.)
    after_subshell = False
    if i:
        # A quoted `(` or `)` arrives unquoted; if no matching `)` is found, assume something
        # may follow it, and check the starting directory too.
        after_subshell = True
        depth = 1
        for k, t in enumerate(rest):
            if is_punctuation(t):
                depth += t.count("(") - t.count(")")
            if depth <= 0:
                after_subshell = any(git_push(argv, cwd) for argv in lexed_commands(rest[k + 1:]))
                break
    if after_subshell or any(unconditional(t) for t in rest):
        return [target, cwd]
    return [target]


def decide(event: dict) -> Tuple[str, str]:
    tool = event.get("tool_name") or ""
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    stop = stop_file(cwd)
    if stop:
        return "deny", f"{stop}. Make no more tool calls; say where you got to and stop"
    if tool == "Bash":
        worst = ("allow", "")
        command = tool_input.get("command") or ""
        directories = command_directories(command, cwd)
        if directories is None:
            if any(git_push(argv, cwd) for argv in simple_commands(command)):
                return "deny", ("this command changes directory in a way the guard can't follow "
                                "(only one leading `cd <dir> &&` to a literal path is), so where "
                                "the push runs can't be resolved; run it as "
                                "`git -C <dir> push …` instead")
            directories = [cwd]
        for directory in directories:
            for argv in simple_commands(command):
                push = git_push(argv, directory)
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
