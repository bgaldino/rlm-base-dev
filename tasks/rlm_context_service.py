"""
Manage Context Definitions via Context Service (connect) endpoints.

Supports adding context nodes, mappings, and tags to an existing Context Definition.
Payloads are supplied via a JSON plan file to keep the task flexible and
aligned with the Context Service Tooling API contracts.
"""
import json
import os
from abc import abstractmethod
from typing import Any, Dict, Optional

import requests

from cumulusci.core.keychain import BaseProjectKeychain
from cumulusci.tasks.sfdx import SFDXBaseTask
from cumulusci.core.exceptions import TaskOptionsError


class ManageContextDefinition(SFDXBaseTask):
    task_options = {
        "access_token": {
            "description": "The access token for the org. Defaults to the project default",
        },
        "context_definition_id": {
            "description": "ContextDefinitionId to modify.",
            "required": False,
        },
        "developer_name": {
            "description": "DeveloperName of the context definition (used to lookup context_definition_id).",
            "required": False,
        },
        "plan_file": {
            "description": "Path to JSON plan with context-nodes/mappings/tags payloads.",
            "required": True,
        },
        "activate": {
            "description": "If true, activate the context definition after updates.",
            "required": False,
        },
        "dry_run": {
            "description": "If true, only logs intended API calls.",
            "required": False,
        },
        "deactivate_before": {
            "description": "If true, deactivate context definition before updates.",
            "required": False,
        },
        "validate_only": {
            "description": "If true, only validates the plan against the context definition.",
            "required": False,
        },
        "translate_plan": {
            "description": "If true, translate mappingRules into contextMappingUpdates.",
            "required": False,
        },
        "verify": {
            "description": "If true, log verification details after updates.",
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.env = self._get_env()

    def _load_keychain(self):
        if not hasattr(self, "keychain") or not self.keychain:
            keychain_class = self.get_keychain_class() or BaseProjectKeychain
            keychain_key = self.get_keychain_key() if keychain_class.encrypted else None
            self.keychain = keychain_class(
                self.project_config or self.universal_config, keychain_key
            )
            if self.project_config:
                self.project_config.keychain = self.keychain

    def _prep_runtime(self):
        self._load_keychain()
        self.access_token = self.options.get(
            "access_token", self.org_config.access_token
        )
        self.instance_url = self.options.get(
            "instance_url", self.org_config.instance_url
        )
        self.api_version = self.project_config.project__package__api_version

    def _run_task(self):
        self._prep_runtime()
        plan_file = self.options.get("plan_file")
        if not plan_file or not os.path.isfile(plan_file):
            raise TaskOptionsError(f"plan_file not found: {plan_file}")

        with open(plan_file, "r", encoding="utf-8") as handle:
            plan = json.load(handle)
        if not isinstance(plan, dict):
            raise TaskOptionsError("plan_file must contain a JSON object")

        if isinstance(plan.get("contexts"), list):
            for context_plan in plan["contexts"]:
                if not isinstance(context_plan, dict):
                    raise TaskOptionsError("Each contexts entry must be an object")
                if "planFile" in context_plan:
                    plan_path = os.path.join(os.path.dirname(plan_file), context_plan["planFile"])
                    with open(plan_path, "r", encoding="utf-8") as nested:
                        nested_plan = json.load(nested)
                    if not isinstance(nested_plan, dict):
                        raise TaskOptionsError(f"planFile must contain a JSON object: {plan_path}")
                    merged = {**nested_plan, **context_plan}
                    self._run_plan_for_context(merged)
                else:
                    self._run_plan_for_context(context_plan)
            return

        self._run_plan_for_context(plan)

    def _run_plan_for_context(self, plan: Dict[str, Any]):
        context_id = self.options.get("context_definition_id") or plan.get("contextDefinitionId")
        developer_name = self.options.get("developer_name") or plan.get("developerName")
        if not context_id:
            if not developer_name:
                raise TaskOptionsError("context_definition_id or developer_name is required")
            context_id = self._resolve_context_definition_id(developer_name)
            if not context_id:
                raise TaskOptionsError(f"Unable to resolve context definition for {developer_name}")

        self.logger.info(f"Using ContextDefinitionId: {context_id}")

        dry_run = str(self.options.get("dry_run", "")).lower() in {"1", "true", "yes"}
        validate_only = str(self.options.get("validate_only", "")).lower() in {"1", "true", "yes"}
        translate_plan = str(self.options.get("translate_plan", "true")).lower() in {"1", "true", "yes"}
        activate = str(self.options.get("activate", plan.get("activate", ""))).lower() in {"1", "true", "yes"}
        verify = str(self.options.get("verify", "")).lower() in {"1", "true", "yes"}

        self._validate_plan(context_id, plan)
        if validate_only:
            self.logger.info("Validation only; skipping API updates.")
            return

        deactivate_before = str(self.options.get("deactivate_before", plan.get("deactivateBefore", "false"))).lower() in {"1", "true", "yes"}
        if deactivate_before and self._is_context_active(context_id):
            self._set_context_active(context_id, False, dry_run)

        # Snapshot before changes; re-fetch after mutations for accurate verification.
        detail = self._fetch_context_definition(context_id)
        if plan.get("contextAttributesByName"):
            resolved_attrs = self._resolve_context_attributes_by_name(context_id, plan["contextAttributesByName"])
            if resolved_attrs:
                self._post_context_attributes(context_id, {"contextAttributes": resolved_attrs}, dry_run)
                detail = self._fetch_context_definition(context_id)

        if translate_plan and plan.get("mappingRules"):
            if not isinstance(detail, dict):
                detail = {}
            # Apply SOBJECT mappings first so context-to-context mapping can reference the new ids.
            rules = plan.get("mappingRules") or []
            sobject_rules = []
            context_rules = []
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                if (rule.get("mappingType") or "SOBJECT").upper() == "CONTEXT":
                    context_rules.append(rule)
                else:
                    sobject_rules.append(rule)

            if sobject_rules:
                translated = self._translate_mapping_rules(sobject_rules, detail)
                if translated:
                    resolved_updates = self._resolve_context_mapping_ids(detail, translated)
                    if resolved_updates:
                        self._apply_context_mapping_updates(context_id, resolved_updates, dry_run)
                        detail = self._fetch_context_definition(context_id)

            if context_rules:
                translated = self._translate_mapping_rules(context_rules, detail, developer_name=developer_name)
                if translated:
                    resolved_updates = self._resolve_context_mapping_ids(detail, translated)
                    if resolved_updates:
                        self._apply_context_mapping_updates(context_id, resolved_updates, dry_run)
                        detail = self._fetch_context_definition(context_id)

        if plan.get("contextMappingUpdates"):
            resolved_updates = self._resolve_context_mapping_ids(detail, plan["contextMappingUpdates"])
            if resolved_updates:
                plan["contextMappingUpdates"] = resolved_updates

        if plan.get("contextNodes"):
            self._post_context_nodes(context_id, plan["contextNodes"], dry_run)
        if plan.get("contextMappings"):
            # Only create mappings that do not already exist in the target definition.
            filtered = self._filter_existing_mappings(context_id, plan["contextMappings"])
            if filtered:
                self._post_context_mappings(context_id, filtered, dry_run)
        if plan.get("contextMappingUpdates"):
            self._apply_context_mapping_updates(context_id, plan["contextMappingUpdates"], dry_run)
        if plan.get("contextTagsByName"):
            resolved = self._resolve_tags_by_name(context_id, plan["contextTagsByName"])
            if resolved:
                self._post_context_tags(context_id, {"contextTags": resolved}, dry_run)
        if plan.get("contextTags"):
            self._post_context_tags(context_id, plan["contextTags"], dry_run)

        if verify:
            detail = self._fetch_context_definition(context_id)
            self._log_verification(detail, plan)

        if activate:
            self._activate_context_definition(context_id, dry_run)

    def _build_url_and_headers(self, endpoint: str):
        url = f"{self.instance_url}/services/data/v{self.api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return url, headers

    def _make_request(self, method, url, dry_run=False, **kwargs) -> Optional[Dict[str, Any]]:
        if dry_run:
            self.logger.info(f"[dry-run] {method.upper()} {url} {kwargs.get('json')}")
            return {}
        response = requests.request(method, url, **kwargs)
        if response.ok:
            if response.text:
                return response.json()
            return {}
        self.logger.error(f"Failed {method.upper()} request to {url}: {response.text}")
        return None

    def _resolve_context_definition_id(self, developer_name: str) -> Optional[str]:
        url, headers = self._build_url_and_headers("connect/context-definitions")
        response = self._make_request("get", url, headers=headers)
        if not response:
            return self._resolve_context_definition_id_fallback(developer_name)
        if isinstance(response, list):
            self.logger.warning("Unexpected list response for context definitions; cannot resolve by name.")
            return self._resolve_context_definition_id_fallback(developer_name)
        for item in response.get("contextDefinitionList", []):
            if item.get("developerName") == developer_name:
                return item.get("contextDefinitionId")
        return self._resolve_context_definition_id_fallback(developer_name)

    def _resolve_context_definition_id_fallback(self, developer_name: str) -> Optional[str]:
        url, headers = self._build_url_and_headers(f"connect/context-definitions/{developer_name}")
        response = self._make_request("get", url, headers=headers)
        if isinstance(response, dict):
            return response.get("contextDefinitionId")
        return None

    def _post_context_nodes(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}/context-nodes"
        )
        self._make_request("post", url, headers=headers, json=payload, dry_run=dry_run)

    def _post_context_mappings(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}/context-mappings"
        )
        self._make_request("post", url, headers=headers, json=payload, dry_run=dry_run)

    def _post_context_tags(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}/context-tags"
        )
        self._make_request("post", url, headers=headers, json=payload, dry_run=dry_run)

    def _post_context_attributes(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        if not isinstance(payload, dict):
            return
        attributes = payload.get("contextAttributes") or []
        if not isinstance(attributes, list):
            return

        by_node = {}
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
            url, headers = self._build_url_and_headers(
                f"connect/context-nodes/{node_id}/context-attributes"
            )
            self._make_request(
                "post",
                url,
                headers=headers,
                json={"contextAttributes": attrs},
                dry_run=dry_run,
            )

    def _patch_context_mappings(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}/context-mappings"
        )
        def strip_none(value):
            if isinstance(value, dict):
                cleaned = {k: strip_none(v) for k, v in value.items() if v is not None}
                return {k: v for k, v in cleaned.items() if v is not None}
            if isinstance(value, list):
                return [strip_none(v) for v in value if v is not None]
            return value

        if isinstance(payload, dict) and isinstance(payload.get("contextMappings"), list):
            for mapping in payload["contextMappings"]:
                if not isinstance(mapping, dict):
                    continue
                mapping.pop("name", None)
                self._make_request(
                    "patch",
                    url,
                    headers=headers,
                    json={"contextMappings": [strip_none(mapping)]},
                    dry_run=dry_run,
                )
            return
        if isinstance(payload, dict):
            payload.pop("name", None)
        self._make_request(
            "patch",
            url,
            headers=headers,
            json={"contextMappings": [strip_none(payload)]},
            dry_run=dry_run,
        )

    def _post_context_node_mappings(self, context_mapping_id: str, node_mappings: list, dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-mappings/{context_mapping_id}/context-node-mappings"
        )
        self.logger.info(
            "Posting %s context node mapping(s) to %s",
            len(node_mappings),
            context_mapping_id,
        )
        self._make_request(
            "post",
            url,
            headers=headers,
            json={"contextNodeMappings": node_mappings},
            dry_run=dry_run,
        )

    def _patch_context_node_mappings(self, context_mapping_id: str, node_mappings: list, dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-mappings/{context_mapping_id}/context-node-mappings"
        )
        self.logger.info(
            "Patching %s context node mapping(s) to %s",
            len(node_mappings),
            context_mapping_id,
        )
        self._make_request(
            "patch",
            url,
            headers=headers,
            json={"contextNodeMappings": node_mappings},
            dry_run=dry_run,
        )

    def _normalize_attribute_mappings(self, node_map: Dict[str, Any]):
        if not isinstance(node_map, dict):
            return node_map
        attribute_mappings = node_map.get("attributeMappings")
        if isinstance(attribute_mappings, list):
            node_map = {**node_map, "attributeMappings": {"contextAttributeMappings": attribute_mappings}}
        return node_map

    def _apply_context_mapping_updates(self, context_id: str, payload: Dict[str, Any], dry_run: bool):
        if not isinstance(payload, dict):
            return
        mappings = payload.get("contextMappings")
        if not isinstance(mappings, list):
            return

        # Split mapping updates: node mappings handled via context-node-mappings endpoint.
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
                    node_map = self._normalize_attribute_mappings(node_map)
                    if not isinstance(node_map, dict):
                        continue
                    normalized.append(node_map)
                if normalized:
                    self.logger.info(
                        "Applying %s node mapping(s) for mappingId=%s",
                        len(normalized),
                        context_mapping_id,
                    )
                    # POST if no ids; PATCH if ids provided.
                    if any(m.get("contextNodeMappingId") for m in normalized):
                        self._patch_context_node_mappings(context_mapping_id, normalized, dry_run)
                    else:
                        self._post_context_node_mappings(context_mapping_id, normalized, dry_run)
                # If the mapping carries mappedContextDefinitionName (CONTEXT-type mapping
                # source), set it via the ContextNodeMapping sObject REST API. The Connect
                # API context-mappings PATCH silently ignores this field.
                mapped_ctx_def = mapping.get("mappedContextDefinitionName")
                if mapped_ctx_def:
                    for nm in normalized:
                        node_mapping_id = nm.get("contextNodeMappingId")
                        if node_mapping_id:
                            self._set_mapped_context_definition(node_mapping_id, mapped_ctx_def, dry_run)
                continue
            remaining.append(mapping)

        if remaining:
            self._patch_context_mappings(context_id, {"contextMappings": remaining}, dry_run)

    def _resolve_context_mapping_ids(self, detail: Dict[str, Any], payload: Dict[str, Any]):
        if not isinstance(payload, dict):
            return payload
        mappings = payload.get("contextMappings")
        if not isinstance(mappings, list):
            return payload
        if not isinstance(detail, dict):
            return payload
        versions = detail.get("contextDefinitionVersionList", [])
        mapping_list = versions[0].get("contextMappings", []) if versions else []
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

    def _fetch_context_definition(self, context_id: str) -> Dict[str, Any]:
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}"
        )
        response = self._make_request("get", url, headers=headers)
        if isinstance(response, list):
            if len(response) == 1 and isinstance(response[0], dict):
                return response[0]
            self.logger.warning("Unexpected list response for context definition; skipping validation.")
            return {}
        return response or {}

    def _set_mapped_context_definition(self, node_mapping_id: str, developer_name: str, dry_run: bool = False):
        """Set MappedContextDefinition on a ContextNodeMapping sObject record.

        The Connect API context-mappings PATCH silently ignores mappedContextDefinitionName,
        so we update the sObject directly via the REST API.
        """
        url, headers = self._build_url_and_headers(
            f"sobjects/ContextNodeMapping/{node_mapping_id}"
        )
        payload = {"MappedContextDefinition": developer_name}
        self.logger.info(
            "Setting MappedContextDefinition=%s on ContextNodeMapping %s",
            developer_name,
            node_mapping_id,
        )
        self._make_request("patch", url, headers=headers, json=payload, dry_run=dry_run)

    def _is_context_active(self, context_id: str) -> bool:
        detail = self._fetch_context_definition(context_id)
        if not isinstance(detail, dict):
            return False
        if detail.get("isActive") is not None or detail.get("active") is not None:
            return bool(detail.get("isActive") or detail.get("active"))
        versions = detail.get("contextDefinitionVersionList", [])
        if versions and isinstance(versions[0], dict):
            return bool(versions[0].get("isActive"))
        return False

    def _set_context_active(self, context_id: str, is_active: bool, dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}"
        )
        payload = {"isActive": "true" if is_active else "false"}
        self._make_request("patch", url, headers=headers, json=payload, dry_run=dry_run)

    def _collect_context_indexes(self, detail: Dict[str, Any], plan: Dict[str, Any]):
        if not isinstance(detail, dict):
            return {}, {}
        versions = detail.get("contextDefinitionVersionList", [])
        mappings = versions[0].get("contextMappings", []) if versions else []

        node_index = {}
        attr_index = {}

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

        context_nodes = versions[0].get("contextNodes", []) if versions else []

        def walk(nodes):
            for node in nodes or []:
                if not isinstance(node, dict):
                    continue
                node_id = node.get("contextNodeId")
                node_name = node.get("name")
                if node_name and node_id:
                    node_index.setdefault(node_name, node_id)
                attrs_container = node.get("attributes", {})
                if isinstance(attrs_container, list):
                    attrs = attrs_container
                else:
                    if not isinstance(attrs_container, dict):
                        attrs_container = {}
                    attrs = attrs_container.get("contextAttributes", [])
                for attr in attrs or []:
                    if not isinstance(attr, dict):
                        continue
                    attr_name = attr.get("name")
                    attr_id = attr.get("contextAttributeId")
                    if node_name and attr_name and attr_id:
                        attr_index.setdefault((node_name, attr_name), attr_id)
                child_nodes_container = node.get("childNodes", {})
                if isinstance(child_nodes_container, list):
                    child_nodes = child_nodes_container
                else:
                    if not isinstance(child_nodes_container, dict):
                        child_nodes_container = {}
                    child_nodes = child_nodes_container.get("contextNodes", [])
                walk(child_nodes)

        walk(context_nodes)

        # Include attributes from plan contextNodes so validation passes for newly added attributes.
        plan_nodes = plan.get("contextNodes")
        if isinstance(plan_nodes, dict):
            plan_nodes_list = plan_nodes.get("contextNodes", [])
        else:
            plan_nodes_list = []
        for node in plan_nodes_list:
            node_name = node.get("name")
            if node_name:
                node_index.setdefault(node_name, None)
            attrs_container = node.get("attributes", {})
            if isinstance(attrs_container, list):
                attrs = attrs_container
            else:
                if not isinstance(attrs_container, dict):
                    attrs_container = {}
                attrs = attrs_container.get("contextAttributes", [])
            for attr in attrs:
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

    def _validate_plan(self, context_id: str, plan: Dict[str, Any]):
        try:
            detail = self._fetch_context_definition(context_id)
            if not isinstance(detail, dict):
                self.logger.warning("Unexpected context definition response; skipping node/attribute validation.")
                detail = {}
            node_index, attr_index = self._collect_context_indexes(detail, plan)

            def check_mapping(mapping_name, node_name, attr_name):
                if node_name not in node_index:
                    self.logger.warning(f"[plan] Mapping {mapping_name}: node '{node_name}' not found.")
                if attr_name and (node_name, attr_name) not in attr_index:
                    self.logger.warning(
                        f"[plan] Mapping {mapping_name}: attribute '{node_name}.{attr_name}' not found."
                    )

            mapping_updates = plan.get("contextMappingUpdates", {})
            if isinstance(mapping_updates, dict):
                mapping_updates_list = mapping_updates.get("contextMappings", [])
            else:
                self.logger.warning("contextMappingUpdates must be an object; skipping mapping validation.")
                mapping_updates_list = []
            for mapping in mapping_updates_list:
                if not isinstance(mapping, dict):
                    continue
                mapping_name = mapping.get("name") or "<unnamed>"
                node_maps = mapping.get("contextNodeMappings", {})
                if isinstance(node_maps, dict):
                    node_maps = node_maps.get("contextNodeMappings", [])
                for node_map in node_maps or []:
                    if not isinstance(node_map, dict):
                        continue
                    node_name = node_map.get("contextNode")
                    attr_maps = node_map.get("contextAttributeMappings", [])
                    if isinstance(attr_maps, dict):
                        attr_maps = attr_maps.get("contextAttributeMappings", [])
                    for attr_map in attr_maps or []:
                        if not isinstance(attr_map, dict):
                            continue
                        attr_name = attr_map.get("contextAttribute")
                        check_mapping(mapping_name, node_name, attr_name)

            for rule in plan.get("mappingRules", []):
                mapping_name = rule.get("mappingName") or "<unnamed>"
                node_name = rule.get("contextNode")
                attr_name = rule.get("contextAttribute")
                check_mapping(mapping_name, node_name, attr_name)
        except Exception as exc:
            self.logger.error(
                "Plan validation failed: %s (plan=%s, context=%s, updates=%s)",
                exc,
                type(plan).__name__,
                type(detail).__name__ if 'detail' in locals() else "n/a",
                type(plan.get("contextMappingUpdates")).__name__ if isinstance(plan, dict) else "n/a",
            )
            raise

    def _resolve_tags_by_name(self, context_id: str, tag_specs: Any):
        if not isinstance(tag_specs, list):
            raise TaskOptionsError("contextTagsByName must be a list")
        detail = self._fetch_context_definition(context_id)
        versions = detail.get("contextDefinitionVersionList", [])
        if not versions:
            self.logger.warning("No contextDefinitionVersionList found; cannot resolve tags by name.")
            return []
        nodes = versions[0].get("contextNodes", [])

        node_index = {}
        attr_index = {}
        node_tag_index = {}
        attr_tag_index = {}

        def walk(node_list):
            for node in node_list or []:
                if not isinstance(node, dict):
                    continue
                node_id = node.get("contextNodeId")
                node_name = node.get("name")
                if node_id and node_name:
                    node_index[node_name] = node_id
                attrs_container = node.get("attributes", {})
                if isinstance(attrs_container, list):
                    attrs = attrs_container
                else:
                    if not isinstance(attrs_container, dict):
                        attrs_container = {}
                    attrs = attrs_container.get("contextAttributes", [])
                for attr in attrs or []:
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
                child_nodes_container = node.get("childNodes", {})
                if isinstance(child_nodes_container, list):
                    child_nodes = child_nodes_container
                else:
                    if not isinstance(child_nodes_container, dict):
                        child_nodes_container = {}
                    child_nodes = child_nodes_container.get("contextNodes", [])
                walk(child_nodes)

        walk(nodes)

        resolved = []
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
                    self.logger.warning(f"Attribute tag not resolved: {node_name}.{attr_name}")
                    continue
                existing = attr_tag_index.get((node_name, attr_name), set())
                if tag_name in existing:
                    continue
                resolved.append({"contextAttributeId": attr_id, "name": tag_name})
            else:
                node_id = node_index.get(node_name)
                if not node_id:
                    self.logger.warning(f"Node tag not resolved: {node_name}")
                    continue
                existing = node_tag_index.get(node_name, set())
                if tag_name in existing:
                    continue
                resolved.append({"contextNodeId": node_id, "name": tag_name})
        return resolved

    def _resolve_context_attributes_by_name(self, context_id: str, attr_specs: Any):
        if not isinstance(attr_specs, list):
            raise TaskOptionsError("contextAttributesByName must be a list")
        detail = self._fetch_context_definition(context_id)
        versions = detail.get("contextDefinitionVersionList", []) if isinstance(detail, dict) else []
        nodes = versions[0].get("contextNodes", []) if versions else []

        node_index = {}
        attr_index = {}

        def walk_nodes(node_list):
            for node in node_list or []:
                if not isinstance(node, dict):
                    continue
                node_id = node.get("contextNodeId")
                node_name = node.get("name")
                if node_name and node_id:
                    node_index[node_name] = node_id
                attrs_container = node.get("attributes", {})
                if isinstance(attrs_container, list):
                    attrs = attrs_container
                else:
                    if not isinstance(attrs_container, dict):
                        attrs_container = {}
                    attrs = attrs_container.get("contextAttributes", [])
                for attr in attrs or []:
                    if not isinstance(attr, dict):
                        continue
                    attr_name = attr.get("name")
                    attr_id = attr.get("contextAttributeId")
                    if node_name and attr_name and attr_id:
                        attr_index[(node_name, attr_name)] = attr_id
                child_nodes_container = node.get("childNodes", {})
                if isinstance(child_nodes_container, list):
                    child_nodes = child_nodes_container
                else:
                    if not isinstance(child_nodes_container, dict):
                        child_nodes_container = {}
                    child_nodes = child_nodes_container.get("contextNodes", [])
                walk_nodes(child_nodes)

        walk_nodes(nodes)

        resolved = []
        for spec in attr_specs:
            if not isinstance(spec, dict):
                continue
            node_name = spec.get("nodeName")
            if not node_name or node_name not in node_index:
                self.logger.warning(f"Context node not resolved for attribute add: {node_name}")
                continue
            attr_name = spec.get("name")
            if attr_name and (node_name, attr_name) in attr_index:
                continue
            resolved.append(
                {
                    "contextNodeId": node_index[node_name],
                    "name": attr_name,
                    "dataType": spec.get("dataType", "STRING"),
                    "fieldType": spec.get("fieldType", "INPUTOUTPUT"),
                }
            )
        return resolved

    def _translate_mapping_rules(self, mapping_rules, detail, developer_name=None):
        if not isinstance(mapping_rules, list):
            raise TaskOptionsError("mappingRules must be a list")

        if not isinstance(detail, dict):
            return None

        mapping_index = {}
        for mapping in detail.get("contextDefinitionVersionList", [])[0].get("contextMappings", []):
            if isinstance(mapping, dict) and mapping.get("name"):
                mapping_index[mapping["name"]] = mapping

        node_index, attr_index = self._collect_context_indexes(detail, {})

        def find_attr_mapping_id(node_name, attr_name):
            for mapping in detail.get("contextDefinitionVersionList", [])[0].get("contextMappings", []):
                if not isinstance(mapping, dict):
                    continue
                for node_map in mapping.get("contextNodeMappings", []) or []:
                    if node_map.get("contextNodeName") != node_name:
                        continue
                    for attr_map in node_map.get("attributeMappings", []) or []:
                        if attr_map.get("contextAttributeName") == attr_name:
                            return attr_map.get("contextAttributeMappingId")
            return None

        updates = []
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
                self.logger.warning(f"Mapping not found for rule: {mapping_name}")
                continue
            mapping_id = mapping_meta.get("contextMappingId")
            if not mapping_id:
                self.logger.warning(f"Mapping id not found for rule: {mapping_name}")
                continue

            node_map_meta = None
            for existing in mapping_meta.get("contextNodeMappings", []) or []:
                if existing.get("contextNodeName") == node_name:
                    node_map_meta = existing
                    break

            node_id = (node_map_meta or {}).get("contextNodeId") or node_index.get(node_name)
            if not node_id:
                self.logger.warning(f"Context node id not found for rule: {mapping_name} -> {node_name}")
                continue

            attr_id = attr_index.get((node_name, attr_name))
            if not attr_id:
                self.logger.warning(
                    f"Context attribute id not found for rule: {mapping_name} -> {node_name}.{attr_name}"
                )
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
                self.logger.info(
                    f"Skipping TransactionType mapping update for {mapping_name} -> {node_name}"
                )
                continue
            if mapping_type == "CONTEXT":
                # Even if the attribute mapping exists, we may still need to set
                # mappedContextDefinitionName on the mapping (Mapping Source = Context Definition).
                existing_mapped_ctx = mapping_meta.get("mappedContextDefinitionId") or mapping_meta.get("mappedContextDefinitionName")
                needs_ctx_def_update = not existing_mapped_ctx
                if attr_mapping_id and (requested_input is None or requested_input == existing_input_name) and not needs_ctx_def_update:
                    self.logger.info(
                        f"Skipping existing attribute mapping for {mapping_name} -> {node_name}.{attr_name}"
                    )
                    continue
                if attr_mapping_id and (requested_input is None or requested_input == existing_input_name) and needs_ctx_def_update:
                    # Attribute mapping exists but MappedContextDefinition is not set on the
                    # ContextNodeMapping sObject. Set it directly via the sObject REST API
                    # (the Connect API context-mappings PATCH silently ignores this field).
                    mapped_ctx_def_name = developer_name or detail.get("developerName") or detail.get("contextDefinitionId")
                    node_mapping_id = (node_map_meta or {}).get("contextNodeMappingId")
                    if mapped_ctx_def_name and node_mapping_id:
                        self.logger.info(
                            f"Attribute mapping exists for {mapping_name} -> {node_name}.{attr_name} "
                            f"but MappedContextDefinition is not set; updating via sObject API."
                        )
                        self._set_mapped_context_definition(node_mapping_id, mapped_ctx_def_name, dry_run=False)
                    continue
                if attr_mapping_id and requested_input and requested_input != existing_input_name:
                    self.logger.warning(
                        f"Existing attribute mapping differs for {mapping_name} -> {node_name}.{attr_name}; skipping update."
                    )
                    continue
            else:
                # For SOBJECT mappings, allow updates to align with desired hydration details.
                if attr_mapping_id and requested_input == existing_input_name:
                    self.logger.info(
                        f"Updating existing attribute mapping for {mapping_name} -> {node_name}.{attr_name}"
                    )
            # For SOBJECT mappings, contextInputAttributeName should remain the context attribute name.
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
                    self.logger.warning(
                        f"Context source not resolved for rule: {mapping_name} -> {source_node}.{source_attr}"
                    )
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
                    context_attribute_mapping["hydrationDetails"] = {
                        "contextAttrHydrationDetails": [
                            {
                                "sObjectDomain": rule.get("sObject"),
                                "queryAttribute": rule.get("sObjectField"),
                            }
                        ]
                    }
            if attr_mapping_id:
                context_attribute_mapping["contextAttributeMappingId"] = attr_mapping_id

            updates.append(
                {
                    "contextMappingId": mapping_id,
                    "contextNodeMappings": {
                        "contextNodeMappings": [
                            {
                                "contextNodeId": node_id,
                                "contextNodeMappingId": (node_map_meta or {}).get("contextNodeMappingId"),
                                "sObjectName": rule.get("sObject"),
                                "mappedContextNodeId": mapped_context_node_id,
                                "attributeMappings": {
                                    "contextAttributeMappings": [
                                        context_attribute_mapping
                                    ]
                                },
                            }
                        ]
                    },
                    "mappedContextDefinitionName": mapped_context_definition,
                }
            )

        if not updates:
            return None
        return {"contextMappings": updates}

    def _filter_existing_mappings(self, context_id: str, payload: Dict[str, Any]):
        detail = self._fetch_context_definition(context_id)
        if not isinstance(detail, dict):
            return payload
        existing = {
            mapping.get("name")
            for mapping in detail.get("contextDefinitionVersionList", [])[0].get("contextMappings", [])
            if isinstance(mapping, dict)
        }
        if not isinstance(payload, dict):
            return payload
        mappings = payload.get("contextMappings")
        if not isinstance(mappings, list):
            return payload
        filtered = [m for m in mappings if isinstance(m, dict) and m.get("name") not in existing]
        if not filtered:
            return None
        return {**payload, "contextMappings": filtered}

    def _log_verification(self, detail: Dict[str, Any], plan: Dict[str, Any]):
        if not isinstance(detail, dict):
            self.logger.warning("Verification skipped: context definition response not a dict.")
            return
        versions = detail.get("contextDefinitionVersionList", [])
        if not versions or not isinstance(versions[0], dict):
            self.logger.warning("Verification skipped: missing contextDefinitionVersionList.")
            return

        mapping_rules = plan.get("mappingRules", []) or []
        rule_keys = {(r.get("mappingName"), r.get("contextNode"), r.get("contextAttribute")) for r in mapping_rules if isinstance(r, dict)}
        tags_by_name = plan.get("contextTagsByName", []) or []
        attrs_by_name = plan.get("contextAttributesByName", []) or []

        matched_rules = []
        missing_rules = []
        for mapping in versions[0].get("contextMappings", []):
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
                        matched_rules.append(
                            {
                                "mapping": mapping_name,
                                "node": node_name,
                                "sObject": sobject,
                                "contextAttribute": attr_name,
                                "contextInputAttribute": attr.get("contextInputAttributeName"),
                                "hasHydrationDetail": bool(attr.get("contextAttrHydrationDetailList")),
                            }
                        )
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
                attrs_container = node.get("attributes", {})
                if isinstance(attrs_container, list):
                    attrs = attrs_container
                else:
                    if not isinstance(attrs_container, dict):
                        attrs_container = {}
                    attrs = attrs_container.get("contextAttributes", [])
                for attr in attrs or []:
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
                child_nodes_container = node.get("childNodes", {})
                if isinstance(child_nodes_container, list):
                    child_nodes = child_nodes_container
                else:
                    if not isinstance(child_nodes_container, dict):
                        child_nodes_container = {}
                    child_nodes = child_nodes_container.get("contextNodes", [])
                walk(child_nodes)

        walk(versions[0].get("contextNodes", []))

        if matched_rules:
            self.logger.info("Verification: mapping rules applied:")
            for item in matched_rules:
                self.logger.info(json.dumps(item))
                if item.get("sObject") and not item.get("hasHydrationDetail"):
                    self.logger.warning(
                        "Verification: missing hydration detail for %s.%s in %s (sObject=%s)",
                        item.get("node"),
                        item.get("contextAttribute"),
                        item.get("mapping"),
                        item.get("sObject"),
                    )
        if missing_rules:
            self.logger.warning("Verification: mapping rules missing:")
            for key in missing_rules:
                self.logger.warning(json.dumps({"mapping": key[0], "node": key[1], "contextAttribute": key[2]}))
        if found_attrs:
            self.logger.info("Verification: attributes present: %s", ", ".join(sorted(set(found_attrs))))
        if found_tags:
            self.logger.info("Verification: tags present: %s", ", ".join(sorted(set(found_tags))))

    def _activate_context_definition(self, context_id: str, dry_run: bool):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{context_id}"
        )
        payload = {"isActive": "true"}
        self._make_request("patch", url, headers=headers, json=payload, dry_run=dry_run)

    @abstractmethod
    def get_keychain_class(self):
        pass

    @abstractmethod
    def get_keychain_key(self):
        pass

