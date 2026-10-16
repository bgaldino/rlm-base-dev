"""Run an ``sf`` CLI command with ``--json`` and return its parsed envelope.

All org access in ``scripts/ux/`` goes through the sf CLI, addressed by an sf
alias or username. No access token is read or handled here.
"""
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.ux._context import UxError


def run_sf_json(
    args: List[str],
    cwd: Optional[Path] = None,
    timeout: int = 600,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """Run ``sf <args> --json``; return the parsed JSON (``status``, ``result``, ...).

    Raises ``UxError`` when sf is missing, times out or prints non-JSON. A
    non-zero ``status`` is returned, not raised, so callers can report
    command-specific failure detail.
    """
    logger = logger or logging.getLogger("rlm_ux")
    cmd = ["sf", *args, "--json"]
    label = "sf " + " ".join(args[:3])
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
        )
    except subprocess.TimeoutExpired:
        raise UxError(f"{label} timed out after {timeout} seconds") from None
    except FileNotFoundError:
        raise UxError(
            "sf command not found. Ensure Salesforce CLI is installed and in PATH."
        ) from None

    if proc.stderr:
        logger.debug(f"{label} stderr: {proc.stderr[:2000]}")

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise UxError(
            f"{label} returned non-JSON output.\n"
            f"Exit code: {proc.returncode}\n"
            f"Stdout: {proc.stdout[:2000]}\n"
            f"Stderr: {proc.stderr[:2000]}"
        ) from None


def cli_error(output: Dict[str, Any]) -> str:
    """The CLI-level error in an sf JSON envelope, e.g. ``[NoOrgFound] ...``."""
    message = output.get("message", "")
    name = output.get("name", "")
    if not message:
        return ""
    return f"[{name}] {message}" if name else message
