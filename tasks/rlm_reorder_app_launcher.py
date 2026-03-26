"""Reorder the App Launcher via the Aura AppLauncherController/saveOrder API.

Salesforce blocks AppSwitcher Metadata API deployment on orgs whose AppMenu
contains managed ConnectedApp or Network entries. AppMenuItem.SortOrder is also
read-only via Tooling API, REST, and Apex.

The Robot suite navigates to the Lightning home page, queries all AppMenuItem
records via the Salesforce REST API (SOQL), builds a priority-ordered ID list,
and calls the Aura AppLauncherController/saveOrder action directly via sync XHR.
No modal or DOM scraping required.
"""

import subprocess
import sys
from pathlib import Path

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object  # type: ignore
    TaskOptionsError = Exception  # type: ignore

from tasks.robot_utils import check_urllib3_for_robot

DEFAULT_SUITE = "robot/rlm-base/tests/setup/reorder_app_launcher.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"
DEFAULT_PRIORITY_LABELS = (
    "Revenue Cloud,"
    "Billing,"
    "Product Catalog Management,"
    "Price Management,"
    "Dynamic Revenue Orchestrator,"
    "Rate Management,"
    "Usage Management,"
    "Approvals,"
    "Salesforce Contracts,"
    "Payments,"
    "Collections,"
    "Revenue Cloud Operations Console"
)


class ReorderAppLauncher(BaseTask):
    """Run the Robot test that applies a priority order to the App Launcher."""

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite (reorder_app_launcher).",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
        "priority_app_labels": {
            "description": (
                "Comma-separated display labels of apps to place first in the App Launcher, "
                "in the desired order. Labels are the display names shown in the App Launcher "
                "(e.g. 'Revenue Cloud', not 'RLM_Revenue_Cloud'). "
                "Apps not in this list follow in their current relative order. "
                f"Default: '{DEFAULT_PRIORITY_LABELS}'."
            ),
            "required": False,
        },
    }

    def _build_ordered_app_ids(self, priority_labels_str: str, api_version: str) -> str:
        """Query AppMenuItem via REST API and return priority-ordered ApplicationIds.

        Runs in Python (has access_token + instance_url) to avoid cross-origin XHR
        issues from browser JS (Lightning on *.lightning.force.com, REST API on
        *.my.salesforce.com).

        Returns a comma-separated string of ApplicationId values, priority apps first.
        """
        instance_url = self.org_config.instance_url.rstrip("/")
        access_token = self.org_config.access_token

        soql = (
            "SELECT ApplicationId, Label, SortOrder "
            "FROM AppMenuItem "
            "WHERE IsVisible=true "
            "ORDER BY SortOrder"
        )
        resp = requests.get(
            f"{instance_url}/services/data/v{api_version}/query",
            params={"q": soql},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        records = resp.json().get("records", [])

        priority_list = [l.strip() for l in priority_labels_str.split(",") if l.strip()]
        priority_map = {label: i for i, label in enumerate(priority_list)}

        priority_ids: list = [None] * len(priority_list)
        remaining_ids: list = []
        matched = []
        for rec in records:
            label = rec.get("Label", "")
            app_id = rec.get("ApplicationId", "")
            if not app_id:
                continue
            idx = priority_map.get(label)
            if idx is not None:
                priority_ids[idx] = app_id
                matched.append(label)
            else:
                remaining_ids.append(app_id)

        unmatched = [l for l in priority_list if l not in matched]
        if unmatched:
            self.logger.warning(
                "Priority app(s) not found in AppMenuItem (will be skipped): %s",
                ", ".join(unmatched),
            )

        ordered = [i for i in priority_ids if i is not None] + remaining_ids
        return ",".join(ordered)

    def _run_task(self):
        check_urllib3_for_robot(task_name="ReorderAppLauncher")

        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "ReorderAppLauncher requires an org (run as part of a flow with --org, "
                "or set org_config)."
            )

        repo_root = Path(self.project_config.repo_root)
        suite = self.options.get("suite") or DEFAULT_SUITE
        suite_path = repo_root / suite
        if not suite_path.exists():
            raise FileNotFoundError(f"Robot suite not found: {suite_path}")

        outputdir = self.options.get("outputdir") or DEFAULT_OUTPUT_DIR
        out_path = repo_root / outputdir
        out_path.mkdir(parents=True, exist_ok=True)

        priority_labels = self.options.get("priority_app_labels") or DEFAULT_PRIORITY_LABELS

        api_version = getattr(self.project_config, "project__package__api_version", None)
        if not api_version:
            raise TaskOptionsError(
                "project.package.api_version is not set in cumulusci.yml"
            )

        ordered_ids = self._build_ordered_app_ids(priority_labels, api_version)
        ordered_list = [i for i in ordered_ids.split(",") if i]
        self.logger.info(
            "App order resolved: %d total app(s) queued for reorder.",
            len(ordered_list),
        )

        cmd = [
            sys.executable,
            "-m",
            "robot",
            "--variable",
            f"ORG_ALIAS:{org_name}",
            "--variable",
            f"ORDERED_APP_IDS:{ordered_ids}",
            "--outputdir",
            str(out_path),
            str(suite_path),
        ]
        self.logger.info(
            "Reordering App Launcher for org %s: %s",
            org_name,
            " ".join(cmd),
        )
        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.logger.error("Robot stdout: %s", result.stdout[-3000:])
            self.logger.error("Robot stderr: %s", result.stderr[-1000:])
            raise RuntimeError(
                f"App Launcher reorder Robot test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info("App Launcher reordered successfully.")
