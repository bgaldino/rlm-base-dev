"""Shared helpers for the Agentforce publish/activate CCI tasks.

``publish_agents`` and ``activate_agents`` both discover agents from disk and
invoke an ``sf agent ...`` subcommand with ``--json``, then interpret the
standard Salesforce CLI JSON envelope (``{status, result, warnings}``) the
same way. This module holds that common logic so the two task classes stay in
sync — in particular they share a single success contract (top-level
``status == 0``), removing the divergence where one task checked ``status``
and the other checked ``result.success``.
"""
import json
import subprocess

try:
    from cumulusci.core.exceptions import CommandException
except ImportError:
    CommandException = Exception


def discover_agent_bundles(bundles_root):
    """Return the sorted directory names under ``bundles_root`` (each is an
    agent api-name), or ``[]`` if the directory does not exist.

    The directory name is the agent api-name for both ``sf agent publish
    authoring-bundle --api-name`` and ``sf agent activate --api-name``; the
    repo keeps it in lockstep with the bundle's ``developer_name`` and the
    permission set ``<agentName>``.
    """
    if not bundles_root.is_dir():
        return []
    return sorted(p.name for p in bundles_root.iterdir() if p.is_dir())


DEFAULT_LEGACY_BOTS_PATH = "unpackaged/post_agents/legacy/bots"


def discover_legacy_agents(bots_root=None):
    """Return sorted directory names under the legacy ``bots/`` directory.

    Each subdirectory name is a bot developer name that can be passed to
    ``sf agent activate --api-name``.
    """
    from pathlib import Path
    root = Path(bots_root) if bots_root else Path(DEFAULT_LEGACY_BOTS_PATH)
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def run_sf_json(cmd, *, timeout, label, cwd=None):
    """Run an ``sf ... --json`` command and return its parsed payload.

    Raises ``CommandException`` on timeout, a missing ``sf`` binary, a
    non-zero exit code, or a non-zero ``status`` in the JSON envelope — the
    canonical Salesforce CLI success contract. When the command exits 0 but
    emits unparseable output, the raw stdout/stderr is surfaced in the error
    message so the failure is diagnosable rather than silently swallowed.

    ``label`` is the human-readable command name used in log/error messages.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandException(f"{label} timed out after {timeout}s.") from exc
    except FileNotFoundError as exc:
        raise CommandException(
            f"{label} failed: the Salesforce CLI ('sf') was not found on PATH."
        ) from exc

    payload = {}
    if result.stdout:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    if result.returncode != 0 or payload.get("status", 1) != 0:
        message = (
            payload.get("message")
            or result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        raise CommandException(f"{label} failed: {message}")

    return payload
