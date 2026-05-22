"""Configure Product Discovery Settings page via Robot Framework.

Sets the Default Catalog to the specified catalog name (default: "QuantumBit Software").
Must run after QB product catalog data has been loaded so the catalog record exists.

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

DEFAULT_SUITE = "robot/rlm-base/tests/setup/configure_product_discovery_settings.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"
DEFAULT_CATALOG = "QuantumBit Software"


class ConfigureProductDiscoverySettings(BaseSalesforceTask):
    """Run the Robot test that sets the Default Catalog on Product Discovery Settings.

    Navigates to /lightning/setup/ProductDiscoverySettings/home and sets the
    "Select Default Catalog" combobox to the configured catalog name. The page
    auto-saves on selection (no explicit Save button needed).
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
        "default_catalog": {
            "description": "Name of the Default Catalog to select in ProductDiscoverySettings.",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="ConfigureProductDiscoverySettings")
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "ConfigureProductDiscoverySettings requires an org (run as part of a flow "
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

        catalog = self.options.get("default_catalog") or DEFAULT_CATALOG

        cmd = [
            sys.executable,
            "-m",
            "robot",
            "--variable",
            f"ORG_ALIAS:{org_name}",
            "--variable",
            f"DEFAULT_CATALOG:{catalog}",
            "--outputdir",
            str(out_path),
            str(suite_path),
        ]

        self.logger.info(
            "Running configure product discovery settings test for org %s: %s",
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
                f"Configure product discovery settings test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info(
            "Product Discovery Settings configured: Default Catalog set to '%s'.", catalog
        )
