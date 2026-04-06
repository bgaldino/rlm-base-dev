"""
BRE (Business Rules Engine) Rule Library export utility for CumulusCI.

Provides a CCI task for exporting BRE Rule Library data from a Salesforce org:
  - ExportBRE: Export Rule Library hierarchy (Definition, DefVersion, Library, Version)
               from a source org to a local CSV directory, plus retrieve the actual rule
               definitions as metadata (RuleLibraryDefinition metadata type).

The BRE Rule Library has a dual nature:
  - DATA objects: RuleLibrary, RuleLibraryVersion, Ruleset (container/versioning/runtime)
  - METADATA: RuleLibraryDefinition (the actual rule content — conditions, actions, logic)

Object hierarchy (data):
  RuleLibraryDefinition (also a metadata type)
    ├── RuleLibraryDefVersion
    └── RuleLibrary
          └── RuleLibraryVersion
                └── Ruleset (published/compiled rules, key prefix 9Qw)
                      ↑ referenced by FulfillmentStepDefinition.ExecuteOnRuleId,
                        ProductFulfillmentScenario.ScenarioRuleId,
                        ProductFulfillmentDecompRule.ExecuteOnRuleId
"""

import csv
import glob
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from typing import Any, Dict, List, Optional

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


# ===================================================================
# ExportBRE
# ===================================================================

class ExportBRE(BaseSalesforceTask):
    """Export BRE Rule Library data and metadata from an org.

    Exports:
      1. Data (via SOQL → CSV):
         - RuleLibraryDefinition
         - RuleLibraryDefVersion
         - RuleLibrary
         - RuleLibraryVersion
      2. Metadata (via sf project retrieve):
         - RuleLibraryDefinition metadata type (the actual rule definitions)

    The data CSVs capture the container/versioning structure.
    The metadata retrieval captures the actual rule content (conditions, actions, logic).
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "api_name": {
            "description": (
                "ApiName of the RuleLibrary to export (e.g. DRORuleLibraryGeneric). "
                "If omitted, exports ALL RuleLibrary records."
            ),
            "required": False,
        },
        "output_dir": {
            "description": "Directory to write CSV exports and retrieved metadata",
            "required": True,
        },
        "api_version": {
            "description": "Override Salesforce API version (e.g. 66.0)",
            "required": False,
        },
        "retrieve_metadata": {
            "description": "If true (default), also retrieve RuleLibraryDefinition metadata via sf CLI",
            "required": False,
        },
    }

    # -- Auth properties (from CCI org config) -------------------------

    @property
    def _access_token(self) -> str:
        return self.org_config.access_token

    @property
    def _instance_url(self) -> str:
        return self.org_config.instance_url

    @property
    def _api_version(self) -> str:
        if self.options.get("api_version"):
            return str(self.options["api_version"])
        return (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _query_url(self) -> str:
        return f"{self._instance_url}/services/data/v{self._api_version}/query"

    # -- REST helpers --------------------------------------------------

    def _soql_query(self, soql: str) -> List[dict]:
        """Execute a SOQL query and return all records (handles pagination)."""
        records: List[dict] = []
        resp = requests.get(self._query_url, headers=self._headers, params={"q": soql})
        if resp.status_code != 200:
            self.logger.error(f"SOQL query failed ({resp.status_code}): {resp.text}")
            return records
        body = resp.json()
        records.extend(body.get("records", []))
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            url = f"{self._instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(url, headers=self._headers)
            if resp.status_code != 200:
                self.logger.error(f"SOQL pagination failed ({resp.status_code}): {resp.text}")
                break
            body = resp.json()
            records.extend(body.get("records", []))
        return records

    def _describe_object(self, obj_name: str) -> Optional[dict]:
        """Describe an sObject and return the full describe result, or None on failure."""
        url = f"{self._instance_url}/services/data/v{self._api_version}/sobjects/{obj_name}/describe"
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 200:
            return resp.json()
        self.logger.warning(f"Describe {obj_name} failed ({resp.status_code}): {resp.text}")
        return None

    def _get_queryable_fields(self, describe: dict, exclude_compounds: bool = True) -> List[str]:
        """Extract queryable field API names from a describe result.

        Excludes compound fields (address, location) by default since they
        cannot appear in SOQL SELECT.
        """
        compound_types = {"address", "location"}
        fields = []
        for f in describe.get("fields", []):
            if not f.get("type"):
                continue
            if not f.get("queryable", True):
                continue
            if f.get("deprecatedAndHidden", False):
                continue
            if exclude_compounds and f["type"] in compound_types:
                continue
            fields.append(f["name"])
        return sorted(fields)

    # -- CSV helpers ---------------------------------------------------

    @staticmethod
    def _get_field_value(record: dict, dotted_field: str):
        """Extract a possibly nested field value (e.g. 'RuleLibraryDefinition.DeveloperName')."""
        if "." in dotted_field:
            parent, child = dotted_field.split(".", 1)
            parent_obj = record.get(parent)
            if parent_obj and isinstance(parent_obj, dict):
                return parent_obj.get(child, "")
            return ""
        return record.get(dotted_field, "")

    @staticmethod
    def _write_csv(path: str, fieldnames: List[str], rows: List[List]) -> None:
        """Write rows (as value lists) to a CSV file."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(fieldnames)
            for row in rows:
                writer.writerow(row)

    def _export_query(self, soql: str, fields: List[str], dest: str) -> List[dict]:
        """Run a SOQL query, write results as CSV, and return raw records."""
        label = os.path.basename(dest)
        self.logger.info(f"Exporting {label}...")
        records = self._soql_query(soql)
        self.logger.info(f"  {len(records)} records fetched")
        rows = [[self._get_field_value(rec, f) for f in fields] for rec in records]
        self._write_csv(dest, fields, rows)
        return records

    # -- Metadata retrieval --------------------------------------------

    def _retrieve_metadata(self, developer_names: List[str], output_dir: str) -> None:
        """Retrieve RuleLibraryDefinition metadata, convert to source format, and place in unpackaged/post_dro/.

        Steps:
          1. Build a package.xml manifest for the target RuleLibraryDefinition members
          2. Retrieve mdapi-format metadata into a temp directory
          3. Unzip the retrieved bundle
          4. Convert from mdapi format to source format via sf project convert mdapi
          5. Copy the converted source into unpackaged/post_dro/
        """
        username = getattr(self.org_config, "username", None)
        if not username:
            self.logger.warning(
                "No org username available for sf CLI retrieve. "
                "Skipping metadata retrieval."
            )
            return

        work_dir = tempfile.mkdtemp(prefix="bre_metadata_")
        try:
            self._do_retrieve_metadata(developer_names, output_dir, work_dir, username)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _do_retrieve_metadata(
        self, developer_names: List[str], output_dir: str, work_dir: str, username: str
    ) -> None:
        mdapi_dir = os.path.join(work_dir, "mdapi")
        os.makedirs(mdapi_dir)

        # 1. Build package.xml
        members_xml = "\n".join(f"        <members>{n}</members>" for n in sorted(developer_names))
        package_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
{members_xml}
        <name>RuleLibraryDefinition</name>
    </types>
    <version>{self._api_version}</version>
</Package>"""
        manifest_path = os.path.join(mdapi_dir, "package.xml")
        with open(manifest_path, "w") as f:
            f.write(package_xml)

        self.logger.info(f"Retrieving RuleLibraryDefinition metadata for: {', '.join(developer_names)}")

        # 2. Retrieve into the mdapi temp dir
        cmd = [
            "sf", "project", "retrieve", "start",
            "--manifest", manifest_path,
            "--target-org", username,
            "--target-metadata-dir", mdapi_dir,
        ]
        self.logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            self.logger.warning(f"Metadata retrieval failed (exit {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().splitlines():
                    self.logger.warning(f"  {line}")
            if result.stdout:
                for line in result.stdout.strip().splitlines():
                    self.logger.warning(f"  {line}")
            return

        self.logger.info("Metadata retrieved successfully")

        # 3. Unzip any zip files produced by the retrieve
        for zip_path in glob.glob(os.path.join(mdapi_dir, "*.zip")):
            self.logger.info(f"Unzipping {os.path.basename(zip_path)}...")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(mdapi_dir)
            os.remove(zip_path)

        # Also save a raw copy to output_dir for inspection
        raw_metadata_dir = os.path.join(output_dir, "metadata_mdapi")
        if os.path.exists(raw_metadata_dir):
            shutil.rmtree(raw_metadata_dir)
        shutil.copytree(mdapi_dir, raw_metadata_dir)
        self.logger.info(f"Raw mdapi metadata saved to {raw_metadata_dir}")

        # Log what was retrieved
        for root, dirs, files in os.walk(mdapi_dir):
            for fname in files:
                rel = os.path.relpath(os.path.join(root, fname), mdapi_dir)
                self.logger.info(f"  Retrieved: {rel}")

        # 4. Convert mdapi → source format
        source_dir = os.path.join(work_dir, "source")
        os.makedirs(source_dir)
        convert_cmd = [
            "sf", "project", "convert", "mdapi",
            "--root-dir", mdapi_dir,
            "--output-dir", source_dir,
        ]
        self.logger.info(f"Converting to source format: {' '.join(convert_cmd)}")
        convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)

        if convert_result.returncode != 0:
            self.logger.warning(f"Source conversion failed (exit {convert_result.returncode})")
            if convert_result.stderr:
                for line in convert_result.stderr.strip().splitlines():
                    self.logger.warning(f"  {line}")
            if convert_result.stdout:
                for line in convert_result.stdout.strip().splitlines():
                    self.logger.warning(f"  {line}")
            self.logger.info(
                f"Raw mdapi metadata is still available at {raw_metadata_dir}. "
                "You can convert manually with: sf project convert mdapi --root-dir <mdapi_dir> --output-dir <dest>"
            )
            return

        # 5. Copy converted source into unpackaged/post_dro/
        post_dro_dir = os.path.join(os.getcwd(), "unpackaged", "post_dro")
        os.makedirs(post_dro_dir, exist_ok=True)

        # The converted output lives under source/main/default/ (or similar).
        # Walk and copy all metadata type folders into post_dro.
        copied = 0
        for root, dirs, files in os.walk(source_dir):
            for fname in files:
                src_path = os.path.join(root, fname)
                # Find the path relative to the first "default" or "main/default" directory
                rel = os.path.relpath(src_path, source_dir)
                # Strip the leading directory structure (e.g., main/default/)
                parts = rel.split(os.sep)
                # Find where the metadata type dir starts (skip main/default prefix)
                start = 0
                for i, p in enumerate(parts):
                    if p == "default":
                        start = i + 1
                        break
                if start == 0:
                    # No main/default found; use the path as-is
                    dest_rel = rel
                else:
                    dest_rel = os.path.join(*parts[start:]) if start < len(parts) else rel

                dest_path = os.path.join(post_dro_dir, dest_rel)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                copied += 1
                self.logger.info(f"  -> unpackaged/post_dro/{dest_rel}")

        if copied:
            self.logger.info(f"Copied {copied} files to unpackaged/post_dro/")
        else:
            self.logger.warning("No source files found after conversion")

    # -- Ruleset export ------------------------------------------------

    def _export_rulesets(self, rlv_ids: set, output_dir: str) -> None:
        """Discover Ruleset fields via describe and export all Rulesets linked to the RuleLibraryVersions.

        Ruleset is a system-managed object (key prefix 9Qw) that represents the
        published/compiled rules. Its schema is not in the ERD, so we describe it
        at runtime to discover queryable fields.
        """
        if not rlv_ids:
            self.logger.info("No RuleLibraryVersion IDs; skipping Ruleset export.")
            return

        describe = self._describe_object("Ruleset")
        if not describe:
            self.logger.warning(
                "Ruleset object not available in this org (describe failed). "
                "Skipping Ruleset export."
            )
            return

        # Discover all queryable fields
        all_fields = self._get_queryable_fields(describe)
        if not all_fields:
            self.logger.warning("No queryable fields found on Ruleset.")
            return

        # Log the discovered fields for visibility
        self.logger.info(f"Ruleset describe: {len(all_fields)} queryable fields discovered")

        # Write the describe to a JSON file for reference
        describe_path = os.path.join(output_dir, "Ruleset.describe.json")
        field_summary = [
            {
                "name": f["name"],
                "type": f["type"],
                "label": f.get("label", ""),
                "referenceTo": f.get("referenceTo", []),
                "relationshipName": f.get("relationshipName"),
            }
            for f in describe.get("fields", [])
        ]
        with open(describe_path, "w") as fp:
            json.dump(field_summary, fp, indent=2)
        self.logger.info(f"  Wrote field describe to {describe_path}")

        # Find a relationship field that links Ruleset back to RuleLibraryVersion
        # Look for reference fields that point to RuleLibraryVersion
        rlv_ref_field = None
        for f in describe.get("fields", []):
            if f.get("type") == "reference" and "RuleLibraryVersion" in (f.get("referenceTo") or []):
                rlv_ref_field = f["name"]
                self.logger.info(f"  Found RuleLibraryVersion reference field: {rlv_ref_field}")
                break

        # Build the query — filter by RuleLibraryVersion if we found the FK,
        # otherwise export all Rulesets (user can filter later)
        fields_csv = ", ".join(all_fields)
        dest = os.path.join(output_dir, "Ruleset.csv")
        if rlv_ref_field:
            # Chunk rlv_ids to stay within SOQL IN-clause limits
            chunk_size = 200
            rlv_id_list = list(rlv_ids)
            all_records: list = []
            for i in range(0, len(rlv_id_list), chunk_size):
                chunk = rlv_id_list[i : i + chunk_size]
                id_filter = ",".join(f"'{i}'" for i in chunk)
                soql = f"SELECT {fields_csv} FROM Ruleset WHERE {rlv_ref_field} IN ({id_filter})"
                all_records.extend(self._soql_query(soql))
            self.logger.info(f"  {len(all_records)} Ruleset records fetched")
            rows = [[self._get_field_value(rec, f) for f in all_fields] for rec in all_records]
            self._write_csv(dest, all_fields, rows)
        else:
            self.logger.info("  No RuleLibraryVersion FK found on Ruleset; exporting all Rulesets")
            soql = f"SELECT {fields_csv} FROM Ruleset"
            self._export_query(soql=soql, fields=all_fields, dest=dest)

        # Check for child relationships on Ruleset (e.g. RulesetRule, RulesetCondition)
        child_relations = [
            cr for cr in describe.get("childRelationships", [])
            if cr.get("childSObject") and cr.get("relationshipName")
            and not cr["childSObject"].startswith("AttachedContentDocument")
            and not cr["childSObject"].startswith("ContentDocument")
            and not cr["childSObject"].endswith("History")
            and not cr["childSObject"].endswith("Feed")
            and not cr["childSObject"].endswith("Share")
        ]
        if child_relations:
            self.logger.info(f"  Ruleset has {len(child_relations)} child relationships:")
            for cr in child_relations:
                self.logger.info(f"    - {cr['childSObject']}.{cr.get('field', '?')} ({cr['relationshipName']})")

    # -- Main task -----------------------------------------------------

    def _run_task(self):
        api_name = self.options.get("api_name")
        output_dir = self.options["output_dir"]
        retrieve_metadata = str(self.options.get("retrieve_metadata", "true")).lower() != "false"
        os.makedirs(output_dir, exist_ok=True)

        if api_name:
            self.logger.info(f"Exporting BRE Rule Library '{api_name}' to {output_dir}")
        else:
            self.logger.info(f"Exporting ALL BRE Rule Libraries to {output_dir}")

        # ---------------------------------------------------------------
        # Phase 1: Data export (SOQL → CSV)
        # ---------------------------------------------------------------
        self.logger.info("--- Phase 1: Data export (SOQL → CSV) ---")

        # 1. RuleLibrary — start here to discover the RuleLibraryDefinitionId
        rl_fields = [
            "Id", "Name", "ApiName", "ContextDefinitionName",
            "RuleLibraryDefinitionId", "RuleLibraryDefinition.DeveloperName",
            "Status", "UsageType",
        ]
        rl_where = f"WHERE ApiName = '{api_name.replace(chr(39), chr(92) + chr(39))}'" if api_name else ""
        rl_records = self._export_query(
            soql=f"SELECT {', '.join(rl_fields)} FROM RuleLibrary {rl_where} ORDER BY ApiName",
            fields=rl_fields,
            dest=os.path.join(output_dir, "RuleLibrary.csv"),
        )

        if not rl_records:
            self.logger.warning("No RuleLibrary records found. Export complete (empty).")
            return

        # Collect parent RuleLibraryDefinition IDs, DeveloperNames, and RuleLibrary IDs
        rld_ids = set()
        rld_dev_names = set()
        rl_ids = set()
        for rec in rl_records:
            rld_id = rec.get("RuleLibraryDefinitionId")
            if rld_id:
                rld_ids.add(rld_id)
            dev_name = self._get_field_value(rec, "RuleLibraryDefinition.DeveloperName")
            if dev_name:
                rld_dev_names.add(dev_name)
            rl_ids.add(rec["Id"])

        # 2. RuleLibraryDefinition
        rld_fields = ["Id", "DeveloperName", "Language", "MasterLabel"]
        if not rld_ids:
            self.logger.warning("No RuleLibraryDefinitionId found on any RuleLibrary record. Skipping dependent exports.")
            return
        rld_id_filter = ",".join(f"'{i}'" for i in rld_ids)
        rld_records = self._export_query(
            soql=f"SELECT {', '.join(rld_fields)} FROM RuleLibraryDefinition WHERE Id IN ({rld_id_filter})",
            fields=rld_fields,
            dest=os.path.join(output_dir, "RuleLibraryDefinition.csv"),
        )
        # Also capture DeveloperNames from the direct query
        for rec in rld_records:
            dev_name = rec.get("DeveloperName")
            if dev_name:
                rld_dev_names.add(dev_name)

        # 3. RuleLibraryDefVersion
        rldv_fields = [
            "Id", "DeveloperName", "Language", "MasterLabel",
            "RuleLibraryDefinitionId", "RuleLibraryDefinition.DeveloperName",
        ]
        self._export_query(
            soql=f"SELECT {', '.join(rldv_fields)} FROM RuleLibraryDefVersion WHERE RuleLibraryDefinitionId IN ({rld_id_filter})",
            fields=rldv_fields,
            dest=os.path.join(output_dir, "RuleLibraryDefVersion.csv"),
        )

        # 4. RuleLibraryVersion
        rl_id_filter = ",".join(f"'{i}'" for i in rl_ids)
        rlv_fields = [
            "Id", "Name", "ApiName", "ContextDefinitionName", "Description",
            "RuleLibraryId", "RuleLibrary.ApiName",
            "RuleLibraryDefVersionId", "RuleLibraryDefVersion.DeveloperName",
            "VersionNumber", "StartDateTime", "EndDateTime", "Status",
        ]
        rlv_records = self._export_query(
            soql=f"SELECT {', '.join(rlv_fields)} FROM RuleLibraryVersion WHERE RuleLibraryId IN ({rl_id_filter}) ORDER BY RuleLibrary.ApiName, VersionNumber",
            fields=rlv_fields,
            dest=os.path.join(output_dir, "RuleLibraryVersion.csv"),
        )
        rlv_ids = {rec["Id"] for rec in rlv_records if rec.get("Id")}

        # ---------------------------------------------------------------
        # Phase 2: Ruleset export (published/compiled rules)
        # ---------------------------------------------------------------
        self.logger.info("--- Phase 2: Ruleset data export ---")
        self._export_rulesets(rlv_ids, output_dir)

        # ---------------------------------------------------------------
        # Phase 3: Metadata retrieval (the actual rule definitions)
        # ---------------------------------------------------------------
        if retrieve_metadata and rld_dev_names:
            self.logger.info("--- Phase 3: Metadata retrieval (rule definitions) ---")
            self._retrieve_metadata(sorted(rld_dev_names), output_dir)
        elif not rld_dev_names:
            self.logger.warning("No RuleLibraryDefinition DeveloperNames found; skipping metadata retrieval.")

        self.logger.info(f"BRE Rule Library export complete -> {output_dir}")
