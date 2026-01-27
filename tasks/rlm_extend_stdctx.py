from abc import abstractmethod
import json
import requests

from cumulusci.core.keychain import BaseProjectKeychain
from cumulusci.tasks.sfdx import SFDXBaseTask


# ExtendStandardContext is a custom task that extends the SFDXBaseTask provided by CumulusCI.
class ExtendStandardContext(SFDXBaseTask):

    # Task options are used to set up configuration settings for this particular task.
    task_options = {
        "access_token": {
            "description": "The access token for the org. Defaults to the project default",
        },
        "name": {
            "description": "The name of the context definition",
            "required": True,
        },
        "description": {
            "description": "The description of the context definition",
            "required": True,
        },
        "developerName": {
            "description": "The developer name of the context definition",
            "required": True,
        },
        "baseReference": {
            "description": "The base reference of the context definition",
            "required": True,
        },
        "startDate": {
            "description": "The start date of the context definition",
            "required": True,
        },
        "contextTtl": {
            "description": "The time-to-live (TTL) of the context definition",
            "required": True, 
        },
        "defaultMapping": {
            "description": "The default mapping of the context definition",
            "required": True,
        },
        "activate": {
            "description": "Whether the context definition should be activated",
            "required": True,
        }
        ,
        "plan_file": {
            "description": "Optional JSON plan with nodes/mappings/tags to apply after creation",
            "required": False,
        }
    }

    # Initialize the task options and environment variables
    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.env = self._get_env()

    # Load keychain with either the current keychain or generate a new one based on environment configuration
    def _load_keychain(self):
        if not hasattr(self, "keychain") or not self.keychain:
            keychain_class = self.get_keychain_class() or BaseProjectKeychain
            keychain_key = self.get_keychain_key() if keychain_class.encrypted else None
            self.keychain = keychain_class(
                self.project_config or self.universal_config, keychain_key
            )
            if self.project_config:
                self.project_config.keychain = self.keychain

    # Prepare runtime by loading keychain and setting up access token and instance URL from options or defaults
    def _prep_runtime(self):
        self._load_keychain()
        self.access_token = self.options.get(
            "access_token", self.org_config.access_token
        )
        self.instance_url = self.options.get(
            "instance_url", self.org_config.instance_url
        )

    # Execute the task after preparation, where the core functionality will be implemented
    def _run_task(self):
        self._prep_runtime()
        self._extend_context_definition()

    # Core logic to extend an existing context definition
    def _extend_context_definition(self):
        url, headers = self._build_url_and_headers("connect/context-definitions")
        payload = {
            "name": self.options.get("name"),
            "description": self.options.get("description"),
            "developerName": self.options.get("developerName"),
            "baseReference": self.options.get("baseReference"),
            "startDate": self.options.get("startDate"),
            "contextTtl": self.options.get("contextTtl")
        }
        response = self._make_request("post", url, headers=headers, json=payload)
        if response:
            self.context_id = response.get("contextDefinitionId")
            if self.context_id:
                self.logger.info(f"Context ID: {self.context_id}")
                self._process_context_id()

    # Post-process after getting the context ID - typically to process the version list
    def _process_context_id(self):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}"
        )
        response = self._make_request("get", url, headers=headers)
        if response:
            version_list = response.get("contextDefinitionVersionList", [])
            if version_list:
                self._process_version_list(version_list)

    # Process the version list obtained from context definitions to obtain context mappings
    def _process_version_list(self, version_list):
        context_mappings = version_list[0].get("contextMappings", [])
        for mapping in context_mappings:
            if mapping.get("name") == self.options.get("defaultMapping"):
                self.default_context_mapping_id = mapping["contextMappingId"]
                self.logger.info(
                    f"{self.options.get('defaultMapping')} Context Mapping ID: {self.default_context_mapping_id}"
                )
                self._update_context_mappings()
                break

    # Update context mappings, typically for marking certain context mappings the default
    def _update_context_mappings(self):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}/context-mappings"
        )
        payload = {
            "contextMappings": [
                {
                    "contextMappingId": self.default_context_mapping_id,
                    "isDefault": "true",
                    "name": self.options.get("defaultMapping"),
                }
            ]
        }
        self._make_request("patch", url, headers=headers, json=payload)
        self._apply_plan_if_present()
        self._activate_context_id()

    def _apply_plan_if_present(self):
        plan_file = self.options.get("plan_file")
        if not plan_file:
            return
        try:
            with open(plan_file, "r", encoding="utf-8") as handle:
                plan = json.load(handle)
        except Exception as exc:
            self.logger.error(f"Failed to load plan_file {plan_file}: {exc}")
            return

        if plan.get("contextNodes"):
            self._post_context_nodes(plan["contextNodes"])
        if plan.get("contextMappings"):
            self._post_context_mappings(plan["contextMappings"])
        if plan.get("contextMappingUpdates"):
            self._patch_context_mappings(plan["contextMappingUpdates"])
        if plan.get("contextTagsByName"):
            resolved = self._resolve_tags_by_name(plan["contextTagsByName"])
            if resolved:
                self._post_context_tags({"contextTags": resolved})
        if plan.get("contextTags"):
            self._post_context_tags(plan["contextTags"])

    def _post_context_nodes(self, payload):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}/context-nodes"
        )
        self._make_request("post", url, headers=headers, json=payload)

    def _post_context_mappings(self, payload):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}/context-mappings"
        )
        self._make_request("post", url, headers=headers, json=payload)

    def _patch_context_mappings(self, payload):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}/context-mappings"
        )
        self._make_request("patch", url, headers=headers, json=payload)

    def _post_context_tags(self, payload):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}/context-tags"
        )
        self._make_request("post", url, headers=headers, json=payload)

    def _resolve_tags_by_name(self, tag_specs):
        if not isinstance(tag_specs, list):
            return []
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}"
        )
        response = self._make_request("get", url, headers=headers)
        if not response:
            return []
        versions = response.get("contextDefinitionVersionList", [])
        if not versions:
            return []
        nodes = versions[0].get("contextNodes", [])

        node_index = {}
        attr_index = {}

        def walk(node_list):
            for node in node_list or []:
                node_id = node.get("contextNodeId")
                node_name = node.get("name")
                if node_id and node_name:
                    node_index[node_name] = node_id
                attrs = node.get("attributes", {}).get("contextAttributes", [])
                for attr in attrs or []:
                    attr_id = attr.get("contextAttributeId")
                    attr_name = attr.get("name")
                    if attr_id and node_name and attr_name:
                        attr_index[(node_name, attr_name)] = attr_id
                child_nodes = node.get("childNodes", {}).get("contextNodes", [])
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
                    continue
                resolved.append({"contextAttributeId": attr_id, "name": tag_name})
            else:
                node_id = node_index.get(node_name)
                if not node_id:
                    continue
                resolved.append({"contextNodeId": node_id, "name": tag_name})
        return resolved

    # Activate the context ID once all changes and updates have been made
    def _activate_context_id(self):
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}"
        )
        payload = {"isActive": "true"}
        self._make_request("patch", url, headers=headers, json=payload)

    # Helper to construct the request URL and headers for making API calls
    def _build_url_and_headers(self, endpoint):
        url = f"{self.instance_url}/services/data/v{self.project_config.project__package__api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return url, headers

    # Make an HTTP request using the requests library and handle the response
    def _make_request(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        if response.ok:
            return response.json()
        else:
            self.logger.error(
                f"Failed {method.upper()} request to {url}: {response.text}"
            )
            return None

    # Abstract method to get the keychain class, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_class(self):
        pass

    # Abstract method to retrieve the keychain key, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_key(self):
        pass

    def get_keychain_key(self):
        pass