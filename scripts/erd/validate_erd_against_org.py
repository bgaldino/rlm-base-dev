#!/usr/bin/env python3
"""
Validate ERD data (docs/erds/erd-data.json) against a live Salesforce org.

Uses `sf sobject describe` to fetch real metadata for each object in the ERD,
then compares fields and relationships against what's documented. Produces a
gap report showing missing fields, extra fields, and missing relationships.

Prerequisites:
    - sf CLI authenticated to the target org (`sf org login web --alias <alias>`)
    - The target org must be set as default or passed via --org

Usage:
    python scripts/erd/validate_erd_against_org.py --org beta
    python scripts/erd/validate_erd_against_org.py --org beta --objects PriceBookRateCard,RateCard
    python scripts/erd/validate_erd_against_org.py --org beta --domain "Rate Management"
    python scripts/erd/validate_erd_against_org.py --org beta --patch  # auto-patch erd-data.json
    python scripts/erd/validate_erd_against_org.py --org beta --report docs/erds/validation-report.md

Options:
    --org ALIAS           Target org alias (required)
    --objects OBJ,OBJ     Comma-separated list of objects to validate (default: all)
    --domain DOMAIN       Only validate objects in this domain
    --patch               Auto-patch erd-data.json with discovered fields/relationships
    --add-objects OBJ,OBJ Describe these objects in the org and add them to the ERD
                          (needs --add-domain); writes erd-data.json and the shards
    --add-domain DOMAIN   ERD domain label for --add-objects, e.g.
                          "Transaction Management (Core Object)"
    --report PATH         Write markdown gap report to file
    --verbose             Show per-object detail during scan
    --concurrency N       Parallel describe calls (default: 10)
    --include-custom      Include custom fields (any __c suffix). Default
                          behavior strips ALL custom fields so the ERD
                          reflects only the canonical Revenue Cloud schema.
    --help                Show this help
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import erd_shards  # sibling module: writes erd-data.json and the per-domain shards


# ── Domain color mapping (must match build_erds.py / erd-data.json) ──────────
DOMAIN_MAP = {
    "Product Catalog Management": {"short": "PCM", "color": "#42a5f5"},
    "Product Catalog Management (Core Object)": {"short": "PCM", "color": "#42a5f5"},
    "Salesforce Pricing": {"short": "Pricing", "color": "#ab47bc"},
    "Rate Management": {"short": "Rates", "color": "#ec407a"},
    "Product Configurator": {"short": "Configurator", "color": "#26c6da"},
    "Configurator": {"short": "Configurator", "color": "#26c6da"},
    "Transaction Management": {"short": "Transactions", "color": "#ffa726"},
    "Transaction Management (Core Object)": {"short": "Transactions", "color": "#ffa726"},
    "Advanced Approvals": {"short": "Approvals", "color": "#8d6e63"},
    "Approvals": {"short": "Approvals", "color": "#8d6e63"},
    "Dynamic Revenue Orchestrator": {"short": "DRO", "color": "#66bb6a"},
    "Usage Management": {"short": "Usage", "color": "#5c6bc0"},
    "Usage Management (Core Object)": {"short": "Usage", "color": "#5c6bc0"},
    "Billing": {"short": "Billing", "color": "#ef5350"},
    "Billing (Core Object)": {"short": "Billing", "color": "#ef5350"},
    "Contracts & CLM": {"short": "Contracts", "color": "#14b8a6"},
}

# Fields to always skip (system/audit fields not useful in ERD)
SYSTEM_FIELDS = {
    "Id", "IsDeleted", "CreatedDate", "CreatedById", "LastModifiedDate",
    "LastModifiedById", "SystemModstamp", "LastActivityDate", "OwnerId",
    "RecordTypeId", "CurrencyIsoCode",
}


@dataclass
class FieldInfo:
    """Metadata about a single field from the org."""
    name: str
    type: str
    label: str
    reference_to: List[str]
    relationship_name: Optional[str]
    nillable: bool
    updateable: bool
    custom: bool
    namespace: Optional[str] = None


@dataclass
class ObjectDiff:
    """Diff between ERD and org for a single object."""
    object_name: str
    domain: str
    org_exists: bool = True
    fields_in_org_not_erd: List[FieldInfo] = field(default_factory=list)
    fields_in_erd_not_org: List[str] = field(default_factory=list)
    rels_in_org_not_erd: List[FieldInfo] = field(default_factory=list)
    rels_in_erd_not_org: List[Tuple[str, str]] = field(default_factory=list)
    erd_field_count: int = 0
    org_field_count: int = 0
    error: Optional[str] = None
    # Platform spelling when it differs from the ERD key. Object describe is
    # case-insensitive, so without this a wrong-cased key reads as "present".
    canonical_name: Optional[str] = None


def describe_sobject(org_alias: str, object_name: str) -> Optional[dict]:
    """Call sf sobject describe and return the parsed JSON."""
    try:
        result = subprocess.run(
            ["sf", "sobject", "describe", "--sobject", object_name,
             "--target-org", org_alias, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("result", data)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def parse_org_fields(describe_result: dict, skip_custom: bool = True) -> List[FieldInfo]:
    """Parse field metadata from a describe result.

    By default skips ALL custom fields (anything ending in ``__c``). The ERD
    represents the canonical Revenue Cloud schema, so custom fields deployed
    by the project itself (e.g. ``RLM_*__c``) or any managed package
    (``namespace__Field__c``) must NOT leak in. Pass ``skip_custom=False``
    only for project-internal tooling that needs to see custom additions.
    """
    fields = []
    for f in describe_result.get("fields", []):
        name = f["name"]
        # Skip system fields
        if name in SYSTEM_FIELDS:
            continue
        # Detect custom fields (bare or managed) and skip when requested
        custom = name.endswith("__c")
        namespace = None
        if custom and "__" in name[:-3]:
            parts = name.split("__")
            if len(parts) >= 3:
                namespace = parts[0]
        if custom and skip_custom:
            continue

        ref_to = f.get("referenceTo", [])
        rel_name = f.get("relationshipName")

        fields.append(FieldInfo(
            name=name,
            type=f.get("type", ""),
            label=f.get("label", ""),
            reference_to=ref_to if ref_to else [],
            relationship_name=rel_name,
            nillable=f.get("nillable", True),
            updateable=f.get("updateable", True),
            custom=custom,
            namespace=namespace,
        ))
    return fields


def diff_object(
    object_name: str,
    erd_obj: dict,
    org_alias: str,
    erd_relationships: List[dict],
    skip_custom: bool = True,
) -> ObjectDiff:
    """Compare a single object between ERD and org."""
    domain = erd_obj.get("domain", "Unknown")
    diff = ObjectDiff(object_name=object_name, domain=domain)

    erd_fields = erd_obj.get("fields", {})
    diff.erd_field_count = len(erd_fields)
    erd_field_names = {k.lower(): k for k in erd_fields}

    # Describe from org
    describe = describe_sobject(org_alias, object_name)
    if describe is None:
        diff.org_exists = False
        diff.error = f"Could not describe {object_name} (may not exist in org)"
        return diff

    if describe.get("name") and describe["name"] != object_name:
        diff.canonical_name = describe["name"]

    org_fields = parse_org_fields(describe, skip_custom=skip_custom)
    diff.org_field_count = len(org_fields)

    org_field_map = {f.name.lower(): f for f in org_fields}

    # Fields in org but not in ERD
    for f in org_fields:
        if f.name.lower() not in erd_field_names:
            if f.reference_to:
                diff.rels_in_org_not_erd.append(f)
            else:
                diff.fields_in_org_not_erd.append(f)

    # Fields in ERD but not in org
    for erd_name in erd_fields:
        if erd_name.lower() not in org_field_map and erd_name not in SYSTEM_FIELDS:
            diff.fields_in_erd_not_org.append(erd_name)

    # Check relationships: ERD says source -> target, does org confirm?
    erd_rels_out = [r for r in erd_relationships if r["source"] == object_name]
    for rel in erd_rels_out:
        field_name = rel.get("field", "")
        if field_name and field_name.lower() not in org_field_map:
            diff.rels_in_erd_not_org.append((field_name, rel["target"]))

    return diff


def link_new_objects(erd_data: dict, new_names: set = None) -> int:
    """Add the relationship rows touching `new_names` that are missing: the new objects' own
    reference fields and existing objects' fields that point at them. `None` means every
    object (a backfill). Every target of a polymorphic field is linked; targets must exist in the
    ERD. Returns rows added; a second run adds 0."""
    objects, rels = erd_data["objects"], erd_data["relationships"]
    seen = {(r["source"], r["target"], r.get("field", "")) for r in rels}
    added = 0
    for name, obj in objects.items():
        for fname, f in obj["fields"].items():
            targets = f.get("refersTo") or []
            if isinstance(targets, str):  # a polymorphic field's targets are comma-joined
                targets = [t.strip() for t in targets.split(",")]
            for target in targets:
                if (new_names is None or name in new_names or target in new_names) and target in objects \
                        and (name, target, fname) not in seen:
                    seen.add((name, target, fname))
                    rels.append({"source": name, "target": target, "field": fname,
                                 "type": f.get("relationshipType", "lookup").lower()})
                    added += 1
    return added


def build_object_entries(erd_data: dict, describes: Dict[str, dict], domain: str,
                         skip_custom: bool = True) -> Tuple[int, int]:
    """Add whole objects, from org describes, to `erd_data`. Returns (objects, relationships).

    `describes` maps a requested name to its describe result; the entry is keyed by the
    describe's canonical `name`, never the spelling that was asked for.
    """
    short = DOMAIN_MAP.get(domain, {}).get("short")
    if short is None:
        raise ValueError(f"unknown ERD domain {domain!r}; known: {sorted(DOMAIN_MAP)}")
    objects, rels = erd_data["objects"], erd_data["relationships"]
    entries = {}
    for describe in describes.values():
        name = describe["name"]
        if name in objects:
            raise ValueError(f"{name} is already in the ERD; use --objects/--patch to refresh it")
        raw = {f["name"]: f for f in describe.get("fields", [])}
        fields = {}
        for fi in parse_org_fields(describe, skip_custom=skip_custom):
            entry = {"description": fi.label or "", "type": fi.type or "string"}
            if fi.reference_to:
                entry["refersTo"] = ", ".join(fi.reference_to)
                entry["relationshipName"] = fi.relationship_name
                entry["relationshipType"] = (
                    "Master-Detail" if raw[fi.name].get("cascadeDelete") else "Lookup")
            fields[fi.name] = entry
        entries[name] = {"domain": domain, "domainShort": short,
                         "isStandard": "(Core Object)" in domain, "fields": fields}
    objects.update(entries)
    return len(entries), link_new_objects(erd_data, set(entries))


def patch_erd(erd_data: dict, diffs: List[ObjectDiff]) -> Tuple[int, int, int]:
    """Apply org discoveries back into erd-data.json. Returns (fields_added, rels_added, fields_removed)."""
    objects = erd_data["objects"]
    relationships = erd_data["relationships"]

    fields_added = 0
    fields_removed = 0
    patched = set()

    for diff in diffs:
        if not diff.org_exists or diff.error:
            continue
        if diff.object_name not in objects:  # new objects go through --add-objects
            continue
        obj_fields = objects[diff.object_name]["fields"]

        # Add missing reference fields (relationships)
        for f in diff.rels_in_org_not_erd:
            if f.name not in obj_fields:
                obj_fields[f.name] = {
                    "description": f.label or "",
                    "type": "reference",
                    "refersTo": ", ".join(f.reference_to),
                    "relationshipType": "lookup",
                }
                fields_added += 1
                patched.add(diff.object_name)

        # Add missing data fields
        for f in diff.fields_in_org_not_erd:
            if f.name not in obj_fields:
                entry = {
                    "description": f.label or "",
                    "type": f.type or "string",
                }
                obj_fields[f.name] = entry
                fields_added += 1

    # Link the patched objects' reference fields, and any pointing at them
    rels_added = link_new_objects(erd_data, patched)

    # Update stats
    total_fields = sum(len(o.get("fields", {})) for o in objects.values())
    erd_data["stats"] = {
        "totalObjects": len(objects),
        "totalRelationships": len(relationships),
        "totalFields": total_fields,
        "domains": sorted(set(o.get("domain", "Unknown") for o in objects.values())),
    }

    return fields_added, rels_added, fields_removed


def generate_report(diffs: List[ObjectDiff]) -> str:
    """Generate a markdown gap report."""
    lines = [
        "# ERD Validation Report",
        f"",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Summary stats
    total_objs = len(diffs)
    missing_objs = sum(1 for d in diffs if not d.org_exists)
    objs_with_gaps = sum(1 for d in diffs if d.org_exists and (
        d.fields_in_org_not_erd or d.rels_in_org_not_erd))
    total_missing_fields = sum(len(d.fields_in_org_not_erd) for d in diffs)
    total_missing_rels = sum(len(d.rels_in_org_not_erd) for d in diffs)
    total_extra_erd = sum(len(d.fields_in_erd_not_org) for d in diffs)

    lines.extend([
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Objects validated | {total_objs} |",
        f"| Objects not found in org | {missing_objs} |",
        f"| Objects with field gaps | {objs_with_gaps} |",
        f"| Fields in org missing from ERD | {total_missing_fields} |",
        f"| Relationships in org missing from ERD | {total_missing_rels} |",
        f"| ERD fields not found in org | {total_extra_erd} |",
        "",
    ])

    # Objects not found in org
    not_found = [d for d in diffs if not d.org_exists]
    if not_found:
        lines.extend([
            "## Objects Not Found in Org",
            "",
            "These objects are in `erd-data.json` but could not be described in the target org.",
            "They may require specific licenses, permissions, or features to be enabled.",
            "",
        ])
        for d in sorted(not_found, key=lambda x: x.object_name):
            lines.append(f"- `{d.object_name}` ({d.domain})")
        lines.append("")

    # Per-object gaps (only objects with issues)
    gaps = [d for d in diffs if d.org_exists and (
        d.fields_in_org_not_erd or d.rels_in_org_not_erd or d.fields_in_erd_not_org)]

    if gaps:
        lines.extend([
            "## Per-Object Gaps",
            "",
        ])

        for d in sorted(gaps, key=lambda x: (-len(x.rels_in_org_not_erd) - len(x.fields_in_org_not_erd), x.object_name)):
            lines.append(f"### {d.object_name}")
            lines.append(f"Domain: {d.domain} | ERD fields: {d.erd_field_count} | Org fields: {d.org_field_count}")
            lines.append("")

            if d.rels_in_org_not_erd:
                lines.append("**Relationships in org, missing from ERD:**")
                lines.append("")
                lines.append("| Field | Type | References |")
                lines.append("|-------|------|------------|")
                for f in sorted(d.rels_in_org_not_erd, key=lambda x: x.name):
                    refs = ", ".join(f.reference_to) if f.reference_to else "?"
                    lines.append(f"| `{f.name}` | {f.type} | {refs} |")
                lines.append("")

            if d.fields_in_org_not_erd:
                lines.append(f"**Data fields in org, missing from ERD ({len(d.fields_in_org_not_erd)}):**")
                lines.append("")
                # Group by type
                by_type = {}
                for f in d.fields_in_org_not_erd:
                    by_type.setdefault(f.type, []).append(f)
                for t in sorted(by_type):
                    names = ", ".join(f"`{f.name}`" for f in sorted(by_type[t], key=lambda x: x.name))
                    lines.append(f"- *{t}*: {names}")
                lines.append("")

            if d.fields_in_erd_not_org:
                lines.append(f"**ERD fields not found in org ({len(d.fields_in_erd_not_org)}):**")
                lines.append("")
                for name in sorted(d.fields_in_erd_not_org):
                    lines.append(f"- `{name}`")
                lines.append("")

    # Clean objects
    clean = [d for d in diffs if d.org_exists and not (
        d.fields_in_org_not_erd or d.rels_in_org_not_erd or d.fields_in_erd_not_org)]
    if clean:
        lines.extend([
            f"## Complete Objects ({len(clean)})",
            "",
            "These objects have no gaps between ERD and org:",
            "",
        ])
        for d in sorted(clean, key=lambda x: x.object_name):
            lines.append(f"- `{d.object_name}` ({d.erd_field_count} fields)")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate ERD data against a live Salesforce org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--org", required=True, help="Target org alias")
    parser.add_argument("--objects", help="Comma-separated object names to validate")
    parser.add_argument("--domain", help="Only validate objects in this domain")
    parser.add_argument("--patch", action="store_true", help="Auto-patch erd-data.json")
    parser.add_argument("--add-objects", help="Comma-separated objects to describe and add")
    parser.add_argument("--add-domain", help="ERD domain label for --add-objects")
    parser.add_argument("--report", help="Write markdown report to file")
    parser.add_argument("--verbose", action="store_true", help="Show per-object progress")
    parser.add_argument("--concurrency", type=int, default=10, help="Parallel describe calls")
    parser.add_argument("--include-custom", action="store_true",
                        help="Include custom fields (any __c suffix). Default "
                        "behavior strips ALL custom fields, including project-"
                        "deployed RLM_*__c fields and managed package fields, "
                        "so the ERD reflects only the canonical Revenue Cloud "
                        "schema.")

    args = parser.parse_args()
    skip_custom = not args.include_custom

    # Find repo root (script lives at scripts/erd/, so go up two levels)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    erd_path = repo_root / "docs" / "erds" / "erd-data.json"

    if not erd_path.exists():
        print(f"ERROR: {erd_path} not found")
        sys.exit(1)

    # Load ERD data
    with open(erd_path) as f:
        erd_data = json.load(f)

    objects = erd_data["objects"]
    relationships = erd_data["relationships"]

    if args.add_objects:
        if not args.add_domain:
            print("ERROR: --add-objects needs --add-domain")
            sys.exit(2)
        describes = {}
        for name in (n.strip() for n in args.add_objects.split(",") if n.strip()):
            describes[name] = describe_sobject(args.org, name)
            if describes[name] is None:
                print(f"ERROR: could not describe {name} in org '{args.org}'")
                sys.exit(1)
        n_obj, n_rel = build_object_entries(erd_data, describes, args.add_domain, skip_custom)
        erd_shards.save(erd_data, erd_path, verified={
            "release": erd_data["metadata"].get("release", ""),
            "apiVersion": erd_data["metadata"].get("apiVersion", "")})
        print(f"Added {n_obj} objects and {n_rel} relationships to {erd_path}")
        print("Run `python scripts/erd/build_erds.py` to rebuild the HTML ERD")
        return 0

    # Filter objects
    if args.objects:
        obj_names = [o.strip() for o in args.objects.split(",")]
    elif args.domain:
        obj_names = [name for name, obj in objects.items() if obj.get("domain") == args.domain]
    else:
        obj_names = list(objects.keys())

    print(f"Validating {len(obj_names)} objects against org '{args.org}'...")
    print(f"ERD: {len(objects)} objects, {len(relationships)} relationships")
    print()

    # Verify sf CLI is available
    try:
        subprocess.run(["sf", "--version"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print("ERROR: sf CLI not found. Install via: npm install -g @salesforce/cli")
        sys.exit(1)

    # Run describes in parallel
    diffs: List[ObjectDiff] = []
    start_time = time.time()
    completed = 0

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {}
        for name in obj_names:
            erd_obj = objects.get(name, {})
            future = executor.submit(
                diff_object, name, erd_obj, args.org, relationships, skip_custom
            )
            futures[future] = name

        for future in as_completed(futures):
            name = futures[future]
            completed += 1
            try:
                diff = future.result()
                diffs.append(diff)
                if args.verbose:
                    status = "NOT FOUND" if not diff.org_exists else "OK"
                    gaps = len(diff.fields_in_org_not_erd) + len(diff.rels_in_org_not_erd)
                    if gaps > 0:
                        status = f"+{gaps} missing"
                    print(f"  [{completed}/{len(obj_names)}] {name}: {status}")
            except Exception as e:
                print(f"  [{completed}/{len(obj_names)}] {name}: ERROR - {e}")

    elapsed = time.time() - start_time
    print(f"\nScanned {len(diffs)} objects in {elapsed:.1f}s")

    # Summary
    missing = sum(1 for d in diffs if not d.org_exists)
    with_gaps = sum(1 for d in diffs if d.org_exists and (
        d.fields_in_org_not_erd or d.rels_in_org_not_erd))
    new_fields = sum(len(d.fields_in_org_not_erd) for d in diffs)
    new_rels = sum(len(d.rels_in_org_not_erd) for d in diffs)
    extra_erd = sum(len(d.fields_in_erd_not_org) for d in diffs)

    print(f"  Objects not in org: {missing}")
    print(f"  Objects with gaps: {with_gaps}")
    miscased = [d for d in diffs if d.canonical_name]
    print(f"  ERD keys whose casing differs from the platform name: {len(miscased)}")
    for d in miscased:
        print(f"    {d.object_name} -> {d.canonical_name}")
    print(f"  Fields in org missing from ERD: {new_fields}")
    print(f"  Relationships in org missing from ERD: {new_rels}")
    print(f"  ERD fields not in org: {extra_erd}")

    # Patch mode
    if args.patch and (new_fields > 0 or new_rels > 0):
        print(f"\nPatching {erd_path}...")
        fa, ra, fr = patch_erd(erd_data, diffs)
        # Writes erd-data.json and the per-domain shards; only shards whose objects changed
        # get a fresh provenance stamp.
        erd_shards.save(erd_data, erd_path, verified={
            "release": erd_data["metadata"].get("release", ""),
            "apiVersion": erd_data["metadata"].get("apiVersion", "")})
        print(f"  Added {fa} fields, {ra} relationships")
        print(f"  Run `python scripts/erd/build_erds.py` to rebuild the HTML ERD")

    # Report
    if args.report:
        report = generate_report(diffs)
        report_path = repo_root / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\nReport written to {report_path}")

    # Exit code
    if missing > 0 or with_gaps > 0 or miscased:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
