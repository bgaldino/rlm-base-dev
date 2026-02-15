"""
Custom CumulusCI task to exclude active decision tables from deployment.
Active decision tables cannot be edited, so we skip deploying them by moving
them into a .skip subdirectory before deploy_pre; restore_decision_tables
moves them back after deploy. No .forceignore changes are made—the .skip
move is sufficient and avoids leaving .forceignore entries behind.
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
    """Exclude active decision tables from deployment and move them out of deploy path."""
    
    task_options = {
        "path": {
            "description": "Path to decision tables directory",
            "required": True
        },
        "skip_dir": {
            "description": "Directory name for temporarily skipped decision tables",
            "required": False
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
        path = Path(self.options.get("path"))
        skip_dir_name = self.options.get("skip_dir") or ".skip"
        skip_dir = path / skip_dir_name
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
        self._move_active_decision_tables(path, skip_dir, active_decision_tables)
    
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

    def _move_active_decision_tables(self, decision_tables_path: Path, skip_dir: Path, active_tables: Set[str]):
        """Move active decision tables out of deploy path to avoid MDAPI updates."""
        try:
            if not decision_tables_path.exists():
                self.logger.warning(f"Decision tables path not found: {decision_tables_path}")
                return

            skip_dir.mkdir(parents=True, exist_ok=True)
            moved = 0

            for dt_name in sorted(active_tables):
                source_file = decision_tables_path / f"{dt_name}.decisionTable-meta.xml"
                target_file = skip_dir / source_file.name
                if source_file.exists():
                    source_file.replace(target_file)
                    moved += 1
                    self.logger.info(f"Moved {dt_name} to {skip_dir}")

            if moved:
                self.logger.info(f"Moved {moved} active decision table(s) to {skip_dir}")
        except Exception as e:
            self.logger.warning(f"Error moving active decision tables: {e}")


class RestoreDecisionTables(BaseTask):
    """Restore decision table metadata moved out of deploy path."""

    task_options = {
        "path": {
            "description": "Path to decision tables directory",
            "required": True
        },
        "skip_dir": {
            "description": "Directory name containing skipped decision tables",
            "required": False
        },
    }

    def _run_task(self):
        decision_tables_path = Path(self.options.get("path"))
        skip_dir_name = self.options.get("skip_dir") or ".skip"
        skip_dir = decision_tables_path / skip_dir_name

        if not skip_dir.exists():
            self.logger.info("No skipped decision tables to restore.")
            return

        restored = 0
        for file in skip_dir.glob("*.decisionTable-meta.xml"):
            target = decision_tables_path / file.name
            if not target.exists():
                file.replace(target)
                restored += 1
                self.logger.info(f"Restored {file.name}")

        if restored:
            self.logger.info(f"Restored {restored} decision table(s) from {skip_dir}")
