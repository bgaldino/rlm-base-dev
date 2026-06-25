"""Manifest persistence and inspection helpers."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any

from .models import Manifest

__all__ = [
    "MANIFEST_DIR",
    "load_manifest",
    "list_manifests",
    "manifest_path",
    "parse_retention",
    "prune_old_runs",
    "resolve_manifest_path",
    "summarize_manifest",
    "write_json",
    "write_manifest",
]

MANIFEST_DIR = Path(__file__).resolve().parent / "out"
_RETENTION_RE = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$", re.IGNORECASE)


def parse_retention(text: str) -> dt.timedelta:
    """Parse a retention window like ``30m``, ``24h``, ``7d``, or ``2w``."""
    match = _RETENTION_RE.match(text or "")
    if not match:
        raise ValueError(f"Invalid retention window: {text!r}")
    value = int(match.group(1))
    if value <= 0:
        raise ValueError("Retention must be greater than zero.")
    unit = match.group(2).lower()
    if unit == "s":
        return dt.timedelta(seconds=value)
    if unit == "m":
        return dt.timedelta(minutes=value)
    if unit == "h":
        return dt.timedelta(hours=value)
    if unit == "d":
        return dt.timedelta(days=value)
    if unit == "w":
        return dt.timedelta(weeks=value)
    raise ValueError(f"Invalid retention unit: {unit!r}")


def write_json(path: Path, payload: Any) -> Path:
    """Write JSON with deterministic layout (indent=2, sort_keys, trailing newline).

    Local helper mirroring the build harness's serialization style so reports and
    manifests are human-diffable, without coupling this package to build_harness.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)
    return path


def manifest_path(run_id: str, manifest_dir: Path = MANIFEST_DIR) -> Path:
    """Return the canonical manifest path for a run id."""
    return manifest_dir / f"{run_id}.json"


def write_manifest(m: Manifest, manifest_dir: Path = MANIFEST_DIR) -> Path:
    """Atomically write a manifest checkpoint and return its path."""
    return write_json(manifest_path(m.run_id, manifest_dir), m.to_dict())


def resolve_manifest_path(run_id_or_path: str, manifest_dir: Path = MANIFEST_DIR) -> Path:
    """Resolve either a run id or an explicit manifest path."""
    candidate = Path(run_id_or_path)
    if candidate.exists() or candidate.suffix == ".json":
        return candidate
    return manifest_path(run_id_or_path, manifest_dir)


def load_manifest(run_id_or_path: str, manifest_dir: Path = MANIFEST_DIR) -> Manifest:
    """Load a manifest by run id or path.

    A manifest missing the ``kind`` discriminator is rejected with a loud
    error -- ``cli step`` / inspect / report tooling switches on ``kind`` to
    pick the right scenario handler, and a defaulted value would silently
    misroute (e.g. ingest a manifest produced by the ingestion path as a PST
    run). This work has not shipped, so there are no on-disk manifests
    without ``kind``.
    """
    path = resolve_manifest_path(run_id_or_path, manifest_dir)
    with open(path) as f:
        data = json.load(f)
    if "kind" not in data:
        raise ValueError(
            f"manifest {path} is missing required 'kind' discriminator; "
            f"regenerate it with the current harness"
        )
    return Manifest.from_dict(data)


def list_manifests(manifest_dir: Path = MANIFEST_DIR) -> list[Path]:
    """Return known manifest files, newest first.

    Excludes ``<base>-report.json`` batch summaries (see ``report.py``), which
    share the directory but have a different schema and would crash
    ``Manifest.from_dict``.
    """
    if not manifest_dir.exists():
        return []
    return sorted(
        (p for p in manifest_dir.glob("*.json") if not p.name.endswith("-report.json")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def summarize_manifest(m: Manifest) -> dict[str, Any]:
    """Return a compact machine-friendly summary for inspect commands.

    Dispatches to the handler registered for ``m.kind`` so each lifecycle
    surfaces its own shape (PST keeps Opportunity/Quote/Order/usage ids;
    ingestion drops them and adds ``creation_mode``). ``path`` (on-disk
    manifest path) is on every shape so scripted workflows can pipe an
    inspect line into a follow-up resume command.
    """
    # Local import to break the circular handlers -> manifests dependency
    # (handlers/__init__.py imports from this module transitively).
    from .handlers import SCENARIO_HANDLERS

    try:
        handler = SCENARIO_HANDLERS[m.kind]
    except KeyError as exc:
        raise ValueError(
            f"summarize_manifest: unknown kind {m.kind!r}; "
            f"valid: {', '.join(sorted(SCENARIO_HANDLERS))}"
        ) from exc
    return handler.summarize(m)


def _is_safe_manifest_dir(manifest_dir: Path, safe_root: Path = MANIFEST_DIR) -> bool:
    """Guard: ``manifest_dir`` must resolve to ``safe_root`` exactly.

    Prevents a stray ``manifest_dir`` from deleting JSON in an arbitrary path.
    Production always uses the harness's own ``out/`` (the default ``safe_root``);
    tests inject a tmp dir as ``safe_root`` so the guard stays an exact-path check
    rather than a weaker name match.
    """
    return manifest_dir.resolve() == safe_root.resolve()


def prune_old_runs(
    retention: dt.timedelta,
    manifest_dir: Path = MANIFEST_DIR,
    *,
    dry_run: bool = True,
    now: dt.datetime | None = None,
    safe_root: Path = MANIFEST_DIR,
) -> list[Path]:
    """Delete manifest JSON files older than ``retention``; return their paths.

    This harness writes flat per-run ``*.json`` files (not run subdirs), so this
    matches files rather than directories. With ``dry_run=True`` (default) it
    reports what *would* be removed without deleting. Refuses any ``manifest_dir``
    that does not resolve to ``safe_root`` (the harness's own ``out/`` in
    production; an injected tmp dir under test).
    """
    if retention <= dt.timedelta(0):
        raise ValueError("Retention must be greater than zero.")
    if not _is_safe_manifest_dir(manifest_dir, safe_root):
        raise ValueError(
            f"Refusing to prune unexpected directory: {manifest_dir}. "
            f"Expected the harness output dir {safe_root}."
        )
    if not manifest_dir.exists():
        return []

    reference = now or dt.datetime.now(dt.timezone.utc)
    cutoff = reference.timestamp() - retention.total_seconds()
    removed: list[Path] = []
    for candidate in sorted(manifest_dir.glob("*.json")):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        try:
            modified = candidate.stat().st_mtime
        except OSError:
            continue
        if modified >= cutoff:
            continue
        if not dry_run:
            try:
                candidate.unlink()
            except OSError:
                continue
        removed.append(candidate)
    return removed
