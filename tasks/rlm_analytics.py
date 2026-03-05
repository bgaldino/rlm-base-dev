"""Enable the Data Sync and Connections toggle (enableWaveReplication) via Robot Framework.

Runs the enable_analytics Robot test with the flow's org so the browser
session is authenticated via sf org open --url-only. Enables the
"Enable Data Sync and Connections" checkbox on the Analytics/Insights Settings
page. Required before rating-related data loads that depend on the Wave
replication engine. Does not require enabling the full CRM Analytics feature.
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

# Relative to repo root (project_config.repo_root when running under CCI)
DEFAULT_SUITE = "robot/rlm-base/tests/setup/enable_analytics.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class EnableAnalyticsReplication(BaseTask):
    """Run the Robot test that enables the Data Sync and Connections toggle (enableWaveReplication)."""

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite (enable_analytics).",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="EnableAnalyticsReplication")
        # sf org open -o requires a value the CLI knows: username or CLI alias.
        # CCI org name (e.g. beta) is not always registered in the CLI; username is.
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "EnableAnalyticsReplication requires an org (run as part of a flow with --org, or set org_config)."
            )

        repo_root = Path(self.project_config.repo_root)
        suite = self.options.get("suite") or DEFAULT_SUITE
        suite_path = repo_root / suite
        if not suite_path.exists():
            raise TaskOptionsError(
                f"Robot suite not found at expected path: {suite_path}. "
                f"Path is resolved relative to the repo root ({repo_root}). "
                "Override with the 'suite' task option, e.g.: "
                "cci task run enable_analytics_replication --suite path/to/enable_analytics.robot"
            )

        outputdir = self.options.get("outputdir") or DEFAULT_OUTPUT_DIR
        out_path = repo_root / outputdir
        out_path.mkdir(parents=True, exist_ok=True)

        # Use same Python as CCI (e.g. pipx venv) so injected robot package is found
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
            "Running Enable Data Sync and Connections (enableWaveReplication) test for org %s: %s",
            org_name,
            " ".join(cmd),
        )
        result = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.error("Robot stdout: %s", result.stdout)
            self.logger.error("Robot stderr: %s", result.stderr)
            log_file = out_path / "log.html"
            detail = (
                f"Check {log_file} for details."
                if log_file.exists()
                else "Robot log not generated — check console output above for details."
            )
            raise RuntimeError(
                f"Enable Data Sync and Connections test failed (exit code {result.returncode}). "
                + detail
            )
        self.logger.info(
            "Data Sync and Connections (enableWaveReplication) enabled successfully."
        )
