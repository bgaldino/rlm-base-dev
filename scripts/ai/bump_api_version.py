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

Match the *whole* two-digit version range in every rule, including the current
target. A range capped at the target (`6[0-7]` when 68.0 is current) stops
matching the moment the repo reaches that target, and then reports "already at
target, nothing to do" — indistinguishable from a clean repo. That has now cost
this script two rules: `python` was blind to 37 in-scope literals and `apex` to
8. Matching the target is a harmless no-op.

Usage:
  python scripts/ai/bump_api_version.py                  # dry run (default)
  python scripts/ai/bump_api_version.py --apply
  python scripts/ai/bump_api_version.py --to 69.0 --apply
  python scripts/ai/bump_api_version.py --verbose         # list every change
  python scripts/ai/bump_api_version.py --check           # exit 1 if anything is off-target
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
    # Same grammar doc-consistency/SKILL.md publishes for the markdown sweep --
    # live-<past participle> and verified <preposition> -- because the two were
    # written independently and drifted: the sweep learned `live-verified`,
    # `live-proven`, `verified by/via/payload` while this guard still knew only
    # `verified on|live|against`. Nothing was being mis-rewritten yet (checked: zero
    # lines today carry one of the missing forms *and* a pattern any rule matches),
    # but the asymmetry was a live trap -- add a service path to a line reading
    # "live-verified v67.0" and the bump would have rewritten the claim. Kept in step
    # deliberately; validate_rules() asserts each form is spared.
    r"live-(?:verified|tested|proven|confirmed)"
    r"|verified (?:live|on|in|against|by|via|payload)"
    r"|as[- ]of|observed (?:on|at)|MIN_API_VERSION",
    re.IGNORECASE,
)


# Probe bounds, kept as ints rather than "NN.0" strings on purpose: this file is
# itself in the `python` rule's scope, and that rule matches any quoted two-digit
# version literal, so written the obvious way it would rewrite its own probes to the
# target and quietly disarm the self-test below.
PROBE_FLOOR = 60
PROBE_CEILING = 99


def validate_rules(rules: list[Rule], target: str) -> list[str]:
    """Assert every rule still matches input it is *defined* to match.

    This is the independent leg ``--check`` needs. ``total_hits`` comes out of these
    same patterns, so the two states "everything is at the target" and "this rule
    went blind" are numerically identical -- both zero. That is not hypothetical:
    the capped ranges (``6[67]``, ``6[0-7]``) stopped matching once the repo reached
    68.0 and reported "already at target, nothing to do" while 37 and 8 in-scope
    literals sat untouched.

    Each rule is probed at a version *below* the target, at the target itself, and
    at one *above* it, because the failure mode is specifically a range that no
    longer reaches. A rule must also rewrite its probe to the target, which catches
    a pattern that matches but whose replacement has lost a group.
    """
    problems: list[str] = []
    for rule in rules:
        if not rule.probe:
            problems.append(f"{rule.name}: no probe defined, so --check cannot verify this rule")
            continue
        for ver in (f"{PROBE_FLOOR}.0", target, next_version(target)):
            text = rule.probe.format(ver=ver)
            m = rule.pattern.search(text)
            if not m:
                problems.append(
                    f"{rule.name}: pattern no longer matches its own probe at v{ver} "
                    f"({text!r}) — the rule has gone blind and would silently skip "
                    "every occurrence of this class"
                )
                continue
            rewritten = rule.pattern.sub(lambda mm: rule.replace(mm, target), text)
            if rewritten != rule.probe.format(ver=target):
                problems.append(
                    f"{rule.name}: matched its probe at v{ver} but rewrote it to "
                    f"{rewritten!r} instead of {rule.probe.format(ver=target)!r}"
                )
    problems.extend(validate_provenance_grammar())
    return problems


# The provenance grammar, spelled out so a regression names the form it lost rather
# than just failing a regex comparison. Kept in step with the sweep expression in
# doc-consistency/SKILL.md.
PROVENANCE_FORMS = (
    "live-verified", "live-tested", "live-proven", "live-confirmed",
    "verified live", "verified on", "verified in", "verified against",
    "verified by", "verified via", "verified payload",
    "as of", "as-of", "observed on", "observed at", "MIN_API_VERSION",
)


def validate_provenance_grammar() -> list[str]:
    """Assert PROVENANCE_LINE_RE still spares every documented provenance form.

    The guard and the markdown sweep encode the same idea in two places and had
    already drifted once -- the sweep knew `live-proven` and `verified by`, this did
    not -- so a form silently dropping out is a real failure mode. A rewrite of a
    line that says "live-verified v67.0" turns evidence into a false claim, which is
    worse than missing a bump.
    """
    return [
        f"PROVENANCE_LINE_RE no longer spares {form!r} — a line carrying that "
        "provenance marker would be rewritten, turning a capture into a false claim"
        for form in PROVENANCE_FORMS
        if not PROVENANCE_LINE_RE.search(f"# {form} v67.0 — some note")
    ]


def next_version(target: str) -> str:
    """The release after ``target`` — Salesforce API versions step by 1.0 per release."""
    try:
        return f"{int(float(target)) + 1}.0"
    except ValueError:
        return f"{PROBE_CEILING}.0"


def validate_excluded_lines() -> list[str]:
    """Check every EXCLUDED_LINES entry still points at a version-bearing line.

    These entries are keyed on a 1-based line number, and nothing kept them
    honest: insert a line above one and the exclusion silently starts shielding
    an unrelated line while the rule rewrites the provenance it was meant to
    protect. Worse, ``process`` counts the skip either way, so the run report
    still says the original line was spared. Cheap to detect — if the recorded
    line no longer contains a version at all, the key has drifted.
    """
    problems: list[str] = []
    for (rel_path, lineno), reason in sorted(EXCLUDED_LINES.items()):
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.isfile(abs_path):
            problems.append(f"{rel_path}:{lineno} — file no longer exists ({reason})")
            continue
        with open(abs_path, encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
        if lineno < 1 or lineno > len(lines):
            problems.append(
                f"{rel_path}:{lineno} — out of range, file has {len(lines)} line(s) ({reason})"
            )
            continue
        if not re.search(r"v?\d{2}\.0", lines[lineno - 1]):
            problems.append(
                f"{rel_path}:{lineno} — no API version on this line, so the key has "
                f"drifted ({reason}); line reads: {lines[lineno - 1].strip()[:70]!r}"
            )
    return problems


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
    # A synthetic line this rule MUST match, with {ver} where the version goes.
    # This is what makes --check mean anything: total_hits is produced by these
    # same patterns, so a rule that has quietly stopped matching contributes 0 and
    # is indistinguishable from a repo that is genuinely at the target. Probing
    # each pattern against input the rule is defined to match is independent of
    # repo contents, so blindness fails loudly instead of reporting PASS.
    probe: str = ""
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
            probe='"sourceApiVersion": "{ver}"',
            description="sfdx-project.json sourceApiVersion",
            paths=("sfdx-project.json",),
            pattern=re.compile(r'"sourceApiVersion"\s*:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="cumulusci",
            probe='    api_version: "{ver}"',
            description="cumulusci.yml project.package.api_version (quoted values only)",
            paths=("cumulusci.yml",),
            # Only quoted values. `api_version: null` has no quotes, so the four
            # optional task overrides are untouched and stay null by construction.
            pattern=re.compile(r'(?m)^(?P<indent>\s+)api_version:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="meta-xml",
            probe='<apiVersion>{ver}</apiVersion>',
            description="<apiVersion> in *-meta.xml",
            suffixes=("-meta.xml",),
            pattern=re.compile(r"<apiVersion>(?P<ver>\d+\.\d+)</apiVersion>"),
            replace=_version_only,
        ),
        Rule(
            name="sfdmu",
            probe='"apiVersion": "{ver}"',
            description='"apiVersion" in SFDMU export.json',
            roots=("datasets",),
            suffixes=("export.json",),
            pattern=re.compile(r'"apiVersion"\s*:\s*"(?P<ver>\d+\.\d+)"'),
            replace=_version_only,
        ),
        Rule(
            name="python",
            probe='API_VERSION = "v{ver}"',
            description="Python defaults/fallbacks (any vNN.0 literal; floors untouched)",
            roots=("tasks", "scripts", "robot"),
            suffixes=(".py",),
            # Any two-digit version, for the reason spelled out on
            # python-service-path below: this rule used to be capped at 6[67],
            # which went stale the moment the repo reached 68.0. It matched
            # nothing while 37 quoted 68.0 literals sat in scope, and reported
            # "already at target, nothing to do" -- affirmatively false, and the
            # next cutover would have silently skipped every one of them.
            #
            # The old cap was also justified as keeping MIN_API_VERSION out of
            # range, which is redundant: PROVENANCE_LINE_RE already contains
            # MIN_API_VERSION, and the only real floor
            # (tasks/rlm_manage_fulfillment_scope_cnfg.py) is on a line it
            # matches. Keeps the quote style and any 'v' prefix.
            pattern=re.compile(r"""(?P<q>['"])(?P<v>v?)(?P<ver>[0-9]{2}\.0)(?P=q)"""),
            replace=_version_only,
        ),
        Rule(
            # Scope note, deliberate: this rule handles versions embedded in a
            # *path*, and there is no companion rule for versions embedded in
            # ordinary prose (comments, help strings, docstrings). That is not an
            # oversight. Sampling every `vNN.0` in tasks/, scripts/ and robot/ that
            # no rule reaches found 74 occurrences, and all but two were release
            # provenance a bump must NOT touch -- "Pinned to Release 262 / v67.0",
            # "live-verified v67.0", "gone in v67.0", "introduced in API v65.0",
            # "required since API v58.0". A prose rule broad enough to catch the two
            # live ones would rewrite the other 72 into lies, and PROVENANCE_LINE_RE
            # does not save them (it matches "verified on/as of/observed on", not
            # "pinned to" or "introduced in"). The two real cases were duplicated
            # declarations, so they were fixed by removing the duplication instead:
            # argparse now renders the default with %(default)s, and the Robot
            # library's comment no longer restates the constant beneath it. A version
            # that appears once cannot drift from itself.
            name="python-service-path",
            probe='url = "/services/data/v{ver}/sobjects/Account"',
            description="Hardcoded /services/data/vNN.0/ paths embedded in Python strings",
            roots=("tasks", "scripts", "robot"),
            suffixes=(".py",),
            # The "python" rule above requires the version to be the *entire*
            # quoted literal, so a version embedded in a longer string is
            # structurally unmatchable there. That left ~10 live v67.0 endpoints
            # in scripts/docgen/ behind on the 264 bump.
            #
            # Any two-digit version matches, deliberately including the current
            # target: a range capped at the target (6[0-7] here) would go stale
            # the moment 68.0 became current, silently reintroducing this very
            # gap at the next cutover. Matching the target is a harmless no-op —
            # the runner reports "already at target". These are live endpoints,
            # never floors, and PROVENANCE_LINE_RE still spares verified-on notes.
            pattern=re.compile(r"(?P<pre>/services/data/v)(?P<ver>[0-9]{2}\.0)(?P<post>/)"),
            replace=_version_only,
        ),
        Rule(
            name="apex",
            probe="String path = '/services/data/v{ver}/query';",
            description="Hardcoded REST paths and constants in .cls/.apex",
            suffixes=(".cls", ".apex"),
            # Two-digit range for the same reason as the two rules above: capped
            # at 6[0-7], this stopped seeing anything at 68.0 or later. In tracked
            # scope its only remaining matches are a provenance line and the one
            # EXCLUDED_LINES entry, both deliberately skipped -- so it was already
            # inert on live code.
            pattern=re.compile(r"(?P<pre>v)(?P<ver>[0-9]{2}\.0)"),
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
        # %(default)s, and "NN.0" rather than a sample version, so this line holds no
        # second copy of the version. The `python` rule matches the bare quoted
        # default below but cannot reach a version inside the longer help string, so
        # spelling it twice meant `--to <next> --apply` moved the default while
        # --help kept reporting the old one -- the identical drift this script fixes
        # in docgen and the Robot library.
        "--to",
        default="68.0",
        help="Target API version as NN.0 (default: %(default)s)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default is a dry run)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print every individual change"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if anything in scope is still off-target (implies a dry run)",
    )
    parser.add_argument(
        "--only", action="append", metavar="RULE",
        help="Limit to named rule(s); repeatable. Names: "
             + ", ".join(r.name for r in build_rules()),
    )
    args = parser.parse_args()

    if not re.fullmatch(r"\d+\.\d+", args.to):
        print(f"error: --to must look like NN.0, got {args.to!r}", file=sys.stderr)
        return 2

    rules = build_rules()
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {r.name for r in rules}
        if unknown:
            print(f"error: unknown rule(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        rules = [r for r in rules if r.name in wanted]

    stale = validate_excluded_lines()
    if stale:
        print(
            "error: EXCLUDED_LINES is keyed on line numbers that have moved, so it is "
            "now protecting the wrong lines (and the run report would still claim the "
            "old ones were skipped):",
            file=sys.stderr,
        )
        for entry in stale:
            print(f"  {entry}", file=sys.stderr)
        print(
            "Re-point the line numbers, or better, reword the target lines so "
            "PROVENANCE_LINE_RE protects them by content instead of position.",
            file=sys.stderr,
        )
        return 2

    # Normalize the mode BEFORE the banner is built. --check forces a dry run, so
    # computing the banner first printed "[APPLY]" for `--apply --check` while the
    # run wrote nothing — telling a release operator the opposite of what happened.
    if args.check:
        args.apply = False
    mode = "APPLY" if args.apply else "DRY RUN"
    if args.check:
        mode = "CHECK (dry run)"
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

    if args.check:
        # Self-test the rules first. total_hits == 0 is ambiguous on its own -- it
        # means either "clean" or "this pattern matches nothing any more" -- so a
        # PASS is only meaningful once every rule has been shown to still match
        # input it is defined to match. Ordered first so a blind rule is reported
        # as a tooling failure rather than as a clean repo.
        blind = validate_rules(rules, args.to)
        if blind:
            print(
                "\ncheck: FAIL — rule self-test failed, so the counts above are not "
                "trustworthy (a rule matching nothing looks exactly like a clean repo):",
                file=sys.stderr,
            )
            for problem in blind:
                print(f"  {problem}", file=sys.stderr)
            return 2
        # Exit non-zero when anything in scope is still off-target. Without this
        # the tool could only ever report, so a rule that quietly stopped
        # matching -- the exact defect this script has now shipped twice -- looked
        # identical to a clean repo: "already at target, nothing to do".
        if total_hits:
            print(
                f"\ncheck: FAIL — {total_hits} occurrence(s) in {total_files} file(s) "
                f"are not at {args.to}.",
                file=sys.stderr,
            )
            return 1
        print(f"\ncheck: PASS — everything in scope is at {args.to}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
