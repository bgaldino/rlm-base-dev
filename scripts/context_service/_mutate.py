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
   * ``remove-tag`` delegates to :class:`_delete.ContextDeleter`, which refuses
     an inherited tag.

2. **Op-specific active-state guard (the ADD-vs-MODIFY/DELETE asymmetry).** The
   platform rule is literal in its own error text — "Cannot **modify/delete** an
   active context definition": **adding a new child is allowed on an active
   version; modifying or deleting an *existing* artifact is blocked.** So by wire
   operation:

   * ``add-tag`` — POSTs a **new** child tag → **allowed on an active version**.
   * ``set-transient`` — an ``IsTransient`` SObject **PATCH of an existing
     attribute** → **BLOCKED on an active version** (``RECORD_UPDATE_FAILED``
     "Cannot modify/delete an active context definition"). Needs
     ``--deactivate-first``.
   * ``set-default-mapping`` — a Connect ``context-mappings`` **PATCH of an
     existing mapping** → **BLOCKED on an active version** (same error). Needs
     ``--deactivate-first``.
   * ``remove-tag`` — a delete → **blocked while active** (same error). Needs
     ``--deactivate-first``.

   So ``add-tag`` is the *only* op that runs on an active version; the other
   three (two modifies + one delete) all require deactivate-first.

3. **No-op detection.** Setting ``IsTransient`` to its current value, or
   flagging an already-default mapping, is reported as "already <value>" and
   skipped rather than issuing a redundant PATCH.
"""

from typing import Any, Callable, Dict, List, Optional

import _client
import _endpoints as ep
import _payload
from _apply import ContextApplier, Transport, _iter_context_mappings
from _delete import ContextDeleter, DeletePreflightError, build_artifact_catalog


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

        Ops with ``requires_inactive`` — every op except the pure insert
        ``add-tag`` — are blocked on an active version ("Cannot modify/delete an
        active context definition", live-verified). ``auto_deactivate``
        (``--deactivate-first``) deactivates in place; otherwise the op is
        refused with guidance.
        """
        if not OP_RULES.get(op, {}).get("requires_inactive"):
            return detail
        if not self.is_active(detail):
            return detail
        if not auto_deactivate:
            raise MutatePreflightError(
                f"Definition {context_id} is ACTIVE, and '{op}' modifies/deletes an "
                f"existing artifact — the platform blocks that on an active version "
                f"(\"Cannot modify/delete an active context definition\"). Re-run "
                f"with --deactivate-first (deactivate, mutate, then --reactivate). "
                f"Note: deactivation itself is blocked while an Expression Set still "
                f"references the definition. (Only 'add-tag' runs on an active "
                f"version, since it inserts a new artifact.)"
            )
        self.log(f"Definition {context_id} is active; deactivating first "
                 f"(--deactivate-first) for '{op}'.")
        self.deactivate(context_id)
        if self.dry_run:
            return detail
        return self.fetch_detail(context_id)

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
        existing = {
            t.get("name")
            for t in _tags_on_attribute(detail, target["contextAttributeId"])
        }
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

def _tags_on_attribute(detail: Dict[str, Any], attr_id: str) -> List[Dict[str, Any]]:
    """Every tag whose contextAttributeId matches, across the active version."""
    out: List[Dict[str, Any]] = []
    version = _client.active_version(detail)
    for node, _depth in _client.iter_nodes(version.get("contextNodes", [])):
        for attr in _client.node_attributes(node):
            if not isinstance(attr, dict):
                continue
            for tag in attr.get("attributeTags") or attr.get("tags") or []:
                if isinstance(tag, dict) and tag.get("contextAttributeId") == attr_id:
                    out.append(tag)
    return out
