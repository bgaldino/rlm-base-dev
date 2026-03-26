"""
Custom CumulusCI task for stamping the current git commit into a Salesforce org.

Deploys a Custom Metadata Type record (RLM_Build_Info__mdt.Latest) containing the
git commit hash, branch, build timestamp, feature flags, and working tree state so
the org's build provenance is queryable via SOQL and visible in Setup.

Usage:
    In cumulusci.yml:
        stamp_git_commit:
            class_path: tasks.rlm_stamp_commit.StampGitCommit
            options:
                flow_name: prepare_rlm_org

    Command line:
        cci task run stamp_git_commit --org beta
"""
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import yaml

try:
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.keychain import BaseProjectKeychain
except ImportError:
    SFDXBaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception
    BaseProjectKeychain = object

DEPLOY_TIMEOUT_SECONDS = 120


class StampGitCommit(SFDXBaseTask):
    """
    Stamps the current git commit hash, branch, and timestamp into the org
    as a Custom Metadata Type record (RLM_Build_Info__mdt.Latest).

    Non-fatal: deploy failures are logged as warnings so this task never
    breaks a flow that has already completed all real work.
    """

    keychain_class = BaseProjectKeychain

    task_options = {
        "flow_name": {
            "description": (
                "Name of the CCI flow that triggered this stamp "
                "(e.g. prepare_rlm_org). Defaults to 'manual'."
            ),
            "required": False,
        },
    }

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

        commit_hash_short = self._git("rev-parse", "--short", "HEAD")
        commit_hash_full = self._git("rev-parse", "HEAD")
        branch = self._resolve_branch(commit_hash_short)
        dirty = self._is_dirty_tree()
        build_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        flow_name = self.options.get("flow_name") or "manual"
        org_def = self._resolve_org_definition()
        feature_flags = self._resolve_feature_flags()

        dirty_label = " (dirty)" if dirty else ""
        self.logger.info(
            f"Stamping org with commit {commit_hash_short}{dirty_label} "
            f"(branch: {branch}, flow: {flow_name}, org: {org_def})"
        )

        temp_dir = tempfile.mkdtemp(prefix="rlm_stamp_")
        try:
            self._write_sfdx_project(temp_dir)
            self._write_cmdt_record(
                temp_dir,
                commit_hash_short=commit_hash_short,
                commit_hash_full=commit_hash_full,
                branch=branch,
                dirty=dirty,
                build_timestamp=build_timestamp,
                flow_name=flow_name,
                org_definition=org_def,
                feature_flags=feature_flags,
            )
            try:
                self._deploy(temp_dir, org_username)
            except Exception as e:
                self.logger.warning(
                    f"Failed to stamp org (non-fatal): {e}\n"
                    "The org build completed successfully but the commit "
                    "stamp was not deployed."
                )
                return
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.logger.info(
            f"Stamped org: commit={commit_hash_short}{dirty_label}, "
            f"branch={branch}, timestamp={build_timestamp}, "
            f"flow={flow_name}, org={org_def}"
        )

    # ------------------------------------------------------------------
    # Git helpers
    # ------------------------------------------------------------------

    def _git(self, *args):
        """Run a git command and return stripped stdout."""
        command = ["git"] + list(args)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise CommandException(
                f"git command failed: {shlex.join(command)}\n{e.stderr}"
            )
        except FileNotFoundError:
            raise CommandException(
                "git not found. Please ensure git is installed and in PATH."
            )

    def _resolve_branch(self, commit_hash_short):
        """Resolve the current branch name, handling detached HEAD."""
        branch = self._git("rev-parse", "--abbrev-ref", "HEAD")
        if branch == "HEAD":
            # Detached HEAD — try tag name first, fall back to detached@<hash>
            try:
                branch = self._git(
                    "describe", "--tags", "--exact-match", "HEAD"
                )
            except CommandException:
                branch = f"detached@{commit_hash_short}"
        return branch

    # Paths regenerated during the build that should not count as dirty.
    # unpackaged/post_ux/ is fully regenerated by assemble_and_deploy_ux (step 29)
    # and will always show as modified after a successful build.
    BUILD_OUTPUT_PATHS = [
        "unpackaged/post_ux/",
    ]

    def _is_dirty_tree(self):
        """Check if the working tree has uncommitted changes.

        Excludes known build-output paths (e.g. unpackaged/post_ux/) that are
        regenerated during the flow and would otherwise always flag dirty in CI.
        """
        output = self._git("status", "--porcelain")
        if not output:
            return False
        for line in output.splitlines():
            # porcelain format: XY <path> or XY <path> -> <renamed>
            path = line[3:].split(" -> ")[0]
            if not any(path.startswith(bp) for bp in self.BUILD_OUTPUT_PATHS):
                return True
        return False

    # ------------------------------------------------------------------
    # Org and feature flag helpers
    # ------------------------------------------------------------------

    def _resolve_org_definition(self):
        """Build an org definition string from org_config properties.

        Examples: "beta (scratch, orgs/beta.json)", "dev-sb0 (sandbox)"
        """
        parts = []
        config_name = getattr(self.org_config, "config_name", None)
        if config_name:
            parts.append(config_name)

        org_type_parts = []
        if getattr(self.org_config, "scratch", False):
            org_type_parts.append("scratch")
        elif getattr(self.org_config, "is_sandbox", False):
            org_type_parts.append("sandbox")
        else:
            org_type_parts.append("production")

        config_file = getattr(self.org_config, "config_file", None)
        if config_file:
            org_type_parts.append(config_file)

        if org_type_parts:
            parts.append(f"({', '.join(org_type_parts)})")

        return " ".join(parts) if parts else "unknown"

    def _resolve_feature_flags(self):
        """Serialize project custom config as YAML for the feature flags field.

        Filters out YAML anchor lists (permission set arrays) and dicts,
        keeping only scalar config values (booleans, strings, numbers).
        """
        custom = getattr(self.project_config, "project__custom", {}) or {}
        config = {
            k: v for k, v in custom.items() if not isinstance(v, (list, dict))
        }
        if not config:
            return "none"
        return yaml.dump(config, default_flow_style=False, sort_keys=True).strip()

    # ------------------------------------------------------------------
    # SFDX project and CMDT record generation
    # ------------------------------------------------------------------

    def _write_sfdx_project(self, temp_dir):
        """Write a minimal sfdx-project.json for the deploy."""
        project = {
            "packageDirectories": [{"path": "force-app", "default": True}],
            "sfdcLoginUrl": "https://login.salesforce.com",
            "sourceApiVersion": self.project_config.project__package__api_version,
        }
        path = os.path.join(temp_dir, "sfdx-project.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2)

    def _write_cmdt_record(self, temp_dir, **fields):
        """Generate the RLM_Build_Info.Latest.md-meta.xml record.

        All string values are XML-escaped to prevent injection from branch
        names, flow names, or other values containing &, <, >, etc.
        """
        cmdt_dir = os.path.join(
            temp_dir, "force-app", "main", "default", "customMetadata"
        )
        os.makedirs(cmdt_dir)

        dirty_str = "true" if fields["dirty"] else "false"

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata"'
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
            "    <label>Latest</label>\n"
            "    <protected>false</protected>\n"
            "    <values>\n"
            "        <field>RLM_Commit_Hash__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['commit_hash_short'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Full_Commit_Hash__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['commit_hash_full'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Branch__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['branch'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Dirty_Tree__c</field>\n"
            f'        <value xsi:type="xsd:boolean">{dirty_str}</value>\n'
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Build_Timestamp__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['build_timestamp'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_CCI_Flow__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['flow_name'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Org_Definition__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['org_definition'])}</value>\n"
            "    </values>\n"
            "    <values>\n"
            "        <field>RLM_Feature_Flags__c</field>\n"
            f'        <value xsi:type="xsd:string">'
            f"{escape(fields['feature_flags'])}</value>\n"
            "    </values>\n"
            "</CustomMetadata>\n"
        )

        path = os.path.join(cmdt_dir, "RLM_Build_Info.Latest.md-meta.xml")
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

        status = output.get("status")
        if status is not None and status != 0:
            message = self._extract_deploy_error(output)
            self.logger.error(f"Deploy failed: {message}")
            raise CommandException(f"Deploy failed: {message}")

        self.logger.debug("CMDT record deployed successfully")

    @staticmethod
    def _extract_deploy_error(output):
        """Extract a meaningful error message from sf CLI deploy JSON output.

        The sf CLI puts errors in various locations depending on the failure
        type: top-level 'message', result.details.componentFailures, etc.
        """
        # Top-level message (covers auth errors, CLI errors)
        top_msg = output.get("message")
        if top_msg:
            return top_msg

        result = output.get("result") or {}

        # Component-level failures (most common for metadata deploy errors)
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

        # result-level message or errorMessage
        for key in ("errorMessage", "message"):
            val = result.get(key)
            if val:
                return val

        # Last resort: dump the whole output for debugging
        return f"Unknown error. Full response:\n{json.dumps(output, indent=2)[:1000]}"
