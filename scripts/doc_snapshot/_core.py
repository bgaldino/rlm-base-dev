"""Shared plumbing for the doc snapshot tools. Stdlib only.

Both snapshotters (``help_portal`` and ``dev_guide``) import from here, and the
offline test suites import those modules under a bare stdlib interpreter, so
nothing in this file may import a third-party package at module load.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def run_browser(coro):
    """Run a snapshot coroutine, turning Playwright failures into SnapshotError.

    A browser launch failure or navigation timeout would otherwise escape the
    CLI's handling and abort a multi-preset run before its summary.
    """
    from playwright.async_api import Error as PlaywrightError

    try:
        return asyncio.run(coro)
    except PlaywrightError as exc:
        raise SnapshotError(f"browser error: {exc}") from exc


def raise_on_capture_errors(failed: List[str], attempted: int, noun: str) -> None:
    """Fail a run whose own captures errored; call after progress is saved."""
    if not failed:
        return
    shown = ", ".join(sorted(failed)[:5]) + (", …" if len(failed) > 5 else "")
    raise SnapshotError(
        f"{len(failed)} of {attempted} {noun} failed to capture: {shown} "
        "(progress saved; errors are recorded in the manifest)"
    )


_TRUE = ("true", "1", "yes", "on")
_FALSE = ("false", "0", "no", "off")


def as_bool(value: Any, default: bool) -> bool:
    """Coerce a CLI/YAML value to bool; None or "" means ``default``.

    Anything else that isn't a recognised spelling is an error, not false: a
    typo such as ``tru`` must not silently drop the release pin or run headed.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "":
        return default
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise OptionsError(
        f"expected a boolean ({'/'.join(_TRUE + _FALSE)}), got {value!r}"
    )


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


def today() -> str:
    """UTC date, as written to frontmatter ``fetched_at`` and ``snapshot_started``."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_FRONTMATTER_LINE_BREAKS = re.compile(r"[\r\n]+")
# A plain YAML scalar can't start with an indicator character ('#' would make
# the rest of the line a comment), and can't contain ': '.
_YAML_INDICATORS = ("-", "*", "&", "?", "|", ">", "%", "@", "`", "#")


def yaml_escape(value: Optional[str]) -> str:
    """Render a string as a single-line YAML frontmatter value."""
    if value is None:
        return ""
    value = _FRONTMATTER_LINE_BREAKS.sub(" ", value)
    if '"' in value or ":" in value or value.startswith(_YAML_INDICATORS):
        value = '"' + value.replace('"', '\\"') + '"'
    return value


def read_manifest(
    path: Path, defaults: Dict[str, Any], records_key: str, logger
) -> Dict[str, Any]:
    """Load ``path``, backfilling any missing top-level key from ``defaults``.

    Older or hand-written manifests may lack keys the snapshotters read. An
    unreadable manifest is logged and replaced by ``defaults``.
    """
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            for key, default in defaults.items():
                existing.setdefault(key, default)
            logger.info(
                f"Loaded existing manifest with {len(existing.get(records_key, []))} "
                f"{records_key}"
            )
            return existing
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Could not load existing manifest ({exc}); starting fresh")
    return defaults


def write_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


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


def stats_table(stats: Dict[str, Any]) -> List[str]:
    """The index.md stats table, followed by a blank line."""
    return [
        "| Metric | Value |",
        "|:--|--:|",
        f"| Discovered | {stats.get('discovered', 0)} |",
        f"| Captured | {stats.get('captured', 0)} |",
        f"| Pending | {stats.get('pending', 0)} |",
        f"| Errored | {stats.get('errored', 0)} |",
        f"| Total captured body chars | {stats.get('total_captured_body_chars', 0):,} |",
        "",
    ]


def log_done(logger, stats: Dict[str, Any], manifest_path: Path) -> None:
    logger.info(
        f"Done. discovered={stats.get('discovered', 0)} "
        f"captured={stats.get('captured', 0)} "
        f"pending={stats.get('pending', 0)} errored={stats.get('errored', 0)}"
    )
    logger.info(f"Manifest: {manifest_path}")
