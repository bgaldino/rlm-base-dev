#!/usr/bin/env python3
"""Offline tests for `scripts/sfdmu_id_lookups.py` (parent Id resolution before a load).

Builds a throwaway plan shaped like qb-rating-entitlements and a fake `query` function,
then checks what `apply_lookups` writes: the parent's Readonly CSV, the children's Id
column (root and per-pass), the Active-over-Draft tie-break, and that a missing or tied
key fails rather than loading a child against the wrong parent.

Run: `python tests/test_sfdmu_id_lookups.py` (offline, no org).
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import sfdmu_id_lookups as il  # noqa: E402

_failures: list[str] = []


def check(label: str, got, want) -> None:
    if got == want:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}\n       got:  {got!r}\n       want: {want!r}")
        _failures.append(label)


KEYS = ["ProductUsageResource.Product.StockKeepingUnit", "ProductUsageResource.UsageResource.Code"]
ID1, ID2 = "1TrWt00000076NFKAY", "1TrWt00000076NGKAY"
LOOKUPS = {"lookups": [{
    "object": "ProductUsageResource",
    "keyFields": ["Product.StockKeepingUnit", "UsageResource.Code"],
    "prefer": {"Status": ["Active", "Draft"]},
    "children": [{"objects": ["ProductUsageResourcePolicy", "ProductUsageGrant"],
                  "idColumn": "ProductUsageResourceId", "keyColumns": KEYS}],
}]}
EXPORT = {"useSeparatedCSVFiles": True, "objectSets": [
    {"objects": [
        {"query": "SELECT Id, Status FROM ProductUsageResource", "operation": "Readonly", "externalId": "Id"},
        {"query": "SELECT ProductUsageResourceId, Quantity FROM ProductUsageGrant", "operation": "Upsert",
         "externalId": "ProductUsageResourceId"}]},
    {"objects": [
        {"query": "SELECT Id, Status FROM ProductUsageResource", "operation": "Readonly", "externalId": "Id"},
        {"query": "SELECT ProductUsageResourceId FROM ProductUsageGrant", "operation": "Update",
         "externalId": "ProductUsageResourceId"}]},
]}


def pur(id_, sku, code, status):
    return {"Id": id_, "Status": status, "Product": {"StockKeepingUnit": sku},
            "UsageResource": {"Code": code}}


def write(path: pathlib.Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        w = csv.writer(handle, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def read(path: pathlib.Path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def make_plan(root: pathlib.Path, pug_rows, export=EXPORT, lookups=LOOKUPS):
    (root / "export.json").write_text(json.dumps(export))
    (root / il.LOOKUPS_FILENAME).write_text(json.dumps(lookups))
    write(root / "ProductUsageGrant.csv", KEYS + ["Quantity", "Status"], pug_rows)
    write(root / "objectset_source/object-set-2/ProductUsageGrant.csv", KEYS + ["Quantity"],
          [r[:3] for r in pug_rows])


def run(records, pug_rows, **kw):
    tmp = pathlib.Path(tempfile.mkdtemp())
    make_plan(tmp, pug_rows, **kw)
    queries = []

    def query(soql):
        queries.append(soql)
        return records
    try:
        filled = il.apply_lookups(str(tmp), query, log=lambda _m: None)
        return tmp, filled, queries, None
    except il.IdLookupError as exc:
        return tmp, None, queries, str(exc)


print("load_lookups")
with tempfile.TemporaryDirectory() as d:
    check("no file -> no lookups", il.load_lookups(d), [])
    pathlib.Path(d, il.LOOKUPS_FILENAME).write_text(json.dumps(
        {"lookups": [{"object": "X", "keyFields": ["A", "B"],
                      "children": [{"objects": ["C"], "idColumn": "XId", "keyColumns": ["X.A"]}]}]}))
    try:
        il.load_lookups(d)
        check("keyColumns must pair with keyFields", "no error", "IdLookupError")
    except il.IdLookupError:
        check("keyColumns must pair with keyFields", "IdLookupError", "IdLookupError")

print("apply_lookups: happy path")
records = [pur("PUR1", "QB-DB", "UR-CPU", "Active"), pur("PUR2", "QB-DB", "UR-DATA", "Active")]
plan, filled, queries, err = run(records, [["QB-DB", "UR-CPU", "5", "Draft"],
                                           ["QB-DB", "UR-DATA", "7", "Draft"]])
check("no error", err, None)
check("one query, declared fields + key + prefer",
      queries, ["SELECT Id, Status, Product.StockKeepingUnit, UsageResource.Code FROM ProductUsageResource"])
check("root and pass-2 child rows filled", filled, 4)
check("root child gets Id column first",
      list(read(plan / "ProductUsageGrant.csv")[0].keys())[0], "ProductUsageResourceId")
check("root child Ids", [r["ProductUsageResourceId"] for r in read(plan / "ProductUsageGrant.csv")],
      ["PUR1", "PUR2"])
check("pass-2 child Ids",
      [r["ProductUsageResourceId"] for r in read(plan / "objectset_source/object-set-2/ProductUsageGrant.csv")],
      ["PUR1", "PUR2"])
check("portable key columns kept", read(plan / "ProductUsageGrant.csv")[0][KEYS[1]], "UR-CPU")
check("parent CSV holds only the Readonly fields",
      read(plan / "ProductUsageResource.csv"), [{"Id": "PUR1", "Status": "Active"}, {"Id": "PUR2", "Status": "Active"}])
check("parent CSV written for pass 2 too",
      (plan / "objectset_source/object-set-2/ProductUsageResource.csv").is_file(), True)

print("apply_lookups: Draft duplicate next to the Active one")
records = [pur("DRAFT", "QB-DB", "UR-CPU", "Draft"), pur("ACT", "QB-DB", "UR-CPU", "Active")]
plan, filled, _q, err = run(records, [["QB-DB", "UR-CPU", "5", "Draft"]])
check("Active wins", [r["ProductUsageResourceId"] for r in read(plan / "ProductUsageGrant.csv")], ["ACT"])
check("parent CSV keeps only the chosen record", [r["Id"] for r in read(plan / "ProductUsageResource.csv")], ["ACT"])

print("apply_lookups: failures")
records = [pur("D1", "QB-DB", "UR-CPU", "Draft"), pur("D2", "QB-DB", "UR-CPU", "Draft")]
_p, _f, _q, err = run(records, [["QB-DB", "UR-CPU", "5", "Draft"]])
check("two Drafts tie -> fails", bool(err and "2 ProductUsageResource records tie for QB-DB;UR-CPU" in err), True)
_p, _f, _q, err = run([pur("PUR1", "QB-DB", "UR-CPU", "Active")], [["QB-DB", "UR-NONE", "5", "Draft"]])
check("missing parent -> fails and names the key",
      bool(err and "no ProductUsageResource for QB-DB;UR-NONE" in err), True)
_p, _f, _q, err = run([], [["QB-DB", "UR-CPU", "5", "Draft"]])
check("fresh org, parent never loaded -> fails", bool(err and "load the plan that creates ProductUsageResource first" in err), True)
bad_export = json.loads(json.dumps(EXPORT))
bad_export["objectSets"][0]["objects"][0]["operation"] = "Upsert"
_p, _f, _q, err = run([pur("PUR1", "QB-DB", "UR-CPU", "Active")], [["QB-DB", "UR-CPU", "5", "Draft"]],
                      export=bad_export)
check("parent not Readonly -> fails", bool(err and "must be declared Readonly" in err), True)

print("extraction")
check("extract export keeps Ids (boolean, not the truthy string)",
      il.prepare_extraction_export({"excludeIdsFromCSVFiles": "false"}, LOOKUPS["lookups"])["excludeIdsFromCSVFiles"],
      False)
check("plan without lookups is unchanged",
      il.prepare_extraction_export({"excludeIdsFromCSVFiles": "true"}, []), {"excludeIdsFromCSVFiles": "true"})
with tempfile.TemporaryDirectory() as d:
    write(pathlib.Path(d, "ProductUsageGrant.csv"), ["Id", "ProductUsageResourceId", "Quantity"],
          [["G1", ID1, "5"], ["G2", ID2, "7"]])
    seen = []

    def q(soql):
        seen.append(soql)
        return [pur(ID1, "QB-DB", "UR-CPU", "Active"), pur(ID2, "QB-DB", "UR-DATA", "Active")]
    n = il.restore_parent_keys(d, LOOKUPS["lookups"], q, log=lambda _m: None)
    rows = read(pathlib.Path(d, "ProductUsageGrant.csv"))
    check("restore: keys filled from the Id", [(r[KEYS[0]], r[KEYS[1]]) for r in rows],
          [("QB-DB", "UR-CPU"), ("QB-DB", "UR-DATA")])
    check("restore: rows counted", n, 2)
    check("restore: one IN query", len(seen) == 1 and f"WHERE Id IN ('{ID1}', '{ID2}')" in seen[0], True)
with tempfile.TemporaryDirectory() as d:
    write(pathlib.Path(d, "ProductUsageGrant.csv"), ["Id", "ProductUsageResourceId"], [["G1", ID1]])
    try:
        il.restore_parent_keys(d, LOOKUPS["lookups"], lambda _s: [], log=lambda _m: None)
        check("restore: unknown parent Id fails", "no error", "IdLookupError")
    except il.IdLookupError:
        check("restore: unknown parent Id fails", "IdLookupError", "IdLookupError")
for label, value in (("blank", "#N/A"), ("not an Id (quote)", "1TrWt0000007'OR'1")):
    with tempfile.TemporaryDirectory() as d:
        write(pathlib.Path(d, "ProductUsageGrant.csv"), ["Id", "ProductUsageResourceId"], [["G1", value]])
        try:
            il.restore_parent_keys(d, LOOKUPS["lookups"], lambda _s: [], log=lambda _m: None)
            check(f"restore: {label} parent Id fails before any query", "no error", "IdLookupError")
        except il.IdLookupError:
            check(f"restore: {label} parent Id fails before any query", "IdLookupError", "IdLookupError")

print("strip_extraction_ids")
with tempfile.TemporaryDirectory() as d:
    root = pathlib.Path(d)
    write(root / "ProductUsageResource.csv", ["Id", "Status"], [[ID1, "Active"]])
    write(root / "Product2.csv", ["Id", "StockKeepingUnit"], [["01t000000000001AAA", "QB-DB"]])
    write(root / "ProductUsageGrant.csv",
          ["Id", "ProductUsageResourceId", "UnitOfMeasureId", "UnitOfMeasure.UnitCode", KEYS[0], KEYS[1], "Quantity"],
          [["G1", ID1, "0hE000000000001AAA", "m", "QB-DB", "UR-CPU", "5"]])
    export = {"objectSets": [
        {"objects": [{"query": "SELECT Id, Status FROM ProductUsageResource", "operation": "Readonly"},
                     {"query": "SELECT StockKeepingUnit FROM Product2", "operation": "Readonly"},
                     {"query": "SELECT Quantity FROM ProductUsageGrant", "operation": "Upsert"}]},
        {"objects": [{"query": "SELECT Quantity FROM ProductUsageGrant", "operation": "Update"}]}]}
    il.strip_extraction_ids(d, export, log=lambda _m: None)
    check("strip: read-only objects' CSVs removed",
          sorted(p.name for p in root.glob("*.csv")), ["ProductUsageGrant.csv"])
    check("strip: Id and direct lookup columns dropped, traversals kept",
          list(read(root / "ProductUsageGrant.csv")[0].keys()),
          ["UnitOfMeasure.UnitCode", KEYS[0], KEYS[1], "Quantity"])
with tempfile.TemporaryDirectory() as d:
    write(pathlib.Path(d, "ProductUsageGrant.csv"), ["Quantity"], [["5"]])
    try:
        il.restore_parent_keys(d, LOOKUPS["lookups"], lambda _s: [], log=lambda _m: None)
        check("restore: extract without the Id column fails", "no error", "IdLookupError")
    except il.IdLookupError:
        check("restore: extract without the Id column fails", "IdLookupError", "IdLookupError")

with tempfile.TemporaryDirectory() as d:
    root = pathlib.Path(d)
    write(root / "Mixed.csv", ["Id", "ParentId", "Parent.Code", "ExternalSystemId", "Name"],
          [["M1", "P1", "PC", "EXT-7", "a"]])
    write(root / "Tracked.csv", ["Id", "Code"], [["T1", "c"]])
    write(root / "Gone.csv", ["Id"], [["G1"]])
    write(root / "MissingParentRecordsReport.csv", ["Id", "Note"], [["X", "y"]])
    write(root / "Skipped.csv", ["Id"], [["S1"]])
    logs = []
    export = {"objectSets": [
        {"objects": [{"query": "SELECT Name FROM Mixed", "operation": "Readonly"},
                     {"query": "SELECT Code FROM Tracked", "operation": "Readonly"},
                     {"query": "SELECT Name FROM Gone", "operation": "Readonly"},
                     {"query": "SELECT Name FROM Skipped", "operation": "Readonly", "excluded": True}]},
        {"objects": [{"query": "SELECT Name FROM Mixed", "operation": "Update"}]}]}
    il.strip_extraction_ids(d, export, log=logs.append, keep_csvs={"Tracked"})
    check("strip: Readonly-in-one-pass, writable-in-another keeps its CSV", (root / "Mixed.csv").is_file(), True)
    check("strip: only lookups with a traversal beside them are dropped; data ...Id kept",
          list(read(root / "Mixed.csv")[0].keys()), ["Parent.Code", "ExternalSystemId", "Name"])
    check("strip: a kept ...Id column is logged", any("ExternalSystemId" in m for m in logs), True)
    check("strip: a tracked Readonly CSV is kept, Id dropped", list(read(root / "Tracked.csv")[0].keys()), ["Code"])
    check("strip: an untracked Readonly CSV is removed", (root / "Gone.csv").exists(), False)
    check("strip: excluded objects and non-plan CSVs are left alone",
          ((root / "Skipped.csv").is_file(), (root / "MissingParentRecordsReport.csv").is_file()), (True, True))
check("id_columns_of", il.id_columns_of(LOOKUPS["lookups"]), {"ProductUsageResourceId"})

print("prefer excludes unlisted statuses")
chosen, tied = il.build_id_map([pur(ID1, "QB-DB", "UR-CPU", "Inactive")], ["Product.StockKeepingUnit", "UsageResource.Code"],
                               {"Status": ["Active", "Draft"]})
check("an Inactive-only key is not resolved", (chosen, tied), ({}, {}))
_p, _f, _q, err = run([pur("A1", "QB-DB", "UR-CPU", "Active"), pur("A2", "QB-DB", "UR-CPU", "Active")],
                      [["QB-DB", "UR-CPU", "5", "Draft"]])
check("two Active copies tie and the message names the status rule",
      bool(err and "2 ProductUsageResource records tie" in err and "Status in ['Active', 'Draft']" in err), True)

print("shipped plan")
shipped = REPO / "datasets/sfdmu/qb/en-US/qb-rating-entitlements"
lookups = il.load_lookups(str(shipped))
check("qb-rating-entitlements declares one lookup", [lk["object"] for lk in lookups], ["ProductUsageResource"])
for name in ("ProductUsageResourcePolicy", "ProductUsageGrant"):
    for path in (shipped / f"{name}.csv", shipped / "objectset_source/object-set-2" / f"{name}.csv"):
        header = list(read(path)[0].keys())
        check(f"{path.relative_to(shipped)} carries the portable key, no Ids",
              (all(k in header for k in KEYS), "ProductUsageResourceId" in header), (True, False))
check("no tracked parent CSV (generated per load)",
      (shipped / "ProductUsageResource.csv").exists(), False)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
