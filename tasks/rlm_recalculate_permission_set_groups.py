"""
Recalculate Permission Set Groups and wait until they are Updated.

Why PSGs show "Outdated": After deploy_pre or assign_permission_set_licenses, Salesforce
marks PSGs as Outdated when their effective permissions need to be recalculated. The normal
transition is Outdated → Updating (platform recalculating) → Updated. We trigger recalc by
updating the PSG (e.g. Description); using the Tooling API for the update is required in
many orgs for the platform to actually start recalc and move status to Updating.
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
            "description": "Max time to wait for all PSGs to become Updated (per attempt).",
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
        "initial_delay_seconds": {
            "description": "Seconds to wait before starting to poll (gives platform time after PSL assign/deploy).",
            "required": False,
        },
        "retry_count": {
            "description": "Number of retries after a timeout (sleep then poll again).",
            "required": False,
        },
        "retry_delay_seconds": {
            "description": "Seconds to wait before retrying after a timeout.",
            "required": False,
        },
        "post_trigger_delay_seconds": {
            "description": "After triggering recalc on Outdated groups, wait this long before next poll (gives platform time to transition to Updating).",
            "required": False,
        },
        "use_tooling_api": {
            "description": "Use Tooling API for PSG updates (can be required in some orgs to trigger recalculation).",
            "required": False,
        },
    }

    def _run_task(self):
        names = self._parse_names(self.options.get("api_names"))
        timeout_seconds = int(self.options.get("timeout_seconds", 300))
        poll_seconds = int(self.options.get("poll_seconds", 10))
        trigger_recalc = str(self.options.get("trigger_recalc", "true")).lower() == "true"
        initial_delay_seconds = int(self.options.get("initial_delay_seconds", 0))
        retry_count = int(self.options.get("retry_count", 2))
        retry_delay_seconds = int(self.options.get("retry_delay_seconds", 120))
        post_trigger_delay_seconds = int(self.options.get("post_trigger_delay_seconds", 90))
        use_tooling_api = str(self.options.get("use_tooling_api", "false")).lower() == "true"
        self._use_tooling_api = use_tooling_api

        # Check once up front: if all PSGs are already Updated, skip delay and wait loop
        rows = self._query_groups(names)
        status_by_name = {row["DeveloperName"]: row["Status"] for row in rows}
        missing = [name for name in names if name not in status_by_name]
        if missing:
            raise TaskOptionsError(
                f"PermissionSetGroup records not found: {', '.join(missing)}"
            )
        outdated = [n for n, s in status_by_name.items() if s == "Outdated"]
        updating = [n for n, s in status_by_name.items() if s == "Updating"]
        failed = [n for n, s in status_by_name.items() if s == "Failed"]
        if failed:
            raise TaskOptionsError(
                f"PermissionSetGroup recalculation failed: {', '.join(failed)}"
            )
        if not outdated and not updating:
            self.logger.info(
                "All target Permission Set Groups are already Updated; skipping recalc and wait."
            )
            return

        if initial_delay_seconds > 0:
            self.logger.info(
                f"Waiting {initial_delay_seconds}s for permission set groups to perform operations before polling."
            )
            time.sleep(initial_delay_seconds)

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                self._wait_until_updated(
                    names=names,
                    timeout_seconds=timeout_seconds,
                    poll_seconds=poll_seconds,
                    trigger_recalc=trigger_recalc,
                    post_trigger_delay_seconds=post_trigger_delay_seconds,
                    use_tooling_api=use_tooling_api,
                )
                return
            except TaskOptionsError as e:
                last_error = e
                if attempt < retry_count:
                    self.logger.warning(
                        f"Permission set groups not yet Updated (attempt {attempt + 1}/{retry_count + 1}). "
                        f"Waiting {retry_delay_seconds}s before retry."
                    )
                    time.sleep(retry_delay_seconds)
                else:
                    raise
        if last_error is not None:
            raise last_error

    def _wait_until_updated(
        self,
        names,
        timeout_seconds,
        poll_seconds,
        trigger_recalc,
        post_trigger_delay_seconds=0,
        use_tooling_api=False,
    ):
        deadline = time.time() + timeout_seconds
        recalc_attempted = set()
        self._use_tooling_api = use_tooling_api

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

            triggered_this_round = False
            if trigger_recalc:
                api_note = " (via Tooling API)" if getattr(self, "_use_tooling_api", False) else ""
                for name in outdated:
                    if name in recalc_attempted:
                        continue
                    self._touch_group_description(name)
                    recalc_attempted.add(name)
                    triggered_this_round = True
                    self.logger.info(
                        f"Triggered recalculation for Permission Set Group '{name}'{api_note}; "
                        "status should transition Outdated → Updating → Updated."
                    )

            if triggered_this_round and post_trigger_delay_seconds > 0:
                self.logger.info(
                    f"Waiting {post_trigger_delay_seconds}s for platform to start recalc before next poll."
                )
                time.sleep(post_trigger_delay_seconds)

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
        base = "tooling" if getattr(self, "_use_tooling_api", False) else "sobjects"
        url = (
            f"{self.org_config.instance_url}/services/data/"
            f"v{self._api_version()}/{base}/PermissionSetGroup/{record_id}"
        )
        response = requests.patch(url, headers=self._headers(), json=payload)
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"PermissionSetGroup update failed: {response.status_code} {response.text}"
            )
