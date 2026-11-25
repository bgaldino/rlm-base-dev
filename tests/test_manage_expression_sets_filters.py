#!/usr/bin/env python3
"""
Invariant: manage_expression_sets list/query honour --status, --interface_source_type and
--process_type, and every value that reaches SOQL is escaped or whitelisted.

    python tests/test_manage_expression_sets_filters.py

Stdlib only: `requests` is replaced by a fake Tooling API.

Why this file exists (pack 457, measured live on 264)
-----------------------------------------------------
ExpressionSetDefinition has neither Status nor InterfaceSourceType nor ProcessType as a field.
Status lives on ExpressionSetDefinitionVersion (semi-join); the other two exist only in the
set's Metadata, which the Tooling API returns one record at a time. The task used to ignore
status and warn-and-ignore the other two. list_versions also selected Rank, StartDate, Label and
Description, none of which exist on ExpressionSetDefinitionVersion, so it failed on every org.
"""
import sys
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


def run(options):
    fake = FakeTooling()
    sys.modules["requests"] = fake
    LOGS.clear()
    task = ManageExpressionSets.__new__(ManageExpressionSets)
    task.org_config = types.SimpleNamespace(access_token="t", instance_url="https://example.my.salesforce.com")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
    task.options = options
    log = lambda msg, *a, **k: LOGS.append(msg)  # noqa: E731
    task.logger = types.SimpleNamespace(info=log, error=log, warning=log, debug=lambda *a, **k: None)
    try:
        task._run_task()
        return fake, None
    except Exception as exc:
        return fake, exc


JOINED = "\n".join

print("status filters in SOQL through the versions (it is not a field of the set)")
fake, err = run({"operation": "list", "status": "Draft"})
check("semi-join on ExpressionSetDefinitionVersion.Status",
      "Id IN (SELECT ExpressionSetDefinitionId FROM ExpressionSetDefinitionVersion WHERE Status = 'Draft')"
      in fake.queries[0], fake.queries[0])
check("no metadata reads when only status is set", not fake.gets, repr(fake.gets))

print("interface_source_type filters on each set's metadata")
fake, err = run({"operation": "query", "interface_source_type": "RatingProcedure"})
check("no error", err is None, repr(err))
check("one metadata read per candidate set", len(fake.gets) == 3, repr(fake.gets))
check("only the rating set is listed", "Query returned 1 expression set(s)." in JOINED(LOGS), JOINED(LOGS))

print("process_type and interface_source_type combine, and the limit applies after filtering")
fake, err = run({"operation": "list", "interface_source_type": "PricingProcedure",
                 "process_type": "DefaultPricing", "limit": "1"})
check("the SOQL carries no LIMIT (it would cut before the filter)", "LIMIT" not in fake.queries[0], fake.queries[0])
check("one set returned", "Query returned 1 expression set(s)." in JOINED(LOGS), JOINED(LOGS))
check("the matched columns are printed", "InterfaceSourceType" in JOINED(LOGS) and "Pricing_One" in JOINED(LOGS),
      JOINED(LOGS))

print("with no metadata filter the limit stays in SOQL")
fake, _ = run({"operation": "list", "limit": "2"})
check("LIMIT 2", fake.queries[0].endswith("LIMIT 2"), fake.queries[0])

print("developer_names splits on commas and every value is escaped")
fake, _ = run({"operation": "list", "developer_names": "A, B'C", "status": "x'y"})
q = fake.queries[0]
check("names split and escaped", "DeveloperName IN ('A', 'B\\'C')" in q, q)
check("status escaped", "Status = 'x\\'y'" in q, q)

print("sort_by, sort_order and limit are whitelisted")
for opts, needle in (({"sort_by": "Id; x"}, "sort_by must be"),
                     ({"sort_order": "Desc; x"}, "sort_order must be"),
                     ({"limit": "1 OFFSET 2"}, "limit must be")):
    _, err = run(dict({"operation": "list"}, **opts))
    check(f"rejects {list(opts)[0]}", err is not None and needle in str(err), repr(err))
fake, _ = run({"operation": "list", "sort_by": "developer_name", "sort_order": "asc"})
check("DeveloperName Asc", fake.queries[0].endswith("ORDER BY DeveloperName Asc"), fake.queries[0])

print("list_versions selects only fields that exist on the version object")
fake, err = run({"operation": "list_versions", "developer_names": "Pricing_One"})
vq = [q for q in fake.queries if "FROM ExpressionSetDefinitionVersion" in q][0]
check("no Rank / StartDate / Label / Description", not any(f in vq for f in ("Rank", "StartDate", ", Label", "Description")), vq)
check("selects VersionNumber and Status", "VersionNumber" in vq and "Status" in vq, vq)
check("prints the version row", "Pricing_One_V1" in JOINED(LOGS), JOINED(LOGS))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")
