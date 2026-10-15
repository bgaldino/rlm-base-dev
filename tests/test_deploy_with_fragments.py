#!/usr/bin/env python3
"""
Offline checks for tasks/rlm_deploy_with_fragments.py and the quote_est_tax wiring.

    python tests/test_deploy_with_fragments.py

No org required, and no CumulusCI install: the module degrades on ImportError.

Why this exists: estimated tax on quotes (IncludeEstTaxInQuoteCPQ) is off by default,
and with it off the Quote and QuoteLineItem tax fields don't exist, so the partner
permission set can't grant them unconditionally (a fresh build failed deploy_post_prm on
Quote.TotalPriceWithTax). quote_est_tax=true turns the setting on and splices the grants
back in. These checks pin that both sides of the flag stay deployable, and that nothing
redeploys the setting off behind the flag's back.
"""
import importlib.util
import io
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml

_spec = importlib.util.spec_from_file_location(
    "_rlm_test_deploy_with_fragments", REPO / "tasks" / "rlm_deploy_with_fragments.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

PERMSET = REPO / "unpackaged/post_prm/force-app/main/default/permissionsets/RLM_Partner_Community_User_Perm_Set.permissionset-meta.xml"
TAX_FIELDS = {
    "Quote.TotalPriceWithTax", "Quote.TotalTaxAmount",
    "QuoteLineItem.TaxTreatmentId", "QuoteLineItem.TotalPriceWithTax", "QuoteLineItem.TotalTaxAmount",
}
NS = "{http://soap.sforce.com/2006/04/metadata}"
CTX = SimpleNamespace(logger=SimpleNamespace(info=lambda *_: None))

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}{'' if condition else ' — ' + str(detail)}")
    if not condition:
        failures.append(label)


def raises(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 - the module's stand-ins are RuntimeError/ValueError
        return str(e)
    return None


def package(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(buf)


def granted(xml_text):
    root = ET.fromstring(xml_text)
    return [fp.find(NS + "field").text for fp in root.findall(NS + "fieldPermissions")]


print("splice")
check("replaces a single marker", mod.splice("a<!-- M -->b", "<!-- M -->", "X", "f") == "aXb")
check("indents later fragment lines to the marker's column",
      mod.splice("<r>\n    <!-- M -->\n</r>", "<!-- M -->", "<a/>\n<b/>", "f") == "<r>\n    <a/>\n    <b/>\n</r>")
check("fails when the marker is missing", "found it 0 times" in (raises(lambda: mod.splice("ab", "<!-- M -->", "X", "f")) or ""))
check("fails when the marker is repeated",
      "found it 2 times" in (raises(lambda: mod.splice("<!-- M --><!-- M -->", "<!-- M -->", "X", "f")) or ""))

print("transform")
files = {"permissionsets/P.permissionset": "<a><!-- M --></a>", "package.xml": "<Package><!-- M --></Package>"}
frag = [("permissionsets/P.permissionset", "<!-- M -->", "<b/>")]
out = mod.SpliceFragmentsTransform(frag).process(package(files), CTX)
check("splices the named file", out.read("permissionsets/P.permissionset").decode() == "<a><b/></a>")
check("leaves other files alone", out.read("package.xml").decode() == "<Package><!-- M --></Package>")
off = mod.SpliceFragmentsTransform(frag, apply=False).process(package(files), CTX)
check("with the flag off the file is unchanged", off.read("permissionsets/P.permissionset").decode() == "<a><!-- M --></a>")
check("with the flag off a lost marker still fails",
      "found it 0 times" in (raises(lambda: mod.SpliceFragmentsTransform(frag, apply=False).process(
          package({"permissionsets/P.permissionset": "<a/>"}), CTX)) or ""))
bad = [("permissionsets/P.permissionset", "<!-- M -->", "<b>")]
check("a fragment that breaks the XML fails before deploy",
      "not well-formed" in (raises(lambda: mod.SpliceFragmentsTransform(bad).process(package(files), CTX)) or ""))
missing = [("permissionsets/Q.permissionset", "<!-- M -->", "<b/>")]
check("fails when the named file isn't in the package",
      "not in the deploy package" in (raises(lambda: mod.SpliceFragmentsTransform(missing).process(package(files), CTX)) or ""))

print("task options")
flags = SimpleNamespace(lookup=lambda key: {"project__custom__on": True, "project__custom__off": False,
                                            "project__custom__s": "false"}.get(key))
check("flag_value reads a true flag", mod.flag_value(flags, "on") is True)
check("flag_value reads a false flag", mod.flag_value(flags, "off") is False)
check("flag_value reads a string override as a bool", mod.flag_value(flags, "s") is False)
check("flag_value fails on an undefined flag", "isn't a project custom flag" in (raises(lambda: mod.flag_value(flags, "nope")) or ""))
check("flag_value fails when no flag is given", raises(lambda: mod.flag_value(flags, None)) is not None)
shared = []
added = mod.with_splice(shared, frag, True)
check("with_splice returns a new list and leaves the shared one empty", shared == [] and len(added) == 1 and added is not shared)
check("parse_fragments rejects an empty list", raises(lambda: mod.parse_fragments([])) is not None)
check("parse_fragments rejects a fragment without text",
      raises(lambda: mod.parse_fragments([{"path": "p", "marker": "m"}])) is not None)

print("quote_est_tax wiring")
cfg = yaml.safe_load((REPO / "cumulusci.yml").read_text())
tasks, flows = cfg["tasks"], cfg["flows"]
check("quote_est_tax defaults to false", cfg["project"]["custom"].get("quote_est_tax") is False)


def task_fragments(name):
    t = tasks[name]
    ok = t["class_path"] == "tasks.rlm_deploy_with_fragments.DeployWithFragments" and t["options"]["flag"] == "quote_est_tax"
    check(f"{name} uses DeployWithFragments on quote_est_tax", ok, t)
    return mod.parse_fragments(t["options"]["fragments"])


((ppath, pmarker, ptext),) = task_fragments("deploy_post_prm")
check("permission set fragment names the converted file",
      ppath == "permissionsets/" + PERMSET.name.replace("-meta.xml", ""), ppath)
source = PERMSET.read_text()
mod.check_marker(source, pmarker, PERMSET.name)
plain = granted(source)
check("with the flag off the permission set grants none of the tax fields", not TAX_FIELDS & set(plain), TAX_FIELDS & set(plain))
spliced = mod.splice(source, pmarker, ptext, PERMSET.name)
on = granted(spliced)  # also proves the spliced file is well-formed XML
check("with the flag on it grants each tax field once",
      all(on.count(f) == 1 for f in TAX_FIELDS) and set(on) - set(plain) == TAX_FIELDS, set(on) - set(plain))
added = [fp for fp in ET.fromstring(spliced).findall(NS + "fieldPermissions") if fp.find(NS + "field").text in TAX_FIELDS]
check("tax grants are read-only", all(fp.find(NS + "editable").text == "false" and fp.find(NS + "readable").text == "true"
                                      for fp in added))

((spath, smarker, stext),) = task_fragments("deploy_quote_est_tax_settings")
setting_file = REPO / tasks["deploy_quote_est_tax_settings"]["options"]["path"] / (spath + "-meta.xml")
setting = setting_file.read_text()
mod.check_marker(setting, smarker, spath)
value = ET.fromstring(setting).find(NS + "enableQuoteEstimatedTaxCPQ").text
check("the setting deploys off with the flag off", value == "false", value)
value = ET.fromstring(mod.splice(setting, smarker, stext, spath)).find(NS + "enableQuoteEstimatedTaxCPQ").text
check("the setting deploys on with the flag on", value == "true", value)
strays = [str(p.relative_to(REPO)) for root in ("unpackaged", "orgs", "force-app", "templates", "tasks/resources") for p in (REPO / root).rglob("*")
          if p.is_file() and p != setting_file and p.suffix in (".xml", ".json")
          and "enableQuoteEstimatedTaxCPQ" in p.read_text(errors="replace")]
check("nothing else sets enableQuoteEstimatedTaxCPQ (deploy_pre or ensure_pricing_schedules would undo the flag)", not strays, strays)

core = flows["prepare_core"]["steps"]
deploy_pre = next(n for n, s in core.items() if s.get("task") == "deploy_pre")
settings = [n for n, s in core.items() if s.get("task") == "deploy_quote_est_tax_settings"]
check("the settings task runs on every build, in prepare_core after deploy_pre",
      len(settings) == 1 and settings[0] > deploy_pre and "when" not in core[settings[0]], settings)
rlm = flows["prepare_rlm_org"]["steps"]
order = [s.get("flow") for _, s in sorted(rlm.items())]
check("prepare_core runs before prepare_prm", order.index("prepare_core") < order.index("prepare_prm"))
prm = [s for s in flows["prepare_prm"]["steps"].values() if s.get("task") == "deploy_post_prm"]
check("prepare_prm deploys post_prm in one step", len(prm) == 1, prm)

print()
if failures:
    print(f"{len(failures)} failed: {', '.join(failures)}")
    sys.exit(1)
print("All checks passed.")
