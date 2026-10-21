"""Offline fixtures for scripts/ai/check_permission_set_dependencies.py.

Stdlib only. Run with: python tests/test_check_permission_set_dependencies.py
"""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "ai"))
import check_permission_set_dependencies as cpd  # noqa: E402


def perm(obj, **flags):
    body = "".join(f"<{k}>{str(v).lower()}</{k}>" for k, v in flags.items())
    return f"<objectPermissions>{body}<object>{obj}</object></objectPermissions>"


def check(*blocks):
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">'
           + "".join(blocks) + "</PermissionSet>")
    with tempfile.NamedTemporaryFile("w", suffix=cpd.SUFFIX, delete=False) as fh:
        fh.write(xml)
    try:
        return cpd.violations(fh.name)
    finally:
        os.unlink(fh.name)


class PermissionSetDependencies(unittest.TestCase):
    def test_account_read_without_contact_fails(self):
        self.assertEqual(len(check(perm("Account", allowRead=True))), 1)

    def test_account_read_with_contact_read_passes(self):
        self.assertEqual(check(perm("Account", allowRead=True), perm("Contact", allowRead=True)), [])

    def test_contact_present_but_not_readable_fails(self):
        self.assertEqual(len(check(perm("Account", allowRead=True),
                                   perm("Contact", allowRead=False))), 1)

    def test_account_edit_implies_read(self):
        self.assertEqual(len(check(perm("Account", allowRead=False, allowEdit=True))), 1)

    def test_contact_view_all_satisfies(self):
        self.assertEqual(check(perm("Account", allowRead=True),
                               perm("Contact", allowRead=False, viewAllRecords=True)), [])

    def test_no_account_passes(self):
        self.assertEqual(check(perm("Opportunity", allowRead=True)), [])

    def test_deleted_and_untracked_files_are_handled(self):
        ps = "p.permissionset-meta.xml"
        with tempfile.TemporaryDirectory() as d:
            for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                        ["config", "user.name", "t"]):
                subprocess.run(["git", *cmd], cwd=d, check=True)
            for name in ("gone", "kept"):
                with open(os.path.join(d, name + "." + ps), "w") as fh:
                    fh.write("<PermissionSet/>")
            subprocess.run(["git", "add", "."], cwd=d, check=True)
            subprocess.run(["git", "commit", "-qm", "x"], cwd=d, check=True)
            os.remove(os.path.join(d, "gone." + ps))
            with open(os.path.join(d, "new." + ps), "w") as fh:
                fh.write("<PermissionSet/>")
            saved, cpd.REPO_ROOT = cpd.REPO_ROOT, d
            try:
                names = sorted(os.path.basename(p) for p in cpd.tracked_permission_sets())
                self.assertEqual(cpd.main([]), 0)
            finally:
                cpd.REPO_ROOT = saved
        self.assertEqual(names, ["kept." + ps, "new." + ps])

    def test_repo_is_clean(self):
        self.assertEqual(cpd.main([]), 0)


if __name__ == "__main__":
    unittest.main()
