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
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

#: Set before re-exec so a second pass cannot loop. See ensure_pyyaml.
_REEXEC_SENTINEL = "_RLM_GATE_REEXECED"

#: A git hook sets this so the venv bootstrap never runs mid-push. isatty() is
#: NOT a reliable proxy for "am I in a hook": git hooks inherit the terminal, so
#: an interactive `git push` DOES have a TTY and would have triggered a pip
#: install in the middle of the push — the exact surprise the TTY check was
#: meant to prevent. Explicit beats inferred.
_NO_BOOTSTRAP = "RLM_GATE_NO_BOOTSTRAP"


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
    ]
    # PATH-resolved python. On a set-up workstation .envrc puts the pyenv shims
    # on PATH, so these are the pinned 3.13 - and they are what makes
    # _bootstrap_venv reachable at all, since without them a clone with no
    # .venv and no pipx has nothing new enough to build a venv FROM.
    for exe in ("python3", "python"):
        found = shutil.which(exe)
        if found:
            out.append(found)
    out += ["/usr/bin/python3", "/opt/homebrew/bin/python3"]
    # De-duplicate, preserving priority order.
    seen, ordered = set(), []
    for c in out:
        if c and c not in seen:
            seen.add(c)
            ordered.append(c)
    return ordered


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


def _bootstrap_venv():
    """Create .venv and install requirements-dev.txt. Returns its python, or None.

    WHERE this may run is the whole design. Installing packages is the right fix
    for a fresh clone, and this repo already does it elsewhere - ./tui-cci builds
    .harness/tui-venv on first run. But a `git push` that blocks for a silent
    90 seconds while pip downloads reads as a broken hook, and the reflex it
    trains is `--no-verify`, which defeats the gate entirely.

    So: bootstrap when a human is watching (a TTY) or asked for it explicitly
    (RLM_GATE_BOOTSTRAP=1). The pre-push hook sets neither, and instead fails
    fast with the exact command. The slow path only happens interactively.
    """
    if os.environ.get(_NO_BOOTSTRAP) == "1":
        return None
    if not (sys.stdout.isatty() or os.environ.get("RLM_GATE_BOOTSTRAP") == "1"):
        return None
    req = REPO_ROOT / "requirements-dev.txt"
    if not req.exists():
        return None

    venv_py = REPO_ROOT / ".venv" / "bin" / "python"
    base = None
    for cand in _candidates():
        if cand and Path(cand).exists() and str(cand) != str(venv_py):
            probe = subprocess.run(
                [cand, "-c", "import sys; sys.exit(0 if sys.version_info >= {} "
                             "else 9)".format(_MIN_PY)], capture_output=True)
            if probe.returncode == 0:
                base = cand
                break
    if not base:
        return None

    if not venv_py.exists():
        sys.stderr.write(f"gate: creating .venv with {base} ...\n")
        if subprocess.run([base, "-m", "venv", str(REPO_ROOT / ".venv")]).returncode:
            return None
    sys.stderr.write("gate: installing requirements-dev.txt (first run only) ...\n")
    if subprocess.run([str(venv_py), "-m", "pip", "install", "-q", "-r",
                       str(req)]).returncode:
        return None
    return str(venv_py) if venv_py.exists() else None


def ensure_pyyaml(script_path):
    """Re-exec `script_path` under an interpreter that has PyYAML AND is new
    enough to parse these scripts.

    Returns normally if the current interpreter already qualifies. Otherwise
    re-execs (this call does not return) or exits 2. Never returns without a
    working `import yaml` on a supported Python.
    """
    if _usable():
        return

    # Precise loop protection: count re-execs rather than inferring from inodes.
    # One hop is all a correct resolution ever needs.
    if os.environ.get(_REEXEC_SENTINEL):
        sys.stderr.write(
            "FATAL: re-exec'd once and PyYAML is still missing.\n"
            f"  interpreter: {sys.executable}\n"
            "  Refusing to loop. Install PyYAML there, or set RLM_PYTHON.\n"
        )
        sys.exit(2)

    tried = []
    for cand in _candidates():
        if not cand:
            continue
        tried.append(cand)
        path = Path(cand)
        if not path.exists():
            continue
        # NOTE: do NOT skip on samefile(sys.executable). `.venv/bin/python` is a
        # symlink to the base interpreter it was built from, so samefile() is
        # True whenever the gate is started by that base python — which is the
        # single most common case (a pyenv shim, which has no PyYAML). The guard
        # meant to prevent an exec loop was instead refusing the project venv
        # exactly when it was needed, silently falling through to pipx. Loop
        # protection is the _REEXEC_SENTINEL below, which is precise: it counts
        # actual re-execs instead of guessing from inodes. A venv python and its
        # base are the same FILE but not the same ENVIRONMENT, which is the
        # whole point of a venv.
        probe = subprocess.run([cand, "-c", _PROBE], capture_output=True)
        if probe.returncode == 0:
            os.environ[_REEXEC_SENTINEL] = cand
            os.execv(cand, [cand, str(Path(script_path).resolve())] + sys.argv[1:])

    # Nothing on disk qualifies. If a human is watching, build the venv the
    # README prescribes rather than just telling them to.
    boot = _bootstrap_venv()
    if boot:
        os.execv(boot, [boot, str(Path(script_path).resolve())] + sys.argv[1:])

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
