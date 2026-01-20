"""
Custom CumulusCI task to exclude active decision tables from deployment.
Active decision tables cannot be edited, so we skip deploying them.
TODO: Find a proper way to deactivate decision tables before deployment.
"""
import os
from pathlib import Path
from typing import Set, List

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ExcludeActiveDecisionTables(BaseTask):
    """Exclude active decision tables from deployment by adding them to .forceignore."""
    
    task_options = {
        "path": {
            "description": "Path to decision tables directory",
            "required": True
        },
        "decision_tables": {
            "description": "List of decision table developer names to check",
            "required": False
        }
    }
    
    # Decision tables that cause issues when active
    PROBLEMATIC_DECISION_TABLES = {
        "RLM_CostBookEntries",
        "RLM_ProductCategoryQualification", 
        "RLM_ProductQualification"
    }
    
    def _run_task(self):
        path = self.options.get("path")
        decision_tables_to_check = self.options.get("decision_tables", self.PROBLEMATIC_DECISION_TABLES)
        
        # Only run for scratch orgs
        is_scratch = False
        try:
            if hasattr(self, 'org_config') and self.org_config:
                is_scratch = getattr(self.org_config, 'scratch', False)
        except AttributeError:
            pass
        
        if not is_scratch:
            self.logger.info("Skipping active decision table exclusion - not a scratch org")
            return
        
        # Query active decision tables
        active_decision_tables = self._get_active_decision_tables(decision_tables_to_check)
        
        if not active_decision_tables:
            self.logger.info("No active decision tables found to exclude")
            return
        
        self.logger.info(f"Found {len(active_decision_tables)} active decision table(s) to exclude from deployment")
        
        # Add active decision tables to .forceignore
        self._manage_forceignore(path, active_decision_tables)
    
    def _get_active_decision_tables(self, decision_table_names: Set[str]) -> Set[str]:
        """Query Salesforce to find which decision tables are active."""
        active_tables = set()
        
        try:
            # Use CumulusCI's Salesforce connection
            if not hasattr(self, 'org_config') or not self.org_config:
                self.logger.warning("No org_config available, excluding all problematic decision tables as safety measure")
                return decision_table_names
            
            # Get Salesforce connection
            sf = self.org_config.salesforce_client
            
            # Build SOQL query
            dev_names = "', '".join(decision_table_names)
            soql = f"SELECT DeveloperName, Status FROM DecisionTable WHERE DeveloperName IN ('{dev_names}') AND Status = 'Active'"
            
            # Query using Salesforce connection
            result = sf.query(soql)
            
            if result and 'records' in result:
                for record in result['records']:
                    dev_name = record.get('DeveloperName')
                    status = record.get('Status')
                    if status == 'Active' and dev_name:
                        active_tables.add(dev_name)
                        self.logger.info(f"Decision table {dev_name} is active - will exclude from deployment")
            
            self.logger.info(f"Found {len(active_tables)} active decision table(s) out of {len(decision_table_names)} checked")
            
        except Exception as e:
            self.logger.warning(f"Error querying decision tables: {e}. Will exclude all problematic decision tables as a safety measure.")
            # If we can't query, exclude all problematic tables to be safe
            active_tables = decision_table_names
        
        return active_tables
    
    def _manage_forceignore(self, decision_tables_path: Path, active_tables: Set[str]):
        """Add active decision tables to .forceignore."""
        forceignore_path = Path.cwd() / ".forceignore"
        if not forceignore_path.exists():
            self.logger.warning(".forceignore file not found, skipping decision table exclusion")
            return
        
        try:
            # Read current .forceignore
            with open(forceignore_path, 'r') as f:
                lines = f.readlines()
            
            # Find existing decision table entries
            existing_entries = set()
            entry_indices = {}
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    for dt_name in active_tables:
                        if dt_name in stripped and 'decisionTable' in stripped:
                            existing_entries.add(dt_name)
                            entry_indices[dt_name] = i
            
            # Add missing entries
            new_entries = active_tables - existing_entries
            if new_entries:
                # Find the decision tables section or add at end
                dt_section_index = -1
                for i, line in enumerate(lines):
                    if "# Decision Tables" in line or "#decisiontables" in line.lower():
                        dt_section_index = i
                        break
                
                comment = "# Active decision tables - excluded from deployment (TODO: implement proper deactivation)"
                
                if dt_section_index >= 0:
                    # Insert after decision tables section
                    insert_index = dt_section_index + 1
                    # Find the next non-comment line after section
                    for i in range(dt_section_index + 1, len(lines)):
                        if lines[i].strip() and not lines[i].strip().startswith('#'):
                            insert_index = i
                            break
                        if lines[i].strip().startswith('#'):
                            insert_index = i + 1
                    
                    # Insert comment if not already there
                    if comment not in ''.join(lines):
                        lines.insert(insert_index, f"{comment}\n")
                        insert_index += 1
                    
                    # Insert decision table entries
                    for dt_name in sorted(new_entries):
                        entry = f"{decision_tables_path}/{dt_name}.decisionTable-meta.xml\n"
                        lines.insert(insert_index, entry)
                        insert_index += 1
                        self.logger.info(f"Added {dt_name} to .forceignore")
                else:
                    # Add at end
                    if comment not in ''.join(lines):
                        lines.append(f"\n{comment}\n")
                    for dt_name in sorted(new_entries):
                        entry = f"{decision_tables_path}/{dt_name}.decisionTable-meta.xml\n"
                        lines.append(entry)
                        self.logger.info(f"Added {dt_name} to .forceignore")
                
                # Write updated .forceignore
                with open(forceignore_path, 'w') as f:
                    f.writelines(lines)
                
                self.logger.info(f"Added {len(new_entries)} active decision table(s) to .forceignore")
            else:
                self.logger.debug("All active decision tables already in .forceignore")
                
        except Exception as e:
            self.logger.warning(f"Error managing .forceignore: {e}")
