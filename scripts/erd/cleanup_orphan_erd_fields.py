#!/usr/bin/env python3
"""
Identify and (optionally) remove orphan ERD fields that don't exist in any
queried Salesforce org.

Orphan = a field in `docs/erds/erd-data.json` that does NOT appear in the
target org's `sobject describe` output. These are typically:

1. PDF extraction artifacts — fields like `Invoice.InvoiceLine`, `Invoice.Settled`,
   or `ApprovalSubmission.POST` that the PDF parser captured by mistake. These
   have no description and just a guessed type.

2. Feature-gated fields — fields documented in v260 dev guide that require a
   feature license/org-perm not enabled in the target org. These typically
   have descriptions and may have `refersTo` for relationships.

3. Removed fields — fields that existed in v260 but were deprecated/removed
   in 262.

Without dual-org cross-validation, we cannot distinguish (1) from (2)/(3)
reliably. This utility supports two safety modes:

  --safe-only   Remove only orphans matching the "PDF artifact" pattern
                (empty description AND no refersTo). 100% safe to remove.

  --aggressive  Remove any orphan field. Use only after cross-validating
                against multiple orgs (e.g., 260 baseline + 262 + ent-pde
                + tso). Pass --orgs <alias1>,<alias2>,... to verify.

Usage:
    # Show candidates without modifying anything
    python scripts/erd/cleanup_orphan_erd_fields.py --org rlm-base__ent-sb0 --dry-run

    # Show only the safe-to-remove candidates
    python scripts/erd/cleanup_orphan_erd_fields.py --org rlm-base__ent-sb0 \\
        --safe-only --dry-run

    # Apply safe-only removal
    python scripts/erd/cleanup_orphan_erd_fields.py --org rlm-base__ent-sb0 \\
        --safe-only --apply

    # Cross-validate against multiple orgs before aggressive removal
    python scripts/erd/cleanup_orphan_erd_fields.py --orgs ent-r1,rlm-base__ent-sb0 \\
        --aggressive --dry-run

    # Include custom (__c) fields in the comparison — only when intentionally
    # validating an extended ERD snapshot that contains deployed RLM_*__c or
    # managed-package fields. Default behavior (skipping custom) aligns with
    # the canonical-platform-schema contract documented in AGENTS.md.
    python scripts/erd/cleanup_orphan_erd_fields.py --org rlm-base__ent-sb0 \\
        --include-custom --dry-run

Outputs a candidates.md report listing every orphan and its classification.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ERD_DATA = REPO_ROOT / "docs" / "erds" / "erd-data.json"

# System fields described by every org — should NEVER be in erd-data.json
SYSTEM_FIELDS = {
    "Id", "IsDeleted", "CreatedDate", "CreatedById", "LastModifiedDate",
    "LastModifiedById", "SystemModstamp", "LastActivityDate", "LastViewedDate",
    "LastReferencedDate", "OwnerId", "RecordTypeId", "CurrencyIsoCode",
}


def describe_sobject(org_alias: str, object_name: str) -> Optional[dict]:
    """Call sf sobject describe. Returns None if the object doesn't exist."""
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


def get_org_fields(org_alias: str, object_name: str,
                   skip_custom: bool = True) -> Optional[Set[str]]:
    """Return the set of field names declared by the org for an object.

    When ``skip_custom`` is True (default), all ``__c``-suffixed fields are
    omitted from the returned set. The ERD is canonical Revenue Cloud
    platform schema; project-deployed (``RLM_*__c``) and managed-package
    fields must not be considered when classifying orphans against the
    default ERD.

    Pass ``skip_custom=False`` (CLI: ``--include-custom``) only for
    project-internal tooling that intentionally wants to consider deployed
    custom fields — e.g. when validating an extended ERD snapshot that
    includes ``RLM_*__c``. See ``AGENTS.md`` for the wider
    custom-fields-excluded contract.

    Returns None if the object doesn't exist in the org (don't treat ERD
    fields as orphans for objects that aren't even in the org).
    """
    describe = describe_sobject(org_alias, object_name)
    if describe is None:
        return None
    fields = set()
    for f in describe.get("fields", []):
        name = f["name"]
        if skip_custom and name.endswith("__c"):
            continue
        fields.add(name)
    return fields


def collect_org_fields(org_aliases: List[str], object_names: List[str],
                       concurrency: int = 10, verbose: bool = False,
                       skip_custom: bool = True
                       ) -> Dict[str, Dict[str, Optional[Set[str]]]]:
    """Collect field sets per (org, object) pair.

    ``skip_custom`` is threaded through to :func:`get_org_fields`; see that
    function for the contract. Defaults to True so the orphan workflow stays
    aligned with the canonical-platform-schema rule.

    Returns: { org_alias: { object_name: {field_set} or None } }
    """
    # Plan: parallelize across (org, object) pairs
    result: Dict[str, Dict[str, Optional[Set[str]]]] = {
        alias: {} for alias in org_aliases
    }
    pairs = [(alias, obj) for alias in org_aliases for obj in object_names]
    print(f"Querying {len(pairs)} (org, object) pairs across "
          f"{len(org_aliases)} orgs (concurrency={concurrency}, "
          f"skip_custom={skip_custom})...")
    start = time.time()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(get_org_fields, alias, obj, skip_custom): (alias, obj)
            for alias, obj in pairs
        }
        for i, future in enumerate(as_completed(futures), 1):
            alias, obj = futures[future]
            try:
                fields = future.result()
                result[alias][obj] = fields
            except Exception as e:
                print(f"  ERROR {alias}/{obj}: {e}", file=sys.stderr)
                result[alias][obj] = None
            if verbose or (i % 50 == 0):
                print(f"  {i}/{len(pairs)} pairs processed...", flush=True)

    elapsed = time.time() - start
    print(f"  Completed in {elapsed:.1f}s")
    return result


def classify_orphan(field_data: dict) -> str:
    """Classify an orphan field.

    Returns one of:
      - 'pdf_artifact'    : empty description + no refersTo (safe to remove)
      - 'documented'      : has a description (legitimate-looking, needs review)
      - 'documented_rel'  : has a refersTo (relationship, needs review)
      - 'malformed'       : couldn't parse the structure

    Safety contract: a field is only ``pdf_artifact`` (auto-removable
    under ``--safe-only``) when it has BOTH an empty description AND no
    ``refersTo``. Relationship orphans (``refersTo`` present) always
    stay in ``documented_rel`` regardless of description — Core-side
    verification is required before removal because relationship
    metadata that ``sf sobject describe`` doesn't surface can mean the
    field exists but is feature-gated, not that it's a PDF artifact.
    """
    if not isinstance(field_data, dict):
        return "malformed"
    desc = (field_data.get("description") or "").strip()
    rt = field_data.get("refersTo")
    if rt:
        return "documented_rel"
    if desc:
        return "documented"
    return "pdf_artifact"


def find_orphans(erd_data: dict, org_data: Dict[str, Dict[str, Optional[Set[str]]]]
                 ) -> List[dict]:
    """Find orphans across all queried orgs.

    A field is an orphan if it appears in the ERD but in NONE of the queried
    orgs (where the object exists in at least one org).

    Returns a list of orphan records:
      [{ object, field, classification, in_org_count, missing_from_org_count }]
    """
    orphans = []
    for obj_name, obj_data in erd_data["objects"].items():
        fields = obj_data.get("fields", {})
        if not isinstance(fields, dict):
            continue

        # Determine which orgs have this object
        org_field_sets = {}
        for alias, alias_data in org_data.items():
            if obj_name in alias_data and alias_data[obj_name] is not None:
                org_field_sets[alias] = alias_data[obj_name]

        if not org_field_sets:
            # Object isn't in any queried org — don't classify as orphan
            continue

        for fname, fdata in fields.items():
            if fname in SYSTEM_FIELDS:
                continue
            # Strip Id suffix for relationship matching (PaymentScheduleId vs PaymentSchedule)
            present_in_any = any(
                fname in fset or
                (fname.endswith("Id") and fname[:-2] in fset) or
                (not fname.endswith("Id") and (fname + "Id") in fset)
                for fset in org_field_sets.values()
            )
            if present_in_any:
                continue

            orphans.append({
                "object": obj_name,
                "field": fname,
                "classification": classify_orphan(fdata),
                "field_data": fdata,
                "missing_from": list(org_field_sets.keys()),
            })

    return orphans


def generate_report(orphans: List[dict], org_aliases: List[str]) -> str:
    """Generate a markdown report of orphan candidates."""
    by_class = {}
    for o in orphans:
        by_class.setdefault(o["classification"], []).append(o)

    lines = [
        "# Orphan ERD Field Candidates",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Orgs queried: {', '.join(org_aliases)}",
        "",
        "## Summary",
        "",
        f"| Classification | Count | Safety |",
        f"|----------------|-------|--------|",
    ]
    safety_map = {
        "pdf_artifact": "Safe to remove",
        "documented": "Review (may be feature-gated)",
        "documented_rel": "Review (relationship may be feature-gated)",
        "malformed": "Review (data quality issue)",
    }
    for cls in ["pdf_artifact", "documented", "documented_rel", "malformed"]:
        count = len(by_class.get(cls, []))
        lines.append(f"| {cls} | {count} | {safety_map[cls]} |")
    lines.append(f"| **Total** | **{len(orphans)}** | |")
    lines.append("")

    # Per-classification detail
    for cls in ["pdf_artifact", "documented", "documented_rel", "malformed"]:
        items = by_class.get(cls, [])
        if not items:
            continue
        lines.extend([
            f"## {cls} ({len(items)})",
            "",
            f"_{safety_map[cls]}_",
            "",
        ])
        # Group by object
        by_object = {}
        for o in items:
            by_object.setdefault(o["object"], []).append(o)
        for obj_name in sorted(by_object):
            lines.append(f"### {obj_name}")
            lines.append("")
            for o in sorted(by_object[obj_name], key=lambda x: x["field"]):
                fd = o["field_data"]
                if isinstance(fd, dict):
                    desc = (fd.get("description") or "").strip()
                    type_ = fd.get("type", "?")
                    rt = fd.get("refersTo", "")
                    suffix = f" -> {rt}" if rt else ""
                    desc_str = f" — {desc[:80]}" if desc else ""
                    lines.append(f"- `{o['field']}` ({type_}){suffix}{desc_str}")
                else:
                    lines.append(f"- `{o['field']}` (malformed: {fd!r})")
            lines.append("")

    return "\n".join(lines)


def apply_removals(erd_data: dict, orphans: List[dict],
                   classes_to_remove: Set[str]) -> Tuple[int, int]:
    """Remove orphans from erd-data.json. Returns (fields_removed, rels_removed)."""
    removed_fields = 0
    removed_rels = 0
    targets = {(o["object"], o["field"]) for o in orphans
               if o["classification"] in classes_to_remove}

    for obj_name, obj_data in erd_data["objects"].items():
        fields = obj_data.get("fields", {})
        if not isinstance(fields, dict):
            continue
        for fname in list(fields.keys()):
            if (obj_name, fname) in targets:
                del fields[fname]
                removed_fields += 1

    # Also remove relationships pointing to removed fields
    rels = erd_data.get("relationships", [])
    new_rels = [
        r for r in rels
        if (r["source"], r.get("field", "")) not in targets
    ]
    removed_rels = len(rels) - len(new_rels)
    erd_data["relationships"] = new_rels

    # Update stats
    total_fields = sum(len(o.get("fields", {})) for o in erd_data["objects"].values())
    erd_data["stats"] = {
        "totalObjects": len(erd_data["objects"]),
        "totalRelationships": len(erd_data["relationships"]),
        "totalFields": total_fields,
        "domains": sorted(set(
            o.get("domain", "Unknown") for o in erd_data["objects"].values()
        )),
    }

    return removed_fields, removed_rels


def main():
    parser = argparse.ArgumentParser(
        description="Identify and clean orphan ERD fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--org", help="Single org alias to query")
    parser.add_argument("--orgs", help="Comma-separated org aliases for cross-validation")
    parser.add_argument("--safe-only", action="store_true",
                        help="Only act on pdf_artifact orphans (empty description)")
    parser.add_argument("--aggressive", action="store_true",
                        help="Act on all orphan types. Requires --orgs (multiple).")
    parser.add_argument("--apply", action="store_true",
                        help="Actually modify erd-data.json (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't modify anything (default behavior)")
    parser.add_argument("--report", default="docs/erds/orphan-candidates.md",
                        help="Output markdown report path (relative to repo root)")
    parser.add_argument("--concurrency", type=int, default=10,
                        help="Parallel describe calls (default: 10)")
    parser.add_argument(
        "--include-custom",
        action="store_true",
        help="Include custom (__c) fields when reading orgs. Default is to "
             "skip them so orphan classification stays aligned with the "
             "canonical platform schema (see AGENTS.md). Use only when you "
             "intentionally want to consider deployed RLM_*__c or managed-"
             "package fields — e.g. validating an extended ERD snapshot.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # Resolve org list
    if args.orgs:
        org_aliases = [a.strip() for a in args.orgs.split(",") if a.strip()]
    elif args.org:
        org_aliases = [args.org]
    else:
        parser.error("--org or --orgs is required")

    if args.aggressive and len(org_aliases) < 2:
        parser.error("--aggressive requires multiple orgs via --orgs (cross-validation)")

    if not args.apply:
        args.dry_run = True

    # Load ERD
    if not ERD_DATA.exists():
        print(f"ERROR: {ERD_DATA} not found", file=sys.stderr)
        return 1
    with open(ERD_DATA) as f:
        erd_data = json.load(f)

    object_names = sorted(erd_data["objects"].keys())
    print(f"ERD has {len(object_names)} objects")

    # Query orgs
    org_data = collect_org_fields(
        org_aliases, object_names,
        concurrency=args.concurrency, verbose=args.verbose,
        skip_custom=not args.include_custom,
    )

    # Find orphans
    orphans = find_orphans(erd_data, org_data)
    print(f"\nFound {len(orphans)} orphan field candidates across "
          f"{len(set(o['object'] for o in orphans))} objects")
    by_cls = {}
    for o in orphans:
        by_cls[o["classification"]] = by_cls.get(o["classification"], 0) + 1
    for cls in ["pdf_artifact", "documented", "documented_rel", "malformed"]:
        print(f"  {cls}: {by_cls.get(cls, 0)}")

    # Generate report
    report = generate_report(orphans, org_aliases)
    report_path = REPO_ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport written to {report_path}")

    # Apply removals if requested
    if args.apply:
        if args.aggressive:
            classes_to_remove = {"pdf_artifact", "documented", "documented_rel", "malformed"}
        elif args.safe_only:
            classes_to_remove = {"pdf_artifact"}
        else:
            print("\nNo --safe-only or --aggressive specified. Nothing removed.")
            return 0

        # Backup
        backup_path = ERD_DATA.with_suffix(".json.bak")
        with open(backup_path, "w") as f:
            json.dump(erd_data, f, indent=2)
        print(f"Backup written to {backup_path}")

        # Apply
        f_removed, r_removed = apply_removals(erd_data, orphans, classes_to_remove)
        with open(ERD_DATA, "w") as f:
            json.dump(erd_data, f, indent=2)

        print(f"\nApplied to {ERD_DATA}:")
        print(f"  Fields removed: {f_removed}")
        print(f"  Relationships removed: {r_removed}")
        print(f"\nNext: re-run validate_erd_against_org.py and build_erds.py")
    else:
        print("\nDry-run mode — no changes made. Use --apply with "
              "--safe-only or --aggressive to remove fields.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
