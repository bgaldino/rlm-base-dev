#!/usr/bin/env python3
"""Offline tests for scripts/ai/check_sfdmu_layering.py (todo 325).

Each case builds a throwaway datasets/sfdmu tree and asserts what the two checks report.

- Lookups: a `$$` lookup matching the parent's externalId in the same pass passes, including
  against a Readonly parent declared in pass 2. A self-referential one, a mis-keyed one, one
  whose parent is only in another pass, and one with an excluded parent fail. An empty column
  is skipped. The allowlist suppresses a finding and is recorded as used only while it does.
- Shared records: two shapes with different final values conflict; the same values, a plan's
  own Draft-then-Active staging, and qb/ja against qb/en-US don't. A stale or missing
  allowlist entry fails the run.

Run: `python tests/test_check_sfdmu_layering.py` (offline, no org).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_sfdmu_layering",
                                              REPO / "scripts" / "ai" / "check_sfdmu_layering.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)


def tree(plans):
    """plans: {"qb/en-US/qb-x": (objects_by_pass, {"File.csv": "csv text"})} -> temp root."""
    td = tempfile.mkdtemp()
    root = pathlib.Path(td)
    for rel, (passes, files) in plans.items():
        plan = root / rel
        plan.mkdir(parents=True)
        (plan / "export.json").write_text(json.dumps(
            {"useSeparatedCSVFiles": True, "objectSets": [{"objects": p} for p in passes]}))
        for name, body in files.items():
            (plan / name).parent.mkdir(parents=True, exist_ok=True)
            (plan / name).write_text(body)
    return root


def decl(obj, key, op="Upsert", **extra):
    return {"query": f"SELECT Id FROM {obj}", "operation": op, "externalId": key, **extra}


SM = decl("ProductSellingModel", "Name;SellingModelType")
PBE = decl("PricebookEntry", "Product2.StockKeepingUnit")


def lookups(plans, reason=""):
    """Findings for the tree, kept only when they contain `reason`, so a case passes for the
    finding it targets rather than any finding."""
    return [f for f in L.lookup_findings(tree(plans), allowed=set())[0] if reason in f]


LOOKUP_CASES = [
    ("a `$$` lookup matching the parent's externalId passes", False, lookups({
        "qb/en-US/p": ([[SM, PBE]], {
            "ProductSellingModel.csv": "$$Name$SellingModelType,Name,SellingModelType\nA;T,A,T\n",
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})})),
    ("a self-referential `$$` lookup fails", True, lookups({
        "qb/en-US/p": ([[decl("ProductComponentGroup", "Code;ParentProduct.StockKeepingUnit")]], {
            "ProductComponentGroup.csv": "$$Code$ParentProduct.StockKeepingUnit,Code,"
                                         "ParentGroup.$$Code$ParentProduct.StockKeepingUnit\n"
                                         "C;P,C,B;P\n"})}, "self-referential")),
    ("a `$$` lookup whose parts don't match the parent's key fails", True, lookups({
        "qb/en-US/p": ([[decl("ProductSellingModel", "Name"), PBE]], {
            "ProductSellingModel.csv": "Name\nA\n",
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "don't match")),
    ("a `$$` lookup with no declared parent fails", True, lookups({
        "qb/en-US/p": ([[PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "declares no")),
    ("an empty `$$` lookup column is skipped", False, lookups({
        "qb/en-US/p": ([[PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,#N/A\nY,\n"})})),
    ("a Readonly declaration's CSV isn't checked", False, lookups({
        "qb/en-US/p": ([[decl("PricebookEntry", "Product2.StockKeepingUnit", op="Readonly")]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})})),
    # The parent is declared in pass 2 with a different key, so the only way to get the
    # don't-match finding is to have read pass 2's override CSV.
    ("a pass-2 override is read for pass 2", True, lookups({
        "qb/en-US/p": ([[PBE], [decl("ProductSellingModel", "Name", op="Readonly"), PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit\nX\n",
            "objectset_source/object-set-2/PricebookEntry.csv":
                "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\nX,A;T\n"})},
        "don't match ProductSellingModel's externalId in pass 2")),
    ("a parent declared only in another pass doesn't resolve the lookup", True, lookups({
        "qb/en-US/p": ([[SM], [PBE]], {
            "ProductSellingModel.csv": "$$Name$SellingModelType,Name,SellingModelType\nA;T,A,T\n",
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "pass 2 declares no ProductSellingModel")),
    ("an excluded parent doesn't resolve the lookup", True, lookups({
        "qb/en-US/p": ([[dict(SM, excluded=True), PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "declares no ProductSellingModel")),
]

_SELF_REF = {"qb/en-US/p": ([[decl("ProductComponentGroup", "Code;ParentProduct.StockKeepingUnit")]], {
    "ProductComponentGroup.csv": "$$Code$ParentProduct.StockKeepingUnit,Code,"
                                 "ParentGroup.$$Code$ParentProduct.StockKeepingUnit\nC;P,C,B;P\n"})}
_ENTRY = ("qb/en-US/p", "ProductComponentGroup.csv", "ParentGroup")


def allowlist_suppresses():
    findings, used = L.lookup_findings(tree(_SELF_REF), allowed={_ENTRY})
    return not findings and used == {_ENTRY}


def unused_allowlist_entry_is_unused():
    """An entry matching nothing comes back out of `used`, which is what main() reports stale."""
    bogus = ("qb/en-US/p", "Nope.csv", "Nope")
    _, used = L.lookup_findings(tree(_SELF_REF), allowed={_ENTRY, bogus})
    return bogus not in used


def fixed_allowlisted_lookup_is_stale():
    """An allowlisted column that now resolves isn't recorded as used, so main() reports it."""
    plans = {"qb/en-US/p": ([[PBE], [dict(SM, operation="Readonly"), PBE]], {
        "PricebookEntry.csv": "Product2.StockKeepingUnit\nX\n",
        "objectset_source/object-set-2/PricebookEntry.csv":
            "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\nX,A;T\n"})}
    entry = ("qb/en-US/p", "objectset_source/object-set-2/PricebookEntry.csv", "ProductSellingModel")
    findings, used = L.lookup_findings(tree(plans), allowed={entry})
    return not findings and entry not in used


LOOKUP_CASES += [
    ("a pass-2 lookup resolves against a Readonly parent declared in pass 2", False, lookups({
        "qb/en-US/p": ([[PBE], [dict(SM, operation="Readonly"), PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit\nX\n",
            "objectset_source/object-set-2/PricebookEntry.csv":
                "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\nX,A;T\n"})})),
    ("an allowlist entry whose lookup now resolves isn't recorded as used (so it goes stale)",
     True, fixed_allowlisted_lookup_is_stale()),
    ("an allowlisted lookup is suppressed and recorded as used", True, allowlist_suppresses()),
    ("an allowlist entry that matches nothing isn't recorded as used", True,
     unused_allowlist_entry_is_unused()),
]

UOM = decl("UnitOfMeasure", "UnitCode")


def conflicts(plans, field=None):
    """Conflicts for the tree, kept only on `field` when given."""
    return {k: v for k, v in L.shared_conflicts(tree(plans)).items() if field in (None, k[1])}


SHARED_CASES = [
    ("two shapes writing the same key with different values conflict", True, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,0.001\n"})},
        "ConversionFactor")),
    ("the same values in two shapes don't conflict", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"})})),
    ("#N/A and blank are both null, so they don't conflict", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Description\nGB,\n"}),
        "mfg/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Description\nGB,#N/A\n"})})),
    ("qb/ja counts as qb, so it doesn't conflict with qb/en-US", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,Gigabyte\n"}),
        "qb/ja/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,ギガバイト\n"})})),
    ("one shape's own plans differing isn't cross-shape", False, conflicts({
        "q3/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,2\n"})})),
    ("an excluded declaration isn't a write", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[dict(UOM, excluded=True)]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,0.001\n"})})),
    ("a composite key is read from its `$$` column", True, conflicts({
        "qb/en-US/a": ([[SM]], {"ProductSellingModel.csv":
                                "$$Name$SellingModelType,Name,SellingModelType,PricingTerm\nA;T,A,T,1\n"}),
        "mfg/en-US/b": ([[SM]], {"ProductSellingModel.csv":
                                 "$$Name$SellingModelType,Name,SellingModelType,PricingTerm\nA;T,A,T,12\n"})},
        "PricingTerm")),
    # Both shapes load Draft in pass 1 and Active in pass 2; each plan's final value is Active.
    ("a plan's own pass-to-pass staging isn't a cross-shape conflict", False, conflicts({
        "qb/en-US/a": ([[UOM], [decl("UnitOfMeasure", "UnitCode", op="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Status\nGB,Draft\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Status\nGB,Active\n"}),
        "q3/en-US/b": ([[UOM], [decl("UnitOfMeasure", "UnitCode", op="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Status\nGB,Draft\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Status\nGB,Active\n"})},
        "Status")),
    ("a final value that differs after staging is a conflict", True, conflicts({
        "qb/en-US/a": ([[UOM], [decl("UnitOfMeasure", "UnitCode", op="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Status\nGB,Draft\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Status\nGB,Active\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Status\nGB,Draft\n"})},
        "Status")),
]


def stale_shared_entry_fails():
    """A KNOWN_SHARED_CONFLICTS entry that no longer conflicts fails the live run."""
    import contextlib
    import io
    saved = L.KNOWN_SHARED_CONFLICTS
    L.KNOWN_SHARED_CONFLICTS = saved | {("Nope__c", "Nope")}
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        return code == 1 and "Nope__c.Nope is in KNOWN_SHARED_CONFLICTS" in out.getvalue()
    finally:
        L.KNOWN_SHARED_CONFLICTS = saved


def unknown_shared_conflict_fails():
    """Dropping a known conflict from the allowlist makes the live run fail on it."""
    import contextlib
    import io
    saved = L.KNOWN_SHARED_CONFLICTS
    L.KNOWN_SHARED_CONFLICTS = saved - {("UnitOfMeasure", "ConversionFactor")}
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        return code == 1 and "UnitOfMeasure.ConversionFactor differs" in out.getvalue()
    finally:
        L.KNOWN_SHARED_CONFLICTS = saved


SHARED_CASES += [
    ("a stale shared-conflict entry fails the run", True, stale_shared_entry_fails()),
    ("a shared conflict missing from the allowlist fails the run", True, unknown_shared_conflict_fails()),
]


def live_tree_passes():
    """The shipped tree is clean: no unresolved lookup, and every shared conflict is known."""
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return L.main([]) == 0


CASES = LOOKUP_CASES + SHARED_CASES + [("the live tree passes", True, live_tree_passes())]


def main() -> int:
    failures = [label for label, expect, found in CASES if bool(found) != expect]
    for label, expect, found in CASES:
        print(f"  [{'FAIL' if label in failures else 'PASS'}] {label}")
        if label in failures:
            print(f"         expected a finding={expect}, got={found or 'none'}")
    print(f"{len(CASES) - len(failures)}/{len(CASES)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
