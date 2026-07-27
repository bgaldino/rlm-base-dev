#!/usr/bin/env python
"""Shared interpreter guard for the pre-push gate scripts (todo 080).

Why this exists, in one sentence: on a dev box here `python` is a pyenv shim
without PyYAML, so a gate that dies on `import yaml` prints a traceback, exits
non-zero, and — if anyone wraps it in a `|| true` or reads only its stdout —
gets recorded as "no findings". A check that could not run must never read as
a pass, so resolve a usable interpreter explicitly or exit 2.

Confirmed on this repo's dev machines: neither `python` nor `python3` has
PyYAML; `~/.local/pipx/venvs/cumulusci/bin/python` does. That is why
AGENTS.md's own `python scripts/ai/generate_cci_reference.py` instruction
crashes, and why the empty diff afterwards looks like success.

Usage, as the FIRST thing a gate script does — before importing yaml:

    from _gate_interpreter import ensure_pyyaml
    ensure_pyyaml(__file__)
    import yaml
"""

import os
import subprocess
import sys
from pathlib import Path

#: Interpreters to try, in order, when the current one lacks PyYAML.
#: RLM_PYTHON wins so a machine with a different layout can override without
#: editing this file.
_CANDIDATES = (
    str(Path.home() / ".local/pipx/venvs/cumulusci/bin/python"),
    "/usr/bin/python3",
    "/opt/homebrew/bin/python3",
)


def ensure_pyyaml(script_path):
    """Re-exec `script_path` under an interpreter that has PyYAML.

    Returns normally if the current interpreter already has it. Otherwise
    re-execs (this call does not return) or exits 2. Never returns without a
    working `import yaml`.
    """
    try:
        import yaml  # noqa: F401
        return
    except ImportError:
        pass

    tried = []
    candidates = []
    if os.environ.get("RLM_PYTHON"):
        candidates.append(os.environ["RLM_PYTHON"])
    candidates.extend(_CANDIDATES)

    for cand in candidates:
        if not cand:
            continue
        tried.append(cand)
        path = Path(cand)
        if not path.exists():
            continue
        try:
            # Never re-exec ourselves: that would loop forever.
            if path.samefile(sys.executable):
                continue
        except OSError:
            continue
        probe = subprocess.run([cand, "-c", "import yaml"], capture_output=True)
        if probe.returncode == 0:
            os.execv(cand, [cand, str(Path(script_path).resolve())] + sys.argv[1:])

    sys.stderr.write(
        "FATAL: no interpreter with PyYAML found.\n"
        f"  current: {sys.executable}\n"
        f"  tried:   {', '.join(tried)}\n"
        "  Set RLM_PYTHON to a python that has PyYAML, or `pip install pyyaml`.\n"
        "  Refusing to continue - a gate that cannot run must not report clean.\n"
    )
    sys.exit(2)
