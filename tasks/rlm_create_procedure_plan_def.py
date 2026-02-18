import requests

from cumulusci.core.keychain import BaseProjectKeychain
from cumulusci.tasks.sfdx import SFDXBaseTask

# CreateProcedurePlanDefinition invokes the POST request for Procedure Plan Definitions
# as described in the RLM Connect API:
# https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_procedure_plan_definition_records.htm


class CreateProcedurePlanDefinition(SFDXBaseTask):
    task_options = {
        "access_token": {
            "description": "The access token for the org. Defaults to the project default",
        },
        "instance_url": {
            "description": "The instance URL for the org. Defaults to the project default",
        },
        "description": {
            "description": "The description of the procedure plan definition",
            "required": True,
        },
        "developerName": {
            "description": "The developer name of the procedure plan definition",
            "required": True,
        },
        "name": {
            "description": "The name of the procedure plan definition",
            "required": True,
        },
        "primaryObject": {
            "description": "The primary object of the procedure plan definition",
            "required": True,
        },
        "processType": {
            "description": "The process type of the procedure plan definition (e.g. Default)",
            "required": True,
        },
        "versionActive": {
            "description": "Whether the procedure plan definition version is active",
            "required": True,
        },
        "versionContextDefinition": {
            "description": "Context definition for the version (e.g. SalesTransactionContext__stdctx)",
            "required": True,
        },
        "versionReadContextMapping": {
            "description": "Read context mapping for the version (e.g. QuoteEntitiesMapping)",
            "required": True,
        },
        "versionSaveContextMapping": {
            "description": "Save context mapping for the version (e.g. QuoteEntitiesMapping)",
            "required": True,
        },
        "versionEffectiveFrom": {
            "description": "Effective from date for the version (ISO datetime, e.g. 2024-07-15T10:15:30.000Z)",
            "required": True,
        },
        "versionDeveloperName": {
            "description": "Developer name of the procedure plan definition version",
            "required": True,
        },
        "versionRank": {
            "description": "Rank of the procedure plan definition version",
            "required": True,
        },
        "versionEffectiveTo": {
            "description": "Effective to date for the version (ISO datetime, optional)",
            "required": False,
        },
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

    # Helper to construct the request URL and headers for Connect API calls
    def _build_url_and_headers(self, endpoint):
        api_version = self.project_config.project__package__api_version
        url = f"{self.instance_url}/services/data/v{api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return url, headers

    # Make an HTTP request and return JSON on success, log error and return None on failure
    def _make_request(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        if response.ok:
            return response.json() if response.content else {}
        self.logger.error(
            f"Failed {method.upper()} request to {url}: {response.status_code} {response.text}"
        )
        return None

    # Build the POST request body per Procedure Plan Definitions resource (POST).
    # procedurePlanDefinitionVersions is constructed from version* task options.
    def _build_request_body(self):
        version_item = {
            "active": self._to_bool(self.options.get("versionActive", False)),
            "contextDefinition": self.options.get("versionContextDefinition"),
            "readContextMapping": self.options.get("versionReadContextMapping"),
            "saveContextMapping": self.options.get("versionSaveContextMapping"),
            "effectiveFrom": self.options.get("versionEffectiveFrom"),
            "developerName": self.options.get("versionDeveloperName"),
            "rank": int(self.options.get("versionRank", 0)),
        }
        effective_to = self.options.get("versionEffectiveTo")
        if effective_to:
            version_item["effectiveTo"] = effective_to

        return {
            "description": self.options.get("description"),
            "developerName": self.options.get("developerName"),
            "name": self.options.get("name"),
            "processType": self.options.get("processType"),
            "primaryObject": self.options.get("primaryObject"),
            "procedurePlanDefinitionVersions": [version_item],
        }

    # Execute the task: invoke POST on Procedure Plan Definitions resource
    def _run_task(self):
        self._prep_runtime()
        body = self._build_request_body()
        if not body:
            self.logger.error("Cannot build request body; check required options")
            return

        url, headers = self._build_url_and_headers("connect/procedure-plan-definitions")
        response = self._make_request("post", url, headers=headers, json=body)
        if response:
            definition_id = response.get("procedurePlanDefinitionId") or response.get("id")
            if definition_id:
                self.logger.info(f"Procedure plan definition created: {definition_id}")

    @staticmethod
    def _to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes")
        return bool(value)

    def get_keychain_class(self):
        return None

    def get_keychain_key(self):
        return None