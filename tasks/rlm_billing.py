import copy
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Optional

# Import repo `tasks.*` before cumulusci: its project_config empties tasks.__path__, so a later `tasks.soql_utils` import fails.
from tasks.soql_utils import project_api_version, require_identifier, soql_quote

try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceApiTask = object
    TaskOptionsError = Exception

DEFAULT_PLAN_DIR = "datasets/sfdmu/qb/en-US/qb-billing"
CONNECT_SEQUENCE_POLICY_PATH = "connect/sequences/policy"
CONNECT_INVOICE_SCHEDULER_PATH = "commerce/invoicing/invoice-schedulers"

# Map human-readable DateStampFormat values to Connect API enum names.
DATE_STAMP_FORMAT_MAP = {
    "YYYY": "Yyyy",
    "MM-YYYY": "MmYyyy",
    "DD-MM-YYYY": "DdMmYyyy",
    "MM-DD-YYYY": "MmDdYyyy",
}


def _api_datetime(value: str) -> str:
    """Convert a date or ISO 8601 datetime to the 'yyyy-MM-dd HH:mm:ss' format
    required by the Connect API.

    Accepts:  '2024-01-01', '2024-01-01T00:00:00.000+0000', '2024-01-01T00:00:00Z'
    Returns:  '2024-01-01 00:00:00'
    """
    v = value.strip()
    if "T" in v:
        date_part = v.split("T")[0]
        time_part = v.split("T")[1].split(".")[0].split("+")[0].rstrip("Z")
        return f"{date_part} {time_part}"
    if len(v) == 10:
        return f"{v} 00:00:00"
    return v


class CreateSequencePolicies(BaseSalesforceApiTask):
    """Create SequencePolicy records (with selection conditions) via the Connect API.

    SequencePolicy cannot be created via the standard REST/Bulk API because required
    fields DateStampFormat and IncrementByNumber are not createable through standard DML.
    The Connect API endpoint /connect/sequences/policy handles these internally.

    Selection conditions are included inline in each policy's POST body.
    Data is sourced from SequencePolicies.json in the plan directory.

    Idempotent: existing policies (matched by Name) are skipped.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "plan_dir": {
            "description": (
                f"Path to the qb-billing plan directory containing SequencePolicies.json. "
                f"Defaults to {DEFAULT_PLAN_DIR}."
            ),
            "required": False,
        },
    }

    def _run_task(self) -> None:
        import requests

        plan_dir = self.options.get("plan_dir", DEFAULT_PLAN_DIR)
        json_path = os.path.join(plan_dir, "SequencePolicies.json")

        if not os.path.isfile(json_path):
            raise TaskOptionsError(f"SequencePolicies.json not found: {json_path}")

        with open(json_path, encoding="utf-8") as f:
            policies = json.load(f)

        # Fetch existing policy names for idempotency
        existing_names = {
            r["Name"]
            for r in self.sf.query("SELECT Name FROM SequencePolicy").get("records", [])
        }
        if existing_names:
            self.logger.info(
                f"Found {len(existing_names)} existing SequencePolicy record(s) — will skip."
            )

        # Pre-resolve Reference-type filterValues (e.g. LegalEntity names → IDs)
        ref_id_cache = self._build_ref_id_cache(policies)

        api_version = project_api_version(self.project_config, TaskOptionsError)
        base_url = (
            f"{self.org_config.instance_url}/services/data/v{api_version}"
            f"/{CONNECT_SEQUENCE_POLICY_PATH}"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

        created = skipped = errors = 0
        for policy in policies:
            name = policy["name"]
            if name in existing_names:
                self.logger.info(f"  Skipping existing policy: {name}")
                skipped += 1
                continue

            body = self._build_body(policy, ref_id_cache)
            self.logger.info(f"  Creating policy: {name}")

            resp = requests.post(base_url, headers=headers, json=body, timeout=30)
            if resp.status_code in (200, 201):
                self.logger.info(f"    Created: {name}")
                created += 1
            else:
                self.logger.error(
                    f"    Failed to create '{name}': HTTP {resp.status_code} — {resp.text}"
                )
                errors += 1

        self.logger.info(
            f"createSequencePolicies: created={created}, skipped={skipped}, errors={errors}."
        )
        if errors:
            raise TaskOptionsError(
                f"createSequencePolicies: {errors} policy creation(s) failed."
            )

    def _build_ref_id_cache(self, policies: list) -> dict:
        """For each Reference-type selection condition across all policies,
        resolve the human-readable name to a Salesforce record ID.

        Returns a dict keyed by (object_type, name) → Salesforce ID.
        """
        by_object: dict = defaultdict(set)
        for policy in policies:
            for c in policy.get("selectionConditions", []):
                if c.get("filterFieldType") == "Reference":
                    field = c["filterField"]  # e.g. "LegalEntityId"
                    object_type = field[:-2] if field.endswith("Id") else field
                    by_object[object_type].add(c["filterValue"])

        cache = {}
        for object_type, names in by_object.items():
            require_identifier(object_type, "filterField", TaskOptionsError)
            names_soql = ", ".join(soql_quote(n) for n in names)
            soql = f"SELECT Id, Name FROM {object_type} WHERE Name IN ({names_soql})"
            try:
                for r in self.sf.query(soql).get("records", []):
                    cache[(object_type, r["Name"])] = r["Id"]
                    self.logger.info(f"  Resolved {object_type} '{r['Name']}' → {r['Id']}")
            except Exception as e:
                self.logger.error(f"  Failed to resolve {object_type} IDs: {e}")

        return cache

    def _build_body(self, policy: dict, ref_id_cache: dict) -> dict:
        """Build the Connect API request body for one SequencePolicy."""
        conditions = policy.get("selectionConditions", [])

        body: dict = {
            "name": policy["name"],
            "effectiveFromDateTime": _api_datetime(policy["effectiveFromDateTime"]),
            "isActive": policy.get("isActive", True),
            "sequenceMode": policy["sequenceMode"],
            "targetObject": policy["targetObject"],
            "dateStampFormat": DATE_STAMP_FORMAT_MAP.get(
                policy["dateStampFormat"], policy["dateStampFormat"]
            ),
            "sequenceStartNumber": policy["sequenceStartNumber"],
            "incrementNumber": policy["incrementByNumber"],
            "sequencePattern": policy["sequencePattern"],
            **({"filterCriteria": "Custom"} if len(conditions) > 1 else {}),
        }

        # Optional fields
        for json_key, api_key in [
            ("description", "description"),
            ("expirationDateTime", "expirationDateTime"),
            ("maximumSequenceNumber", "maximumSequenceNumber"),
            ("minimumSequenceNumberWidth", "minimumSequenceNumberWidth"),
            ("selectionLogic", "selectionLogic"),
            ("timeZone", "timeZone"),
        ]:
            if json_key in policy and policy[json_key] is not None:
                body[api_key] = policy[json_key]

        # Selection conditions — Reference-type filterValues resolved to org IDs
        if conditions:
            cond_list = []
            for c in conditions:
                field = c["filterField"]
                fv = c["filterValue"]
                if c.get("filterFieldType") == "Reference":
                    object_type = field[:-2] if field.endswith("Id") else field
                    fv = ref_id_cache.get((object_type, fv), fv)
                cond_list.append({
                    "conditionNumber": c["conditionNumber"],
                    "filterField": field,
                    "operator": c["operator"],
                    "filterValue": fv,
                })
            body["selectionCondition"] = cond_list

        return body


def scheduler_start_date(today_utc: Optional[date] = None) -> str:
    """The sample schedulers' start date: the next UTC day.

    The Connect API refuses a start date before the current date in the user's time zone. The
    next UTC day is on or after that date in every time zone up to UTC+14.
    """
    today_utc = today_utc or datetime.now(timezone.utc).date()
    return (today_utc + timedelta(days=1)).isoformat()


def build_invoice_scheduler_body(entry: dict, start_date: str) -> dict:
    """Connect POST body for one sample invoice scheduler.

    The scheduler is always created Inactive and never set to start a run on create, so a build
    starts no bill run whatever the JSON says. A Once scheduler without a target date (the
    catch-up sample) gets the start date as its target date; set the real date before activating.
    """
    body = copy.deepcopy(entry)
    body["status"] = "Inactive"
    body["startDate"] = start_date
    if isinstance(body.get("frequencyCadenceOptions"), dict):
        body["frequencyCadenceOptions"].pop("shouldStartRunImmediately", None)
    if body.get("frequencyCadence") == "Once" and not body.get("targetDate"):
        body["targetDate"] = start_date
    return body


class CreateInvoiceSchedulers(BaseSalesforceApiTask):
    """Create inactive sample invoice schedulers via the Connect API.

    BillingBatchScheduler and InvoiceBatchRunCriteria are neither createable nor updateable
    through DML; POST /commerce/invoicing/invoice-schedulers creates both. One sample per 264
    scheduler option (catch-up, target day of month and month offset, billing period count,
    Generate Invoice Documents), read from InvoiceSchedulers.json in the plan directory.

    Idempotent: a scheduler whose name already exists is skipped. The platform does not let
    a scheduler be deleted, so an existing sample is never replaced.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "plan_dir": {
            "description": (
                f"Path to the qb-billing plan directory containing InvoiceSchedulers.json. "
                f"Defaults to {DEFAULT_PLAN_DIR}."
            ),
            "required": False,
        },
    }

    def _run_task(self) -> None:
        import requests

        plan_dir = self.options.get("plan_dir", DEFAULT_PLAN_DIR)
        json_path = os.path.join(plan_dir, "InvoiceSchedulers.json")
        if not os.path.isfile(json_path):
            raise TaskOptionsError(f"InvoiceSchedulers.json not found: {json_path}")
        with open(json_path, encoding="utf-8") as f:
            schedulers = json.load(f)

        existing_names = {
            r["BillingSchedulerName"]
            for r in self.sf.query_all(
                "SELECT BillingSchedulerName FROM BillingBatchScheduler"
            ).get("records", [])
        }

        api_version = project_api_version(self.project_config, TaskOptionsError)
        url = (
            f"{self.org_config.instance_url}/services/data/v{api_version}"
            f"/{CONNECT_INVOICE_SCHEDULER_PATH}"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        start_date = scheduler_start_date()

        created = skipped = errors = 0
        for entry in schedulers:
            name = entry["schedulerName"]
            if name in existing_names:
                self.logger.info(f"  Skipping existing scheduler: {name}")
                skipped += 1
                continue
            body = build_invoice_scheduler_body(entry, start_date)
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code in (200, 201):
                self.logger.info(f"  Created inactive scheduler: {name}")
                created += 1
            else:
                self.logger.error(
                    f"  Failed to create '{name}': HTTP {resp.status_code} — {resp.text}"
                )
                errors += 1

        self.logger.info(
            f"createInvoiceSchedulers: created={created}, skipped={skipped}, errors={errors}."
        )
        if errors:
            raise TaskOptionsError(
                f"createInvoiceSchedulers: {errors} scheduler creation(s) failed."
            )
