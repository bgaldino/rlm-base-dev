#!/usr/bin/env python3
"""Offline tests for scripts/ai/check_sfdmu_layering.py (todo 325).

Each case builds a throwaway datasets/sfdmu tree and asserts what the two checks report.

- Lookups: a `$$` lookup matching the parent's externalId in the same pass passes, including
  against a Readonly parent declared in pass 2. A self-referential one, a mis-keyed one, one
  whose parent is only in another pass, and one with an excluded parent fail. An empty column
  is skipped. The allowlist suppresses a finding and is recorded as used only while it does.
- Shared records: two shapes with different final values conflict, matched on the loading
  plan's key, `$$` lookups and key parts held only in the `$$` column included. The same
  values, a plan's own Draft-then-Active staging, qb/ja against qb/en-US, records an extra key
  field keeps apart, and Updates to a record nobody creates don't. A narrower key's load
  overwriting a wider key's extra field does, and so do Updates to a record another plan
  creates and a lookup set through different parent keys. A stale or missing allowlist entry
  fails the run, per record.
- Intra-shape (todo 337): two plans of one shape writing different values to one field of one
  record conflict, labelled by plan (the todo 336 DisplayUrl replay). The same values, one plan's
  staging, plans of different shapes, and qb/ja against qb/en-US don't; two qb/ja plans are
  compared. A pair sees records only from plans that load into its org (qb/ja pairs see
  qb/en-US's; two top-level plans see every shape's). A new conflict and a stale allowlist
  entry each fail the run.
- Top-level plans (scratch_data and the other plans every build loads) count as the shape
  `common`, so they're compared against every shape.
- sourceRecordsFilter: `LIKE` (case-insensitive, whole value), `=` and `<>` are applied in both
  checks; any other form, or a column the CSV lacks, is reported.

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
    # `SELECT all` so every CSV column counts as written; written-column cases set `query`.
    return {"query": f"SELECT all FROM {obj}", "operation": op, "externalId": key, **extra}


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
    ("a `$$` lookup the query doesn't select isn't checked", False, lookups({
        "qb/en-US/p": ([[dict(PBE, query="SELECT Product2.StockKeepingUnit FROM PricebookEntry")]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})})),
    ("a `$$` lookup in excludedFields isn't checked", False, lookups({
        "qb/en-US/p": ([[dict(PBE, excludedFields=["ProductSellingModelId"])]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})})),
    ("a `$$` lookup the query selects through its Id is checked", True, lookups({
        "qb/en-US/p": ([[dict(PBE, query="SELECT Product2.StockKeepingUnit, ProductSellingModelId "
                                         "FROM PricebookEntry")]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "declares no")),
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
    ("a row the sourceRecordsFilter drops isn't checked for its lookup", False, lookups({
        "qb/en-US/p": ([[dict(PBE, sourceRecordsFilter="Kind = 'good'")]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,Kind,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,bad,A;T\nY,good,\n"})})),
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
    """Conflicts for the tree, kept only on `field` when given. Keys are (object, record, field)."""
    return {k: v for k, v in L.shared_conflicts(tree(plans)).items() if field in (None, k[2])}


def filter_errors(plans):
    return L.filter_errors(tree(plans))


LOOKUPS = json.dumps({"lookups": [{
    "object": "ProductUsageResource",
    "keyFields": ["Product.StockKeepingUnit", "UsageResource.Code"],
    "children": [{"objects": ["ProductUsageGrant"], "idColumn": "ProductUsageResourceId",
                  "keyColumns": ["ProductUsageResource.Product.StockKeepingUnit",
                                 "ProductUsageResource.UsageResource.Code"]}]}]})

PRS = decl("ProductRampSegment", "Product.StockKeepingUnit;SegmentType")


def key_field_outside_composite_doesnt_raise():
    """Parent.Name isn't one of `Parent.$$Code$Other`'s fields; the CSV just doesn't carry it,
    so it's an empty part rather than a part lost in the composite."""
    try:
        conflicts({"qb/en-US/a": ([[decl("Child__c", "Code__c;Parent.Name")]], {
                       "Child__c.csv": "Code__c,Parent.$$Code$Other\nC,Z\n"}),
                   "q3/en-US/b": ([[decl("Child__c", "Code__c;Parent.Name")]], {
                       "Child__c.csv": "Code__c\nC\n"})})
    except ValueError:
        return False
    return True


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
    # Review cases (PR #674).
    ("a shape keyed differently still matches the same record (mfg `Name` vs qb "
     "`Name;SellingModelType`)", True, conflicts({
        "qb/en-US/a": ([[SM]], {"ProductSellingModel.csv":
                                "$$Name$SellingModelType,Name,SellingModelType,PricingTerm\n"
                                "Evergreen Annual;Evergreen,Evergreen Annual,Evergreen,1\n"}),
        "mfg/en-US/b": ([[decl("ProductSellingModel", "Name")]], {"ProductSellingModel.csv":
                        "Name,SellingModelType,PricingTerm\nEvergreen Annual,Evergreen,99\n"})},
        "PricingTerm")),
    ("a composite lookup reference that differs between shapes is a conflict", True, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv":
                                 "UnitCode,UnitOfMeasureClass.$$Code$Type\nGB,DATAVOL;Data\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv":
                                 "UnitCode,UnitOfMeasureClass.$$Code$Type\nGB,DAT01;Data\n"})},
        "UnitOfMeasureClass.Code")),
    ("equal value sets with different per-plan values still conflict", True, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
        "qb/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,2\n"}),
        "q3/en-US/c": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,2\n"}),
        "q3/en-US/d": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"})},
        "Sequence")),
    ("a row a pass's sourceRecordsFilter drops isn't a write", False, conflicts({
        "qb/en-US/a": ([[PRS]], {"ProductRampSegment.csv":
                                 "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                 "SegmentType,Label\nX;Yearly,X,Yearly,One\n"}),
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="SegmentType <> 'Yearly'")]], {
            "ProductRampSegment.csv": "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                      "SegmentType,Label\nX;Yearly,X,Yearly,Two\n"})})),
    ("a LIKE sourceRecordsFilter is case-insensitive and whole-value", True, conflicts({
        "qb/en-US/a": ([[PRS]], {"ProductRampSegment.csv":
                                 "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                 "SegmentType,Label\nX;Yearly,X,Yearly,One\n"}),
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="[SegmentType] LIKE 'y%LY'")]], {
            "ProductRampSegment.csv": "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                      "SegmentType,Label\nX;Yearly,X,Yearly,Two\n"})}, "Label")),
    ("a sourceRecordsFilter the check can't evaluate is reported", True, filter_errors({
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="SegmentType IN ('A','B')")]], {
            "ProductRampSegment.csv": "Product.StockKeepingUnit,SegmentType\nX,A\n"})})),
    ("a sourceRecordsFilter on a column the CSV doesn't have is reported", True, filter_errors({
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="Segment = 'A'")]], {
            "ProductRampSegment.csv": "Product.StockKeepingUnit,SegmentType\nX,A\n"})})),
    ("a LIKE without wildcards doesn't match a substring", False, conflicts({
        "qb/en-US/a": ([[PRS]], {"ProductRampSegment.csv":
                                 "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                 "SegmentType,Label\nX;Yearly,X,Yearly,One\n"}),
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="[SegmentType] LIKE 'year'")]], {
            "ProductRampSegment.csv": "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                      "SegmentType,Label\nX;Yearly,X,Yearly,Two\n"})})),
    ("an `=` sourceRecordsFilter keeps exact matches", True, conflicts({
        "qb/en-US/a": ([[PRS]], {"ProductRampSegment.csv":
                                 "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                 "SegmentType,Label\nX;Yearly,X,Yearly,One\n"}),
        "q3/en-US/b": ([[dict(PRS, sourceRecordsFilter="SegmentType = 'Yearly'")]], {
            "ProductRampSegment.csv": "$$Product.StockKeepingUnit$SegmentType,Product.StockKeepingUnit,"
                                      "SegmentType,Label\nX;Yearly,X,Yearly,Two\n"})}, "Label")),
    # mfg keys selling models on Name alone, so its load overwrites qb's SellingModelType too.
    ("a narrower key's load overwrites the wider key's extra key field", True, conflicts({
        "qb/en-US/a": ([[SM]], {"ProductSellingModel.csv":
                                "$$Name$SellingModelType,Name,SellingModelType\nA;Evergreen,A,Evergreen\n"}),
        "mfg/en-US/b": ([[decl("ProductSellingModel", "Name")]], {"ProductSellingModel.csv":
                        "Name,SellingModelType\nA,TermDefined\n"})}, "SellingModelType")),
    # Both create; the JPY and USD rows are different records under both keys.
    ("records keyed apart by an extra key field aren't merged", False, conflicts({
        "qb/ja/a": ([[decl("CurrencyThing__c", "Name;CurrencyIsoCode")]], {
            "CurrencyThing__c.csv": "$$Name$CurrencyIsoCode,Name,CurrencyIsoCode,IsActive\n"
                                    "V;JPY,V,JPY,true\n"}),
        "q3/en-US/b": ([[decl("CurrencyThing__c", "Name;CurrencyIsoCode")]], {
            "CurrencyThing__c.csv": "$$Name$CurrencyIsoCode,Name,CurrencyIsoCode,IsActive\n"
                                    "V;USD,V,USD,false\n"})},
        "IsActive")),
    ("an Update-only plan doesn't create a record another shape would meet", False, conflicts({
        "qb/en-US/a": ([[decl("UnitOfMeasure", "UnitCode", op="Update")]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[decl("UnitOfMeasure", "UnitCode", op="Update")]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,0.001\n"})})),
    # A key part present only inside the primary `$$` column (`$$A$B` with no `B` column). Without
    # the split, qb's two rows would collide on `X` and q3's Annual row would meet the wrong one.
    ("a key part held only in the `$$` column is still matched", False, conflicts({
        "qb/en-US/a": ([[decl("PricebookEntry", "Product2.StockKeepingUnit;ProductSellingModel.Name")]], {
            "PricebookEntry.csv": "$$Product2.StockKeepingUnit$ProductSellingModel.Name,"
                                  "Product2.StockKeepingUnit,UnitPrice\nX;Annual,X,10\nX;Monthly,X,20\n"}),
        "q3/en-US/b": ([[decl("PricebookEntry", "Product2.StockKeepingUnit;ProductSellingModel.Name")]], {
            "PricebookEntry.csv": "$$Product2.StockKeepingUnit$ProductSellingModel.Name,"
                                  "Product2.StockKeepingUnit,UnitPrice\nX;Annual,X,10\n"})}, "UnitPrice")),
    # qb's later pass clears the composite lookup; q3 sets it. Cleared is a value too.
    ("a cleared `$$` lookup conflicts with a set one", True, conflicts({
        "qb/en-US/a": ([[PBE], [dict(PBE, operation="Update")]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n",
            "objectset_source/object-set-2/PricebookEntry.csv":
                "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\nX,#N/A\n"}),
        "q3/en-US/b": ([[PBE]], {
            "PricebookEntry.csv": "Product2.StockKeepingUnit,ProductSellingModel.$$Name$SellingModelType\n"
                                  "X,A;T\n"})}, "ProductSellingModel.Name")),
    # A blank primary `$$` key column matches nothing and writes nothing; it mustn't blank the
    # key part it would carry (SellingModelType here), which mfg's narrower key would compare.
    ("a blank `$$` key column doesn't blank its parts", False, conflicts({
        "q3/en-US/a": ([[SM]], {"ProductSellingModel.csv":
                                "$$Name$SellingModelType,Name,PricingTerm\n,A,1\n"}),
        "mfg/en-US/b": ([[decl("ProductSellingModel", "Name")]], {
            "ProductSellingModel.csv": "Name,SellingModelType,PricingTerm\nA,TermDefined,1\n"})},
        "SellingModelType")),
    # Rows the `$$` key shortens (an empty part dropped) are split using the columns known
    # empty, so qb's AUD and CAD rows stay two records; only CAD meets q3's and conflicts.
    ("a `$$` key with a dropped empty part is rebuilt", True, conflicts({
        "qb/en-US/a": ([[decl("Thing__c", "A__c;B__c;C__c")]], {
            "Thing__c.csv": "$$A__c$B__c$C__c,B__c,Label\nX;AUD,,one\nX;CAD,,two\n"}),
        "q3/en-US/b": ([[decl("Thing__c", "A__c;B__c;C__c")]], {
            "Thing__c.csv": "$$A__c$B__c$C__c,A__c,B__c,C__c,Label\nX;CAD,X,,CAD,three\n"})},
        "Label") == {("Thing__c", "X;CAD", "Label"): "q3=['three']; qb=['two']"}),
    ("SFDMU's key drops empty parts, so (X,'',Y) meets (X,Y,'')", True, conflicts({
        "qb/en-US/a": ([[decl("Thing__c", "A__c;B__c;C__c")]], {
            "Thing__c.csv": "A__c,B__c,C__c,Label\nX,,Y,one\n"}),
        "q3/en-US/b": ([[decl("Thing__c", "A__c;B__c;C__c")]], {
            "Thing__c.csv": "A__c,B__c,C__c,Label\nX,Y,,two\n"})}, "Label")),
    ("surrounding whitespace keeps keys apart, as SFDMU does", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\n GB ,One\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,Two\n"})}, "Name")),
    ("#VALUE! and #ERROR! are null, so they don't conflict with a blank", False, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Description\nGB,#VALUE!\nMB,#error!\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Description\nGB,\nMB,\n"})},
        "Description")),
    # qb's skipExistingRecords pass leaves its 'one'; q3's 'two' conflicts with it.
    ("a skipExistingRecords pass doesn't change an existing record", True, conflicts({
        "qb/en-US/a": ([[UOM], [dict(UOM, skipExistingRecords=True)]], {
            "UnitOfMeasure.csv": "UnitCode,Name\nGB,one\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Name\nGB,two\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,two\n"})}, "Name")),
    # Pass 1 only updates (nothing exists on a fresh org); pass 2 inserts with skip. The record
    # is created in pass 2, with its values, and meets q3's.
    ("a skip pass after an Update still creates the record", True, conflicts({
        "qb/en-US/a": ([[dict(UOM, operation="Update")], [dict(UOM, skipExistingRecords=True)]], {
            "UnitOfMeasure.csv": "UnitCode,Name\nGB,one\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Name\nGB,two\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,one\n"})}, "Name")),
    # mfg keys on Name and has no SellingModelType column; qb's row with a blank type keys on
    # Name alone too, as SFDMU drops the empty part, so the two meet.
    ("a key field the other plan doesn't carry is an empty part", True, conflicts({
        "qb/en-US/a": ([[SM]], {"ProductSellingModel.csv":
                                "Name,SellingModelType,PricingTerm\nA,,1\n"}),
        "mfg/en-US/b": ([[decl("ProductSellingModel", "Name")]], {
            "ProductSellingModel.csv": "Name,PricingTerm\nA,2\n"})}, "PricingTerm")),
    # The plan's CSV has no CurrencyIsoCode column; its rows are placed on Name, as SFDMU would.
    ("a key column the CSV lacks doesn't drop the plan's rows", True, conflicts({
        "qb/en-US/a": ([[decl("Thing__c", "Name;CurrencyIsoCode")]], {
            "Thing__c.csv": "Name,Label\nA,one\n"}),
        "q3/en-US/b": ([[decl("Thing__c", "Name;CurrencyIsoCode")]], {
            "Thing__c.csv": "Name,Label\nA,two\n"})}, "Label")),
    # A shortened composite lookup with no component columns can't be split; it's compared whole.
    ("an unsplittable `$$` lookup is compared whole", True, conflicts({
        "qb/en-US/a": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,A\n"}),
        "q3/en-US/b": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,B\n"})},
        "Parent__r.$$Name$Optional__c")),
    # Keyed on a parent Id that parent_id_lookups.json fills at load: matched on the portable keys.
    ("a parent-Id key is matched on its parent_id_lookups.json columns", True, conflicts({
        "qb/en-US/a": ([[decl("ProductUsageGrant", "ProductUsageResourceId")]], {
            "parent_id_lookups.json": LOOKUPS,
            "ProductUsageGrant.csv": "ProductUsageResource.Product.StockKeepingUnit,"
                                     "ProductUsageResource.UsageResource.Code,Quantity\nX,T,10\n"}),
        "q3/en-US/b": ([[decl("ProductUsageGrant", "ProductUsageResourceId")]], {
            "parent_id_lookups.json": LOOKUPS,
            "ProductUsageGrant.csv": "ProductUsageResource.Product.StockKeepingUnit,"
                                     "ProductUsageResource.UsageResource.Code,Quantity\nX,T,20\n"})},
        "Quantity")),
    # qb's row splits (X;Y), q3's can't (Z): they still meet on the whole value.
    ("a split `$$` lookup meets an unsplit one", True, conflicts({
        "qb/en-US/a": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,X;Y\n"}),
        "q3/en-US/b": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,Z\n"})},
        "Parent__r.$$Name$Optional__c")),
    ("`X;` and `X` are the same lookup, as SFDMU drops the empty part", False, conflicts({
        "qb/en-US/a": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,X;\n"}),
        "q3/en-US/b": ([[decl("Child__c", "Code__c")]], {
            "Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nK,X\n"})},
        "Parent__r.$$Name$Optional__c")),
    ("a key field outside the composite isn't reported as lost in it", True,
     key_field_outside_composite_doesnt_raise()),
    ("a lookup set through different parent keys is reported", True, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Code__c\nR,4100\n"}),
        "mfg/en-US/b": ([[decl("Rule__c", "Name")]], {
            "Rule__c.csv": "Name,Account__r.Name\nR,4100 Revenue\n"})},
        "Account__r (different parent keys)")),
    ("a lookup left whole isn't reported as a different parent key", False, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {
            "Rule__c.csv": "Name,Parent__r.$$Name$Optional__c\nR,A\n"}),
        "q3/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Parent__r.Name\nR,A\n"})},
        "Parent__r (different parent keys)")),
    ("a plain different key beside a lookup left whole is still reported", True, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {
            "Rule__c.csv": "Name,Parent__r.$$Name$Optional__c,Parent__r.Code__c\nR,A,1\n"}),
        "q3/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Parent__r.Other__c\nR,1\n"})},
        "Parent__r (different parent keys)")),
    ("a lookup cleared through one parent key and set through another is reported", True, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Code__c\nR,4100\n"}),
        "mfg/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Name\nR,#N/A\n"})},
        "Account__r (set in one plan, cleared in another)")),
    ("a lookup cleared in both shapes, through different keys, isn't reported", False, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Code__c\nR,\n"}),
        "mfg/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Name\nR,#N/A\n"})})),
    # qb creates R/C; q3 updates it by Name, mfg by Code__c. Neither row carries the other's key.
    ("differently keyed Updates meet through the creator's record", True, conflicts({
        "qb/en-US/a": ([[decl("Thing__c", "Name")]], {"Thing__c.csv": "Name,Code__c\nR,C\n"}),
        "q3/en-US/b": ([[decl("Thing__c", "Name", op="Update")]], {
            "Thing__c.csv": "Name,Description\nR,two\n"}),
        "mfg/en-US/c": ([[decl("Thing__c", "Code__c", op="Update")]], {
            "Thing__c.csv": "Code__c,Description\nC,three\n"})}, "Description")),
    # qb-pcm creates; qb-x updates by Name; mfg updates by Code__c. The creator shares qb's shape.
    ("Updates meet through a creator of the same shape, in another plan", True, conflicts({
        "qb/en-US/pcm": ([[decl("Thing__c", "Code__c")]], {"Thing__c.csv": "Name,Code__c\nR,C\n"}),
        "qb/en-US/x": ([[decl("Thing__c", "Name", op="Update")]], {
            "Thing__c.csv": "Name,Description\nR,two\n"}),
        "mfg/en-US/c": ([[decl("Thing__c", "Code__c", op="Update")]], {
            "Thing__c.csv": "Code__c,Description\nC,three\n"})}, "Description")),
    # qb's pass 2 moves the lookup from Account__r.Name to Account__r.Code__c and clears it;
    # mfg sets it by Name. qb's final state is cleared, so it conflicts.
    ("a later pass's lookup column replaces an earlier pass's", True, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")], [decl("Rule__c", "Name", op="Update")]], {
            "Rule__c.csv": "Name,Account__r.Name\nR,X\n",
            "objectset_source/object-set-2/Rule__c.csv": "Name,Account__r.Code__c\nR,\n"}),
        "mfg/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Name\nR,X\n"})},
        "Account__r (set in one plan, cleared in another)")),
    ("a lookup set through the same parent key isn't reported that way", False, conflicts({
        "qb/en-US/a": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Code__c\nR,4100\n"}),
        "mfg/en-US/b": ([[decl("Rule__c", "Name")]], {"Rule__c.csv": "Name,Account__r.Code__c\nR,4100\n"})},
        "Account__r (different parent keys)")),
    # q3 and mfg only Update a record qb creates, and agree with qb but not with each other.
    # Their Updates still meet, though neither creates the record.
    ("two shapes' Updates meet on a record a third creates", True, conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name,Description\nGB,one,x\n"}),
        "q3/en-US/b": ([[dict(UOM, operation="Update")]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,two\n"}),
        "mfg/en-US/c": ([[dict(UOM, operation="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Name\nGB,three\n"})}, "Name")
     .get(("UnitOfMeasure", "GB", "Name"), "") == "mfg=['three']; q3=['two']; qb=['one']"),
    ("Updates meet on a created record even when the creator doesn't write the field", True,
     bool(conflicts({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"}),
        "q3/en-US/b": ([[dict(UOM, operation="Update")]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,two\n"}),
        "mfg/en-US/c": ([[dict(UOM, operation="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Name\nGB,three\n"})}, "Name"))),
    ("a declaration with no externalId is reported as unkeyed", True, L.unkeyed_writes(tree({
        "qb/en-US/a": ([[decl("Thing__c", "")]], {"Thing__c.csv": "Label\none\n"})}))),
    ("rows that carry none of their key are reported", True, L.unkeyed_writes(tree({
        "qb/en-US/a": ([[decl("Thing__c", "Missing__c")]], {"Thing__c.csv": "Label\none\n"})}))),
    ("keyed rows aren't reported as unkeyed", False, L.unkeyed_writes(tree({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"})}))),
    ("a CSV column the query doesn't select isn't a write", False, conflicts({
        "qb/en-US/a": ([[dict(UOM, query="SELECT UnitCode FROM UnitOfMeasure")]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[dict(UOM, query="SELECT UnitCode FROM UnitOfMeasure")]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,0.001\n"})})),
    ("a lookup column counts as written when the query selects its Id field", True, conflicts({
        "qb/en-US/a": ([[dict(UOM, query="SELECT UnitCode, UnitOfMeasureClassId FROM UnitOfMeasure")]],
                       {"UnitOfMeasure.csv": "UnitCode,UnitOfMeasureClass.Code\nGB,DATAVOL\n"}),
        "q3/en-US/b": ([[dict(UOM, query="SELECT UnitCode, UnitOfMeasureClassId FROM UnitOfMeasure")]],
                       {"UnitOfMeasure.csv": "UnitCode,UnitOfMeasureClass.Code\nGB,DAT01\n"})},
        "UnitOfMeasureClass.Code")),
    ("two Updates to a platform-seeded record meet", True, conflicts({
        "qb/ja/a": ([[decl("PriceAdjustmentSchedule", "Name;CurrencyIsoCode", op="Update")]], {
            "PriceAdjustmentSchedule.csv": "$$Name$CurrencyIsoCode,Name,CurrencyIsoCode,EffectiveFrom\n"
                                           "Standard Price Adjustment Tier;USD,Standard Price Adjustment Tier,"
                                           "USD,2025\n"}),
        "mfg/en-US/b": ([[decl("PriceAdjustmentSchedule", "Name", op="Update")]], {
            "PriceAdjustmentSchedule.csv": "Name,CurrencyIsoCode,EffectiveFrom\n"
                                           "Standard Price Adjustment Tier,USD,2024\n"})},
        "EffectiveFrom")),
]


def cases(plans):
    return L.case_collisions(tree(plans))


SHARED_CASES += [
    ("keys two shapes create that differ only in case are reported", True, cases({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nEACH\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nEach\n"})})),
    ("a case collision is found along a narrower key", True, cases({
        "qb/ja/a": ([[decl("ProductComponentGroup", "Code;ParentProduct.StockKeepingUnit")]], {
            "ProductComponentGroup.csv": "$$Code$ParentProduct.StockKeepingUnit,Code,"
                                         "ParentProduct.StockKeepingUnit\nAccessories;X,Accessories,X\n"}),
        "q3/en-US/b": ([[decl("ProductComponentGroup", "Code")]],
                       {"ProductComponentGroup.csv": "Code\nACCESSORIES\n"})})),
    ("a key column the query doesn't select still places the row", True, conflicts({
        "qb/en-US/a": ([[dict(UOM, query="SELECT ConversionFactor FROM UnitOfMeasure")]],
                       {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,ConversionFactor\nGB,0.001\n"})},
        "ConversionFactor")),
    ("an unscoped deleteOldData on an object another shape writes is reported", True,
     L.cross_shape_deletes(tree({
         "qb/en-US/a": ([[dict(UOM, deleteOldData=True)]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"}),
         "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nMB\n"})}))),
    # A scope is reported too: whether it spares the other shape's records takes a person.
    ("a deleteOldData scoped by a deleteQuery is still reported", True,
     L.cross_shape_deletes(tree({
         "qb/en-US/a": ([[dict(UOM, deleteOldData=True,
                               deleteQuery="SELECT Id FROM UnitOfMeasure WHERE UnitCode = 'GB'")]],
                        {"UnitOfMeasure.csv": "UnitCode\nGB\n"}),
         "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nMB\n"})}))),
    ("a deleteOldData scoped by a WHERE is still reported", True,
     L.cross_shape_deletes(tree({
         "qb/en-US/a": ([[dict(UOM, deleteOldData=True,
                               query="SELECT all FROM UnitOfMeasure WHERE IsActive = true")]],
                        {"UnitOfMeasure.csv": "UnitCode\nGB\n"}),
         "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nMB\n"})}))),
    ("a deleteOldData on an object only its own shape writes isn't reported", False,
     L.cross_shape_deletes(tree({
         "qb/en-US/a": ([[dict(UOM, deleteOldData=True)]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"}),
         "qb/ja/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nMB\n"})}))),
    ("one collision across key widths is one entry", True, len(cases({
        "qb/ja/a": ([[decl("ProductComponentGroup", "Code;ParentProduct.StockKeepingUnit")]], {
            "ProductComponentGroup.csv": "$$Code$ParentProduct.StockKeepingUnit,Code,"
                                         "ParentProduct.StockKeepingUnit\nAccessories;X,Accessories,X\n"}),
        "q3/en-US/b": ([[decl("ProductComponentGroup", "Code")]],
                       {"ProductComponentGroup.csv": "Code,ParentProduct.StockKeepingUnit\n"
                                                     "ACCESSORIES,X\n"})})) == 1),
    # Only q3's load meets qb's record (on Code;Sequence); the entry is filed under qb's
    # Code;Name, the narrower by tiebreak, with qb's own Name, not q3's.
    ("keys of one width on different fields file under the owner's key", True, set(cases({
        "qb/en-US/a": ([[decl("ProductComponentGroup", "Code;Name")]], {
            "ProductComponentGroup.csv": "$$Code$Name,Code,Name,Sequence\nAcc;Acc,Acc,Acc,1\n"}),
        "q3/en-US/b": ([[decl("ProductComponentGroup", "Code;Sequence")]], {
            "ProductComponentGroup.csv": "$$Code$Sequence,Code,Name,Sequence\n"
                                         "ACC;1,ACC,Accessory group,1\n"})}))
     == {("ProductComponentGroup", "acc;acc")}),
    ("identical keys in two shapes aren't a case collision", False, cases({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nEACH\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nEACH\n"})})),
]


def stale_shared_entry_fails():
    """A KNOWN_SHARED_CONFLICTS entry that no longer conflicts fails the live run."""
    import contextlib
    import io
    saved = L.KNOWN_SHARED_CONFLICTS
    L.KNOWN_SHARED_CONFLICTS = saved | {("Nope__c", "X", "Nope")}
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        return code == 1 and "Nope__c 'X' Nope is in KNOWN_SHARED_CONFLICTS" in out.getvalue()
    finally:
        L.KNOWN_SHARED_CONFLICTS = saved


def unknown_shared_conflict_fails():
    """Dropping one record's conflict from the allowlist makes the live run fail on that record,
    though another record still conflicts on the same field."""
    import contextlib
    import io
    saved = L.KNOWN_SHARED_CONFLICTS
    L.KNOWN_SHARED_CONFLICTS = saved - {("CurrencyType", "CAD", "ConversionRate")}  # AUD stays
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        text = out.getvalue()
        return (code == 1 and "CurrencyType 'CAD' ConversionRate differs" in text
                and "CurrencyType 'AUD' ConversionRate differs" not in text)
    finally:
        L.KNOWN_SHARED_CONFLICTS = saved


def later_pass_row_without_first_key_raises():
    """One unplaceable row raises even when another row of the same pass carries the first key."""
    try:
        conflicts({"qb/en-US/a": ([[UOM], [dict(UOM, externalId="Name", operation="Update")]],
                                  {"UnitOfMeasure.csv": "UnitCode,Name\nGB,Gigabyte\n",
                                   "objectset_source/object-set-2/UnitOfMeasure.csv":
                                       "UnitCode,Name,Description\nGB,Gigabyte,x\n,Megabyte,y\n"}),
                   "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"})})
    except ValueError as e:
        return "Megabyte" in str(e)
    return False


def later_pass_without_first_key_raises():
    """A later pass whose rows carry none of the plan's first key can't be placed and raises."""
    try:
        conflicts({"qb/en-US/a": ([[UOM], [dict(UOM, externalId="Name", operation="Update")]],
                                  {"UnitOfMeasure.csv": "UnitCode,Name\nGB,Gigabyte\n",
                                   "objectset_source/object-set-2/UnitOfMeasure.csv":
                                       "Name,Description\nGigabyte,1e9 bytes\n"}),
                   "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nGB\n"})})
    except ValueError as e:
        return "without the plan's first key (UnitCode)" in str(e)
    return False


def ambiguous_dropped_key_part_raises():
    """A `$$` key that drops a part this check can't place stops it rather than merging rows."""
    try:
        conflicts({"qb/en-US/a": ([[decl("Thing__c", "A__c;B__c;C__c")]],
                                  {"Thing__c.csv": "$$A__c$B__c$C__c,Label\nX;Y,one\n"}),
                   "q3/en-US/b": ([[decl("Thing__c", "A__c;B__c;C__c")]],
                                  {"Thing__c.csv": "A__c,B__c,C__c,Label\nX,Y,Z,two\n"})})
    except ValueError as e:
        return "drops empty parts" in str(e)
    return False


def extra_key_pieces_raise_with_their_cause():
    """A `$$` key with more pieces than parts says so, rather than asking for missing columns."""
    try:
        conflicts({"qb/en-US/a": ([[decl("Thing__c", "A__c;B__c")]],
                                  {"Thing__c.csv": "$$A__c$B__c,Label\nX;Y;Z,one\n"}),
                   "q3/en-US/b": ([[decl("Thing__c", "A__c;B__c")]],
                                  {"Thing__c.csv": "A__c,B__c,Label\nX,Y,two\n"})})
    except ValueError as e:
        return "3 pieces for 2 key parts" in str(e)
    return False


def key_part_in_unsplittable_lookup_raises():
    """A key part found only in a `$$` lookup that can't be split stops the check."""
    try:
        conflicts({"qb/en-US/a": ([[decl("Child__c", "Code__c;Parent__r.Name")]],
                                  {"Child__c.csv": "Code__c,Parent__r.$$Name$Optional__c\nC,Z\nC,W\n"}),
                   "q3/en-US/b": ([[decl("Child__c", "Code__c;Parent__r.Name")]],
                                  {"Child__c.csv": "Code__c,Parent__r.Name\nC,Z\n"})})
    except ValueError as e:
        return "only in a `$$` lookup" in str(e)
    return False


def multi_hop_key_part_in_unsplittable_lookup_raises():
    """The same, where the key part is two hops down the lookup."""
    try:
        conflicts({"qb/en-US/a": ([[decl("Child__c", "Code__c;PUR.Product.StockKeepingUnit")]],
                                  {"Child__c.csv": "Code__c,PUR.$$Product.StockKeepingUnit$X__c\nC,Z\n"}),
                   "q3/en-US/b": ([[decl("Child__c", "Code__c")]],
                                  {"Child__c.csv": "Code__c\nC\n"})})
    except ValueError as e:
        return "only in a `$$` lookup" in str(e)
    return False


def malformed_lookups_file_exits_2():
    """A structurally invalid parent_id_lookups.json is a tool error (exit 2), not a finding."""
    import contextlib
    import io
    root = tree({"qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode\nGB\n",
                                         "parent_id_lookups.json": '{"lookups": []}'})})
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        return L.main(["--root", str(root)]) == 2


def stale_case_collision_fails():
    """A KNOWN_CASE_COLLISIONS entry with no collision left fails the live run."""
    import contextlib
    import io
    saved = L.KNOWN_CASE_COLLISIONS
    L.KNOWN_CASE_COLLISIONS = saved | {("Nope__c", "x")}
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        return code == 1 and "Nope__c" in out.getvalue()
    finally:
        L.KNOWN_CASE_COLLISIONS = saved


SHARED_CASES += [
    ("a later pass keyed on none of the first key raises", True, later_pass_without_first_key_raises()),
    ("a later pass row without the first key raises", True, later_pass_row_without_first_key_raises()),
    ("an ambiguous dropped `$$` key part raises", True, ambiguous_dropped_key_part_raises()),
    ("extra `$$` key pieces raise with their own cause", True, extra_key_pieces_raise_with_their_cause()),
    ("a key part only in an unsplittable `$$` lookup raises", True,
     key_part_in_unsplittable_lookup_raises()),
    ("a multi-hop key part only in an unsplittable `$$` lookup raises", True,
     multi_hop_key_part_in_unsplittable_lookup_raises()),
    ("a malformed parent_id_lookups.json exits 2", True, malformed_lookups_file_exits_2()),
    ("a stale case-collision entry fails the run", True, stale_case_collision_fails()),
    ("a stale shared-conflict entry fails the run", True, stale_shared_entry_fails()),
    ("a shared conflict missing from the allowlist fails the run", True, unknown_shared_conflict_fails()),
]


def intra(plans, field=None):
    """Intra-shape conflicts for the tree, kept only on `field` when given."""
    return {k: v for k, v in L.intra_shape_conflicts(tree(plans)).items() if field in (None, k[2])}


P2 = decl("Product2", "StockKeepingUnit")
P2_UPDATE = decl("Product2", "StockKeepingUnit", op="Update")


def stale_intra_entry_fails():
    """A KNOWN_INTRA_SHAPE_CONFLICTS entry that no longer conflicts fails the live run."""
    import contextlib
    import io
    saved = L.KNOWN_INTRA_SHAPE_CONFLICTS
    L.KNOWN_INTRA_SHAPE_CONFLICTS = saved | {("Nope__c", "X", "Nope")}
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main([])
        return code == 1 and "Nope__c 'X' Nope is in KNOWN_INTRA_SHAPE_CONFLICTS" in out.getvalue()
    finally:
        L.KNOWN_INTRA_SHAPE_CONFLICTS = saved


def new_intra_conflict_fails():
    """Two qb plans disagreeing on a field fail the run with an `intra:` line; agreeing, they don't."""
    import contextlib
    import io

    lists = ("KNOWN_SHARED_CONFLICTS", "KNOWN_INTRA_SHAPE_CONFLICTS", "KNOWN_CASE_COLLISIONS",
             "KNOWN_CROSS_SHAPE_DELETES", "KNOWN_UNKEYED_WRITES", "KNOWN_UNRESOLVED_LOOKUPS")
    saved = {n: getattr(L, n) for n in lists}

    def run(second):
        root = tree({"qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
                     "qb/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": f"UnitCode,Sequence\nGB,{second}\n"})})
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = L.main(["--root", str(root)])
        return code, out.getvalue()
    try:
        for n in lists:  # the shipped allowlists would all be stale against this tree
            setattr(L, n, set())
        (bad_code, bad), (good_code, _) = run(2), run(1)
    finally:
        for n, v in saved.items():
            setattr(L, n, v)
    return (bad_code == 1 and good_code == 0
            and "intra: UnitOfMeasure 'GB' Sequence differs between two plans" in bad)


INTRA_CASES = [
    # The todo 336 defect: qb-pcm upserts Product2 with a blank DisplayUrl, and a second qb plan
    # (an Update on StockKeepingUnit) sets it, so a reload of qb-pcm alone blanks the image.
    ("two plans of one shape writing different values to one field conflict (todo 336)", True,
     intra({"qb/en-US/qb-pcm": ([[P2]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,\n"}),
            "qb/en-US/qb-images": ([[P2_UPDATE]], {
                "Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/img/qb-1.png\n"})}, "DisplayUrl")),
    ("it is labelled by plan, not shape", True, list(intra({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
        "qb/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,2\n"})}).values())
     == ["qb/en-US/a=['1']; qb/en-US/b=['2']"]),
    ("the same values in two plans of one shape don't conflict", False, intra({
        "q3/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"})})),
    ("one plan's own Draft-then-Active staging isn't an intra-shape conflict", False, intra({
        "q3/en-US/a": ([[UOM], [dict(UOM, op="Update")]], {
            "UnitOfMeasure.csv": "UnitCode,Status\nGB,Draft\n",
            "objectset_source/object-set-2/UnitOfMeasure.csv": "UnitCode,Status\nGB,Active\n"})})),
    ("qb/ja isn't compared against qb/en-US (its locale overlay: todo 212)", False, intra({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,Gigabyte\n"}),
        "qb/ja/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,ギガバイト\n"})})),
    ("two qb/ja plans are compared with each other", True, intra({
        "qb/ja/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,ギガ\n"}),
        "qb/ja/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Name\nGB,ギガバイト\n"})}, "Name")),
    ("plans of different shapes aren't intra-shape", False, intra({
        "qb/en-US/a": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,1\n"}),
        "q3/en-US/b": ([[UOM]], {"UnitOfMeasure.csv": "UnitCode,Sequence\nGB,2\n"})})),
    ("a top-level plan (sample data) loads with every shape, so it meets them as `common`", True,
     intra({"qb/en-US/a": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,United States\n"}),
            "scratch_data": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,US\n"})})
     == {} and list(conflicts({
         "qb/en-US/a": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,United States\n"}),
         "scratch_data": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,US\n"})}).values())
     == ["common=['US']; qb=['United States']"]),
    ("a top-level plan that agrees with a shape doesn't conflict", False, conflicts({
        "q3/en-US/a": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,US\n"}),
        "scratch_data": ([[decl("Account", "Name")]], {"Account.csv": "Name,BillingCountry\nApex,US\n"})})),
    ("two same-shape Updates meet on a record a third plan of that locale creates", True, intra({
        "qb/en-US/c": ([[P2]], {"Product2.csv": "StockKeepingUnit\nQB-1\n"}),
        "qb/en-US/a": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/a.png\n"}),
        "qb/en-US/b": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/b.png\n"})},
        "DisplayUrl")),
    ("two same-shape Updates to a record nobody creates don't conflict", False, intra({
        "qb/en-US/a": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/a.png\n"}),
        "qb/en-US/b": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/b.png\n"})})),
    ("nor do they when only another locale creates it (qb/ja's records aren't in a qb/en-US org)", False, intra({
        "qb/ja/c": ([[P2]], {"Product2.csv": "StockKeepingUnit\nQB-1\n"}),
        "qb/en-US/a": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/a.png\n"}),
        "qb/en-US/b": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/b.png\n"})})),
    ("two qb/ja Updates meet on a record qb/en-US creates (qb/ja loads over a qb org)", True, intra({
        "qb/en-US/c": ([[P2]], {"Product2.csv": "StockKeepingUnit\nQB-1\n"}),
        "qb/ja/a": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,Name\nQB-1,ア\n"}),
        "qb/ja/b": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,Name\nQB-1,イ\n"})}, "Name")),
    ("two top-level plans' Updates meet on a record a shape creates (they load into its org)", True, intra({
        "qb/en-US/c": ([[P2]], {"Product2.csv": "StockKeepingUnit\nQB-1\n"}),
        "inapp": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/a.png\n"}),
        "scratch_data": ([[P2_UPDATE]], {"Product2.csv": "StockKeepingUnit,DisplayUrl\nQB-1,/b.png\n"})},
        "DisplayUrl")),
    ("a new intra-shape conflict fails the run", True, new_intra_conflict_fails()),
    ("a stale intra-shape entry fails the run", True, stale_intra_entry_fails()),
]


def live_tree_passes():
    """The shipped tree is clean: no unresolved lookup, and every shared conflict is known."""
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return L.main([]) == 0


CASES = LOOKUP_CASES + SHARED_CASES + INTRA_CASES + [("the live tree passes", True, live_tree_passes())]


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
