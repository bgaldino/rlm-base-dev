#!/usr/bin/env python3
"""Pure payload / translation logic for the Context Service mutation scripts.

This module is **import-only**: no ``sf`` CLI, no network, no ``cumulusci``. It
is a faithful port of the drift-prone payload-shaping logic in
``tasks/rlm_context_service.py`` (``ManageContextDefinition``) so the standalone
scripts build byte-identical Connect/SObject payloads to the production CCI task.
The parity target is the task itself.

Every function takes a **normalized GET detail snapshot** (the
``connect/context-definitions/<id>`` response) plus plan rows and returns
payload dicts. Where the task performs a side effect *inside* the translation
loop (setting ``MappedContextDefinition`` via SObject REST), the pure version
instead **returns side-effect descriptors** the orchestrator (``_apply.py``)
executes afterward — keeping this module network-free and testable.

Cited line numbers refer to ``tasks/rlm_context_service.py`` at port time.
"""

from typing import Any, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
# Small helpers (ports of the task's static/inline helpers)
# --------------------------------------------------------------------------- #

def as_bool(value: Any) -> bool:
    """Port of ``_as_bool`` (rlm_context_service.py:1269-1277)."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).lower() in {"1", "true", "yes"}


def strip_none(value: Any) -> Any:
    """Recursively drop keys/items whose value is ``None``.

    Port of the nested ``strip_none`` inside ``_patch_context_mappings``
    (rlm_context_service.py:571-577).
    """
    if isinstance(value, dict):
        cleaned = {k: strip_none(v) for k, v in value.items() if v is not None}
        return {k: v for k, v in cleaned.items() if v is not None}
    if isinstance(value, list):
        return [strip_none(v) for v in value if v is not None]
    return value


def normalize_attribute_mappings(node_map: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap a bare ``attributeMappings`` list under ``contextAttributeMappings``.

    Port of ``_normalize_attribute_mappings`` (rlm_context_service.py:636-642).
    """
    if not isinstance(node_map, dict):
        return node_map
    attribute_mappings = node_map.get("attributeMappings")
    if isinstance(attribute_mappings, list):
        node_map = {**node_map, "attributeMappings": {"contextAttributeMappings": attribute_mappings}}
    return node_map


# --------------------------------------------------------------------------- #
# Detail-snapshot walkers / indexes
# --------------------------------------------------------------------------- #

def _version0(detail: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(detail, dict):
        return {}
    versions = detail.get("contextDefinitionVersionList", [])
    return versions[0] if versions and isinstance(versions[0], dict) else {}


def _node_attrs(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    container = node.get("attributes", {})
    if isinstance(container, list):
        return container
    if isinstance(container, dict):
        return container.get("contextAttributes", []) or []
    return []


def _child_nodes(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    container = node.get("childNodes", {})
    if isinstance(container, list):
        return container
    if isinstance(container, dict):
        return container.get("contextNodes", []) or []
    return []


def collect_node_names(detail: Dict[str, Any]) -> set:
    """Port of ``_collect_node_names`` (rlm_context_service.py:1494-1516)."""
    names: set = set()
    nodes = _version0(detail).get("contextNodes", [])

    def walk(node_list):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            name = node.get("name")
            if name:
                names.add(name)
            walk(_child_nodes(node))

    walk(nodes)
    return names


def collect_context_indexes(
    detail: Dict[str, Any], plan: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Dict[tuple, Any]]:
    """Port of ``_collect_context_indexes`` (rlm_context_service.py:891-984).

    Returns ``(node_index, attr_index)`` where ``node_index[name] = nodeId`` and
    ``attr_index[(node_name, attr_name)] = attributeId``. When ``plan`` is given,
    plan-declared nodes/attributes are added with ``None`` ids (used by the
    validate path); the translate path passes ``{}``.
    """
    plan = plan or {}
    if not isinstance(detail, dict):
        return {}, {}
    version0 = _version0(detail)
    mappings = version0.get("contextMappings", [])

    node_index: Dict[str, Any] = {}
    attr_index: Dict[tuple, Any] = {}

    for mapping in mappings or []:
        if not isinstance(mapping, dict):
            continue
        for node_map in mapping.get("contextNodeMappings", []):
            if not isinstance(node_map, dict):
                continue
            node_name = node_map.get("contextNodeName")
            node_id = node_map.get("contextNodeId")
            if node_name:
                node_index[node_name] = node_id
            for attr in node_map.get("attributeMappings", []) or []:
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("contextAttributeName")
                attr_id = attr.get("contextAttributeId")
                if node_name and attr_name:
                    attr_index[(node_name, attr_name)] = attr_id

    context_nodes = version0.get("contextNodes", [])

    def walk(nodes):
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            node_id = node.get("contextNodeId")
            node_name = node.get("name")
            if node_name and node_id:
                node_index.setdefault(node_name, node_id)
            for attr in _node_attrs(node):
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("name")
                attr_id = attr.get("contextAttributeId")
                if node_name and attr_name and attr_id:
                    attr_index.setdefault((node_name, attr_name), attr_id)
            walk(_child_nodes(node))

    walk(context_nodes)

    # Plan-side augmentation (validate path): declared nodes/attrs get None ids.
    plan_nodes = plan.get("contextNodes")
    plan_nodes_list = plan_nodes.get("contextNodes", []) if isinstance(plan_nodes, dict) else []
    for node in plan_nodes_list:
        node_name = node.get("name")
        if node_name:
            node_index.setdefault(node_name, None)
        for attr in _node_attrs(node):
            attr_name = attr.get("name")
            if node_name and attr_name:
                attr_index.setdefault((node_name, attr_name), None)

    for attr in plan.get("contextAttributesByName", []) or []:
        if not isinstance(attr, dict):
            continue
        node_name = attr.get("nodeName")
        attr_name = attr.get("name")
        if node_name and attr_name:
            node_index.setdefault(node_name, None)
            attr_index.setdefault((node_name, attr_name), None)

    return node_index, attr_index


def collect_parent_ids(detail: Dict[str, Any]) -> Dict[str, str]:
    """Map each child node name to its parent node id.

    Port of the nested ``_collect_parent_ids`` (rlm_context_service.py:1298-1313),
    used to derive ``mappedContextNodeId`` on child node mappings (CS DocGen).
    """
    parent_node_id_by_node_name: Dict[str, str] = {}
    version0 = _version0(detail)

    def _walk(nodes_list, parent_id=None):
        for node in nodes_list if isinstance(nodes_list, list) else []:
            name = node.get("name")
            nid = node.get("contextNodeId")
            if parent_id and name:
                parent_node_id_by_node_name[name] = parent_id
            _walk(_child_nodes(node), nid)

    _walk(version0.get("contextNodes", []))
    return parent_node_id_by_node_name


# --------------------------------------------------------------------------- #
# Create payload
# --------------------------------------------------------------------------- #

def build_create_payload(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Build the ``connect/context-definitions`` create body.

    Port of ``_create_context_definition_record`` payload build
    (rlm_context_service.py:266-281): alphanumeric ``name``, allow-listed
    passthrough, ``primaryDomainObject`` omission (rejected with
    JSON_PARSER_ERROR by the create endpoint).

    The allow-list is extended (vs. the task) with the two source fields the
    Context Definition REST reference documents on this endpoint:
    ``sourceDefinitionId`` (**clone** an existing definition) and ``payload``
    (persist a whole definition + mappings in one POST). These are additive —
    none of the repo's active plans set them, so create parity with the task on
    those plans is unchanged; they enable the clone / whole-definition paths the
    task never exposed. ``baseReference`` (extend a standard base) and
    ``endDate``/``isActive`` are also allow-listed here.
    """
    raw_name = plan.get("label") or plan.get("name") or plan.get("developerName") or ""
    api_name = "".join(c for c in raw_name if c.isalnum())
    payload: Dict[str, Any] = {
        "name": api_name,
        "developerName": plan.get("developerName"),
    }
    for field in ("description", "startDate", "endDate", "contextTtl", "baseReference",
                  "contextType", "sourceDefinitionId", "payload", "isActive"):
        if plan.get(field) is not None:
            payload[field] = plan[field]
    if isinstance(plan.get("createPayload"), dict):
        payload.update(plan["createPayload"])
    return payload


# --------------------------------------------------------------------------- #
# Attribute / tag resolution (idempotent — skips artifacts that already exist)
# --------------------------------------------------------------------------- #

def _walk_node_attr_index(nodes) -> Tuple[Dict[str, str], Dict[tuple, str]]:
    """Build node/attr id indexes from the contextNodes tree only."""
    node_index: Dict[str, str] = {}
    attr_index: Dict[tuple, str] = {}

    def walk(node_list):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            node_id = node.get("contextNodeId")
            node_name = node.get("name")
            if node_name and node_id:
                node_index[node_name] = node_id
            for attr in _node_attrs(node):
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("name")
                attr_id = attr.get("contextAttributeId")
                if node_name and attr_name and attr_id:
                    attr_index[(node_name, attr_name)] = attr_id
            walk(_child_nodes(node))

    walk(nodes)
    return node_index, attr_index


def resolve_attributes_by_name(
    attr_specs: Any, detail: Dict[str, Any], logger=None
) -> List[Dict[str, Any]]:
    """Port of ``_resolve_context_attributes_by_name`` (rlm_context_service.py:1128-1191).

    Returns the ``contextAttributes`` payload list for attributes that do not yet
    exist on the definition (idempotent skip). Unresolved nodes are warned and
    skipped.
    """
    if not isinstance(attr_specs, list):
        raise ValueError("contextAttributesByName must be a list")
    nodes = _version0(detail).get("contextNodes", [])
    node_index, attr_index = _walk_node_attr_index(nodes)

    resolved: List[Dict[str, Any]] = []
    for spec in attr_specs:
        if not isinstance(spec, dict):
            continue
        node_name = spec.get("nodeName")
        if not node_name or node_name not in node_index:
            if logger:
                logger(f"Context node not resolved for attribute add: {node_name}")
            continue
        attr_name = spec.get("name")
        if attr_name and (node_name, attr_name) in attr_index:
            continue
        attr_payload = {
            "contextNodeId": node_index[node_name],
            "name": attr_name,
            "dataType": spec.get("dataType", "STRING"),
            "fieldType": spec.get("fieldType", "INPUTOUTPUT"),
        }
        if "isTransient" in spec:
            attr_payload["isTransient"] = as_bool(spec.get("isTransient"))
        resolved.append(attr_payload)
    return resolved


def transient_updates(
    attr_specs: Any, detail: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Return SObject-REST IsTransient patches for existing attributes that drift.

    Pure port of the decision logic in ``_sync_context_attribute_properties``
    (rlm_context_service.py:1193-1261). Each entry is
    ``{"context_attribute_id", "node_name", "name", "is_transient"}`` for the
    orchestrator to PATCH via ``sobjects/ContextAttribute/<id>``.
    """
    if not isinstance(attr_specs, list):
        raise ValueError("contextAttributesByName must be a list")
    nodes = _version0(detail).get("contextNodes", [])
    attr_by_key: Dict[tuple, Dict[str, Any]] = {}

    def walk(node_list):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            node_name = node.get("name")
            for attr in _node_attrs(node):
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("name")
                attr_id = attr.get("contextAttributeId")
                if node_name and attr_name and attr_id:
                    attr_by_key[(node_name, attr_name)] = attr
            walk(_child_nodes(node))

    walk(nodes)

    updates: List[Dict[str, Any]] = []
    for spec in attr_specs:
        if not isinstance(spec, dict) or "isTransient" not in spec:
            continue
        attr = attr_by_key.get((spec.get("nodeName"), spec.get("name")))
        if not attr:
            continue
        desired = as_bool(spec.get("isTransient"))
        current = attr.get("isTransient")
        if current is None:
            current = attr.get("IsTransient")
        if as_bool(current) == desired:
            continue
        updates.append({
            "context_attribute_id": attr.get("contextAttributeId"),
            "node_name": spec.get("nodeName"),
            "name": spec.get("name"),
            "is_transient": desired,
        })
    return updates


def resolve_tags_by_name(
    tag_specs: Any, detail: Dict[str, Any], logger=None
) -> List[Dict[str, Any]]:
    """Port of ``_resolve_tags_by_name`` (rlm_context_service.py:1043-1126).

    Returns the ``contextTags`` payload list, skipping tags already present on
    the node/attribute (idempotent).
    """
    if not isinstance(tag_specs, list):
        raise ValueError("contextTagsByName must be a list")
    version0 = _version0(detail)
    if not version0:
        if logger:
            logger("No contextDefinitionVersionList found; cannot resolve tags by name.")
        return []
    nodes = version0.get("contextNodes", [])

    node_index: Dict[str, str] = {}
    attr_index: Dict[tuple, str] = {}
    node_tag_index: Dict[str, set] = {}
    attr_tag_index: Dict[tuple, set] = {}

    def walk(node_list):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            node_id = node.get("contextNodeId")
            node_name = node.get("name")
            if node_id and node_name:
                node_index[node_name] = node_id
            for attr in _node_attrs(node):
                attr_id = attr.get("contextAttributeId")
                attr_name = attr.get("name")
                if attr_id and node_name and attr_name:
                    attr_index[(node_name, attr_name)] = attr_id
                    tags = attr.get("attributeTags") or attr.get("tags") or []
                    if isinstance(tags, list):
                        attr_tag_index[(node_name, attr_name)] = {
                            t.get("name") for t in tags if isinstance(t, dict) and t.get("name")
                        }
            tags = node.get("tags") or []
            if isinstance(tags, list) and node_name:
                node_tag_index[node_name] = {
                    t.get("name") for t in tags if isinstance(t, dict) and t.get("name")
                }
            walk(_child_nodes(node))

    walk(nodes)

    resolved: List[Dict[str, Any]] = []
    for spec in tag_specs:
        if not isinstance(spec, dict):
            continue
        tag_name = spec.get("name")
        node_name = spec.get("nodeName")
        attr_name = spec.get("attributeName")
        if not tag_name or not node_name:
            continue
        if attr_name:
            attr_id = attr_index.get((node_name, attr_name))
            if not attr_id:
                if logger:
                    logger(f"Attribute tag not resolved: {node_name}.{attr_name}")
                continue
            if tag_name in attr_tag_index.get((node_name, attr_name), set()):
                continue
            resolved.append({"contextAttributeId": attr_id, "name": tag_name})
        else:
            node_id = node_index.get(node_name)
            if not node_id:
                if logger:
                    logger(f"Node tag not resolved: {node_name}")
                continue
            if tag_name in node_tag_index.get(node_name, set()):
                continue
            resolved.append({"contextNodeId": node_id, "name": tag_name})
    return resolved


# --------------------------------------------------------------------------- #
# Mapping filters / id resolution
# --------------------------------------------------------------------------- #

def filter_existing_mappings(
    context_mappings_payload: Dict[str, Any], detail: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Port of ``_filter_existing_mappings`` (rlm_context_service.py:1518-1536).

    Drop mapping shells whose ``name`` already exists on the definition. Returns
    ``None`` when nothing is left to create.
    """
    version0 = _version0(detail)
    existing = {
        m.get("name")
        for m in version0.get("contextMappings", [])
        if isinstance(m, dict)
    }
    if not isinstance(context_mappings_payload, dict):
        return context_mappings_payload
    mappings = context_mappings_payload.get("contextMappings")
    if not isinstance(mappings, list):
        return context_mappings_payload
    filtered = [m for m in mappings if isinstance(m, dict) and m.get("name") not in existing]
    if not filtered:
        return None
    return {**context_mappings_payload, "contextMappings": filtered}


def filter_new_nodes(
    node_defs: List[Dict[str, Any]], detail: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Filter ``contextNodeDefinitions`` to those not already present.

    Port of the inline node filter in ``_run_plan_for_context``
    (rlm_context_service.py:171-176).
    """
    existing_names = collect_node_names(detail)
    return [
        nd for nd in (node_defs or [])
        if isinstance(nd, dict) and nd.get("name") not in existing_names
    ]


def resolve_context_mapping_ids(
    detail: Dict[str, Any], payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Port of ``_resolve_context_mapping_ids`` (rlm_context_service.py:693-716).

    Fill ``contextMappingId`` on each mapping by matching ``name`` against the
    definition's existing mappings.
    """
    if not isinstance(payload, dict):
        return payload
    mappings = payload.get("contextMappings")
    if not isinstance(mappings, list):
        return payload
    version0 = _version0(detail)
    mapping_list = version0.get("contextMappings", [])
    index = {m.get("name"): m for m in mapping_list if isinstance(m, dict) and m.get("name")}
    changed = False
    resolved = []
    for mapping in mappings:
        if not isinstance(mapping, dict):
            resolved.append(mapping)
            continue
        if not mapping.get("contextMappingId") and mapping.get("name") in index:
            mapping = {**mapping, "contextMappingId": index[mapping["name"]].get("contextMappingId")}
            changed = True
        resolved.append(mapping)
    if not changed:
        return payload
    return {**payload, "contextMappings": resolved}


# --------------------------------------------------------------------------- #
# The core: flat mapping rules -> nested Connect PATCH payload
# --------------------------------------------------------------------------- #

def translate_mapping_rules(
    mapping_rules: Any,
    detail: Dict[str, Any],
    developer_name: Optional[str] = None,
    logger=None,
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Translate flat ``mappingRules`` into a nested ``contextMappings`` PATCH body.

    Faithful port of ``_translate_mapping_rules`` (rlm_context_service.py:1279-1492)
    with one purity change: where the task calls ``_set_mapped_context_definition``
    *inside* the loop (:1393-1406), this returns a **side-effect descriptor** in
    the second element of the tuple instead:
    ``{"type": "set_mapped_context_definition", "node_mapping_id", "developer_name"}``.

    Returns ``(payload_or_None, side_effects)``. The
    ``(mapping_id, node_id, sObject)`` grouping (:1463) is the DUPLICATE_VALUE
    guard; traversal rules (``childSObjectField`` set) are excluded from the PATCH
    (:1453) and handled by the orchestrator via SObject REST.
    """
    if not isinstance(mapping_rules, list):
        raise ValueError("mappingRules must be a list")
    if not isinstance(detail, dict):
        return None, []

    version0 = _version0(detail)
    version0_mappings = version0.get("contextMappings", [])

    mapping_index: Dict[str, Any] = {}
    for mapping in version0_mappings:
        if isinstance(mapping, dict) and mapping.get("name"):
            mapping_index[mapping["name"]] = mapping

    node_index, attr_index = collect_context_indexes(detail, {})
    parent_node_id_by_node_name = collect_parent_ids(detail)

    def find_attr_mapping_id(node_name, attr_name):
        for mapping in version0_mappings:
            if not isinstance(mapping, dict):
                continue
            for node_map in mapping.get("contextNodeMappings", []) or []:
                if node_map.get("contextNodeName") != node_name:
                    continue
                for attr_map in node_map.get("attributeMappings", []) or []:
                    if attr_map.get("contextAttributeName") == attr_name:
                        return attr_map.get("contextAttributeMappingId")
        return None

    side_effects: List[Dict[str, Any]] = []
    grouped: Dict[tuple, Dict] = {}

    for rule in mapping_rules:
        if not isinstance(rule, dict):
            continue
        mapping_name = rule.get("mappingName")
        node_name = rule.get("contextNode")
        attr_name = rule.get("contextAttribute")
        if not mapping_name or not node_name or not attr_name:
            continue

        mapping_meta = mapping_index.get(mapping_name)
        if not mapping_meta:
            if logger:
                logger(f"Mapping not found for rule: {mapping_name}")
            continue
        mapping_id = mapping_meta.get("contextMappingId")
        if not mapping_id:
            if logger:
                logger(f"Mapping id not found for rule: {mapping_name}")
            continue

        node_map_meta = None
        for existing in mapping_meta.get("contextNodeMappings", []) or []:
            if existing.get("contextNodeName") == node_name:
                node_map_meta = existing
                break

        node_id = (node_map_meta or {}).get("contextNodeId") or node_index.get(node_name)
        if not node_id:
            if logger:
                logger(f"Context node id not found for rule: {mapping_name} -> {node_name}")
            continue

        attr_id = attr_index.get((node_name, attr_name))
        if not attr_id:
            if logger:
                logger(f"Context attribute id not found for rule: {mapping_name} -> {node_name}.{attr_name}")
            continue

        attr_mapping_id = None
        existing_input_name = None
        if node_map_meta:
            for attr_map in node_map_meta.get("attributeMappings", []) or []:
                if attr_map.get("contextAttributeName") == attr_name:
                    attr_mapping_id = attr_map.get("contextAttributeMappingId")
                    existing_input_name = attr_map.get("contextInputAttributeName")
                    break

        mapping_type = (rule.get("mappingType") or "SOBJECT").upper()
        requested_input = rule.get("sObjectField")
        if mapping_type != "CONTEXT" and attr_name == "TransactionType":
            if logger:
                logger(f"Skipping TransactionType mapping update for {mapping_name} -> {node_name}")
            continue
        if mapping_type == "CONTEXT":
            existing_mapped_ctx = (
                mapping_meta.get("mappedContextDefinitionId")
                or mapping_meta.get("mappedContextDefinitionName")
            )
            needs_ctx_def_update = not existing_mapped_ctx
            if attr_mapping_id and (requested_input is None or requested_input == existing_input_name) and not needs_ctx_def_update:
                if logger:
                    logger(f"Skipping existing attribute mapping for {mapping_name} -> {node_name}.{attr_name}")
                continue
            if attr_mapping_id and (requested_input is None or requested_input == existing_input_name) and needs_ctx_def_update:
                # Purity change: defer the SObject-REST MappedContextDefinition set
                # (task calls _set_mapped_context_definition here at :1405).
                mapped_ctx_def_name = developer_name or detail.get("developerName") or detail.get("contextDefinitionId")
                node_mapping_id = (node_map_meta or {}).get("contextNodeMappingId")
                if mapped_ctx_def_name and node_mapping_id:
                    side_effects.append({
                        "type": "set_mapped_context_definition",
                        "node_mapping_id": node_mapping_id,
                        "developer_name": mapped_ctx_def_name,
                    })
                continue
            if attr_mapping_id and requested_input and requested_input != existing_input_name:
                if logger:
                    logger(f"Existing attribute mapping differs for {mapping_name} -> {node_name}.{attr_name}; skipping update.")
                continue

        context_attribute_mapping = {
            "contextAttributeId": attr_id,
            "contextInputAttributeName": attr_name,
        }
        mapped_context_node_id = None
        mapped_context_definition = None
        if mapping_type == "CONTEXT":
            source_node = rule.get("sourceContextNode")
            source_attr = rule.get("sourceContextAttribute")
            source_node_id = node_index.get(source_node)
            source_attr_id = attr_index.get((source_node, source_attr))
            source_attr_mapping_id = find_attr_mapping_id(source_node, source_attr)
            if not source_node_id or not source_attr_id or not source_attr_mapping_id:
                if logger:
                    logger(f"Context source not resolved for rule: {mapping_name} -> {source_node}.{source_attr}")
                continue
            context_attribute_mapping["contextInputAttributeName"] = attr_name
            context_attribute_mapping["hydrationDetails"] = {
                "contextAttrContextHydrationDetails": [
                    {
                        "queryAttribute": source_attr_id,
                        "parentAttributeMappingId": source_attr_mapping_id,
                    }
                ]
            }
            mapped_context_node_id = source_node_id
            mapped_context_definition = developer_name or detail.get("developerName") or detail.get("contextDefinitionId")
        else:
            if rule.get("sObject") and rule.get("sObjectField"):
                hydration_entry: Dict[str, Any] = {
                    "sObjectDomain": rule.get("sObject"),
                    "queryAttribute": rule.get("sObjectField"),
                }
                if not rule.get("childSObjectField"):
                    # Simple field mapping — include hydration in the PATCH payload.
                    # Traversal rules (childSObjectField set) go through SObject REST.
                    context_attribute_mapping["hydrationDetails"] = {
                        "contextAttrHydrationDetails": [hydration_entry]
                    }
        if attr_mapping_id:
            context_attribute_mapping["contextAttributeMappingId"] = attr_mapping_id

        group_key = (mapping_id, node_id, rule.get("sObject"))
        if group_key not in grouped:
            effective_mapped_node_id = mapped_context_node_id or parent_node_id_by_node_name.get(node_name)
            grouped[group_key] = {
                "contextMappingId": mapping_id,
                "contextNodeMappings": {
                    "contextNodeMappings": [
                        {
                            "contextNodeId": node_id,
                            "contextNodeMappingId": (node_map_meta or {}).get("contextNodeMappingId"),
                            "sObjectName": rule.get("sObject"),
                            "mappedContextNodeId": effective_mapped_node_id,
                            "attributeMappings": {
                                "contextAttributeMappings": []
                            },
                        }
                    ]
                },
                "mappedContextDefinitionName": mapped_context_definition,
            }
        grouped[group_key]["contextNodeMappings"]["contextNodeMappings"][0][
            "attributeMappings"
        ]["contextAttributeMappings"].append(context_attribute_mapping)

    updates = list(grouped.values())
    if not updates:
        return None, side_effects
    return {"contextMappings": updates}, side_effects


# --------------------------------------------------------------------------- #
# Verification (returns structure; scripts + task both render from it)
# --------------------------------------------------------------------------- #

def plan_verification(detail: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    """Port of ``_log_verification`` (rlm_context_service.py:1538-1643) that
    **returns** the matched/missing/present structure instead of logging it.

    Result keys: ``matched_rules`` (list of dicts), ``missing_rules`` (list of
    ``(mapping, node, attr)`` tuples), ``found_attrs`` (sorted names),
    ``found_tags`` (sorted ``node.attr:tag`` strings), plus ``ok`` (bool: no
    missing rules and every SOBJECT match carries hydration).
    """
    result: Dict[str, Any] = {
        "matched_rules": [],
        "missing_rules": [],
        "found_attrs": [],
        "found_tags": [],
        "hydration_gaps": [],
        "ok": False,
    }
    version0 = _version0(detail)
    if not version0:
        return result

    mapping_rules = plan.get("mappingRules", []) or []
    rule_keys = {
        (r.get("mappingName"), r.get("contextNode"), r.get("contextAttribute"))
        for r in mapping_rules if isinstance(r, dict)
    }
    tags_by_name = plan.get("contextTagsByName", []) or []
    attrs_by_name = plan.get("contextAttributesByName", []) or []

    matched_rules = []
    for mapping in version0.get("contextMappings", []):
        if not isinstance(mapping, dict):
            continue
        mapping_name = mapping.get("name")
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if not isinstance(node_map, dict):
                continue
            node_name = node_map.get("contextNodeName")
            sobject = node_map.get("sObjectName")
            for attr in node_map.get("attributeMappings", []) or []:
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("contextAttributeName")
                key = (mapping_name, node_name, attr_name)
                if key in rule_keys:
                    matched_rules.append({
                        "mapping": mapping_name,
                        "node": node_name,
                        "sObject": sobject,
                        "contextAttribute": attr_name,
                        "contextInputAttribute": attr.get("contextInputAttributeName"),
                        "hasHydrationDetail": bool(attr.get("contextAttrHydrationDetailList")),
                    })

    missing_rules = []
    for key in sorted(rule_keys):
        if not any(
            item.get("mapping") == key[0] and item.get("node") == key[1] and item.get("contextAttribute") == key[2]
            for item in matched_rules
        ):
            missing_rules.append(key)

    found_attrs = []
    found_tags = []

    def walk(nodes):
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            node_name = node.get("name")
            for attr in _node_attrs(node):
                if not isinstance(attr, dict):
                    continue
                attr_name = attr.get("name")
                if any(a.get("nodeName") == node_name and a.get("name") == attr_name for a in attrs_by_name):
                    found_attrs.append(f"{node_name}.{attr_name}")
                for tag in attr.get("attributeTags") or attr.get("tags") or []:
                    if isinstance(tag, dict) and any(
                        t.get("nodeName") == node_name and t.get("attributeName") == attr_name and t.get("name") == tag.get("name")
                        for t in tags_by_name
                    ):
                        found_tags.append(f"{node_name}.{attr_name}:{tag.get('name')}")
            walk(_child_nodes(node))

    walk(version0.get("contextNodes", []))

    hydration_gaps = [
        (item["node"], item["contextAttribute"], item["mapping"], item["sObject"])
        for item in matched_rules
        if item.get("sObject") and not item.get("hasHydrationDetail")
    ]

    result["matched_rules"] = matched_rules
    result["missing_rules"] = missing_rules
    result["found_attrs"] = sorted(set(found_attrs))
    result["found_tags"] = sorted(set(found_tags))
    result["hydration_gaps"] = hydration_gaps
    result["ok"] = not missing_rules
    return result
