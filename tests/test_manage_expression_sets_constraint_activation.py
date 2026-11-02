#!/usr/bin/env python3
"""
Invariant: manage_expression_sets activates constraint models through the constraint-version resource.

    python tests/test_manage_expression_sets_constraint_activation.py

Stdlib only: `requests` is replaced by a stub, so no org, no network and no CumulusCI install.

Why this file exists
--------------------
An ExpressionSetVersion.IsActive update flips the record but never deploys a constraint model to
the solver. prepare_constraints' deactivate/reactivate cycle therefore left a re-imported model
running the old one on any warm org (todo 064, measured live). Constraint versions must go through
PATCH /industries/constraints/{setId}/versions/{versionId}, and because that resource reports a
failed deploy as HTTP 200 with success: false, the body has to be checked. Other expression sets
keep the sObject update.
"""
import json
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
        self.text = "" if body is None else json.dumps(body)
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._body


class RawResponse(FakeResponse):
    """A 200 whose body is not JSON."""

    def __init__(self, text):
        super().__init__(200, None)
        self.text = text

    def json(self):
        raise ValueError("Expecting value: line 1 column 1 (char 0)")


class FakeRequests(types.ModuleType):
    """Answers the version query with `record`, and PATCHes with `patch_response`.

    `patch_response` may be a list, consumed one response per PATCH.
    """

    def __init__(self, record, patch_response):
        super().__init__("requests")
        self.record = record
        self.patch_response = patch_response
        self.queries = []
        self.patches = []

    def get(self, url, headers=None, params=None):
        self.queries.append((url, params))
        return FakeResponse(200, {"records": [self.record] if self.record else []})

    def patch(self, url, headers=None, json=None):
        self.patches.append((url, json))
        if isinstance(self.patch_response, list):
            return self.patch_response.pop(0)
        return self.patch_response


from tasks.rlm_manage_expression_sets import ManageExpressionSets  # noqa: E402


WARNINGS = []


def run(record, status, patch_response=None):
    """Call _update_version_status against the stub; return (stub, result_or_exception)."""
    fake = FakeRequests(record, patch_response or FakeResponse(204))
    sys.modules["requests"] = fake
    WARNINGS.clear()
    task = ManageExpressionSets.__new__(ManageExpressionSets)
    task.org_config = types.SimpleNamespace(
        access_token="t", instance_url="https://example.my.salesforce.com", api_version="68.0")
    task.project_config = None
    task.options = {}
    task.logger = types.SimpleNamespace(
        info=lambda *a, **k: None, error=lambda *a, **k: None,
        warning=lambda msg, *args, **k: WARNINGS.append(msg % args if args else msg))
    try:
        return fake, task._update_version_status(record and "Model_V1" or "Missing_V1", status)
    except Exception as exc:  # TaskOptionsError, or Exception when CumulusCI is absent
        return fake, exc


def constraint_record(active):
    return {"Id": "9QMx", "IsActive": active, "ExpressionSetId": "9QLx",
            "ExpressionSet": {"UsageType": "Constraint"}}


print("the version query fetches what the routing needs")
fake, _ = run(constraint_record(False), "Active", FakeResponse(200, {"success": True, "errors": []}))
soql = fake.queries[0][1]["q"]
check("query selects ExpressionSet.UsageType and ExpressionSetId",
      "ExpressionSet.UsageType" in soql and "ExpressionSetId" in soql, soql)

print("a constraint version activates through the constraint-version resource")
check("exactly one PATCH", len(fake.patches) == 1, repr(fake.patches))
url, body = fake.patches[0]
check("PATCH goes to /industries/constraints/{setId}/versions/{versionId}",
      url.endswith("/services/data/v68.0/industries/constraints/9QLx/versions/9QMx"), url)
check("body is {'status': 'Active'}", body == {"status": "Active"}, repr(body))
check("no /connect segment (that path 404s)", "/connect/" not in url, url)

print("deactivating a constraint version removes it from the solver the same way")
fake, result = run(constraint_record(True), "Inactive", FakeResponse(200, {"success": True, "errors": []}))
check("body is {'status': 'Inactive'}", fake.patches and fake.patches[0][1] == {"status": "Inactive"},
      repr(fake.patches))
check("returns True on success", result is True, repr(result))

print("HTTP 200 with success: false is a failure, not a pass")
fake, result = run(constraint_record(False), "Active",
                   FakeResponse(200, {"success": False, "errors": [{"message": "Model is invalid"}]}))
check("raises", isinstance(result, Exception), repr(result))
check("the error names the platform's message", "Model is invalid" in str(result), str(result))

print("other expression sets keep the sObject IsActive update")
pricing = {"Id": "9QMp", "IsActive": False, "ExpressionSetId": "9QLp",
           "ExpressionSet": {"UsageType": "Pricing"}}
fake, result = run(pricing, "Active")
url, body = fake.patches[0]
check("PATCH goes to /sobjects/ExpressionSetVersion/{id}",
      url.endswith("/sobjects/ExpressionSetVersion/9QMp"), url)
check("body is {'IsActive': True}", body == {"IsActive": True}, repr(body))
check("returns True on 204", result is True, repr(result))

print("a version without a parent UsageType is treated as non-constraint")
fake, _ = run({"Id": "9QMn", "IsActive": False, "ExpressionSetId": "9QLn", "ExpressionSet": None}, "Active")
check("sObject route", fake.patches and "/sobjects/ExpressionSetVersion/9QMn" in fake.patches[0][0],
      repr(fake.patches))

print("a version already in the target state is left alone")
fake, result = run(constraint_record(True), "Active")
check("no PATCH", fake.patches == [], repr(fake.patches))
check("returns True", result is True, repr(result))
check("an already-Active constraint model warns that skipping does not deploy it",
      any("does not redeploy" in w for w in WARNINGS), repr(WARNINGS))
fake, _ = run({"Id": "9QMp", "IsActive": True, "ExpressionSetId": "9QLp",
               "ExpressionSet": {"UsageType": "Pricing"}}, "Active")
check("an already-Active pricing procedure does not get that warning",
      not any("does not redeploy" in w for w in WARNINGS), repr(WARNINGS))

print("a 200 from the constraint resource that is not JSON fails with a readable message")
fake, result = run(constraint_record(False), "Active", RawResponse("<html>Service Unavailable</html>"))
check("raises", isinstance(result, Exception), repr(result))
check("the message says the body was not JSON and quotes it",
      "not JSON" in str(result) and "Service Unavailable" in str(result), str(result))

print("a row lock on the constraint resource is retried, then succeeds")
original_sleep = __import__("time").sleep
__import__("time").sleep = lambda s: None
try:
    fake, result = run(constraint_record(False), "Active",
                       [FakeResponse(400, [{"errorCode": "UNABLE_TO_LOCK_ROW"}]),
                        FakeResponse(200, {"success": True, "errors": []})])
finally:
    __import__("time").sleep = original_sleep
check("two PATCHes", len(fake.patches) == 2, repr(fake.patches))
check("returns True after the retry", result is True, repr(result))

print("a missing version still reports 'not found by ApiName' (the bulk path skips on that text)")
fake, result = run(None, "Active")
check("raises with the skip text", isinstance(result, Exception) and "not found by ApiName" in str(result),
      repr(result))

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) failed")
    sys.exit(1)
print("all checks passed")
