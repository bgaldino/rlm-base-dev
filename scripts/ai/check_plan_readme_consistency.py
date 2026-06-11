#!/usr/bin/env python3
"""Check SFDMU plan READMEs against their export.json + CSVs for drift.

The repo's doc-consistency rule says a plan's README "must match the plan's
export.json". That match was *manual* and drifted badly (record counts, phantom
objects, wrong operations) as the QB datasets grew. This script makes the match
mechanically checkable so drift is caught before it merges, not in a later audit.

For each plan directory (one containing `export.json` + `README.md`) it derives
ground truth from export.json + the CSVs and compares it to two structured
locations in the README:

  1. The **object table** — the canonical *load* table: a markdown table with an
     `Object` column AND an `Operation` column (other columns such as `External ID`,
     `Records`, `v5 Notes` are optional). Tables that lack an `Operation` column —
     e.g. dated "Schema Analysis" / "ExternalId Assessment" tables — are deliberately
     NOT treated as the object table, so a README whose only object-style table has
     no `Operation` column is reported as "Skipped".
  2. The **file-structure listing** — lines like `Foo.csv   # 315 records`.

Free-form prose and dated changelog/history counts are intentionally NOT parsed,
which keeps false positives low (the two locations above are where drift matters
and where the data is canonical).

Findings:
  ERROR  record-count mismatch; README references an object/CSV absent from the plan
  WARN   operation / externalId mismatch; a non-excluded plan object missing from the
         README object table (these are more parse-sensitive)

Exit code is non-zero if any ERROR is found, so this can gate a PR. WARN-only
runs exit 0. Use `--strict` to also fail on warnings.

Usage:
  python scripts/ai/check_plan_readme_consistency.py            # all plans
  python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/qb/en-US/qb-pcm
  python scripts/ai/check_plan_readme_consistency.py --strict
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SFDMU_ROOT = os.path.join(REPO_ROOT, "datasets", "sfdmu")

# A README line carrying this marker is skipped by every check.
IGNORE_MARKER = "readme-check: ignore"


def csv_row_count(path: str) -> int:
    """Data-row count (excludes header), via the csv module so embedded newlines
    inside quoted fields don't inflate the count the way `wc -l` would. Streams
    the reader instead of materializing the file, so memory stays constant
    regardless of how large a plan's CSV grows."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        n = sum(1 for _ in csv.reader(fh))
    return max(0, n - 1)


def object_name(obj: dict) -> str:
    q = obj.get("query", "") or ""
    if " FROM " in q:
        return q.split(" FROM ", 1)[1].split()[0]
    return obj.get("name", "?")


def load_plan(export_json: str) -> dict:
    """Return {object_name: [variant, ...]} where each variant is one pass's
    definition {operation, externalId, deleteOldData, excluded}. An object that
    appears in several passes (e.g. Upsert in Pass 1, Update in Pass 2) keeps a
    variant per pass, so a README row matches if it agrees with ANY variant."""
    with open(export_json, encoding="utf-8") as fh:
        data = json.load(fh)
    objs = data.get("objects") or [
        o for s in data.get("objectSets", []) for o in s.get("objects", [])
    ]
    out: dict[str, list[dict]] = {}
    for o in objs:
        name = object_name(o)
        out.setdefault(name, []).append({
            "operation": (o.get("operation") or "").strip(),
            "externalId": (o.get("externalId") or "").strip(),
            "deleteOldData": bool(o.get("deleteOldData", False)),
            "excluded": bool(o.get("excluded", False)),
        })
    return out


def csv_index(plan_dir: str) -> dict[str, list[str]]:
    """basename (without .csv) -> [absolute paths] across the plan tree."""
    idx: dict[str, list[str]] = {}
    for root, _dirs, files in os.walk(plan_dir):
        for f in files:
            if f.endswith(".csv"):
                idx.setdefault(f[:-4], []).append(os.path.join(root, f))
    return idx


# --- README parsing -------------------------------------------------------

FILE_STRUCT_RE = re.compile(r"([A-Za-z0-9_]+)\.csv\b.*?#\s*([\d,]+)\s+record", re.I)
LEADING_INT_RE = re.compile(r"(\d[\d,]*)")
# A cell that looks like a real externalId key (single field, or `;`/`.`-joined),
# as opposed to prose like "4-field composite".
KEYLIKE_RE = re.compile(r"^[A-Za-z0-9_.;]+$")


def norm_op(text: str) -> str:
    """First operation word, lowercased: 'Insert (+deleteOldData)' -> 'insert'."""
    m = re.match(r"[`*]*([A-Za-z]+)", text.strip())
    return m.group(1).lower() if m else ""


def parse_int(text: str):
    m = LEADING_INT_RE.search(text)
    return int(m.group(1).replace(",", "")) if m else None


def parse_object_tables(lines: list[str]):
    """Yield dict rows from any markdown table that has an 'Object' column plus at
    least one of Operation / External ID / Records. Column lookups are by header
    name so extra columns (e.g. 'v5 Notes') don't break parsing."""
    i = 0
    n = len(lines)
    while i < n - 1:
        header = lines[i]
        sep = lines[i + 1]
        if header.strip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", sep):
            cols = [c.strip().lower() for c in header.strip().strip("|").split("|")]
            has_obj = any(c == "object" for c in cols)
            # Require an Operation column to identify the canonical *load* table.
            # This excludes dated "Schema Analysis" / "ExternalId Assessment" /
            # cross-object-dependency tables, which describe state rather than the plan.
            has_operation = any(c == "operation" for c in cols)
            if has_obj and has_operation:
                def col(name_options):
                    for idx_, c in enumerate(cols):
                        if c in name_options:
                            return idx_
                    return None
                ci = {
                    "object": col({"object"}),
                    "operation": col({"operation"}),
                    "externalId": col({"external id", "externalid"}),
                    "records": col({"records"}),
                }
                j = i + 2
                while j < n and lines[j].strip().startswith("|"):
                    if IGNORE_MARKER in lines[j]:
                        j += 1
                        continue
                    cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    if ci["object"] is not None and ci["object"] < len(cells):
                        name = cells[ci["object"]].strip(" `*")
                        if re.match(r"^[A-Za-z][A-Za-z0-9_]+$", name):
                            yield {
                                "line": j + 1,
                                "object": name,
                                "operation": cells[ci["operation"]] if ci["operation"] is not None and ci["operation"] < len(cells) else None,
                                "externalId": cells[ci["externalId"]].strip(" `") if ci["externalId"] is not None and ci["externalId"] < len(cells) else None,
                                "records": cells[ci["records"]] if ci["records"] is not None and ci["records"] < len(cells) else None,
                            }
                    j += 1
                i = j
                continue
        i += 1


# --- checks ---------------------------------------------------------------

def check_plan(plan_dir: str):
    """Return (errors, warns, checked_anything) for one plan dir."""
    errors: list[str] = []
    warns: list[str] = []
    export_json = os.path.join(plan_dir, "export.json")
    readme = os.path.join(plan_dir, "README.md")
    plan = load_plan(export_json)
    csvs = csv_index(plan_dir)
    counts = {name: [csv_row_count(p) for p in paths] for name, paths in csvs.items()}
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    rel = os.path.relpath(readme, REPO_ROOT)

    parsed_anything = False
    object_table_found = False

    # 1) Object-table rows
    seen_objects = set()
    for row in parse_object_tables(lines):
        parsed_anything = True
        object_table_found = True
        name = row["object"]
        seen_objects.add(name)
        ln = row["line"]
        variants = plan.get(name, [])
        in_plan = bool(variants)
        has_csv = name in counts
        excluded = in_plan and all(v["excluded"] for v in variants)

        # phantom object: named in the table but not an export.json object and no CSV
        if not in_plan and not has_csv:
            errors.append(f"{rel}:{ln} object table lists `{name}` — not in export.json and no {name}.csv on disk")
            continue

        # operation — matches if it agrees with ANY pass's operation (excluded objects are descriptive only)
        if in_plan and not excluded and row["operation"]:
            wants = {(v["operation"] or "").lower() for v in variants if v["operation"]}
            got = norm_op(row["operation"])
            if wants and got and got not in wants:
                warns.append(f"{rel}:{ln} `{name}` operation README={row['operation'].strip()!r} export.json={sorted(wants)}")

        # externalId — matches ANY pass; only when the README cell looks like a literal key, not prose
        if in_plan and not excluded and row["externalId"] and KEYLIKE_RE.match(row["externalId"]):
            wants = {v["externalId"].replace("`", "").strip() for v in variants if v["externalId"]}
            got = row["externalId"].replace("`", "").strip()
            if wants and got not in wants:
                warns.append(f"{rel}:{ln} `{name}` externalId README={got!r} export.json={sorted(wants)}")

        # record count — only when the object maps to a single CSV (avoid multi-pass ambiguity)
        if row["records"] is not None and has_csv:
            claimed = parse_int(row["records"])
            actual_set = set(counts[name])
            if claimed is not None and claimed not in actual_set:
                if len(actual_set) == 1:
                    errors.append(f"{rel}:{ln} `{name}` record count README={claimed} actual CSV={counts[name][0]}")
                # multi-CSV (multi-pass): skip to avoid false positives

    # 2) File-structure CSV listings  (Foo.csv  # N records)
    for idx_, line in enumerate(lines, start=1):
        if IGNORE_MARKER in line:
            continue
        m = FILE_STRUCT_RE.search(line)
        if not m:
            continue
        parsed_anything = True
        name, claimed_s = m.group(1), m.group(2)
        claimed = int(claimed_s.replace(",", ""))
        if name not in counts:
            errors.append(f"{rel}:{idx_} file-structure lists `{name}.csv` — no such CSV on disk")
            continue
        if claimed not in set(counts[name]):
            actual = counts[name][0] if len(counts[name]) == 1 else counts[name]
            errors.append(f"{rel}:{idx_} `{name}.csv` record count README={claimed} actual={actual}")

    # 3) Missing objects — a non-excluded export.json object that the README's object
    # table never lists (so a README can't silently omit objects and still pass).
    # Only enforced when an object table exists, and reported as WARN since some
    # READMEs legitimately tabulate a subset.
    if object_table_found:
        for name, variants in plan.items():
            if all(v["excluded"] for v in variants):
                continue
            if name not in seen_objects:
                warns.append(f"{rel} object `{name}` is in export.json but absent from the README object table")

    return errors, warns, parsed_anything


def find_plan_dirs(targets: list[str]) -> list[str]:
    if targets:
        dirs = []
        for t in targets:
            t = os.path.abspath(t)
            if os.path.isfile(os.path.join(t, "export.json")) and os.path.isfile(os.path.join(t, "README.md")):
                dirs.append(t)
            else:
                print(f"skip {os.path.relpath(t, REPO_ROOT)} — no export.json + README.md", file=sys.stderr)
        return dirs
    dirs = []
    for root, _d, files in os.walk(SFDMU_ROOT):
        if "export.json" in files and "README.md" in files:
            dirs.append(root)
    return sorted(dirs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help="Plan dirs to check (default: all under datasets/sfdmu)")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero on warnings too")
    args = ap.parse_args()

    plan_dirs = find_plan_dirs(args.targets)
    total_err = total_warn = 0
    skipped = []
    for d in plan_dirs:
        errors, warns, parsed = check_plan(d)
        rel = os.path.relpath(d, REPO_ROOT)
        if not parsed:
            skipped.append(rel)
            continue
        if errors or warns:
            print(f"\n### {rel}")
            for e in errors:
                print(f"  ERROR  {e}")
            for w in warns:
                print(f"  WARN   {w}")
        else:
            print(f"### OK   {rel}")
        total_err += len(errors)
        total_warn += len(warns)

    print(f"\n{'='*60}")
    print(f"Checked {len(plan_dirs) - len(skipped)} plan READMEs: {total_err} error(s), {total_warn} warning(s)")
    if skipped:
        print(f"Skipped (no parseable object table / file listing): {', '.join(skipped)}")
    if total_err or (args.strict and total_warn):
        print("FAILED — fix the README to match export.json/CSVs (or add a `<!-- readme-check: ignore -->` marker for an intentional deviation).")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
