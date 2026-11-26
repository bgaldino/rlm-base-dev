#!/usr/bin/env python3
"""
Invariant: manage_expression_sets list/query honour --status, --interface_source_type and
--process_type, and every value that reaches SOQL is escaped or whitelisted.

    python tests/test_manage_expression_sets_filters.py

Stdlib only: `requests` is replaced by a fake Tooling API.

Why this file exists (pack 457, measured live on 264)
-----------------------------------------------------
ExpressionSetDefinition has neither Status nor InterfaceSourceType nor ProcessType as a field.
Status lives on ExpressionSetDefinitionVersion (semi-join; the Tooling API accepts it and it
filters: on a 264 scratch org, 12 sets listed unfiltered, 11 Active, 1 Draft, 2026-11-26); the
other two exist only in the
set's Metadata, which the Tooling API returns one record at a time. The task used to ignore
status and warn-and-ignore the other two. list_versions also selected Rank, StartDate, Label and
Description, none of which exist on ExpressionSetDefinitionVersion, so it failed on every org.
"""
import os
import sys
import tempfile
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body
        self.text = str(body)
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._body


SETS = {
    "9QA1": ("Pricing_One", "PricingProcedure", "DefaultPricing"),
    "9QA2": ("Rating_One", "RatingProcedure", "DefaultRating"),
    "9QA3": ("Pricing_Two", "PricingProcedure", "DefaultPricing"),
}


class FakeTooling(types.ModuleType):
    def __init__(self):
        super().__init__("requests")
        self.queries = []
        self.gets = []

    def get(self, url, headers=None, params=None):
        if params:
            self.queries.append(params["q"])
            if "FROM ExpressionSetDefinitionVersion" in params["q"]:
                return FakeResponse(200, {"records": [{"Id": "v", "FullName": "Pricing_One_V1", "VersionNumber": 1,
                                                       "Status": "Active", "MasterLabel": "x"}], "done": True})
            return FakeResponse(200, {"records": [
                {"attributes": {}, "Id": i, "DeveloperName": n, "MasterLabel": n,
                 "LastModifiedDate": "2026-11-25T00:00:00.000+0000"} for i, (n, _, _) in SETS.items()],
                "done": True})
        self.gets.append(url)
        set_id = url.rsplit("/", 1)[1]
        _, iface, proc = SETS[set_id]
        return FakeResponse(200, {"Metadata": {"interfaceSourceType": iface, "processType": proc}})


from tasks.rlm_manage_expression_sets import ManageExpressionSets  # noqa: E402

LOGS = []
LAST = {}


def run(options):
    fake = FakeTooling()
    saved = sys.modules.get("requests")
    sys.modules["requests"] = fake
    LOGS.clear()
    task = ManageExpressionSets.__new__(ManageExpressionSets)
    task.org_config = types.SimpleNamespace(access_token="t", instance_url="https://example.my.salesforce.com")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
    task.options = options
    LAST["task"] = task
    log = lambda msg, *a, **k: LOGS.append(msg)  # noqa: E731
    task.logger = types.SimpleNamespace(info=log, error=log, warning=log, debug=lambda *a, **k: None)
    try:
        task._run_task()
        return fake, None
    except Exception as exc:
        return fake, exc
    finally:
        if saved is None:
            sys.modules.pop("requests", None)
        else:
            sys.modules["requests"] = saved


JOINED = "\n".join


def first_query(fake):
    """The first SOQL sent; with none sent, record a FAIL here (so a `not in` check cannot pass vacuously) and return ""."""
    if not fake.queries:
        if not getattr(fake, "no_query_reported", False):  # one FAIL per run, however often it is called
            fake.no_query_reported = True
            check("a query was sent", False, "no SOQL was sent")
        return ""
    return fake.queries[0]

print("status filters in SOQL through the versions (it is not a field of the set)")
fake, err = run({"operation": "list", "status": "Draft"})
check("semi-join on ExpressionSetDefinitionVersion.Status",
      "Id IN (SELECT ExpressionSetDefinitionId FROM ExpressionSetDefinitionVersion WHERE Status = 'Draft')"
      in first_query(fake), first_query(fake))
check("no metadata reads when only status is set", not fake.gets, repr(fake.gets))

print("interface_source_type filters on each set's metadata")
fake, err = run({"operation": "query", "interface_source_type": "RatingProcedure"})
check("no error", err is None, repr(err))
check("one metadata read per candidate set", len(fake.gets) == 3, repr(fake.gets))
check("only the rating set is listed", "Query returned 1 expression set(s)." in JOINED(LOGS), JOINED(LOGS))

print("process_type and interface_source_type combine, and the limit applies after filtering")
fake, err = run({"operation": "list", "interface_source_type": "PricingProcedure",
                 "process_type": "DefaultPricing", "limit": "1"})
check("the SOQL carries no LIMIT (it would cut before the filter)", "LIMIT" not in first_query(fake), first_query(fake))
check("one set returned", "Query returned 1 expression set(s)." in JOINED(LOGS), JOINED(LOGS))
check("metadata reads stop once the limit is met", len(fake.gets) == 1, repr(fake.gets))
check("the matched columns are printed", "InterfaceSourceType" in JOINED(LOGS) and "Pricing_One" in JOINED(LOGS),
      JOINED(LOGS))

print("with no metadata filter the limit stays in SOQL")
fake, _ = run({"operation": "list", "limit": "2"})
check("LIMIT 2", first_query(fake).endswith("LIMIT 2"), first_query(fake))

print("developer_names splits on commas and every value is escaped")
fake, _ = run({"operation": "list", "developer_names": "A, B'C", "status": "x'y"})
q = first_query(fake)
check("names split and escaped", "DeveloperName IN ('A', 'B\\'C')" in q, q)
check("status escaped", "Status = 'x\\'y'" in q, q)

print("sort_by, sort_order and limit are whitelisted")
for opts, needle in (({"sort_by": "Id; x"}, "sort_by must be"),
                     ({"sort_order": "Desc; x"}, "sort_order must be"),
                     ({"limit": "1 OFFSET 2"}, "limit must be")):
    _, err = run(dict({"operation": "list"}, **opts))
    check(f"rejects {list(opts)[0]}", err is not None and needle in str(err), repr(err))
fake, _ = run({"operation": "list", "sort_by": "developer_name", "sort_order": "asc"})
check("DeveloperName Asc", first_query(fake).endswith("ORDER BY DeveloperName Asc"), first_query(fake))
fake, _ = run({"operation": "list", "sort_order": " asc "})
check("sort_order is trimmed", first_query(fake).endswith("Asc"), first_query(fake))
fake, _ = run({"operation": "list", "sort_by": " "})
check("blank sort_by orders by LastModifiedDate", "ORDER BY LastModifiedDate" in first_query(fake), first_query(fake))
fake, err = run({"operation": "list", "limit": " "})
check("blank limit means no LIMIT", err is None and "LIMIT" not in first_query(fake), repr((err, fake.queries)))
fake, _ = run({"operation": "list", "limit": " 3 "})
check("padded limit is trimmed", first_query(fake).endswith("LIMIT 3"), first_query(fake))
_, err = run({"operation": "list", "limit": 0})
check("an int 0 limit is rejected, not dropped", err is not None and "limit must be" in str(err), repr(err))
fake, err = run({"operation": " list "})
check("padded operation runs", err is None and len(fake.queries) == 1, repr((err, fake.queries)))
fake, err = run({"operation": "list", "developer_names": "  "})
check("whitespace-only developer_names means not set", err is None and "DeveloperName IN" not in first_query(fake),
      repr((err, fake.queries)))
_, err = run({"operation": "list", "sort_by": 0})
check("an int 0 sort_by is rejected, not defaulted", err is not None and "sort_by must be" in str(err), repr(err))
fake, _ = run({"operation": "list", "developer_names": ["A", "B"]})
check("a list developer_names still works", "DeveloperName IN ('A', 'B')" in first_query(fake), first_query(fake))


def parsed_versions(options):
    """_parse_version_names_option's result, or the exception it raised."""
    task = ManageExpressionSets.__new__(ManageExpressionSets)
    task.options = options
    LOGS.clear()
    task.logger = types.SimpleNamespace(info=LOGS.append, warning=LOGS.append)
    try:
        return task._parse_version_names_option()
    except Exception as exc:
        return exc


check("version_full_names: string, list, tuple and comma items parse alike",
      all(parsed_versions({"version_full_names": v}) == ["A_V1", "B_V1"]
          for v in ("A_V1, B_V1", ["A_V1", "B_V1"], ("A_V1", "B_V1"), ["A_V1,B_V1"])))

with tempfile.TemporaryDirectory() as tmp:
    meta_dir = Path(tmp) / "force-app/main/default/expressionSetDefinition"
    meta_dir.mkdir(parents=True)
    (meta_dir / "X.expressionSetDefinition-meta.xml").write_text(
        '<ExpressionSetDefinition xmlns="http://soap.sforce.com/2006/04/metadata">'
        "<versions><fullName>X_V1</fullName></versions></ExpressionSetDefinition>")
    for blank in (None, "", "  ", []):
        got = parsed_versions({"version_full_names": blank, "metadata_path": str(meta_dir)})
        check(f"version_full_names {blank!r} falls through to discovery and names the fallback",
              got == ["X_V1"] and any("not set: using all 1" in m for m in LOGS), repr((got, LOGS)))
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        for blank in (None, "", " "):
            got = parsed_versions({"metadata_path": blank})
            check(f"metadata_path {blank!r} means the default path", got == ["X_V1"], repr(got))
    finally:
        os.chdir(cwd)
    got = parsed_versions({"metadata_path": [str(meta_dir)]})
    check("a list metadata_path is refused", "single value" in str(got), repr(got))

for op in ("activate_version", "deactivate_version"):
    _, err = run({"operation": op, "version_full_name": "  "})
    check(f"{op}: a blank version_full_name is missing", err is not None and "is required" in str(err), repr(err))
    _, err = run({"operation": op, "version_full_name": ["A_V1"]})
    check(f"{op}: a list version_full_name is refused", err is not None and "single value" in str(err), repr(err))
for opt in ("status", "process_type", "interface_source_type"):
    _, err = run({"operation": "list", opt: ["Active"]})
    check(f"a list {opt} is refused", err is not None and "single value" in str(err), repr(err))
fake, _ = run({"operation": "list", "sort_by": " developer_name "})
check("padded sort_by is trimmed", "ORDER BY DeveloperName" in first_query(fake), first_query(fake))

print("list_versions selects only fields that exist on the version object")
fake, err = run({"operation": "list_versions", "developer_names": "Pricing_One"})
vq = next((q for q in fake.queries if "FROM ExpressionSetDefinitionVersion" in q), "")
check("a version query was sent", bool(vq), repr(fake.queries))
check("no Rank / StartDate / Label / Description", not any(f in vq for f in ("Rank", "StartDate", ", Label", "Description")), vq)
check("selects VersionNumber and Status", "VersionNumber" in vq and "Status" in vq, vq)
check("prints the version row", "Pricing_One_V1" in JOINED(LOGS), JOINED(LOGS))

print("query returns its rows; operation is stripped and cased")
for op in ("query", "  QUERY ", "Query\n"):
    fake, err = run({"operation": op})
    check(f"operation {op!r} runs query", err is None and any("FROM ExpressionSetDefinition" in q for q in fake.queries), repr(err))
fake, err = run({"operation": " query ", "limit": "2"})
rv = getattr(LAST["task"], "return_values", None)
check("query sets return_values['expression_sets'] with the rows",
      err is None and isinstance(rv, dict) and [r["DeveloperName"] for r in rv.get("expression_sets", [])] == ["Pricing_One", "Rating_One", "Pricing_Two"],
      repr(rv))
check("rows carry no 'attributes'", all("attributes" not in r for r in rv["expression_sets"]), repr(rv))
check("query still logs the count", "Query returned 3 expression set(s)." in JOINED(LOGS), JOINED(LOGS))
_, err = run({"operation": None})
check("operation None is refused as unknown", err is not None and "Unknown operation" in str(err), repr(err))
_, err = run({"operation": "   "})
check("blank operation is refused as unknown", err is not None and "Unknown operation" in str(err), repr(err))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")
