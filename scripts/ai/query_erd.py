#!/usr/bin/env python3
"""Query the Revenue Cloud ERD data model (docs/erds/erd-data.json).

Usage:
    python scripts/ai/query_erd.py describe Product2
    python scripts/ai/query_erd.py relationships Product2
    python scripts/ai/query_erd.py domain Billing
    python scripts/ai/query_erd.py path Product2 Invoice
    python scripts/ai/query_erd.py search "usage"
    python scripts/ai/query_erd.py stats
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ERD_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "erds" / "erd-data.json"


def load_erd():
    with open(ERD_PATH) as f:
        return json.load(f)


def get_domain_short(obj_data):
    return obj_data.get("domainShort", obj_data.get("domain", "Unknown"))


def extract_refs(field_data):
    """Extract referenced object names from a field's refersTo."""
    refs_raw = field_data.get("refersTo", "")
    if not refs_raw:
        return []
    if isinstance(refs_raw, list):
        return [r.strip().rstrip(",") for r in refs_raw if r.strip().rstrip(",")]
    return [r.strip().rstrip(",") for r in refs_raw.split(",") if r.strip().rstrip(",")]


def build_relationship_index(erd):
    """Build forward and reverse relationship indexes."""
    outgoing = defaultdict(list)  # object -> [(field, target_object)]
    incoming = defaultdict(list)  # target_object -> [(source_object, field)]

    for obj_name, obj_data in erd["objects"].items():
        for field_name, field_data in obj_data.get("fields", {}).items():
            if field_data.get("type") == "reference" or "refersTo" in field_data:
                for ref in extract_refs(field_data):
                    if ref and ref in erd["objects"]:
                        outgoing[obj_name].append((field_name, ref))
                        incoming[ref].append((obj_name, field_name))

    return outgoing, incoming


def cmd_describe(erd, obj_name):
    obj_name_match = find_object(erd, obj_name)
    if not obj_name_match:
        print(f"Object '{obj_name}' not found. Try: python scripts/query_erd.py search \"{obj_name}\"")
        return

    obj_data = erd["objects"][obj_name_match]
    domain = obj_data.get("domain", "Unknown")
    domain_short = get_domain_short(obj_data)
    fields = obj_data.get("fields", {})

    ref_fields = {}
    data_fields = {}
    for fname, fdata in sorted(fields.items()):
        if fdata.get("type") == "reference" or "refersTo" in fdata:
            ref_fields[fname] = fdata
        else:
            data_fields[fname] = fdata

    print(f"\n{obj_name_match}")
    print(f"  Domain: {domain} ({domain_short})")
    print(f"  Fields: {len(fields)} total ({len(ref_fields)} relationships, {len(data_fields)} data)")
    print(f"  Standard: {obj_data.get('isStandard', obj_data.get('is_standard', 'unknown'))}")

    if ref_fields:
        print(f"\n  Relationship Fields ({len(ref_fields)}):")
        for fname, fdata in sorted(ref_fields.items()):
            refs = extract_refs(fdata)
            rel_name = fdata.get("relationshipName", "")
            targets = ", ".join(refs) if refs else "?"
            desc = fdata.get("description", "")[:80]
            suffix = f" ({rel_name})" if rel_name else ""
            print(f"    {fname}{suffix} → {targets}")
            if desc:
                print(f"      {desc}")

    if data_fields:
        print(f"\n  Data Fields ({len(data_fields)}):")
        for fname, fdata in sorted(data_fields.items()):
            ftype = fdata.get("type", "?")
            desc = fdata.get("description", "")[:80]
            print(f"    {fname} ({ftype}){': ' + desc if desc else ''}")


def cmd_relationships(erd, obj_name):
    obj_name_match = find_object(erd, obj_name)
    if not obj_name_match:
        print(f"Object '{obj_name}' not found.")
        return

    outgoing, incoming = build_relationship_index(erd)

    print(f"\n{obj_name_match} — Relationships\n")

    out = outgoing.get(obj_name_match, [])
    if out:
        print(f"  Outgoing (this object references):")
        for field, target in sorted(out, key=lambda x: x[1]):
            target_domain = get_domain_short(erd["objects"].get(target, {}))
            print(f"    {field} → {target} [{target_domain}]")

    inc = incoming.get(obj_name_match, [])
    if inc:
        print(f"\n  Incoming (referenced by):")
        for source, field in sorted(inc, key=lambda x: x[0]):
            source_domain = get_domain_short(erd["objects"].get(source, {}))
            print(f"    {source}.{field} [{source_domain}]")

    if not out and not inc:
        print("  No relationships found.")


def cmd_domain(erd, domain_name):
    matches = []
    for obj_name, obj_data in sorted(erd["objects"].items()):
        d = obj_data.get("domain", "")
        ds = get_domain_short(obj_data)
        if domain_name.lower() in d.lower() or domain_name.lower() in ds.lower():
            matches.append((obj_name, obj_data))

    if not matches:
        domains = sorted(set(get_domain_short(d) for d in erd["objects"].values()))
        print(f"No objects found for domain '{domain_name}'.")
        print(f"Available domains: {', '.join(domains)}")
        return

    domain_label = matches[0][1].get("domain", domain_name)
    print(f"\n{domain_label} — {len(matches)} objects\n")

    for obj_name, obj_data in matches:
        fields = obj_data.get("fields", {})
        ref_count = sum(1 for f in fields.values()
                        if f.get("type") == "reference" or "refersTo" in f)
        print(f"  {obj_name} ({len(fields)} fields, {ref_count} relationships)")


def cmd_path(erd, start, end):
    start_match = find_object(erd, start)
    end_match = find_object(erd, end)
    if not start_match:
        print(f"Start object '{start}' not found.")
        return
    if not end_match:
        print(f"End object '{end}' not found.")
        return

    outgoing, _ = build_relationship_index(erd)

    visited = {start_match}
    queue = [(start_match, [(start_match, None, None)])]

    while queue:
        current, path = queue.pop(0)
        if current == end_match:
            print(f"\nPath: {start_match} → {end_match} ({len(path) - 1} hops)\n")
            for i, (obj, field, via) in enumerate(path):
                domain = get_domain_short(erd["objects"].get(obj, {}))
                if i == 0:
                    print(f"  {obj} [{domain}]")
                else:
                    print(f"    ↓ {field}")
                    print(f"  {obj} [{domain}]")
            return

        for field, target in outgoing.get(current, []):
            if target not in visited:
                visited.add(target)
                queue.append((target, path + [(target, field, current)]))

    _, incoming = build_relationship_index(erd)
    visited = {start_match}
    queue = [(start_match, [(start_match, None, None)])]

    while queue:
        current, path = queue.pop(0)
        if current == end_match:
            print(f"\nPath: {start_match} → {end_match} ({len(path) - 1} hops, reverse traversal)\n")
            for i, (obj, field, via) in enumerate(path):
                domain = get_domain_short(erd["objects"].get(obj, {}))
                if i == 0:
                    print(f"  {obj} [{domain}]")
                else:
                    print(f"    ↑ {via}.{field}")
                    print(f"  {obj} [{domain}]")
            return

        for source, field in incoming.get(current, []):
            if source not in visited:
                visited.add(source)
                queue.append((source, path + [(source, field, source)]))

    print(f"\nNo path found between {start_match} and {end_match}.")


def cmd_search(erd, query):
    query_lower = query.lower()
    obj_matches = []
    field_matches = []

    for obj_name, obj_data in sorted(erd["objects"].items()):
        if query_lower in obj_name.lower():
            obj_matches.append((obj_name, obj_data))

        for field_name, field_data in obj_data.get("fields", {}).items():
            if query_lower in field_name.lower():
                field_matches.append((obj_name, field_name, field_data))

    if obj_matches:
        print(f"\nObjects matching '{query}' ({len(obj_matches)}):\n")
        for obj_name, obj_data in obj_matches:
            domain = get_domain_short(obj_data)
            field_count = len(obj_data.get("fields", {}))
            print(f"  {obj_name} [{domain}] ({field_count} fields)")

    if field_matches:
        print(f"\nFields matching '{query}' ({len(field_matches)}):\n")
        for obj_name, field_name, field_data in field_matches[:50]:
            ftype = field_data.get("type", "?")
            refs = extract_refs(field_data)
            if refs:
                print(f"  {obj_name}.{field_name} ({ftype}) → {', '.join(refs)}")
            else:
                print(f"  {obj_name}.{field_name} ({ftype})")
        if len(field_matches) > 50:
            print(f"  ... and {len(field_matches) - 50} more")

    if not obj_matches and not field_matches:
        print(f"No results for '{query}'.")


def cmd_stats(erd):
    domain_counts = defaultdict(int)
    total_fields = 0
    total_rels = 0

    for obj_data in erd["objects"].values():
        domain = get_domain_short(obj_data)
        domain_counts[domain] += 1
        fields = obj_data.get("fields", {})
        total_fields += len(fields)
        for fdata in fields.values():
            if fdata.get("type") == "reference" or "refersTo" in fdata:
                total_rels += 1

    print(f"\nRevenue Cloud Data Model — v66.0 (Spring '26)\n")
    print(f"  Total Objects: {len(erd['objects'])}")
    print(f"  Total Fields:  {total_fields}")
    print(f"  Total Relationships: {total_rels}")
    print(f"  Domains: {len(domain_counts)}\n")

    print(f"  {'Domain':<30} {'Objects':>8}")
    print(f"  {'─' * 30} {'─' * 8}")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"  {domain:<30} {count:>8}")


def find_object(erd, name):
    """Case-insensitive object name lookup."""
    if name in erd["objects"]:
        return name
    name_lower = name.lower()
    for obj_name in erd["objects"]:
        if obj_name.lower() == name_lower:
            return obj_name
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()
    erd = load_erd()

    if command == "describe" and len(sys.argv) >= 3:
        cmd_describe(erd, sys.argv[2])
    elif command == "relationships" and len(sys.argv) >= 3:
        cmd_relationships(erd, sys.argv[2])
    elif command == "domain" and len(sys.argv) >= 3:
        cmd_domain(erd, " ".join(sys.argv[2:]))
    elif command == "path" and len(sys.argv) >= 4:
        cmd_path(erd, sys.argv[2], sys.argv[3])
    elif command == "search" and len(sys.argv) >= 3:
        cmd_search(erd, " ".join(sys.argv[2:]))
    elif command == "stats":
        cmd_stats(erd)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
