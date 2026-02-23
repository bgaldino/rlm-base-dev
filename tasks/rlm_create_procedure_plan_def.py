"""
Custom CumulusCI task to create a Procedure Plan Definition via the RLM Connect API.

ProcedurePlanDefinition records cannot be created via standard sObject REST API;
the Connect API endpoint POST /connect/procedure-plan-definitions must be used.

This task is idempotent: if a ProcedurePlanDefinition with the given DeveloperName
already exists, it logs a message and skips creation.

Reference:
https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_procedure_plan_definition_records.htm
"""
from typing import Any, Dict, Optional

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class CreateProcedurePlanDefinition(BaseSalesforceTask):
    """Create a Procedure Plan Definition + Version via the RLM Connect API.

    The task first checks whether a definition with the given developerName
    already exists.  If so it logs and returns without making changes
    (idempotent).  Otherwise it resolves the target ContextDefinition,
    builds the Connect API payload, and POSTs it.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "description": {
            "description": "The description of the procedure plan definition",
            "required": True,
        },
        "developerName": {
            "description": "The developer name of the procedure plan definition",
            "required": True,
        },
        "name": {
            "description": "The name (label) of the procedure plan definition",
            "required": True,
        },
        "primaryObject": {
            "description": "The primary object of the procedure plan definition (e.g. Quote)",
            "required": True,
        },
        "processType": {
            "description": "The process type (e.g. RevenueCloud)",
            "required": True,
        },
        "versionActive": {
            "description": "Whether the procedure plan definition version should be active",
            "required": True,
        },
        "versionContextDefinition": {
            "description": (
                "Explicit ContextDefinition Id for the version. "
                "If omitted, the Id is looked up by context_definition_label."
            ),
            "required": False,
        },
        "context_definition_label": {
            "description": (
                "MasterLabel of the ContextDefinition to look up when "
                "versionContextDefinition is not set (default: RLM_SalesTransactionContext)"
            ),
            "required": False,
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
            "description": "Effective-from date in ISO-8601 format (e.g. 2026-01-01T00:00:00.000Z)",
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
            "description": "Effective-to date in ISO-8601 format (optional)",
            "required": False,
        },
    }

    # -- Auth / API helpers --------------------------------------------

    @property
    def _api_version(self) -> str:
        return (
            getattr(self.org_config, "api_version", None)
            or getattr(
                self.project_config,
                "project__package__api_version",
                "66.0",
            )
        )

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _base_url(self) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._api_version}"

    # -- SOQL helpers --------------------------------------------------

    @staticmethod
    def _soql_escape(value: str) -> str:
        """Escape a string for use in a SOQL literal (single-quoted value)."""
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _soql_query(self, soql: str) -> list:
        """Execute a SOQL query and return all records."""
        url = f"{self._base_url}/query"
        resp = requests.get(url, headers=self._headers, params={"q": soql})
        if resp.status_code != 200:
            self.logger.error(
                "SOQL query failed (%s): %s", resp.status_code, resp.text
            )
            return []
        body = resp.json()
        records = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            nurl = f"{self.org_config.instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(nurl, headers=self._headers)
            if resp.status_code != 200:
                break
            body = resp.json()
            records.extend(body.get("records", []))
        return records

    # -- Idempotency check ---------------------------------------------

    def _definition_exists(self, developer_name: str) -> bool:
        """Return True if a ProcedurePlanDefinition with this DeveloperName exists."""
        safe = self._soql_escape(developer_name)
        records = self._soql_query(
            f"SELECT Id FROM ProcedurePlanDefinition "
            f"WHERE DeveloperName = '{safe}'"
        )
        return len(records) > 0

    # -- Context definition resolution ---------------------------------

    def _get_context_definition_id_by_label(self, label: str) -> Optional[str]:
        """Query ContextDefinition by MasterLabel and return its Id."""
        safe = self._soql_escape(label)
        records = self._soql_query(
            f"SELECT Id FROM ContextDefinition WHERE MasterLabel = '{safe}'"
        )
        if not records:
            self.logger.error(
                "No ContextDefinition found with MasterLabel = '%s'", label
            )
            return None
        return records[0].get("Id")

    def _resolve_context_definition_id(self) -> Optional[str]:
        """Resolve the ContextDefinition Id from explicit option or label lookup."""
        explicit = self.options.get("versionContextDefinition")
        if explicit:
            return explicit
        label = self.options.get("context_definition_label") or "RLM_SalesTransactionContext"
        return self._get_context_definition_id_by_label(label)

    # -- Request body --------------------------------------------------

    def _build_request_body(self) -> Optional[dict]:
        """Build the Connect API POST body for the procedure plan definition."""
        context_definition_id = self._resolve_context_definition_id()
        if not context_definition_id:
            return None

        version_item = {
            "active": self._to_bool(self.options.get("versionActive", False)),
            "contextDefinition": context_definition_id,
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

    # -- Main task logic -----------------------------------------------

    def _run_task(self):
        dev_name = self.options["developerName"]

        if self._definition_exists(dev_name):
            self.logger.info(
                "ProcedurePlanDefinition '%s' already exists. Skipping creation.",
                dev_name,
            )
            return

        body = self._build_request_body()
        if not body:
            raise TaskOptionsError(
                "Cannot build request body. Verify context_definition_label "
                "or versionContextDefinition is correct."
            )

        url = f"{self._base_url}/connect/procedure-plan-definitions"
        self.logger.info(
            "Creating ProcedurePlanDefinition '%s' via Connect API ...", dev_name
        )
        resp = requests.post(url, headers=self._headers, json=body)

        if resp.ok:
            result = resp.json() if resp.content else {}
            definition_id = (
                result.get("procedurePlanDefinitionId")
                or result.get("id")
                or "unknown"
            )
            self.logger.info(
                "ProcedurePlanDefinition created: %s", definition_id
            )
        else:
            self.logger.error(
                "Connect API POST failed (%s): %s", resp.status_code, resp.text
            )
            raise TaskOptionsError(
                f"Failed to create ProcedurePlanDefinition '{dev_name}': "
                f"{resp.status_code} {resp.text}"
            )

    @staticmethod
    def _to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes")
        return bool(value)


class ActivateProcedurePlanVersion(BaseSalesforceTask):
    """Activate a ProcedurePlanDefinitionVersion by its parent definition's DeveloperName.

    Queries for the PPDV linked to the given DeveloperName and patches
    IsActive = true via the sObject REST API.  Idempotent: if already
    active, logs and returns.
    """

    task_options = {
        "developerName": {
            "description": "DeveloperName of the parent ProcedurePlanDefinition",
            "required": True,
        },
    }

    @property
    def _base_url(self):
        return f"{self.org_config.instance_url}/services/data/v66.0"

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _run_task(self):
        dev_name = self.options["developerName"]

        query = (
            "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
            f"WHERE ProcedurePlanDefinition.DeveloperName = '{dev_name}'"
        )
        url = f"{self._base_url}/query/?q={requests.utils.requote_uri(query)}"
        resp = requests.get(url, headers=self._headers)
        resp.raise_for_status()
        records = resp.json().get("records", [])

        if not records:
            raise TaskOptionsError(
                f"No ProcedurePlanDefinitionVersion found for DeveloperName '{dev_name}'"
            )

        version = records[0]
        version_id = version["Id"]

        if version.get("IsActive"):
            self.logger.info(
                "ProcedurePlanDefinitionVersion %s is already active. Skipping.",
                version_id,
            )
            return

        patch_url = f"{self._base_url}/sobjects/ProcedurePlanDefinitionVersion/{version_id}"
        patch_resp = requests.patch(patch_url, headers=self._headers, json={"IsActive": True})

        if patch_resp.ok or patch_resp.status_code == 204:
            self.logger.info(
                "ProcedurePlanDefinitionVersion %s activated successfully.", version_id
            )
        else:
            self.logger.error(
                "Failed to activate PPDV %s (%s): %s",
                version_id, patch_resp.status_code, patch_resp.text,
            )
            raise TaskOptionsError(
                f"Failed to activate ProcedurePlanDefinitionVersion: "
                f"{patch_resp.status_code} {patch_resp.text}"
            )
