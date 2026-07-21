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

from . import _client  # leaf module (no network at import) — for the shared tag-unwrap
from ._model import _hydration_hops  # canonical GET-hydration flattener (import-only)


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


def collect_root_node_ids(detail: Dict[str, Any]) -> set:
    """Return the set of ``contextNodeId`` values that are **root** nodes
    (top-level entries of the ``contextNodes`` tree).

    Companion to :func:`collect_parent_ids` (which maps *child* node name ->
    parent id). A **root** node mapping legitimately carries
    ``mappedContextNodeId: null`` — there is no parent node to point at —
    whereas a **child** node mapping must point at its parent. Callers use this
    set to tell the two apart (e.g. the node-mapping PATCH shape validator, so a
    valid root mapping is not mistaken for one missing a required field).
    Live-verified 2026-07-08 against ``RLM_SalesTransactionContext``: the
    existing ``SalesTransaction`` root mapping stores ``mappedContextNodeId:
    null``.
    """
    version0 = _version0(detail)
    roots: set = set()
    for node in version0.get("contextNodes", []) or []:
        if isinstance(node, dict) and node.get("contextNodeId"):
            roots.add(node["contextNodeId"])
    return roots


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
    if not api_name:
        # Punctuation-only label collapses to '' — fall back to developerName
        # so the create POST doesn't fail with an opaque required-field error.
        api_name = "".join(c for c in (plan.get("developerName") or "") if c.isalnum())
    if not api_name:
        raise ValueError(
            "Cannot derive an alphanumeric 'name' for the create payload from "
            "label / name / developerName — all are empty after stripping "
            "non-alphanumeric characters."
        )
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
                    # Shared GET-shape unwrap lives in _client (single source of truth).
                    attr_tag_index[(node_name, attr_name)] = _client.attr_tag_names(attr)
            if node_name:
                node_tag_index[node_name] = _client.node_tag_names(node)
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

def _expected_hydration_hops(rule: Dict[str, Any]) -> List[str]:
    """Reconstruct the hydration hop chain a SObject mapping rule requests.

    Mirrors ``_model.normalize_plan`` (which builds the same chain for the diff):
    a simple rule is one hop ``sObject.sObjectField``; a traversal rule prepends
    the lookup hop and appends the terminal ``childSObject.childSObjectField``.
    Used for display; the *mismatch* decision compares the terminal source field
    (see ``_binding_mismatch``), not the whole chain.
    """
    hops: List[str] = []
    s_object, s_field = rule.get("sObject"), rule.get("sObjectField")
    child_object, child_field = rule.get("childSObject"), rule.get("childSObjectField")
    if child_object and child_field:
        if s_object and s_field:
            hops.append(f"{s_object}.{s_field}")
        hops.append(f"{child_object}.{child_field}")
    elif s_object and s_field:
        hops.append(f"{s_object}.{s_field}")
    return hops


def _ci_eq(a: Optional[str], b: Optional[str]) -> bool:
    """Case-insensitive equality for SObject / field API names.

    Salesforce SObject and field API names are case-insensitive, so the org GET
    can echo a field in a different case than the plan authored it. Comparing
    case-sensitively here would wrongly fail a correctly-bound field.
    """
    return (a or "").casefold() == (b or "").casefold()


def _terminal_field(hops: List[str]) -> Optional[str]:
    """The deepest hop's field — the real source field a hydration chain lands on.

    A simple mapping is one hop (``Quote.Amount`` -> ``Amount``); a traversal
    nests intermediate lookup hops then the terminal field
    (``QuoteLineItem.Product2`` -> ``Product2.ProductCode`` -> ``ProductCode``).
    """
    if not hops:
        return None
    return hops[-1].rpartition(".")[2] or None


def _binding_mismatch(rule: Dict[str, Any], org_sobject: Optional[str],
                      actual_hops: List[str]) -> bool:
    """True when a matched rule's org binding contradicts what the plan requested.

    Grounded in the canonical model (``docs/references/context-service-patch-shapes.md``,
    ``.cursor/skills/context-service/data-model-and-api.md``): a hydration
    detail's ``queryAttribute`` **is** the source SObject field API name, and
    there is ≤1 detail per attribute mapping — so a simple mapping's terminal
    field must equal the plan's ``sObjectField``. Deliberately lenient to avoid
    blocking valid configs:

    * comparisons are **case-insensitive** (API names are);
    * only the **root SObject** and the **terminal source field** are compared —
      NOT the full hop chain. Multi-hop traversal chains are not fully recoverable
      from the flattened GET (see ``_model._mappings_to_rules`` caveats), so a
      valid deeper traversal that still lands on the requested terminal field is
      NOT a mismatch;
    * an **empty** actual chain is a hydration *gap* (reported separately), not a
      mismatch — this only fires when a chain is present and points elsewhere.
    """
    if not actual_hops:
        return False
    plan_sobject = rule.get("sObject")
    if plan_sobject and org_sobject and not _ci_eq(plan_sobject, org_sobject):
        return True
    # Terminal field the plan requests: childSObjectField for a traversal, else
    # the simple sObjectField.
    expected_terminal = rule.get("childSObjectField") or rule.get("sObjectField")
    if not expected_terminal:
        return False  # plan requested no specific field — nothing to contradict
    return not _ci_eq(expected_terminal, _terminal_field(actual_hops))


def plan_verification(detail: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    """Port of ``_log_verification`` (rlm_context_service.py:1538-1643) that
    **returns** the matched/missing/present structure instead of logging it.

    Result keys: ``matched_rules`` (list of dicts), ``missing_rules`` (list of
    ``(mapping, node, attr)`` tuples), ``found_attrs`` (sorted names),
    ``found_tags`` (sorted ``node.attr:tag`` strings), ``missing_attrs`` /
    ``missing_tags`` (declared-but-absent, sorted), ``hydration_gaps`` (matched
    SOBJECT rules with no hydration detail), ``binding_mismatches`` (matched
    rules whose org ``sObjectName`` / hydration ``queryAttribute`` chain differs
    from the plan's requested ``sObject`` / ``sObjectField`` / traversal),
    ``missing_nodes`` (plan-declared nodes absent from the org),
    ``missing_mappings`` (plan-declared mapping shells absent from the org),
    ``default_mapping_gaps`` (mappings the plan requests as default that the org
    does not flag ``isDefault``), plus ``ok`` (bool). ``ok`` is True only when the
    definition fully realizes the plan: **no** missing mapping rules, **no**
    missing declared attributes/tags, **no** hydration gaps, **no** binding
    mismatches, and **no** missing nodes / mapping shells / default-mapping gaps.
    A matched attribute rule alone is not enough — the field it binds to and the
    node/mapping/default it lives in must all match, or ``--verify`` would certify
    a miswired definition.
    """
    result: Dict[str, Any] = {
        "matched_rules": [],
        "missing_rules": [],
        "found_attrs": [],
        "found_tags": [],
        "missing_attrs": [],
        "missing_tags": [],
        "hydration_gaps": [],
        "binding_mismatches": [],
        "missing_nodes": [],
        "missing_mappings": [],
        "default_mapping_gaps": [],
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
    # Keep the full rule alongside its key so the matched-rule loop can compare
    # the actual org binding (sObjectName + hydration chain) against what the
    # plan requested — the check Finding 1 adds.
    rule_by_key = {
        (r.get("mappingName"), r.get("contextNode"), r.get("contextAttribute")): r
        for r in mapping_rules if isinstance(r, dict)
    }
    tags_by_name = plan.get("contextTagsByName", []) or []
    attrs_by_name = plan.get("contextAttributesByName", []) or []

    matched_rules = []
    binding_mismatches = []
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
                    # Finding 1 — a matched rule is not enough: compare the actual
                    # SObject field binding against the plan's request. CONTEXT
                    # rules bind a context source (no sObjectField), so skip them.
                    rule = rule_by_key.get(key) or {}
                    is_context = (
                        rule.get("mappingType") == "CONTEXT"
                        or rule.get("sourceContextNode")
                    )
                    if not is_context:
                        actual_hops: List[str] = []
                        for h in attr.get("contextAttrHydrationDetailList") or []:
                            if isinstance(h, dict):
                                actual_hops.extend(_hydration_hops(h, sobject))
                        if _binding_mismatch(rule, sobject, actual_hops):
                            binding_mismatches.append({
                                "mapping": mapping_name,
                                "node": node_name,
                                "contextAttribute": attr_name,
                                "expected": {"sObject": rule.get("sObject"),
                                             "hydration": _expected_hydration_hops(rule)},
                                "actual": {"sObject": sobject,
                                           "hydration": actual_hops},
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
                for tag in _client.attr_tag_list(attr):
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

    # Declared-but-absent attributes/tags. Without this, a plan that declares
    # only attributes or only tags returned ok=true even when NONE of them were
    # created (found_attrs / found_tags empty) — the expected sets were never
    # compared. Build the expected set from the plan and subtract what was found.
    found_attr_set = set(found_attrs)
    expected_attrs = {
        f"{a.get('nodeName')}.{a.get('name')}"
        for a in attrs_by_name
        if isinstance(a, dict) and a.get("nodeName") and a.get("name")
    }
    missing_attrs = sorted(expected_attrs - found_attr_set)

    found_tag_set = set(found_tags)
    expected_tags = {
        f"{t.get('nodeName')}.{t.get('attributeName')}:{t.get('name')}"
        for t in tags_by_name
        if isinstance(t, dict) and t.get("nodeName") and t.get("attributeName")
        and t.get("name")
    }
    missing_tags = sorted(expected_tags - found_tag_set)

    # Finding 2 — the plan can declare structural artifacts (nodes, mapping
    # shells, a default mapping) that carry no mappingRules / attributes / tags,
    # so none of the checks above would notice them missing. An empty mapping
    # shell is a valid create-plan artifact. Collect what the plan declares and
    # subtract what the org realizes.
    org_node_names = collect_node_names(detail)
    missing_nodes = sorted(
        node["name"]
        for node in plan.get("contextNodeDefinitions") or []
        if isinstance(node, dict) and node.get("name")
        and node["name"] not in org_node_names
    )

    # Org-side mapping shells: name -> {isDefault, nodeSObjects{node: sObject}}.
    org_mappings: Dict[str, Dict[str, Any]] = {}
    for mapping in version0.get("contextMappings", []) or []:
        if not isinstance(mapping, dict) or not mapping.get("name"):
            continue
        node_sobjects = {}
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if isinstance(node_map, dict) and node_map.get("contextNodeName"):
                node_sobjects[node_map["contextNodeName"]] = node_map.get("sObjectName")
        org_mappings[mapping["name"]] = {
            "isDefault": as_bool(mapping.get("isDefault")),
            "nodeSObjects": node_sobjects,
        }

    # Plan-declared mapping shells come from the contextMappings /
    # contextMappingUpdates blocks (the create/update shell source). A shell is
    # "missing" when its name isn't a mapping on the org; a node SObject binding
    # is a mismatch when the org's shell binds the node to a different sObject
    # than the plan's mappingRules request for that mapping/node.
    missing_mappings: List[str] = []
    for block_key in ("contextMappings", "contextMappingUpdates"):
        block = plan.get(block_key)
        rows = block.get("contextMappings") if isinstance(block, dict) else None
        for row in rows or []:
            if not isinstance(row, dict) or not row.get("name"):
                continue
            if row["name"] not in org_mappings:
                missing_mappings.append(row["name"])
    # A mappingRule naming a mapping the org has no shell for is also a missing
    # shell (rules bind into shells that must already exist).
    for r in mapping_rules:
        if isinstance(r, dict) and r.get("mappingName") and r["mappingName"] not in org_mappings:
            missing_mappings.append(r["mappingName"])
    missing_mappings = sorted(set(missing_mappings))

    # Node SObject binding mismatches: a plan rule requests mapping/node -> sObject
    # but the org's shell binds that node to a different sObject.
    for r in mapping_rules:
        if not isinstance(r, dict):
            continue
        mname, node_name, want_sobject = (
            r.get("mappingName"), r.get("contextNode"), r.get("sObject"))
        if not (mname and node_name and want_sobject):
            continue
        org_map = org_mappings.get(mname)
        if not org_map or node_name not in org_map["nodeSObjects"]:
            continue  # missing shell / node handled elsewhere (missing_mappings / rules)
        actual_sobject = org_map["nodeSObjects"][node_name]
        if actual_sobject and not _ci_eq(actual_sobject, want_sobject) and not any(
            b["mapping"] == mname and b["node"] == node_name for b in binding_mismatches
        ):
            binding_mismatches.append({
                "mapping": mname, "node": node_name, "contextAttribute": None,
                "expected": {"sObject": want_sobject, "hydration": []},
                "actual": {"sObject": actual_sobject, "hydration": []},
            })

    # Requested default mapping (top-level defaultMapping or an isDefault shell
    # row) that the org does not honor.
    requested_defaults = set()
    top_default = plan.get("defaultMapping")
    if isinstance(top_default, str) and top_default:
        requested_defaults.add(top_default)
    for block_key in ("contextMappings", "contextMappingUpdates"):
        block = plan.get(block_key)
        rows = block.get("contextMappings") if isinstance(block, dict) else None
        for row in rows or []:
            if isinstance(row, dict) and as_bool(row.get("isDefault")) and row.get("name"):
                requested_defaults.add(row["name"])
    default_mapping_gaps = sorted(
        name for name in requested_defaults
        if not (org_mappings.get(name) or {}).get("isDefault")
    )

    result["matched_rules"] = matched_rules
    result["missing_rules"] = missing_rules
    result["found_attrs"] = sorted(found_attr_set)
    result["found_tags"] = sorted(found_tag_set)
    result["missing_attrs"] = missing_attrs
    result["missing_tags"] = missing_tags
    result["hydration_gaps"] = hydration_gaps
    result["binding_mismatches"] = binding_mismatches
    result["missing_nodes"] = missing_nodes
    result["missing_mappings"] = missing_mappings
    result["default_mapping_gaps"] = default_mapping_gaps
    # ``ok`` must include every failure the result reports (per the contract):
    # missing mapping rules, missing declared attributes/tags, hydration gaps (a
    # matched SObject rule with no hydration detail), field-binding mismatches (a
    # matched rule bound to the wrong sObject/field — Finding 1), and missing
    # structural artifacts (nodes / mapping shells / requested default — Finding 2).
    result["ok"] = not (
        missing_rules or missing_attrs or missing_tags or hydration_gaps
        or binding_mismatches or missing_nodes or missing_mappings
        or default_mapping_gaps
    )
    return result
