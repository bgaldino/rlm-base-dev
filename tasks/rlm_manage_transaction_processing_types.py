"""
CumulusCI task for managing TransactionProcessingType via Tooling API.

Use this task to create or upsert TransactionProcessingType records required
by constraints and related RLM configuration dependencies.
"""
from typing import Dict, Any, List
import json
import os

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ManageTransactionProcessingTypes(BaseTask):
    task_options = {
        "operation": {
            "description": "Operation to perform: 'list', 'upsert'",
            "required": True,
        },
        "input_file": {
            "description": "Path to JSON file with records to upsert.",
            "required": False,
        },
        "key_field": {
            "description": "Field used to find existing records (default: DeveloperName).",
            "required": False,
        },
        "api_version": {
            "description": "Salesforce API version override (default from org/project).",
            "required": False,
        },
        "dry_run": {
            "description": "If true, only logs intended changes.",
            "required": False,
        },
    }

    def _run_task(self):
        operation = self.options.get("operation", "").lower().strip()
        if operation == "list":
            self._list_records()
        elif operation == "upsert":
            self._upsert_records()
        else:
            raise TaskOptionsError("operation must be 'list' or 'upsert'")

    def _get_api_context(self):
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = self.options.get("api_version") or getattr(
            self.org_config, "api_version", None
        ) or getattr(self.project_config, "project__package__api_version", "66.0")
        return access_token, instance_url, api_version

    def _tooling_headers(self, access_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    def _describe(self, access_token: str, instance_url: str, api_version: str) -> Dict[str, Any]:
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/TransactionProcessingType/describe"
        resp = requests.get(url, headers=self._tooling_headers(access_token))
        if not resp.ok:
            raise TaskOptionsError(
                f"Describe failed for TransactionProcessingType: {resp.status_code} - {resp.text}"
            )
        return resp.json()

    def _query(self, access_token: str, instance_url: str, api_version: str, soql: str) -> List[Dict[str, Any]]:
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/query"
        resp = requests.get(url, headers=self._tooling_headers(access_token), params={"q": soql})
        if not resp.ok:
            raise TaskOptionsError(f"Tooling query failed: {resp.status_code} - {resp.text}")
        records = resp.json().get("records", [])
        for rec in records:
            rec.pop("attributes", None)
        return records

    def _list_records(self):
        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        fields = {f["name"] for f in describe.get("fields", [])}
        preferred = ["Id", "DeveloperName", "MasterLabel", "Description", "IsActive"]
        select_fields = [f for f in preferred if f in fields]
        if "Id" not in select_fields:
            select_fields.insert(0, "Id")
        soql = f"SELECT {', '.join(select_fields)} FROM TransactionProcessingType"
        records = self._query(access_token, instance_url, api_version, soql)
        if not records:
            self.logger.info("No TransactionProcessingType records found.")
            return
        self.logger.info(f"Found {len(records)} TransactionProcessingType records:")
        for rec in records:
            self.logger.info(json.dumps(rec, indent=2))

    def _upsert_records(self):
        input_file = self.options.get("input_file")
        if not input_file:
            raise TaskOptionsError("input_file is required for upsert")
        if not os.path.isfile(input_file):
            raise TaskOptionsError(f"input_file not found: {input_file}")

        with open(input_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise TaskOptionsError("input_file must contain a JSON array of records")

        key_field = self.options.get("key_field") or "DeveloperName"
        dry_run = str(self.options.get("dry_run", "")).lower() in {"1", "true", "yes"}

        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        fields = {f["name"] for f in describe.get("fields", [])}
        if key_field not in fields:
            raise TaskOptionsError(f"Key field '{key_field}' not available on TransactionProcessingType")

        for record in payload:
            if not isinstance(record, dict):
                raise TaskOptionsError("Each record must be an object")
            key_value = record.get(key_field)
            if not key_value:
                raise TaskOptionsError(f"Record missing key field '{key_field}': {record}")

            # Remove any keys not supported by the object
            cleaned = {k: v for k, v in record.items() if k in fields}

            existing = self._query(
                access_token,
                instance_url,
                api_version,
                f"SELECT Id FROM TransactionProcessingType WHERE {key_field} = '{key_value}'",
            )
            if existing:
                record_id = existing[0]["Id"]
                if dry_run:
                    self.logger.info(f"[dry-run] Would update {key_field}={key_value} ({record_id})")
                    continue
                self._update_record(access_token, instance_url, api_version, record_id, cleaned)
                self.logger.info(f"Updated {key_field}={key_value} ({record_id})")
            else:
                if dry_run:
                    self.logger.info(f"[dry-run] Would create {key_field}={key_value}")
                    continue
                record_id = self._create_record(access_token, instance_url, api_version, cleaned)
                self.logger.info(f"Created {key_field}={key_value} ({record_id})")

    def _create_record(self, access_token: str, instance_url: str, api_version: str, body: Dict[str, Any]) -> str:
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/TransactionProcessingType"
        resp = requests.post(url, headers=self._tooling_headers(access_token), json=body)
        if not resp.ok:
            raise TaskOptionsError(f"Create failed: {resp.status_code} - {resp.text}")
        return resp.json().get("id")

    def _update_record(self, access_token: str, instance_url: str, api_version: str, record_id: str, body: Dict[str, Any]):
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/TransactionProcessingType/{record_id}"
        resp = requests.patch(url, headers=self._tooling_headers(access_token), json=body)
        if resp.status_code not in (200, 204):
            raise TaskOptionsError(f"Update failed: {resp.status_code} - {resp.text}")
