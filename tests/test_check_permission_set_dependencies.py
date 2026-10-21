"""Offline fixtures for scripts/ai/check_permission_set_dependencies.py.

Stdlib only. Run with: python tests/test_check_permission_set_dependencies.py
"""
import os
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

    def test_repo_is_clean(self):
        self.assertEqual(cpd.main([]), 0)


if __name__ == "__main__":
    unittest.main()
