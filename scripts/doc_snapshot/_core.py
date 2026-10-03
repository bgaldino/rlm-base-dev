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
from typing import Any, Dict, List, Optional, Tuple

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
    """Coerce a CLI/YAML value to bool; None means ``default``.

    Anything else that isn't a recognised spelling is an error, not false: a
    typo such as ``tru`` must not silently drop the release pin or run headed.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise OptionsError(
        f"expected a boolean ({'/'.join(_TRUE + _FALSE)}), got {value!r}"
    )


def as_int(value: Any, default: Optional[int]) -> Optional[int]:
    """Coerce a CLI/YAML value to int; None means ``default``."""
    if value is None:
        return default
    # int() would read `true` as 1 and truncate 2.5 to 2.
    if isinstance(value, (bool, float)):
        raise OptionsError(f"expected an integer, got {value!r}")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise OptionsError(f"expected an integer, got {value!r}")


def normalize_mode(value: Any) -> str:
    mode = str(value or "all").lower()
    if mode not in VALID_MODES:
        raise OptionsError(f"mode must be one of {VALID_MODES}, got {mode!r}")
    return mode


def blank_options(options: Dict[str, Any]) -> List[str]:
    """Names of options set to a blank string, an empty list, or a list with a blank item."""
    def blank(value: Any) -> bool:
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, tuple)):
            return not value or any(blank(v) for v in value)
        return False
    return sorted(name for name, value in options.items() if blank(value))


def validate_options(
    options: Dict[str, Any], *required: str, list_options: Tuple[str, ...] = ()
) -> None:
    """Reject blank or misshapen values, then missing ``required`` ones.

    A blank value must not read as "use the default": an unset shell variable
    passed as ``--output-dir ""`` would send release notes into the Help
    corpus, and ``sections: []`` would capture the whole guide. Only
    ``list_options`` may be a list (of scalars); no option may be a mapping.
    """
    blank = blank_options(options)
    if blank:
        raise OptionsError(f"empty value for {', '.join(blank)}; omit it to use the default")

    def misshapen(name: str, value: Any) -> bool:
        if isinstance(value, (list, tuple)):
            return name not in list_options or any(isinstance(v, (list, tuple, dict)) for v in value)
        return isinstance(value, dict)
    bad = sorted(name for name, value in options.items() if misshapen(name, value))
    if bad:
        allowed = f" ({', '.join(list_options)} may also be a list)" if list_options else ""
        raise OptionsError(f"{', '.join(bad)}: expected a single value{allowed}")
    missing = [k for k in required if not options.get(k)]
    if missing:
        raise OptionsError(f"missing required option(s): {', '.join(missing)}")


def require_positive(options: Dict[str, Any], *names: str) -> None:
    for name in names:
        if options[name] <= 0:
            raise OptionsError(f"{name} must be positive, got {options[name]!r}")


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


# read_manifest's logger when the caller wants no output.
_SILENT = logging.getLogger(__name__ + ".silent")
_SILENT.addHandler(logging.NullHandler())
_SILENT.propagate = False


def read_manifest(
    path: Path, defaults: Dict[str, Any], records_key: str, logger=None
) -> Dict[str, Any]:
    """Load ``path``, backfilling any missing top-level key from ``defaults``.

    Older or hand-written manifests may lack keys the snapshotters read. An
    unreadable manifest, or one whose shape the snapshotters can't read, is
    logged and replaced by ``defaults``. Pass no ``logger`` to load silently.
    """
    log = logger or _SILENT
    if not path.exists():
        return defaults
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning(f"Could not load existing manifest ({exc}); starting fresh")
        return defaults
    if not isinstance(existing, dict):
        log.warning("Existing manifest is not a JSON object; starting fresh")
        return defaults
    for key, default in defaults.items():
        existing.setdefault(key, default)
    # The snapshotters iterate these lists and read each record as an object.
    misshapen = [
        key for key, default in defaults.items()
        if isinstance(default, list) and not (
            isinstance(existing[key], list) and all(isinstance(r, dict) for r in existing[key])
        )
    ]
    if misshapen:
        log.warning(
            f"Existing manifest's {', '.join(misshapen)} is not a list of objects; starting fresh"
        )
        return defaults
    log.info(
        f"Loaded existing manifest with {len(existing.get(records_key, []))} {records_key}"
    )
    return existing


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


def captured_table(
    heading: str, records: List[Dict[str, Any]], id_key: str, noun: str, size: str
) -> List[str]:
    """An index.md table of captured records linking to their files, then a blank line."""
    lines = [heading, "", f"| {noun} | ID | {size} |", "|:--|:--|--:|"]
    for r in sorted(records, key=lambda x: x[id_key]):
        rid = r[id_key]
        lines.append(
            f"| [{r.get('title', rid)}](./{r.get('file', f'articles/{rid}.md')}) | "
            f"`{rid}` | {r.get('body_length', 0):,} |"
        )
    lines.append("")
    return lines


def index_footer(command: str, manifest: Dict[str, Any]) -> List[str]:
    return [
        "---",
        "",
        f"*Generated by `scripts/doc_snapshot {command}` "
        f"on {manifest.get('last_updated', 'n/a')}.*",
    ]


def log_done(logger, stats: Dict[str, Any], manifest_path: Path) -> None:
    logger.info(
        f"Done. discovered={stats.get('discovered', 0)} "
        f"captured={stats.get('captured', 0)} "
        f"pending={stats.get('pending', 0)} errored={stats.get('errored', 0)}"
    )
    logger.info(f"Manifest: {manifest_path}")
