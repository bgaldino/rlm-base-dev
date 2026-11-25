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
    """A snapshot run failed (bad walk, blocked fetch, missing dependency).

    A run whose captures failed also carries what the capture guard found:
    ``refused`` is ``[(id, reason)]`` for captures it refused, ``orphaned`` the
    ids of errored pages the current table of contents no longer lists.
    """

    refused: Tuple[Tuple[str, str], ...] = ()
    orphaned: Tuple[str, ...] = ()


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


def raise_on_capture_errors(
    failed: List[str],
    attempted: int,
    noun: str,
    refused: Optional[List[Tuple[str, str]]] = None,
    orphaned: Optional[List[str]] = None,
) -> None:
    """Fail a run whose own captures errored; call after progress is saved.

    The guard's counts ride on the error (message and attributes) because a
    failed run returns no stats: the multi-preset summary prints this message
    on the FAILED row.
    """
    if not failed:
        return
    refused = list(refused or [])
    orphaned = list(orphaned or [])
    shown = ", ".join(sorted(failed)[:5]) + (", …" if len(failed) > 5 else "")
    guard = []
    if refused:
        guard.append(f"{len(refused)} refused by the capture guard")
    if orphaned:
        guard.append(f"{len(orphaned)} no longer in the contents")
    detail = f" [{', '.join(guard)}]" if guard else ""
    error = SnapshotError(
        f"{len(failed)} of {attempted} {noun} failed to capture{detail}: {shown} "
        "(progress saved; errors are recorded in the manifest)"
    )
    error.refused = tuple(refused)
    error.orphaned = tuple(orphaned)
    raise error


def as_id_set(value: Any) -> frozenset:
    """Ids from a comma-separated string or a list of them (``--accept-shrinkage``)."""
    if value is None or value is False:
        return frozenset()
    items = [value] if isinstance(value, str) else list(value)
    return frozenset(
        part.strip() for item in items for part in str(item).split(",") if part.strip()
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
    mode = "all" if value is None else str(value).lower()
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


def attribution_note(source_url: str, content: str) -> str:
    """The source-attribution footer every captured article file ends with.

    ``content`` names what was captured (e.g. "Salesforce Help content"). The
    frontmatter ``source_url`` is machine-readable only; this puts the source
    and its limited-use terms in the article body, where a reader sees them.
    """
    return (
        "---\n"
        "\n"
        "> **Source attribution and limited-use note.** This file is a captured "
        f"copy of publicly readable {content} ([source]({source_url})), "
        "© Salesforce, Inc., kept in this repository as grounding material for "
        "people and AI agents. It is not an official or authoritative copy: the "
        "source URL is the system of record, and if this text differs from the "
        "live page, the live page wins. Do not republish it elsewhere without "
        "confirming Salesforce's terms."
    )


_SOURCE_URL_LINE = re.compile(r"^source_url:[ \t]*(\S+)[ \t]*$", re.M)


def attribution_state(text: str) -> Tuple[str, str]:
    """Classify a captured article's footer: ``(state, source_url)``.

    ``state`` is "ok" (footer present), "missing" (frontmatter with a source_url, no
    footer), "no-frontmatter" or "no-source_url" (nothing to build a footer from).
    The one definition the backfill and ``check`` share.
    """
    if not text.startswith("---\n"):
        return "no-frontmatter", ""
    if "> **Source attribution" in text:
        return "ok", ""
    end = text.find("\n---\n", 4)
    m = _SOURCE_URL_LINE.search(text[:end]) if end > 0 else None
    if not m:
        return "no-source_url", ""
    return "missing", m.group(1).strip("'\"")


def scan_attribution(articles: Path) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """``(missing, skipped)`` for ``articles/*.md``: ``(file name, source_url)`` of every
    article lacking the footer, and ``(file name, reason)`` of every file that cannot be
    judged (unreadable, no frontmatter, no source_url). A missing directory is empty."""
    missing: List[Tuple[str, str]] = []
    skipped: List[Tuple[str, str]] = []
    if not articles.is_dir():
        return missing, skipped
    for f in sorted(articles.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped.append((f.name, f"unreadable: {exc.__class__.__name__}"))
            continue
        state, url = attribution_state(text)
        if state == "missing":
            missing.append((f.name, url))
        elif state != "ok":
            skipped.append((f.name, state))
    return missing, skipped


def backfill_attribution(articles: Path) -> Tuple[List[str], List[Tuple[str, str]]]:
    """Append the attribution footer to captured articles that lack it.

    Retained atlas articles (a page the site move did not replace) were captured
    before the footer existed, and a refresh never rewrites them. Every ``*.md``
    in ``articles`` that ``scan_attribution`` reports missing gets ``attribution_note``
    appended, labelled by the source host ("Salesforce Help content" for
    help.salesforce.com, else "Salesforce developer documentation"). Idempotent;
    ``index.md`` lives outside ``articles`` and is never touched.

    Returns ``(changed, skipped)``: the names changed, and ``(name, reason)`` for each
    file left alone (no frontmatter or source_url, unreadable, or "not writable: ...").
    """
    missing, skipped = scan_attribution(articles)
    changed: List[str] = []
    for name, url in missing:
        label = ("Salesforce Help content" if "help.salesforce.com" in url
                 else "Salesforce developer documentation")
        f = articles / name
        try:
            text = f.read_text(encoding="utf-8")
            f.write_text(text.rstrip() + "\n\n" + attribution_note(url, label) + "\n", encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped.append((name, f"not writable: {exc.__class__.__name__}"))
            continue
        changed.append(name)
    return changed, skipped


def log_done(logger, stats: Dict[str, Any], manifest_path: Path) -> None:
    logger.info(
        f"Done. discovered={stats.get('discovered', 0)} "
        f"captured={stats.get('captured', 0)} "
        f"pending={stats.get('pending', 0)} errored={stats.get('errored', 0)}"
    )
    logger.info(f"Manifest: {manifest_path}")
