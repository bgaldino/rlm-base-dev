"""The Collections Dashboard ships whole for a collections user (todo 435).

RLM_CollectionsDashboard must grant every Apex class the dashboard component calls and its
tab, and nothing else; the tab must name the page, and the page the component. The page,
tab and permission set ship together in unpackaged/post_billing_ui (billing_ui), so none of
them may reference metadata from a bundle that can be off while billing_ui is on.
"""
import re
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


def test_permission_set_grants_exactly_the_classes_the_component_calls_and_its_tab():
    root = ET.parse(PERMSET).getroot()
    granted = {e.findtext("sf:apexClass", namespaces=NS) for e in root.findall("sf:classAccesses", NS)}
    assert _apex_classes_called() == {"RLM_CollectionsDashboardController"}
    assert granted == _apex_classes_called()
    tabs = {(e.findtext("sf:tab", namespaces=NS), e.findtext("sf:visibility", namespaces=NS))
            for e in root.findall("sf:tabSettings", NS)}
    assert tabs == {("RLM_Collections_Dashboard", "Visible")}
    # Least privilege: no object, field, user or app grants; those come from the collections sets.
    for tag in ("objectPermissions", "fieldPermissions", "userPermissions", "applicationVisibilities"):
        assert root.findall(f"sf:{tag}", NS) == [], tag


def test_tab_page_and_component_reference_each_other_inside_the_bundle():
    assert ET.parse(TAB).getroot().findtext("sf:flexiPage", namespaces=NS) == PAGE.name.split(".")[0]
    components = {e.text for e in ET.parse(PAGE).getroot().iter("{%s}componentName" % NS["sf"])}
    assert components == {COMPONENT.name}
    for cls in _apex_classes_called():
        assert (BUNDLE / "classes" / f"{cls}.cls").exists()


def test_collections_console_patch_names_the_shipped_tab():
    text = APP_PATCH.read_text(encoding="utf-8")
    assert "<tabs>RLM_Collections_Dashboard</tabs>" in text
    assert "<tab>RLM_Collections_Dashboard</tab>" in text
