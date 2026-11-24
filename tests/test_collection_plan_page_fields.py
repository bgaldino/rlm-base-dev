"""Offline check: every CollectionPlan field the Collection Plan record page shows is readable.

The page template lists its fields as `Record.<Field>` items. Each one must be granted read in
RLM_CollectionsUI on its own (it ships with the collections flag, and RLM_BillingUI only with
billing_ui, so a grant there does not count), or sit on the allowlist below with its reason.
Stdlib only. Run with:
python tests/test_collection_plan_page_fields.py
"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAGE = os.path.join(ROOT, "templates", "flexipages", "standalone", "collections",
                    "RLM_Collection_Plan_Record_Page.flexipage-meta.xml")
OWNERS = [
    os.path.join(ROOT, "unpackaged", "post_collections", "permissionsets",
                 "RLM_CollectionsUI.permissionset-meta.xml"),
]

# Fields that need no grant, with the reason, checked against a 264 org's describe:
# the platform does not let a permission set grant them (permissionable=false).
ALLOWLIST = {
    "Name": "permissionable=false on CollectionPlan (always readable with the object)",
    "TotalInvoiceBalance": "permissionable=false on CollectionPlan",
}


def page_fields():
    with open(PAGE, encoding="utf-8") as fh:
        return set(re.findall(r"<fieldItem>Record\.(\w+)</fieldItem>", fh.read()))


def granted_fields():
    granted = set()
    for path in OWNERS:
        with open(path, encoding="utf-8") as fh:
            xml = fh.read()
        for block in re.findall(r"<fieldPermissions>.*?</fieldPermissions>", xml, re.S):
            field = re.search(r"<field>CollectionPlan\.(\w+)</field>", block)
            if field and "<readable>true</readable>" in block:
                granted.add(field.group(1))
    return granted


class CollectionPlanPageFields(unittest.TestCase):
    def test_page_declares_fields(self):
        self.assertGreater(len(page_fields()), 10, "the page parse found too few Record.* fields")

    def test_every_page_field_is_granted_or_allowlisted(self):
        missing = sorted(page_fields() - granted_fields() - set(ALLOWLIST))
        self.assertEqual(missing, [], f"page fields with no read grant and no allowlist entry: {missing}")

    def test_allowlist_entries_are_on_the_page(self):
        stale = sorted(set(ALLOWLIST) - page_fields())
        self.assertEqual(stale, [], f"allowlist entries the page no longer shows: {stale}")

    def test_allowlisted_fields_are_not_also_granted(self):
        both = sorted(set(ALLOWLIST) & granted_fields())
        self.assertEqual(both, [], f"granted fields on the allowlist (not permissionable): {both}")

    def test_billing_account_lookup_target_is_readable(self):
        # A field grant on the BillingAccountId lookup has no effect for a user who cannot read
        # BillingAccount, and no managed collections set grants it (measured on a 264 org).
        with open(OWNERS[0], encoding="utf-8") as fh:
            xml = fh.read()
        blocks = [b for b in re.findall(r"<objectPermissions>.*?</objectPermissions>", xml, re.S)
                  if "<object>BillingAccount</object>" in b]
        self.assertTrue(blocks and "<allowRead>true</allowRead>" in blocks[0],
                        "RLM_CollectionsUI must grant read on BillingAccount")


if __name__ == "__main__":
    unittest.main()
