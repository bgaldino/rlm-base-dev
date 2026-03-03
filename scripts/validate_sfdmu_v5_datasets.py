#!/usr/bin/env python3
"""
Validate and fix SFDMU v5 datasets for composite key compliance and configuration correctness.

This script validates SFDMU datasets to ensure they conform to SFDMU v5 requirements,
including proper composite key notation, CSV structure, and documentation alignment.
It can also automatically fix common issues.

Usage:
    python scripts/validate_sfdmu_v5_datasets.py [--dataset <path>] [--strict] [--verbose]
    python scripts/validate_sfdmu_v5_datasets.py --fix-headers --fix-composite-keys [--dry-run]

Options:
    --dataset PATH        Validate a single dataset (default: validate all SFDMU datasets)
    --strict              Treat warnings as errors (fail on Medium-level issues)
    --verbose             Print detailed validation steps
    --fix-headers         Add missing headers to empty CSV files
    --fix-composite-keys  Add missing composite key columns to CSVs
    --fix-all             Enable all fixes (headers + composite keys)
    --dry-run             Show what would be fixed without making changes
    --help                Show this help message
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    INFO = "Info"


@dataclass
class Issue:
    """Represents a validation issue."""
    severity: Severity
    object_name: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ValidationResult:
    """Validation result for a single dataset."""
    dataset_path: str
    dataset_name: str
    passed: bool = True
    issues: List[Issue] = field(default_factory=list)
    objects_validated: int = 0

    def add_issue(self, issue: Issue):
        """Add an issue to the result."""
        self.issues.append(issue)
        if issue.severity in (Severity.CRITICAL, Severity.HIGH):
            self.passed = False


class SFDMUValidator:
    """Validator for SFDMU v5 datasets."""

    # Known objects that use deleteOldData strategy (from sfdmu_composite_key_optimizations.md)
    DELETE_OLD_DATA_OBJECTS = {
        "FulfillmentWorkspaceItem",
        "PriceBookRateCard",
        "RateCardEntry",
        "RateAdjustmentByTier",
    }

    # Known excluded objects (from optimization doc)
    KNOWN_EXCLUDED_OBJECTS = {
        "PricebookEntryDerivedPrice",
        "ProductUsageResourcePolicy",
        "ProductUsageGrant",
        "ProductDecompEnrichmentRule",
        "ProductComponentGrpOverride",
        "ProductRelComponentOverride",
    }

    # Objects with known empty CSVs (0 records placeholders)
    KNOWN_EMPTY_CSV_OBJECTS = {
        "ValTfrmGrp",
        "ValTfrm",
        "FulfillmentTaskAssignmentRule",
        "ProductQualification",
        "ProductDisqualification",
        "ProductCategoryDisqual",
        "ProductCategoryQualification",
        "CostBook",
        "CostBookEntry",
        "GeneralLedgerJrnlEntryRule",
        "ProductRelComponentOverride",
        "PriceAdjustmentTier",
        "BundleBasedAdjustment",
        "PricebookEntryDerivedPrice",
        "ProductRampSegment",
        "UsagePrdGrantBindingPolicy",
    }

    def __init__(self, base_dir: str, strict: bool = False, verbose: bool = False,
                 fix_headers: bool = False, fix_composite_keys: bool = False, dry_run: bool = False):
        """Initialize the validator.

        Args:
            base_dir: Base directory of the project (e.g., /Users/scheck/Code/rlm-base-dev)
            strict: If True, treat warnings (Medium severity) as errors
            verbose: If True, print detailed validation steps
            fix_headers: If True, add missing headers to empty CSVs
            fix_composite_keys: If True, add missing composite key columns
            dry_run: If True, show what would be fixed without making changes
        """
        self.base_dir = Path(base_dir)
        if not self.base_dir.exists():
            raise ValueError(f"Base directory does not exist: {base_dir}")

        self.strict = strict
        self.verbose = verbose
        self.fix_headers = fix_headers
        self.fix_composite_keys = fix_composite_keys
        self.dry_run = dry_run
        self.sfdmu_base = self.base_dir / "datasets" / "sfdmu"
        self.fixes_applied = {"headers": 0, "composite_keys": 0}

    def log(self, message: str, level: str = "INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            prefix = f"[{level}]" if level != "INFO" else ""
            print(f"{prefix} {message}")

    def _make_relative_path(self, path: Path) -> str:
        """Convert path to relative from base_dir for portability.

        Args:
            path: Path to convert

        Returns:
            Relative path string, or filename if conversion fails
        """
        try:
            return str(path.relative_to(self.base_dir))
        except ValueError:
            # If not under base_dir, just use filename
            return path.name

    def find_sfdmu_datasets(self) -> List[Path]:
        """Find all SFDMU dataset directories.

        Returns:
            List of paths to dataset directories containing export.json
        """
        datasets = []
        if not self.sfdmu_base.exists():
            return datasets

        # Find all export.json files in SFDMU directory tree
        for export_json in self.sfdmu_base.rglob("export.json"):
            dataset_dir = export_json.parent
            # Skip if it's in a subdirectory like objectset_source or processed
            if any(p in export_json.parts for p in ["objectset_source", "processed", "source", "logs"]):
                continue
            datasets.append(dataset_dir)

        return sorted(datasets)

    def get_dataset_name(self, dataset_path: Path) -> str:
        """Extract dataset name from path (e.g., qb/en-US/qb-pcm).

        Args:
            dataset_path: Path to the dataset directory

        Returns:
            String like "qb/en-US/qb-pcm" or "qb/ja/qb-pricing"
        """
        # Get relative path from SFDMU base
        try:
            rel_path = dataset_path.relative_to(self.sfdmu_base)
            return str(rel_path)
        except ValueError:
            return dataset_path.name

    def validate_dataset(self, dataset_path: Path) -> ValidationResult:
        """Validate a single SFDMU dataset.

        Args:
            dataset_path: Path to the dataset directory

        Returns:
            ValidationResult with all issues found
        """
        dataset_name = self.get_dataset_name(dataset_path)

        # Store dataset path relative to base_dir for portability
        # Use full path from repo root (e.g., datasets/sfdmu/qb/en-US/qb-pcm)
        try:
            display_dataset_path = dataset_path.relative_to(self.base_dir)
        except ValueError:
            # Fall back to absolute if not under base_dir
            display_dataset_path = dataset_path

        result = ValidationResult(
            dataset_path=str(display_dataset_path),
            dataset_name=dataset_name
        )

        self.log(f"\n{'='*60}")
        self.log(f"Validating dataset: {dataset_name}")
        self.log(f"{'='*60}")

        export_json_path = dataset_path / "export.json"
        if not export_json_path.exists():
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message="export.json file not found",
                file_path=self._make_relative_path(export_json_path)
            ))
            return result

        # Validate export.json structure and content
        export_data = self._validate_export_json(export_json_path, result)
        if not export_data:
            return result

        # Parse object configurations
        object_configs = self._parse_object_configs(export_data)
        result.objects_validated = len(object_configs)

        # Find per-pass CSV overrides
        objectset_source_overrides = self._find_objectset_source_overrides(dataset_path, export_data)

        # Apply fixes if requested (before validation)
        if self.fix_headers or self.fix_composite_keys:
            self.log(f"\n{'='*60}")
            self.log(f"Applying fixes to: {dataset_name}")
            self.log(f"{'='*60}")
            headers_fixed, composite_keys_fixed = self.fix_dataset_issues(dataset_path, object_configs)

            # Also fix per-pass CSVs
            if objectset_source_overrides:
                self.log(f"Fixing {len(objectset_source_overrides)} per-pass CSV(s)")
                for (obj_name, pass_index), (csv_path, _) in objectset_source_overrides.items():
                    obj_config = self._get_object_config_for_pass(export_data, obj_name, pass_index)
                    if obj_config:
                        # Apply header fix if needed
                        if self.fix_headers and self._is_csv_empty(csv_path):
                            headers = obj_config.get("fields", [])
                            if self._fix_empty_csv_header(csv_path, headers, obj_name):
                                headers_fixed += 1

                        # Apply composite key fix if needed
                        if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                            external_id = obj_config.get("externalId", "")
                            if ";" in external_id and not external_id.startswith("$$"):
                                fields = [f.strip() for f in external_id.split(";")]
                                composite_col_name = self._build_composite_key_column_name(fields)

                                # Check if column is missing using helper method
                                if self._csv_missing_composite_key(csv_path, composite_col_name):
                                    if self._fix_missing_composite_key(csv_path, fields, obj_name):
                                        composite_keys_fixed += 1

            if headers_fixed > 0 or composite_keys_fixed > 0:
                print(f"\n  Fixed {headers_fixed} header(s) and {composite_keys_fixed} composite key column(s)")

        # Validate each object's CSV and composite key configuration
        for obj_name, obj_config in object_configs.items():
            self._validate_object(dataset_path, obj_name, obj_config, result)

        # Validate per-pass CSV overrides
        if objectset_source_overrides:
            self.log(f"\nValidating {len(objectset_source_overrides)} per-pass CSV override(s)")
            for (obj_name, pass_index), (csv_path, _) in objectset_source_overrides.items():
                obj_config = self._get_object_config_for_pass(export_data, obj_name, pass_index)
                if obj_config:
                    self._validate_per_pass_csv(csv_path, obj_name, pass_index, obj_config, result)
                else:
                    result.add_issue(Issue(
                        severity=Severity.HIGH,
                        object_name=obj_name,
                        message=f"Per-pass CSV found but no matching object in pass {pass_index + 1}",
                        file_path=self._make_relative_path(csv_path)
                    ))

        self.log(f"\nValidation complete for {dataset_name}")
        self.log(f"Objects validated: {result.objects_validated}")
        self.log(f"Issues found: {len(result.issues)}")

        return result

    def _validate_export_json(self, export_json_path: Path, result: ValidationResult) -> Optional[dict]:
        """Validate export.json file structure and format.

        Args:
            export_json_path: Path to export.json
            result: ValidationResult to add issues to

        Returns:
            Parsed export.json data, or None if critical error
        """
        self.log(f"Validating export.json: {export_json_path}")

        try:
            with open(export_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message=f"Invalid JSON: {e}",
                file_path=self._make_relative_path(export_json_path),
                line_number=getattr(e, 'lineno', None)
            ))
            return None
        except Exception as e:
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message=f"Error reading export.json: {e}",
                file_path=self._make_relative_path(export_json_path)
            ))
            return None

        # Check required fields
        if "apiVersion" not in data:
            result.add_issue(Issue(
                severity=Severity.HIGH,
                object_name="N/A",
                message="Missing 'apiVersion' field in export.json",
                file_path=self._make_relative_path(export_json_path)
            ))

        # Must have either objects or objectSets
        has_objects = "objects" in data and isinstance(data["objects"], list)
        has_object_sets = "objectSets" in data and isinstance(data["objectSets"], list)

        if not has_objects and not has_object_sets:
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message="export.json must have either 'objects' or 'objectSets' array",
                file_path=self._make_relative_path(export_json_path)
            ))
            return None

        self.log(f"export.json structure valid, contains {len(data.get('objects', [])) + sum(len(obj_set.get('objects', [])) for obj_set in data.get('objectSets', []))} object configurations")

        return data

    def _parse_object_configs(self, export_data: dict) -> Dict[str, dict]:
        """Parse export.json into object name -> config mapping.

        Args:
            export_data: Parsed export.json data

        Returns:
            Dictionary mapping object API name to configuration
        """
        configs = {}

        # Handle both objectSets (multi-pass) and flat objects (single-pass)
        object_sets = export_data.get("objectSets", [])
        if not object_sets and "objects" in export_data:
            object_sets = [{"objects": export_data["objects"]}]

        for idx, obj_set in enumerate(object_sets):
            for obj in obj_set.get("objects", []):
                query = obj.get("query", "")
                obj_name = self._extract_object_name(query)

                if not obj_name:
                    continue

                # Store first pass configuration (later passes may be activations)
                if obj_name not in configs:
                    configs[obj_name] = {
                        "pass_index": idx,
                        "operation": obj.get("operation", "Upsert"),
                        "externalId": obj.get("externalId", "Id"),
                        "query": query,
                        "fields": self._parse_select_fields(query),
                        "excluded": obj.get("excluded", False),
                        "deleteOldData": obj.get("deleteOldData", False),
                        "skipExistingRecords": obj.get("skipExistingRecords", False),
                    }

        return configs

    def _extract_object_name(self, query: str) -> str:
        """Extract object API name from SOQL query.

        Args:
            query: SOQL query string

        Returns:
            Object API name, or empty string if not found
        """
        match = re.search(r'\sFROM\s+(\w+)', query, re.IGNORECASE)
        return match.group(1) if match else ""

    def _parse_select_fields(self, query: str) -> List[str]:
        """Parse field names from SOQL SELECT clause.

        Args:
            query: SOQL query string

        Returns:
            List of field names (including relationship traversals like Product.Name)
        """
        match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not match:
            return []

        fields_str = match.group(1)
        # Split by comma, strip whitespace
        fields = [f.strip() for f in fields_str.split(',')]
        return fields

    def _find_objectset_source_overrides(self, dataset_path: Path, export_data: dict) -> Dict[Tuple[str, int], Tuple[Path, int]]:
        """Find per-pass CSV overrides in objectset_source/object-set-N/.

        Args:
            dataset_path: Path to dataset directory
            export_data: Parsed export.json data

        Returns:
            Dictionary mapping (object_name, pass_index) -> (csv_path, pass_index)
            Example: {("BillingTreatmentItem", 1): (Path(".../object-set-2/BillingTreatmentItem.csv"), 1)}
        """
        overrides = {}
        objectset_source_dir = dataset_path / "objectset_source"

        if not objectset_source_dir.exists():
            return overrides

        # Find all object-set-N directories
        for obj_set_dir in sorted(objectset_source_dir.glob("object-set-*")):
            if not obj_set_dir.is_dir():
                continue

            # Extract pass number from directory name (object-set-2 -> pass_index 1)
            match = re.match(r"object-set-(\d+)", obj_set_dir.name)
            if not match:
                continue

            pass_number = int(match.group(1))  # 1-based
            pass_index = pass_number - 1  # Convert to 0-based index for objectSets array

            # Check if this pass exists in export.json
            object_sets = export_data.get("objectSets", [])
            if pass_index >= len(object_sets):
                self.log(f"Warning: {obj_set_dir.name} has no corresponding pass in export.json", level="WARN")
                continue

            # Find all CSVs in this directory
            for csv_path in obj_set_dir.glob("*.csv"):
                obj_name = csv_path.stem  # Remove .csv extension
                overrides[(obj_name, pass_index)] = (csv_path, pass_index)
                self.log(f"Found override: {obj_name} in pass {pass_number} (index {pass_index})", level="DEBUG")

        return overrides

    def _get_object_config_for_pass(self, export_data: dict, obj_name: str, pass_index: int) -> Optional[dict]:
        """Get object configuration for a specific pass.

        Args:
            export_data: Parsed export.json data
            obj_name: Object API name
            pass_index: 0-based pass index

        Returns:
            Object configuration dict, or None if not found
        """
        object_sets = export_data.get("objectSets", [])
        if pass_index >= len(object_sets):
            return None

        for obj in object_sets[pass_index].get("objects", []):
            query = obj.get("query", "")
            if self._extract_object_name(query) == obj_name:
                # Parse the config similar to _parse_object_configs
                return {
                    "pass_index": pass_index,
                    "operation": obj.get("operation", "Upsert"),
                    "externalId": obj.get("externalId", "Id"),
                    "query": query,
                    "fields": self._parse_select_fields(query),
                    "excluded": obj.get("excluded", False),
                    "deleteOldData": obj.get("deleteOldData", False),
                    "skipExistingRecords": obj.get("skipExistingRecords", False),
                }

        return None

    def _validate_per_pass_csv(self, csv_path: Path, obj_name: str, pass_index: int,
                               obj_config: dict, result: ValidationResult):
        """Validate a per-pass CSV override in objectset_source/object-set-N/.

        Args:
            csv_path: Path to the CSV file
            obj_name: Object API name
            pass_index: 0-based pass index
            obj_config: Object configuration for this pass
            result: ValidationResult to add issues to
        """
        pass_name = f"Pass {pass_index + 1}"
        self.log(f"\nValidating {pass_name} override: {obj_name} ({csv_path.name})", level="DEBUG")

        # Skip excluded objects
        if obj_config.get("excluded"):
            self.log(f"  Skipping excluded object in {pass_name}: {obj_name}", level="DEBUG")
            return

        # Validate externalId format (reuse existing method)
        external_id = obj_config.get("externalId", "")
        self._validate_external_id(obj_name, external_id, obj_config, result)

        # Validate CSV file with pass context
        self._validate_csv_file(csv_path, obj_name, obj_config, result, pass_index=pass_index)

    def _validate_object(self, dataset_path: Path, obj_name: str, obj_config: dict, result: ValidationResult):
        """Validate a single object's CSV and configuration.

        Args:
            dataset_path: Path to dataset directory
            obj_name: Object API name
            obj_config: Object configuration from export.json
            result: ValidationResult to add issues to
        """
        self.log(f"\nValidating object: {obj_name}", level="DEBUG")

        # Skip excluded objects
        if obj_config.get("excluded"):
            self.log(f"  Skipping excluded object: {obj_name}", level="DEBUG")
            if obj_name not in self.KNOWN_EXCLUDED_OBJECTS:
                result.add_issue(Issue(
                    severity=Severity.INFO,
                    object_name=obj_name,
                    message=f"Object is excluded but not in known excluded list"
                ))
            return

        # Validate externalId format
        external_id = obj_config.get("externalId", "")
        self._validate_external_id(obj_name, external_id, obj_config, result)

        # Validate CSV file
        csv_path = dataset_path / f"{obj_name}.csv"
        self._validate_csv_file(csv_path, obj_name, obj_config, result)

        # Check deleteOldData usage
        if obj_config.get("deleteOldData"):
            if obj_name not in self.DELETE_OLD_DATA_OBJECTS:
                result.add_issue(Issue(
                    severity=Severity.INFO,
                    object_name=obj_name,
                    message=f"Object uses 'deleteOldData: true' but not in documented list"
                ))

    def _validate_external_id(self, obj_name: str, external_id: str, obj_config: dict, result: ValidationResult):
        """Validate externalId format and structure.

        Args:
            obj_name: Object API name
            external_id: externalId value from export.json
            obj_config: Object configuration
            result: ValidationResult to add issues to
        """
        if not external_id or external_id == "Id":
            return

        # Check for legacy $$ notation in externalId definition
        if "$$" in external_id:
            result.add_issue(Issue(
                severity=Severity.MEDIUM,
                object_name=obj_name,
                message=f"externalId uses legacy $$ notation: '{external_id}'. SFDMU v5 requires semicolon-delimited format (e.g., 'Field1;Field2')"
            ))

        # Check for nested relationship paths (v5 flattening issue)
        fields = external_id.split(";")
        for field in fields:
            # Count dots (more than 1 = nested relationship)
            dot_count = field.count(".")
            if dot_count > 1:
                result.add_issue(Issue(
                    severity=Severity.MEDIUM,
                    object_name=obj_name,
                    message=f"externalId contains nested relationship path '{field}' which may cause v5 flattening errors"
                ))

        # Validate that composite key components are in the query
        if ";" in external_id:
            query_fields = set(obj_config.get("fields", []))
            for field in fields:
                # Check if the field or its base is in the query
                if field not in query_fields:
                    # For relationship fields like Parent.Name, check if it's in query
                    base_match = any(qf.startswith(field.split(".")[0]) for qf in query_fields)
                    if not base_match:
                        result.add_issue(Issue(
                            severity=Severity.HIGH,
                            object_name=obj_name,
                            message=f"externalId component '{field}' not found in query SELECT clause"
                        ))

    def _validate_csv_file(self, csv_path: Path, obj_name: str, obj_config: dict, result: ValidationResult, pass_index: Optional[int] = None):
        """Validate CSV file existence, headers, and composite key columns.

        Args:
            csv_path: Path to CSV file
            obj_name: Object API name
            obj_config: Object configuration
            result: ValidationResult to add issues to
            pass_index: Optional 0-based pass index for per-pass CSV context
        """
        # Create pass prefix for issue messages
        pass_prefix = f"Pass {pass_index + 1}: " if pass_index is not None else ""

        # Check if CSV file exists
        if not csv_path.exists():
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name=obj_name,
                message=f"{pass_prefix}CSV file not found: {csv_path.name}",
                file_path=self._make_relative_path(csv_path)
            ))
            return

        # Read CSV to check headers and content
        try:
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                try:
                    headers = next(reader)
                except StopIteration:
                    # Empty file
                    if obj_name in self.KNOWN_EMPTY_CSV_OBJECTS:
                        result.add_issue(Issue(
                            severity=Severity.HIGH,
                            object_name=obj_name,
                            message=f"{pass_prefix}CSV file is completely empty (no header row). Add header row with fields from query.",
                            file_path=self._make_relative_path(csv_path)
                        ))
                    else:
                        result.add_issue(Issue(
                            severity=Severity.CRITICAL,
                            object_name=obj_name,
                            message=f"{pass_prefix}CSV file is completely empty (no header row)",
                            file_path=self._make_relative_path(csv_path)
                        ))
                    return

                # Normalize headers (strip BOM, quotes, whitespace)
                headers = [self._normalize_header(h) for h in headers]

                # Count data rows
                data_row_count = sum(1 for _ in reader)

                self.log(f"  CSV has {len(headers)} columns, {data_row_count} data rows", level="DEBUG")

                # Check if this is a known empty CSV (0 data rows)
                if data_row_count == 0 and obj_name in self.KNOWN_EMPTY_CSV_OBJECTS:
                    self.log(f"  Object {obj_name} has 0 data rows (known placeholder)", level="DEBUG")

                # Validate composite key columns for objects with multi-field externalId
                external_id = obj_config.get("externalId", "")
                if ";" in external_id and not external_id.startswith("$$"):
                    # This is a composite key - check if CSV has the $$ column
                    expected_composite_col = "$$" + "$".join(external_id.split(";"))

                    if expected_composite_col not in headers:
                        result.add_issue(Issue(
                            severity=Severity.HIGH,
                            object_name=obj_name,
                            message=f"{pass_prefix}CSV missing composite key column '{expected_composite_col}' for externalId '{external_id}'. This will break re-import idempotency in SFDMU v5.",
                            file_path=self._make_relative_path(csv_path)
                        ))
                    else:
                        self.log(f"  Composite key column '{expected_composite_col}' found", level="DEBUG")

        except Exception as e:
            result.add_issue(Issue(
                severity=Severity.HIGH,
                object_name=obj_name,
                message=f"{pass_prefix}Error reading CSV: {type(e).__name__}: {e}",
                file_path=self._make_relative_path(csv_path)
            ))

    def _normalize_header(self, header: str) -> str:
        """Normalize CSV header (strip BOM, quotes, whitespace).

        Args:
            header: Raw header string

        Returns:
            Normalized header string
        """
        if not header:
            return header

        # Strip BOM and whitespace
        h = header.lstrip("\ufeff").strip()

        # Strip surrounding quotes
        if len(h) >= 2 and h[0] == '"' and h[-1] == '"':
            h = h[1:-1].strip()

        return h

    def _is_csv_empty(self, csv_path: Path) -> bool:
        """Check if a CSV file is completely empty (0 bytes or no content).

        Args:
            csv_path: Path to CSV file

        Returns:
            True if file is empty, False otherwise
        """
        if not csv_path.exists():
            return False

        # Check file size
        if csv_path.stat().st_size == 0:
            return True

        # Check if file has any non-whitespace content
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                return len(content) == 0
        except Exception:
            return False

    def _csv_missing_composite_key(self, csv_path: Path, composite_col_name: str) -> bool:
        """Check if CSV is missing the composite key column.

        Args:
            csv_path: Path to CSV file
            composite_col_name: Name of composite key column to check

        Returns:
            True if column is missing, False if present or on error
        """
        try:
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                normalized_headers = [self._normalize_header(h) for h in headers]
                return composite_col_name not in normalized_headers
        except Exception:
            return False

    def _fix_empty_csv_header(self, csv_path: Path, headers: List[str], obj_name: str) -> bool:
        """Add header row to an empty CSV file.

        Args:
            csv_path: Path to CSV file
            headers: List of header names
            obj_name: Object name for logging

        Returns:
            True if header was added (or would be added in dry-run), False otherwise
        """
        if not self._is_csv_empty(csv_path):
            return False

        if self.dry_run:
            print(f"  [DRY-RUN] Would add header to: {csv_path.name}")
            print(f"            Headers: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
            return True

        try:
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"  ✅ Added header to: {csv_path.name} ({len(headers)} columns)")
            self.fixes_applied["headers"] += 1
            return True
        except PermissionError:
            print(f"  ❌ Permission denied writing {csv_path.name}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  ❌ Error writing {csv_path.name}: {type(e).__name__}: {e}", file=sys.stderr)
            return False

    def _build_composite_key_column_name(self, fields: List[str]) -> str:
        """Build the $$Field1$Field2 column name from field list.

        Args:
            fields: List of field names (e.g., ['Name', 'LegalEntity.Name'])

        Returns:
            Composite key column name (e.g., '$$Name$LegalEntity.Name')
        """
        return "$$" + "$".join(fields)

    def _build_composite_key_value(self, row: dict, fields: List[str]) -> str:
        """Build composite key value from row data.

        Args:
            row: Dictionary of row data
            fields: List of field names to concatenate

        Returns:
            Composite key value with semicolon separators
        """
        values = [str(row.get(field, "")) for field in fields]
        return ";".join(values)

    def _fix_missing_composite_key(self, csv_path: Path, fields: List[str], obj_name: str) -> bool:
        """Add composite key column to a CSV file.

        Args:
            csv_path: Path to CSV file
            fields: List of field names for composite key
            obj_name: Object name for logging

        Returns:
            True if column was added, False otherwise
        """
        if not csv_path.exists():
            return False

        composite_col_name = self._build_composite_key_column_name(fields)

        # Read existing CSV
        try:
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                headers = list(reader.fieldnames) if reader.fieldnames else []
                rows = list(reader)
        except PermissionError:
            print(f"  ❌ Permission denied reading {csv_path.name}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  ❌ Error reading {csv_path.name}: {type(e).__name__}: {e}", file=sys.stderr)
            return False

        if not headers:
            return False

        # Check if composite key column already exists
        if composite_col_name in headers:
            return False

        # Check if all component fields exist
        missing_fields = [f for f in fields if f not in headers]
        if missing_fields:
            self.log(f"  ⚠️  Warning: Missing component fields for {obj_name}: {', '.join(missing_fields)}", level="WARN")
            # Continue anyway - we'll use empty values for missing fields

        if self.dry_run:
            print(f"  [DRY-RUN] Would add composite key column to: {csv_path.name}")
            print(f"            Column: {composite_col_name}")
            return True

        # Build new rows with composite key column as first column
        new_headers = [composite_col_name] + headers
        new_rows = []

        for row in rows:
            composite_value = self._build_composite_key_value(row, fields)
            new_row = {composite_col_name: composite_value}
            new_row.update(row)
            new_rows.append(new_row)

        # Write updated CSV
        try:
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=new_headers)
                writer.writeheader()
                writer.writerows(new_rows)
            print(f"  ✅ Added composite key column to: {csv_path.name} ({len(new_rows)} rows)")
            self.fixes_applied["composite_keys"] += 1
            return True
        except PermissionError:
            print(f"  ❌ Permission denied writing {csv_path.name}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  ❌ Error writing {csv_path.name}: {type(e).__name__}: {e}", file=sys.stderr)
            return False

    def fix_dataset_issues(self, dataset_path: Path, object_configs: Dict[str, dict]) -> Tuple[int, int]:
        """Fix issues in a dataset (headers and/or composite keys).

        Args:
            dataset_path: Path to dataset directory
            object_configs: Object configurations from export.json

        Returns:
            Tuple of (headers_fixed, composite_keys_fixed)
        """
        headers_fixed = 0
        composite_keys_fixed = 0

        for obj_name, obj_config in object_configs.items():
            if obj_config.get("excluded"):
                continue

            csv_path = dataset_path / f"{obj_name}.csv"
            if not csv_path.exists():
                continue

            # Fix missing headers
            if self.fix_headers and self._is_csv_empty(csv_path):
                headers = obj_config.get("fields", [])
                if self._fix_empty_csv_header(csv_path, headers, obj_name):
                    headers_fixed += 1

            # Fix missing composite keys (only if CSV is not empty)
            if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                external_id = obj_config.get("externalId", "")
                if ";" in external_id and not external_id.startswith("$$"):
                    fields = [f.strip() for f in external_id.split(";")]
                    composite_col_name = self._build_composite_key_column_name(fields)

                    # Check if column is missing using helper method
                    if self._csv_missing_composite_key(csv_path, composite_col_name):
                        if self._fix_missing_composite_key(csv_path, fields, obj_name):
                            composite_keys_fixed += 1

        return headers_fixed, composite_keys_fixed

    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate a markdown validation report.

        Args:
            results: List of ValidationResult objects

        Returns:
            Markdown-formatted report string
        """
        # Count issues by severity
        severity_counts = {s: 0 for s in Severity}
        for result in results:
            for issue in result.issues:
                severity_counts[issue.severity] += 1

        # Count passed/failed datasets
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        # Build report
        lines = []
        lines.append("# SFDMU v5 Dataset Validation Report\n")
        lines.append(f"**Generated:** {self._get_timestamp()}\n")
        lines.append("## Summary\n")
        lines.append(f"- **Total datasets validated:** {len(results)}")
        lines.append(f"- **Passed:** {passed}")
        lines.append(f"- **Failed:** {failed}")
        lines.append(f"- **Total objects validated:** {sum(r.objects_validated for r in results)}")
        lines.append(f"- **Total issues found:** {len([i for r in results for i in r.issues])}\n")

        lines.append("### Issues by Severity\n")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.INFO]:
            lines.append(f"| {severity.value} | {severity_counts[severity]} |")
        lines.append("")

        lines.append("## Dataset Results\n")
        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"### {status} {result.dataset_name}\n")
            # Dataset path is already stored as relative, use as-is
            lines.append(f"- **Path:** `{result.dataset_path}`")
            lines.append(f"- **Objects validated:** {result.objects_validated}")
            lines.append(f"- **Issues found:** {len(result.issues)}\n")

            if result.issues:
                # Group issues by severity
                for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.INFO]:
                    severity_issues = [i for i in result.issues if i.severity == severity]
                    if severity_issues:
                        lines.append(f"#### {severity.value} Issues ({len(severity_issues)})\n")
                        for issue in severity_issues:
                            # File path is already stored as relative, use as-is
                            location = f" ({issue.file_path})" if issue.file_path else ""
                            lines.append(f"- **{issue.object_name}**: {issue.message}{location}")
                        lines.append("")

        return "\n".join(lines)

    def _get_timestamp(self) -> str:
        """Get current timestamp for report."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate SFDMU v5 datasets for composite key compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all SFDMU datasets
  python scripts/validate_sfdmu_v5_datasets.py

  # Validate single dataset with verbose output
  python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-pcm --verbose

  # Run in strict mode (warnings as errors)
  python scripts/validate_sfdmu_v5_datasets.py --strict
        """
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to a dataset directory or parent directory (recursively finds all datasets within)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (Medium severity) as errors"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed validation steps"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write report to file (default: print to stdout)"
    )
    parser.add_argument(
        "--fix-headers",
        action="store_true",
        help="Add missing headers to empty CSV files"
    )
    parser.add_argument(
        "--fix-composite-keys",
        action="store_true",
        help="Add missing composite key columns to CSVs"
    )
    parser.add_argument(
        "--fix-all",
        action="store_true",
        help="Enable all fixes (headers + composite keys)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )

    args = parser.parse_args()

    # Handle --fix-all flag
    if args.fix_all:
        args.fix_headers = True
        args.fix_composite_keys = True

    # Determine base directory (script location -> project root)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    validator = SFDMUValidator(
        str(base_dir),
        strict=args.strict,
        verbose=args.verbose,
        fix_headers=args.fix_headers,
        fix_composite_keys=args.fix_composite_keys,
        dry_run=args.dry_run
    )

    # Find datasets to validate
    if args.dataset:
        dataset_path = Path(args.dataset)
        if not dataset_path.is_absolute():
            dataset_path = base_dir / dataset_path

        if not dataset_path.exists():
            print(f"Error: Dataset path not found: {args.dataset}", file=sys.stderr)
            return 1

        # Check if this is a single dataset or a parent directory
        if (dataset_path / "export.json").exists():
            # Single dataset
            datasets = [dataset_path]
        else:
            # Parent directory - find all datasets recursively
            datasets = []
            for export_json in dataset_path.rglob("export.json"):
                dataset_dir = export_json.parent
                # Skip if it's in a subdirectory like objectset_source or processed
                if any(p in export_json.parts for p in ["objectset_source", "processed", "source", "logs"]):
                    continue
                datasets.append(dataset_dir)
            datasets = sorted(datasets)

            if not datasets:
                print(f"Error: No SFDMU datasets found in: {args.dataset}", file=sys.stderr)
                return 1
    else:
        datasets = validator.find_sfdmu_datasets()
        if not datasets:
            print("Error: No SFDMU datasets found in datasets/sfdmu/", file=sys.stderr)
            return 1

    print(f"\nFound {len(datasets)} dataset(s) to validate\n")

    # Validate all datasets
    results = []
    for dataset_path in datasets:
        result = validator.validate_dataset(dataset_path)
        results.append(result)

    # Generate report
    report = validator.generate_report(results)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding='utf-8')
        print(f"\nReport written to: {output_path}")
    else:
        print("\n" + "="*80)
        print(report)

    # Show fix summary if fixes were applied
    if args.fix_headers or args.fix_composite_keys:
        print(f"\n{'='*80}")
        print("Fix Summary")
        print(f"{'='*80}")
        print(f"Headers added: {validator.fixes_applied['headers']}")
        print(f"Composite key columns added: {validator.fixes_applied['composite_keys']}")
        if args.dry_run:
            print("\n⚠️  This was a dry-run. Run without --dry-run to apply changes.")

    # Determine exit code
    has_critical_or_high = any(
        issue.severity in (Severity.CRITICAL, Severity.HIGH)
        for result in results
        for issue in result.issues
    )

    has_medium = any(
        issue.severity == Severity.MEDIUM
        for result in results
        for issue in result.issues
    )

    if has_critical_or_high:
        print("\n❌ Validation FAILED (Critical or High severity issues found)")
        return 1
    elif args.strict and has_medium:
        print("\n❌ Validation FAILED (Medium severity issues found in strict mode)")
        return 1
    else:
        print("\n✅ Validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
