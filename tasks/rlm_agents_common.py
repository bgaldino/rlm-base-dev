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
        raise CommandException(f"{label} failed: {_failure_detail(result, payload)}")

    return payload


def _strip_cli_noise(text):
    """Drop the CLI's own update-available notice from a captured stream.

    The npm-installed CLI writes `›   Warning: @salesforce/cli update available
    from X to Y.` to **stderr**, which is not part of any error. It cost a real
    diagnosis: a `sf agent activate` failure in CI reported nothing but that
    warning, because the fallback chain reached for stderr and found the notice
    sitting where the cause should have been.
    """
    keep = []
    for line in (text or "").splitlines():
        bare = line.strip().lstrip("›").strip()
        if not bare or "update available" in bare:
            continue
        keep.append(bare)
    return " ".join(keep)


def _failure_detail(result, payload):
    """Build a failure description that cannot come out empty or misleading.

    Every source is reported rather than the first non-empty one, because they
    carry different halves of the story: the JSON envelope names the error
    (`name`) and explains it (`message`), while an argument or plugin-resolution
    failure never reaches JSON at all and only shows up on a raw stream. The
    exit code is always included, so a silent non-zero still says something.
    """
    parts = []
    for key in ("name", "message"):
        value = str(payload.get(key) or "").strip()
        if value and value not in parts:
            parts.append(value)
    for label, stream in (("stderr", result.stderr), ("stdout", result.stdout)):
        # stdout is only worth quoting when it was not already parsed as the
        # envelope above; a full JSON dump in an error line is noise.
        if label == "stdout" and payload:
            continue
        cleaned = _strip_cli_noise(stream)
        if cleaned:
            parts.append(f"{label}: {cleaned}")
    parts.append(f"exit {result.returncode}")
    return " | ".join(parts)
