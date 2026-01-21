import subprocess
import time
from typing import List

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class EnsurePricingSchedules(BaseTask):
    """Ensure PriceAdjustmentSchedule records exist; toggle pricing if missing."""

    task_options = {
        "schedule_names": {
            "description": "List of PriceAdjustmentSchedule names to verify.",
            "required": False,
        },
        "poll_attempts": {
            "description": "Number of times to poll after toggle.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds to wait between polls.",
            "required": False,
        },
        "disable_settings_path": {
            "description": "Path to settings bundle that disables pricing.",
            "required": True,
        },
        "enable_settings_path": {
            "description": "Path to settings bundle that enables pricing.",
            "required": True,
        },
    }

    def _run_task(self):
        schedule_names = self.options.get(
            "schedule_names",
            [
                "Standard Attribute Based Adjustment",
                "Standard Price Adjustment Tier",
                "Standard Bundle Based Adjustment",
            ],
        )

        missing = self._get_missing_schedules(schedule_names)
        if not missing:
            self.logger.info("PriceAdjustmentSchedule records are present.")
            return

        self.logger.warning(
            "Missing PriceAdjustmentSchedule records: %s", ", ".join(missing)
        )
        self.logger.info(
            "Toggling pricing setting to regenerate missing schedules."
        )

        self._deploy_settings(self.options["disable_settings_path"])
        self._deploy_settings(self.options["enable_settings_path"])

        attempts = int(self.options.get("poll_attempts") or 6)
        interval = int(self.options.get("poll_interval_seconds") or 10)
        missing_after = []
        for attempt in range(1, attempts + 1):
            time.sleep(interval)
            missing_after = self._get_missing_schedules(schedule_names)
            if not missing_after:
                break
            self.logger.warning(
                "Pricing schedules still missing (attempt %s/%s): %s",
                attempt,
                attempts,
                ", ".join(missing_after),
            )

        if missing_after:
            raise TaskOptionsError(
                "PriceAdjustmentSchedule records still missing after toggle: "
                + ", ".join(missing_after)
            )

        self.logger.info("Pricing schedules created after toggle.")

    def _get_missing_schedules(self, schedule_names: List[str]) -> List[str]:
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        import requests

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

        name_list = "', '".join([n.replace("'", "\\'") for n in schedule_names])
        soql = (
            "SELECT Name FROM PriceAdjustmentSchedule "
            f"WHERE Name IN ('{name_list}')"
        )
        url = f"{instance_url}/services/data/v{api_version}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params={"q": soql})
        if not response.ok:
            raise TaskOptionsError(
                f"Failed to query PriceAdjustmentSchedule: {response.text}"
            )

        records = response.json().get("records", [])
        found_names = {r.get("Name") for r in records if r.get("Name")}
        return [n for n in schedule_names if n not in found_names]

    def _deploy_settings(self, settings_path: str):
        target_org = getattr(self.org_config, "username", None)
        if not target_org:
            raise TaskOptionsError("No target org username available for deploy.")

        cmd = [
            "sf",
            "project",
            "deploy",
            "start",
            "--source-dir",
            settings_path,
            "--target-org",
            target_org,
            "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise TaskOptionsError(
                f"Deploy failed for {settings_path}: {result.stderr or result.stdout}"
            )
