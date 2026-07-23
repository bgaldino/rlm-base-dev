#!/usr/bin/env python3
"""Granular single-artifact mutation for the Context Service scripts.

Where ``_apply`` applies a *whole plan* and ``_delete`` tears artifacts *down*,
this edits **one existing artifact in place**: flip an attribute's
``IsTransient``, (re)designate the default context mapping, or add / remove a
single tag. Built on the same standalone ``sf``-CLI transport (``_client`` via
the injected :class:`_apply.Transport`), reusing the verified
:class:`_apply.ContextApplier` primitives (``_sync_transient``,
``_set_default_mapping``, ``_post_tags`` / ``resolve_tags_by_name``) and
:class:`_delete.ContextDeleter` (tag removal + the active-state guard). No
``cumulusci`` import, no ``access_token`` ever handled.

Three properties make this distinct from a raw PATCH:

1. **Op-specific ``baseReference`` (inheritance) guard.** Unlike delete — where
   *every* inherited artifact is off-limits — a mutate's inheritance rule
   depends on the op:

   * ``set-transient`` **modifies** an existing attribute → refused on an
     inherited attribute (the platform blocks editing a base attribute in place;
     custom ``__c`` attributes only).
   * ``set-default-mapping`` sets a *property* on a mapping, and the standard
     default mapping is itself inherited (``QuoteEntitiesMapping`` etc.) — so an
     inherited mapping **is** an allowed target (this is exactly what the extend
     flow does). No inheritance refusal.
   * ``add-tag`` attaches a **new** custom tag; the *attribute* it hangs off may
     be inherited (a custom ``__c`` tag attaches fine to an inherited attribute).
     No inheritance refusal on the attribute; the platform enforces the ``__c``
     suffix and per-definition name uniqueness.
   * ``add-mapping`` binds an **existing** attribute to an SObject field by
     creating a **new** ``ContextAttributeMapping`` (+ its
     ``ContextAttrHydrationDetail``) on an existing node mapping. The attribute
     and node it targets may be inherited (this is the additive-binding case
     ``apply_context_plan.py`` reaches through the whole-body PATCH); no
     inheritance refusal. Sibling-loss-safe by construction — a granular POST
     touches only the one new row, never re-emitting siblings.
   * ``remove-tag`` delegates to :class:`_delete.ContextDeleter`, which refuses
     an inherited tag.

2. **Op-specific active-state guard (the ADD-vs-MODIFY/DELETE asymmetry).** The
   platform rule is literal in its own error text — "Cannot **modify/delete** an
   active context definition": **adding a new child is allowed on an active
   version; modifying or deleting an *existing* artifact is blocked.** So by wire
   operation:

   * ``add-tag`` — POSTs a **new** child tag → **allowed on an active version**.
   * ``add-mapping`` — POSTs a **new** ``ContextAttributeMapping`` (+ hydration
     detail) via SObject REST → **allowed on an active version** (a pure insert,
     live-verified 2026-07-08). This is the granular, sibling-safe alternative
     to the whole-body node-mapping PATCH.
   * ``set-transient`` — an ``IsTransient`` SObject **PATCH of an existing
     attribute** → **BLOCKED on an active version** (``RECORD_UPDATE_FAILED``
     "Cannot modify/delete an active context definition"). Needs
     ``--deactivate-first``.
   * ``set-default-mapping`` — a Connect ``context-mappings`` **PATCH of an
     existing mapping** → **BLOCKED on an active version** (same error). Needs
     ``--deactivate-first``.
   * ``remove-tag`` — a delete → **blocked while active** (same error). Needs
     ``--deactivate-first``.

   So the two pure inserts (``add-tag``, ``add-mapping``) run on an active
   version; the rest (two modifies + one delete) all require deactivate-first.

3. **No-op detection.** Setting ``IsTransient`` to its current value, or
   flagging an already-default mapping, is reported as "already <value>" and
   skipped rather than issuing a redundant PATCH.
"""

from typing import Any, Callable, Dict, List, Optional

from . import _client
from . import _endpoints as ep
from . import _payload
from ._apply import (
    ContextApplier,
    _index_node_mapping_ids,
    _iter_context_mappings,
    _record_id,
)
from ._client import Transport
from ._delete import ContextDeleter, DeletePreflightError, build_artifact_catalog


# --------------------------------------------------------------------------- #
# Op metadata — inheritance / active-state rules per operation (live-verified)
# --------------------------------------------------------------------------- #

# refuses_inherited: the op modifies an existing base artifact → block inherited.
# requires_inactive: the op is blocked by the platform while the version active.
#   Live-verified rule (v67.0): the platform allows *adding a new child* on an
#   active version but blocks *modifying or deleting an existing artifact*
#   ("Cannot modify/delete an active context definition"). So every op except
#   the pure insert (add-tag) requires the version to be inactive.
OP_RULES = {
    "set-transient":       {"refuses_inherited": True,  "requires_inactive": True},
    "set-default-mapping": {"refuses_inherited": False, "requires_inactive": True},
    "add-tag":             {"refuses_inherited": False, "requires_inactive": False},
    "add-mapping":         {"refuses_inherited": False, "requires_inactive": False},
    "remove-tag":          {"refuses_inherited": True,  "requires_inactive": True},
}


class MutatePreflightError(RuntimeError):
    """Raised when a requested mutation targets an artifact that cannot be
    mutated (inherited where the op forbids it, unresolved, or ambiguous)."""


# --------------------------------------------------------------------------- #
# Detail walkers (pure) — find the raw artifact dict so we can read its current
# state (isTransient / isDefault / baseReference / ids) for no-op + guard checks.
# --------------------------------------------------------------------------- #

def find_attribute(detail: Dict[str, Any], node_attr: str) -> Optional[Dict[str, Any]]:
    """Locate one attribute by ``Node.Attr`` or bare ``Attr``.

    Returns an enriched dict ``{node_name, name, contextAttributeId,
    contextNodeId, baseReference, isTransient}`` or ``None``. A bare name that
    matches on >1 node raises :class:`MutatePreflightError` (ambiguous).
    """
    node_name, _, attr_name = node_attr.rpartition(".")
    matches: List[Dict[str, Any]] = []
    version = _client.active_version(detail)
    for node, _depth in _client.iter_nodes(version.get("contextNodes", [])):
        nname = node.get("name")
        if node_name and nname != node_name:
            continue
        for attr in _client.node_attributes(node):
            if not isinstance(attr, dict):
                continue
            if attr.get("name") != attr_name:
                continue
            matches.append({
                "node_name": nname,
                "name": attr.get("name"),
                "contextAttributeId": attr.get("contextAttributeId"),
                "contextNodeId": node.get("contextNodeId"),
                "baseReference": attr.get("baseReference"),
                "isTransient": _payload.as_bool(attr.get("isTransient")),
            })
    if len(matches) > 1:
        labels = ", ".join(sorted(f"{m['node_name']}.{m['name']}" for m in matches))
        raise MutatePreflightError(
            f"'{node_attr}' matches {len(matches)} attributes ({labels}). "
            f"Qualify it as Node.Attr."
        )
    return matches[0] if matches else None


def find_mapping(detail: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    """Locate one context mapping by name; return its raw dict or ``None``."""
    for mapping in _iter_context_mappings(detail):
        if mapping.get("name") == name:
            return mapping
    return None


# --------------------------------------------------------------------------- #
# Mutator
# --------------------------------------------------------------------------- #

class ContextMutator:
    """Apply one granular mutation to a Context Definition, in place.

    Reuses :class:`_apply.ContextApplier` for resolution/detail/primitives and
    :class:`_delete.ContextDeleter` for tag removal + the active-state guard, so
    no verified path is duplicated.
    """

    def __init__(self, transport: Transport, logger: Callable[..., None] = None):
        self.t = transport
        self.log = logger or transport.logger
        self.dry_run = transport.dry_run
        self._applier = ContextApplier(transport, logger=self.log)
        self._deleter = ContextDeleter(transport, logger=self.log)

    # ---- delegated reads / lifecycle ------------------------------------- #

    def resolve_definition_id(self, developer_name: str) -> Optional[str]:
        return self._applier.resolve_definition_id(developer_name)

    def fetch_detail(self, context_id: str) -> Dict[str, Any]:
        return self._applier.fetch_detail(context_id)

    def is_active(self, detail: Dict[str, Any]) -> bool:
        return self._applier._is_active(detail)

    def deactivate(self, context_id: str) -> None:
        self._applier._set_active(context_id, False)

    def activate(self, context_id: str) -> None:
        self._applier._set_active(context_id, True)

    # ---- shared guards ---------------------------------------------------- #

    def guard_inherited(self, op: str, target: Dict[str, Any], label: str) -> None:
        """Refuse an op that modifies an inherited (standard-base) artifact.

        Only applied for ops in :data:`OP_RULES` with ``refuses_inherited``. The
        distinction (vs. delete's blanket rule) is deliberate — see the module
        docstring: ``set-default-mapping`` and ``add-tag`` legitimately target
        inherited mappings/attributes.
        """
        if not OP_RULES.get(op, {}).get("refuses_inherited"):
            return
        if target.get("baseReference"):
            raise MutatePreflightError(
                f"'{label}' is inherited from its standard base "
                f"(baseReference={target['baseReference']!r}); '{op}' modifies an "
                f"existing artifact and the platform blocks editing a base "
                f"artifact in place. Target a custom (__c) artifact instead."
            )

    def guard_active_state(self, op: str, detail: Dict[str, Any], *, context_id: str,
                           auto_deactivate: bool = False) -> Dict[str, Any]:
        """Refuse (or, if opted in, resolve) an op that the platform blocks on an
        *active* version.

        Ops with ``requires_inactive`` — every op except the pure inserts
        (``add-tag``, ``add-mapping``) — are blocked on an active version
        ("Cannot modify/delete an active context definition", live-verified).
        ``auto_deactivate`` (``--deactivate-first``) deactivates in place;
        otherwise the op is refused with guidance.

        Mutate's trigger is *op-gated* (per :data:`OP_RULES`); once that gate
        passes, the shared body in :func:`_client.guard_active` handles the
        refuse-or-deactivate mechanics.
        """
        if not OP_RULES.get(op, {}).get("requires_inactive"):
            return detail
        return _client.guard_active(
            detail, context_id=context_id, auto_deactivate=auto_deactivate,
            is_active_fn=self.is_active, deactivate_fn=self.deactivate,
            fetch_detail_fn=self.fetch_detail, dry_run=self.dry_run, logger=self.log,
            exception_type=MutatePreflightError,
            refuse_message=(
                f"Definition {context_id} is ACTIVE, and '{op}' modifies/deletes an "
                f"existing artifact — the platform blocks that on an active version "
                f"(\"Cannot modify/delete an active context definition\"). Re-run "
                f"with --deactivate-first (deactivate, mutate, then --reactivate). "
                f"Note: deactivation itself is blocked while an Expression Set still "
                f"references the definition. (Only 'add-tag' / 'add-mapping' run on "
                f"an active version, since they insert a new artifact.)"
            ),
            deactivate_message=(
                f"Definition {context_id} is active; deactivating first "
                f"(--deactivate-first) for '{op}'."
            ),
        )

    # ---- op: set-transient ----------------------------------------------- #

    def plan_set_transient(self, detail: Dict[str, Any], node_attr: str,
                           value: bool) -> Dict[str, Any]:
        target = find_attribute(detail, node_attr)
        if not target:
            raise MutatePreflightError(
                f"No attribute '{node_attr}' found on this definition. "
                f"(Use Node.Attr; names are case-sensitive.)"
            )
        self.guard_inherited("set-transient", target, node_attr)
        return {
            "op": "set-transient",
            "target": f"{target['node_name']}.{target['name']}",
            "id": target["contextAttributeId"],
            "from": target["isTransient"],
            "to": value,
            "noop": target["isTransient"] == value,
            "via": "SObject PATCH ContextAttribute.IsTransient",
            "_target": target,
        }

    def execute_set_transient(self, change: Dict[str, Any]) -> Dict[str, Any]:
        if change["noop"]:
            self.log(f"{change['target']}.IsTransient already {change['to']}; no change.")
            return {"op": change["op"], "target": change["target"],
                    "changed": False, "value": change["to"]}
        t = change["_target"]
        self._applier._sync_transient([{
            "node_name": t["node_name"], "name": t["name"],
            "context_attribute_id": t["contextAttributeId"],
            "is_transient": change["to"],
        }])
        return {"op": change["op"], "target": change["target"], "changed": True,
                "from": change["from"], "to": change["to"], "dry_run": self.dry_run}

    # ---- op: set-default-mapping ----------------------------------------- #

    def plan_set_default_mapping(self, detail: Dict[str, Any],
                                 mapping_name: str) -> Dict[str, Any]:
        target = find_mapping(detail, mapping_name)
        if not target:
            names = ", ".join(sorted(
                m.get("name", "?") for m in _iter_context_mappings(detail)))
            raise MutatePreflightError(
                f"No context mapping named '{mapping_name}'. Available: {names}"
            )
        current_default = None
        for m in _iter_context_mappings(detail):
            if _payload.as_bool(m.get("isDefault") or m.get("default")):
                current_default = m.get("name")
                break
        already = _payload.as_bool(target.get("isDefault") or target.get("default"))
        return {
            "op": "set-default-mapping",
            "target": mapping_name,
            "id": target.get("contextMappingId"),
            "from_default": current_default,
            "noop": already,
            "via": "Connect PATCH context-mappings isDefault:true",
        }

    def execute_set_default_mapping(self, context_id: str, detail: Dict[str, Any],
                                    change: Dict[str, Any]) -> Dict[str, Any]:
        if change["noop"]:
            self.log(f"'{change['target']}' is already the default mapping; no change.")
            return {"op": change["op"], "target": change["target"], "changed": False}
        ok = self._applier._set_default_mapping(context_id, change["target"], detail)
        if not ok and not self.dry_run:
            raise MutatePreflightError(
                f"Could not set '{change['target']}' as default (not found among "
                f"the definition's mappings)."
            )
        return {"op": change["op"], "target": change["target"], "changed": True,
                "previous_default": change["from_default"], "dry_run": self.dry_run}

    # ---- op: add-tag ----------------------------------------------------- #

    def plan_add_tag(self, detail: Dict[str, Any], node_attr: str,
                     tag_name: str) -> Dict[str, Any]:
        target = find_attribute(detail, node_attr)
        if not target:
            raise MutatePreflightError(
                f"No attribute '{node_attr}' found on this definition."
            )
        self.guard_inherited("add-tag", target, node_attr)  # no-op (rule allows inherited)
        existing = _tag_names_on_attribute(detail, target["contextAttributeId"])
        return {
            "op": "add-tag",
            "target": f"{target['node_name']}.{target['name']}",
            "tag": tag_name,
            "attribute_id": target["contextAttributeId"],
            "noop": tag_name in existing,
            "via": "POST context-tags",
            "_target": target,
            "_note": ("Custom tags on an extended base must end in '__c' and be "
                      "unique across the whole definition (platform-enforced)."),
        }

    def execute_add_tag(self, context_id: str, change: Dict[str, Any]) -> Dict[str, Any]:
        if change["noop"]:
            self.log(f"Tag '{change['tag']}' already on {change['target']}; no change.")
            return {"op": change["op"], "target": change["target"],
                    "tag": change["tag"], "changed": False}
        # Reuse the applier's tag writer with a direct id-based spec (bypasses
        # resolve_tags_by_name's name-index so a second tag on the same attribute
        # is not treated as "already present" at a different attribute).
        self._applier._post_tags(
            context_id,
            [{"contextAttributeId": change["attribute_id"], "name": change["tag"]}],
        )
        return {"op": change["op"], "target": change["target"], "tag": change["tag"],
                "changed": True, "dry_run": self.dry_run}

    # ---- op: add-mapping ------------------------------------------------- #

    def plan_add_mapping(self, detail: Dict[str, Any], node_attr: str,
                         mapping_name: str, sobject_field: str) -> Dict[str, Any]:
        """Bind an existing attribute to an SObject field on an existing node
        mapping, by creating a new ``ContextAttributeMapping`` + its
        ``ContextAttrHydrationDetail`` via SObject REST.

        This is the granular, **sibling-safe** alternative to the whole-body
        Connect node-mapping PATCH (which re-emits every sibling and, on a root
        node, tripped the ``mappedContextNodeId`` shape guard). A pure insert:
        it never touches an existing row, so no siblings can be lost and it runs
        on an **active** version.

        The node mapping's ``sObjectName`` is taken from ``detail`` (the caller
        supplies only the *field*), so the binding can never point at the wrong
        object. Direction (hydrate / persist) is **not** set here — it derives
        from the mapping's intents and the attribute's ``fieldType`` (e.g. an
        ``INPUTOUTPUT`` attribute on a mapping with both HYDRATION + PERSISTENCE
        intents reads as ``hydrate+persist`` in ``trace_context``). If the
        binding needs a tag for an engine to read/write it by name, add one
        separately with ``--add-tag``.
        """
        target = find_attribute(detail, node_attr)
        if not target:
            raise MutatePreflightError(
                f"No attribute '{node_attr}' found on this definition. "
                f"(Use Node.Attr; names are case-sensitive.)"
            )
        # Rule allows inherited attributes/nodes (this is the additive-binding
        # case); call kept for symmetry — it is a no-op for add-mapping.
        self.guard_inherited("add-mapping", target, node_attr)

        node_name = target["node_name"]
        nm_index = _index_node_mapping_ids(detail)
        node_mapping_id = nm_index.get((mapping_name, node_name))
        if not node_mapping_id:
            avail = ", ".join(sorted(
                f"{m}/{n}" for (m, n) in nm_index)) or "(none)"
            raise MutatePreflightError(
                f"No node mapping for mapping '{mapping_name}' on node "
                f"'{node_name}'. Available mapping/node pairs: {avail}"
            )
        sobject = _node_mapping_sobject(detail, node_mapping_id)
        if not sobject:
            raise MutatePreflightError(
                f"Node mapping {node_mapping_id} ('{mapping_name}'/'{node_name}') "
                f"has no sObjectName; cannot bind a field."
            )

        existing = _existing_attr_binding(
            detail, node_mapping_id, target["contextAttributeId"])
        # Four states the caller must tell apart (a prior run can die between
        # the CAM POST and the hydration-detail POST, leaving an orphan CAM):
        #   existing is None                 -> nothing bound; full create.
        #   complete + binding == requested  -> true no-op (already in this state).
        #   complete + binding != requested  -> rebind CONFLICT; must not no-op.
        #   CAM present, no hydration        -> incomplete; repair by POSTing only
        #                                       the ContextAttrHydrationDetail onto
        #                                       the existing CAM (never a second CAM).
        requested_binding = f"{sobject}.{sobject_field}"
        complete = bool(existing and existing.get("complete"))
        if complete:
            # ``complete`` only proves *some* hydration row exists — not that it
            # matches the requested field. No-op ONLY when the canonical existing
            # binding equals the requested sObject+field; a different field is a
            # rebind, which this granular pure-insert path does not support
            # (there is no CAM to update, and POSTing a second detail would leave
            # two source fields on one attribute). Surface an actionable conflict
            # rather than exiting 0 while silently leaving the old binding intact.
            existing_fields = existing.get("fields") or []
            matches = requested_binding in existing_fields
            if not matches:
                current = existing.get("hydration") or "(unknown)"
                raise MutatePreflightError(
                    f"{node_name}.{target['name']} on '{mapping_name}' is already "
                    f"bound to {current}, not the requested {requested_binding}. "
                    f"Rebinding an existing field is not supported by --add-mapping "
                    f"(a pure insert). Remove the existing binding first "
                    f"(deactivate + delete the ContextAttrHydrationDetail via "
                    f"describe_context.py), then re-run --add-mapping."
                )
        noop = complete  # complete AND matching, per the guard above
        repair = bool(existing and not complete)
        existing_cam_id = existing.get("cam_id") if existing else None
        if repair and not existing_cam_id:
            # CAM row is in the snapshot but carries no id we can bind to — we
            # cannot safely repair (a fresh CAM POST would duplicate it), so
            # surface it rather than silently no-op'ing an unusable mapping.
            raise MutatePreflightError(
                f"{node_name}.{target['name']} on '{mapping_name}' has a "
                f"ContextAttributeMapping with no source field and no "
                f"contextAttributeMappingId in the snapshot; cannot auto-repair "
                f"the missing ContextAttrHydrationDetail. Inspect the mapping "
                f"with describe_context.py and fix it manually."
            )
        return {
            "op": "add-mapping",
            "target": f"{node_name}.{target['name']}",
            "mapping": mapping_name,
            "sObject": sobject,
            "field": sobject_field,
            "attribute_id": target["contextAttributeId"],
            "node_mapping_id": node_mapping_id,
            "noop": noop,
            "repair": repair,
            "existing_cam_id": existing_cam_id,
            "existing_binding": existing.get("hydration") if existing else None,
            "via": "POST ContextAttributeMapping + ContextAttrHydrationDetail (SObject REST)",
            "_target": target,
            "_note": ("Granular insert — sibling-safe (never re-emits existing "
                      "attribute mappings) and allowed on an active version. Add "
                      "a tag separately with --add-tag if an engine reads it by name."),
        }

    def execute_add_mapping(self, change: Dict[str, Any]) -> Dict[str, Any]:
        if change["noop"]:
            self.log(f"{change['target']} is already bound on '{change['mapping']}' "
                     f"(-> {change['existing_binding']}); no change.")
            return {"op": change["op"], "target": change["target"],
                    "mapping": change["mapping"], "changed": False}
        if change.get("repair"):
            # A prior run left a ContextAttributeMapping with no source field
            # (it died before the hydration-detail POST). Reuse that CAM —
            # POSTing a second one would duplicate the binding — and only add
            # the missing ContextAttrHydrationDetail.
            keeper_id = change["existing_cam_id"]
            self.log(f"{change['target']} on '{change['mapping']}' has a "
                     f"ContextAttributeMapping ({keeper_id}) with no source "
                     f"field; repairing by adding the missing "
                     f"ContextAttrHydrationDetail.")
        else:
            # 1) ContextAttributeMapping — the binding row on the node mapping.
            cam_resp = self.t.sobject(
                "POST", ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING, None,
                {
                    "ContextNodeMappingId": change["node_mapping_id"],
                    "ContextAttributeId": change["attribute_id"],
                    "ContextInputAttributeName": change["target"].split(".", 1)[-1],
                },
            )
            keeper_id = None if self.dry_run else _record_id(cam_resp)
            if not keeper_id and not self.dry_run:
                raise MutatePreflightError(
                    f"Failed to create ContextAttributeMapping for {change['target']}."
                )
        # 2) ContextAttrHydrationDetail — the source-field binding (simple, 1 hop).
        #    Validate the id (mirrors _apply._apply_traversal_hydration): the two
        #    POSTs are not atomic, so a silent failure here would leave the same
        #    orphan CAM the repair path exists to fix — surface it instead of
        #    reporting a phantom `changed: True`.
        detail_resp = self.t.sobject(
            "POST", ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL, None,
            {"ContextAttributeMappingId": keeper_id,
             "ObjectName": change["sObject"],
             "QueryAttribute": change["field"]},
        )
        detail_id = None if self.dry_run else _record_id(detail_resp)
        if not detail_id and not self.dry_run:
            raise MutatePreflightError(
                f"Failed to create ContextAttrHydrationDetail for {change['target']} "
                f"(ContextAttributeMapping {keeper_id} left without a source field). "
                f"Re-run --add-mapping to repair the orphan CAM."
            )
        return {"op": change["op"], "target": change["target"],
                "mapping": change["mapping"],
                "binding": f"{change['sObject']}.{change['field']}",
                "repaired": bool(change.get("repair")),
                "changed": True, "dry_run": self.dry_run}

    # ---- op: remove-tag (delegated to the deleter) ----------------------- #

    def plan_remove_tag(self, detail: Dict[str, Any], context_id: str,
                        tag_name: str) -> List[Dict[str, Any]]:
        catalog = build_artifact_catalog(detail, context_id)
        try:
            return self._deleter.plan_target_deletion(
                catalog, kind="tag", name=tag_name, cascade=False)
        except DeletePreflightError as exc:
            raise MutatePreflightError(str(exc)) from exc

    def execute_remove_tag(self, ordered: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._deleter.execute(ordered)


# --------------------------------------------------------------------------- #
# Module helpers
# --------------------------------------------------------------------------- #

def _node_mapping_sobject(detail: Dict[str, Any], node_mapping_id: str) -> Optional[str]:
    """The ``sObjectName`` of the node mapping with the given id, from ``detail``.

    Read from the snapshot (authoritative) rather than SOQL'd — SOQL on the
    Context* objects is unreliable for this (live-verified 2026-07-08).
    """
    for mapping in _iter_context_mappings(detail):
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if isinstance(node_map, dict) and \
                    node_map.get("contextNodeMappingId") == node_mapping_id:
                return node_map.get("sObjectName")
    return None


def _existing_attr_binding(detail: Dict[str, Any], node_mapping_id: str,
                           attr_id: str) -> Optional[Dict[str, Any]]:
    """If the attribute already has a ``ContextAttributeMapping`` on this node
    mapping, return a dict describing it; else ``None``.

    Idempotency guard for ``add-mapping`` — re-running must not create a
    duplicate ``ContextAttributeMapping``. Matches on ``contextAttributeId``
    within the target node mapping and reads the flat ``contextAttrHydrationDetailList``
    that a Connect GET returns (SOQL on these objects is unreliable — the
    snapshot is authoritative).

    The returned dict distinguishes a **complete** binding from an **incomplete**
    one so a retry after a partial failure can finish the job::

        {"cam_id": <ContextAttributeMappingId | None>,
         "hydration": <"Obj.Field, ..." | None>,   # None => no source field yet
         "fields":    [<"Obj.Field">, ...],          # structured hops (for match)
         "complete":  <bool>}                        # True only when hydration exists

    A CAM created without its ``ContextAttrHydrationDetail`` (e.g. the process
    died between the two POSTs) reports ``complete=False`` so the caller repairs
    it rather than reporting a bound-but-unusable mapping as a no-op. ``fields``
    is the list form of ``hydration`` so a caller can decide whether an existing
    complete binding actually **matches** the requested sObject+field (a true
    no-op) versus points at a *different* field (a rebind conflict).
    """
    for mapping in _iter_context_mappings(detail):
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if not isinstance(node_map, dict):
                continue
            if node_map.get("contextNodeMappingId") != node_mapping_id:
                continue
            sobj = node_map.get("sObjectName")
            attr_maps = node_map.get("attributeMappings")
            if isinstance(attr_maps, dict):
                attr_maps = attr_maps.get("contextAttributeMappings", [])
            for attr_map in attr_maps or []:
                if not isinstance(attr_map, dict):
                    continue
                if attr_map.get("contextAttributeId") != attr_id:
                    continue
                fields = [
                    f"{h.get('sObjectDomain') or h.get('objectName') or sobj}."
                    f"{h.get('queryAttribute')}"
                    for h in (attr_map.get("contextAttrHydrationDetailList") or [])
                    if isinstance(h, dict) and h.get("queryAttribute")
                ]
                return {
                    "cam_id": attr_map.get("contextAttributeMappingId"),
                    "hydration": ", ".join(fields) if fields else None,
                    "fields": fields,
                    "complete": bool(fields),
                }
    return None


def _tag_names_on_attribute(detail: Dict[str, Any], attr_id: str) -> set:
    """Names of every tag hanging off the attribute whose id matches.

    Nested ``attributeTags`` on a Connect GET only carry ``{name, dynamic}`` —
    ``contextAttributeId`` lives on the enclosing attribute, so a
    ``contextAttributeId``-based filter finds nothing and duplicates the tag on
    re-run. Since the caller has already located the attribute, collect ``name``
    from that attribute's tag list directly.
    """
    version = _client.active_version(detail)
    for node, _depth in _client.iter_nodes(version.get("contextNodes", [])):
        for attr in _client.node_attributes(node):
            if not isinstance(attr, dict):
                continue
            if attr.get("contextAttributeId") != attr_id:
                continue
            # Shared GET-shape unwrap lives in _client (single source of truth).
            return _client.attr_tag_names(attr)
    return set()
