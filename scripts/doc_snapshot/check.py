#!/usr/bin/env python3
"""Scan the captured Help corpus for glued-link text artifacts.

Salesforce's Help portal occasionally ships source HTML with a link-intro
verb directly abutting the link text with no separating space (e.g.
"...a rating element. See<a>Create a Constant Resource</a>." renders as
"SeeCreate a Constant Resource."). The help snapshot (``help_portal``) captures
`innerText` verbatim, so this is a faithful capture of an upstream content
defect, not a bug in the extraction JS (confirmed by inspecting the live
DOM for known instances — see todo 184 in the artifacts repo). Recapturing
does not fix it; only a hand-edit of the affected article does.

This script is a spot-check, not a gate: only 3 instances have ever been
found across the whole corpus, so a hit here means "go look," not "fail
the build."

Usage:
    python -m scripts.doc_snapshot check [--release 264]
    python scripts/doc_snapshot/check.py [--release 264]
"""
import argparse
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.doc_snapshot._core import attribution_state  # noqa: E402

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


def find_self_renames(paths):
    """``X, formerly X`` brand-rename artifacts: (path, line, snippet)."""
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if ", formerly " not in text:
            continue
        for m in SELF_RENAME_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append((path, line_no, m.group(0)))
    return findings


def find_artifacts(paths):
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for m in GLUED_LINK_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append((path, line_no, m.group(0)))
    return findings


def find_missing_footers(paths):
    """``(path, source_url)`` of each article with frontmatter and a source_url but no
    attribution footer; the same test as the backfill (``_core.attribution_state``)."""
    out = []
    for path in paths:
        try:
            state, url = attribution_state(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if state == "missing":
            out.append((path, url))
    return out


def scan(release=None):
    """Scan one release's Help corpus (or every release's); returns 1 when an article of the
    named release lacks the attribution footer, else 0."""
    # Only for a named release: frozen snapshots (e.g. 262) predate the footer and are left as-is.
    missing = (find_missing_footers(sorted(REPO_ROOT.glob(ALL_CORPORA_GLOB.format(release=release))))
               if release else [])
    if not release:
        print("Footer check skipped: pass --release R (frozen older snapshots predate the footer).\n")
    if missing:
        print(f"{len(missing)} article(s) without the source-attribution footer:")
        for path, _ in missing:
            print(f"  {path.relative_to(REPO_ROOT)}")
        print("  Run `python -m scripts.doc_snapshot backfill-attribution --release R`.\n")
    rc = _scan_help(release)
    return 1 if missing else rc


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
    args = parser.parse_args(argv)
    return scan(args.release)


if __name__ == "__main__":
    sys.exit(main())
