#!/usr/bin/env python3
"""Check that NODE_EXTRA_CA_CERTS covers every CA bundle the shell files assign to it.

A managed workstation can carry two tool-managed blocks that each set NODE_EXTRA_CA_CERTS
to their own bundle; the later one wins, so Node silently loses the other's certificates.
A registry with a public certificate still answers, so `npm ping` can't show it.

This starts a fresh non-interactive and a fresh login-interactive zsh with xtrace on, so
zsh itself reports every assignment to the variable, already expanded, from every startup
file it reads (/etc/zsh*, ZDOTDIR, sourced files). It then checks what each shell actually
exports (printenv) and that the exported file holds every certificate of every assigned
bundle (by SHA-256 of each certificate's DER bytes). zsh only: bash startup files are out
of scope.

Read-only. Only trace lines that assign NODE_EXTRA_CA_CERTS are parsed, and of the trace
only those assigned paths are printed (home as ~), with certificate counts; never file
contents. A startup file that sets a PS4 without its trailing "> " hides the assignments
traced after it; the export check still runs.
Exit status: 0 pass, 1 fail, 3 not applicable (nothing assigns or exports the variable).

Usage: python3 scripts/ai/check_node_ca.py
Stdlib only and Python 3.9-safe. Run with the repo's audit (workstation-audit.md §6).
"""
import argparse
import base64
import hashlib
import os
import re
import shlex
import subprocess
import sys
import tempfile

# An xtrace line: "+<file>:<line>> <command words>".
TRACE_LINE = re.compile(r"^\+[^>]*> (.*)$")
NAME = "NODE_EXTRA_CA_CERTS="
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PEM = re.compile(r"-----BEGIN CERTIFICATE-----(.*?)-----END CERTIFICATE-----", re.S)
SENTINEL = "__NODE_EXTRA_CA_CERTS__="
NA = 3


def tilde(path, home):
    return "~" + path[len(home):] if path == home or path.startswith(home + "/") else path


def tilde_list(value, home):
    return ":".join(tilde(p, home) for p in value.split(":"))


def assigned_from_trace(trace):
    """Bundle paths assigned to NODE_EXTRA_CA_CERTS in a zsh xtrace, in order.

    Counts `export`/`typeset`/`declare` words (any position, so `export A=1 NAME=…` too)
    and bare assignment statements. Skips `local` (never reaches the environment) and a
    one-command prefix (`NAME=… cmd`), which zsh traces with the command after it.
    """
    out = []
    for line in trace.splitlines():
        m = TRACE_LINE.match(line)
        if not m or NAME not in m.group(1):
            continue
        try:
            words = shlex.split(m.group(1))
        except ValueError:
            continue
        if not words:
            continue
        if words[0] in ("export", "typeset", "declare", "readonly"):
            values = [w[len(NAME):] for w in words[1:] if w.startswith(NAME)]
        elif all(ASSIGNMENT.match(w) for w in words):
            values = [w[len(NAME):] for w in words if w.startswith(NAME)]
        else:
            continue
        for value in values:
            for part in value.split(":"):
                if part and part not in out:
                    out.append(part)
    return out


def fingerprints(path):
    """SHA-256 of each certificate in a PEM file; empty if it can't be read."""
    try:
        with open(path, encoding="ascii", errors="replace") as f:
            text = f.read()
    except OSError:
        return set()
    out = set()
    for body in PEM.findall(text):
        try:
            der = base64.b64decode("".join(body.split()), validate=False)
        except ValueError:
            continue
        out.add(hashlib.sha256(der).hexdigest())
    return out


def run_shell(home, flags):
    """(exported value or None if zsh failed, assigned paths) for a fresh traced zsh."""
    script = 'printf "\\n%s%s\\n" "' + SENTINEL + '" "$(printenv NODE_EXTRA_CA_CERTS)"'
    try:
        r = subprocess.run(["env", "-i", "HOME=" + home, "TERM=xterm", "zsh", "-x", flags, script],
                           cwd=tempfile.gettempdir(), stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None, []
    value = None
    for line in reversed(r.stdout.splitlines()):
        if line.startswith(SENTINEL):
            value = line[len(SENTINEL):]
            break
    return value, assigned_from_trace(r.stderr)


def evaluate(home, assigned, values):
    """(status, lines) for the assigned bundles and each shell's exported value."""
    lines, fail = [], False
    if any(v is None for v in values.values()):
        lines = [f"FAIL: zsh {f} didn't run (zsh missing, or no finish within two minutes)"
                 for f, v in values.items() if v is None]
        return 1, lines
    if not assigned and not any(values.values()):
        return NA, ["n.a.: no zsh startup file assigns NODE_EXTRA_CA_CERTS and no shell exports it"]
    for flags, value in values.items():
        label = "zsh " + flags
        if value is None:
            lines.append(f"FAIL: {label} didn't run, so its value is unknown")
            fail = True
        elif not value:
            lines.append(f"FAIL: {label} exports nothing")
            fail = True
        elif ":" in value:
            lines.append(f"FAIL: {label} exports a colon-separated list ({tilde_list(value, home)}); Node loads none of it")
            fail = True
        elif not os.path.isfile(value):
            lines.append(f"FAIL: {label} exports {tilde(value, home)}, which doesn't exist")
            fail = True
        elif not fingerprints(value):
            lines.append(f"FAIL: {label} exports {tilde(value, home)}, which holds no PEM certificates")
            fail = True
        else:
            lines.append(f"ok: {label} exports {tilde(value, home)} ({len(fingerprints(value))} certs)")
    distinct = {v for v in values.values() if v}
    if len(distinct) > 1:
        lines.append("FAIL: the two shells export different files")
        fail = True
    good = [v for v in values.values() if v and ":" not in v and os.path.isfile(v)]
    effective = fingerprints(good[0]) if good else set()
    for path in assigned:
        if not os.path.isfile(path):
            lines.append(f"note: {tilde(path, home)} is assigned but doesn't exist")
            continue
        certs = fingerprints(path)
        if not certs:
            lines.append(f"note: {tilde(path, home)} is assigned but holds no PEM certificates")
            continue
        missing = len(certs - effective)
        if missing:
            lines.append(f"FAIL: {tilde(path, home)}: {missing} of its {len(certs)} certs aren't in the exported file")
            fail = True
        else:
            lines.append(f"ok: {tilde(path, home)}: all {len(certs)} certs are in the exported file")
    return (1 if fail else 0), lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--home", default=os.path.expanduser("~"), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    values, assigned = {}, []
    for flags in ("-c", "-lic"):
        values[flags], paths = run_shell(a.home, flags)
        assigned += [p for p in paths if p not in assigned]
    status, lines = evaluate(a.home, assigned, values)
    print("\n".join(lines))
    print({0: "PASS", 1: "FAIL", NA: "N.A."}[status])
    return status


if __name__ == "__main__":
    sys.exit(main())
