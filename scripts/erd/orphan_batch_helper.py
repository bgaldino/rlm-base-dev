#!/usr/bin/env python3
"""
Helper for orphan ERD field cleanup batch workflow.

Usage:
  # Prepare next batch input from current orphan state
  python scripts/erd/orphan_batch_helper.py prepare --batch 4 --size 20

  # Apply ownership findings (after researcher returns batch JSON merged into orphan-field-ownership.json)
  python scripts/erd/orphan_batch_helper.py apply --orphan-report docs/erds/orphan-candidates-after-batch3.md

  # Re-validate against both orgs and produce next orphan report
  python scripts/erd/orphan_batch_helper.py validate --batch 4

This script consolidates the manual steps used in batches 1-3 into one place.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO = Path(__file__).resolve().parent.parent.parent
ERD_DATA = REPO / "docs" / "erds" / "erd-data.json"
# Ownership tracking lives in .agents/ by default (intentionally untracked —
# accumulates iterative researcher findings during a cleanup campaign). The
# default path is configurable via --ownership-json so this script works on
# fresh clones and in CI without requiring the .agents/ artifacts to exist.
DEFAULT_OWNERSHIP_JSON = REPO / ".agents" / "artifacts" / "orphan-field-ownership.json"


def _load_ownership(path: Path) -> Tuple[dict, bool]:
    """Load the ownership JSON, returning (data, was_bootstrapped).

    If the file is missing, return an empty bootstrap structure rather
    than raising. Callers can decide whether to error or proceed with
    zero already-verified entities (which is the correct behavior on a
    fresh clone or when starting a new cleanup campaign).
    """
    if not path.exists():
        return {"by_entity": {}}, True
    with open(path) as f:
        return json.load(f), False


def parse_orphan_report(report_path: Path) -> Dict[str, Set[str]]:
    """Parse a cleanup_orphan_erd_fields.py report into {object: {field, ...}}."""
    with open(report_path) as f:
        report = f.read()
    sections = re.split(r"(?=^## )", report, flags=re.MULTILINE)
    orphans: Dict[str, Set[str]] = {}
    for sec in sections:
        if not sec.startswith("## "):
            continue
        cls_match = re.match(r"## (\w+) \(", sec)
        if not cls_match or cls_match.group(1) in ("pdf_artifact", "malformed", "Summary"):
            continue
        obj_sections = re.split(r"(?=^### )", sec, flags=re.MULTILINE)
        for ob_sec in obj_sections[1:]:
            head = re.match(r"### (\S+)", ob_sec)
            if not head:
                continue
            obj = head.group(1)
            fields = re.findall(r"- `([^`]+)`", ob_sec)
            if fields:
                orphans.setdefault(obj, set()).update(fields)
    return orphans


def _latest_orphan_report() -> Path:
    """Find the most recent orphan report by batch number."""
    batch_reports = []
    for p in REPO.glob("docs/erds/orphan-candidates-after-batch*.md"):
        m = re.search(r"batch(\d+)", p.name)
        if m:
            batch_reports.append((int(m.group(1)), p))
    if batch_reports:
        return max(batch_reports)[1]
    # Fall back to non-batched
    candidates = sorted(REPO.glob("docs/erds/orphan-candidates-after-*.md"))
    if candidates:
        return candidates[-1]
    return None


def cmd_prepare(args):
    """Prepare batch input JSON from current orphan state."""
    report_path = _latest_orphan_report()
    if report_path is None:
        print("ERROR: No orphan report found. Run cleanup_orphan_erd_fields.py first.")
        return 1
    print(f"Reading {report_path.name}...")
    orphans = parse_orphan_report(report_path)

    ownership_path = Path(args.ownership_json) if args.ownership_json else DEFAULT_OWNERSHIP_JSON
    own, bootstrapped = _load_ownership(ownership_path)
    if bootstrapped:
        print(f"NOTE: ownership file {ownership_path} not present — treating "
              f"all entities as unverified. Use --ownership-json to point at a "
              f"persisted file once the cleanup campaign accumulates findings.")
    already_verified = set(own["by_entity"].keys())

    # Load ERD for domain
    with open(ERD_DATA) as f:
        erd = json.load(f)

    # Build remaining list
    remaining = []
    for obj_name, fields in orphans.items():
        if obj_name in already_verified:
            continue
        domain = erd["objects"].get(obj_name, {}).get("domain", "Unknown")
        remaining.append({
            "object": obj_name,
            "domain": domain,
            "count": len(fields),
            "fields": sorted(fields),
        })
    remaining.sort(key=lambda x: -x["count"])
    next_batch = remaining[: args.size]

    output = {
        "total_remaining_objects": len(remaining),
        "total_remaining_fields": sum(r["count"] for r in remaining),
        "batch_number": args.batch,
        "batch_size": len(next_batch),
        "batch_coverage": sum(r["count"] for r in next_batch),
        "objects": next_batch,
    }
    # Default output dir lives under .agents/ (intentionally untracked); create
    # parents so this works on fresh clones where .agents/artifacts/ doesn't
    # exist yet. Override via --output-dir for CI or alternate staging.
    out_dir = Path(args.output_dir) if args.output_dir else REPO / ".agents" / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"orphan-fields-batch{args.batch}-input.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nRemaining unverified entities: {len(remaining)}")
    print(f"Remaining unverified fields: {output['total_remaining_fields']}")
    print(f"Batch {args.batch} coverage: {output['batch_coverage']} fields across {len(next_batch)} entities")
    try:
        rel = out_path.relative_to(REPO)
    except ValueError:
        rel = out_path
    print(f"\nWrote {rel}")
    if next_batch:
        print(f"\nFirst 10 entities:")
        for r in next_batch[:10]:
            print(f"  {r['object']} ({r['domain']}): {r['count']}")
    return 0


def cmd_apply(args):
    """Apply removals based on current ownership JSON state."""
    report_path = Path(args.orphan_report) if args.orphan_report else _latest_orphan_report()
    if report_path is None:
        print("ERROR: No orphan report found. Specify with --orphan-report.")
        return 1
    print(f"Reading orphan state from {report_path.name}")

    orphans = parse_orphan_report(report_path)

    ownership_path = Path(args.ownership_json) if args.ownership_json else DEFAULT_OWNERSHIP_JSON
    own, bootstrapped = _load_ownership(ownership_path)
    if bootstrapped:
        print(f"ERROR: ownership file {ownership_path} not present and `apply` "
              f"needs concrete findings to act on. Run `prepare` first, gather "
              f"researcher findings into the ownership JSON, then re-run "
              f"`apply --ownership-json <path>`.")
        return 1

    # Build removal set: ALL remove_all entities + C-classified fields from partial entities
    remove_set: Set[Tuple[str, str]] = set()
    for ent_name, ent_data in own["by_entity"].items():
        rec = ent_data.get("recommendation")
        if rec == "remove_all":
            for f in orphans.get(ent_name, set()):
                remove_set.add((ent_name, f))
        elif rec == "partial":
            for fname, fdata in ent_data.get("fields", {}).items():
                if fdata.get("classification") == "C":
                    if ent_name in orphans and fname in orphans[ent_name]:
                        remove_set.add((ent_name, fname))

    # Backup ERD. Suffix order keeps `.bak` LAST so the repo-wide `*.bak`
    # gitignore rule catches it. Earlier versions used `.bak.batchN` which
    # fell *outside* the `*.bak` glob and left untracked working-tree files
    # despite the PR documenting these as local-only artifacts. The
    # equivalent legacy pattern is covered defensively by the
    # `docs/erds/erd-data.json.bak*` entry in .gitignore.
    backup = ERD_DATA.with_suffix(f".json.batch{args.batch or 'X'}.bak")
    shutil.copy(ERD_DATA, backup)

    # Apply
    with open(ERD_DATA) as f:
        erd = json.load(f)

    removed = 0
    for obj_name, obj_data in erd["objects"].items():
        fields = obj_data.get("fields", {})
        if not isinstance(fields, dict):
            continue
        for fname in list(fields.keys()):
            if (obj_name, fname) in remove_set:
                del fields[fname]
                removed += 1

    rels = erd.get("relationships", [])
    new_rels = [r for r in rels if (r["source"], r.get("field", "")) not in remove_set]
    removed_rels = len(rels) - len(new_rels)
    erd["relationships"] = new_rels

    total_fields = sum(len(o.get("fields", {})) for o in erd["objects"].values())
    erd["stats"] = {
        "totalObjects": len(erd["objects"]),
        "totalRelationships": len(erd["relationships"]),
        "totalFields": total_fields,
        "domains": sorted(set(o.get("domain", "Unknown") for o in erd["objects"].values())),
    }

    with open(ERD_DATA, "w") as f:
        json.dump(erd, f, indent=2)

    print(f"\nApplied removals:")
    print(f"  Fields removed: {removed}")
    print(f"  Relationships removed: {removed_rels}")
    print(f"\nNew ERD totals:")
    print(f"  Objects: {erd['stats']['totalObjects']}")
    print(f"  Fields: {total_fields}")
    print(f"  Relationships: {len(new_rels)}")
    print(f"\nBackup at {backup.relative_to(REPO)}")
    return 0


def cmd_validate(args):
    """Run cleanup_orphan_erd_fields against both orgs to produce post-batch report."""
    report_out = REPO / "docs" / "erds" / f"orphan-candidates-after-batch{args.batch}.md"
    cmd = [
        "python3", str(REPO / "scripts" / "erd" / "cleanup_orphan_erd_fields.py"),
        "--orgs", "ent-r1,rlm-base__ent-sb0",
        "--dry-run",
        "--report", str(report_out),
        "--concurrency", "15",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout[-1000:] if result.stdout else "")
    if result.returncode != 0:
        print(result.stderr[-1000:] if result.stderr else "", file=sys.stderr)
    print(f"\nReport: {report_out.relative_to(REPO)}")

    # Also rebuild HTML. Earlier revisions discarded build_erds.py's exit
    # code, so a failed regeneration would leave a stale viewer behind while
    # the batch workflow happily reported success. Capture the result, log
    # stderr on failure, and propagate the worse of the two return codes so
    # callers (and CI) actually see the breakage.
    print("\nRegenerating HTML...")
    html_result = subprocess.run(
        ["python3", str(REPO / "scripts" / "erd" / "build_erds.py")],
        capture_output=True, text=True,
    )
    if html_result.returncode != 0:
        print(
            f"  [ERROR] build_erds.py exited {html_result.returncode}; "
            f"HTML viewer may be stale.",
            file=sys.stderr,
        )
        if html_result.stderr:
            print(html_result.stderr[-1000:], file=sys.stderr)
    return result.returncode or html_result.returncode


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prepare", help="Prepare next batch input JSON")
    p_prep.add_argument("--batch", type=int, required=True)
    p_prep.add_argument("--size", type=int, default=20)
    p_prep.add_argument("--ownership-json",
                        help=f"Path to ownership findings JSON "
                             f"(default: {DEFAULT_OWNERSHIP_JSON.relative_to(REPO)}; "
                             f"missing-file is non-fatal for prepare).")
    p_prep.add_argument("--output-dir",
                        help="Directory to write the batch input JSON into "
                             "(default: .agents/artifacts/; the directory is "
                             "auto-created so fresh clones work without "
                             "manually mkdir-ing .agents/artifacts/).")
    p_prep.set_defaults(func=cmd_prepare)

    p_apply = sub.add_parser("apply", help="Apply removals from current ownership JSON")
    p_apply.add_argument("--orphan-report", help="Path to orphan-candidates-*.md (default: latest)")
    p_apply.add_argument("--batch", type=int)
    p_apply.add_argument("--ownership-json",
                        help=f"Path to ownership findings JSON "
                             f"(default: {DEFAULT_OWNERSHIP_JSON.relative_to(REPO)}; "
                             f"required for apply — errors out if missing).")
    p_apply.set_defaults(func=cmd_apply)

    p_val = sub.add_parser("validate", help="Run validator + regenerate HTML")
    p_val.add_argument("--batch", type=int, required=True)
    p_val.set_defaults(func=cmd_validate)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
