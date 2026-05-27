#!/usr/bin/env python3
"""
Diff two schema extractions to identify changes between Salesforce releases.

Compares two JSON snapshots produced by extract_schema.py and reports:
- Objects added / removed
- Fields added / removed / type-changed per object
- Picklist values added / removed
- Relationship changes

Usage:
    python scripts/schema_diff/diff_schemas.py \
        --baseline scripts/schema_diff/260-schema.json \
        --target scripts/schema_diff/262-schema.json \
        --report scripts/schema_diff/260-vs-262-diff.md

Options:
    --baseline PATH   The older (baseline) schema JSON
    --target PATH     The newer (target) schema JSON
    --report PATH     Output markdown report (default: stdout)
    --json PATH       Output structured JSON diff
    --impact          Cross-reference against data plans and show impact
    --verbose         Show unchanged objects too
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_schema(path: str) -> dict:
    """Load a schema JSON file."""
    with open(path) as f:
        return json.load(f)


def diff_fields(baseline_fields: dict, target_fields: dict) -> dict:
    """Compare fields between baseline and target."""
    baseline_names = set(baseline_fields.keys())
    target_names = set(target_fields.keys())

    added = sorted(target_names - baseline_names)
    removed = sorted(baseline_names - target_names)

    # Check for type changes and picklist changes on common fields
    type_changed = []
    picklist_changed = []
    for name in sorted(baseline_names & target_names):
        b = baseline_fields[name]
        t = target_fields[name]
        if b["type"] != t["type"]:
            type_changed.append({
                "field": name,
                "from_type": b["type"],
                "to_type": t["type"],
            })
        # Picklist value changes
        if b.get("picklistValues") or t.get("picklistValues"):
            b_vals = set(b.get("picklistValues", []))
            t_vals = set(t.get("picklistValues", []))
            if b_vals != t_vals:
                picklist_changed.append({
                    "field": name,
                    "added": sorted(t_vals - b_vals),
                    "removed": sorted(b_vals - t_vals),
                })

    return {
        "added": added,
        "removed": removed,
        "type_changed": type_changed,
        "picklist_changed": picklist_changed,
    }


def diff_schemas(baseline: dict, target: dict) -> dict:
    """Produce a full diff between two schema snapshots."""
    b_objects = set(baseline["objects"].keys())
    t_objects = set(target["objects"].keys())

    objects_added = sorted(t_objects - b_objects)
    objects_removed = sorted(b_objects - t_objects)

    object_diffs = {}
    for obj_name in sorted(b_objects & t_objects):
        b_fields = baseline["objects"][obj_name]["fields"]
        t_fields = target["objects"][obj_name]["fields"]
        field_diff = diff_fields(b_fields, t_fields)

        # Only include if there are actual changes
        if (field_diff["added"] or field_diff["removed"] or
                field_diff["type_changed"] or field_diff["picklist_changed"]):
            object_diffs[obj_name] = field_diff

    return {
        "baseline": baseline.get("metadata", {}),
        "target": target.get("metadata", {}),
        "summary": {
            "objects_added": len(objects_added),
            "objects_removed": len(objects_removed),
            "objects_changed": len(object_diffs),
            "objects_unchanged": len(b_objects & t_objects) - len(object_diffs),
            "total_fields_added": sum(
                len(d["added"]) for d in object_diffs.values()
            ),
            "total_fields_removed": sum(
                len(d["removed"]) for d in object_diffs.values()
            ),
            "total_type_changes": sum(
                len(d["type_changed"]) for d in object_diffs.values()
            ),
        },
        "objects_added": objects_added,
        "objects_removed": objects_removed,
        "object_diffs": object_diffs,
    }


def find_impacted_plans(diff: dict) -> dict:
    """Cross-reference schema changes against SFDMU data plans."""
    sfdmu_dir = REPO_ROOT / "datasets" / "sfdmu"
    impacts = {}

    # Build a map of object -> plans that use it
    object_to_plans = {}
    for plan_dir in sfdmu_dir.iterdir():
        if not plan_dir.is_dir():
            continue
        export_json = plan_dir / "export.json"
        if not export_json.exists():
            continue
        try:
            with open(export_json) as f:
                plan = json.load(f)
            for obj_def in plan.get("objects", []):
                obj_name = obj_def.get("objectName", obj_def.get("query", "").split(" ")[-1])
                # Extract object name from query if needed
                if "FROM" in obj_name:
                    parts = obj_name.split("FROM")
                    if len(parts) > 1:
                        obj_name = parts[1].strip().split()[0]
                elif " " in obj_name:
                    # Try to get from query field
                    query = obj_def.get("query", "")
                    if "FROM " in query:
                        obj_name = query.split("FROM ")[1].split()[0].strip()

                if obj_name:
                    if obj_name not in object_to_plans:
                        object_to_plans[obj_name] = []
                    object_to_plans[obj_name].append(plan_dir.name)
        except (json.JSONDecodeError, KeyError):
            continue

    # Map changes to impacted plans
    all_changed = set(diff["objects_removed"]) | set(diff["object_diffs"].keys())
    for obj_name in sorted(all_changed):
        plans = object_to_plans.get(obj_name, [])
        if plans:
            change_type = "removed" if obj_name in diff["objects_removed"] else "modified"
            impacts[obj_name] = {
                "change": change_type,
                "plans": sorted(set(plans)),
            }
            if change_type == "modified" and obj_name in diff["object_diffs"]:
                d = diff["object_diffs"][obj_name]
                impacts[obj_name]["fields_removed"] = d["removed"]
                impacts[obj_name]["fields_added"] = d["added"]
                impacts[obj_name]["type_changed"] = d["type_changed"]

    return impacts


def generate_markdown_report(diff: dict, impacts: Optional[dict] = None) -> str:
    """Generate a markdown report from the diff."""
    lines = []
    b_meta = diff["baseline"]
    t_meta = diff["target"]
    summary = diff["summary"]

    lines.append("# Schema Diff Report")
    lines.append("")
    lines.append(f"**Baseline:** {b_meta.get('org_alias', 'unknown')} "
                 f"(extracted {b_meta.get('extracted_at', 'unknown')})")
    lines.append(f"**Target:** {t_meta.get('org_alias', 'unknown')} "
                 f"(extracted {t_meta.get('extracted_at', 'unknown')})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Objects added | {summary['objects_added']} |")
    lines.append(f"| Objects removed | {summary['objects_removed']} |")
    lines.append(f"| Objects with field changes | {summary['objects_changed']} |")
    lines.append(f"| Objects unchanged | {summary['objects_unchanged']} |")
    lines.append(f"| Total fields added | {summary['total_fields_added']} |")
    lines.append(f"| Total fields removed | {summary['total_fields_removed']} |")
    lines.append(f"| Total type changes | {summary['total_type_changes']} |")
    lines.append("")

    # Objects added
    if diff["objects_added"]:
        lines.append("## Objects Added (new in target)")
        lines.append("")
        for obj in diff["objects_added"]:
            lines.append(f"- `{obj}`")
        lines.append("")

    # Objects removed
    if diff["objects_removed"]:
        lines.append("## Objects Removed (missing from target)")
        lines.append("")
        for obj in diff["objects_removed"]:
            lines.append(f"- `{obj}` **ACTION REQUIRED**")
        lines.append("")

    # Per-object field changes
    if diff["object_diffs"]:
        lines.append("## Field Changes by Object")
        lines.append("")
        for obj_name, field_diff in sorted(diff["object_diffs"].items()):
            lines.append(f"### `{obj_name}`")
            lines.append("")
            if field_diff["added"]:
                lines.append("**Fields added:**")
                for f in field_diff["added"]:
                    lines.append(f"- `{f}`")
                lines.append("")
            if field_diff["removed"]:
                lines.append("**Fields removed:** (check data plans and Apex)")
                for f in field_diff["removed"]:
                    lines.append(f"- `{f}` **ACTION REQUIRED**")
                lines.append("")
            if field_diff["type_changed"]:
                lines.append("**Type changes:**")
                for tc in field_diff["type_changed"]:
                    lines.append(f"- `{tc['field']}`: {tc['from_type']} -> {tc['to_type']} **REVIEW**")
                lines.append("")
            if field_diff["picklist_changed"]:
                lines.append("**Picklist changes:**")
                for pc in field_diff["picklist_changed"]:
                    if pc["added"]:
                        lines.append(f"- `{pc['field']}` added: {', '.join(pc['added'])}")
                    if pc["removed"]:
                        lines.append(f"- `{pc['field']}` removed: {', '.join(pc['removed'])} **REVIEW**")
                lines.append("")

    # Impact analysis
    if impacts:
        lines.append("## Data Plan Impact Analysis")
        lines.append("")
        lines.append("Objects with schema changes that are used in SFDMU data plans:")
        lines.append("")
        lines.append("| Object | Change | Impacted Plans | Action |")
        lines.append("|--------|--------|----------------|--------|")
        for obj_name, impact in sorted(impacts.items()):
            plans_str = ", ".join(f"`{p}`" for p in impact["plans"])
            change = impact["change"]
            if change == "removed":
                action = "Remove from plans"
            elif impact.get("fields_removed"):
                action = f"Update CSV headers: remove {', '.join(impact['fields_removed'])}"
            elif impact.get("type_changed"):
                action = "Verify CSV data types"
            else:
                action = "Verify compatibility"
            lines.append(f"| `{obj_name}` | {change} | {plans_str} | {action} |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Diff two schema snapshots")
    parser.add_argument("--baseline", required=True, help="Baseline schema JSON")
    parser.add_argument("--target", required=True, help="Target schema JSON")
    parser.add_argument("--report", help="Output markdown report path")
    parser.add_argument("--json", help="Output JSON diff path", dest="json_output")
    parser.add_argument("--impact", action="store_true",
                        help="Cross-reference against data plans")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # Load schemas
    print(f"Loading baseline: {args.baseline}")
    baseline = load_schema(args.baseline)
    print(f"  Objects: {baseline['metadata']['object_count']}, "
          f"Fields: {baseline['metadata']['total_fields']}")

    print(f"Loading target: {args.target}")
    target = load_schema(args.target)
    print(f"  Objects: {target['metadata']['object_count']}, "
          f"Fields: {target['metadata']['total_fields']}")

    # Diff
    print("\nComputing diff...")
    diff = diff_schemas(baseline, target)
    summary = diff["summary"]
    print(f"  Objects added: {summary['objects_added']}")
    print(f"  Objects removed: {summary['objects_removed']}")
    print(f"  Objects changed: {summary['objects_changed']}")
    print(f"  Fields added: {summary['total_fields_added']}")
    print(f"  Fields removed: {summary['total_fields_removed']}")
    print(f"  Type changes: {summary['total_type_changes']}")

    # Impact analysis
    impacts = None
    if args.impact:
        print("\nAnalyzing data plan impact...")
        impacts = find_impacted_plans(diff)
        print(f"  Impacted objects: {len(impacts)}")

    # Generate report
    report = generate_markdown_report(diff, impacts)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w") as f:
            f.write(report)
        print(f"\nReport written to {args.report}")
    else:
        print("\n" + report)

    # JSON output
    if args.json_output:
        output = diff
        if impacts:
            output["impacts"] = impacts
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"JSON diff written to {args.json_output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
