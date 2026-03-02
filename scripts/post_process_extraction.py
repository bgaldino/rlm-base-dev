#!/usr/bin/env python3
"""
Post-process SFDMU extraction output into import-ready CSVs.

This script bridges the gap between raw SFDMU extraction output (org > CSV)
and the import-ready format expected by the data plans (CSV > org).

Key transformations:
  - Status rewrite:  Active/Inactive > Draft for configurable objects
  - Column alignment: Reorder and filter columns to match the existing plan CSVs
  - objectset_source: Generate Pass 2+ CSVs in the objectset_source/ directory
  - Composite keys:   Build composite key columns from component fields (individual columns preferred over $$ notation)
  - Diff mode:        Compare extraction against current plan and report deltas

Usage:
  python3 scripts/post_process_extraction.py <extraction_dir> <plan_dir> [options]

  --output-dir DIR   Write processed CSVs here (default: <extraction_dir>/processed/)
  --diff-only        Only produce a diff report; don't write processed CSVs
  --copy-to-plan     Copy processed CSVs into the plan directory (updates in place)
  --verbose          Print detailed processing info
"""
import argparse
import csv
import json
import os
import shutil
import sys
from collections import OrderedDict
from pathlib import Path


# Objects whose Status field should be rewritten from Active/Inactive to Draft.
# Only objects that go through a Draft-then-Activate workflow are listed here.
# Objects loaded directly as Active (e.g., UnitOfMeasure, UsageGrantRenewalPolicy,
# UsageGrantRolloverPolicy, UsageResourceBillingPolicy) are NOT rewritten because
# they don't have an Apex-driven activation step -- they're imported as Active.
STATUS_REWRITE_MAP = {
    "UnitOfMeasureClass": ["Status"],
    "UsageResource": ["Status"],
    "ProductUsageResource": ["Status"],
    "ProductUsageGrant": ["Status"],
    "RateCard": ["Status"],
    "RateCardEntry": ["Status"],
    "BillingPolicy": ["Status"],
    "BillingTreatment": ["Status"],
    "BillingTreatmentItem": ["Status"],
    "TaxTreatment": ["Status"],
    "TaxPolicy": ["Status"],
}

# Values that should be rewritten to Draft
ACTIVE_STATUSES = {"Active", "Inactive"}


def normalize_header(h: str) -> str:
    """Normalize a CSV header for matching: strip BOM, whitespace, and surrounding quotes.

    SFDMU extraction can write headers with BOM (\\ufeff) and/or quoted names (e.g. "Code"),
    which would otherwise prevent matching plan columns like Code.
    """
    if not h:
        return h
    s = h.strip().lstrip("\ufeff").strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    return s


def load_export_json(plan_dir: str) -> dict:
    """Load and return the export.json from the plan directory."""
    path = os.path.join(plan_dir, "export.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_object_name_from_query(query: str) -> str:
    """Extract the object API name from a SOQL query string."""
    upper = query.upper()
    idx = upper.find(" FROM ")
    if idx == -1:
        return ""
    rest = query[idx + 6:].strip()
    return rest.split()[0].strip()


def parse_plan_structure(export_json: dict) -> tuple:
    """Parse export.json into a structure mapping object names to their config.

    Returns a tuple (plan_structure, passes) where:
      plan_structure: object_name -> {
        "pass_index": int (0-based),
        "operation": str,
        "externalId": str,
        "query": str,
        "fields": list[str],  # fields from the SELECT clause
      }
      passes: object_name -> list of (pass_index, entry) for all passes
        (used for objectset_source generation; plan_structure keeps only first pass).
    For objects appearing in multiple passes, only the first pass entry
    is stored in plan_structure; later passes are in passes.

    Supports both objectSets (multi-pass plans like qb-rating) and flat
    "objects" (single-pass plans like qb-pcm).
    """
    result = {}
    passes = {}
    object_sets = export_json.get("objectSets", [])
    if not object_sets and "objects" in export_json:
        # Single-pass plan (e.g. qb-pcm): treat as one virtual object set
        object_sets = [{"objects": export_json["objects"]}]
    for idx, obj_set in enumerate(object_sets):
        for obj in obj_set.get("objects", []):
            if obj.get("excluded"):
                continue
            query = obj.get("query", "")
            name = get_object_name_from_query(query)
            if not name:
                continue
            fields = parse_select_fields(query)
            entry = {
                "pass_index": idx,
                "operation": obj.get("operation", "Upsert"),
                "externalId": obj.get("externalId", "Id"),
                "query": query,
                "fields": fields,
            }
            if name not in result:
                result[name] = entry
            # Track all passes for objectset_source generation
            passes.setdefault(name, []).append((idx, entry))
    return result, passes


def parse_select_fields(query: str) -> list:
    """Extract field names from a SOQL SELECT clause."""
    upper = query.upper()
    select_idx = upper.find("SELECT ")
    from_idx = upper.find(" FROM ")
    if select_idx == -1 or from_idx == -1:
        return []
    fields_str = query[select_idx + 7:from_idx].strip()
    return [f.strip() for f in fields_str.split(",") if f.strip()]


def load_plan_csv(plan_dir: str, object_name: str) -> tuple:
    """Load an existing plan CSV and return (headers, rows). Headers are normalized for matching."""
    path = os.path.join(plan_dir, f"{object_name}.csv")
    if not os.path.isfile(path):
        return None, None
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if headers:
            headers = [normalize_header(h) for h in headers]
        rows = list(reader)
    return headers, rows


def load_extracted_csv(extraction_dir: str, object_name: str) -> tuple:
    """Load an extracted CSV and return (headers, rows). Headers are normalized for matching."""
    path = os.path.join(extraction_dir, f"{object_name}.csv")
    if not os.path.isfile(path):
        return None, None
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if headers:
            headers = [normalize_header(h) for h in headers]
        rows = list(reader)
    return headers, rows


def rewrite_status(rows: list, headers: list, object_name: str) -> list:
    """Rewrite Status fields from Active/Inactive to Draft."""
    fields = STATUS_REWRITE_MAP.get(object_name, [])
    if not fields:
        return rows
    indices = []
    for field in fields:
        if field in headers:
            indices.append(headers.index(field))
    if not indices:
        return rows
    new_rows = []
    for row in rows:
        row = list(row)
        for idx in indices:
            if idx < len(row) and row[idx] in ACTIVE_STATUSES:
                row[idx] = "Draft"
        new_rows.append(row)
    return new_rows


def build_composite_key_column(row_dict: dict, components: list) -> str:
    """Build a composite key value from component field values (legacy $$ support).

    components is a list of field names like ["Product.StockKeepingUnit", "UsageResource.Code"].
    The composite value is the concatenation with ; separators (matching SFDMU import notation).

    NOTE: Plan CSVs now use individual columns instead of $$ composite columns.
    This function is retained for backward compatibility with older plan formats.
    """
    values = [str(row_dict.get(c, "")) for c in components]
    return ";".join(values)


def parse_composite_key_header(header: str) -> list:
    """Parse a $$Field1$Field2 header into its component field names (legacy $$ support).

    Example: "$$Product.StockKeepingUnit$UsageResource.Code"
      returns ["Product.StockKeepingUnit", "UsageResource.Code"]

    NOTE: Plan CSVs now use individual columns instead of $$ composite columns.
    This function is retained for backward compatibility with older plan formats.
    """
    if not header.startswith("$$"):
        return []
    inner = header[2:]
    return inner.split("$")


def align_columns(extracted_headers: list, extracted_rows: list,
                   plan_headers: list, object_name: str, verbose: bool = False) -> tuple:
    """Align extracted CSV columns to match the plan CSV column order.

    For columns present in the plan but missing from extraction, fill with empty string.
    For legacy $$ composite key columns, build them from component fields.
    Plan CSVs now prefer individual columns over $$ notation for SOQL compatibility.
    Returns (aligned_headers, aligned_rows).
    """
    if plan_headers is None:
        return extracted_headers, extracted_rows

    # Build index map for extracted data
    ext_idx = {h: i for i, h in enumerate(extracted_headers)}

    aligned_headers = list(plan_headers)
    aligned_rows = []

    for row in extracted_rows:
        row_dict = {h: (row[i] if i < len(row) else "") for h, i in ext_idx.items()}
        aligned_row = []
        for h in plan_headers:
            if h in ext_idx:
                # Column exists in extraction -- use the original value directly.
                # This preserves SFDMU's composite key formatting (e.g., omitting
                # trailing empty parts in Parent.$$Field1$Field2 values).
                idx = ext_idx[h]
                aligned_row.append(row[idx] if idx < len(row) else "")
            elif h.startswith("$$"):
                # Composite key column not in extraction -- build from components
                components = parse_composite_key_header(h)
                aligned_row.append(build_composite_key_column(row_dict, components))
            elif "." in h and "$$" in h:
                # Nested composite reference not in extraction -- build from
                # parent relationship + component fields
                dot_idx = h.index(".")
                parent = h[:dot_idx]
                composite = h[dot_idx + 1:]
                components = parse_composite_key_header(composite)
                full_components = [f"{parent}.{c}" for c in components]
                aligned_row.append(build_composite_key_column(row_dict, full_components))
            else:
                if verbose:
                    print(f"    WARNING: Plan column '{h}' not found in extraction for {object_name}")
                aligned_row.append("")
        aligned_rows.append(aligned_row)

    return aligned_headers, aligned_rows


def write_csv(path: str, headers: list, rows: list) -> None:
    """Write a CSV file with the given headers and rows."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def diff_csvs(plan_headers: list, plan_rows: list,
              proc_headers: list, proc_rows: list,
              object_name: str, key_columns: list) -> dict:
    """Compare plan CSV against processed extraction and return a diff report.

    Returns dict with:
      - "new_records": records in extraction but not in plan
      - "missing_records": records in plan but not in extraction
      - "changed_records": records with same key but different values
      - "identical": count of unchanged records
    """
    report = {
        "new_records": [],
        "missing_records": [],
        "changed_records": [],
        "identical": 0,
    }

    if plan_headers is None or proc_headers is None:
        if proc_headers and proc_rows:
            report["new_records"] = proc_rows
        return report

    # Build key indices based on matching plan_headers
    plan_key_idx = [plan_headers.index(k) for k in key_columns if k in plan_headers]
    proc_key_idx = [proc_headers.index(k) for k in key_columns if k in proc_headers]

    if not plan_key_idx or not proc_key_idx:
        return report

    def make_key(row, indices):
        return tuple(row[i] if i < len(row) else "" for i in indices)

    plan_map = {}
    for row in plan_rows:
        key = make_key(row, plan_key_idx)
        plan_map[key] = row

    proc_map = {}
    for row in proc_rows:
        key = make_key(row, proc_key_idx)
        proc_map[key] = row

    for key, proc_row in proc_map.items():
        if key not in plan_map:
            report["new_records"].append(proc_row)
        elif proc_row != plan_map[key]:
            report["changed_records"].append((plan_map[key], proc_row))
        else:
            report["identical"] += 1

    for key in plan_map:
        if key not in proc_map:
            report["missing_records"].append(plan_map[key])

    return report


def get_key_columns(plan_headers: list, external_id: str) -> list:
    """Determine which columns to use as the diff key.

    Parses the externalId (semicolon-separated components) and maps each
    component to a CSV column.  Components may be:
      - Simple fields: "StockKeepingUnit" or "Product.StockKeepingUnit"
      - Relationship traversals: "RateCardEntry.RateCard.Name"
      - Legacy composite key references: "RateCardEntry.$$..." (deprecated)

    Plan CSVs now use individual relationship traversal fields instead of
    $$ composite key notation, for SOQL compatibility during Upsert operations.

    Falls back to all columns if no externalId fields found.
    """
    if not external_id or external_id == "Id":
        return list(plan_headers) if plan_headers else []

    # Split externalId on ";" but be aware that composite key references
    # (containing $$) are single components even though they contain $
    parts = external_id.split(";")
    key_cols = []
    for p in parts:
        if plan_headers and p in plan_headers:
            key_cols.append(p)

    if not key_cols and plan_headers:
        # Try the full composite $$-prefixed column as a single key
        composite = "$$" + "$".join(parts)
        if composite in plan_headers:
            key_cols.append(composite)

    return key_cols if key_cols else (list(plan_headers) if plan_headers else [])


def process_extraction(extraction_dir: str, plan_dir: str, output_dir: str,
                        diff_only: bool, copy_to_plan: bool, verbose: bool) -> None:
    """Main post-processing logic."""
    export_json = load_export_json(plan_dir)
    plan_structure, all_passes = parse_plan_structure(export_json)

    # Find extracted CSV files
    extracted_files = [f for f in os.listdir(extraction_dir) if f.endswith(".csv")]
    extracted_objects = {os.path.splitext(f)[0]: f for f in extracted_files}

    if not extracted_objects:
        print("No CSV files found in extraction directory.")
        return

    print(f"Found {len(extracted_objects)} extracted CSV files")
    print(f"Plan has {len(plan_structure)} objects configured")
    print()

    os.makedirs(output_dir, exist_ok=True)
    diff_report = {}

    for obj_name in sorted(extracted_objects.keys()):
        # Skip SFDMU internal files
        if obj_name.startswith("_") or obj_name in ("MissingParentRecordsReport", "CSVIssuesReport"):
            continue

        config = plan_structure.get(obj_name)
        if not config:
            if verbose:
                print(f"  SKIP {obj_name} (not in export.json)")
            continue

        print(f"  Processing {obj_name}...")

        # Load extracted data
        ext_headers, ext_rows = load_extracted_csv(extraction_dir, obj_name)
        if ext_headers is None:
            continue

        # Load existing plan CSV for column alignment and diff
        plan_headers, plan_rows = load_plan_csv(plan_dir, obj_name)

        # Rewrite status fields
        ext_rows = rewrite_status(ext_rows, ext_headers, obj_name)

        # Align columns to match plan CSV format
        proc_headers, proc_rows = align_columns(
            ext_headers, ext_rows, plan_headers, obj_name, verbose
        )

        # Diff against existing plan
        if plan_headers is not None:
            key_cols = get_key_columns(plan_headers, config.get("externalId", ""))
            report = diff_csvs(plan_headers, plan_rows, proc_headers, proc_rows, obj_name, key_cols)
            diff_report[obj_name] = report

            if verbose or report["new_records"] or report["missing_records"] or report["changed_records"]:
                print(f"    Identical: {report['identical']}, "
                      f"New: {len(report['new_records'])}, "
                      f"Changed: {len(report['changed_records'])}, "
                      f"Missing: {len(report['missing_records'])}")

        if not diff_only:
            # Write processed CSV
            out_path = os.path.join(output_dir, f"{obj_name}.csv")
            write_csv(out_path, proc_headers, proc_rows)

            if copy_to_plan:
                plan_path = os.path.join(plan_dir, f"{obj_name}.csv")
                shutil.copy2(out_path, plan_path)
                if verbose:
                    print(f"    Copied to plan: {plan_path}")

    # Handle objectset_source for multi-pass plans
    if not diff_only:
        generate_objectset_source(extraction_dir, plan_dir, output_dir, all_passes, verbose)

    # Print diff summary
    print_diff_summary(diff_report)


def generate_objectset_source(extraction_dir: str, plan_dir: str, output_dir: str,
                                all_passes: dict, verbose: bool) -> None:
    """Generate objectset_source CSVs for Pass 2+ objects.

    For objects that appear in multiple passes, create stripped-down CSVs
    matching the objectset_source format (usually just external ID + Status).
    """
    existing_source_dir = os.path.join(plan_dir, "objectset_source")
    if not os.path.isdir(existing_source_dir):
        return

    print("\n  Generating objectset_source CSVs...")
    for obj_name, passes in all_passes.items():
        if len(passes) < 2:
            continue

        for pass_idx, config in passes[1:]:
            set_name = f"object-set-{pass_idx + 1}"
            existing_csv_path = os.path.join(existing_source_dir, set_name, f"{obj_name}.csv")
            if not os.path.isfile(existing_csv_path):
                continue

            # Read the existing objectset_source CSV to get its column structure
            with open(existing_csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                source_headers = next(reader, None)

            if not source_headers:
                continue

            # Load extracted data for this object
            ext_headers, ext_rows = load_extracted_csv(extraction_dir, obj_name)
            if ext_headers is None:
                continue

            # Build rows with only the columns needed for this pass
            ext_idx = {h: i for i, h in enumerate(ext_headers)}
            source_rows = []
            for row in ext_rows:
                source_row = []
                for h in source_headers:
                    if h in ext_idx:
                        idx = ext_idx[h]
                        source_row.append(row[idx] if idx < len(row) else "")
                    else:
                        source_row.append("")
                source_rows.append(source_row)

            # Write to output objectset_source
            out_dir = os.path.join(output_dir, "objectset_source", set_name)
            write_csv(os.path.join(out_dir, f"{obj_name}.csv"), source_headers, source_rows)
            if verbose:
                print(f"    {set_name}/{obj_name}.csv ({len(source_rows)} rows)")


def print_diff_summary(diff_report: dict) -> None:
    """Print a summary of all diffs."""
    if not diff_report:
        return

    print("\n" + "=" * 80)
    print("DIFF SUMMARY: Extraction vs Current Plan")
    print("=" * 80)
    print(f"{'Object':<45} {'Same':>6} {'New':>6} {'Chg':>6} {'Miss':>6}")
    print("-" * 80)

    total_identical = 0
    total_new = 0
    total_changed = 0
    total_missing = 0

    for obj_name in sorted(diff_report.keys()):
        r = diff_report[obj_name]
        n_id = r["identical"]
        n_new = len(r["new_records"])
        n_chg = len(r["changed_records"])
        n_miss = len(r["missing_records"])
        total_identical += n_id
        total_new += n_new
        total_changed += n_chg
        total_missing += n_miss

        flag = "" if (n_new == 0 and n_chg == 0 and n_miss == 0) else " *"
        print(f"{obj_name:<45} {n_id:>6} {n_new:>6} {n_chg:>6} {n_miss:>6}{flag}")

    print("-" * 80)
    print(f"{'TOTAL':<45} {total_identical:>6} {total_new:>6} {total_changed:>6} {total_missing:>6}")
    print()
    if total_new or total_changed or total_missing:
        print("Objects marked with * have differences.")
    else:
        print("Extraction matches current plan exactly.")


def main():
    parser = argparse.ArgumentParser(
        description="Post-process SFDMU extraction output into import-ready CSVs"
    )
    parser.add_argument("extraction_dir", help="Path to the directory containing extracted CSVs")
    parser.add_argument("plan_dir", help="Path to the data plan directory (contains export.json and plan CSVs)")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for processed CSVs (default: <extraction_dir>/processed/)")
    parser.add_argument("--diff-only", action="store_true",
                        help="Only produce a diff report; don't write processed CSVs")
    parser.add_argument("--copy-to-plan", action="store_true",
                        help="Copy processed CSVs into the plan directory")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed processing info")

    args = parser.parse_args()

    extraction_dir = os.path.abspath(args.extraction_dir)
    plan_dir = os.path.abspath(args.plan_dir)
    output_dir = args.output_dir or os.path.join(extraction_dir, "processed")

    if not os.path.isdir(extraction_dir):
        print(f"ERROR: Extraction directory not found: {extraction_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(plan_dir):
        print(f"ERROR: Plan directory not found: {plan_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(os.path.join(plan_dir, "export.json")):
        print(f"ERROR: export.json not found in plan directory: {plan_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Extraction dir: {extraction_dir}")
    print(f"Plan dir:       {plan_dir}")
    print(f"Output dir:     {output_dir}")
    print(f"Diff only:      {args.diff_only}")
    print(f"Copy to plan:   {args.copy_to_plan}")
    print()

    process_extraction(
        extraction_dir=extraction_dir,
        plan_dir=plan_dir,
        output_dir=output_dir,
        diff_only=args.diff_only,
        copy_to_plan=args.copy_to_plan,
        verbose=args.verbose,
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
