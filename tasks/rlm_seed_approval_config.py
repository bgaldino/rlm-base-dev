"""Seed the RLM_Approval_Config__mdt.Default custom metadata record.

RLM_Approval_Config__mdt is the admin-facing routing toggle for the three
composable approval chains (Discount, Margin, Finance) in
RLM_Quote_Smart_Approval. The Default record is intentionally NOT a static
customMetadata/*.md-meta.xml file in unpackaged/post_approvals: a plain
metadata Deploy upserts any such file's values on every run, which would
silently reset an admin's runtime toggle back to its committed defaults
every time prepare_approvals is rerun against an already-configured org.

Instead this task seeds the Default record once, the first time it is
missing, and never touches it again if it already exists — mirroring the
check-before-create idempotency of create_approval_email_templates (the
next step in the same flow). Record deployment reuses the temp-directory
+ sf CLI mechanism from rlm_stamp_commit.py, inverted from "always
overwrite" (correct for build provenance) to "create only if absent"
(correct for an admin-mutable toggle). Seeded values are per-chain, not
uniformly enabled — see CHAIN_ENABLED_FIELDS below.
"""

import json
import os
import shlex
import shutil
import subprocess
import tempfile

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import CommandException, TaskOptionsError
except ImportError:
    BaseSalesforceTask = object  # type: ignore
    CommandException = Exception  # type: ignore
    TaskOptionsError = Exception  # type: ignore

# Total subprocess timeout for the deploy.
DEPLOY_TIMEOUT_SECONDS = 300
# --wait value passed to sf CLI (minutes); kept slightly below the subprocess
# timeout so the CLI can return its JSON output before being force-killed.
DEPLOY_WAIT_MINUTES = max(1, (DEPLOY_TIMEOUT_SECONDS - 30) // 60)  # 4

DEFAULT_RECORD_DEVELOPER_NAME = "Default"

# Chain-enabled fields and their seeded values. Discount and Finance seed
# true (fail-open: every chain runs unless an admin explicitly disables it).
# Margin seeds false — it ships opt-in only; an admin must explicitly flip
# RLM_Margin_Chain_Enabled__c to true to turn it on. This is a seed-time
# default only: the flow's own fallback (used if the Default record is
# ever missing/deleted entirely) still fails open for Margin, same as the
# other two chains — see RLM_Quote_Approval_Data.flow-meta.xml.
CHAIN_ENABLED_FIELDS = {
    "RLM_Discount_Chain_Enabled__c": True,
    "RLM_Margin_Chain_Enabled__c": False,
    "RLM_Finance_Chain_Enabled__c": True,
}


class SeedApprovalConfig(BaseSalesforceTask):
    """Create RLM_Approval_Config__mdt.Default only if it does not already exist.

    Never updates an existing record — this is the entire mechanism that
    lets an admin's chain-enabled toggles survive every future
    prepare_approvals / prepare_rlm_org rerun.
    """

    _TIMEOUT = 30  # seconds; prevents indefinite hang if Salesforce stalls

    def _run_task(self):
        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError(
                "No org config available. This task requires a connected org."
            )

        org_username = getattr(self.org_config, "username", None)
        if not org_username:
            raise TaskOptionsError(
                "Org config has no username. This task requires an org with a username."
            )

        if self._default_record_exists():
            self.logger.info(
                "RLM_Approval_Config__mdt.Default already exists; skipping seed "
                "(preserving any admin toggles)."
            )
            return

        self.logger.info(
            "RLM_Approval_Config__mdt.Default not found; seeding "
            "Discount/Finance enabled, Margin disabled (opt-in)."
        )
        temp_dir = tempfile.mkdtemp(prefix="rlm_seed_approval_config_")
        try:
            self._write_sfdx_project(temp_dir)
            self._write_cmdt_record(temp_dir)
            self._deploy(temp_dir, org_username)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.logger.info("Seeded RLM_Approval_Config__mdt.Default.")

    # ------------------------------------------------------------------
    # Existence check
    # ------------------------------------------------------------------

    def _default_record_exists(self):
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.project_config, "project__package__api_version", None)
            or "67.0"
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        soql = (
            "SELECT DeveloperName FROM RLM_Approval_Config__mdt "
            f"WHERE DeveloperName = '{DEFAULT_RECORD_DEVELOPER_NAME}'"
        )
        resp = requests.get(
            f"{instance_url}/services/data/v{api_version}/query",
            headers=headers,
            params={"q": soql},
            timeout=self._TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("totalSize", 0) > 0

    # ------------------------------------------------------------------
    # SFDX project and CMDT record generation
    # ------------------------------------------------------------------

    def _write_sfdx_project(self, temp_dir):
        """Write a minimal sfdx-project.json for the deploy."""
        project = {
            "packageDirectories": [{"path": "force-app", "default": True}],
            "sfdcLoginUrl": "https://login.salesforce.com",
            "sourceApiVersion": str(self.project_config.project__package__api_version),
        }
        path = os.path.join(temp_dir, "sfdx-project.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2)

    def _write_cmdt_record(self, temp_dir):
        """Generate the RLM_Approval_Config.Default.md-meta.xml record.

        DeveloperName ("Default") comes from the filename
        ({ObjectDeveloperName}.{RecordDeveloperName}.md-meta.xml), not from
        any XML element inside <CustomMetadata>.
        """
        cmdt_dir = os.path.join(
            temp_dir, "force-app", "main", "default", "customMetadata"
        )
        os.makedirs(cmdt_dir)

        values = "\n".join(
            "    <values>\n"
            f"        <field>{field}</field>\n"
            f'        <value xsi:type="xsd:boolean">{str(enabled).lower()}</value>\n'
            "    </values>"
            for field, enabled in CHAIN_ENABLED_FIELDS.items()
        )

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata"'
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
            "    <label>Default (only this record is read)</label>\n"
            "    <protected>false</protected>\n"
            f"{values}\n"
            "</CustomMetadata>\n"
        )

        path = os.path.join(
            cmdt_dir,
            f"RLM_Approval_Config.{DEFAULT_RECORD_DEVELOPER_NAME}.md-meta.xml",
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)

        self.logger.debug(f"Wrote CMDT record to {path}")

    # ------------------------------------------------------------------
    # Deploy
    # ------------------------------------------------------------------

    def _deploy(self, temp_dir, org_username):
        """Deploy the CMDT record to the org.

        Runs the sf CLI from within the temp directory using a relative
        --source-dir path to avoid "unsafe character sequences" errors
        from the CLI's path-traversal checks.
        """
        command = [
            "sf",
            "project",
            "deploy",
            "start",
            "--source-dir",
            "force-app",
            "--target-org",
            org_username,
            "--ignore-conflicts",
            "--wait",
            str(DEPLOY_WAIT_MINUTES),
            "--json",
        ]

        self.logger.debug(f"Deploying: {shlex.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=DEPLOY_TIMEOUT_SECONDS,
                cwd=temp_dir,
            )
        except subprocess.TimeoutExpired:
            raise CommandException(
                f"Deploy timed out after {DEPLOY_TIMEOUT_SECONDS} seconds."
            )
        except FileNotFoundError:
            raise CommandException(
                "sf command not found. Please ensure Salesforce CLI is "
                "installed and in PATH."
            )

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise CommandException(
                f"Deploy returned invalid JSON.\n"
                f"Exit code: {result.returncode}\n"
                f"Stdout: {result.stdout[:500]}\n"
                f"Stderr: {result.stderr[:500]}"
            )

        # Check result.success first — sf CLI can return top-level status=0
        # even when the deploy itself failed (failure is in result.success/status).
        deploy_result = output.get("result") or {}
        deploy_succeeded = deploy_result.get("success")
        if deploy_succeeded is False:
            message = self._extract_deploy_error(output)
            raise CommandException(f"Deploy failed: {message}")

        # Fall back to top-level status / process return code when result.success
        # is absent (e.g. auth errors that never reach the deploy phase).
        if deploy_succeeded is None:
            status = output.get("status", result.returncode)
            if status != 0:
                message = self._extract_deploy_error(output)
                raise CommandException(f"Deploy failed: {message}")

        self.logger.debug("CMDT record deployed successfully")

    @staticmethod
    def _extract_deploy_error(output):
        """Extract a meaningful error message from sf CLI deploy JSON output.

        The sf CLI puts errors in various locations depending on the failure
        type: top-level 'message', result.details.componentFailures, etc.
        """
        top_msg = output.get("message")
        if top_msg:
            return top_msg

        result = output.get("result") or {}

        details = result.get("details") or {}
        failures = details.get("componentFailures")
        if failures:
            if isinstance(failures, dict):
                failures = [failures]
            lines = []
            for f in failures[:5]:  # cap at 5 to keep output readable
                problem = f.get("problem", "unknown")
                comp = f.get("fullName") or f.get("fileName") or "unknown"
                lines.append(f"  {comp}: {problem}")
            return "Component failures:\n" + "\n".join(lines)

        for key in ("errorMessage", "message"):
            val = result.get(key)
            if val:
                return val

        return f"Unknown error. Full response:\n{json.dumps(output, indent=2)[:1000]}"
