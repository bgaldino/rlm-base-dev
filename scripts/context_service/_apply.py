#!/usr/bin/env python3
"""Orchestration sequencer for the Context Service mutation scripts.

Holds the **parity-critical ordering** that ``tasks/rlm_context_service.py``
uses to apply a plan (``_run_plan_for_context`` / ``_run_create_flow``), but
built on the standalone ``sf``-CLI transport (``_client``) and the pure payload
library (``_payload``) instead of CumulusCI internals. No ``cumulusci`` import.

Transport is injected via a small :class:`Transport` adapter so the ordering can
be unit-tested with a fake (no org). The default adapter binds ``_client`` to a
target org / api version / dry-run flag.

Endpoint paths come from ``_endpoints`` (confirmed against the public Context
Service REST reference). SObject-REST-only operations (MappedContextDefinition,
IsTransient, traversal hydration) go through ``Transport.sobject`` /
``Transport.soql``.
"""

from typing import Any, Callable, Dict, List, Optional

import _client
import _endpoints as ep
import _payload


# --------------------------------------------------------------------------- #
# Transport adapter (injectable)
# --------------------------------------------------------------------------- #

class Transport:
    """Binds the CLI transport to one org / api-version / dry-run setting.

    Swappable in tests: any object exposing ``request``, ``sobject``, ``soql``
    with these signatures works.
    """

    def __init__(self, target_org: str, api_version: str = _client.DEFAULT_API_VERSION,
                 dry_run: bool = False, logger: Callable[..., None] = None):
        self.target_org = target_org
        self.api_version = api_version
        self.dry_run = dry_run
        self.logger = logger or _client.eprint

    def request(self, method: str, path: str, body: Any = None) -> Any:
        return _client.connect_request(
            method, path, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run, logger=self.logger,
        )

    def sobject(self, method: str, sobject: str, record_id: Optional[str] = None,
                body: Any = None) -> Any:
        return _client.sobjects_request(
            method, sobject, record_id, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run, logger=self.logger,
        )

    def soql(self, query: str) -> List[Dict[str, Any]]:
        # Reads always execute (non-mutating), even under dry_run.
        return _client.soql_query(
            query, target_org=self.target_org, api_version=self.api_version
        )


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

class ContextApplier:
    """Apply an additive context plan (or create a new definition) to an org.

    Mirrors ``ManageContextDefinition._run_plan_for_context`` /
    ``_run_create_flow``.
    """

    def __init__(self, transport: Transport, logger: Callable[..., None] = None):
        self.t = transport
        self.log = logger or transport.logger
        self.dry_run = transport.dry_run

    # ---- definition resolution / creation -------------------------------- #

    def resolve_definition_id(self, developer_name: str) -> Optional[str]:
        """Find a definition id by developerName (list, then direct lookup)."""
        resp = self.t.request("GET", f"{ep.DEFINITION_COLLECTION}?includeInactive=true")
        for item in _client.normalize_definition_list(resp):
            if _client.definition_developer_name(item) == developer_name:
                return item.get("contextDefinitionId") or item.get("id")
        # Fallback: direct lookup endpoint returns isSuccess:false for unknown.
        try:
            direct = self.t.request(
                "GET", ep.DEFINITION_ITEM.format(context_definition_id=developer_name)
            )
        except _client.ContextClientError:
            return None
        if isinstance(direct, dict) and direct.get("isSuccess") is not False:
            return direct.get("contextDefinitionId")
        return None

    def create_definition(self, plan: Dict[str, Any]) -> Optional[str]:
        """POST a create payload; recover the id on DUPLICATE_VALUE.

        Mirrors ``_create_context_definition_record`` +
        ``ExtendStandardContext._recover_context_id`` (DUPLICATE_VALUE) and the
        ``allow_skip_if_unavailable`` UNKNOWN_EXCEPTION skip.
        """
        payload = _payload.build_create_payload(plan)
        self.log(f"Creating context definition: {payload.get('developerName')}")
        try:
            resp = self.t.request("POST", ep.DEFINITION_COLLECTION, payload)
        except _client.ContextClientError as exc:
            if exc.has_error_code("UNKNOWN_EXCEPTION"):
                # Base context not provisioned on this edition.
                if _payload.as_bool(plan.get("allow_skip_if_unavailable")):
                    self.log(
                        f"Base context definition not available for "
                        f"'{plan.get('developerName')}'; skipping "
                        f"(allow_skip_if_unavailable)."
                    )
                    return None
                raise
            if exc.has_error_code("DUPLICATE_VALUE"):
                self.log(
                    f"Context definition '{plan.get('developerName')}' already "
                    f"exists; recovering id."
                )
                return self.resolve_definition_id(plan.get("developerName"))
            raise
        if self.dry_run:
            return "dry-run-id"
        if isinstance(resp, dict):
            ctx_id = resp.get("contextDefinitionId") or resp.get("id")
            if ctx_id:
                return ctx_id
            self.log(f"Create response missing contextDefinitionId: {resp}")
        return None

    def fetch_detail(self, context_id: str) -> Dict[str, Any]:
        resp = self.t.request(
            "GET", ep.DEFINITION_ITEM.format(context_definition_id=context_id)
        )
        if isinstance(resp, list):
            return resp[0] if len(resp) == 1 and isinstance(resp[0], dict) else {}
        return resp or {}

    # ---- low-level writers (port of the task's _post_* / _patch_* ) ------- #

    def _create_nodes_hierarchical(
        self, context_id: str, node_defs: List[Dict[str, Any]],
        existing_detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Port of ``_create_context_nodes_hierarchical`` (parent-first, capture ids)."""
        node_id_by_name: Dict[str, str] = {}
        if existing_detail and not self.dry_run:
            node_id_by_name.update(_index_node_ids(existing_detail))
        path = ep.NODE_COLLECTION.format(context_definition_id=context_id)
        for node_def in node_defs:
            if not isinstance(node_def, dict):
                continue
            node_name = node_def.get("name")
            if not node_name:
                raise ValueError(f"contextNodeDefinitions entry missing 'name': {node_def}")
            node_payload = {"name": node_name}
            parent_name = node_def.get("parentNodeName")
            if parent_name:
                parent_id = node_id_by_name.get(parent_name)
                if parent_id:
                    node_payload["parentNodeId"] = parent_id
                else:
                    self.log(f"Parent node '{parent_name}' not yet created for "
                             f"'{node_name}'; skipping parent link.")
            self.log(f"Creating context node: {node_name}")
            resp = self.t.request("POST", path, {"contextNodes": [node_payload]})
            if self.dry_run:
                continue
            node_id = _first_created_node_id(resp)
            if node_id:
                node_id_by_name[node_name] = node_id
                continue
            # Fallback: re-fetch to locate the node id.
            detail = self.fetch_detail(context_id)
            found = _index_node_ids(detail).get(node_name)
            if found:
                node_id_by_name[node_name] = found

    def _post_mapping_shells(self, context_id: str, filtered: Dict[str, Any]) -> None:
        self.t.request(
            "POST", ep.MAPPING_COLLECTION.format(context_definition_id=context_id), filtered
        )

    def _post_attributes(self, attributes: List[Dict[str, Any]]) -> None:
        """Port of ``_post_context_attributes``: group by node id, POST per node."""
        by_node: Dict[str, List[Dict[str, Any]]] = {}
        for attr in attributes:
            if not isinstance(attr, dict):
                continue
            node_id = attr.get("contextNodeId")
            if not node_id:
                continue
            by_node.setdefault(node_id, []).append(
                {k: v for k, v in attr.items() if k != "contextNodeId"}
            )
        for node_id, attrs in by_node.items():
            self.t.request(
                "POST", ep.ATTRIBUTE_COLLECTION.format(context_node_id=node_id),
                {"contextAttributes": attrs},
            )

    def _post_tags(self, context_id: str, tags: List[Dict[str, Any]]) -> None:
        self.t.request(
            "POST", ep.TAG_COLLECTION.format(context_definition_id=context_id),
            {"contextTags": tags},
        )

    def _sync_transient(self, updates: List[Dict[str, Any]]) -> None:
        for u in updates:
            self.log(f"Updating ContextAttribute {u['node_name']}.{u['name']} "
                     f"IsTransient={u['is_transient']}")
            self.t.sobject(
                "PATCH", ep.SOBJECT_CONTEXT_ATTRIBUTE, u["context_attribute_id"],
                {"IsTransient": u["is_transient"]},
            )

    def _apply_mapping_updates(self, context_id: str, payload: Dict[str, Any]) -> None:
        """Port of ``_apply_context_mapping_updates``: split node mappings out to
        the context-node-mappings endpoint; set MappedContextDefinition via
        sObject REST; PATCH the remainder via context-mappings."""
        if not isinstance(payload, dict):
            return
        mappings = payload.get("contextMappings")
        if not isinstance(mappings, list):
            return
        remaining = []
        for mapping in mappings:
            if not isinstance(mapping, dict):
                continue
            context_mapping_id = mapping.get("contextMappingId")
            node_maps = mapping.get("contextNodeMappings")
            if context_mapping_id and node_maps:
                if isinstance(node_maps, dict):
                    node_maps = node_maps.get("contextNodeMappings", [])
                normalized = []
                for node_map in node_maps or []:
                    node_map = _payload.normalize_attribute_mappings(node_map)
                    if isinstance(node_map, dict):
                        normalized.append(node_map)
                if normalized:
                    nm_path = ep.NODE_MAPPING_COLLECTION.format(
                        context_mapping_id=context_mapping_id
                    )
                    verb = "PATCH" if any(m.get("contextNodeMappingId") for m in normalized) else "POST"
                    self.log(f"{verb} {len(normalized)} node mapping(s) for "
                             f"mappingId={context_mapping_id}")
                    self.t.request(verb, nm_path, {"contextNodeMappings": normalized})
                mapped_ctx_def = mapping.get("mappedContextDefinitionName")
                if mapped_ctx_def:
                    for nm in normalized:
                        nm_id = nm.get("contextNodeMappingId")
                        if nm_id:
                            self._set_mapped_context_definition(nm_id, mapped_ctx_def)
                continue
            remaining.append(mapping)
        if remaining:
            self._patch_context_mappings(context_id, remaining)

    def _patch_context_mappings(self, context_id: str, mappings: List[Dict[str, Any]]) -> None:
        path = ep.MAPPING_COLLECTION.format(context_definition_id=context_id)
        for mapping in mappings:
            if not isinstance(mapping, dict):
                continue
            mapping = {k: v for k, v in mapping.items() if k != "name"}
            self.t.request("PATCH", path, {"contextMappings": [_payload.strip_none(mapping)]})

    def _set_mapped_context_definition(self, node_mapping_id: str, developer_name: str) -> None:
        self.log(f"Setting MappedContextDefinition={developer_name} on "
                 f"ContextNodeMapping {node_mapping_id}")
        self.t.sobject(
            "PATCH", ep.SOBJECT_CONTEXT_NODE_MAPPING, node_mapping_id,
            {"MappedContextDefinition": developer_name},
        )

    def _apply_traversal_hydration(
        self, rules: List[Dict[str, Any]], detail: Dict[str, Any]
    ) -> None:
        """Port of ``_apply_traversal_hydration`` (SObject REST + SOQL idempotency)."""
        version0 = detail.get("contextDefinitionVersionList", []) if isinstance(detail, dict) else []
        mappings = version0[0].get("contextMappings", []) if version0 else []
        node_mapping_id_index: Dict[tuple, str] = {}
        for mapping in mappings or []:
            if not isinstance(mapping, dict):
                continue
            m_name = mapping.get("name") or mapping.get("title")
            for node_map in mapping.get("contextNodeMappings", []) or []:
                if not isinstance(node_map, dict):
                    continue
                n_name = node_map.get("contextNodeName")
                n_map_id = node_map.get("contextNodeMappingId")
                if m_name and n_name and n_map_id:
                    node_mapping_id_index[(m_name, n_name)] = n_map_id
        _, attr_index = _payload.collect_context_indexes(detail, {})

        for rule in rules:
            attr_name = rule.get("contextAttribute")
            mapping_name = rule.get("mappingName")
            node_name = rule.get("contextNode")
            s_object = rule.get("sObject")
            s_object_field = rule.get("sObjectField")
            child_s_object = rule.get("childSObject")
            child_s_object_field = rule.get("childSObjectField")
            if not all([attr_name, mapping_name, node_name, s_object, s_object_field,
                        child_s_object, child_s_object_field]):
                continue

            existing = self.t.soql(
                f"SELECT Id,CreatedDate FROM ContextAttributeMapping "
                f"WHERE ContextInputAttributeName='{attr_name}' ORDER BY CreatedDate DESC"
            )
            if existing:
                keeper_id = existing[0]["Id"]
            else:
                node_mapping_id = node_mapping_id_index.get((mapping_name, node_name))
                attr_id = attr_index.get((node_name, attr_name))
                if not node_mapping_id or not attr_id:
                    self.log(f"Cannot create ContextAttributeMapping for {attr_name}: "
                             f"node_mapping_id={node_mapping_id} attr_id={attr_id}")
                    continue
                cam_resp = self.t.sobject(
                    "POST", ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING, None,
                    {
                        "ContextNodeMappingId": node_mapping_id,
                        "ContextAttributeId": attr_id,
                        "ContextInputAttributeName": attr_name,
                    },
                )
                if self.dry_run:
                    continue
                keeper_id = _record_id(cam_resp)
                if not keeper_id:
                    self.log(f"Failed to create ContextAttributeMapping for {attr_name}")
                    continue

            hd_existing = self.t.soql(
                f"SELECT Id FROM ContextAttrHydrationDetail "
                f"WHERE ContextAttributeMappingId='{keeper_id}'"
            )
            if hd_existing:
                self.log(f"Traversal hydration already exists for {attr_name}; skipping")
                continue

            self.log(f"Creating traversal hydration for {attr_name}: "
                     f"{s_object}.{s_object_field} -> {child_s_object}.{child_s_object_field}")
            parent_resp = self.t.sobject(
                "POST", ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL, None,
                {"ContextAttributeMappingId": keeper_id, "ObjectName": s_object,
                 "QueryAttribute": s_object_field},
            )
            if self.dry_run:
                continue
            parent_id = _record_id(parent_resp)
            if not parent_id:
                self.log(f"Failed to get parent hydration detail id for {attr_name}")
                continue
            self.t.sobject(
                "POST", ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL, None,
                {"ContextAttributeMappingId": keeper_id, "ObjectName": child_s_object,
                 "QueryAttribute": child_s_object_field, "ParentHydrationDetailId": parent_id},
            )

    def _set_active(self, context_id: str, is_active: bool) -> None:
        """Activate / deactivate a definition (PATCH isActive).

        Live-confirmed platform constraint: deactivation returns
        ``RECORD_UPDATE_FAILED`` when the definition is referenced by an
        Expression Set (e.g. a pricing procedure or DocGen template). We
        re-raise with an actionable note rather than swallowing it, matching the
        CCI task (which lets the error bubble).
        """
        try:
            self.t.request(
                "PATCH", ep.DEFINITION_ITEM.format(context_definition_id=context_id),
                {"isActive": "true" if is_active else "false"},
            )
        except _client.ContextClientError as exc:
            if not is_active and exc.has_error_code("RECORD_UPDATE_FAILED"):
                raise _client.ContextClientError(
                    f"Cannot deactivate context definition {context_id}: it is "
                    f"referenced by an Expression Set (pricing procedure / DocGen "
                    f"template). Detach or deactivate the referencing Expression "
                    f"Set first, or apply this plan on an org where the definition "
                    f"is not yet wired. Original error:\n{exc}",
                    error_codes=exc.error_codes, body=exc.body, returncode=exc.returncode,
                ) from exc
            raise

    def _is_active(self, detail: Dict[str, Any]) -> bool:
        if not isinstance(detail, dict):
            return False
        if detail.get("isActive") is not None or detail.get("active") is not None:
            return bool(detail.get("isActive") or detail.get("active"))
        versions = detail.get("contextDefinitionVersionList", [])
        if versions and isinstance(versions[0], dict):
            return bool(versions[0].get("isActive"))
        return False

    def _has_default_mapping(self, detail: Dict[str, Any]) -> bool:
        """True if any contextMapping on the active version is flagged default."""
        for mapping in _iter_context_mappings(detail):
            if _payload.as_bool(mapping.get("isDefault") or mapping.get("default")):
                return True
        return False

    def _set_default_mapping(self, context_id: str, mapping_name: str,
                             detail: Dict[str, Any]) -> bool:
        """Flag ``mapping_name`` as the default context mapping (isDefault:true).

        Port of ``ExtendStandardContext._process_version_list`` /
        ``_update_context_mappings``: a version cannot activate without a default
        mapping (``DATA_MAPPING_NOT_FOUND``), so this must run before activation
        on a freshly-created definition. Returns True if the mapping was found
        and the PATCH was issued. Live-confirmed on API v67.0.
        """
        mapping_id = None
        for mapping in _iter_context_mappings(detail):
            if mapping.get("name") == mapping_name:
                mapping_id = mapping.get("contextMappingId")
                break
        if not mapping_id:
            self.log(f"Default mapping '{mapping_name}' not found among the "
                     f"definition's mappings; cannot set it as default.")
            return False
        self.log(f"Setting '{mapping_name}' as the default context mapping.")
        self.t.request(
            "PATCH", ep.MAPPING_COLLECTION.format(context_definition_id=context_id),
            {"contextMappings": [
                {"contextMappingId": mapping_id, "isDefault": "true", "name": mapping_name}
            ]},
        )
        return True

    def _ensure_default_mapping(self, context_id: str, plan: Dict[str, Any],
                                detail: Dict[str, Any]) -> None:
        """Ensure a default mapping is set before activation.

        Uses the plan's ``defaultMapping`` if provided; otherwise, if the
        definition already has a default flagged, does nothing. Skips silently
        under dry-run (the detail is a live read, but the PATCH is a mutation).
        """
        if self.dry_run:
            # detail reflects the live pre-state; only warn if clearly missing.
            if plan.get("defaultMapping") and not self._has_default_mapping(detail):
                self.log(f"[dry-run] would set default mapping "
                         f"'{plan['defaultMapping']}' before activation.")
            return
        if self._has_default_mapping(detail):
            return
        mapping_name = plan.get("defaultMapping")
        if not mapping_name:
            self.log("No default mapping set and plan has no 'defaultMapping'; "
                     "activation may fail with DATA_MAPPING_NOT_FOUND.")
            return
        self._set_default_mapping(context_id, mapping_name, detail)

    # ---- the sequencer ---------------------------------------------------- #

    def apply_plan(
        self, plan: Dict[str, Any], *,
        context_id: Optional[str] = None,
        developer_name: Optional[str] = None,
        translate_plan: bool = True,
        activate: Optional[bool] = None,
        deactivate_before: bool = False,
        verify: bool = False,
    ) -> Dict[str, Any]:
        """Apply one plan. Returns a summary dict (``context_id``, ``created``,
        ``verification`` if verify)."""
        developer_name = developer_name or plan.get("developerName")
        if activate is None:
            activate = _payload.as_bool(plan.get("activate"))
        created = False

        if not context_id:
            context_id = plan.get("contextDefinitionId")
        if not context_id:
            if not developer_name:
                raise ValueError("context_definition_id or developer_name is required")
            context_id = self.resolve_definition_id(developer_name)

        if not context_id:
            if _payload.as_bool(plan.get("create")):
                context_id = self.create_definition(plan)
                created = True
                if context_id is None:
                    # skipped (allow_skip_if_unavailable) or dry-run miss
                    return {"context_id": None, "created": False, "skipped": True}
                self.log(f"Created ContextDefinitionId: {context_id}")
                return self._run_create_flow(
                    context_id, developer_name, plan,
                    translate_plan=translate_plan, activate=activate, verify=verify,
                    created=created,
                )
            raise ValueError(
                f"Unable to resolve context definition for {developer_name}. "
                f"Set 'create: true' in the plan to create it."
            )

        self.log(f"Using ContextDefinitionId: {context_id}")
        return self._run_additive_flow(
            context_id, developer_name, plan,
            translate_plan=translate_plan, activate=activate,
            deactivate_before=deactivate_before, verify=verify,
        )

    def _run_additive_flow(self, context_id, developer_name, plan, *,
                           translate_plan, activate, deactivate_before, verify):
        if deactivate_before:
            pre = self.fetch_detail(context_id)
            if self._is_active(pre):
                self._set_active(context_id, False)

        detail = self.fetch_detail(context_id)

        if plan.get("contextNodeDefinitions"):
            new_defs = _payload.filter_new_nodes(plan["contextNodeDefinitions"], detail)
            if new_defs:
                self._create_nodes_hierarchical(context_id, new_defs, existing_detail=detail)
                detail = self.fetch_detail(context_id)

        if plan.get("contextMappings"):
            filtered = _payload.filter_existing_mappings(plan["contextMappings"], detail)
            if filtered:
                self._post_mapping_shells(context_id, filtered)
            detail = self.fetch_detail(context_id)

        if plan.get("contextAttributesByName"):
            resolved_attrs = _payload.resolve_attributes_by_name(
                plan["contextAttributesByName"], detail, logger=self.log
            )
            if resolved_attrs:
                self._post_attributes(resolved_attrs)
                detail = self.fetch_detail(context_id)
            transient = _payload.transient_updates(plan["contextAttributesByName"], detail)
            if transient:
                self._sync_transient(transient)
                detail = self.fetch_detail(context_id)

        if translate_plan and plan.get("mappingRules"):
            detail = self._apply_mapping_rules(context_id, developer_name, plan, detail)

        if plan.get("contextMappingUpdates"):
            resolved = _payload.resolve_context_mapping_ids(detail, plan["contextMappingUpdates"])
            self._apply_mapping_updates(context_id, resolved)

        self._apply_tags(context_id, plan, detail)

        result = {"context_id": context_id, "created": False}
        if verify:
            detail = self.fetch_detail(context_id)
            result["verification"] = _payload.plan_verification(detail, plan)
        if activate:
            # Guard against DATA_MAPPING_NOT_FOUND if the def has no default
            # mapping yet (only acts when the plan supplies defaultMapping and
            # none is already flagged).
            self._ensure_default_mapping(context_id, plan, self.fetch_detail(context_id))
            self._set_active(context_id, True)
        return result

    def _run_create_flow(self, context_id, developer_name, plan, *,
                         translate_plan, activate, verify, created):
        node_defs = plan.get("contextNodeDefinitions")
        if node_defs:
            self._create_nodes_hierarchical(context_id, node_defs)
        elif plan.get("contextNodes"):
            self.t.request(
                "POST", ep.NODE_COLLECTION.format(context_definition_id=context_id),
                plan["contextNodes"],
            )
        if plan.get("contextMappings"):
            filtered = plan["contextMappings"]  # nothing exists yet on a new def
            if filtered:
                self._post_mapping_shells(context_id, filtered)
        if self.dry_run:
            return {"context_id": context_id, "created": created, "dry_run": True}
        detail = self.fetch_detail(context_id)

        if plan.get("contextAttributesByName"):
            resolved_attrs = _payload.resolve_attributes_by_name(
                plan["contextAttributesByName"], detail, logger=self.log
            )
            if resolved_attrs:
                self._post_attributes(resolved_attrs)
                detail = self.fetch_detail(context_id)
            transient = _payload.transient_updates(plan["contextAttributesByName"], detail)
            if transient:
                self._sync_transient(transient)
                detail = self.fetch_detail(context_id)

        if translate_plan and plan.get("mappingRules"):
            detail = self._apply_mapping_rules(context_id, developer_name, plan, detail)

        if plan.get("contextMappingUpdates"):
            resolved = _payload.resolve_context_mapping_ids(detail, plan["contextMappingUpdates"])
            self._apply_mapping_updates(context_id, resolved)

        self._apply_tags(context_id, plan, detail)

        result = {"context_id": context_id, "created": created}
        if verify:
            detail = self.fetch_detail(context_id)
            result["verification"] = _payload.plan_verification(detail, plan)
        if activate:
            # A freshly-created definition cannot activate without a default
            # mapping (DATA_MAPPING_NOT_FOUND). Mirror ExtendStandardContext:
            # flag the plan's defaultMapping before flipping isActive.
            self._ensure_default_mapping(context_id, plan, self.fetch_detail(context_id))
            self._set_active(context_id, True)
        return result

    def _apply_mapping_rules(self, context_id, developer_name, plan, detail):
        """SOBJECT (simple + traversal) then CONTEXT rules, in the task's order."""
        rules = plan.get("mappingRules") or []
        sobject_rules, context_rules = [], []
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            if (rule.get("mappingType") or "SOBJECT").upper() == "CONTEXT":
                context_rules.append(rule)
            else:
                sobject_rules.append(rule)

        if sobject_rules:
            traversal_rules = [r for r in sobject_rules if r.get("childSObjectField")]
            patch_rules = [r for r in sobject_rules if not r.get("childSObjectField")]
            if patch_rules:
                translated, side_effects = _payload.translate_mapping_rules(
                    patch_rules, detail, logger=self.log
                )
                if translated:
                    resolved = _payload.resolve_context_mapping_ids(detail, translated)
                    self._apply_mapping_updates(context_id, resolved)
                    detail = self.fetch_detail(context_id)
                self._run_side_effects(side_effects)
            if traversal_rules:
                self._apply_traversal_hydration(traversal_rules, detail)
                detail = self.fetch_detail(context_id)

        if context_rules:
            translated, side_effects = _payload.translate_mapping_rules(
                context_rules, detail, developer_name=developer_name, logger=self.log
            )
            if translated:
                resolved = _payload.resolve_context_mapping_ids(detail, translated)
                self._apply_mapping_updates(context_id, resolved)
                detail = self.fetch_detail(context_id)
            self._run_side_effects(side_effects)
        return detail

    def _run_side_effects(self, side_effects: List[Dict[str, Any]]) -> None:
        for se in side_effects or []:
            if se.get("type") == "set_mapped_context_definition":
                self._set_mapped_context_definition(
                    se["node_mapping_id"], se["developer_name"]
                )

    def _apply_tags(self, context_id, plan, detail):
        if plan.get("contextTagsByName"):
            resolved = _payload.resolve_tags_by_name(
                plan["contextTagsByName"], detail, logger=self.log
            )
            if resolved:
                self._post_tags(context_id, resolved)
        if plan.get("contextTags"):
            tags = plan["contextTags"]
            if isinstance(tags, dict):
                tags = tags.get("contextTags", [])
            if tags:
                self._post_tags(context_id, tags)


# --------------------------------------------------------------------------- #
# Module helpers
# --------------------------------------------------------------------------- #

def _iter_context_mappings(detail: Dict[str, Any]):
    """Yield each contextMapping dict on the (first/active) version."""
    if not isinstance(detail, dict):
        return
    versions = detail.get("contextDefinitionVersionList", [])
    mappings = versions[0].get("contextMappings", []) if versions else []
    for mapping in mappings or []:
        if isinstance(mapping, dict):
            yield mapping


def _index_node_ids(detail: Dict[str, Any]) -> Dict[str, str]:
    """name -> contextNodeId across the whole node tree."""
    out: Dict[str, str] = {}
    versions = detail.get("contextDefinitionVersionList", []) if isinstance(detail, dict) else []
    nodes = versions[0].get("contextNodes", []) if versions else []

    def walk(node_list):
        for node in node_list or []:
            if not isinstance(node, dict):
                continue
            name, nid = node.get("name"), node.get("contextNodeId")
            if name and nid:
                out[name] = nid
            child = node.get("childNodes", {})
            children = child.get("contextNodes", []) if isinstance(child, dict) else (child or [])
            walk(children)

    walk(nodes)
    return out


def _first_created_node_id(resp: Any) -> Optional[str]:
    if isinstance(resp, dict):
        created = resp.get("contextNodes", [])
        if created and isinstance(created[0], dict):
            return created[0].get("contextNodeId")
    return None


def _record_id(resp: Any) -> Optional[str]:
    if isinstance(resp, dict):
        return resp.get("id") or resp.get("Id")
    return None
