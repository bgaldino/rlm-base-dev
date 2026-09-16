"""
Configure Salesforce MCP servers on an org via the Tooling API.

Companion to the ``unpackaged/post_mcp`` metadata bundle. The bundle deploys the
two pieces that ARE metadata — the ``ClaudeMcpClientRC`` External Client
Application and the ``RampCloneSalesTransaction`` invocable — and this task does
everything that is not:

  * activates the hosted Salesforce MCP servers (``McpServerAccess``)
  * creates the custom ``rampdealsconnect`` server: ``McpServerDefinition``,
    its ``McpServerToolDefinition`` tools, and their
    ``McpServerToolApiDefinition`` bindings, plus its own access record

Only ``McpServerDefinition`` is a deployable metadata type; the access records,
tool definitions, and bindings are Tooling API records, so a metadata deploy
cannot activate a server. That asymmetry is the whole reason this task exists.

ORDERING THAT MATTERS: deploy ``unpackaged/post_mcp`` before running this, because
the ``cloneSalesTransaction`` CLASSIC binding references the Apex invocable by
path (``/actions/custom/apex/RampCloneSalesTransaction``). Creating the binding
first fails.

Every write checks for an existing record first, so re-running is safe and
reports ``already``. ``-o dry_run True`` reports intended changes and writes
nothing.

Also here: ``DeployMcpOverlay``, which deploys the ``unpackaged/post_mcp_264``
overlay only on orgs new enough to compile it. See that class for why the clone
invocable exists in two copies.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.utils import process_bool_arg
    from cumulusci.tasks.salesforce import Deploy
except ImportError:  # pragma: no cover - offline import path
    BaseTask = object
    Deploy = object
    TaskOptionsError = Exception
    CommandException = Exception

    def process_bool_arg(arg):
        """
        Offline fallback so this module still imports without CumulusCI.

        Same vocabulary and the same TypeError as
        ``cumulusci.core.utils.process_bool_arg``.
        """
        if isinstance(arg, (int, bool)):
            return bool(arg)
        if arg is None:
            return False
        if isinstance(arg, str):
            if arg.lower() in ("yes", "y", "true", "on", "1"):
                return True
            if arg.lower() in ("no", "n", "false", "off", "0"):
                return False
        raise TypeError(f"Cannot interpret as boolean: `{arg}`")


# Hosted servers the Revenue Cloud MCP path needs. DeveloperName is the
# namespaced platform form; MasterLabel is what Setup shows.
CORE_HOSTED: Tuple[Tuple[str, str], ...] = (
    ("industries_revenue_cloud", "revenue-cloud"),
    ("industries_revenue_cloud_billing", "revenue-cloud-billing"),
    ("industries_revenue_configurator", "revenue-configurator"),
)

# Broad platform servers, opt-in via `-o platform_servers True`. Off by default:
# sobject-all exposes read/write across every object in the org, which is a wider
# grant than the Revenue Cloud servers above and should be a deliberate choice.
PLATFORM_HOSTED: Tuple[Tuple[str, str], ...] = (
    ("platform_sobject_all", "sobject-all"),
    ("platform_headless_360", "headless-360"),
)

CUSTOM_SERVER_DEVELOPER_NAME = "rampdealsconnect"
CUSTOM_SERVER_LABEL = "ramp-deals-connect"
CUSTOM_SERVER_DESCRIPTION = "RampDealsBinding"

# (tool name, apiSource, apiIdentifier, operation). The two entries show both
# binding styles: CONNECT hits a Connect API resource, CLASSIC hits an Apex
# @InvocableMethod by action path.
CUSTOM_TOOLS: Tuple[Tuple[str, str, str, str], ...] = (
    (
        "placeSalesTransaction",
        "CONNECT",
        "industries-revenue",
        "placeSalesTransaction",
    ),
    (
        "cloneSalesTransaction",
        "CLASSIC",
        "/actions/custom/apex/RampCloneSalesTransaction",
        "RampCloneSalesTransaction",
    ),
)


class ConfigureMcpServers(BaseTask):
    """Activate hosted MCP servers and build the custom ramp-deals server."""

    # Every operation here talks to an org. Without this, BaseTask.salesforce_task
    # defaults to False, cci offers no `--org` option, and the task can only ever
    # hit the default org.
    salesforce_task = True

    task_options = {
        "operation": {
            "description": (
                "'ensure' (default) creates anything missing; 'list' reports the "
                "org's current MCP surface and changes nothing."
            ),
            "required": False,
        },
        "platform_servers": {
            "description": (
                "If true, also activate the broad platform servers "
                f"({', '.join(label for _, label in PLATFORM_HOSTED)}). "
                "Defaults to false."
            ),
            "required": False,
        },
        "custom_server": {
            "description": (
                "If false, skip the custom rampdealsconnect server and configure "
                "only the hosted ones. Defaults to true."
            ),
            "required": False,
        },
        "api_version": {
            "description": "Salesforce API version override.",
            "required": False,
        },
        "dry_run": {
            "description": "If true, log intended changes without writing to the org.",
            "required": False,
        },
    }

    def _run_task(self):
        operation = (self.options.get("operation") or "ensure").strip().lower()
        if operation not in {"ensure", "list"}:
            raise TaskOptionsError("operation must be 'ensure' or 'list'")

        self.dry_run = process_bool_arg(self.options.get("dry_run") or False)
        self.access_token = self.org_config.access_token
        self.instance_url = self.org_config.instance_url
        self.api_version = (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "67.0")
        )

        self.created: List[str] = []
        self.skipped: List[str] = []
        self.failed: List[str] = []

        self._preflight()

        wanted_hosted = list(CORE_HOSTED)
        if process_bool_arg(self.options.get("platform_servers") or False):
            wanted_hosted.extend(PLATFORM_HOSTED)

        want_custom = process_bool_arg(
            self.options.get("custom_server")
            if self.options.get("custom_server") is not None
            else True
        )

        if operation == "list":
            self._list_surface(wanted_hosted, want_custom)
            return

        self._ensure_hosted(wanted_hosted)
        if want_custom:
            self._ensure_custom_server()
        else:
            self.logger.info("Skipping custom server (custom_server=False)")

        self._report()

    # ─── Preflight ──────────────────────────────────────────────────────────

    def _preflight(self):
        """Fail fast and legibly when the org has no MCP feature."""
        records = self._tooling_query(
            "SELECT QualifiedApiName FROM EntityDefinition "
            "WHERE QualifiedApiName = 'McpServerDefinition'"
        )
        if not records:
            raise CommandException(
                "This org has no McpServerDefinition entity, so it lacks the MCP "
                "feature. Nothing here can be configured against it."
            )

    # ─── Hosted servers ─────────────────────────────────────────────────────

    def _ensure_hosted(self, wanted: List[Tuple[str, str]]):
        self.logger.info("Hosted MCP servers")
        existing = self._existing_access()

        for developer_name, label in wanted:
            if developer_name in existing:
                self.skipped.append(label)
                self.logger.info(f"  already   {label}")
                continue
            self._tooling_create(
                "McpServerAccess",
                {
                    "DeveloperName": developer_name,
                    "MasterLabel": label,
                    "Active": True,
                },
                label,
            )

    # ─── Custom server ──────────────────────────────────────────────────────

    def _ensure_custom_server(self):
        self.logger.info(f"Custom MCP server {CUSTOM_SERVER_DEVELOPER_NAME}")

        server_id = self._custom_server_id()
        if server_id:
            self.skipped.append("definition")
            self.logger.info(
                f"  already   definition {CUSTOM_SERVER_DEVELOPER_NAME}  {server_id}"
            )
        else:
            server_id = self._tooling_create(
                "McpServerDefinition",
                {
                    "DeveloperName": CUSTOM_SERVER_DEVELOPER_NAME,
                    "MasterLabel": CUSTOM_SERVER_LABEL,
                    "Description": CUSTOM_SERVER_DESCRIPTION,
                },
                f"definition {CUSTOM_SERVER_DEVELOPER_NAME}",
            )

        if not server_id:
            # Dry run, or the definition failed. Either way there is no id to hang
            # tools off, and reporting a dozen downstream failures would be noise.
            if self.dry_run:
                for tool_name, api_source, _, _ in CUSTOM_TOOLS:
                    self._note_would_create(f"tool {tool_name}")
                    self._note_would_create(f"binding {tool_name} ({api_source})")
                self._note_would_create(f"access {CUSTOM_SERVER_LABEL} (custom)")
            return

        self._ensure_tools(server_id)
        self._ensure_custom_access(server_id)

    def _ensure_tools(self, server_id: str):
        # Batch both lookups before the loop rather than querying per tool.
        existing_tools = {
            record["ToolName"]: record["Id"]
            for record in self._tooling_query(
                "SELECT Id, ToolName FROM McpServerToolDefinition "
                f"WHERE McpServerId = '{server_id}'"
            )
        }
        existing_bindings = {
            (record.get("ApiSource"), record.get("Operation"))
            for record in self._tooling_query(
                "SELECT ApiSource, Operation FROM McpServerToolApiDefinition"
            )
        }

        for tool_name, api_source, api_identifier, operation in CUSTOM_TOOLS:
            tool_id = existing_tools.get(tool_name)
            if tool_id:
                self.skipped.append(f"tool {tool_name}")
                self.logger.info(f"  already   tool {tool_name}")
            else:
                tool_id = self._tooling_create(
                    "McpServerToolDefinition",
                    {
                        "McpServerId": server_id,
                        "ToolName": tool_name,
                        "ReadOnly": False,
                        "Destructive": False,
                        "Idempotent": False,
                    },
                    f"tool {tool_name}",
                )

            if not tool_id:
                continue

            if (api_source, operation) in existing_bindings:
                self.skipped.append(f"binding {tool_name}")
                self.logger.info(f"  already   binding {tool_name}")
                continue

            self._tooling_create(
                "McpServerToolApiDefinition",
                {
                    "ToolId": tool_id,
                    "ApiSource": api_source,
                    "ApiIdentifier": api_identifier,
                    "Operation": operation,
                },
                f"binding {tool_name} ({api_source})",
            )

    def _ensure_custom_access(self, server_id: str):
        if CUSTOM_SERVER_DEVELOPER_NAME in self._existing_access():
            self.skipped.append("custom access")
            self.logger.info(f"  already   access {CUSTOM_SERVER_LABEL}")
            return

        # For a CUSTOM server, DeveloperName must EQUAL the definition's
        # DeveloperName. The namespaced form used for hosted servers fails with
        # FIELD_INTEGRITY_EXCEPTION here.
        self._tooling_create(
            "McpServerAccess",
            {
                "DeveloperName": CUSTOM_SERVER_DEVELOPER_NAME,
                "MasterLabel": CUSTOM_SERVER_LABEL,
                "Active": True,
                "McpServerId": server_id,
            },
            f"access {CUSTOM_SERVER_LABEL} (custom)",
        )

    # ─── Reporting ──────────────────────────────────────────────────────────

    def _list_surface(self, wanted: List[Tuple[str, str]], want_custom: bool):
        """Report what the org has, and flag anything this task does not manage."""
        expected = {developer_name for developer_name, _ in wanted}
        if want_custom:
            expected.add(CUSTOM_SERVER_DEVELOPER_NAME)
        optional = {developer_name for developer_name, _ in PLATFORM_HOSTED}

        records = self._tooling_query(
            "SELECT DeveloperName, MasterLabel, Active FROM McpServerAccess"
        )
        if not records:
            self.logger.info("No MCP servers are activated on this org.")
        else:
            self.logger.info("Activated MCP servers")
            for record in records:
                developer_name = record["DeveloperName"]
                if developer_name in expected:
                    note = "managed"
                elif developer_name in optional:
                    note = "opt-in — pass platform_servers True to manage it"
                else:
                    note = "UNMANAGED — activated by hand; will not survive a rebuild"
                self.logger.info(
                    f"  {record['MasterLabel']:26} active={record['Active']!s:5} {note}"
                )

        missing = expected - {record["DeveloperName"] for record in records}
        if missing:
            self.logger.warning(
                f"Missing {len(missing)} expected server(s): {', '.join(sorted(missing))}"
                " — run this task without -o operation list to create them."
            )

        server_id = self._custom_server_id()
        if not server_id:
            self.logger.info(
                f"Custom server {CUSTOM_SERVER_DEVELOPER_NAME} does not exist."
            )
            return

        self.logger.info(f"Custom server {CUSTOM_SERVER_DEVELOPER_NAME}  {server_id}")
        tools = self._tooling_query(
            "SELECT Id, ToolName FROM McpServerToolDefinition "
            f"WHERE McpServerId = '{server_id}'"
        )
        bindings: Dict[str, List[str]] = {}
        for record in self._tooling_query(
            "SELECT ToolId, ApiSource, ApiIdentifier FROM McpServerToolApiDefinition"
        ):
            bindings.setdefault(record["ToolId"], []).append(
                f"{record.get('ApiSource')} {record.get('ApiIdentifier')}"
            )
        for tool in tools:
            bound = "; ".join(bindings.get(tool["Id"], [])) or "NO BINDING"
            self.logger.info(f"  {tool['ToolName']:26} {bound}")

    def _report(self):
        self.logger.info(
            f"Summary: created {len(self.created)}  "
            f"already/skipped {len(self.skipped)}  failed {len(self.failed)}"
        )
        for failure in self.failed:
            self.logger.error(f"  FAILED  {failure}")
        if self.failed:
            raise CommandException(
                f"{len(self.failed)} MCP configuration step(s) failed; see the log above."
            )

    # ─── Tooling API plumbing ───────────────────────────────────────────────

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _existing_access(self) -> Dict[str, str]:
        return {
            record["DeveloperName"]: record["Id"]
            for record in self._tooling_query(
                "SELECT Id, DeveloperName FROM McpServerAccess"
            )
        }

    def _custom_server_id(self) -> Optional[str]:
        records = self._tooling_query(
            "SELECT Id FROM McpServerDefinition "
            f"WHERE DeveloperName = '{CUSTOM_SERVER_DEVELOPER_NAME}'"
        )
        return records[0]["Id"] if records else None

    def _tooling_query(self, soql: str) -> List[Dict[str, Any]]:
        url = f"{self.instance_url}/services/data/v{self.api_version}/tooling/query/"
        response = requests.get(url, headers=self._headers, params={"q": soql})
        if response.status_code >= 400:
            raise CommandException(
                f"Tooling query failed ({response.status_code}): {response.text[:300]}"
            )
        return response.json().get("records", [])

    def _note_would_create(self, label: str):
        """Log and count a simulated create so dry-run totals match the log."""
        self.skipped.append(f"{label} (would create)")
        self.logger.info(f"  would create  {label}")

    def _tooling_create(
        self, sobject: str, body: Dict[str, Any], label: str
    ) -> Optional[str]:
        if self.dry_run:
            self._note_would_create(label)
            return None

        url = (
            f"{self.instance_url}/services/data/v{self.api_version}"
            f"/tooling/sobjects/{sobject}/"
        )
        response = requests.post(url, headers=self._headers, json=body)
        if response.status_code >= 400:
            message = response.text[:200].replace("\n", " ")
            self.failed.append(f"{label}: {message}")
            self.logger.error(f"  FAILED    {label}: {message}")
            return None

        record_id = response.json().get("id")
        self.created.append(label)
        self.logger.info(f"  created   {label}  {record_id}")
        return record_id


class DeployMcpOverlay(Deploy):
    """
    Deploy a release-gated MCP overlay, skipping orgs too old to compile it.

    ``unpackaged/post_mcp`` carries the clone invocable compiled at 67.0 and
    synchronous-only, because the async members do not exist on 262 / v67.0 — a compile
    probe against a 262 org reports ``Variable does not exist`` for ``input.contextId``,
    ``options.contextId``, and ``output.trackerId``, and ConnectApi input
    representations reject ``JSON.serialize``/``deserialize``, so there is no reflective
    way to reach them from a 67.0 class. ``unpackaged/post_mcp_264`` therefore carries a
    second copy at 68.0 that adds the async path, and this task overlays it on any org
    that can take it.

    Without the version gate, a plain ``Deploy`` of the overlay would hard-fail every
    262 org in the fleet; with it, a 262 org keeps the sync class and the flow moves on.
    The reverse footgun matters just as much: because the overlay runs after the base
    bundle, a v68 org ends up with the async class rather than being quietly downgraded
    to the sync one.

    Retire this the moment Foundations' baseline reaches 264 — promote the overlay copy
    into ``unpackaged/post_mcp`` and delete this class, the task, and the parity test.
    """

    task_options = {
        **getattr(Deploy, "task_options", {}),
        "min_api_version": {
            "description": (
                "Minimum org API version required to compile this bundle. Below it, the "
                "deploy is skipped with a log line instead of failing. Defaults to 68.0."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        raw_minimum = self.options.get("min_api_version") or "68.0"
        try:
            minimum = float(raw_minimum)
        except (TypeError, ValueError):
            raise TaskOptionsError(
                f"min_api_version must be a number like 68.0, got {raw_minimum!r}"
            )

        raw_org_version = self.org_config.latest_api_version
        try:
            org_version = float(raw_org_version)
        except (TypeError, ValueError):
            raise CommandException(
                f"Could not read the org's API version (got {raw_org_version!r}), so "
                f"whether it can compile {self.options.get('path')} is unknown. "
                "Refusing to guess."
            )

        path = self.options.get("path")
        if org_version < minimum:
            self.logger.info(
                f"Org is v{org_version:g}, below the v{minimum:g} this overlay needs — "
                f"skipping {path}. The release-appropriate copy from the base bundle "
                "stays in place."
            )
            return

        self.logger.info(
            f"Org is v{org_version:g}; deploying the v{minimum:g}+ overlay {path}."
        )
        return super()._run_task()
