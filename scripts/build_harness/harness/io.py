"""Shared filesystem and serialization helpers for the build harness.

These helpers were previously duplicated across `harness.py`,
`scenario_runner.py`, `provenance.py`, and `reporting.py`. Centralising them
keeps JSON layout (indent + sort_keys), JSONL parsing, UTC timestamp format,
and directory creation behavior identical across all writers/readers.
"""

from __future__ import annotations

import datetime as dt
import json
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
