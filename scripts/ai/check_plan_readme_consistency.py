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
  python scripts/ai/check_plan_readme_consistency.py --strict   # all plans (pr_gate.py's own invocation)
  python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/qb/en-US/qb-pcm
  python scripts/ai/check_plan_readme_consistency.py            # WARN-only — exits 0 on drift a --strict run would fail
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SFDMU_ROOT = os.path.join(REPO_ROOT, "datasets", "sfdmu")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from validate_sfdmu_v5_datasets import _SKIP_SEGMENTS  # noqa: E402

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


def load_export_data(export_json: str) -> dict:
    """Raw parsed export.json. Split out of load_plan() so a caller that also
    needs a top-level flag (e.g. generate_plan_readme.py reading
    useSeparatedCSVFiles) can pass the already-parsed dict back into load_plan()
    instead of opening and re-parsing the same file a second time."""
    with open(export_json, encoding="utf-8") as fh:
        return json.load(fh)


def load_plan(export_json: str, data: dict | None = None) -> dict:
    """Return {object_name: [variant, ...]} where each variant is one pass's
    definition {pass, operation, externalId, deleteOldData, excluded}. An object
    that appears in several passes (e.g. Upsert in Pass 1, Update in Pass 2) keeps a
    variant per pass, so a README row matches if it agrees with ANY variant.

    `pass` is the object's actual 1-based objectSets index, not the occurrence
    count within `out[name]` — an object skipping a set (e.g. declared in sets 1
    and 3 but not 2) would otherwise have its second variant mislabeled pass 2."""
    if data is None:
        data = load_export_data(export_json)
    # Mirrors validate_sfdmu_v5_datasets.py's _normalized_object_sets: non-empty
    # objectSets wins outright over a sibling `objects` array — the real SFDMU
    # dominance rule, e.g. a leftover flat `objects` array from before a plan
    # migrated to objectSets. Checking `objects` truthy first (the prior order
    # here) read the dead array instead of the live objectSets whenever both were
    # non-empty.
    object_sets = data.get("objectSets") or []
    if object_sets:
        passes = list(enumerate((s.get("objects", []) for s in object_sets), start=1))
    else:
        passes = [(1, data.get("objects") or [])]
    out: dict[str, list[dict]] = {}
    for pass_no, objs in passes:
        for o in objs:
            name = object_name(o)
            out.setdefault(name, []).append({
                "pass": pass_no,
                # str() before .strip(): SFDMU tolerates a malformed plan declaring
                # operation/externalId as a boolean or number instead of a string
                # (validate_sfdmu_v5_datasets.py's _resolve_operation guards the
                # same shape) — `(True or "").strip()` raises AttributeError since
                # the `or` short-circuits to the truthy bool, not the string
                # fallback.
                "operation": str(o.get("operation") or "").strip(),
                "externalId": str(o.get("externalId") or "").strip(),
                "deleteOldData": bool(o.get("deleteOldData", False)),
                "excluded": bool(o.get("excluded", False)),
            })
    return out


# SFDMU runtime-artifact dirs — gitignored (datasets/**/source/**, target/**, logs).
# They hold per-run snapshots (e.g. Product2_source.csv, *_insert_target.csv) that
# must not feed into counts; pruning them keeps results deterministic across working
# trees and matches a clean CI checkout regardless of whether SFDMU has been run.
RUNTIME_DIRS = {"source", "target", "logs"}
# Gitignored SFDMU report files that would otherwise add spurious index entries.
SKIP_CSV = {"CSVIssuesReport.csv", "MissingParentRecordsReport.csv"}


def csv_index(plan_dir: str) -> dict[str, list[str]]:
    """basename (without .csv) -> [absolute paths] for the plan's source CSVs.
    SFDMU runtime dirs (source/target/logs) and report CSVs are pruned during the
    walk so counts don't depend on local, gitignored working-tree artifacts."""
    idx: dict[str, list[str]] = {}
    for root, dirs, files in os.walk(plan_dir):
        dirs[:] = [d for d in dirs if d not in RUNTIME_DIRS and not d.startswith(".")]
        for f in files:
            if f.endswith(".csv") and f not in SKIP_CSV:
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
    """Yield dict rows from the canonical *load* table(s): any markdown table that
    has BOTH an 'Object' column and an 'Operation' column. Requiring 'Operation'
    excludes dated "Schema Analysis" / "ExternalId Assessment" tables (which have
    Object + External ID but no Operation), so they aren't mis-parsed as the object
    table. Other columns (External ID, Records, 'v5 Notes', …) are optional, and
    column lookups are by header name so extra columns don't break parsing."""
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

def check_count_claims(rel, claims_by_name, counts, errors, suffix=""):
    """Match each claimed record count to a DISTINCT actual CSV.

    An object can map to several CSVs — a Pass-1 source plus a smaller
    `objectset_source/object-set-N/` override is common. When those CSVs have
    *different* row counts (e.g. 9 and 5), each claim must consume a distinct
    count, so a README that lists 9/9 is flagged even though 9 is "present".
    When every CSV shares one count (or there's a single CSV), duplicate correct
    claims are fine and under-listing (fewer claims than CSVs) is not an error.
    """
    for name, claims in claims_by_name.items():
        if name not in counts:
            continue  # phantom / no-CSV handled by the caller
        actual = counts[name]
        label = f"`{name}{suffix}`"
        if len(set(actual)) > 1:
            avail = Counter(actual)
            for ln, claimed in claims:
                if avail.get(claimed, 0) > 0:
                    avail[claimed] -= 1
                else:
                    errors.append(f"{rel}:{ln} {label} record count README={claimed} — no un-consumed CSV matches; actual CSVs={sorted(actual)}")
        else:
            val = actual[0]
            for ln, claimed in claims:
                if claimed != val:
                    errors.append(f"{rel}:{ln} {label} record count README={claimed} actual CSV={val}")


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
    table_count_claims: dict[str, list] = {}  # object -> [(line, claimed_count)]
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

        # phantom object: a load-table row that isn't an export.json object is drift —
        # the plan won't load it, even if a leftover/supporting CSV happens to exist.
        if not in_plan:
            extra = "" if not has_csv else (
                f" (a {name}.csv exists but the plan doesn't reference it; "
                "add a `<!-- readme-check: ignore -->` marker on the row if intentional)"
            )
            errors.append(f"{rel}:{ln} object table lists `{name}` — not an object in export.json{extra}")
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

        # record count — collected here, matched per-CSV after the loop (handles
        # multi-CSV objects, e.g. a Pass-1 source + a smaller objectset override)
        if row["records"] is not None and has_csv:
            claimed = parse_int(row["records"])
            if claimed is not None:
                table_count_claims.setdefault(name, []).append((ln, claimed))

    # object-table record counts: each claim must match a distinct actual CSV
    check_count_claims(rel, table_count_claims, counts, errors)

    # 2) File-structure CSV listings  (Foo.csv  # N records)
    fs_claims: dict[str, list] = {}
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
        fs_claims.setdefault(name, []).append((idx_, claimed))
    check_count_claims(rel, fs_claims, counts, errors, suffix=".csv")

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


# Reuses validate_sfdmu_v5_datasets.py's own _SKIP_SEGMENTS rather than a second,
# independent copy of it — a hand-copied subset (this used to be just {"test"}) can
# only drift from the canonical list as it grows. datasets/sfdmu/test/ itself is
# entirely gitignored, developer-local scratch (zero files git-tracked, confirmed via
# `git ls-files datasets/sfdmu/test`); without skipping it, --strict (added by this
# same change to pr_gate.py's invocation) fails on whatever stale scratch plans a
# developer happens to have lying around locally, unrelated to anything that ships.
_DISCOVERY_SKIP_DIRS = set(_SKIP_SEGMENTS)


def find_plan_dirs(targets: list[str]) -> tuple[list[str], list[str]]:
    """Discover on export.json ALONE, so a plan missing its README is reported by
    name (second return value) instead of never entering the walk — the gate used
    to require both files to co-exist before a plan was even visible, which let a
    plan with no README pass by absence rather than by being audited."""
    if targets:
        dirs, no_readme = [], []
        for t in targets:
            t = os.path.abspath(t)
            # A target outside REPO_ROOT (typo, sibling checkout) would otherwise reach
            # tracked_paths() as a "../.."-relative pathspec and crash with a raw
            # subprocess.CalledProcessError from `git ls-files` ("fatal: ... is outside
            # repository") instead of the same clean skip message bad input gets below.
            if os.path.relpath(t, REPO_ROOT).startswith(".."):
                print(f"skip {t} — outside the repo", file=sys.stderr)
            elif not os.path.isfile(os.path.join(t, "export.json")):
                print(f"skip {os.path.relpath(t, REPO_ROOT)} — no export.json", file=sys.stderr)
            elif os.path.isfile(os.path.join(t, "README.md")):
                dirs.append(t)
            else:
                no_readme.append(t)
        return dirs, no_readme
    dirs, no_readme = [], []
    for root, subdirs, files in os.walk(SFDMU_ROOT):
        subdirs[:] = [d for d in subdirs if d not in _DISCOVERY_SKIP_DIRS]
        if "export.json" not in files:
            continue
        (dirs if "README.md" in files else no_readme).append(root)
    return sorted(dirs), sorted(no_readme)


def tracked_paths(paths: list[str]) -> set[str]:
    """Absolute paths of `paths` that are REPO-tracked — one batched `git ls-files`
    call for all candidates, mirroring generate_plan_readme.py's --all-missing
    approach, instead of spawning one `git ls-files --error-unmatch` subprocess per
    candidate (the prior is_tracked() shape, ~30+ processes on this repo's tree).
    A README is required for every tracked plan — not for local/gitignored scratch
    dirs (e.g. datasets/sfdmu/test/) that happen to carry an export.json.

    Deliberately not bump_api_version.py's tracked_files() (a cached, whole-repo,
    repo-relative frozenset) — this takes a handful of specific candidate paths and
    returns which of THOSE are tracked, not a full-repo inventory; the two scripts
    are unrelated concern domains and importing across them for a few-item lookup
    isn't worth the coupling. Named differently (tracked_paths, not tracked_files) so
    grepping doesn't turn up two same-named helpers with different shapes."""
    if not paths:
        return set()
    rels = [os.path.relpath(p, REPO_ROOT) for p in paths]
    # check=True: a git failure (e.g. run outside a checkout) must not silently yield
    # empty stdout, which would misclassify every tracked README-less plan as
    # untracked/optional — the exact silent-pass-by-absence defect this script exists
    # to close. generate_plan_readme.py has no git call of its own — it imports and
    # calls this same function, so there is nothing else to keep in sync here.
    # -z: git's default core.quotepath=true C-quotes/octal-escapes non-ASCII (or
    # otherwise "unusual") bytes in plain `ls-files` output (e.g. a tracked café/
    # export.json is echoed as "caf\303\251/export.json"), which would never
    # string-match the plain relpath below and misclassify a genuinely tracked path
    # as untracked — the same silent-pass-by-absence defect this script exists to
    # close, one level down. -z disables quoting and NUL-delimits instead.
    r = subprocess.run(["git", "ls-files", "-z", "--"] + rels, cwd=REPO_ROOT,
                        capture_output=True, text=True, check=True)
    # Compare case-folded, and return the CALLER's own paths rather than reconstructing
    # from git's stdout: on a case-insensitive filesystem (macOS's default APFS), a repo
    # with core.ignorecase set (the git-init default there) matches a pathspec
    # case-insensitively but echoes it back in the INDEX's casing, which can differ from
    # the caller's/disk's casing after a case-only rename the index missed. Exact-string
    # reconstruction would then silently miss a real match.
    tracked_rel_lower = {line.lower() for line in r.stdout.split("\0") if line}
    return {p for p, rel in zip(paths, rels) if rel.lower() in tracked_rel_lower}


def tracked_plan_dirs(dirs: list[str]) -> list[str]:
    """Subset of `dirs` (plan directories, not export.json paths) whose export.json is
    git-tracked, order preserved. Shared by this module's own no-README report and
    generate_plan_readme.py's --all-missing filter, so the "plan dir -> export.json ->
    tracked_paths()" idiom lives in one place rather than two call sites free to drift
    apart on how a plan dir maps to its tracked-ness check."""
    tracked_set = tracked_paths([os.path.join(d, "export.json") for d in dirs])
    return [d for d in dirs if os.path.join(d, "export.json") in tracked_set]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help="Plan dirs to check (default: all under datasets/sfdmu)")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero on warnings too")
    args = ap.parse_args()

    plan_dirs, no_readme = find_plan_dirs(args.targets)
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

    # A plan with export.json and no README used to never enter the walk above, so
    # "0 errors" could mean "nothing drifted" or "the plan was never looked at" —
    # indistinguishable. Report it by name; a tracked plan missing a README is an
    # ERROR (a README is required for every tracked plan), a local/untracked scratch
    # dir is a note only.
    tracked_no_readme = tracked_plan_dirs(no_readme)
    tracked_no_readme_set = set(tracked_no_readme)
    untracked_no_readme = [d for d in no_readme if d not in tracked_no_readme_set]
    if tracked_no_readme:
        rels = ", ".join(os.path.relpath(d, REPO_ROOT) for d in tracked_no_readme)
        print(f"\nERROR  {len(tracked_no_readme)} tracked plan(s) have no README — not audited: {rels}")
        total_err += len(tracked_no_readme)
    if untracked_no_readme:
        rels = ", ".join(os.path.relpath(d, REPO_ROOT) for d in untracked_no_readme)
        print(f"\n(untracked, no README, not required: {rels})")

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
