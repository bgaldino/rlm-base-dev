"""Configure Billing Email Delivery Settings via Robot Framework.

Cycles the "Configure Email Delivery Settings" toggle on the Billing Settings
Lightning Setup page (/lightning/setup/BillingSettings/home) via browser automation.

The Metadata API toggle cycling in prepare_billing (steps 9→10: disable then re-enable
enableInvoiceEmailDelivery) sets the BillingSettings boolean but does not trigger the
Salesforce backend logic that auto-creates the default invoice email template and
sets BillingSettings.defaultEmailTemplate. A UI toggle cycle (off then on) is required.

This task is idempotent: the Robot toggle keywords check current toggle state before
clicking (skipping the click if already in the target state), and the post-cycle
verification polls until the Default Invoice Email Template field is populated.
"""

import subprocess
import sys
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object  # type: ignore
    TaskOptionsError = Exception  # type: ignore

from tasks.robot_utils import check_urllib3_for_robot

DEFAULT_SUITE = "robot/rlm-base/tests/setup/configure_billing_email_settings.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class ConfigureBillingEmailSettings(BaseSalesforceTask):
    """Run the Robot test that cycles the Billing Email Delivery Settings toggle.

    Navigates to /lightning/setup/BillingSettings/home and cycles the
    "Configure Email Delivery Settings" toggle off→on to trigger auto-creation
    of the default invoice email template. Skips if the template already exists.
    """

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite.",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="ConfigureBillingEmailSettings")
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "ConfigureBillingEmailSettings requires an org (run as part of a flow "
                "with --org, or set org_config)."
            )

        repo_root = Path(self.project_config.repo_root)
        suite = self.options.get("suite") or DEFAULT_SUITE
        suite_path = repo_root / suite
        if not suite_path.exists():
            raise FileNotFoundError(f"Robot suite not found: {suite_path}")

        outputdir = self.options.get("outputdir") or DEFAULT_OUTPUT_DIR
        out_path = repo_root / outputdir
        out_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "robot",
            "--variable",
            f"ORG_ALIAS:{org_name}",
            "--outputdir",
            str(out_path),
            str(suite_path),
        ]

        self.logger.info(
            "Running configure billing email settings test for org %s: %s",
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
            self.logger.error("Robot stdout: %s", result.stdout)
            self.logger.error("Robot stderr: %s", result.stderr)
            raise RuntimeError(
                f"Configure billing email settings test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info(
            "Billing Email Delivery Settings configured: default invoice email template created or already present."
        )
