import json
import os
import shlex
import subprocess
import time
from typing import List
from pathlib import Path
import xml.etree.ElementTree as ET

# Import before CumulusCI: cumulusci's project_config does sys.modules.setdefault("tasks", <synthetic>) and then
# sets tasks.__path__ = [], which empties the repo package's path, so a later `tasks.soql_utils` import fails.
from tasks.soql_utils import option_flag, option_text, positive_int, project_api_version, requested_names, soql_quote

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class EnsurePricingSchedules(BaseSalesforceTask):
    """Ensure PriceAdjustmentSchedule records exist; toggle pricing if missing."""

    task_options = {
        "schedule_names": {
            "description": "PriceAdjustmentSchedule names to verify, a list or comma-separated. Blank is the three Standard schedules.",
            "required": False,
        },
        "poll_attempts": {
            "description": "Number of times to poll after toggle. Default 6, also when blank; anything but a positive integer is refused.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds to wait between polls. Default 10, also when blank; anything but a positive integer is refused.",
            "required": False,
        },
        "disable_settings_path": {
            "description": "Path to the settings bundle or file that disables pricing; keep it to the Pricing "
            "settings so the toggle changes nothing else.",
            "required": True,
        },
        "enable_settings_path": {
            "description": "Path to the settings bundle or file that enables pricing; keep it to the Pricing "
            "settings so the toggle and its restore command change nothing else.",
            "required": True,
        },
        "expression_sets_metadata_path": {
            "description": "Path to expression set metadata used to discover DecisionTable lookup API names.",
            "required": False,
        },
        "validate_decision_table_lookups": {
            "description": "When true, ensure lookup DecisionTable records referenced by expression sets exist. Default true, also when blank; a list or an unparseable value is refused.",
            "required": False,
        },
    }

    DEFAULT_SCHEDULE_NAMES = [
        "Standard Attribute Based Adjustment",
        "Standard Price Adjustment Tier",
        "Standard Bundle Based Adjustment",
    ]

    def _positive_option(self, name: str, default: int) -> int:
        text = option_text(self.options.get(name), name, TaskOptionsError)
        return default if text is None else positive_int(text, name, TaskOptionsError)

    def _run_task(self):
        # Every option is read before the first query (poll_attempts and poll_interval_seconds were
        # read after the two settings deploys). None, blank or whitespace is the default; a list for a
        # scalar, a value outside CumulusCI's boolean vocabulary, a non-positive number, or a schedule
        # name that is not a string is refused by name.
        # schedule_names: a list or comma-separated; a string used to be iterated character by character.
        schedule_names = (
            requested_names(self.options.get("schedule_names"), "schedule_names", TaskOptionsError)
            or list(self.DEFAULT_SCHEDULE_NAMES)
        )
        validate_decision_tables = option_flag(
            self.options.get("validate_decision_table_lookups"), "validate_decision_table_lookups",
            TaskOptionsError, default=True,
        )
        attempts = self._positive_option("poll_attempts", 6)
        interval = self._positive_option("poll_interval_seconds", 10)
        decision_table_names = (
            self._discover_lookup_decision_tables()
            if validate_decision_tables
            else []
        )

        enable_path = self.options["enable_settings_path"]

        pricing_was_off = False
        try:
            missing = self._get_missing_schedules(schedule_names)
        except TaskOptionsError:
            if self._probe_pricing(enable_path, "checking whether Pricing is on") != "off":
                raise
            # An earlier toggle was left half done: skip the disable and turn Pricing back on.
            pricing_was_off = True
            missing = []
            self.logger.warning(
                "Pricing reads as DISABLED on the org (PriceAdjustmentSchedule is not queryable: Pricing is "
                "off, or this user cannot see the object; an earlier toggle may not have finished); "
                "enabling it."
            )
        # While Pricing is off the polling below does the decision-table check.
        missing_decision_tables = (
            self._get_missing_decision_tables(decision_table_names)
            if decision_table_names and not pricing_was_off
            else []
        )
        if not pricing_was_off and not missing and not missing_decision_tables:
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
        if not pricing_was_off:
            self.logger.info(
                "Toggling pricing setting to regenerate missing pricing artifacts."
            )

        self._require_username()
        if not pricing_was_off:
            try:
                self._deploy_settings(self.options["disable_settings_path"])
            except TaskOptionsError as error:
                # A deploy that reports failure can still have landed: say what the org reads as.
                state = self._probe_pricing(enable_path, "checking Pricing after a failed disable deploy")
                lead = self._sentence(error)
                if state == "off":
                    message = (
                        f"{lead}Pricing now reads as DISABLED on the org (the disable deploy reported failure "
                        f"but landed); {self._restore_hint(enable_path)}"
                    )
                elif state == "unknown":
                    message = (
                        f"{lead}Pricing may now be off on the org; if it is, {self._restore_hint(enable_path)}"
                    )
                else:
                    message = (
                        f"{lead}Pricing reads as enabled, but the deploy may still be finishing on the org; "
                        "check Pricing before rerunning. If it turns off, a rerun of this task re-enables it."
                    )
                raise TaskOptionsError(message) from error
            except BaseException:
                self.logger.error(
                    "Stopped while disabling pricing, which may now be off; if it is, %s",
                    self._restore_hint(enable_path),
                )
                raise
        self._enable_pricing_or_explain(enable_path, interval, disabled_here=not pricing_was_off)
        missing_after = []
        missing_decision_tables_after = []
        pricing_off = False
        for attempt in range(1, attempts + 1):
            time.sleep(interval)
            try:
                missing_after = self._get_missing_schedules(schedule_names)
            except (TaskOptionsError, OSError, ValueError) as error:
                # The type can take a moment to become queryable after the enable deploy; a dropped
                # connection (requests errors are OSErrors) or a non-JSON error page is as transient.
                state = self._probe_pricing(enable_path, "waiting for Pricing to come back")
                pricing_off = state == "off"
                if state == "unknown" and attempt == attempts:
                    raise TaskOptionsError(
                        f"{self._sentence(error)}Pricing may still be off on the org; if it is, "
                        + self._restore_hint(enable_path)
                    ) from error
                if state == "on" and attempt == attempts:
                    raise
                self.logger.warning(
                    "Schedule query failed while Pricing reads as %s (attempt %s/%s): %s",
                    state, attempt, attempts, error,
                )
                continue
            pricing_off = False
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

        if pricing_off:
            raise TaskOptionsError(
                "Pricing still reads as DISABLED on the org after the toggle (PriceAdjustmentSchedule is not "
                "queryable: Pricing is off, or this user cannot see the object); "
                + self._restore_hint(enable_path)
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
        if not schedule_names:
            return []

        import requests

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            project_api_version(self.project_config, TaskOptionsError, "68.0")
        )

        name_list = ", ".join(soql_quote(n) for n in schedule_names)
        soql = (
            "SELECT Name FROM PriceAdjustmentSchedule "
            f"WHERE Name IN ({name_list})"
        )
        url = f"{instance_url}/services/data/v{api_version}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params={"q": soql}, timeout=30)
        if not response.ok:
            raise TaskOptionsError(
                f"Failed to query PriceAdjustmentSchedule: {response.text}"
            )

        records = response.json().get("records", [])
        found_names = {r.get("Name") for r in records if r.get("Name")}
        return [n for n in schedule_names if n not in found_names]

    def _enable_pricing_or_explain(self, settings_path: str, interval: int, disabled_here: bool = True):
        """Deploy the enable bundle, retrying once after a pause.

        disabled_here: this run's disable deploy turned Pricing off (False when the run found it already off).
        """
        cause = (
            "the disable deploy succeeded and the enable deploy failed twice"
            if disabled_here
            else "it was already off and the enable deploy failed twice"
        )
        for attempt in (1, 2):
            try:
                if attempt == 2:
                    time.sleep(interval)
                self._deploy_settings(settings_path)
                return
            except TaskOptionsError as error:
                if attempt == 1:
                    self.logger.warning(
                        "Enabling pricing failed; retrying once: %s", error
                    )
                    continue
                state = self._probe_pricing(settings_path, "checking Pricing after the enable deploy failed twice")
                if state == "on":
                    # A deploy that reports failure can still have landed; polling reports what is missing.
                    self.logger.warning(
                        "The enable deploy failed twice, but Pricing reads as enabled on the org: %s", error
                    )
                    return
                if state == "off":
                    lead = f"Pricing reads as DISABLED on the org: {cause}"
                else:
                    lead = f"Pricing may be DISABLED on the org: {cause}, and the setting could not be read"
                raise TaskOptionsError(
                    f"{lead}. Deploy error: {self._sentence(error)}"
                    f"If Pricing is off, {self._restore_hint(settings_path)}"
                ) from error
            except BaseException:
                self.logger.error(
                    "Stopped while re-enabling pricing, which may now be off; if it is, %s",
                    self._restore_hint(settings_path),
                )
                raise

    @staticmethod
    def _sentence(error) -> str:
        """An error's text as a finished sentence followed by a space."""
        return str(error).rstrip(". \n") + ". "

    def _probe_pricing(self, settings_path: str, doing: str) -> str:
        """_pricing_state, logging the restore command if an interrupt lands while probing."""
        try:
            return self._pricing_state()
        except BaseException:
            self.logger.error(
                "Stopped while %s; Pricing may be off, and if it is, %s", doing, self._restore_hint(settings_path)
            )
            raise

    def _require_username(self) -> str:
        target_org = getattr(self.org_config, "username", None)
        if not target_org:
            raise TaskOptionsError("No target org username available for deploy.")
        return target_org

    def _restore_hint(self, settings_path: str) -> str:
        """Ends with the command on its own line, so copying it picks up no trailing punctuation.

        The path is absolute, resolved the way the deploy resolved it, so the command works from anywhere inside the project.
        """
        target_org = getattr(self.org_config, "username", None)
        return (
            f"restore it with:\n  sf project deploy start --source-dir {shlex.quote(os.path.abspath(settings_path))} "
            f"--target-org {shlex.quote(str(target_org))} --ignore-conflicts"
        )

    def _pricing_state(self) -> str:
        """"on", "off" (PriceAdjustmentSchedule is not a supported type) or "unknown"."""
        try:
            import requests

            api_version = project_api_version(self.project_config, TaskOptionsError, "68.0")
            response = requests.get(
                f"{self.org_config.instance_url}/services/data/v{api_version}/query",
                headers={"Authorization": f"Bearer {self.org_config.access_token}"},
                params={"q": "SELECT Id FROM PriceAdjustmentSchedule LIMIT 1"},
                timeout=30,
            )
            if response.ok:
                return "on"
            codes = {e.get("errorCode") for e in response.json() if isinstance(e, dict)}
            return "off" if "INVALID_TYPE" in codes else "unknown"
        except Exception:  # noqa: BLE001 (only feeds the wording of an error already being raised)
            return "unknown"

    def _deploy_settings(self, settings_path: str):
        target_org = self._require_username()

        cmd = [
            "sf",
            "project",
            "deploy",
            "start",
            "--source-dir",
            settings_path,
            "--target-org",
            target_org,
            # Both bundles carry the same Pricing settings component; without this the
            # second deploy conflicts with the tracking state the first one left.
            "--ignore-conflicts",
            "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise TaskOptionsError(
                f"Deploy failed for {settings_path}: {self._deploy_error(result)}"
            )

    @staticmethod
    def _deploy_error(result) -> str:
        """The failure `sf --json` reports on stdout; stderr carries only warnings such as an update notice."""
        try:
            payload = json.loads(result.stdout or "")
        except ValueError:
            payload = None
        both = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part and part.strip())
        if not isinstance(payload, dict):
            return both
        details = payload.get("result")
        details = details.get("details") if isinstance(details, dict) else None
        failures = (details.get("componentFailures") if isinstance(details, dict) else None) or []
        if isinstance(failures, dict):
            failures = [failures]
        parts = [str(payload.get("message") or "")] + [
            f"{f.get('fullName')}: {f.get('problem')}" for f in failures if isinstance(f, dict)
        ]
        return "; ".join(part for part in parts if part) or both

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
            project_api_version(self.project_config, TaskOptionsError, "68.0")
        )

        name_list = ", ".join(soql_quote(n) for n in developer_names)
        soql = (
            "SELECT DeveloperName FROM DecisionTable "
            f"WHERE DeveloperName IN ({name_list})"
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
