"""
Activate Salesforce Hosted MCP servers via the Tooling API.

MCP servers in Salesforce have a two-part lifecycle:

  1. The *definition* (``McpServerDefinition``) is deployed via the Metadata
     API — for the custom RLM server this happens in ``deploy_post_mcp``. A
     freshly deployed server is **Inactive**.
  2. *Activation* is a separate ``McpServerAccess`` record (Tooling API only —
     it is NOT deployable via Metadata API). A server is active iff an
     ``McpServerAccess`` row exists with ``Active = true``.

The set of servers to activate is declared as an explicit, source-controlled
**manifest** of Tooling-API ``McpServerAccess`` payloads under
``datasets/tooling/McpServerAccess/`` (``platform_servers.json`` +
``custom_servers.json``). Each file is a JSON array of records; see that
folder's README for the contract. To enable another server, add a row — no code
change here.

Two server *kinds*, resolved differently (declared via each row's ``kind``):

  * **Custom** servers each have an ``McpServerDefinition`` record (deployed via
    Metadata API), so their ``McpServerAccess.McpServerId`` is resolved at
    runtime by querying that definition's Id (never hardcoded across orgs).
  * **Platform** servers (``platform_sobject_*``) have **no** definition record
    (``McpServerId = null``) and are not pre-seeded as access records, so they
    cannot be discovered — they must be declared in the manifest.

Activation is **manifest-only** — the only servers activated are those declared
in the manifest. There is **no auto-discovery**: deploying an
``McpServerDefinition`` does NOT activate it; a row must be added here. This keeps
the enabled set an explicit, reviewable, source-controlled decision. The RLM
build's default manifest activates:

  * ``platform_sobject_all`` (the platform SObject server — its tools already
    include the delete tools, so the narrower ``platform_sobject_deletes`` is not
    separately activated), ``platform_metadata_experts``, and
    ``platform_salesforce_api_context``
  * ``RLMQuotingMCP`` (the custom RLM server)

Options (see ``task_options``) — the activated set is tunable per-org / per-flow
without editing this file:

  * ``manifest_dir`` — folder of ``*.json`` ``McpServerAccess`` arrays
    (default ``datasets/tooling/McpServerAccess``).

Behavior (deliberate, because the ``mcp`` feature flag is opt-in — running this
task expresses intent to enable these servers):

  * **Precheck / hard-fail:** every target is resolved BEFORE any write. If the
    custom server's ``McpServerDefinition`` is missing (deploy step skipped or
    failed), the task raises immediately and writes nothing — no partial state.
  * **Activate-if-absent, reactivate-if-disabled:** creates the access record
    when missing, flips ``Active`` to ``true`` when present-but-disabled, and
    no-ops when already active.
  * **Respects manually-managed records:** if an access record already exists
    with a different ``MasterLabel`` / ``McpServerId``, those fields are treated
    as authoritative and left untouched — only ``Active = true`` is enforced.
    Divergent linkage is logged for visibility, not overwritten.

Idempotent: a second run reports all targets already active with zero changes.
"""

import json
import os

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.core.utils import process_bool_arg
except ImportError:  # pragma: no cover - allows import outside a CCI runtime
    BaseTask = object
    TaskOptionsError = Exception

    def process_bool_arg(arg):  # minimal stand-in for non-CCI imports
        if isinstance(arg, bool):
            return arg
        return str(arg).strip().lower() in ("true", "1", "yes", "y", "on")


# Default location of the source-controlled McpServerAccess manifest — a folder
# of JSON arrays whose objects map to Tooling-API McpServerAccess fields. See
# datasets/tooling/McpServerAccess/README.md for the contract.
DEFAULT_MANIFEST_DIR = "datasets/tooling/McpServerAccess"

# Recognized server ``kind`` values in the manifest. ``platform`` rows have no
# McpServerDefinition (McpServerId = null); ``custom`` rows resolve their
# McpServerId at runtime by DeveloperName.
KIND_PLATFORM = "platform"
KIND_CUSTOM = "custom"


def _soql_escape(value):
    """Escape a string literal for safe interpolation into SOQL.

    DeveloperName / Id values are platform-constrained to alphanumerics today, so
    this is defense-in-depth rather than a known live vector — but it keeps the
    query correct if a value ever carries a quote or backslash (e.g. a future,
    less-constrained field, or a copy of this helper)."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


class ActivateMcpServers(BaseTask):
    """Activate the RLM MCP servers (platform SObject servers + custom RLM server)."""

    # This task hits an org (the Tooling API), so it must accept ``--org`` on
    # ``cci task run`` and fail clearly when no org is available. ``BaseTask``
    # defaults ``salesforce_task`` to ``False`` (no ``--org`` flag, silently
    # uses the default org); set it True so the task is portable for direct
    # runs as well as inside ``prepare_rlm_org`` / ``prepare_mcp``. We keep the
    # ``BaseTask`` base + manual ``org_config.access_token`` Tooling pattern
    # (the repo's blessed approach for direct REST/Tooling calls) rather than
    # ``BaseSalesforceApiTask`` (which is for CCI's built-in ``self.sf`` client).
    salesforce_task = True

    task_docs = """
    Activates Salesforce Hosted MCP servers for the RLM build by upserting
    ``McpServerAccess`` records via the Tooling API.

    Activation is **manifest-driven**: a server is activated only if it is
    explicitly declared in the source-controlled manifest
    (``datasets/tooling/McpServerAccess/`` — JSON arrays of McpServerAccess
    payloads). Deploying an ``McpServerDefinition`` alone does NOT activate it;
    there is no auto-discovery. To enable a server, add a manifest row — no code
    change here.

    Idempotent and opt-in (gated by the ``mcp`` feature flag): creates the
    access record if absent, reactivates it if disabled, no-ops if already
    active. Existing manually-managed records keep their label/linkage; only
    ``Active = true`` is enforced.
    """

    task_options = {
        "manifest_dir": {
            "description": (
                "Folder of `*.json` McpServerAccess payload arrays declaring which "
                "servers to activate. Default: 'datasets/tooling/McpServerAccess'. "
                "See that folder's README for the JSON contract."
            ),
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.manifest_dir = self.options.get("manifest_dir") or DEFAULT_MANIFEST_DIR

    def _load_manifest(self):
        """Load and validate the McpServerAccess manifest.

        Returns an ordered list of normalized server dicts
        ``{developer_name, master_label, language, active, custom}``. Reads every
        ``*.json`` in ``manifest_dir`` (sorted for deterministic order). Each
        file must be a JSON array of objects carrying at least ``kind`` and
        ``DeveloperName``.
        """
        if not os.path.isdir(self.manifest_dir):
            raise TaskOptionsError(
                f"manifest_dir not found: {self.manifest_dir}. Expected a folder "
                "of McpServerAccess JSON payloads (see "
                "datasets/tooling/McpServerAccess/README.md)."
            )

        servers = []
        seen = set()
        files = sorted(
            f for f in os.listdir(self.manifest_dir) if f.endswith(".json")
        )
        for fname in files:
            path = os.path.join(self.manifest_dir, fname)
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, list):
                raise TaskOptionsError(f"{path} must contain a JSON array")
            for idx, row in enumerate(payload, start=1):
                if not isinstance(row, dict):
                    raise TaskOptionsError(f"{path} row {idx} must be an object")
                kind = str(row.get("kind", "")).strip().lower()
                if kind not in (KIND_PLATFORM, KIND_CUSTOM):
                    raise TaskOptionsError(
                        f"{path} row {idx}: 'kind' must be "
                        f"'{KIND_PLATFORM}' or '{KIND_CUSTOM}' (got {row.get('kind')!r})"
                    )
                dev_name = str(row.get("DeveloperName", "")).strip()
                if not dev_name:
                    raise TaskOptionsError(
                        f"{path} row {idx}: 'DeveloperName' is required"
                    )
                if dev_name in seen:
                    raise TaskOptionsError(
                        f"Duplicate McpServerAccess DeveloperName '{dev_name}' "
                        f"in manifest ({path} row {idx})"
                    )
                seen.add(dev_name)
                servers.append(
                    {
                        "developer_name": dev_name,
                        "master_label": str(
                            row.get("MasterLabel") or dev_name
                        ).strip(),
                        "language": str(row.get("Language") or "en_US").strip(),
                        "active": (
                            True
                            if row.get("Active") is None
                            else process_bool_arg(row.get("Active"))
                        ),
                        "custom": kind == KIND_CUSTOM,
                    }
                )
        return servers

    def _run_task(self):
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = getattr(self.org_config, "api_version", None) or "67.0"
        api_version = str(api_version).lstrip("v")

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self.instance_url = instance_url
        self.tooling_base = f"{instance_url}/services/data/v{api_version}/tooling"

        # The manifest is the single source of truth — only servers declared
        # there are activated (no auto-discovery of deployed definitions).
        servers = self._load_manifest()
        if not servers:
            self.logger.warning(
                "No MCP servers declared in the manifest (%s); nothing to do. "
                "Add a row to activate a server.",
                self.manifest_dir,
            )
            return
        self.logger.info(
            "Activating %d MCP server(s) declared in %s: %s",
            len(servers),
            self.manifest_dir,
            [s["developer_name"] for s in servers],
        )

        # ── Phase 1: resolve every target BEFORE any write (hard-fail) ──────
        # Each resolved target carries its McpServerId (None for platform) and
        # the existing McpServerAccess record (if any).
        resolved = []
        for server in servers:
            dev_name = server["developer_name"]
            if server["custom"]:
                mcp_server_id = self._resolve_definition_id(dev_name)
                if not mcp_server_id:
                    raise TaskOptionsError(
                        f"McpServerDefinition '{dev_name}' was not found in the org. "
                        "Deploy it first (deploy_post_mcp / the 'mcp' feature flag) "
                        "before running activate_mcp_servers. No records were modified."
                    )
            else:
                mcp_server_id = None

            existing = self._query_access_record(dev_name, mcp_server_id)
            resolved.append(
                {
                    "server": server,
                    "mcp_server_id": mcp_server_id,
                    "existing": existing,
                }
            )

        # ── Phase 2: activate (create / reactivate / no-op) ─────────────────
        activated, reactivated, already_active = [], [], []
        for item in resolved:
            server = item["server"]
            dev_name = server["developer_name"]
            mcp_server_id = item["mcp_server_id"]
            existing = item["existing"]

            if existing is None:
                self._create_access_record(server, mcp_server_id)
                activated.append(dev_name)
                continue

            # Existing record: respect manually-managed label/linkage, only
            # enforce Active=true. Surface divergent linkage for visibility.
            self._warn_on_divergence(existing, server, mcp_server_id)

            # A manifest row may declare Active:false (registered but
            # deliberately disabled). Honor that intent but never tear down an
            # already-active record — this task only ever moves toward active.
            if not server.get("active", True):
                self.logger.info(
                    "MCP server '%s' declared Active:false in manifest; leaving "
                    "as-is (currently %s).",
                    dev_name,
                    "active" if existing.get("Active") else "inactive",
                )
                continue

            if existing.get("Active"):
                already_active.append(dev_name)
            else:
                self._patch_active(existing["Id"], dev_name)
                reactivated.append(dev_name)

        self.logger.info(
            "MCP server activation complete — created: %s | reactivated: %s | "
            "already active: %s",
            activated or "none",
            reactivated or "none",
            already_active or "none",
        )

    # ────────────────────────────────────────────────────────────────────────
    # Tooling API helpers
    # ────────────────────────────────────────────────────────────────────────
    def _tooling_query(self, soql):
        resp = requests.get(
            f"{self.tooling_base}/query",
            headers=self.headers,
            params={"q": soql},
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(
                f"Tooling query failed: {resp.status_code} {resp.text}\nSOQL: {soql}"
            )
        return resp.json().get("records", [])

    def _resolve_definition_id(self, developer_name):
        records = self._tooling_query(
            "SELECT Id FROM McpServerDefinition "
            f"WHERE DeveloperName = '{_soql_escape(developer_name)}'"
        )
        return records[0]["Id"] if records else None

    def _query_access_record(self, developer_name, mcp_server_id):
        # Match on DeveloperName AND McpServerId (DeveloperName alone is not
        # assumed unique across namespaces). Platform servers => null id.
        id_clause = (
            f"McpServerId = '{_soql_escape(mcp_server_id)}'"
            if mcp_server_id
            else "McpServerId = null"
        )
        records = self._tooling_query(
            "SELECT Id, Active, MasterLabel, McpServerId FROM McpServerAccess "
            f"WHERE DeveloperName = '{_soql_escape(developer_name)}' AND {id_clause}"
        )
        return records[0] if records else None

    def _create_access_record(self, server, mcp_server_id):
        dev_name = server["developer_name"]
        body = {
            "DeveloperName": dev_name,
            "MasterLabel": server["master_label"],
            "Language": server.get("language", "en_US"),
            "Active": server.get("active", True),
        }
        if mcp_server_id:
            body["McpServerId"] = mcp_server_id

        resp = requests.post(
            f"{self.tooling_base}/sobjects/McpServerAccess",
            headers=self.headers,
            json=body,
            timeout=30,
        )
        if resp.ok:
            self.logger.info("Activated MCP server '%s' (created access record).", dev_name)
            return

        # A DUPLICATE_VALUE means a record already exists (race / pre-existing
        # row our matched query didn't catch). Do NOT assume success — re-query
        # and ensure it is active. Match only on the errorCode (not a bare 400),
        # so genuine validation failures surface as errors instead of being
        # misrouted through duplicate-recovery.
        if "DUPLICATE_VALUE" in resp.text:
            existing = self._query_access_record(dev_name, mcp_server_id)
            if existing is None:
                raise RuntimeError(
                    f"Failed to create McpServerAccess for '{dev_name}': "
                    f"{resp.status_code} {resp.text}"
                )
            if existing.get("Active"):
                self.logger.info(
                    "MCP server '%s' already active (existing access record).", dev_name
                )
            else:
                self._patch_active(existing["Id"], dev_name)
            return

        raise RuntimeError(
            f"Failed to create McpServerAccess for '{dev_name}': "
            f"{resp.status_code} {resp.text}"
        )

    def _patch_active(self, record_id, dev_name):
        resp = requests.patch(
            f"{self.tooling_base}/sobjects/McpServerAccess/{record_id}",
            headers=self.headers,
            json={"Active": True},
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(
                f"Failed to activate McpServerAccess '{dev_name}' ({record_id}): "
                f"{resp.status_code} {resp.text}"
            )
        self.logger.info("Reactivated MCP server '%s'.", dev_name)

    def _warn_on_divergence(self, existing, server, mcp_server_id):
        existing_label = existing.get("MasterLabel")
        if existing_label and existing_label != server["master_label"]:
            self.logger.warning(
                "Existing McpServerAccess for '%s' has MasterLabel '%s' "
                "(build expects '%s'); leaving it as-is (admin-managed).",
                server["developer_name"],
                existing_label,
                server["master_label"],
            )
        existing_id = existing.get("McpServerId")
        if mcp_server_id and existing_id and existing_id != mcp_server_id:
            self.logger.warning(
                "Existing McpServerAccess for '%s' links McpServerId '%s' "
                "(deployed definition is '%s'); leaving linkage as-is.",
                server["developer_name"],
                existing_id,
                mcp_server_id,
            )
