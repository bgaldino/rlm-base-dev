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
    return {"Id": f"301{def_id}{version}", "DefinitionId": def_id, "Definition": {"DeveloperName": name},
            "MasterLabel": name, "Status": status, "ProcessType": process_type, "VersionNumber": version}


class FakeTooling(types.ModuleType):
    """Answers every query with `rows`; records queries and PATCHes. `fail_patch_for` ids get a 400."""

    def __init__(self, rows, fail_patch_for=()):
        super().__init__("requests")
        self.rows = rows
        self.fail_patch_for = set(fail_patch_for)
        self.queries = []
        self.patches = []

    def get(self, url, headers=None, params=None):
        self.queries.append(params["q"])
        return FakeResponse(200, {"records": [dict(r, attributes={}) for r in self.rows], "done": True})

    def patch(self, url, headers=None, json=None):
        self.patches.append((url, json))
        if any(url.endswith("/" + d) for d in self.fail_patch_for):
            return FakeResponse(400, "boom")
        return FakeResponse(204, None)


from tasks.rlm_manage_flows import ManageFlows  # noqa: E402

LOGS = []


def run(rows, options, fail_patch_for=()):
    fake = FakeTooling(rows, fail_patch_for)
    sys.modules["requests"] = fake
    LOGS.clear()
    task = ManageFlows.__new__(ManageFlows)
    task.org_config = types.SimpleNamespace(
        access_token="t", instance_url="https://example.my.salesforce.com", api_version="68.0")
    task.project_config = None
    task.options = options
    log = lambda msg, *a, **k: LOGS.append(msg)  # noqa: E731
    task.logger = types.SimpleNamespace(info=log, error=log, warning=log, debug=lambda *a, **k: None)
    try:
        task._run_task()
        return fake, None
    except Exception as exc:  # TaskOptionsError, or Exception when CumulusCI is absent
        return fake, exc


A, B = "300000000000AAA", "300000000000BBB"
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
check("queried by DefinitionId", f"DefinitionId IN ('{A[:15]}')" in fake.queries[0], fake.queries[0])
check("no error, one PATCH", err is None and len(fake.patches) == 1, repr((err, fake.patches)))

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

print("list prints DeveloperName, not the DefinitionId")
run(TWO, {"operation": "list"})
check("names in the table", "Flow_A" in JOINED(LOGS) and "Flow_B" in JOINED(LOGS), JOINED(LOGS))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")
