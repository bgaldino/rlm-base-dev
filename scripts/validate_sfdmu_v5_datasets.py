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


# Path segments (relative to the scan root) that mark a directory we never validate:
# internal SFDMU subdirs, developer-local scratch (test/), and backup dirs (*.bak).
_SKIP_SEGMENTS = ("objectset_source", "processed", "source", "logs", "test")


def _is_skippable_export(export_json: Path, root: Path) -> bool:
    """Return True if an export.json found under ``root`` should be skipped.

    The skip filters are applied to the path RELATIVE TO ``root`` (the SFDMU base
    or the ``--dataset`` parent), not the absolute filesystem path. Otherwise a
    checkout directory literally named, e.g., ``test`` or ``source`` (such as
    ``/tmp/test/rlm-base-dev``) would wrongly filter out every shipped dataset.
    """
    try:
        rel_parts = export_json.relative_to(root).parts
    except ValueError:
        rel_parts = export_json.parts
    if any(seg in _SKIP_SEGMENTS for seg in rel_parts):
        return True
    return any(seg.endswith(".bak") for seg in rel_parts)


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
        """Add an issue, ignoring one identical to an issue already recorded.

        Identical means same object, severity, message and file — indistinguishable to a reader, so
        two of them read as two defects when there is one. The dedup lives here rather than at the
        call sites because the checks now run **per declaration**: an object declared in several
        passes is validated once per pass, and a finding that does not depend on the differing field
        is emitted once per pass. `qb-prm-pricing/Account` produced two identical
        `CSV file not found` Criticals that way, and no choice of config-dedup key can prevent it —
        the two declarations genuinely differ, while the *finding* does not depend on how.

        That matters beyond tidiness: the High count is pinned by `tests/test_sfdmu_csv_expectation.py`
        and quoted in several documents, so a count that scales with pass multiplicity stops counting
        defects. Deduping here makes every future per-declaration loop safe by construction instead of
        correct by inspection.
        """
        if any(i.severity == issue.severity and i.object_name == issue.object_name
               and i.message == issue.message and i.file_path == issue.file_path
               for i in self.issues):
            return
        self.issues.append(issue)
        if issue.severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM):
            self.passed = False


class SFDMUValidator:
    """Validator for SFDMU v5 datasets."""

    # Known objects that use deleteOldData strategy (from sfdmu_composite_key_optimizations.md)
    DELETE_OLD_DATA_OBJECTS = {
        "FulfillmentWorkspaceItem",
        "PriceBookRateCard",
        "RateCardEntry",
        "RateAdjustmentByTier",
        # MFG AAF — forecast facts use deleteOldData for full refresh
        "AdvAccountForecastFact",
        "AdvAcctForecastSetPartner",
        # Guided selling — OmniProcess/AssessmentQuestion objects require deleteOldData
        # due to complex self-referential keys that SFDMU v5 cannot upsert safely
        "AssessmentQuestionAssignment",
        "AssessmentQuestionVersion",
        "OmniProcessElement",
        "OmniProcessAsmtQuestionVer",
        # Rating usage grants require deleteOldData due to composite key structure
        "ProductUsageResource",
        "ProductUsageResourcePolicy",
        "ProductUsageGrant",
    }

    # Known excluded objects (from optimization doc)
    KNOWN_EXCLUDED_OBJECTS = {
        "PricebookEntryDerivedPrice",
        "ProductUsageResourcePolicy",
        "ProductUsageGrant",
        "ProductDecompEnrichmentRule",
        "ProductComponentGrpOverride",
        "ProductRelComponentOverride",
        # CostBookEntry excluded in qb-pricing (no cost book data in base dataset)
        "CostBookEntry",
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
            # Skip internal subdirs, developer-local scratch (test/), and backup dirs (*.bak).
            # Filter on the path relative to sfdmu_base so the checkout path can't matter.
            if _is_skippable_export(export_json, self.sfdmu_base):
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
        objectset_source_overrides = self._find_objectset_source_overrides(dataset_path, export_data, result)

        # Computed once and reused below for both the fixer and the main validate loop:
        # `export_data`/`objectset_source_overrides` are both already fixed at this point, so a
        # second call to either would re-walk the same deterministic per-pass traversal for an
        # identical answer.
        all_pass_configs = self._all_pass_configs(export_data)
        # Hoisted alongside `all_pass_configs` for the same reason: both the fixer block and the
        # per-pass validate loop below recomputed this identical `bool(...)` independently, and
        # `_objects_owing_root_csv` recomputed it a third time internally — three places to
        # disagree if this flag's interpretation ever grows a second condition.
        use_separated_csv_files = self._is_js_truthy(export_data.get("useSeparatedCSVFiles"))
        objects_owing_root_csv = self._objects_owing_root_csv(objectset_source_overrides,
                                                              all_pass_configs,
                                                              use_separated_csv_files)

        # Apply fixes if requested (before validation)
        if self.fix_headers or self.fix_composite_keys:
            self.log(f"\n{'='*60}")
            self.log(f"Applying fixes to: {dataset_name}")
            self.log(f"{'='*60}")
            headers_fixed, composite_keys_fixed = self.fix_dataset_issues(
                dataset_path, object_configs, objects_owing_root_csv)

            # Also fix per-pass CSVs
            if objectset_source_overrides:
                self.log(f"Fixing {len(objectset_source_overrides)} per-pass CSV(s)")
                # Same gate as the validation loop below: a pass 2+ override is inert without
                # `useSeparatedCSVFiles`, so writing into it is a fix nothing reads.
                for (obj_name, pass_index), (csv_path, _) in objectset_source_overrides.items():
                    if not self._override_content_should_be_checked(pass_index, use_separated_csv_files):
                        continue
                    writable_cfgs = self._writable_configs_for_pass(all_pass_configs, obj_name, pass_index)
                    # Same bookkeeping the root fixer uses. `--dry-run` does not mutate the file, so
                    # `_is_csv_empty` / `_csv_missing_composite_key` stay true across same-pass
                    # duplicate declarations and each one printed/counted a proposal a real run
                    # would apply only once. The header is written once, from the union of every
                    # writable declaration's fields — see `_union_fields` for why a single
                    # declaration's fields are not enough.
                    columns_written = set()
                    if self.fix_headers and writable_cfgs and self._is_csv_empty(csv_path):
                        headers = self._union_fields(writable_cfgs)
                        if self._fix_empty_csv_header(csv_path, headers, obj_name):
                            headers_fixed += 1

                    for obj_config in writable_cfgs:
                        if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                            external_id = obj_config.get("externalId", "")
                            if self._owes_composite_key_column(external_id, obj_config):
                                fields = self._split_external_id_fields(external_id)
                                composite_col_name = self._build_composite_key_column_name(fields)
                                if (composite_col_name not in columns_written
                                        and self._csv_missing_composite_key(csv_path, composite_col_name)):
                                    if self._fix_missing_composite_key(csv_path, fields, obj_name):
                                        composite_keys_fixed += 1
                                        columns_written.add(composite_col_name)

            if headers_fixed > 0 or composite_keys_fixed > 0:
                print(f"\n  Fixed {headers_fixed} header(s) and {composite_keys_fixed} composite key column(s)")

        # Validate each object's CSV and composite key configuration
        for obj_name in object_configs:
            self._validate_object(dataset_path, obj_name, result,
                                  objects_owing_root_csv, all_pass_configs)

        # Validate per-pass CSV overrides
        if objectset_source_overrides:
            self.log(f"\nValidating {len(objectset_source_overrides)} per-pass CSV override(s)")
            # `_objects_owing_root_csv` applies the same flag to *coverage*: SFDMU substitutes
            # object-set-N (N>1) for the plan root only when it is true (`Script.js`'s
            # `rawSourceDirectoryPath`) — pass 1's own object-set-1 directory has no such gate. Below,
            # the gate is scoped to the CONTENT check only (empty file, missing composite key), not
            # to the directory-to-pass mapping sanity checks above it: a misfiled override — a CSV
            # sitting in a pass that does not even declare the object — is a naming/authoring mistake
            # worth flagging regardless of whether this flag happens to be set right now, the same
            # reason the object-set-0 and non-canonical-directory checks elsewhere are unconditional.
            # A pass 2+ override without the flag is never read by SFDMU at runtime, so validating
            # its *content* against a file nothing loads is the false positive pack 123 exists to
            # eliminate — but the directory being wrong is not a fact about runtime reads.
            for (obj_name, pass_index), (csv_path, _) in objectset_source_overrides.items():
                declared = self._get_object_configs_for_pass(all_pass_configs, obj_name, pass_index)
                if not declared:
                    result.add_issue(Issue(
                        severity=Severity.HIGH,
                        object_name=obj_name,
                        message=f"Per-pass CSV found but no matching object in pass {pass_index + 1}",
                        file_path=self._make_relative_path(csv_path)
                    ))
                    continue
                if not self._override_content_should_be_checked(pass_index, use_separated_csv_files):
                    self.log(f"  Skipping content check on inert override (useSeparatedCSVFiles is "
                             f"not true): {obj_name} pass {pass_index + 1}", level="DEBUG")
                    continue
                writable_cfgs = self._writable_configs_for_pass(all_pass_configs, obj_name, pass_index)
                if not writable_cfgs:
                    # `declared` is non-empty but every declaration in this pass is Readonly/excluded
                    # — SFDMU queries a Readonly object from the target org and never reads a file
                    # for it, so this override is dead weight, not a defect worth a finding. Logged
                    # rather than silently falling out of the loop: the "flag not true" skip above
                    # gets a DEBUG line, and a reader diagnosing "0 issues" for a suspicious file
                    # deserves the same signal for this skip, not silence indistinguishable from
                    # "nothing to check here."
                    self.log(f"  Skipping content check on Readonly/excluded override (no live "
                             f"writable declaration): {obj_name} pass {pass_index + 1}", level="DEBUG")
                    continue
                for obj_config in writable_cfgs:
                    self._validate_per_pass_csv(csv_path, obj_name, pass_index, obj_config, result)

        self.log(f"\nValidation complete for {dataset_name}")
        self.log(f"Objects validated: {result.objects_validated}")
        self.log(f"Issues found: {len(result.issues)}")

        return result

    @staticmethod
    def _reject_non_finite_json_constant(token: str):
        """Reject `NaN`/`Infinity`/`-Infinity` the way SFDMU's own loader would.

        SFDMU loads export.json with JavaScript's `JSON.parse` (`ScriptLoader.js:54`, confirmed
        against the installed `sfdmu@5.8.0` source), which treats a bare `NaN`/`Infinity`/
        `-Infinity` token as a syntax error — the file never loads. Python's `json` module accepts
        all three as an extension by default (`json.load`'s `parse_constant`), so without this
        guard the validator could load and evaluate a plan SFDMU itself would refuse outright.
        Passed as `json.load`'s `parse_constant` callback; raising here surfaces as the same
        "Error reading export.json" Critical any other unreadable file gets.
        """
        raise ValueError(
            f"{token} is not valid JSON — SFDMU loads export.json with JavaScript's JSON.parse, "
            f"which rejects non-finite numeric constants outright, unlike Python's json module"
        )

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
                data = json.load(f, parse_constant=self._reject_non_finite_json_constant)
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

        if not isinstance(data, dict):
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message=(f"export.json root is {type(data).__name__}, not an object — "
                         f"a JSON object is required"),
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

        # Present container types, not just "is either a list". A sibling being a valid list used to
        # skip the other: `{"objects": 7, "objectSets": []}` passed the either-array check (objectSets
        # is a list) then `enumerate(data.get("objects") or [])` raised `TypeError` — `7 or []` is 7 —
        # and `main()` does not catch per-plan exceptions, so later plans were never validated. The
        # element-type loop below cannot save it. Reported as Critical and the plan abandoned.
        for key in ("objects", "objectSets"):
            if key not in data:
                continue
            value = data[key]
            if not isinstance(value, list):
                result.add_issue(Issue(
                    severity=Severity.CRITICAL,
                    object_name="N/A",
                    message=f"'{key}' is {type(value).__name__}, not an array",
                    file_path=self._make_relative_path(export_json_path)
                ))
                return None

        # Must have either objects or objectSets
        has_objects = "objects" in data
        has_object_sets = "objectSets" in data

        if not has_objects and not has_object_sets:
            result.add_issue(Issue(
                severity=Severity.CRITICAL,
                object_name="N/A",
                message="export.json must have either 'objects' or 'objectSets' array",
                file_path=self._make_relative_path(export_json_path)
            ))
            return None

        # Element types, not just the container's. Everything below assumes each element is a dict and
        # calls `.get()` on it, so `"objects": ["SELECT Id FROM Account"]` raised `AttributeError`
        # straight out of `main()` and lost **all 39 plans with no report at all** — nine such shapes
        # did. That is the same failure the `str()` coercion and the total dedup key were written to
        # prevent, surviving them because those guard *values* while these are *containers*: a guard
        # written against one shape of a defect does not cover the class. Reported as Critical and the
        # plan abandoned, which is what "report the broken plan, do not abort the run" means.
        for key in ("objects", "objectSets"):
            for i, element in enumerate(data.get(key) or []):
                if not isinstance(element, dict):
                    result.add_issue(Issue(
                        severity=Severity.CRITICAL,
                        object_name="N/A",
                        message=(f"'{key}[{i}]' is {type(element).__name__}, not an object — "
                                 f"export.json entries must be JSON objects"),
                        file_path=self._make_relative_path(export_json_path)
                    ))
                    return None
        # One level deeper: `objectSets: [{"objects": 7}]` reached `len()` on an int, and
        # `{"objects": {...}}` iterated a dict's *keys* as declarations, so every one of them was
        # silently dropped and the plan reported nothing.
        for i, obj_set in enumerate(data.get("objectSets") or []):
            # Present `null` is not "missing". `get` returns None either way, and
            # `if objects is not None` treated an explicit `"objects": null` as an empty pass, then
            # the log below did `len(obj_set.get("objects", []))` — the default is ignored when the
            # key is present — and aborted the whole run. Same class as the top-level type check:
            # a present non-list is a defect; only an absent key is an empty default.
            if "objects" in obj_set and not isinstance(obj_set["objects"], list):
                result.add_issue(Issue(
                    severity=Severity.CRITICAL,
                    object_name="N/A",
                    message=(f"'objectSets[{i}].objects' is {type(obj_set['objects']).__name__}, "
                             f"not an array"),
                    file_path=self._make_relative_path(export_json_path)
                ))
                return None
            objects = obj_set["objects"] if "objects" in obj_set else []
            for j, element in enumerate(objects or []):
                if not isinstance(element, dict):
                    result.add_issue(Issue(
                        severity=Severity.CRITICAL,
                        object_name="N/A",
                        message=(f"'objectSets[{i}].objects[{j}]' is {type(element).__name__}, not "
                                 f"an object — export.json entries must be JSON objects"),
                        file_path=self._make_relative_path(export_json_path)
                    ))
                    return None

        # A non-string `query` is reported rather than only skipped. `_extract_object_name` returns
        # "" for one so the declaration never enters any config map — which is what stops
        # `re.search` aborting the run — and every caller already treats "" as "not an object".
        # Without a finding here a plan of only `{"query": [...]}` plus a valid `apiVersion` returned
        # `passed=True` with zero objects validated, even though SFDMU cannot execute it. The object
        # is unknowable, so the finding is keyed on the index. The plan is not abandoned: a sibling
        # declaration is still worth validating.
        for j, obj in enumerate(data.get("objects") or []):
            self._report_non_string_query(f"objects[{j}]", obj, result, export_json_path)
        for i, obj_set in enumerate(data.get("objectSets") or []):
            for j, obj in enumerate(obj_set.get("objects") or []):
                self._report_non_string_query(f"objectSets[{i}].objects[{j}]", obj, result,
                                              export_json_path)

        objects_n = len(data["objects"]) if isinstance(data.get("objects"), list) else 0
        sets_n = sum(len(s["objects"]) if isinstance(s.get("objects"), list) else 0
                     for s in (data.get("objectSets") or []) if isinstance(s, dict))
        self.log(f"export.json structure valid, contains {objects_n + sets_n} object configurations")

        return data

    def _report_non_string_query(self, loc: str, obj: dict, result: ValidationResult,
                                 export_json_path: Path) -> None:
        """Report a `query` SFDMU cannot use: absent, non-string, blank, or unparseable.

        A non-blank string with no ` FROM <Object>` clause (a typo like `"SELECT Id"`) passed
        every check above unnoticed: `_extract_object_name` returns `""` for it too, the same
        silent-drop this function exists to report for the other three shapes, just reached via a
        fourth one. `{"apiVersion": "68.0", "objects": [{"query": "SELECT Id", "operation":
        "Upsert", "externalId": "Id"}]}` reported `passed=True` with zero objects validated before
        this branch covered it.

        `obj.get("query") is not None` treated an explicit `"query": null` as absent, after which
        `_extract_object_name` returned "" and the declaration vanished. A plan of only that
        declaration plus a valid `apiVersion` still reported success.

        An outright-missing key is not skippable either, despite `query` being unknowable in both
        cases. `ScriptLoader`'s loader (`ScriptLoader.ts:437-444`, v5.8.0) treats "absent" and
        "present but not a non-empty string" identically: `object.query` becomes `''` and the
        declaration is dropped with an `objectIsExcluded` warning rather than executed. A plan of
        `{"apiVersion": "68.0", "objects": [{"operation": "Upsert"}]}` — no `query` at all —
        reported `passed=True` with zero objects validated before this branch covered the missing
        case, exactly the silent-success gap the non-string branch already existed to close for
        the sibling shape.

        `excluded: true` is exempted, plain-truthy like `_is_live_writable`'s check on the same
        field: the outcome this check exists to catch — SFDMU dropping the declaration with an
        `objectIsExcluded` warning instead of executing it — is exactly what the author already
        asked for. Flagging a bad query there is the same false positive already fixed for
        `operation`/`externalId`/`deleteOldData`: an excluded declaration's content is inert, so a
        defect in it changes nothing SFDMU does.

        Deliberately not aware of `_normalized_object_sets`'s dominance rule (non-empty
        `objectSets` wins outright; a sibling top-level `objects` is never read). That rule is
        about deriving what SFDMU's *runtime* will do — the right lens for `_is_live_writable`/
        `_all_pass_configs`, which answer "what does this pass write" — not about whether the file
        is well-formed. The two callers here (lines ~531-536) mirror the container-type sweep
        immediately above them in this same function (lines 483-493), which also walks both
        `objects` and `objectSets` unconditionally: a malformed element in a container SFDMU
        happens to ignore right now is still an authoring mistake — e.g. a leftover flat `objects`
        array from before a plan migrated to `objectSets` — and dominance can flip with an edit to
        either container, so validating only the "live" one would make correctness depend on
        which one is currently winning.
        """
        if self._is_js_truthy(obj.get("excluded")):
            return
        query = obj.get("query")
        if isinstance(query, str) and query.strip():
            if self._extract_object_name(query):
                return
            message = (f"'{loc}.query' has no parseable ' FROM <Object>' clause — "
                       f"the declaration's object cannot be identified and it is skipped")
        elif "query" not in obj:
            message = f"'{loc}.query' is missing — SFDMU requires it; the declaration is excluded, not executed"
        elif isinstance(query, str):
            message = f"'{loc}.query' is blank — SFDMU requires a non-empty query; the declaration is excluded, not executed"
        else:
            message = (f"'{loc}.query' is {type(query).__name__}, not a string — "
                       f"the declaration cannot be identified and is skipped")
        result.add_issue(Issue(
            severity=Severity.HIGH,
            object_name="N/A",
            message=message,
            file_path=self._make_relative_path(export_json_path)
        ))

    @staticmethod
    def _normalized_object_sets(export_data: dict) -> List[dict]:
        """The plan's passes, with a flat `objects` plan presented as a single pass.

        Three call sites need to agree on this and used to disagree: the writable-pass map
        normalized flat plans, `_get_object_configs_for_pass` read `objectSets` raw (so it resolved
        nothing for a flat plan), and `_find_objectset_source_overrides` bounds-checked against the
        raw list (so it discarded every per-pass CSV in a flat plan, reporting only a WARN that is
        suppressed at default verbosity). Any two of those disagreeing is a silent wrong answer
        rather than an error, so the normalization lives in one place.

        It changes what the fix modes *write*, not only what validation reads, and that is easy to
        miss because every justification above is about reading. A flat `objects` plan with an
        `objectset_source/object-set-1/` directory previously had those CSVs discarded before the
        fix loop saw them; now `--fix-headers` writes a header row into them. That is the intended
        behavior — native SFDMU never reads `object-set-1/` itself (pass 1 always reads the plan
        root, per `_objects_owing_root_csv`'s docstring), but this repo's opt-in
        `sync_objectset_source_to_source` task copies it onto the root before SFDMU runs, so a
        correct header there still matters — but no shipped plan has that shape (flat `objects`
        plus `objectset_source/`: zero, and no `object-set-1/` exists anywhere in the tree), so real
        `--fix-all` output is byte-identical either way and nothing would have caught a mistake here.
        Pinned by the fix-mode cases in `tests/test_sfdmu_csv_expectation.py`, which are the repo's
        only fix-mode coverage.
        """
        object_sets = export_data.get("objectSets") or []
        if not object_sets and "objects" in export_data:
            return [{"objects": export_data["objects"]}]
        return object_sets

    def _all_pass_configs(self, export_data: dict) -> Dict[str, Dict[int, List[dict]]]:
        """Map each object to `{pass index: [that pass's declarations]}`, every pass.

        The counterpart to `_parse_object_configs`, which merges an object's declarations down to
        the *first* one. Every check that reads the merged config therefore validates pass 1 and
        silently exempts passes 2..n — a shape this file has now hit three times (`operation`,
        `excluded`, and the root-CSV `externalId`/query), so the per-pass view is a primitive rather
        than a special case.

        A **list** per index, not one config, because a single `objectSet` may declare the same
        object twice. Assigning by index made the second declaration overwrite the first, so the
        merged view kept the first and this view kept the *last* — and a real defect in the
        overwritten one went silent (a missing composite-key column, or an `operation` SFDMU cannot
        resolve, both reproduced). No shipped plan has that shape and SFDMU 5.8.0 does not reject
        it, so it was a latent regression on a loadable plan rather than a live false green; a
        collection whose size depends on declaration order is the kind of thing to fix while it is
        still latent.
        """
        by_pass: Dict[str, Dict[int, List[dict]]] = {}
        for idx, obj_set in enumerate(self._normalized_object_sets(export_data)):
            for obj in obj_set.get("objects", []):
                query = obj.get("query", "")
                obj_name = self._extract_object_name(query)
                if obj_name:
                    by_pass.setdefault(obj_name, {}).setdefault(idx, []).append(
                        self._normalize_object_config(obj, query, idx))
        return by_pass

    # Dedup keys, one tuple per *list*, each the union of what every consumer of that list reads.
    # Per-consumer keys were the obvious design and are wrong, because a dedup can only remove and
    # never restore: the reading-declaration list feeds both `_validate_csv_file` (externalId,
    # operation, deleteOldData) and `_validate_external_id` (externalId, operation, fields), so
    # keying it on the CSV check's fields dropped later passes before the externalId check could see
    # them — silently disabling SELECT-coverage for passes 2..n, 96 lost findings across a 59,400-plan
    # sweep. Re-deduping downstream on a wider key cannot undo it. Union per list, and dedup the
    # *findings* rather than the declarations where multiplicity is the concern: since
    # `ValidationResult.add_issue` drops identical findings, this dedup exists only to avoid repeated
    # work, so erring wide is free and erring narrow loses checks.
    _READING_CONFIG_KEYS = ("externalId", "operation", "deleteOldData", "fields")
    _OPERATION_CHECK_KEYS = ("operation",)

    @staticmethod
    def _dedup_configs(configs: List[dict], keys: Tuple[str, ...]) -> List[dict]:
        """Distinct declarations by `keys` — the union of what every consumer of the list reads.

        Two passes commonly declare an object identically; validating both is wasted work. `keys` is
        required rather than defaulted so a new call site has to state what its consumers read instead
        of inheriting someone else's answer.

        Key building is *total*, via `json.dumps(default=repr)`. A one-level `tuple()` looked
        sufficient — the values are strings, bools and the parsed `fields` list — but a list
        containing a list stays unhashable, so `"operation": [["x"]]` in one malformed `export.json`
        raised `TypeError` out of `main()` and killed all 39 plans with no report at all. That is the
        same failure the `str()` coercions elsewhere in this file exist to prevent: report the broken
        plan, do not abort the run.
        """
        seen, out = set(), []
        for cfg in configs:
            key = tuple(json.dumps(cfg.get(k), sort_keys=True, default=repr) for k in keys)
            if key not in seen:
                seen.add(key)
                out.append(cfg)
        return out

    @staticmethod
    def _is_js_truthy(value) -> bool:
        """Python truthiness corrected to match SFDMU's JS truthiness for a JSON-decoded value.

        Diverges from Python's own truthiness for containers: `[]`/`{}` are falsy in Python but
        truthy in JS, so an `"excluded": []`/`{}` declaration is dropped by SFDMU (JS reads
        `object.excluded` as truthy) while a plain `if cfg.get("excluded")` read it as
        live/writable — a false missing-CSV Critical. Every other boolean-like field SFDMU also
        reads with plain JS truthiness (`deleteOldData`, top-level `useSeparatedCSVFiles`) is
        swept through this same helper for the identical reason, not just `excluded`.

        Does NOT special-case `NaN`: Python's `json` module can decode the `NaN` extension to a
        Python-truthy `float('nan')`, which JS treats as falsy, but a value reaches this function
        only after `_validate_export_json`'s `json.load` already rejects that token
        (`_reject_non_finite_json_constant`) the way SFDMU's real `JSON.parse` would — so a `NaN`
        can no longer survive to be read here. A truthiness rule for a state the loader has
        already ruled out would be untestable except by calling this function directly.
        """
        if isinstance(value, (list, dict)):
            return True
        return bool(value)

    @staticmethod
    def _is_live_writable(cfg: dict) -> bool:
        """True if SFDMU will write this declaration from a source file.

        `excluded` declarations are skipped entirely; `Readonly` and plain `Delete` ones are both
        skipped by the same runtime gate (`MigrationJobTask.updateRecordsAsync`'s early return —
        see the inline comment below) without ever reading a source file. All three owe no CSV,
        and a High on any of them is a false positive — including when one shares a pass with a
        writable sibling, which is the shape `_objects_owing_root_csv` used to miss because it
        filtered only `excluded`. An unresolvable or `Unknown` `operation` is the other direction:
        it is NOT exempted like `Readonly`/`Delete` — SFDMU still writes it from source, so a
        missing CSV for it is a real Critical, not a false positive.
        """
        if SFDMUValidator._is_js_truthy(cfg.get("excluded")):
            return False
        # str() because a malformed plan can carry a non-string here (`"operation": true`).
        # `.strip().lower()` matches SFDMU, and the authoritative function is worth naming because
        # there are two and they disagree. `ScriptLoader._resolveOperation` is the one that loads
        # export.json (v5.8.0): it does `operation.trim().toLowerCase()` and matches enum keys
        # case-insensitively, so `" ReadOnly "` resolves to Readonly. `ScriptObject.getOperation` is
        # a secondary path doing a raw `OPERATION[operation]` lookup with neither. Reading the latter
        # as authoritative makes this look too lenient and argues for dropping the normalization —
        # which would then report the nine `"ReadOnly"` declarations in this repo as defects. SFDMU
        # accepts them.
        # Absent defaults to Readonly, not Upsert: `ScriptObject.operation` is initialized to
        # `OPERATION.Readonly` (ScriptObject.ts:162, v5.8.0), and that class-field default only
        # survives when the `operation` key is absent from the plan — `_normalize_object_config`
        # (the sole path a config reaches this function through) already coalesces an absent key to
        # the string `"Readonly"` before this runs, so `resolved is None` below can never mean
        # "absent"; it only means the key was present with a value SFDMU cannot resolve.
        #
        # A *present* unresolvable value (a typo like "Upser", a Boolean, an out-of-range index, or
        # an explicit `null`) does NOT fall back to that class default. Verified against the
        # installed `sfdmu@5.8.0` source: `ScriptLoader._buildObject` builds `object` via
        # `class-transformer`'s `plainToInstance(ScriptObject, rawObject, {exposeDefaultValues:
        # true})` *before* `_resolveOperation` runs, and `plainToInstance` copies a *present* raw
        # value onto the instance regardless of validity — only an absent key leaves the class
        # default untouched. `_resolveOperation` then only overwrites `object.operation` when it
        # resolves (`if (typeof operation !== 'undefined') { object.operation = operation; }` —
        # ScriptLoader.js:306-309); on failure it leaves `object.operation` as whatever
        # `plainToInstance` already put there — the raw invalid value itself, not `OPERATION.Readonly`.
        # That raw value is `===`-checked against exactly `OPERATION.Readonly`(3) and
        # `OPERATION.Delete`(4) at the one runtime gate that decides whether an object is written
        # from source (`MigrationJobTask.updateRecordsAsync`, the `Readonly`/`Delete` early return);
        # a garbage value matches neither, so it falls through to the same insert/update/upsert
        # dispatch a real writable operation gets — the plan behaves as if the object were writable,
        # just not with the operation the author intended. Treating it as non-writable here (this
        # function's behavior through several earlier rounds of this PR) was itself the false
        # negative this validator exists to catch: it silently excused such an object from the
        # missing-CSV Critical it will actually need at runtime.
        #
        # Index 8 / the string "Unknown" is the same shape: SFDMU *does* resolve it (to committed
        # value 8, not `undefined` — see `SFDMU_OPERATION_BY_INDEX`), so `object.operation` becomes
        # numeric `8` — still neither `Readonly`(3) nor `Delete`(4), so it hits the identical
        # write-dispatch fallthrough. Checked separately from `resolved is None` (rather than folded
        # into the same branch) because a future caller distinguishing "declared nothing usable" from
        # "declared Unknown" needs the signal, even though both currently answer `True` here.
        resolved = SFDMUValidator._resolve_operation(cfg.get("operation"))
        if resolved is None or resolved == "unknown":
            return True
        # Plain `delete` hits the exact same early return as `readonly` at that gate
        # (`this.scriptObject.operation === OPERATION.Readonly || ... === OPERATION.Delete`) —
        # found by Copilot (comment 3888882830) after this docstring/comment block already named
        # the gate but the code below it excluded only "readonly". The other delete-family values
        # (`deletesource`, `deletehierarchy`, `harddelete`) are distinct enum members that gate does
        # not match, so they are deliberately left out of this exclusion — verified they fall
        # through to the normal dispatch instead, so they still owe a CSV.
        return resolved not in ("readonly", "delete")

    def _writable_passes_by_object(self, all_pass_configs: Dict[str, Dict[int, List[dict]]]) -> Dict[str, Set[int]]:
        """Map each object to the 0-based passes in which this plan writes it from a file.

        Distinct from the merged config `_parse_object_configs` returns, which keeps only the
        *first* declaration: an object may be Readonly in one pass and Upsert in another, and it
        is the per-pass detail — not the union, and not the first entry — that decides which
        source files are owed. Keeping the pass numbers is what lets a caller ask whether *this*
        pass has a file, rather than whether the object has one somewhere.

        Takes `all_pass_configs` rather than `export_data`. An earlier version re-walked
        `_normalized_object_sets(export_data)` on its own — a second, independent traversal of
        the same input `_all_pass_configs` already walks for this method's sole caller
        (`_objects_owing_root_csv`, which is handed `all_pass_configs` specifically to avoid
        recomputing it). The two walks agreed only because `_is_live_writable`'s own
        `operation`/`excluded` handling happens to mirror `_normalize_object_config`'s
        defaulting — a coincidence to maintain by hand, not a guarantee, and one more place for
        the two to silently diverge the next time either changes.
        """
        writable: Dict[str, Set[int]] = {}
        for obj_name, by_pass in all_pass_configs.items():
            for idx, cfgs in by_pass.items():
                if any(self._is_live_writable(cfg) for cfg in cfgs):
                    writable.setdefault(obj_name, set()).add(idx)
        return writable

    # SFDMU's `OPERATION` enum as spelled in `Enumerations.js` (v5.8.0), lowercased because that is
    # how `ScriptLoader._resolveOperation` compares. `Unknown` is the enum's own fallback rather
    # than a value a plan should declare, so it is deliberately absent here — `_resolve_operation`
    # still resolves it (via `SFDMU_OPERATION_BY_INDEX` below), it is just never a *legal* choice.
    SFDMU_OPERATIONS = frozenset({"insert", "update", "upsert", "readonly", "delete",
                                  "deletesource", "deletehierarchy", "harddelete"})

    # Numeric enum indices `ScriptLoader._resolveOperation` resolves via `OPERATION[value]`
    # (Enumerations.js, v5.8.0): 0 Insert .. 7 HardDelete .. 8 Unknown. TypeScript numeric enums are
    # bidirectional at runtime (`OPERATION[8] === "Unknown"` and `OPERATION["Unknown"] === 8`), so
    # SFDMU resolves index 8 *and* the string `"Unknown"` to the committed value 8 — unlike an
    # out-of-range index or unrecognized word, which fail to resolve at all (see `_resolve_operation`
    # below; neither case is written from the plan's intended operation, but neither is "dropped"
    # from processing either — see `_is_live_writable`). Index 8 is included here (unlike the
    # earlier, source-unverified assumption that it resolved to nothing) so `_resolve_operation`
    # returns `"unknown"` rather than `None` for it; callers then treat `"unknown"` as its own
    # state — resolved to a committed value, but not a real operation — rather than lumping it in
    # with a value that fails resolution outright.
    SFDMU_OPERATION_BY_INDEX = ("insert", "update", "upsert", "readonly", "delete",
                                "deletesource", "deletehierarchy", "harddelete", "unknown")

    @staticmethod
    def _resolve_operation(value) -> Optional[str]:
        """Mirror `ScriptLoader._resolveOperation` (v5.8.0): the canonical lowercase enum name
        SFDMU would resolve `value` to, or `None` if SFDMU cannot resolve it. `None` does NOT mean
        the object falls back to a safe default — the raw, unresolved value is left in place on
        `ScriptObject.operation` instead (see `_is_live_writable`).

        Order matters: `bool` is checked before `int` because Python's `isinstance(True, int)` is
        `True` and `False == 0` — but JS `typeof true === 'boolean'` fails the loader's `typeof
        operation === 'number'` check, so a Boolean is *always* dropped, never read as 0/1.

        An integral `float` (e.g. `2.0`, which `json.load` produces for that literal) is accepted
        alongside `int`: JS has one numeric type, so `OPERATION[2.0]` is the same property lookup
        as `OPERATION[2]` and resolves to Upsert — rejecting the float here would report a valid
        plan's operation as unresolvable. `is_integer()` is `False` for `2.5` (out of the loader's
        reach — `OPERATION[2.5]` is `undefined`) and for `nan`/`inf`, so both still fall through.

        The string branch matches against `SFDMU_OPERATION_BY_INDEX`, not `SFDMU_OPERATIONS`: the
        enum's numeric keys are bidirectional at runtime, so the loader's `Object.keys(OPERATION)`
        also matches the literal string `"Unknown"` and resolves it to `8` — the same committed
        value a numeric `8` resolves to. Returning `"unknown"` here (rather than `None`) lets
        callers distinguish that from a value that fails resolution outright.
        """
        if isinstance(value, bool):
            return None
        if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
            idx = int(value)
            return (SFDMUValidator.SFDMU_OPERATION_BY_INDEX[idx]
                    if 0 <= idx < len(SFDMUValidator.SFDMU_OPERATION_BY_INDEX) else None)
        if isinstance(value, str):
            normalized = value.strip().lower()
            return (normalized if normalized in SFDMUValidator.SFDMU_OPERATION_BY_INDEX
                    else None)
        return None

    def _validate_operation_value(self, obj_name: str, obj_config: dict, result: ValidationResult):
        """Report an `operation` declaration SFDMU cannot resolve to a real, actionable operation —
        whether it fails to resolve at all, or resolves to the enum's own `Unknown` fallback.

        Mirrors `ScriptLoader._resolveOperation` (v5.8.0), the function that loads export.json:
        strings are matched `trim().toLowerCase()` against the enum keys (so `" ReadOnly "` is
        fine) and numeric enum indices 0-8 resolve directly (`OPERATION[value]`, bidirectional at
        runtime for a TypeScript numeric enum, so the string `"Unknown"` resolves the same way as
        numeric `8`); anything else — a Boolean, an out-of-range index, or a word not in the enum —
        resolves to `undefined`.

        Neither case resets the object to a safe, inert default. Verified against the installed
        `sfdmu@5.8.0` source: `plainToInstance` copies a *present* raw value onto the `ScriptObject`
        instance before `_resolveOperation` ever runs; on a failed resolve, `ScriptLoader` skips its
        own overwrite (`if (typeof operation !== 'undefined') { object.operation = operation; }`),
        leaving that raw, invalid value in place. Index 8 / `"Unknown"` resolves, so `object.operation`
        becomes the committed value `8` instead. Either way, the object's `operation` is neither
        `OPERATION.Readonly`(3) nor `OPERATION.Delete`(4) — the only two values the runtime write
        gate (`MigrationJobTask.updateRecordsAsync`) checks for before skipping a declaration — so
        it falls through to the same insert/update/upsert dispatch a real writable operation gets.
        The plan runs as if the object were declared writable, just not with the operation intended;
        see `_is_live_writable`, which this reporting is kept consistent with.

        Written first against `ScriptObject.getOperation`, which does a raw `OPERATION[operation]`
        lookup with no trimming or case folding. That reading made the nine `"ReadOnly"`
        declarations in this repo look like defects, which is how the wrong function was caught:
        they are accepted, because the loader is the code path a plan actually goes through.

        `obj_config` always carries an `operation` key here: the sole caller passes a declaration
        from `_normalize_object_config`, which injects `obj.get("operation", "Readonly")`
        unconditionally, so an absent declared value already arrives as the string `"Readonly"`.
        """
        operation = obj_config["operation"]
        resolved = self._resolve_operation(operation)
        if resolved is not None and resolved != "unknown":
            return
        if resolved == "unknown":
            result.add_issue(Issue(
                severity=Severity.HIGH,
                object_name=obj_name,
                message=(f"operation {operation!r} resolves to SFDMU's own enum fallback, Unknown "
                         f"(index 8) — not a real operation the plan can act on, and SFDMU does not "
                         f"reset it to Readonly either: the committed value 8 matches neither "
                         f"Readonly(3) nor Delete(4) at SFDMU's write-dispatch gate, so the object "
                         f"still falls through to the insert/update/upsert path and is written from "
                         f"source with no real operation behind it; declare one of "
                         f"{', '.join(sorted(self.SFDMU_OPERATIONS))} or a numeric index 0-7")
            ))
            return
        result.add_issue(Issue(
            severity=Severity.HIGH,
            object_name=obj_name,
            message=(f"operation {operation!r} is not one SFDMU can resolve; it matches "
                     f"trim()/case-insensitively against {', '.join(sorted(self.SFDMU_OPERATIONS))} "
                     f"or a numeric enum index 0-7 (0 Insert .. 7 HardDelete), and silently "
                     f"ignores anything else — including a Boolean. That does NOT reset the object "
                     f"to Readonly: the invalid value stays on it, matches neither Readonly(3) nor "
                     f"Delete(4) at SFDMU's write-dispatch gate, and the object still falls through "
                     f"to the insert/update/upsert path — written from source with no real "
                     f"operation behind it")
        ))

    @staticmethod
    def _override_content_should_be_checked(pass_index: int, use_separated_csv_files: bool) -> bool:
        """Whether this pass's `objectset_source` override is worth validating the *content* of.

        Not "is it read by SFDMU at runtime" — native SFDMU never reads `object-set-1/` itself for
        pass 1 either (see `_objects_owing_root_csv`'s docstring: pass 1 always reads the plan
        root; only this repo's opt-in `sync_objectset_source_to_source` task reads `object-set-1/`
        at all, to copy it onto the root first). Pass 1's override is still checked unconditionally
        because that copy step, and this file's own `--fix-headers`/`--fix-all` modes, both treat
        `object-set-1/<Object>.csv` as real output regardless of `useSeparatedCSVFiles` — see the
        fix-mode docstring above (`_normalized_object_sets`, "It changes what the fix modes
        *write*"). Every other pass's override is genuinely inert for native SFDMU without the
        flag, and this validator deliberately doesn't model the sync task's independent handling of
        those passes — same scoping decision as everywhere else in this file. Shared by the two
        content-check sites that used to write `pass_index > 0 and not use_separated_csv_files`
        independently (and cross-referenced each other in comments to stay in sync: "Same gate
        as ...").

        Deliberately NOT reused inside `_objects_owing_root_csv`'s coverage loop below, which asks a
        different question — "does this override *relieve the root CSV requirement*" — and answers
        pass 1 the opposite way: pass 1's root CSV is owed regardless of `object-set-1/`'s content
        (see that method's docstring). Conflating the two once already broke an existing regression
        test in this PR; kept apart on purpose.
        """
        return pass_index == 0 or use_separated_csv_files

    def _objects_owing_root_csv(self, objectset_source_overrides: Dict[Tuple[str, int], Tuple[Path, int]],
                                all_pass_configs: Dict[str, Dict[int, List[dict]]],
                                use_separated_csv_files: bool) -> Dict[str, List[dict]]:
        """Objects that must have a CSV at the plan root -> the declarations that read it.

        `all_pass_configs` and `use_separated_csv_files`: both per `_all_pass_configs`/
        `export_data.get("useSeparatedCSVFiles")`, supplied rather than recomputed here — the sole
        call site already builds both for the main validate loop and neither changes between the
        two, so a second computation of either was the same redundant work twice over.

        Returns a mapping rather than a set so membership (`obj_name in ...`) still answers "is a
        root CSV owed", while the value carries **which** passes read it. The root file has to be
        validated against those, not against the merged config: `_parse_object_configs` keeps the
        first declaration, so a pass-1 `Readonly`/excluded declaration followed by a writable pass 2
        had the file checked against pass 1's `query` and `externalId`. A pass-2 composite key needing
        a `$$A$B` column in that same file was then never asked for, and a CSV carrying only pass 1's
        single column passed. Verified by the `MERGED CONFIG` cases in
        `tests/test_sfdmu_csv_expectation.py`.

        A plan reads a writable pass's records from `objectset_source/object-set-N/<Object>.csv`
        when that file exists AND the plan's top-level `useSeparatedCSVFiles` is `true`, and from
        `<plan>/<Object>.csv` otherwise — except pass 1, which SFDMU always reads from the plan
        root regardless of an `object-set-1/` file or the flag: `Script.ts`'s
        `rawSourceDirectoryPath` returns `basePath` whenever `objectSetIndex` is falsy (index 0) OR
        `useSeparatedCSVFiles` is falsy — pass 1 has no `useSeparatedCSVFiles` escape hatch, and
        passes 2..n have no escape hatch *without* the flag. `objectset_source/object-set-1/`
        becomes readable only through this repo's opt-in `sync_objectset_source_to_source` step
        (`tasks/rlm_sfdmu.py:187-205,390-391`), which copies it onto the root before SFDMU runs —
        it is never a substitute for the root file itself. So the root file is owed as soon as
        *any* writable pass lacks a flag-gated override, pass 1 always included; keyed on the pass
        and not on the object name for the same reason.

        Keying on the name is a live false negative, not a hypothetical one: `BillingPolicy` in
        `qb/en-US/qb-billing` is `Upsert` in pass 1 and `Update` in pass 3, and only pass 3 has an
        override. Exempting the object because *an* override exists means pass 1 — which reads the
        root file — stops being checked, and deleting that file leaves the plan reporting PASS.
        Sixteen objects across seven scanned plans have this shape — eleven of them in the five that
        `cumulusci.yml` wires, the other five in `mfg-billing`/`mfg-tax`, which it does not. Of the
        **seventeen objects that carry a per-pass override**, exactly one
        (`procedure-plans/ProcedurePlanOption`) is declared in a single pass, which is the only shape
        a name-keyed gate gets right. The domain restriction matters: repo-wide, 399 objects are
        single-pass, so "exactly one" is only true among the objects a name-keyed gate would exempt.

        A misfiled override — a CSV in an `object-set-N/` whose pass does not declare the object —
        needs no filtering here, and an earlier version's check for one was inert. Keying on the
        pass already handles it: a coverage index can only cancel the same index, and a misfiled
        override's index is by definition one where the object is not declared, so it is not in
        `writable_passes[obj]` and cancels nothing. (Verified exhaustively over every 1–2 pass plan
        with two objects across all operation/`excluded` combinations and all override sets up to
        size 2 — 0 disagreements. It is reported separately as a High, by the per-pass loop.)
        """
        writable_passes = self._writable_passes_by_object(all_pass_configs)
        # SFDMU's `rawSourceDirectoryPath` (`Script.js`) substitutes the object-set-N subdirectory
        # only when `objectSetIndex` is truthy AND `useSeparatedCSVFiles` is true; either condition
        # false, and every pass — not just pass 1 — reads the plan root. Without this gate, a plan
        # with an `objectset_source/object-set-2/<Object>.csv` but no (or a false) top-level
        # `useSeparatedCSVFiles` credited that file as coverage, so a missing root CSV — which SFDMU
        # still needs at runtime — silently passed instead of failing Critical.
        covered: Dict[str, Set[int]] = {}
        for (obj_name, pass_index) in objectset_source_overrides:
            if pass_index == 0:
                # object-set-1 never relieves pass 1's root-CSV requirement — see the docstring
                # above. Left in `objectset_source_overrides` itself (not filtered at the source)
                # so the fix/validate loops over that dict still check the file's own header and
                # composite-key shape; only its use as *coverage* here is excluded.
                continue
            if not use_separated_csv_files:
                continue
            covered.setdefault(obj_name, set()).add(pass_index)

        owed: Dict[str, List[dict]] = {}
        for obj_name, passes in writable_passes.items():
            uncovered = sorted(passes - covered.get(obj_name, set()))
            if uncovered:
                # Flattened: a pass index maps to a *list* of declarations, since one objectSet may
                # declare the object more than once. Deduped on the union of what every consumer of
                # this list reads — see `_READING_CONFIG_KEYS`; narrowing it to one consumer's fields
                # silently disabled the other's check.
                # `excluded` *and* `Readonly` dropped here, not just at the pass level.
                # `writable_passes` already excludes a pass whose *only* declaration is excluded or
                # Readonly, but a pass declaring the object twice — once either — contributed the
                # inert one to this list, and widening the dedup key to include `fields` stopped it
                # collapsing into its sibling. SFDMU never writes either, so a SELECT gap or
                # composite-key requirement on one is not a defect of the root CSV. The first version
                # filtered only `excluded`; a Readonly sibling in the same pass was still checked.
                #
                # Via `_writable_configs_for_pass`, not a second hand-rolled `_is_live_writable`
                # filter — that primitive already exists for "live writable declarations of this
                # object in this pass," and a second copy is one more place for the two to drift the
                # next time either's definition of "writable" changes. The outer `_dedup_configs`
                # call below still runs on the flattened result: each pass is deduped internally by
                # `_writable_configs_for_pass`, but a duplicate spanning two different `uncovered`
                # passes is only caught by deduping again across all of them together.
                declarations = [cfg for i in uncovered
                                for cfg in self._writable_configs_for_pass(all_pass_configs, obj_name, i)]
                # Only when non-empty. Membership in this mapping is what makes `_validate_object` ask
                # for the file at all, so a key with an empty list would claim the CSV is owed and
                # then validate it against nothing — dropping the missing-file Critical silently. It
                # cannot currently happen (`_writable_passes_by_object` records a pass only if some
                # declaration there is both writable and non-excluded, and that declaration survives
                # the filter above), so this is an invariant guard rather than live handling; it is
                # here because the filter above is what put the invariant at risk.
                if declarations:
                    owed[obj_name] = self._dedup_configs(declarations, self._READING_CONFIG_KEYS)
        return owed

    def _parse_object_configs(self, export_data: dict) -> Dict[str, dict]:
        """Parse export.json into object name -> config mapping.

        Args:
            export_data: Parsed export.json data

        Returns:
            Dictionary mapping object API name to configuration
        """
        configs = {}

        # A fifth reimplementation of the same flat-vs-objectSets normalization would have been a
        # fifth place to disagree — see `_normalized_object_sets`'s docstring for the three that
        # already did. This one additionally crashed outright: `export_data.get("objectSets", [])`
        # only substitutes `[]` when the key is *absent*, so `{"objectSets": null}` (a malformed but
        # syntactically valid export.json) left `object_sets` as `None`, and `enumerate(None)` raised
        # `TypeError` out of `main()` — the same "one broken plan takes down all 39" shape this file
        # exists to avoid for `query` and `operation`.
        object_sets = self._normalized_object_sets(export_data)

        for idx, obj_set in enumerate(object_sets):
            for obj in obj_set.get("objects", []):
                query = obj.get("query", "")
                obj_name = self._extract_object_name(query)

                if not obj_name:
                    continue

                # Store first pass configuration (later passes may be activations)
                if obj_name not in configs:
                    configs[obj_name] = self._normalize_object_config(obj, query, idx)

        return configs

    def _normalize_object_config(self, obj: dict, query: str, idx: int) -> dict:
        """One export.json declaration in the shape every check downstream expects.

        Shared with `_all_pass_configs` so a per-pass config is indistinguishable from a merged one.
        Not cosmetic: the checks read *derived* keys, not the raw declaration — `_validate_external_id`
        reads `fields` (the parsed SELECT), so handing it a raw declaration makes `fields` empty and
        every externalId component read as absent from the query. Measured: forcing `fields` empty
        adds 245 spurious SELECT-coverage findings on top of the documented High baseline, landing
        at 252 High overall. So this normalizer, not the reading-pass scoping below it, is what
        holds that back — the two were conflated in earlier notes quoting 241 and 258, neither of
        which reproduces. Deliberately not spelled as "N High to 252 High": the baseline number
        belongs to `tests/test_sfdmu_csv_expectation.py`'s pinned sites, which is what a reader
        should update when it changes; restating it bare here, next to "High", would read as a
        second live claim that sweep neither discovers (this file is not one of its roots) nor
        keeps in sync — the exact drift its pinning exists to prevent, one document over.

        `externalId` is coerced to `str` here — the single point that does so, now that all three
        config builders route through this function. Four sites downstream call
        `external_id.split(";")`, and a non-string value (a JSON list or object, easy to produce by
        hand-editing an `export.json`) raised `AttributeError` straight out of `main()` and aborted
        **all 39 plans with no report**, rather than reporting the one that is broken. Same threat
        model as the total dedup key in `_dedup_configs` and the other `str()` coercions here.

        Coercion alone was not enough, and the first version of this docstring claimed otherwise: it
        said the `str()` "renders it visibly wrong … so the plan gets reported". It does not. The repr
        contains no `;`, no `$$` and no second `.`, so every downstream gate is skipped and the plan
        reports **nothing at all** — loud failure traded for silent acceptance, which is the worse of
        the two. Hence `externalId_malformed`: the coercion loses the type, so the type is recorded
        here and reported by `_validate_object`.
        """
        # `externalId` gets `obj.get(key)` + a JS-truthiness check rather than `obj.get(key,
        # default)`, because SFDMU's own runtime does not draw the absent-vs-explicit-null line for
        # this field, or even the null-vs-other-falsy line: `ScriptObject.js`'s init path ends with
        # `this.externalId = this.externalId || DEFAULT_EXTERNAL_ID_FIELD_NAME` — a JS falsy-OR
        # fallback that defaults an explicit `null`, `0`, `false`, or `""` exactly like an absent
        # key (all falsy in JS). Confirmed against the installed `sfdmu@5.8.0` source,
        # `ScriptObject.js` (init method around the "Setup start" log line). An earlier version
        # here checked only `is None`, so `"externalId": 0`/`false`/`""` fell through unchanged
        # instead of defaulting to `"Id"`, then got `str()`-coerced and reported malformed below —
        # a false High for a declaration SFDMU accepts and quietly redirects to `Id`. Routed
        # through `_is_js_truthy` rather than a second bespoke falsy check, for the same reason
        # `excluded`/`deleteOldData` are: a list/dict is JS-truthy (`[]`/`{}` are objects, not
        # falsy), so an `externalId: []` still falls through to the malformed report instead of
        # being silently defaulted — only the scalar falsy values redirect.
        #
        # `operation` does NOT get the same treatment, and used to here — a prior version of this
        # normalizer coalesced `"operation": null` to `"Readonly"` on the theory that
        # `ScriptLoader._resolveOperation`'s `typeof operation !== 'string'` branch treats
        # `undefined` and `null` identically. That's true of `_resolveOperation` in isolation, but
        # not of the pipeline around it: `ScriptLoader._buildObject` builds the object via
        # `class-transformer`'s `plainToInstance(ScriptObject, rawObject, {exposeDefaultValues:
        # true})` *before* `_resolveOperation` ever runs. For an absent key, `exposeDefaultValues`
        # writes the class's own default (`OPERATION.Readonly`) onto the instance. For an explicit
        # `null`, the key IS present in the raw object, so class-transformer commits the raw `null`
        # onto `object.operation` instead — and `_resolveOperation(null)` resolving to `undefined`
        # only means the *later* assignment at `object.operation = operation` is skipped, leaving
        # that already-committed `null` in place. Unlike `externalId`, `operation` has no
        # `this.operation || OPERATION.Readonly`-style fallback anywhere in `ScriptObject.js` to
        # catch it afterward. So an absent key ends up `Readonly`; an explicit `null` ends up
        # `null` — a value that matches none of the `===` comparisons the engine dispatches
        # operations on (Insert/Upsert/Delete/Readonly all excluded), which is a genuinely broken
        # declaration, not a clean default. Reported as unresolvable below, same as any other bad
        # `operation` value — not silently defaulted.
        raw_operation = obj.get("operation", "Readonly")
        raw_external_id = obj.get("externalId")
        if not self._is_js_truthy(raw_external_id):
            raw_external_id = "Id"
        return {
            "pass_index": idx,
            # Readonly, not Upsert: SFDMU leaves `ScriptObject.operation` at its Readonly class
            # default when export.json omits the key (see `_is_live_writable`). Baking Upsert in
            # here would defeat that fix for every consumer reading the normalized config. An
            # explicit `"operation": null` is deliberately NOT folded into this default — see the
            # comment above `raw_operation`'s assignment — so it passes through as `None` and
            # `_validate_operation_value` reports it as unresolvable.
            "operation": raw_operation,
            "externalId": str(raw_external_id),
            # Recorded rather than reported here: this function has no `result` to add an issue to,
            # and threading one in would make a pure normalizer a validator. The type name is carried
            # alongside the flag because `str()` destroys it, and the reported repr of `1` is
            # indistinguishable from that of `"1"` — the one case where the reader needs the type.
            "externalId_malformed": not isinstance(raw_external_id, str),
            "externalId_type": type(raw_external_id).__name__,
            "query": query,
            "fields": self._parse_select_fields(query),
            "excluded": obj.get("excluded", False),
            "deleteOldData": obj.get("deleteOldData", False),
            "skipExistingRecords": obj.get("skipExistingRecords", False),
        }

    def _extract_object_name(self, query: str) -> str:
        """Extract object API name from SOQL query.

        Args:
            query: SOQL query string

        Returns:
            Object API name, or empty string if not found

        Non-string `query` returns "" rather than raising. `re.search` on a list raises `TypeError`
        out of `main()`, taking all 39 plans down over one malformed declaration; returning "" makes
        the caller skip the declaration, which the callers already handle (`if not obj_name`).
        """
        if not isinstance(query, str):
            return ""
        match = re.search(r'\sFROM\s+(\w+)', query, re.IGNORECASE)
        return match.group(1) if match else ""

    def _parse_select_fields(self, query: str) -> List[str]:
        """Parse field names from SOQL SELECT clause.

        Args:
            query: SOQL query string

        Returns:
            List of field names (including relationship traversals like Product.Name)
        """
        if not isinstance(query, str):
            return []
        match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not match:
            return []

        fields_str = match.group(1)
        # Split by comma, strip whitespace
        fields = [f.strip() for f in fields_str.split(',')]
        return fields

    def _find_objectset_source_overrides(self, dataset_path: Path, export_data: dict,
                                         result: ValidationResult) -> Dict[Tuple[str, int], Tuple[Path, int]]:
        """Find per-pass CSV overrides in objectset_source/object-set-N/.

        Includes `object-set-1` (pass_index 0) in the returned mapping — its file still gets
        header/composite-key validation — but `_objects_owing_root_csv` deliberately drops
        pass_index 0 when deciding what counts as *coverage*, since SFDMU always reads pass 1 from
        the plan root regardless of this directory. See that function's docstring.

        Args:
            dataset_path: Path to dataset directory
            export_data: Parsed export.json data
            result: Result to report a directory that maps to no pass into. Required, not
                defaulted: the sole caller (`validate_dataset`) always has one in scope, and an
                `Optional[...] = None` here invited a second, dead code path — no caller has ever
                passed `None` — that duplicated every `if result is not None:` guard below it.

        Returns:
            Dictionary mapping (object_name, pass_index) -> (csv_path, pass_index)
            Example: {("BillingTreatmentItem", 1): (Path(".../object-set-2/BillingTreatmentItem.csv"), 1)}
        """
        overrides = {}
        objectset_source_dir = dataset_path / "objectset_source"

        if not objectset_source_dir.exists():
            return overrides

        # Hoisted out of the loop below: `export_data` does not change per directory, so a call per
        # iteration re-walked the same normalization once for every object-set-N directory.
        object_sets = self._normalized_object_sets(export_data)

        # Find all object-set-N directories
        for obj_set_dir in sorted(objectset_source_dir.glob("object-set-*")):
            if not obj_set_dir.is_dir():
                continue

            # Extract pass number from directory name (object-set-2 -> pass_index 1). Anchored at
            # both ends and no leading zero on a multi-digit number: `re.match` alone accepts
            # `object-set-1-backup` as a match on the `object-set-1` prefix, and unrestricted `\d+`
            # accepts `object-set-01` as if it were `object-set-1` — both are non-canonical names
            # the runtime sync in `tasks/rlm_sfdmu.py` does not special-case (it string-compares
            # against the literal `object-set-1` and otherwise preserves the directory name as-is),
            # so a plan with such a directory has its CSVs silently never read at runtime while a
            # loose match here would have credited it as covering the pass. `0|[1-9]\d*` still
            # admits the bare `object-set-0` typo below it, which does not carry a leading zero and
            # is reported through the existing out-of-range path instead.
            match = re.fullmatch(r"object-set-(0|[1-9]\d*)", obj_set_dir.name)
            if not match:
                self.log(f"Warning: {obj_set_dir.name} is not a canonical object-set-N directory",
                          level="WARN")
                csv_names = sorted(p.name for p in obj_set_dir.glob("*.csv"))
                result.add_issue(Issue(
                    severity=Severity.HIGH,
                    object_name=obj_set_dir.name,
                    message=(f"objectset_source/{obj_set_dir.name}/ is not a canonical "
                             f"object-set-N directory (expected 'object-set-' followed by a "
                             f"positive integer with no leading zero, and nothing else) — "
                             f"SFDMU never reads it, so the {len(csv_names)} CSV(s) in it are "
                             f"silently never loaded"
                             + (f": {', '.join(csv_names)}" if csv_names else "")),
                    file_path=self._make_relative_path(obj_set_dir)
                ))
                continue

            pass_number = int(match.group(1))  # 1-based
            pass_index = pass_number - 1  # Convert to 0-based index for objectSets array

            # Check if this pass exists in export.json. Normalized, so a flat `objects` plan counts
            # as one pass and its per-pass CSVs are read rather than silently discarded; and both
            # bounds, so `object-set-0` (pass_index -1) is rejected instead of indexing from the end.
            if not 0 <= pass_index < len(object_sets):
                self.log(f"Warning: {obj_set_dir.name} has no corresponding pass in export.json", level="WARN")
                # Reported, not only logged. A WARN is suppressed at default verbosity, so before
                # this a mistyped directory name was invisible: every CSV under it is silently
                # never read, which is the same end state as not having written them at all.
                # `object-set-0` is the likely typo — the directories are 1-based, so it maps to
                # pass_index -1 and used to be resolved against the *last* pass and mutated by the
                # fix modes.
                csv_names = sorted(p.name for p in obj_set_dir.glob("*.csv"))
                result.add_issue(Issue(
                    severity=Severity.HIGH,
                    object_name=obj_set_dir.name,
                    message=(f"objectset_source/{obj_set_dir.name}/ maps to no pass in "
                             f"export.json (directories are 1-based, and this plan has "
                             f"{len(object_sets)} pass(es)), so SFDMU never reads the "
                             f"{len(csv_names)} CSV(s) in it"
                             + (f": {', '.join(csv_names)}" if csv_names else "")),
                    file_path=self._make_relative_path(obj_set_dir)
                ))
                continue

            # Find all CSVs in this directory
            for csv_path in obj_set_dir.glob("*.csv"):
                obj_name = csv_path.stem  # Remove .csv extension
                overrides[(obj_name, pass_index)] = (csv_path, pass_index)
                self.log(f"Found override: {obj_name} in pass {pass_number} (index {pass_index})", level="DEBUG")

        return overrides

    def _get_object_configs_for_pass(self, all_pass_configs: Dict[str, Dict[int, List[dict]]],
                                     obj_name: str, pass_index: int) -> List[dict]:
        """Every declaration of `obj_name` in this pass, including Readonly and excluded.

        Reads `all_pass_configs` (per `_all_pass_configs`) rather than re-walking
        `_normalized_object_sets(export_data)` and re-normalizing every match — the same
        independent-traversal class already fixed once in this PR for
        `_writable_passes_by_object`. All three callers already have `all_pass_configs` in scope
        for the same plan, so the old walk was pure duplicate work; it was also a fourth private
        reimplementation of the normalizer's own logic, and reimplementations are exactly how a
        `str(externalId)` coercion landed in `_normalize_object_config` while this sibling, 143
        lines away, went without it — a non-string `externalId` still aborted the whole run for
        any plan with an `objectset_source/` override, which `qb/en-US/qb-billing` has.

        A list, not the first match. `_all_pass_configs` was changed to keep same-pass duplicates;
        this helper was not, so a per-pass override was still validated against whichever
        declaration came first. Readonly or simple-key first, writable composite second: the
        override was accepted without the required column.

        No bounds check on `pass_index`: `dict.get(key, default)` on `all_pass_configs[obj_name]`
        already returns `[]` for any pass this object was never declared in, negative or
        out-of-range alike — the same answer the old explicit `0 <= pass_index < len(...)` guard
        gave, without a comparison that guard's own docstring already said no mutation could kill.

        Callers that need "was this object declared here?" use this; callers that need "which
        declarations write the CSV?" use `_writable_configs_for_pass`. The two questions used to
        be one return, which is why a Readonly-only object with a per-pass CSV would have been
        reported as misfiled if this filtered.
        """
        return all_pass_configs.get(obj_name, {}).get(pass_index, [])

    def _writable_configs_for_pass(self, all_pass_configs: Dict[str, Dict[int, List[dict]]],
                                   obj_name: str, pass_index: int) -> List[dict]:
        """Live writable declarations of `obj_name` in this pass — what a source CSV is checked against."""
        return self._dedup_configs(
            [c for c in self._get_object_configs_for_pass(all_pass_configs, obj_name, pass_index)
             if self._is_live_writable(c)],
            self._READING_CONFIG_KEYS)

    def _validate_per_pass_csv(self, csv_path: Path, obj_name: str, pass_index: int,
                               obj_config: dict, result: ValidationResult):
        """Validate a per-pass CSV override in objectset_source/object-set-N/.

        externalId is not re-validated here: `_validate_object`'s `live_declarations` sweep already
        runs `_validate_external_id` on every non-excluded declaration in every pass, drawn from the
        same `_normalized_object_sets` source as `obj_config` — including this exact declaration.
        A second call here duplicated that check via an independent code path, made safe only by
        `add_issue`'s exact-message dedup; a pass-specific message on either side would double the
        finding for one declaration.

        No `excluded` guard: the sole caller draws `obj_config` from `_writable_configs_for_pass`,
        which already filters through `_is_live_writable` — the same dead-guard class already
        removed from `_validate_operation_value` in this PR.

        Args:
            csv_path: Path to the CSV file
            obj_name: Object API name
            pass_index: 0-based pass index
            obj_config: Object configuration for this pass
            result: ValidationResult to add issues to
        """
        pass_name = f"Pass {pass_index + 1}"
        self.log(f"\nValidating {pass_name} override: {obj_name} ({csv_path.name})", level="DEBUG")
        self._validate_csv_file(csv_path, obj_name, obj_config, result, pass_index=pass_index)

    def _validate_object(self, dataset_path: Path, obj_name: str, result: ValidationResult,
                         objects_owing_root_csv: Dict[str, List[dict]],
                         all_pass_configs: Dict[str, Dict[int, List[dict]]]):
        """Validate a single object's CSV and configuration.

        Args:
            dataset_path: Path to dataset directory
            obj_name: Object API name
            result: ValidationResult to add issues to
            objects_owing_root_csv: Objects that must have a CSV at the plan root, mapped to the
                declarations that read it, per `_objects_owing_root_csv`. Required, not defaulted:
                there is one call site and it always computes the mapping, so an `Optional` default
                would be unreachable code — including the two paragraphs that justified `None` as
                "the safe direction", which no input exercised.
            all_pass_configs: Every declaration of every object, per `_all_pass_configs`, so the
                `operation` and `externalId` checks can run per pass instead of on the merged view.
        """
        self.log(f"\nValidating object: {obj_name}", level="DEBUG")

        # Skip excluded objects — but the merged config (`object_configs`'s value, kept only for the
        # first declaration) would make `excluded` mean "excluded in the first pass that declared it"
        # and not "excluded everywhere". Returning on that hides a later pass that does write from a
        # file: excluded in pass 1 and Upsert in pass 2 with no CSV anywhere reported nothing worse
        # than Info. Same merged-config trap as `operation`, which `_objects_owing_root_csv` exists
        # to avoid, so defer to it — it enumerates passes and already skips the excluded ones.
        # `objects_owing_root_csv and` used to guard this, left over from the `Optional` signature.
        # Dead once the parameter became required — an empty mapping already fails the `in`, and it is
        # a `Dict[str, List[dict]]` now rather than the `Set[str]` an earlier version passed — and
        # worse than dead: it read as if `None` were still reachable, which the docstring above
        # explicitly says it is not.
        # Both per-declaration sweeps run BEFORE the excluded early return below, because that return
        # reads the *merged* config and these do not. An object excluded in its first-declaring pass
        # but live and writable in a later one exits there whenever the later pass is covered by an
        # `objectset_source/` override — the `qb/en-US/qb-billing` shape — so a defect on the live
        # declaration was unreportable. For the malformed-externalId check that was the worse of the
        # two failures this file is built to avoid: the same plan *aborted* the whole run before the
        # coercion landed, and was silent after it. Placement, not logic, was the defect.
        live_declarations = [cfg for by_pass in [all_pass_configs.get(obj_name, {})]
                             for cfgs in by_pass.values() for cfg in cfgs
                             if not self._is_js_truthy(cfg.get("excluded"))]

        # `operation` per declaration, not per merged config: reading the merged config validates
        # pass 1 and exempts passes 2..n, so a bogus operation introduced in a later pass was
        # unreportable. Readonly declarations are included, since a Readonly operation is exactly the
        # kind that resolves to `undefined` unnoticed; `excluded` ones are not, because SFDMU does not
        # process them, so their operation is inert and reporting it is a false positive.
        for cfg in self._dedup_configs(live_declarations, self._OPERATION_CHECK_KEYS):
            self._validate_operation_value(obj_name, cfg, result)

        # A non-string `externalId` is reported rather than silently accepted. Coercing it to `str` in
        # `_normalize_object_config` is what stops it aborting the whole run, but the coerced repr
        # matches no downstream gate, so without this the plan reports nothing.
        #
        # Filtered to live declarations, like the operation check above it. The first version was not,
        # which inverted the treatment of `excluded` inside one commit: inert declarations reported,
        # live ones skipped. Deduped only to avoid repeated work — `ValidationResult.add_issue`
        # already collapses identical findings, and this message is a pure function of the value, so
        # removing the dedup changes no count.
        for cfg in self._dedup_configs([c for c in live_declarations
                                        if c.get("externalId_malformed")], ("externalId",)):
            value = cfg.get("externalId")
            result.add_issue(Issue(
                severity=Severity.HIGH,
                object_name=obj_name,
                # Names the type as well as the value: the repr alone cannot distinguish `1` from
                # `"1"`, which is the one case where a reader needs to be told which they have.
                message=(f"externalId is not a string, it is {cfg.get('externalId_type')}: {value} — "
                         f"SFDMU expects a ';'-delimited field list, so this declaration cannot "
                         f"match target records"),
            ))

        # Scoped to `objects_owing_root_csv` once, on the theory that a pass reading no file cannot
        # have a SELECT-coverage defect. Wrong: a `Readonly` declaration reads no *file* but still
        # executes its SOQL against the target org in every pass, so its externalId fields still need
        # to be in that pass's SELECT clause — a requirement that has nothing to do with whether some
        # *other* declaration of the same object owes a CSV. Scoping by CSV-reading status meant that
        # adding a writable sibling pass (or covering every writable pass under `objectset_source/`)
        # made an unrelated Readonly pass's own SELECT gap stop being validated — reachable identically
        # whether the Readonly declaration shared a pass with a writable one or lived in its own pass.
        # `live_declarations` (computed above, for the `operation`/malformed-externalId sweeps) is
        # already every non-excluded declaration across every pass, so it is reused here too — CSV
        # existence/header checks stay scoped to `objects_owing_root_csv` below, where "which pass
        # reads the file" is the actual question.
        #
        # Run BEFORE the excluded early return below, for the same reason the operation and
        # malformed-externalId sweeps above are: that return reads the *merged* config, so an object
        # excluded in its first-declaring pass but live (e.g. Readonly) in a later one exited before
        # this loop ever ran, silently dropping that live declaration's own SELECT-coverage check.
        # Excludes an already-malformed externalId (`str()`-coerced non-string, flagged above):
        # a coerced repr that happens to contain ';' would otherwise be split and checked for
        # SELECT-clause coverage component-by-component, piling extra HIGHs onto the dedicated
        # malformed-externalId HIGH for the same root cause.
        #
        # Dedup key adds `externalId_malformed` to `_READING_CONFIG_KEYS`: the coercion in
        # `_normalize_object_config` means a malformed declaration's `externalId` string can equal a
        # well-formed sibling's (e.g. int `123` coerces to `"123"`, same as a literal `"123"`), so with
        # `_READING_CONFIG_KEYS` alone the two collapse into one entry. If the malformed one sorts
        # first, the `continue` above then skips the *kept* entry — silently dropping the well-formed
        # sibling's SELECT-coverage check instead of just skipping the malformed one, as intended.
        for cfg in self._dedup_configs(live_declarations,
                                        self._READING_CONFIG_KEYS + ("externalId_malformed",)):
            if cfg.get("externalId_malformed"):
                continue
            self._validate_external_id(obj_name, cfg.get("externalId", ""), cfg, result)

        # Check deleteOldData usage — per declaration, not the merged config: reading the
        # merged view here validates only the first pass and exempts passes 2..n, the same
        # merged-config trap already fixed above for `operation`/excluded/externalId. `add_issue`'s
        # exact-message dedup keeps a shared flag across passes from reporting twice.
        #
        # Run BEFORE the excluded early return below, same reason as the three sweeps above it: an
        # object excluded in its first-declaring pass but live and writable in a later one — the
        # later pass fully covered by an `objectset_source/` override — exits at that return before
        # ever reaching a loop placed after it, silently dropping the later pass's own flag.
        for cfg in self._dedup_configs(live_declarations, ("deleteOldData",)):
            if self._is_js_truthy(cfg.get("deleteOldData")) and obj_name not in self.DELETE_OLD_DATA_OBJECTS:
                result.add_issue(Issue(
                    severity=Severity.INFO,
                    object_name=obj_name,
                    message=f"Object uses 'deleteOldData: true' but not in documented list"
                ))

        # `not live_declarations`, not the merged config's own `excluded`: the merged view
        # means "excluded in the first pass that declared it", so an object excluded in pass 1 but
        # live (e.g. Readonly, or Upsert covered under objectset_source/) in a later pass hit this
        # branch and got a spurious "excluded but not in known excluded list" Info — the same
        # merged-config trap fixed above for operation/externalId/deleteOldData, here in this
        # check's own message rather than in what it validates. `live_declarations` is already
        # every non-excluded declaration across every pass, so "no live declarations" is the
        # correct "excluded everywhere" test; a live-but-excluded-first-pass object is never in it.
        # This also makes the old `and obj_name not in objects_owing_root_csv` guard redundant:
        # `_is_live_writable`/`_writable_passes_by_object` already treat `excluded` as non-writable,
        # so an object with no live declarations can never appear in `objects_owing_root_csv` either.
        if not live_declarations:
            self.log(f"  Skipping excluded object: {obj_name}", level="DEBUG")
            if obj_name not in self.KNOWN_EXCLUDED_OBJECTS:
                result.add_issue(Issue(
                    severity=Severity.INFO,
                    object_name=obj_name,
                    message=f"Object is excluded but not in known excluded list"
                ))
            return

        # Ask for a root CSV only where one is owed. Asking unconditionally was this check's entire
        # false-positive rate (#264-51 / pack 123) — two Criticals on correct data, which is enough
        # to make a validator ignored. `_objects_owing_root_csv` carries the reasoning and the two
        # shapes that owe nothing: Readonly in every pass (queried from the target org), and every
        # writable pass already supplied under objectset_source/ (an alternative location for the
        # same file, validated by _validate_per_pass_csv below).
        if obj_name in objects_owing_root_csv:
            csv_path = dataset_path / f"{obj_name}.csv"
            # Against every pass that reads this file, not the merged config — see
            # `_objects_owing_root_csv`. A pass-2 composite key went unasked-for otherwise.
            #
            # Deliberately not passing `pass_index` here (unlike the per-pass override call
            # below): the root file is one shared path read by every pass in this list, not a
            # per-pass artifact, so "CSV file not found" is a property of the *path*, not of
            # whichever pass's declaration happens to trigger it first. A local `/code-review`
            # pass flagged the omission as an inconsistency and threading `cfg["pass_index"]`
            # through was tried — it broke "a missing CSV is one finding however many passes read
            # it" immediately: the message became "Pass 1: ... not found" vs "Pass 2: ... not
            # found" for the identical missing file, and `add_issue`'s message-keyed dedup no
            # longer collapsed them. Reverted; the omission is intentional.
            for cfg in objects_owing_root_csv[obj_name]:
                self._validate_csv_file(csv_path, obj_name, cfg, result)
        else:
            self.log(f"  No root CSV owed by {obj_name} — Readonly, or every writable pass is "
                     f"supplied under objectset_source/", level="DEBUG")

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

        # Resolve operation once — both downstream externalId checks (nested-path
        # traversal, SELECT-coverage) need to skip Insert mode, where externalId
        # is used for CSV composite-key matching within the dataset rather than
        # SOQL behavior.
        # `_resolve_operation` mirrors `ScriptLoader._resolveOperation`, resolving string,
        # numeric-index and integral-float operations alike and returning `None` (kept off
        # `insert`, same as an absent/malformed operation) for anything SFDMU would drop. A raw
        # `str(obj_config.get("operation") or "Readonly")` used to bypass this: `0 or "Readonly"`
        # treats numeric Insert (index 0) as falsy, coercing it to Readonly and wrongly running
        # the nested-path/SELECT-coverage checks below that string Insert correctly skips.
        is_insert = self._resolve_operation(obj_config.get("operation")) == "insert"

        # Check for legacy $$ notation in externalId definition
        if "$$" in external_id:
            result.add_issue(Issue(
                severity=Severity.MEDIUM,
                object_name=obj_name,
                message=f"externalId uses legacy $$ notation: '{external_id}'. SFDMU v5 requires semicolon-delimited format (e.g., 'Field1;Field2')"
            ))

        # Check for nested relationship paths (v5 flattening issue).
        # Skip for Insert operations: externalId is only used for CSV composite key
        # matching, not for SOQL traversal, so nested paths do not cause runtime errors.
        #
        # Shared with every other externalId-splitting site via `_split_external_id_fields`: an
        # unstripped "Field1; Field2" leaves ' Field2', which never matches the parsed (trimmed)
        # SELECT-field set below even when the query correctly selects Field2 — a false HIGH on
        # correct data, the exact class this PR exists to eliminate.
        fields = self._split_external_id_fields(external_id)
        if not is_insert:
            for field in fields:
                # Count dots (more than 1 = nested relationship)
                dot_count = field.count(".")
                if dot_count > 1:
                    result.add_issue(Issue(
                        severity=Severity.MEDIUM,
                        object_name=obj_name,
                        message=f"externalId contains nested relationship path '{field}' which may cause v5 flattening errors"
                    ))

        # Validate that composite key components are in the query.
        # Skip for Insert operations: externalId is used only for CSV composite key
        # matching within the dataset, not for SOQL record matching, so the fields
        # do not need to appear in the SELECT clause.
        if ";" in external_id and not is_insert:
            query_fields = set(obj_config.get("fields", []))
            for field in fields:
                # Require that each externalId component is explicitly present in the query
                if field not in query_fields:
                    # For relationship fields like Parent.Name, require an exact match in the
                    # SELECT clause to avoid incorrectly treating similarly prefixed fields
                    # (e.g., ParentId) as satisfying the externalId component.
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
                # Skip objects with deleteOldData: true (delete-then-insert strategy doesn't need composite key)
                external_id = obj_config.get("externalId", "")
                if self._owes_composite_key_column(external_id, obj_config):
                    # This is a composite key - check if CSV has the $$ column. Stripped fields,
                    # same as the fixer that writes this column — an unstripped "Field1; Field2"
                    # expects a column with an embedded space that the fixer, which does strip,
                    # never writes, so --fix-composite-keys and re-validating the same plan would
                    # never converge.
                    expected_composite_col = self._build_composite_key_column_name(
                        self._split_external_id_fields(external_id))

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

    @staticmethod
    def _union_fields(configs: List[dict]) -> List[str]:
        """Ordered union of every config's `fields`, first-seen order, no duplicates.

        An empty CSV's header must satisfy every declaration that reads it, not just the first:
        a composite-key fix for a later declaration can only add its `$$A$B` column when `A` and
        `B` are already headers, so building from a single declaration silently stranded any
        field only a *different* declaration in the same `reading`/pass group selects.
        """
        return list(dict.fromkeys(
            field for cfg in configs for field in cfg.get("fields", [])
        ))

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

        # An empty header list is not writable. `writer.writerow([])` emits only a line terminator, so
        # the file stays empty by `_is_csv_empty`, SFDMU still cannot read it, and returning True
        # counted a fix that did not happen. Harmless while the caller re-fixed on the next
        # declaration; a real defect once `header_written` began trusting the return value, which
        # turned a later pass's correct header into a suppressed one and left `"\r\n"` on disk where a
        # usable header had been. Guarded here rather than at that call site so both callers get it.
        if not headers:
            self.log(f"  Cannot add header to {csv_path.name}: no SELECT fields to write",
                     level="WARN")
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

    @staticmethod
    def _split_external_id_fields(external_id: str) -> List[str]:
        """Split a ';'-delimited externalId into stripped field names.

        Centralizes a pattern that was hand-copied at four sites (the two composite-key
        fixer loops, `_validate_external_id`'s nested-path check, and `_validate_csv_file`'s
        composite-column-name check) — stripped, unlike a bare `.split(";")`, because an
        unstripped `"Field1; Field2"` leaves `" Field2"`, which matches neither a parsed SELECT
        field nor the fixer's own (stripped) composite-key column name.

        Empty segments are dropped: a trailing or doubled `;` (`"Field1;Field2;"`,
        `"Field1;;Field2"`) otherwise yields a `""` field that flows into every consumer as a
        component to check, reporting a confusing `externalId component '' not found in query
        SELECT clause` instead of leaving the malformed-externalId detection in
        `_normalize_object_config` to name the actual problem.
        """
        return [f for f in (segment.strip() for segment in external_id.split(";")) if f]

    def _owes_composite_key_column(self, external_id: str, cfg: dict) -> bool:
        """Whether a declaration's CSV must carry a `$$`-prefixed composite key column.

        Centralizes a predicate hand-copied at three sites (both fixer loops and
        `_validate_csv_file`): a multi-field, non-`$$`-notation externalId needs the column
        UNLESS `deleteOldData` makes SFDMU delete-then-insert instead of upsert-matching against
        it. `deleteOldData` is read via `_is_js_truthy`, not plain Python truthiness, for the same
        reason `excluded` is — SFDMU reads it with JS truthiness, so `deleteOldData: []`/`{}`
        (JS-truthy) would otherwise be misread as Python-falsy and wrongly demand a column
        SFDMU's delete-then-insert path doesn't need.
        """
        return (";" in external_id and not external_id.startswith("$$")
                and not self._is_js_truthy(cfg.get("deleteOldData")))

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
            self.log(
                f"  ❌ Error: Missing component fields for {obj_name}: {', '.join(missing_fields)}",
                level="ERROR",
            )
            self.log(
                f"  ❌ Cannot generate composite key column {composite_col_name} because required component field(s) are missing.",
                level="ERROR",
            )
            return False

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

    def fix_dataset_issues(self, dataset_path: Path, object_configs: Dict[str, dict],
                           objects_owing_root_csv: Dict[str, List[dict]]) -> Tuple[int, int]:
        """Fix issues in a dataset (headers and/or composite keys).

        Args:
            dataset_path: Path to dataset directory
            object_configs: Object configurations from export.json
            objects_owing_root_csv: Per `_objects_owing_root_csv` — the declarations validation checks
                each root CSV against, so the fixer writes what validation asks for. Required, not
                defaulted: the merged-config fallback an optional default would invite is the exact
                non-convergent `--fix-all` behavior this file exists to have fixed, and the sole call
                site already has this dict in scope — there is no real caller for a default to serve.

        Returns:
            Tuple of (headers_fixed, composite_keys_fixed)
        """
        headers_fixed = 0
        composite_keys_fixed = 0

        for obj_name in object_configs:
            # The merged first declaration is the wrong skip: an object excluded (or Readonly) in
            # pass 1 and writable in pass 2 has `excluded=True` here, so the per-reading-config loop
            # below never ran and `--fix-all` left pass 2's composite-key finding standing. Skip on
            # whether anything *reads* the root CSV, which is the same question validation asks.
            reading = objects_owing_root_csv.get(obj_name)
            if not reading:
                continue

            csv_path = dataset_path / f"{obj_name}.csv"
            if not csv_path.exists():
                continue

            # The same declarations validation checks this file against, so what is reportable is
            # fixable. Reading the merged config here while validation read the reading passes made
            # `--fix-all` non-convergent for exactly the class this file just started reporting: with
            # pass 1 `Readonly`/`externalId: Name` and pass 2 `Upsert`/`Name;Code`, validation asked
            # for a `$$Name$Code` column and the fixer saw no `;` in `Name` and wrote nothing, so a
            # fix run left the finding standing. A checker that reports what its own fixer cannot
            # clear teaches people to ignore it.
            #
            # The empty-CSV header is written once, from the union of every reading declaration's
            # fields — not just the first, which stranded a later declaration's composite-key fix:
            # with an empty CSV, pass 1 selecting `Id,Name` and pass 2's externalId `Name;Code`,
            # writing pass 1's header alone left `Code` absent, so pass 2's `$$Name$Code` fix could
            # never run and `--fix-all` left its own High finding standing. See `_union_fields`.
            # Composite-key fixes are idempotent via `_csv_missing_composite_key`, so iterating
            # cannot double-write. Tracked across declarations because `--dry-run` does not mutate
            # the file, so the `_csv_missing_composite_key` probe that makes a real run's second
            # iteration a no-op stays true — iterating without `columns_written` then proposed the
            # same composite column once per declaration that shares it. A real run's byte output
            # was always correct; the dry-run *report* was not, which is worse than a wrong count,
            # because the dry run is what people read before deciding to apply it.
            columns_written = set()
            if self.fix_headers and self._is_csv_empty(csv_path):
                headers = self._union_fields(reading)
                if self._fix_empty_csv_header(csv_path, headers, obj_name):
                    headers_fixed += 1

            for cfg in reading:
                # Fix missing composite keys (only if CSV is not empty, skip deleteOldData objects)
                if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                    external_id = cfg.get("externalId", "")
                    if self._owes_composite_key_column(external_id, cfg):
                        fields = self._split_external_id_fields(external_id)
                        composite_col_name = self._build_composite_key_column_name(fields)

                        # Check if column is missing using helper method
                        if (composite_col_name not in columns_written
                                and self._csv_missing_composite_key(csv_path, composite_col_name)):
                            if self._fix_missing_composite_key(csv_path, fields, obj_name):
                                composite_keys_fixed += 1
                                columns_written.add(composite_col_name)

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
                # Skip internal subdirs, developer-local scratch (test/), and backup dirs (*.bak).
                # Filter on the path relative to the --dataset parent, not the checkout path.
                if _is_skippable_export(export_json, dataset_path):
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
