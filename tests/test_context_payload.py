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
sys.path.insert(0, REPO_ROOT)

import scripts.context_service._payload as _payload  # noqa: E402
import scripts.context_service._model as _model  # noqa: E402
import scripts.context_service._client as _client  # noqa: E402

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


def _from_scratch_get():
    """A GET for a from-scratch custom definition (no baseReference).

    Author-chosen node/attribute/tag names that do NOT end with ``__c`` — this is
    legal for a create-new definition (nothing is inherited), and the exported
    plan must re-lint clean, which requires ``create: true`` in the output.
    """
    return {
        "developerName": "RLM_CtxTest_AccountContact",
        "isActive": True,
        "baseReference": None,
        "label": "RLM CtxTest Account Contact",
        "description": "From-scratch Account+Contact test definition.",
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "Account",
                        "contextNodeId": "11oA",
                        "contextAttributes": [
                            {"name": "AccountName", "contextAttributeId": "11nA",
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"},
                        ],
                        "childNodes": [
                            {
                                "name": "Contact",
                                "contextNodeId": "11oC",
                                "parentNodeName": "Account",
                                "contextAttributes": [
                                    {"name": "ContactLastName", "contextAttributeId": "11nC",
                                     "dataType": "STRING", "fieldType": "INPUTOUTPUT"},
                                ],
                                "childNodes": [],
                            }
                        ],
                    }
                ],
                "contextMappings": [
                    {
                        "name": "AccountContactMapping",
                        "isDefault": True,
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "Account",
                                "sObjectName": "Account",
                                "attributeMappings": [
                                    {
                                        "contextAttributeName": "AccountName",
                                        "contextAttrHydrationDetailList": [
                                            {"sObjectDomain": "Account",
                                             "queryAttribute": "Name"}
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


def _nested_no_parentname_get():
    """A from-scratch GET whose child node carries NO ``parentNodeName``.

    The live v67 Context Node GET identifies ancestry by ``childNodes`` nesting
    and ``parentNodeId`` — it does NOT stamp ``parentNodeName`` on the child. A
    normalizer that reads only ``parentNodeName`` off the child sees ``None`` and
    serializes the child as a second root, corrupting the hierarchy on reapply.
    Contact is nested under Account with only ``parentNodeId`` (plus position),
    exactly the documented shape.
    """
    return {
        "developerName": "RLM_CtxTest_NestedNoParentName",
        "isActive": True,
        "baseReference": None,
        "label": "RLM CtxTest Nested",
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "Account",
                        "contextNodeId": "11oA",
                        "contextAttributes": [
                            {"name": "AccountName", "contextAttributeId": "11nA",
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"},
                        ],
                        "childNodes": {
                            "contextNodes": [
                                {
                                    "name": "Contact",
                                    "contextNodeId": "11oC",
                                    # No parentNodeName — only parentNodeId + nesting,
                                    # the real v67 shape.
                                    "parentNodeId": "11oA",
                                    "contextAttributes": [
                                        {"name": "ContactLastName",
                                         "contextAttributeId": "11nC",
                                         "dataType": "STRING",
                                         "fieldType": "INPUTOUTPUT"},
                                    ],
                                    "childNodes": [],
                                }
                            ]
                        },
                    }
                ],
                "contextMappings": [
                    {
                        "name": "AccountContactMapping",
                        "isDefault": True,
                        "contextNodeMappings": [
                            {
                                "contextNodeName": "Account",
                                "sObjectName": "Account",
                                "attributeMappings": [
                                    {
                                        "contextAttributeName": "AccountName",
                                        "contextAttrHydrationDetailList": [
                                            {"sObjectDomain": "Account",
                                             "queryAttribute": "Name"}
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


def _extension_get():
    """A GET for a definition that EXTENDS a standard base (baseReference set)."""
    return {
        "developerName": "RLM_SalesTransactionContext",
        "isActive": True,
        "baseReference": "SalesTransactionContext__stdctx",
        "description": "Extension of Standard Sales Transaction Context Definition",
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {
                        "name": "SalesTransactionItem",
                        "contextNodeId": "11oS",
                        "contextAttributes": [
                            {"name": "CtxTestFlag__c", "contextAttributeId": "11nS",
                             "dataType": "STRING", "fieldType": "INPUTOUTPUT"},
                        ],
                        "childNodes": [],
                    }
                ],
                "contextMappings": [],
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


def test_normalize_plan_traversal_hydration_matches_org():
    # Regression: normalize_plan must record the SAME full hop chain the org-side
    # normalizer (_hydration_hops) produces for a traversal rule, or diff_context
    # reports a permanent "~ changed" mapping after the plan is already applied.
    plan = {
        "developerName": "RLM_TraversalProbeContext",
        "activate": True,
        "mappingRules": [
            {
                "mappingName": "QuoteLineEntitiesMapping",
                "contextNode": "SalesTransactionItem",
                "contextAttribute": "ProductCode__c",
                "mappingType": "SOBJECT",
                "sObject": "QuoteLineItem",
                "sObjectField": "Product2",
                "childSObject": "Product2",
                "childSObjectField": "ProductCode",
            }
        ],
    }
    plan_model = _model.normalize_plan(plan)
    plan_hydration = (plan_model["mappings"]["QuoteLineEntitiesMapping"]
                      ["nodes"]["SalesTransactionItem"]
                      ["attributes"]["ProductCode__c"]["hydration"])
    org_model = _model.normalize_definition(_traversal_get())
    org_hydration = (org_model["mappings"]["QuoteLineEntitiesMapping"]
                     ["nodes"]["SalesTransactionItem"]
                     ["attributes"]["ProductCode__c"]["hydration"])
    check(
        "plan-side traversal hydration records both hops (lookup + terminal)",
        plan_hydration == ["QuoteLineItem.Product2", "Product2.ProductCode"],
    )
    check(
        "plan-side traversal hydration equals the org-side normalization",
        plan_hydration == org_hydration,
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
    import scripts.context_service.definition.validate_context_plan as V

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
# _model — from-scratch export emits create:true and lints clean
# ----------------------------------------------------------------------

def test_from_scratch_export_sets_create_true():
    model = _model.normalize_definition(_from_scratch_get())
    check("model captures absent baseReference as None",
          model.get("baseReference") is None)
    plan = _model.model_to_plan(model)  # whole export (include=None)
    check("from-scratch whole export sets create:true",
          plan.get("create") is True)
    check("from-scratch export carries label for the create name source",
          plan.get("label") == "RLM CtxTest Account Contact")
    check("from-scratch export carries description",
          plan.get("description") == "From-scratch Account+Contact test definition.")
    check("from-scratch export emits author-named node definitions",
          any(n.get("name") == "Contact" and n.get("parentNodeName") == "Account"
              for n in (plan.get("contextNodeDefinitions") or [])))


def test_from_scratch_export_lints_clean():
    # The bug: without create:true the exported plan re-lints as an additive plan
    # against a standard base, firing false __c-suffix errors on author-named
    # nodes/attrs/tags (e.g. AccountName, ContactLastName). With create:true the
    # validator's _is_create_new() suppresses the suffix rule and the plan lints
    # clean — closing the export -> lint -> apply round trip.
    import scripts.context_service.definition.validate_context_plan as V

    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(model)
    plan.pop("_caveats", None)
    result = V.PlanResult(path="<from-scratch>")
    V._validate_plan_object(plan, result, "from-scratch")
    check("from-scratch export lints with 0 errors (create:true suppresses __c rule)",
          not result.errors)


def test_patch_delta_never_sets_create_true():
    # patch_context passes an include dict (even for a from-scratch source) — the
    # emitted delta is additive against an existing definition and must never
    # carry create:true, else re-applying it would try to re-create the def.
    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(
        model,
        include={"nodes": set(), "attributes": {"Account.AccountName"},
                 "mappings": set(), "tags": set()},
    )
    check("patch delta from a from-scratch source does NOT set create:true",
          "create" not in plan)
    check("patch delta does not leak label/description",
          "label" not in plan and "description" not in plan)


def test_empty_patch_delta_not_treated_as_whole_export():
    # An empty include ({} with all-empty sets) is a no-delta patch, NOT a whole
    # export — it must not gain create:true. Guards the include-is-None vs
    # include-is-empty distinction in model_to_plan.
    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(
        model,
        include={"nodes": set(), "attributes": set(),
                 "mappings": set(), "tags": set()},
    )
    check("empty patch include does not set create:true",
          "create" not in plan)


def test_full_extension_export_flags_caveat():
    # A full (non custom-only) export of an extension emits inherited standard
    # artifacts and is not directly appliable; model_to_plan flags it as a caveat
    # rather than emitting create:true.
    model = _model.normalize_definition(_extension_get())
    check("model captures baseReference for an extension",
          model.get("baseReference") == "SalesTransactionContext__stdctx")
    plan = _model.model_to_plan(model)  # whole export
    check("full extension export does NOT set create:true",
          "create" not in plan)
    caveats = plan.get("_caveats") or []
    check("full extension export flags a not-appliable caveat",
          any("not directly appliable" in c for c in caveats))


# ----------------------------------------------------------------------
# _model — nested node ancestry (finding: v67 uses parentNodeId + childNodes
# nesting, NOT parentNodeName; a child must not export as a second root)
# ----------------------------------------------------------------------

def test_normalize_nested_child_resolves_parent_from_position():
    # The child carries only parentNodeId + childNodes nesting (no
    # parentNodeName). The normalizer must still record its parent as "Account".
    model = _model.normalize_definition(_nested_no_parentname_get())
    contact = (model.get("nodes") or {}).get("Contact")
    check("nested child node is captured", contact is not None)
    check("nested child parent resolved from position (not None)",
          contact and contact.get("parent") == "Account")


def test_model_to_plan_nested_child_carries_parentnodename():
    # The round trip: a whole export of the nested-no-parentNodeName definition
    # must emit Contact WITH parentNodeName=Account (not as a second root), so
    # reapplying the plan preserves the hierarchy.
    model = _model.normalize_definition(_nested_no_parentname_get())
    plan = _model.model_to_plan(model)  # whole export
    node_defs = plan.get("contextNodeDefinitions") or []
    contact = next((n for n in node_defs if n.get("name") == "Contact"), None)
    check("export emits the Contact node", contact is not None)
    check("exported Contact carries parentNodeName=Account (not a second root)",
          contact and contact.get("parentNodeName") == "Account")
    account = next((n for n in node_defs if n.get("name") == "Account"), None)
    check("exported Account root has no parentNodeName",
          account is not None and "parentNodeName" not in account)


def test_normalize_parent_from_flat_parentnodeid_index():
    # A flat (non-nested) shape that carries parentNodeId but no childNodes
    # nesting must still resolve the parent via the id->name index.
    flat = {
        "developerName": "RLM_FlatParent",
        "baseReference": None,
        "contextDefinitionVersionList": [
            {
                "isActive": True,
                "contextNodes": [
                    {"name": "Account", "contextNodeId": "11oA", "childNodes": []},
                    {"name": "Contact", "contextNodeId": "11oC",
                     "parentNodeId": "11oA", "childNodes": []},
                ],
            }
        ],
    }
    model = _model.normalize_definition(flat)
    contact = (model.get("nodes") or {}).get("Contact")
    check("flat child parent resolved via parentNodeId index",
          contact and contact.get("parent") == "Account")


# ----------------------------------------------------------------------
# _model — whole export emits mapping shells + defaultMapping (finding: the
# create flow needs both; rules alone can't resolve or activate)
# ----------------------------------------------------------------------

def test_from_scratch_export_emits_mapping_shells_and_default():
    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(model)  # whole export
    shells = plan.get("contextMappings")
    check("whole export emits a contextMappings shell block",
          isinstance(shells, dict) and isinstance(shells.get("contextMappings"), list))
    names = [m.get("name") for m in (shells or {}).get("contextMappings", [])]
    check("shell block includes AccountContactMapping",
          "AccountContactMapping" in names)
    check("shell block sets generate flags",
          (shells or {}).get("generateInputMappings") is True
          and (shells or {}).get("generateSObjectMappings") is True)
    check("whole export emits top-level defaultMapping = the isDefault mapping",
          plan.get("defaultMapping") == "AccountContactMapping")


def test_create_export_round_trips_shells_and_activates():
    # Reapply readiness: the exported create:true plan must carry a mapping shell
    # for every mappingRule's mappingName (so rules can resolve) and a
    # defaultMapping (so activation won't hit DATA_MAPPING_NOT_FOUND).
    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(model)
    shell_names = {m.get("name")
                   for m in (plan.get("contextMappings") or {}).get("contextMappings", [])}
    rule_mappings = {r.get("mappingName") for r in (plan.get("mappingRules") or [])}
    check("every mappingRule's mapping has a shell to resolve against",
          rule_mappings and rule_mappings <= shell_names)
    check("defaultMapping is one of the emitted shells",
          plan.get("defaultMapping") in shell_names)


def test_patch_delta_omits_mapping_shells_and_default():
    # A patch delta is additive against a live definition whose shells already
    # exist; it must NOT re-emit shells or defaultMapping.
    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(
        model,
        include={"nodes": set(), "attributes": {"Account.AccountName"},
                 "mappings": set(), "tags": set()},
    )
    check("patch delta omits contextMappings shells", "contextMappings" not in plan)
    check("patch delta omits defaultMapping", "defaultMapping" not in plan)


def test_create_export_with_shells_lints_clean():
    # The full export -> lint round trip must stay clean with the new shell +
    # defaultMapping keys present.
    import scripts.context_service.definition.validate_context_plan as V

    model = _model.normalize_definition(_from_scratch_get())
    plan = _model.model_to_plan(model)
    plan.pop("_caveats", None)
    result = V.PlanResult(path="<create-shells>")
    V._validate_plan_object(plan, result, "create-shells")
    check("create export with mapping shells + defaultMapping lints clean",
          not result.errors)


# ----------------------------------------------------------------------
# _client — shared tag-unwrap helpers (the B2 consolidation)
#
# The GET-shape unwrap for attribute/node tags used to be copy-pasted in
# _delete, _mutate, and _payload; it now lives once in _client. These lock the
# three shapes a live GET returns (bare list / dict-wrapper / absent) and the
# node-vs-attribute key asymmetry (nodes: ``tags``; attributes: ``attributeTags``)
# so a future GET-shape change can't silently drop a tag (which would let add-tag
# dedup re-POST a duplicate).
# ----------------------------------------------------------------------

def test_attr_tag_list_unwraps_bare_list():
    attr = {"attributeTags": [{"name": "LineItemQuantity"}, {"name": "RampMode"}]}
    names = _client.attr_tag_names(attr)
    check("attr_tag_names reads a bare attributeTags list",
          names == {"LineItemQuantity", "RampMode"})


def test_attr_tag_list_unwraps_dict_container():
    # The live GET sometimes wraps the list in a container dict; iterating it
    # directly would yield the string key "attributeTags", not tag dicts.
    attr = {"attributeTags": {"attributeTags": [{"name": "LineItemQuantity"}]}}
    names = _client.attr_tag_names(attr)
    check("attr_tag_names unwraps the {attributeTags: [...]} container",
          names == {"LineItemQuantity"})


def test_attr_tag_list_falls_back_to_tags_key():
    # Some shapes carry the attribute tags under the plain ``tags`` key.
    attr = {"tags": [{"name": "Discount"}]}
    check("attr_tag_list falls back to the tags key",
          [t.get("name") for t in _client.attr_tag_list(attr)] == ["Discount"])


def test_attr_tag_names_absent_is_empty():
    check("attr_tag_names on an attribute with no tags is empty",
          _client.attr_tag_names({"name": "NoTags"}) == set())
    check("attr_tag_list on an attribute with no tags is empty list",
          _client.attr_tag_list({"name": "NoTags"}) == [])


def test_node_tag_names_key_asymmetry():
    # Nodes key their tags under ``tags`` (NOT ``attributeTags``) — the asymmetry
    # that justifies a separate helper. An attributeTags key on a node must be
    # ignored, and the node's own ``tags`` used.
    node = {"tags": [{"name": "NodeTagA"}],
            "attributeTags": [{"name": "WrongKey"}]}
    names = _client.node_tag_names(node)
    check("node_tag_names reads the node 'tags' key, not 'attributeTags'",
          names == {"NodeTagA"})


def test_node_tag_list_unwraps_dict_container():
    node = {"tags": {"tags": [{"name": "NodeTagA"}, {"name": "NodeTagB"}]}}
    names = _client.node_tag_names(node)
    check("node_tag_names unwraps the {tags: [...]} container",
          names == {"NodeTagA", "NodeTagB"})


def test_tag_names_ignore_nameless_and_nondict_entries():
    # Defensive: a nameless tag or a non-dict entry (a stray string key from a
    # mis-iterated wrapper) must not crash or leak into the name set.
    attr = {"attributeTags": [{"name": "Real"}, {"noName": "x"}, "stray"]}
    check("attr_tag_names drops nameless and non-dict tag entries",
          _client.attr_tag_names(attr) == {"Real"})


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
