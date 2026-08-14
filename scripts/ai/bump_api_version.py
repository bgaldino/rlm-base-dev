#!/usr/bin/env python3
"""Bump the Salesforce API version pinned across the repo (e.g. 67.0 -> 68.0).

Release cutovers have to move every API pin in the tree at once. The 66.0 -> 67.0
bump (commit `4ed9be1b`) was a one-shot manual edit over 127 files, and it missed
whole classes of pin that are *still* stale: 51 meta.xml left at 66.0, nine SFDMU
plans at 66/65, the Robot `SalesforceAPI.py` at v66.0, and several task fallbacks.
This script exists so the next cutover is mechanical, reviewable, and repeatable.

It normalizes every pin it knows about to the target version, rather than only
rewriting the previous release's value -- so historical drift gets corrected in
the same pass instead of accumulating.

Two things it deliberately does NOT touch:

  * Version *floors* (`MIN_API_VERSION`) and non-API versions (the SFDMU plugin
    floor, content-asset `<version>` tags, `32767.0` in gltfFileLoader.js).
  * **Provenance** -- text recording what was observed or verified at a past
    release. Rewriting "verified on 262 / v67.0" to say 264/v68.0 would assert a
    verification that never happened. Same reasoning excludes
    `docs/erds/erd-data.json`, whose metadata block describes which orgs the ERD
    was extracted from; it changes only when the ERD is regenerated.

Usage:
  python scripts/ai/bump_api_version.py                  # dry run (default)
  python scripts/ai/bump_api_version.py --apply
  python scripts/ai/bump_api_version.py --to 69.0 --apply
  python scripts/ai/bump_api_version.py --verbose         # list every change
"""
from __future__ import annotations

import argparse
import functools
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Iterable, Pattern

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@functools.lru_cache(maxsize=1)
def tracked_files() -> frozenset[str]:
    """Every git-tracked path, repo-relative.

    Scope is deliberately limited to tracked files. Walking the working tree
    instead picks up gitignored build output -- retrieved metadata under
    `unpackaged/post_ux/`, extracted SFDMU data, `.rescan_tmp/` -- which more
    than doubles the apparent file count and would rewrite artifacts that get
    regenerated anyway.
    """
    out = subprocess.run(
        ["git", "-C", REPO_ROOT, "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return frozenset(p for p in out.split("\0") if p)

# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------

# Path prefixes never rewritten, with the reason each one is off-limits.
EXCLUDED_PREFIXES: dict[str, str] = {
    ".git/": "vcs internals",
    ".agents/": "private agent artifacts, not shipped config",
    "docs/salesforce/": "frozen per-release Help/dev-guide snapshot corpora",
    "docs/enablement/260/": "frozen per-release enablement extract",
    "docs/enablement/262/": "frozen per-release enablement extract",
    "postman/": "collection is version-branded end to end; regenerate, do not sed",
    # Arrives via forward-merge of PR #356. The bundle is intentionally kept at
    # the older version as the base copy against a `post_mcp_264` overlay, and
    # tests/test_mcp_overlay_parity.py asserts exactly that split -- a blanket
    # sweep would silently collapse the design and break the test.
    "unpackaged/post_mcp/": "deliberate dual-baseline overlay split (see PR #356)",
    # Arrives via forward-merge of PR #289. Its low pins (61-63) may be
    # deliberate for the Babylon.js/RenderDraw prototype; confirm before sweeping.
    "unpackaged/post_manufacturing_visualization/": (
        "low pins may be deliberate for the 3D prototype; confirm before normalizing"
    ),
}

# Individual files never rewritten.
EXCLUDED_FILES: dict[str, str] = {
    "docs/erds/erd-data.json": (
        "metadata.release/apiVersion are provenance describing which orgs the ERD "
        "was extracted from; changes only when the ERD is regenerated"
    ),
    # Salesforce sample Aura Local Action (c) 2018, vendored verbatim. Ancient
    # pins are normal for this pattern and bumping it means retesting Aura.
    "unpackaged/post_manufacturing_core/aura/OpenSObject/OpenSObject.cmp-meta.xml": (
        "vendored 2018 Salesforce sample Aura component"
    ),
}

# Exact (path, 1-based line) pairs holding provenance rather than a live pin.
EXCLUDED_LINES: dict[tuple[str, int], str] = {
    ("scripts/context_service/examples/contextServiceLifecycle.apex", 28): (
        "records dataPath semantics as verified on 262/v67.0"
    ),
    ("unpackaged/post_utils/classes/RLM_DecisionTableManagerController.cls", 238): (
        "records bindingobjectformula behavior as observed at 262/v67.0"
    ),
}

# Any line matching one of these keeps its version, wherever it appears: the
# version is part of a statement about the past, or a floor, not a pin.
PROVENANCE_LINE_RE = re.compile(
    r"verified (?:on|live|against)|as[- ]of|observed (?:on|at)|MIN_API_VERSION",
    re.IGNORECASE,
)


def excluded_reason(rel_path: str) -> str | None:
    """Return why `rel_path` is excluded, or None if it is in scope."""
    if rel_path in EXCLUDED_FILES:
        return EXCLUDED_FILES[rel_path]
    for prefix, reason in EXCLUDED_PREFIXES.items():
        if rel_path.startswith(prefix):
            return reason
    return None


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


@dataclass
class Rule:
    """One class of API pin: which files to look at and how to rewrite them."""

    name: str
    description: str
    pattern: Pattern[str]
    # Builds the replacement from a match and the target version.
    replace: Callable[[re.Match[str], str], str]
    # Files matched: either explicit relative paths or a (suffix, root) filter.
    paths: tuple[str, ...] = ()
    suffixes: tuple[str, ...] = ()
    roots: tuple[str, ...] = ()
    # Optional per-file veto, given the file's full text.
    skip_file_if: Callable[[str], bool] | None = None
    changed: list[str] = field(default_factory=list, repr=False)

    def files(self) -> Iterable[str]:
        tracked = tracked_files()
        if self.paths:
            for rel in self.paths:
                if rel in tracked:
                    yield rel
            return
        for rel in tracked:
            if not rel.endswith(self.suffixes):
                continue
            if self.roots and not any(
                rel == root or rel.startswith(root + "/") for root in self.roots
            ):
                continue
            yield rel


def _version_only(match: re.Match[str], target: str) -> str:
    """Replace just the numeric version inside the match, keeping delimiters."""
    return match.group(0).replace(match.group("ver"), target)


def build_rules() -> list[Rule]:
    return [
        Rule(
            name="sfdx-project",
            description="sfdx-project.json sourceApiVersion",
            paths=("sfdx-project.json",),
            pattern=re.compile(r'"sourceApiVersion"\s*:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="cumulusci",
            description="cumulusci.yml project.package.api_version (quoted values only)",
            paths=("cumulusci.yml",),
            # Only quoted values. `api_version: null` has no quotes, so the four
            # optional task overrides are untouched and stay null by construction.
            pattern=re.compile(r'(?m)^(?P<indent>\s+)api_version:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="meta-xml",
            description="<apiVersion> in *-meta.xml",
            suffixes=("-meta.xml",),
            pattern=re.compile(r"<apiVersion>(?P<ver>\d+\.\d+)</apiVersion>"),
            replace=_version_only,
        ),
        Rule(
            name="sfdmu",
            description='"apiVersion" in SFDMU export.json',
            roots=("datasets",),
            suffixes=("export.json",),
            pattern=re.compile(r'"apiVersion"\s*:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="python",
            description="Python defaults/fallbacks (66.0, 67.0; floors untouched)",
            roots=("tasks", "scripts", "robot"),
            suffixes=(".py",),
            # Only 66.0/67.0 so MIN_API_VERSION = "65.0" is out of range by
            # construction. Keeps the quote style and any 'v' prefix.
            pattern=re.compile(r"""(?P<q>['"])(?P<v>v?)(?P<ver>6[67]\.0)(?P=q)"""),
            replace=_version_only,
        ),
        Rule(
            name="python-service-path",
            description="Hardcoded /services/data/vNN.0/ paths embedded in Python strings",
            roots=("tasks", "scripts", "robot"),
            suffixes=(".py",),
            # The "python" rule above requires the version to be the *entire*
            # quoted literal, so a version embedded in a longer string is
            # structurally unmatchable there. That left ~10 live v67.0 endpoints
            # in scripts/docgen/ behind on the 264 bump. Range starts at 60.0
            # because these are live endpoints, not floors, and the
            # PROVENANCE_LINE_RE guard still spares verified-on notes.
            pattern=re.compile(r"(?P<pre>/services/data/v)(?P<ver>6[0-7]\.0)(?P<post>/)"),
            replace=_version_only,
        ),
        Rule(
            name="apex",
            description="Hardcoded REST paths and constants in .cls/.apex",
            suffixes=(".cls", ".apex"),
            pattern=re.compile(r"(?P<pre>v)(?P<ver>6[0-7]\.0)"),
            replace=_version_only,
        ),
    ]


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def process(rule: Rule, target: str, apply: bool, verbose: bool) -> tuple[int, int, Counter]:
    """Rewrite matches for one rule. Returns (files_changed, hits, skipped)."""
    files_changed = 0
    hits = 0
    skipped: Counter = Counter()

    for rel in sorted(set(rule.files())):
        reason = excluded_reason(rel)
        if reason:
            skipped[reason] += 1
            continue

        abs_path = os.path.join(REPO_ROOT, rel)
        try:
            with open(abs_path, encoding="utf-8") as fh:
                original = fh.read()
        except (UnicodeDecodeError, OSError):
            continue

        if rule.skip_file_if and rule.skip_file_if(original):
            skipped["per-file veto"] += 1
            continue

        # Rewrite line by line so provenance lines can be spared individually.
        out_lines: list[str] = []
        file_hits = 0
        for lineno, line in enumerate(original.splitlines(keepends=True), start=1):
            if (rel, lineno) in EXCLUDED_LINES:
                skipped[EXCLUDED_LINES[(rel, lineno)]] += 1
                out_lines.append(line)
                continue
            if PROVENANCE_LINE_RE.search(line):
                if rule.pattern.search(line):
                    skipped["provenance / floor line"] += 1
                out_lines.append(line)
                continue

            new_line, n = rule.pattern.subn(lambda m: rule.replace(m, target), line)
            if n and new_line != line:
                file_hits += n
                if verbose:
                    print(f"    {rel}:{lineno}")
                    print(f"      - {line.rstrip()}")
                    print(f"      + {new_line.rstrip()}")
            out_lines.append(new_line)

        if not file_hits:
            continue

        files_changed += 1
        hits += file_hits
        rule.changed.append(rel)
        if apply:
            with open(abs_path, "w", encoding="utf-8") as fh:
                fh.write("".join(out_lines))

    return files_changed, hits, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump the Salesforce API version pinned across the repo.",
    )
    parser.add_argument(
        "--to", default="68.0", help="Target API version, e.g. 68.0 (default: 68.0)"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default is a dry run)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print every individual change"
    )
    parser.add_argument(
        "--only", action="append", metavar="RULE",
        help="Limit to named rule(s); repeatable. Names: "
             + ", ".join(r.name for r in build_rules()),
    )
    args = parser.parse_args()

    if not re.fullmatch(r"\d+\.\d+", args.to):
        print(f"error: --to must look like 68.0, got {args.to!r}", file=sys.stderr)
        return 2

    rules = build_rules()
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {r.name for r in rules}
        if unknown:
            print(f"error: unknown rule(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        rules = [r for r in rules if r.name in wanted]

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"Bumping API version to {args.to}  [{mode}]\n")

    total_files = 0
    total_hits = 0
    all_skipped: Counter = Counter()

    for rule in rules:
        print(f"  {rule.name}: {rule.description}")
        files_changed, hits, skipped = process(rule, args.to, args.apply, args.verbose)
        all_skipped.update(skipped)
        total_files += files_changed
        total_hits += hits
        if hits:
            print(f"    {hits} replacement(s) in {files_changed} file(s)")
        else:
            print("    already at target, nothing to do")
        print()

    print(f"Total: {total_hits} replacement(s) across {total_files} file(s)")

    if all_skipped:
        print("\nDeliberately skipped:")
        for reason, count in sorted(all_skipped.items(), key=lambda kv: -kv[1]):
            print(f"  {count:4d}  {reason}")

    if not args.apply and total_hits:
        print("\nDry run only. Re-run with --apply to write these changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
