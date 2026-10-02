"""Shared plumbing for the doc snapshot tools. Stdlib only.

Both snapshotters (``help_portal`` and ``dev_guide``) import from here, and the
offline test suites import those modules under a bare stdlib interpreter, so
nothing in this file may import a third-party package at module load.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

# scripts/doc_snapshot/_core.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

VALID_MODES = ("discover", "capture", "all", "refresh")

PLAYWRIGHT_INSTALL_HINT = """
Playwright is required for doc snapshots. Install the tool's dependencies into
the Python you run it with (a project .venv is fine; no CumulusCI needed):

    python -m pip install -r scripts/doc_snapshot/requirements.txt
    python -m playwright install chromium

See scripts/doc_snapshot/README.md for details.
"""


class SnapshotError(Exception):
    """A snapshot run failed (bad walk, blocked fetch, missing dependency)."""


class OptionsError(SnapshotError):
    """An option value is missing or invalid."""


def get_logger(name: str = "doc_snapshot") -> logging.Logger:
    return logging.getLogger(name)


def require_playwright(logger) -> None:
    """Fail with an install hint when Playwright isn't importable."""
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError:
        logger.error(PLAYWRIGHT_INSTALL_HINT)
        raise SnapshotError("Playwright not installed")


def as_bool(value: Any, default: bool) -> bool:
    """Coerce a CLI/YAML value to bool; None means ``default``."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def as_int(value: Any, default: Optional[int]) -> Optional[int]:
    """Coerce a CLI/YAML value to int; None or "" means ``default``."""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        raise OptionsError(f"expected an integer, got {value!r}")


def normalize_mode(value: Any) -> str:
    mode = str(value or "all").lower()
    if mode not in VALID_MODES:
        raise OptionsError(f"mode must be one of {VALID_MODES}, got {mode!r}")
    return mode


def require_options(options: Dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if not options.get(k)]
    if missing:
        raise OptionsError(f"missing required option(s): {', '.join(missing)}")


def resolve_output_dir(output_dir: str) -> Path:
    """Resolve ``output_dir`` against the repo root (absolute paths pass through).

    The CCI tasks resolved it against the current directory; anchoring on the
    repo root makes the tool safe to run from anywhere.
    """
    path = Path(output_dir).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def compute_stats(manifest: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Status counts over ``manifest[key]`` (``articles`` or ``pages``)."""
    records = manifest.get(key, [])
    captured = [r for r in records if r.get("status") == "captured"]
    return {
        "discovered": len(records),
        "captured": len(captured),
        "pending": len([r for r in records if r.get("status") == "pending"]),
        "errored": len([r for r in records if r.get("status") == "error"]),
        "total_captured_body_chars": sum(r.get("body_length", 0) for r in captured),
    }
