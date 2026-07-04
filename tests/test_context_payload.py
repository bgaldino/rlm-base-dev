#!/usr/bin/env python3
"""Unit tests for scripts.context_service._payload and _model.

Self-contained — no pytest required (matches this repo's lightweight test
convention; see tests/test_expression_set_schema.py). Run from the repo root
with base Python:

    python tests/test_context_payload.py

Exits 0 when all checks pass, 1 otherwise.

Why these two modules: both are **import-only** (no CLI, no network) and carry
the drift-prone shaping logic. ``_payload`` is a byte-parity port of the CCI
task's Connect/SObject payload builders — nothing else pins that contract.
``_model`` normalizes a Connect GET into a comparable model and inverts it back
to plan JSON; its relationship-traversal handling (descending
``childDetails`` to the terminal source field, and reading ``sObjectDomain``
rather than ``objectName``) is subtle enough to warrant a locked round-trip.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The modules bootstrap their siblings with a bare ``import`` off their own
# directory, so put that directory on the path for a standalone import.
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "context_service"))

import _payload  # noqa: E402
import _model  # noqa: E402

RESULTS = []


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


# ----------------------------------------------------------------------
# Fixtures — a Connect GET detail snapshot (connect/context-definitions/<id>)
# ----------------------------------------------------------------------

def _detail_with_attr(node_name, attr_name, attr_id, node_id="11oX"):
    """A minimal GET detail carrying one node + one attribute (version 0).

    Node attributes live under ``node["attributes"]`` (a list, or the
    ``{"contextAttributes": [...]}`` wrapper) — that is the key both
    ``_client.node_attributes`` and ``_payload._node_attrs`` read; an attribute
    parked anywhere else is invisible to the resolvers.
    """
    return {
        "contextDefinitionVersionList": [
            {
                "contextNodes": [
                    {
                        "name": node_name,
                        "contextNodeId": node_id,
                        "attributes": [
                            {"name": attr_name, "contextAttributeId": attr_id,
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"}
                        ],
                        "childNodes": [],
                    }
                ]
            }
        ]
    }


def _traversal_get():
    """A GET whose hydration nests a traversal terminal under childDetails.

    Outer detail = the lookup hop (QuoteLineItem.Product2); the child detail =
    the terminal source field (Product2.ProductCode). This is the exact shape
    the model must descend and read via ``sObjectDomain`` (not ``objectName``).
    """
    return {
        "developerName": "RLM_TraversalProbeContext",
        "isActive": True,
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "SalesTransactionItem",
                        "contextNodeId": "11oT",
                        "contextAttributes": [
                            {"name": "ProductCode__c", "contextAttributeId": "11nT",
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"}
                        ],
                        "childNodes": [],
                    }
                ],
                "contextMappings": [
                    {
                        "name": "QuoteLineEntitiesMapping",
                        "isDefault": True,
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "SalesTransactionItem",
                                "sObjectName": "QuoteLineItem",
                                "attributeMappings": [
                                    {
                                        "contextAttributeName": "ProductCode__c",
                                        "contextAttrHydrationDetailList": [
                                            {
                                                "sObjectDomain": "QuoteLineItem",
                                                "queryAttribute": "Product2",
                                                "childDetails": [
                                                    {
                                                        "sObjectDomain": "Product2",
                                                        "queryAttribute": "ProductCode",
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


# ----------------------------------------------------------------------
# _payload — build_create_payload allow-list
# ----------------------------------------------------------------------

def test_create_payload_alphanumeric_name():
    p = _payload.build_create_payload(
        {"developerName": "RLM_FooContext", "label": "My Ctx (v2)!"}
    )
    check("create name is stripped to alphanumerics", p["name"] == "MyCtxv2")
    check("create payload carries developerName", p["developerName"] == "RLM_FooContext")


def test_create_payload_allow_list_passthrough():
    p = _payload.build_create_payload({
        "developerName": "RLM_FooContext",
        "label": "Foo",
        "description": "d",
        "baseReference": "SalesTransactionContext__stdctx",
        "contextType": "Standard",
    })
    check("allow-listed 'description' passes through", p.get("description") == "d")
    check(
        "allow-listed 'baseReference' passes through",
        p.get("baseReference") == "SalesTransactionContext__stdctx",
    )


def test_create_payload_drops_unknown_and_banned_keys():
    p = _payload.build_create_payload({
        "developerName": "RLM_FooContext",
        "label": "Foo",
        "primaryDomainObject": "Quote",   # banned (JSON_PARSER_ERROR on the endpoint)
        "somethingRandom": "x",           # not on the allow-list
    })
    check("banned primaryDomainObject omitted", "primaryDomainObject" not in p)
    check("non-allow-listed key omitted", "somethingRandom" not in p)


# ----------------------------------------------------------------------
# _payload — resolve_attributes_by_name idempotency
# ----------------------------------------------------------------------

def test_resolve_attributes_skips_existing():
    detail = _detail_with_attr("SalesTransaction", "RampMode__c", "11nExisting")
    # An attribute that already exists on the definition must be skipped.
    out = _payload.resolve_attributes_by_name(
        [{"nodeName": "SalesTransaction", "name": "RampMode__c"}], detail
    )
    check("existing attribute is not re-POSTed (idempotent)", out == [])


def test_resolve_attributes_emits_new():
    detail = _detail_with_attr("SalesTransaction", "RampMode__c", "11nExisting")
    out = _payload.resolve_attributes_by_name(
        [{"nodeName": "SalesTransaction", "name": "NewAttr__c",
          "dataType": "NUMBER", "fieldType": "OUTPUT"}],
        detail,
    )
    check("new attribute yields one payload row", len(out) == 1)
    check("new attribute carries resolved parent node id",
          out and out[0].get("contextNodeId") == "11oX")
    check("new attribute preserves dataType/fieldType",
          out and out[0].get("dataType") == "NUMBER" and out[0].get("fieldType") == "OUTPUT")


def test_resolve_attributes_skips_unresolved_node():
    detail = _detail_with_attr("SalesTransaction", "RampMode__c", "11nExisting")
    logged = []
    out = _payload.resolve_attributes_by_name(
        [{"nodeName": "NoSuchNode", "name": "X__c"}], detail, logger=logged.append
    )
    check("attribute on an unresolved node is skipped", out == [])
    check("unresolved node is logged", any("NoSuchNode" in m for m in logged))


# ----------------------------------------------------------------------
# _model — hydration traversal (the childDetails / sObjectDomain fix)
# ----------------------------------------------------------------------

def test_hydration_hops_descends_child_details():
    detail = {
        "sObjectDomain": "QuoteLineItem",
        "queryAttribute": "Product2",
        "childDetails": [
            {"sObjectDomain": "Product2", "queryAttribute": "ProductCode"}
        ],
    }
    hops = _model._hydration_hops(detail, node_sobject="QuoteLineItem")
    check(
        "hydration hops include the lookup hop",
        "QuoteLineItem.Product2" in hops,
    )
    check(
        "hydration hops descend to the terminal traversal field",
        "Product2.ProductCode" in hops,
    )


def test_hydration_reads_sobject_domain_not_object_name():
    # The live GET uses sObjectDomain; a single-hop with only queryAttribute must
    # fall back to the node's SObject, not silently drop the field.
    hops = _model._hydration_hops(
        {"queryAttribute": "AccountId"}, node_sobject="Quote"
    )
    check("single-hop falls back to node SObject", hops == ["Quote.AccountId"])


def test_normalize_definition_surfaces_traversal_field():
    model = _model.normalize_definition(_traversal_get())
    mapping = model["mappings"]["QuoteLineEntitiesMapping"]
    attr = mapping["nodes"]["SalesTransactionItem"]["attributes"]["ProductCode__c"]
    check(
        "normalized model carries the full traversal hop chain",
        "Product2.ProductCode" in attr["hydration"],
    )


# ----------------------------------------------------------------------
# _model — GET -> plan round-trip
# ----------------------------------------------------------------------

def test_model_to_plan_round_trips_traversal():
    model = _model.normalize_definition(_traversal_get())
    plan = _model.model_to_plan(model)
    check("round-tripped plan keeps developerName",
          plan.get("developerName") == "RLM_TraversalProbeContext")
    check("round-tripped plan is active", plan.get("activate") is True)

    rules = plan.get("mappingRules") or []
    rule = next((r for r in rules if r.get("contextAttribute") == "ProductCode__c"), None)
    check("round-tripped plan emits the mapping rule for the attribute", rule is not None)
    # The terminal traversal field must reconstruct into childSObject/childSObjectField.
    check(
        "round-trip reconstructs the traversal terminal (childSObject/Field)",
        rule is not None
        and rule.get("childSObject") == "Product2"
        and rule.get("childSObjectField") == "ProductCode",
    )


def test_model_to_plan_output_lints_clean():
    # The delta a patch emits must lint with 0 errors — otherwise patch_context
    # would produce un-appliable plans. This mirrors patch_context: ``include``
    # scopes the output to only the drifted artifacts (here, the one mapping
    # rule). An empty set for a category means "emit nothing from it"; a category
    # omitted from ``include`` means "emit everything", so pass empty sets for
    # nodes/attributes/tags to isolate the mapping delta (inherited nodes like
    # SalesTransactionItem would otherwise be emitted and — correctly — trip the
    # __c node-name lint, which is why the export path selects a subset).
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "context_service"))
    import validate_context_plan as V

    model = _model.normalize_definition(_traversal_get())
    flat_key = "QuoteLineEntitiesMapping/SalesTransactionItem/ProductCode__c"
    plan = _model.model_to_plan(
        model,
        include={"nodes": set(), "attributes": set(), "tags": set(),
                 "mappings": {flat_key}},
    )
    plan.pop("_caveats", None)
    check("patch delta emits exactly the selected mapping rule",
          len(plan.get("mappingRules") or []) == 1)
    check("patch delta emits no node/attribute/tag defs",
          not any(k in plan for k in
                  ("contextNodeDefinitions", "contextAttributesByName", "contextTagsByName")))
    result = V.PlanResult(path="<roundtrip>")
    V._validate_plan_object(plan, result, "roundtrip")
    check(
        "patch delta lints with 0 errors",
        not result.errors,
    )


# ----------------------------------------------------------------------

def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} payload/model test groups...\n")
    for t in tests:
        t()
    print()
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
