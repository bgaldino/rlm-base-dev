"""CCI task that deactivates Agentforce agents via ``sf agent deactivate``.

Supports idempotent re-runs of ``prepare_agents``: the platform rejects
updates to an *active* agent version, so deactivating first lets
``publish_agents`` + ``activate_agents`` re-publish and re-activate.

Agents are discovered from ``aiAuthoringBundles`` — the same source as
``publish_agents`` and ``activate_agents``, so all three act on one set.
This task previously read the ``legacy/bots`` tree, which held the only
Bot + BotVersion agent in the repo; Release 264 retired both
``BotVersion`` and ``GenAiPlannerBundle`` as metadata types (absent from
the v68.0 describe), so that tree and its deploy step are gone and every
agent is now an authoring bundle.

Deactivation is best-effort — if an agent is already inactive, or not yet
deployed, the CLI returns a non-zero exit and we treat that as a no-op
rather than a failure.
"""
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object

from tasks.rlm_agents_common import discover_agent_bundles, run_sf_json

DEFAULT_BUNDLES_PATH = "unpackaged/post_agents/aiAuthoringBundles"


class DeactivateAgents(BaseSalesforceTask):
    """Run ``sf agent deactivate`` for each RLM agent, tolerating agents that
    are already inactive or not yet deployed.
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

        if not agents:
            self.logger.info(
                f"No agents discovered under {bundles_root}; nothing to deactivate."
            )
            return

        target = self.org_config.username
        self.logger.info(
            f"Deactivating {len(agents)} agent(s) on {target}: " + ", ".join(agents)
        )

        for api_name in agents:
            self._deactivate(api_name, target)

    def _deactivate(self, api_name, target):
        cmd = [
            "sf", "agent", "deactivate",
            "--api-name", api_name,
            "--target-org", target,
            "--json",
        ]
        self.logger.info(f"  → sf agent deactivate --api-name {api_name}")

        try:
            run_sf_json(
                cmd,
                timeout=self.CLI_TIMEOUT_SECONDS,
                label=f"sf agent deactivate ({api_name})",
            )
            self.logger.info(f"    deactivated {api_name}")
        except Exception as exc:
            msg = str(exc).lower()
            if "not active" in msg or "inactive" in msg or "no active" in msg:
                self.logger.info(f"    {api_name} already inactive — skipping")
            elif "not found" in msg or "does not exist" in msg or "no bot" in msg:
                self.logger.info(f"    {api_name} not yet deployed — skipping")
            else:
                raise
