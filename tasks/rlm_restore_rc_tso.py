"""
Custom CumulusCI task to restore RC_TSO from .skip file before deployment.
"""
from pathlib import Path
from typing import Dict, Any

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class RestoreRLMTSO(BaseTask):
    """Restore RLM_TSO from .skip file so it can be deployed."""
    
    task_options: Dict[str, Dict[str, Any]] = {
        "path": {
            "description": "Path to permission set groups directory",
            "required": True
        }
    }
    
    def _run_task(self):
        path = self.options.get("path")
        psg_path = Path(path) / "3_permissionsetgroups"
        tso_storage_dir = Path(path) / "3_permissionsetgroups_tso"
        tso_storage_file = tso_storage_dir / "RLM_TSO.permissionsetgroup-meta.xml"
        tso_file = psg_path / "RLM_TSO.permissionsetgroup-meta.xml"
        
        if not tso_storage_dir.exists():
            self.logger.warning(f"RLM_TSO storage directory does not exist: {tso_storage_dir}")
            return
        
        if tso_storage_file.exists() and not tso_file.exists():
            # Move RC_TSO from storage to main directory for deployment
            tso_storage_file.rename(tso_file)
            self.logger.info("RLM_TSO moved from storage directory for deployment")
        elif tso_file.exists():
            self.logger.debug("RLM_TSO already exists in main directory, no move needed")
        else:
            self.logger.warning("RLM_TSO file not found in storage directory")
