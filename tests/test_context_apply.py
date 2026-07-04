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
# _apply_mapping_updates — non-destructive PATCH (P2, whole-body-replace fix)
# --------------------------------------------------------------------------- #

def _detail_with_siblings():
    """A detail with one existing node mapping carrying TWO attribute mappings —
    used to verify the PATCH doesn't destroy the sibling the plan didn't touch.

    Shape mirrors the live GET response: ``attributeMappings`` is a bare list of
    row dicts (with ``contextAttributeMappingId``); the outgoing PATCH wraps
    them under ``attributeMappings.contextAttributeMappings``.
    """
    # Response-shape mirror of a live GET: ``contextAttributeName`` is the
    # response-only mirror of ``contextInputAttributeName``. The Quantity row
    # also carries a flat hydration list — the PATCH must re-nest this under
    # ``hydrationDetails.contextAttrHydrationDetails`` (live-verified 2026-07-04).
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
                                     "contextInputAttributeName": "RampMode__c",
                                     "contextAttributeId": "11n1",
                                     "contextAttributeMappingId": "11a1",
                                     "mappedField": "RampMode__c",
                                     "baseReference": "std/x/y/RampMode__c",
                                     "parentNodeMappingId": "11b0"},
                                    {"contextAttributeName": "Quantity",
                                     "contextInputAttributeName": "Quantity",
                                     "contextAttributeId": "11n2",
                                     "contextAttributeMappingId": "11a2",
                                     "mappedField": "Quantity",
                                     "baseReference": "std/x/y/Quantity",
                                     "parentNodeMappingId": "11b0",
                                     "contextAttrHydrationDetailList": [
                                         {"sObjectDomain": "Quote",
                                          "queryAttribute": "Quantity",
                                          "contextAttrHydrationDetailId": "11P0",
                                          "baseReference": "std/x/hyd"}
                                     ]},
                                ],
                            }
                        ],
                    }
                ]
            }
        ]
    }


def _payload_touching_one_attr():
    """A ``contextMappings`` PATCH body that re-emits only ONE of the two
    attribute mappings on the node — the shape that would silently delete the
    other sibling without the merge fix (P2)."""
    return {
        "contextMappings": [
            {
                "contextMappingId": "11j1",
                "contextNodeMappings": [
                    {
                        "contextNodeName": "SalesTransaction",
                        "contextNodeMappingId": "11b1",
                        "attributeMappings": [
                            {"contextAttributeId": "11n1",
                             "contextAttributeName": "RampMode__c",
                             "mappedField": "RampModeAlias__c"},
                        ],
                    }
                ],
            }
        ]
    }


def test_apply_mapping_updates_preserves_untouched_siblings():
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates(
        "11O1", _payload_touching_one_attr(), detail=_detail_with_siblings()
    )
    patch = next(
        (r for r in t.requests if r[0] == "PATCH" and "context-node-mappings" in r[1]),
        None,
    )
    check("PATCH to context-node-mappings was issued", patch is not None)
    if not patch:
        return
    node_maps = patch[2]["contextNodeMappings"]
    inner = node_maps[0]["attributeMappings"]["contextAttributeMappings"]
    # Caller row uses ``contextAttributeName`` (that's what plan builders emit
    # for the touched row); the merged sibling row was projected to remove that
    # response-only key, so look for it via ``contextInputAttributeName`` too.
    names = {a.get("contextAttributeName") or a.get("contextInputAttributeName")
             for a in inner}
    check("plan-touched RampMode__c is in the PATCH body", "RampMode__c" in names)
    check("untouched sibling Quantity was merged back in (not deleted)",
          "Quantity" in names)
    check("exactly two attribute mappings in the outgoing PATCH", len(inner) == 2)
    # Live-verified projection contract (2026-07-04): the Connect PATCH rejects
    # response-only fields on each attribute mapping row. Merged siblings must
    # not carry ``baseReference`` / ``parentNodeMappingId`` / ``contextAttributeName``.
    merged = next(a for a in inner
                  if a.get("contextInputAttributeName") == "Quantity"
                  or a.get("contextAttributeId") == "11n2")
    check("merged sibling drops response-only 'baseReference'",
          "baseReference" not in merged)
    check("merged sibling drops response-only 'parentNodeMappingId'",
          "parentNodeMappingId" not in merged)
    check("merged sibling drops response-only 'contextAttributeName'",
          "contextAttributeName" not in merged)
    # And the flat GET-side ``contextAttrHydrationDetailList`` was re-nested
    # under ``hydrationDetails.contextAttrHydrationDetails`` with the entry
    # projected to only ``sObjectDomain`` + ``queryAttribute``.
    check("flat contextAttrHydrationDetailList not carried through as top-level",
          "contextAttrHydrationDetailList" not in merged)
    hyd = ((merged.get("hydrationDetails") or {})
           .get("contextAttrHydrationDetails") or [])
    check("hydrationDetails re-nested with one entry",
          isinstance(hyd, list) and len(hyd) == 1)
    if hyd:
        check("hydration entry projected to writable sub-fields only",
              set(hyd[0].keys()) == {"sObjectDomain", "queryAttribute"})


def test_apply_mapping_updates_deduplicates_by_id():
    # If the caller re-emits an existing row (by contextAttributeMappingId), the
    # merge must not double-count it.
    payload = _payload_touching_one_attr()
    payload["contextMappings"][0]["contextNodeMappings"][0]["attributeMappings"][0][
        "contextAttributeMappingId"] = "11a1"
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates("11O1", payload, detail=_detail_with_siblings())
    patch = next(r for r in t.requests if r[0] == "PATCH")
    inner = patch[2]["contextNodeMappings"][0]["attributeMappings"]["contextAttributeMappings"]
    ids = [a.get("contextAttributeMappingId") for a in inner]
    check("no duplicate ContextAttributeMapping rows in the PATCH body",
          ids.count("11a1") == 1)


def test_apply_mapping_updates_skips_inherited_siblings():
    # Attribute mappings inherited from the standard base carry a
    # ``baseReference`` into ``…__stdctx/…``. Re-emitting them on a PATCH
    # against a child definition raises INVALID_INPUT "An Inherited mapping
    # for ContextAttribute X already exists." — live-verified 2026-07-04.
    # The merge must skip them entirely rather than project them through.
    detail = _detail_with_siblings()
    inh = {"contextAttributeName": "PeriodBoundary",
           "contextInputAttributeName": "PeriodBoundary",
           "contextAttributeId": "11nStd",
           "contextAttributeMappingId": "11aStd",
           "baseReference":
               "SalesTransactionContext__stdctx/version/QuoteEntitiesMapping/"
               "SalesTransactionItem/PeriodBoundary",
           "parentNodeMappingId": "11b0"}
    detail["contextDefinitionVersionList"][0]["contextMappings"][0][
        "contextNodeMappings"][0]["attributeMappings"].append(inh)
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates("11O1", _payload_touching_one_attr(), detail=detail)
    patch = next(r for r in t.requests if r[0] == "PATCH")
    inner = patch[2]["contextNodeMappings"][0]["attributeMappings"]["contextAttributeMappings"]
    names = {a.get("contextAttributeName") or a.get("contextInputAttributeName")
             for a in inner}
    check("inherited-from-base sibling is NOT re-emitted",
          "PeriodBoundary" not in names)
    check("plan-touched RampMode__c is in the PATCH body", "RampMode__c" in names)
    check("custom sibling Quantity IS preserved (non-inherited)",
          "Quantity" in names)


def test_apply_mapping_updates_deduplicates_by_name_when_id_absent():
    # The caller re-emits the same attribute WITHOUT its
    # contextAttributeMappingId; merge must dedupe on (attrId, name).
    payload = _payload_touching_one_attr()
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates("11O1", payload, detail=_detail_with_siblings())
    patch = next(r for r in t.requests if r[0] == "PATCH")
    inner = patch[2]["contextNodeMappings"][0]["attributeMappings"]["contextAttributeMappings"]
    names = [a.get("contextAttributeName") or a.get("contextInputAttributeName")
             for a in inner]
    check("re-emitted attr not duplicated (dedup on attrId+name)",
          names.count("RampMode__c") == 1)


def test_apply_mapping_updates_without_detail_is_a_noop_merge():
    # Backward-compat: if the caller doesn't pass a detail snapshot the merge
    # does nothing and the original behavior is preserved (destructive but
    # unchanged from historical).
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates("11O1", _payload_touching_one_attr(), detail=None)
    patch = next(r for r in t.requests if r[0] == "PATCH")
    inner = patch[2]["contextNodeMappings"][0]["attributeMappings"]["contextAttributeMappings"]
    check("no merge when detail is None (only the caller's row goes through)",
          len(inner) == 1)


def test_apply_mapping_updates_post_branch_is_untouched():
    # A brand-new node mapping (no contextNodeMappingId) goes through the POST
    # branch, which has no siblings to preserve — the merge must not touch it.
    payload = {
        "contextMappings": [
            {
                "contextMappingId": "11j1",
                "contextNodeMappings": [
                    {
                        "contextNodeName": "SalesTransaction",
                        "attributeMappings": [
                            {"contextAttributeName": "New__c",
                             "contextAttributeId": "11n9"},
                        ],
                    }
                ],
            }
        ]
    }
    t = RecordingTransport()
    _applier(t)._apply_mapping_updates("11O1", payload, detail=_detail_with_siblings())
    post = next(
        (r for r in t.requests if r[0] == "POST" and "context-node-mappings" in r[1]),
        None,
    )
    check("POST branch is used for new node mappings", post is not None)
    if not post:
        return
    inner = post[2]["contextNodeMappings"][0]["attributeMappings"]["contextAttributeMappings"]
    check("POST body carries exactly the caller's rows (no merge)",
          len(inner) == 1 and inner[0].get("contextAttributeName") == "New__c")


# --------------------------------------------------------------------------- #
# _guard_active_for_patch — deactivate-first guards (P2)
# --------------------------------------------------------------------------- #

def _active_detail():
    return {"isActive": True,
            "contextDefinitionVersionList": [{"isActive": True, "contextMappings": []}]}


def _inactive_detail():
    return {"isActive": False,
            "contextDefinitionVersionList": [{"isActive": False, "contextMappings": []}]}


def test_guard_active_refuses_when_not_opted_in():
    t = RecordingTransport()
    applier = _applier(t)
    applier._deactivate_first = False
    raised = False
    try:
        applier._guard_active_for_patch("11O1", _active_detail(), "sync IsTransient")
    except _client.ContextClientError as exc:
        raised = "ACTIVE" in str(exc) and "deactivate_before" in str(exc)
    check("active + no deactivate_before → raises with actionable message", raised)


def test_guard_active_deactivates_when_opted_in():
    # Two requests: the first `sf api request` is the isActive:false PATCH; the
    # second is the fetch_detail. RecordingTransport.request returns {}; we need
    # the post-deactivate detail to be inactive so the guard doesn't loop, so
    # patch fetch_detail on the applier instance.
    t = RecordingTransport()
    applier = _applier(t)
    applier._deactivate_first = True
    applier.fetch_detail = lambda ctx: _inactive_detail()  # type: ignore
    out = applier._guard_active_for_patch("11O1", _active_detail(), "sync IsTransient")
    patch = next(
        (r for r in t.requests if r[0] == "PATCH" and "context-definitions/11O1" in r[1]),
        None,
    )
    check("active + deactivate_before → issues the isActive:false PATCH",
          patch is not None and patch[2] == {"isActive": "false"})
    check("guard returns the post-deactivate detail", out.get("isActive") is False)


def test_guard_active_is_noop_when_already_inactive():
    t = RecordingTransport()
    applier = _applier(t)
    applier._deactivate_first = False  # not opted in — must still be a no-op
    out = applier._guard_active_for_patch("11O1", _inactive_detail(), "op")
    check("inactive detail → no PATCH issued", not t.requests)
    check("inactive detail → detail returned unchanged",
          out is not None and out.get("isActive") is False)


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


def test_validate_shape_accepts_well_formed_patch():
    body = {
        "contextNodeMappings": [
            {
                "contextNodeId":        "11a",
                "contextNodeMappingId": "11b",
                "sObjectName":          "QuoteLineItem",
                "mappedContextNodeId":  "11a",
                "attributeMappings": {
                    "contextAttributeMappings": [
                        {
                            "contextAttributeId":         "11c",
                            "contextInputAttributeName":  "MyAttr__c",
                            "contextAttributeMappingId":  "11d",
                            "isKey":                       False,
                            "isValue":                     True,
                            "hydrationDetails": {
                                "contextAttrHydrationDetails": [
                                    {"sObjectDomain": "QuoteLineItem",
                                     "queryAttribute": "Description"}
                                ]
                            },
                        }
                    ]
                },
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(body)
    check("well-formed PATCH body has zero violations", violations == [])


def test_validate_shape_flags_missing_node_shell_fields():
    body = {
        "contextNodeMappings": [
            {
                "contextNodeMappingId": "11b",
                # missing contextNodeId, sObjectName, mappedContextNodeId
                "attributeMappings": {"contextAttributeMappings": []},
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(body)
    paths = {v["path"] for v in violations}
    check("missing contextNodeId flagged",
          "contextNodeMappings[0].contextNodeId" in paths)
    check("missing sObjectName flagged",
          "contextNodeMappings[0].sObjectName" in paths)
    check("missing mappedContextNodeId flagged",
          "contextNodeMappings[0].mappedContextNodeId" in paths)


def test_validate_shape_ignores_post_intent_node_shell():
    """A POST (no contextNodeMappingId) is not required to carry the full
    PATCH shell — the validator only enforces shell fields when it looks
    like a PATCH intent, so a fresh POST body can still be validated for
    response-only-field violations without false positives."""
    body = {
        "contextNodeMappings": [
            {
                # No contextNodeMappingId -> POST intent
                "contextNodeId":       "11a",
                "sObjectName":         "QuoteLineItem",
                "mappedContextNodeId": "11a",
                "attributeMappings": {"contextAttributeMappings": []},
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(
        body, require_node_shell=False,
    )
    check("POST intent skips shell-required-field checks", violations == [])


def test_validate_shape_flags_response_only_attribute_fields():
    body = {
        "contextNodeMappings": [
            {
                "contextNodeId":        "11a",
                "contextNodeMappingId": "11b",
                "sObjectName":          "QuoteLineItem",
                "mappedContextNodeId":  "11a",
                "attributeMappings": {
                    "contextAttributeMappings": [
                        {
                            "contextAttributeId":         "11c",
                            "contextInputAttributeName":  "MyAttr__c",
                            # response-only offenders below
                            "baseReference":              "std/…",
                            "contextAttributeName":       "MyAttr__c",
                            "parentNodeMappingId":        "11b",
                            "mappedField":                "Description",
                            "contextAttrHydrationDetailList": [{}],
                        }
                    ]
                },
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(body)
    flagged_leaves = {v["path"].rsplit(".", 1)[-1] for v in violations}
    check("baseReference flagged", "baseReference" in flagged_leaves)
    check("contextAttributeName flagged", "contextAttributeName" in flagged_leaves)
    check("parentNodeMappingId flagged", "parentNodeMappingId" in flagged_leaves)
    check("mappedField (SObject REST) flagged", "mappedField" in flagged_leaves)
    check("flat contextAttrHydrationDetailList flagged",
          "contextAttrHydrationDetailList" in flagged_leaves)
    check("each violation carries a rule string",
          all(isinstance(v.get("rule"), str) and v["rule"] for v in violations))


def test_validate_shape_flags_non_dict_payload():
    violations = _apply.validate_node_mapping_patch_shape(["not", "a", "dict"])
    check("non-dict payload flagged",
          len(violations) == 1 and violations[0]["path"] == "<root>")


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
