"""CCI task that publishes Agentforce authoring bundles.

Deploying an ``AiAuthoringBundle`` puts the bundle source in the org but does
not produce a runnable ``BotVersion``. ``sf agent publish authoring-bundle``
is the platform compile step that converts the bundle into a ``BotVersion``.
This task wraps that CLI call so it can run as part of ``prepare_agents``.

The CLI scans only the default package directory of the active SFDX project,
which here is ``force-app``. Our bundles live under
``unpackaged/post_agents/aiAuthoringBundles``, so we stage a temporary SFDX
project once, place each bundle inside its default package directory in turn,
and run the publish from there.

Idempotent: re-publishing a bundle that hasn't changed produces a no-op on
the platform side. Activation is a separate step (`activate_agents`).
"""
import json
import shutil
import tempfile
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object

from tasks.rlm_agents_common import discover_agent_bundles, run_sf_json

DEFAULT_BUNDLES_PATH = "unpackaged/post_agents/aiAuthoringBundles"
# Fallback only used when project config can't be read (e.g. unit import).
FALLBACK_API_VERSION = "67.0"


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
        bundles_root = Path(self.options.get("bundles_path") or DEFAULT_BUNDLES_PATH)

        bundles = discover_agent_bundles(bundles_root)
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

        # The staging SFDX project is invariant across bundles, so build it
        # once and swap each bundle into its package directory in turn.
        with tempfile.TemporaryDirectory(prefix="rlm-publish-") as stage:
            stage_path = Path(stage)
            self._write_sfdx_project(stage_path)
            package_dir = stage_path / "force-app" / "main" / "default" / "aiAuthoringBundles"
            for api_name in bundles:
                self._publish_bundle(
                    api_name, bundles_root / api_name, target, stage, package_dir
                )

    def _publish_bundle(self, api_name, source_dir, target, stage, package_dir):
        self.logger.info(f"  → sf agent publish authoring-bundle --api-name {api_name}")

        dest = package_dir / api_name
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
        payload = run_sf_json(
            cmd,
            timeout=self.CLI_TIMEOUT_SECONDS,
            label=f"sf agent publish authoring-bundle ({api_name})",
            cwd=stage,
        )

        # Clean up so a later bundle's directory listing isn't polluted.
        shutil.rmtree(dest, ignore_errors=True)

        summary = payload.get("result", {}).get("summary", {})
        self.logger.info(
            f"    published {api_name} "
            f"(retrieved={summary.get('retrieved')}, deployed={summary.get('deployed')})"
        )

    def _api_version(self):
        return (
            getattr(self.project_config, "project__package__api_version", None)
            or FALLBACK_API_VERSION
        )

    def _write_sfdx_project(self, stage_path):
        (stage_path / "sfdx-project.json").write_text(json.dumps({
            "packageDirectories": [{"path": "force-app", "default": True}],
            "name": "rlm-base-publish-stage",
            "namespace": "",
            "sourceApiVersion": self._api_version(),
        }))
