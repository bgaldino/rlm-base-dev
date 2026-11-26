"""The Collections Dashboard ships whole for a collections user (todo 435).

RLM_CollectionsDashboard must grant every Apex class the dashboard component calls, its tab, and
read-only access to exactly the records the controller reads that the managed Billing Collections
and Recovery Specialist set lacks (measured on 264; the Apex tests prove them as that user). The tab
must name the page, and the page the component. The page,
tab and permission set ship together in unpackaged/post_billing_ui (billing_ui), so none of
them may reference metadata from a bundle that can be off while billing_ui is on.

Stdlib only; the gate runs it as `python tests/test_collections_dashboard_access.py`.
"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = REPO_ROOT / "unpackaged" / "post_billing_ui"
NS = {"sf": "http://soap.sforce.com/2006/04/metadata"}
COMPONENT = BUNDLE / "lwc" / "rlmCollectionsDashboard"
PERMSET = BUNDLE / "permissionsets" / "RLM_CollectionsDashboard.permissionset-meta.xml"
TAB = BUNDLE / "tabs" / "RLM_Collections_Dashboard.tab-meta.xml"
PAGE = BUNDLE / "flexipages" / "RLM_Collections_Dashboard.flexipage-meta.xml"
APP_PATCH = REPO_ROOT / "templates/applications/patches/billing_ui/standard__CollectionConsole.patch.xml"


def _apex_classes_called():
    classes = set()
    for js in COMPONENT.glob("*.js"):
        classes |= set(re.findall(r"@salesforce/apex/(\w+)\.\w+", js.read_text(encoding="utf-8")))
    return classes


class CollectionsDashboardAccessTest(unittest.TestCase):
    def test_permission_set_grants_exactly_the_classes_the_component_calls_and_its_tab(self):
        root = ET.parse(PERMSET).getroot()
        granted = {e.findtext("sf:apexClass", namespaces=NS) for e in root.findall("sf:classAccesses", NS)}
        self.assertEqual(_apex_classes_called(), {"RLM_CollectionsDashboardController"})
        self.assertEqual(granted, _apex_classes_called())
        tabs = {(e.findtext("sf:tab", namespaces=NS), e.findtext("sf:visibility", namespaces=NS))
                for e in root.findall("sf:tabSettings", NS)}
        self.assertEqual(tabs, {("RLM_Collections_Dashboard", "Visible")})
        # Least privilege: read-only, only the specialist set's gaps, no user or app grants.
        objects = {}
        for e in root.findall("sf:objectPermissions", NS):
            flags = {k: e.findtext(f"sf:{k}", namespaces=NS) for k in (
                "allowRead", "allowCreate", "allowEdit", "allowDelete", "viewAllRecords", "modifyAllRecords")}
            objects[e.findtext("sf:object", namespaces=NS)] = flags
        self.assertEqual(set(objects), {"Case", "Payment"})
        for name, flags in objects.items():
            self.assertEqual(flags, {"allowRead": "true", "allowCreate": "false", "allowEdit": "false",
                                     "allowDelete": "false", "viewAllRecords": "false",
                                     "modifyAllRecords": "false"}, name)
        fields = {e.findtext("sf:field", namespaces=NS): (e.findtext("sf:readable", namespaces=NS),
                                                         e.findtext("sf:editable", namespaces=NS))
                  for e in root.findall("sf:fieldPermissions", NS)}
        self.assertEqual(set(fields), {
            "Case.AccountId", "Case.Description", "Case.Reason", "Case.Subject",
            "CollectionPlanItem.InvoiceId", "Event.WhatId", "Task.ActivityDate", "Task.WhatId"})
        self.assertEqual(set(fields.values()), {("true", "false")})
        for tag in ("userPermissions", "applicationVisibilities"):
            self.assertEqual(root.findall(f"sf:{tag}", NS), [], tag)

    def test_tab_page_and_component_reference_each_other_inside_the_bundle(self):
        self.assertEqual(ET.parse(TAB).getroot().findtext("sf:flexiPage", namespaces=NS), PAGE.name.split(".")[0])
        components = {e.text for e in ET.parse(PAGE).getroot().iter("{%s}componentName" % NS["sf"])}
        self.assertEqual(components, {COMPONENT.name})
        for cls in _apex_classes_called():
            self.assertTrue((BUNDLE / "classes" / f"{cls}.cls").exists(), cls)

    def test_collections_console_patch_names_the_shipped_tab(self):
        text = APP_PATCH.read_text(encoding="utf-8")
        self.assertIn("<tabs>RLM_Collections_Dashboard</tabs>", text)
        self.assertIn("<tab>RLM_Collections_Dashboard</tab>", text)


if __name__ == "__main__":
    unittest.main()
