"""Enable the Timeline feature toggle at Setup → Feature Settings → Timeline via Robot Framework.

Runs the enable_timeline Robot test with the flow's org so the browser session is
authenticated via sf org open --url-only. Required before billing_ui flexipages that
reference industries_common:timeline can be deployed. Once enabled, the toggle cannot
be disabled.
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

DEFAULT_SUITE = "robot/rlm-base/tests/setup/enable_timeline.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


class EnableTimeline(BaseTask):
    """Run the Robot test that enables the Timeline feature toggle in Setup."""

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite (enable_timeline).",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="EnableTimeline")
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "EnableTimeline requires an org (run as part of a flow with --org, or set org_config)."
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
            "Running enable Timeline toggle test for org %s: %s",
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
                f"Enable Timeline toggle test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info("Timeline feature enabled successfully.")
