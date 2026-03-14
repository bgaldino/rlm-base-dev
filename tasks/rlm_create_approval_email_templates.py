"""Create Lightning Email Templates for RLM Approval notifications.

EmailTemplatePage FlexiPages cannot be deployed via Metadata API or Tooling API
(platform restriction). This task creates EmailTemplate SObject records directly
via the REST API, reading template definitions from the dataset CSV.

Template definitions are stored in:
  datasets/sfdmu/qb/en-US/qb-approvals/EmailTemplate.csv

Alert→template linkage is derived from:
  datasets/sfdmu/qb/en-US/qb-approvals/ApprovalAlertContentDef.csv

The task is idempotent: it skips templates that already exist by Name, and
skips ApprovalAlertContentDef records that are already linked correctly.
"""

import csv
import json
import requests
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object  # type: ignore
    TaskOptionsError = Exception  # type: ignore

DEFAULT_TEMPLATE_CSV = "datasets/sfdmu/qb/en-US/qb-approvals/EmailTemplate.csv"
DEFAULT_ALERT_CSV = "datasets/sfdmu/qb/en-US/qb-approvals/ApprovalAlertContentDef.csv"


class CreateApprovalEmailTemplates(BaseSalesforceTask):
    """Create Lightning Email Templates from CSV and link to ApprovalAlertContentDef.

    Reads EmailTemplate.csv from the qb-approvals dataset to create SFX-type
    Lightning Email Templates in the target org, then links them to the
    corresponding ApprovalAlertContentDef records.
    """

    task_options = {
        "template_csv": {
            "description": (
                "Path to EmailTemplate CSV (relative to repo root). "
                f"Defaults to {DEFAULT_TEMPLATE_CSV}."
            ),
            "required": False,
        },
        "alert_csv": {
            "description": (
                "Path to ApprovalAlertContentDef CSV (relative to repo root) "
                "used to derive alert→template linkage. "
                f"Defaults to {DEFAULT_ALERT_CSV}."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)

        template_csv = repo_root / (
            self.options.get("template_csv") or DEFAULT_TEMPLATE_CSV
        )
        alert_csv = repo_root / (self.options.get("alert_csv") or DEFAULT_ALERT_CSV)

        if not template_csv.exists():
            raise FileNotFoundError(f"EmailTemplate CSV not found: {template_csv}")
        if not alert_csv.exists():
            raise FileNotFoundError(
                f"ApprovalAlertContentDef CSV not found: {alert_csv}"
            )

        templates = self._read_csv(template_csv)
        alerts = self._read_csv(alert_csv)

        self.logger.info("Read %d template(s) from %s", len(templates), template_csv)
        self.logger.info(
            "Read %d alert definition(s) from %s", len(alerts), alert_csv
        )

        headers, base_url = self._api_headers()
        folder_id = self._get_org_id(base_url, headers)

        self.logger.info("Using org ID as FolderId (Unfiled Public): %s", folder_id)

        template_id_by_name = self._create_templates(
            base_url, headers, templates, folder_id
        )
        self._link_alerts(base_url, headers, alerts, template_id_by_name)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_csv(self, path):
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    def _api_headers(self):
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.project_config, "project__package__api_version", None)
            or "66.0"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        base_url = f"{instance_url}/services/data/v{api_version}"
        return headers, base_url

    def _get_org_id(self, base_url, headers):
        resp = requests.get(
            f"{base_url}/query?q=SELECT+Id+FROM+Organization+LIMIT+1",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()["records"][0]["Id"]

    def _create_templates(self, base_url, headers, templates, folder_id):
        names = [t["Name"] for t in templates]
        names_soql = ", ".join(f"'{n.replace(chr(39), chr(92) + chr(39))}'" for n in names)
        soql = f"SELECT Id, Name FROM EmailTemplate WHERE Name IN ({names_soql})"
        resp = requests.get(
            f"{base_url}/query",
            params={"q": soql},
            headers=headers,
        )
        resp.raise_for_status()
        existing = {r["Name"]: r["Id"] for r in resp.json()["records"]}

        template_id_by_name = {}
        for tmpl in templates:
            name = tmpl["Name"]
            if name in existing:
                self.logger.info("Template already exists, skipping: %s", name)
                template_id_by_name[name] = existing[name]
                continue

            payload = {
                "Name": name,
                "DeveloperName": tmpl["DeveloperName"],
                "Subject": tmpl["Subject"],
                "HtmlValue": tmpl["HtmlValue"],
                "TemplateType": "custom",
                "UiType": tmpl.get("UiType") or "SFX",
                "FolderId": folder_id,
            }
            resp = requests.post(
                f"{base_url}/sobjects/EmailTemplate",
                headers=headers,
                data=json.dumps(payload),
            )
            if resp.status_code in (200, 201):
                record_id = resp.json()["id"]
                self.logger.info("Created template: %s (%s)", name, record_id)
                template_id_by_name[name] = record_id
            else:
                raise RuntimeError(
                    f"Failed to create EmailTemplate '{name}': {resp.text}"
                )

        return template_id_by_name

    def _link_alerts(self, base_url, headers, alerts, template_id_by_name):
        """Link ApprovalAlertContentDef records to their EmailTemplates."""
        # Build alert_name → template_id from the CSV's EmailTemplate.Name column
        alert_to_template_id = {}
        for row in alerts:
            alert_name = row.get("Name", "").strip()
            template_name = row.get("EmailTemplate.Name", "").strip()
            if alert_name and template_name and template_name in template_id_by_name:
                alert_to_template_id[alert_name] = template_id_by_name[template_name]
            elif template_name and template_name not in template_id_by_name:
                self.logger.warning(
                    "Template '%s' not found for alert '%s'", template_name, alert_name
                )

        if not alert_to_template_id:
            self.logger.info("No alert→template mappings to process.")
            return

        alert_names_soql = ", ".join(
            f"'{n.replace(chr(39), chr(92) + chr(39))}'" for n in alert_to_template_id
        )
        soql = (
            f"SELECT Id, Name, EmailTemplateId FROM ApprovalAlertContentDef"
            f" WHERE Name IN ({alert_names_soql})"
        )
        resp = requests.get(
            f"{base_url}/query",
            params={"q": soql},
            headers=headers,
        )
        resp.raise_for_status()
        org_alerts = {r["Name"]: r for r in resp.json()["records"]}

        updated = 0
        for alert_name, template_id in alert_to_template_id.items():
            alert = org_alerts.get(alert_name)
            if not alert:
                self.logger.warning(
                    "ApprovalAlertContentDef not found in org: %s", alert_name
                )
                continue
            if alert.get("EmailTemplateId") == template_id:
                self.logger.info("Already linked: %s", alert_name)
                continue

            resp = requests.patch(
                f"{base_url}/sobjects/ApprovalAlertContentDef/{alert['Id']}",
                headers=headers,
                data=json.dumps({"EmailTemplateId": template_id}),
            )
            if resp.status_code == 204:
                self.logger.info("Linked: %s", alert_name)
                updated += 1
            else:
                raise RuntimeError(
                    f"Failed to link ApprovalAlertContentDef '{alert_name}': {resp.text}"
                )

        self.logger.info(
            "Linked %d ApprovalAlertContentDef record(s).", updated
        )
