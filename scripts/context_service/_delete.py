#!/usr/bin/env python3
"""Reverse-order deletion sequencer for the Context Service mutation scripts.

The inverse of ``_apply.ContextApplier``: where the applier *adds* artifacts in
dependency order (parent → child), this *removes* them in reverse (child →
parent) using the granular **GET+DELETE-by-id** resources documented in
``_endpoints`` (all since API 59.0). Built on the same standalone ``sf``-CLI
transport (``_client`` via the injected :class:`_apply.Transport`) — no
``cumulusci`` import, no ``access_token`` ever handled.

Two safety properties make this module distinct from a naive "DELETE the id":

1. **Reverse-order teardown.** Layer-2 (mappings) reference Layer-1 (nodes /
   attributes) by id, and within each layer children reference parents, so a
   safe delete order is::

       attribute-mappings -> node-mappings -> mappings   (Layer-2, child→parent)
       tags -> attributes -> nodes                        (Layer-1, child→parent)

   (matching the ``_endpoints`` module header). Nodes within a tree are deleted
   deepest-first. The *whole definition* is a single DELETE on
   ``DEFINITION_ITEM`` — the platform cascades all children, so the sequencer is
   only needed for **granular / subtree** deletes.

2. **``baseReference`` pre-flight guard.** On an *extended* definition every
   inherited node / attribute / tag / mapping carries a ``baseReference`` path
   into its standard base (e.g. ``SalesTransactionContext__stdctx/version/…``);
   custom-added artifacts have ``baseReference: None``. Inherited artifacts
   **cannot be deleted** — the platform blocks it (you extend / deactivate the
   whole definition instead of editing the base's contribution in place). This
   module refuses to target an inherited artifact up front, with an actionable
   message, rather than letting the opaque platform error surface. Inherited vs
   custom is read from ``baseReference`` (a path into the standard base = inherited;
   ``None`` = custom-added).

3. **Active-state pre-flight.** The platform blocks *every* structural delete —
   whole-definition and granular, down to a single custom ``__c`` tag — while the
   version is active (``RECORD_UPDATE_FAILED``: "Cannot modify/delete an active
   context definition"): a custom leaf-tag DELETE on an active version is blocked
   and the same DELETE succeeds once the version is deactivated (adds, by
   contrast, apply in-place on an active version — an add/delete asymmetry).
   :meth:`ContextDeleter.guard_active_state` refuses up front (or deactivates
   first, if opted in).

The flagship granular mode is :meth:`ContextDeleter.plan_custom_teardown` — strip
**every** custom (``baseReference: None``) artifact from an extended base while
leaving the inherited base intact. It is the exact inverse of
``export_context.py --custom-only`` / an additive apply.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import _client
import _endpoints as ep
from _apply import ContextApplier, Transport  # reuse verified resolve/fetch/_set_active


# --------------------------------------------------------------------------- #
# Delete ordering
# --------------------------------------------------------------------------- #

# Child → parent. A delete set is sorted by this order (nodes additionally
# deepest-first) so every dependent is gone before the thing it depends on.
DELETE_ORDER = [
    "attr-mapping",   # Layer-2 leaf
    "node-mapping",
    "mapping",
    "tag",            # Layer-1: references an attribute by contextAttributeId
    "attribute",
    "node",           # Layer-1 root (below the definition)
]
_ORDER_INDEX = {kind: i for i, kind in enumerate(DELETE_ORDER)}


# --------------------------------------------------------------------------- #
# Artifact catalog (a flat, delete-ready view of one definition version)
# --------------------------------------------------------------------------- #

def build_artifact_catalog(detail: Dict[str, Any], context_id: str) -> List[Dict[str, Any]]:
    """Flatten a ``connect/context-definitions/<id>`` GET into deletable artifacts.

    Returns a list of dicts, one per artifact::

        {
          "kind":  "node" | "attribute" | "tag" | "mapping"
                   | "node-mapping" | "attr-mapping",
          "name":  <human label, e.g. "SalesTransaction.RampMode__c">,
          "id":    <the record id used in the by-id DELETE path>,
          "baseReference": <str | None>,     # truthy => inherited => undeletable
          "path":  <ready-to-DELETE by-id endpoint path>,
          "depth": <int, node tree depth (0 for non-nodes / top nodes)>,
          # linkage keys for cascade grouping:
          "context_attribute_id":    <attr id, on attribute/tag/attr-mapping>,
          "context_node_id":         <node id, on node/attribute/node-mapping>,
          "context_mapping_id":      <mapping id, on mapping/node-mapping>,
          "context_node_mapping_id": <node-mapping id, on node-mapping/attr-mapping>,
        }

    Operates on the **active** version (``_client.active_version``); on a
    single-version definition that is the only version. Layer-1 (nodes/attrs/
    tags) comes from ``contextNodes``; Layer-2 (mappings/node-mappings/attr-
    mappings) from ``contextMappings``.
    """
    artifacts: List[Dict[str, Any]] = []
    version = _client.active_version(detail)
    if not version:
        return artifacts

    # ---- Layer 1: nodes -> attributes -> tags ---------------------------- #
    def walk_nodes(node_list, depth):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            node_id = node.get("contextNodeId")
            node_name = node.get("name")
            if node_id:
                artifacts.append({
                    "kind": "node",
                    "name": node_name or node_id,
                    "id": node_id,
                    "baseReference": node.get("baseReference"),
                    "path": ep.NODE_ITEM.format(
                        context_definition_id=context_id, context_node_id=node_id),
                    "depth": depth,
                    "context_node_id": node_id,
                })
            # node-level tags (rare; most tags live on attributes)
            for tag in node.get("tags") or []:
                _append_tag(artifacts, tag, context_id, node_id=node_id,
                            owner_label=node_name)
            # attributes on this node
            for attr in _node_attrs(node):
                if not isinstance(attr, dict):
                    continue
                attr_id = attr.get("contextAttributeId")
                attr_name = attr.get("name")
                label = f"{node_name}.{attr_name}" if node_name else attr_name
                if attr_id and node_id:
                    artifacts.append({
                        "kind": "attribute",
                        "name": label or attr_id,
                        "id": attr_id,
                        "baseReference": attr.get("baseReference"),
                        "path": ep.ATTRIBUTE_ITEM.format(
                            context_node_id=node_id, context_attribute_id=attr_id),
                        "depth": 0,
                        "context_attribute_id": attr_id,
                        "context_node_id": node_id,
                    })
                for tag in attr.get("attributeTags") or attr.get("tags") or []:
                    _append_tag(artifacts, tag, context_id,
                                attr_id=attr_id, owner_label=label)
            walk_nodes(_child_nodes(node), depth + 1)

    walk_nodes(version.get("contextNodes", []), 0)

    # ---- Layer 2: mappings -> node-mappings -> attr-mappings ------------- #
    for mapping in version.get("contextMappings", []) or []:
        if not isinstance(mapping, dict):
            continue
        mapping_id = mapping.get("contextMappingId")
        mapping_name = mapping.get("name")
        if mapping_id:
            artifacts.append({
                "kind": "mapping",
                "name": mapping_name or mapping_id,
                "id": mapping_id,
                "baseReference": mapping.get("baseReference"),
                "path": ep.MAPPING_ITEM.format(
                    context_definition_id=context_id, context_mapping_id=mapping_id),
                "depth": 0,
                "context_mapping_id": mapping_id,
            })
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if not isinstance(node_map, dict):
                continue
            nm_id = node_map.get("contextNodeMappingId")
            nm_node = node_map.get("contextNodeName")
            nm_label = f"{mapping_name}/{nm_node}" if mapping_name else nm_node
            if nm_id and mapping_id:
                artifacts.append({
                    "kind": "node-mapping",
                    "name": nm_label or nm_id,
                    "id": nm_id,
                    "baseReference": node_map.get("baseReference"),
                    "path": ep.NODE_MAPPING_ITEM.format(
                        context_mapping_id=mapping_id, context_node_mapping_id=nm_id),
                    "depth": 0,
                    "context_mapping_id": mapping_id,
                    "context_node_mapping_id": nm_id,
                    "context_node_id": node_map.get("contextNodeId"),
                })
            for attr_map in node_map.get("attributeMappings", []) or []:
                if not isinstance(attr_map, dict):
                    continue
                am_id = attr_map.get("contextAttributeMappingId")
                am_attr = attr_map.get("contextAttributeName")
                am_label = f"{nm_label}.{am_attr}" if nm_label else am_attr
                if am_id and nm_id:
                    artifacts.append({
                        "kind": "attr-mapping",
                        "name": am_label or am_id,
                        "id": am_id,
                        "baseReference": attr_map.get("baseReference"),
                        "path": ep.ATTR_MAPPING_ITEM.format(
                            context_node_mapping_id=nm_id,
                            context_attribute_mapping_id=am_id),
                        "depth": 0,
                        "context_attribute_id": attr_map.get("contextAttributeId"),
                        "context_node_mapping_id": nm_id,
                    })
    return artifacts


def _append_tag(artifacts, tag, context_id, *, attr_id=None, node_id=None,
                owner_label=None):
    if not isinstance(tag, dict):
        return
    tag_id = tag.get("contextTagId")
    tag_name = tag.get("name")
    if not tag_id:
        return
    artifacts.append({
        "kind": "tag",
        "name": (f"{owner_label}:{tag_name}" if owner_label else tag_name) or tag_id,
        "id": tag_id,
        "baseReference": tag.get("baseReference"),
        "path": ep.TAG_ITEM.format(
            context_definition_id=context_id, context_tag_id=tag_id),
        "depth": 0,
        "context_attribute_id": tag.get("contextAttributeId") or attr_id,
        "context_node_id": node_id,
        "tag_name": tag_name,
    })


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


# --------------------------------------------------------------------------- #
# Ordering / partitioning helpers (pure)
# --------------------------------------------------------------------------- #

def order_for_deletion(artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort a delete set child→parent (DELETE_ORDER; nodes deepest-first)."""
    return sorted(
        artifacts,
        key=lambda a: (_ORDER_INDEX.get(a["kind"], 99), -a.get("depth", 0)),
    )


def partition_by_inheritance(
    artifacts: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split into (custom, inherited). Inherited = truthy ``baseReference``."""
    custom, inherited = [], []
    for a in artifacts:
        (inherited if a.get("baseReference") else custom).append(a)
    return custom, inherited


# --------------------------------------------------------------------------- #
# Deleter
# --------------------------------------------------------------------------- #

class DeletePreflightError(RuntimeError):
    """Raised when a requested delete targets an inherited (undeletable) artifact
    or would need a cascade that was not opted into."""


class ContextDeleter:
    """Delete Context Definition artifacts in safe reverse order.

    Reuses ``_apply.ContextApplier`` for definition resolution, detail fetch, and
    (soft) deactivation so those verified paths are not duplicated.
    """

    def __init__(self, transport: Transport, logger: Callable[..., None] = None):
        self.t = transport
        self.log = logger or transport.logger
        self.dry_run = transport.dry_run
        self._applier = ContextApplier(transport, logger=self.log)

    # ---- delegated reads / deactivation ---------------------------------- #

    def resolve_definition_id(self, developer_name: str) -> Optional[str]:
        return self._applier.resolve_definition_id(developer_name)

    def fetch_detail(self, context_id: str) -> Dict[str, Any]:
        return self._applier.fetch_detail(context_id)

    def deactivate(self, context_id: str) -> None:
        """Soft-disable a definition (preferred over hard delete). Port of
        ``ContextApplier._set_active(False)`` with its ES-reference guidance."""
        self._applier._set_active(context_id, False)

    def is_active(self, detail: Dict[str, Any]) -> bool:
        """Whether the definition (its active version) is currently active.

        A live read, so it is accurate even under dry-run. Deletes — both the
        whole-definition DELETE and structural granular deletes — are blocked by
        the platform while the version is active, so callers pre-flight this.
        """
        return self._applier._is_active(detail)

    # ---- active-state pre-flight ----------------------------------------- #

    def guard_active_state(self, detail: Dict[str, Any], *, context_id: str,
                           auto_deactivate: bool = False) -> Dict[str, Any]:
        """Refuse (or, if opted in, resolve) a delete against an *active* version.

        The platform blocks **every** structural delete — whole-definition and
        granular alike, down to a single custom ``__c`` tag — while the version
        is active, returning ``RECORD_UPDATE_FAILED`` "Cannot modify/delete an
        active context definition": deleting a custom leaf tag on an active
        version is blocked, and the identical DELETE succeeds once the version is
        deactivated. (Note the asymmetry with *adds*, which DO apply in-place on
        an active version.) Rather than let that surface mid-teardown, this
        checks up front. Default:
        raise :class:`DeletePreflightError` telling the caller to deactivate
        first. With ``auto_deactivate=True`` it deactivates in place (subject to
        the ES-reference guard in :meth:`deactivate`) and returns the refreshed
        detail. No-op when already inactive.
        """
        if not self.is_active(detail):
            return detail
        if not auto_deactivate:
            raise DeletePreflightError(
                f"Context definition {context_id} is ACTIVE; the platform blocks "
                f"deleting an active definition or its structural artifacts. "
                f"Deactivate it first (soft-disable is the preferred teardown), "
                f"then delete — or re-run with --deactivate-first to do both. "
                f"Note: deactivation itself is blocked while an Expression Set "
                f"(pricing procedure / DocGen template) still references the "
                f"definition; detach that first."
            )
        self.log(f"Definition {context_id} is active; deactivating before delete "
                 f"(--deactivate-first).")
        self.deactivate(context_id)
        # Under dry-run the PATCH was logged, not executed, so the live detail is
        # still 'active' — re-fetching would loop the guard. Trust the intent.
        if self.dry_run:
            return detail
        return self.fetch_detail(context_id)

    # ---- whole-definition hard delete ------------------------------------ #

    def delete_definition(self, context_id: str) -> Dict[str, Any]:
        """DELETE the whole definition (platform cascades all children).

        A single by-id DELETE on ``DEFINITION_ITEM``. This is the only path that
        does not need the reverse-order sequencer — the platform removes the
        version, nodes, attributes, tags, and mappings atomically. Fails (error
        surfaced) if the definition is still active / referenced by an Expression
        Set; deactivate or detach first (see :meth:`guard_active_state`).
        """
        self.log(f"Deleting whole context definition {context_id} "
                 f"(platform cascade).")
        try:
            self.t.request(
                "DELETE", ep.DEFINITION_ITEM.format(context_definition_id=context_id)
            )
        except _client.ContextClientError as exc:
            raise self._annotate_delete_error(exc, context_id, "definition") from exc
        return {"context_id": context_id, "deleted": "definition"}

    # ---- granular delete planning ---------------------------------------- #

    def plan_custom_teardown(self, catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Every custom (``baseReference: None``) artifact, in delete order.

        The inverse of an additive apply: leaves the inherited base intact and
        removes only what was added on top of it. No inherited artifact can enter
        this set by construction, so the pre-flight guard is satisfied trivially.
        """
        custom, _inherited = partition_by_inheritance(catalog)
        return order_for_deletion(custom)

    def plan_target_deletion(
        self, catalog: List[Dict[str, Any]], *, kind: str, name: str,
        cascade: bool = False,
    ) -> List[Dict[str, Any]]:
        """Resolve one named target (+ its custom dependents if ``cascade``) into
        an ordered delete set. Raises :class:`DeletePreflightError` when the
        target is inherited, unresolved, ambiguous, or has custom children while
        ``cascade`` is off.
        """
        targets = _match_targets(catalog, kind, name)
        if not targets:
            raise DeletePreflightError(
                f"No {kind} named '{name}' found on this definition. "
                f"(Names are case-sensitive; for attributes use 'Node.Attr'.)"
            )
        if len(targets) > 1:
            labels = ", ".join(sorted(t["name"] for t in targets))
            raise DeletePreflightError(
                f"'{name}' matches {len(targets)} {kind}s ({labels}). "
                f"Qualify it (e.g. 'Node.Attr' for an attribute)."
            )
        target = targets[0]
        if target.get("baseReference"):
            raise DeletePreflightError(_inherited_message(target))

        dependents = _dependents_of(catalog, target)
        # An inherited dependent must never be deleted (it belongs to the base).
        inherited_deps = [d for d in dependents if d.get("baseReference")]
        if inherited_deps:
            names = ", ".join(sorted(d["name"] for d in inherited_deps))
            raise DeletePreflightError(
                f"Cannot delete '{target['name']}': it has inherited dependent(s) "
                f"({names}) that the platform will not remove. Target a custom "
                f"artifact instead."
            )
        custom_deps = [d for d in dependents if not d.get("baseReference")]
        if custom_deps and not cascade:
            names = ", ".join(sorted(d["name"] for d in custom_deps))
            raise DeletePreflightError(
                f"'{target['name']}' still has {len(custom_deps)} custom "
                f"dependent(s) ({names}). Re-run with --cascade to delete them "
                f"first, or delete them individually."
            )
        return order_for_deletion([target] + (custom_deps if cascade else []))

    # ---- execution -------------------------------------------------------- #

    def execute(self, ordered: List[Dict[str, Any]]) -> Dict[str, Any]:
        """DELETE each artifact in the given (already-ordered) list.

        Under dry-run the transport logs each ``[dry-run] DELETE <path>`` without
        mutating. Returns a summary of what was (or would be) deleted.
        """
        deleted: List[Dict[str, str]] = []
        for art in ordered:
            self.log(f"Deleting {art['kind']}: {art['name']} (id={art['id']})")
            try:
                self.t.request("DELETE", art["path"])
            except _client.ContextClientError as exc:
                raise self._annotate_delete_error(
                    exc, art["id"], art["kind"], label=art["name"]) from exc
            deleted.append({"kind": art["kind"], "name": art["name"], "id": art["id"]})
        return {"deleted": deleted, "count": len(deleted), "dry_run": self.dry_run}

    def _annotate_delete_error(self, exc: "_client.ContextClientError", record_id: str,
                               kind: str, label: str = None) -> "_client.ContextClientError":
        """Turn an opaque platform DELETE failure into an actionable one.

        The two dominant reasons a Context Service delete fails are (1) the
        definition/version is still **active** (live-verified: ``RECORD_UPDATE_
        FAILED`` "Cannot modify/delete an active context definition"), and (2) it
        is **referenced** by an Expression Set / another definition. The message
        is more telling than the code, so we surface the likely cause and the fix.
        """
        blocked_codes = {
            "RECORD_UPDATE_FAILED", "DELETE_FAILED", "ENTITY_IS_DELETED",
            "INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY", "DEPENDENCY_EXISTS",
            "CANNOT_DELETE_ROOT_ENTITY", "FIELD_INTEGRITY_EXCEPTION",
        }
        target = f"{kind} '{label}'" if label else kind
        if exc.error_codes and not (set(exc.error_codes) & blocked_codes):
            return exc  # a different, already-informative error — pass through
        return _client.ContextClientError(
            f"Failed to delete {target} ({record_id}). The platform commonly "
            f"blocks a Context Service delete when the definition is still ACTIVE "
            f"or is REFERENCED by an Expression Set (pricing procedure / DocGen "
            f"template) or another context definition. Fixes, in order: "
            f"(1) deactivate the definition (or re-run with --deactivate-first); "
            f"(2) detach/deactivate any referencing Expression Set; "
            f"(3) delete child artifacts first (--cascade). Original error:\n{exc}",
            error_codes=exc.error_codes, body=exc.body, returncode=exc.returncode,
        )


# --------------------------------------------------------------------------- #
# Target matching / dependency gathering (pure)
# --------------------------------------------------------------------------- #

def _match_targets(catalog, kind: str, name: str) -> List[Dict[str, Any]]:
    """Find catalog artifacts of ``kind`` matching ``name`` (exact, case-sensitive).

    Attributes accept either the qualified ``Node.Attr`` label or a bare
    ``Attr`` (which may match several nodes → caller treats >1 as ambiguous).
    Tags match on the raw tag name (``tag_name``) or the qualified ``owner:tag``
    label.
    """
    out = []
    for a in catalog:
        if a["kind"] != kind:
            continue
        if a["name"] == name:
            out.append(a)
            continue
        if kind == "attribute" and a["name"].rsplit(".", 1)[-1] == name:
            out.append(a)
        elif kind == "tag" and a.get("tag_name") == name:
            out.append(a)
    return out


def _dependents_of(catalog, target: Dict[str, Any]) -> List[Dict[str, Any]]:
    """All artifacts that reference ``target`` and must be deleted before it."""
    kind = target["kind"]
    deps: List[Dict[str, Any]] = []

    if kind == "node":
        node_id = target["context_node_id"]
        attr_ids = {
            a["context_attribute_id"] for a in catalog
            if a["kind"] == "attribute" and a.get("context_node_id") == node_id
        }
        for a in catalog:
            if a is target:
                continue
            if a["kind"] == "attribute" and a.get("context_node_id") == node_id:
                deps.append(a)
            elif a["kind"] == "tag" and (
                a.get("context_node_id") == node_id
                or a.get("context_attribute_id") in attr_ids):
                deps.append(a)
            elif a["kind"] == "node-mapping" and a.get("context_node_id") == node_id:
                deps.append(a)
            elif a["kind"] == "attr-mapping" and a.get("context_attribute_id") in attr_ids:
                deps.append(a)
            elif a["kind"] == "node" and a.get("depth", 0) > target.get("depth", 0) \
                    and _is_descendant(catalog, a, node_id):
                deps.append(a)

    elif kind == "attribute":
        attr_id = target["context_attribute_id"]
        for a in catalog:
            if a is target:
                continue
            if a["kind"] in ("tag", "attr-mapping") \
                    and a.get("context_attribute_id") == attr_id:
                deps.append(a)

    elif kind == "mapping":
        mapping_id = target["context_mapping_id"]
        nm_ids = {
            a["context_node_mapping_id"] for a in catalog
            if a["kind"] == "node-mapping" and a.get("context_mapping_id") == mapping_id
        }
        for a in catalog:
            if a is target:
                continue
            if a["kind"] == "node-mapping" and a.get("context_mapping_id") == mapping_id:
                deps.append(a)
            elif a["kind"] == "attr-mapping" and a.get("context_node_mapping_id") in nm_ids:
                deps.append(a)

    elif kind == "node-mapping":
        nm_id = target["context_node_mapping_id"]
        for a in catalog:
            if a is target:
                continue
            if a["kind"] == "attr-mapping" and a.get("context_node_mapping_id") == nm_id:
                deps.append(a)

    # tag / attr-mapping: leaves, no dependents.
    return deps


def _is_descendant(catalog, node_artifact, ancestor_node_id) -> bool:
    """Best-effort: the GET does not expose a node's parent id directly here, so
    a deeper node is treated as a descendant only when the caller has already
    scoped by the ancestor subtree. Conservative: return False (child nodes are
    handled by whole-definition delete, not granular node delete) so we never
    silently sweep an unrelated deeper node.
    """
    return False


def _inherited_message(target: Dict[str, Any]) -> str:
    return (
        f"'{target['name']}' is inherited from its standard base "
        f"(baseReference={target['baseReference']!r}); inherited "
        f"{target['kind']}s cannot be deleted — the platform blocks it. Target a "
        f"custom (__c) artifact instead, or deactivate/extend the whole "
        f"definition. Custom artifacts have baseReference: None."
    )
