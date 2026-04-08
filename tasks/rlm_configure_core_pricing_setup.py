"""Configure Salesforce Pricing Setup (CorePricingSetup) page via Robot Framework.

Sets the default Pricing Procedure on the CorePricingSetup Lightning Setup page
(/lightning/setup/CorePricingSetup/home). Uses the same anchored default procedure
as configure_revenue_settings (RLM Revenue Management Default Pricing Procedure).

Follows the same pattern as rlm_configure_revenue_settings.py.
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

DEFAULT_SUITE = "robot/rlm-base/tests/setup/configure_core_pricing_setup.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class ConfigureCorePricingSetup(BaseSalesforceTask):
    """Run the Robot test that configures the CorePricingSetup default Pricing Procedure.

    Navigates to /lightning/setup/CorePricingSetup/home and sets the default
    Pricing Procedure to the anchored RLM procedure. Required after the Pricing
    Procedure expression set is deployed and activated.
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
        "pricing_procedure": {
            "description": "Name of the default Pricing Procedure to set on CorePricingSetup.",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="ConfigureCorePricingSetup")
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "ConfigureCorePricingSetup requires an org (run as part of a flow "
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
        ]

        if self.options.get("pricing_procedure"):
            cmd.extend(["--variable", f"PRICING_PROCEDURE:{self.options['pricing_procedure']}"])

        cmd.extend([
            "--outputdir",
            str(out_path),
            str(suite_path),
        ])

        self.logger.info(
            "Running configure core pricing setup test for org %s: %s",
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
                f"Configure core pricing setup test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info(
            "CorePricingSetup configured: default Pricing Procedure set."
        )
