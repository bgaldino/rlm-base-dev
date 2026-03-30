"""Run E2E functional tests via Robot Framework.

Passes the org identifier (username or alias), feature flags, and browser
mode to Robot Framework test suites. Feature flags are read from the CCI
project custom settings and injected as Robot variables so tests can use
``Skip If`` to gate on feature availability.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object  # type: ignore
    TaskOptionsError = Exception  # type: ignore

from tasks.robot_utils import check_urllib3_for_robot

DEFAULT_SUITE = "robot/rlm-base/tests/e2e"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"

# Feature flags to pass from project__custom to Robot variables
FEATURE_FLAGS = [
    "qb", "billing", "constraints", "dro", "clm", "rating", "rates",
    "ramps", "payments", "approvals", "docgen", "prm", "commerce",
    "guidedselling", "tso", "ux",
]


class RunE2ETests(BaseTask):
    """Run end-to-end Robot Framework tests with org and feature flag context."""

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite or directory.",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
        "headed": {
            "description": (
                "Run Chrome in headed (visible) mode with CDP debugging port 9222. "
                "Default: false (headless)."
            ),
            "required": False,
        },
        "include_tags": {
            "description": "Comma-separated Robot tags to include (--include).",
            "required": False,
        },
        "exclude_tags": {
            "description": "Comma-separated Robot tags to exclude (--exclude).",
            "required": False,
        },
        "pause_for_recording": {
            "description": (
                "Pause at key steps for DOM inspection via Chrome DevTools. "
                "Only effective when headed=true. Default: false."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        check_urllib3_for_robot(task_name="RunE2ETests")

        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "RunE2ETests requires an org "
                "(run with --org or set org_config)."
            )

        repo_root = Path(self.project_config.repo_root)
        suite = self.options.get("suite") or DEFAULT_SUITE
        suite_path = repo_root / suite
        if not suite_path.exists():
            raise TaskOptionsError(
                f"Robot suite not found at path: {suite_path}. "
                "Check the 'suite' task option or update the default suite path."
            )

        outputdir = self.options.get("outputdir") or DEFAULT_OUTPUT_DIR
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = repo_root / outputdir / f"e2e_{timestamp}"
        out_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "robot",
            "--variable",
            f"ORG_ALIAS:{org_name}",
        ]

        # Pass headed/debug mode
        headed = str(self.options.get("headed", "false")).lower() == "true"
        if headed:
            cmd.extend(["--variable", "HEADED:true"])
        pause = str(self.options.get("pause_for_recording", "false")).lower() == "true"
        if pause and headed:
            cmd.extend(["--variable", "PAUSE_FOR_RECORDING:true"])
        elif pause and not headed:
            self.logger.warning(
                "pause_for_recording was requested but headed=false; "
                "ignoring PAUSE_FOR_RECORDING to avoid hanging headless/CI runs."
            )

        # Pass feature flags from project custom settings
        custom = getattr(self.project_config, "project__custom", {}) or {}
        for flag in FEATURE_FLAGS:
            value = custom.get(flag, False)
            robot_value = "true" if value else "false"
            cmd.extend(["--variable", f"{flag.upper()}:{robot_value}"])

        # Tag filtering
        include_tags = self.options.get("include_tags")
        if include_tags:
            for tag in include_tags.split(","):
                tag = tag.strip()
                if tag:
                    cmd.extend(["--include", tag])

        exclude_tags = self.options.get("exclude_tags")
        if exclude_tags:
            for tag in exclude_tags.split(","):
                tag = tag.strip()
                if tag:
                    cmd.extend(["--exclude", tag])

        cmd.extend([
            "--outputdir",
            str(out_path),
            str(suite_path),
        ])

        self.logger.info(
            "Running E2E tests for org %s: %s",
            org_name,
            " ".join(cmd),
        )
        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )

        # Always log output for visibility
        if result.stdout:
            self.logger.info("Robot stdout:\n%s", result.stdout)
        if result.stderr:
            self.logger.info("Robot stderr:\n%s", result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                f"E2E tests failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info("E2E tests passed successfully.")
