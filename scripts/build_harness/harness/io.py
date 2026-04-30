"""Shared filesystem and serialization helpers for the build harness.

These helpers were previously duplicated across `harness.py`,
`scenario_runner.py`, `provenance.py`, and `reporting.py`. Centralising them
keeps JSON layout (indent + sort_keys), JSONL parsing, UTC timestamp format,
and directory creation behavior identical across all writers/readers.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List


def now_utc() -> str:
    """Return an ISO-8601 UTC timestamp suitable for run/event metadata."""
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    """Create `path` (and any missing parents). No-op if it already exists."""
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    """Read a JSON file. Raises FileNotFoundError if missing."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with deterministic layout (indent=2, sort_keys=True, trailing newline)."""
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read a JSONL file. Returns [] if the file does not exist."""
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    """Append a single JSON object as one JSONL line (sorted keys)."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


_RETENTION_RE = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$", re.IGNORECASE)


def parse_retention(value: str) -> dt.timedelta:
    """Parse retention text like ``7d``/``24h``/``30m`` into a timedelta."""
    match = _RETENTION_RE.match(value or "")
    if not match:
        raise ValueError(f"Invalid retention '{value}'. Use <int><unit> like 7d, 24h, 30m.")
    amount = int(match.group(1))
    unit = match.group(2).lower()
    if amount <= 0:
        raise ValueError("Retention must be greater than zero.")
    if unit == "s":
        return dt.timedelta(seconds=amount)
    if unit == "m":
        return dt.timedelta(minutes=amount)
    if unit == "h":
        return dt.timedelta(hours=amount)
    if unit == "d":
        return dt.timedelta(days=amount)
    if unit == "w":
        return dt.timedelta(weeks=amount)
    raise ValueError(f"Unsupported retention unit: {unit}")


def prune_old_runs(output_root: Path, retention: dt.timedelta) -> List[Path]:
    """Delete run directories older than ``retention`` and return removed paths."""
    if retention <= dt.timedelta(0):
        raise ValueError("Retention must be greater than zero.")
    if not output_root.exists():
        return []

    cutoff = dt.datetime.now(dt.timezone.utc).timestamp() - retention.total_seconds()
    removed: List[Path] = []
    for candidate in sorted(output_root.iterdir()):
        if not candidate.is_dir() or candidate.is_symlink():
            continue
        try:
            modified = candidate.stat().st_mtime
        except OSError:
            continue
        if modified >= cutoff:
            continue
        try:
            shutil.rmtree(candidate)
        except OSError:
            continue
        removed.append(candidate)
    return removed
