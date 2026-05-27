#!/usr/bin/env python3
"""
Extract Revenue Cloud schema from a Salesforce org for cross-release comparison.

Queries EntityDefinition and FieldDefinition via the Tooling API to capture
every RLM-related object and field. Outputs a normalized JSON snapshot that
can be diffed between releases (e.g., 260 vs 262).

Usage:
    python scripts/schema_diff/extract_schema.py --org rlm-base__262buildtest --output scripts/schema_diff/262-schema.json
    python scripts/schema_diff/extract_schema.py --org techido-260 --output scripts/schema_diff/260-schema.json

Options:
    --org ALIAS       sf CLI target org alias (required)
    --output PATH     Output JSON file path (required)
    --objects FILE    Optional file with object names (one per line); defaults to erd-data.json objects
    --all-objects     Query ALL EntityDefinitions, not just ERD-tracked ones
    --include-custom  Include custom fields (any __c suffix). Default behavior
                      strips ALL custom fields so the schema diff reflects
                      only the canonical Revenue Cloud platform schema.
    --verbose         Show progress per object
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ERD_DATA = REPO_ROOT / "docs" / "erds" / "erd-data.json"

# System fields to exclude from comparison (noise)
SYSTEM_FIELDS = {
    "Id", "IsDeleted", "CreatedDate", "CreatedById", "LastModifiedDate",
    "LastModifiedById", "SystemModstamp", "LastActivityDate", "LastViewedDate",
    "LastReferencedDate",
}


def get_erd_objects() -> list:
    """Load object names from erd-data.json."""
    with open(ERD_DATA) as f:
        data = json.load(f)
    return sorted(data["objects"].keys())


def query_tooling(org_alias: str, soql: str) -> list:
    """Run a Tooling API SOQL query via sf CLI."""
    result = subprocess.run(
        ["sf", "data", "query",
         "--query", soql,
         "--target-org", org_alias,
         "--use-tooling-api",
         "--json"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        error = result.stderr or result.stdout
        raise RuntimeError(f"Tooling query failed: {error[:500]}")
    data = json.loads(result.stdout)
    records = data.get("result", {}).get("records", [])
    return records


def describe_sobject(org_alias: str, object_name: str) -> Optional[dict]:
    """Describe a single SObject via sf CLI."""
    try:
        result = subprocess.run(
            ["sf", "sobject", "describe",
             "--sobject", object_name,
             "--target-org", org_alias,
             "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("result", data)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def extract_field_info(field_data: dict) -> dict:
    """Normalize a field describe result into a comparable dict."""
    return {
        "name": field_data["name"],
        "type": field_data.get("type", ""),
        "label": field_data.get("label", ""),
        "length": field_data.get("length", 0),
        "precision": field_data.get("precision", 0),
        "scale": field_data.get("scale", 0),
        "nillable": field_data.get("nillable", False),
        "updateable": field_data.get("updateable", False),
        "createable": field_data.get("createable", False),
        "referenceTo": field_data.get("referenceTo", []),
        "relationshipName": field_data.get("relationshipName"),
        "picklistValues": [
            v["value"] for v in field_data.get("picklistValues", [])
            if v.get("active", True)
        ] if field_data.get("type") in ("picklist", "multipicklist") else [],
        "custom": field_data["name"].endswith("__c"),
    }


def extract_object_schema(org_alias: str, object_name: str,
                          verbose: bool = False,
                          skip_custom: bool = True) -> Optional[dict]:
    """Extract full schema for a single object.

    By default skips ALL custom fields (any ``__c`` suffix). The schema diff
    compares Core Revenue Cloud schema between releases — project-deployed
    custom fields (``RLM_*__c``) and managed package fields would contaminate
    the diff with content unrelated to the platform.
    """
    if verbose:
        print(f"  Describing {object_name}...", flush=True)

    describe = describe_sobject(org_alias, object_name)
    if describe is None:
        if verbose:
            print(f"    SKIP (not found or error)", flush=True)
        return None

    fields = {}
    for f in describe.get("fields", []):
        name = f["name"]
        if name in SYSTEM_FIELDS:
            continue
        if skip_custom and name.endswith("__c"):
            continue
        fields[name] = extract_field_info(f)

    return {
        "name": object_name,
        "label": describe.get("label", ""),
        "keyPrefix": describe.get("keyPrefix", ""),
        "queryable": describe.get("queryable", False),
        "createable": describe.get("createable", False),
        "updateable": describe.get("updateable", False),
        "deletable": describe.get("deletable", False),
        "fieldCount": len(fields),
        "fields": fields,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract RLM schema from org")
    parser.add_argument("--org", required=True, help="sf CLI target org alias")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--objects", help="File with object names (one per line)")
    parser.add_argument("--all-objects", action="store_true",
                        help="Query ALL objects, not just ERD-tracked")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--concurrency", type=int, default=10,
                        help="Parallel describe calls (default: 10)")
    parser.add_argument("--include-custom", action="store_true",
                        help="Include custom fields (any __c suffix). "
                        "Default skips ALL custom fields so the diff "
                        "reflects only the canonical Revenue Cloud schema.")
    args = parser.parse_args()
    skip_custom = not args.include_custom

    # Determine object list
    if args.objects:
        with open(args.objects) as f:
            objects = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    elif args.all_objects:
        print(f"Querying all EntityDefinitions from {args.org}...")
        records = query_tooling(
            args.org,
            "SELECT QualifiedApiName FROM EntityDefinition WHERE IsQueryable = true ORDER BY QualifiedApiName"
        )
        objects = [r["QualifiedApiName"] for r in records]
        print(f"  Found {len(objects)} queryable objects")
    else:
        objects = get_erd_objects()
        print(f"Using {len(objects)} objects from erd-data.json")

    # Extract schema for each object
    print(f"Extracting schema from {args.org} ({len(objects)} objects, concurrency={args.concurrency})...")
    schema = {}
    errors = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(extract_object_schema, args.org, obj, args.verbose, skip_custom): obj
            for obj in objects
        }
        for i, future in enumerate(as_completed(futures), 1):
            obj_name = futures[future]
            try:
                result = future.result()
                if result:
                    schema[obj_name] = result
                else:
                    errors.append(obj_name)
            except Exception as e:
                errors.append(f"{obj_name}: {e}")
            if not args.verbose and i % 25 == 0:
                print(f"  {i}/{len(objects)} objects processed...", flush=True)

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Extracted: {len(schema)} objects")
    print(f"  Errors/missing: {len(errors)}")
    if errors:
        print(f"  Failed: {', '.join(errors[:20])}")

    # Build output
    output = {
        "metadata": {
            "org_alias": args.org,
            "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "object_count": len(schema),
            "total_fields": sum(obj["fieldCount"] for obj in schema.values()),
            "source": "sf sobject describe",
        },
        "objects": schema,
    }

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, sort_keys=True)
    print(f"\nSchema written to {output_path}")
    print(f"  Objects: {output['metadata']['object_count']}")
    print(f"  Fields: {output['metadata']['total_fields']}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
