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
  * ``diff_context`` CONTEXT-mapping comparison — the name(plan)-vs-ID(org)
    ``mappedContextDefinitionId`` is excluded from equality (P6), so a CONTEXT
    mapping no longer reports perpetual ``~ changed`` drift, while a genuine
    SObject/hydration change on the row is still detected.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import scripts.context_service._apply as _apply  # noqa: E402
import scripts.context_service._client as _client  # noqa: E402
import scripts.context_service._delete as _delete  # noqa: E402
import scripts.context_service._model as _model  # noqa: E402
import scripts.context_service._mutate as _mutate  # noqa: E402
import scripts.context_service._payload as _payload  # noqa: E402
import scripts.context_service.definition.diff_context as diff_context  # noqa: E402

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


class CamDropTransport(RecordingTransport):
    """A RecordingTransport whose ContextAttributeMapping POST returns **no id**
    (empty body), simulating the silent CAM-create failure that would otherwise
    drop the rule's traversal hydration while the run still reported success."""

    def sobject(self, method, sobject, record_id=None, body=None, *, dry_run=None):
        if method == "POST" and sobject == "ContextAttributeMapping":
            self.sobjects.append((method, sobject, record_id, body))
            return {}  # no "id"/"Id" → _record_id returns None
        return super().sobject(method, sobject, record_id, body, dry_run=dry_run)


def test_traversal_raises_when_cam_post_returns_no_id():
    # A transient CAM-create failure (no id) used to be logged-and-skipped, so the
    # run reported success with the traversal hydration silently missing. It must
    # now raise a summarizing ContextClientError (same class as the A2/_mutate fix).
    t = CamDropTransport()  # all probes empty → create path runs; CAM POST drops id
    raised = False
    msg = ""
    try:
        _applier(t)._apply_traversal_hydration([_rule()], _detail())
    except _client.ContextClientError as exc:
        raised = True
        msg = str(exc)
    check("a CAM POST that returns no id raises ContextClientError", raised)
    if raised:
        check("the error names the dropped rule's attribute", "RampMode__c" in msg)
        check("the error points at re-running to repair", "re-run" in msg.lower())


def test_traversal_raises_when_hydration_post_returns_no_id():
    # The child/parent ContextAttrHydrationDetail POST returning no id is the same
    # silent-drop class — it too must surface, not report success.
    t = HydrationDropTransport()  # CAM POST gets a real id; hydration POST drops it
    raised = False
    msg = ""
    try:
        _applier(t)._apply_traversal_hydration([_rule()], _detail())
    except _client.ContextClientError as exc:
        raised = True
        msg = str(exc)
    check("a hydration-detail POST that returns no id raises ContextClientError",
          raised)
    if raised:
        check("the hydration-drop error names the dropped rule", "RampMode__c" in msg)


def test_traversal_reports_all_dropped_rules_together():
    # Two rules both fail their CAM create → one summarizing error names BOTH, and
    # the loop did not abort after the first (it kept going per-rule).
    t = CamDropTransport()
    detail = _detail()
    nm = detail["contextDefinitionVersionList"][0]["contextMappings"][0][
        "contextNodeMappings"][0]
    nm["attributeMappings"] = [
        {"contextAttributeName": "A__c", "contextAttributeId": "11n1"},
        {"contextAttributeName": "B__c", "contextAttributeId": "11n2"},
    ]
    msg = ""
    try:
        _applier(t)._apply_traversal_hydration([_rule("A__c"), _rule("B__c")], detail)
    except _client.ContextClientError as exc:
        msg = str(exc)
    check("both dropped rules are named in one summary error",
          "A__c" in msg and "B__c" in msg)
    posted_cams = [s for s in t.sobjects if s[1] == _apply.ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING]
    check("the loop attempted BOTH CAM POSTs (did not abort on the first drop)",
          len(posted_cams) == 2)


def test_traversal_dry_run_never_raises_on_no_id():
    # Under dry-run no id is expected (nothing is really POSTed), so the no-id
    # guard must NOT fire — dry-run only logs.
    t = CamDropTransport(dry_run=True)
    raised = False
    try:
        _applier(t)._apply_traversal_hydration([_rule()], _detail())
    except _client.ContextClientError:
        raised = True
    check("dry-run does not raise on a no-id POST", not raised)


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
    other sibling without the merge fix (P2).

    Mirrors what the real builder (``_payload.translate_mapping_rules``) emits: the
    node mapping carries the four required shell fields (``contextNodeId``,
    ``contextNodeMappingId``, ``sObjectName``, ``mappedContextNodeId``) and the
    caller's attribute row uses the writable ``contextInputAttributeName`` +
    ``hydrationDetails`` — NOT the response-only ``contextAttributeName`` /
    ``mappedField``. This keeps the fixture inside the PATCH accept-shape so the
    pre-flight block does not (correctly) refuse it."""
    return {
        "contextMappings": [
            {
                "contextMappingId": "11j1",
                "contextNodeMappings": [
                    {
                        "contextNodeName": "SalesTransaction",
                        "contextNodeId": "11nST",
                        "contextNodeMappingId": "11b1",
                        "sObjectName": "Quote",
                        "mappedContextNodeId": "11mcST",
                        "attributeMappings": [
                            {"contextAttributeId": "11n1",
                             "contextInputAttributeName": "RampMode__c",
                             "hydrationDetails": {
                                 "contextAttrHydrationDetails": [
                                     {"sObjectDomain": "Quote",
                                      "queryAttribute": "RampModeAlias__c"}
                                 ]
                             }},
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


def test_apply_mapping_updates_patch_shape_violation_raises_before_wire():
    # A PATCH whose node mapping is missing the required shell fields is a shape
    # violation on the whole-body-replace endpoint. Since the merge has already
    # folded siblings in, sending it risks silent data loss — the applier must
    # RAISE and issue no PATCH, not log-and-send.
    bad_payload = {
        "contextMappings": [
            {
                "contextMappingId": "11j1",
                "contextNodeMappings": [
                    {
                        # existing node mapping (PATCH intent) but missing
                        # contextNodeId / sObjectName / mappedContextNodeId
                        "contextNodeName": "SalesTransaction",
                        "contextNodeMappingId": "11b1",
                        "attributeMappings": [
                            {"contextAttributeId": "11n1",
                             "contextInputAttributeName": "RampMode__c"},
                        ],
                    }
                ],
            }
        ]
    }
    t = RecordingTransport()
    raised = False
    try:
        _applier(t)._apply_mapping_updates(
            "11O1", bad_payload, detail=_detail_with_siblings()
        )
    except _client.ContextClientError as exc:
        raised = True
        msg = str(exc)
    check("a malformed PATCH body raises ContextClientError", raised)
    if raised:
        check("the error names the destructive-PATCH refusal",
              "Refusing destructive node-mapping PATCH" in msg)
    patches = [r for r in t.requests
               if r[0] == "PATCH" and "context-node-mappings" in r[1]]
    check("no PATCH was sent to the wire after a shape violation", not patches)


def test_apply_mapping_updates_post_shape_violation_does_not_raise():
    # The block is PATCH-only: a POST (new node mapping) with the same missing
    # shell fields is fine (the platform has no siblings to lose and rejects a
    # bad POST loudly), so it must NOT raise.
    payload = {
        "contextMappings": [
            {
                "contextMappingId": "11j1",
                "contextNodeMappings": [
                    {   # no contextNodeMappingId → POST branch
                        "contextNodeName": "SalesTransaction",
                        "attributeMappings": [
                            {"contextAttributeId": "11n9",
                             "contextInputAttributeName": "New__c"},
                        ],
                    }
                ],
            }
        ]
    }
    t = RecordingTransport()
    raised = False
    try:
        _applier(t)._apply_mapping_updates("11O1", payload, detail=_detail_with_siblings())
    except _client.ContextClientError:
        raised = True
    check("a POST with missing shell fields does not raise (POST is log-only)",
          not raised)


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


def _active_detail_with_transient_drift():
    """An ACTIVE definition whose ContextAttribute needs an IsTransient flip.

    build_create_payload allow-lists ``isActive`` and ``sourceDefinitionId``
    (clone of an active def), so ``_run_create_flow`` can legitimately run
    against an already-active version. This fixture drives the transient block:
    the attribute exists (so resolve_attributes_by_name skips the POST) but its
    IsTransient=False drifts from the plan's isTransient:true, so
    transient_updates yields one SObject PATCH.
    """
    return {
        "isActive": True,
        "contextDefinitionVersionList": [{
            "isActive": True,
            "contextMappings": [],
            "contextNodes": [{
                "name": "SalesTransaction",
                "contextNodeId": "11q1",
                "attributes": {"contextAttributes": [
                    {"name": "RampMode__c", "contextAttributeId": "11n1",
                     "isTransient": False},
                ]},
            }],
        }],
    }


def test_create_flow_guards_transient_patch_on_active_def():
    # Regression for the create-vs-additive drift: _run_create_flow's transient
    # sync was NOT wrapped by _guard_active_for_patch, so a create with
    # isActive:true (or clone-of-active) would hit a raw RECORD_UPDATE_FAILED
    # instead of the actionable guard message. With _deactivate_first False the
    # guard must REFUSE before issuing the (platform-blocked) SObject PATCH.
    t = RecordingTransport()
    applier = _applier(t)
    applier._deactivate_first = False
    active = _active_detail_with_transient_drift()
    applier.fetch_detail = lambda ctx: active  # type: ignore
    plan = {"contextAttributesByName": [
        {"nodeName": "SalesTransaction", "name": "RampMode__c", "isTransient": True},
    ]}
    raised = False
    try:
        applier._run_create_flow(
            "11O1", "RLM_Demo", plan,
            translate_plan=False, activate=False, verify=False, created=True,
        )
    except _client.ContextClientError as exc:
        raised = "ACTIVE" in str(exc) and "deactivate_before" in str(exc)
    check("create flow on active def → transient sync is guarded (refuses)", raised)
    check("create flow guard refusal → no IsTransient SObject PATCH issued",
          not any(s[1] == "ContextAttribute" for s in t.sobjects))


def test_create_flow_transient_patch_unguarded_on_inactive_def():
    # The guard is a no-op on the normal (inactive, freshly-created) path: the
    # transient SObject PATCH still goes out exactly as before.
    t = RecordingTransport()
    applier = _applier(t)
    applier._deactivate_first = False
    detail = _active_detail_with_transient_drift()
    detail["isActive"] = False
    detail["contextDefinitionVersionList"][0]["isActive"] = False
    applier.fetch_detail = lambda ctx: detail  # type: ignore
    plan = {"contextAttributesByName": [
        {"nodeName": "SalesTransaction", "name": "RampMode__c", "isTransient": True},
    ]}
    applier._run_create_flow(
        "11O1", "RLM_Demo", plan,
        translate_plan=False, activate=False, verify=False, created=True,
    )
    patch = next((s for s in t.sobjects
                  if s[0] == "PATCH" and s[1] == "ContextAttribute"), None)
    check("create flow on inactive def → IsTransient PATCH still issued",
          patch is not None and patch[3] == {"IsTransient": True})


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
    # The three *structural* shell fields (contextNodeId, contextNodeMappingId,
    # sObjectName) are required on every PATCH node mapping, root or child.
    # mappedContextNodeId is conditional (child-only) — covered separately below.
    body = {
        "contextNodeMappings": [
            {
                "contextNodeMappingId": "11b",
                # missing contextNodeId, sObjectName
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


def test_validate_shape_skips_mapped_node_id_without_root_info():
    # Without root_node_ids the validator cannot tell root from child, so it
    # must NOT flag a null mappedContextNodeId — that false positive is exactly
    # the bug that fatally refused a valid additive root-node PATCH (2026-07-08).
    body = {
        "contextNodeMappings": [
            {
                "contextNodeId":        "11nST",
                "contextNodeMappingId": "11b",
                "sObjectName":          "Quote",
                # mappedContextNodeId omitted (null) — legit for a root node
                "attributeMappings": {"contextAttributeMappings": []},
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(body)
    paths = {v["path"] for v in violations}
    check("null mappedContextNodeId not flagged when root/child is unknown",
          "contextNodeMappings[0].mappedContextNodeId" not in paths)


def test_validate_shape_exempts_root_node_null_mapped_node_id():
    # A ROOT node mapping (its contextNodeId is in root_node_ids) with a null
    # mappedContextNodeId is valid — the platform stores null there. No flag.
    body = {
        "contextNodeMappings": [
            {
                "contextNodeId":        "11nST",
                "contextNodeMappingId": "11b",
                "sObjectName":          "Quote",
                "attributeMappings": {"contextAttributeMappings": []},
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(
        body, root_node_ids={"11nST"})
    paths = {v["path"] for v in violations}
    check("root node's null mappedContextNodeId is exempt",
          "contextNodeMappings[0].mappedContextNodeId" not in paths)


def test_validate_shape_flags_child_node_missing_mapped_node_id():
    # A CHILD node mapping (its contextNodeId is NOT in root_node_ids) must
    # carry a non-null mappedContextNodeId pointing at its parent — omitting it
    # yields INVALID_DEFINITION, so flag it.
    body = {
        "contextNodeMappings": [
            {
                "contextNodeId":        "11nQLI",
                "contextNodeMappingId": "11b",
                "sObjectName":          "QuoteLineItem",
                # mappedContextNodeId omitted — invalid for a child node
                "attributeMappings": {"contextAttributeMappings": []},
            }
        ]
    }
    violations = _apply.validate_node_mapping_patch_shape(
        body, root_node_ids={"11nST"})  # QLI id not in the root set → child
    paths = {v["path"] for v in violations}
    check("child node's missing mappedContextNodeId flagged",
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
# P6 — CONTEXT mapping no longer reports perpetual name<->ID drift
# --------------------------------------------------------------------------- #

def _context_plan():
    """A repo plan authoring a CONTEXT mapping rule the way live plans do:
    ``sourceContextNode``/``sourceContextAttribute`` set, no
    ``mappedContextDefinitionName`` (mirrors ConstraintEngineNodeStatus)."""
    return {
        "developerName": "RLM_CtxTest",
        "activate": True,
        "mappingRules": [
            {
                "mappingName": "AssetToSalesTransactionMapping",
                "contextNode": "SalesTransactionItem",
                "contextAttribute": "ConstraintEngineNodeStatus__c",
                "mappingType": "CONTEXT",
                "sourceContextNode": "AssetActionSource",
                "sourceContextAttribute": "AssetConstraintEngineNodeStatus__c",
            }
        ],
    }


def _context_org_get():
    """The org GET for the same definition: the CONTEXT node mapping carries the
    org-scoped ``mappedContextDefinitionId`` (an ``11O…`` ID) — the value that
    used to force a perpetual ``~ changed``."""
    return {
        "developerName": "RLM_CtxTest",
        "isActive": True,
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "SalesTransactionItem",
                        "contextAttributes": [
                            {"name": "ConstraintEngineNodeStatus__c",
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"},
                        ],
                        "childNodes": [],
                    }
                ],
                "contextMappings": [
                    {
                        "name": "AssetToSalesTransactionMapping",
                        "isDefault": False,
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "SalesTransactionItem",
                                "sObjectName": None,
                                "mappedContextDefinitionId": "11O5F000000ABCDUAO",
                                "attributeMappings": [
                                    {
                                        "contextAttributeName":
                                            "ConstraintEngineNodeStatus__c",
                                        "contextAttrHydrationDetailList": [],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_context_mapping_no_perpetual_drift():
    plan_model = _model.normalize_plan(_context_plan())
    org_model = _model.normalize_definition(_context_org_get())

    flat_key = ("AssetToSalesTransactionMapping/SalesTransactionItem/"
                "ConstraintEngineNodeStatus__c")
    plan_flat = diff_context._flatten_mapping_attrs(plan_model["mappings"])
    org_flat = diff_context._flatten_mapping_attrs(org_model["mappings"])
    check("plan side stores name-slot (None) for the CONTEXT ref",
          plan_flat[flat_key]["mappedContextDefinitionId"] is None)
    check("org side stores the raw 11O… ID for the CONTEXT ref",
          org_flat[flat_key]["mappedContextDefinitionId"] == "11O5F000000ABCDUAO")

    diff = diff_context.diff_models(plan_model, org_model)
    changed_keys = {c["key"] for c in diff["mappings"]["changed"]}
    check("CONTEXT mapping does NOT report perpetual ~changed drift (P6)",
          flat_key not in changed_keys)
    check("no spurious mapping drift at all for the CONTEXT row",
          not diff["mappings"]["changed"])


def test_context_mapping_real_sobject_change_still_detected():
    """The exclusion is narrow: a genuine SObject/hydration change on a mapping
    row must still surface (proves we didn't blunt the diff wholesale)."""
    left = {"sObject": "Quote", "hydration": ["Quote.Name"],
            "mappedContextDefinitionId": None}
    right = {"sObject": "Order", "hydration": ["Order.Name"],
             "mappedContextDefinitionId": None}
    check("differing sObject is still a change",
          diff_context._mapping_attr_differs(left, right))

    same_but_diff_ref_left = {"sObject": None, "hydration": [],
                              "mappedContextDefinitionId": None}
    same_but_diff_ref_right = {"sObject": None, "hydration": [],
                               "mappedContextDefinitionId": "11O…"}
    check("differing CONTEXT ref alone is NOT a change",
          not diff_context._mapping_attr_differs(
              same_but_diff_ref_left, same_but_diff_ref_right))


# --------------------------------------------------------------------------- #
# collect_root_node_ids — root vs child node id set
# --------------------------------------------------------------------------- #

def _detail_root_and_child():
    """A definition with a root node (SalesTransaction) and a child node
    (SalesTransactionItem), plus a matching mapping/node-mapping so the
    add-mapping op can resolve ids and sObjectName."""
    return {
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "SalesTransaction",
                        "contextNodeId": "11nST",
                        "attributes": {"contextAttributes": [
                            {"name": "TotalCost__c", "contextAttributeId": "11aTC"},
                        ]},
                        "childNodes": {"contextNodes": [
                            {
                                "name": "SalesTransactionItem",
                                "contextNodeId": "11nSTI",
                                "attributes": {"contextAttributes": [
                                    {"name": "Quantity", "contextAttributeId": "11aQ"},
                                ]},
                                "childNodes": {"contextNodes": []},
                            }
                        ]},
                    }
                ],
                "contextMappings": [
                    {
                        "name": "QuoteEntitiesMapping",
                        "contextMappingId": "11j1",
                        "intents": ["HYDRATION", "PERSISTENCE"],
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "SalesTransaction",
                                "contextNodeId": "11nST",
                                "contextNodeMappingId": "11bST",
                                "sObjectName": "Quote",
                                "mappedContextNodeId": None,
                                "attributeMappings": [],
                            },
                            {
                                "contextNodeName": "SalesTransactionItem",
                                "contextNodeId": "11nSTI",
                                "contextNodeMappingId": "11bSTI",
                                "sObjectName": "QuoteLineItem",
                                "mappedContextNodeId": "11nST",
                                "attributeMappings": [
                                    {"contextAttributeName": "Quantity",
                                     "contextAttributeId": "11aQ",
                                     "contextAttrHydrationDetailList": [
                                         {"sObjectDomain": "QuoteLineItem",
                                          "queryAttribute": "Quantity"}]},
                                ],
                            },
                        ],
                    }
                ],
            }
        ]
    }


def test_collect_root_node_ids_returns_only_top_level():
    roots = _payload.collect_root_node_ids(_detail_root_and_child())
    check("root SalesTransaction id is in the set", "11nST" in roots)
    check("child SalesTransactionItem id is NOT in the set", "11nSTI" not in roots)
    check("exactly one root", len(roots) == 1)


def test_collect_root_node_ids_empty_detail():
    check("empty detail → empty root set", _payload.collect_root_node_ids({}) == set())


# --------------------------------------------------------------------------- #
# add-mapping mutator op — granular, sibling-safe, active-allowed
# --------------------------------------------------------------------------- #

def _mutator(transport):
    return _mutate.ContextMutator(transport)


def test_add_mapping_op_rules_are_pure_insert():
    rules = _mutate.OP_RULES["add-mapping"]
    check("add-mapping does not refuse inherited (additive binding)",
          rules["refuses_inherited"] is False)
    check("add-mapping runs on an active version (pure insert)",
          rules["requires_inactive"] is False)


def test_add_mapping_plan_resolves_root_node_binding():
    detail = _detail_root_and_child()
    change = _mutator(RecordingTransport()).plan_add_mapping(
        detail, "SalesTransaction.TotalCost__c",
        "QuoteEntitiesMapping", "RLM_TotalCost__c")
    check("target resolved to the root attribute",
          change["target"] == "SalesTransaction.TotalCost__c")
    check("node mapping id resolved from the snapshot",
          change["node_mapping_id"] == "11bST")
    check("sObject taken from the node mapping (Quote), not the caller",
          change["sObject"] == "Quote")
    check("field is the caller-supplied SObject field",
          change["field"] == "RLM_TotalCost__c")
    check("not a no-op (attribute is unbound on this mapping)",
          change["noop"] is False)


def test_add_mapping_execute_posts_cam_then_hydration():
    detail = _detail_root_and_child()
    t = RecordingTransport()
    mut = _mutator(t)
    change = mut.plan_add_mapping(
        detail, "SalesTransaction.TotalCost__c",
        "QuoteEntitiesMapping", "RLM_TotalCost__c")
    summary = mut.execute_add_mapping(change)
    posts = [s for s in t.sobjects if s[0] == "POST"]
    check("exactly two SObject POSTs (CAM + hydration)", len(posts) == 2)
    cam = next((s for s in posts if s[1] == "ContextAttributeMapping"), None)
    hyd = next((s for s in posts if s[1] == "ContextAttrHydrationDetail"), None)
    check("ContextAttributeMapping POSTed", cam is not None)
    check("ContextAttrHydrationDetail POSTed", hyd is not None)
    if cam:
        body = cam[3]
        check("CAM carries the resolved node-mapping id",
              body.get("ContextNodeMappingId") == "11bST")
        check("CAM carries the attribute id",
              body.get("ContextAttributeId") == "11aTC")
        check("CAM ContextInputAttributeName is the bare attr name",
              body.get("ContextInputAttributeName") == "TotalCost__c")
    if hyd:
        body = hyd[3]
        check("hydration ObjectName is the node-mapping sObject (Quote)",
              body.get("ObjectName") == "Quote")
        check("hydration QueryAttribute is the target field",
              body.get("QueryAttribute") == "RLM_TotalCost__c")
        check("hydration chained to the created CAM keeper id",
              body.get("ContextAttributeMappingId") == cam_keeper_id(t))
    check("summary reports changed=True", summary.get("changed") is True)
    # No whole-body PATCH — the sibling-loss surface is never touched.
    check("no node-mapping PATCH issued (sibling-safe)",
          not any(r[0] == "PATCH" and "context-node-mappings" in r[1]
                  for r in t.requests))


def cam_keeper_id(t):
    """Fake id the RecordingTransport returned for the ContextAttributeMapping
    POST (first POST -> 'fake1')."""
    return "fake1"


def test_add_mapping_is_idempotent_when_already_bound():
    # Binding Quantity (already mapped on the child node mapping) is a no-op.
    detail = _detail_root_and_child()
    t = RecordingTransport()
    mut = _mutator(t)
    change = mut.plan_add_mapping(
        detail, "SalesTransactionItem.Quantity",
        "QuoteEntitiesMapping", "Quantity")
    check("plan detects the existing binding", change["noop"] is True)
    check("existing binding is described",
          "QuoteLineItem.Quantity" in (change["existing_binding"] or ""))
    summary = mut.execute_add_mapping(change)
    check("no-op execute reports changed=False", summary.get("changed") is False)
    check("no-op execute issues zero POSTs",
          not [s for s in t.sobjects if s[0] == "POST"])


def _detail_with_incomplete_cam():
    """Root-and-child detail where the root node mapping already carries a
    ``ContextAttributeMapping`` for TotalCost__c that has an id but **no**
    ``contextAttrHydrationDetailList`` — the shape left behind when a prior
    add-mapping run died between the CAM POST and the hydration POST."""
    detail = _detail_root_and_child()
    root_nm = detail["contextDefinitionVersionList"][0]["contextMappings"][0][
        "contextNodeMappings"][0]  # SalesTransaction / Quote / 11bST
    root_nm["attributeMappings"] = [
        {"contextAttributeName": "TotalCost__c",
         "contextAttributeId": "11aTC",
         "contextAttributeMappingId": "11cTC",
         "contextAttrHydrationDetailList": []},
    ]
    return detail


def test_add_mapping_repairs_cam_missing_hydration_detail():
    # A CAM with no source field is NOT a no-op — a retry must finish the
    # binding by POSTing only the missing ContextAttrHydrationDetail against
    # the existing CAM (never a second CAM).
    detail = _detail_with_incomplete_cam()
    t = RecordingTransport()
    mut = _mutator(t)
    change = mut.plan_add_mapping(
        detail, "SalesTransaction.TotalCost__c",
        "QuoteEntitiesMapping", "RLM_TotalCost__c")
    check("incomplete CAM is not reported as a no-op", change["noop"] is False)
    check("incomplete CAM flagged for repair", change.get("repair") is True)
    check("repair carries the existing CAM id", change.get("existing_cam_id") == "11cTC")
    summary = mut.execute_add_mapping(change)
    posts = [s for s in t.sobjects if s[0] == "POST"]
    check("repair POSTs exactly one row (hydration only, no 2nd CAM)", len(posts) == 1)
    check("repair does not POST a ContextAttributeMapping",
          not any(s[1] == "ContextAttributeMapping" for s in posts))
    hyd = next((s for s in posts if s[1] == "ContextAttrHydrationDetail"), None)
    check("repair POSTs the ContextAttrHydrationDetail", hyd is not None)
    if hyd:
        body = hyd[3]
        check("repair hydration chains to the EXISTING CAM id",
              body.get("ContextAttributeMappingId") == "11cTC")
        check("repair hydration ObjectName is the node-mapping sObject (Quote)",
              body.get("ObjectName") == "Quote")
        check("repair hydration QueryAttribute is the target field",
              body.get("QueryAttribute") == "RLM_TotalCost__c")
    check("repair summary reports changed=True", summary.get("changed") is True)
    check("repair summary flags repaired=True", summary.get("repaired") is True)


def test_add_mapping_unresolved_node_mapping_raises():
    detail = _detail_root_and_child()
    raised = False
    try:
        _mutator(RecordingTransport()).plan_add_mapping(
            detail, "SalesTransaction.TotalCost__c",
            "NoSuchMapping", "RLM_TotalCost__c")
    except _mutate.MutatePreflightError:
        raised = True
    check("unresolved mapping/node pair raises MutatePreflightError", raised)


def test_add_mapping_unknown_attribute_raises():
    detail = _detail_root_and_child()
    raised = False
    try:
        _mutator(RecordingTransport()).plan_add_mapping(
            detail, "SalesTransaction.NoSuchAttr__c",
            "QuoteEntitiesMapping", "RLM_Foo__c")
    except _mutate.MutatePreflightError:
        raised = True
    check("unknown attribute raises MutatePreflightError", raised)


# --------------------------------------------------------------------------- #
# A2 (Finding 6) — execute_add_mapping validates the hydration-detail POST
# --------------------------------------------------------------------------- #

class HydrationDropTransport(RecordingTransport):
    """A RecordingTransport whose ContextAttrHydrationDetail POST returns **no
    id** (an empty body), simulating the silent second-POST failure that would
    otherwise leave an orphan CAM and report a phantom ``changed: True``. The
    CAM POST still returns a real fake id so the code reaches the hydration POST.
    """

    def sobject(self, method, sobject, record_id=None, body=None, *, dry_run=None):
        if method == "POST" and sobject == "ContextAttrHydrationDetail":
            self.sobjects.append((method, sobject, record_id, body))
            return {}  # no "id"/"Id" → _record_id returns None
        return super().sobject(method, sobject, record_id, body, dry_run=dry_run)


def test_add_mapping_raises_when_hydration_post_returns_no_id():
    # The CAM POST succeeds (fake id) but the hydration-detail POST returns no id
    # → the binding is only half-created. execute_add_mapping must raise rather
    # than report a phantom success (round-1 Fix #7's orphan-CAM scenario).
    detail = _detail_root_and_child()
    t = HydrationDropTransport()
    mut = _mutator(t)
    change = mut.plan_add_mapping(
        detail, "SalesTransaction.TotalCost__c",
        "QuoteEntitiesMapping", "RLM_TotalCost__c")
    raised = False
    msg = ""
    try:
        mut.execute_add_mapping(change)
    except _mutate.MutatePreflightError as exc:
        raised = True
        msg = str(exc)
    check("hydration-detail POST with no id raises MutatePreflightError", raised)
    check("the error names ContextAttrHydrationDetail",
          "ContextAttrHydrationDetail" in msg)
    check("the error points at the orphan-CAM repair path",
          "repair" in msg.lower() or "--add-mapping" in msg)
    # The CAM was still POSTed (that's the orphan the message warns about).
    check("a ContextAttributeMapping was POSTed before the failure",
          any(s[0] == "POST" and s[1] == "ContextAttributeMapping" for s in t.sobjects))


def test_add_mapping_dry_run_does_not_raise_on_no_id():
    # Under dry-run the transport returns {} for every POST by design; the id
    # validation is gated on ``not self.dry_run`` so a dry-run add-mapping must
    # still report changed=True without raising.
    detail = _detail_root_and_child()
    t = RecordingTransport(dry_run=True)
    mut = _mutator(t)
    change = mut.plan_add_mapping(
        detail, "SalesTransaction.TotalCost__c",
        "QuoteEntitiesMapping", "RLM_TotalCost__c")
    summary = mut.execute_add_mapping(change)
    check("dry-run add-mapping reports changed=True (no id validation)",
          summary.get("changed") is True)
    check("dry-run add-mapping flags dry_run=True", summary.get("dry_run") is True)


# --------------------------------------------------------------------------- #
# B1 (Finding 2) — the mutate guard delegates to the shared _client core
# --------------------------------------------------------------------------- #

def test_mutate_guard_refuses_active_when_not_opted_in():
    # set-transient is requires_inactive → the op-gate passes → the shared body
    # refuses an active version with a MutatePreflightError (its own type).
    t = RecordingTransport()
    mut = _mutator(t)
    raised = False
    msg = ""
    try:
        mut.guard_active_state("set-transient", _active_detail(),
                               context_id="11O1", auto_deactivate=False)
    except _mutate.MutatePreflightError as exc:
        raised = True
        msg = str(exc)
    check("mutate guard raises MutatePreflightError on active + not opted in", raised)
    check("mutate refusal keeps its own message (ACTIVE + --deactivate-first)",
          "ACTIVE" in msg and "--deactivate-first" in msg)
    check("mutate refusal issues no PATCH (refuse, don't deactivate)",
          not any(r[0] == "PATCH" for r in t.requests))


def test_mutate_guard_is_noop_for_pure_insert_op():
    # add-mapping is NOT requires_inactive → the op-gate short-circuits before the
    # shared body, so even an ACTIVE version is returned untouched (adds apply
    # in place on an active version).
    t = RecordingTransport()
    mut = _mutator(t)
    detail = _active_detail()
    out = mut.guard_active_state("add-mapping", detail, context_id="11O1")
    check("add-mapping guard returns the active detail unchanged", out is detail)
    check("add-mapping guard issues no request", not t.requests)


def test_mutate_guard_deactivates_when_opted_in():
    # requires_inactive op + auto_deactivate → the shared body issues the
    # isActive:false PATCH and returns the refreshed (inactive) detail.
    t = RecordingTransport()
    mut = _mutator(t)
    mut.fetch_detail = lambda ctx: _inactive_detail()  # type: ignore
    out = mut.guard_active_state("set-transient", _active_detail(),
                                 context_id="11O1", auto_deactivate=True)
    patch = next(
        (r for r in t.requests if r[0] == "PATCH" and "context-definitions/11O1" in r[1]),
        None,
    )
    check("mutate guard (opted in) issues the isActive:false PATCH",
          patch is not None and patch[2] == {"isActive": "false"})
    check("mutate guard returns the post-deactivate detail",
          out.get("isActive") is False)


def test_delete_guard_refuses_active_with_its_own_type():
    # Delete's trigger is unconditional; on an active version + not opted in it
    # raises DeletePreflightError (distinct type from mutate/apply — the B1
    # decision preserved each module's exception type).
    t = RecordingTransport()
    deleter = _delete.ContextDeleter(t)
    raised = False
    is_delete_type = False
    try:
        deleter.guard_active_state(_active_detail(), context_id="11O1",
                                   auto_deactivate=False)
    except _delete.DeletePreflightError:
        raised = True
        is_delete_type = True
    except Exception:
        raised = True
    check("delete guard raises on active + not opted in", raised)
    check("delete guard raises DeletePreflightError (its own type)", is_delete_type)


def test_delete_guard_is_noop_when_inactive():
    t = RecordingTransport()
    deleter = _delete.ContextDeleter(t)
    out = deleter.guard_active_state(_inactive_detail(), context_id="11O1")
    check("delete guard is a no-op on an inactive version (no request)",
          not t.requests)
    check("delete guard returns the inactive detail unchanged",
          out.get("isActive") is False)


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
