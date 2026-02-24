"""Enable the Document Builder toggle on Revenue Settings via Robot Framework.

Runs the enable_document_builder Robot test with the flow's org so the browser
session is authenticated via sf org open --url-only. Required before
deploy_post_docgen when the org does not have Document Builder enabled via metadata.
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


# Relative to repo root (project_config.repo_root when running under CCI)
DEFAULT_SUITE = "robot/rlm-base/tests/setup/enable_document_builder.robot"
DEFAULT_OUTPUT_DIR = "robot/rlm-base/results"


def _check_urllib3_for_robot():
    """Fail fast with a clear message if urllib3 2.x is installed (causes Timeout value connect error)."""
    try:
        import urllib3
        ver = getattr(urllib3, "__version__", "0")
        major = int(ver.split(".")[0])
        if major >= 2:
            raise TaskOptionsError(
                "urllib3 2.x is installed; it causes the 'Timeout value connect was <object object at ...>' error "
                "when running Robot setup tests. Pin urllib3 to 1.x in this environment (e.g. pip install \"urllib3>=1.26,<2\" "
                "or pip install -r robot/requirements.txt). See README Troubleshooting for details."
            )
    except (ImportError, ValueError):
        pass


class EnableDocumentBuilderToggle(BaseTask):
    """Run the Robot test that enables the Document Builder toggle on Revenue Settings."""

    task_options = {
        "suite": {
            "description": "Path to the Robot test suite (enable_document_builder).",
            "required": False,
        },
        "outputdir": {
            "description": "Directory for Robot output (log.html, report.html, output.xml).",
            "required": False,
        },
    }

    def _run_task(self):
        _check_urllib3_for_robot()
        # sf org open -o requires a value the CLI knows: username or CLI alias.
        # CCI org name (e.g. tfid-cdo) is not always in the CLI; username is.
        org_name = getattr(self.org_config, "username", None)
        if not org_name:
            org_name = getattr(self.org_config, "name", None) or getattr(
                self.org_config, "alias", None
            )
        if not org_name:
            raise TaskOptionsError(
                "EnableDocumentBuilderToggle requires an org (run as part of a flow with --org, or set org_config)."
            )

        repo_root = Path(self.project_config.repo_root)
        suite = self.options.get("suite") or DEFAULT_SUITE
        suite_path = repo_root / suite
        if not suite_path.exists():
            raise FileNotFoundError(f"Robot suite not found: {suite_path}")

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
            "Running enable Document Builder toggle test for org %s: %s",
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
                f"Enable Document Builder toggle test failed (exit code {result.returncode}). "
                f"Check {out_path / 'log.html'} for details."
            )
        self.logger.info("Document Builder toggle enabled successfully.")
