import subprocess
import time
from typing import List
from pathlib import Path
import xml.etree.ElementTree as ET

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
        "expression_sets_metadata_path": {
            "description": "Path to expression set metadata used to discover DecisionTable lookup API names.",
            "required": False,
        },
        "validate_decision_table_lookups": {
            "description": "When true, ensure lookup DecisionTable records referenced by expression sets exist.",
            "required": False,
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
        validate_decision_tables = (
            str(self.options.get("validate_decision_table_lookups", "true")).lower()
            == "true"
        )
        decision_table_names = (
            self._discover_lookup_decision_tables()
            if validate_decision_tables
            else []
        )

        missing = self._get_missing_schedules(schedule_names)
        missing_decision_tables = (
            self._get_missing_decision_tables(decision_table_names)
            if decision_table_names
            else []
        )
        if not missing and not missing_decision_tables:
            self.logger.info(
                "PriceAdjustmentSchedule and expression-set DecisionTable lookups are present."
            )
            return

        if missing:
            self.logger.warning(
                "Missing PriceAdjustmentSchedule records: %s", ", ".join(missing)
            )
        if missing_decision_tables:
            self.logger.warning(
                "Missing DecisionTable lookups used by expression sets: %s",
                ", ".join(missing_decision_tables),
            )
        self.logger.info(
            "Toggling pricing setting to regenerate missing pricing artifacts."
        )

        self._deploy_settings(self.options["disable_settings_path"])
        self._deploy_settings(self.options["enable_settings_path"])

        attempts = int(self.options.get("poll_attempts") or 6)
        interval = int(self.options.get("poll_interval_seconds") or 10)
        missing_after = []
        missing_decision_tables_after = []
        for attempt in range(1, attempts + 1):
            time.sleep(interval)
            missing_after = self._get_missing_schedules(schedule_names)
            missing_decision_tables_after = (
                self._get_missing_decision_tables(decision_table_names)
                if decision_table_names
                else []
            )
            if not missing_after and not missing_decision_tables_after:
                break
            if missing_after:
                self.logger.warning(
                    "Pricing schedules still missing (attempt %s/%s): %s",
                    attempt,
                    attempts,
                    ", ".join(missing_after),
                )
            if missing_decision_tables_after:
                self.logger.warning(
                    "Decision table lookups still missing (attempt %s/%s): %s",
                    attempt,
                    attempts,
                    ", ".join(missing_decision_tables_after),
                )

        if missing_after or missing_decision_tables_after:
            details = []
            if missing_after:
                details.append(
                    "PriceAdjustmentSchedule: " + ", ".join(missing_after)
                )
            if missing_decision_tables_after:
                details.append(
                    "DecisionTable: " + ", ".join(missing_decision_tables_after)
                )
            raise TaskOptionsError(
                "Pricing dependencies still missing after toggle: " + " | ".join(details)
            )

        self.logger.info("Pricing dependencies are available after toggle.")

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

    def _discover_lookup_decision_tables(self) -> List[str]:
        metadata_path = self.options.get(
            "expression_sets_metadata_path",
            "force-app/main/default/expressionSetDefinition",
        )
        metadata_dir = Path(metadata_path)
        if not metadata_dir.is_absolute():
            metadata_dir = Path.cwd() / metadata_dir
        if not metadata_dir.exists() or not metadata_dir.is_dir():
            raise TaskOptionsError(
                f"expression_sets_metadata_path is invalid: {metadata_dir}"
            )

        ns = {"md": "http://soap.sforce.com/2006/04/metadata"}
        lookup_api_names: List[str] = []
        for xml_file in sorted(
            metadata_dir.glob("*.expressionSetDefinition-meta.xml")
        ):
            root = ET.parse(xml_file).getroot()
            params = root.findall(".//md:versions/md:steps/md:customElement/md:parameters", ns)
            for param in params:
                name_el = param.find("md:name", ns)
                value_el = param.find("md:value", ns)
                type_el = param.find("md:type", ns)
                if (
                    name_el is not None
                    and value_el is not None
                    and type_el is not None
                    and (name_el.text or "").strip() == "LookUpApiName"
                    and (type_el.text or "").strip() == "Literal"
                ):
                    value = (value_el.text or "").strip()
                    if value:
                        lookup_api_names.append(value)

        deduped = list(dict.fromkeys(lookup_api_names))
        self.logger.info(
            "Discovered %s DecisionTable lookup API name(s) from expression set metadata.",
            len(deduped),
        )
        return deduped

    def _get_missing_decision_tables(self, developer_names: List[str]) -> List[str]:
        if not developer_names:
            return []
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        import requests

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

        escaped = [n.replace("'", "\\'") for n in developer_names]
        name_list = "', '".join(escaped)
        soql = (
            "SELECT DeveloperName FROM DecisionTable "
            f"WHERE DeveloperName IN ('{name_list}')"
        )
        url = f"{instance_url}/services/data/v{api_version}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params={"q": soql})
        if not response.ok:
            raise TaskOptionsError(
                f"Failed to query DecisionTable: {response.text}"
            )
        records = response.json().get("records", [])
        found_names = {
            r.get("DeveloperName") for r in records if r.get("DeveloperName")
        }
        return [name for name in developer_names if name not in found_names]
