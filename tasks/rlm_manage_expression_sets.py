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
from pathlib import Path
import xml.etree.ElementTree as ET
import time

# Import before CumulusCI: cumulusci's project_config does sys.modules.setdefault("tasks", <synthetic>) and then
# sets tasks.__path__ = [], which empties the repo package's path, so a later `tasks.soql_utils` import fails.
from tasks.soql_utils import option_text, positive_int, requested_names, soql_quote

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


# sort_by values accepted for list/query, mapped to ExpressionSetDefinition fields.
_SORT_FIELDS = {
    "developername": "DeveloperName",
    "label": "MasterLabel",
    "masterlabel": "MasterLabel",
    "lastmodifieddate": "LastModifiedDate",
    "createddate": "CreatedDate",
}


class ManageExpressionSets(BaseSalesforceTask):
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
            "description": "Expression Set DeveloperNames to operate on (comma-separated string or list). If not provided, queries all expression sets. Used by list, query and list_versions only; version operations ignore it: activate_version and deactivate_version read version_full_name; activate_versions and deactivate_versions read version_full_names, else every version under metadata_path (default force-app/main/default/expressionSetDefinition).",
            "required": False
        },
        "status": {
            "description": "list/query/list_versions: keep only expression sets that have at least one version with this Status ('Active', 'Draft' or 'Inactive'). Status lives on the version, not on the expression set. Default: None",
            "required": False
        },
        "interface_source_type": {
            "description": "list/query/list_versions: keep only expression sets whose InterfaceSourceType matches (e.g., 'PricingProcedure', 'RatingProcedure', 'DiscoveryProcedure'). Read from each set's metadata, so it costs one request per candidate set. Default: None",
            "required": False
        },
        "process_type": {
            "description": "list/query/list_versions: keep only expression sets whose ProcessType matches (e.g., 'DefaultPricing', 'DefaultRating', 'PricingDiscovery'). Read from each set's metadata, so it costs one request per candidate set. Default: None",
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
            "description": "Path to the expression set metadata directory used to discover version full names when version_full_names is not set. Default: force-app/main/default/expressionSetDefinition",
            "required": False
        },
        "sort_by": {
            "description": "list/query/list_versions: DeveloperName, Label, LastModifiedDate or CreatedDate. Default: 'LastModifiedDate'",
            "required": False
        },
        "sort_order": {
            "description": "list/query/list_versions: 'Asc' or 'Desc'. Default: 'Desc'",
            "required": False
        },
        "limit": {
            "description": "list/query/list_versions: maximum number of expression sets to return, applied after the filters. Default: None (no limit)",
            "required": False
        }
    }
    
    def _run_task(self):
        """Execute the task based on the operation specified."""
        operation = (self._option_text("operation") or "").lower()
        
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
        """Return the project API version (OrgConfig has no api_version attribute)."""
        # Not org_config.api_version: OrgConfig has no such attribute (BaseConfig.__getattr__ warns, and
        # raises AssertionError under STRICT_GETATTR).
        version = self.project_config.project__package__api_version
        if not version:
            raise TaskOptionsError("No API version: set project.package.api_version in cumulusci.yml")
        return str(version).lstrip("v")
    
    def _list_expression_sets(self):
        """List expression sets with their metadata."""
        expression_sets = self._query_expression_sets()
        
        if not expression_sets:
            self.logger.info("No expression sets found matching the criteria.")
            return
        
        self.logger.info(f"Found {len(expression_sets)} expression set(s):")
        self.logger.info("")
        with_meta = any("InterfaceSourceType" in es for es in expression_sets)
        header = f"{'DeveloperName':<50} {'MasterLabel':<50} {'LastModified':<20}"
        if with_meta:
            header += f" {'InterfaceSourceType':<22} {'ProcessType':<20}"
        self.logger.info(header)
        self.logger.info("-" * len(header))
        
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
            
            line = f"{dev_name:<50} {label:<50} {last_modified:<20}"
            if with_meta:
                line += f" {es.get('InterfaceSourceType') or 'N/A':<22} {es.get('ProcessType') or 'N/A':<20}"
            self.logger.info(line)
        
        return expression_sets
    
    def _query_expression_sets(self) -> List[Dict]:
        """
        Query expression sets from Salesforce using Tooling API.

        Status is filtered in SOQL (a semi-join on the versions). InterfaceSourceType and
        ProcessType exist only in each set's Metadata, which the Tooling API returns one
        record at a time, so those two filters read each candidate set's Metadata and
        filter here; the limit then applies to the filtered result.
        """
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")

        interface_type = self._option_text("interface_source_type")
        process_type = self._option_text("process_type")
        needs_metadata = bool(interface_type or process_type)

        limit = self._option_text("limit")
        limit = positive_int(limit, "limit", TaskOptionsError) if limit else None
        soql = self._build_soql_query(apply_limit=not needs_metadata)
        expression_sets = self._tooling_query(soql, "expression sets")

        if needs_metadata:
            matched = []
            for es in expression_sets:
                meta = self._tooling_get(
                    f"sobjects/ExpressionSetDefinition/{es['Id']}", "expression set metadata"
                ).get("Metadata") or {}
                es["InterfaceSourceType"] = meta.get("interfaceSourceType")
                es["ProcessType"] = meta.get("processType")
                if interface_type and es["InterfaceSourceType"] != interface_type:
                    continue
                if process_type and es["ProcessType"] != process_type:
                    continue
                matched.append(es)
                if limit and len(matched) == limit:
                    break
            expression_sets = matched

        self.logger.info(f"Query returned {len(expression_sets)} expression set(s).")
        return expression_sets

    def _option_text(self, name: str):
        """The option as stripped text; blank means not set; a list or dict is refused."""
        return option_text(self.options.get(name), name, TaskOptionsError)

    def _tooling_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _tooling_url(self, path: str) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._get_api_version()}/tooling/{path}"

    def _tooling_get(self, path: str, what: str) -> Dict:
        import requests

        response = requests.get(self._tooling_url(path), headers=self._tooling_headers())
        if not response.ok:
            raise TaskOptionsError(f"Failed to read {what}: {response.status_code} - {response.text}")
        return response.json() or {}

    def _tooling_query(self, soql: str, what: str) -> List[Dict]:
        """Run a Tooling API query, follow nextRecordsUrl, and drop `attributes`."""
        import requests

        self.logger.debug(f"Executing Tooling API SOQL query: {soql}")
        response = requests.get(
            self._tooling_url("query"), headers=self._tooling_headers(), params={"q": soql}
        )
        records: List[Dict] = []
        while True:
            if not response.ok:
                raise TaskOptionsError(f"Failed to query {what}: {response.status_code} - {response.text}")
            body = response.json() or {}
            records.extend(body.get("records", []))
            next_url = body.get("nextRecordsUrl")
            if not next_url or body.get("done", True):
                break
            response = requests.get(
                f"{self.org_config.instance_url}{next_url}", headers=self._tooling_headers()
            )
        for record in records:
            record.pop("attributes", None)
        return records

    def _build_soql_query(self, apply_limit: bool = True) -> str:
        """Build the ExpressionSetDefinition SOQL (every value escaped or whitelisted)."""
        fields = [
            "Id",
            "DeveloperName",
            "MasterLabel",
            "LastModifiedDate",
            "LastModifiedBy.Name",
        ]
        where_clauses = []

        names = requested_names(self.options.get("developer_names"), "developer_names", TaskOptionsError)
        if names:
            where_clauses.append("DeveloperName IN (" + ", ".join(soql_quote(n) for n in names) + ")")

        status = self._option_text("status")
        if status:
            where_clauses.append(
                "Id IN (SELECT ExpressionSetDefinitionId FROM ExpressionSetDefinitionVersion "
                f"WHERE Status = {soql_quote(status)})"
            )

        soql = f"SELECT {', '.join(fields)} FROM ExpressionSetDefinition"
        if where_clauses:
            soql += " WHERE " + " AND ".join(where_clauses)

        sort_key = (self._option_text("sort_by") or "LastModifiedDate").replace("_", "").lower()
        if sort_key not in _SORT_FIELDS:
            raise TaskOptionsError(
                "sort_by must be one of DeveloperName, Label, LastModifiedDate, CreatedDate; "
                f"got {self.options.get('sort_by')!r}"
            )
        sort_order = (self._option_text("sort_order") or "Desc").capitalize()
        if sort_order not in ("Asc", "Desc"):
            raise TaskOptionsError(f"sort_order must be 'Asc' or 'Desc', got {self.options.get('sort_order')!r}")
        soql += f" ORDER BY {_SORT_FIELDS[sort_key]} {sort_order}"

        limit = self._option_text("limit")
        if apply_limit and limit:
            soql += f" LIMIT {positive_int(limit, 'limit', TaskOptionsError)}"

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
                self.logger.info(f"{'Version FullName':<60} {'Status':<12} {'Version':<8}")
                self.logger.info("-" * 82)
                
                for version in versions:
                    self.logger.info(
                        f"{version.get('FullName') or 'N/A':<60} "
                        f"{version.get('Status') or 'N/A':<12} "
                        f"{str(version.get('VersionNumber', 'N/A')):<8}"
                    )

            except Exception as e:
                self.logger.error(f"❌ Failed to list versions for '{developer_name}': {e}")
    
    def _query_expression_set_versions(self, expression_set_id: str) -> List[Dict]:
        """Query versions for a specific expression set."""
        if not hasattr(self, 'org_config') or not self.org_config:
            raise TaskOptionsError("No org_config available")
        soql = (
            "SELECT Id, FullName, VersionNumber, Status, MasterLabel "
            "FROM ExpressionSetDefinitionVersion "
            f"WHERE ExpressionSetDefinitionId = {soql_quote(expression_set_id)} "
            "ORDER BY VersionNumber ASC"
        )
        return self._tooling_query(soql, "expression set versions")

    def _activate_version(self):
        """Activate an expression set version."""
        version_full_name = self._option_text("version_full_name")
        
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
        version_full_name = self._option_text("version_full_name")
        
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
        version_names = requested_names(
            self.options.get("version_full_names"), "version_full_names", TaskOptionsError
        )
        if not version_names:
            discovered_names = self._discover_version_names_from_metadata()
            if not discovered_names:
                raise TaskOptionsError(
                    "No version_full_names provided and no versions discovered from metadata_path"
                )
            # Blank counts as not set, so name the fallback: the operation acts on every discovered version.
            self.logger.warning(f"version_full_names not set: using all {len(discovered_names)} discovered version(s)")
            return discovered_names

        return version_names

    def _discover_version_names_from_metadata(self) -> List[str]:
        """Discover version full names from expression set metadata XML files."""
        metadata_path = self._option_text("metadata_path") or "force-app/main/default/expressionSetDefinition"

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
        # Query expression sets
        return self._query_expression_sets()
    
    def _update_version_status(self, version_full_name: str, status: str):
        """
        Update an expression set version's status using the REST API.

        Constraint models (ExpressionSet.UsageType = 'Constraint') go through the
        constraint-version resource, /industries/constraints/{setId}/versions/{versionId}:
        it deploys the model to the constraint solver on activation (with every other active
        constraint model, todo 313) and removes it on deactivation. A plain
        ExpressionSetVersion.IsActive update flips the record but never reaches the solver,
        so a re-imported model kept running the old one (todo 064).
        Every other expression set keeps the sObject IsActive update.

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
            "SELECT Id, IsActive, ExpressionSetId, ExpressionSet.UsageType FROM ExpressionSetVersion "
            f"WHERE ApiName = {soql_quote(version_full_name)}"
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
        is_constraint_model = (record.get("ExpressionSet") or {}).get("UsageType") == "Constraint"

        if current_is_active == target_is_active:
            self.logger.info(
                "Version '%s' is already %s. Skipping.",
                version_full_name,
                status,
            )
            if is_constraint_model and target_is_active:
                self.logger.warning(
                    "'%s' is a constraint model: skipping an already-Active version does not "
                    "redeploy it to the solver. Deactivate it first to pick up a re-import.",
                    version_full_name,
                )
            return True

        if is_constraint_model:
            # Deploys to (or removes from) the constraint solver; see the docstring.
            url = (
                f"{instance_url}/services/data/v{api_version}/industries/constraints/"
                f"{record['ExpressionSetId']}/versions/{version_id}"
            )
            payload = {"status": status}
        else:
            # Update the data record directly.
            url = f"{instance_url}/services/data/v{api_version}/sobjects/ExpressionSetVersion/{version_id}"
            payload = {"IsActive": target_is_active}

        try:
            max_attempts = 4
            for attempt in range(1, max_attempts + 1):
                response = requests.patch(url, headers=headers, json=payload)
                if response.status_code in [200, 204]:
                    if not is_constraint_model:
                        return True
                    # The constraint resource reports a failed deploy as HTTP 200 with
                    # success: false, so the status code alone proves nothing.
                    try:
                        body = response.json() if response.text else {}
                    except ValueError:
                        raise TaskOptionsError(
                            "Constraint version status update returned a 200 that is not JSON: "
                            f"{response.text[:300]}"
                        )
                    if body.get("success") is True:
                        return True
                    raise TaskOptionsError(
                        f"Constraint version status update failed: {body.get('errors') or body}"
                    )

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
