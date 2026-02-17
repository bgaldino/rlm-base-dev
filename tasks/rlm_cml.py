"""
Consolidated CML (Constraint Modeling Language) utility for CumulusCI.

Provides three CCI tasks for managing constraint model data:
  - ExportCML:   Export constraint model metadata + blob from a Salesforce org
  - ImportCML:   Import constraint model metadata + blob into a Salesforce org
  - ValidateCML: Validate CML file structure and ESC association coverage

Replaces the standalone scripts:
  - scripts/cml/export_cml.py  (DEPRECATED)
  - scripts/cml/import_cml.py  (DEPRECATED)
  - scripts/cml/validate_cml.py (DEPRECATED)
"""

import base64
import csv
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    BaseSalesforceTask = object
    TaskOptionsError = Exception

# ---------------------------------------------------------------------------
# Salesforce object ID prefix -> object name mapping for polymorphic
# ReferenceObjectId resolution on ExpressionSetConstraintObj
# ---------------------------------------------------------------------------
ID_PREFIX_MAP = {
    "01t": "Product2",
    "11B": "ProductClassification",
    "0dS": "ProductRelatedComponent",
}

# ---------------------------------------------------------------------------
# CML validation regex patterns
# ---------------------------------------------------------------------------
TYPE_RE = re.compile(
    r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*([A-Za-z_][A-Za-z0-9_]*))?\s*(\{|;)\s*$"
)
DEFINE_RE = re.compile(r"^\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s+\[(.*)\]\s*$")
RELATION_RE = re.compile(
    r"^\s*relation\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)"
)
EXTERN_RE = re.compile(
    r"^\s*(?:@\(.*\)\s*)*extern\s+([A-Za-z0-9_()]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(=\s*[^;]+)?;"
)
CONSTRAINT_LINE_RE = re.compile(
    r"^\s*(?:@\(.*\)\s*)*(constraint|message|preference|require|exclude|rule|setdefault)\b"
)
ORDER_RE = re.compile(r"order\s*\(([^)]*)\)")
FIELD_RE = re.compile(
    r"^\s*(?:@\(.*\)\s*)*(string|int|boolean|decimal(?:\(\d+\))?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+);"
)
DEFAULT_RE = re.compile(r"defaultValue\s*=\s*(\"[^\"]*\"|[^,\)]+)")
RANGE_RE = re.compile(r"\[\s*(\d+)\s*\.\.\s*(\d+)\s*\]")
ANNOTATION_KEY_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=")
ANNOTATION_KV_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\"[^\"]*\"|[^,\)]+)"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CARDINALITY_RE = re.compile(r"\[\s*(\d+)\s*(?:\.\.\s*(\d+))?\s*\]")
HEADER_DECL_RE = re.compile(r"^\s*(define|property|extern)\b")

# ---------------------------------------------------------------------------
# CML annotation dictionaries
# ---------------------------------------------------------------------------
SUPPORTED_ANNOTATIONS = {
    "type": {
        "sequence", "groupBy", "peelable", "sharingCount", "source", "split",
        "virtual", "minInstanceQty", "maxInstanceQty",
        "computeDomainBeforeRelation", "computeDomainBeforeAttribute",
        "computeDomainBeforeAllAttributesAndRelations",
    },
    "port": {
        "closeRelation", "compNumberVar", "configurable",
        "disableCardinalityConstraint", "domainComputation", "filterExpression",
        "generic", "goal", "goalFactory", "noneLeafCardVar", "orderBy",
        "domainOrder", "propagateUp", "relatedAttributes", "relatedRelations",
        "sequence", "sharing", "singleton", "source", "sourceAttribute",
        "sourceContextNode", "sharingExpression", "sharingClass",
        "sharingSource", "readOnly", "allowNewInstance",
        "removeAssetWithZeroQuantity",
    },
    "attribute": {
        "allowOverride", "configurable", "contextPath", "defaultValue",
        "domainComputation", "goal", "goalFactory", "nullAssignable",
        "peelable", "relatedAttributes", "relatedRelations", "sequence",
        "setDefault", "source", "sourceAttribute", "strategy", "tagName",
        "domainScope", "attributeSource", "productGroup",
        "skipParentAttributeValidation",
    },
    "extern": {"contextPath", "tagName"},
    "constraint": {
        "sequence", "abort", "active", "endDate", "startDate", "targetType",
        "skipValidation",
    },
}

BOOLEAN_ANNOTATIONS = {
    "allowOverride", "configurable", "domainComputation", "nullAssignable",
    "setDefault", "closeRelation", "allowNewInstance",
    "disableCardinalityConstraint", "generic", "noneLeafCardVar",
    "propagateUp", "readOnly", "sharing", "singleton", "abort", "active",
    "skipValidation", "peelable",
}

INTEGER_ANNOTATIONS = {
    "sequence", "sharingCount", "maxInstanceQty", "minInstanceQty",
    "productGroup",
}

ENUM_ANNOTATIONS = {
    "split": {"true", "false", "none"},
}


# ===================================================================
# CMLBaseTask -- shared utilities for Export, Import, and Validate
# ===================================================================

class CMLBaseTask(BaseSalesforceTask):
    """Base class providing shared Salesforce REST and CSV utilities.

    Extends BaseSalesforceTask so CCI provides org config and the --org CLI flag.
    """

    task_options: Dict[str, Dict[str, Any]] = {
        "api_version": {
            "description": "Override Salesforce API version (e.g. 66.0)",
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

    def soql_query(self, soql: str) -> List[dict]:
        """Execute a SOQL query and return all records (handles pagination)."""
        records = []
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

    def create_record(self, obj_name: str, record: dict) -> Optional[str]:
        """POST a new sObject record. Returns the new record Id or None."""
        url = f"{self._instance_url}/services/data/v{self._api_version}/sobjects/{obj_name}/"
        payload = {k: v for k, v in record.items() if k != "Id"}
        resp = requests.post(url, headers=self._headers, json=payload)
        if resp.status_code == 201:
            new_id = resp.json()["id"]
            self.logger.info(f"Created {obj_name} -> {record.get('Name', record.get('ApiName', new_id))}")
            return new_id
        self.logger.error(f"Failed to create {obj_name}: {resp.status_code} - {resp.text}")
        return None

    def update_record(self, obj_name: str, record_id: str, data: dict) -> bool:
        """PATCH an existing sObject record. Returns True on success."""
        url = f"{self._instance_url}/services/data/v{self._api_version}/sobjects/{obj_name}/{record_id}"
        resp = requests.patch(url, headers=self._headers, json=data)
        if resp.status_code in (200, 204):
            return True
        self.logger.error(f"Failed to update {obj_name}/{record_id}: {resp.status_code} - {resp.text}")
        return False

    def delete_record(self, obj_name: str, record_id: str) -> bool:
        """DELETE an sObject record. Returns True on success."""
        url = f"{self._instance_url}/services/data/v{self._api_version}/sobjects/{obj_name}/{record_id}"
        resp = requests.delete(url, headers=self._headers)
        if resp.status_code in (200, 204):
            return True
        self.logger.error(f"Failed to delete {obj_name}/{record_id}: {resp.status_code} - {resp.text}")
        return False

    def upload_blob(self, obj_name: str, record_id: str, field_name: str, blob_path: str) -> bool:
        """PATCH a base64-encoded blob field on a record."""
        url = f"{self._instance_url}/services/data/v{self._api_version}/sobjects/{obj_name}/{record_id}"
        with open(blob_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        resp = requests.patch(url, headers=self._headers, json={field_name: encoded})
        if resp.status_code in (200, 204):
            self.logger.info(f"Uploaded blob to {obj_name}/{record_id}.{field_name}")
            return True
        self.logger.error(f"Blob upload failed for {obj_name}/{record_id}: {resp.status_code} - {resp.text}")
        return False

    def download_blob(self, blob_url: str, dest_path: str) -> bool:
        """Download a blob from a Salesforce URL to a local file."""
        headers = {"Authorization": f"Bearer {self._access_token}"}
        full_url = blob_url if blob_url.startswith("http") else f"{self._instance_url}{blob_url}"
        resp = requests.get(full_url, headers=headers)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            self.logger.info(f"Downloaded blob to {dest_path}")
            return True
        self.logger.error(f"Blob download failed ({resp.status_code}): {resp.text}")
        return False

    def resolve_name_map(self, obj_name: str, names: Set[str]) -> Dict[str, str]:
        """Query an sObject by Name and return a Name->Id mapping."""
        if not names:
            return {}
        name_filter = ",".join(f"'{self._soql_escape(n)}'" for n in names)
        records = self.soql_query(f"SELECT Id, Name FROM {obj_name} WHERE Name IN ({name_filter})")
        return {r["Name"]: r["Id"] for r in records}

    @staticmethod
    def _soql_escape(value: str) -> str:
        """Escape a string for safe inclusion in a SOQL literal."""
        return value.replace("\\", "\\\\").replace("'", "\\'")

    # -- CSV helpers ---------------------------------------------------

    @staticmethod
    def read_csv(path: str) -> List[dict]:
        """Read a CSV file and return a list of row dicts."""
        with open(path, newline="") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def read_csv_optional(path: str) -> List[dict]:
        """Read a CSV file if it exists, else return empty list."""
        if not os.path.exists(path):
            return []
        with open(path, newline="") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def write_csv(path: str, fieldnames: List[str], rows: List[dict]) -> None:
        """Write rows to a CSV file, creating parent dirs as needed."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def write_csv_raw(path: str, fieldnames: List[str], rows: List[List]) -> None:
        """Write rows (as value lists) to a CSV file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for row in rows:
                writer.writerow(row)

    @staticmethod
    def get_field_value(record: dict, dotted_field: str):
        """Extract a possibly nested field value (e.g. 'Parent.Name')."""
        if "." in dotted_field:
            parent, child = dotted_field.split(".", 1)
            parent_obj = record.get(parent)
            if parent_obj and isinstance(parent_obj, dict):
                return parent_obj.get(child, "")
            return ""
        return record.get(dotted_field, "")


# ===================================================================
# ExportCML
# ===================================================================

class ExportCML(CMLBaseTask):
    """Export constraint model data from an org to a local directory.

    Exports:
      - ExpressionSetDefinitionVersion (with ConstraintModel blob URL)
      - ExpressionSetDefinitionContextDefinition
      - ExpressionSet
      - ExpressionSetConstraintObj (all associations)
      - Referenced Product2, ProductClassification, ProductRelatedComponent
      - ConstraintModel blob file
    """

    task_options = {
        **CMLBaseTask.task_options,
        "developer_name": {
            "description": "DeveloperName of the Expression Set Definition",
            "required": True,
        },
        "version": {
            "description": "Version number (default: 1)",
            "required": False,
        },
        "output_dir": {
            "description": "Directory to write CSV exports and blobs",
            "required": True,
        },
    }

    def _run_task(self):
        dev_name = self.options["developer_name"]
        version = str(self.options.get("version", "1"))
        output_dir = self.options["output_dir"]
        api_name_versioned = f"{dev_name}_V{version}"

        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Exporting CML model '{dev_name}' v{version} to {output_dir}")

        # 1. ExpressionSetDefinitionVersion
        self._export_esdv(dev_name, version, api_name_versioned, output_dir)

        # 2. ExpressionSetDefinitionContextDefinition
        self._export_query(
            soql=f"""
                SELECT ContextDefinitionApiName, ContextDefinitionId,
                       ExpressionSetApiName, ExpressionSetDefinitionId
                FROM ExpressionSetDefinitionContextDefinition
                WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
            """,
            fields=["ContextDefinitionApiName", "ContextDefinitionId",
                     "ExpressionSetApiName", "ExpressionSetDefinitionId"],
            dest=os.path.join(output_dir, "ExpressionSetDefinitionContextDefinition.csv"),
        )

        # 3. ExpressionSet
        self._export_query(
            soql=f"""
                SELECT ApiName, Description, ExpressionSetDefinitionId, Id,
                       InterfaceSourceType, Name, ResourceInitializationType, UsageType
                FROM ExpressionSet
                WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
            """,
            fields=["ApiName", "Description", "ExpressionSetDefinitionId", "Id",
                     "InterfaceSourceType", "Name", "ResourceInitializationType", "UsageType"],
            dest=os.path.join(output_dir, "ExpressionSet.csv"),
        )

        # 4. ExpressionSetConstraintObj
        self._export_query(
            soql=f"""
                SELECT Name, ExpressionSetId, ExpressionSet.ApiName,
                       ReferenceObjectId, ConstraintModelTag, ConstraintModelTagType
                FROM ExpressionSetConstraintObj
                WHERE ExpressionSet.ApiName = '{dev_name}'
            """,
            fields=["Name", "ExpressionSetId", "ExpressionSet.ApiName",
                     "ReferenceObjectId", "ConstraintModelTag", "ConstraintModelTagType"],
            dest=os.path.join(output_dir, "ExpressionSetConstraintObj.csv"),
        )

        # 5. Referenced objects (filtered by ID prefix from ESC)
        self._export_referenced_objects(output_dir)

        # 6. Download ConstraintModel blob
        self._download_blob(api_name_versioned, output_dir)

        self.logger.info(f"Export complete -> {output_dir}")

    # -- Export helpers ------------------------------------------------

    def _export_esdv(self, dev_name: str, version: str, api_name_versioned: str, output_dir: str):
        """Export ExpressionSetDefinitionVersion, trying ConstraintModel field first."""
        primary_fields = [
            "ConstraintModel", "DeveloperName",
            "ExpressionSetDefinition.DeveloperName", "ExpressionSetDefinitionId",
            "Id", "Language", "MasterLabel", "Status", "VersionNumber",
        ]
        primary_soql = f"""
            SELECT {', '.join(primary_fields)}
            FROM ExpressionSetDefinitionVersion
            WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
              AND VersionNumber = {version}
        """
        dest = os.path.join(output_dir, "ExpressionSetDefinitionVersion.csv")
        if self._export_query(soql=primary_soql, fields=primary_fields, dest=dest):
            return

        # Fallback without ConstraintModel (non-Industries orgs)
        fallback_fields = [f for f in primary_fields if f != "ConstraintModel"]
        fallback_soql = f"""
            SELECT {', '.join(fallback_fields)}
            FROM ExpressionSetDefinitionVersion
            WHERE ExpressionSetDefinition.DeveloperName = '{dev_name}'
              AND VersionNumber = {version}
        """
        self._export_query(soql=fallback_soql, fields=fallback_fields, dest=dest)

    def _export_query(self, soql: str, fields: List[str], dest: str) -> bool:
        """Run a SOQL query and write results as CSV. Returns True on success."""
        self.logger.info(f"Exporting {os.path.basename(dest)}...")
        records = self.soql_query(soql)
        if records is None:
            return False
        self.logger.info(f"  {len(records)} records fetched")
        rows = [[self.get_field_value(rec, f) for f in fields] for rec in records]
        self.write_csv_raw(dest, fields, rows)
        return len(records) > 0

    def _export_referenced_objects(self, output_dir: str):
        """Export Product2, ProductClassification, and ProductRelatedComponent
        records that are referenced by ExpressionSetConstraintObj."""
        esc_path = os.path.join(output_dir, "ExpressionSetConstraintObj.csv")
        if not os.path.exists(esc_path):
            self.logger.warning("Skipping reference exports; ESC CSV missing")
            return

        product_ids = self._get_ref_ids_by_prefix(esc_path, "01t")
        classification_ids = self._get_ref_ids_by_prefix(esc_path, "11B")
        component_ids = self._get_ref_ids_by_prefix(esc_path, "0dS")

        # Product2
        self._export_query(
            soql=self._build_id_query("Product2", ["Id", "Name"], product_ids),
            fields=["Id", "Name"],
            dest=os.path.join(output_dir, "Product2.csv"),
        )

        # ProductClassification
        self._export_query(
            soql=self._build_id_query("ProductClassification", ["Id", "Name"], classification_ids),
            fields=["Id", "Name"],
            dest=os.path.join(output_dir, "ProductClassification.csv"),
        )

        # ProductRelatedComponent (with traversal fields for portable resolution)
        prc_fields = [
            "Id", "Name", "ParentProductId", "ParentProduct.Name",
            "ChildProductId", "ChildProduct.Name",
            "ChildProductClassificationId", "ChildProductClassification.Name",
            "ProductRelationshipTypeId", "ProductRelationshipType.Name", "Sequence",
        ]
        if component_ids:
            id_filter = ",".join(f"'{i}'" for i in component_ids)
            prc_soql = f"SELECT {', '.join(prc_fields)} FROM ProductRelatedComponent WHERE Id IN ({id_filter})"
        else:
            prc_soql = f"SELECT Id, Name FROM ProductRelatedComponent WHERE Id = '000000000000000AAA'"
            prc_fields = ["Id", "Name"]
        self._export_query(soql=prc_soql, fields=prc_fields, dest=os.path.join(output_dir, "ProductRelatedComponent.csv"))

    def _download_blob(self, api_name_versioned: str, output_dir: str):
        """Download the ConstraintModel blob from the ESDV CSV."""
        esdv_path = os.path.join(output_dir, "ExpressionSetDefinitionVersion.csv")
        if not os.path.exists(esdv_path):
            self.logger.warning("Skipping blob download; ESDV CSV missing")
            return

        rows = self.read_csv(esdv_path)
        for row in rows:
            if row.get("DeveloperName") != api_name_versioned:
                continue
            blob_url = row.get("ConstraintModel", "")
            if not blob_url or not blob_url.startswith("/services"):
                self.logger.warning(f"No valid blob URL for {api_name_versioned}")
                continue
            dev_name = api_name_versioned.rsplit("_V", 1)[0]
            version = api_name_versioned.rsplit("_V", 1)[1] if "_V" in api_name_versioned else "1"
            dest = os.path.join(output_dir, "blobs", f"ESDV_{dev_name}_V{version}.ffxblob")
            self.download_blob(blob_url, dest)
            return

        # ConstraintModel column may not have been available
        if rows and "ConstraintModel" not in (rows[0] if rows else {}):
            self.logger.info("ConstraintModel field not available in ESDV export; skipping blob")

    @staticmethod
    def _get_ref_ids_by_prefix(csv_path: str, prefix: str) -> List[str]:
        """Filter ReferenceObjectId values from ESC CSV by ID prefix."""
        ids = set()
        try:
            with open(csv_path, newline="") as f:
                for row in csv.DictReader(f):
                    ref_id = row.get("ReferenceObjectId", "")
                    if ref_id.startswith(prefix):
                        ids.add(ref_id)
        except Exception:
            pass
        return list(ids)

    @staticmethod
    def _build_id_query(obj_name: str, fields: List[str], ids: List[str]) -> str:
        """Build a SELECT ... WHERE Id IN (...) query, with a no-match fallback."""
        field_str = ", ".join(fields)
        if not ids:
            return f"SELECT {field_str} FROM {obj_name} WHERE Id = '000000000000000AAA'"
        id_filter = ",".join(f"'{i}'" for i in ids)
        return f"SELECT {field_str} FROM {obj_name} WHERE Id IN ({id_filter})"


# ===================================================================
# ImportCML
# ===================================================================

class ImportCML(CMLBaseTask):
    """Import constraint model data from a local directory into an org.

    Steps:
      1. Upsert ExpressionSet (by ApiName)
      2. Resolve ExpressionSetDefinitionVersion by DeveloperName
      3. Upsert ExpressionSetDefinitionContextDefinition
      4. Build polymorphic lookup maps for ReferenceObjectId resolution
      5. Create ExpressionSetConstraintObj records
      6. Delete old ESC records (only if all new ones succeeded)
      7. Upload ConstraintModel blob via PATCH
    """

    task_options = {
        **CMLBaseTask.task_options,
        "data_dir": {
            "description": "Directory containing CML CSV exports and blobs/",
            "required": True,
        },
        "dataset_dirs": {
            "description": "Comma-separated additional directories for cross-referencing (e.g. qb-pcm plan dir)",
            "required": False,
        },
        "dry_run": {
            "description": "Log operations without executing (default: false)",
            "required": False,
        },
    }

    def _run_task(self):
        data_dir = self.options["data_dir"]
        dataset_dirs_raw = self.options.get("dataset_dirs", "")
        if isinstance(dataset_dirs_raw, str):
            dataset_dirs = [d.strip() for d in dataset_dirs_raw.split(",") if d.strip()] if dataset_dirs_raw else []
        else:
            dataset_dirs = list(dataset_dirs_raw) if dataset_dirs_raw else []
        dry_run = str(self.options.get("dry_run", "false")).lower() in ("true", "1", "yes")
        blob_dir = os.path.join(data_dir, "blobs")

        self.logger.info(f"Importing CML data from {data_dir} (dry_run={dry_run})")

        # Load input CSVs
        esdv = self.read_csv(os.path.join(data_dir, "ExpressionSetDefinitionVersion.csv"))[0]
        esdcd = self.read_csv(os.path.join(data_dir, "ExpressionSetDefinitionContextDefinition.csv"))[0]
        ess = self.read_csv(os.path.join(data_dir, "ExpressionSet.csv"))[0]

        # Load ESC records (try dataset_dirs first, then data_dir)
        esc_list = []
        for dd in dataset_dirs:
            esc_path = os.path.join(dd, "ExpressionSetConstraintObj.csv")
            if os.path.exists(esc_path):
                esc_list = self.read_csv_optional(esc_path)
                self.logger.info(f"Loaded {len(esc_list)} ESC records from {esc_path}")
                break
        if not esc_list:
            esc_list = self.read_csv(os.path.join(data_dir, "ExpressionSetConstraintObj.csv"))
            self.logger.info(f"Loaded {len(esc_list)} ESC records from {data_dir}")

        # Step 1: Upsert ExpressionSet
        ess.pop("Id", None)
        ess_id = self._upsert_expression_set(ess, dry_run)
        if not ess_id:
            self.logger.error("Could not create or update ExpressionSet. Aborting.")
            return

        # Step 2: Resolve ESDV
        devname = esdv["DeveloperName"]
        esdv_records = self.soql_query(
            f"SELECT Id FROM ExpressionSetDefinitionVersion WHERE DeveloperName = '{devname}'"
        )
        if not esdv_records:
            self.logger.error(f"Could not find ExpressionSetDefinitionVersion for {devname}")
            return
        esdv_id = esdv_records[0]["Id"]
        self.logger.info(f"Resolved ESDV '{devname}' -> {esdv_id}")

        # Step 3: Upsert ESDCD
        self._upsert_esdcd(esdcd, ess, dry_run)

        # Step 4: Build polymorphic maps
        legacy_to_uk, product_names, classification_names, prc_parent_names = (
            self._build_legacy_maps(data_dir, dataset_dirs)
        )
        uk_to_target_prod = self.resolve_name_map("Product2", product_names)
        uk_to_target_class = self.resolve_name_map("ProductClassification", classification_names)
        uk_to_target_prc = self._resolve_prc_composite_map(prc_parent_names)
        prc_name_to_id = self.resolve_name_map("ProductRelatedComponent", prc_parent_names)

        self.logger.info(
            f"Resolution maps: Product2={len(uk_to_target_prod)}, "
            f"Classification={len(uk_to_target_class)}, "
            f"PRC_composite={len(uk_to_target_prc)}, PRC_name={len(prc_name_to_id)}"
        )

        # Step 5: Create ESC records
        existing_esc = self.soql_query(
            f"SELECT Id FROM ExpressionSetConstraintObj WHERE ExpressionSetId = '{ess_id}'"
        )
        existing_esc_ids = [r["Id"] for r in existing_esc]
        self.logger.info(f"Found {len(existing_esc_ids)} existing ESC records to replace")

        import_failed = False
        new_count = 0

        for row in esc_list:
            # Capture reference info before cleaning
            ref_id = row.get("ReferenceObjectId", "").strip()
            ref_name = row.get("ReferenceObject.Name", "").strip()
            ref_type = row.get("ReferenceObject.Type", "").strip()
            tag_type = row.get("ConstraintModelTagType", "").strip()

            # Clean row for insert
            clean = {}
            for k, v in row.items():
                if k in ("Id", "Name") or k.startswith("$$") or "." in k:
                    continue
                clean[k] = v
            clean["ExpressionSetId"] = ess_id

            # Resolve polymorphic ReferenceObjectId
            resolved_id = self._resolve_reference_id(
                ref_id, ref_name, ref_type, tag_type,
                legacy_to_uk, uk_to_target_prod, uk_to_target_class,
                uk_to_target_prc, prc_name_to_id,
            )

            if resolved_id:
                clean["ReferenceObjectId"] = resolved_id
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would create ESC: tag={row.get('ConstraintModelTag')}, ref={resolved_id}")
                    new_count += 1
                else:
                    if self.create_record("ExpressionSetConstraintObj", clean):
                        new_count += 1
                    else:
                        import_failed = True
            else:
                uk = legacy_to_uk.get(ref_id, "N/A")
                self.logger.warning(f"Could not resolve ReferenceObjectId: {ref_id} (UK: {uk}, name: {ref_name})")
                import_failed = True

        self.logger.info(f"{new_count} ESC records {'would be ' if dry_run else ''}created")

        # Step 6: Delete old ESC records
        if not import_failed and not dry_run:
            self.logger.info(f"Deleting {len(existing_esc_ids)} old ESC records...")
            for eid in existing_esc_ids:
                self.delete_record("ExpressionSetConstraintObj", eid)
            self.logger.info("Old ESC records deleted")
        elif import_failed:
            self.logger.warning(
                "Import had errors -- skipping deletion of old ESC records. "
                "Target org may contain a mix of old and new constraints."
            )

        # Step 7: Upload blob
        version_num = esdv.get("VersionNumber", "1")
        base_dev = devname.replace(f"_V{version_num}", "") if f"_V{version_num}" in devname else devname
        blob_file = os.path.join(blob_dir, f"ESDV_{base_dev}_V{version_num}.ffxblob")
        if os.path.exists(blob_file):
            if dry_run:
                self.logger.info(f"[DRY RUN] Would upload blob {blob_file} to ESDV {esdv_id}")
            else:
                self.upload_blob("ExpressionSetDefinitionVersion", esdv_id, "ConstraintModel", blob_file)
        else:
            self.logger.warning(f"Blob file not found: {blob_file}")

        self.logger.info("Import complete")

    # -- Import helpers ------------------------------------------------

    def _upsert_expression_set(self, record: dict, dry_run: bool) -> Optional[str]:
        """Upsert an ExpressionSet by ApiName. Returns the record Id."""
        api_name = record.get("ApiName")
        if not api_name:
            self.logger.error("ExpressionSet record missing ApiName")
            return None

        existing = self.soql_query(f"SELECT Id FROM ExpressionSet WHERE ApiName = '{api_name}'")
        record.pop("ExpressionSetDefinitionId", None)

        if existing:
            record_id = existing[0]["Id"]
            if dry_run:
                self.logger.info(f"[DRY RUN] Would update ExpressionSet '{api_name}' ({record_id})")
                return record_id
            patch_data = {k: v for k, v in record.items() if k != "ApiName"}
            if self.update_record("ExpressionSet", record_id, patch_data):
                self.logger.info(f"Updated ExpressionSet '{api_name}' -> {record_id}")
                return record_id
            return None
        else:
            if dry_run:
                self.logger.info(f"[DRY RUN] Would create ExpressionSet '{api_name}'")
                return "DRY_RUN_ID"
            return self.create_record("ExpressionSet", record)

    def _upsert_esdcd(self, esdcd: dict, ess: dict, dry_run: bool):
        """Upsert ExpressionSetDefinitionContextDefinition."""
        api_name = ess.get("ApiName", "")
        cd_apiname = esdcd.get("ContextDefinitionApiName", "").strip()
        if not cd_apiname:
            self.logger.error("ESDCD missing ContextDefinitionApiName. Ensure your CML uses a custom Context Definition.")
            return

        # Resolve ContextDefinition by DeveloperName
        cd_records = self.soql_query(f"SELECT Id FROM ContextDefinition WHERE DeveloperName = '{cd_apiname}'")
        if not cd_records:
            self.logger.error(f"Could not find ContextDefinition for '{cd_apiname}'")
            return
        cd_id = cd_records[0]["Id"]

        # Resolve ExpressionSetDefinition by DeveloperName
        esd_records = self.soql_query(f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{api_name}'")
        if not esd_records:
            self.logger.error(f"Could not find ExpressionSetDefinition for '{api_name}'")
            return
        esd_id = esd_records[0]["Id"]

        # Check if ESDCD already exists
        existing = self.soql_query(
            f"SELECT Id FROM ExpressionSetDefinitionContextDefinition WHERE ExpressionSetDefinitionId = '{esd_id}'"
        )

        if existing:
            record_id = existing[0]["Id"]
            if dry_run:
                self.logger.info(f"[DRY RUN] Would update ESDCD {record_id} with ContextDefinitionId={cd_id}")
            else:
                self.update_record("ExpressionSetDefinitionContextDefinition", record_id, {"ContextDefinitionId": cd_id})
                self.logger.info(f"Updated ESDCD -> {record_id}")
        else:
            payload = {"ContextDefinitionId": cd_id, "ExpressionSetDefinitionId": esd_id}
            if dry_run:
                self.logger.info(f"[DRY RUN] Would create ESDCD for ESD={esd_id}, CD={cd_id}")
            else:
                self.create_record("ExpressionSetDefinitionContextDefinition", payload)

    def _build_legacy_maps(self, data_dir: str, dataset_dirs: List[str]):
        """Build legacy ID -> portable unique key maps from CSV data.

        The legacy-to-UK map MUST come from the constraints export (data_dir)
        because it contains source org IDs. The dataset_dirs provide
        additional name candidates for resolution in the target org.
        """
        legacy_to_uk = {}
        product_names = set()
        classification_names = set()
        prc_parent_names = set()

        # Product2 -- legacy IDs from data_dir, names from both
        for row in self.read_csv_optional(os.path.join(data_dir, "Product2.csv")):
            legacy_id = row.get("Id", "")
            name = row.get("Name", "")
            if name:
                product_names.add(name)
            if legacy_id:
                legacy_to_uk[legacy_id] = name
        for dd in dataset_dirs:
            for row in self.read_csv_optional(os.path.join(dd, "Product2.csv")):
                name = row.get("Name", "")
                if name:
                    product_names.add(name)

        # ProductClassification -- legacy IDs from data_dir, names from both
        for row in self.read_csv_optional(os.path.join(data_dir, "ProductClassification.csv")):
            legacy_id = row.get("Id", "")
            name = row.get("Name", "")
            if name:
                classification_names.add(name)
            if legacy_id:
                legacy_to_uk[legacy_id] = name
        for dd in dataset_dirs:
            for row in self.read_csv_optional(os.path.join(dd, "ProductClassification.csv")):
                name = row.get("Name", "")
                if name:
                    classification_names.add(name)

        # ProductRelatedComponent (composite unique key) -- legacy from data_dir
        for row in self.read_csv_optional(os.path.join(data_dir, "ProductRelatedComponent.csv")):
            legacy_id = row.get("Id", "")
            name = row.get("Name", "")
            if legacy_id and row.get("ParentProduct.Name"):
                uk = (
                    row["ParentProduct.Name"] + "|"
                    + (row.get("ChildProduct.Name") or "") + "|"
                    + (row.get("ChildProductClassification.Name") or "") + "|"
                    + (row.get("ProductRelationshipType.Name") or "") + "|"
                    + (row.get("Sequence") or "")
                )
                prc_parent_names.add(row["ParentProduct.Name"])
                legacy_to_uk[legacy_id] = uk
            if name:
                prc_parent_names.add(name)
        for dd in dataset_dirs:
            for row in self.read_csv_optional(os.path.join(dd, "ProductRelatedComponent.csv")):
                name = row.get("Name", "")
                if name:
                    prc_parent_names.add(name)
                pp = row.get("ParentProduct.Name", "")
                if pp:
                    prc_parent_names.add(pp)

        return legacy_to_uk, product_names, classification_names, prc_parent_names

    def _resolve_prc_composite_map(self, prc_parent_names: Set[str]) -> Dict[str, str]:
        """Query target org for ProductRelatedComponent records and build composite UK -> Id map."""
        if not prc_parent_names:
            return {}
        name_filter = ",".join(f"'{self._soql_escape(n)}'" for n in prc_parent_names)
        records = self.soql_query(f"""
            SELECT Id, Name, ParentProduct.Name, ChildProduct.Name,
                   ChildProductClassification.Name, ProductRelationshipType.Name, Sequence
            FROM ProductRelatedComponent
            WHERE ParentProduct.Name IN ({name_filter}) OR Name IN ({name_filter})
        """)
        result = {}
        for r in records:
            pp = r.get("ParentProduct")
            if not pp:
                continue
            uk = (
                pp["Name"] + "|"
                + (r["ChildProduct"]["Name"] if r.get("ChildProduct") else "") + "|"
                + (r["ChildProductClassification"]["Name"] if r.get("ChildProductClassification") else "") + "|"
                + (r["ProductRelationshipType"]["Name"] if r.get("ProductRelationshipType") else "") + "|"
                + (str(r["Sequence"]) if r.get("Sequence") is not None else "")
            )
            result[uk] = r["Id"]
        return result

    @staticmethod
    def _resolve_reference_id(
        ref_id: str, ref_name: str, ref_type: str, tag_type: str,
        legacy_to_uk: dict,
        uk_to_prod: dict, uk_to_class: dict, uk_to_prc: dict,
        prc_name_to_id: dict,
    ) -> Optional[str]:
        """Resolve a polymorphic ReferenceObjectId to a target org Id."""
        if ref_id:
            uk = legacy_to_uk.get(ref_id)
            if ref_id.startswith("01t"):
                return uk_to_prod.get(uk)
            elif ref_id.startswith("11B"):
                return uk_to_class.get(uk)
            elif ref_id.startswith("0dS"):
                return uk_to_prc.get(uk)
        if ref_name:
            if ref_type == "ProductRelatedComponent" or tag_type.lower() == "port":
                return prc_name_to_id.get(ref_name)
            elif ref_type == "ProductClassification":
                return uk_to_class.get(ref_name)
            elif ref_type == "Product2":
                return uk_to_prod.get(ref_name)
            else:
                return uk_to_class.get(ref_name) or uk_to_prod.get(ref_name)
        return None


# ===================================================================
# ValidateCML
# ===================================================================

class ValidateCML(BaseTask):
    """Validate CML constraint model files and ESC association coverage.

    This task does NOT require Salesforce org access -- it validates
    local .cml files and optionally cross-references them against
    ExpressionSetConstraintObj CSV data.

    Extends BaseTask (not CMLBaseTask) since no org connection is needed.
    """

    task_options = {
        "cml_dir": {
            "description": "Directory containing .cml files (default: scripts/cml)",
            "required": False,
        },
        "data_dir": {
            "description": "Constraints data plan directory for association checking",
            "required": False,
        },
        "expression_set_name": {
            "description": "Override Expression Set name for association checks",
            "required": False,
        },
    }

    def _run_task(self):
        cml_dir = self.options.get("cml_dir") or "scripts/cml"
        data_dir = self.options.get("data_dir")
        dataset_dirs = [data_dir] if data_dir else []
        expression_set_override = (self.options.get("expression_set_name") or "").strip()

        cml_files = sorted([
            os.path.join(cml_dir, name)
            for name in os.listdir(cml_dir)
            if name.endswith(".cml")
        ])

        if not cml_files:
            self.logger.warning(f"No .cml files found in {cml_dir}")
            return

        self.logger.info(f"Validating {len(cml_files)} CML file(s) in {cml_dir}")

        # Load ESC associations from data directories
        associations = {}
        for dd in dataset_dirs:
            associations.update(self._read_dataset_associations(dd))

        all_issues = {}
        association_issues = {}
        has_errors = False

        for path in cml_files:
            rel_path = os.path.relpath(path, cml_dir)
            issues, types, relations, leaf_types = self._validate_file(path)

            if issues:
                all_issues[rel_path] = issues
                if any(sev == "error" for sev, _, _ in issues):
                    has_errors = True

            if dataset_dirs:
                model_name = expression_set_override or self._infer_expression_set_name(path, dataset_dirs)
                assoc = associations.get(model_name, {"type": set(), "port": set()})
                assoc_issues_list = []

                relation_names = {rel_name for _, rel_name, _ in relations}
                for rel_name in sorted(relation_names):
                    if rel_name not in assoc["port"]:
                        assoc_issues_list.append(("warning", None, f"Missing port association for relation '{rel_name}' in '{model_name}'"))

                for type_name in sorted(leaf_types):
                    if type_name not in assoc["type"]:
                        assoc_issues_list.append(("warning", None, f"Missing type association for leaf type '{type_name}' in '{model_name}'"))

                for tag in sorted(assoc["type"]):
                    if tag not in types:
                        assoc_issues_list.append(("warning", None, f"Type association '{tag}' not found in CML types for '{model_name}'"))

                for tag in sorted(assoc["port"]):
                    if tag not in relation_names:
                        assoc_issues_list.append(("warning", None, f"Port association '{tag}' not found in CML relations for '{model_name}'"))

                if assoc_issues_list:
                    association_issues[rel_path] = assoc_issues_list

        # Report results
        if not all_issues and not association_issues:
            self.logger.info("No structural issues found in CML files")
            return

        for rel_path, issues in all_issues.items():
            self.logger.warning(f"\n{rel_path}:")
            for severity, line_no, message in issues:
                loc = f"L{line_no}: " if line_no else ""
                self.logger.warning(f"  [{severity}] {loc}{message}")

        for rel_path, issues in association_issues.items():
            self.logger.warning(f"\n{rel_path} (associations):")
            for severity, line_no, message in issues:
                loc = f"L{line_no}: " if line_no else ""
                self.logger.warning(f"  [{severity}] {loc}{message}")

        if has_errors:
            self.logger.error("CML validation found errors")

    # -- CML Parsing ---------------------------------------------------

    def _validate_file(self, path: str) -> Tuple[list, dict, list, set]:
        """Validate a single CML file. Returns (issues, types, relations, leaf_types)."""
        issues = []
        types = {}
        abstract_types = set()
        child_types = set()
        defines = {}
        relations = []
        type_order_refs = []
        pending_annotations = []
        supported = SUPPORTED_ANNOTATIONS
        supported_any = set()
        for vals in supported.values():
            supported_any |= vals

        with open(path, "r", encoding="utf-8") as handle:
            raw_lines = handle.readlines()
        lines = self._strip_comments(raw_lines)

        brace_balance = 0
        paren_balance = 0
        first_type_line = None

        for line_no, line in enumerate(lines, start=1):
            brace_balance += line.count("{") - line.count("}")
            paren_balance += line.count("(") - line.count(")")
            if brace_balance < 0:
                issues.append(("error", line_no, "Unbalanced '}' brace."))
                brace_balance = 0
            if paren_balance < 0:
                issues.append(("warning", line_no, "Unbalanced ')' parenthesis."))
                paren_balance = 0

            define_parsed = self._parse_define(line)
            if define_parsed:
                if first_type_line is not None:
                    issues.append(("warning", line_no, "Header declarations should appear before the first type."))
                defines[define_parsed[0]] = define_parsed[1]
                continue

            if HEADER_DECL_RE.match(line):
                if first_type_line is not None:
                    issues.append(("warning", line_no, "Header declarations should appear before the first type."))

            type_match = TYPE_RE.match(line)
            if type_match:
                type_name = type_match.group(1)
                base_name = type_match.group(2)
                body_token = type_match.group(3)
                if first_type_line is None:
                    first_type_line = line_no
                annotation_text = " ".join(pending_annotations + [line])
                pending_annotations = []
                keys = extract_annotation_keys(annotation_text)
                values = extract_annotation_kv(annotation_text)
                for key in sorted(keys):
                    if key not in supported["type"]:
                        issues.append(("warning", line_no, f"Unsupported annotation '{key}' on type '{type_name}'."))
                _validate_annotation_values(keys, values, line_no, issues, f"type '{type_name}'")
                if type_name in types:
                    issues.append(("error", line_no, f"Duplicate type definition '{type_name}'."))
                types[type_name] = base_name
                if base_name:
                    child_types.add(base_name)
                if body_token == ";":
                    abstract_types.add(type_name)
                continue

            relation_match = RELATION_RE.match(line)
            if relation_match:
                rel_name, rel_type = relation_match.groups()
                annotation_text = " ".join(pending_annotations + [line])
                pending_annotations = []
                keys = extract_annotation_keys(annotation_text)
                values = extract_annotation_kv(annotation_text)
                for key in sorted(keys):
                    if key not in supported["port"]:
                        issues.append(("warning", line_no, f"Unsupported annotation '{key}' on relation '{rel_name}'."))
                _validate_annotation_values(keys, values, line_no, issues, f"relation '{rel_name}'")
                relations.append((line_no, rel_name, rel_type))
                card_match = CARDINALITY_RE.search(line)
                if card_match:
                    min_val = card_match.group(1)
                    max_val = card_match.group(2)
                    if max_val is not None and int(max_val) < int(min_val):
                        issues.append(("warning", line_no, f"Relation '{rel_name}' cardinality has max < min."))
                order_match = ORDER_RE.search(line)
                if order_match:
                    for item in order_match.group(1).split(","):
                        item = item.strip()
                        if item:
                            type_order_refs.append((line_no, item))
                continue

            if line.strip().startswith("@("):
                pending_annotations.append(line.strip())
                continue

            extern_match = EXTERN_RE.match(line)
            if extern_match:
                _, extern_name, extern_default = extern_match.groups()
                annotation_text = " ".join(pending_annotations + [line])
                pending_annotations = []
                if first_type_line is not None:
                    issues.append(("warning", line_no, "Header declarations should appear before the first type."))
                keys = extract_annotation_keys(annotation_text)
                values = extract_annotation_kv(annotation_text)
                for key in sorted(keys):
                    if key not in supported["extern"]:
                        issues.append(("warning", line_no, f"Unsupported annotation '{key}' on extern '{extern_name}'."))
                _validate_annotation_values(keys, values, line_no, issues, f"extern '{extern_name}'")
                if "contextPath" not in keys and not extern_default:
                    issues.append(("warning", line_no, f"Extern '{extern_name}' has no default and no contextPath; it may remain unbound."))
                continue

            constraint_match = CONSTRAINT_LINE_RE.match(line)
            if constraint_match:
                annotation_text = " ".join(pending_annotations + [line])
                pending_annotations = []
                keys = extract_annotation_keys(annotation_text)
                values = extract_annotation_kv(annotation_text)
                for key in sorted(keys):
                    if key not in supported["constraint"]:
                        issues.append(("warning", line_no, f"Unsupported annotation '{key}' on constraint/rule."))
                _validate_annotation_values(keys, values, line_no, issues, "constraint/rule")
                continue

            field_match = FIELD_RE.match(line)
            if field_match:
                field_type, field_name, raw_rhs = field_match.groups()
                annotation_text = " ".join(pending_annotations + [line])
                pending_annotations = []
                keys = extract_annotation_keys(annotation_text)
                values = extract_annotation_kv(annotation_text)
                for key in sorted(keys):
                    if key not in supported_any:
                        issues.append(("warning", line_no, f"Unsupported annotation '{key}' on attribute '{field_name}'."))
                if "contextPath" in keys:
                    issues.append(("warning", line_no, f"contextPath should only be used on extern variables (found on attribute '{field_name}')."))
                if "productGroup" in keys:
                    issues.append(("warning", line_no, "productGroup is deprecated; use minInstanceQty/maxInstanceQty type annotations instead."))
                _validate_annotation_values(keys, values, line_no, issues, f"attribute '{field_name}'")

                default_value = _parse_default_value(annotation_text)
                if default_value is not None:
                    rhs = raw_rhs.strip()
                    domain_values = None
                    range_match = RANGE_RE.search(rhs)
                    if rhs.startswith("[") and rhs.endswith("]"):
                        domain_values = _split_list_values(rhs[1:-1])
                    elif rhs in defines:
                        domain_values = defines[rhs]

                    if field_type.startswith("string"):
                        if domain_values is not None and default_value not in domain_values:
                            issues.append(("warning", line_no, f"Default '{default_value}' not in enum for '{field_name}'."))
                    elif field_type.startswith("int") or field_type.startswith("decimal"):
                        if range_match:
                            low, high = int(range_match.group(1)), int(range_match.group(2))
                            try:
                                numeric_default = int(float(default_value))
                                if numeric_default < low or numeric_default > high:
                                    issues.append(("warning", line_no, f"Default '{default_value}' outside range for '{field_name}'."))
                            except ValueError:
                                issues.append(("warning", line_no, f"Default '{default_value}' is not numeric for '{field_name}'."))
                continue

            if line.strip() and not line.strip().startswith("//"):
                if pending_annotations:
                    annotation_text = " ".join(pending_annotations)
                    keys = extract_annotation_keys(annotation_text)
                    for key in sorted(keys):
                        if key not in supported_any:
                            issues.append(("warning", line_no, f"Unsupported annotation '{key}'."))
                pending_annotations = []

        if brace_balance != 0:
            issues.append(("error", None, "Unbalanced '{'/'}' braces in file."))
        if paren_balance != 0:
            issues.append(("warning", None, "Unbalanced '('/')' parentheses in file."))

        for line_no, rel_name, rel_type in relations:
            if rel_type not in types:
                issues.append(("error", line_no, f"Relation '{rel_name}' references missing type '{rel_type}'."))

        for line_no, order_type in type_order_refs:
            if order_type not in types:
                issues.append(("warning", line_no, f"Order list references missing type '{order_type}'."))

        for type_name, base_name in types.items():
            if base_name and base_name not in types:
                issues.append(("warning", None, f"Type '{type_name}' extends missing base '{base_name}'."))

        leaf_types = {t for t in types if t not in child_types and t not in abstract_types}
        return issues, types, relations, leaf_types

    @staticmethod
    def _strip_comments(lines: List[str]) -> List[str]:
        """Remove // and /* */ comments from source lines."""
        cleaned = []
        in_block = False
        for line in lines:
            text = line
            if in_block:
                if "*/" in text:
                    text = text.split("*/", 1)[1]
                    in_block = False
                else:
                    cleaned.append("")
                    continue
            while "/*" in text:
                before, rest = text.split("/*", 1)
                if "*/" in rest:
                    text = before + rest.split("*/", 1)[1]
                else:
                    text = before
                    in_block = True
                    break
            if "//" in text:
                text = text.split("//", 1)[0]
            cleaned.append(text)
        return cleaned

    @staticmethod
    def _parse_define(line: str) -> Optional[Tuple[str, list]]:
        """Parse a 'define Name [values]' declaration."""
        match = DEFINE_RE.match(line)
        if not match:
            return None
        name = match.group(1)
        raw_vals = match.group(2).strip()
        values = _split_list_values(raw_vals) if raw_vals else []
        return name, values

    @staticmethod
    def _read_dataset_associations(dataset_dir: str) -> dict:
        """Read ESC associations from a data directory."""
        esc_path = os.path.join(dataset_dir, "ExpressionSetConstraintObj.csv")
        if not os.path.exists(esc_path):
            return {}
        associations_by_model = {}
        with open(esc_path, newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                model_name = row.get("ExpressionSet.Name", "").strip()
                if not model_name:
                    model_name = row.get("ExpressionSet.ApiName", "").strip()
                if not model_name:
                    continue
                tag = row.get("ConstraintModelTag", "").strip()
                tag_type = row.get("ConstraintModelTagType", "").strip().lower()
                if not tag or not tag_type:
                    continue
                entry = associations_by_model.setdefault(model_name, {"type": set(), "port": set()})
                if tag_type == "type":
                    entry["type"].add(tag)
                elif tag_type == "port":
                    entry["port"].add(tag)
        return associations_by_model

    @staticmethod
    def _infer_expression_set_name(cml_path: str, dataset_dirs: List[str]) -> str:
        """Infer the Expression Set name from CSVs or CML filename."""
        cml_name = os.path.splitext(os.path.basename(cml_path))[0]
        for dd in dataset_dirs:
            expr_path = os.path.join(dd, "ExpressionSet.csv")
            if not os.path.exists(expr_path):
                continue
            with open(expr_path, newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    name = (row.get("Name") or "").strip()
                    if name:
                        return name
        return cml_name


# ---------------------------------------------------------------------------
# Module-level helper functions used by ValidateCML
# (kept at module level for clarity since they are pure functions)
# ---------------------------------------------------------------------------

def _split_list_values(raw: str) -> List[str]:
    """Parse comma-separated list values, stripping quotes."""
    values = []
    for part in raw.split(","):
        part = part.strip()
        if part.startswith('"') and part.endswith('"'):
            part = part[1:-1]
        values.append(part)
    return [v for v in values if v != ""]


def _parse_default_value(annotation_text: str) -> Optional[str]:
    """Extract defaultValue from an annotation string."""
    match = DEFAULT_RE.search(annotation_text)
    if not match:
        return None
    raw = match.group(1).strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    return raw


def extract_annotation_keys(annotation_text: str) -> Set[str]:
    """Extract annotation key names from annotation text."""
    return {match.group(1) for match in ANNOTATION_KEY_RE.finditer(annotation_text)}


def extract_annotation_kv(annotation_text: str) -> Dict[str, str]:
    """Extract annotation key-value pairs from annotation text."""
    result = {}
    for match in ANNOTATION_KV_RE.finditer(annotation_text):
        key, raw = match.group(1), match.group(2).strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        result[key] = raw
    return result


def _validate_annotation_values(
    keys: Set[str], values: Dict[str, str], line_no, issues: list, context_label: str
):
    """Validate annotation value types (boolean, integer, enum, date)."""
    for key in sorted(keys):
        value = values.get(key)
        if value is None:
            continue
        if key in BOOLEAN_ANNOTATIONS and value not in {"true", "false"}:
            issues.append(("warning", line_no, f"Annotation '{key}' expects true/false on {context_label}."))
        if key in INTEGER_ANNOTATIONS and not value.isdigit():
            issues.append(("warning", line_no, f"Annotation '{key}' expects an integer on {context_label}."))
        if key in ENUM_ANNOTATIONS and value not in ENUM_ANNOTATIONS[key]:
            issues.append(("warning", line_no, f"Annotation '{key}' expects one of {sorted(ENUM_ANNOTATIONS[key])} on {context_label}."))
        if key in {"startDate", "endDate"} and not DATE_RE.match(value):
            issues.append(("warning", line_no, f"Annotation '{key}' expects ISO date YYYY-MM-DD on {context_label}."))
