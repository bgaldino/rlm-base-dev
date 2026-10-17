"""
Configure Salesforce MCP servers on an org via the Tooling API.

Companion to the ``unpackaged/post_mcp`` and ``unpackaged/post_mcp_custom`` metadata
bundles. They deploy the pieces that ARE metadata — the ``RLM_McpClient`` External
Client Application, and (custom server only) the ``RLM_CloneSalesTransaction``
invocable and its ``RLM_McpSalesTransactions`` permission set — and this task does
everything that is not:

  * activates the hosted Salesforce MCP servers (``McpServerAccess``)
  * creates the custom ``RLMSalesTransactions`` server: ``McpServerDefinition``,
    its ``McpServerToolDefinition`` tools, and their
    ``McpServerToolApiDefinition`` bindings, plus its own access record

Only ``McpServerDefinition`` is a deployable metadata type; the access records,
tool definitions, and bindings are Tooling API records, so a metadata deploy
cannot activate a server. That asymmetry is the whole reason this task exists.

The custom server is optional (``mcp_custom_server`` flag, or ``-o custom_server``):
it is a stopgap until the hosted ``revenue-cloud`` server covers place and clone.

ORDERING THAT MATTERS: deploy ``unpackaged/post_mcp_custom`` before running this, because
the ``cloneSalesTransaction`` CLASSIC binding references the Apex invocable by
path (``/actions/custom/apex/RLM_CloneSalesTransaction``). Creating the binding
first fails.

Prerequisites are resolved before the first write: with the custom server
enabled, a missing invocable fails the task with nothing modified.

Every write checks for an existing record first, so re-running is safe and
reports ``already``. An access record that exists but is inactive is reactivated;
one linked to the wrong server fails instead of counting as done.
``-o dry_run True`` reports intended changes and writes nothing.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.utils import process_bool_arg
except ImportError:  # pragma: no cover - offline import path
    BaseTask = object
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

# From the Tooling API rejection `No "<id>" identifier found for source "CONNECT"`:
# the org's Connect catalog has no such identifier. (A bad operation on a known
# identifier reads "found for identifier", so it stays a failure.)
UNRESOLVED_IDENTIFIER_MARK = "identifier found for source"

CUSTOM_SERVER_DEVELOPER_NAME = "RLMSalesTransactions"
CUSTOM_SERVER_LABEL = "rlm-sales-transactions"
CUSTOM_SERVER_DESCRIPTION = "Place and clone Revenue Cloud sales transactions"

# (tool name, apiSource, apiIdentifier, operation). The two entries show both
# binding styles: CONNECT hits a Connect API resource, CLASSIC hits an Apex
# @InvocableMethod by action path. A CONNECT identifier is the API's
# "<domain>-<sub-domain>", lowercased; 264 re-catalogued place from
# industries-revenue to Revenue/TransactionManagement.
CUSTOM_TOOLS: Tuple[Tuple[str, str, str, str], ...] = (
    (
        "placeSalesTransaction",
        "CONNECT",
        "revenue-transactionmanagement",
        "placeSalesTransaction",
    ),
    (
        "cloneSalesTransaction",
        "CLASSIC",
        "/actions/custom/apex/RLM_CloneSalesTransaction",
        "RLM_CloneSalesTransaction",
    ),
)

# Bindings an earlier version of this task created, which no longer resolve. A tool
# bound only to one of these is rebound rather than failed. (ToolId is unique on
# McpServerToolApiDefinition, so the old binding is deleted before the new create.)
LEGACY_BINDINGS: Dict[str, Tuple[Tuple[str, str, str], ...]] = {
    "placeSalesTransaction": (
        ("CONNECT", "industries-revenue", "placeSalesTransaction"),
    ),
}


class ConfigureMcpServers(BaseTask):
    """Activate hosted MCP servers and build the custom sales-transactions server."""

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
                "If false, skip the custom RLMSalesTransactions server and configure "
                "only the hosted ones. Defaults to the mcp_custom_server feature flag "
                "(true when the flag is absent)."
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
            or getattr(self.project_config, "project__package__api_version", "68.0")
        )

        self.created: List[str] = []
        self.skipped: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []

        wanted_hosted = list(CORE_HOSTED)
        if process_bool_arg(self.options.get("platform_servers") or False):
            wanted_hosted.extend(PLATFORM_HOSTED)

        # Absent flag counts as on, the historical default. prepare_mcp's `when:` reads an
        # absent flag as off, so the flow relies on mcp_custom_server being declared.
        want_custom = self.options.get("custom_server")
        if want_custom is None:
            want_custom = getattr(self.project_config, "project__custom__mcp_custom_server", None)
        want_custom = process_bool_arg(True if want_custom is None else want_custom)

        self._preflight()

        if operation == "list":
            self._list_surface(wanted_hosted, want_custom)
            return

        # Resolve every prerequisite before the first write, so a missing one leaves
        # the org untouched instead of half-configured.
        if want_custom:
            self._preflight_custom()

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

    def _preflight_custom(self):
        """The CLASSIC binding references the clone invocable by action path, so the
        class must already be deployed (deploy_post_mcp_custom) before anything is written."""
        records = self._tooling_query(
            "SELECT Id FROM ApexClass WHERE Name = 'RLM_CloneSalesTransaction'"
        )
        if not records:
            raise CommandException(
                "ApexClass RLM_CloneSalesTransaction is not on this org, and the "
                "cloneSalesTransaction binding needs it. Run deploy_post_mcp_custom first, or "
                "pass -o custom_server False. No records were modified."
            )

    # ─── Hosted servers ─────────────────────────────────────────────────────

    def _ensure_hosted(self, wanted: List[Tuple[str, str]]):
        self.logger.info("Hosted MCP servers")
        existing = self._existing_access()

        for developer_name, label in wanted:
            self._ensure_access(
                existing.get(developer_name),
                {
                    "DeveloperName": developer_name,
                    "MasterLabel": label,
                    "Active": True,
                },
                label,
            )

    def _ensure_access(
        self,
        current: Optional[Dict[str, Any]],
        body: Dict[str, Any],
        label: str,
    ):
        """
        Create the access record, or reactivate it if it exists but is disabled.

        Presence is not activation: a record switched off in Setup still exists, and
        treating it as done would leave the server disabled forever.

        A record is matched on DeveloperName and must also point at the expected
        server: McpServerId is null for a hosted server and the definition's id for
        a custom one. A record linked elsewhere activates the wrong server, so it
        fails rather than counting as done; a changed label only warns.
        """
        if current is None:
            self._tooling_create("McpServerAccess", body, label)
            return
        expected_server = body.get("McpServerId") or None
        if (current.get("McpServerId") or None) != expected_server:
            message = (
                f"{label}: access {current.get('DeveloperName')} is linked to server "
                f"{current.get('McpServerId') or 'none (hosted)'}, expected "
                f"{expected_server or 'none (hosted)'}; fix or delete it in Setup"
            )
            self.failed.append(message)
            self.logger.error(f"  FAILED    {message}")
            return
        if current.get("MasterLabel") and current["MasterLabel"] != body["MasterLabel"]:
            self.logger.warning(
                f"  label     {label}: org has '{current['MasterLabel']}', "
                f"expected '{body['MasterLabel']}' (left as is)"
            )
        if current.get("Active"):
            self.skipped.append(label)
            self.logger.info(f"  already   {label}")
        else:
            self._tooling_update(
                "McpServerAccess", current["Id"], {"Active": True}, f"reactivate {label}"
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
        existing_bindings = self._bindings_by_tool(list(existing_tools.values()))
        # CONNECT identifiers this org could not resolve; tools that depend on one
        # are skipped with a warning rather than failing the build.
        unresolved: set = set()

        for tool_name, api_source, api_identifier, operation in CUSTOM_TOOLS:
            tool_id = existing_tools.get(tool_name)
            if (api_source, api_identifier) in unresolved and not tool_id:
                self._warn(
                    f"tool {tool_name} skipped: depends on CONNECT {api_identifier}, "
                    f"which this org does not resolve"
                )
                continue
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
                if self.dry_run:  # same totals as the no-server dry run
                    self._note_would_create(f"binding {tool_name} ({api_source})")
                continue

            # Scoped to THIS tool: another server may bind the same
            # (ApiSource, Operation), which says nothing about this tool.
            bound = existing_bindings.get(tool_id, [])
            if any(
                b.get("ApiSource") == api_source
                and b.get("Operation") == operation
                and b.get("ApiIdentifier") == api_identifier
                for b in bound
            ):
                self.skipped.append(f"binding {tool_name}")
                self.logger.info(f"  already   binding {tool_name}")
                continue
            legacy = LEGACY_BINDINGS.get(tool_name, ())
            if bound and all(
                (b.get("ApiSource"), b.get("ApiIdentifier"), b.get("Operation")) in legacy
                for b in bound
            ):
                if self.dry_run:
                    self.skipped.append(f"binding {tool_name} (would rebind legacy)")
                    self.logger.info(f"  would rebind  {tool_name} (legacy binding)")
                    continue
                if not all(
                    self._tooling_delete(
                        "McpServerToolApiDefinition",
                        b["Id"],
                        f"legacy binding {tool_name} "
                        f"({b.get('ApiSource')} {b.get('ApiIdentifier')}), rebinding",
                        on_failure=(
                            f"could not delete legacy binding {tool_name} ({b['Id']}); the "
                            f"server may stay unserved until it is deleted in Setup"
                        ),
                    )
                    for b in bound
                ):
                    continue
                bound = []
            if bound:
                found = "; ".join(
                    f"{b.get('ApiSource')} {b.get('ApiIdentifier')} {b.get('Operation')}"
                    for b in bound
                )
                message = (
                    f"binding {tool_name}: tool is bound to [{found}], expected "
                    f"{api_source} {api_identifier} {operation}; fix or delete it in Setup"
                )
                self.failed.append(message)
                self.logger.error(f"  FAILED    {message}")
                continue

            binding_id = self._tooling_create(
                "McpServerToolApiDefinition",
                {
                    "ToolId": tool_id,
                    "ApiSource": api_source,
                    "ApiIdentifier": api_identifier,
                    "Operation": operation,
                },
                f"binding {tool_name} ({api_source})",
                # The org's Connect catalog does not list this identifier: not
                # something this task can fix, so warn and skip the tool.
                soft_error=(
                    UNRESOLVED_IDENTIFIER_MARK if api_source == "CONNECT" else None
                ),
            )
            if not binding_id and not self.dry_run:
                # A tool with no binding makes the gateway answer 500 for the WHOLE
                # server (verified on 264), so an unbound tool must not be left behind.
                hint = ""
                if self._last_soft_error:
                    unresolved.add((api_source, api_identifier))
                    hint = f"; the org does not resolve CONNECT {api_identifier}"
                self._tooling_delete(
                    "McpServerToolDefinition",
                    tool_id,
                    f"tool {tool_name} (unbound, removed so the server stays served{hint})",
                    on_failure=(
                        f"could not delete unbound tool {tool_name} ({tool_id}); the gateway "
                        f"returns 500 for the whole server until it is deleted in Setup"
                    ),
                )

    def _ensure_custom_access(self, server_id: str):
        # For a CUSTOM server, DeveloperName must EQUAL the definition's
        # DeveloperName. The namespaced form used for hosted servers fails with
        # FIELD_INTEGRITY_EXCEPTION here.
        self._ensure_access(
            self._existing_access().get(CUSTOM_SERVER_DEVELOPER_NAME),
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
                elif developer_name == CUSTOM_SERVER_DEVELOPER_NAME:
                    note = "custom server (custom_server off; not removed)"
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
        for tool_id, records in self._bindings_by_tool(
            [tool["Id"] for tool in tools]
        ).items():
            bindings[tool_id] = [
                f"{r.get('ApiSource')} {r.get('ApiIdentifier')}" for r in records
            ]
        for tool in tools:
            bound = (
                "; ".join(bindings.get(tool["Id"], []))
                or "NO BINDING — the gateway fails the whole server until this is fixed"
            )
            self.logger.info(f"  {tool['ToolName']:26} {bound}")

    def _report(self):
        self.logger.info(
            f"Summary: created {len(self.created)}  "
            f"already/skipped {len(self.skipped)}  warnings {len(self.warnings)}  "
            f"failed {len(self.failed)}"
        )
        for warning in self.warnings:
            self.logger.warning(f"  WARNING {warning}")
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

    def _existing_access(self) -> Dict[str, Dict[str, Any]]:
        return {
            record["DeveloperName"]: record
            for record in self._tooling_query(
                "SELECT Id, DeveloperName, MasterLabel, McpServerId, Active "
                "FROM McpServerAccess"
            )
        }

    def _bindings_by_tool(self, tool_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Bindings keyed by ToolId, queried only for the given tools."""
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        if not tool_ids:
            return grouped
        id_list = ", ".join(f"'{tool_id}'" for tool_id in tool_ids)
        for record in self._tooling_query(
            "SELECT Id, ToolId, ApiSource, ApiIdentifier, Operation "
            f"FROM McpServerToolApiDefinition WHERE ToolId IN ({id_list})"
        ):
            grouped.setdefault(record["ToolId"], []).append(record)
        return grouped

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

    def _tooling_update(
        self, sobject: str, record_id: str, body: Dict[str, Any], label: str
    ) -> bool:
        if self.dry_run:
            self.skipped.append(f"{label} (would update)")
            self.logger.info(f"  would update  {label}")
            return False

        url = (
            f"{self.instance_url}/services/data/v{self.api_version}"
            f"/tooling/sobjects/{sobject}/{record_id}"
        )
        response = requests.patch(url, headers=self._headers, json=body)
        if response.status_code >= 400:
            message = response.text[:200].replace("\n", " ")
            self.failed.append(f"{label}: {message}")
            self.logger.error(f"  FAILED    {label}: {message}")
            return False

        self.created.append(label)
        self.logger.info(f"  updated   {label}  {record_id}")
        return True

    def _tooling_delete(
        self, sobject: str, record_id: str, label: str, on_failure: str
    ) -> bool:
        if self.dry_run:
            self.logger.info(f"  would delete  {label}")
            return False

        url = (
            f"{self.instance_url}/services/data/v{self.api_version}"
            f"/tooling/sobjects/{sobject}/{record_id}"
        )
        response = requests.delete(url, headers=self._headers)
        if response.status_code >= 400:
            message = response.text[:200].replace("\n", " ")
            self.failed.append(f"{on_failure}: {message}")
            self.logger.error(f"  FAILED    {on_failure}: {message}")
            return False

        self.logger.warning(f"  deleted   {label}  {record_id}")
        return True

    def _warn(self, message: str):
        self.warnings.append(message)
        self.logger.warning(f"  WARNING   {message}")

    def _tooling_create(
        self,
        sobject: str,
        body: Dict[str, Any],
        label: str,
        soft_error: Optional[str] = None,
    ) -> Optional[str]:
        """Create a record. A rejection containing ``soft_error`` is a warning,
        not a failure; ``_last_soft_error`` says which one happened."""
        self._last_soft_error = False
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
            if soft_error and soft_error in response.text:
                self._last_soft_error = True
                self._warn(f"{label}: {message}")
                return None
            self.failed.append(f"{label}: {message}")
            self.logger.error(f"  FAILED    {label}: {message}")
            return None

        record_id = response.json().get("id")
        self.created.append(label)
        self.logger.info(f"  created   {label}  {record_id}")
        return record_id
