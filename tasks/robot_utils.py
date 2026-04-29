"""Shared utilities for CCI tasks that invoke Robot Framework setup tests."""

import re
from pathlib import Path
from typing import Optional

try:
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    TaskOptionsError = Exception  # type: ignore

MIN_URLLIB3_VERSION = (2, 6, 3)

_URLLIB3_FIX = (
    "Upgrade urllib3 in this environment "
    '(e.g. pip install "urllib3>=2.6.3" or pip install -r robot/requirements.txt). '
    "See README Troubleshooting for details."
)

_URLLIB3_ROOT_CAUSE = (
    "urllib3 {ver} is below the minimum required version {min_ver}. "
    "Older urllib3 1.x releases have known security vulnerabilities (CVE-2026-21441 and others)."
)


def _parse_version(ver_str: str) -> tuple:
    """Parse a dotted version string into a tuple of ints for comparison."""
    parts = []
    for part in ver_str.split("."):
        try:
            parts.append(int(part))
        except (ValueError, AttributeError):
            break
    return tuple(parts)


def check_urllib3_for_robot(task_name: str = "") -> None:
    """Warn if urllib3 is below the minimum required version (2.6.3).

    Pass ``task_name`` (e.g. ``"EnableDocumentBuilderToggle"``) to include the
    failing task in the message for faster diagnosis.
    """
    try:
        import urllib3
    except ImportError:
        return

    ver_str = getattr(urllib3, "__version__", None)
    if ver_str is None:
        return

    ver_tuple = _parse_version(ver_str)
    if ver_tuple < MIN_URLLIB3_VERSION:
        min_ver_str = ".".join(str(v) for v in MIN_URLLIB3_VERSION)
        msg = _URLLIB3_ROOT_CAUSE.format(ver=ver_str, min_ver=min_ver_str)
        prefix = f"{task_name}: " if task_name else ""
        raise TaskOptionsError(f"{prefix}{msg} {_URLLIB3_FIX}")


def _sanitize_path_token(value: str) -> str:
    """Normalize a value for safe filesystem path usage."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or "unknown"


def resolve_robot_output_dir(
    repo_root: Path,
    outputdir_option: Optional[str],
    default_output_dir: str,
    task_slug: str,
    org_name: str,
) -> Path:
    """Resolve and create the Robot output directory.

    If ``outputdir_option`` is provided, preserve the explicit caller choice.
    Otherwise, isolate artifacts per task and org to avoid cross-run collisions
    when multiple Robot wrapper tasks run in parallel.
    """
    if outputdir_option:
        out_path = repo_root / outputdir_option
    else:
        out_path = (
            repo_root
            / default_output_dir
            / _sanitize_path_token(task_slug)
            / _sanitize_path_token(org_name)
        )
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path
