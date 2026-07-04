#!/usr/bin/env python3
"""Shared runtime module for the Context Service **instance** lifecycle.

Where ``_apply``/``_payload`` cover the design-time **definition** (nodes,
attributes, tags, mappings), this module covers the runtime **instance**:
hydrate a context from records, query/inspect the hydrated attribute values,
update them, read/write tags, and persist them back to the mapped SObjects. It
is the shared library behind ``context_session.py`` and the individual runtime
CLI scripts.

EXPERIMENTAL / verify-live (262 / v67.0). Endpoint paths and the
create/query-record/persist/query-tags-leaner body shapes are confirmed against
the public Context Service REST references; the two PATCH bodies
(``update_attributes`` → ``/contexts/attributes``, ``write_through_tags`` →
``/contexts/write-through-tags``) are grounded in internal sources and should be
re-verified on a live org. See ``.cursor/skills/context-service/runtime-and-persistence.md``.

Transport is the injected ``_apply.Transport`` adapter (or any object exposing
``request(method, path, body=None, *, dry_run=None)``) — auth is delegated to the
``sf`` CLI, no access token is ever handled.

**Runtime identity.** A ``contextId`` is a request-scoped opaque cache handle
(UUID/hex), NOT an SObject id — never prefix-validate it. It is not guaranteed to
survive across separate ``sf`` invocations unless the org's "Runtime Context
Instance Reuse to Improve Response Times" setting is on and the call is within
``contextTtl``. That is why the primary entry point (``context_session.py``) does
create→use→persist→delete in one process.

**Dry-run contract.** Mutations (create, persist, both PATCHes, DELETEs) only log
under dry-run. Read-shaped POSTs (``query-record``, ``query-tags[-leaner]``) and
the interface/schema-cache reads always execute (``dry_run=False`` forced), so an
existing ``--context-id`` can still be inspected during a dry run. Because create
is a mutation, a dry-run session has **no real contextId** and skips the
downstream steps that need one, with a log line — no fabricated id.
"""

import json
from typing import Any, Callable, Dict, List, Optional

import _endpoints as ep


# --------------------------------------------------------------------------- #
# Pure body-builders (import-only, unit-tested — no network)
# --------------------------------------------------------------------------- #

def build_create_metadata(
    context_definition_id: str,
    mapping_id: str,
    tagged_data: Optional[bool] = None,
) -> Dict[str, Any]:
    """The ``metadata`` block for ``POST /connect/contexts``.

    ``taggedData`` is included only when explicitly set (True/False) — it is on
    the Context MetaData Input rep per internal sources; omit it otherwise to
    avoid a ``JSON_PARSER_ERROR`` on an org that does not accept it (verify live).
    """
    metadata: Dict[str, Any] = {
        "contextDefinitionId": context_definition_id,
        "mappingId": mapping_id,
    }
    if tagged_data is not None:
        metadata["taggedData"] = bool(tagged_data)
    return metadata


def stringify_data(records: Any) -> str:
    """Serialize the records object to the **stringified JSON** the ``data`` field
    expects. The create body carries ``data`` as a JSON *string*, not a nested
    object: ``{"metadata": {...}, "data": "<stringified JSON>"}``."""
    if isinstance(records, str):
        # Already a JSON string — trust it (caller passed pre-stringified data).
        return records
    return json.dumps(records)


def build_create_body(
    context_definition_id: str,
    mapping_id: str,
    records: Any,
    tagged_data: Optional[bool] = None,
) -> Dict[str, Any]:
    """Full ``POST /connect/contexts`` body."""
    return {
        "metadata": build_create_metadata(context_definition_id, mapping_id, tagged_data),
        "data": stringify_data(records),
    }


def build_node_path(data_path: Optional[List[str]]) -> Dict[str, Any]:
    """A ``nodePath`` wrapper: ``{"nodePath": {"dataPath": [...]}}``.

    ``dataPath`` is the ordered node-name path from the root node to the target
    node (empty list = the root node itself).
    """
    return {"nodePath": {"dataPath": list(data_path or [])}}


def build_update_attributes_body(
    context_id: str, updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Body for ``PATCH /connect/contexts/attributes`` (verify-live).

    ``updates`` is a list of ``{"dataPath": [...], "attributes": [{"attributeName",
    "attributeValue"}, ...]}`` entries. Shaped into the documented-internal
    ``updateContextAttributesInput`` envelope.
    """
    node_path_and_attributes = []
    for entry in updates:
        node_path_and_attributes.append({
            **build_node_path(entry.get("dataPath")),
            "attributes": [
                {"attributeName": a["attributeName"], "attributeValue": a.get("attributeValue")}
                for a in (entry.get("attributes") or [])
            ],
        })
    return {
        "updateContextAttributesInput": {
            "contextId": context_id,
            "nodePathAndAttributes": node_path_and_attributes,
        }
    }


def build_write_tags_body(
    context_id: str, tag_updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Body for ``PATCH /connect/contexts/write-through-tags`` (verify-live).

    ``tag_updates`` is a list of ``{"dataPath": [...], "tagValues": [{"tagName",
    "tagValue"}, ...]}`` entries.
    """
    node_path_and_tag_values = []
    for entry in tag_updates:
        node_path_and_tag_values.append({
            **build_node_path(entry.get("dataPath")),
            "tagValues": [
                {"tagName": t["tagName"], "tagValue": t.get("tagValue")}
                for t in (entry.get("tagValues") or [])
            ],
        })
    return {
        "contextId": context_id,
        "nodePathAndTagValues": node_path_and_tag_values,
    }


def build_query_record_body(
    context_id: str,
    attributes: Optional[List[str]] = None,
    business_object_type_filter: Optional[str] = None,
    query_path: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Body for ``POST /connect/contexts/query-record``.

    Only non-empty optional keys are included — an empty ``attributes`` list means
    "all attributes", so it is omitted rather than sent as ``[]``.
    """
    body: Dict[str, Any] = {"contextId": context_id}
    if attributes:
        body["attributes"] = list(attributes)
    if business_object_type_filter:
        body["businessObjectTypeFilter"] = business_object_type_filter
    if query_path:
        body["queryPath"] = list(query_path)
    return body


def build_query_tags_body(context_id: str, tags: List[str]) -> Dict[str, Any]:
    """Body for ``POST /connect/contexts/query-tags[-leaner]`` (same input shape)."""
    return {"contextId": context_id, "tags": list(tags or [])}


def build_persist_body(context_id: str, target_mapping_id: str) -> Dict[str, Any]:
    """Body for ``POST /connect/contexts/persist-records``."""
    return {
        "contextPersistInput": {
            "contextId": context_id,
            "targetMappingId": target_mapping_id,
        }
    }


# --------------------------------------------------------------------------- #
# Query-result shaping (import-only, unit-tested)
# --------------------------------------------------------------------------- #

def flatten_query_records(result: Any) -> List[Dict[str, Any]]:
    """Flatten a Query Context Record Result into rows with a ``depth`` field.

    Descends the recursive ``queryRecords[].childQueryRecords[...]`` tree. Each
    row is a shallow copy of the record with ``childQueryRecords`` removed and
    ``depth`` (0 at the top) added, preserving parent-before-child order.
    """
    rows: List[Dict[str, Any]] = []

    def walk(records, depth):
        for rec in records or []:
            if not isinstance(rec, dict):
                continue
            children = rec.get("childQueryRecords") or []
            row = {k: v for k, v in rec.items() if k != "childQueryRecords"}
            row["depth"] = depth
            rows.append(row)
            walk(children, depth + 1)

    if isinstance(result, dict):
        walk(result.get("queryRecords") or [], 0)
    elif isinstance(result, list):
        walk(result, 0)
    return rows


def decode_compound_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort decode of stringified compound values in a query record.

    ``record.attributesAndValues`` may carry compound values (e.g. an Address) as
    a **stringified** JSON blob. Parse any string value that looks like JSON
    (starts with ``{`` or ``[``) and replace it with the parsed object; leave the
    raw string untouched when it does not parse. Returns a new record; the caller
    keeps the original for the ``--json`` (raw) path.
    """
    if not isinstance(record, dict):
        return record
    out = dict(record)
    values = record.get("attributesAndValues")
    if isinstance(values, dict):
        decoded = {}
        for name, value in values.items():
            if isinstance(value, str):
                stripped = value.strip()
                if stripped[:1] in ("{", "["):
                    try:
                        decoded[name] = json.loads(stripped)
                        continue
                    except (ValueError, TypeError):
                        pass
            decoded[name] = value
        out["attributesAndValues"] = decoded
    return out


# --------------------------------------------------------------------------- #
# Hydration-payload skeleton builder (import-only, unit-tested)
# --------------------------------------------------------------------------- #

_PLACEHOLDER_BY_DATATYPE = {
    "STRING": "",
    "TEXT": "",
    "TEXTAREA": "",
    "PICKLIST": "",
    "REFERENCE": "",
    "ID": "",
    "NUMBER": 0,
    "DOUBLE": 0,
    "INTEGER": 0,
    "CURRENCY": 0,
    "PERCENT": 0,
    "BOOLEAN": False,
}


def _placeholder_for(datatype: Optional[str]) -> Any:
    """A fillable placeholder value for an attribute of the given dataType.

    Typed so the author sees the expected kind at a glance; ``None`` (JSON null)
    for anything unrecognized (dates, compound, etc.).
    """
    if not datatype:
        return None
    return _PLACEHOLDER_BY_DATATYPE.get(str(datatype).upper(), None)


def _node_attr_list(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    container = node.get("attributes", {})
    if isinstance(container, list):
        return [a for a in container if isinstance(a, dict)]
    if isinstance(container, dict):
        return [a for a in (container.get("contextAttributes") or []) if isinstance(a, dict)]
    return []


def _child_node_list(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    container = node.get("childNodes", {})
    if isinstance(container, list):
        return [n for n in container if isinstance(n, dict)]
    if isinstance(container, dict):
        return [n for n in (container.get("contextNodes") or []) if isinstance(n, dict)]
    return []


def node_sobject_lookup(mapping: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """``{contextNodeName: sObjectName}`` from a context mapping's node mappings.

    **This lookup is load-bearing for hydration** (live-verified, v67.0): the
    ``businessObjectType`` in the ``data`` payload must be the **mapped SObject
    name** (e.g. ``Quote``), *not* the context node name (e.g. ``SalesTransaction``).
    A payload whose ``businessObjectType`` is the node name hydrates **zero
    records** — the engine silently returns empty tag results (``recordIds: []``)
    with ``isSuccess: true``, which reads like a definition/permission problem but
    is really a node-name-vs-SObject-name mismatch.

    ``contextNodeMappings`` is a flat list (not nested) keyed ``contextNodeName``
    → ``sObjectName``. Returns ``{}`` for a missing/empty mapping so callers fall
    back to the node name (still the only sensible default with no mapping).
    """
    lookup: Dict[str, str] = {}
    if not isinstance(mapping, dict):
        return lookup
    for nm in mapping.get("contextNodeMappings") or []:
        if not isinstance(nm, dict):
            continue
        node_name = nm.get("contextNodeName")
        sobject = nm.get("sObjectName")
        if node_name and sobject:
            lookup[node_name] = sobject
    return lookup


def _skeleton_record(
    node: Dict[str, Any], sobject_by_node: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """One placeholder record for a node: id + businessObjectType + attrs + children.

    ``businessObjectType`` is the node's **mapped SObject name** when
    ``sobject_by_node`` supplies one (the shape hydration actually requires — see
    ``node_sobject_lookup``); it falls back to the node name only when no mapping
    row is available.
    """
    sobject_by_node = sobject_by_node or {}
    name = node.get("name")
    business_object_type = sobject_by_node.get(name, name)
    record: Dict[str, Any] = {"id": "", "businessObjectType": business_object_type}
    for attr in _node_attr_list(node):
        attr_name = attr.get("name")
        if attr_name and attr_name not in record:
            record[attr_name] = _placeholder_for(attr.get("dataType"))
    for child in _child_node_list(node):
        child_name = child.get("name")
        if child_name:
            # A child node hydrates as an array under its node name (key stays the
            # node name; only businessObjectType is the mapped SObject).
            record[child_name] = [_skeleton_record(child, sobject_by_node)]
    return record


def build_hydration_skeleton(
    detail: Dict[str, Any],
    *,
    node_filter: Optional[List[str]] = None,
    mapping: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a ``data``-payload skeleton from a definition detail (read-only shaping).

    Walks the active version's node tree and emits ``{nodeName: [placeholder
    record]}`` — each record carrying ``id`` (empty), ``businessObjectType``,
    every attribute as a typed placeholder, and each child node as a nested
    single-element array. The author fills in real ids/values, then feeds it to
    ``create``/``context_session`` via ``--data-file``.

    Pass ``mapping`` (the context mapping the instance will hydrate with) so each
    record's ``businessObjectType`` is the **mapped SObject name** — the shape
    hydration requires (live-verified). Without a mapping the node name is used,
    which does **not** hydrate; ``build_hydration_data.py`` always resolves and
    passes the mapping.

    With ``node_filter`` set, only nodes whose ``name`` is in the filter become
    top-level keys (each with its full subtree) — restrict to a subtree without
    hand-editing the whole payload.
    """
    import _client  # local import to avoid a hard dep for pure-helper importers

    sobject_by_node = node_sobject_lookup(mapping)

    version = _client.active_version(detail)
    top_nodes = version.get("contextNodes") if isinstance(version, dict) else None
    top_nodes = [n for n in (top_nodes or []) if isinstance(n, dict)]

    skeleton: Dict[str, Any] = {}
    if node_filter:
        wanted = set(node_filter)
        # Find every node (at any depth) whose name is wanted; emit as top-level.
        for node, _depth in _client.iter_nodes(top_nodes):
            if node.get("name") in wanted:
                skeleton[node["name"]] = [_skeleton_record(node, sobject_by_node)]
    else:
        for node in top_nodes:
            name = node.get("name")
            if name:
                skeleton[name] = [_skeleton_record(node, sobject_by_node)]
    return skeleton


def build_from_record_skeleton(
    detail: Dict[str, Any],
    *,
    root_id: str,
    node_name: Optional[str] = None,
    mapping: Optional[Dict[str, Any]] = None,
) -> "tuple[Optional[Dict[str, Any]], Optional[str]]":
    """Build an **id-only** hydration payload for a single root record.

    Unlike ``build_hydration_skeleton`` (which emits every attribute as a fillable
    placeholder and each child node as a nested array to hand-populate), this emits
    the minimal ``{nodeName: [{"id": root_id, "businessObjectType": <mapped
    SObject>}]}`` — nothing else.

    That is the whole payload because an id-only record hydrates the mapped SObject
    **and its child nodes** server-side (live-verified, v67.0): the runtime walks
    the mapping's node tree and queries the children itself, so child arrays and
    attribute placeholders are unnecessary. (Inline attribute values only matter as
    what-if *overrides* of the org-queried values — use ``build_hydration_skeleton``
    when you want to supply those.)

    Root-node selection: ``node_name`` picks a top-level node by name; when it is
    omitted and the definition has exactly one top-level node, that node is used; an
    ambiguous choice (multiple top-level nodes, no ``node_name``) returns an error
    so the caller can ask for ``--node``. Returns ``(skeleton_or_None,
    error_or_None)``.
    """
    import _client  # local import — keep pure-helper importers free of the dep

    version = _client.active_version(detail)
    top_nodes = version.get("contextNodes") if isinstance(version, dict) else None
    top_nodes = [
        n for n in (top_nodes or []) if isinstance(n, dict) and n.get("name")
    ]
    if not top_nodes:
        return None, "No top-level nodes on the active version — nothing to hydrate."

    if node_name:
        node = next((n for n in top_nodes if n.get("name") == node_name), None)
        if node is None:
            available = ", ".join(sorted(n["name"] for n in top_nodes))
            return None, (
                f"No top-level node named '{node_name}'. Top-level nodes: {available}."
            )
    elif len(top_nodes) == 1:
        node = top_nodes[0]
    else:
        available = ", ".join(sorted(n["name"] for n in top_nodes))
        return None, (
            "Multiple top-level nodes — pass --node to name the one your record id "
            f"belongs to. Top-level nodes: {available}."
        )

    sobject_by_node = node_sobject_lookup(mapping)
    name = node["name"]
    business_object_type = sobject_by_node.get(name, name)
    return {name: [{"id": root_id, "businessObjectType": business_object_type}]}, None


# --------------------------------------------------------------------------- #
# Runtime client (thin, testable transport wrappers)
# --------------------------------------------------------------------------- #

class RuntimeContextClient:
    """Thin wrappers over the transport for the runtime instance endpoints.

    Mutations honor the transport's ``dry_run`` (so a dry-run session only logs
    them). Reads (``query_record``, ``query_tags``, ``clear_runtime_schema``, the
    interface lookups) force ``dry_run=False`` on the call so they still execute
    against a live ``contextId`` under a dry-run session, per the dry-run contract.
    """

    def __init__(self, transport, logger: Optional[Callable[..., None]] = None):
        self.t = transport
        self.log = logger or getattr(transport, "logger", None) or print
        self.dry_run = getattr(transport, "dry_run", False)

    # ---- mutations (honor dry_run) --------------------------------------- #

    def create_instance(self, *, context_definition_id, mapping_id, data,
                        tagged_data=None) -> Any:
        body = build_create_body(context_definition_id, mapping_id, data, tagged_data)
        return self.t.request("POST", ep.CONTEXTS_COLLECTION, body)

    def get_instance(self, context_id: str) -> Any:
        # A GET is always a read; force execution regardless of dry-run.
        return self.t.request(
            "GET", ep.CONTEXT_ITEM.format(context_id=context_id), dry_run=False
        )

    def delete_instance(self, context_id: str) -> Any:
        return self.t.request("DELETE", ep.CONTEXT_ITEM.format(context_id=context_id))

    def update_attributes(self, context_id: str,
                          updates: List[Dict[str, Any]]) -> Any:
        body = build_update_attributes_body(context_id, updates)
        return self.t.request("PATCH", ep.CONTEXT_ATTRIBUTES, body)

    def write_through_tags(self, context_id: str,
                          tag_updates: List[Dict[str, Any]]) -> Any:
        body = build_write_tags_body(context_id, tag_updates)
        return self.t.request("PATCH", ep.CONTEXT_WRITE_THROUGH_TAGS, body)

    def persist_records(self, *, context_id: str, target_mapping_id: str) -> Any:
        body = build_persist_body(context_id, target_mapping_id)
        return self.t.request("POST", ep.CONTEXT_PERSIST_RECORDS, body)

    # ---- reads (ALWAYS execute, even under dry-run) ---------------------- #

    def query_record(self, *, context_id: str, children: bool = True,
                    attributes=None, business_object_type_filter=None,
                    query_path=None) -> Any:
        body = build_query_record_body(
            context_id, attributes, business_object_type_filter, query_path
        )
        children_flag = "true" if children else "false"
        path = f"{ep.CONTEXT_QUERY_RECORD}?children={children_flag}"
        return self.t.request("POST", path, body, dry_run=False)

    def query_tags(self, *, context_id: str, tags: List[str],
                  leaner: bool = False) -> Any:
        body = build_query_tags_body(context_id, tags)
        path = ep.CONTEXT_QUERY_TAGS_LEANER if leaner else ep.CONTEXT_QUERY_TAGS
        return self.t.request("POST", path, body, dry_run=False)

    def clear_runtime_schema(self, *, context_definition_name: str,
                            mapping_names: Optional[List[str]] = None) -> Any:
        # A schema-cache eviction (a DELETE) — honors dry_run like the other
        # mutations. Parameters are query-string, URL-encoded via the client.
        from urllib.parse import quote
        params = [f"contextDefinitionName={quote(context_definition_name)}"]
        if mapping_names:
            params.append(f"contextMappingNames={quote(','.join(mapping_names))}")
        path = f"{ep.CONTEXT_RUNTIME_SCHEMA_CLEAR}?{'&'.join(params)}"
        return self.t.request("DELETE", path)

    def list_definition_interfaces(self) -> Any:
        return self.t.request(
            "GET", ep.CONTEXT_DEFINITION_INTERFACES, dry_run=False
        )

    def get_definition_interface(self, name: str) -> Any:
        from urllib.parse import quote
        path = ep.CONTEXT_DEFINITION_INTERFACE_ITEM.format(name=quote(name))
        return self.t.request("GET", path, dry_run=False)


# --------------------------------------------------------------------------- #
# Session orchestrator (create → use → persist → delete, one process)
# --------------------------------------------------------------------------- #

class RuntimeSession:
    """Round-trip a runtime context instance within a single process.

    Because a ``contextId`` is request-scoped, the reliable way to exercise the
    runtime lifecycle is to create, use, persist, and delete back-to-back. This
    orchestrator does exactly that and returns a structured summary.
    """

    def __init__(self, client: RuntimeContextClient,
                 logger: Optional[Callable[..., None]] = None):
        self.client = client
        self.log = logger or client.log
        self.dry_run = client.dry_run

    def _extract_context_id(self, create_response: Any) -> Optional[str]:
        if isinstance(create_response, dict):
            return create_response.get("contextId") or create_response.get("id")
        return None

    def run(self, *, create_spec: Optional[Dict[str, Any]] = None,
            existing_context_id: Optional[str] = None,
            attribute_updates: Optional[List[Dict[str, Any]]] = None,
            tag_writes: Optional[List[Dict[str, Any]]] = None,
            do_query: bool = False,
            query_spec: Optional[Dict[str, Any]] = None,
            persist_target_mapping_id: Optional[str] = None,
            keep_instance: bool = False) -> Dict[str, Any]:
        """Execute the requested runtime lifecycle steps in order.

        create (or reuse ``existing_context_id``) → update_attributes →
        write_through_tags → query_record → persist_records → delete_instance
        (unless ``keep_instance`` or reusing an existing id). Returns
        ``{context_id, created, query?, persist?, deleted, dry_run}``.

        Dry-run: create only logs, so there is no real id — the dependent steps
        are skipped with a log line (no fabricated id). An ``existing_context_id``
        is still usable for the read steps under dry-run.
        """
        summary: Dict[str, Any] = {
            "dry_run": self.dry_run,
            "created": False,
            "context_id": None,
            "deleted": False,
        }

        context_id = existing_context_id
        reused = bool(existing_context_id)

        if not context_id and create_spec is not None:
            resp = self.client.create_instance(**create_spec)
            summary["create_response"] = resp
            if self.dry_run:
                self.log(
                    "[dry-run] create only logged — no contextId minted; "
                    "skipping attribute/tag/query/persist/delete steps that need one."
                )
                return summary
            context_id = self._extract_context_id(resp)
            summary["created"] = bool(context_id)
            if not context_id:
                self.log("Create returned no contextId; aborting session.")
                return summary

        if not context_id:
            self.log("No contextId (nothing created, none supplied); nothing to do.")
            return summary

        summary["context_id"] = context_id

        if attribute_updates:
            summary["attributes_response"] = self.client.update_attributes(
                context_id, attribute_updates
            )
        if tag_writes:
            summary["write_tags_response"] = self.client.write_through_tags(
                context_id, tag_writes
            )
        if do_query:
            query_spec = query_spec or {}
            summary["query"] = self.client.query_record(
                context_id=context_id, **query_spec
            )
        if persist_target_mapping_id:
            summary["persist"] = self.client.persist_records(
                context_id=context_id, target_mapping_id=persist_target_mapping_id
            )

        # Evict the instance unless the caller wants to keep it or is operating on
        # a supplied (reused) id it did not create.
        if not keep_instance and not reused:
            self.client.delete_instance(context_id)
            summary["deleted"] = not self.dry_run

        return summary
