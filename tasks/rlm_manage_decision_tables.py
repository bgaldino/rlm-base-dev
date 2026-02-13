"""
Custom CumulusCI task for comprehensive Decision Table management.

This task provides functionality to:
- Query/list decision tables (similar to RC_UpdateDecisionTables flow)
- Refresh decision tables (full or incremental)
- Support other operations (activate, deactivate, etc.)

Based on the RC_UpdateDecisionTables flow which:
- Queries DecisionTable records with Status = 'Active'
- Uses refreshDecisionTable action
- Supports incremental refresh
"""
import json
from typing import List, Dict, Optional, Set
from datetime import datetime

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ManageDecisionTables(BaseTask):
    """
    Comprehensive Decision Table management task.
    
    Supports:
    - Querying decision tables (by status, developer name, etc.)
    - Refreshing decision tables (full or incremental)
    - Listing decision tables with metadata
    """
    
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
            sf = self.org_config.salesforce_client
            
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
            if isinstance(developer_names, str):
                developer_names = [developer_names]
            elif not isinstance(developer_names, list):
                raise TaskOptionsError("developer_names must be a string or list of strings")
            
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
            # Convert to list if string
            if isinstance(developer_names, str):
                developer_names = [developer_names]
            elif not isinstance(developer_names, list):
                raise TaskOptionsError("developer_names must be a string or list of strings")
        
        is_incremental = self.options.get("is_incremental", False)
        refresh_type = "incremental" if is_incremental else "full"
        
        self.logger.info(f"Refreshing {len(developer_names)} decision table(s) ({refresh_type} refresh)...")
        
        # Use Salesforce REST API to call the refreshDecisionTable action
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")
        
        # Get connection and API version
        conn = self.org_config.get_connection()
        api_version = self.org_config.api_version
        
        success_count = 0
        fail_count = 0
        
        for developer_name in developer_names:
            try:
                result = self._refresh_single_decision_table(conn, api_version, developer_name, is_incremental)
                
                if result.get('isSuccess'):
                    success_count += 1
                    status = result.get('outputValues', {}).get('Status', 'Unknown')
                    self.logger.info(f"✅ Successfully refreshed '{developer_name}' - Status: {status}")
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
        self.logger.info(f"Refresh Summary: {success_count} succeeded, {fail_count} failed")
        
        if fail_count > 0:
            raise TaskOptionsError(f"Failed to refresh {fail_count} decision table(s). Check logs for details.")

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
            if isinstance(list_anchors, str):
                list_anchors = [list_anchors]
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
    
    def _refresh_single_decision_table(self, conn, api_version: str, developer_name: str, is_incremental: bool) -> Dict:
        """
        Refresh a single decision table using the refreshDecisionTable action.
        
        Uses the Salesforce REST API actions endpoint.
        """
        endpoint = f"/services/data/v{api_version}/actions/standard/refreshDecisionTable"
        
        payload = {
            "inputs": [
                {
                    "decisionTableApiName": developer_name,
                    "isIncremental": is_incremental
                }
            ]
        }
        
        # Use the connection's restful method
        result = conn.restful(endpoint, method='POST', json=payload)
        
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

        if isinstance(developer_names, str):
            developer_names = [developer_names]
        elif not isinstance(developer_names, list):
            raise TaskOptionsError("developer_names must be a string or list of strings")

        escaped_names = [name.replace("'", "\\'") for name in developer_names]
        names_str = "', '".join(escaped_names)
        soql = (
            "SELECT Id, DeveloperName, Status FROM DecisionTable "
            f"WHERE DeveloperName IN ('{names_str}')"
        )
        sf = self.org_config.salesforce_client
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
