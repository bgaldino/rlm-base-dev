"""CCI task that publishes Agentforce authoring bundles.

Deploying an ``AiAuthoringBundle`` puts the bundle source in the org but does
not produce a runnable ``BotVersion``. ``sf agent publish authoring-bundle``
is the platform compile step that converts the bundle into a ``BotVersion``.
This task wraps that CLI call so it can run as part of ``prepare_agents``.

The CLI scans only the default package directory of the active SFDX project,
which here is ``force-app``. Our bundles live under
``unpackaged/post_agents/aiAuthoringBundles``, so we stage a temporary SFDX
project that places the bundle inside its default package directory and run
the publish from there. Stage dir is removed after each agent.

Idempotent: re-publishing a bundle that hasn't changed produces a no-op on
the platform side. Activation is a separate step (`activate_agents`).
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception
    CommandException = Exception


class PublishAgents(BaseSalesforceTask):
    """Run ``sf agent publish authoring-bundle`` for each bundle under
    ``unpackaged/post_agents/aiAuthoringBundles``.

    The set of bundles is discovered from disk so adding a new authoring
    bundle does not require touching this file.
    """

    CLI_TIMEOUT_SECONDS = 600

    task_options = {
        "bundles_path": {
            "description": "Path (relative to repo root) containing aiAuthoringBundles directories.",
            "required": False,
        },
    }

    def _run_task(self):
        bundles_root = Path(
            self.options.get("bundles_path")
            or "unpackaged/post_agents/aiAuthoringBundles"
        )

        if not bundles_root.is_dir():
            self.logger.info(
                f"No authoring bundles directory at {bundles_root}; nothing to publish."
            )
            return

        bundles = sorted(p.name for p in bundles_root.iterdir() if p.is_dir())
        if not bundles:
            self.logger.info(
                f"No authoring bundles found under {bundles_root}; nothing to publish."
            )
            return

        target = self.org_config.username
        self.logger.info(
            f"Publishing {len(bundles)} authoring bundle(s) to {target}: "
            + ", ".join(bundles)
        )

        for api_name in bundles:
            self._publish_bundle(api_name, bundles_root / api_name, target)

    def _publish_bundle(self, api_name, source_dir, target):
        self.logger.info(f"  → sf agent publish authoring-bundle --api-name {api_name}")

        with tempfile.TemporaryDirectory(prefix="rlm-publish-") as stage:
            stage_path = Path(stage)
            self._write_sfdx_project(stage_path)
            dest = stage_path / "force-app" / "main" / "default" / "aiAuthoringBundles" / api_name
            dest.mkdir(parents=True, exist_ok=True)
            for f in source_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, dest / f.name)

            cmd = [
                "sf", "agent", "publish", "authoring-bundle",
                "--api-name", api_name,
                "--target-org", target,
                "--json",
            ]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=stage,
                    capture_output=True,
                    text=True,
                    timeout=self.CLI_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as exc:
                raise CommandException(
                    f"sf agent publish authoring-bundle ({api_name}) "
                    f"timed out after {self.CLI_TIMEOUT_SECONDS}s."
                ) from exc
            except FileNotFoundError as exc:
                raise CommandException(
                    "sf agent publish authoring-bundle failed: the Salesforce "
                    "CLI ('sf') was not found on PATH."
                ) from exc

            payload = {}
            if result.stdout:
                try:
                    payload = json.loads(result.stdout)
                except json.JSONDecodeError:
                    payload = {}

            if result.returncode != 0 or not payload.get("result", {}).get("success", False):
                message = (
                    payload.get("message")
                    or result.stderr.strip()
                    or result.stdout.strip()
                    or f"exit {result.returncode}"
                )
                raise TaskOptionsError(
                    f"sf agent publish authoring-bundle failed for {api_name}: {message}"
                )

            summary = payload.get("result", {}).get("summary", {})
            self.logger.info(
                f"    published {api_name} "
                f"(retrieved={summary.get('retrieved')}, deployed={summary.get('deployed')})"
            )

    @staticmethod
    def _write_sfdx_project(stage_path):
        (stage_path / "sfdx-project.json").write_text(json.dumps({
            "packageDirectories": [{"path": "force-app", "default": True}],
            "name": "rlm-base-publish-stage",
            "namespace": "",
            "sourceApiVersion": "67.0",
        }))
