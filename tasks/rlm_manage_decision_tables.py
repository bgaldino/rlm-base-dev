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

That screen flow is gone: do not go looking for it as a reference. In the org the
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
        """Offline fallback for cumulusci.core.utils.process_bool_arg.
        Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Importing without CumulusCI."""
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


def _anchor_gates(config: Dict, names: List[str]) -> List[Dict]:
    """
    Every flow step that refreshes or activates the decision-table list `names`.

    The `dt_*_decision_tables` anchors carry no flag of their own: the flag is the `when:` on
    the flow step that runs the task the anchor is wired into. Reading it from the loaded
    config, rather than keeping a second anchor-to-flag map, means it cannot drift from the
    flows. YAML aliases load as equal lists, so a list matches on the same names in any order.
    A step's own list option overrides its task's. Every flow counts, not only the build:
    an unconditional step anywhere means some run expects the tables. A parent `flow:` step's
    `when:` is not read, as CumulusCI's flow runner does not read it either.

    Returns [{"flow", "step", "task", "when"}]; "when" is None for an unconditional step.
    """
    wanted = set(names)

    def list_in(options):
        """The decision-table list an options dict carries, or None."""
        for key in ("developerNames", "developer_names"):
            if isinstance(options.get(key), list):
                return options[key]
        return None

    def matches(options):
        value = list_in(options)
        return value is not None and set(value) == wanted

    tasks = config.get("tasks") or {}
    using = {name for name, task in tasks.items() if matches((task or {}).get("options") or {})}
    gates = []
    for flow_name, flow in (config.get("flows") or {}).items():
        for step_num, step in ((flow or {}).get("steps") or {}).items():
            if not isinstance(step, dict) or not step.get("task"):
                continue
            step_options = step.get("options") or {}
            if list_in(step_options) is not None:
                hit = matches(step_options)
            else:
                hit = step["task"] in using
            if hit:
                gates.append({
                    "flow": flow_name,
                    "step": step_num,
                    "task": step["task"],
                    "when": step.get("when"),
                })
    return gates


def _evaluate_when(when: Optional[str], project_config, org_config) -> Optional[bool]:
    """
    A flow step's `when:` as CumulusCI's flow runner evaluates it. True for an unconditional
    step; None only when CumulusCI is not installed. An expression that fails to evaluate
    raises, as it fails the flow itself.
    """
    if when is None:
        return True
    try:
        from cumulusci.core.flowrunner import jinja2_env
    except ImportError:
        return None
    return bool(jinja2_env.compile_expression(when)(project_config=project_config, org_config=org_config))


EXPECTED = "expected"
UNEXPECTED = "unexpected"
UNKNOWN = "unknown"


def _list_verdict(gates: List[Dict], verdicts: List[Optional[bool]]) -> tuple:
    """
    Whether a list's missing names are explained by its flags: (kind, reason).

    `verdicts` holds _evaluate_when's value for each gate, in order. UNEXPECTED when any step
    using the list runs, or when no flow uses it at all; EXPECTED only when every step is
    off; otherwise UNKNOWN, which strict mode treats as unexpected.
    """
    if not gates:
        return UNEXPECTED, "no flow uses this list, so no flag explains the absence"
    if any(v is True for v in verdicts):
        return UNEXPECTED, "a step that uses this list runs for this project's flags"
    if all(v is False for v in verdicts):
        return EXPECTED, "every step that uses this list is off for this project's flags"
    return UNKNOWN, "a step condition could not be evaluated here (CumulusCI not installed)"


def _soql_quote(value: str) -> str:
    """A SOQL string literal: backslash first, then the quote."""
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _as_name_list(value, option_name: str) -> List[str]:
    """
    Normalise a task option that names one or more records into a list, splitting a
    comma-separated CLI string. Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → CLI option parsing.
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


def queued_guidance(is_incremental):
    """What to check once a queued refresh completes. Kept identical to the copy in
    rlm_refresh_decision_table.py; tests/test_decision_table_tasks.py holds them together."""
    # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Queued is not refreshed.
    requested = "an incremental" if is_incremental else "a full"
    return (
        f"Completion is asynchronous, and {requested} request does not fix the type that runs: "
        "a full refresh advances LastSyncDate, an incremental one only LastIncrementalSyncDate. "
        "AFTER the job completes, judge it by the later of the two."
    )


class ManageDecisionTables(BaseTask):
    """
    Comprehensive Decision Table management task.
    
    Supports:
    - Querying decision tables (by status, developer name, etc.)
    - Refreshing decision tables (full or incremental)
    - Listing decision tables with metadata
    """

    # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Auth and the token refresh.
    salesforce_task = True

    def _update_credentials(self):
        """Refresh the OAuth token before the task runs."""
        # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Auth and the token refresh.
        with self.org_config.save_if_changed():
            self.org_config.refresh_oauth_token(self.project_config.keychain)

    def _pinned_salesforce_client(self):
        """
        A Salesforce client on the PROJECT's API version, not the org's newest. Called
        only by `_sf`. Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → The API-version pin.
        """
        api_version = self.project_config.project__package__api_version
        if not api_version or Salesforce is None:
            # Why the warning: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → The API-version pin.
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
        """
        The pinned client, built once per task run. Every operation, including the
        activate/deactivate write, must use it. Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → The API-version pin.
        """
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
        },
        "strict": {
            "description": "For validate_lists: fail when a listed table is missing or inactive and its flags don't explain it (a step using its list runs, no flow uses it, or a condition can't be evaluated). Default: False (report only).",
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
                except Exception:
                    # Cosmetic only — an unparseable stamp is printed raw rather than
                    # failing a listing. `except Exception:` not a bare `except:`, which
                    # would also swallow KeyboardInterrupt.
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

            names_str = ", ".join(_soql_quote(name) for name in developer_names)
            where_clauses.append(f"DeveloperName IN ({names_str})")
        
        # Filter by status
        status = self.options.get("status", "Active")
        if status:
            where_clauses.append(f"Status = {_soql_quote(status)}")
        
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

        # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → CLI option parsing.
        is_incremental = process_bool_arg(self.options.get("is_incremental") or False)
        # Why "full requested": .cursor/skills/decision-tables/lifecycle-and-refresh.md → Release 264 chooses the refresh type.
        refresh_type = "incremental" if is_incremental else "full requested; the platform may run incremental"
        
        self.logger.info(f"Refreshing {len(developer_names)} decision table(s) ({refresh_type})...")
        
        # Use Salesforce REST API to call the refreshDecisionTable action
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")

        sf = self._sf  # pinned client

        success_count = 0
        fail_count = 0

        for developer_name in developer_names:
            try:
                result = self._refresh_single_decision_table(sf, developer_name, is_incremental)

                # Only an explicit Queued counts; kept identical to refresh_dt_*.
                # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Queued is not refreshed.
                action_status = ((result.get('outputValues') or {}).get('Status') or '').strip() or 'Unknown'
                if result.get('isSuccess') and action_status.lower() == 'queued':
                    success_count += 1
                    self.logger.info(
                        f"Refresh queued for '{developer_name}' - Status: {action_status}. "
                        + queued_guidance(is_incremental)
                    )
                elif result.get('isSuccess'):
                    fail_count += 1
                    self.logger.error(
                        f"❌ Refresh of '{developer_name}' was accepted but reported "
                        f"Status: {action_status} (expected 'Queued'); treating as not queued. "
                        "If this is a new platform status rather than a failure, confirm with "
                        "check_decision_table_freshness once any queued job completes, then "
                        "extend the accepted set."
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
            # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Queued is not refreshed.
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
            # Carry on: with nothing active, every list in use is a finding, and strict must see it.
            self.logger.warning("No active decision tables found in org.")
            decision_tables = []

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

        # --- Report: In lists but not in org, attributed to the flag that gates the list ---
        not_in_org = all_listed_names - org_names
        unexpected: Set[str] = set()
        if not_in_org:
            inactive = self._statuses_of(sorted(not_in_org))
            self.logger.info("=== In configured lists but not active in org ===")
            config = getattr(self.project_config, "config", None) or {}
            for anchor in list_anchors:
                names = anchor_to_names.get(anchor, [])
                missing = sorted(n for n in names if n not in org_names)
                if not missing:
                    continue
                gates = _anchor_gates(config, names)
                try:
                    verdicts = [_evaluate_when(g["when"], self.project_config, self.org_config) for g in gates]
                    kind, reason = _list_verdict(gates, verdicts)
                except Exception as e:  # a when: that cannot evaluate fails the flow, so it fails here
                    kind, reason = UNKNOWN, f"a step condition failed to evaluate: {e}"
                if kind != EXPECTED:
                    unexpected.update(missing)
                runs = " · ".join(
                    f"{g['flow']} step {g['step']} ({g['task']}"
                    + (f", when: {g['when']}" if g["when"] else ", unconditional") + ")"
                    for g in gates
                ) or "no flow step"
                self.logger.info("  %s — %s: %s", anchor, kind.upper() if kind != EXPECTED else kind, reason)
                self.logger.info("    used by: %s", runs)
                for name in missing:
                    status = inactive.get(name)
                    self.logger.info("    %s%s", name, f" (in org, {status})" if status else " (not in org)")
            self.logger.info("  Total: %d (%d not explained by a flag)", len(not_in_org), len(unexpected))
            self.logger.info(
                "  A name in several lists is judged once per list. Flags are read from this "
                "project's config, which may differ from the flags the org was built with (a "
                "runtime -o override, for example)."
            )
        else:
            self.logger.info("=== In lists but not in org: (none) ===")
        self.logger.info("")
        self.logger.info("Validate lists complete. Org total: %d, Listed total (unique): %d.", len(org_names), len(all_listed_names))
        if unexpected and process_bool_arg(self.options.get("strict") or False):
            raise TaskOptionsError(
                "Decision tables missing or inactive, not explained by a flag: " + ", ".join(sorted(unexpected))
            )

    def _statuses_of(self, names: List[str]) -> Dict[str, str]:
        """{DeveloperName: Status} for those of `names` that exist in the org, in any status."""
        if not names:
            return {}
        quoted = ", ".join(_soql_quote(n) for n in names)
        result = self._sf.query(f"SELECT DeveloperName, Status FROM DecisionTable WHERE DeveloperName IN ({quoted})")
        return {r["DeveloperName"]: r["Status"] for r in (result or {}).get("records") or []}

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
        # Why: .cursor/skills/decision-tables/lifecycle-and-refresh.md → The CCI refresh tasks → Request shape.
        endpoint = "actions/standard/refreshDecisionTable"

        payload = {
            "inputs": [
                {
                    "decisionTableApiName": developer_name,
                    # Not isIncremental.
                    "isDecisionTableIncremental": is_incremental
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

        names_str = ", ".join(_soql_quote(name) for name in developer_names)
        soql = (
            "SELECT Id, DeveloperName, Status FROM DecisionTable "
            f"WHERE DeveloperName IN ({names_str})"
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
