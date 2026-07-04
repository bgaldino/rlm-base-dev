#!/usr/bin/env python3
"""Unit tests for _apply traversal-hydration and diff_context fetch batching.

Self-contained — no pytest (matches this repo's lightweight test convention; see
tests/test_context_payload.py). Run from the repo root with base Python:

    python tests/test_context_apply.py

Exits 0 when all checks pass, 1 otherwise.

Coverage (all offline — a recording transport / monkeypatched connect_get, no
org is touched):
  * ``_apply._apply_traversal_hydration`` — the idempotency SOQL is node-scoped
    (``ContextNodeMappingId``), plan-authored attr names are escaped, and the
    probes are batched (bounded query count regardless of rule count).
  * ``diff_context._fetch_model`` — passing a prefetched definition index skips
    the per-call collection GET (the N+1 fix).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "context_service"))

import _apply  # noqa: E402
import _client  # noqa: E402
import diff_context  # noqa: E402

RESULTS = []


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


# --------------------------------------------------------------------------- #
# RecordingTransport — records soql/request/sobject calls, returns canned data
# --------------------------------------------------------------------------- #

class RecordingTransport:
    """Mirror of _apply.Transport for offline tests.

    ``soql_responses`` maps a substring of the query → the record list to return
    (first match wins; default ``[]``). ``sobject`` POSTs return an incrementing
    fake id so the create path can proceed.
    """

    def __init__(self, dry_run=False, soql_responses=None):
        self.dry_run = dry_run
        self.logger = lambda *a, **k: None
        self.requests = []
        self.sobjects = []
        self.soql_calls = []
        self.soql_responses = soql_responses or {}
        self._next_id = 0

    def request(self, method, path, body=None, *, dry_run=None):
        self.requests.append((method, path, body))
        return {}

    def sobject(self, method, sobject, record_id=None, body=None, *, dry_run=None):
        self.sobjects.append((method, sobject, record_id, body))
        if self.dry_run:
            return {}
        self._next_id += 1
        return {"id": f"fake{self._next_id}"}

    def soql(self, query):
        self.soql_calls.append(query)
        for needle, resp in self.soql_responses.items():
            if needle in query:
                return resp
        return []


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

def _detail():
    """A definition detail with one mapping/node-mapping and one attribute,
    so node_mapping_id and attr_id both resolve for the rule below."""
    return {
        "contextDefinitionVersionList": [
            {
                "contextMappings": [
                    {
                        "name": "QuoteEntitiesMapping",
                        "contextMappingId": "11j1",
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "SalesTransaction",
                                "contextNodeMappingId": "11b1",
                                "attributeMappings": [
                                    {"contextAttributeName": "RampMode__c",
                                     "contextAttributeId": "11n1"},
                                ],
                            }
                        ],
                    }
                ]
            }
        ]
    }


def _rule(attr="RampMode__c"):
    return {
        "contextAttribute": attr,
        "mappingName": "QuoteEntitiesMapping",
        "contextNode": "SalesTransaction",
        "sObject": "Quote",
        "sObjectField": "Account",
        "childSObject": "Account",
        "childSObjectField": "Name",
    }


def _applier(transport):
    return _apply.ContextApplier(transport)


# --------------------------------------------------------------------------- #
# soql_literal / _soql_in
# --------------------------------------------------------------------------- #

def test_soql_literal_escapes_quote_and_backslash():
    check("single quote is backslash-escaped",
          _client.soql_literal("O'Malley") == "O\\'Malley")
    check("backslash is doubled",
          _client.soql_literal("a\\b") == "a\\\\b")


def test_soql_in_quotes_and_escapes_each():
    check("_soql_in escapes each element and quotes it",
          _apply._soql_in(["A'x", "B"]) == "'A\\'x', 'B'")


# --------------------------------------------------------------------------- #
# _apply_traversal_hydration
# --------------------------------------------------------------------------- #

def test_traversal_query_is_node_scoped_and_escaped():
    # A (contrived) attr name with a quote proves escaping; the real guard is the
    # node scope. CAM probe returns nothing → the create path also runs.
    t = RecordingTransport()
    _applier(t)._apply_traversal_hydration([_rule("Ramp'Mode")], _detail())
    cam_probe = next((q for q in t.soql_calls if "FROM ContextAttributeMapping" in q), "")
    check("CAM probe scopes on ContextNodeMappingId",
          "ContextNodeMappingId IN (" in cam_probe)
    check("CAM probe escapes the plan-authored attr name",
          "Ramp\\'Mode" in cam_probe and "'Ramp'Mode'" not in cam_probe)


def test_traversal_probes_are_batched():
    # Three distinct rules → still exactly two SOQL probes (one CAM, one
    # hydration), not two-per-rule.
    t = RecordingTransport()
    rules = [_rule("A__c"), _rule("B__c"), _rule("C__c")]
    detail = _detail()
    # Give all three attrs resolvable ids/attr-mappings.
    nm = detail["contextDefinitionVersionList"][0]["contextMappings"][0][
        "contextNodeMappings"][0]
    nm["attributeMappings"] = [
        {"contextAttributeName": "A__c", "contextAttributeId": "11n1"},
        {"contextAttributeName": "B__c", "contextAttributeId": "11n2"},
        {"contextAttributeName": "C__c", "contextAttributeId": "11n3"},
    ]
    _applier(t)._apply_traversal_hydration(rules, detail)
    check("exactly 2 SOQL probes for 3 rules (batched)", len(t.soql_calls) == 2)


def test_traversal_reuses_existing_mapping_by_scope():
    # CAM probe returns a same-named row on THIS node mapping (reuse) plus a
    # same-named row on a DIFFERENT node mapping (must be ignored). No CAM POST
    # should fire; hydration is created against the correctly-scoped keeper.
    t = RecordingTransport(soql_responses={
        "FROM ContextAttributeMapping": [
            {"Id": "camKeep", "CreatedDate": "2026-01-02",
             "ContextInputAttributeName": "RampMode__c", "ContextNodeMappingId": "11b1"},
            {"Id": "camOther", "CreatedDate": "2026-01-03",
             "ContextInputAttributeName": "RampMode__c", "ContextNodeMappingId": "OTHER"},
        ],
        # hydration probe: none yet
        "FROM ContextAttrHydrationDetail": [],
    })
    _applier(t)._apply_traversal_hydration([_rule()], _detail())
    posted_cams = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING]
    check("existing scoped mapping is reused (no CAM POST)", not posted_cams)
    hyd = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL]
    check("hydration is created against the scoped keeper (2 chained rows)",
          len(hyd) == 2 and hyd[0][3]["ContextAttributeMappingId"] == "camKeep")


def test_traversal_creates_mapping_when_absent():
    t = RecordingTransport()  # all probes empty
    _applier(t)._apply_traversal_hydration([_rule()], _detail())
    posted_cams = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING]
    check("CAM is POSTed when no existing mapping", len(posted_cams) == 1)
    check("CAM POST carries the resolved node-mapping + attr ids",
          posted_cams[0][3]["ContextNodeMappingId"] == "11b1"
          and posted_cams[0][3]["ContextAttributeId"] == "11n1")
    hyd = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL]
    check("two chained hydration rows created against the new keeper",
          len(hyd) == 2 and hyd[0][3]["ContextAttributeMappingId"] == "fake1")


def test_traversal_skips_when_hydration_exists():
    t = RecordingTransport(soql_responses={
        "FROM ContextAttributeMapping": [
            {"Id": "camKeep", "CreatedDate": "2026-01-02",
             "ContextInputAttributeName": "RampMode__c", "ContextNodeMappingId": "11b1"},
        ],
        "FROM ContextAttrHydrationDetail": [
            {"Id": "hd1", "ContextAttributeMappingId": "camKeep"},
        ],
    })
    _applier(t)._apply_traversal_hydration([_rule()], _detail())
    hyd = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL]
    check("no hydration POST when it already exists (idempotent)", not hyd)


def test_traversal_skips_unresolvable_node_mapping():
    t = RecordingTransport()
    rule = _rule()
    rule["mappingName"] = "NoSuchMapping"
    _applier(t)._apply_traversal_hydration([rule], _detail())
    check("unresolvable node mapping → no SOQL, no writes",
          not t.soql_calls and not t.sobjects)


# --------------------------------------------------------------------------- #
# diff_context._fetch_model — N+1 collection GET fix
# --------------------------------------------------------------------------- #

def _patch_connect_get(monkey_calls, collection, detail):
    """Return a fake connect_get recording each path; serves the collection for
    the list endpoint and a detail for the item endpoint."""
    def fake(path, target_org, api_version):
        monkey_calls.append(path)
        if "context-definitions?" in path or path.endswith("context-definitions"):
            return collection
        return detail
    return fake


def test_fetch_model_with_index_skips_collection_get():
    calls = []
    collection = {"contextDefinitionList": [
        {"developerName": "RLM_Foo", "contextDefinitionId": "11O1"},
    ]}
    detail = {"contextDefinitionId": "11O1", "developerName": "RLM_Foo",
              "contextDefinitionVersionList": [{"contextNodes": [], "contextMappings": []}]}
    orig = diff_context.connect_get
    diff_context.connect_get = _patch_connect_get(calls, collection, detail)
    try:
        index = diff_context._definition_index("orgA", "67.0")
        check("index built with one collection GET", len(calls) == 1)
        calls.clear()
        diff_context._fetch_model("RLM_Foo", "orgA", "67.0", index=index)
        check("fetch with index issues only the detail GET (no collection re-list)",
              len(calls) == 1 and "context-definitions/11O1" in calls[0])
    finally:
        diff_context.connect_get = orig


def test_fetch_model_without_index_still_lists_inline():
    calls = []
    collection = {"contextDefinitionList": [
        {"developerName": "RLM_Foo", "contextDefinitionId": "11O1"},
    ]}
    detail = {"contextDefinitionId": "11O1", "developerName": "RLM_Foo",
              "contextDefinitionVersionList": [{"contextNodes": [], "contextMappings": []}]}
    orig = diff_context.connect_get
    diff_context.connect_get = _patch_connect_get(calls, collection, detail)
    try:
        diff_context._fetch_model("RLM_Foo", "orgA", "67.0")
        check("one-shot fetch (no index) does collection + detail = 2 GETs",
              len(calls) == 2)
    finally:
        diff_context.connect_get = orig


def test_fetch_model_unknown_name_returns_none():
    calls = []
    collection = {"contextDefinitionList": []}
    orig = diff_context.connect_get
    diff_context.connect_get = _patch_connect_get(calls, collection, {})
    try:
        index = diff_context._definition_index("orgA", "67.0")
        check("unknown developerName resolves to None (no detail GET)",
              diff_context._fetch_model("RLM_Missing", "orgA", "67.0", index=index) is None)
    finally:
        diff_context.connect_get = orig


# --------------------------------------------------------------------------- #

def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} apply/diff test groups...\n")
    for t in tests:
        t()
    print()
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
