"""Enable constraints settings on Revenue Settings via Robot Framework.

Sets the Default Transaction Type to "Advanced Configurator", sets the
Asset Context for Product Configurator, and enables the "Set Up
Configuration Rules and Constraints with Constraints Engine" toggle.
Must run before constraint data can be imported (CML import steps).

Follows the same pattern as rlm_enable_document_builder_toggle.py.
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

DEFAULT_SUITE = "robot/rlm-base/tests/setup/enable_constraints_settings.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class EnableConstraintsSettings(BaseSalesforceTask):
    """Run the Robot test that configures constraints prerequisites on Revenue Settings.

    Sets Default Transaction Type to 'Advanced Configurator', sets the Asset
    Context for Product Configurator, and enables the Constraints Engine toggle.
    Required before CML import tasks can run.
    """

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite (enable_constraints_settings).",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
        "default_transaction_type": {
            "description": "Value for the Default Transaction Type dropdown.",
            "required": False,
        },
        "asset_context": {
            "description": "Name of the Asset Context to set for Product Configurator.",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot()
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "EnableConstraintsSettings requires an org (run as part of a flow "
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

        if self.options.get("default_transaction_type"):
            cmd.extend(["--variable", f"DEFAULT_TRANSACTION_TYPE_VALUE:{self.options['default_transaction_type']}"])
        if self.options.get("asset_context"):
            cmd.extend(["--variable", f"ASSET_CONTEXT:{self.options['asset_context']}"])

        cmd.extend([
            "--outputdir",
            str(out_path),
            str(suite_path),
        ])

        self.logger.info(
            "Running enable constraints settings test for org %s: %s",
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
                f"Enable constraints settings test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info(
            "Constraints settings configured: Default Transaction Type, "
            "Asset Context, and Constraints Engine toggle set."
        )
