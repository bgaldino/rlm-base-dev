"""
Custom CumulusCI task for comprehensive Decision Table management.

This task provides functionality to:
- Query/list decision tables
- Refresh decision tables (full or incremental)
- Support other operations (activate, deactivate, etc.)

Modelled on the behaviour the ``RLM_Refresh_Decision_Tables`` screen flow used to
provide, which this task predates the removal of:
- Queries DecisionTable records with Status = 'Active'
- Uses refreshDecisionTable action
- Supports All / ByUsageType / Individual modes with incremental refresh toggle

⚠ That screen flow is GONE — do not go looking for it as a reference. In the org the
equivalents are the **Decision Table Manager** component on the Home page
(interactive, with a freshness verdict per table) and ``RLM_Refresh_Decision_Tables_Bulk``
(autolaunched; the only route Apex has to the refresh action). Do not confuse either
with ``RLM_Refresh_Decision_Tables_By_Usage_Type``, which is a different, live flow
called by ``RLM_Account_Utilities``. For headless verdicts see the
``check_decision_table_freshness`` task.
"""
import json
from typing import List, Dict, Optional, Set
from datetime import datetime

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.core.utils import process_bool_arg
    from simple_salesforce import Salesforce
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception
    Salesforce = None

    def process_bool_arg(arg):
        """
        Offline fallback so this module still imports without CumulusCI.

        ⚠ Mirrors cumulusci.core.utils.process_bool_arg deliberately, INCLUDING the
        TypeError on an uninterpretable value. An earlier version returned bool(arg)
        for anything unrecognised, so "maybe" became True offline and raised under the
        real helper — a fallback that disagrees with the thing it stands in for makes
        any test using it prove the wrong thing.
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


def _as_name_list(value, option_name: str) -> List[str]:
    """
    Normalise a task option that names one or more records into a list.

    ⚠ The comma split is the whole point. `cci task run ... -o developer_names "A,B,C"`
    hands this a single string; treating it as one name silently operates on a table
    called "A,B,C" — which does not exist — while reporting "1 decision table(s)".
    That is what shipped before 2026-07-27, so a multi-table refresh from the CLI never
    worked. YAML callers still pass a real list and are unaffected.
    """
    if isinstance(value, str):
        names = [part.strip() for part in value.split(",")]
    elif isinstance(value, list):
        names = [str(part).strip() for part in value]
    else:
        raise TaskOptionsError(
            f"{option_name} must be a string or list of strings, got {type(value).__name__}"
        )

    names = [name for name in names if name]
    if not names:
        raise TaskOptionsError(f"{option_name} was provided but contained no usable names.")
    return names


class ManageDecisionTables(BaseTask):
    """
    Comprehensive Decision Table management task.
    
    Supports:
    - Querying decision tables (by status, developer name, etc.)
    - Refreshing decision tables (full or incremental)
    - Listing decision tables with metadata
    """

    # Every operation here needs an org. Without this, BaseTask.salesforce_task defaults
    # to False, the CLI builds no --org option, and the task silently runs against the
    # CCI DEFAULT org instead of the one asked for (see issue #320 for the repo-wide
    # sweep — this task was one of the 102).
    salesforce_task = True

    def _update_credentials(self):
        """
        Refresh the OAuth token before the task runs.

        ⚠ `salesforce_task = True` buys the `--org` option and the missing-org guard —
        it does NOT bring a token refresh. Only `BaseSalesforceTask` overrides
        `BaseTask._update_credentials`, which is a bare `pass`, and this task hits the
        REST API directly, so per `cci-orchestration/custom-task-authoring.md` it wants
        the refresh.

        ⚠ Scope the risk honestly. The stale-token failure this guards against needs a
        plain `OrgConfig` — the `cci org connect` shape, where the stored token is used
        as-is. **This project does not have that shape**: the sf CLI manages auth, so
        every org is `ScratchOrgConfig` or `SfdxOrgConfig`, both of which resolve
        `access_token` through `sfdx_info` and are always fresh. So the override is
        correctness insurance for the class, not a fix for an incidence anyone here has
        met — do not cite it as one.
        """
        # save_if_changed, matching BaseSalesforceTask. refresh_oauth_token also
        # reloads user and org info; without the wrapper that work is discarded at
        # process exit and the keychain-updated log line never appears.
        #
        # ⚠ Safe under this project's auth model, which is why there is no
        # connected-app handling here: CCI wraps the sf CLI and leverages its auth.
        # Every org is a ScratchOrgConfig or SfdxOrgConfig, and BOTH override refresh_oauth_token to
        # shell `sf org display` rather than run an OAuth flow — no connected app is
        # ever involved. Verified against the keychain 2026-07-27: zero plain OrgConfig.
        # So this call costs a cached `sf org display` and cannot raise
        # ServiceNotConfigured. It is kept because the flag genuinely does not bring a
        # refresh (see above) and the class should not depend on the caller's org type.
        with self.org_config.save_if_changed():
            self.org_config.refresh_oauth_token(self.project_config.keychain)

    def _pinned_salesforce_client(self):
        """
        A Salesforce client on the PROJECT's API version, not the org's newest.

        `org_config.salesforce_client` builds itself with `latest_api_version`, which
        GETs /services/data and takes the last entry — so it drifts upward the moment an
        org is upgraded ahead of the project.

        ⚠ Use this for EVERY call site in this class, not just the refresh. An earlier
        version pinned only the refresh, which left the task querying DecisionTable on
        the org's newest version and — worse — performing its only WRITE
        (`sf.DecisionTable.update`, the activate/deactivate operations) there too. Writes
        are exactly where an unannounced version bump is most likely to change validation
        or required-field behaviour. `_sf` below is the single client all three share.

        The instance normalisation is character-for-character what CCI's own
        `OrgConfig.salesforce_client` does, so My Domain / sandbox / enhanced-domain
        hostnames behave exactly as they do under the unpinned client.
        """
        api_version = self.project_config.project__package__api_version
        if not api_version or Salesforce is None:
            # ⚠ Say so. A fix that silently degrades is the "stops the damage but does
            # not propagate the signal" shape REVIEW.md calls out. Unreachable in this
            # repo today (cumulusci.yml pins api_version: "67.0", a truthy string), which
            # is precisely why it would go unnoticed if it ever became reachable.
            self.logger.warning(
                "No project api_version pin available; falling back to the org's latest "
                "API version. Decision-table calls are NOT pinned to the project version."
            )
            return self.org_config.salesforce_client
        return Salesforce(
            instance=self.org_config.instance_url.replace("https://", ""),
            session_id=self.org_config.access_token,
            version=api_version,
        )

    @property
    def _sf(self):
        """The pinned client, built once per task run and reused by every operation."""
        if getattr(self, "_sf_client", None) is None:
            self._sf_client = self._pinned_salesforce_client()
        return self._sf_client

    task_options = {
        "operation": {
            "description": "Operation to perform: 'list', 'refresh', 'query', 'activate', 'deactivate', 'validate_lists'",
            "required": True
        },
        "developer_names": {
            "description": "List of Decision Table DeveloperNames to operate on. If not provided, queries all active tables.",
            "required": False
        },
        "status": {
            "description": "Filter by Status ('Active', 'Inactive', or None for all). Default: 'Active'",
            "required": False
        },
        "is_incremental": {
            "description": "For refresh operation: True for incremental refresh, False for full refresh. Default: False",
            "required": False
        },
        "sort_by": {
            "description": "Field to sort by (e.g., 'LastSyncDate', 'DeveloperName'). Default: 'LastSyncDate'",
            "required": False
        },
        "sort_order": {
            "description": "Sort order: 'Asc' or 'Desc'. Default: 'Desc'",
            "required": False
        },
        "limit": {
            "description": "Maximum number of decision tables to return. Default: None (no limit)",
            "required": False
        },
        "list_anchors": {
            "description": "For validate_lists: list of config anchor names (e.g. dt_rating_decision_tables). If omitted, all dt_*_decision_tables from project custom are used.",
            "required": False
        }
    }
    
    def _run_task(self):
        """Execute the task based on the operation specified."""
        operation = self.options.get("operation", "").lower()
        
        if operation == "list":
            self._list_decision_tables()
        elif operation == "query":
            self._query_decision_tables()
        elif operation == "refresh":
            self._refresh_decision_tables()
        elif operation == "activate":
            self._set_decision_tables_status("Active")
        elif operation == "deactivate":
            self._set_decision_tables_status("Inactive")
        elif operation == "validate_lists":
            self._validate_lists()
        else:
            raise TaskOptionsError(
                f"Unknown operation: {operation}. Supported operations: "
                "'list', 'query', 'refresh', 'activate', 'deactivate', 'validate_lists'"
            )
    
    def _list_decision_tables(self):
        """List decision tables with their metadata (similar to the flow's query)."""
        decision_tables = self._query_decision_tables()
        
        if not decision_tables:
            self.logger.info("No decision tables found matching the criteria.")
            return
        
        self.logger.info(f"Found {len(decision_tables)} decision table(s):")
        self.logger.info("")
        self.logger.info(f"{'DeveloperName':<50} {'Status':<10} {'UsageType':<28} {'LastSyncDate':<25} {'SetupName':<50}")
        self.logger.info("-" * 165)
        
        for dt in decision_tables:
            dev_name = dt.get('DeveloperName', 'N/A')
            status = dt.get('Status', 'N/A')
            usage_type = dt.get('UsageType', '') or ''
            last_sync = dt.get('LastSyncDate', 'N/A')
            setup_name = dt.get('SetupName', 'N/A')
            
            # Format LastSyncDate if it exists
            if last_sync and last_sync != 'N/A':
                try:
                    # Parse ISO format datetime
                    dt_obj = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    last_sync = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            self.logger.info(f"{dev_name:<50} {status:<10} {usage_type:<28} {last_sync:<25} {setup_name:<50}")
        
        # Return results as JSON for programmatic use
        return decision_tables
    
    def _query_decision_tables(self) -> List[Dict]:
        """
        Query decision tables from Salesforce using Tooling API.
        
        Returns a list of decision table records with their metadata.
        """
        try:
            # Use Salesforce client (works for Tooling API objects like DecisionTable)
            if not hasattr(self, 'org_config') or not self.org_config:
                raise TaskOptionsError("No org_config available")
            
            # Get Salesforce connection - DecisionTable is a Tooling API object
            # Try using salesforce_client first (works for some Tooling API objects)
            sf = self._sf
            
            # Build SOQL query
            soql = self._build_soql_query()
            
            self.logger.debug(f"Executing SOQL query: {soql}")
            
            # Query using Salesforce connection
            query_result = sf.query(soql)
            
            if not query_result or 'records' not in query_result:
                self.logger.warning("No records returned from query.")
                return []
            
            decision_tables = query_result['records']
            
            # Remove attributes field if present
            for dt in decision_tables:
                dt.pop('attributes', None)
            
            self.logger.info(f"Query returned {len(decision_tables)} decision table(s).")
            
            return decision_tables
            
        except Exception as e:
            self.logger.error(f"Error querying decision tables: {e}")
            raise TaskOptionsError(f"Failed to query decision tables: {e}")
    
    def _build_soql_query(self) -> str:
        """Build SOQL query based on task options."""
        # Base fields to query (matching the flow's query)
        fields = [
            "Id",
            "DeveloperName",
            "Status",
            "LastSyncDate",
            "SetupName",
            "UsageType"
        ]
        
        # Build WHERE clause
        where_clauses = []
        
        # Filter by developer names if provided
        developer_names = self.options.get("developer_names")
        if developer_names:
            developer_names = _as_name_list(developer_names, "developer_names")

            # Escape single quotes in developer names
            escaped_names = [name.replace("'", "\\'") for name in developer_names]
            names_str = "', '".join(escaped_names)
            where_clauses.append(f"DeveloperName IN ('{names_str}')")
        
        # Filter by status
        status = self.options.get("status", "Active")
        if status:
            where_clauses.append(f"Status = '{status}'")
        
        # Build query
        soql = f"SELECT {', '.join(fields)} FROM DecisionTable"
        
        if where_clauses:
            soql += " WHERE " + " AND ".join(where_clauses)
        
        # Add sorting
        sort_by = self.options.get("sort_by", "LastSyncDate")
        sort_order = self.options.get("sort_order", "Desc")
        soql += f" ORDER BY {sort_by} {sort_order}"
        
        # Add limit if specified
        limit = self.options.get("limit")
        if limit:
            soql += f" LIMIT {limit}"
        
        return soql
    
    def _refresh_decision_tables(self):
        """
        Refresh decision tables using the refreshDecisionTable action.
        
        Supports both full and incremental refresh.
        """
        # Get decision tables to refresh
        developer_names = self.options.get("developer_names")
        
        if not developer_names:
            # Query all active decision tables if none specified
            self.logger.info("No developer_names specified, querying all active decision tables...")
            decision_tables = self._query_decision_tables()
            developer_names = [dt.get('DeveloperName') for dt in decision_tables if dt.get('DeveloperName')]
            
            if not developer_names:
                self.logger.warning("No active decision tables found to refresh.")
                return
        else:
            developer_names = _as_name_list(developer_names, "developer_names")

        # ⚠ process_bool_arg, not the raw option. CCI hands CLI options through as
        # STRINGS, so `-o is_incremental false` arrives as "false" — truthy — and would
        # silently select an incremental refresh while logging "full". YAML callers pass
        # a real bool and are unaffected.
        is_incremental = process_bool_arg(self.options.get("is_incremental") or False)
        refresh_type = "incremental" if is_incremental else "full"
        
        self.logger.info(f"Refreshing {len(developer_names)} decision table(s) ({refresh_type} refresh)...")
        
        # Use Salesforce REST API to call the refreshDecisionTable action
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")

        # ⚠ salesforce_client, NOT org_config.get_connection(). OrgConfig inherits
        # BaseConfig.__getattr__, which returns None for any key it does not know
        # instead of raising — so `get_connection` resolved to None and calling it
        # died with "'NoneType' object is not callable". This refresh path therefore
        # never ran successfully from the day it was written; the sibling operations
        # all use salesforce_client, which is why only refresh was affected.
        #
        # ⚠ salesforce_client pins itself to org_config.latest_api_version — the org's
        # NEWEST version, not this project's. Rebuild it on the project's pinned version
        # so both decision-table refresh paths call the same action on the same API, and
        # so the call does not drift when an org upgrades ahead of the project.
        sf = self._sf

        success_count = 0
        fail_count = 0

        for developer_name in developer_names:
            try:
                result = self._refresh_single_decision_table(sf, developer_name, is_incremental)

                # ⚠ isSuccess means the action was ACCEPTED, not that the table was
                # rebuilt. refreshDecisionTable is asynchronous: it returns Status
                # 'Queued' and the work completes later. Reporting "successfully
                # refreshed" off isSuccess alone is the stale-but-claims-otherwise
                # failure this task exists to prevent, so the log says exactly what was
                # established — queued.
                #
                # ⚠ Fail CLOSED on the status. Salesforce documents the output as Queued
                # or Failed, so only an explicit Queued is evidence of acceptance; a
                # missing, empty or unrecognised Status (including the 'Unknown'
                # fallback below) is not evidence and is counted as a failure. An
                # earlier version accepted "anything but Failed", which let a malformed
                # or version-drifted response claim a queue that never happened.
                #
                # ⚠ Points at check_decision_table_freshness ONLY. Do not add
                # DecisionTable.RefreshStatus here — pricing-wiring/SKILL.md rules it out
                # as a detector, because it lives on a table record and so says nothing
                # for the failure that actually occurs (an unresolvable name leaves no
                # record to stamp). LastSyncDate, which the freshness check uses, is the
                # one signal that holds for every shape.
                action_status = (result.get('outputValues') or {}).get('Status') or 'Unknown'
                if result.get('isSuccess') and action_status.lower() == 'queued':
                    success_count += 1
                    self.logger.info(
                        f"Refresh queued for '{developer_name}' - Status: {action_status}. "
                        "Completion is asynchronous; verify with check_decision_table_freshness."
                    )
                elif result.get('isSuccess'):
                    fail_count += 1
                    self.logger.error(
                        f"❌ Refresh of '{developer_name}' was accepted but reported "
                        f"Status: {action_status} (expected 'Queued'); treating as not queued."
                    )
                else:
                    fail_count += 1
                    errors = result.get('errors', [])
                    error_messages = [e.get('message', str(e)) for e in errors if isinstance(e, dict)]
                    error_messages.extend([str(e) for e in errors if not isinstance(e, dict)])
                    error_msg = "; ".join(error_messages) if error_messages else "Unknown error"
                    self.logger.error(f"❌ Failed to refresh '{developer_name}': {error_msg}")
                    
            except Exception as e:
                fail_count += 1
                self.logger.error(f"❌ Exception refreshing '{developer_name}': {e}")
        
        # Summary
        self.logger.info("")
        self.logger.info(
            f"Refresh Summary: {success_count} queued, {fail_count} not queued"
        )
        
        if fail_count > 0:
            # "not queued", not "failed to refresh" — this task never observes a refresh
            # completing, so it cannot claim one failed. It covers both a rejected request
            # and one accepted with a Status other than Queued.
            raise TaskOptionsError(
                f"Failed to queue a refresh for {fail_count} decision table(s). "
                "Check logs for details."
            )

    def _validate_lists(self):
        """
        Validate decision table list anchors from project config against the org.
        - Lists all org DTs grouped by UsageType.
        - Reports DTs in org that are not in any configured list.
        - Reports list entries that are not in the org (invalid/missing).
        """
        # Query all active decision tables (ignore developer_names so we get full org list)
        saved_dev_names = self.options.get("developer_names")
        try:
            self.options["developer_names"] = None
            self.logger.info("Querying all active decision tables from org...")
            decision_tables = self._query_decision_tables()
        finally:
            if saved_dev_names is not None:
                self.options["developer_names"] = saved_dev_names
            elif "developer_names" in self.options:
                del self.options["developer_names"]
        if not decision_tables:
            self.logger.warning("No active decision tables found in org.")
            return

        org_by_name = {dt["DeveloperName"]: dt for dt in decision_tables}
        org_names = set(org_by_name.keys())

        # Resolve which list anchors to validate
        list_anchors = self.options.get("list_anchors")
        if list_anchors:
            list_anchors = _as_name_list(list_anchors, "list_anchors")
        else:
            list_anchors = self._get_decision_table_list_anchors()

        # Build: anchor -> list of developer names; and set of all names in any list
        anchor_to_names: Dict[str, List[str]] = {}
        all_listed_names: Set[str] = set()
        custom = self._get_project_custom_config()
        for anchor in list_anchors:
            names = custom.get(anchor)
            if names is None:
                self.logger.warning("List anchor '%s' not found in project custom config.", anchor)
                continue
            if not isinstance(names, list):
                self.logger.warning("List anchor '%s' is not a list, skipping.", anchor)
                continue
            anchor_to_names[anchor] = names
            all_listed_names.update(names)

        # --- Report: DTs in org grouped by UsageType ---
        by_usage: Dict[str, List[Dict]] = {}
        for dt in decision_tables:
            ut = dt.get("UsageType") or "(blank)"
            by_usage.setdefault(ut, []).append(dt)
        self.logger.info("")
        self.logger.info("=== Decision tables in org by UsageType ===")
        for ut in sorted(by_usage.keys()):
            dts = by_usage[ut]
            self.logger.info("  %s (%d): %s", ut, len(dts), ", ".join(d["DeveloperName"] for d in sorted(dts, key=lambda d: d["DeveloperName"])))
        self.logger.info("")

        # --- Report: In org but not in any list ---
        not_in_any_list = org_names - all_listed_names
        if not_in_any_list:
            self.logger.info("=== In org but not in any configured list ===")
            by_ut = {}
            for name in not_in_any_list:
                rec = org_by_name.get(name, {})
                ut = rec.get("UsageType") or "(blank)"
                by_ut.setdefault(ut, []).append(name)
            for ut in sorted(by_ut.keys()):
                names = sorted(by_ut[ut])
                self.logger.info("  %s: %s", ut, ", ".join(names))
            self.logger.info("  Total: %d", len(not_in_any_list))
        else:
            self.logger.info("=== In org but not in any list: (none) ===")
        self.logger.info("")

        # --- Report: In lists but not in org (invalid entries) ---
        not_in_org = all_listed_names - org_names
        if not_in_org:
            self.logger.info("=== In configured lists but not in org (invalid/missing) ===")
            for anchor in list_anchors:
                names = anchor_to_names.get(anchor, [])
                missing = [n for n in names if n not in org_names]
                if missing:
                    self.logger.info("  %s: %s", anchor, ", ".join(sorted(missing)))
            self.logger.info("  Total: %d", len(not_in_org))
        else:
            self.logger.info("=== In lists but not in org: (none) ===")
        self.logger.info("")
        self.logger.info("Validate lists complete. Org total: %d, Listed total (unique): %d.", len(org_names), len(all_listed_names))

    def _get_project_custom_config(self) -> Dict:
        """Return project custom config dict (e.g. from cumulusci.yml project.custom)."""
        if not getattr(self, "project_config", None):
            return {}
        config = getattr(self.project_config, "config", None) or {}
        project = config.get("project") or {}
        return project.get("custom") or {}

    def _get_decision_table_list_anchors(self) -> List[str]:
        """Return list of decision table anchor names from project custom (dt_*_decision_tables)."""
        custom = self._get_project_custom_config()
        anchors = [k for k in custom.keys() if k.startswith("dt_") and k.endswith("_decision_tables")]
        return sorted(anchors)
    
    def _refresh_single_decision_table(self, sf, developer_name: str, is_incremental: bool) -> Dict:
        """
        Refresh a single decision table using the refreshDecisionTable action.

        Uses the Salesforce REST API actions endpoint.
        """
        # ⚠ Relative path, deliberately. simple_salesforce's restful() joins this onto
        # base_url, which already ends in /services/data/v<version>/ — passing an
        # absolute path produced a doubled prefix and a 404.
        endpoint = "actions/standard/refreshDecisionTable"

        payload = {
            "inputs": [
                {
                    "decisionTableApiName": developer_name,
                    "isIncremental": is_incremental
                }
            ]
        }

        result = sf.restful(endpoint, method='POST', json=payload)
        
        # Handle response format
        if isinstance(result, list):
            if len(result) > 0:
                return result[0]
            else:
                raise TaskOptionsError(f"Empty response for decision table '{developer_name}'")
        elif isinstance(result, dict):
            return result
        else:
            raise TaskOptionsError(f"Unexpected response format for decision table '{developer_name}': {type(result)}")

    def _set_decision_tables_status(self, target_status: str):
        """Set status for specified DecisionTable records."""
        developer_names = self.options.get("developer_names")
        if not developer_names:
            raise TaskOptionsError(
                "developer_names is required for activate/deactivate operations"
            )

        developer_names = _as_name_list(developer_names, "developer_names")

        escaped_names = [name.replace("'", "\\'") for name in developer_names]
        names_str = "', '".join(escaped_names)
        soql = (
            "SELECT Id, DeveloperName, Status FROM DecisionTable "
            f"WHERE DeveloperName IN ('{names_str}')"
        )
        sf = self._sf
        records = sf.query(soql).get("records", [])
        if not records:
            raise TaskOptionsError(
                f"No DecisionTable records found for developer_names: {', '.join(developer_names)}"
            )

        found_names = {rec.get("DeveloperName") for rec in records if rec.get("DeveloperName")}
        missing_names = [name for name in developer_names if name not in found_names]
        if missing_names:
            self.logger.warning(
                "DecisionTable records not found for: %s", ", ".join(missing_names)
            )

        updates = 0
        skips = 0
        for rec in records:
            record_id = rec.get("Id")
            dev_name = rec.get("DeveloperName")
            current_status = rec.get("Status")
            if current_status == target_status:
                skips += 1
                self.logger.info(
                    "DecisionTable '%s' already in status '%s'.", dev_name, target_status
                )
                continue

            sf.DecisionTable.update(record_id, {"Status": target_status})
            updates += 1
            self.logger.info(
                "Updated DecisionTable '%s' status: %s -> %s",
                dev_name,
                current_status,
                target_status,
            )

        self.logger.info(
            "DecisionTable status update complete. Updated: %s, unchanged: %s",
            updates,
            skips,
        )
