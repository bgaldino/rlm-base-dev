#!/usr/bin/env python3
"""Offline tests for scripts/check_classification_attrs.py.

- norm: blank equals null; Is* fields compare as true/false and numeric fields numerically; text
  fields compare exactly after strip(); nan/inf stay text.
- compare: a differing KEY field, a missing row and an org-only row are each reported; equal rows
  report nothing.
- index_org: a key held by two org rows is reported, not overwritten.
- build_query: scoped to the CSV's classification codes, with quotes escaped.
- main exit codes: 0 clean, 1 a missing row or a difference in a key field (AttributeNameOverride, IsRequired, DefaultValue, Description, HelpText),
  0 for a difference in any other field (printed as INFO), 2 duplicate CSV key, missing CSV, missing
  `sf`, a query error, non-JSON output, or an ambiguous org key. The real read_org runs against a
  patched subprocess.run.

Run: `python tests/test_check_classification_attrs.py` (offline, no org).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cca", REPO / "scripts" / "check_classification_attrs.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

_failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        _failures.append(label)
        print(f"       got:  {got!r}\n       want: {want!r}")


check("norm None is blank", M.norm(None), "")
check("norm bool", M.norm(True), "true")
check("norm Is* 'False'", M.norm("False", "IsHidden"), "false")
check("norm 5 equals 5.0", M.norm("5.0", "Sequence"), M.norm(5, "Sequence"))
check("norm nan stays text", M.norm("nan", "Sequence"), "nan")
check("norm inf stays text", M.norm("Infinity", "MaximumCharacterCount"), "Infinity")

HEADER = ("ProductClassification.Code,AttributeDefinition.Code,AttributeCategory.Code,"
          "AttributeNameOverride,IsRequired,UnitOfMeasure.UnitCode\n")


def org_rec(cls, attr, cat, override, req):
    rec = {f: None for f in M.FIELDS}
    rec.update({"AttributeNameOverride": override, "IsRequired": req,
                "ProductClassification": {"Code": cls}, "AttributeDefinition": {"Code": attr},
                "AttributeCategory": {"Code": cat} if cat else None, "UnitOfMeasure": None})
    return rec


def plan_dir(rows: str) -> str:
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "ProductClassificationAttr.csv").write_text(HEADER + rows)
    return str(d)


class Result:
    def __init__(self, stdout="", stderr=""):
        self.stdout, self.stderr = stdout, stderr


def run_out(plan, records=None, sf=None):
    """Run main() with the real read_org; subprocess.run is faked. `sf` is an exception to raise
    or a Result to return; by default sf returns `records` as a successful query. Returns the exit
    code and the captured stdout."""
    saved = M.subprocess.run

    def fake(*_a, **_k):
        if isinstance(sf, Exception):
            raise sf
        if sf is not None:
            return sf
        return Result(json.dumps({"status": 0, "result": {"records": records}}))

    M.subprocess.run = fake
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = M.main(["--target-org", "x", "--plan", plan])
    finally:
        M.subprocess.run = saved
    return code, out.getvalue()


def run(plan, records=None, sf=None):
    return run_out(plan, records, sf)[0]


bom_dir = pathlib.Path(tempfile.mkdtemp())
(bom_dir / "ProductClassificationAttr.csv").write_bytes(b"\xef\xbb\xbf" + (HEADER + "PC-A,ATTR-1,AC-1,Type,false,\n").encode())
bom = str(bom_dir)
good = plan_dir("PC-A,ATTR-1,AC-1,Type,false,\nPC-B,ATTR-2,,Name,true,\n")
recs = [org_rec("PC-A", "ATTR-1", "AC-1", "Type", False), org_rec("PC-B", "ATTR-2", "", "Name", True)]
check("clean exits 0", run(good, recs), 0)
check("BOM-prefixed CSV reads", M.read_csv(pathlib.Path(bom))[("PC-A", "ATTR-1", "AC-1")]["IsRequired"], "false")
check("numeric fields compare numerically",
      (M.norm("007", "Sequence"), M.norm("1e3", "MinimumCharacterCount"), M.norm(1.0, "Sequence")),
      ("7", "1000", "1"))
check("string-typed value fields compare exactly",
      (M.norm("1.0", "StepValue"), M.norm("007", "MinimumValue"), M.norm("1e3", "MaximumValue")),
      ("1.0", "007", "1e3"))
check("text fields compare exactly", (M.norm("1.0", "DefaultValue"), M.norm("1", "DefaultValue"),
                                      M.norm(" a ", "DefaultValue")), ("1.0", "1", "a"))
text_exp = {("PC-A", "ATTR-1", ""): {"DefaultValue": "1"}}
text_org = org_rec("PC-A", "ATTR-1", "", "", None)
text_org["DefaultValue"] = "1.0"
text_diffs, _m, _e = M.compare(text_exp, M.index_org([text_org])[0])
check("text '1.0' vs '1' is reported", [(d["field"], d["csv"], d["org"]) for d in text_diffs],
      [("DefaultValue", "1", "1.0")])
text_org["DefaultValue"] = "1"
text_org["Sequence"] = 1.0
text_exp[("PC-A", "ATTR-1", "")]["Sequence"] = "1"
check("numeric 1.0 vs '1' is equal", M.compare(text_exp, M.index_org([text_org])[0])[0], [])
check("differing IsRequired exits 1", run(good, [recs[0], org_rec("PC-B", "ATTR-2", "", "Name", False)]), 1)
ov_code, ov_out = run_out(good, [org_rec("PC-A", "ATTR-1", "AC-1", "Other", False), recs[1]])
check("differing AttributeNameOverride exits 1", ov_code, 1)
check("and prints it as a key difference",
      any(line.startswith("DIFF KEY") and "AttributeNameOverride" in line
          for line in ov_out.splitlines()), True)
check("missing row exits 1", run(good, [recs[0]]), 1)

expected = M.read_csv(pathlib.Path(good))
diffs, missing, extra = M.compare(expected, M.index_org(recs + [org_rec("PC-C", "X", "", "n", False)])[0])
check("org-only row is Info, no diff", (diffs, missing, extra), ([], [], [("PC-C", "X", "")]))
diffs, _m, _e = M.compare(expected, M.index_org([org_rec("PC-A", "ATTR-1", "AC-1", "Other", False), recs[1]])[0])
check("names the differing field", [d["field"] for d in diffs], ["AttributeNameOverride"])

_rows, dupes = M.index_org(recs + [org_rec("PC-A", "ATTR-1", "AC-1", "Type", False)])
check("duplicate org key reported", dupes, {("PC-A", "ATTR-1", "AC-1"): 2})
check("ambiguous org key exits 2", run(good, recs + [org_rec("PC-A", "ATTR-1", "AC-1", "Type", False)]), 2)
check("duplicate CSV key exits 2", run(plan_dir("PC-A,ATTR-1,AC-1,T,false,\nPC-A,ATTR-1,AC-1,T,false,\n"), recs), 2)
check("missing CSV exits 2", run(tempfile.mkdtemp(), recs), 2)
check("missing sf exits 2", run(good, sf=FileNotFoundError("sf")), 2)
check("sf error status exits 2", run(good, sf=Result(json.dumps({"status": 1, "message": "x"}))), 2)
check("non-JSON output exits 2", run(good, sf=Result("not json", "boom")), 2)

other = org_rec("PC-A", "ATTR-1", "AC-1", "Type", False)
other["DisplayType"] = "Text"  # the CSV leaves it blank; the platform may fill it
info_code, info_out = run_out(good, [other, recs[1]])
check("a difference in a non-key field exits 0", info_code, 0)
check("and prints an INFO DisplayType line",
      any(line.startswith("INFO") and "DisplayType" in line for line in info_out.splitlines()), True)
check("with no key difference", "DIFF KEY" in info_out, False)
d_other, _m, _e = M.compare(expected, M.index_org([other, recs[1]])[0])
check("and it is still reported", [d["field"] for d in d_other], ["DisplayType"])

q = M.build_query(["PC-A", "O'Brien", ""])
check("query scoped to the CSV's codes", "WHERE ProductClassification.Code IN ('O\\'Brien', 'PC-A')" in q, True)
check("default plan is anchored to the repo", M.DEFAULT_PLAN.is_dir(), True)

dv_exp = {("PC-A", "ATTR-1", ""): {"DefaultValue": "x"}}
dv_org = org_rec("PC-A", "ATTR-1", "", "", None)
dv_org["DefaultValue"] = "y"
check("DefaultValue difference is a key difference",
      [d["field"] for d in M.compare(dv_exp, M.index_org([dv_org])[0])[0] if d["field"] in M.KEY_FIELDS],
      ["DefaultValue"])
check("payload without result exits 2",
      run(good, sf=Result(json.dumps({"status": 0}))), 2)
check("blank Is* equals false", (M.norm("", "IsRequired"), M.norm(None, "IsRequired"), M.norm(False, "IsRequired")),
      ("false", "false", "false"))
check("list payload exits 2", run(good, sf=Result(json.dumps([1]))), 2)
_saved = M.subprocess.run
M.subprocess.run = lambda *_a, **_k: Result(json.dumps({"status": 0, "result": {"records": recs}}))
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    json_code = M.main(["--target-org", "x", "--plan", good, "--json", "/nonexistent-dir/x.json"])
M.subprocess.run = _saved
check("unwritable --json exits 2", json_code, 2)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
