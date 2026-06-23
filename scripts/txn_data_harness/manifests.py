"""Manifest persistence and inspection helpers."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from scripts.build_harness.harness.io import parse_retention

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
    """Load a manifest by run id or path."""
    path = resolve_manifest_path(run_id_or_path, manifest_dir)
    with open(path) as f:
        return Manifest.from_dict(json.load(f))


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

    ``path`` (on-disk manifest path) is included so scripted workflows can read
    it from ``cli inspect --json`` and pipe it into a follow-up resume command.
    ``usage_journal_ids`` carries the TJ count + first few ids for quick review.
    """
    return {
        "run_id": m.run_id,
        "path": str(manifest_path(m.run_id)),
        "account": m.account_name or m.account_id,
        "reached_stage": m.reached_stage,
        "attempts": m.attempts,
        "failure_class": m.failure_class,
        "error": m.error,
        "start_date": m.start_date,
        "line_count": len(m.lines),
        "usage_journals": {
            "count": len(m.usage_journal_ids),
            "ids": m.usage_journal_ids[:5],
        },
        "ids": {
            "opportunity": m.opportunity_id,
            "quote": m.quote_id,
            "order": m.order_id,
            "billing_schedules": m.billing_schedule_ids,
            "assets": m.asset_ids,
            "invoice": m.invoice_id,
        },
        "invoice_number": m.invoice_number,
    }


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
