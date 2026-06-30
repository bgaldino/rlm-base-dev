"""CCI task that deactivates legacy Agentforce agents via ``sf agent deactivate``.

Required for idempotent re-runs of ``prepare_agents``: legacy agents
deploy Bot + BotVersion metadata directly, and the platform rejects
updates to an active BotVersion. Deactivating first allows
``deploy_legacy_agents`` to update the metadata, after which
``publish_agents`` + ``activate_agents`` will re-publish and re-activate.

New Agent Script agents (aiAuthoringBundles) are NOT affected — their
deploy pushes authoring bundle source, not the runtime BotVersion.

Deactivation is best-effort — if an agent is already inactive the CLI
returns a non-zero exit but we treat that as a no-op rather than a
failure.
"""

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
except ImportError:
    BaseSalesforceTask = object

from tasks.rlm_agents_common import discover_legacy_agents, run_sf_json


class DeactivateAgents(BaseSalesforceTask):
    """Run ``sf agent deactivate`` for each legacy RLM agent, tolerating
    already-inactive agents.
    """

    CLI_TIMEOUT_SECONDS = 300

    task_options = {}

    def _run_task(self):
        agents = discover_legacy_agents()

        if not agents:
            self.logger.info("No legacy agents discovered; nothing to deactivate.")
            return

        target = self.org_config.username
        self.logger.info(
            f"Deactivating {len(agents)} legacy agent(s) on {target}: " + ", ".join(agents)
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
            else:
                raise
