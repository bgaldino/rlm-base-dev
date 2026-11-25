#!/usr/bin/env python3
"""
Invariant: manage_flows activates and deactivates by flow DeveloperName through FlowDefinition.

    python tests/test_manage_flows.py

Stdlib only: `requests` is replaced by a fake Tooling API, so no org, no network, no CumulusCI.

Why this file exists (pack 457, measured live on 264)
-----------------------------------------------------
- A PATCH of Flow.Status is rejected ("You must provide a valid Metadata field"). Activation is
  a PATCH of FlowDefinition.Metadata.activeVersionNumber (the version to activate, 0 to deactivate).
- The task logged an undefined name after the first PATCH, so the second flow was never changed.
- developer_names was not split on commas, and filtered DefinitionId rather than DeveloperName.
- status, process_type, sort_by, sort_order and limit reached SOQL unescaped.
"""
import copy
import re
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


def row(def_id, name, version, status, process_type="AutoLaunchedFlow"):
    return {"Id": f"301{def_id}{version}", "DefinitionId": def_id, "Definition": {"DeveloperName": name, "attributes": {}},
            "MasterLabel": name, "Status": status, "ProcessType": process_type, "VersionNumber": version}


class FakeTooling(types.ModuleType):
    """Answers queries from `rows`. Models: DeveloperName IN (case-insensitive), DefinitionId IN (an 18-character
    Id compares case-insensitively, a 15-character one is a case-sensitive prefix), Id IN, Status = and
    ProcessType = filters, ORDER BY on the row fields (not CreatedDate), LIMIT, and `attributes` on records.
    Records queries, URLs and PATCHes. `fail_patch_for` ids get a 400. With `pages`, every query returns
    a nextRecordsUrl and the follow-up call (params None) returns the `pages` tail."""

    ORDER_KEYS = {
        "Definition.DeveloperName": lambda r: r["Definition"]["DeveloperName"],
        "MasterLabel": lambda r: r["MasterLabel"], "Status": lambda r: r["Status"],
        "ProcessType": lambda r: r["ProcessType"], "VersionNumber": lambda r: r["VersionNumber"],
    }

    def __init__(self, rows, fail_patch_for=(), pages=None):
        super().__init__("requests")
        self.rows = rows
        self.pages = pages
        self.fail_patch_for = set(fail_patch_for)
        self.queries = []
        self.urls = []
        self.patches = []

    def get(self, url, headers=None, params=None):
        self.urls.append(url)
        if params is None:  # follow-up page
            self.queries.append("<next page>")
            return FakeResponse(200, {"records": [dict(copy.deepcopy(r), attributes={}) for r in (self.pages or [])], "done": True})
        q = params["q"]
        self.queries.append(q)
        rows = self.rows
        where = q.split(" WHERE ", 1)[1].split(" ORDER BY ")[0].split(" LIMIT ")[0] if " WHERE " in q else ""

        def in_list(field):
            m = re.search(r"(?<![\w.])" + re.escape(field) + r" IN \((.*?)\)(?= AND | OR |\)|$)", where)
            return [v.replace("\\'", "'") for v in re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))] if m else None

        dev, def_ids = in_list("Definition.DeveloperName"), in_list("DefinitionId")
        if dev is not None or def_ids is not None:  # the two name clauses are OR-ed
            dev_l = {v.lower() for v in dev or []}  # DeveloperName compares case-insensitively

            def id_match(r):
                return any(r["DefinitionId"].lower() == d.lower() if len(d) == 18 else r["DefinitionId"][:15] == d
                           for d in def_ids or [])

            rows = [r for r in rows if r["Definition"]["DeveloperName"].lower() in dev_l or id_match(r)]
        m = re.search(r"Status = '([^']*)'", where)
        if m:
            rows = [r for r in rows if r["Status"] == m.group(1)]
        m = re.search(r"ProcessType = '([^']*)'", where)
        if m:
            rows = [r for r in rows if r["ProcessType"] == m.group(1)]
        m = re.search(r" ORDER BY ([\w.]+) (Asc|Desc)", q)
        if m and m.group(1) in self.ORDER_KEYS:  # CreatedDate is not modelled: the rows keep their given order
            key = self.ORDER_KEYS[m.group(1)]
            rows = sorted(rows, key=lambda r: key(r), reverse=m.group(2) == "Desc")
        m = re.search(r" LIMIT (\d+)$", q)
        if m:
            rows = rows[: int(m.group(1))]
        body = {"records": [dict(copy.deepcopy(r), attributes={}) for r in rows], "done": True}
        if self.pages is not None:
            body.update(done=False, nextRecordsUrl="/services/data/next")
        return FakeResponse(200, body)

    def patch(self, url, headers=None, json=None):
        self.patches.append((url, json))
        if any(url.endswith("/" + d) for d in self.fail_patch_for):
            return FakeResponse(400, "boom")
        return FakeResponse(204, None)


from tasks.rlm_manage_flows import ManageFlows  # noqa: E402

LOGS = []


class StrictOrgConfig(types.SimpleNamespace):
    """Like OrgConfig: no api_version attribute, and reading one fails hard (STRICT_GETATTR)."""

    def __getattr__(self, name):
        raise AssertionError(f"org_config.{name} is not an OrgConfig attribute")


def run(rows, options, fail_patch_for=(), pages=None):
    fake = FakeTooling(rows, fail_patch_for, pages)
    saved = sys.modules.get("requests")
    sys.modules["requests"] = fake
    LOGS.clear()
    task = ManageFlows.__new__(ManageFlows)
    task.org_config = StrictOrgConfig(access_token="t", instance_url="https://example.my.salesforce.com")
    task.project_config = types.SimpleNamespace(project__package__api_version="68.0")
    task.return_values = {}
    fake.task = task
    task.options = options
    log = lambda msg, *a, **k: LOGS.append(msg)  # noqa: E731
    task.logger = types.SimpleNamespace(info=log, error=log, warning=log, debug=lambda *a, **k: None)
    try:
        task._run_task()
        return fake, None
    except Exception as exc:  # TaskOptionsError, or Exception when CumulusCI is absent
        return fake, exc
    finally:
        if saved is None:
            sys.modules.pop("requests", None)
        else:
            sys.modules["requests"] = saved


# The Tooling API returns 18-character Ids; a 15-character prefix is also accepted as a name.
A, B = "300000000000AAAQA2", "300000000000BBBQA2"
TWO = [row(A, "Flow_A", 1, "Active"), row(B, "Flow_B", 1, "Active")]
JOINED = "\n".join

print("deactivate over a comma-separated pair changes both flows")
fake, err = run(TWO, {"operation": "deactivate", "developer_names": "Flow_A, Flow_B"})
check("no error", err is None, repr(err))
check("two PATCHes, one per FlowDefinition", len(fake.patches) == 2, repr(fake.patches))
check("PATCH targets FlowDefinition with activeVersionNumber 0",
      all("/tooling/sobjects/FlowDefinition/" in u and b == {"Metadata": {"activeVersionNumber": 0}}
          for u, b in fake.patches), repr(fake.patches))
check("the query filters on Definition.DeveloperName with both names split",
      "Definition.DeveloperName IN ('Flow_A', 'Flow_B')" in fake.queries[0], fake.queries[0])
check("the log names each flow and a summary",
      "Deactivated 'Flow_A'" in JOINED(LOGS) and "Deactivated 'Flow_B'" in JOINED(LOGS)
      and "2 deactivated, 0 already in that state, 0 failed" in JOINED(LOGS), JOINED(LOGS))

print("activate picks the newest valid version and skips one already active")
rows = [row(A, "Flow_A", 1, "Obsolete"), row(A, "Flow_A", 2, "Draft"), row(A, "Flow_A", 3, "InvalidDraft"),
        row(B, "Flow_B", 4, "Active")]
fake, err = run(rows, {"operation": "activate", "developer_names": ["Flow_A", "Flow_B"]})
check("no error", err is None, repr(err))
check("Flow_A goes to version 2 (3 is InvalidDraft)",
      fake.patches == [(fake.patches[0][0], {"Metadata": {"activeVersionNumber": 2}})] and len(fake.patches) == 1,
      repr(fake.patches))
check("Flow_B, already active at its newest version, is skipped",
      "'Flow_B' version 4 is already active" in JOINED(LOGS), JOINED(LOGS))

print("deactivate skips a flow with no active version")
fake, err = run([row(A, "Flow_A", 1, "Obsolete")], {"operation": "deactivate", "developer_names": "Flow_A"})
check("no PATCH and no error", err is None and not fake.patches, repr((err, fake.patches)))

print("one failing flow does not stop the rest, and the task still fails")
fake, err = run(TWO, {"operation": "deactivate", "developer_names": "Flow_A,Flow_B"}, fail_patch_for=[A])
check("both PATCHes were attempted", len(fake.patches) == 2, repr(fake.patches))
check("the task raises", err is not None and "1 flow(s)" in str(err), repr(err))
check("the failure names the flow", "Failed to deactivate 'Flow_A'" in JOINED(LOGS), JOINED(LOGS))

print("a name that matches nothing stops before any change")
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "deactivate", "developer_names": "Flow_A,Nope"})
check("raises naming the missing flow", err is not None and "Nope" in str(err), repr(err))
check("no PATCH was sent", not fake.patches, repr(fake.patches))

print("a FlowDefinition Id is accepted too (15 or 18 characters)")
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "deactivate", "developer_names": A[:15]})
check("queried by DefinitionId (15 characters)", f"DefinitionId IN ('{A[:15]}')" in fake.queries[0], fake.queries[0])
check("no error, one PATCH", err is None and len(fake.patches) == 1, repr((err, fake.patches)))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "deactivate", "developer_names": A})
check("queried by DefinitionId (18 characters)", f"DefinitionId IN ('{A}')" in fake.queries[0], fake.queries[0])
check("no error, one PATCH (18)", err is None and len(fake.patches) == 1, repr((err, fake.patches)))

print("activate and deactivate require developer_names and reject the list-only filters")
_, err = run(TWO, {"operation": "activate"})
check("developer_names required", err is not None and "developer_names is required" in str(err), repr(err))
_, err = run(TWO, {"operation": "deactivate", "developer_names": "Flow_A", "status": "Active"})
check("status rejected", err is not None and "status is not used" in str(err), repr(err))
_, err = run(TWO, {"operation": "deactivate", "developer_names": "Flow_A", "limit": "1"})
check("limit rejected", err is not None and "limit is not used" in str(err), repr(err))

print("every interpolated value is escaped or whitelisted")
fake, err = run([], {"operation": "list", "developer_names": "O'Brien,a\\b", "status": "x' OR Id != '",
                     "process_type": "p'q", "sort_by": "DeveloperName", "sort_order": "asc", "limit": "5"})
q = fake.queries[0]
check("names escaped", "'O\\'Brien'" in q and "'a\\\\b'" in q, q)
check("status escaped", "Status = 'x\\' OR Id != \\''" in q, q)
check("process_type escaped", "ProcessType = 'p\\'q'" in q, q)
check("sort and limit applied", q.endswith("ORDER BY Definition.DeveloperName Asc LIMIT 5"), q)
for opts, needle in (({"sort_by": "Id; DROP"}, "sort_by must be"),
                     ({"sort_order": "Desc; x"}, "sort_order must be"),
                     ({"limit": "5 OFFSET 1"}, "limit must be")):
    _, err = run([], dict({"operation": "list"}, **opts))
    check(f"rejects {list(opts)[0]}", err is not None and needle in str(err), repr(err))

print("LastModifiedDate maps to CreatedDate (Flow has no LastModifiedDate)")
fake, _ = run([], {"operation": "list", "sort_by": "LastModifiedDate"})
check("ORDER BY CreatedDate Desc", fake.queries[0].endswith("ORDER BY CreatedDate Desc"), fake.queries[0])

print("list prints the DeveloperName and the DefinitionId (which tells apart flows sharing a name)")
run(TWO, {"operation": "list"})
check("names in the table", "Flow_A" in JOINED(LOGS) and "Flow_B" in JOINED(LOGS), JOINED(LOGS))
check("DefinitionIds in the table", A in JOINED(LOGS) and B in JOINED(LOGS), JOINED(LOGS))

print("names match case-insensitively, as the SOQL IN does")
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "deactivate", "developer_names": "flow_a"})
check("flow_a finds Flow_A", err is None and len(fake.patches) == 1, repr((err, fake.patches)))

print("activation target: an older draft never beats a newer version that was live")
def target(versions):
    return ManageFlows._activation_target([dict(v) for v in versions])["VersionNumber"]


def st(n, status):
    return {"VersionNumber": n, "Status": status}


check("[Draft v1, Obsolete v2] -> v2", target([st(1, "Draft"), st(2, "Obsolete")]) == 2)
check("[Active v1, Draft v2, Obsolete v3] -> v2 (a draft newer than the Active one)",
      target([st(1, "Active"), st(2, "Draft"), st(3, "Obsolete")]) == 2)
check("[Draft v1, Active v2, Obsolete v3] -> v2 (an older draft loses to the Active one)",
      target([st(1, "Draft"), st(2, "Active"), st(3, "Obsolete")]) == 2)
check("[Obsolete v1, Active v2] -> v2 (rollback stands)", target([st(1, "Obsolete"), st(2, "Active")]) == 2)
fake, err = run([row(A, "Flow_A", 1, "Draft"), row(A, "Flow_A", 2, "Obsolete")],
                {"operation": "activate", "developer_names": "Flow_A"})
check("run: deactivated flow returns to v2, not the stale draft",
      err is None and [b for _, b in fake.patches] == [{"Metadata": {"activeVersionNumber": 2}}], repr((err, fake.patches)))
_, err = run([row(A, "Flow_A", 1, "InvalidDraft"), row(A, "Flow_A", 2, "Weird")],
             {"operation": "activate", "developer_names": "Flow_A"})
check("no usable version names the statuses seen",
      err is not None and any("InvalidDraft, Weird" in m for m in LOGS), repr((err, LOGS)))

print("process_type is rejected by activate/deactivate; list/query report a name that matches no flow")
for verb in ("activate", "deactivate"):
    _, err = run(TWO, {"operation": verb, "developer_names": "Flow_A", "process_type": "Flow"})
    check(f"{verb} rejects process_type", err is not None and "process_type is not used" in str(err), repr(err))
_, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "Flow_A,Nope"})
check("list raises naming the missing flow", err is not None and "Nope" in str(err), repr(err))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "flow_a", "status": "Draft"})
check("a status filter that excludes an existing flow is not a missing name",
      err is None and len(fake.queries) == 2 and "Status = 'Draft'" in fake.queries[0] and "Status" not in fake.queries[1].split("WHERE")[1],
      repr((err, fake.queries)))
fake, err = run([row(A, "Flow_A", 1, "Active"), row(B, "Flow_B", 1, "Active")],
                {"operation": "list", "developer_names": "Flow_A,Flow_B", "limit": "1"})
check("a limit does not make an existing name missing",
      err is None and len(fake.queries) == 2 and fake.queries[0].endswith("LIMIT 1") and "LIMIT" not in fake.queries[1],
      repr((err, fake.queries)))
# A 15-character Id is case-sensitive, so a wrong-case one is refused (raises, changes nothing: fail safe).
# This is the guard for the 15-character Id branch of _raise_on_missing: the wrong-case Id matches nothing
# in SOQL, so only another name's row could (wrongly) satisfy it. How the org treats a wrong-case
# 15-character Id in a SOQL IN is unverified.
_, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "Flow_A,300000000000aaa"})
check("a wrong-case 15-character Id is not satisfied by another name's row",
      err is not None and "300000000000aaa" in str(err), repr(err))
# An 18-character Id is case-insensitive by design, so a lowercased one that the org resolves is not missing.
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "deactivate", "developer_names": A.lower()})
check("a wrong-case 18-character Id matches", err is None and len(fake.patches) == 1, repr((err, fake.patches)))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "Flow_A"})
check("the project API version is used (org_config has no api_version)",
      err is None and fake.urls and all("/v68.0/" in u for u in fake.urls), repr((err, fake.urls)))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "Flow_A"})
check("no status, process_type or limit: one query serves the missing-name check", err is None and len(fake.queries) == 1, repr(fake.queries))
fake, err = run([row(A, "Flow_A", 1, "Active"), row(A, "Flow_A", 2, "Draft")], {"operation": "query", "developer_names": "FLOW_A"})
check("query returns the rows in return_values['flows'] (case-insensitive DeveloperName)",
      err is None and sorted(f["VersionNumber"] for f in fake.task.return_values.get("flows", [])) == [1, 2]
      and all("attributes" not in f and "attributes" not in f["Definition"] for f in fake.task.return_values["flows"]),
      repr((err, fake.task.return_values)))
fake, err = run([row(A, "Flow_A", 1, "Active", "AutoLaunchedFlow"), row(B, "Flow_B", 1, "Active", "Flow")],
                {"operation": "query", "process_type": "Flow"})
check("process_type filters the rows", err is None and [f["ProcessType"] for f in fake.task.return_values["flows"]] == ["Flow"],
      repr((err, fake.queries)))
fake, err = run([row(A, "Flow_A", 3, "Active"), row(A, "Flow_A", 1, "Draft"), row(A, "Flow_A", 2, "Obsolete")],
                {"operation": "query", "sort_by": "VersionNumber", "sort_order": "asc", "limit": "2"})
check("sort_by and sort_order order the rows before LIMIT",
      err is None and [f["VersionNumber"] for f in fake.task.return_values["flows"]] == [1, 2], repr((err, fake.queries)))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list"})
check("list returns no values", err is None and fake.task.return_values == {}, repr(fake.task.return_values))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "list", "developer_names": "Flow_A"},
                pages=[row(B, "Flow_B", 1, "Active")])
check("a paginated query follows nextRecordsUrl", err is None and "<next page>" in fake.queries, repr((err, fake.queries)))
fake, err = run([row(A, "Flow_A", 1, "Active")], {"operation": "query", "developer_names": "Flow_A"},
                pages=[row(B, "Flow_B", 1, "Active")])
check("the tail page's rows are returned",
      err is None and [f["Definition"]["DeveloperName"] for f in fake.task.return_values["flows"]] == ["Flow_A", "Flow_B"],
      repr((err, fake.task.return_values)))

print("activate never undoes a rollback and does re-activate a deactivated flow")
fake, err = run([row(A, "Flow_A", 1, "Obsolete"), row(A, "Flow_A", 2, "Active")],
                {"operation": "activate", "developer_names": "Flow_A"})
check("an Obsolete older version is not chosen over the Active one", err is None and not fake.patches,
      repr((err, fake.patches)))
fake, err = run([row(A, "Flow_A", 1, "Obsolete"), row(A, "Flow_A", 2, "Active"), row(A, "Flow_A", 3, "Obsolete")],
                {"operation": "activate", "developer_names": "Flow_A"})
check("an Obsolete newer version does not displace the Active one", err is None and not fake.patches,
      repr((err, fake.patches)))
fake, err = run([row(A, "Flow_A", 1, "Obsolete"), row(A, "Flow_A", 2, "Obsolete")],
                {"operation": "activate", "developer_names": "Flow_A"})
check("with nothing Draft or Active, the newest Obsolete version is re-activated",
      err is None and [b for _, b in fake.patches] == [{"Metadata": {"activeVersionNumber": 2}}],
      repr((err, fake.patches)))
_, err = run([row(A, "Flow_A", 1, "InvalidDraft")], {"operation": "activate", "developer_names": "Flow_A"})
check("only InvalidDraft versions is a per-flow failure", err is not None and "1 flow(s)" in str(err), repr(err))

print("a DeveloperName shared by two flows (a managed package's and the org's) is refused; a DefinitionId is not")
SHARED = [row(A, "Flow_A", 1, "Active"), row(B, "Flow_A", 1, "Active")]
for verb in ("activate", "deactivate"):
    fake, err = run(SHARED, {"operation": verb, "developer_names": "Flow_A"})
    check(f"{verb}: refused before any change, naming both flows",
          err is not None and "more than one flow" in str(err) and A in str(err) and B in str(err)
          and not fake.patches, repr((err, fake.patches)))
fake, err = run(SHARED, {"operation": "deactivate", "developer_names": A})
check("deactivate by DefinitionId changes only that flow",
      err is None and len(fake.patches) == 1 and A in fake.patches[0][0], repr((err, fake.patches)))
fake, err = run([row(A, "MyFlow", 1, "Active"), row(B, "myflow", 1, "Active")],
                {"operation": "deactivate", "developer_names": "MyFlow"})
check("names differing only in case are the same name: refused, both shown",
      err is not None and "more than one flow" in str(err) and "MyFlow" in str(err) and "myflow" in str(err)
      and not fake.patches, repr((err, fake.patches)))

print("a blank or padded sort_by means the default or the trimmed value")
fake, _ = run([], {"operation": "list", "sort_by": " "})
check("blank sort_by orders by CreatedDate", "ORDER BY CreatedDate" in fake.queries[0], fake.queries[0])
fake, _ = run([], {"operation": "list", "sort_by": " DeveloperName "})
check("padded sort_by is trimmed", "ORDER BY Definition.DeveloperName" in fake.queries[0], fake.queries[0])

print("blank or padded status, process_type, limit and operation mean not set or the trimmed value")
fake, err = run([], {"operation": " list ", "status": " ", "process_type": "  ", "limit": " "})
q = fake.queries[0] if fake.queries else ""
check("padded operation runs; blank filters add no WHERE and no LIMIT",
      err is None and " WHERE " not in q and " LIMIT " not in q, repr((err, q)))
fake, _ = run([], {"operation": "list", "status": " Active ", "process_type": " Flow "})
check("padded filters are trimmed", "Status = 'Active'" in fake.queries[0] and "ProcessType = 'Flow'" in fake.queries[0],
      fake.queries[0])
fake, err = run([row(A, "Flow_A", 1, "Active")],
                {"operation": "deactivate", "developer_names": "Flow_A", "status": " ", "limit": ""})
check("deactivate does not reject blank list-only filters", err is None and len(fake.patches) == 1,
      repr((err, fake.patches)))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")
