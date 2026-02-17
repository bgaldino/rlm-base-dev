"""Configure Revenue Settings page via Robot Framework.

Sets default procedures (Pricing, Usage Rating), enables Instant Pricing,
and sets the Create Orders from Quote screen flow. Must run after all
data/metadata is deployed and before decision table refresh.
Asset Context is configured separately via enable_constraints_settings.

Follows the same pattern as rlm_enable_constraints_settings.py.
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


DEFAULT_SUITE = "robot/rlm-base/tests/setup/configure_revenue_settings.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class ConfigureRevenueSettings(BaseSalesforceTask):
    """Run the Robot test that configures Revenue Settings page defaults.

    Sets default Pricing Procedure, Usage Rating Procedure, enables Instant
    Pricing, and sets the Create Orders from Quote flow.
    Required before decision table refresh can run successfully.
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
            "description": "Name of the default Pricing Procedure to set.",
            "required": False,
        },
        "usage_rating_procedure": {
            "description": "Name of the default Usage Rating Procedure to set.",
            "required": False,
        },
        "create_orders_flow": {
            "description": "API name of the Create Orders from Quote screen flow.",
            "required": False,
        },
    }

    def _run_task(self):
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "ConfigureRevenueSettings requires an org (run as part of a flow "
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

        # Pass optional overrides as Robot variables
        if self.options.get("pricing_procedure"):
            cmd.extend(["--variable", f"PRICING_PROCEDURE:{self.options['pricing_procedure']}"])
        if self.options.get("usage_rating_procedure"):
            cmd.extend(["--variable", f"USAGE_RATING_PROCEDURE:{self.options['usage_rating_procedure']}"])
        if self.options.get("create_orders_flow"):
            cmd.extend(["--variable", f"CREATE_ORDERS_FLOW:{self.options['create_orders_flow']}"])

        cmd.extend([
            "--outputdir",
            str(out_path),
            str(suite_path),
        ])

        self.logger.info(
            "Running configure revenue settings test for org %s: %s",
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
                f"Configure revenue settings test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info(
            "Revenue Settings configured: Pricing Procedure, Usage Rating, "
            "Instant Pricing, and Create Orders Flow set."
        )
