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

        # Apply fixes if requested (before validation)
        if self.fix_headers or self.fix_composite_keys:
            self.log(f"\n{'='*60}")
            self.log(f"Applying fixes to: {dataset_name}")
            self.log(f"{'='*60}")
            headers_fixed, composite_keys_fixed = self.fix_dataset_issues(
                dataset_path, object_configs,
                self._objects_owing_root_csv(export_data, objectset_source_overrides))

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

                        # Apply composite key fix if needed (skip deleteOldData objects)
                        if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                            external_id = obj_config.get("externalId", "")
                            if ";" in external_id and not external_id.startswith("$$") and not obj_config.get("deleteOldData"):
                                fields = [f.strip() for f in external_id.split(";")]
                                composite_col_name = self._build_composite_key_column_name(fields)

                                # Check if column is missing using helper method
                                if self._csv_missing_composite_key(csv_path, composite_col_name):
                                    if self._fix_missing_composite_key(csv_path, fields, obj_name):
                                        composite_keys_fixed += 1

            if headers_fixed > 0 or composite_keys_fixed > 0:
                print(f"\n  Fixed {headers_fixed} header(s) and {composite_keys_fixed} composite key column(s)")

        # Validate each object's CSV and composite key configuration
        objects_owing_root_csv = self._objects_owing_root_csv(export_data, objectset_source_overrides)
        all_pass_configs = self._all_pass_configs(export_data)
        for obj_name, obj_config in object_configs.items():
            self._validate_object(dataset_path, obj_name, obj_config, result,
                                  objects_owing_root_csv, all_pass_configs)

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

    @staticmethod
    def _normalized_object_sets(export_data: dict) -> List[dict]:
        """The plan's passes, with a flat `objects` plan presented as a single pass.

        Three call sites need to agree on this and used to disagree: the writable-pass map
        normalized flat plans, `_get_object_config_for_pass` read `objectSets` raw (so it resolved
        nothing for a flat plan), and `_find_objectset_source_overrides` bounds-checked against the
        raw list (so it discarded every per-pass CSV in a flat plan, reporting only a WARN that is
        suppressed at default verbosity). Any two of those disagreeing is a silent wrong answer
        rather than an error, so the normalization lives in one place.

        It changes what the fix modes *write*, not only what validation reads, and that is easy to
        miss because every justification above is about reading. A flat `objects` plan with an
        `objectset_source/object-set-1/` directory previously had those CSVs discarded before the
        fix loop saw them; now `--fix-headers` writes a header row into them. That is the intended
        behavior — the file is one SFDMU reads — but no shipped plan has that shape (flat `objects`
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

    def _writable_passes_by_object(self, export_data: dict) -> Dict[str, Set[int]]:
        """Map each object to the 0-based passes in which this plan writes it from a file.

        Distinct from the merged config `_parse_object_configs` returns, which keeps only the
        *first* declaration: an object may be Readonly in one pass and Upsert in another, and it
        is the per-pass detail — not the union, and not the first entry — that decides which
        source files are owed. Keeping the pass numbers is what lets a caller ask whether *this*
        pass has a file, rather than whether the object has one somewhere.
        """
        writable: Dict[str, Set[int]] = {}
        for idx, obj_set in enumerate(self._normalized_object_sets(export_data)):
            for obj in obj_set.get("objects", []):
                obj_name = self._extract_object_name(obj.get("query", ""))
                if not obj_name or obj.get("excluded"):
                    continue
                # str() because a malformed plan can carry a non-string here (`"operation": true`).
                # This runs for every object in every plan, so an AttributeError would abort the
                # whole run and turn a reportable defect in one plan into no report at all.
                #
                # `.strip().lower()` matches SFDMU, and the authoritative function is worth naming
                # because there are two and they disagree. `ScriptLoader._resolveOperation` is the
                # one that loads export.json (v5.8.0): it does `operation.trim().toLowerCase()` and
                # matches enum keys case-insensitively, so `" ReadOnly "` resolves to Readonly.
                # `ScriptObject.getOperation` is a secondary path doing a raw `OPERATION[operation]`
                # lookup with neither. Reading the latter as authoritative makes this look too
                # lenient and argues for dropping the normalization — which would then report the
                # nine `"ReadOnly"` declarations in this repo as defects. SFDMU accepts them.
                if str(obj.get("operation") or "Upsert").strip().lower() != "readonly":
                    writable.setdefault(obj_name, set()).add(idx)
        return writable

    # SFDMU's `OPERATION` enum as spelled in `Enumerations.js` (v5.8.0), lowercased because that is
    # how `ScriptLoader._resolveOperation` compares. `Unknown` is the enum's own fallback rather
    # than something a plan declares, so it is not accepted.
    SFDMU_OPERATIONS = frozenset({"insert", "update", "upsert", "readonly", "delete",
                                  "deletesource", "deletehierarchy", "harddelete"})

    def _validate_operation_value(self, obj_name: str, obj_config: dict, result: ValidationResult):
        """Report an `operation` SFDMU cannot resolve.

        Mirrors `ScriptLoader._resolveOperation` (v5.8.0), the function that loads export.json:
        strings are matched `trim().toLowerCase()` against the enum keys, so `" ReadOnly "` is fine;
        anything else — a non-string, or a word not in the enum — resolves to `undefined` and the
        declaration is silently dropped, leaving the object on SFDMU's default rather than the
        operation the plan asked for.

        Written first against `ScriptObject.getOperation`, which does a raw `OPERATION[operation]`
        lookup with no trimming or case folding. That reading made the nine `"ReadOnly"`
        declarations in this repo look like defects, which is how the wrong function was caught:
        they are accepted, because the loader is the code path a plan actually goes through.
        """
        if "operation" not in obj_config:
            return  # absent is legal; SFDMU's script default applies
        operation = obj_config["operation"]
        if isinstance(operation, str) and operation.strip().lower() in self.SFDMU_OPERATIONS:
            return
        result.add_issue(Issue(
            severity=Severity.HIGH,
            object_name=obj_name,
            message=(f"operation {operation!r} is not one SFDMU can resolve; it matches "
                     f"trim()/case-insensitively against {', '.join(sorted(self.SFDMU_OPERATIONS))} "
                     f"and silently ignores anything else, leaving the object on the default "
                     f"operation instead of the one declared")
        ))

    def _objects_owing_root_csv(self, export_data: dict,
                                objectset_source_overrides: Dict[Tuple[str, int], Tuple[Path, int]]) -> Dict[str, List[dict]]:
        """Objects that must have a CSV at the plan root -> the declarations that read it.

        Returns a mapping rather than a set so membership (`obj_name in ...`) still answers "is a
        root CSV owed", while the value carries **which** passes read it. The root file has to be
        validated against those, not against the merged config: `_parse_object_configs` keeps the
        first declaration, so a pass-1 `Readonly`/excluded declaration followed by a writable pass 2
        had the file checked against pass 1's `query` and `externalId`. A pass-2 composite key needing
        a `$$A$B` column in that same file was then never asked for, and a CSV carrying only pass 1's
        single column passed. Verified by the `MERGED CONFIG` cases in
        `tests/test_sfdmu_csv_expectation.py`.

        A plan reads a writable pass's records from `objectset_source/object-set-N/<Object>.csv`
        when that file exists, and from `<plan>/<Object>.csv` otherwise. So the root file is owed
        as soon as *any* writable pass lacks an override — which is why this is keyed on the pass
        and not on the object name.

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
        writable_passes = self._writable_passes_by_object(export_data)
        all_configs = self._all_pass_configs(export_data)
        covered: Dict[str, Set[int]] = {}
        for (obj_name, pass_index) in objectset_source_overrides:
            covered.setdefault(obj_name, set()).add(pass_index)

        owed: Dict[str, List[dict]] = {}
        for obj_name, passes in writable_passes.items():
            uncovered = sorted(passes - covered.get(obj_name, set()))
            if uncovered:
                # Flattened: a pass index maps to a *list* of declarations, since one objectSet may
                # declare the object more than once. Deduped on the union of what every consumer of
                # this list reads — see `_READING_CONFIG_KEYS`; narrowing it to one consumer's fields
                # silently disabled the other's check.
                # `excluded` declarations dropped here, not just at the pass level. `writable_passes`
                # already excludes a pass whose *only* declaration is excluded, but a pass declaring
                # the object twice — once excluded — contributed the excluded one to this list, and
                # widening the dedup key to include `fields` stopped it collapsing into its sibling.
                # SFDMU never processes an excluded declaration, so a SELECT gap in one is not a
                # defect; the operation check has taken that stance all along.
                declarations = [cfg for i in uncovered for cfg in all_configs[obj_name][i]
                                if not cfg.get("excluded")]
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
                    configs[obj_name] = self._normalize_object_config(obj, query, idx)

        return configs

    def _normalize_object_config(self, obj: dict, query: str, idx: int) -> dict:
        """One export.json declaration in the shape every check downstream expects.

        Shared with `_all_pass_configs` so a per-pass config is indistinguishable from a merged one.
        Not cosmetic: the checks read *derived* keys, not the raw declaration — `_validate_external_id`
        reads `fields` (the parsed SELECT), so handing it a raw declaration makes `fields` empty and
        every externalId component read as absent from the query. Measured: forcing `fields` empty
        takes the tree from 7 High to **252 High**, 245 of them spurious SELECT-coverage findings. So
        this normalizer, not the reading-pass scoping below it, is what holds that back — the two were
        conflated in earlier notes quoting 241 and 258, neither of which reproduces.

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
        raw_external_id = obj.get("externalId", "Id")
        return {
            "pass_index": idx,
            "operation": obj.get("operation", "Upsert"),
            "externalId": str(raw_external_id),
            # Recorded rather than reported here: this function has no `result` to add an issue to,
            # and threading one in would make a pure normalizer a validator.
            "externalId_malformed": not isinstance(raw_external_id, str),
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
        match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not match:
            return []

        fields_str = match.group(1)
        # Split by comma, strip whitespace
        fields = [f.strip() for f in fields_str.split(',')]
        return fields

    def _find_objectset_source_overrides(self, dataset_path: Path, export_data: dict,
                                         result: Optional[ValidationResult] = None) -> Dict[Tuple[str, int], Tuple[Path, int]]:
        """Find per-pass CSV overrides in objectset_source/object-set-N/.

        Args:
            dataset_path: Path to dataset directory
            export_data: Parsed export.json data
            result: Optional result to report a directory that maps to no pass. Optional because
                the fix modes call this to locate files and have no result to report into; when it
                is omitted the condition is still logged.

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

            # Check if this pass exists in export.json. Normalized, so a flat `objects` plan counts
            # as one pass and its per-pass CSVs are read rather than silently discarded; and both
            # bounds, so `object-set-0` (pass_index -1) is rejected instead of indexing from the end.
            object_sets = self._normalized_object_sets(export_data)
            if not 0 <= pass_index < len(object_sets):
                self.log(f"Warning: {obj_set_dir.name} has no corresponding pass in export.json", level="WARN")
                # Reported, not only logged. A WARN is suppressed at default verbosity, so before
                # this a mistyped directory name was invisible: every CSV under it is silently
                # never read, which is the same end state as not having written them at all.
                # `object-set-0` is the likely typo — the directories are 1-based, so it maps to
                # pass_index -1 and used to be resolved against the *last* pass and mutated by the
                # fix modes.
                if result is not None:
                    csv_names = sorted(p.name for p in obj_set_dir.glob("*.csv"))
                    result.add_issue(Issue(
                        severity=Severity.HIGH,
                        object_name=obj_set_dir.name,
                        message=(f"objectset_source/{obj_set_dir.name}/ maps to no pass in "
                                 f"export.json (directories are 1-based, and this plan has "
                                 f"{len(object_sets)} pass(es)), so SFDMU never reads the "
                                 f"{len(csv_names)} CSV(s) in it"
                                 + (f": {', '.join(csv_names)}" if csv_names else "")),
                        file_path=str(obj_set_dir)
                    ))
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
        object_sets = self._normalized_object_sets(export_data)
        # Both bounds, because `object-set-0` maps to pass_index -1 and an upper-bound-only check
        # admits it, resolving the negative index against the LAST pass.
        #
        # Redundant today, and said plainly rather than left to look load-bearing: all three callers
        # take `pass_index` from `_find_objectset_source_overrides`, which now applies the same
        # check, so no input reaches here out of range and mutating this line kills no test. It
        # stays as an argument-validity check on a helper that accepts an arbitrary int — but a
        # guard no mutation can kill is exactly what this repo keeps learning to distrust, so it is
        # labelled instead of counted as coverage.
        if not 0 <= pass_index < len(object_sets):
            return None

        for obj in object_sets[pass_index].get("objects", []):
            query = obj.get("query", "")
            if self._extract_object_name(query) == obj_name:
                # Through the shared normalizer, not a hand-rolled copy of it. This was the copy, and
                # it is why "the single point that makes the file total" was a false claim when it was
                # written: the normalizer grew a `str(externalId)` coercion and this sibling, 143
                # lines away, did not — so a non-string externalId still aborted the whole run for any
                # plan with an `objectset_source/` override, which `qb/en-US/qb-billing` has. Three
                # config builders drifting is the shape of the bug; two were already merged, this is
                # the third.
                return self._normalize_object_config(obj, query, pass_index)

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

    def _validate_object(self, dataset_path: Path, obj_name: str, obj_config: dict, result: ValidationResult,
                         objects_owing_root_csv: Dict[str, List[dict]],
                         all_pass_configs: Dict[str, Dict[int, List[dict]]]):
        """Validate a single object's CSV and configuration.

        Args:
            dataset_path: Path to dataset directory
            obj_name: Object API name
            obj_config: Object configuration from export.json
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

        # Skip excluded objects — but `obj_config` is the *merged* view, which keeps only the first
        # declaration, so `excluded` here means "excluded in the first pass that declared it" and
        # not "excluded everywhere". Returning on that hides a later pass that does write from a
        # file: excluded in pass 1 and Upsert in pass 2 with no CSV anywhere reported nothing worse
        # than Info. Same merged-config trap as `operation`, which `_objects_owing_root_csv` exists
        # to avoid, so defer to it — it enumerates passes and already skips the excluded ones.
        # `objects_owing_root_csv and` used to guard this, left over from the `Optional` signature.
        # Dead once the parameter became required — an empty mapping already fails the `in`, and it is
        # a `Dict[str, List[dict]]` now rather than the `Set[str]` an earlier version passed — and
        # worse than dead: it read as if `None` were still reachable, which the docstring above
        # explicitly says it is not.
        if obj_config.get("excluded") and obj_name not in objects_owing_root_csv:
            self.log(f"  Skipping excluded object: {obj_name}", level="DEBUG")
            if obj_name not in self.KNOWN_EXCLUDED_OBJECTS:
                result.add_issue(Issue(
                    severity=Severity.INFO,
                    object_name=obj_name,
                    message=f"Object is excluded but not in known excluded list"
                ))
            return

        # `operation` per declaration, not per merged config: same trap as `excluded` above and the
        # root CSV below — reading the merged config validates pass 1 and exempts passes 2..n, so a
        # bogus operation introduced in a later pass was unreportable. Readonly declarations are
        # included, since a Readonly operation is exactly the kind that resolves to `undefined`
        # unnoticed; `excluded` ones are not, because SFDMU does not process them, so their operation
        # is inert and reporting it is a false positive the merged-config version never produced.
        # Every other site in this file takes that stance already.
        declarations = [cfg for by_pass in [all_pass_configs.get(obj_name, {})]
                        for cfgs in by_pass.values() for cfg in cfgs
                        if not cfg.get("excluded")]
        for cfg in self._dedup_configs(declarations, self._OPERATION_CHECK_KEYS):
            self._validate_operation_value(obj_name, cfg, result)

        # A non-string `externalId` is reported rather than silently accepted. Coercing it to `str`
        # in `_normalize_object_config` is what stops it aborting the whole run, but the coerced repr
        # matches no downstream gate, so without this the plan reports nothing — the trade the
        # normalizer's docstring first claimed it had avoided. Swept across every declaration, since
        # any pass can carry one, and deduped on the value so one malformed declaration is one issue.
        for cfg in self._dedup_configs(
                [c for by in [all_pass_configs.get(obj_name, {})] for cs in by.values() for c in cs
                 if c.get("externalId_malformed")], ("externalId",)):
            result.add_issue(Issue(
                severity=Severity.HIGH,
                object_name=obj_name,
                message=(f"externalId is not a string: {cfg.get('externalId')} — SFDMU expects a "
                         f"';'-delimited field list, so this declaration cannot match target records"),
            ))

        # externalId is *not* swept across every declaration, and the honest reason is narrower than
        # the one that was written here first. **Measured on this tree, scoping makes no difference:**
        # sweeping every normalized declaration leaves High at 7 and produces 0 SELECT-coverage
        # findings, identical to the scoped form. The earlier claim — that sweeping "reported 241 High
        # findings against correct plans" because later passes are narrow-SELECT activations — is
        # false, and worth correcting rather than deleting, because it would tell a future reader this
        # line is holding back a flood and make them refuse a simplification on evidence that does not
        # exist. No later-pass declaration in this repo has that shape.
        #
        # The flood was real but came from somewhere else: **un-normalized** declarations, whose
        # derived `fields` is absent, so every externalId component reads as missing from the SELECT.
        # Forcing `fields` empty gives 252 High / 245 SELECT-coverage findings — and gives the *same*
        # 252 whether scoped or swept, which is the proof that normalization fixed it and scoping did
        # not. (Earlier notes said 241 and 258; both are unreproducible artifacts of intermediate
        # trees. The number depends on the reconstruction, which is why the mechanism above is stated
        # instead of a figure alone.)
        #
        # Scoping stays because it is semantically right, not because it is load-bearing: a pass that
        # reads no file cannot have a SELECT-coverage defect. That property is real in the abstract
        # and pinned by a synthetic case (a Readonly later pass with a narrow SELECT), since no plan
        # in the tree exercises it. No re-dedup here: the list arrives deduped on the union of what
        # its consumers read, this check included.
        reading_configs = objects_owing_root_csv.get(obj_name) or [obj_config]
        for cfg in reading_configs:
            self._validate_external_id(obj_name, cfg.get("externalId", ""), cfg, result)

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
            for cfg in objects_owing_root_csv[obj_name]:
                self._validate_csv_file(csv_path, obj_name, cfg, result)
        else:
            self.log(f"  No root CSV owed by {obj_name} — Readonly, or every writable pass is "
                     f"supplied under objectset_source/", level="DEBUG")

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

        # Resolve operation once — both downstream externalId checks (nested-path
        # traversal, SELECT-coverage) need to skip Insert mode, where externalId
        # is used for CSV composite-key matching within the dataset rather than
        # SOQL behavior.
        # str() for the same reason as `_writable_passes_by_object`: a malformed plan can carry a
        # non-string here, and an AttributeError aborts every remaining plan rather than reporting
        # the one that is broken. Both sites read `operation`, so both need it.
        # `.strip().lower()` mirrors `ScriptLoader._resolveOperation` — see the other site for why
        # that function and not `ScriptObject.getOperation`.
        operation = str(obj_config.get("operation") or "Upsert")
        is_insert = operation.strip().lower() == "insert"

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
        fields = external_id.split(";")
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
                if ";" in external_id and not external_id.startswith("$$") and not obj_config.get("deleteOldData"):
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
                           objects_owing_root_csv: Optional[Dict[str, List[dict]]] = None) -> Tuple[int, int]:
        """Fix issues in a dataset (headers and/or composite keys).

        Args:
            dataset_path: Path to dataset directory
            object_configs: Object configurations from export.json
            objects_owing_root_csv: Per `_objects_owing_root_csv` — the declarations validation checks
                each root CSV against, so the fixer writes what validation asks for. Optional only
                because this is a public entry point; the one internal call site always supplies it,
                and omitting it restores the merged-config behavior that made `--fix-all`
                non-convergent.

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

            # The same declarations validation checks this file against, so what is reportable is
            # fixable. Reading the merged config here while validation read the reading passes made
            # `--fix-all` non-convergent for exactly the class this file just started reporting: with
            # pass 1 `Readonly`/`externalId: Name` and pass 2 `Upsert`/`Name;Code`, validation asked
            # for a `$$Name$Code` column and the fixer saw no `;` in `Name` and wrote nothing, so a
            # fix run left the finding standing. A checker that reports what its own fixer cannot
            # clear teaches people to ignore it.
            #
            # Empty-CSV headers are written from whichever reading pass comes first, since the file
            # stops being empty after that and the remaining declarations no-op. Composite-key fixes
            # are idempotent via `_csv_missing_composite_key`, so iterating cannot double-write.
            # Tracked across declarations because `--dry-run` does not mutate the file, so the
            # `_is_csv_empty` / `_csv_missing_composite_key` probes that make a real run's second
            # iteration a no-op stay true — two passes then proposed two headers for one file (only
            # the first of which a real run writes) and double-counted every composite column. A real
            # run's byte output was always correct; the dry-run *report* was not, which is worse than
            # a wrong count, because the dry run is what people read before deciding to apply it.
            header_written = False
            columns_written = set()
            for cfg in (objects_owing_root_csv or {}).get(obj_name) or [obj_config]:
                # Fix missing headers
                if self.fix_headers and not header_written and self._is_csv_empty(csv_path):
                    headers = cfg.get("fields", [])
                    if self._fix_empty_csv_header(csv_path, headers, obj_name):
                        headers_fixed += 1
                        header_written = True

                # Fix missing composite keys (only if CSV is not empty, skip deleteOldData objects)
                if self.fix_composite_keys and not self._is_csv_empty(csv_path):
                    external_id = cfg.get("externalId", "")
                    if ";" in external_id and not external_id.startswith("$$") and not cfg.get("deleteOldData"):
                        fields = [f.strip() for f in external_id.split(";")]
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
