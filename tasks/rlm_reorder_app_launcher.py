"""Reorder the App Launcher via the Aura AppLauncherController/saveOrder API.

Salesforce blocks AppSwitcher Metadata API deployment on orgs whose AppMenu
contains managed ConnectedApp or Network entries (Trialforce-based scratch orgs).
AppMenuItem.SortOrder is read-only via Tooling API, REST, and Apex. The only
path is browser automation against the App Launcher modal, which this task wraps.

The Robot suite opens the Lightning home page, clicks the waffle icon, opens
"View All", reads all tile IDs from the shadow DOM, and calls saveOrder directly
via synchronous XHR — no drag required.
"""

import subprocess
import sys
from pathlib import Path

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

        cmd = [
            sys.executable,
            "-m",
            "robot",
            "--variable",
            f"ORG_ALIAS:{org_name}",
            "--variable",
            f"PRIORITY_APP_LABELS:{priority_labels}",
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
