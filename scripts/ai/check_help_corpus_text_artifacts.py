#!/usr/bin/env python3
"""Scan the captured Help corpus for glued-link text artifacts.

Salesforce's Help portal occasionally ships source HTML with a link-intro
verb directly abutting the link text with no separating space (e.g.
"...a rating element. See<a>Create a Constant Resource</a>." renders as
"SeeCreate a Constant Resource."). `SnapshotSalesforceHelp` captures
`innerText` verbatim, so this is a faithful capture of an upstream content
defect, not a bug in the extraction JS (confirmed by inspecting the live
DOM for known instances — see todo 184 in the artifacts repo). Recapturing
does not fix it; only a hand-edit of the affected article does.

This script is a spot-check, not a gate: only 3 instances have ever been
found across the whole corpus, so a hit here means "go look," not "fail
the build."
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_GLOB = "docs/salesforce/*/help/articles/*.md"

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


def find_artifacts(paths):
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for m in GLUED_LINK_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append((path, line_no, m.group(0)))
    return findings


def main():
    paths = sorted(REPO_ROOT.glob(CORPUS_GLOB))
    if not paths:
        print(f"No corpus files matched {CORPUS_GLOB}")
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


if __name__ == "__main__":
    sys.exit(main())
