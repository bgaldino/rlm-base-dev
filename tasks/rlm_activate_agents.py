"""CCI task that activates Agentforce agents via ``sf agent activate``.

Fresh deploys (and ``sf agent publish``) land BotVersions as Inactive.
``BotVersion.Status`` is not DML-writable from Apex, so activation has to go
through a Connect REST endpoint. ``sf agent activate`` is the supported CLI
wrapper for that endpoint — preferred over hand-rolled HTTP callouts because
the Salesforce CLI maintains it.

The agent list is sourced from disk: anything under
``unpackaged/post_agents/aiAuthoringBundles/<Name>/`` is treated as an agent
that should be activated. ``bundles_path`` and its default match
``publish_agents`` so the two tasks always discover the same set.
"""
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object

from tasks.rlm_agents_common import discover_agent_bundles, discover_legacy_agents, run_sf_json

DEFAULT_BUNDLES_PATH = "unpackaged/post_agents/aiAuthoringBundles"


class ActivateAgents(BaseSalesforceTask):
    """Run ``sf agent activate`` for each RLM agent under
    ``unpackaged/post_agents/aiAuthoringBundles``.

    Without ``--version``, the CLI activates the latest published version,
    which is the behavior we want — the previously-active version is
    automatically deactivated by the platform on activation of a newer one.
    """

    CLI_TIMEOUT_SECONDS = 300

    task_options = {
        "bundles_path": {
            "description": "Path (relative to repo root) containing aiAuthoringBundles directories.",
            "required": False,
        },
    }

    def _run_task(self):
        bundles_root = Path(self.options.get("bundles_path") or DEFAULT_BUNDLES_PATH)
        agents = discover_agent_bundles(bundles_root)
        legacy = discover_legacy_agents()
        all_agents = sorted(set(agents + legacy))

        if not all_agents:
            self.logger.info(
                f"No agents discovered under {bundles_root} or legacy bots; nothing to activate."
            )
            return

        target = self.org_config.username
        self.logger.info(
            f"Activating {len(all_agents)} agent(s) on {target}: " + ", ".join(all_agents)
        )

        for api_name in all_agents:
            self._activate(api_name, target)

    def _activate(self, api_name, target):
        cmd = [
            "sf", "agent", "activate",
            "--api-name", api_name,
            "--target-org", target,
            "--json",
        ]
        self.logger.info(f"  → sf agent activate --api-name {api_name}")

        run_sf_json(
            cmd,
            timeout=self.CLI_TIMEOUT_SECONDS,
            label=f"sf agent activate ({api_name})",
        )

        self.logger.info(f"    activated {api_name}")
