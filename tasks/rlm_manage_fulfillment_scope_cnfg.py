"""
CumulusCI task for managing CustomFulfillmentScopeCnfg via Tooling API.

CustomFulfillmentScopeCnfg is a DRO/Industries Fulfillment setup object
introduced in API v65.0. It is inaccessible via standard SOAP/REST APIs
(apiAccess="never") and must be accessed through the Tooling API at:
  /services/data/v{api_version}/tooling/sobjects/CustomFulfillmentScopeCnfg

Supported operations:
  list     — query records and log to console
  extract  — query records and write to output_file (JSON array)
  upsert   — read records from input_file and create/update in target org
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception

OBJECT_NAME = "CustomFulfillmentScopeCnfg"
DEFAULT_OUTPUT_FILE = "datasets/tooling/CustomFulfillmentScopeCnfg.json"
MIN_API_VERSION = "65.0"


class ManageFulfillmentScopeCnfg(BaseTask):
    task_options = {
        "operation": {
            "description": (
                "Operation to perform: 'list' (log to console), "
                "'extract' (write to output_file), 'upsert' (import from input_file)."
            ),
            "required": True,
        },
        "output_file": {
            "description": (
                f"Path to write extracted records (JSON array). "
                f"Default: {DEFAULT_OUTPUT_FILE}. Used by 'extract' only."
            ),
            "required": False,
        },
        "input_file": {
            "description": (
                "Path to JSON file (array) with records to upsert. "
                "Required for 'upsert' operation."
            ),
            "required": False,
        },
        "key_field": {
            "description": (
                "Field used to match existing records during upsert. "
                "Default: DeveloperName."
            ),
            "required": False,
        },
        "api_version": {
            "description": (
                f"Salesforce API version override (minimum {MIN_API_VERSION}). "
                "Default: project/org version."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "If true, log intended changes without writing to the org.",
            "required": False,
        },
    }

    # Fields that are read-only / system-managed and must not be sent on write
    _READONLY_FIELDS = frozenset(
        {"Id", "CreatedDate", "LastModifiedDate", "CreatedById", "LastModifiedById",
         "SystemModstamp", "NamespacePrefix", "attributes"}
    )

    # Preferred display/export field order (subset; describe drives actual selection)
    _PREFERRED_FIELDS = [
        "Id", "DeveloperName", "MasterLabel", "Language", "NamespacePrefix",
        "Description", "IsActive",
    ]

    # ------------------------------------------------------------------ #
    # Entry point                                                           #
    # ------------------------------------------------------------------ #

    def _run_task(self):
        operation = self.options.get("operation", "").lower().strip()
        if operation == "list":
            self._list_records()
        elif operation == "extract":
            self._extract_records()
        elif operation == "upsert":
            self._upsert_records()
        else:
            raise TaskOptionsError(
                f"operation must be one of: 'list', 'extract', 'upsert'. Got: {operation!r}"
            )

    # ------------------------------------------------------------------ #
    # Shared helpers                                                        #
    # ------------------------------------------------------------------ #

    def _get_api_context(self):
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available — pass --org <alias>")

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url

        api_version = (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(
                self.project_config, "project__package__api_version", "66.0"
            )
        )
        # Enforce minimum version
        try:
            if float(api_version) < float(MIN_API_VERSION):
                self.logger.warning(
                    f"api_version {api_version} is below the minimum {MIN_API_VERSION} "
                    f"required by {OBJECT_NAME}. Upgrading to {MIN_API_VERSION}."
                )
                api_version = MIN_API_VERSION
        except ValueError:
            pass

        return access_token, instance_url, api_version

    def _headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _describe(
        self, access_token: str, instance_url: str, api_version: str
    ) -> Dict[str, Any]:
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}/describe"
        )
        resp = requests.get(url, headers=self._headers(access_token))
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling describe failed for {OBJECT_NAME}: "
                f"{resp.status_code} — {resp.text}"
            )
        return resp.json()

    def _query(
        self, access_token: str, instance_url: str, api_version: str, soql: str
    ) -> List[Dict[str, Any]]:
        import requests

        url = f"{instance_url}/services/data/v{api_version}/tooling/query"
        resp = requests.get(
            url, headers=self._headers(access_token), params={"q": soql}
        )
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling query failed: {resp.status_code} — {resp.text}"
            )
        records = resp.json().get("records", [])
        for rec in records:
            rec.pop("attributes", None)
        return records

    def _build_select_fields(self, describe: Dict[str, Any]) -> List[str]:
        available = {f["name"] for f in describe.get("fields", [])}
        ordered = [f for f in self._PREFERRED_FIELDS if f in available]
        # Append any remaining fields not already in the ordered list
        for f in sorted(available - set(ordered)):
            ordered.append(f)
        return ordered

    # ------------------------------------------------------------------ #
    # Operations                                                            #
    # ------------------------------------------------------------------ #

    def _list_records(self):
        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        select_fields = self._build_select_fields(describe)

        soql = f"SELECT {', '.join(select_fields)} FROM {OBJECT_NAME}"
        records = self._query(access_token, instance_url, api_version, soql)

        if not records:
            self.logger.info(f"No {OBJECT_NAME} records found.")
            return

        self.logger.info(f"Found {len(records)} {OBJECT_NAME} record(s):")
        for rec in records:
            self.logger.info(json.dumps(rec, indent=2))

    def _extract_records(self):
        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        select_fields = self._build_select_fields(describe)

        soql = f"SELECT {', '.join(select_fields)} FROM {OBJECT_NAME}"
        records = self._query(access_token, instance_url, api_version, soql)

        output_file = self.options.get("output_file") or DEFAULT_OUTPUT_FILE
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2)

        self.logger.info(
            f"Extracted {len(records)} {OBJECT_NAME} record(s) → {output_path}"
        )

    def _upsert_records(self):
        input_file = self.options.get("input_file")
        if not input_file:
            raise TaskOptionsError("input_file is required for upsert operation")
        if not os.path.isfile(input_file):
            raise TaskOptionsError(f"input_file not found: {input_file}")

        with open(input_file, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if not isinstance(payload, list):
            raise TaskOptionsError("input_file must contain a JSON array of records")

        key_field = self.options.get("key_field") or "DeveloperName"
        dry_run = str(self.options.get("dry_run", "")).lower() in {"1", "true", "yes"}

        access_token, instance_url, api_version = self._get_api_context()
        describe = self._describe(access_token, instance_url, api_version)
        available_fields = {f["name"] for f in describe.get("fields", [])}

        if key_field not in available_fields:
            raise TaskOptionsError(
                f"key_field '{key_field}' is not a field on {OBJECT_NAME}. "
                f"Available: {sorted(available_fields)}"
            )

        writable_fields = {
            f["name"]
            for f in describe.get("fields", [])
            if not f.get("calculated", False) and f.get("name") not in self._READONLY_FIELDS
        }

        created = updated = skipped = 0

        for record in payload:
            if not isinstance(record, dict):
                raise TaskOptionsError(f"Each record must be a JSON object, got: {record!r}")

            key_value = record.get(key_field)
            if not key_value:
                raise TaskOptionsError(
                    f"Record is missing key_field '{key_field}': {record}"
                )

            # Strip read-only and unavailable fields before sending
            cleaned = {
                k: v
                for k, v in record.items()
                if k in writable_fields and k not in self._READONLY_FIELDS
            }

            existing = self._query(
                access_token,
                instance_url,
                api_version,
                f"SELECT Id FROM {OBJECT_NAME} WHERE {key_field} = '{key_value}'",
            )

            if existing:
                record_id = existing[0]["Id"]
                # Remove key field from PATCH body — it's already matched
                patch_body = {k: v for k, v in cleaned.items() if k != key_field}
                if dry_run:
                    self.logger.info(
                        f"[dry-run] Would UPDATE {key_field}={key_value} ({record_id})"
                    )
                    skipped += 1
                    continue
                self._update_record(access_token, instance_url, api_version, record_id, patch_body)
                self.logger.info(f"Updated {key_field}={key_value} ({record_id})")
                updated += 1
            else:
                if dry_run:
                    self.logger.info(f"[dry-run] Would CREATE {key_field}={key_value}")
                    skipped += 1
                    continue
                new_id = self._create_record(access_token, instance_url, api_version, cleaned)
                self.logger.info(f"Created {key_field}={key_value} ({new_id})")
                created += 1

        if dry_run:
            self.logger.info(f"[dry-run] {skipped} record(s) would be processed.")
        else:
            self.logger.info(
                f"Upsert complete — created: {created}, updated: {updated}"
            )

    # ------------------------------------------------------------------ #
    # Tooling API write helpers                                             #
    # ------------------------------------------------------------------ #

    def _create_record(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        body: Dict[str, Any],
    ) -> Optional[str]:
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}"
        )
        resp = requests.post(url, headers=self._headers(access_token), json=body)
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling create failed: {resp.status_code} — {resp.text}"
            )
        return resp.json().get("id")

    def _update_record(
        self,
        access_token: str,
        instance_url: str,
        api_version: str,
        record_id: str,
        body: Dict[str, Any],
    ):
        import requests

        url = (
            f"{instance_url}/services/data/v{api_version}"
            f"/tooling/sobjects/{OBJECT_NAME}/{record_id}"
        )
        resp = requests.patch(url, headers=self._headers(access_token), json=body)
        if resp.status_code not in (200, 204):
            raise TaskOptionsError(
                f"Tooling update failed: {resp.status_code} — {resp.text}"
            )
