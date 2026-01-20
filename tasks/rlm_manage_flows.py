"""
Custom CumulusCI task for comprehensive Flow management.

This task provides functionality to:
- Query/list flows (by type, status, name, etc.)
- Activate/deactivate flows
- Manage flow versions
- Filter by processType, status, and other metadata

Flows have:
- DeveloperName, Label, Status (Active/Inactive/Draft)
- ProcessType (AutoLaunchedFlow, ScreenFlow, etc.)
- ApiVersion
- Description
"""
from typing import List, Dict, Optional
from datetime import datetime

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ManageFlows(BaseTask):
    """
    Comprehensive Flow management task.
    
    Supports:
    - Querying flows (by type, status, name, etc.)
    - Listing flows with metadata
    - Activating/deactivating flows
    - Managing flow versions
    """
    
    task_options = {
        "operation": {
            "description": "Operation to perform: 'list', 'query', 'activate', 'deactivate'",
            "required": True
        },
        "developer_names": {
            "description": "List of Flow DeveloperNames to operate on. If not provided, queries all flows.",
            "required": False
        },
        "status": {
            "description": "Filter by Status ('Active', 'Inactive', 'Draft', or None for all). Default: None",
            "required": False
        },
        "process_type": {
            "description": "Filter by ProcessType (e.g., 'AutoLaunchedFlow', 'ScreenFlow', 'Workflow', etc.). Default: None",
            "required": False
        },
        "sort_by": {
            "description": "Field to sort by (e.g., 'LastModifiedDate', 'DeveloperName', 'Label'). Default: 'LastModifiedDate'",
            "required": False
        },
        "sort_order": {
            "description": "Sort order: 'Asc' or 'Desc'. Default: 'Desc'",
            "required": False
        },
        "limit": {
            "description": "Maximum number of flows to return. Default: None (no limit)",
            "required": False
        }
    }
    
    def _run_task(self):
        """Execute the task based on the operation specified."""
        operation = self.options.get("operation", "").lower()
        
        if operation == "list":
            self._list_flows()
        elif operation == "query":
            self._query_flows()
        elif operation == "activate":
            self._activate_flows()
        elif operation == "deactivate":
            self._deactivate_flows()
        else:
            raise TaskOptionsError(f"Unknown operation: {operation}. Supported operations: 'list', 'query', 'activate', 'deactivate'")
    
    def _list_flows(self):
        """List flows with their metadata."""
        flows = self._query_flows()
        
        if not flows:
            self.logger.info("No flows found matching the criteria.")
            return
        
        self.logger.info(f"Found {len(flows)} flow(s):")
        self.logger.info("")
        self.logger.info(f"{'DefinitionId':<50} {'MasterLabel':<50} {'Status':<12} {'ProcessType':<20} {'Version':<10}")
        self.logger.info("-" * 142)
        
        for flow in flows:
            definition_id = flow.get('DefinitionId', 'N/A')
            label = flow.get('MasterLabel', 'N/A')
            status = flow.get('Status', 'N/A')
            process_type = flow.get('ProcessType', 'N/A')
            version = flow.get('VersionNumber', 'N/A')
            
            self.logger.info(f"{definition_id:<50} {label:<50} {status:<12} {process_type:<20} {version:<10}")
        
        return flows
    
    def _query_flows(self) -> List[Dict]:
        """
        Query flows from Salesforce using Tooling API.
        
        Returns a list of flow records with their metadata.
        """
        try:
            if not hasattr(self, 'org_config') or not self.org_config:
                raise TaskOptionsError("No org_config available")
            
            # Use requests library for Tooling API calls (like refresh_decision_table task)
            import requests
            
            # Get access token and instance URL
            access_token = self.org_config.access_token
            instance_url = self.org_config.instance_url
            # Get API version from project config or org config
            api_version = getattr(self.org_config, 'api_version', None) or getattr(self.project_config, 'project__package__api_version', '66.0')
            
            # First, try to describe Flow object to see available fields
            describe_url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/Flow/describe"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            describe_response = requests.get(describe_url, headers=headers)
            if describe_response.ok:
                describe_data = describe_response.json()
                field_names = [f['name'] for f in describe_data.get('fields', [])]
                self.logger.debug(f"Available Flow fields: {', '.join(field_names[:10])}...")
            
            # Build SOQL query
            soql = self._build_soql_query()
            
            self.logger.debug(f"Executing Tooling API SOQL query: {soql}")
            
            # Query using Tooling API endpoint
            url = f"{instance_url}/services/data/v{api_version}/tooling/query"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            params = {"q": soql}
            
            self.logger.debug(f"Query URL: {url}")
            self.logger.debug(f"Query params: {params}")
            
            response = requests.get(url, headers=headers, params=params)
            
            if not response.ok:
                self.logger.error(f"Tooling API query failed: {response.status_code} - {response.text}")
                raise TaskOptionsError(f"Failed to query flows: {response.text}")
            
            query_result = response.json()
            
            if not query_result or 'records' not in query_result:
                self.logger.warning("No records returned from query.")
                return []
            
            flows = query_result['records']
            
            # Remove attributes field if present
            for flow in flows:
                flow.pop('attributes', None)
            
            self.logger.info(f"Query returned {len(flows)} flow(s).")
            
            return flows
            
        except Exception as e:
            self.logger.error(f"Error querying flows: {e}")
            raise TaskOptionsError(f"Failed to query flows: {e}")
    
    def _build_soql_query(self) -> str:
        """Build SOQL query based on task options."""
        # Base fields to query - Flow object fields (from describe)
        # Flow uses: DefinitionId, MasterLabel (not Label), Status, ProcessType, etc.
        fields = [
            "Id",
            "DefinitionId",  # Flow uses DefinitionId, not DeveloperName
            "MasterLabel",  # Flow uses MasterLabel, not Label
            "Status",
            "ProcessType",
            "VersionNumber",  # Flow has VersionNumber, not ApiVersion
            "Description",
            "CreatedDate",  # Flow has CreatedDate, not LastModifiedDate
            "CreatedById"  # Flow has CreatedById, not LastModifiedBy
        ]
        
        # Build WHERE clause
        where_clauses = []
        
        # Filter by developer names if provided (Flow uses DefinitionId)
        developer_names = self.options.get("developer_names")
        if developer_names:
            if isinstance(developer_names, str):
                developer_names = [developer_names]
            elif not isinstance(developer_names, list):
                raise TaskOptionsError("developer_names must be a string or list of strings")
            
            # Escape single quotes in developer names
            escaped_names = [name.replace("'", "\\'") for name in developer_names]
            names_str = "', '".join(escaped_names)
            where_clauses.append(f"DefinitionId IN ('{names_str}')")
        
        # Filter by status
        status = self.options.get("status")
        if status:
            where_clauses.append(f"Status = '{status}'")
        
        # Filter by process type
        process_type = self.options.get("process_type")
        if process_type:
            where_clauses.append(f"ProcessType = '{process_type}'")
        
        # Build query - Try Flow object directly (may work in Tooling API)
        # Note: FlowDefinition is metadata, Flow is the runtime object
        # For querying active flows, we might need to use Flow object
        soql = f"SELECT {', '.join(fields)} FROM Flow"
        
        if where_clauses:
            soql += " WHERE " + " AND ".join(where_clauses)
        
        # Add sorting (Flow uses CreatedDate instead of LastModifiedDate)
        sort_by = self.options.get("sort_by", "CreatedDate")
        if sort_by == "LastModifiedDate":
            sort_by = "CreatedDate"  # Flow doesn't have LastModifiedDate
        sort_order = self.options.get("sort_order", "Desc")
        soql += f" ORDER BY {sort_by} {sort_order}"
        
        # Add limit if specified
        limit = self.options.get("limit")
        if limit:
            soql += f" LIMIT {limit}"
        
        return soql
    
    def _activate_flows(self):
        """Activate flows using the Tooling API."""
        flows = self._get_flows_to_operate_on()
        
        if not flows:
            self.logger.warning("No flows found to activate.")
            return
        
        self.logger.info(f"Activating {len(flows)} flow(s)...")
        
        success_count = 0
        fail_count = 0
        
        for flow in flows:
            developer_name = flow.get('DeveloperName')
            flow_id = flow.get('Id')
            
            try:
                self._update_flow_status(flow_id, 'Active')
                success_count += 1
                self.logger.info(f"✅ Successfully activated '{definition_id}'")
            except Exception as e:
                fail_count += 1
                self.logger.error(f"❌ Failed to activate '{definition_id}': {e}")
        
        self.logger.info(f"Activation Summary: {success_count} succeeded, {fail_count} failed")
        
        if fail_count > 0:
            raise TaskOptionsError(f"Failed to activate {fail_count} flow(s). Check logs for details.")
    
    def _deactivate_flows(self):
        """Deactivate flows using the Tooling API."""
        flows = self._get_flows_to_operate_on()
        
        if not flows:
            self.logger.warning("No flows found to deactivate.")
            return
        
        self.logger.info(f"Deactivating {len(flows)} flow(s)...")
        
        success_count = 0
        fail_count = 0
        
        for flow in flows:
            developer_name = flow.get('DeveloperName')
            flow_id = flow.get('Id')
            
            try:
                self._update_flow_status(flow_id, 'Inactive')
                success_count += 1
                self.logger.info(f"✅ Successfully deactivated '{definition_id}'")
            except Exception as e:
                fail_count += 1
                self.logger.error(f"❌ Failed to deactivate '{definition_id}': {e}")
        
        self.logger.info(f"Deactivation Summary: {success_count} succeeded, {fail_count} failed")
        
        if fail_count > 0:
            raise TaskOptionsError(f"Failed to deactivate {fail_count} flow(s). Check logs for details.")
    
    def _get_flows_to_operate_on(self) -> List[Dict]:
        """Get flows to operate on based on developer_names or query all."""
        developer_names = self.options.get("developer_names")
        
        if developer_names:
            # Convert to list if string
            if isinstance(developer_names, str):
                developer_names = [developer_names]
            elif not isinstance(developer_names, list):
                raise TaskOptionsError("developer_names must be a string or list of strings")
            
            # Query specific flows
            flows = self._query_flows()
        else:
            # Query all flows matching filters
            flows = self._query_flows()
        
        return flows
    
    def _update_flow_status(self, flow_id: str, status: str):
        """
        Update flow status using Tooling API REST call.
        
        Args:
            flow_id: The Flow Id
            status: 'Active' or 'Inactive'
        """
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")
        
        # Use Tooling API REST endpoint to update Flow
        import requests
        
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        # Get API version from project config or org config
        api_version = getattr(self.org_config, 'api_version', None) or getattr(self.project_config, 'project__package__api_version', '66.0')
        
        url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/Flow/{flow_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"Status": status}
        
        try:
            response = requests.patch(url, headers=headers, json=payload)
            if response.status_code in [200, 204]:
                return True
            else:
                raise TaskOptionsError(f"Failed to update flow status: {response.status_code} - {response.text}")
        except Exception as e:
            raise TaskOptionsError(f"Failed to update flow status to {status}: {e}")
