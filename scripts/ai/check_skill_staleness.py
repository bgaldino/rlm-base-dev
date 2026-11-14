#!/usr/bin/env python3
"""Flag stale release references and missing Help ids in `.cursor/skills/**/*.md`.

The active release is `salesforce_release_active` in `.claude/skill-manifest.yml`. Per-release
snapshots live under `docs/salesforce/<N>/`. Text is read in blocks (a paragraph, a list item,
a table row, a heading, or one line inside a code fence), so a label or pin that wraps onto the
next line is still read whole. A finding reports the line its match starts on; one finding per
distinct message on a line. Three rules:

* `snapshot-link`: a path `docs/salesforce/<N>/<rel>` where N is older than the active release
  and the same `<rel>` exists, with the same case, under the active release (a `:line` suffix
  is not part of the path). Repoint it. A path that exists only in the older snapshot is
  allowed (the content was dropped or never carried forward); a newer N is never flagged.
* `stale-pin`: "Verified on Release <N>" / "verified on <N>" with N older than the active
  release, unless the same block says it was not re-verified (`not re-verified`, `not yet
  re-verified`, `not been re-verified`) or also pins the active release or a newer one; either
  exempts every pin in that block.
* `help-id`: an id in an evidence label `[Help: \\`ind.xxx\\`, ...]` (ids may be comma- or
  semicolon-separated; `.htm`, `.md` and `.htm.md` suffixes are optional) that exists in no
  `docs/salesforce/*/help/articles/` snapshot, or that is missing from the active snapshot
  but present in an older one and the block does not name that older release number. An id
  found only in snapshots newer than the active release is not flagged. If the active release
  has no Help snapshot, only the in-no-snapshot case applies.

Intentional cases carry the full marker `<!-- staleness: allow -->` on a line the match spans;
it exempts only matches touching that line. Use it for a deliberate older-release citation, never to
silence a real stale pin.

Usage:
    python scripts/ai/check_skill_staleness.py            # scan every skill markdown file
    python scripts/ai/check_skill_staleness.py FILE...    # scan these files only

Output: one line per finding, `path:line: rule: message`. Stdlib only.
Exit codes: 0 = clean, 1 = findings, 2 = tool error.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOW = "<!-- staleness: allow -->"
MANIFEST = Path(".claude/skill-manifest.yml")
SKILLS = Path(".cursor/skills")
SNAPSHOTS = Path("docs/salesforce")

ACTIVE_KEY = re.compile(r"^salesforce_release_active:\s*[\"']?(\d+)[\"']?", re.MULTILINE)
SNAP_PATH = re.compile(r"docs/salesforce/(\d+)/([^\s)`'\"\]>#,;|:]+)")
PIN = re.compile(r"\bverified\s+on\s+(?:release\s+)?(\d{3})\b", re.IGNORECASE)
NOT_REVERIFIED = re.compile(r"\bnot\s+(?:yet\s+)?(?:been\s+)?re-?verified", re.IGNORECASE)
HELP_LABEL = re.compile(r"\[Help:([^\]]*)\]")
HELP_ID = re.compile(r"`(ind\.[\w.-]+?)(?:\.htm)?(?:\.md)?`")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
OWN_BLOCK = re.compile(r"^\s*(\||#{1,6}(\s|$))")
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s")


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


def exists_exact(root: Path, rel: str) -> bool:
    """True if root/rel exists with the same case in every part (macOS is case-insensitive)."""
    current = root
    for part in Path(rel).parts:
        try:
            if part not in os.listdir(current):
                return False
        except OSError:
            return False
        current = current / part
    return True


def closes(marker: str, opener: str, line: str) -> bool:
    """A fence closes on the same character, at least as long, with nothing after it."""
    return (marker[0] == opener[0] and len(marker) >= len(opener)
            and not line.strip()[len(marker):])


def blocks(lines: list):
    """Yield (first line number, lines) for each block; see the module docstring."""
    block, start, fence_open = [], 0, ""
    for number, line in enumerate(lines, 1):
        fence = FENCE.match(line)
        own = fence_open or fence or OWN_BLOCK.match(line)
        if block and (own or not line.strip() or LIST_ITEM.match(line)):
            yield start, block
            block = []
        if fence and not fence_open:
            fence_open = fence.group(1)
        elif fence and closes(fence.group(1), fence_open, line):
            fence_open = ""
        if own:
            yield number, [line]
        elif line.strip():
            if not block:
                start = number
            block.append(line)
    if block:
        yield start, block


def findings(text: str, root: Path, active: str, index: dict):
    seen = set()
    for start, block in blocks(text.splitlines()):
        joined = "\n".join(block)
        for pos, end, rule, message in _block_findings(joined, root, active, index):
            first = joined.count("\n", 0, pos)
            last = joined.count("\n", 0, end)
            if any(ALLOW in block[i] for i in range(first, last + 1)):
                continue
            number = start + first
            if (number, rule, message) not in seen:
                seen.add((number, rule, message))
                yield number, rule, message


def _block_findings(text: str, root: Path, active: str, index: dict):
    for match in SNAP_PATH.finditer(text):
        release, rel = match.group(1), match.group(2).rstrip(".")
        if int(release) >= int(active) or any(c in rel for c in "<*{$"):
            continue
        if exists_exact(root, str(SNAPSHOTS / active / rel)):
            yield match.start(), match.end(), "snapshot-link", (
                f"docs/salesforce/{release}/{rel} exists under {active}; repoint it")
    pins = list(PIN.finditer(text))
    exempt = NOT_REVERIFIED.search(text) or any(int(m.group(1)) >= int(active) for m in pins)
    for match in pins:
        if int(match.group(1)) < int(active) and not exempt:
            yield match.start(), match.end(), "stale-pin", (
                f"pinned to release {match.group(1)}, active is {active}; re-verify "
                f"or say it was not re-verified")
    for label in HELP_LABEL.finditer(text):
        for ident in HELP_ID.findall(label.group(1)):
            homes = [r for r, ids in index.items() if ident in ids]
            if not homes:
                yield label.start(), label.end(), "help-id", f"`{ident}` is in no help snapshot"
            elif active in index and active not in homes:
                if all(int(r) > int(active) for r in homes):
                    continue
                if not any(re.search(rf"\b{r}\b", text) for r in homes):
                    yield label.start(), label.end(), "help-id", (
                        f"`{ident}` is missing from the {active} snapshot "
                        f"(only in {', '.join(sorted(homes))}) and the block names none")


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
