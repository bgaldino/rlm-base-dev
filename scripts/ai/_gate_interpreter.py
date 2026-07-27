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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _candidates():
    """Interpreters to try, in priority order, when the current one lacks PyYAML.

    Order matters and follows the repo's documented environment (README Step 5,
    docs/guides/dev-environment-setup.md):

      1. RLM_PYTHON        explicit override always wins
      2. $VIRTUAL_ENV      an already-activated venv (direnv or `source`)
      3. .venv             the project venv the README designates for running
                           scripts/ and tasks/ outside CCI
      4. .harness/tui-venv the build-harness venv, auto-created by ./tui-cci
      5. pipx cumulusci    LAST RESORT. This one works only by accident: the CCI
                           venv has PyYAML because CumulusCI depends on it, not
                           because anyone chose it as the script runtime. Keeping
                           it means an unprepared clone still runs; putting it
                           last means a prepared clone uses its own venv.
      6. system python3
    """
    out = []
    if os.environ.get("RLM_PYTHON"):
        out.append(os.environ["RLM_PYTHON"])
    if os.environ.get("VIRTUAL_ENV"):
        out.append(str(Path(os.environ["VIRTUAL_ENV"]) / "bin" / "python"))
    out += [
        str(REPO_ROOT / ".venv" / "bin" / "python"),
        str(REPO_ROOT / ".harness" / "tui-venv" / "bin" / "python"),
        str(Path.home() / ".local/pipx/venvs/cumulusci/bin/python"),
        "/usr/bin/python3",
        "/opt/homebrew/bin/python3",
    ]
    return out


#: Minimum Python for the gate scripts. Matches pyproject's
#: [tool.build_harness] requires_python = ">=3.11" and buys `tomllib`.
#: This floor is not cosmetic: /usr/bin/python3 on macOS is 3.9 AND ships
#: PyYAML, so a yaml-only check happily selects it and the scripts then die on
#: 3.12+ syntax — exiting non-zero in a way that reads as findings rather than
#: as "did not run". Version and yaml must BOTH be satisfied.
_MIN_PY = (3, 11)

_PROBE = (
    "import sys, yaml; "
    "sys.exit(0 if sys.version_info >= {} else 9)".format(_MIN_PY)
)


def _usable(version_info=None):
    if version_info is None:
        version_info = sys.version_info
    if tuple(version_info[:2]) < _MIN_PY:
        return False
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        return False


def ensure_pyyaml(script_path):
    """Re-exec `script_path` under an interpreter that has PyYAML AND is new
    enough to parse these scripts.

    Returns normally if the current interpreter already qualifies. Otherwise
    re-execs (this call does not return) or exits 2. Never returns without a
    working `import yaml` on a supported Python.
    """
    if _usable():
        return

    tried = []
    for cand in _candidates():
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
        probe = subprocess.run([cand, "-c", _PROBE], capture_output=True)
        if probe.returncode == 0:
            os.execv(cand, [cand, str(Path(script_path).resolve())] + sys.argv[1:])

    need = ".".join(str(n) for n in _MIN_PY)
    sys.stderr.write(
        f"FATAL: no interpreter found with PyYAML on Python >= {need}.\n"
        f"  current: {sys.executable} "
        f"({sys.version_info.major}.{sys.version_info.minor})\n"
        f"  tried:   {', '.join(tried)}\n"
        "\n"
        "  Prepare the project venv (README Step 5):\n"
        "      python -m venv .venv && source .venv/bin/activate\n"
        "      pip install -r requirements-dev.txt\n"
        "  or point RLM_PYTHON at an interpreter that has PyYAML.\n"
        "  Refusing to continue - a gate that cannot run must not report clean.\n"
    )
    sys.exit(2)
