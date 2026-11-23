#!/usr/bin/env python3
"""Fail when a Robot result file contains a Salesforce session URL.

``sf org open --url-only`` prints a frontdoor URL (``secur/frontdoor.jsp?sid=...&otp=...``) that
is a live login. Robot setup suites must never write one into ``output.xml`` or ``log.html``
(``robot/rlm-base/resources/SessionUrlGuard.py``; robot-testing skill, "Session URLs"). This scans
Robot result trees for that material.

``log.html`` stores most strings zlib-compressed and base64-encoded, so a plain text search of it
proves nothing; this decodes them first.

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
    r"secur/frontdoor\.jsp|[?&;](?:sid|otp)=|(?:^|[\s\"'(])(?:sid|otp)=[^\s&\"']{6,}",
    re.IGNORECASE,
)
_STRINGS_RE = re.compile(r'window\.output\["strings"\]\s*=\s*window\.output\["strings"\]\.concat\((\[.*?\])\);', re.S)
_SUFFIXES = {".xml", ".html", ".htm", ".txt", ".log", ".json"}


def _decoded_strings(html: str):
    """Yield the strings Robot embeds in log.html (plain ``*`` entries and compressed ones)."""
    for match in _STRINGS_RE.finditer(html):
        try:
            entries = json.loads(match.group(1).replace("\\x3c", "<"))
        except ValueError:
            yield match.group(1)  # undecodable: still search the raw text
            continue
        for entry in entries:
            if entry.startswith("*"):
                yield entry[1:]
                continue
            try:
                yield zlib.decompress(base64.b64decode(entry)).decode("utf-8", "replace")
            except (ValueError, zlib.error):
                yield entry


def scan_file(path: Path) -> bool:
    """True when ``path`` holds session-URL material."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if SESSION_URL_PATTERN.search(text):
        return True
    return path.suffix in {".html", ".htm"} and any(
        SESSION_URL_PATTERN.search(s) for s in _decoded_strings(text)
    )


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
