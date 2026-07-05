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
import time
from typing import Any, Callable, Dict, List, Optional

import _client
import _endpoints as ep

# ``persist-records`` is asynchronous: the synchronous response returns a
# ``referenceId`` that is the **Id of an AsyncOperationTracker row** (live-verified
# 2026-07-05 on rlm-base__july4_ctxPilot — the returned referenceId equalled
# ``AsyncOperationTracker.Id`` exactly). The real per-node outcome lands on that
# row's ``Response`` (JSON with ``savedNodes``/``skippedNodes``/``errorNodes`` on
# success; a plain error string on failure) once ``Status`` reaches a terminal
# value. Polling by Id is therefore deterministic — no "most recent row" heuristic.
_PERSIST_TERMINAL_STATUSES = frozenset(
    {"Completed", "CompletedWithFailures", "Failure"}
)
_PERSIST_FAILURE_STATUSES = frozenset({"CompletedWithFailures", "Failure"})


# --------------------------------------------------------------------------- #
# Pure body-builders (import-only, unit-tested — no network)
# --------------------------------------------------------------------------- #

def build_create_metadata(
    context_definition_id: str,
    mapping_id: str,
    tagged_data: Optional[bool] = None,
    context_scope: Optional[str] = None,
) -> Dict[str, Any]:
    """The ``metadata`` block for ``POST /connect/contexts``.

    ``taggedData`` is included only when explicitly set (True/False) — it is on
    the Context MetaData Input rep per internal sources; omit it otherwise to
    avoid a ``JSON_PARSER_ERROR`` on an org that does not accept it (verify live).

    ``contextScope`` controls cross-call survival of the minted ``contextId``:
    - ``REQUEST`` (default when omitted) — thread/request-local, ~15 s TTL,
      cannot be looked up by a later HTTP call.
    - ``SESSION`` — persisted to a distributed cache, survives across calls
      (subject to ``contextTtl``). **Pilot-gated**: requires the
      ``SessionScopeContext`` user permission (via ``ContextServicePilot``).
      Live-verified on 262 / v67.0.
    """
    metadata: Dict[str, Any] = {
        "contextDefinitionId": context_definition_id,
        "mappingId": mapping_id,
    }
    if tagged_data is not None:
        metadata["taggedData"] = bool(tagged_data)
    if context_scope is not None:
        metadata["contextScope"] = context_scope.upper()
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
    context_scope: Optional[str] = None,
) -> Dict[str, Any]:
    """Full ``POST /connect/contexts`` body."""
    return {
        "metadata": build_create_metadata(
            context_definition_id, mapping_id, tagged_data, context_scope
        ),
        "data": stringify_data(records),
    }


def build_node_path(data_path: Optional[List[str]]) -> Dict[str, Any]:
    """A ``nodePath`` wrapper: ``{"nodePath": {"dataPath": [...]}}``.

    ``dataPath`` is an ordered list of **record IDs** from root to target
    (e.g. ``["0Q0...quoteId"]`` for a root-level record, or
    ``["0Q0...quoteId", "0QL...lineId"]`` for a child). Empty list or
    node-name paths return ``isSuccess=true`` but **silently no-op** — the
    value is never mutated. Live-verified on 262 / v67.0.
    """
    return {"nodePath": {"dataPath": list(data_path or [])}}


def build_update_attributes_body(
    context_id: str, updates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Body for ``PATCH /connect/contexts/attributes`` (live-verified, v67.0).

    ``updates`` is a list of ``{"dataPath": [...], "attributes": [{"attributeName",
    "attributeValue"}, ...]}`` entries.

    **Flat shape** — ``contextId`` + ``nodePathAndAttributes`` at the top level,
    NOT wrapped in ``updateContextAttributesInput``. The wrapped form is rejected
    with ``JSON_PARSER_ERROR: Unrecognized field "updateContextAttributesInput"``.
    Live-verified on a ContextServicePilot org (262 / v67.0).
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
        "contextId": context_id,
        "nodePathAndAttributes": node_path_and_attributes,
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
    """Body for ``POST /connect/contexts/persist-records``.

    **Flat shape, live-verified (v67.0).** The endpoint takes ``contextId`` and
    ``targetMappingId`` at the top level — NOT wrapped in a ``contextPersistInput``
    object. The public doc shows the wrapper, but a live POST of the wrapped form
    is rejected at the parser (``JSON_PARSER_ERROR: Unrecognized field
    "contextPersistInput"``) while the flat form parses and reaches contextId
    validation. This matches the Apex ``persistContext`` example, which passes a
    flat ``{contextId, targetMappingId}`` map.
    """
    return {"contextId": context_id, "targetMappingId": target_mapping_id}


def build_persist_tracker_soql(reference_id: str) -> str:
    """SOQL to look up the ``AsyncOperationTracker`` row for a persist ``referenceId``.

    The persist ``referenceId`` **is** the tracker row Id (live-verified), so this
    is a direct Id lookup — deterministic, no ``JobType``/``CreatedDate`` ordering
    needed. ``reference_id`` is escaped for the single-quoted literal because it
    reaches the query as free text from the persist response.
    """
    return (
        "SELECT Id, Status, Response, JobType, CreatedDate "
        "FROM AsyncOperationTracker "
        f"WHERE Id = '{_client.soql_literal(reference_id)}'"
    )


def decode_persist_response(response: Any) -> Any:
    """Parse an ``AsyncOperationTracker.Response`` value.

    On a successful persist the ``Response`` is a JSON object
    (``savedNodes``/``skippedNodes``/``errorNodes``); on a hard failure it is a
    plain error string (e.g. *"An unexpected error occurred… ErrorId: …"*). Parse
    JSON when it looks like JSON, otherwise return the raw value untouched so the
    caller can surface the error text.
    """
    if isinstance(response, (dict, list)) or response is None:
        return response
    if isinstance(response, str):
        stripped = response.strip()
        if stripped[:1] in ("{", "["):
            try:
                return json.loads(stripped)
            except (ValueError, TypeError):
                return response
    return response


def summarize_persist_tracker(
    row: Optional[Dict[str, Any]], *, timed_out: bool = False
) -> Dict[str, Any]:
    """Reduce an ``AsyncOperationTracker`` row to a persist-outcome summary.

    Returns a dict with ``found``/``status``/``is_terminal``/``is_failure`` plus
    the decoded ``saved``/``skipped``/``errors`` node maps and the ``raw_response``.
    ``is_failure`` is ``None`` until the job is terminal; a terminal job is a
    failure when its ``Status`` is a failure status **or** its ``errorNodes`` map
    is non-empty (a ``Completed`` status with populated ``errorNodes`` is the
    documented dirty-persist signature and must not read as success).
    """
    if not isinstance(row, dict):
        return {
            "found": False, "timed_out": timed_out, "status": None,
            "is_terminal": False, "is_failure": None,
            "saved": None, "skipped": None, "errors": None, "raw_response": None,
        }
    status = row.get("Status")
    is_terminal = status in _PERSIST_TERMINAL_STATUSES
    parsed = decode_persist_response(row.get("Response"))
    saved = parsed.get("savedNodes") if isinstance(parsed, dict) else None
    skipped = parsed.get("skippedNodes") if isinstance(parsed, dict) else None
    errors = parsed.get("errorNodes") if isinstance(parsed, dict) else None
    is_failure: Optional[bool] = None
    if is_terminal:
        is_failure = (status in _PERSIST_FAILURE_STATUSES) or bool(errors)
    return {
        "found": True,
        "id": row.get("Id"),
        "status": status,
        "is_terminal": is_terminal,
        "timed_out": timed_out and not is_terminal,
        "is_failure": is_failure,
        "saved": saved,
        "skipped": skipped,
        "errors": errors,
        "raw_response": parsed,
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
                        tagged_data=None, context_scope=None) -> Any:
        body = build_create_body(
            context_definition_id, mapping_id, data, tagged_data, context_scope
        )
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

    def confirm_persist(
        self, reference_id: str, *,
        poll_seconds: float = 30.0, interval_seconds: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> Dict[str, Any]:
        """Poll ``AsyncOperationTracker`` until the persist job is terminal.

        ``persist-records`` is async — its synchronous ``referenceId`` is the Id
        of the tracker row that carries the real outcome. Poll that row (a SOQL
        read, so it runs even under a dry-run transport) until ``Status`` reaches
        a terminal value or ``poll_seconds`` elapses, then return the summary from
        :func:`summarize_persist_tracker`. A persist that "succeeded"
        synchronously but wrote nothing (``errorNodes`` populated, or a ``Failure``
        status) comes back with ``is_failure=True`` — the whole point of the poll.

        ``sleep`` is injectable so unit tests can drive the loop without real time.
        """
        if not reference_id:
            return summarize_persist_tracker(None)
        soql = build_persist_tracker_soql(reference_id)
        deadline = poll_seconds
        elapsed = 0.0
        last_row: Optional[Dict[str, Any]] = None
        while True:
            rows = self.t.soql(soql)
            last_row = rows[0] if rows else None
            summary = summarize_persist_tracker(last_row)
            if summary["is_terminal"]:
                return summary
            if elapsed >= deadline:
                return summarize_persist_tracker(last_row, timed_out=True)
            sleep(interval_seconds)
            elapsed += interval_seconds

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
            confirm_persist: bool = True,
            persist_poll_seconds: float = 30.0,
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
            # A create can return ``isSuccess:false`` (with or without a
            # contextId) — do not proceed to query/persist an instance the
            # platform reported as failed. Surface it and abort.
            if isinstance(resp, dict) and resp.get("isSuccess") is False:
                summary["create_failed"] = True
                self.log(
                    "Create returned isSuccess:false; aborting session. "
                    f"Response: {json.dumps(resp)}"
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
            persist_resp = self.client.persist_records(
                context_id=context_id, target_mapping_id=persist_target_mapping_id
            )
            summary["persist"] = persist_resp
            # persist-records is async — the referenceId is a tracker Id, not a
            # success signal. Poll AsyncOperationTracker for the real outcome so a
            # dirty persist (errorNodes / Failure) is not reported as success.
            # Skipped under dry-run (no real persist ran → no tracker row).
            if confirm_persist and not self.dry_run:
                reference_id = (
                    (persist_resp.get("referenceId") or persist_resp.get("id"))
                    if isinstance(persist_resp, dict) else None
                )
                if reference_id:
                    outcome = self.client.confirm_persist(
                        reference_id, poll_seconds=persist_poll_seconds
                    )
                    summary["persist_outcome"] = outcome
                    if outcome.get("is_failure"):
                        self.log(
                            "Persist FAILED per AsyncOperationTracker "
                            f"(status={outcome.get('status')}): "
                            f"{json.dumps(outcome.get('raw_response'), default=str)}"
                        )
                    elif outcome.get("timed_out"):
                        self.log(
                            "Persist still running after poll window "
                            f"(status={outcome.get('status')}); confirm "
                            f"AsyncOperationTracker Id={reference_id} manually."
                        )
                else:
                    self.log(
                        "Persist returned no referenceId; cannot confirm async "
                        "outcome via AsyncOperationTracker."
                    )

        # Evict the instance unless the caller wants to keep it or is operating on
        # a supplied (reused) id it did not create.
        if not keep_instance and not reused:
            self.client.delete_instance(context_id)
            summary["deleted"] = not self.dry_run

        return summary
