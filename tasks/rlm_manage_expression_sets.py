"""
Custom CumulusCI task for comprehensive Expression Set management.

    This task provides functionality to:
- Query/list expression sets (by type, process type, status, etc.)
- Manage expression set versions (activate, deactivate, list)
- Filter by interfaceSourceType, processType, status, and other metadata

Expression Sets have:
- DeveloperName, Label, Status (Active/Inactive/Draft)
- InterfaceSourceType (PricingProcedure, RatingProcedure, DiscoveryProcedure, etc.)
- ProcessType (DefaultPricing, DefaultRating, PricingDiscovery, etc.)
- Versions with: fullName, status, rank, startDate, etc.
"""
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import time

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ManageExpressionSets(BaseTask):
    """
    Comprehensive Expression Set management task.
    
    Supports:
    - Querying expression sets (by type, process type, status, etc.)
    - Listing expression sets with metadata
    - Managing expression set versions (activate, deactivate, list)
    """
    
    task_options = {
        "operation": {
            "description": "Operation to perform: 'list', 'query', 'list_versions', 'activate_version', 'deactivate_version', 'activate_versions', 'deactivate_versions'",
            "required": True
        },
        "developer_names": {
            "description": "List of Expression Set DeveloperNames to operate on. If not provided, queries all expression sets.",
            "required": False
        },
        "status": {
            "description": "Filter by Status ('Active', 'Inactive', 'Draft', or None for all). Default: None",
            "required": False
        },
        "interface_source_type": {
            "description": "Filter by InterfaceSourceType (e.g., 'PricingProcedure', 'RatingProcedure', 'DiscoveryProcedure', etc.). Default: None",
            "required": False
        },
        "process_type": {
            "description": "Filter by ProcessType (e.g., 'DefaultPricing', 'DefaultRating', 'PricingDiscovery', etc.). Default: None",
            "required": False
        },
        "version_full_name": {
            "description": "For version operations: Full name of the version (e.g., 'RLM_DefaultPricingProcedure_V1'). Default: None",
            "required": False
        },
        "version_full_names": {
            "description": "For bulk version operations: list or comma-separated FullName values.",
            "required": False
        },
        "metadata_path": {
            "description": "Path to expression set metadata directory used to auto-discover version full names.",
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
            "description": "Maximum number of expression sets to return. Default: None (no limit)",
            "required": False
        }
    }
    
    def _run_task(self):
        """Execute the task based on the operation specified."""
        operation = self.options.get("operation", "").lower()
        
        if operation == "list":
            self._list_expression_sets()
        elif operation == "query":
            self._query_expression_sets()
        elif operation == "list_versions":
            self._list_versions()
        elif operation == "activate_version":
            self._activate_version()
        elif operation == "deactivate_version":
            self._deactivate_version()
        elif operation == "activate_versions":
            self._activate_versions()
        elif operation == "deactivate_versions":
            self._deactivate_versions()
        else:
            raise TaskOptionsError(
                f"Unknown operation: {operation}. Supported operations: "
                "'list', 'query', 'list_versions', 'activate_version', "
                "'deactivate_version', 'activate_versions', 'deactivate_versions'"
            )

    def _get_api_version(self) -> str:
        """Return API version from org config with project fallback."""
        return (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )
    
    def _list_expression_sets(self):
        """List expression sets with their metadata."""
        expression_sets = self._query_expression_sets()
        
        if not expression_sets:
            self.logger.info("No expression sets found matching the criteria.")
            return
        
        self.logger.info(f"Found {len(expression_sets)} expression set(s):")
        self.logger.info("")
        self.logger.info(f"{'DeveloperName':<50} {'MasterLabel':<50} {'LastModified':<20}")
        self.logger.info("-" * 120)
        
        for es in expression_sets:
            dev_name = es.get('DeveloperName', 'N/A')
            label = es.get('MasterLabel', 'N/A')  # ExpressionSetDefinition uses MasterLabel
            last_modified = es.get('LastModifiedDate', 'N/A')
            
            # Format date if present
            if last_modified and last_modified != 'N/A':
                try:
                    from datetime import datetime
                    dt_obj = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                    last_modified = dt_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            self.logger.info(f"{dev_name:<50} {label:<50} {last_modified:<20}")
        
        return expression_sets
    
    def _query_expression_sets(self) -> List[Dict]:
        """
        Query expression sets from Salesforce using Tooling API.
        
        Returns a list of expression set records with their metadata.
        """
        try:
            if not hasattr(self, 'org_config') or not self.org_config:
                raise TaskOptionsError("No org_config available")
            
            # Use requests library for Tooling API calls
            import requests
            
            # Get access token and instance URL
            access_token = self.org_config.access_token
            instance_url = self.org_config.instance_url
            # Get API version from project config or org config
            api_version = self._get_api_version()
            
            # First, try to describe ExpressionSetDefinition object to see available fields
            describe_url = f"{instance_url}/services/data/v{api_version}/tooling/sobjects/ExpressionSetDefinition/describe"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            describe_response = requests.get(describe_url, headers=headers)
            if describe_response.ok:
                describe_data = describe_response.json()
                field_names = [f['name'] for f in describe_data.get('fields', [])]
                self.logger.debug(f"Available ExpressionSetDefinition fields: {', '.join(field_names[:10])}...")
            
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
            
            response = requests.get(url, headers=headers, params=params)
            
            if not response.ok:
                self.logger.error(f"Tooling API query failed: {response.status_code} - {response.text}")
                raise TaskOptionsError(f"Failed to query expression sets: {response.text}")
            
            query_result = response.json()
            
            if not query_result or 'records' not in query_result:
                self.logger.warning("No records returned from query.")
                return []
            
            expression_sets = query_result['records']
            
            # Remove attributes field if present
            for es in expression_sets:
                es.pop('attributes', None)
            
            self.logger.info(f"Query returned {len(expression_sets)} expression set(s).")
            
            return expression_sets
            
        except Exception as e:
            self.logger.error(f"Error querying expression sets: {e}")
            raise TaskOptionsError(f"Failed to query expression sets: {e}")
    
    def _build_soql_query(self) -> str:
        """Build SOQL query based on task options."""
        # Base fields to query - ExpressionSetDefinition fields (from describe)
        # Available fields: Id, DeveloperName, MasterLabel, LastModifiedDate, LastModifiedBy
        # Note: Description, InterfaceSourceType, and ProcessType are not on ExpressionSetDefinition
        # They exist on ExpressionSetDefinitionVersion instead
        fields = [
            "Id",
            "DeveloperName",
            "MasterLabel",  # ExpressionSetDefinition uses MasterLabel, not Label
            "LastModifiedDate",
            "LastModifiedBy.Name"  # Relationship field for LastModifiedBy
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
        
        # Note: InterfaceSourceType and ProcessType are not directly queryable on ExpressionSetDefinition
        # They exist on ExpressionSetDefinitionVersion. We'll filter after querying or query versions.
        # For now, we'll skip these filters at the ExpressionSetDefinition level
        # TODO: Implement filtering via ExpressionSetDefinitionVersion queries
        
        interface_type = self.options.get("interface_source_type")
        process_type = self.options.get("process_type")
        
        if interface_type or process_type:
            self.logger.warning("Filtering by interface_source_type or process_type is not supported at ExpressionSetDefinition level.")
            self.logger.warning("These fields exist on ExpressionSetDefinitionVersion. Use list_versions operation to filter by these fields.")
        
        # Build query
        soql = f"SELECT {', '.join(fields)} FROM ExpressionSetDefinition"
        
        if where_clauses:
            soql += " WHERE " + " AND ".join(where_clauses)
        
        # Add sorting
        sort_by = self.options.get("sort_by", "LastModifiedDate")
        sort_order = self.options.get("sort_order", "Desc")
        soql += f" ORDER BY {sort_by} {sort_order}"
        
        # Add limit if specified
        limit = self.options.get("limit")
        if limit:
            soql += f" LIMIT {limit}"
        
        return soql
    
    def _list_versions(self):
        """List versions for expression sets."""
        expression_sets = self._get_expression_sets_to_operate_on()
        
        if not expression_sets:
            self.logger.warning("No expression sets found to list versions for.")
            return
        
        self.logger.info(f"Listing versions for {len(expression_sets)} expression set(s)...")
        
        for es in expression_sets:
            developer_name = es.get('DeveloperName')
            es_id = es.get('Id')
            
            try:
                versions = self._query_expression_set_versions(es_id)
                
                self.logger.info("")
                self.logger.info(f"Expression Set: {developer_name}")
                self.logger.info(f"{'Version FullName':<60} {'Status':<12} {'Rank':<6} {'StartDate':<25}")
                self.logger.info("-" * 103)
                
                for version in versions:
                    full_name = version.get('FullName', 'N/A')
                    status = version.get('Status', 'N/A')
                    rank = version.get('Rank', 'N/A')
                    start_date = version.get('StartDate', 'N/A')
                    
                    # Format start date
                    if start_date and start_date != 'N/A':
                        try:
                            dt_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                            start_date = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    self.logger.info(f"{full_name:<60} {status:<12} {rank:<6} {start_date:<25}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to list versions for '{developer_name}': {e}")
    
    def _query_expression_set_versions(self, expression_set_id: str) -> List[Dict]:
        """Query versions for a specific expression set."""
        try:
            if not hasattr(self, 'org_config') or not self.org_config:
                raise TaskOptionsError("No org_config available")
            
            # Use requests library for Tooling API calls
            import requests
            
            # Get access token and instance URL
            access_token = self.org_config.access_token
            instance_url = self.org_config.instance_url
            # Get API version from project config or org config
            api_version = self._get_api_version()
            
            # Query ExpressionSetDefinitionVersion using Tooling API
            soql = f"SELECT Id, FullName, Status, Rank, StartDate, Label, Description FROM ExpressionSetDefinitionVersion WHERE ExpressionSetDefinitionId = '{expression_set_id}' ORDER BY Rank ASC"
            
            self.logger.debug(f"Executing Tooling API SOQL query: {soql}")
            
            # Query using Tooling API endpoint
            url = f"{instance_url}/services/data/v{api_version}/tooling/query"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            params = {"q": soql}
            
            response = requests.get(url, headers=headers, params=params)
            
            if not response.ok:
                self.logger.error(f"Tooling API query failed: {response.status_code} - {response.text}")
                raise TaskOptionsError(f"Failed to query expression set versions: {response.text}")
            
            query_result = response.json()
            
            if not query_result or 'records' not in query_result:
                return []
            
            versions = query_result['records']
            
            # Remove attributes field if present
            for version in versions:
                version.pop('attributes', None)
            
            return versions
            
        except Exception as e:
            self.logger.error(f"Error querying expression set versions: {e}")
            raise TaskOptionsError(f"Failed to query expression set versions: {e}")
    
    def _activate_version(self):
        """Activate an expression set version."""
        version_full_name = self.options.get("version_full_name")
        
        if not version_full_name:
            raise TaskOptionsError("version_full_name is required for activate_version operation")
        
        self.logger.info(f"Activating expression set version: {version_full_name}")
        
        try:
            self._update_version_status(version_full_name, 'Active')
            self.logger.info(f"✅ Successfully activated version '{version_full_name}'")
        except Exception as e:
            self.logger.error(f"❌ Failed to activate version '{version_full_name}': {e}")
            raise TaskOptionsError(f"Failed to activate version: {e}")
    
    def _deactivate_version(self):
        """Deactivate an expression set version."""
        version_full_name = self.options.get("version_full_name")
        
        if not version_full_name:
            raise TaskOptionsError("version_full_name is required for deactivate_version operation")
        
        self.logger.info(f"Deactivating expression set version: {version_full_name}")
        
        try:
            self._update_version_status(version_full_name, 'Inactive')
            self.logger.info(f"✅ Successfully deactivated version '{version_full_name}'")
        except Exception as e:
            self.logger.error(f"❌ Failed to deactivate version '{version_full_name}': {e}")
            raise TaskOptionsError(f"Failed to deactivate version: {e}")

    def _activate_versions(self):
        """Activate multiple expression set versions."""
        version_names = self._parse_version_names_option()
        self._set_version_status_for_names(version_names, "Active")

    def _deactivate_versions(self):
        """Deactivate multiple expression set versions."""
        version_names = self._parse_version_names_option()
        self._set_version_status_for_names(version_names, "Inactive")

    def _parse_version_names_option(self) -> List[str]:
        """Get version names from options or discover from metadata files."""
        version_names = self.options.get("version_full_names")
        if not version_names:
            discovered_names = self._discover_version_names_from_metadata()
            if not discovered_names:
                raise TaskOptionsError(
                    "No version_full_names provided and no versions discovered from metadata_path"
                )
            return discovered_names

        if isinstance(version_names, str):
            parsed_names = [name.strip() for name in version_names.split(",") if name.strip()]
        elif isinstance(version_names, list):
            parsed_names = [str(name).strip() for name in version_names if str(name).strip()]
        else:
            raise TaskOptionsError("version_full_names must be a list or comma-separated string")

        if not parsed_names:
            raise TaskOptionsError("No valid values provided in version_full_names")

        return parsed_names

    def _discover_version_names_from_metadata(self) -> List[str]:
        """Discover version full names from expression set metadata XML files."""
        metadata_path = self.options.get(
            "metadata_path", "force-app/main/default/expressionSetDefinition"
        )

        metadata_dir = Path(metadata_path)
        if not metadata_dir.is_absolute():
            metadata_dir = Path.cwd() / metadata_dir

        if not metadata_dir.exists():
            raise TaskOptionsError(f"metadata_path does not exist: {metadata_dir}")
        if not metadata_dir.is_dir():
            raise TaskOptionsError(f"metadata_path is not a directory: {metadata_dir}")

        version_names: List[str] = []
        pattern = "*.expressionSetDefinition-meta.xml"
        xml_files = sorted(metadata_dir.glob(pattern))
        if not xml_files:
            raise TaskOptionsError(
                f"No expression set metadata files found at {metadata_dir} with pattern {pattern}"
            )

        ns = {"md": "http://soap.sforce.com/2006/04/metadata"}
        for xml_file in xml_files:
            try:
                root = ET.parse(xml_file).getroot()
            except ET.ParseError as exc:
                raise TaskOptionsError(f"Failed parsing metadata file {xml_file}: {exc}") from exc

            found_in_file = [
                elem.text.strip()
                for elem in root.findall(".//md:versions/md:fullName", ns)
                if elem.text and elem.text.strip()
            ]
            version_names.extend(found_in_file)

        deduped = list(dict.fromkeys(version_names))
        self.logger.info(
            f"Discovered {len(deduped)} expression set version(s) from metadata path {metadata_dir}"
        )
        return deduped

    def _set_version_status_for_names(self, version_names: List[str], status: str):
        """Set the status for each version name and continue on individual failures."""
        failures = []
        self.logger.info(
            f"Setting status '{status}' for {len(version_names)} expression set version(s)."
        )

        for version_full_name in version_names:
            try:
                self._update_version_status(version_full_name, status)
                self.logger.info(
                    f"✅ Successfully set version '{version_full_name}' to '{status}'"
                )
            except Exception as exc:
                error_text = str(exc)
                if "not found by ApiName" in error_text:
                    self.logger.warning(
                        f"⚠️ Skipping '{version_full_name}': version not present in this org."
                    )
                    continue
                failures.append((version_full_name, error_text))
                self.logger.error(
                    f"❌ Failed to set version '{version_full_name}' to '{status}': {error_text}"
                )

        if failures:
            failed_names = ", ".join(name for name, _ in failures)
            raise TaskOptionsError(
                f"Failed to update {len(failures)} expression set version(s): {failed_names}"
            )
    
    def _get_expression_sets_to_operate_on(self) -> List[Dict]:
        """Get expression sets to operate on based on developer_names or query all."""
        developer_names = self.options.get("developer_names")
        
        if developer_names:
            # Convert to list if string
            if isinstance(developer_names, str):
                developer_names = [developer_names]
            elif not isinstance(developer_names, list):
                raise TaskOptionsError("developer_names must be a string or list of strings")
        
        # Query expression sets
        return self._query_expression_sets()
    
    def _update_version_status(self, version_full_name: str, status: str):
        """
        Update expression set version IsActive using REST API.
        
        Args:
            version_full_name: Version ApiName (e.g., 'RLM_DefaultPricingProcedure_V1')
            status: 'Active' or 'Inactive'
        """
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")
        
        # Use requests library for Tooling API calls
        import requests
        
        # Get access token and instance URL
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = self._get_api_version()
        
        target_is_active = status == "Active"

        # Query ExpressionSetVersion by ApiName to get record Id.
        soql = (
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE ApiName = '{version_full_name}'"
        )
        url = f"{instance_url}/services/data/v{api_version}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {"q": soql}
        
        response = requests.get(url, headers=headers, params=params)
        
        if not response.ok:
            raise TaskOptionsError(f"Failed to query version: {response.text}")
        
        query_result = response.json()
        
        if not query_result or 'records' not in query_result or len(query_result['records']) == 0:
            raise TaskOptionsError(f"Version '{version_full_name}' not found by ApiName")
        
        record = query_result['records'][0]
        version_id = record['Id']
        current_is_active = record.get('IsActive', False)

        if current_is_active == target_is_active:
            self.logger.info(
                "Version '%s' is already %s. Skipping.",
                version_full_name,
                status,
            )
            return True

        # Update the data record directly.
        url = f"{instance_url}/services/data/v{api_version}/sobjects/ExpressionSetVersion/{version_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"IsActive": target_is_active}
        
        try:
            max_attempts = 4
            for attempt in range(1, max_attempts + 1):
                response = requests.patch(url, headers=headers, json=payload)
                if response.status_code in [200, 204]:
                    return True

                response_text = response.text or ""
                is_lock_error = "UNABLE_TO_LOCK_ROW" in response_text
                if is_lock_error and attempt < max_attempts:
                    wait_seconds = attempt * 2
                    self.logger.warning(
                        "Row lock updating '%s' (attempt %s/%s). Retrying in %ss.",
                        version_full_name,
                        attempt,
                        max_attempts,
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)
                    continue

                raise TaskOptionsError(
                    f"Failed to update version status: {response.status_code} - {response_text}"
                )
        except Exception as e:
            raise TaskOptionsError(f"Failed to update version status to {status}: {e}")
