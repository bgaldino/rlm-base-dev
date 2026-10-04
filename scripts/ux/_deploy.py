"""Deploy assembled UX metadata with ``sf project deploy start``.

The target is an sf CLI alias or username (``--target-org``), never a CCI
alias and never an access token. The CCI wrapper passes
``org_config.username``.
"""
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.ux._context import UxError, UxOptionError
from scripts.ux._sf import cli_error, run_sf_json


def deploy(
    output_path: Path,
    target_org: str,
    logger: Optional[logging.Logger] = None,
    timeout: int = 600,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """Deploy ``output_path`` to ``target_org``; return the sf ``result`` payload.

    ``cwd`` is the sf project root (the directory holding sfdx-project.json);
    sf resolves ``--source-dir`` against the project there.
    """
    logger = logger or logging.getLogger("rlm_ux")
    if not target_org:
        raise UxOptionError("No target org given. Cannot deploy without a target org.")
    if not Path(output_path).is_dir():
        raise UxOptionError(f"Nothing to deploy: {output_path} does not exist.")

    logger.info(f"Deploying {output_path} → {target_org}")
    output = run_sf_json(
        [
            "project", "deploy", "start",
            "--source-dir", str(output_path),
            "--target-org", target_org,
            "--ignore-conflicts",
        ],
        cwd=cwd,
        timeout=timeout,
        logger=logger,
    )

    status = output.get("status", -1)
    deploy_result = output.get("result", {}) or {}
    deploy_status = deploy_result.get("status", "Unknown")

    # SucceededPartial means some components failed: treat it as a failure.
    if status != 0 or deploy_status != "Succeeded":
        # Surface CLI-level errors (e.g. MissingPackageDirectoryError) that
        # occur before a deploy job is created — result will be empty.
        cli_message = cli_error(output)

        errors = deploy_result.get("details", {}).get("componentFailures", [])
        if isinstance(errors, dict):
            errors = [errors]

        err_msgs = [
            f"  {e.get('componentType')}/{e.get('fullName')}: {e.get('problem')}"
            for e in errors[:20]
        ]

        if cli_message and not err_msgs:
            err_msgs = [f"  {cli_message}"]

        raise UxError(
            f"Deployment failed (status={deploy_status}).\n"
            + "\n".join(err_msgs)
        )

    deployed_count = deploy_result.get("numberComponentsDeployed", 0)
    logger.info(
        f"Deployment succeeded: {deployed_count} component(s) deployed (status={deploy_status})"
    )
    return deploy_result
