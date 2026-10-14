#!/usr/bin/env python3
"""Find the one interpreter that runs `pr_gate.py`, and prove it can run every check.

The gate fails a check whose dependency is missing (MISSING-DEP), which is right in CI and
wrong as a surprise: on a workstation whose only CumulusCI venv lacks `textual`, every
build-harness change fails the gate for a setup reason, not a code reason. So there is one
declared gate interpreter, found the same way by every caller (the Claude Code Stop hook in
`.claude/hooks/stop_gate.py`, `cci task run validate_setup`, `pr_gate.py` itself when it
re-runs under it, and `scripts/bash/update-toolchain.sh`):

1. `$RLM_GATE_PYTHON`, if set — for a venv kept somewhere else.
2. `<main checkout>/.venv/bin/python` — the default. A git worktree resolves to the main
   checkout's `.venv`, so a loop builder in `.loop/wt-*` uses the same interpreter.

Create the default with (Python 3.13 matches CI):

    python3.13 -m venv .venv
    .venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)

The setup guides carry the same steps: docs/guides/local-installation.md (Step 6) and
docs/guides/dev-environment-setup.md, whose update script (scripts/bash/update-toolchain.sh)
rebuilds the venv after a Python patch bump and reinstalls these requirements.

Stdlib only and Python 3.9-safe on purpose: the hook imports this under whatever `python3`
the shell has (macOS ships 3.9), and only the gate interpreter itself needs 3.11+.

Usage:
    python3 scripts/ai/gate_python.py      # print the interpreter; exit 1 with the reason if unusable
    python3 scripts/ai/gate_python.py --default-venv   # print <main checkout>/.venv; exit 1 outside git
    python3 scripts/ai/gate_python.py --carry-over VENV  # requirements that restore VENV's own packages

Exit codes: 0 = usable (or the flag's output printed) · 1 = missing or incomplete, or not in a
git checkout · 2 = usage error.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import unquote, urlparse

ENV_VAR = "RLM_GATE_PYTHON"

# Run *under the gate interpreter*, so pr_gate's own matrix decides what "complete" means: its
# DEPS map and import probe for packages, and the highest `min_python` of any check for the
# version. Restating either here would let the two drift.
_PROBE = (
    "import json, sys; sys.path.insert(0, sys.argv[1]); import pr_gate; "
    "print(json.dumps({'version': list(sys.version_info[:2]), "
    "'needs': list(max([c.get('min_python') or (0,) for c in pr_gate.CHECKS] or [(0,)])), "
    "'missing': [p for p, m in pr_gate.DEPS.items() if not pr_gate.have_module(m)]}))"
)


def main_checkout(start: Path) -> Optional[Path]:
    """The main checkout's root, also from inside a linked worktree; None outside git."""
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return Path(out.stdout.strip()).parent


def checkout_root(start: Path) -> Optional[Path]:
    """The root of the checkout (main or linked worktree) that contains `start`."""
    try:
        out = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return Path(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None


def default_venv(start: Path) -> Optional[Path]:
    """The default gate venv, `<main checkout>/.venv`, whether or not $RLM_GATE_PYTHON is set."""
    root = main_checkout(start)
    return None if root is None else root / ".venv"


def resolve(start: Path) -> Tuple[Optional[Path], str]:
    """(interpreter, where it came from). The interpreter is None when nothing is configured."""
    override = os.environ.get(ENV_VAR)
    if override:
        return Path(override), f"${ENV_VAR}"
    venv = default_venv(start)
    if venv is None:
        return None, "not inside a git checkout"
    return venv / "bin" / "python", str(venv)


def problems(start: Path) -> Tuple[Optional[Path], List[str]]:
    """(interpreter, every reason it cannot run the whole gate). An empty list means usable."""
    python, source = resolve(start)
    if python is None:
        return None, [source]
    if not python.exists():
        return python, [f"{python} does not exist (from {source})"]
    # The interpreter is shared (the main checkout's .venv), but what it must be able to run
    # is the matrix of the checkout being verified: a worktree's branch may raise
    # `min_python` or add a dependency the main checkout's copy doesn't know about yet.
    root = checkout_root(start) or start
    try:
        out = subprocess.run(
            [str(python), "-c", _PROBE, str(root / "scripts" / "ai")],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return python, [f"{python} could not run: {exc}"]
    if out.returncode != 0:
        tail = (out.stderr.strip().splitlines() or ["no output"])[-1]
        return python, [f"{python} could not import pr_gate: {tail}"]
    report = None
    for line in reversed(out.stdout.splitlines()):  # the report, wherever other output lands
        try:
            parsed = json.loads(line)
        except ValueError:
            continue
        if isinstance(parsed, dict) and {"version", "needs", "missing"} <= parsed.keys():
            report = parsed
            break
    if report is None:
        return python, [f"{python} probe printed no readable report: {out.stdout[-200:]!r}"]
    found: List[str] = []
    if tuple(report["version"]) < tuple(report["needs"]):
        found.append(f"{python} is Python {'.'.join(map(str, report['version']))}, "
                     f"needs {'.'.join(map(str, report['needs']))}+")
    if report["missing"]:
        found.append(f"{python} lacks: {', '.join(report['missing'])}")
    return python, found


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def carry_over(venv: Path) -> List[str]:
    """Requirements that put back what `venv` holds, for `scripts/bash/update-toolchain.sh` to
    reinstall after it rebuilds the gate venv with `venv --clear`.

    Read from the venv's site-packages by the *calling* interpreter, so it works when the
    venv's own Python is gone (the usual reason for the rebuild). Only top-level packages
    are listed — nothing else in the venv requires them — each pinned as installed, so their
    dependencies resolve afresh instead of being frozen as if someone asked for them.
    Editable installs come back as `-e <path>` and VCS installs at their commit. A cycle with
    nothing outside it requiring it is kept whole rather than lost.
    """
    from importlib import metadata  # 3.8+; local so the hook's import of this module stays cheap

    # One unreadable distribution costs only itself: an exception here would lose the whole list,
    # and the caller clears the venv next.
    sites = [str(p) for p in sorted(venv.glob("lib/python*/site-packages"))]
    dists: Dict[str, "metadata.Distribution"] = {}
    for dist in metadata.distributions(path=sites):
        try:
            name = dist.metadata["Name"]
        except Exception:
            continue
        if name and _norm(name) not in ("pip", "setuptools", "wheel"):
            dists.setdefault(_norm(name), dist)
    needs: Dict[str, Set[str]] = {}
    for key, dist in dists.items():
        needs[key] = set()
        try:
            requires = dist.requires or []
        except Exception:
            requires = []
        for req in requires:
            spec, _, marker = req.partition(";")
            if "extra" in marker:  # optional: required only when someone asked for that extra
                continue
            head = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", spec)
            if head and _norm(head.group(1)) in dists:
                needs[key].add(_norm(head.group(1)))
    required = set().union(*needs.values()) if needs else set()
    keep = [k for k in dists if k not in required]
    reached: Set[str] = set()
    stack = list(keep)
    while stack:
        key = stack.pop()
        if key not in reached:
            reached.add(key)
            stack.extend(needs[key])
    # Whatever no top-level package reaches sits in a dependency cycle; keep one member of each.
    for key in sorted(dists):
        if key not in reached:
            keep.append(key)
            stack = [key]
            while stack:
                k = stack.pop()
                if k not in reached:
                    reached.add(k)
                    stack.extend(needs[k])
    lines = []
    for key in sorted(keep):
        dist = dists[key]
        try:
            direct = json.loads(dist.read_text("direct_url.json") or "{}")
        except (OSError, ValueError):  # half-written by an interrupted install: pin it instead
            direct = {}
        if not isinstance(direct, dict):
            direct = {}
        url, vcs = direct.get("url", ""), direct.get("vcs_info") or {}
        if direct.get("dir_info", {}).get("editable") and url.startswith("file://"):
            lines.append(f"-e {unquote(urlparse(url).path)}")
        elif vcs.get("vcs") and url:
            lines.append(f"{dist.metadata['Name']} @ {vcs['vcs']}+{url}@{vcs.get('commit_id', '')}"
                         .rstrip("@"))
        else:
            lines.append(f"{dist.metadata['Name']}=={dist.version}")
    return lines


USAGE = "usage: gate_python.py [--default-venv | --carry-over VENV]"


def main() -> int:
    args = sys.argv[1:]
    if args[:1] == ["--carry-over"]:
        # Exactly one non-empty VENV. Anything else falling through to the probe would print the
        # interpreter path where a caller expects requirements.
        if len(args) != 2 or not args[1]:
            print(USAGE, file=sys.stderr)
            return 2
        for line in carry_over(Path(args[1])):
            print(line)
        return 0
    if args and args != ["--default-venv"]:
        print(USAGE, file=sys.stderr)
        return 2
    if args == ["--default-venv"]:
        venv = default_venv(Path.cwd())
        if venv is None:
            print("not inside a git checkout", file=sys.stderr)
            return 1
        print(venv)
        return 0
    python, found = problems(Path.cwd())
    if found:
        for line in found:
            print(f"gate interpreter unusable: {line}", file=sys.stderr)
        print("create it as described in scripts/ai/gate_python.py", file=sys.stderr)
        return 1
    print(python)
    return 0


if __name__ == "__main__":
    sys.exit(main())
