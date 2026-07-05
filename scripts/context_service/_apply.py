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

    def request(self, method: str, path: str, body: Any = None,
                *, dry_run: Optional[bool] = None) -> Any:
        # ``dry_run`` overrides the transport's bound flag for this one call — the
        # runtime path uses it to force read-shaped POSTs (query-record,
        # query-tags) to execute even under a dry-run session (see _runtime.py /
        # the dry-run contract). ``None`` (the design-time default) inherits.
        return _client.connect_request(
            method, path, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
        )

    def sobject(self, method: str, sobject: str, record_id: Optional[str] = None,
                body: Any = None, *, dry_run: Optional[bool] = None) -> Any:
        return _client.sobjects_request(
            method, sobject, record_id, body,
            target_org=self.target_org, api_version=self.api_version,
            dry_run=self.dry_run if dry_run is None else dry_run,
            logger=self.logger,
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
        # Set by ``apply_plan`` from its ``deactivate_before`` kwarg; consulted
        # by ``_guard_active_for_patch`` at each hazard point (see P2 in
        # .claude/plans/context-service-followup-fixes.md).
        self._deactivate_first = False

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

    def _apply_mapping_updates(
        self, context_id: str, payload: Dict[str, Any],
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Port of ``_apply_context_mapping_updates``: split node mappings out to
        the context-node-mappings endpoint; set MappedContextDefinition via
        sObject REST; PATCH the remainder via context-mappings.

        **Whole-body-replace hazard on the PATCH branch (v67.0):** Connect
        ``PATCH context-mappings/{id}/context-node-mappings`` returns
        ``isSuccess:true`` on an active version but interprets a
        ``contextAttributeMappings`` list that omits sibling rows as a
        **delete** of those siblings — a silent data-loss surface. Live-verified
        2026-07-04, `RLM_TEMP_ContextProbe` on ``rlm-base__july3_noramps``.

        Mitigation on the PATCH path: before issuing, look up the existing
        ``contextAttributeMappings`` for each target node mapping from the
        supplied ``detail`` snapshot and merge any siblings we did not re-emit
        back into the payload. This keeps the PATCH non-destructive without
        changing the endpoint. If ``detail`` is not supplied the merge is a
        no-op and the historical destructive behavior is unchanged — new callers
        should thread the current ``detail`` snapshot in.

        The POST branch (new node mappings) is unaffected; the platform has no
        siblings to lose.
        """
        if not isinstance(payload, dict):
            return
        mappings = payload.get("contextMappings")
        if not isinstance(mappings, list):
            return
        existing_children = _existing_node_mapping_children(detail)
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
                        node_map = _merge_existing_attribute_mappings(
                            node_map, existing_children, logger=self.log
                        )
                        normalized.append(node_map)
                if normalized:
                    nm_path = ep.NODE_MAPPING_COLLECTION.format(
                        context_mapping_id=context_mapping_id
                    )
                    verb = "PATCH" if any(m.get("contextNodeMappingId") for m in normalized) else "POST"
                    body = {"contextNodeMappings": normalized}
                    # Pre-flight shape check — logs any client-catchable
                    # ``JSON_PARSER_ERROR: Unrecognized field`` or
                    # ``INVALID_DEFINITION: Invalid mapping for given context``
                    # class before we hit the wire. Log-only by design: the
                    # primary builder (``_payload.translate_mapping_rules``)
                    # and the projection helper are the sources of truth; a
                    # flag here means either has drifted from the accept-shape.
                    violations = validate_node_mapping_patch_shape(
                        body, require_node_shell=(verb == "PATCH"),
                    )
                    for v in violations:
                        self.log(
                            f"[shape-check] {verb} node-mappings: {v['path']} — "
                            f"{v['rule']}"
                        )
                    # A shape violation on a PATCH is fatal, not advisory: this is
                    # the whole-body-replace endpoint, so we have *already* folded
                    # the existing sibling attribute-mappings into ``body`` via
                    # ``_merge_existing_attribute_mappings``. Firing a PATCH the
                    # platform rejects (JSON_PARSER_ERROR / INVALID_DEFINITION)
                    # after that merge risks the silent sibling-loss the merge
                    # exists to prevent — so refuse to send it and surface the
                    # drift instead. POST has no siblings to lose and the platform
                    # rejects a bad POST loudly, so those stay log-only.
                    if verb == "PATCH" and violations:
                        summary = "; ".join(
                            f"{v['path']}: {v['rule']}" for v in violations
                        )
                        raise _client.ContextClientError(
                            f"Refusing destructive node-mapping PATCH for "
                            f"mappingId={context_mapping_id}: payload failed the "
                            f"accept-shape pre-flight ({len(violations)} "
                            f"violation(s)). The builder or projection has drifted "
                            f"from the PATCH accept-shape; sending it could silently "
                            f"drop sibling attribute-mappings. Violations: {summary}"
                        )
                    self.log(f"{verb} {len(normalized)} node mapping(s) for "
                             f"mappingId={context_mapping_id}")
                    self.t.request(verb, nm_path, body)
                mapped_ctx_def = mapping.get("mappedContextDefinitionName")
                if mapped_ctx_def:
                    for nm in normalized:
                        nm_id = nm.get("contextNodeMappingId")
                        if nm_id:
                            self._set_mapped_context_definition(nm_id, mapped_ctx_def)
                continue
            remaining.append(mapping)
        if remaining:
            # The remaining branch is a Connect PATCH against
            # context-definitions/{id}/context-mappings — BLOCKED on active
            # (P2 matrix, live-verified 2026-07-04). Guard before mutating.
            self._guard_active_for_patch(
                context_id, detail or {}, "patch context-mappings (metadata)"
            )
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
        """Create ContextAttributeMapping + chained ContextAttrHydrationDetail rows
        for relationship-traversal mapping rules, via SObject REST.

        Idempotency uses two SOQL probes. Unlike the CCI-task original, both are:
          * **node-scoped** — the ContextAttributeMapping probe matches on
            ``ContextInputAttributeName`` *and* ``ContextNodeMappingId``, so a
            same-named attribute on another node/definition can't be mistaken for
            this one and bind hydration to the wrong mapping;
          * **batched** — one ``IN (...)`` query up front instead of one probe per
            rule (the per-rule reads dominated idempotent re-runs);
          * **escaped** — plan-authored ``attr_name`` values go through
            ``_client.soql_literal`` so a stray quote yields a valid literal, not
            malformed SOQL.
        """
        node_mapping_id_index = _index_node_mapping_ids(detail)
        _, attr_index = _payload.collect_context_indexes(detail, {})

        # Resolve each usable rule to its keys once. A rule whose node mapping
        # can't be resolved is misconfigured for this definition (we could
        # neither scope a match nor create the row), so skip it with a log.
        prepared: List[Dict[str, Any]] = []
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
            node_mapping_id = node_mapping_id_index.get((mapping_name, node_name))
            if not node_mapping_id:
                self.log(f"Cannot resolve node mapping for {attr_name} "
                         f"(mapping={mapping_name}, node={node_name}); skipping.")
                continue
            prepared.append({
                "attr_name": attr_name, "node_mapping_id": node_mapping_id,
                "attr_id": attr_index.get((node_name, attr_name)),
                "s_object": s_object, "s_object_field": s_object_field,
                "child_s_object": child_s_object,
                "child_s_object_field": child_s_object_field,
            })
        if not prepared:
            return

        # One batched probe for existing ContextAttributeMapping rows, keyed by
        # (attr_name, node_mapping_id). ORDER BY CreatedDate DESC + setdefault
        # keeps the most-recent row per key (matching the original's existing[0]).
        attr_names = sorted({p["attr_name"] for p in prepared})
        nm_ids = sorted({p["node_mapping_id"] for p in prepared})
        cam_by_key: Dict[tuple, str] = {}
        for row in self.t.soql(
            f"SELECT Id,CreatedDate,ContextInputAttributeName,ContextNodeMappingId "
            f"FROM ContextAttributeMapping "
            f"WHERE ContextInputAttributeName IN ({_soql_in(attr_names)}) "
            f"AND ContextNodeMappingId IN ({_soql_in(nm_ids)}) "
            f"ORDER BY CreatedDate DESC"
        ):
            key = (row.get("ContextInputAttributeName"), row.get("ContextNodeMappingId"))
            if row.get("Id"):
                cam_by_key.setdefault(key, row["Id"])

        # Resolve a keeper ContextAttributeMapping id for each rule, creating the
        # row when absent (creation is per-record; it can't be batched here).
        for p in prepared:
            keeper_id = cam_by_key.get((p["attr_name"], p["node_mapping_id"]))
            if not keeper_id:
                if not p["attr_id"]:
                    self.log(f"Cannot create ContextAttributeMapping for {p['attr_name']}: "
                             f"attr_id unresolved")
                    p["keeper_id"] = None
                    continue
                cam_resp = self.t.sobject(
                    "POST", ep.SOBJECT_CONTEXT_ATTRIBUTE_MAPPING, None,
                    {
                        "ContextNodeMappingId": p["node_mapping_id"],
                        "ContextAttributeId": p["attr_id"],
                        "ContextInputAttributeName": p["attr_name"],
                    },
                )
                keeper_id = None if self.dry_run else _record_id(cam_resp)
                if not keeper_id and not self.dry_run:
                    self.log(f"Failed to create ContextAttributeMapping for {p['attr_name']}")
            p["keeper_id"] = keeper_id

        keeper_ids = sorted({p["keeper_id"] for p in prepared if p.get("keeper_id")})
        if not keeper_ids:
            return

        # One batched probe for existing hydration details across all keepers.
        keepers_with_hydration = {
            row.get("ContextAttributeMappingId")
            for row in self.t.soql(
                f"SELECT Id,ContextAttributeMappingId FROM ContextAttrHydrationDetail "
                f"WHERE ContextAttributeMappingId IN ({_soql_in(keeper_ids)})"
            )
        }

        for p in prepared:
            keeper_id = p.get("keeper_id")
            if not keeper_id:
                continue
            if keeper_id in keepers_with_hydration:
                self.log(f"Traversal hydration already exists for {p['attr_name']}; skipping")
                continue
            self.log(f"Creating traversal hydration for {p['attr_name']}: "
                     f"{p['s_object']}.{p['s_object_field']} -> "
                     f"{p['child_s_object']}.{p['child_s_object_field']}")
            parent_resp = self.t.sobject(
                "POST", ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL, None,
                {"ContextAttributeMappingId": keeper_id, "ObjectName": p["s_object"],
                 "QueryAttribute": p["s_object_field"]},
            )
            if self.dry_run:
                continue
            parent_id = _record_id(parent_resp)
            if not parent_id:
                self.log(f"Failed to get parent hydration detail id for {p['attr_name']}")
                continue
            self.t.sobject(
                "POST", ep.SOBJECT_CONTEXT_ATTR_HYDRATION_DETAIL, None,
                {"ContextAttributeMappingId": keeper_id, "ObjectName": p["child_s_object"],
                 "QueryAttribute": p["child_s_object_field"], "ParentHydrationDetailId": parent_id},
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

    def _guard_active_for_patch(self, context_id: str, detail: Dict[str, Any],
                                op_label: str) -> Dict[str, Any]:
        """Deactivate (or refuse) before a mutation that the platform blocks on
        an active version.

        Applied at exactly the two apply-path hazard surfaces the P2 matrix
        classifies as **BLOCKED on active**:

          * ``_sync_transient`` — SObject REST PATCH ``ContextAttribute.IsTransient``
          * ``_ensure_default_mapping`` / ``_patch_context_mappings`` — Connect
            PATCH ``context-definitions/{id}/context-mappings``

        Other surfaces reached from ``_run_additive_flow`` are safe on active:
        ``_apply_traversal_hydration`` (POST), ``_apply_tags`` (POST),
        ``_set_mapped_context_definition`` (SObject REST PATCH, allowed on
        active), and any POST of a new artifact. ``_apply_mapping_updates``'s
        PATCH branch is a *silently destructive* surface — deactivation does
        NOT fix it; the sibling-merge in ``_merge_existing_attribute_mappings``
        does.

        If already inactive: no-op, returns ``detail`` unchanged.
        If active and ``deactivate_first`` opted in: deactivates, refetches, logs.
        If active and not opted in: raises with an actionable message.
        """
        if not self._is_active(detail):
            return detail
        if not self._deactivate_first:
            raise _client.ContextClientError(
                f"Definition {context_id} is ACTIVE, and '{op_label}' modifies an "
                f"existing artifact — the platform blocks that on an active version "
                f"(\"Cannot modify/delete an active context definition\"). Re-apply "
                f"with deactivate_before=True (CLI: --deactivate-first). Note: "
                f"deactivation is itself blocked while an Expression Set references "
                f"this definition; detach the reference first if that happens."
            )
        self.log(f"Definition {context_id} is active; deactivating before "
                 f"'{op_label}' (deactivate_before=True).")
        self._set_active(context_id, False)
        if self.dry_run:
            return detail
        return self.fetch_detail(context_id)

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
        # Latch for the run so hazard-point guards (_guard_active_for_patch)
        # see the same setting the caller passed.
        self._deactivate_first = bool(deactivate_before)
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
                # SObject PATCH IsTransient is BLOCKED on active (P2 matrix,
                # live-verified 2026-07-04); guard before mutating.
                detail = self._guard_active_for_patch(
                    context_id, detail, "sync IsTransient on ContextAttribute"
                )
                self._sync_transient(transient)
                detail = self.fetch_detail(context_id)

        if translate_plan and plan.get("mappingRules"):
            detail = self._apply_mapping_rules(context_id, developer_name, plan, detail)

        if plan.get("contextMappingUpdates"):
            resolved = _payload.resolve_context_mapping_ids(detail, plan["contextMappingUpdates"])
            self._apply_mapping_updates(context_id, resolved, detail=detail)

        self._apply_tags(context_id, plan, detail)

        result = {"context_id": context_id, "created": False}
        if verify:
            detail = self.fetch_detail(context_id)
            result["verification"] = _payload.plan_verification(detail, plan)
        if activate:
            # Guard against DATA_MAPPING_NOT_FOUND if the def has no default
            # mapping yet (only acts when the plan supplies defaultMapping and
            # none is already flagged).
            pre_active = self.fetch_detail(context_id)
            if plan.get("defaultMapping") and not self._has_default_mapping(pre_active):
                # Connect PATCH context-mappings is BLOCKED on active (P2 matrix);
                # guard before setting isDefault.
                pre_active = self._guard_active_for_patch(
                    context_id, pre_active, "set default context mapping"
                )
            self._ensure_default_mapping(context_id, plan, pre_active)
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
            self._apply_mapping_updates(context_id, resolved, detail=detail)

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
                    self._apply_mapping_updates(context_id, resolved, detail=detail)
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
                self._apply_mapping_updates(context_id, resolved, detail=detail)
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
    """Yield each contextMapping dict on the (single) version.

    ContextDefinitionVersion is a 1:1 singleton with its definition (live-verified
    v67.0: a second version is rejected MAX_LIMIT_EXCEEDED; deactivate/reactivate
    bumps VersionNumber in place), so ``versions[0]`` and the active version are
    always the same record.
    """
    if not isinstance(detail, dict):
        return
    versions = detail.get("contextDefinitionVersionList", [])
    mappings = versions[0].get("contextMappings", []) if versions else []
    for mapping in mappings or []:
        if isinstance(mapping, dict):
            yield mapping


def _index_node_mapping_ids(detail: Dict[str, Any]) -> Dict[tuple, str]:
    """(mapping_name, node_name) -> contextNodeMappingId across all mappings."""
    index: Dict[tuple, str] = {}
    for mapping in _iter_context_mappings(detail):
        m_name = mapping.get("name") or mapping.get("title")
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if not isinstance(node_map, dict):
                continue
            n_name = node_map.get("contextNodeName")
            n_map_id = node_map.get("contextNodeMappingId")
            if m_name and n_name and n_map_id:
                index[(m_name, n_name)] = n_map_id
    return index


def _soql_in(values) -> str:
    """Render an escaped, quoted comma list for a SOQL ``IN (...)`` clause."""
    return ", ".join(f"'{_client.soql_literal(v)}'" for v in values)


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


def _existing_node_mapping_children(
    detail: Optional[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Index existing ``attributeMappings`` rows by ``contextNodeMappingId``.

    Used by ``_apply_mapping_updates`` to re-emit sibling rows on a PATCH so the
    whole-body-replace semantics don't silently delete them (v67.0 hazard,
    live-verified 2026-07-04). If ``detail`` is None/empty the index is empty
    and the merge is a no-op.

    The GET response returns ``attributeMappings`` as a bare list of rows
    (``{contextAttributeName, contextAttributeId, contextAttributeMappingId,
    ...}``). The outgoing PATCH shape wraps that list under
    ``attributeMappings.contextAttributeMappings`` (see
    :func:`_payload.normalize_attribute_mappings`); the merge below handles
    both.
    """
    out: Dict[str, List[Dict[str, Any]]] = {}
    if not isinstance(detail, dict):
        return out
    for mapping in _iter_context_mappings(detail):
        for node_map in mapping.get("contextNodeMappings", []) or []:
            if not isinstance(node_map, dict):
                continue
            nm_id = node_map.get("contextNodeMappingId")
            if not nm_id:
                continue
            attr_maps = node_map.get("attributeMappings")
            if isinstance(attr_maps, dict):
                attr_maps = attr_maps.get("contextAttributeMappings", [])
            if not isinstance(attr_maps, list):
                continue
            out[nm_id] = [a for a in attr_maps if isinstance(a, dict)]
    return out


def _merge_existing_attribute_mappings(
    node_map: Dict[str, Any],
    existing_by_nm_id: Dict[str, List[Dict[str, Any]]],
    *, logger: Callable[..., None] = None,
) -> Dict[str, Any]:
    """Merge omitted sibling attribute mappings back into ``node_map``.

    Rationale (v67.0, live-verified 2026-07-04): the Connect endpoint
    ``PATCH context-mappings/{id}/context-node-mappings`` uses whole-body-replace
    semantics for the ``attributeMappings.contextAttributeMappings`` child
    collection. A row that exists on the org but is absent from the outgoing
    payload is **silently deleted** (response is ``isSuccess:true`` with no
    diagnostic). To keep the PATCH non-destructive we merge sibling rows from
    the current ``detail`` snapshot back onto the payload — matching on
    ``contextAttributeMappingId`` first, then on
    ``(contextAttributeId, contextAttributeName)`` for rows the caller
    re-emitted with fresh keys.

    ``node_map`` is expected in the outgoing (post-``normalize_attribute_mappings``)
    shape — ``{attributeMappings: {contextAttributeMappings: [ ... ]}}``. New
    (POST) node mappings — no ``contextNodeMappingId`` — are returned unchanged.
    Existing (PATCH) node mappings with no entry in the index are also
    unchanged (nothing to merge).
    """
    nm_id = node_map.get("contextNodeMappingId")
    if not nm_id:
        return node_map
    existing = existing_by_nm_id.get(nm_id)
    if not existing:
        return node_map
    outer = node_map.get("attributeMappings")
    inner: List[Dict[str, Any]] = []
    if isinstance(outer, dict):
        raw = outer.get("contextAttributeMappings")
        if isinstance(raw, list):
            inner = [a for a in raw if isinstance(a, dict)]
    elif isinstance(outer, list):
        inner = [a for a in outer if isinstance(a, dict)]
    outgoing_ids = {a.get("contextAttributeMappingId")
                    for a in inner if a.get("contextAttributeMappingId")}
    outgoing_keys = {
        (a.get("contextAttributeId"),
         a.get("contextAttributeName") or a.get("contextInputAttributeName"))
        for a in inner
        if a.get("contextAttributeId")
        or a.get("contextAttributeName")
        or a.get("contextInputAttributeName")
    }
    added = 0
    skipped_inherited = 0
    for sibling in existing:
        sib_id = sibling.get("contextAttributeMappingId")
        sib_key = (
            sibling.get("contextAttributeId"),
            sibling.get("contextAttributeName") or sibling.get("contextInputAttributeName"),
        )
        if sib_id and sib_id in outgoing_ids:
            continue
        if sib_key != (None, None) and sib_key in outgoing_keys:
            continue
        # Skip *inherited* siblings — they belong to the standard base
        # (``baseReference`` points into ``…__stdctx/…``). Re-emitting an
        # inherited mapping on the child definition raises
        # ``INVALID_INPUT: "An Inherited mapping for ContextAttribute X
        # already exists. Create custom mappings for attributes that do not
        # have inherited attribute mappings."`` (live-verified 2026-07-04 on
        # ``rlm-base__july3_noramps`` against ``RLM_SalesTransactionContext``).
        # The base already carries these; nothing to preserve on the child.
        if _is_inherited_row(sibling):
            skipped_inherited += 1
            continue
        # Project to fields the PATCH endpoint accepts. The GET shape carries
        # response-only fields (``baseReference``, ``dataType``, ``sourceObject``,
        # …) that the Connect PATCH rejects with JSON_PARSER_ERROR. Live-verified
        # 2026-07-04 on rlm-base__july3_noramps.
        inner.append(_project_attribute_mapping_for_patch(sibling))
        added += 1
    if logger is not None and (added or skipped_inherited):
        parts = []
        if added:
            parts.append(f"preserving {added} custom sibling(s)")
        if skipped_inherited:
            parts.append(f"skipping {skipped_inherited} inherited sibling(s) "
                         f"(already carried by base)")
        logger(f"Non-destructive PATCH on ContextNodeMapping {nm_id}: "
               + ", ".join(parts) + ".")
    merged = dict(node_map)
    merged["attributeMappings"] = {"contextAttributeMappings": inner}
    return merged


def _is_inherited_row(row: Dict[str, Any]) -> bool:
    """Return True if this attribute-mapping row came from the standard base.

    Inherited attribute mappings carry a ``baseReference`` path pointing into
    ``…__stdctx/…`` (i.e. the standard context base the current definition
    extends). Re-emitting these on the child raises
    ``INVALID_INPUT: "An Inherited mapping for ContextAttribute X already
    exists. Create custom mappings for attributes that do not have inherited
    attribute mappings."`` — live-verified 2026-07-04 on
    ``rlm-base__july3_noramps``.
    """
    if not isinstance(row, dict):
        return False
    ref = row.get("baseReference") or ""
    return isinstance(ref, str) and "__stdctx/" in ref


# Fields the Connect ``context-node-mappings`` PATCH endpoint accepts on each
# child ``contextAttributeMapping``. The GET response carries additional
# response-only fields (``baseReference``, ``contextAttributeName``,
# ``parentNodeMappingId``, ``dataType``, ``sourceObject``, ``mappedContextTag``,
# …) that the same endpoint rejects with ``JSON_PARSER_ERROR: Unrecognized
# field``. Live-verified 2026-07-04 on ``rlm-base__july3_noramps``.
#
# Notably, ``contextAttributeName`` is a response-only mirror of the writable
# ``contextInputAttributeName`` — the primary builder in
# ``_payload.translate_mapping_rules`` only emits the latter. Sending the
# former back gets ``JSON_PARSER_ERROR: Unrecognized field "contextAttributeName"``.
_ATTR_MAPPING_PATCH_FIELDS = frozenset({
    "contextAttributeMappingId",
    "contextAttributeId",
    "contextInputAttributeName",
    "mappedContextAttributeName",
    "mappedContextTagName",
    "isKey",
    "isValue",
    "sequence",
    # NOTE: ``mappedField`` is the SObject REST / ``ATTR_MAPPING_COLLECTION``
    # shape — the Connect ``context-node-mappings`` PATCH endpoint rejects it
    # with ``JSON_PARSER_ERROR: Unrecognized field``. Live-verified 2026-07-04.
    # SObject-domain field mapping on this endpoint goes through
    # ``hydrationDetails.contextAttrHydrationDetails[{sObjectDomain,queryAttribute}]``
    # (see ``_payload.translate_mapping_rules`` at ~L710).
})

# The GET also flattens hydration into two response-side lists — SObject-domain
# hydration under ``contextAttrHydrationDetailList`` and CONTEXT-mapping-source
# hydration under ``contextAttrContextHydrationDetailList``. The PATCH expects
# them nested under ``hydrationDetails`` with only the writable sub-fields per
# entry — the primary builder emits ``sObjectDomain`` + ``queryAttribute`` for
# the sobject side and ``queryAttribute`` + ``parentAttributeMappingId`` for
# the context side (``_payload.translate_mapping_rules``). All other entry
# fields (``baseReference``, ``contextAttrHydrationDetailId``,
# ``mappedAttributeDataTypeInfo``, ``childDetails``, …) are response-only.
_SOBJECT_HYDRATION_ENTRY_FIELDS = frozenset({"sObjectDomain", "queryAttribute"})
_CONTEXT_HYDRATION_ENTRY_FIELDS = frozenset({
    "queryAttribute", "parentAttributeMappingId",
})


def _project_attribute_mapping_for_patch(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of ``row`` restricted to keys the PATCH endpoint accepts.

    Response-only fields on the GET (``baseReference``, ``contextAttributeName``,
    ``parentNodeMappingId``, ``dataType``, ``sourceObject``, …) would raise
    ``JSON_PARSER_ERROR: Unrecognized field`` on the PATCH. Hydration lists on
    the GET are flat top-level fields (``contextAttrHydrationDetailList`` /
    ``contextAttrContextHydrationDetailList``); the PATCH expects them nested
    under ``hydrationDetails.contextAttrHydrationDetails`` /
    ``contextAttrContextHydrationDetails`` with only the writable sub-fields
    per entry — so we re-shape here.
    """
    projected: Dict[str, Any] = {
        k: v for k, v in row.items() if k in _ATTR_MAPPING_PATCH_FIELDS
    }

    sobj_hyd = row.get("contextAttrHydrationDetailList") or []
    ctx_hyd = row.get("contextAttrContextHydrationDetailList") or []

    # Also accept an already-nested ``hydrationDetails`` shape (defensive — we
    # may be re-projecting a row that a previous merge left in the nested
    # form). Merge both sources.
    nested = row.get("hydrationDetails") or {}
    if isinstance(nested, dict):
        sobj_hyd = sobj_hyd + (nested.get("contextAttrHydrationDetails") or [])
        ctx_hyd = ctx_hyd + (nested.get("contextAttrContextHydrationDetails") or [])

    hydration: Dict[str, Any] = {}
    if sobj_hyd:
        hydration["contextAttrHydrationDetails"] = [
            {k: v for k, v in entry.items() if k in _SOBJECT_HYDRATION_ENTRY_FIELDS}
            for entry in sobj_hyd
            if isinstance(entry, dict)
        ]
    if ctx_hyd:
        hydration["contextAttrContextHydrationDetails"] = [
            {k: v for k, v in entry.items() if k in _CONTEXT_HYDRATION_ENTRY_FIELDS}
            for entry in ctx_hyd
            if isinstance(entry, dict)
        ]
    if hydration:
        projected["hydrationDetails"] = hydration

    return projected


# --------------------------------------------------------------------------- #
# Pre-flight shape validator for the Connect node-mapping PATCH
# --------------------------------------------------------------------------- #

# Node-mapping shell fields required by the Connect PATCH ``context-mappings/
# {id}/context-node-mappings`` endpoint. Omitting any raises the generic
# ``INVALID_DEFINITION: "Invalid mapping for given context"`` — which does not
# name the missing field. Detecting client-side saves a round-trip.
_NODE_MAPPING_PATCH_REQUIRED = frozenset({
    "contextNodeId",
    "contextNodeMappingId",
    "sObjectName",
    "mappedContextNodeId",
})

# Response-only fields — if the caller re-emits them the platform raises
# ``JSON_PARSER_ERROR: Unrecognized field "<name>"``. Catch them here first.
_ATTR_MAPPING_RESPONSE_ONLY = frozenset({
    "baseReference", "contextAttributeName", "parentNodeMappingId",
    "dataType", "sourceObject", "mappedContextTag",
    "contextAttrHydrationDetailList",           # flat GET shape
    "contextAttrContextHydrationDetailList",    # flat GET shape
    "mappedField",                              # SObject REST shape
})


def validate_node_mapping_patch_shape(
    payload: Dict[str, Any], *, require_node_shell: bool = True,
) -> List[Dict[str, Any]]:
    """Pre-flight validate a payload destined for
    ``PATCH connect/context-mappings/{id}/context-node-mappings``.

    Returns a list of violations, each as
    ``{"path": <str>, "rule": <str>, "offending": <value>}``. An empty list
    means the shape is likely acceptable to the platform on shape grounds
    (semantic validity — mappings actually existing, no many-to-one, active
    version, etc. — is out of scope for this checker; those errors come back
    from the platform).

    Purpose: catch the common ``JSON_PARSER_ERROR: Unrecognized field`` and
    ``INVALID_DEFINITION: Invalid mapping for given context`` classes before
    the round-trip. These are the two error classes the P2 live-probe
    iteratively surfaced. Live-verified rules per
    ``docs/references/context-service-patch-shapes.md``.

    Rules enforced:
    - Every ``contextNodeMappings`` entry with a ``contextNodeMappingId``
      (PATCH intent) must carry the four required shell fields
      (:data:`_NODE_MAPPING_PATCH_REQUIRED`), unless ``require_node_shell``
      is False.
    - Every ``contextAttributeMappings`` row must not carry any key in
      :data:`_ATTR_MAPPING_RESPONSE_ONLY` (project via
      :func:`_project_attribute_mapping_for_patch` first).
    - Hydration must be nested under ``hydrationDetails`` — flat top-level
      ``contextAttrHydrationDetailList`` / ``contextAttrContextHydrationDetailList``
      on an attribute-mapping row is caught by the response-only rule above.

    Pure function; no network. Safe to call in dry-run / test paths.
    """
    violations: List[Dict[str, Any]] = []

    def flag(path: str, rule: str, offending: Any = None) -> None:
        violations.append({"path": path, "rule": rule, "offending": offending})

    if not isinstance(payload, dict):
        flag("<root>", "payload must be a dict", type(payload).__name__)
        return violations

    node_maps = payload.get("contextNodeMappings")
    if not isinstance(node_maps, list):
        flag("contextNodeMappings", "must be a list", type(node_maps).__name__)
        return violations

    for i, nm in enumerate(node_maps):
        nm_path = f"contextNodeMappings[{i}]"
        if not isinstance(nm, dict):
            flag(nm_path, "must be a dict", type(nm).__name__)
            continue
        nm_id = nm.get("contextNodeMappingId")
        if require_node_shell and nm_id:
            for key in _NODE_MAPPING_PATCH_REQUIRED:
                if not nm.get(key):
                    flag(
                        f"{nm_path}.{key}",
                        "required for PATCH — omitting yields "
                        "INVALID_DEFINITION: 'Invalid mapping for given context'",
                        nm.get(key),
                    )
        attr_maps = nm.get("attributeMappings")
        if isinstance(attr_maps, dict):
            inner = attr_maps.get("contextAttributeMappings")
            inner_path = f"{nm_path}.attributeMappings.contextAttributeMappings"
        elif isinstance(attr_maps, list):
            inner = attr_maps  # backward compat — bare list
            inner_path = f"{nm_path}.attributeMappings"
        else:
            continue
        if not isinstance(inner, list):
            continue
        for j, row in enumerate(inner):
            row_path = f"{inner_path}[{j}]"
            if not isinstance(row, dict):
                flag(row_path, "must be a dict", type(row).__name__)
                continue
            offenders = [k for k in row.keys() if k in _ATTR_MAPPING_RESPONSE_ONLY]
            for offender in offenders:
                flag(
                    f"{row_path}.{offender}",
                    "response-only field — rejected by PATCH with "
                    "JSON_PARSER_ERROR: Unrecognized field. Project via "
                    "_project_attribute_mapping_for_patch first.",
                    row.get(offender),
                )

    return violations
