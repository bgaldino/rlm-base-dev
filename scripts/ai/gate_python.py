#!/usr/bin/env python3
"""Find the one interpreter that runs `pr_gate.py`, and prove it can run every check.

The gate fails a check whose dependency is missing (MISSING-DEP), which is right in CI and
wrong as a surprise: on a workstation whose only CumulusCI venv lacks `textual`, every
build-harness change fails the gate for a setup reason, not a code reason. So there is one
declared gate interpreter, found the same way by every caller (the Claude Code Stop hook in
`.claude/hooks/stop_gate.py` and `cci task run validate_setup`):

1. `$RLM_GATE_PYTHON`, if set — for a venv kept somewhere else.
2. `<main checkout>/.venv/bin/python` — the default. A git worktree resolves to the main
   checkout's `.venv`, so a loop builder in `.loop/wt-*` uses the same interpreter.

Create the default with (Python 3.13 matches CI):

    python3.13 -m venv .venv
    .venv/bin/python -m pip install $(.venv/bin/python scripts/ai/pr_gate.py --requirements --all)

Stdlib only and Python 3.9-safe on purpose: the hook imports this under whatever `python3`
the shell has (macOS ships 3.9), and only the gate interpreter itself needs 3.11+.

Usage:
    python3 scripts/ai/gate_python.py      # print the interpreter; exit 1 with the reason if unusable

Exit codes: 0 = usable · 1 = missing or incomplete.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

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


def resolve(start: Path) -> Tuple[Optional[Path], str]:
    """(interpreter, where it came from). The interpreter is None when nothing is configured."""
    override = os.environ.get(ENV_VAR)
    if override:
        return Path(override), f"${ENV_VAR}"
    root = main_checkout(start)
    if root is None:
        return None, "not inside a git checkout"
    return root / ".venv" / "bin" / "python", f"{root}/.venv"


def problems(start: Path) -> Tuple[Optional[Path], List[str]]:
    """(interpreter, every reason it cannot run the whole gate). An empty list means usable."""
    python, source = resolve(start)
    if python is None:
        return None, [source]
    if not python.exists():
        return python, [f"{python} does not exist (from {source})"]
    root = main_checkout(start) or start
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
    report = json.loads(out.stdout)
    found: List[str] = []
    if tuple(report["version"]) < tuple(report["needs"]):
        found.append(f"{python} is Python {'.'.join(map(str, report['version']))}, "
                     f"needs {'.'.join(map(str, report['needs']))}+")
    if report["missing"]:
        found.append(f"{python} lacks: {', '.join(report['missing'])}")
    return python, found


def main() -> int:
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
