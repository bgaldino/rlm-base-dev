import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from abc import abstractmethod
from typing import Dict, Any, Optional

# Note: If CumulusCI is not installed, you'll need to install it or mock these imports for development.
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
EXTRACT_COMMAND = "sf sfdmu run --sourceusername {sourceusername} --targetusername CSVFILE -p {pathtoexportjson} --noprompt --verbose"
EXPORT_JSON_FILENAME = "export.json"
DRO_ASSIGNED_TO_PLACEHOLDER = "__DRO_ASSIGNED_TO_USER__"
DRO_CSV_FILES_TO_REPLACE = ("FulfillmentStepDefinition.csv", "UserAndGroup.csv")


def run_post_process_script(
    extraction_dir: str,
    plan_dir: str,
    output_dir: str,
    cwd: Optional[str] = None,
    logger: Optional[Any] = None,
) -> None:
    """Run post_process_extraction.py to make extracted CSVs v5 import-ready ($$ columns, header normalization).
    Shared by ExtractSFDMUData and TestSFDMUIdempotency.
    """
    cwd = cwd or os.getcwd()
    script = os.path.join(cwd, "scripts", "post_process_extraction.py")
    if not os.path.isfile(script):
        raise FileNotFoundError(f"Post-process script not found: {script}")
    cmd = [sys.executable, script, extraction_dir, plan_dir, "--output-dir", output_dir]
    if logger:
        logger.info(f"Running post-process: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if logger:
        for line in (result.stdout or "").splitlines():
            logger.info(line)
    if result.returncode != 0:
        if logger:
            logger.error(result.stderr or "")
        raise CommandException(f"Post-process failed with exit code {result.returncode}")
    if logger and result.stderr:
        logger.warning(result.stderr)


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
        "sync_objectset_source_to_source": {
            "description": "If true, before running SFDMU copy objectset_source/object-set-* into source/object-set-* so object set 2+ use the version-controlled CSVs as source (avoids org-export overwriting desired state for billing etc.).",
            "required": False
        },
        "object_sets": {
            "description": "Optional list of 0-based object set indices to run (e.g. [0] for Pass 1 only, [1, 2] for Pass 2 and 3). If omitted, all object sets run.",
            "required": False
        },
        "assigned_to_placeholder": {
            "description": "Placeholder string in DRO CSVs to replace with the target org user's Name. Used when dynamic_assigned_to_user is true.",
            "required": False
        },
        "simulation": {
            "description": "If true, run SFDMU in simulation mode (dry run without writing to the target org).",
            "required": False
        }
    }

    def _sync_objectset_source_to_source(self) -> None:
        """Copy objectset_source/object-set-* into source so SFDMU uses version-controlled CSVs.
        Object set 1: also copy to plan root (base) so Pass 1 uses our composites; copy to source/ with _source suffix.
        Object sets 2+ use source/object-set-N only.
        Set 1 must have BillingPolicy (no default treatment) and BillingTreatment so lookups resolve in order.
        """
        base = self.pathtoexportjson
        objectset_source_dir = os.path.join(base, "objectset_source")
        source_dir = os.path.join(base, "source")
        if not os.path.isdir(objectset_source_dir):
            return
        for name in sorted(os.listdir(objectset_source_dir)):
            if not name.startswith("object-set-"):
                continue
            src_set = os.path.join(objectset_source_dir, name)
            if not os.path.isdir(src_set):
                continue
            # Object set 1 uses source/ (root); sets 2+ use source/object-set-N
            if name == "object-set-1":
                dst_set = source_dir
            else:
                dst_set = os.path.join(source_dir, name)
            os.makedirs(dst_set, exist_ok=True)
            for f in os.listdir(src_set):
                if not f.endswith(".csv"):
                    continue
                src_f = os.path.join(src_set, f)
                dst_name = f.replace(".csv", "_source.csv") if not f.endswith("_source.csv") else f
                dst_f = os.path.join(dst_set, dst_name)
                shutil.copy2(src_f, dst_f)
                self.logger.info(f"Synced objectset_source -> source: {name}/{f} -> {dst_set}/{dst_name}")
                # Pass 1 reads object set 1 from plan root (working dir); overwrite root with object-set-1 so composites match.
                if name == "object-set-1":
                    root_f = os.path.join(base, f)
                    shutil.copy2(src_f, root_f)
                    self.logger.info(f"Synced object-set-1 to plan root: {name}/{f} -> {root_f}")
                # Some SFDMU versions read object set 2+ by base name (e.g. BillingTreatment.csv); write both base and _source.
                elif not f.endswith("_source.csv"):
                    dst_base = os.path.join(dst_set, f)
                    shutil.copy2(src_f, dst_base)
                    self.logger.info(f"Synced object-set to source (base name): {name}/{f} -> {dst_base}")

    def _prepare_export_json_file(self) -> None:
        export_json_path = os.path.join(self.pathtoexportjson, EXPORT_JSON_FILENAME)
        if not os.path.isdir(self.pathtoexportjson):
            raise FileNotFoundError(f"Path to export.json is not valid: {self.pathtoexportjson}")
        if not os.path.isfile(export_json_path):
            raise FileNotFoundError(f"export.json is missing: {export_json_path}")
        
        try:
            with open(export_json_path, "r") as file:
                export_json = json.load(file)

            object_sets = self.options.get("object_sets")
            if object_sets is not None:
                if isinstance(object_sets, str):
                    object_sets = json.loads(object_sets)
                object_sets = [int(i) for i in object_sets]
                all_sets = export_json.get("objectSets", [])
                filtered = [all_sets[i] for i in object_sets if 0 <= i < len(all_sets)]
                if len(filtered) < len(object_sets):
                    raise TaskOptionsError(
                        f"object_sets {object_sets} out of range for {len(all_sets)} object sets"
                    )
                self._original_object_sets = all_sets
                export_json["objectSets"] = filtered
                self.logger.info(f"Running only object sets (0-based): {object_sets}")

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
            if getattr(self, "_original_object_sets", None) is not None:
                export_json["objectSets"] = self._original_object_sets

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
        if self.options.get("sync_objectset_source_to_source"):
            self._sync_objectset_source_to_source()
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
            cmd = LOAD_COMMAND.format(
                targetusername=self.targetusername,
                pathtoexportjson=self.pathtoexportjson,
                instanceurl=trimmed_instance_url
            )
        else:
            cmd = SCRATCHORG_LOAD_COMMAND.format(
                targetusername=self.targetusername,
                pathtoexportjson=self.pathtoexportjson,
                instanceurl=trimmed_instance_url
            )
        if self.options.get("simulation"):
            cmd += " --simulation"
        return cmd
        
    def _trim_instance_url(self, url: str) -> str:
        return url.replace("https://", "").replace("http://", "")


def _sobjects_from_export_json(export_path: str) -> list:
    """Parse export.json and return list of sobject API names (excluding excluded objects)."""
    path = os.path.join(export_path, EXPORT_JSON_FILENAME)
    with open(path, "r") as f:
        data = json.load(f)
    sobjects = []
    if "objects" in data:
        for obj in data["objects"]:
            if obj.get("excluded"):
                continue
            q = obj.get("query", "")
            m = re.search(r"\s+FROM\s+(\w+)(?:\s|$)", q, re.IGNORECASE)
            if m:
                name = m.group(1)
                if name not in sobjects:
                    sobjects.append(name)
    for obj_set in data.get("objectSets", []):
        for obj in obj_set.get("objects", []):
            if obj.get("excluded"):
                continue
            q = obj.get("query", "")
            m = re.search(r"\s+FROM\s+(\w+)(?:\s|$)", q, re.IGNORECASE)
            if m:
                name = m.group(1)
                if name not in sobjects:
                    sobjects.append(name)
    return sobjects


class TestSFDMUIdempotency(SFDXBaseTask):
    """Run an SFDMU load twice and assert record counts do not increase (idempotency).

    Use this to verify that a data plan uses SFDMU v5 composite key notation correctly:
    objects with multi-component externalIds must have a $$ column in the CSV so the
    second run matches existing records instead of inserting duplicates.
    """

    keychain_class = BaseProjectKeychain
    task_options: Dict[str, Dict[str, Any]] = {
        "pathtoexportjson": {"description": "Directory path to the export.json (same as the load task)", "required": True},
        "targetusername": {"description": "Target org username or alias", "required": False},
        "instanceurl": {"description": "Instance URL for the target org", "required": False},
        "accesstoken": {"description": "Access token for the target org", "required": False},
        "org": {"description": "Org name (for keychain resolution)", "required": False},
        "use_extraction_roundtrip": {
            "description": "If true, second load uses extract -> post_process -> load from processed dir (validates v5 re-import from extracted data)",
            "required": False,
        },
        "persist_extraction_output": {
            "description": "If true and use_extraction_roundtrip is true, write extraction and processed output to datasets/sfdmu/extractions/<plan>/<timestamp> instead of a temp dir. Omit or false to use temp dir only.",
            "required": False,
        },
    }

    def _init_options(self, kwargs: Dict[str, Any]) -> None:
        super(TestSFDMUIdempotency, self)._init_options(kwargs)
        self.env = self._get_env()
        self.keychain: Optional[BaseProjectKeychain] = None

    @property
    def keychain_cls(self):
        return self.get_keychain_class() or self.keychain_class

    def get_keychain_class(self):
        return None

    @property
    def keychain_key(self):
        return self.get_keychain_key()

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

    def _get_org_for_cli(self) -> str:
        if isinstance(self.org_config, ScratchOrgConfig):
            return self.org_config.username
        return self.options.get("targetusername") or self.org_config.access_token or self.org_config.username

    def _get_record_counts(self, sobjects: list) -> Dict[str, int]:
        org_alias = self._get_org_for_cli()
        counts = {}
        for sobject in sobjects:
            try:
                result = subprocess.run(
                    ["sf", "data", "query", "-q", f"SELECT COUNT(Id) cnt FROM {sobject}", "-o", org_alias, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.options.get("dir"),
                )
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout querying {sobject}, skipping")
                continue
            if result.returncode != 0:
                self.logger.warning(f"Query {sobject} failed: {result.stderr or result.stdout}, skipping")
                continue
            try:
                out = json.loads(result.stdout)
                records = out.get("result", {}).get("records") or []
                if records and "cnt" in records[0]:
                    counts[sobject] = int(records[0]["cnt"])
                else:
                    counts[sobject] = 0
            except (json.JSONDecodeError, KeyError, IndexError):
                self.logger.warning(f"Could not parse count for {sobject}, skipping")
        return counts

    def _run_load_once(self, plan_dir: Optional[str] = None) -> None:
        plan_dir = plan_dir or self.options.get("pathtoexportjson", "datasets/sfdmu/")
        export_path = os.path.join(plan_dir, EXPORT_JSON_FILENAME)
        if not os.path.isfile(export_path):
            raise FileNotFoundError(f"export.json not found: {export_path}")
        with open(export_path, "r") as f:
            export_json = json.load(f)
        org_data = {"name": self._get_org_for_cli(), "accessToken": self.accesstoken, "instanceUrl": self.instanceurl}
        export_json["orgs"] = [org_data]
        with open(export_path, "w") as f:
            json.dump(export_json, f, indent=2)
        trimmed = self.instanceurl.replace("https://", "").replace("http://", "")
        cmd = f"sf sfdmu run --sourceusername CSVFILE --targetusername {self._get_org_for_cli()} -p {plan_dir} --canmodify {trimmed} --noprompt --verbose"
        self.logger.info(f"Running SFDMU: {cmd}")
        result = None
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, cwd=self.options.get("dir")
            )
            if result.returncode != 0:
                self.logger.error(result.stdout)
                self.logger.error(result.stderr)
                raise CommandException(f"SFDMU load failed with exit code {result.returncode}")
            for line in result.stdout.splitlines():
                self.logger.info(line)
        finally:
            # Always clear injected org credentials from export.json
            export_json["orgs"] = []
            with open(export_path, "w") as f:
                json.dump(export_json, f, indent=2)

    def _run_extract_once(self, work_dir: str) -> None:
        """Extract from org into work_dir (must contain export.json with orgs injected)."""
        cmd = EXTRACT_COMMAND.format(sourceusername=self._get_org_for_cli(), pathtoexportjson=work_dir)
        self.logger.info(f"Running SFDMU extract: {cmd}")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=self.options.get("dir"),
        )
        if result.returncode != 0:
            self.logger.error(result.stdout)
            self.logger.error(result.stderr)
            raise CommandException(f"SFDMU extract failed with exit code {result.returncode}")
        for line in result.stdout.splitlines():
            self.logger.info(line)

    def _run_task(self) -> None:
        if "org" not in self.options or not self.options["org"]:
            self._load_keychain()
        plan_dir = self.options.get("pathtoexportjson", "datasets/sfdmu/")
        if not os.path.isdir(plan_dir):
            raise FileNotFoundError(f"Plan directory not found: {plan_dir}")
        if isinstance(self.org_config, ScratchOrgConfig):
            self.targetusername = self.org_config.username
        else:
            self.targetusername = self.options.get("targetusername") or self.org_config.access_token or getattr(self.org_config, "username", None)
        self.accesstoken = self.options.get("accesstoken") or self.org_config.access_token
        self.instanceurl = self.options.get("instanceurl") or self.org_config.instance_url
        org_identifier = self.options.get("org") or getattr(self.org_config, "name", None) or self._get_org_for_cli()
        self.logger.info(f"Using org for source and target: {org_identifier}")
        sobjects = _sobjects_from_export_json(plan_dir)
        if not sobjects:
            raise TaskOptionsError("No sobjects found in export.json")
        self.logger.info("First run: load data into org")
        self._run_load_once()
        counts_after_first = self._get_record_counts(sobjects)
        use_roundtrip = str(self.options.get("use_extraction_roundtrip", "")).lower() in {"1", "true", "yes"}
        if use_roundtrip:
            self.logger.info("Extraction roundtrip: extract -> post-process -> load from processed (validates v5 re-import)")
            persist_output = str(self.options.get("persist_extraction_output", "")).lower() in {"1", "true", "yes"}
            if persist_output:
                from datetime import datetime
                plan_name = os.path.basename(os.path.normpath(plan_dir))
                base = os.path.normpath(os.path.join(os.path.dirname(plan_dir), "..", "..", "extractions", plan_name))
                timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
                work_dir = os.path.join(base, timestamp)
                os.makedirs(work_dir, exist_ok=True)
                self.logger.info(f"Writing extraction and processed output to: {work_dir}")
                use_temp = False
            else:
                work_dir = tempfile.mkdtemp(prefix="sfdmu_idem_extract_")
                use_temp = True
            try:
                export_src = os.path.join(plan_dir, EXPORT_JSON_FILENAME)
                export_dst = os.path.join(work_dir, EXPORT_JSON_FILENAME)
                shutil.copy2(export_src, export_dst)
                with open(export_dst, "r") as f:
                    export_json = json.load(f)
                export_json["orgs"] = [{"name": self._get_org_for_cli(), "accessToken": self.accesstoken, "instanceUrl": self.instanceurl}]
                with open(export_dst, "w") as f:
                    json.dump(export_json, f, indent=2)
                self._run_extract_once(work_dir)
                processed_dir = os.path.join(work_dir, "processed")
                os.makedirs(processed_dir, exist_ok=True)
                run_post_process_script(
                    work_dir, plan_dir, processed_dir,
                    cwd=self.options.get("dir"), logger=self.logger,
                )
                shutil.copy2(export_src, os.path.join(processed_dir, EXPORT_JSON_FILENAME))
                self.logger.info("Second run: load from post-processed extraction (should not add records)")
                self._run_load_once(processed_dir)
            finally:
                # Always clear credentials from work_dir/export.json (persist mode leaves dir on disk)
                if work_dir and os.path.isdir(work_dir):
                    export_in_work = os.path.join(work_dir, EXPORT_JSON_FILENAME)
                    if os.path.isfile(export_in_work):
                        try:
                            with open(export_in_work, "r") as f:
                                ej = json.load(f)
                            ej["orgs"] = []
                            with open(export_in_work, "w") as f:
                                json.dump(ej, f, indent=2)
                        except Exception as e:
                            self.logger.warning(f"Could not clear credentials from {export_in_work}: {e}")
                    if use_temp:
                        shutil.rmtree(work_dir, ignore_errors=True)
                        self.logger.info("Removed extraction roundtrip temp directory.")
        else:
            self.logger.info("Second run: idempotent re-run from source (should not add records)")
            self._run_load_once()
        counts_after_second = self._get_record_counts(sobjects)
        failures = []
        for sobject in sobjects:
            c1 = counts_after_first.get(sobject, 0)
            c2 = counts_after_second.get(sobject, 0)
            if c2 > c1:
                failures.append(f"{sobject}: count increased from {c1} to {c2} (not idempotent)")
            else:
                self.logger.info(f"  {sobject}: {c1} -> {c2} (ok)")
        if failures:
            self.logger.error("Idempotency check failed:")
            for msg in failures:
                self.logger.error(f"  {msg}")
            raise CommandException("Re-run added records. Ensure composite-key objects have a $$ column in the CSV (SFDMU v5).")
        self.logger.info("Idempotency check passed: no record count increase on second run.")


class ExtractSFDMUData(SFDXBaseTask):
    """Extract data from a Salesforce org into CSV files using SFDMU.

    Uses the same export.json as LoadSFDMUData but reverses the direction:
    the org becomes the source and CSVFILE becomes the target.  SFDMU writes
    one CSV per queried object into the plan directory (or a separate output
    directory when ``output_dir`` is specified).

    Relationship traversal fields in the SOQL queries (e.g.
    Product.StockKeepingUnit) are resolved during extraction, producing
    portable CSVs with human-readable names/codes instead of raw Salesforce
    Ids.
    """

    keychain_class = BaseProjectKeychain
    task_options: Dict[str, Dict[str, Any]] = {
        "pathtoexportjson": {
            "description": "Directory path containing the export.json to use for extraction",
            "required": True
        },
        "sourceusername": {
            "description": "Username or alias of the org to extract from.  Defaults to the current CCI org.",
            "required": False
        },
        "output_dir": {
            "description": (
                "Directory where extracted CSVs will be written.  "
                "If omitted, SFDMU writes CSVs into the plan directory itself.  "
                "When set, the export.json is copied to a temp working directory "
                "and SFDMU writes its output there, then CSVs are moved to output_dir."
            ),
            "required": False
        },
        "object_sets": {
            "description": "Optional list of 0-based object set indices to extract (e.g. [0] for Pass 1 only).  If omitted, all object sets are extracted.",
            "required": False
        },
        "run_post_process": {
            "description": "If True (default), run post_process_extraction.py after extraction so output is re-import-ready (adds $$ composite key columns, normalizes headers). Processed CSVs are written to <output_dir>/processed/.",
            "required": False
        }
    }

    def _init_options(self, kwargs: Dict[str, Any]) -> None:
        super(ExtractSFDMUData, self)._init_options(kwargs)
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

    def _prepare_working_dir(self) -> str:
        """Create a temporary working directory with a copy of the export.json.

        SFDMU writes extracted CSVs into the directory that contains
        export.json.  To avoid clobbering the version-controlled plan CSVs we
        copy only the export.json to a temp dir and point SFDMU there.
        """
        plan_dir = self.options.get("pathtoexportjson", "datasets/sfdmu/")
        export_json_path = os.path.join(plan_dir, EXPORT_JSON_FILENAME)
        if not os.path.isfile(export_json_path):
            raise FileNotFoundError(f"export.json not found: {export_json_path}")

        work_dir = tempfile.mkdtemp(prefix="sfdmu_extract_")
        shutil.copy2(export_json_path, os.path.join(work_dir, EXPORT_JSON_FILENAME))
        self.logger.info(f"Created extraction working directory: {work_dir}")
        return work_dir

    def _prepare_export_json(self, work_dir: str) -> None:
        """Inject org credentials and optional object_sets filter."""
        export_json_path = os.path.join(work_dir, EXPORT_JSON_FILENAME)
        with open(export_json_path, "r") as f:
            export_json = json.load(f)

        object_sets = self.options.get("object_sets")
        if object_sets is not None:
            if isinstance(object_sets, str):
                object_sets = json.loads(object_sets)
            object_sets = [int(i) for i in object_sets]
            all_sets = export_json.get("objectSets", [])
            filtered = [all_sets[i] for i in object_sets if 0 <= i < len(all_sets)]
            if len(filtered) < len(object_sets):
                raise TaskOptionsError(
                    f"object_sets {object_sets} out of range for {len(all_sets)} object sets"
                )
            export_json["objectSets"] = filtered
            self.logger.info(f"Extracting only object sets (0-based): {object_sets}")

        # For extraction the source is the org; inject auth so SFDMU can connect
        org_data = {
            "name": self.sourceusername,
            "accessToken": self.accesstoken,
            "instanceUrl": self.instanceurl,
        }
        export_json["orgs"] = [org_data]

        with open(export_json_path, "w") as f:
            json.dump(export_json, f, indent=2)

        self.logger.info(f"Prepared export.json for extraction in {work_dir}")

    def _collect_output(self, work_dir: str) -> str:
        """Move extracted CSVs from work_dir to the output_dir (or plan dir).

        Returns the final output directory path.
        """
        output_dir = self.options.get("output_dir")
        plan_dir = self.options.get("pathtoexportjson", "datasets/sfdmu/")
        if not output_dir:
            # Default: timestamped subdirectory under datasets/sfdmu/extractions/<plan_name>/
            plan_name = os.path.basename(os.path.normpath(plan_dir))
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
            output_dir = os.path.join(
                os.path.dirname(plan_dir), "..", "..", "extractions", plan_name, timestamp
            )
            output_dir = os.path.normpath(output_dir)

        os.makedirs(output_dir, exist_ok=True)

        csv_count = 0
        for fname in os.listdir(work_dir):
            if fname.endswith(".csv"):
                src = os.path.join(work_dir, fname)
                dst = os.path.join(output_dir, fname)
                shutil.move(src, dst)
                csv_count += 1
                self.logger.info(f"  {fname}")

        self.logger.info(f"Collected {csv_count} CSV files to {output_dir}")
        return output_dir

    def _run_task(self) -> None:
        work_dir = None
        try:
            # Resolve org credentials
            if "org" not in self.options or not self.options["org"]:
                self._load_keychain()

            plan_dir = self.options.get("pathtoexportjson", "datasets/sfdmu/")
            if not os.path.isdir(plan_dir):
                raise FileNotFoundError(f"Plan directory not found: {plan_dir}")

            if isinstance(self.org_config, ScratchOrgConfig):
                self.sourceusername = self.org_config.username
            else:
                self.sourceusername = self.options.get("sourceusername") or self.org_config.access_token

            self.accesstoken = self.org_config.access_token
            self.instanceurl = self.org_config.instance_url

            # Prepare isolated working directory
            work_dir = self._prepare_working_dir()
            self._prepare_export_json(work_dir)

            # Build and run SFDMU extract command
            cmd = EXTRACT_COMMAND.format(
                sourceusername=self.sourceusername,
                pathtoexportjson=work_dir,
            )
            self.logger.info(f"Executing extraction: {cmd}")
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=self.options.get("dir"),
            )

            for line in result.stdout.splitlines():
                self.logger.info(line)

            if result.returncode != 0:
                self.logger.error(f"SFDMU extraction failed (exit {result.returncode})")
                self.logger.error(f"STDERR: {result.stderr}")
                raise CommandException(
                    f"SFDMU extraction failed with exit code {result.returncode}"
                )

            # Move CSVs to final destination
            output_dir = self._collect_output(work_dir)
            self.logger.info(f"Extraction complete. Output: {output_dir}")
            self.return_values = {"output_dir": output_dir}

            # Optionally run post-process so output is re-import-ready ($$ columns, header normalization)
            raw_run_post_process = self.options.get("run_post_process")
            if raw_run_post_process is None:
                run_post_process = True  # default when option is absent
            else:
                run_post_process = str(raw_run_post_process).strip().lower() not in {"0", "false", "no"}
            if run_post_process:
                processed_dir = os.path.join(output_dir, "processed")
                os.makedirs(processed_dir, exist_ok=True)
                run_post_process_script(
                    output_dir, plan_dir, processed_dir,
                    cwd=self.options.get("dir"), logger=self.logger,
                )
                export_src = os.path.join(plan_dir, EXPORT_JSON_FILENAME)
                shutil.copy2(export_src, os.path.join(processed_dir, EXPORT_JSON_FILENAME))
                self.return_values["processed_dir"] = processed_dir
                self.logger.info(f"Post-process complete. Re-import-ready CSVs: {processed_dir}")

        except Exception as e:
            self.logger.error(f"Extraction error: {e}")
            raise
        finally:
            if work_dir and os.path.isdir(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)
                self.logger.info("Cleaned up extraction working directory.")