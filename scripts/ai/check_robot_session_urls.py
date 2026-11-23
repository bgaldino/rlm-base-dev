#!/usr/bin/env python3
"""Fail when a Robot result file contains a Salesforce session URL.

``sf org open --url-only`` prints a frontdoor URL (``secur/frontdoor.jsp?sid=...&otp=...``) that
is a live login. Robot setup suites must never write one into ``output.xml`` or ``log.html``
(``robot/rlm-base/resources/SessionUrlGuard.py``; robot-testing skill, "Session URLs"). This scans
Robot result trees for that material.

``log.html`` stores most strings zlib-compressed and base64-encoded, so a plain text search of it
proves nothing; this decodes them first (each embedded array with ``raw_decode``; an array
that will not decode is itself a finding) and also reads split-log ``.js`` files.

Usage:
    python scripts/ai/check_robot_session_urls.py [PATH ...]

With no PATH it scans ``robot/rlm-base/results``, ``.harness/runs/*/robot_results`` and
``.harness/tui-runs/*/robot_results`` that exist (none existing is a pass: a clean checkout has no
results). Run it on a live run's output directory before declaring a Robot change verified.

Exit 0 clean, 1 on a finding (file and kind only; the match is never printed), 2 on bad usage.
Stdlib only.
"""
from __future__ import annotations

import base64
import json
import re
import sys
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# Keep in step with SESSION_URL_PATTERN in robot/rlm-base/resources/SessionUrlGuard.py.
SESSION_URL_PATTERN = re.compile(
    r"secur(?:/|%2F|%252F)frontdoor\.jsp"
    r"|(?:[?&;]|%3F|%26|%25(?:3F|26))(?:sid|otp)(?:=|%3D|%253D)"
    r"|(?:^|[\s\"';(,])(?:sid|otp)="
    r"|(?:(?<![0-9A-Za-z])|(?<=%[0-9A-Fa-f]{2}))00D[0-9A-Za-z]{12,15}(?:!|%21|%2521)[0-9A-Za-z._]{20,}",
    re.IGNORECASE,
)
# log.html appends string tables with ``window.output["strings"].concat([...])`` (other
# ``.concat(`` calls in its bundled JavaScript are not data); a split log (--splitlog) keeps each
# fragment's strings in ``window.strings<N> = [...]`` in a separate .js file.
_CONCAT = 'window.output["strings"].concat('
_STRINGS_ASSIGN_RE = re.compile(r"window\.strings\d+\s*=\s*")
_SUFFIXES = {".xml", ".html", ".htm", ".txt", ".log", ".json", ".js"}
UNDECODABLE = "<undecodable embedded JSON>"


def _json_text(text: str) -> str:
    """Robot escapes ``<`` and friends as ``\\xNN``, which is not valid JSON."""
    return re.sub(r"\\x([0-9a-fA-F]{2})", r"\\u00\1", text)


def _decode_array(text: str, start: int):
    """Decode the JSON array at ``text[start:]``; ``None`` when it does not decode."""
    try:
        value, _ = json.JSONDecoder().raw_decode(text, start)
    except ValueError:
        return None
    return value if isinstance(value, list) else None


def _decode_entry(entry):
    if not isinstance(entry, str):
        return str(entry)
    if entry.startswith("*"):
        return entry[1:]
    try:
        return zlib.decompress(base64.b64decode(entry)).decode("utf-8", "replace")
    except (ValueError, zlib.error):
        return entry


def _decoded_strings(text: str):
    """Yield every string embedded in a log.html or split-log .js file.

    An embedded array that cannot be decoded is yielded as ``UNDECODABLE`` so the caller reports
    it: an unreadable chunk is never assumed clean.
    """
    text = _json_text(text)  # once, over the whole file
    starts = [m.end() for m in _STRINGS_ASSIGN_RE.finditer(text)]
    pos = text.find(_CONCAT)
    while pos != -1:
        starts.append(pos + len(_CONCAT))
        pos = text.find(_CONCAT, pos + 1)
    for start in starts:
        entries = _decode_array(text, start)
        if entries is None:
            yield UNDECODABLE
            continue
        for entry in entries:
            yield _decode_entry(entry)


def scan_file(path: Path) -> bool:
    """True when ``path`` holds session-URL material (or an embedded chunk that cannot be read)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if SESSION_URL_PATTERN.search(text):
        return True
    if path.suffix not in {".html", ".htm", ".js"}:
        return False
    return any(s == UNDECODABLE or SESSION_URL_PATTERN.search(s) for s in _decoded_strings(text))


def scan_paths(paths) -> list[Path]:
    hits = []
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        hits += [f for f in files if f.suffix in _SUFFIXES and scan_file(f)]
    return hits


def default_paths() -> list[Path]:
    candidates = [REPO / "robot" / "rlm-base" / "results"]
    for tier in ("runs", "tui-runs"):
        candidates += sorted((REPO / ".harness" / tier).glob("*/robot_results"))
    return [p for p in candidates if p.exists()]


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(a in ("-h", "--help") for a in args):
        print(__doc__)
        return 0
    paths = [Path(a) for a in args] or default_paths()
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"error: not found: {', '.join(map(str, missing))}", file=sys.stderr)
        return 2
    hits = scan_paths(paths)
    for hit in hits:
        print(f"SESSION URL in Robot results: {hit}")
    print(f"scanned {len(paths)} results location(s); {len(hits)} file(s) with session URL material")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
