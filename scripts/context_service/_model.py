#!/usr/bin/env python3
"""Normalize a Context Definition GET response into a stable, comparable model.

Shared by ``diff_context.py`` (org-vs-org / plan-vs-org drift) and
``export_context.py`` (serialize a live definition back to plan JSON). Both need
the *same* flattened view of a definition, so the parse lives here once.

The normalizer walks the version-centric GET shape
(definition -> active version -> nodes -> attributes -> mappings -> node
mappings -> attribute mappings -> hydration) using the defensive helpers in
``_client.py`` (``active_version``, ``iter_nodes``, ``node_attributes``) so it
tolerates the list-or-wrapper variations the Connect API returns.

Output shape (all names are the stable dotted keys the diff compares on):

    {
      "developerName": str | None,
      "isActive": bool | None,
      "nodes": { nodeName: {"parent": str|None, "depth": int} },
      "attributes": { "node.attr": {"dataType", "fieldType", "isTransient"} },
      "mappings": {
          mappingName: {
              "isDefault": bool,
              "nodes": {
                  nodeName: {
                      "sObject": str|None,
                      "attributes": {
                          contextAttributeName: {
                              "input": str|None,
                              "mappedContextDefinitionId": str|None,
                              "hydration": [ "Object.field", ... ],
                          }
                      }
                  }
              }
          }
      },
      "tags": { "node.tag": {"attribute": str|None} },
    }

This module is import-only (no CLI). Auth/GET is delegated to ``_client.py``.
"""

from typing import Any, Dict, List, Optional

from ._client import (
    active_version,
    attr_tag_list,
    iter_nodes,
    node_attributes,
    node_tag_list,
)


def _as_bool(value: Any) -> Optional[bool]:
    """Coerce the API's bool-or-"true"/"false" strings to a real bool (or None)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "1", "yes"):
            return True
        if low in ("false", "0", "no"):
            return False
    return bool(value)


def _node_parent(node: Dict[str, Any]) -> Optional[str]:
    """Best-effort parent-node name from a GET node (varies by shape)."""
    return (
        node.get("parentNodeName")
        or node.get("parentContextNodeName")
        or node.get("parentName")
    )


def _hydration_hops(detail: Dict[str, Any], node_sobject: Optional[str]) -> List[str]:
    """Flatten one hydration detail (+ its ``childDetails`` chain) to hops.

    The live GET names the source object **`sObjectDomain`**, not `objectName`
    (0/883 details on the standard Sales Transaction context carry `objectName`),
    so read `sObjectDomain` first and only fall back to the node's own SObject
    for a plain single-hop detail. A relationship traversal nests the terminal
    field under `childDetails`; descend it so the real source field (e.g.
    ``Product2.ProductCode``) appears, not just the intermediate lookup hop
    (``QuoteLineItem.Product2``).
    """
    hops: List[str] = []
    obj = detail.get("sObjectDomain") or detail.get("objectName") or node_sobject or "?"
    field = detail.get("queryAttribute")
    if field:
        hops.append(f"{obj}.{field}")
    for child in detail.get("childDetails") or []:
        if isinstance(child, dict):
            hops.extend(_hydration_hops(child, obj))
    return hops


def normalize_definition(defn: Dict[str, Any]) -> Dict[str, Any]:
    """Return the stable comparable model for one context-definition GET dict."""
    if not isinstance(defn, dict):
        return {
            "developerName": None,
            "isActive": None,
            "nodes": {},
            "attributes": {},
            "mappings": {},
            "tags": {},
        }

    version = active_version(defn)
    is_active = defn.get("isActive")
    if is_active is None:
        is_active = version.get("isActive")

    nodes: Dict[str, Dict[str, Any]] = {}
    attributes: Dict[str, Dict[str, Any]] = {}

    node_list = version.get("contextNodes") or []
    for node, depth in iter_nodes(node_list):
        name = node.get("name")
        if not name:
            continue
        nodes[name] = {"parent": _node_parent(node), "depth": depth}
        for attr in node_attributes(node):
            if not isinstance(attr, dict):
                continue
            attr_name = attr.get("name")
            if not attr_name:
                continue
            attributes[f"{name}.{attr_name}"] = {
                "dataType": attr.get("dataType"),
                "fieldType": attr.get("fieldType"),
                "isTransient": _as_bool(attr.get("isTransient")) or False,
            }

    mappings = _normalize_mappings(version.get("contextMappings") or [])
    tags = _normalize_tags(version)

    return {
        "developerName": defn.get("developerName") or defn.get("DeveloperName"),
        "isActive": _as_bool(is_active),
        # Top-level baseReference distinguishes a from-scratch custom definition
        # (None) from one that extends a standard base (e.g.
        # "SalesTransactionContext__stdctx"). ``model_to_plan`` uses this to decide
        # whether a whole-definition export should carry ``create: true``.
        "baseReference": defn.get("baseReference") or None,
        "label": defn.get("label"),
        "description": defn.get("description"),
        "nodes": nodes,
        "attributes": attributes,
        "mappings": mappings,
        "tags": tags,
    }


def _normalize_mappings(mapping_list: List[Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for mapping in mapping_list:
        if not isinstance(mapping, dict):
            continue
        mname = mapping.get("name")
        if not mname:
            continue
        node_maps: Dict[str, Any] = {}
        for node_map in mapping.get("contextNodeMappings") or []:
            if not isinstance(node_map, dict):
                continue
            node_name = node_map.get("contextNodeName")
            if not node_name:
                continue
            sobj = node_map.get("sObjectName")
            attr_maps: Dict[str, Any] = {}
            for attr_map in node_map.get("attributeMappings") or []:
                if not isinstance(attr_map, dict):
                    continue
                attr_name = attr_map.get("contextAttributeName")
                if not attr_name:
                    continue
                hydration = []
                for h in attr_map.get("contextAttrHydrationDetailList") or []:
                    if isinstance(h, dict):
                        hydration.extend(_hydration_hops(h, sobj))
                attr_maps[attr_name] = {
                    "input": attr_map.get("contextInputAttributeName"),
                    "mappedContextDefinitionId": node_map.get(
                        "mappedContextDefinitionId"
                    )
                    or attr_map.get("mappedContextDefinitionId"),
                    "hydration": hydration,
                }
            node_maps[node_name] = {"sObject": sobj, "attributes": attr_maps}
        out[mname] = {
            "isDefault": _as_bool(mapping.get("isDefault")) or False,
            "nodes": node_maps,
        }
    return out


def normalize_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Return the same comparable model for a *plan JSON* object.

    Lets ``diff_context.py`` compare a repo plan against a live org using one
    shape. The plan is **additive** (declares only what it adds on top of a
    base), so a plan-vs-org diff is directional: plan artifacts absent from the
    org are drift; org artifacts absent from the plan are usually inherited, not
    drift. Callers should interpret the two directions accordingly.

    Mapping rows (flat ``mappingRules``) are grouped into the same
    ``mappings -> nodes -> attributes`` tree the GET normalizer produces, with
    the SObject-field target recorded as the attribute's ``input`` (mirroring
    the GET ``contextInputAttributeName``).
    """
    if not isinstance(plan, dict):
        return {
            "developerName": None,
            "isActive": None,
            "nodes": {},
            "attributes": {},
            "mappings": {},
            "tags": {},
        }

    nodes: Dict[str, Dict[str, Any]] = {}
    for node in plan.get("contextNodeDefinitions") or []:
        if not isinstance(node, dict) or not node.get("name"):
            continue
        nodes[node["name"]] = {"parent": node.get("parentNodeName"), "depth": None}

    attributes: Dict[str, Dict[str, Any]] = {}
    for attr in plan.get("contextAttributesByName") or []:
        if not isinstance(attr, dict):
            continue
        node_name = attr.get("nodeName")
        name = attr.get("name")
        if not node_name or not name:
            continue
        attributes[f"{node_name}.{name}"] = {
            "dataType": attr.get("dataType", "STRING"),
            "fieldType": attr.get("fieldType", "INPUTOUTPUT"),
            "isTransient": _as_bool(attr.get("isTransient")) or False,
        }

    # isDefault designations come from contextMappings / contextMappingUpdates.
    default_mappings = set()
    for block_key in ("contextMappings", "contextMappingUpdates"):
        block = plan.get(block_key)
        rows = block.get("contextMappings") if isinstance(block, dict) else None
        for row in rows or []:
            if isinstance(row, dict) and _as_bool(row.get("isDefault")):
                if row.get("name"):
                    default_mappings.add(row["name"])

    mappings: Dict[str, Any] = {}
    for rule in plan.get("mappingRules") or []:
        if not isinstance(rule, dict):
            continue
        mname = rule.get("mappingName")
        node_name = rule.get("contextNode")
        attr_name = rule.get("contextAttribute")
        if not mname or not node_name or not attr_name:
            continue
        mapping = mappings.setdefault(
            mname, {"isDefault": mname in default_mappings, "nodes": {}}
        )
        node_map = mapping["nodes"].setdefault(
            node_name, {"sObject": rule.get("sObject"), "attributes": {}}
        )
        # Reconstruct the hydration hop chain the same way the GET side flattens
        # it (``_hydration_hops``). A traversal rule applies as a parent
        # hydration detail (``sObject.sObjectField``, e.g. QuoteLineItem.Product2)
        # with the terminal field nested under ``childDetails``
        # (``childSObject.childSObjectField``, e.g. Product2.ProductCode), so the
        # org normalizer records BOTH hops. Emit both here as well — recording
        # only the terminal hop made ``diff_context`` report a permanent
        # ``~ changed`` mapping after a traversal plan had already been applied.
        hydration = []
        if rule.get("childSObject") and rule.get("childSObjectField"):
            if rule.get("sObject") and rule.get("sObjectField"):
                hydration.append(f"{rule['sObject']}.{rule['sObjectField']}")
            hydration.append(f"{rule['childSObject']}.{rule['childSObjectField']}")
        elif rule.get("sObject") and rule.get("sObjectField"):
            hydration.append(f"{rule['sObject']}.{rule['sObjectField']}")
        # NOTE: the plan's ``sObjectField`` is the *hydration target* (captured
        # above), NOT the GET's ``contextInputAttributeName``. The org side's
        # ``input`` is the context input attribute name, which the plan does not
        # model — leave ``input`` unset on the plan side so hydration (which
        # both sides carry) is what the mapping diff compares on.
        node_map["attributes"][attr_name] = {
            "input": None,
            "mappedContextDefinitionId": rule.get("mappedContextDefinitionName"),
            "hydration": hydration,
        }

    tags: Dict[str, Any] = {}
    for tag in plan.get("contextTagsByName") or []:
        if not isinstance(tag, dict) or not tag.get("name"):
            continue
        node_name = tag.get("nodeName")
        key = f"{node_name}.{tag['name']}" if node_name else tag["name"]
        tags[key] = {"attribute": tag.get("attributeName")}

    return {
        "developerName": plan.get("developerName"),
        "isActive": _as_bool(plan.get("activate")),
        "nodes": nodes,
        "attributes": attributes,
        "mappings": mappings,
        "tags": tags,
    }


def model_to_plan(
    model: Dict[str, Any],
    include: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Invert a normalized model back into repo **plan JSON**.

    Produces the additive plan format consumed by ``manage_context_definition``
    / ``ExtendStandardContext`` and linted by ``validate_context_plan.py``:
    ``contextNodeDefinitions`` / ``contextAttributesByName`` / ``mappingRules`` /
    ``contextTagsByName`` / ``activate``. Shared by ``export_context.py`` (whole
    definition) and ``patch_context.py`` (a delta subset).

    ``include`` optionally restricts the output to a subset of artifacts — the
    patch delta. It is a dict of key sets, any of which may be omitted (meaning
    "emit everything in that category"):

        {
          "nodes":      {nodeName, ...},              # keys of model["nodes"]
          "attributes": {"node.attr", ...},           # keys of model["attributes"]
          "mappings":   {"mapping/node/attr", ...},   # flattened mapping grain
          "tags":       {"node.tag", ...},            # keys of model["tags"]
        }

    When ``include`` is None the whole model is serialized (the export case).

    Returns a dict with the plan JSON plus a ``_caveats`` list flagging reversals
    that cannot be fully reconstructed from a GET (CONTEXT-to-CONTEXT sources,
    multi-hop traversals). ``_caveats`` and any other ``_``-prefixed key are
    ignored by both the CCI task and the validator, so the output stays directly
    consumable. Callers strip ``_caveats`` before writing an apply-ready plan and
    surface it to the user separately.
    """
    model = model or {}
    # A whole-definition export passes ``include=None`` (emit everything); a
    # ``patch_context`` delta always passes an ``include`` dict (even an empty
    # one when nothing drifted). Capture that distinction *before* the ``or {}``
    # collapse, so the create-new detection below never misreads a no-delta patch
    # as a whole export.
    whole_export = include is None
    include = include or {}

    def _wanted(category: str, key: str) -> bool:
        keys = include.get(category)
        return keys is None or key in keys

    caveats: List[str] = []

    # --- nodes -------------------------------------------------------------
    # Emit contextNodeDefinitions only for nodes actually selected. On extend
    # plans nodes are usually inherited (not selected), so this list is often
    # empty; on create-new / net-new nodes it carries name + parentNodeName.
    node_defs: List[Dict[str, Any]] = []
    for name, node in sorted((model.get("nodes") or {}).items()):
        if not _wanted("nodes", name):
            continue
        entry: Dict[str, Any] = {"name": name}
        if node.get("parent"):
            entry["parentNodeName"] = node["parent"]
        node_defs.append(entry)

    # --- attributes --------------------------------------------------------
    attrs_by_name: List[Dict[str, Any]] = []
    for key, attr in sorted((model.get("attributes") or {}).items()):
        if not _wanted("attributes", key):
            continue
        node_name, _, attr_name = key.partition(".")
        entry = {
            "nodeName": node_name,
            "name": attr_name,
            "dataType": attr.get("dataType") or "STRING",
            "fieldType": attr.get("fieldType") or "INPUTOUTPUT",
        }
        if attr.get("isTransient"):
            entry["isTransient"] = True
        attrs_by_name.append(entry)

    # --- mapping rules -----------------------------------------------------
    mapping_rules = _mappings_to_rules(model.get("mappings"), include, caveats)

    # --- tags --------------------------------------------------------------
    tags_by_name: List[Dict[str, Any]] = []
    for key, tag in sorted((model.get("tags") or {}).items()):
        if not _wanted("tags", key):
            continue
        # Node-level identity tags (attribute is None, tag name == node name)
        # are not repo-authored plan tags — skip them so the emitted plan only
        # carries attribute tags, which is what contextTagsByName models.
        if not tag.get("attribute"):
            continue
        node_name, _, tag_name = key.partition(".")
        tags_by_name.append({
            "nodeName": node_name,
            "attributeName": tag["attribute"],
            "name": tag_name,
        })

    plan: Dict[str, Any] = {"developerName": model.get("developerName")}

    # Create-new vs extend detection — only meaningful for a *whole-definition*
    # export (``include is None``). A ``patch_context`` delta always passes an
    # ``include`` and must never carry ``create: true`` (it is additive against an
    # existing definition). A from-scratch custom definition has no top-level
    # ``baseReference``; an extension of a standard base does. Without
    # ``create: true`` the emitted plan re-lints as an additive plan against a
    # standard base, which wrongly enforces the ``__c`` suffix rule on the
    # definition's author-chosen node/attribute/tag names.
    base_reference = model.get("baseReference")
    if whole_export and not base_reference:
        plan["create"] = True
        # Give the create payload a clean name source (``build_create_payload``
        # derives ``name`` from label/name/developerName).
        if model.get("label"):
            plan["label"] = model["label"]
        if model.get("description"):
            plan["description"] = model["description"]
    elif whole_export and base_reference:
        # A full export of an *extension* cannot faithfully round-trip: it emits
        # the inherited standard artifacts, which cannot be re-created against the
        # base. Flag it rather than pretend the output is directly appliable —
        # ``--custom-only`` is the appliable form for an extension.
        caveats.append(
            f"Full export of an extension of '{base_reference}' includes inherited "
            f"standard artifacts and is not directly appliable; re-export with "
            f"--custom-only to emit only the custom (__c) layer."
        )

    if node_defs:
        plan["contextNodeDefinitions"] = node_defs
    if attrs_by_name:
        plan["contextAttributesByName"] = attrs_by_name
    if mapping_rules:
        plan["mappingRules"] = mapping_rules
    if tags_by_name:
        plan["contextTagsByName"] = tags_by_name
    plan["activate"] = bool(model.get("isActive"))
    if caveats:
        plan["_caveats"] = caveats
    return plan


def _mappings_to_rules(
    mappings: Optional[Dict[str, Any]],
    include: Dict[str, Any],
    caveats: List[str],
) -> List[Dict[str, Any]]:
    """Flatten the mappings tree back into flat ``mappingRules`` plan rows.

    Inverts ``_normalize_mappings`` / ``_flatten_mapping_attrs``: one plan row
    per (mapping, node, attribute). SOBJECT rows reconstruct ``sObject`` /
    ``sObjectField`` from the node's sObject and the hydration hop; traversal and
    CONTEXT-to-CONTEXT rows are best-effort and recorded in ``caveats``.
    """
    want = include.get("mappings")
    rules: List[Dict[str, Any]] = []
    for mname, mapping in sorted((mappings or {}).items()):
        for node_name, node_map in sorted((mapping.get("nodes") or {}).items()):
            sobj = node_map.get("sObject")
            for attr_name, attr_map in sorted((node_map.get("attributes") or {}).items()):
                flat_key = f"{mname}/{node_name}/{attr_name}"
                if want is not None and flat_key not in want:
                    continue
                rule: Dict[str, Any] = {
                    "mappingName": mname,
                    "contextNode": node_name,
                    "contextAttribute": attr_name,
                }
                ref_id = attr_map.get("mappedContextDefinitionId")
                hydration = attr_map.get("hydration") or []
                if ref_id:
                    # CONTEXT-to-CONTEXT: the GET gives an ID, but the plan needs
                    # sourceContextNode/sourceContextAttribute (names). We cannot
                    # resolve those from a read alone — emit the ID as
                    # mappedContextDefinitionName and flag it for the author.
                    rule["mappingType"] = "CONTEXT"
                    rule["mappedContextDefinitionName"] = ref_id
                    rule["_todo"] = (
                        "CONTEXT source: resolve mappedContextDefinitionName (currently a "
                        "raw ID) to a developerName and add sourceContextNode / "
                        "sourceContextAttribute before applying."
                    )
                    caveats.append(
                        f"{flat_key}: CONTEXT-to-CONTEXT mapping emitted with raw "
                        f"mappedContextDefinitionId '{ref_id}' — resolve to a "
                        f"developerName + source node/attribute before applying."
                    )
                else:
                    rule["mappingType"] = "SOBJECT"
                    if sobj:
                        rule["sObject"] = sobj
                    if hydration:
                        # Simple mapping: one hop, "sObject.field" → sObjectField.
                        first_obj, _, first_field = hydration[0].rpartition(".")
                        rule["sObjectField"] = first_field
                        if len(hydration) > 1:
                            # Multi-hop traversal: reconstruct the final hop as
                            # childSObject/childSObjectField. Exact chain semantics
                            # are not fully recoverable from the flattened GET.
                            last_obj, _, last_field = hydration[-1].rpartition(".")
                            rule["childSObject"] = last_obj
                            rule["childSObjectField"] = last_field
                            caveats.append(
                                f"{flat_key}: multi-hop traversal hydration "
                                f"({' -> '.join(hydration)}) reconstructed best-effort; "
                                f"verify childSObject/childSObjectField before applying."
                            )
                rules.append(rule)
    return rules


def _normalize_tags(version: Dict[str, Any]) -> Dict[str, Any]:
    """Collect tags from the GET shape, keyed to match ``normalize_plan``.

    The Connect GET surfaces tags in two places (confirmed live on v67.0):

    * **Attribute-level** — ``attribute.attributeTags[]`` (each with a ``name``).
      These correspond to the plan's ``contextTagsByName`` entries that carry an
      ``attributeName``. The plan keys such a tag ``node.tagName`` and records
      ``attribute=attributeName``, so we key the org side the same way: by the
      **owning attribute's** node and name (``node.attributeName``) and record
      ``attribute=attributeName``. (In practice the tag name equals the
      attribute name, e.g. ``RampMode__c``.)
    * **Node-level** — ``node.tags[]`` are node-identity tags (tag name == node
      name) that the plan does not usually declare; we still surface them under
      ``node.tagName`` with ``attribute=None`` so an org-vs-org diff sees them.

    Keys are chosen so a repo plan's attribute tags line up with the org's
    attribute tags without spurious added/removed noise.
    """
    tags: Dict[str, Any] = {}

    for node, _depth in iter_nodes(version.get("contextNodes") or []):
        node_name = node.get("name")

        # Attribute-level tags — the ones repo plans declare.
        for attr in node_attributes(node):
            if not isinstance(attr, dict):
                continue
            attr_name = attr.get("name")
            for tag in attr_tag_list(attr):  # shared GET-shape unwrap (_client)
                if not isinstance(tag, dict):
                    continue
                tag_name = tag.get("name") or attr_name
                if not tag_name:
                    continue
                key = f"{node_name}.{tag_name}" if node_name else tag_name
                tags[key] = {"attribute": attr_name}

        # Node-level identity tags.
        for tag in node_tag_list(node):  # shared GET-shape unwrap (_client)
            if not isinstance(tag, dict):
                continue
            tag_name = tag.get("name")
            if not tag_name:
                continue
            key = f"{node_name}.{tag_name}" if node_name else tag_name
            # Do not clobber an attribute tag already recorded under this key.
            tags.setdefault(key, {"attribute": None})

    return tags
