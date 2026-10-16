#!/usr/bin/env python3
"""Run the read-only toolchain audit (.cursor/skills/toolchain/workstation-audit.md).

The audit's tables say what each check expects and where its fix is documented; the
commands live here, keyed by section and check id, so nobody has to pick a command out
of a markdown table cell. An agent once took the Expect column instead and ran what it
held. Every command is read-only: it prints versions, paths, key names and whether a
proxy is set, never rc-file contents, `.env.local` values or credentials.

Each check runs in its own shell (zsh, or bash where zsh is missing) from the repo root,
exactly as written below, with stdout and stderr merged. The output is evidence: this
script doesn't judge pass or fail. Read each result against the check's row in
workstation-audit.md. A check's exit status is printed but isn't a verdict either
(`git config --get` exits 1 for an unset key, for example).

Usage:
  python3 scripts/ai/toolchain_audit.py --list
  python3 scripts/ai/toolchain_audit.py --section 1 --section 2
  python3 scripts/ai/toolchain_audit.py --all            # sections 1-6
  python3 scripts/ai/toolchain_audit.py --check pipx-shared-venv
  python3 scripts/ai/toolchain_audit.py --show older-patch-users   # print, don't run

On-request checks (the direct Node probe) run only when named with --check.
Each check runs in its own process group: a timeout stops everything it started.
Exit status: 0 every selected check ran, 1 one couldn't start or timed out, 2 usage.
Stdlib only and Python 3.9-safe.
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from collections import namedtuple

from check_node_ca import tilde

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECTIONS = {
    1: "Baseline",
    2: "Python and OpenSSL",
    3: "Node, sf, SFDMU",
    4: ".env.local",
    5: "PATH order in fresh shells",
    6: "Corporate CA (managed workstations)",
}
# validate_setup and npm ping are the slow ones; a silently dropped connection can hold
# npm ping for over a minute.
DEFAULT_TIMEOUT = 600
# Seconds to wait, once the shell has exited, for whatever it left holding its output.
HELD_OUTPUT_GRACE = 10

Check = namedtuple("Check", "section id title on_request command", defaults=(False, ""))

# The commands are the spec: keep them read-only, and keep each one a single run that
# needs nothing set by another (sections 5 and 6 capture the repo path themselves).
CHECKS = [
    Check(1, "validate-setup", "Validator, no auto-fix", command=r"""
cci task run validate_setup -o auto_fix false -o auto_fix_robot false
"""),
    Check(1, "gate-interpreter", "Gate interpreter", command=r"""
python3 scripts/ai/gate_python.py; echo "exit $?"
"""),
    Check(1, "envrc-allowed", ".envrc allowed", command=r"""
direnv status | grep 'Found RC allowed'
"""),
    Check(1, "signing", "Signing", command=r"""
git config --get commit.gpgsign; git config --get gpg.format; git config --get user.signingkey
"""),
    Check(2, "patch-current", "Patch is current", command=r"""
pyenv versions --bare; pyenv latest -k 3.13
"""),
    Check(2, "pyenv-global", "pyenv global", command=r"""
pyenv global; python3 scripts/ai/gate_python.py --carry-over "$(pyenv root)/versions/$(pyenv global)"
"""),
    Check(2, "envrc-python", ".envrc resolves it", command=r"""
direnv exec . python3 --version
"""),
    Check(2, "cci-python", "CCI's Python", command=r"""
cci version
"""),
    Check(2, "tui-venvs", "TUI venvs' Python", command=r"""
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r v; do [ -d "$v/.harness/tui-venv" ] && echo "$("$v/.harness/tui-venv/bin/python" -V 2>&1) $v"; done
"""),
    Check(2, "older-patch-users", "Other users of an older patch", command=r"""
(setopt nullglob 2>/dev/null || shopt -s nullglob; cur="$(pyenv latest 3.13)"; for v in "$(pipx environment --value PIPX_LOCAL_VENVS)"/*/; do h=$(sed -n 's/^home *= *//p' "$v/pyvenv.cfg"); case "$h" in *"/versions/$cur/"*) ;; *"/versions/3.13."*) echo "pipx $(basename "$v"): $(printf %s "$h" | sed "s#$HOME#~#")";; esac; done; for f in ~/.local/bin/*; do l=$(head -c 300 "$f" 2>/dev/null | LC_ALL=C sed -n '1{/^#!/p;}'); case "$l" in *"/versions/3.13."*) case "$l" in *"/versions/$cur/"*) ;; *) echo "script $(basename "$f"): $(printf %s "$l" | sed "s#$HOME#~#")";; esac;; esac; done)
"""),
    Check(2, "pipx-shared-venv", "pipx shared venv", command=r"""
(setopt nullglob 2>/dev/null || shopt -s nullglob; cur="$(pyenv latest 3.13)"; s="$(pipx environment --value PIPX_SHARED_LIBS)"; [ -n "$s" ] || { echo "pipx: PIPX_SHARED_LIBS not resolved"; exit; }; h=$(sed -n 's/^home *= *//p' "$s/pyvenv.cfg"); case "$h" in *"/versions/$cur/"*) ;; *) echo "shared: $(printf %s "$h" | sed "s#$HOME#~#") lib=$(ls "$s/lib" | paste -sd " " -)";; esac; for p in "$(pipx environment --value PIPX_LOCAL_VENVS)"/*/lib/python*/site-packages/pipx_shared.pth; do t=$(head -1 "$p"); l=$(basename "$(dirname "$(dirname "$p")")"); a=$(basename "${p%/lib/python*/site-packages/pipx_shared.pth}"); if [ ! -d "$t" ]; then echo "pth $a (missing): $(printf %s "$t" | sed "s#$HOME#~#")"; elif [ "$l" = python3.13 ]; then case "$t" in *"/lib/$l/"*) ;; *) echo "pth $a (other lib): $(printf %s "$t" | sed "s#$HOME#~#")";; esac; fi; done)
"""),
    Check(2, "gate-venv-python", "Gate venv's Python", command=r"""
.venv/bin/python -V; grep '^home' .venv/pyvenv.cfg
"""),
    Check(2, "openssl-kept", "openssl@3 kept", command=r"""
brew info openssl@3 | grep -i 'on request'
"""),
    Check(2, "ssl-linkage", "Linkage", command=r"""
otool -L "$(pyenv prefix "$(pyenv latest 3.13)")"/lib/python3.13/lib-dynload/_ssl*.so | grep ssl
"""),
    Check(2, "cci-ssl", "CCI's ssl", command=r"""
"$(pipx environment --value PIPX_LOCAL_VENVS)/cumulusci/bin/python" -c 'import ssl; print(ssl.OPENSSL_VERSION)'
"""),
    Check(3, "node", "Node from nvm", command=r"""
command -v node; node -v
"""),
    Check(3, "sf", "sf", command=r"""
sf --version; npm ls -g --depth=0 @salesforce/cli
"""),
    Check(3, "sfdmu", "SFDMU", command=r"""
sf plugins | grep -i sfdmu
"""),
    Check(4, "env-keys", "Key names only", command=r"""
[ -f .env.local ] && sed -nE 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_.]*)[[:space:]]*[=:].*/\2/p' .env.local
"""),
    Check(4, "env-ignored", "Ignored by git", command=r"""
git check-ignore -q .env.local && echo ignored
"""),
    Check(4, "chrome-for-testing", "Chrome for Testing (if set)", command=r"""
direnv exec . sh -c '"${CHROME_BINARY:-$CHROME_BIN}" --version; "$CHROMEDRIVER_PATH" --version'
"""),
    Check(5, "path-outside-repo", "Terminal opened outside the repo, then cd in", command=r"""
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && command -v python3 node' zsh "$repo")
"""),
    Check(5, "path-started-in-repo", "Terminal that starts in the repo", command=r"""
env -i HOME="$HOME" TERM=xterm zsh -lic 'command -v python3 node'
"""),
    Check(6, "ca-non-interactive", "NODE_EXTRA_CA_CERTS, non-interactive shell", command=r"""
env -i HOME="$HOME" TERM=xterm zsh -c   'echo "[$NODE_EXTRA_CA_CERTS]"'
"""),
    Check(6, "ca-terminal", "NODE_EXTRA_CA_CERTS, Terminal-window shell", command=r"""
env -i HOME="$HOME" TERM=xterm zsh -lic 'echo "[$NODE_EXTRA_CA_CERTS]"'
"""),
    Check(6, "ca-bundles", "Every assigned bundle is in the exported file", command=r"""
python3 scripts/ai/check_node_ca.py
"""),
    Check(6, "tls-proxy-env", "TLS override and proxy variables", command=r"""
env -i HOME="$HOME" TERM=xterm zsh -lic \
  'echo "[TLS_REJECT=$NODE_TLS_REJECT_UNAUTHORIZED][HTTPS_PROXY=${HTTPS_PROXY:+set}][https_proxy=${https_proxy:+set}][HTTP_PROXY=${HTTP_PROXY:+set}][http_proxy=${http_proxy:+set}]"'
"""),
    Check(6, "npm-config-ping", "npm's settings and one npm ping", command=r"""
repo="$PWD"
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && for k in ca cafile strict-ssl registry proxy https-proxy; do v=$(npm config get "$k" 2>&1); case "$v" in *"is protected"*) v="set (credentials hidden)";; esac; echo "$k=$v"; done | sed -E "s#(://)[^/@]+@#\\1<redacted>@#g" && npm ping --fetch-retries=0 --loglevel=notice 2>&1 | sed -E "s#(://)[^/@]+@#\\1<redacted>@#g"' zsh "$repo")
"""),
    Check(6, "ca-direct-probe", "Direct Node probe", on_request=True, command=r"""
repo="$PWD"
probe='setTimeout(() => { console.log("timeout"); process.exit(2) }, 15000); require("https").get("https://registry.npmjs.org/", r => { console.log(r.statusCode); process.exit(0) }).on("error", e => { console.log(e.code || e.message); process.exit(1) })'
(cd /tmp && env -i HOME="$HOME" TERM=xterm zsh -lic \
  'cd "${1:?repo path missing}" && eval "$(direnv export zsh 2>/dev/null)" && node -e "$2"' zsh "$repo" "$probe")
"""),
]


def command(check):
    return check.command.strip("\n")


def pick_shell(requested):
    """The shell to run the checks in, or None when the requested one isn't on PATH."""
    if requested:
        return shutil.which(requested)
    return shutil.which("zsh") or shutil.which("bash") or "/bin/sh"


def select(args):
    sections = set(SECTIONS) if args.all else set(args.section)
    named = set(args.check)
    return [c for c in CHECKS
            if c.id in named or (c.section in sections and not c.on_request)]


def main_checkout(repo):
    """The main checkout when `repo` is a linked worktree, else None.

    The audit belongs to the main checkout: `.venv` and `.env.local` live there, so a
    worktree reports them missing. git can't answer (not a checkout, too old for
    --path-format) means no note rather than a guess.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--path-format=absolute",
             "--git-dir", "--git-common-dir"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = proc.stdout.splitlines()
    if proc.returncode != 0 or len(lines) != 2:
        return None
    git_dir, common_dir = (os.path.realpath(line) for line in lines)
    return os.path.dirname(common_dir) if git_dir != common_dir else None


def finish(out):
    sys.stdout.write(out if not out or out.endswith("\n") else out + "\n")


def kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        pass  # already gone


def run(check, shell, repo, timeout, grace=HELD_OUTPUT_GRACE):
    """Run one check and print its output; False when it timed out or couldn't start.

    The shell leads its own process group, so a timeout stops everything it started
    (npm, cci, the fresh zsh shells), not just the shell. A process left holding the
    output open after the shell has exited (a background job from a startup file) is
    stopped after `grace` seconds instead of holding the check until the timeout. An
    interrupt (Ctrl-C) stops the group too, since its own session doesn't get the
    terminal's SIGINT.
    """
    print(f"== §{check.section} {check.id}: {check.title}", flush=True)
    try:
        proc = subprocess.Popen([shell, "-c", command(check)], cwd=repo,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, errors="replace",
                                start_new_session=True)
    except OSError as exc:
        print(f"[could not start: {exc}]", flush=True)
        return False
    deadline = time.monotonic() + timeout
    exited_at = None
    try:
        while True:
            try:
                out, _ = proc.communicate(timeout=0.5)
                break
            except subprocess.TimeoutExpired:
                now = time.monotonic()
                if exited_at is None and proc.poll() is not None:
                    exited_at = now
                if now >= deadline:
                    kill_group(proc)
                    finish(proc.communicate()[0])
                    print(f"[timeout after {timeout}s]", flush=True)
                    return False
                if exited_at is not None and now - exited_at >= grace:
                    kill_group(proc)
                    finish(proc.communicate()[0])
                    print(f"[exit {proc.returncode}; stopped what it left holding its "
                          f"output {grace}s after it exited]", flush=True)
                    return True
    except BaseException:
        # Ctrl-C (or anything else) mid-check: the group is in its own session, so the
        # terminal's SIGINT never reached it. Stop and reap it before the interrupt leaves.
        kill_group(proc)
        proc.communicate()
        raise
    finish(out)
    print(f"[exit {proc.returncode}]", flush=True)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the read-only toolchain audit's commands (workstation-audit.md).")
    parser.add_argument("--section", type=int, action="append", default=[],
                        choices=sorted(SECTIONS), help="run every check in this section")
    parser.add_argument("--check", action="append", default=[], metavar="ID",
                        help="run this check (repeatable); see --list")
    parser.add_argument("--all", action="store_true", help="run sections 1-6")
    parser.add_argument("--list", action="store_true", help="list the checks and exit")
    parser.add_argument("--show", metavar="ID", help="print a check's command; don't run it")
    parser.add_argument("--repo", default=REPO,
                        help="checkout to audit (default: the one holding this script)")
    parser.add_argument("--shell", help="shell to run the commands in (default: zsh, else bash)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"seconds per check (default {DEFAULT_TIMEOUT})")
    args = parser.parse_args(argv)
    by_id = {c.id: c for c in CHECKS}

    if args.list:
        for section, name in SECTIONS.items():
            print(f"§{section} {name}")
            for c in CHECKS:
                if c.section == section:
                    note = "  (on request: name it with --check)" if c.on_request else ""
                    print(f"    {c.id:<22} {c.title}{note}")
        return 0
    if args.show:
        if args.show not in by_id:
            parser.error(f"unknown check id: {args.show} (see --list)")
        print(command(by_id[args.show]))
        return 0
    if not (args.section or args.check or args.all):
        parser.error("choose --section N, --check ID, --all or --list")
    unknown = [i for i in args.check if i not in by_id]
    if unknown:
        parser.error(f"unknown check id(s): {', '.join(unknown)} (see --list)")
    if args.timeout <= 0:
        parser.error("--timeout must be a positive number of seconds")

    repo = os.path.abspath(args.repo)
    if not os.path.isfile(os.path.join(repo, "scripts", "ai", "gate_python.py")):
        parser.error(f"not an rlm-base-dev checkout: {repo}")
    shell = pick_shell(args.shell)
    if not shell:
        parser.error(f"shell not found: {args.shell}")
    home = os.path.expanduser("~")
    print(f"# toolchain audit: repo {tilde(repo, home)}, shell {shell}", flush=True)
    primary = main_checkout(repo)
    if primary:
        print(f"# note: this is a linked worktree. The audit is meant for the main checkout "
              f"({tilde(primary, home)}), where .venv and .env.local live: run it there or pass "
              f"--repo", flush=True)
    ok = True
    for check in select(args):
        ok = run(check, shell, repo, args.timeout) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
