"""
Activate RateCardEntry records via the Salesforce REST API.

In Release 262, updating RateCardEntry.Status via Apex anonymous DML (SOAP)
raises UNKNOWN_EXCEPTION (500) — a platform regression. The REST API works
correctly. This task replaces the activateRateCardEntries.apex script.

Idempotent: queries only Draft records; no-ops if all are already Active.
Uses the Composite API (25 records per request) for efficiency.
"""

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception

BATCH_SIZE = 25  # Composite API max sub-requests per call


class ActivateRateCardEntries(BaseTask):
    """Activate Draft RateCardEntry records via REST API (262+ workaround)."""

    task_docs = """
    Activates all Draft RateCardEntry records by setting Status = 'Active'.
    Uses the Salesforce REST Composite API to batch updates (25 per request).

    This task replaces the Apex-based activateRateCardEntries.apex approach
    which fails in Release 262 due to a platform regression in the SOAP
    Execute Anonymous endpoint for RateCardEntry DML.
    """

    def _run_task(self):
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = getattr(self.org_config, "api_version", None) or "67.0"
        api_version = str(api_version).lstrip("v")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        base_url = f"{instance_url}/services/data/v{api_version}"

        # Step 1: Query Draft records
        soql = "SELECT Id FROM RateCardEntry WHERE Status = 'Draft'"
        resp = requests.get(
            f"{base_url}/query",
            headers=headers,
            params={"q": soql},
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(
                f"Failed to query RateCardEntry: {resp.status_code} {resp.text}"
            )
        records = resp.json().get("records", [])

        if not records:
            self.logger.info("No Draft RateCardEntry records found — already Active.")
            return

        self.logger.info(
            "Found %d Draft RateCardEntry record(s) to activate.", len(records)
        )

        # Step 2: Activate in batches via Composite API
        ids = [r["Id"] for r in records]
        total_updated = 0
        errors = []

        for i in range(0, len(ids), BATCH_SIZE):
            batch = ids[i : i + BATCH_SIZE]
            sub_requests = [
                {
                    "method": "PATCH",
                    "url": f"/services/data/v{api_version}/sobjects/RateCardEntry/{rec_id}",
                    "referenceId": f"rce_{j}",
                    "body": {"Status": "Active"},
                }
                for j, rec_id in enumerate(batch)
            ]
            composite_resp = requests.post(
                f"{base_url}/composite",
                headers=headers,
                json={"allOrNone": False, "compositeRequest": sub_requests},
                timeout=60,
            )
            if not composite_resp.ok:
                raise RuntimeError(
                    f"Composite API call failed: {composite_resp.status_code} {composite_resp.text}"
                )
            results = composite_resp.json().get("compositeResponse", [])
            for sub, rec_id in zip(results, batch):
                http_status = sub.get("httpStatusCode", 0)
                if http_status in (200, 204):
                    total_updated += 1
                else:
                    body = sub.get("body", "")
                    errors.append(f"  {rec_id}: HTTP {http_status} — {body}")

        if errors:
            self.logger.warning(
                "%d record(s) failed to activate:\n%s",
                len(errors),
                "\n".join(errors),
            )
            raise RuntimeError(
                f"RateCardEntry activation failed for {len(errors)} record(s). "
                "See warnings above."
            )

        self.logger.info(
            "Successfully activated %d RateCardEntry record(s).", total_updated
        )
