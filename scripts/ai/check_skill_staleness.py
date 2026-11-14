#!/usr/bin/env python3
"""Flag stale release references and missing Help ids in `.cursor/skills/**/*.md`.

The active release is `salesforce_release_active` in `.claude/skill-manifest.yml`. Per-release
snapshots live under `docs/salesforce/<N>/`. Three rules, one finding per line and rule:

* `snapshot-link`: a path `docs/salesforce/<N>/<rel>` where N is older than the active release
  and the same `<rel>` exists under the active release (a `:line` suffix is not part of the
  path). Repoint it. A path that exists only in the older snapshot is allowed (the content was
  dropped or never carried forward); a newer N is never flagged.
* `stale-pin`: "Verified on Release <N>" / "verified on <N>" with N older than the active
  release, unless the same line says `not re-verified` (also `not yet re-verified`) or also
  pins the active release or a newer one.
* `help-id`: an id in an evidence label `[Help: \\`ind.xxx\\`, ...]` (ids may be comma- or
  semicolon-separated; a trailing `.htm` is optional) that exists in no
  `docs/salesforce/*/help/articles/` snapshot, or that is missing from the active snapshot
  but present in an older one and the line does not name that older release number. An id
  found only in snapshots newer than the active release is not flagged.

Intentional cases carry the full marker `<!-- staleness: allow -->` on the same line; it
exempts that line only.
Use it for a deliberate older-release citation, never to silence a real stale pin.

Usage:
    python scripts/ai/check_skill_staleness.py            # scan every skill markdown file
    python scripts/ai/check_skill_staleness.py FILE...    # scan these files only

Output: one line per finding, `path:line: rule: message`. Stdlib only.
Exit codes: 0 = clean, 1 = findings, 2 = tool error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1].parent
ALLOW = "<!-- staleness: allow -->"
MANIFEST = Path(".claude/skill-manifest.yml")
SKILLS = Path(".cursor/skills")
SNAPSHOTS = Path("docs/salesforce")

ACTIVE_KEY = re.compile(r"^salesforce_release_active:\s*[\"']?(\d+)[\"']?", re.MULTILINE)
SNAP_PATH = re.compile(r"docs/salesforce/(\d+)/([^\s)`'\"\]>#,;|:]+)")
PIN = re.compile(r"verified\s+on\s+(?:release\s+)?(\d{3})\b", re.IGNORECASE)
NOT_REVERIFIED = re.compile(r"\bnot\s+(?:yet\s+)?re-?verified", re.IGNORECASE)
HELP_LABEL = re.compile(r"\[Help:([^\]]*)\]")
HELP_ID = re.compile(r"`(ind\.[\w.-]+?)(?:\.htm)?(?:\.md)?`")


def active_release(root: Path) -> str:
    match = ACTIVE_KEY.search((root / MANIFEST).read_text(encoding="utf-8"))
    if not match:
        raise OSError(f"salesforce_release_active not found in {MANIFEST}")
    return match.group(1)


def help_index(root: Path) -> dict:
    """release -> set of Help article ids (no .htm.md suffix)."""
    index = {}
    base = root / SNAPSHOTS
    for rel_dir in sorted(base.iterdir()) if base.is_dir() else []:
        articles = rel_dir / "help" / "articles"
        if rel_dir.name.isdigit() and articles.is_dir():
            index[rel_dir.name] = {re.sub(r"(?:\.htm)?\.md$", "", p.name)
                                   for p in articles.iterdir()}
    return index


def findings(text: str, root: Path, active: str, index: dict):
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if ALLOW in line:
            continue
        for rule, message in _line_findings(line, root, active, index):
            if (number, rule, message) not in seen:
                seen.add((number, rule, message))
                yield number, rule, message


def _line_findings(line: str, root: Path, active: str, index: dict):
    for match in SNAP_PATH.finditer(line):
        release, rel = match.group(1), match.group(2).rstrip(".")
        if int(release) >= int(active) or any(c in rel for c in "<*{$"):
            continue
        if (root / SNAPSHOTS / active / rel).exists():
            yield "snapshot-link", (
                f"docs/salesforce/{release}/{rel} exists under {active}; repoint it")
    for match in PIN.finditer(line):
        if int(match.group(1)) < int(active) and not NOT_REVERIFIED.search(line) \
                and not any(int(m.group(1)) >= int(active) for m in PIN.finditer(line)):
            yield "stale-pin", (
                f"pinned to release {match.group(1)}, active is {active}; re-verify "
                f"or say it was not re-verified")
    for label in HELP_LABEL.finditer(line):
        for ident in HELP_ID.findall(label.group(1)):
            homes = [r for r, ids in index.items() if ident in ids]
            if not homes:
                yield "help-id", f"`{ident}` is in no help snapshot"
            elif active in index and active not in homes:
                if all(int(r) > int(active) for r in homes):
                    continue
                if not any(re.search(rf"\b{r}\b", line) for r in homes):
                    yield "help-id", (
                        f"`{ident}` is missing from the {active} snapshot "
                        f"(only in {', '.join(sorted(homes))}) and the line names none")


def skill_files(root: Path) -> list:
    return sorted(p for p in (root / SKILLS).rglob("*.md") if p.is_file())


def main(argv: list, root: Path = REPO) -> int:
    try:
        active = active_release(root)
        index = help_index(root)
        paths = [Path(a).resolve() for a in argv] if argv else skill_files(root)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    total = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for number, rule, message in findings(text, root, active, index):
            total += 1
            print(f"{rel}:{number}: {rule}: {message}")
    print(f"\n{len(paths)} files scanned, {total} staleness finding(s).")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
