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
on_all = lambda f: all(mod.flag_states(flags, f).values())
check("flag_states reads true and false flags", mod.flag_states(flags, "on,off") == {"on": True, "off": False})
check("flag_states reads a string override as a bool", mod.flag_states(flags, "s") == {"s": False})
check("flag_states takes a list too", mod.flag_states(flags, ["on", "on"]) == {"on": True})
check("flag_states fails on an undefined flag", "isn't a project custom flag" in (raises(lambda: mod.flag_states(flags, "on,nope")) or ""))
check("flag_states fails when no flag is given", raises(lambda: mod.flag_states(flags, None)) is not None
      and raises(lambda: mod.flag_states(flags, "")) is not None)
check("every flag must be on for the splice", on_all("on, on") and not on_all("on,off") and not on_all("off,on"))
check("a feature on without its prerequisite is reported", mod.missing_prerequisites({"q": True, "t": False}) == ["t"])
check("a feature left off is not reported", mod.missing_prerequisites({"q": False, "t": False}) == []
      and mod.missing_prerequisites({"q": False, "t": True}) == [])
check("should_deploy rejects an unknown deploy_when", raises(lambda: mod.should_deploy("sometimes", True)) is not None)
check("should_deploy rejects unquoted YAML off/on (booleans)", raises(lambda: mod.should_deploy(False, True)) is not None
      and raises(lambda: mod.should_deploy(True, True)) is not None)
check("flag_states rejects an empty name in the list", raises(lambda: mod.flag_states(flags, "on,")) is not None
      and raises(lambda: mod.flag_states(flags, ["on", ""])) is not None)
shared = []
added = mod.with_splice(shared, frag, True)
check("with_splice returns a new list and leaves the shared one empty", shared == [] and len(added) == 1 and added is not shared)
check("parse_fragments rejects an empty list", raises(lambda: mod.parse_fragments([])) is not None)
check("parse_fragments rejects a fragment without text",
      raises(lambda: mod.parse_fragments([{"path": "p", "marker": "m"}])) is not None)

print("_run_task")


class _Deployed(Exception):
    """Raised by the stand-in for Deploy._run_task: the task went on to deploy."""


def _stub_run_task(self):
    raise _Deployed()


_BASE = mod.DeployWithFragments.__mro__[1]
if _BASE is object:
    # No CumulusCI: give DeployWithFragments a parent with _run_task through a mixin.
    _Probe = type("_Probe", (mod.DeployWithFragments, type("_Stub", (), {"_run_task": _stub_run_task})), {})
    _saved = None
else:
    _Probe, _saved = mod.DeployWithFragments, _BASE.__dict__.get("_run_task")
    _BASE._run_task = _stub_run_task


class Log:
    def __init__(self):
        self.lines = []

    def info(self, m):
        self.lines.append(("info", m))

    def warning(self, m):
        self.lines.append(("warning", m))


def run(states, deploy_when, require_on=None, count=1, query_error=None):
    t = object.__new__(_Probe)
    t.flag_states, t.splice_on, t.deploy_when = states, all(states.values()), deploy_when
    t.options, t.logger = {"flag": ",".join(states), "require_on": require_on}, Log()
    t.fragments, t.base_transforms, t.transforms = frag, [], []
    queried = []

    def query(soql):
        queried.append(soql)
        if query_error:
            raise query_error
        return {"totalSize": count}
    t.org_config = SimpleNamespace(salesforce_client=SimpleNamespace(query=query))
    try:
        t._run_task()
        outcome = "skipped"
    except _Deployed:
        outcome = "deployed"
    except Exception as e:  # noqa: BLE001 - anything else is a real failure
        outcome = f"failed: {type(e).__name__}: {e}"
    applies = [x.apply for x in t.transforms if isinstance(x, mod.SpliceFragmentsTransform)]
    return outcome, t.logger.lines, queried, applies


try:
    both = {"quote_est_tax": True, "tax": True}
    out, log, q, ap = run(both, "off", "SELECT COUNT() FROM TaxPolicy")
    check("a deploy_when=off step skips with both flags on, without querying", out == "skipped" and not q, (out, q))
    out, log, q, ap = run(both, "on", "SELECT COUNT() FROM TaxPolicy", count=0)
    check("require_on finding nothing deploys unspliced, with a warning",
          out == "deployed" and ap == [False] and any(l[0] == "warning" and "nothing matches" in l[1] for l in log),
          (out, ap, log))
    out, log, q, ap = run(both, "on", "SELECT COUNT() FROM TaxPolicy", count=2)
    check("require_on finding a record deploys spliced", out == "deployed" and q and ap == [True], (out, q, ap))
    out, log, q, ap = run(both, "on", "bad", query_error=ValueError("INVALID_TYPE"))
    check("a failing require_on query fails the task", "require_on query failed" in out, out)
    out, log, q, ap = run({"quote_est_tax": False, "tax": True}, "off", "SELECT COUNT() FROM TaxPolicy")
    check("deploying off never queries, and a default build doesn't warn",
          out == "deployed" and not q and ap == [False] and not [l for l in log if l[0] == "warning"], (out, q, log))
    out, log, q, ap = run({"quote_est_tax": True, "tax": False}, "off")
    check("quote_est_tax on with tax off deploys off and warns about tax",
          out == "deployed" and ap == [False] and any(l[0] == "warning" and "tax is off" in l[1] for l in log), (out, log))
finally:
    if _BASE is not object:
        if _saved is None:
            del _BASE._run_task
        else:
            _BASE._run_task = _saved

print("quote_est_tax wiring")
cfg = yaml.safe_load((REPO / "cumulusci.yml").read_text())
tasks, flows = cfg["tasks"], cfg["flows"]
check("quote_est_tax defaults to false", cfg["project"]["custom"].get("quote_est_tax") is False)


def task_fragments(name):
    t = tasks[name]
    ok = t["class_path"] == "tasks.rlm_deploy_with_fragments.DeployWithFragments" and t["options"]["flag"] == "quote_est_tax,tax"
    check(f"{name} uses DeployWithFragments, on only with quote_est_tax and tax", ok, t)
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
check("turning it on requires an active tax policy",
      "FROM TaxPolicy" in tasks["deploy_quote_est_tax_settings"]["options"].get("require_on", "")
      and "'Active'" in tasks["deploy_quote_est_tax_settings"]["options"]["require_on"])
check("the partner grants require the field they name to exist",
      "FROM FieldDefinition" in tasks["deploy_post_prm"]["options"].get("require_on", "")
      and "'TotalPriceWithTax'" in tasks["deploy_post_prm"]["options"]["require_on"]
      and "Quote.TotalPriceWithTax" in tasks["deploy_post_prm"]["options"]["fragments"][0]["text"])
check("quote_est_tax is named first, so a missing tax is what gets reported",
      all(tasks[t]["options"]["flag"].split(",")[0] == "quote_est_tax" for t in ("deploy_post_prm", "deploy_quote_est_tax_settings")))
value = ET.fromstring(mod.splice(setting, smarker, stext, spath)).find(NS + "enableQuoteEstimatedTaxCPQ").text
check("the setting deploys on with the flag on", value == "true", value)
strays = [str(p.relative_to(REPO)) for root in ("unpackaged", "orgs", "force-app", "templates", "tasks/resources") for p in (REPO / root).rglob("*")
          if p.is_file() and p != setting_file and p.suffix in (".xml", ".json")
          and "enableQuoteEstimatedTaxCPQ" in p.read_text(errors="replace")]
check("nothing else sets enableQuoteEstimatedTaxCPQ (deploy_pre or ensure_pricing_schedules would undo the flag)", not strays, strays)

core = flows["prepare_core"]["steps"]
deploy_pre = next(n for n, s in core.items() if s.get("task") == "deploy_pre")
off = [n for n, s in core.items() if s.get("task") == "deploy_quote_est_tax_settings"]
check("prepare_core deploys the setting after deploy_pre with deploy_when off, no when: of its own",
      len(off) == 1 and off[0] > deploy_pre and core[off[0]].get("options", {}).get("deploy_when") == "off"
      and "when" not in core[off[0]], off and core[off[0]])
tax = flows["prepare_tax"]["steps"]
on = [n for n, s in tax.items() if s.get("task") == "deploy_quote_est_tax_settings"]
setup = [n for n, s in tax.items() if s.get("task") in ("create_tax_engine", "insert_tax_data", "insert_q3_tax_data",
                                                       "activate_tax_records")]
check("prepare_tax deploys it with deploy_when on, after the tax engine, data and activation",
      len(on) == 1 and on[0] > max(setup) and tax[on[0]].get("options", {}).get("deploy_when") == "on"
      and "when" not in tax[on[0]], on and tax[on[0]])
# Truth table: for every combination exactly one of the two steps deploys, and it deploys
# the value the flags call for.
for qet in (False, True):
    for tx in (False, True):
        cfg_flags = SimpleNamespace(lookup=lambda k, q=qet, t=tx: {"project__custom__quote_est_tax": q,
                                                                     "project__custom__tax": t}.get(k))
        both = all(mod.flag_states(cfg_flags, tasks["deploy_quote_est_tax_settings"]["options"]["flag"]).values())
        runs = [mod.should_deploy(core[off[0]]["options"]["deploy_when"], both),
                mod.should_deploy(tax[on[0]]["options"]["deploy_when"], both)]
        check(f"quote_est_tax={qet} tax={tx}: exactly one step deploys, setting {'on' if qet and tx else 'off'}",
              runs.count(True) == 1 and (runs[1] if (qet and tx) else runs[0]) and both == (qet and tx), runs)
rlm = flows["prepare_rlm_org"]["steps"]
order = [s.get("flow") for _, s in sorted(rlm.items())]
check("prepare_core, then prepare_tax, then prepare_prm",
      order.index("prepare_core") < order.index("prepare_tax") < order.index("prepare_prm"))
prm = [s for s in flows["prepare_prm"]["steps"].values() if s.get("task") == "deploy_post_prm"]
check("prepare_prm deploys post_prm in one step", len(prm) == 1, prm)

print()
if failures:
    print(f"{len(failures)} failed: {', '.join(failures)}")
    sys.exit(1)
print("All checks passed.")
