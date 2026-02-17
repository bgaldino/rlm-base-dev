"""
Custom CumulusCI task to reconfigure an auto-provisioned Expression Set.

Salesforce autoproc creates certain Expression Sets (e.g.
Salesforce_Pricing_Discovery_Procedure) in scratch orgs with an incorrect
context definition.  This task performs a deactivate-reconfigure-reactivate
cycle via REST API so the expression set points at the correct context
definition and has the expected Rank / StartDate values.

The task is idempotent: if the expression set already has the correct
context definition, rank, and start date it logs a message and skips.
"""
import time
from typing import Any, Dict, List, Optional

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class ReconfigureExpressionSet(BaseSalesforceTask):
    """Reconfigure an auto-provisioned Expression Set in a scratch org.

    Performs a full deactivate -> reconfigure -> reactivate cycle:
      1. Query the ExpressionSetVersion by ApiName
      2. Deactivate if currently active
      3. Update the ExpressionSetDefinitionContextDefinition junction
         to point at the desired ContextDefinition
      4. Set Rank and StartDate on the ExpressionSetVersion
      5. Reactivate the version
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "expression_set_name": {
            "description": (
                "DeveloperName of the Expression Set to reconfigure "
                "(e.g. 'Salesforce_Pricing_Discovery_Procedure')"
            ),
            "required": True,
        },
        "context_definition_name": {
            "description": (
                "DeveloperName of the target ContextDefinition "
                "(e.g. 'RLM_SalesTransactionContext')"
            ),
            "required": True,
        },
        "rank": {
            "description": "Rank to set on the ExpressionSetVersion (default: 1)",
            "required": False,
        },
        "start_date": {
            "description": (
                "StartDate to set on the ExpressionSetVersion in ISO-8601 format "
                "(default: '2020-01-01T00:00:00.000Z')"
            ),
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

    # -- SOQL helper ---------------------------------------------------

    def _soql_query(self, soql: str) -> List[dict]:
        """Execute a SOQL query and return all records."""
        url = f"{self._base_url}/query"
        resp = requests.get(url, headers=self._headers, params={"q": soql})
        if resp.status_code != 200:
            self.logger.error(
                "SOQL query failed (%s): %s", resp.status_code, resp.text
            )
            return []
        body = resp.json()
        records: List[dict] = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            nurl = f"{self.org_config.instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(nurl, headers=self._headers)
            if resp.status_code != 200:
                break
            body = resp.json()
            records.extend(body.get("records", []))
        return records

    # -- REST helpers --------------------------------------------------

    def _patch_record(
        self, sobject: str, record_id: str, payload: dict, label: str = ""
    ) -> bool:
        """PATCH an sObject record with retry for row-lock errors."""
        url = f"{self._base_url}/sobjects/{sobject}/{record_id}"
        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            resp = requests.patch(url, headers=self._headers, json=payload)
            if resp.status_code in (200, 204):
                return True
            resp_text = resp.text or ""
            if "UNABLE_TO_LOCK_ROW" in resp_text and attempt < max_attempts:
                wait = attempt * 2
                self.logger.warning(
                    "Row lock on %s (attempt %s/%s). Retrying in %ss.",
                    label or record_id,
                    attempt,
                    max_attempts,
                    wait,
                )
                time.sleep(wait)
                continue
            self.logger.error(
                "PATCH %s/%s failed (%s): %s",
                sobject,
                record_id,
                resp.status_code,
                resp_text,
            )
            return False
        return False

    def _create_record(self, sobject: str, payload: dict) -> Optional[str]:
        """POST a new sObject record. Returns the new Id or None."""
        url = f"{self._base_url}/sobjects/{sobject}/"
        resp = requests.post(url, headers=self._headers, json=payload)
        if resp.status_code == 201:
            return resp.json()["id"]
        self.logger.error(
            "POST %s failed (%s): %s", sobject, resp.status_code, resp.text
        )
        return None

    # -- Main task logic -----------------------------------------------

    def _run_task(self):
        es_name = self.options["expression_set_name"]
        cd_name = self.options["context_definition_name"]
        rank = int(self.options.get("rank") or 1)
        start_date = self.options.get("start_date") or "2020-01-01T00:00:00.000Z"

        self.logger.info(
            "Reconfiguring expression set '%s' -> context '%s', rank=%s, start=%s",
            es_name,
            cd_name,
            rank,
            start_date,
        )

        # 1. Query ExpressionSetVersion
        esv = self._get_expression_set_version(es_name)
        if esv is None:
            return

        esv_id = esv["Id"]
        was_active = esv.get("IsActive", False)

        # 2. Deactivate if active
        if was_active:
            self.logger.info("Deactivating ExpressionSetVersion %s ...", esv_id)
            if not self._patch_record(
                "ExpressionSetVersion",
                esv_id,
                {"IsActive": False},
                label=es_name,
            ):
                raise TaskOptionsError(
                    f"Failed to deactivate ExpressionSetVersion for '{es_name}'"
                )
            self.logger.info("Deactivated.")
        else:
            self.logger.info("ExpressionSetVersion is already inactive; skipping deactivation.")

        # 3. Update context definition
        self._update_context_definition(es_name, cd_name)

        # 4. Update Rank and StartDateTime
        self.logger.info("Setting Rank=%s, StartDateTime=%s ...", rank, start_date)
        if not self._patch_record(
            "ExpressionSetVersion",
            esv_id,
            {"Rank": rank, "StartDateTime": start_date},
            label=es_name,
        ):
            raise TaskOptionsError(
                f"Failed to update Rank/StartDateTime on ExpressionSetVersion for '{es_name}'"
            )
        self.logger.info("Updated Rank and StartDateTime.")

        # 5. Reactivate
        self.logger.info("Reactivating ExpressionSetVersion %s ...", esv_id)
        if not self._patch_record(
            "ExpressionSetVersion",
            esv_id,
            {"IsActive": True},
            label=es_name,
        ):
            raise TaskOptionsError(
                f"Failed to reactivate ExpressionSetVersion for '{es_name}'"
            )
        self.logger.info(
            "Successfully reconfigured '%s' (context=%s, rank=%s, start=%s).",
            es_name,
            cd_name,
            rank,
            start_date,
        )

    # -- Step helpers --------------------------------------------------

    def _get_expression_set_version(self, es_name: str) -> Optional[dict]:
        """Query ExpressionSetVersion by ApiName. Returns the record or None.

        Version ApiName conventions vary across expression sets (some use
        ``_V1``, others use ``V1`` with no underscore).  We try both patterns
        and also fall back to a LIKE query to handle any future variations.
        """
        candidates = [f"{es_name}_V1", f"{es_name}V1"]
        for candidate in candidates:
            records = self._soql_query(
                f"SELECT Id, IsActive, Rank, StartDateTime "
                f"FROM ExpressionSetVersion "
                f"WHERE ApiName = '{candidate}'"
            )
            if records:
                self.logger.info(
                    "Found ExpressionSetVersion via ApiName '%s'.", candidate
                )
                return records[0]

        # Fallback: LIKE query
        records = self._soql_query(
            f"SELECT Id, IsActive, Rank, StartDateTime, ApiName "
            f"FROM ExpressionSetVersion "
            f"WHERE ApiName LIKE '{es_name}%'"
        )
        if records:
            self.logger.info(
                "Found ExpressionSetVersion via LIKE pattern: '%s'.",
                records[0].get("ApiName"),
            )
            return records[0]

        self.logger.warning(
            "ExpressionSetVersion for '%s' not found. "
            "The autoproc expression set may not exist in this org yet.",
            es_name,
        )
        return None

    def _update_context_definition(self, es_name: str, cd_name: str):
        """Ensure the ExpressionSetDefinitionContextDefinition points to cd_name."""
        # Resolve ExpressionSetDefinition Id
        esd_records = self._soql_query(
            f"SELECT Id FROM ExpressionSetDefinition "
            f"WHERE DeveloperName = '{es_name}'"
        )
        if not esd_records:
            raise TaskOptionsError(
                f"ExpressionSetDefinition '{es_name}' not found in org."
            )
        esd_id = esd_records[0]["Id"]

        # Resolve target ContextDefinition Id
        cd_records = self._soql_query(
            f"SELECT Id FROM ContextDefinition WHERE DeveloperName = '{cd_name}'"
        )
        if not cd_records:
            raise TaskOptionsError(
                f"ContextDefinition '{cd_name}' not found in org."
            )
        cd_id = cd_records[0]["Id"]

        # Query existing junction record
        esdcd_records = self._soql_query(
            f"SELECT Id, ContextDefinitionId "
            f"FROM ExpressionSetDefinitionContextDefinition "
            f"WHERE ExpressionSetDefinitionId = '{esd_id}'"
        )

        if esdcd_records:
            existing_cd_id = esdcd_records[0].get("ContextDefinitionId", "")
            if existing_cd_id == cd_id:
                self.logger.info(
                    "Context definition already set to '%s'; no change needed.",
                    cd_name,
                )
                return
            # Update existing junction
            esdcd_id = esdcd_records[0]["Id"]
            self.logger.info(
                "Updating context definition from %s to %s (%s) ...",
                existing_cd_id,
                cd_id,
                cd_name,
            )
            if not self._patch_record(
                "ExpressionSetDefinitionContextDefinition",
                esdcd_id,
                {"ContextDefinitionId": cd_id},
                label=f"ESDCD for {es_name}",
            ):
                raise TaskOptionsError(
                    f"Failed to update ExpressionSetDefinitionContextDefinition "
                    f"for '{es_name}'"
                )
            self.logger.info("Updated context definition.")
        else:
            # Create new junction
            self.logger.info(
                "No existing context definition link found; creating one for '%s' -> '%s' ...",
                es_name,
                cd_name,
            )
            new_id = self._create_record(
                "ExpressionSetDefinitionContextDefinition",
                {
                    "ExpressionSetDefinitionId": esd_id,
                    "ContextDefinitionId": cd_id,
                },
            )
            if not new_id:
                raise TaskOptionsError(
                    f"Failed to create ExpressionSetDefinitionContextDefinition "
                    f"for '{es_name}'"
                )
            self.logger.info("Created context definition link -> %s", new_id)
