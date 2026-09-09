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

# Recovery-by-developerName settings. Separate from the constants above:
# _MAX_RETRIES/_RETRY_BACKOFF govern _make_request's fast per-call retry on a
# single HTTP transaction and must stay short. This governs polling for the
# *side effect* of a POST whose own log says it "may take 5-10 minutes on some
# org types" -- a 3-attempt/~90s window gives up long before that commit
# finishes (see todo 126 / #264-64).
_RECOVER_BUDGET_SECONDS = 600   # total poll window; sized to the documented 5-10 min commit
_RECOVER_INITIAL_WAIT = 15      # first inter-probe wait, then doubles
_RECOVER_MAX_INTERVAL = 120     # cap on the exponential inter-probe wait


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
        },
        "allow_skip_if_unavailable": {
            "description": "If true, skip gracefully when the base context definition "
                           "is not available (UNKNOWN_EXCEPTION). Use for optional contexts "
                           "whose base may not be provisioned. Defaults to false.",
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
        self.logger.info("      (this API call may take 5-10 minutes on some org types — please wait)")
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
        self.context_id = None
        self._last_response_status = None
        self._last_response_body = None
        response = self._make_request("post", url, headers=headers, json=payload)
        if response is not None:
            self.context_id = response.get("contextDefinitionId")
        # Determine how to handle failure:
        # - UNKNOWN_EXCEPTION = base context definition not available in this org.
        #   This is expected for optional contexts (e.g. Contracts when CLM feature
        #   is not fully enabled). Skip gracefully.
        # - DUPLICATE_VALUE = context definition already exists. Recover the ID
        #   and continue with configuration (set default mapping, activate, etc.).
        # - Other API errors (401, 403, 400, etc.) = fail loudly.
        # - Network error (no response status) = attempt recovery by querying org.
        if not self.context_id:
            allow_skip = str(self.options.get("allow_skip_if_unavailable", "false")).lower() == "true"
            if self._last_response_status is not None and self._is_missing_base_context_error():
                if allow_skip:
                    self.logger.warning(
                        f"      Base context definition not available for '{developer_name}'. "
                        f"Skipping — allow_skip_if_unavailable is set."
                    )
                    return
                raise RuntimeError(
                    f"Base context definition not available for '{developer_name}'. "
                    f"Salesforce returned UNKNOWN_EXCEPTION. If this context is optional, "
                    f"set allow_skip_if_unavailable: true in the task options."
                )
            if self._last_response_status is not None and self._is_duplicate_value_error():
                self.logger.info(
                    f"      Context definition '{developer_name}' already exists. "
                    f"Recovering ID to continue configuration..."
                )
                recovery_reason = "duplicate_value"
                self.context_id = self._recover_context_id(developer_name)
            elif self._last_response_status is not None:
                # Non-recoverable API error (auth, validation, etc.) — fail loudly
                raise RuntimeError(
                    f"Salesforce API error creating context definition '{developer_name}': "
                    f"HTTP {self._last_response_status} — {self._last_response_body[:300]}"
                )
            elif response is None:
                # Network failure — no response came back at all. Attempt recovery.
                self.logger.warning(
                    f"      No response from server — attempting to recover by developerName..."
                )
                recovery_reason = "network_drop"
                self.context_id = self._recover_context_id(developer_name)
            else:
                # Got a response, but it had no contextDefinitionId (empty/non-JSON
                # body, or a success payload missing the field) — not a dropped
                # connection. Attempt recovery.
                self.logger.warning(
                    f"      contextDefinitionId not in response — attempting to recover by developerName..."
                )
                recovery_reason = "missing_id"
                self.context_id = self._recover_context_id(developer_name)
        if self.context_id:
            self.logger.info(f"      Context Definition ID: {self.context_id}")
            self._process_context_id()
        else:
            raise RuntimeError(
                self._recovery_failure_message(developer_name, recovery_reason)
            )

    def _is_missing_base_context_error(self):
        """Check if the last API error indicates the base context is unavailable.

        Salesforce returns UNKNOWN_EXCEPTION when the base context definition
        referenced by baseReference does not exist in the org (feature not enabled).
        """
        return self._has_error_code("UNKNOWN_EXCEPTION")

    def _is_duplicate_value_error(self):
        """Check if the last API error indicates the context definition already exists.

        Salesforce returns DUPLICATE_VALUE when a definition with the same
        Name or DeveloperName already exists. The task should recover the
        existing ID and continue with configuration steps.
        """
        return self._has_error_code("DUPLICATE_VALUE")

    def _has_error_code(self, error_code):
        """Check if the last response body contains a specific Salesforce errorCode."""
        if not self._last_response_body:
            return False
        try:
            errors = json.loads(self._last_response_body)
            if isinstance(errors, list):
                return any(
                    e.get("errorCode") == error_code for e in errors
                )
        except (ValueError, TypeError):
            pass
        return False

    def _recover_context_id(self, developer_name, *, sleep=time.sleep, monotonic=time.monotonic):
        """Query the org for an existing context definition by developerName.

        Polls on a total elapsed-time budget (_RECOVER_BUDGET_SECONDS) rather than
        a fixed attempt count, because the operation being recovered from ("this
        API call may take 5-10 minutes on some org types") is far slower than a
        short attempt count can wait out. Backoff between probes grows
        exponentially from _RECOVER_INITIAL_WAIT, capped at _RECOVER_MAX_INTERVAL,
        so an early-committing org gets a fast answer while a slow one still gets
        the full budget. ``sleep``/``monotonic`` are injectable so tests can drive
        the loop without real time.
        """
        self.logger.info(f"      Querying for existing context definition '{developer_name}'...")
        # Use the direct lookup endpoint (avoids paging the full list)
        url, headers = self._build_url_and_headers(
            f"connect/context-definitions/{developer_name}"
        )
        start = monotonic()
        wait = _RECOVER_INITIAL_WAIT
        attempt = 0
        while True:
            elapsed = monotonic() - start
            remaining = _RECOVER_BUDGET_SECONDS - elapsed
            if remaining <= 0:
                return None
            attempt += 1
            # Disable _make_request's own retries — this loop owns the backoff.
            # Cap the probe's own connect/read timeout to what's left of the
            # budget, so a stalled probe can't itself run the loop well past
            # _RECOVER_BUDGET_SECONDS (the default per-call timeout is 630s).
            probe_timeout = (min(_CONNECT_TIMEOUT, remaining), min(_READ_TIMEOUT, remaining))
            response = self._make_request(
                "get", url, headers=headers, retryable=False, timeout=probe_timeout
            )
            if response is not None:
                # The API returns isSuccess:false for unknown definitions
                if response.get("isSuccess") is not False:
                    ctx_id = response.get("contextDefinitionId")
                    if ctx_id:
                        self.logger.info(
                            f"      Recovered context definition from org "
                            f"(attempt {attempt}, {int(monotonic() - start)}s elapsed)."
                        )
                        return ctx_id
            elapsed = monotonic() - start
            remaining = _RECOVER_BUDGET_SECONDS - elapsed
            if remaining <= 0:
                return None
            this_wait = min(wait, remaining)
            self.logger.warning(
                f"      Context definition not found yet (attempt {attempt}, "
                f"{int(elapsed)}s/{_RECOVER_BUDGET_SECONDS}s elapsed). "
                f"Waiting {int(this_wait)}s for server-side commit..."
            )
            sleep(this_wait)
            wait = min(wait * 2, _RECOVER_MAX_INTERVAL)

    def _recovery_failure_message(self, developer_name, reason):
        """Build the exhausted-recovery error message for the given ``reason``.

        The three reasons need different operator framing, so the message must not
        conflate them (todo 126 / #264-64):
        - "network_drop": no response came back at all (a real connection drop),
          so whether the definition was created server-side is genuinely unknown.
        - "missing_id": a response did come back, just without a
          contextDefinitionId (empty/non-JSON body, or a success payload missing
          the field) — the connection did not drop, but the outcome is still
          unknown, so the operator guidance is the same as network_drop.
        - "duplicate_value": Salesforce already told us a definition exists
          (DUPLICATE_VALUE), so its absence from the lookup is either a
          visibility/permission problem on this exact record, or (per
          _is_duplicate_value_error) a *different* definition sharing the same
          display Name but a different developerName — a developerName lookup
          can never resolve that second case.
        """
        budget_minutes = _RECOVER_BUDGET_SECONDS // 60
        if reason == "duplicate_value":
            return (
                f"Salesforce reported a context definition matching '{developer_name}' "
                f"already exists (DUPLICATE_VALUE), but it was not retrievable by "
                f"developerName after polling for ~{budget_minutes} minutes. Two "
                f"distinct causes produce DUPLICATE_VALUE: a visibility/permission gap "
                f"on this exact record, or another definition that shares the same "
                f"display Name but a different developerName — a developerName lookup "
                f"can never resolve that second case. Inspect the org's "
                f"ContextDefinition via the Connect API "
                f"(.cursor/skills/context-service/SKILL.md); if no record with "
                f"developerName '{developer_name}' exists, search by Name instead."
            )
        if reason == "missing_id":
            outcome = (
                f"The POST to create context definition '{developer_name}' returned "
                f"a response without a contextDefinitionId (empty or unexpected body)"
            )
        else:
            outcome = (
                f"The POST to create context definition '{developer_name}' had its "
                f"connection drop before returning an ID"
            )
        return (
            f"{outcome}, and it was not visible by developerName after polling for "
            f"~{budget_minutes} minutes. It was very likely created server-side and "
            f"is still committing, OR the POST never reached the server — this "
            f"cannot be distinguished from here. Re-run the task: if it was created, "
            f"the re-run returns DUPLICATE_VALUE and recovers the ID automatically; "
            f"if it was not, the re-run creates it cleanly. Neither outcome "
            f"duplicates the definition."
        )

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
                    if response.status_code == 204 or not response.text.strip():
                        return {}
                    try:
                        return response.json()
                    except ValueError:
                        self.logger.warning(
                            f"      Non-JSON response body on {response.status_code}: "
                            f"{response.text[:200]}"
                        )
                        return {}
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
                self._last_response_status = response.status_code
                self._last_response_body = response.text
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
                    self._last_response_status = None
                    self._last_response_body = None
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