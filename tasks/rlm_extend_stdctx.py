from abc import abstractmethod
import json
import time
import requests
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError

from cumulusci.core.keychain import BaseProjectKeychain
from cumulusci.tasks.sfdx import SFDXBaseTask

# Network resilience settings for long-running Salesforce APIs
_CONNECT_TIMEOUT = 30       # seconds to establish TCP connection
_READ_TIMEOUT = 600         # seconds to wait for response (context APIs can take 5-10 min)
_MAX_RETRIES = 3            # total attempts on transient failures
_RETRY_BACKOFF = 30         # seconds between retries (doubles each attempt)


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
        developer_name = self.options.get("developerName")
        self.logger.info(f"[1/4] Creating context definition: {developer_name}...")
        self.logger.info("      (this API call may take up to 5 minutes on some org types — please wait)")
        url, headers = self._build_url_and_headers("connect/context-definitions")
        payload = {
            "name": self.options.get("name"),
            "description": self.options.get("description"),
            "developerName": developer_name,
            "baseReference": self.options.get("baseReference"),
            "startDate": self.options.get("startDate"),
            "contextTtl": self.options.get("contextTtl")
        }
        # POST is NOT idempotent — default retryable=None means no retry for POST.
        # If the network drops after the server processes the request, we recover
        # the context definition ID by querying the org (see _recover_context_id).
        response = self._make_request("post", url, headers=headers, json=payload)
        if response is not None:
            self.context_id = response.get("contextDefinitionId")
        # Recover by querying the org if we didn't get a context ID — covers both
        # network failures (response is None) and empty/unexpected response bodies.
        if not self.context_id:
            self.logger.warning(
                f"      contextDefinitionId not in response — attempting to recover by developerName..."
            )
            self.context_id = self._recover_context_id(developer_name)
        if self.context_id:
            self.logger.info(f"      Context Definition ID: {self.context_id}")
            self._process_context_id()
        else:
            self.logger.error(
                f"      Could not obtain context definition ID for '{developer_name}'. "
                f"The creation may have failed — check the org manually."
            )

    def _recover_context_id(self, developer_name):
        """Query the org for an existing context definition by developerName."""
        self.logger.info(f"      Querying for existing context definition '{developer_name}'...")
        # Wait briefly for server-side commit to propagate
        time.sleep(10)
        # Use the direct lookup endpoint (avoids paging the full list)
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{developer_name}"
        )
        for attempt in range(1, _MAX_RETRIES + 1):
            response = self._make_request("get", url, headers=headers)
            if response is not None:
                # The API returns isSuccess:false for unknown definitions
                if response.get("isSuccess") is not False:
                    ctx_id = response.get("contextDefinitionId")
                    if ctx_id:
                        self.logger.info(f"      Recovered context definition from org.")
                        return ctx_id
            if attempt < _MAX_RETRIES:
                wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                self.logger.warning(
                    f"      Context definition not found yet (attempt {attempt}/{_MAX_RETRIES}). "
                    f"Waiting {wait}s for server-side commit..."
                )
                time.sleep(wait)
        return None

    # Post-process after getting the context ID - typically to process the version list
    def _process_context_id(self):
        self.logger.info(f"[2/4] Fetching version list for context definition {self.context_id}...")
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{self.context_id}"
        )
        response = self._make_request("get", url, headers=headers)
        if response is not None:
            version_list = response.get("contextDefinitionVersionList", [])
            self.logger.info(f"      Found {len(version_list)} version(s)")
            if version_list:
                self._process_version_list(version_list)

    # Process the version list obtained from context definitions to obtain context mappings
    def _process_version_list(self, version_list):
        context_mappings = version_list[0].get("contextMappings", [])
        default_mapping = self.options.get("defaultMapping")
        self.logger.info(f"[3/4] Locating default mapping '{default_mapping}' among {len(context_mappings)} mapping(s)...")
        for mapping in context_mappings:
            if mapping.get("name") == default_mapping:
                self.default_context_mapping_id = mapping["contextMappingId"]
                self.logger.info(
                    f"      Context Mapping ID: {self.default_context_mapping_id}"
                )
                self._update_context_mappings()
                break

    # Update context mappings, typically for marking certain context mappings the default
    def _update_context_mappings(self):
        self.logger.info(f"      Setting '{self.options.get('defaultMapping')}' as the default context mapping...")
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
        self.logger.info(f"      Applying plan file: {plan_file}")
        try:
            with open(plan_file, "r", encoding="utf-8") as handle:
                plan = json.load(handle)
        except Exception as exc:
            self.logger.error(f"Failed to load plan_file {plan_file}: {exc}")
            return

        if plan.get("contextNodes"):
            self.logger.info(f"      → Posting {len(plan['contextNodes'])} context node(s)...")
            self._post_context_nodes(plan["contextNodes"])
        if plan.get("contextMappings"):
            self.logger.info(f"      → Posting {len(plan['contextMappings'])} context mapping(s)...")
            self._post_context_mappings(plan["contextMappings"])
        if plan.get("contextMappingUpdates"):
            self.logger.info(f"      → Patching {len(plan['contextMappingUpdates'])} context mapping update(s)...")
            self._patch_context_mappings(plan["contextMappingUpdates"])
        if plan.get("contextTagsByName"):
            self.logger.info(f"      → Resolving {len(plan['contextTagsByName'])} tag(s) by name...")
            resolved = self._resolve_tags_by_name(plan["contextTagsByName"])
            if resolved:
                self.logger.info(f"      → Posting {len(resolved)} resolved context tag(s)...")
                self._post_context_tags({"contextTags": resolved})
        if plan.get("contextTags"):
            self.logger.info(f"      → Posting {len(plan['contextTags'])} context tag(s)...")
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
        if response is None:
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

    # Make an HTTP request with optional retry logic for transient network failures.
    # Context definition APIs can take 5-10 minutes; intermediate network
    # devices (NAT gateways, load balancers) may drop idle TCP connections.
    #
    # retryable: controls retry behavior on network errors and 5xx responses.
    #   None (default) = auto: retry GET/PATCH (idempotent), don't retry POST
    #   True  = force retry regardless of method
    #   False = never retry
    def _make_request(self, method, url, retryable=None, **kwargs):
        kwargs.setdefault("timeout", (_CONNECT_TIMEOUT, _READ_TIMEOUT))
        if retryable is None:
            retryable = method.lower() in ("get", "patch", "put", "delete", "head", "options")
        max_attempts = _MAX_RETRIES if retryable else 1
        last_exc = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.request(method, url, **kwargs)
                if response.ok:
                    if response.status_code == 204 or not response.text:
                        return {}
                    return response.json()
                # 5xx = server-side transient; retry if allowed.
                if response.status_code >= 500 and attempt < max_attempts:
                    wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"      Received {response.status_code} on attempt {attempt}/{max_attempts}. "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)
                    continue
                self.logger.error(
                    f"Failed {method.upper()} request to {url}: {response.text}"
                )
                return None
            except (ConnectionError, Timeout, ChunkedEncodingError, OSError) as exc:
                last_exc = exc
                if attempt < max_attempts:
                    wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"      Network error on attempt {attempt}/{max_attempts}: {exc}. "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)
                else:
                    self.logger.error(
                        f"Failed {method.upper()} request to {url} after {max_attempts} attempt(s): {last_exc}"
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