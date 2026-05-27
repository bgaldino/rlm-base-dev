"""
Verify that the PRM procedure-plan overlay was applied.

This task checks for the PRM-only conditional branch records on
RLM_Quote_Pricing_Procedure_Plan:
- Section: IFPartnerDistributorOnQuote
- Option: RLM_PRM_DISTI_Pricing_Procedure (priority 1)
- Criterion: IsNotNull on PartnerAccount.BillingAddress

If any record is missing or duplicated, the task fails with a clear message so
the flow does not silently succeed with incomplete or non-idempotent PRM pricing
behavior.
"""

import time
from typing import Dict

import requests

try:
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class VerifyPrmProcedurePlanOverlay(BaseSalesforceTask):
    """Validate PRM overlay data exists for the Quote pricing procedure plan."""

    task_options: Dict[str, Dict[str, object]] = {
        "developerName": {
            "description": "ProcedurePlanDefinition DeveloperName",
            "required": True,
        },
        "subSectionType": {
            "description": "Expected PRM conditional section SubSectionType",
            "required": False,
        },
        "expressionSetDeveloperName": {
            "description": "Expected PRM pricing expression set DeveloperName",
            "required": False,
        },
        "criterionFieldPath": {
            "description": "Expected criterion FieldPath",
            "required": False,
        },
        "criterionOperator": {
            "description": "Expected criterion Operator",
            "required": False,
        },
        "maxWaitSeconds": {
            "description": "Maximum seconds to wait for overlay records to become queryable",
            "required": False,
        },
        "pollIntervalSeconds": {
            "description": "Seconds between verification polling attempts",
            "required": False,
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

    def _query_count(self, soql: str) -> int:
        url = f"{self._base_url}/query/?q={requests.utils.requote_uri(soql)}"
        resp = requests.get(url, headers=self._headers, timeout=60)
        resp.raise_for_status()
        return int(resp.json().get("totalSize", 0))

    def _run_task(self):
        dev_name = self.options["developerName"]
        sub_section = self.options.get("subSectionType", "IFPartnerDistributorOnQuote")
        expr_set = self.options.get(
            "expressionSetDeveloperName", "RLM_PRM_DISTI_Pricing_Procedure"
        )
        criterion_field = self.options.get(
            "criterionFieldPath", "PartnerAccount.BillingAddress"
        )
        criterion_operator = self.options.get("criterionOperator", "IsNotNull")
        max_wait_seconds = int(self.options.get("maxWaitSeconds", 45))
        poll_interval_seconds = int(self.options.get("pollIntervalSeconds", 3))

        section_q = (
            "SELECT Id FROM ProcedurePlanSection "
            f"WHERE ProcedurePlanVersion.DeveloperName = '{dev_name}' "
            f"AND SubSectionType = '{sub_section}'"
        )
        option_q = (
            "SELECT Id FROM ProcedurePlanOption "
            f"WHERE ProcedurePlanSection.ProcedurePlanVersion.DeveloperName = '{dev_name}' "
            f"AND ProcedurePlanSection.SubSectionType = '{sub_section}' "
            "AND Priority = 1 "
            f"AND ExpressionSetDefinition.DeveloperName = '{expr_set}'"
        )
        criterion_q = (
            "SELECT Id FROM ProcedurePlanCriterion "
            f"WHERE ProcedurePlanOption.ProcedurePlanSection.ProcedurePlanVersion.DeveloperName = '{dev_name}' "
            f"AND ProcedurePlanOption.ProcedurePlanSection.SubSectionType = '{sub_section}' "
            "AND ProcedurePlanOption.Priority = 1 "
            "AND Sequence = 1 "
            f"AND FieldPath = '{criterion_field}' "
            f"AND Operator = '{criterion_operator}'"
        )

        attempts = max(1, (max_wait_seconds // max(1, poll_interval_seconds)) + 1)
        section_count = option_count = criterion_count = 0

        for attempt in range(1, attempts + 1):
            section_count = self._query_count(section_q)
            option_count = self._query_count(option_q)
            criterion_count = self._query_count(criterion_q)

            if section_count == 1 and option_count == 1 and criterion_count == 1:
                break

            if attempt < attempts:
                self.logger.info(
                    "PRM overlay not fully visible yet (attempt %s/%s): "
                    "section=%s option=%s criterion=%s. Retrying in %ss...",
                    attempt,
                    attempts,
                    section_count,
                    option_count,
                    criterion_count,
                    poll_interval_seconds,
                )
                time.sleep(poll_interval_seconds)

        self.logger.info(
            "PRM procedure-plan overlay check counts: section=%s option=%s criterion=%s",
            section_count,
            option_count,
            criterion_count,
        )

        invalid_counts = {
            "section": section_count,
            "option": option_count,
            "criterion": criterion_count,
        }
        invalid_counts = {
            name: count for name, count in invalid_counts.items() if count != 1
        }

        if invalid_counts:
            count_details = ", ".join(
                f"{name}={count}" for name, count in invalid_counts.items()
            )
            raise TaskOptionsError(
                "PRM procedure-plan overlay must have exactly one section, "
                f"option, and criterion for {dev_name}/{sub_section}; found "
                f"{count_details}. Re-run insert_prm_procedure_plan_data and "
                "inspect SFDMU reports for missing records or duplicate inserts."
            )

        self.logger.info("PRM procedure-plan overlay verification passed.")
