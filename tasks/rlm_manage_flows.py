"""
Custom CumulusCI task for Flow management.

This task provides functionality to:
- Query/list flow versions (by DeveloperName, status, process type)
- Activate/deactivate flows by DeveloperName

Tooling API model (verified live on 264):
- `Flow` is one row per flow VERSION: Id, DefinitionId, Definition.DeveloperName,
  MasterLabel, Status (Active/Draft/Obsolete/InvalidDraft), ProcessType, VersionNumber.
  It is read-only for status changes (a PATCH of Status is rejected).
- `FlowDefinition` is one row per flow. Activating or deactivating means PATCHing
  Metadata.activeVersionNumber (the version number to activate, 0 to deactivate).
"""
import re
from typing import Dict, List, Optional

# Import before CumulusCI: cumulusci's project_config does sys.modules.setdefault("tasks", <synthetic>) and then
# sets tasks.__path__ = [], which empties the repo package's path, so a later `tasks.soql_utils` import fails.
from tasks.soql_utils import positive_int, soql_quote, split_names

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


# A FlowDefinition Id (key prefix 300), 15 or 18 characters.
_DEFINITION_ID = re.compile(r"^300[A-Za-z0-9]{12}([A-Za-z0-9]{3})?$")

# sort_by values accepted, mapped to the Flow field they order by.
_SORT_FIELDS = {
    "developername": "Definition.DeveloperName",
    "label": "MasterLabel",
    "masterlabel": "MasterLabel",
    "status": "Status",
    "processtype": "ProcessType",
    "versionnumber": "VersionNumber",
    "createddate": "CreatedDate",
    # Flow has no LastModifiedDate; a version is immutable once created.
    "lastmodifieddate": "CreatedDate",
}

# sort_by/sort_order carry cumulusci.yml defaults and cannot change what is activated.
_MUTATING_REJECTS = ("status", "process_type", "limit")


class ManageFlows(BaseSalesforceTask):
    """
    Flow management task.

    Supports:
    - Querying flow versions (by DeveloperName, status, process type)
    - Listing flows with metadata
    - Activating (newest Draft or Active version; see _activation_target) and deactivating flows by DeveloperName
    """

    task_options = {
        "operation": {
            "description": "Operation to perform: 'list', 'query', 'activate', 'deactivate'",
            "required": True
        },
        "developer_names": {
            "description": (
                "Flow DeveloperNames to operate on: a comma-separated string or a list "
                "(a FlowDefinition Id also works; list shows it). Required for activate and "
                "deactivate, which refuse a DeveloperName shared by two flows (pass the Id). "
                "For list and query, omitted means all flows. Names that match no flow "
                "are an error."
            ),
            "required": False
        },
        "status": {
            "description": (
                "list/query only: filter flow versions by Status ('Active', 'Draft', "
                "'Obsolete', 'InvalidDraft'). Default: all. Rejected by activate and deactivate."
            ),
            "required": False
        },
        "process_type": {
            "description": "list/query only: filter by ProcessType (e.g., 'AutoLaunchedFlow', 'Flow', 'Workflow'). Default: None. Rejected by activate and deactivate.",
            "required": False
        },
        "sort_by": {
            "description": (
                "list/query: DeveloperName, Label, Status, ProcessType, VersionNumber or "
                "CreatedDate. LastModifiedDate is accepted as CreatedDate. Default: CreatedDate"
            ),
            "required": False
        },
        "sort_order": {
            "description": "list/query: 'Asc' or 'Desc'. Default: 'Desc'",
            "required": False
        },
        "limit": {
            "description": "list/query only: maximum number of flow versions to return. Default: None (no limit). Rejected by activate and deactivate.",
            "required": False
        }
    }

    def _run_task(self):
        """Execute the task based on the operation specified."""
        operation = (self._option_text("operation") or "").lower()

        if operation == "list":
            self._list_flows()
        elif operation == "query":
            # The rows go to flow steps (^^step.flows) and Python callers; the CLI prints only a count.
            self.return_values = {"flows": self._query_flows()}
        elif operation == "activate":
            self._activate_flows()
        elif operation == "deactivate":
            self._deactivate_flows()
        else:
            raise TaskOptionsError(f"Unknown operation: {operation}. Supported operations: 'list', 'query', 'activate', 'deactivate'")

    # -- shared plumbing ------------------------------------------------

    def _api_version(self) -> str:
        # Not org_config.api_version: OrgConfig has no such attribute (BaseConfig.__getattr__ warns, and
        # raises AssertionError under STRICT_GETATTR). The project's API version is what the repo's tasks use.
        version = self.project_config.project__package__api_version
        if not version:
            raise TaskOptionsError("No API version: set project.package.api_version in cumulusci.yml")
        return str(version).lstrip("v")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _tooling_url(self, path: str) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._api_version()}/tooling/{path}"

    def _tooling_query(self, soql: str) -> List[Dict]:
        """Run a Tooling API query and follow nextRecordsUrl."""
        import requests

        self.logger.debug(f"Executing Tooling API SOQL query: {soql}")
        response = requests.get(self._tooling_url("query"), headers=self._headers(), params={"q": soql})
        records: List[Dict] = []
        while True:
            if not response.ok:
                raise TaskOptionsError(f"Failed to query flows: {response.status_code} - {response.text}")
            body = response.json() or {}
            records.extend(body.get("records", []))
            next_url = body.get("nextRecordsUrl")
            if not next_url or body.get("done", True):
                break
            response = requests.get(
                f"{self.org_config.instance_url}{next_url}", headers=self._headers()
            )
        for record in records:
            record.pop("attributes", None)
            if isinstance(record.get("Definition"), dict):
                record["Definition"].pop("attributes", None)
        return records

    def _requested_names(self) -> List[str]:
        value = self.options.get("developer_names")
        if value is None or value == "" or value == []:
            return []
        return split_names(value, "developer_names", TaskOptionsError)

    # -- list / query ---------------------------------------------------

    def _list_flows(self):
        """List flows with their metadata."""
        flows = self._query_flows()

        if not flows:
            self.logger.info("No flows found matching the criteria.")
            return flows

        self.logger.info(f"Found {len(flows)} flow version(s):")
        self.logger.info("")
        # DefinitionId tells apart two flows that share a DeveloperName (a managed package's and the org's).
        self.logger.info(
            f"{'DeveloperName':<50} {'DefinitionId':<19} {'MasterLabel':<50} {'Status':<12} {'ProcessType':<20} {'Version':<10}"
        )
        self.logger.info("-" * 162)

        for flow in flows:
            self.logger.info(
                f"{self._developer_name(flow):<50} {flow.get('DefinitionId') or 'N/A':<19} "
                f"{flow.get('MasterLabel') or 'N/A':<50} "
                f"{flow.get('Status') or 'N/A':<12} {flow.get('ProcessType') or 'N/A':<20} "
                f"{str(flow.get('VersionNumber', 'N/A')):<10}"
            )

        return flows

    def _option_text(self, name: str) -> Optional[str]:
        """The option as stripped text; blank or whitespace means not set."""
        value = str(self.options.get(name) or "").strip()
        return value or None

    @staticmethod
    def _developer_name(flow: Dict) -> str:
        return (flow.get("Definition") or {}).get("DeveloperName") or flow.get("DefinitionId") or "N/A"

    def _query_flows(self) -> List[Dict]:
        """Query flow versions from the Tooling API, one row per version."""
        names = self._requested_names()
        flows = self._tooling_query(self._build_soql_query(names=names))
        if names:
            # status, process_type and limit may legitimately leave out a flow that exists, so a
            # name is only "missing" when no flow of that name exists at all: check against an
            # unfiltered, unordered, unlimited query (the main query already is that when none is set).
            by_name = flows
            if self._option_text("status") or self._option_text("process_type") or self._option_text("limit"):
                by_name = self._tooling_query(self._build_soql_query(names=names, filtered=False, ordered=False))
            self._raise_on_missing(names, by_name)
        self.logger.info(f"Query returned {len(flows)} flow version(s).")
        return flows

    def _raise_on_missing(self, names: List[str], rows: List[Dict]):
        """Raise when a requested name (DeveloperName or FlowDefinition Id) matches no flow."""
        # DeveloperName comparison in SOQL is case-insensitive, so that check is too. An 18-character Id is
        # case-insensitive by design (the last three characters encode the case of the first 15); a
        # 15-character Id is case-sensitive. A 15-character Id also matches the first 15 of the 18.
        found_names = {self._developer_name(row).lower() for row in rows}
        found_ids18 = {row["DefinitionId"].lower() for row in rows}
        found_ids15 = {row["DefinitionId"][:15] for row in rows}
        missing = []
        for n in names:
            if not _DEFINITION_ID.match(n):
                ok = n.lower() in found_names
            elif len(n) == 18:
                ok = n.lower() in found_ids18
            else:
                ok = n in found_ids15
            if not ok:
                missing.append(n)
        if missing:
            raise TaskOptionsError(
                "No flow matches: " + ", ".join(missing)
                + ". Nothing was changed. Run list without developer_names to see the DeveloperNames."
            )

    def _name_clause(self, names: List[str]) -> str:
        ids = [n for n in names if _DEFINITION_ID.match(n)]
        dev_names = [n for n in names if n not in ids]
        parts = []
        if dev_names:
            parts.append("Definition.DeveloperName IN (" + ", ".join(soql_quote(n) for n in dev_names) + ")")
        if ids:
            parts.append("DefinitionId IN (" + ", ".join(soql_quote(n) for n in ids) + ")")
        return parts[0] if len(parts) == 1 else "(" + " OR ".join(parts) + ")"

    def _build_soql_query(self, names=None, filtered=True, ordered=True) -> str:
        """Build the Flow SOQL from the task options (every value escaped or whitelisted)."""
        fields = [
            "Id",
            "DefinitionId",
            "Definition.DeveloperName",
            "MasterLabel",
            "Status",
            "ProcessType",
            "VersionNumber",
            "Description",
            "CreatedDate",
        ]
        where = []

        names = self._requested_names() if names is None else names
        if names:
            where.append(self._name_clause(names))

        status = self._option_text("status")
        if status and filtered:
            where.append(f"Status = {soql_quote(status)}")

        process_type = self._option_text("process_type")
        if process_type and filtered:
            where.append(f"ProcessType = {soql_quote(process_type)}")

        soql = f"SELECT {', '.join(fields)} FROM Flow"
        if where:
            soql += " WHERE " + " AND ".join(where)

        if ordered:
            sort_key = (self._option_text("sort_by") or "CreatedDate").replace("_", "").lower()
            if sort_key not in _SORT_FIELDS:
                raise TaskOptionsError(
                    f"sort_by must be one of DeveloperName, Label, Status, ProcessType, "
                    f"VersionNumber, CreatedDate; got {self.options.get('sort_by')!r}"
                )
            sort_order = (self._option_text("sort_order") or "Desc").capitalize()
            if sort_order not in ("Asc", "Desc"):
                raise TaskOptionsError(f"sort_order must be 'Asc' or 'Desc', got {self.options.get('sort_order')!r}")
            soql += f" ORDER BY {_SORT_FIELDS[sort_key]} {sort_order}"

            limit = self._option_text("limit")
            if limit:
                soql += f" LIMIT {positive_int(limit, 'limit', TaskOptionsError)}"

        return soql

    # -- activate / deactivate ------------------------------------------

    def _activate_flows(self):
        """Activate each named flow (see _activation_target for which version)."""
        self._change_activation(activate=True)

    def _deactivate_flows(self):
        """Deactivate each named flow (no version stays active)."""
        self._change_activation(activate=False)

    def _definitions_to_change(self, verb: str) -> Dict[str, List[Dict]]:
        """Resolve developer_names to {DefinitionId: [version rows]}; error on any miss."""
        for opt in _MUTATING_REJECTS:
            if self._option_text(opt):
                raise TaskOptionsError(
                    f"{opt} is not used by {verb}; it only filters list and query. Remove it."
                )
        names = self._requested_names()
        if not names:
            raise TaskOptionsError(f"developer_names is required for {verb}")

        rows = self._tooling_query(self._build_soql_query(names=names, ordered=False))
        by_definition: Dict[str, List[Dict]] = {}
        for row in rows:
            by_definition.setdefault(row["DefinitionId"], []).append(row)

        self._raise_on_missing(names, rows)
        # A managed package's flow can share a DeveloperName with an org flow; changing both
        # would be a surprise, so a DeveloperName that resolves to more than one flow is refused
        # (a DefinitionId names exactly one).
        # Names compare case-insensitively, as the lookup does (MyFlow and myflow are the same request).
        requested = {n.lower() for n in names if not _DEFINITION_ID.match(n)}
        names_seen: Dict[str, List[str]] = {}
        for def_id, versions in by_definition.items():
            key = self._developer_name(versions[0]).lower()
            if key in requested:
                names_seen.setdefault(key, []).append(def_id)
        ambiguous = {n: ids for n, ids in names_seen.items() if len(ids) > 1}
        if ambiguous:
            detail = "; ".join(
                ", ".join(f"{self._developer_name(by_definition[i][0])} ({i})" for i in sorted(ids))
                for _, ids in sorted(ambiguous.items())
            )
            raise TaskOptionsError(
                f"Cannot {verb}: these names match more than one flow (pass the DefinitionId instead): {detail}"
            )
        return by_definition

    def _change_activation(self, activate: bool):
        verb, past, gerund = (
            ("activate", "activated", "Activating") if activate
            else ("deactivate", "deactivated", "Deactivating")
        )
        definitions = self._definitions_to_change(verb)

        self.logger.info(f"{gerund} {len(definitions)} flow(s)...")
        success_count = skipped = fail_count = 0

        for def_id, versions in definitions.items():
            name = self._developer_name(versions[0])
            try:
                if activate:
                    target = self._activation_target(versions)
                    if target.get("Status") == "Active":
                        skipped += 1
                        self.logger.info(f"'{name}' version {target['VersionNumber']} is already active. Skipping.")
                        continue
                    self._set_active_version(def_id, int(target["VersionNumber"]))
                    self.logger.info(f"Activated '{name}' (version {target['VersionNumber']})")
                else:
                    if not any(v.get("Status") == "Active" for v in versions):
                        skipped += 1
                        self.logger.info(f"'{name}' has no active version. Skipping.")
                        continue
                    self._set_active_version(def_id, 0)
                    self.logger.info(f"Deactivated '{name}'")
                success_count += 1
            except Exception as e:
                fail_count += 1
                self.logger.error(f"Failed to {verb} '{name}': {e}")

        self.logger.info(
            f"{verb.capitalize()} summary: {success_count} {past}, "
            f"{skipped} already in that state, {fail_count} failed"
        )
        if fail_count > 0:
            raise TaskOptionsError(f"Failed to {verb} {fail_count} flow(s). Check logs for details.")

    @staticmethod
    def _activation_target(versions: List[Dict]) -> Dict:
        """Pick the version to activate.

        A version is Active, Draft, Obsolete (superseded or deactivated) or InvalidDraft,
        which is never chosen.
        - When a version is Active: the newest Draft numbered above it, else the Active one
          itself (the flow is skipped), so a rollback to an older active version stands and an
          abandoned older draft is never picked.
        - When none is Active: the newest Draft or Obsolete version, so a deactivated flow
          is restored to its newest non-active version. The org keeps no record of which
          version was last active, so this is the newest Draft or Obsolete one, not
          necessarily the version that was live.
        """
        def number(v):
            return int(v.get("VersionNumber") or 0)

        def newest(rows):
            return max(rows, key=number)

        active = [v for v in versions if v.get("Status") == "Active"]
        if active:
            current = newest(active)
            newer_drafts = [
                v for v in versions if v.get("Status") == "Draft" and number(v) > number(current)
            ]
            return newest(newer_drafts) if newer_drafts else current
        candidates = [v for v in versions if v.get("Status") in ("Draft", "Obsolete")]
        if candidates:
            return newest(candidates)
        seen = sorted({str(v.get("Status")) for v in versions})
        raise TaskOptionsError(
            "it has no Draft, Active or Obsolete version to activate (statuses seen: " + ", ".join(seen) + ")"
        )

    def _set_active_version(self, definition_id: str, version_number: int):
        """PATCH FlowDefinition.Metadata.activeVersionNumber (0 deactivates)."""
        import requests

        url = self._tooling_url(f"sobjects/FlowDefinition/{definition_id}")
        payload = {"Metadata": {"activeVersionNumber": version_number}}
        response = requests.patch(url, headers=self._headers(), json=payload)
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"FlowDefinition update returned {response.status_code} - {response.text}"
            )
        return True
