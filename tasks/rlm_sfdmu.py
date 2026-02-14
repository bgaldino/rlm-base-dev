import json
import os
import shutil
import subprocess
import tempfile
from abc import abstractmethod
from typing import Dict, Any, Optional

# Note: If CumulusCI is not installed, you'll need to install it or mock these imports for development
try:
    from cumulusci.core.config import ScratchOrgConfig
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.keychain import BaseProjectKeychain
except ImportError:
    print("CumulusCI not found. Please install it or mock these imports for development.")
    # For development without CumulusCI, you can use:
    # ScratchOrgConfig = object
    # SFDXBaseTask = object
    # TaskOptionsError = Exception
    # CommandException = Exception
    # BaseProjectKeychain = object

# Constants
LOAD_COMMAND = "sf sfdmu run --sourceusername CSVFILE --targetusername {targetusername} -p {pathtoexportjson} --canmodify {instanceurl} --noprompt --verbose"
SCRATCHORG_LOAD_COMMAND = "sf sfdmu run --sourceusername CSVFILE --targetusername {targetusername} -p {pathtoexportjson} --canmodify {instanceurl} --noprompt --verbose"
EXPORT_JSON_FILENAME = "export.json"
DRO_ASSIGNED_TO_PLACEHOLDER = "__DRO_ASSIGNED_TO_USER__"
DRO_CSV_FILES_TO_REPLACE = ("FulfillmentStepDefinition.csv", "UserAndGroup.csv")

class LoadSFDMUData(SFDXBaseTask):
    keychain_class = BaseProjectKeychain
    task_options: Dict[str, Dict[str, Any]] = {
        "pathtoexportjson": {
            "description": "Directory path to the export.json to upload",
            "required": True
        },
        "targetusername": {
            "description": "Username or AccessToken of the account that will be used to upload the data",
            "required": False
        },
        "instanceurl": {
            "description": "Instance url for the targetusername.",
            "required": False
        },
        "accesstoken": {
            "description": "Passed in accesstoken associated to the targetusername and instance url.",
            "required": False
        },
        "org": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        },
        "dynamic_assigned_to_user": {
            "description": "If true, query the target org for the default user's Name and replace the placeholder in DRO CSVs (FulfillmentStepDefinition.csv, UserAndGroup.csv) so one plan works for both scratch (User User) and TSO (Admin User).",
            "required": False
        },
        "assigned_to_placeholder": {
            "description": "Placeholder string in DRO CSVs to replace with the target org user's Name. Used when dynamic_assigned_to_user is true.",
            "required": False
        }
    }

    def _prepare_export_json_file(self) -> None:
        export_json_path = os.path.join(self.pathtoexportjson, EXPORT_JSON_FILENAME)
        if not os.path.isdir(self.pathtoexportjson):
            raise FileNotFoundError(f"Path to export.json is not valid: {self.pathtoexportjson}")
        if not os.path.isfile(export_json_path):
            raise FileNotFoundError(f"export.json is missing: {export_json_path}")
        
        try:
            with open(export_json_path, "r") as file:
                export_json = json.load(file)
            
            org_data = {
                'name': self.targetusername,
                'accessToken': self.accesstoken,
                'instanceUrl': self.instanceurl
            }
            export_json["orgs"] = [org_data]
            
            with open(export_json_path, "w") as file:
                json.dump(export_json, file, indent=2)
            
            self.logger.info(f'Formatted EXPORT.JSON: {json.dumps(export_json, indent=2)}')
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing export.json: {e}")
            raise
        except IOError as e:
            self.logger.error(f"Error reading/writing export.json: {e}")
            raise

    def _cleanup_export_json_file(self) -> None:
        export_json_path = os.path.join(self.pathtoexportjson, EXPORT_JSON_FILENAME)
        try:
            with open(export_json_path, "r") as file:
                export_json = json.load(file)
            
            export_json["orgs"] = []
            
            with open(export_json_path, "w") as file:
                json.dump(export_json, file, indent=2)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error cleaning up export.json: {e}")

    def _get_target_org_user_name(self) -> str:
        """Query the target org for the current user's Name (e.g. 'User User' or 'Admin User')."""
        username = getattr(self.org_config, "username", None) or self.targetusername
        if not username or "@" not in str(username):
            raise CommandException(
                "dynamic_assigned_to_user requires an org with a username (e.g. scratch or connected org). "
                "Cannot determine user when target is token-only."
            )
        # Use username for -o so SF CLI finds the org (CCI org name like 'tfid-cdo' may not be a valid CLI alias)
        org_for_cli = str(username)
        escaped = org_for_cli.replace("\\", "\\\\").replace("'", "\\'")
        query = "SELECT Name FROM User WHERE Username = '%s'" % escaped
        result = subprocess.run(
            ["sf", "data", "query", "-q", query, "-o", org_for_cli, "--json"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.logger.error(f"sf data query STDERR: {result.stderr}")
            raise CommandException(f"Failed to query User Name: {result.stderr or result.stdout}")
        out = json.loads(result.stdout)
        records = out.get("result", {}).get("records") or []
        if not records:
            raise CommandException("No User record found for target org username.")
        name = records[0].get("Name")
        if not name:
            raise CommandException("User record has no Name.")
        return name

    def _apply_dynamic_assigned_to_user(self) -> None:
        """Copy plan to a temp dir and replace DRO assigned-to placeholder with target org user Name."""
        placeholder = self.options.get("assigned_to_placeholder") or DRO_ASSIGNED_TO_PLACEHOLDER
        user_name = self._get_target_org_user_name()
        self.logger.info(f"Replacing DRO assigned-to placeholder with target org user Name: {user_name}")
        source_dir = self.pathtoexportjson
        self._temp_plan_dir = tempfile.mkdtemp(prefix="sfdmu_dro_")
        try:
            for item in os.listdir(source_dir):
                src = os.path.join(source_dir, item)
                dst = os.path.join(self._temp_plan_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            for filename in DRO_CSV_FILES_TO_REPLACE:
                path = os.path.join(self._temp_plan_dir, filename)
                if not os.path.isfile(path):
                    continue
                with open(path, "r", encoding="utf-8", newline="") as f:
                    content = f.read()
                if placeholder not in content:
                    continue
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(content.replace(placeholder, user_name))
                self.logger.info(f"Replaced placeholder in {filename}")
            self.pathtoexportjson = self._temp_plan_dir
        except Exception:
            if getattr(self, "_temp_plan_dir", None) and os.path.isdir(self._temp_plan_dir):
                shutil.rmtree(self._temp_plan_dir, ignore_errors=True)
            raise

    def _set_project_defaults(self, instanceurl: str) -> None:
        try:
            subprocess.run(["sf", "config set", f"instanceUrl={instanceurl}"], 
                           check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting project defaults: {e}")
            raise CommandException(f"Error setting project defaults: {e}")

    def _init_options(self, kwargs: Dict[str, Any]) -> None:
        super(LoadSFDMUData, self)._init_options(kwargs)
        self.env = self._get_env()
        self.keychain: Optional[BaseProjectKeychain] = None

    @property
    def keychain_cls(self):
        return self.get_keychain_class() or self.keychain_class

    @abstractmethod
    def get_keychain_class(self):
        return None

    @property
    def keychain_key(self):
        return self.get_keychain_key()

    @abstractmethod
    def get_keychain_key(self):
        return None
    
    def _load_keychain(self) -> None:
        if self.keychain is not None:
            return

        keychain_key = self.keychain_key if self.keychain_cls.encrypted else None

        if self.project_config is None:
            self.keychain = self.keychain_cls(self.universal_config, keychain_key)
        else:
            self.keychain = self.keychain_cls(self.project_config, keychain_key)
            self.project_config.keychain = self.keychain

    def _prep_runtime(self) -> None:
        if "org" not in self.options or not self.options["org"]:
            self._load_keychain()
        
        self.pathtoexportjson = self.options.get("pathtoexportjson", "datasets/sfdmu/")
        self._temp_plan_dir = None

        if isinstance(self.org_config, ScratchOrgConfig):
            self.targetusername = self.org_config.username
        else:
            self.targetusername = self.options.get("targetusername") or self.org_config.access_token

        self.accesstoken = self.options.get("accesstoken") or self.org_config.access_token
        self.instanceurl = self.options.get("instanceurl") or self.org_config.instance_url

        if self.options.get("dynamic_assigned_to_user"):
            self._apply_dynamic_assigned_to_user()
        self._prepare_export_json_file()
    
    def _run_task(self) -> None:
        try:
            self._prep_runtime()
            
            self.logger.info(f'Target Path: {self.pathtoexportjson}')
            self.logger.info(f'Current Working Directory: {self.options.get("dir")}')
            
            cmd = self._get_command()
            self.logger.info(f'Executing command: {cmd}')  # Log the command being executed
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.options.get("dir"))
            
            if result.returncode != 0:
                self.logger.error(f"Command failed with exit code {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                raise CommandException(f"Command failed with exit code {result.returncode}")
            
            for line in result.stdout.splitlines():
                self.logger.info(line)
            
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            raise
        finally:
            self.logger.info('Cleaning up export.json...')
            self._cleanup_export_json_file()
            if getattr(self, "_temp_plan_dir", None) and os.path.isdir(self._temp_plan_dir):
                shutil.rmtree(self._temp_plan_dir, ignore_errors=True)
                self.logger.info("Removed temp plan directory.")
    def _get_command(self) -> str:
        trimmed_instance_url = self._trim_instance_url(self.instanceurl)
        if not isinstance(self.org_config, ScratchOrgConfig):
            return LOAD_COMMAND.format(
                targetusername=self.targetusername,
                pathtoexportjson=self.pathtoexportjson,
                instanceurl=trimmed_instance_url
            )
        else:
            return SCRATCHORG_LOAD_COMMAND.format(
                targetusername=self.targetusername,
                pathtoexportjson=self.pathtoexportjson,
                instanceurl=trimmed_instance_url
            )
        
    def _trim_instance_url(self, url: str) -> str:
        return url.replace("https://", "").replace("http://", "")