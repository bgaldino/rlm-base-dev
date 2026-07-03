"""
Inspect an Extract ODT's internal hierarchy and validate field mapping depth.

Queries all items from an Extract ODT and displays:
  1. The internal hierarchy tree (object queries as nodes, field mappings as leaves)
  2. Output array analysis — which mappings contribute to each output path
  3. Depth validation — flags when mappings to the same output array read
     from different hierarchy depths (the #1 cause of phantom array entries)

Usage:
  python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <sf_alias>
  python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <alias> --validate-only
  python scripts/ai/docgen/docgen_inspect_hierarchy.py <odt_name_or_id> --org <alias> --json
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict


def sf_query(query, org):
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") != 0:
            print(f"ERROR: {data.get('message', '')}", file=sys.stderr)
            return None
        return data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Failed to parse query result\n{result.stderr}", file=sys.stderr)
        return None


def resolve_odt(name_or_id, org):
    if name_or_id.startswith("0jI"):
        where = f"Id = '{name_or_id}'"
    else:
        where = f"Name = '{name_or_id}'"

    records = sf_query(
        f"SELECT Id, Name, Type FROM OmniDataTransform WHERE {where}", org
    )
    if not records:
        print(f"ERROR: ODT '{name_or_id}' not found", file=sys.stderr)
        sys.exit(1)
    return records[0]


def get_items(odt_id, org):
    fields = (
        "Id, InputObjectName, InputFieldName, OutputFieldName, "
        "OutputObjectName, InputObjectQuerySequence, OutputCreationSequence, "
        "FilterOperator, FilterValue, FilterGroup"
    )
    return sf_query(
        f"SELECT {fields} FROM OmniDataTransformItem "
        f"WHERE OmniDataTransformationId = '{odt_id}' "
        f"ORDER BY InputObjectQuerySequence NULLS LAST, OutputCreationSequence, OutputFieldName",
        org,
    )


def classify_items(items):
    object_queries = []
    field_mappings = []

    for item in items:
        if item.get("InputObjectName") and item.get("InputObjectQuerySequence"):
            object_queries.append(item)
        else:
            field_mappings.append(item)

    return object_queries, field_mappings


def build_hierarchy_tree(object_queries):
    """Build a tree structure from object queries based on OutputFieldName nesting."""
    tree = {}
    for oq in object_queries:
        path = oq["OutputFieldName"]
        parts = path.split(":")
        node = tree
        for part in parts:
            if part not in node:
                node[part] = {}
            node = node[part]
        node["__item__"] = oq
    return tree


def compute_depth(input_path, object_queries):
    """Compute the hierarchy depth of an InputFieldName path.

    Depth = number of object query path segments the input path traverses.
    A field at "Parent:Child:Field" reading from a hierarchy with
    Parent (depth 1) and Parent:Child (depth 2) has depth 2.
    """
    parts = input_path.split(":")
    oq_paths = sorted(
        [oq["OutputFieldName"] for oq in object_queries],
        key=lambda p: -len(p.split(":"))
    )

    best_depth = 0
    for oq_path in oq_paths:
        oq_parts = oq_path.split(":")
        if len(oq_parts) <= len(parts):
            if parts[:len(oq_parts)] == oq_parts:
                best_depth = max(best_depth, len(oq_parts))

    return best_depth


def get_output_array_root(output_path):
    """Extract the array root from an output path.

    For "Grant:ProductName" → "Grant"
    For "Grant:Items:Name" → "Grant:Items"
    For "Line:ProductName" → "Line"
    Single-segment paths (no colon) → themselves as root.
    """
    parts = output_path.split(":")
    if len(parts) == 1:
        return parts[0]
    return ":".join(parts[:-1])


def print_tree(tree, indent=0, prefix=""):
    """Pretty-print the hierarchy tree."""
    entries = [(k, v) for k, v in tree.items() if k != "__item__"]
    for i, (key, subtree) in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        item = subtree.get("__item__")

        label = key
        if item:
            obj = item.get("InputObjectName", "?")
            seq = item.get("InputObjectQuerySequence", "?")
            filt = item.get("FilterValue", "")
            filt_op = item.get("FilterOperator", "=")
            filt_str = f"  [{filt_op} {filt}]" if filt else ""
            label = f"{key}  (Seq {seq}: {obj}{filt_str})"

        print(f"{prefix}{connector}{label}")

        next_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(subtree, indent + 1, next_prefix)


def validate_depth_uniformity(field_mappings, object_queries):
    """Check that all field mappings for the same output array read from the same depth.

    Returns list of violations: [{array_root, mappings: [{path, depth, output}]}]
    """
    by_array = defaultdict(list)

    for fm in field_mappings:
        inp = fm.get("InputFieldName", "")
        out = fm.get("OutputFieldName", "")
        if not inp or not out:
            continue

        depth = compute_depth(inp, object_queries)
        array_root = get_output_array_root(out)
        by_array[array_root].append({
            "input": inp,
            "output": out,
            "depth": depth,
        })

    violations = []
    for array_root, mappings in by_array.items():
        depths = set(m["depth"] for m in mappings)
        if len(depths) > 1:
            violations.append({
                "array_root": array_root,
                "depths_found": sorted(depths),
                "mappings": mappings,
            })

    return violations


def print_output_analysis(field_mappings, object_queries):
    """Print field mappings grouped by output array, showing depth."""
    by_array = defaultdict(list)

    for fm in field_mappings:
        inp = fm.get("InputFieldName", "")
        out = fm.get("OutputFieldName", "")
        if not inp or not out:
            continue

        depth = compute_depth(inp, object_queries)
        array_root = get_output_array_root(out)
        field_name = out.split(":")[-1]
        by_array[array_root].append({
            "input": inp,
            "output_field": field_name,
            "depth": depth,
        })

    for array_root in sorted(by_array.keys()):
        mappings = by_array[array_root]
        depths = set(m["depth"] for m in mappings)
        status = "MIXED DEPTHS" if len(depths) > 1 else f"depth {list(depths)[0]}"
        marker = " ✗" if len(depths) > 1 else " ✓"

        print(f"\n  {array_root} ({status}){marker}")
        for m in mappings:
            depth_flag = " ←←" if len(depths) > 1 and m["depth"] != max(depths) else ""
            print(f"    {m['output_field']} ← {m['input']}  [depth {m['depth']}]{depth_flag}")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect Extract ODT hierarchy and validate depth uniformity"
    )
    parser.add_argument("odt", help="ODT Name or Id (0jI prefix)")
    parser.add_argument("--org", required=True, help="SF CLI target org alias")
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only run depth validation (skip tree display)"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output as JSON (hierarchy + violations)"
    )
    args = parser.parse_args()

    odt = resolve_odt(args.odt, args.org)
    items = get_items(odt["Id"], args.org)
    if items is None:
        sys.exit(1)

    object_queries, field_mappings = classify_items(items)

    if args.json_output:
        violations = validate_depth_uniformity(field_mappings, object_queries)
        output = {
            "odt": {"id": odt["Id"], "name": odt["Name"], "type": odt["Type"]},
            "object_queries": [
                {
                    "seq": oq["InputObjectQuerySequence"],
                    "object": oq["InputObjectName"],
                    "path": oq["OutputFieldName"],
                    "filter": oq.get("FilterValue"),
                    "filter_op": oq.get("FilterOperator"),
                }
                for oq in object_queries
            ],
            "field_mappings": [
                {
                    "input": fm.get("InputFieldName"),
                    "output": fm.get("OutputFieldName"),
                    "depth": compute_depth(fm.get("InputFieldName", ""), object_queries),
                }
                for fm in field_mappings
                if fm.get("InputFieldName") and fm.get("OutputFieldName")
            ],
            "violations": violations,
        }
        print(json.dumps(output, indent=2))
        sys.exit(1 if violations else 0)

    print(f"ODT: {odt['Name']} ({odt['Id']})  Type: {odt['Type']}")
    print(f"Items: {len(object_queries)} queries + {len(field_mappings)} field mappings")

    if not args.validate_only:
        print(f"\n{'='*60}")
        print("INTERNAL HIERARCHY (object queries)")
        print(f"{'='*60}\n")

        tree = build_hierarchy_tree(object_queries)
        print_tree(tree)

        print(f"\n{'='*60}")
        print("OUTPUT ARRAYS (field mappings by target path)")
        print(f"{'='*60}")
        print_output_analysis(field_mappings, object_queries)

    violations = validate_depth_uniformity(field_mappings, object_queries)

    print(f"\n{'='*60}")
    print("DEPTH VALIDATION")
    print(f"{'='*60}\n")

    if not violations:
        print("  ✓ All output arrays have uniform field mapping depth")
    else:
        print(f"  ⚠ {len(violations)} output array(s) have MIXED DEPTHS:\n")
        for v in violations:
            print(f"  Array: {v['array_root']}")
            print(f"  Depths found: {v['depths_found']}")
            print(f"  Mappings:")
            for m in v["mappings"]:
                flag = " ← SHALLOWER" if m["depth"] < max(v["depths_found"]) else ""
                print(f"    depth {m['depth']}: {m['input']} → {m['output']}{flag}")
            print()
        print("  Review: mixed depths cause phantom entries when shallower fields")
        print("  read from a PARENT that has MORE records than the child. Safe when")
        print("  all paths share the same pivot object (e.g., Child:Field vs")
        print("  Child:Grandchild:Field both anchored by Child).")
        print("  Fix (if phantom entries appear): use a redundant join to read")
        print("  parent fields at child level. See: extract-engine-reference.md")

    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
