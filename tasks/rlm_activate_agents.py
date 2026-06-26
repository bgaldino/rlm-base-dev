"""CCI task that activates Agentforce agents via ``sf agent activate``.

Fresh deploys (and ``sf agent publish``) land BotVersions as Inactive.
``BotVersion.Status`` is not DML-writable from Apex, so activation has to go
through a Connect REST endpoint. ``sf agent activate`` is the supported CLI
wrapper for that endpoint — preferred over hand-rolled HTTP callouts because
the Salesforce CLI maintains it.

The agent list is sourced from disk: anything under
``unpackaged/post_agents/aiAuthoringBundles/<Name>/`` is treated as an agent
that should be activated.
"""
import json
import subprocess
from pathlib import Path

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception
    CommandException = Exception


class ActivateAgents(BaseSalesforceTask):
    """Run ``sf agent activate`` for each RLM agent under
    ``unpackaged/post_agents``.

    Without ``--version``, the CLI activates the latest published version,
    which is the behavior we want — the previously-active version is
    automatically deactivated by the platform on activation of a newer one.
    """

    CLI_TIMEOUT_SECONDS = 300

    task_options = {
        "post_agents_path": {
            "description": "Path (relative to repo root) containing post_agents source.",
            "required": False,
        },
    }

    def _run_task(self):
        root = Path(self.options.get("post_agents_path") or "unpackaged/post_agents")
        agents = self._discover_agents(root)

        if not agents:
            self.logger.info(f"No agents discovered under {root}; nothing to activate.")
            return

        target = self.org_config.username
        self.logger.info(f"Activating {len(agents)} agent(s) on {target}: " + ", ".join(agents))

        for api_name in agents:
            self._activate(api_name, target)

    def _discover_agents(self, root):
        bundles = root / "aiAuthoringBundles"
        if not bundles.is_dir():
            return []
        return sorted(p.name for p in bundles.iterdir() if p.is_dir())

    def _activate(self, api_name, target):
        cmd = [
            "sf", "agent", "activate",
            "--api-name", api_name,
            "--target-org", target,
            "--json",
        ]
        self.logger.info(f"  → sf agent activate --api-name {api_name}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.CLI_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise CommandException(
                f"sf agent activate ({api_name}) timed out after "
                f"{self.CLI_TIMEOUT_SECONDS}s."
            ) from exc
        except FileNotFoundError as exc:
            raise CommandException(
                "sf agent activate failed: the Salesforce CLI ('sf') was not "
                "found on PATH."
            ) from exc

        payload = {}
        if result.stdout:
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                payload = {}

        if result.returncode != 0 or payload.get("status", 1) != 0:
            message = (
                payload.get("message")
                or result.stderr.strip()
                or result.stdout.strip()
                or f"exit {result.returncode}"
            )
            raise TaskOptionsError(
                f"sf agent activate failed for {api_name}: {message}"
            )

        self.logger.info(f"    activated {api_name}")
