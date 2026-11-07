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


def current_meta():
    return {"release": A.active_release(), "api_version": A.active_api_version()}


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
        snap.write_text(json.dumps({"metadata": current_meta(), "objects": SNAPSHOT}), encoding="utf-8")
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
        check("a key repeated after a rejected row is checked again (n1, n2 on c1, n3 on c2)",
              [f["detail"] for f in req],
              ["pass 1: Widget__x.Required is required on create and 3 row(s) leave it blank"])
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code"}],
            {"Widget__x.csv": "Name,Code,Required\nn1,c1,\nn2,c1,r\nn3,c1,\n"})
        req = [f["detail"] for f in A.audit(SNAPSHOT, tmp)["findings"] if f["check"] == "required"]
        check("c1's first row is rejected, the second creates it, the third patches it", req,
              ["pass 1: Widget__x.Required is required on create and 1 row(s) leave it blank"])


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
        check("pass 2 creates c2 (rejected: blank Required); pass 3 (the plan's Code key) re-checks "
              "c2 and checks c3, but c1 from pass 1 persisted", req, [
            "pass 2: Widget__x.Required is required on create and 1 row(s) leave it blank",
            "pass 3: Widget__x.Required is required on create and 2 row(s) leave it blank"])


def test_required_unselected_column_is_not_a_key():
    print("required: an earlier pass's unselected CSV column can't match a later pass's key")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        plan = tmp / "qb/en-US/p"
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        (plan / "export.json").write_text(json.dumps({
            "useSeparatedCSVFiles": True,
            "objectSets": [
                {"objects": [{"query": "SELECT Name, Code, Required FROM Widget__x",
                              "operation": "Upsert", "externalId": "Code"}]},
                {"objects": [{"query": "SELECT Name, Code, Required FROM Widget__x",
                              "operation": "Upsert", "externalId": "Code"}]}]}), encoding="utf-8")
        (plan / "Widget__x.csv").write_text("Name,Code,Required,Family\nn1,c1,r,f1\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required\nn1,c1,\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        check("the matching key is still the selected Code", [f for f in r["findings"]
              if f["check"] == "required"], [])
        # Key on the unselected column in pass 2: pass 1 never wrote Family.
        (plan / "export.json").write_text(json.dumps({
            "useSeparatedCSVFiles": True,
            "objectSets": [
                {"objects": [{"query": "SELECT Name, Code, Required FROM Widget__x",
                              "operation": "Upsert", "externalId": "Code"}]},
                {"objects": [{"query": "SELECT Name, Code, Required, Family FROM Widget__x",
                              "operation": "Upsert", "externalId": "Family"}]}]}), encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required,Family\nn2,c2,,f1\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        check("pass 2's f1 isn't a record pass 1 wrote, so its blank Required counts",
              [f["detail"] for f in r["findings"] if f["check"] == "required"],
              ["pass 2: Widget__x.Required is required on create and 1 row(s) leave it blank"])


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


def test_csv_lookup_paths_and_api_version():
    print("written CSV lookup paths are checked; describe uses the manifest's API version")
    snap = {"Widget__x": {"fields": {"Name": field(), "ParentId": {**field("reference", rel="Parent"),
                                                              "referenceTo": ["Parent__x"]}}},
            "Parent__x": {"fields": {"Name": field()}}}
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, ParentId FROM Widget__x", "operation": "Upsert",
             "externalId": "Name"}],
            {"Widget__x.csv": "$$Name,Name,Parent.Code,Parent.$$Name$Gone\nn,n,c,p;g\n"})
        r = A.audit(snap, tmp)
        check("a CSV path the parent lacks, plain or composite, is unknown",
              sorted(f["field"] for f in r["findings"] if f["check"] == "unknown-field"),
              ["Parent.Code", "Parent.Gone"])
    tsnap = {"Task__x": {"fields": {"Name": field(), "WhoId": {**field("reference", rel="Who", nillable=False),
                                                                "referenceTo": ["Contact__x", "Lead__x"]}}},
             "Contact__x": {"fields": {"Name": field()}},
             "Lead__x": {"fields": {"Name": field(), "LeadOnly__c": field()}}}
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/t", [
            {"query": "SELECT Name, WhoId FROM Task__x", "operation": "Upsert", "externalId": "Name"}],
            {"Task__x.csv": "$$Name,Name,Who$Contact__x.LeadOnly__c\nn,n,x\n"})
        r = A.audit(tsnap, tmp)
        check("a typed CSV header is validated against its target, and counts as writing the lookup",
              ([f["field"] for f in r["findings"] if f["check"] == "unknown-field"],
               [f["field"] for f in r["findings"] if f["check"] == "required"]),
              (["Who$Contact__x.LeadOnly__c"], []))
    with tempfile.TemporaryDirectory() as d:
        manifest = pathlib.Path(d) / "m.yml"
        manifest.write_text('api_version_active: "v70.0"\n', encoding="utf-8")
        check("the active API version", A.active_api_version(manifest), "70.0")
    poly = {"Task__x": {"fields": {"WhoId": {**field("reference", rel="Who"),
                                              "referenceTo": ["Contact__x", "Lead__x"]}}},
            "Contact__x": {"fields": {"Name": field("string")}},
            "Lead__x": {"fields": {"Name": field("string"), "LeadOnly__c": field("string")}}}
    problem = lambda path: A._path_problem("Task__x", path.split("."), poly)
    check("an untyped polymorphic path resolves on any target", problem("Who.LeadOnly__c"), None)
    check("a typed path is checked against its own target only",
          problem("Who$Contact__x.LeadOnly__c") is not None, True)
    check("a typed path that resolves on its target", problem("Who$Lead__x.LeadOnly__c"), None)
    check("a type matches case-insensitively", problem("Who$lead__x.LeadOnly__c"), None)
    check("a type the lookup doesn't reference is a problem", problem("Who$Account.Name") is not None, True)
    check("a type outside the snapshot is left unchecked",
          A._path_problem("Task__x", ["Who$Elsewhere", "Name"],
                          {**poly, "Task__x": {"fields": {"WhoId": {**field("reference", rel="Who"),
                                               "referenceTo": ["Elsewhere"]}}}}), None)
    check("a type on the last segment names the field", problem("WhoId$Contact__x"), None)
    check("a type on the last segment must be one the field references",
          problem("WhoId$Account") is not None, True)
    check("a typed plain header is its field",
          A._field_of("WhoId$Contact__x", poly["Task__x"]["fields"]), "WhoId")
    check("a typed header counts as writing its lookup", A._field_of("Who$Contact__x.Name", poly["Task__x"]["fields"]), "WhoId")


def test_classify():
    print("classify")
    r = run_fixture()
    known = {("qb/en-US/qb-widgets", "Widget__x", "picklist", "Kind"): "reason",
             ("qb/en-US/qb-widgets", "Widget__x", "required", "Gone"): "stale one"}
    kind = next(f for f in r["findings"] if f["field"] == "Kind")
    kind_key = ("qb/en-US/qb-widgets", "Widget__x", "picklist", "Kind")
    new, kept, stale = A.classify(r, known, {kind_key: frozenset(kind["values"])})
    check("known finding kept", [f["field"] for f in kept], ["Kind"])
    new_v, kept_v, stale_v = A.classify(r, known, {kind_key: frozenset({"Other"})})
    check("a picklist value the entry didn't triage is a new finding",
          ("Kind" in [f["field"] for f in new_v], kept_v), (True, []))
    check("and the entry isn't stale while the field still has a finding",
          [k for k in stale_v if k[3] == "Kind"], [])
    check("no triaged values means no value is known", [f["field"] for f in A.classify(r, known)[1]], [])
    check("others new", sorted(f["field"] for f in new), ["", "Ghost.Name", "Missing", "Required"])
    check("an object the describe lacks is a gating finding, not a silent pass",
          [(f["object"], f["check"]) for f in new if f["check"] == "object-missing"],
          [("Gone__x", "object-missing")])
    gone = ("qb/en-US/qb-widgets", "Gone__x", "object-missing", "")
    new_g, kept_g, stale_g = A.classify(r, {**known, gone: "feature gated"}, {})
    check("triaged, it is known; and stays so while the object is missing",
          ([f["object"] for f in kept_g if f["check"] == "object-missing"], [k for k in stale_g if k == gone]),
          (["Gone__x"], []))
    check("a triaged missing object that appears is stale",
          [k for k in A.classify({**r, "findings": [f for f in r["findings"] if f["check"] != "object-missing"],
                                  "info": {**r["info"], "object-missing": {}}},
                                 {**known, gone: "feature gated"}, {})[2] if k == gone], [gone])
    check("stale entry", stale, [("qb/en-US/qb-widgets", "Widget__x", "required", "Gone")])
    _, _, stale_other = A.classify(r, {("qb/en-US/elsewhere", "Widget__x", "picklist", "Kind"): "x"})
    check("an entry for a plan not audited isn't stale", stale_other, [])
    r_missing = dict(r, info={**r["info"], "object-missing":
                              {"Widget__x": ["qb/en-US/qb-widgets"]}})
    _, _, stale_missing = A.classify(r_missing, {("qb/en-US/qb-widgets", "Widget__x", "required",
                                                  "Gone"): "x"})
    check("an entry whose object the describe lacks isn't stale", stale_missing, [])
    check("a triaged value that is gone makes the entry stale",
          A.classify(r, known, {kind_key: frozenset(kind["values"]) | {"Gone"}})[2],
          [kind_key, ("qb/en-US/qb-widgets", "Widget__x", "required", "Gone")])
    check("TRIAGED_VALUES has no entry without a KNOWN_FINDINGS one",
          [k for k in A.TRIAGED_VALUES if k not in A.KNOWN_FINDINGS], [])
    check("every committed picklist entry lists its triaged values",
          [k for k in A.KNOWN_FINDINGS if k[2] == "picklist" and k not in A.TRIAGED_VALUES], [])
    md = A.render_markdown(r, "test", known, {kind_key: frozenset(kind["values"])})
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


def _two_pass_plan(tmp, second_extra):
    plan = tmp / "qb/en-US/p"
    (plan / "objectset_source/object-set-2").mkdir(parents=True)
    (plan / "export.json").write_text(json.dumps({"useSeparatedCSVFiles": True, "objectSets": [
        {"objects": [{"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
                      "externalId": "Code"}]},
        {"objects": [{"query": "SELECT Name, Code FROM Widget__x", "operation": "Upsert",
                      "externalId": "Code", **second_extra}]}]}), encoding="utf-8")
    (plan / "Widget__x.csv").write_text("Name,Code,Required\nn1,c1,r\n", encoding="utf-8")
    (plan / "objectset_source/object-set-2/Widget__x.csv").write_text("Name,Code\nn1,c1\n", encoding="utf-8")


def _f(result, name):
    return [f["field"] for f in result["findings"] if f["check"] == name]


def test_rejected_rows_are_not_persisted():
    print("a row an earlier pass would be rejected for a required field isn't patched by a later pass")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        plan = tmp / "qb/en-US/p"
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        decl = {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
                "externalId": "Code"}
        (plan / "export.json").write_text(json.dumps({"useSeparatedCSVFiles": True, "objectSets": [
            {"objects": [decl]}, {"objects": [decl]}]}), encoding="utf-8")
        (plan / "Widget__x.csv").write_text("Name,Code,Required\nn1,c1,\nn2,c2,r\n", encoding="utf-8")
        (plan / "objectset_source/object-set-2/Widget__x.csv").write_text(
            "Name,Code,Required\nn1,c1,\nn2,c2,\n", encoding="utf-8")
        found = sorted(f["detail"] for f in A.audit(SNAPSHOT, tmp)["findings"] if f["check"] == "required")
        check("pass 2 re-checks c1 (rejected in pass 1) but not c2 (persisted)", found, [
            "pass 1: Widget__x.Required is required on create and 1 row(s) leave it blank",
            "pass 2: Widget__x.Required is required on create and 1 row(s) leave it blank"])


def test_delete_old_data_and_exclusions():
    print("deleteOldData clears earlier rows; every written column is validated; excludedFields")
    with tempfile.TemporaryDirectory() as d:
        _two_pass_plan(pathlib.Path(d), {})
        check("a later Upsert on a row an earlier pass created only patches it",
              _f(A.audit(SNAPSHOT, pathlib.Path(d)), "required"), [])
    with tempfile.TemporaryDirectory() as d:
        _two_pass_plan(pathlib.Path(d), {"deleteOldData": True})
        check("deleteOldData removed that row, so the Upsert creates it and must load Required",
              _f(A.audit(SNAPSHOT, pathlib.Path(d)), "required"), ["Required"])
    with tempfile.TemporaryDirectory() as d:
        _two_pass_plan(pathlib.Path(d), {"deleteOldData": []})
        check("a JS-truthy deleteOldData (an empty list) deletes too",
              _f(A.audit(SNAPSHOT, pathlib.Path(d)), "required"), ["Required"])
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [{"query": "SELECT all FROM Widget__x", "operation": "Upsert",
                                         "externalId": "Code"}],
                   {"Widget__x.csv": "Name,Code,Required,Gone\nn,c,r,x\n"})
        check("a plain CSV column that SELECT all writes is checked against the describe",
              _f(A.audit(SNAPSHOT, tmp), "unknown-field"), ["Gone"])
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [{"query": "SELECT all FROM Widget__x", "operation": "Upsert",
                                         "externalId": "Code", "excludedFields": ["Required", "Kind"]}],
                   {"Widget__x.csv": "Name,Code,Required,Kind\nn,c,r,Z\n"})
        r = A.audit(SNAPSHOT, tmp)
        check("an excluded field isn't loaded, so a required one is missing and a bad value never lands",
              (_f(r, "required"), _f(r, "picklist")), (["Required"], []))


def test_object_missing_once_per_plan_object():
    print("object-missing is one finding per plan and object")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        plan = write_plan(tmp, "qb/en-US/p", [], {"Gone__x.csv": "Name\ng\n"})
        decl = {"query": "SELECT Name FROM Gone__x", "operation": "Upsert", "externalId": "Name"}
        (plan / "objectset_source/object-set-2").mkdir(parents=True)
        (plan / "export.json").write_text(json.dumps({"useSeparatedCSVFiles": True,
                                                      "objectSets": [{"objects": [decl]}, {"objects": [decl]}]}),
                                          encoding="utf-8")
        (plan / "objectset_source/object-set-2/Gone__x.csv").write_text("Name\ng\n", encoding="utf-8")
        r = A.audit(SNAPSHOT, tmp)
        check("two passes over a missing object give one finding",
              [(f["object"], f["check"]) for f in r["findings"] if f["check"] == "object-missing"],
              [("Gone__x", "object-missing")])


def test_main():
    print("main")
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        write_plan(tmp, "qb/en-US/p", [
            {"query": "SELECT Name, Code, Required FROM Widget__x", "operation": "Upsert",
             "externalId": "Code"}], {"Widget__x.csv": "Name,Code,Required\nn,c,r\n"})
        snap = tmp / "snap.json"
        snap.write_text(json.dumps({"metadata": current_meta(), "objects": SNAPSHOT}), encoding="utf-8")
        out = tmp / "r.md"
        check("clean snapshot exits 0",
              A.main(["audit", "--snapshot", str(snap), "--root", str(tmp), "--out", str(out)]), 0)
        check("report written", out.read_text().startswith("# Data-plan release audit"), True)
        (tmp / "qb/en-US/p/Widget__x.csv").write_text("Name,Code,Required\nn,c,\n", encoding="utf-8")
        check("a finding exits 1",
              A.main(["audit", "--snapshot", str(snap), "--root", str(tmp), "--out", str(out)]), 1)
        for label, meta in (("another release", {**current_meta(), "release": "260"}),
                            ("another API version", {**current_meta(), "api_version": "60.0"}),
                            ("no api_version", {"release": A.active_release()}),
                            ("no metadata", None)):
            stale = tmp / "stale.json"
            stale.write_text(json.dumps({**({"metadata": meta} if meta else {}), "objects": SNAPSHOT}),
                             encoding="utf-8")
            check(f"a snapshot with {label} exits 2",
                  A.main(["audit", "--snapshot", str(stale), "--root", str(tmp)]), 2)
        real_describe = A.describe_org

        def no_org(*a, **k):
            raise AssertionError("the merge base must be refused before the org is described")
        A.describe_org = no_org
        try:
            check("a merge base without release metadata is refused before any org call",
                  A.main(["snapshot", "--target-org", "none", "--merge", str(stale),
                          "--out", str(tmp / "o.json"), "--root", str(tmp)]), 2)
        finally:
            A.describe_org = real_describe
        check("a missing snapshot exits 2",
              A.main(["audit", "--snapshot", str(tmp / "nope.json"), "--root", str(tmp)]), 2)


def test_committed_snapshot():
    print("committed snapshot (the pr_gate run)")
    release = A.active_release()
    path = A.default_snapshot(release)
    check(f"{path.name} exists for the active release", path.exists(), True)
    meta = json.loads(path.read_text(encoding="utf-8")).get("metadata") or {}
    check("it records the active release and API version",
          {k: meta.get(k) for k in current_meta()}, current_meta())


for t in (test_findings, test_required_missing_column, test_deep_paths_and_external_id,
          test_unsupported_filter_is_an_error, test_required_each_creating_pass,
          test_required_later_pass_keyed_on_fewer_fields, test_required_repeated_key_in_a_pass,
          test_required_three_passes_and_default_key, test_required_unselected_column_is_not_a_key,
          test_csv_lookup_paths_and_api_version, test_insert_after_upsert_is_checked, test_delete_old_data_and_exclusions, test_object_missing_once_per_plan_object, test_rejected_rows_are_not_persisted,
          test_system_fields_and_dead_columns, test_classify, test_merge,
          test_compact_describe, test_main, test_committed_snapshot):
    t()
print(f"\n{len(_failures)} failure(s)")
sys.exit(1 if _failures else 0)
