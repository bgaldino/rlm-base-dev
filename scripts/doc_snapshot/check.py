#!/usr/bin/env python3
"""Lint the captured corpus: a footer gate, and two spot-checks.

Gate (``--release R`` or ``--active``): every ``docs/salesforce/R/*/articles/*.md`` that
has frontmatter with a ``source_url`` must end with the source-attribution footer
(``_core.attribution_state``, the same test the backfill uses). A missing footer, or a
file that cannot be read, has a BOM or unterminated frontmatter, exits 1; fix with
``python -m scripts.doc_snapshot backfill-attribution --release R``. Files with no
frontmatter or no ``source_url`` are listed, not failed. ``--active`` reads R from
``salesforce_release_active`` in ``.claude/skill-manifest.yml`` (pr_gate runs it).
Without either flag the gate is skipped: frozen older snapshots predate the footer.

Spot-checks (not gates): glued-link text artifacts in the Help corpus, and
``X, formerly X`` rename artifacts in every corpus.

Salesforce's Help portal occasionally ships source HTML with a link-intro
verb directly abutting the link text with no separating space (e.g.
"...a rating element. See<a>Create a Constant Resource</a>." renders as
"SeeCreate a Constant Resource."). The help snapshot (``help_portal``) captures
`innerText` verbatim, so this is a faithful capture of an upstream content
defect, not a bug in the extraction JS (confirmed by inspecting the live
DOM for known instances; see todo 184 in the artifacts repo). Recapturing
does not fix it; only a hand-edit of the affected article does. Only 3
instances have ever been found, so a hit means "go look," not "fail the build."

Usage:
    python -m scripts.doc_snapshot check [--release 264 | --active]
    python scripts/doc_snapshot/check.py [--release 264 | --active]
"""
import argparse
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.doc_snapshot._core import BOM_HINT, is_failure, scan_attribution  # noqa: E402

MANIFEST = Path(".claude/skill-manifest.yml")
# Same pattern as scripts/ai/check_skill_staleness.py (not shared: that module is a gate script
# with its own constants, and importing it here would couple two tools for one regex).
ACTIVE_KEY = re.compile(r"^salesforce_release_active:[ \t]*[\"']?(\d+)[\"']?[ \t]*(?:#.*)?$", re.M)

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_GLOB = "docs/salesforce/{release}/help/articles/*.md"

# Known link-intro verbs that should never be directly glued to the
# capitalized word that follows them. Deliberately excludes verbs like
# "Create"/"Add"/"Use"/"Enable" -- those are common leading words in API
# action-name identifiers (e.g. "AddGroup", "CreateRampSchedule") that this
# script would otherwise misflag; every verb below was checked against the
# full corpus and produces zero false positives.
GLUED_LINK_RE = re.compile(
    r"\b(See|Refer to|Click|Select|View)"
    r"([A-Z][a-z]+)"
)


# Salesforce renamed the product, then ran the new name over the old one in
# the release notes: "Agentforce Revenue Management, formerly Revenue Cloud"
# became "Revenue Cloud, formerly Revenue Cloud". The snapshot tool rewrites no
# text, so this is served that way upstream (inferred from the tool, which has
# no brand substitution; not re-checked against the live page).
# A word boundary before the name keeps "McDonald, formerly Donald" out; the
# lookahead after it keeps "Sales, formerly Salesforce", "Sales, formerly
# Sales-Cloud" and "Agentforce Sales, formerly Sales Cloud" (a longer old name
# that merely starts like the new one) out. It misses, by design, a real artifact
# followed by a capitalised word, a word character or "-", names of five or more words,
# and names that are not plain Capitalised words: acronyms, digits or non-ASCII
# letters ("Salesforce CPQ", "B2B Commerce").
SELF_RENAME_RE = re.compile(
    r"\b((?:[A-Z][a-z]+ ){0,3}[A-Z][a-z]+), formerly \1(?![\w-]| [A-Z])"
)
ALL_CORPORA_GLOB = "docs/salesforce/{release}/*/articles/*.md"


def _read(path):
    """The file's text, or None when unreadable (the footer scan reports those)."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def find_self_renames(paths):
    """``X, formerly X`` brand-rename artifacts: (path, line, snippet)."""
    findings = []
    for path in paths:
        text = _read(path)
        if text is None or ", formerly " not in text:
            continue
        for m in SELF_RENAME_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append((path, line_no, m.group(0)))
    return findings


def find_artifacts(paths):
    findings = []
    for path in paths:
        text = _read(path)
        if text is None:
            continue
        for m in GLUED_LINK_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append((path, line_no, m.group(0)))
    return findings


def active_release(root=None):
    """``salesforce_release_active`` from the skill manifest; raises OSError when absent."""
    path = (root or REPO_ROOT) / MANIFEST
    m = ACTIVE_KEY.search(path.read_text(encoding="utf-8"))
    if not m:
        raise OSError(f"salesforce_release_active not found in {MANIFEST}")
    return m.group(1)


def footer_problems(release):
    """``(missing, skipped)`` over every ``docs/salesforce/<release>/*/articles``, built on
    ``_core.scan_attribution`` so ``check`` and the backfill agree by construction.
    ``missing``: ``(path, source_url)``; ``skipped``: ``(path, reason)``."""
    missing, skipped = [], []
    for articles in sorted((REPO_ROOT / "docs" / "salesforce" / release).glob("*/articles")):
        miss, skip = scan_attribution(articles)
        missing += [(articles / n, u) for n, u in miss]
        skipped += [(articles / n, r) for n, r in skip]
    return missing, skipped


def scan(release=None):
    """Scan one release's Help corpus (or every release's). Returns 1 when an article of the
    named release lacks the attribution footer, or cannot be judged for a real reason
    (unreadable, ``bom-frontmatter``, ``unterminated-frontmatter``); ``no-frontmatter`` and
    ``no-source_url`` files are listed only. Else 0."""
    failed = False
    # Only for a named release: frozen snapshots (e.g. 262) predate the footer and are left as-is.
    if release:
        missing, skipped = footer_problems(release)
        if missing:
            print(f"{len(missing)} article(s) without the source-attribution footer:")
            for path, _ in missing:
                print(f"  {path.relative_to(REPO_ROOT)}")
            print(f"  Run `python -m scripts.doc_snapshot backfill-attribution --release {release}`.\n")
        if skipped:
            print(f"{len(skipped)} article(s) the footer check could not judge:")
            for path, reason in skipped:
                print(f"  {path.relative_to(REPO_ROOT)}: {reason}")
            if any(r == "bom-frontmatter" for _, r in skipped):
                print(f"  bom-frontmatter: {BOM_HINT}.")
            print()
        failed = bool(missing) or any(is_failure(r) for _, r in skipped)
    else:
        print("Footer check skipped: pass --release R or --active (frozen older snapshots predate the footer).\n")
    rc = _scan_help(release)
    return 1 if failed else rc


def _scan_help(release):
    corpus_glob = CORPUS_GLOB.format(release=release or "*")
    paths = sorted(REPO_ROOT.glob(corpus_glob))

    # The rename scan covers every captured corpus (Help, release notes, dev
    # guides), so it runs even when there is no Help corpus to lint.
    renames = find_self_renames(sorted(REPO_ROOT.glob(ALL_CORPORA_GLOB.format(release=release or "*"))))
    if renames:
        print(f"{len(renames)} self-referential rename(s) ('X, formerly X'), upstream text:")
        for path, line_no, snippet in renames:
            print(f"  {path.relative_to(REPO_ROOT)}:{line_no}: {snippet!r}")
        print("  Served that way by the source; a recapture will not change it.\n")

    if not paths:
        print(f"No corpus files matched {corpus_glob}")
        return 0

    findings = find_artifacts(paths)
    if not findings:
        print(f"Scanned {len(paths)} article(s); 0 glued-link artifacts found.")
        return 0

    print(f"Scanned {len(paths)} article(s); {len(findings)} glued-link artifact(s) found:")
    for path, line_no, snippet in findings:
        print(f"  {path.relative_to(REPO_ROOT)}:{line_no}: {snippet!r}")
    print(
        "\nVerify each candidate against the live DOM before acting -- this "
        "regex flags a pattern, not a confirmed defect. A genuine hit is an "
        "upstream Salesforce content typo, faithfully captured verbatim, so "
        "recapturing will not fix it. Hand-fix only in the active release's "
        "corpus (e.g. docs/salesforce/264/); frozen snapshots (e.g. "
        "docs/salesforce/262/) are left as-is by design."
    )
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--release", help="limit the scan to one release, e.g. 264")
    parser.add_argument("--active", action="store_true",
                        help="the release named by salesforce_release_active in the skill manifest")
    args = parser.parse_args(argv)
    if args.active and args.release:
        parser.error("--active and --release are exclusive")
    try:
        return scan(active_release() if args.active else args.release)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
