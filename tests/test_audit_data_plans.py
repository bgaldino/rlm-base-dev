#!/usr/bin/env python3
"""Offline tests for scripts/audit_data_plans.py (todo 321).

- unknown-field: a selected field, an `externalId` component, or a traversal (any depth, followed
  through `referenceTo` where the target is in the snapshot) the object lacks.
- An unsupported `sourceRecordsFilter` is a tool error (exit 2), not a skipped declaration.
- picklist: a value outside a restricted picklist's active values gates; an unrestricted one is
  informational (undefined-value), as is CurrencyIsoCode never.
- required: each creating declaration of an object, on the rows it creates (a row a creating
  pass already created is only patched), leaving out or blanking a field that is createable, not
  nillable and not defaulted; an Update pass, a boolean and a defaulted field don't.
- dead-columns: values in a field that is neither createable nor updateable are informational, and
  a key field used only for matching is left out.
- unwritten: writable fields no plan writes, with the release diff's new fields marked;
  OwnerId/CurrencyIsoCode and custom fields aren't listed.
- release-values: values the release added to a picklist a plan writes.
- excluded and Readonly declarations aren't audited; an object missing from the describe is listed.
- classify: KNOWN_FINDINGS entries are known, and one that no longer matches is stale, but only
  for a plan the run audited, and not for an object the describe lacks.
- compact_describe drops a picklist's record-Id values (18 characters with a valid case checksum,
  15 with an Id's zero run), keeps object names that look like Ids, and marks the field so the
  audit doesn't value-check it.
- Multipicklist values are trimmed.
- merge_snapshots adds objects, fields and picklist values; the base wins on attributes, but an
  org-record (orgValues) marking from either side carries over.
- main: no snapshot for the active release exits 2; a clean snapshot exits 0, a finding 1.

Run: `python tests/test_audit_data_plans.py` (offline, no org).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("audit_data_plans", REPO / "scripts" / "audit_data_plans.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

_failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        _failures.append(label)
        print(f"       got:  {got!r}\n       want: {want!r}")


def field(type_="string", createable=True, updateable=True, nillable=True, defaulted=False,
          restricted=False, values=None, rel=None, calculated=False):
    f = {"type": type_, "createable": createable, "updateable": updateable, "nillable": nillable,
         "defaultedOnCreate": defaulted, "calculated": calculated, "autoNumber": False,
         "restrictedPicklist": restricted, "relationshipName": rel, "referenceTo": []}
    if values is not None:
        f["values"] = values
    return f


SNAPSHOT = {
    "Widget__x": {"fields": {
        "Name": field(),
        "Code": field(nillable=False),
        "Kind": field("picklist", restricted=True, values=["A", "B"]),
        "Family": field("picklist", values=["X"]),
        "CurrencyIsoCode": field("picklist", restricted=True, values=["USD"]),
        "Derived": field(createable=False, updateable=False),
        "Required": field(nillable=False),
        "Flag": field("boolean", nillable=False),
        "Defaulted": field(nillable=False, defaulted=True),
        "ParentId": {**field("reference", rel="Parent"), "referenceTo": ["Parent__x"]},
        "Spare": field(),
        "Added": field(),
        "OwnerId": field("reference", rel="Owner"),
        "Custom__c": field(),
        "Formula": field(calculated=True),
    }},
    "Parent__x": {"fields": {"Name": field(), "Code": field()}},
}
DIFF = {"object_diffs": {"Widget__x": {"added": ["Added"], "picklist_changed": [
    {"field": "Kind", "added": ["B"], "removed": []}, {"field": "Spare", "added": ["Z"], "removed": []}]}}}


def write_plan(root: pathlib.Path, rel: str, objects, csvs):
    plan = root / rel
    plan.mkdir(parents=True)
    (plan / "export.json").write_text(json.dumps({"objects": objects}), encoding="utf-8")
    for name, text in csvs.items():
        (plan / name).write_text(text, encoding="utf-8")
    return plan


def fixture(tmp: pathlib.Path):
    write_plan(tmp, "qb/en-US/qb-widgets", [
        {"query": "SELECT Name, Code, Kind, Family, CurrencyIsoCode, Derived, Required, ParentId, "
                  "Parent.Code, Missing, Ghost.Name FROM Widget__x",
         "operation": "Upsert", "externalId": "Code"},
        {"query": "SELECT Name, Code FROM Widget__x", "operation": "Update", "externalId": "Code"},
        {"query": "SELECT Name, Code FROM Parent__x", "operation": "Readonly", "externalId": "Code"},
        {"query": "SELECT Name FROM Gone__x", "operation": "Upsert", "externalId": "Name"},
        {"query": "SELECT Name FROM Excluded__x", "operation": "Upsert", "externalId": "Name",
         "excluded": True},
    ], {
        "Widget__x.csv": "Name,Code,Kind,Family,CurrencyIsoCode,Derived,Required,Parent.Code\n"
                         "w1,C1,A,X,EUR,d,r,P1\n"
                         "w2,C2,Q,Y,USD,,,P1\n",
        "Gone__x.csv": "Name\ng\n",
    })


def run_fixture(known=None):
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        fixture(tmp)
        result = A.audit(SNAPSHOT, tmp, (), DIFF)
    return result


def by_check(result, check_name):
    return sorted((f["object"], f["field"]) for f in result["findings"] if f["check"] == check_name)


def test_findings():
    print("findings")
    r = run_fixture()
    check("unknown fields and traversals", by_check(r, "unknown-field"),
          [("Widget__x", "Ghost.Name"), ("Widget__x", "Missing")])
    check("restricted picklist value gates; CurrencyIsoCode is skipped", by_check(r, "picklist"),
          [("Widget__x", "Kind")])
    check("the bad value is named", [f["detail"].split(":")[1].split(" not")[0].strip()
                                     for f in r["findings"] if f["check"] == "picklist"], ["Q"])
    check("required: blank in a row, and missing entirely; boolean and defaulted skipped",
          by_check(r, "required"), [("Widget__x", "Required")])
    check("required detail counts the blank row",
          ["1 row(s)" in f["detail"] for f in r["findings"] if f["check"] == "required"], [True])
    with tempfile.TemporaryDirectory() as d2:
        t2 = pathlib.Path(d2)
        snap = {"M__x": {"fields": {"Code": field(nillable=False),
                                    "Tags": field("multipicklist", restricted=True, values=["A", "B"])}}}
        write_plan(t2, "qb/en-US/m", [{"query": "SELECT Code, Tags FROM M__x", "operation": "Upsert",
                                        "externalId": "Code"}], {"M__x.csv": "Code,Tags\nc,A; B\n"})
        check("multipicklist values are trimmed", by_check(A.audit(snap, t2), "picklist"), [])
    check("unrestricted picklist value is informational",
          [(u["field"], u["values"]) for u in r["info"]["undefined-value"]], [("Family", ["Y"])])
    check("dead columns are informational",
          r["info"]["dead-columns"], {"Widget__x": {"Derived": ["qb/en-US/qb-widgets"]}})
    check("object missing from the describe is listed, excluded isn't",
          r["info"]["object-missing"], {"Gone__x": ["qb/en-US/qb-widgets"]})
    check("unwritten fields, new marked, noise and custom left out",
          r["info"]["unwritten"]["Widget__x"],
          [{"field": "Added", "new": True}, {"field": "Defaulted", "new": False},
           {"field": "Flag", "new": False}, {"field": "Spare", "new": False}])
    check("release values only for fields a plan writes",
          r["info"]["release-values"], [{"object": "Widget__x", "field": "Kind", "added": ["B"]}])
    check("a Readonly object isn't audited", "Parent__x" in r["info"]["unwritten"], False)


def test_required_missing_column():
    print("required when the column is absent")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code FROM Widget__x", "operation": "Insert", "externalId": "Code"}],
            {"Widget__x.csv": "Name,Code\nn,c\n"})
        r = A.audit(SNAPSHOT, tmp)
        check("absent required column", by_check(r, "required"), [("Widget__x", "Required")])
        check("detail says it isn't loaded",
              ["doesn't load it" in f["detail"] for f in r["findings"] if f["check"] == "required"],
              [True])
        write_plan(tmp, "qb/en-US/q", [
            {"query": "SELECT Name, Code FROM Widget__x", "operation": "Update", "externalId": "Code"}],
            {"Widget__x.csv": "Name,Code\nn,c\n"})
        r = A.audit(SNAPSHOT, tmp, ["qb/en-US/q"])
        check("an Update-only plan isn't checked for required fields", by_check(r, "required"), [])


def test_deep_paths_and_external_id():
    print("relationship paths and externalId")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required, Parent.Code, Parent.Gone, Parent.Nope.Code, "
                      "Owner.Anything FROM Widget__x", "operation": "Upsert", "externalId": "Code;Nokey"},
        ], {"Widget__x.csv": "Name,Code,Required\nn,c,r\n"})
        r = A.audit(SNAPSHOT, tmp)
        got = sorted(f["field"] for f in r["findings"] if f["check"] == "unknown-field")
        check("a missing field on the parent, a missing second relationship and a missing key part",
              got, ["Nokey", "Parent.Gone", "Parent.Nope.Code"])
        check("a lookup whose target isn't in the snapshot is left unchecked",
              "Owner.Anything" in got, False)
        snap = {**SNAPSHOT, "Poly__x": {"fields": {
            "OwnerId": {**field("reference", rel="Owner"), "referenceTo": ["Parent__x", "Elsewhere"]}}}}
        write_plan(tmp, "qb/en-US/poly", [{"query": "SELECT Owner.Nope FROM Poly__x",
                                            "operation": "Update", "externalId": "Id"}],
                   {"Poly__x.csv": "Owner.Nope\nx\n"})
        check("a polymorphic lookup with a target outside the snapshot isn't flagged",
              [f for f in A.audit(snap, tmp, ["qb/en-US/poly"])["findings"]], [])
        check("the externalId finding says where it came from",
              any("its externalId names `Nokey`" in f["detail"] for f in r["findings"]), True)


def test_unsupported_filter_is_an_error():
    print("unsupported sourceRecordsFilter")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code", "sourceRecordsFilter": "Name IN ('a', 'b')"}],
            {"Widget__x.csv": "Name,Code,Required\nn,c,r\n"})
        try:
            A.audit(SNAPSHOT, tmp)
            raised = False
        except ValueError as exc:
            raised = "sourceRecordsFilter" in str(exc)
        check("raises instead of skipping the rows", raised, True)
        snap = tmp / "snap.json"
        snap.write_text(json.dumps({"objects": SNAPSHOT}), encoding="utf-8")
        check("main exits 2 from the filter, not the snapshot",
              A.main(["audit", "--snapshot", str(snap), "--root", str(tmp)]), 2)
        write_plan(tmp, "qb/en-US/q", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code", "sourceRecordsFilter": "Code IN ('z')"}],
            {"Widget__x.csv": "Name,Code,Required\nn,c,r\n"})
        try:
            A.audit(SNAPSHOT, tmp)
            both = ""
        except ValueError as exc:
            both = str(exc)
        check("every bad filter is reported together", "qb/en-US/p" in both and "qb/en-US/q" in both,
              True)


def test_required_each_creating_pass():
    print("required across creating passes (the later pass is keyed on Name;Code, the plan's key is Code)")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        # Pass 1 creates c1; pass 2 creates a disjoint row (c2) with Required blank, and patches c1.
        plan = tmp / "qb/en-US/p"
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        decl = {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
                "externalId": "Code"}
        (plan / "export.json").write_text(json.dumps({
            "useSeparatedCSVFiles": True,
            "objectSets": [{"objects": [decl]}, {"objects": [{**decl, "externalId": "Name;Code"}]}]}),
            encoding="utf-8")
        (plan / "Widget__x.csv").write_text("Name,Code,Required\nn1,c1,r\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required\nn1,c1,\nn2,c2,\nn3,c1,\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        req = [f for f in r["findings"] if f["check"] == "required"]
        check("the later pass counts the rows it creates (n2; n3 shares only Code, not the "
              "Name;Code key), not the patched one (n1)",
              [(f["field"], f["detail"]) for f in req],
              [("Required", "pass 2: Widget__x.Required is required on create and 2 row(s) "
                            "leave it blank")])


def test_required_later_pass_keyed_on_fewer_fields():
    print("required when the earlier pass is keyed on Name;Code (with a $$ column) and the later on Code")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        plan = tmp / "qb/en-US/p"
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        decl = {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert"}
        (plan / "export.json").write_text(json.dumps({
            "useSeparatedCSVFiles": True,
            "objectSets": [{"objects": [{**decl, "externalId": "Name;Code"}]},
                           {"objects": [{**decl, "externalId": "Code"}]}]}), encoding="utf-8")
        (plan / "Widget__x.csv").write_text(
            "$$Name$Code,Name,Code,Required\nn1;c1,n1,c1,r\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required\nother,c1,\nn2,c2,\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        req = [f for f in r["findings"] if f["check"] == "required"]
        check("only the row with a new Code is created blank; c1 is patched",
              [f["detail"] for f in req],
              ["pass 2: Widget__x.Required is required on create and 1 row(s) leave it blank"])


def test_required_repeated_key_in_a_pass():
    print("required counts a key once when it repeats within one Upsert pass")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code"}],
            {"Widget__x.csv": "Name,Code,Required\nn1,c1,\nn2,c1,\nn3,c2,\n"})
        r = A.audit(SNAPSHOT, tmp)
        req = [f for f in r["findings"] if f["check"] == "required"]
        check("c1 twice is one created record", [f["detail"] for f in req],
              ["pass 1: Widget__x.Required is required on create and 2 row(s) leave it blank"])


def test_required_three_passes_and_default_key():
    print("required across three passes, one keyed differently and one with no externalId")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        plan = tmp / "qb/en-US/p"
        for n in (2, 3):
            (plan / f"objectset_source/object-set-{n}").mkdir(parents=True)
        decl = {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert"}
        (plan / "export.json").write_text(json.dumps({
            "useSeparatedCSVFiles": True,
            "objectSets": [{"objects": [{**decl, "externalId": "Code"}]},
                           {"objects": [{**decl, "externalId": "Name;Code"}]},
                           {"objects": [decl]}]}), encoding="utf-8")
        head = "Name,Code,Required\n"
        (plan / "Widget__x.csv").write_text(head + "n1,c1,r\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            head + "n1,c1,\nn2,c2,\n", encoding="utf-8")
        (plan / "objectset_source/object-set-3/Widget__x.csv").write_text(
            head + "n1,c1,\nn2,c2,\nn3,c3,\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        req = sorted(f["detail"] for f in r["findings"] if f["check"] == "required")
        check("pass 2 creates c2; pass 3 (the plan's Code key) creates only c3", req, [
            "pass 2: Widget__x.Required is required on create and 1 row(s) leave it blank",
            "pass 3: Widget__x.Required is required on create and 1 row(s) leave it blank"])


def test_insert_after_upsert_is_checked():
    print("an Insert pass creates rows even when an earlier pass used the key")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        decl = {"query": "SELECT Name, Code, Required FROM Widget__x", "externalId": "Code"}
        plan = tmp / "qb/en-US/p"
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        (plan / "export.json").write_text(json.dumps({"useSeparatedCSVFiles": True, "objectSets": [
            {"objects": [{**decl, "operation": "Upsert"}]},
            {"objects": [{**decl, "operation": "Insert"}]}]}), encoding="utf-8")
        (plan / "Widget__x.csv").write_text("Name,Code,Required\nn1,c1,r\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required\nn1,c1,\n", encoding="utf-8")
        req = [(f["field"], f["detail"][:6]) for f in A.audit(SNAPSHOT, tmp)["findings"]
               if f["check"] == "required"]
        check("the Insert row with Required blank is flagged", req, [("Required", "pass 2")])


def test_system_fields_and_dead_columns():
    print("system fields are not exempt; dead columns aren't value-checked")
    snap = {"Widget__x": {"fields": {
        "Name": field(), "Code": field(nillable=False),
        "Role": field("picklist", createable=False, updateable=False, restricted=True, values=["A"])}}}
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Role, LastActivityDate FROM Widget__x",
             "operation": "Upsert", "externalId": "Code"}],
            {"Widget__x.csv": "Name,Code,Role,LastActivityDate\nn,c,Zed,\n"})
        r = A.audit(snap, tmp)
        check("LastActivityDate absent from the describe is unknown", by_check(r, "unknown-field"),
              [("Widget__x", "LastActivityDate")])
        check("a dead column's undefined value isn't a picklist finding", by_check(r, "picklist"), [])
        check("it is still listed as a dead column", r["info"]["dead-columns"],
              {"Widget__x": {"Role": ["qb/en-US/p"]}})


def test_classify():
    print("classify")
    r = run_fixture()
    known = {("qb/en-US/qb-widgets", "Widget__x", "picklist", "Kind"): "reason",
             ("qb/en-US/qb-widgets", "Widget__x", "required", "Gone"): "stale one"}
    new, kept, stale = A.classify(r, known)
    check("known finding kept", [f["field"] for f in kept], ["Kind"])
    check("others new", sorted(f["field"] for f in new), ["Ghost.Name", "Missing", "Required"])
    check("stale entry", stale, [("qb/en-US/qb-widgets", "Widget__x", "required", "Gone")])
    _, _, stale_other = A.classify(r, {("qb/en-US/elsewhere", "Widget__x", "picklist", "Kind"): "x"})
    check("an entry for a plan not audited isn't stale", stale_other, [])
    r_missing = dict(r, info={**r["info"], "object-missing":
                              {"Widget__x": ["qb/en-US/qb-widgets"]}})
    _, _, stale_missing = A.classify(r_missing, {("qb/en-US/qb-widgets", "Widget__x", "required",
                                                  "Gone"): "x"})
    check("an entry whose object the describe lacks isn't stale", stale_missing, [])
    md = A.render_markdown(r, "test", known)
    check("report shows the reason", "| reason |" in md, True)
    check("report lists the stale entry", "no longer found; remove it" in md, True)


def test_merge():
    print("merge_snapshots")
    base = {"O": {"fields": {"P": field("picklist", values=["A"]), "F": field(createable=False)}}}
    extra = {"O": {"fields": {"P": field("picklist", values=["B"]), "F": field(), "G": field()}},
             "N": {"fields": {"X": field()}}}
    m = A.merge_snapshots(base, extra)
    check("values unioned", m["O"]["fields"]["P"]["values"], ["A", "B"])
    check("base attributes win", m["O"]["fields"]["F"]["createable"], False)
    check("new field and object added", (sorted(m["O"]["fields"]), sorted(m)), (["F", "G", "P"], ["N", "O"]))
    check("base not mutated", base["O"]["fields"]["P"]["values"], ["A"])
    m = A.merge_snapshots({"O": {"fields": {"C": field("picklist", restricted=True, values=[])}}},
                          {"O": {"fields": {"C": {**field("picklist", restricted=True, values=[]),
                                                  "orgValues": True}}}})
    check("orgValues carries over from the merged org", m["O"]["fields"]["C"].get("orgValues"), True)


def test_compact_describe():
    print("compact_describe")
    d = A.compact_describe({"fields": [
        {"name": "K", "type": "picklist", "createable": True, "picklistValues": [
            {"value": "b", "active": True}, {"value": "a", "active": True}, {"value": "z", "active": False}]},
        {"name": "S", "type": "string", "label": "dropped"}]})
    check("active values sorted", d["fields"]["K"]["values"], ["a", "b"])
    check("only audit keys kept", sorted(d["fields"]["S"]), sorted(A.DESCRIBE_KEYS))
    d = A.compact_describe({"fields": [
        {"name": "Ctx", "type": "picklist", "restrictedPicklist": True, "picklistValues": [
            {"value": "11OWt000000L45RMAS", "active": True}, {"value": "0zMWt0000001IKf", "active": True},
            {"value": "AssetContext__stdctx", "active": True}]},
        {"name": "Obj", "type": "picklist", "restrictedPicklist": True, "picklistValues": [
            {"value": "Pricebook2Share", "active": True}, {"value": "S2XTransactionLock", "active": True},
            {"value": "Account", "active": True}]}]})
    check("record Ids (18 with checksum, 15 with a zero run) dropped, names kept",
          (d["fields"]["Ctx"]["values"], d["fields"]["Ctx"].get("orgValues")),
          (["AssetContext__stdctx"], True))
    check("object names that look like Ids are kept and the field stays checked",
          (d["fields"]["Obj"]["values"], d["fields"]["Obj"].get("orgValues")),
          (["Account", "Pricebook2Share", "S2XTransactionLock"], None))
    check("an 18-character value with a wrong checksum isn't an Id",
          A._is_record_id("11OWt000000L45RAAA"), False)
    snap = {"W__x": {"fields": {"Code": field(nillable=False), "Ctx": {**field("picklist", restricted=True,
                                                                            values=[]), "orgValues": True}}}}
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = pathlib.Path(tmpd)
        write_plan(tmp, "qb/en-US/p", [{"query": "SELECT Code, Ctx FROM W__x", "operation": "Upsert",
                                         "externalId": "Code"}], {"W__x.csv": "Code,Ctx\nc,anything\n"})
        check("an org-values picklist isn't value-checked", by_check(A.audit(snap, tmp), "picklist"), [])


def test_main():
    print("main")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code"}], {"Widget__x.csv": "Name,Code,Required\nn,c,r\n"})
        snap = tmp / "snap.json"
        snap.write_text(json.dumps({"objects": SNAPSHOT}), encoding="utf-8")
        out = tmp / "r.md"
        check("clean snapshot exits 0",
              A.main(["audit", "--snapshot", str(snap), "--root", str(tmp), "--out", str(out)]), 0)
        check("report written", out.read_text().startswith("# Data-plan release audit"), True)
        (tmp / "qb/en-US/p/Widget__x.csv").write_text("Name,Code,Required\nn,c,\n", encoding="utf-8")
        check("a finding exits 1",
              A.main(["audit", "--snapshot", str(snap), "--root", str(tmp), "--out", str(out)]), 1)
        check("a missing snapshot exits 2",
              A.main(["audit", "--snapshot", str(tmp / "nope.json"), "--root", str(tmp)]), 2)


def test_committed_snapshot():
    print("committed snapshot (the pr_gate run)")
    release = A.active_release()
    path = A.default_snapshot(release)
    check(f"{path.name} exists for the active release", path.exists(), True)


for t in (test_findings, test_required_missing_column, test_deep_paths_and_external_id,
          test_unsupported_filter_is_an_error, test_required_each_creating_pass,
          test_required_later_pass_keyed_on_fewer_fields, test_required_repeated_key_in_a_pass,
          test_required_three_passes_and_default_key, test_insert_after_upsert_is_checked,
          test_system_fields_and_dead_columns, test_classify, test_merge,
          test_compact_describe, test_main, test_committed_snapshot):
    t()
print(f"\n{len(_failures)} failure(s)")
sys.exit(1 if _failures else 0)
