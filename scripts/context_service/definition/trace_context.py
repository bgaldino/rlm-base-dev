#!/usr/bin/env python3
"""Trace how SObject fields link to Context tags/attributes — and back (read-only).

Answers the two questions ``describe_context.py`` cannot:

* **Hydration** — *"how does a specific SObject field get loaded into the context?"*
  Which context attribute/tag reads ``QuoteLineItem.RLM_RampMode__c``, in which
  mapping (lens), and in which direction.
* **Persistence** — *"how does a context attribute/tag get written back to a
  field?"* The **same** binding, run in the opposite direction. Context Service
  has **no** separate persistence structure: ``ContextAttrHydrationDetail``
  (``sObjectDomain`` + ``queryAttribute``) is the single object that describes an
  attribute<->SObject.field binding for **both** read and write. Direction is
  governed by the mapping's ``intents`` (``HYDRATION`` reads, ``PERSISTENCE``
  writes) and the attribute's ``fieldType`` (``INPUT`` read-only, ``OUTPUT``
  write-only, ``INPUTOUTPUT`` both, ``AGGREGATE`` computed; ``isTransient`` is
  skipped on persist).

The trace is a pure join over one Connect GET, keyed on ``contextAttributeId``:

    ContextTag ──(contextAttributeId)──▶ ContextAttribute ──(contextAttributeId,
    per ContextAttributeMapping)──▶ SObject.field  (contextAttrHydrationDetailList)

Layer 1 (node -> attribute -> tag) is SObject-agnostic; Layer 2 (mapping ->
node-mapping -> attribute-mapping -> hydration) binds the *same* attribute to a
*different* SObject per mapping. So one attribute/tag can bind to several fields
(one per lens) — QuoteLineItem in ``QuoteEntitiesMapping``, OrderItem in
``OrderEntitiesMapping``, etc.

The three selectors match on **different axes** and are not interchangeable:

* ``--field`` matches **SObject field** names at *any* traversal hop
  (case-insensitive substring of ``Object.field``) — the reverse lookup.
* ``--tag`` matches **tag** names (case-insensitive **substring**) — forward.
* ``--attribute`` matches the **attribute** name (``node.attr`` or bare, exact).

So ``--field ProductCode`` and ``--tag ProductCode`` overlap but differ:
``--field`` returns only field-bound rows named ``ProductCode``; ``--tag``, being
a substring over tag names, also matches ``ItemProductCode`` /
``RootItemProductCode`` and surfaces lenses where the attribute carries the tag
but binds no field (including transient/computed attributes). For the exact
forward mirror of a ``--field`` result, use ``--attribute Node.Attr`` (exact)
rather than the fuzzy ``--tag``. The substring behavior is deliberate.

Auth is delegated to the sf CLI (see _client.py) — no tokens are handled here.
Read-only: this tool never mutates. Pinned to Release 262 / API v67.0; re-verify
the GET response shape against a live org if the platform changes.

FLS caveat (live-verified v67.0): this tool reads the Connect GET, which HONORS
the running user's field-level security. A field that is *physically* bound
(``ContextAttributeMapping`` + ``ContextAttrHydrationDetail`` rows exist) but
that the running user cannot read is FILTERED OUT of the GET and shows here as
``(no field bound)`` — indistinguishable from a genuinely unmapped attribute.
The renderer prints a note when a non-transient attribute is unbound in a lens;
grant read on the field (or run as a user who has it) to surface a hidden
binding. This is also why a newly mapped field can look unbound until FLS is
granted — it is an FLS effect, not a missing activate/deactivate cycle.

Usage:
    # everything that touches a field (hydration + persistence, every lens)
    python scripts/context_service/trace_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --field RLM_RampMode__c

    # every field a tag reads/writes, across all mappings
    python scripts/context_service/trace_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --tag RampMode__c

    # one attribute (node.attr or bare name); scope to one lens with --mapping
    python scripts/context_service/trace_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --attribute SalesTransactionItem.RampMode__c --mapping QuoteEntitiesMapping

    # find gaps: tagged-but-unbound, bound-but-untagged, inert attributes
    python scripts/context_service/trace_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --unmapped

    # default: per-mapping binding summary (no selector)
    python scripts/context_service/trace_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._client import (  # noqa: E402
    ContextClientError,
    active_version,
    connect_get,
    definition_developer_name,
    eprint,
    iter_nodes,
    node_attributes,
    normalize_definition_list,
)

# fieldType read/write eligibility (Core UDD enum). INPUT is hydration-only,
# OUTPUT is persist-only, INPUTOUTPUT is both, AGGREGATE is computed (rollup) —
# not a plain field write, so it is reported separately, never as "persist".
_READ_TYPES = {"INPUT", "INPUTOUTPUT"}
_WRITE_TYPES = {"OUTPUT", "INPUTOUTPUT"}


def _as_bool(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


def _resolve_id(developer_name: str, target_org: str, api_version: str) -> Optional[str]:
    """Resolve a definition id from a developerName via the list endpoint.

    Mirrors describe_context._resolve_id — includeInactive=true so an inactive
    definition still resolves, and the shared normalizer/name reader so the two
    tools see the same set of definitions.
    """
    response = connect_get(
        "connect/context-definitions?includeInactive=true", target_org, api_version
    )
    for item in normalize_definition_list(response):
        if definition_developer_name(item) == developer_name:
            return item.get("contextDefinitionId")
    return None


def _walk_hydration(detail: Dict[str, Any], node_sobject: Optional[str]) -> List[str]:
    """Flatten one hydration detail (and its ``childDetails`` chain) to hops.

    A **simple** mapping is one detail: ``QuoteLineItem.RLM_RampMode__c``. A
    **relationship traversal** nests a child detail under ``childDetails`` — the
    parent hop is the lookup field, the child is the terminal field on the
    traversed object, e.g. ``ProductCode`` is ``QuoteLineItem.Product2`` ->
    ``Product2.ProductCode``. Both hops are returned in order so the caller can
    render the whole path and index the terminal field (the real source), not
    just the intermediate lookup.
    """
    hops: List[str] = []
    obj = detail.get("sObjectDomain") or detail.get("objectName") or node_sobject or "?"
    field = detail.get("queryAttribute")
    if field:
        hops.append(f"{obj}.{field}")
    for child in detail.get("childDetails") or []:
        if isinstance(child, dict):
            hops.extend(_walk_hydration(child, obj))
    return hops


def _hydration_fields(attr_map: Dict[str, Any], node_sobject: Optional[str]) -> Dict[str, Any]:
    """Resolve an attribute mapping's source binding(s).

    Returns ``{"fields": [Object.field, ...], "kind": "sobject"|"context"|"none",
    "terminal": Object.field|None}``:

    * **sobject** — from ``contextAttrHydrationDetailList``; ``fields`` is the
      full hop chain (simple = 1 hop; traversal = lookup hop(s) then terminal).
      ``terminal`` is the last hop — the actual source field.
    * **context** — from ``contextAttrContextHydrationDetailList`` (attribute
      sourced from *another context*, not an SObject field); ``fields`` names the
      referenced context attribute so the trace doesn't mislabel it "unbound".
    * **none** — no hydration detail of either kind.
    """
    fields: List[str] = []
    for detail in attr_map.get("contextAttrHydrationDetailList") or []:
        if isinstance(detail, dict):
            fields.extend(_walk_hydration(detail, node_sobject))
    if fields:
        return {"fields": fields, "kind": "sobject", "terminal": fields[-1]}

    ctx = attr_map.get("contextAttrContextHydrationDetailList") or []
    ctx_fields = []
    for detail in ctx:
        if not isinstance(detail, dict):
            continue
        qa = detail.get("queryAttribute")
        if qa:
            ctx_fields.append(f"context:{qa}")
    if ctx_fields:
        return {"fields": ctx_fields, "kind": "context", "terminal": None}

    return {"fields": [], "kind": "none", "terminal": None}


def _direction(intents: Set[str], field_type: Optional[str], is_transient: bool) -> Dict[str, Any]:
    """Classify a binding's data-flow direction from mapping intents + fieldType.

    Returns ``{"hydrate": bool, "persist": bool, "aggregate": bool, "label": str,
    "symbol": str}``. ``symbol`` reads field-relative: ``->`` field feeds the
    context (hydrate), ``<-`` context writes the field (persist), ``<->`` both.
    """
    ft = (field_type or "").upper()
    hydrate = "HYDRATION" in intents and ft in _READ_TYPES
    persist = "PERSISTENCE" in intents and ft in _WRITE_TYPES and not is_transient
    aggregate = ft == "AGGREGATE"

    if hydrate and persist:
        label, symbol = "hydrate+persist", "<->"
    elif hydrate:
        label, symbol = "hydrate", "->"
    elif persist:
        label, symbol = "persist", "<-"
    elif aggregate:
        label, symbol = "aggregate (computed)", "(agg)"
    elif ft == "OUTPUT" and "PERSISTENCE" not in intents:
        label, symbol = "output, no persist intent", "(x)"
    elif ft in _WRITE_TYPES and is_transient:
        label, symbol = "transient (skipped on persist)", "(x)"
    else:
        label, symbol = "no active direction", "(x)"
    return {
        "hydrate": hydrate,
        "persist": persist,
        "aggregate": aggregate,
        "label": label,
        "symbol": symbol,
    }


def build_index(defn: Dict[str, Any]) -> Dict[str, Any]:
    """Join a context-definition GET into a queryable field<->tag<->attribute index.

    Returns:
        {
          "developerName": str,
          "isActive": bool,
          "attributes": { attrId: {node, name, dataType, fieldType, isTransient,
                                   tags: [tagName, ...]} },
          "tagIndex":   { tagName(lower): [attrId, ...] },   # attribute-tags only
          "bindings":   [ {mapping, intents:[...], node, sObject, attrId,
                           attribute, dataType, fieldType, isTransient,
                           tags:[...], fields:[Object.field, ...],
                           direction:{...}} ],
          "mappings":   [ {name, isDefault, intents:[...], nodeMappings:int,
                           fieldBindings:int} ],
        }

    ``bindings`` is the grain everything queries: one row per (mapping, node,
    attribute). A row with an empty ``fields`` list is an attribute mapped into
    the lens but bound to no concrete field.
    """
    version = active_version(defn)
    is_active = defn.get("isActive")
    if is_active is None:
        is_active = version.get("isActive")

    # --- Layer 1: attribute id -> descriptor, plus tag -> attribute id(s) ---
    attributes: Dict[str, Dict[str, Any]] = {}
    tag_index: Dict[str, List[str]] = {}
    for node, _depth in iter_nodes(version.get("contextNodes") or []):
        node_name = node.get("name")
        for attr in node_attributes(node):
            if not isinstance(attr, dict):
                continue
            attr_id = attr.get("contextAttributeId")
            if not attr_id:
                continue
            tags: List[str] = []
            attr_tags = attr.get("attributeTags")
            if isinstance(attr_tags, dict):
                attr_tags = attr_tags.get("attributeTags")
            for tag in attr_tags or []:
                if isinstance(tag, dict) and tag.get("name"):
                    tags.append(tag["name"])
                    tag_index.setdefault(tag["name"].lower(), []).append(attr_id)
            attributes[attr_id] = {
                "node": node_name,
                "name": attr.get("name"),
                "dataType": attr.get("dataType"),
                "fieldType": attr.get("fieldType"),
                "isTransient": _as_bool(attr.get("isTransient")),
                "tags": tags,
            }

    # --- Layer 2: bindings (mapping -> node-mapping -> attribute-mapping) ---
    bindings: List[Dict[str, Any]] = []
    mapping_summ: List[Dict[str, Any]] = []
    for mapping in version.get("contextMappings") or []:
        if not isinstance(mapping, dict):
            continue
        mname = mapping.get("name")
        intents = [str(i).upper() for i in (mapping.get("intents") or [])]
        intent_set = set(intents)
        node_maps = mapping.get("contextNodeMappings") or []
        field_bindings = 0
        for node_map in node_maps:
            if not isinstance(node_map, dict):
                continue
            sobj = node_map.get("sObjectName")
            node_name = node_map.get("contextNodeName")
            attr_maps = (
                node_map.get("attributeMappings")
                or node_map.get("contextAttributeMappings")
                or []
            )
            for attr_map in attr_maps:
                if not isinstance(attr_map, dict):
                    continue
                attr_id = attr_map.get("contextAttributeId")
                a = attributes.get(attr_id, {})
                src = _hydration_fields(attr_map, sobj)
                fields = src["fields"]
                if fields:
                    field_bindings += 1
                bindings.append({
                    "mapping": mname,
                    "intents": intents,
                    "node": node_name or a.get("node"),
                    "sObject": sobj,
                    "attrId": attr_id,
                    "attribute": a.get("name") or attr_map.get("contextAttributeName"),
                    "dataType": a.get("dataType"),
                    "fieldType": a.get("fieldType"),
                    "isTransient": a.get("isTransient", False),
                    "tags": a.get("tags", []),
                    "fields": fields,
                    "bindingKind": src["kind"],   # sobject | context | none
                    "terminal": src["terminal"],  # final source field for a traversal
                    "direction": _direction(
                        intent_set, a.get("fieldType"), a.get("isTransient", False)
                    ),
                })
        mapping_summ.append({
            "name": mname,
            "isDefault": _as_bool(mapping.get("isDefault")),
            "intents": intents,
            "nodeMappings": len(node_maps),
            "fieldBindings": field_bindings,
        })

    return {
        "developerName": definition_developer_name(defn) or defn.get("name"),
        "isActive": _as_bool(is_active),
        "attributes": attributes,
        "tagIndex": tag_index,
        "bindings": bindings,
        "mappings": mapping_summ,
    }


# --------------------------------------------------------------------------- #
# Query modes
# --------------------------------------------------------------------------- #

def _mapping_filter(bindings: List[Dict[str, Any]], mapping: Optional[str]):
    if not mapping:
        return bindings
    m = mapping.lower()
    return [b for b in bindings if (b.get("mapping") or "").lower() == m]


def query_field(index: Dict[str, Any], query: str, mapping: Optional[str]) -> List[Dict[str, Any]]:
    """Bindings whose Object.field matches ``query`` (case-insensitive substring).

    Matches on the full ``Object.field``, so ``RLM_RampMode__c`` finds the field
    on any object and ``QuoteLineItem`` finds every field on that object.
    """
    q = query.lower()
    out = []
    for b in _mapping_filter(index["bindings"], mapping):
        if any(q in f.lower() for f in b["fields"]):
            out.append(b)
    return out


def query_tag(index: Dict[str, Any], query: str, mapping: Optional[str]) -> List[Dict[str, Any]]:
    """Bindings for the attribute(s) a tag names (tag match is substring, ci)."""
    q = query.lower()
    attr_ids: Set[str] = set()
    for tag_lower, ids in index["tagIndex"].items():
        if q in tag_lower:
            attr_ids.update(ids)
    return [
        b for b in _mapping_filter(index["bindings"], mapping)
        if b["attrId"] in attr_ids
    ]


def query_attribute(index: Dict[str, Any], query: str, mapping: Optional[str]) -> List[Dict[str, Any]]:
    """Bindings for an attribute named ``node.attr`` or a bare ``attr`` (ci)."""
    q = query.lower()
    node_q = attr_q = None
    if "." in query:
        node_q, _, attr_q = (p.lower() for p in query.partition("."))
    out = []
    for b in _mapping_filter(index["bindings"], mapping):
        name = (b.get("attribute") or "").lower()
        node = (b.get("node") or "").lower()
        if attr_q is not None:
            if name == attr_q and node == node_q:
                out.append(b)
        elif name == q:
            out.append(b)
    return out


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def _render_fields(b: Dict[str, Any]) -> str:
    """Render a binding's source as a single string.

    A relationship traversal (>1 hop) is joined with ` -> ` so the lookup hop and
    the terminal source field read as one path (``QuoteLineItem.Product2 ->
    Product2.ProductCode``); a simple binding is the one hop; a context-sourced
    attribute shows its ``context:`` entries; an empty binding says so.
    """
    if not b["fields"]:
        return "(no field bound)"
    if len(b["fields"]) > 1:
        return " -> ".join(b["fields"])
    return b["fields"][0]


def _binding_line(b: Dict[str, Any]) -> str:
    fields = _render_fields(b)
    tags = ",".join(b["tags"]) if b["tags"] else "(untagged)"
    return (
        f"    {b['mapping']}: {fields}  "
        f"[{b['direction']['symbol']} {b['direction']['label']}]  tags:{tags}"
    )


def _print_matches(index: Dict[str, Any], matches: List[Dict[str, Any]], header: str):
    print(f"{header} in {index['developerName']} "
          f"({'active' if index['isActive'] else 'inactive'}) — {len(matches)} binding(s):\n")
    if not matches:
        print("  (no matching binding)")
        return
    # Group by attribute so each attribute shows all its lenses together.
    by_attr: Dict[str, List[Dict[str, Any]]] = {}
    for b in matches:
        key = f"{b.get('node')}.{b.get('attribute')}"
        by_attr.setdefault(key, []).append(b)
    unexpected_unbound = False
    for attr_key in sorted(by_attr):
        rows = by_attr[attr_key]
        r0 = rows[0]
        print(f"  {attr_key}  [{r0.get('dataType')}/{r0.get('fieldType')}"
              + (" transient" if r0.get("isTransient") else "") + "]")
        for b in sorted(rows, key=lambda x: x.get("mapping") or ""):
            print(_binding_line(b))
            # A non-transient attribute that binds no field in a lens is a
            # candidate FLS-hidden binding: the Connect GET this tool reads
            # honors FLS, so a physically-bound field the running user cannot
            # read is filtered out and shows as "(no field bound)". (Transient
            # / computed attributes bind nothing by design — not flagged.)
            if not b["fields"] and not b.get("isTransient"):
                unexpected_unbound = True
        print()
    if unexpected_unbound:
        print("  Note: a non-transient attribute shown as \"(no field bound)\" may be "
              "FLS-hidden, not\n  truly unmapped — this tool reads the Connect GET, "
              "which honors the running user's\n  field-level security. Verify the "
              "mapped field's FLS (and its existence) before concluding\n  it is "
              "unmapped; grant read on the field to surface a hidden binding.\n")


def _print_summary(index: Dict[str, Any], mapping: Optional[str]):
    attrs = index["attributes"]
    tagged = sum(1 for a in attrs.values() if a["tags"])
    print(f"{index['developerName']}  ({'active' if index['isActive'] else 'inactive'})")
    print(f"  attributes: {len(attrs)}   tagged: {tagged}   "
          f"distinct attr-tags: {len(index['tagIndex'])}   "
          f"mappings: {len(index['mappings'])}")
    bound = sum(1 for b in index["bindings"] if b["fields"])
    print(f"  attribute-mappings: {len(index['bindings'])}   with a field binding: {bound}")
    print("\n  mappings (lenses):")
    for m in index["mappings"]:
        if mapping and (m["name"] or "").lower() != mapping.lower():
            continue
        default = " [default]" if m["isDefault"] else ""
        assoc = "  (association-only)" if m["intents"] == ["ASSOCIATION"] else ""
        print(f"    {m['name']}{default}  intents={','.join(m['intents']) or '-'}  "
              f"nodeMappings={m['nodeMappings']}  fieldBindings={m['fieldBindings']}{assoc}")


def _print_unmapped(index: Dict[str, Any], mapping: Optional[str], verbose: bool):
    """Surface the partial-combo gaps from the authoring decision table.

    * tagged but never bound to a field -> referenceable but never populated
    * bound to a field but untagged     -> populated but unreachable by an ES
    * neither tag nor binding            -> inert

    **Scope matters.** Without ``--mapping`` the analysis is across *all* lenses:
    an attribute counts as "bound" if any mapping binds it, so "never bound" =
    truly never populated (the real inert/gap signal). With ``--mapping`` it is
    *per that lens*: an attribute bound in another lens (e.g. an ``Asset.*`` attr
    bound only in ``AssetEntitiesMapping``) shows as "not populated by this lens"
    — expected for cross-lens attributes, not necessarily a defect. The labels
    below reflect which scope is active.
    """
    bindings = _mapping_filter(index["bindings"], mapping)
    bound_attr_ids = {b["attrId"] for b in bindings if b["fields"]}
    scoped = bool(mapping)
    scope = f" (mapping {mapping})" if scoped else " (all lenses)"
    where = f"by {mapping}" if scoped else "by any lens"

    tagged_unbound = [
        (aid, a) for aid, a in index["attributes"].items()
        if a["tags"] and aid not in bound_attr_ids
    ]
    # untagged-but-bound and inert are computed from the attribute descriptor.
    untagged_bound = [
        (aid, a) for aid, a in index["attributes"].items()
        if not a["tags"] and aid in bound_attr_ids
    ]
    inert = [
        (aid, a) for aid, a in index["attributes"].items()
        if not a["tags"] and aid not in bound_attr_ids
    ]

    print(f"Unmapped analysis for {index['developerName']}{scope}:\n")
    if scoped:
        print("  Note: scoped to one lens — an attribute bound in another mapping "
              "still\n  shows here as 'not populated by this lens'. Drop --mapping "
              "for the\n  never-populated-anywhere signal.\n")

    print(f"  Tagged attributes never bound to a field "
          f"(referenceable but never populated {where}): {len(tagged_unbound)}")
    if verbose or not scoped:
        for _aid, a in sorted(tagged_unbound, key=lambda x: (x[1]['node'] or '', x[1]['name'] or '')):
            print(f"    - {a['node']}.{a['name']} [{a['fieldType']}] tags:{','.join(a['tags'])}")
    elif tagged_unbound:
        print("    (use --verbose to list)")

    print(f"\n  Bound attributes with no tag "
          f"(populated but unreachable by expression sets): {len(untagged_bound)}")
    if verbose:
        for _aid, a in sorted(untagged_bound, key=lambda x: (x[1]['node'] or '', x[1]['name'] or '')):
            print(f"    - {a['node']}.{a['name']} [{a['fieldType']}]")
    elif untagged_bound:
        print("    (use --verbose to list)")

    print(f"\n  Inert attributes (no tag, no field binding {where}): {len(inert)}")
    if verbose:
        for _aid, a in sorted(inert, key=lambda x: (x[1]['node'] or '', x[1]['name'] or '')):
            print(f"    - {a['node']}.{a['name']} [{a['fieldType']}]")
    elif inert:
        print("    (use --verbose to list)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Trace how SObject fields link to Context tags/attributes "
                    "(hydration) and back (persistence). Read-only."
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--developer-name", help="DeveloperName of the definition.")
    group.add_argument("--id", dest="context_id", help="ContextDefinitionId.")

    selector = parser.add_mutually_exclusive_group()
    selector.add_argument(
        "--field",
        help="Reverse trace by SObject FIELD name, any traversal hop (ci substring "
             "of Object.field, e.g. RLM_RampMode__c, Quote.AccountId, ProductCode).",
    )
    selector.add_argument(
        "--tag",
        help="Forward trace by TAG name (ci SUBSTRING — 'Account' matches every "
             "account tag). Not the same axis as --field; see the module docstring.",
    )
    selector.add_argument(
        "--attribute",
        help="Forward trace by ATTRIBUTE name, EXACT match (node.attr or bare). "
             "Use this for the exact forward mirror of a --field result.",
    )
    selector.add_argument("--unmapped", action="store_true",
                          help="Report tagged-but-unbound / bound-but-untagged / inert attributes.")

    parser.add_argument("--mapping", help="Scope the trace to one mapping (lens) by name.")
    parser.add_argument("--api-version", default="67.0", help="Salesforce API version (default 67.0).")
    parser.add_argument("--verbose", action="store_true", help="List every attribute in --unmapped.")
    parser.add_argument("--json", action="store_true", help="Emit the query result as JSON.")
    args = parser.parse_args(argv)

    try:
        context_id = args.context_id
        if not context_id:
            context_id = _resolve_id(args.developer_name, args.target_org, args.api_version)
            if not context_id:
                eprint(f"Error: no context definition found with developerName "
                       f"'{args.developer_name}' in org '{args.target_org}'.")
                return 1
        defn = connect_get(
            f"connect/context-definitions/{context_id}", args.target_org, args.api_version
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if isinstance(defn, list):
        defn = defn[0] if defn and isinstance(defn[0], dict) else {}
    if not isinstance(defn, dict) or not defn:
        eprint("Error: empty or unexpected response for the context definition.")
        return 1

    index = build_index(defn)

    # Selector dispatch.
    if args.field is not None:
        matches = query_field(index, args.field, args.mapping)
        result_kind, header = "field", f"Field trace for '{args.field}'"
    elif args.tag is not None:
        matches = query_tag(index, args.tag, args.mapping)
        result_kind, header = "tag", f"Tag trace for '{args.tag}'"
    elif args.attribute is not None:
        matches = query_attribute(index, args.attribute, args.mapping)
        result_kind, header = "attribute", f"Attribute trace for '{args.attribute}'"
    elif args.unmapped:
        result_kind = "unmapped"
    else:
        result_kind = "summary"

    if args.json:
        if result_kind in ("field", "tag", "attribute"):
            print(json.dumps({"query": result_kind, "matches": matches}, indent=2))
        else:
            # summary / unmapped: emit the whole index (attributes keyed by id).
            print(json.dumps(index, indent=2))
        return 0

    if result_kind in ("field", "tag", "attribute"):
        _print_matches(index, matches, header)
    elif result_kind == "unmapped":
        _print_unmapped(index, args.mapping, args.verbose)
    else:
        _print_summary(index, args.mapping)
    return 0


if __name__ == "__main__":
    sys.exit(main())
