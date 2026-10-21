#!/usr/bin/env python3
"""Fail a permission set that grants Account read without Contact read.

Salesforce rejects the deploy ("Permission Read Account depends on permission(s): Read
Contact") when a permission set grants read on Account but not on Contact. It is for the person
accounts in the TSO orgs: a person account is stored as an Account plus a Contact, so the platform
ties the two together, and an org with person accounts enabled enforces it at deploy time.
This repo has already patched it twice, in RLM_RenewalQuotes and RLM_BillingUI, each time
after a deploy failed. This lint moves the failure to the PR.

Scope: every tracked or untracked-not-ignored `*.permissionset-meta.xml` (the gate selects on a
new, unstaged one), except the generated `unpackaged/post_ux/`.
`allowRead`, `allowEdit`, `viewAllRecords` and `modifyAllRecords` on Account all imply read, so
any of them requires Contact read (Contact `viewAllRecords`/`modifyAllRecords` also satisfy it).

Usage: python scripts/ai/check_permission_set_dependencies.py [path ...]
With no paths it checks every permission set git lists. Stdlib only.
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NS = "{http://soap.sforce.com/2006/04/metadata}"
SKIP_PREFIXES = ("unpackaged/post_ux/",)
SUFFIX = ".permissionset-meta.xml"


def grants_read(root, obj):
    """True when the set grants read on `obj` directly or through a broader flag."""
    for perm in root.iter(NS + "objectPermissions"):
        if perm.findtext(NS + "object") != obj:
            continue
        return any(perm.findtext(NS + flag) == "true"
                   for flag in ("allowRead", "allowEdit", "viewAllRecords", "modifyAllRecords"))
    return False


def violations(path):
    """Messages for one permission set file; empty when it is fine."""
    root = ET.parse(path).getroot()
    if grants_read(root, "Account") and not grants_read(root, "Contact"):
        return [f"{path}: grants Account read without Contact read. Person accounts in TSO orgs "
                "make Account depend on Contact; add an objectPermissions block for Contact "
                "(allowRead true)."]
    return []


def tracked_permission_sets():
    out = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
                                   f"*{SUFFIX}"],
                                  cwd=REPO_ROOT, text=True)
    return [os.path.join(REPO_ROOT, p) for p in out.split("\0")
            if p and not p.startswith(SKIP_PREFIXES)]


def main(argv):
    paths = argv or tracked_permission_sets()
    problems = [m for p in paths for m in violations(p)]
    for message in problems:
        print(message)
    print(f"checked {len(paths)} permission sets, {len(problems)} violation(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
