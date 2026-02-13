"""
Recalculate Permission Set Groups and wait until they are Updated.
"""
import time
from typing import List
import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class RecalculatePermissionSetGroups(BaseTask):
    """Ensure PSGs are in Updated status before assignment."""

    task_options = {
        "api_names": {
            "description": "List or comma-separated PSG DeveloperName values.",
            "required": True,
        },
        "timeout_seconds": {
            "description": "Max time to wait for all PSGs to become Updated.",
            "required": False,
        },
        "poll_seconds": {
            "description": "Polling interval in seconds.",
            "required": False,
        },
        "trigger_recalc": {
            "description": "Update Description on Outdated PSGs to trigger recalculation.",
            "required": False,
        },
    }

    def _run_task(self):
        names = self._parse_names(self.options.get("api_names"))
        timeout_seconds = int(self.options.get("timeout_seconds", 300))
        poll_seconds = int(self.options.get("poll_seconds", 10))
        trigger_recalc = str(self.options.get("trigger_recalc", "true")).lower() == "true"

        deadline = time.time() + timeout_seconds
        recalc_attempted = set()

        while True:
            rows = self._query_groups(names)
            status_by_name = {row["DeveloperName"]: row["Status"] for row in rows}

            missing = [name for name in names if name not in status_by_name]
            if missing:
                raise TaskOptionsError(
                    f"PermissionSetGroup records not found: {', '.join(missing)}"
                )

            outdated = [name for name, status in status_by_name.items() if status == "Outdated"]
            failed = [name for name, status in status_by_name.items() if status == "Failed"]
            updating = [name for name, status in status_by_name.items() if status == "Updating"]

            if failed:
                raise TaskOptionsError(
                    f"PermissionSetGroup recalculation failed: {', '.join(failed)}"
                )

            if not outdated and not updating:
                self.logger.info("All target Permission Set Groups are Updated.")
                return

            if trigger_recalc:
                for name in outdated:
                    if name in recalc_attempted:
                        continue
                    self._touch_group_description(name)
                    recalc_attempted.add(name)
                    self.logger.info(f"Triggered recalculation for Permission Set Group '{name}'.")

            if time.time() >= deadline:
                statuses = ", ".join(
                    f"{n}:{status_by_name.get(n, 'Missing')}" for n in names
                )
                raise TaskOptionsError(
                    f"Timed out waiting for Permission Set Groups to become Updated. Statuses: {statuses}"
                )

            self.logger.info(
                "Waiting for Permission Set Groups to reach Updated. "
                f"Outdated: {len(outdated)}, Updating: {len(updating)}"
            )
            time.sleep(poll_seconds)

    def _parse_names(self, value) -> List[str]:
        if isinstance(value, list):
            names = [str(v).strip() for v in value if str(v).strip()]
        elif isinstance(value, str):
            names = [v.strip() for v in value.split(",") if v.strip()]
        else:
            raise TaskOptionsError("api_names must be a list or comma-separated string")

        if not names:
            raise TaskOptionsError("api_names cannot be empty")
        return names

    def _query_groups(self, names: List[str]):
        quoted = ", ".join(f"'{self._escape_soql(name)}'" for name in names)
        soql = (
            "SELECT Id, DeveloperName, Status, Description "
            f"FROM PermissionSetGroup WHERE DeveloperName IN ({quoted})"
        )
        return self._query(soql)

    def _touch_group_description(self, name: str):
        rows = self._query(
            "SELECT Id, Description FROM PermissionSetGroup "
            f"WHERE DeveloperName = '{self._escape_soql(name)}' LIMIT 1"
        )
        if not rows:
            raise TaskOptionsError(f"PermissionSetGroup not found: {name}")

        row = rows[0]
        description = (row.get("Description") or "").strip()
        marker = "[cci-recalc]"
        if marker in description:
            new_description = description.replace(marker, "").strip()
        else:
            new_description = f"{description} {marker}".strip()

        self._update_permission_set_group(row["Id"], {"Description": new_description})

    def _escape_soql(self, value: str) -> str:
        return value.replace("'", "\\'")

    def _api_version(self) -> str:
        return (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _query(self, soql: str):
        url = f"{self.org_config.instance_url}/services/data/v{self._api_version()}/query"
        response = requests.get(url, headers=self._headers(), params={"q": soql})
        if not response.ok:
            raise TaskOptionsError(f"SOQL query failed: {response.status_code} {response.text}")
        return response.json().get("records", [])

    def _update_permission_set_group(self, record_id: str, payload: dict):
        url = (
            f"{self.org_config.instance_url}/services/data/"
            f"v{self._api_version()}/sobjects/PermissionSetGroup/{record_id}"
        )
        response = requests.patch(url, headers=self._headers(), json=payload)
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"PermissionSetGroup update failed: {response.status_code} {response.text}"
            )
