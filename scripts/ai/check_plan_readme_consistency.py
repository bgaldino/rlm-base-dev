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
     For unambiguously live writable declarations, a valid `Pass` binds the count
     to that pass's source CSV. Other rows retain unordered CSV-count matching
     when files exist; Readonly/Delete/excluded declarations do not require a CSV.
  2. The **file-structure listing** — lines like `Foo.csv   # 315 records`.

Free-form prose and dated changelog/history counts are intentionally NOT parsed,
which keeps false positives low (the two locations above are where drift matters
and where the data is canonical).

A row can carry `<!-- readme-check: ignore -->` to skip every check on that row.
A README that intentionally tabulates only a subset of its export.json objects
can declare the rest with `<!-- readme-check: omit: Name1, Name2 -->` anywhere in
the file, to opt those names out of the missing-object WARN below.

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
import sys
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SFDMU_ROOT = os.path.join(REPO_ROOT, "datasets", "sfdmu")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sfdmu_export  # noqa: E402
import repo_paths  # noqa: E402
from validate_sfdmu_v5_datasets import _is_skip_segment, SFDMUValidator  # noqa: E402

# A README line carrying this marker is skipped by every per-row check, but the row's
# object still counts as "seen" for the missing-objects check below — an ignored row is
# still a row that lists the object, just one whose operation/externalId/count details
# aren't checked (round 15 of PR #406's review, pack 147: the two markers didn't compose
# before this — an ignored row was never yielded at all, so it never reached seen_objects
# either, and the missing-objects WARN fired for an object the README does in fact list).
IGNORE_MARKER = "readme-check: ignore"
# A whole-README marker declaring that named export.json objects are intentionally
# left out of the object table — e.g. `<!-- readme-check: omit: LegacyThing, Scratch -->`.
# The missing-objects check (below) has no existing row to attach IGNORE_MARKER to for
# an object that was never tabulated in the first place, so it needs its own opt-out;
# without one, pr_gate.py's --strict wiring (pack 147) turns this check's own documented
# "some READMEs legitimately tabulate a subset" case into an ungated-around gate failure.
OMIT_MARKER_RE = re.compile(r"<!--\s*readme-check:\s*omit:\s*([^>]*?)\s*-->")


def parse_omitted_objects(lines: list[str]) -> set[str]:
    """Union of object names named by every `readme-check: omit:` marker in the file.

    finditer(), not search(): two markers can share one line (e.g. pasted side by
    side rather than merged into one comma list) — search() would silently drop
    every marker after the first (round 20 of PR #406's review, pack 147)."""
    omitted: set[str] = set()
    for line in lines:
        for m in OMIT_MARKER_RE.finditer(line):
            omitted.update(name.strip() for name in m.group(1).split(",") if name.strip())
    return omitted


def csv_row_count(path: str) -> int:
    """Data-row count (excludes header), via the csv module so embedded newlines
    inside quoted fields don't inflate the count the way `wc -l` would. Streams
    the reader instead of materializing the file, so memory stays constant
    regardless of how large a plan's CSV grows."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        n = sum(1 for _ in csv.reader(fh))
    return max(0, n - 1)


def object_name(obj: dict) -> str:
    """The object's API name from its SOQL query — case-insensitive and subquery-aware.

    Delegates to the shared `sfdmu_export.extract_object_name` (todo pack 169) instead of the
    old literal `" FROM "` split, which matched only an uppercase, single-space-delimited
    keyword. A legal lowercase `from` (SOQL keywords are case-insensitive) fell through to
    `obj.get("name", "?")`, and an SFDMU object declaration has no `name` key, so it returned the
    literal `"?"`. That `"?"` then keyed `load_plan`'s output and — once written into a generated
    README table — was silently dropped by `parse_object_tables`' name regex (`^[A-Za-z]...`) on
    the next parse, so the object was never checked at all.

    A query with no parseable FROM (malformed — SFDMU identifies objects by their FROM clause)
    yields a visible `Unparseable(...)` sentinel rather than a silent `""`/`"?"`: it cannot match
    a README row's object-name regex, so the object surfaces through the missing-object check
    instead of vanishing. Mirrors the `Unresolvable(...)` operation sentinel in `load_plan`.
    """
    q = obj.get("query", "") or ""
    return sfdmu_export.extract_object_name(q) or f"Unparseable({q!r})"


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
    and 3 but not 2) would otherwise have its second variant mislabeled pass 2.

    `operation` is never "" or None: an absent key resolves to `"readonly"`
    (SFDMU's own class-field default); a present-but-unresolvable value (wrong
    type, out-of-range index, typo) resolves to a distinct `"Unresolvable(...)"`
    sentinel rather than being treated as absent or as Readonly — the two read
    identically to `_resolve_operation` alone, but SFDMU's own runtime does NOT
    treat them alike (`_is_live_writable`'s docstring): only a genuinely absent
    key gets the Readonly default; an unresolvable value is still written from
    source, so it must not be silently exempted from a missing-CSV check the way
    a real Readonly/Delete is."""
    if data is None:
        data = load_export_data(export_json)
    # Calls the validator's own centralized pass-normalization rule instead of re-deriving it
    # here as a fourth independent copy — this module already imports _is_skip_segment,
    # and generate_plan_readme.py already imports _is_js_truthy, from this same sibling
    # module for the identical drift-avoidance reason (three call sites disagreeing on
    # this exact rule is the failure _normalized_object_sets's own docstring documents).
    passes = list(enumerate((s.get("objects", []) for s in SFDMUValidator._normalized_object_sets(data)), start=1))
    out: dict[str, list[dict]] = {}
    for pass_no, objs in passes:
        for o in objs:
            name = object_name(o)
            if "operation" not in o:
                # ScriptObject.operation's own class-field default (ScriptObject.ts:162,
                # v5.8.0) — an ABSENT key only. _resolve_operation(None) can't tell "key
                # absent" apart from "key present with an unresolvable value" (both reach
                # it as None/non-resolvable), so that distinction has to be made here,
                # before calling it, not inside it.
                operation = "readonly"
            else:
                operation = SFDMUValidator._resolve_operation(o.get("operation"))
                if operation is None:
                    # Present but unresolvable (wrong type, out-of-range index, typo).
                    # _is_live_writable's docstring: SFDMU does NOT fall back to Readonly
                    # here — it leaves the raw value in place and still writes the object
                    # from source. A distinct non-empty sentinel (not "", not "readonly")
                    # keeps this from being silently read as absent or as Readonly by any
                    # downstream consumer — a missing CSV for it is a real Critical, not
                    # a false positive the Readonly/Delete exemption should swallow.
                    operation = f"Unresolvable({o.get('operation')!r})"
            out.setdefault(name, []).append({
                "pass": pass_no,
                "operation": operation,
                "externalId": str(o.get("externalId") or "").strip(),
                # JS truthiness, not plain Python bool() — SFDMU reads these the same
                # way it reads useSeparatedCSVFiles, where `[]`/`{}` are truthy in JS but
                # falsy in Python (validate_sfdmu_v5_datasets.py's _is_js_truthy).
                "deleteOldData": SFDMUValidator._is_js_truthy(o.get("deleteOldData")),
                "excluded": SFDMUValidator._is_js_truthy(o.get("excluded")),
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


def resolve_pass_csv(plan_dir: str, csv_idx: dict, use_separated: bool, name: str, pass_no: int,
                      count_cache: dict):
    """(count, path-relative-to-plan_dir) for the CSV at this pass's source location,
    mirroring validate_sfdmu_v5_datasets.py's _objects_owing_root_csv rule: pass 1
    always reads the root CSV regardless of an object-set-1/ override or the flag;
    pass N>1 reads objectset_source/object-set-N/<name>.csv only when
    useSeparatedCSVFiles is true and that file exists, else falls back to root.
    Restricting to the root CSV unconditionally (the prior behavior) emitted `—`
    for an object sourced only from an objectset_source override, e.g.
    procedure-plans' ProcedurePlanOption.csv (object-set-2 only, no root file).

    This locates files, not runtime reads: the generator also documents optional
    files for Readonly/Delete/excluded declarations. The checker imposes source
    requirements only on live writable variants.

    This is a deliberately simpler read-only echo of that rule for display purposes,
    not a call into the validator itself — commit 50d7e383 changed exactly this rule
    (excluding pass-1 overrides from the coverage set) after it had already shipped
    once, so re-check this docstring against `_objects_owing_root_csv`'s current
    docstring whenever that method changes.

    `count_cache`, keyed by absolute CSV path: an object declared in two passes with
    no per-pass override (common — most objects only override the root in one pass)
    resolves to the same physical file twice; without the cache that file is
    re-scanned by csv_row_count() once per pass instead of once per distinct file. The
    checker and generator share this resolver and each supply a cache."""
    by_abspath = {os.path.abspath(p): p for p in csv_idx.get(name, [])}
    # Override candidate first (only when it applies), then root — first match wins.
    candidates = []
    if pass_no > 1 and use_separated:
        candidates.append(os.path.join(plan_dir, "objectset_source", f"object-set-{pass_no}", f"{name}.csv"))
    candidates.append(os.path.join(plan_dir, f"{name}.csv"))
    for candidate in candidates:
        abs_candidate = os.path.abspath(candidate)
        if abs_candidate in by_abspath:
            p = by_abspath[abs_candidate]
            if p not in count_cache:
                count_cache[p] = csv_row_count(p)
            return count_cache[p], os.path.relpath(p, plan_dir)
    return None, None


# --- README parsing -------------------------------------------------------

FILE_STRUCT_RE = re.compile(r"([A-Za-z0-9_]+)\.csv\b.*?#\s*([\d,]+)\s+record", re.I)
LEADING_INT_RE = re.compile(r"(\d[\d,]*)")
# A record-count cell may carry an explicit `(org)` marker — e.g. `2 (org)` — declaring
# that the count is *org records* (a Readonly/Delete object resolved from the target org)
# rather than *file rows* loaded from a CSV. pack 151: the Records column meant two
# different things depending on the operation and was indistinguishable by sight; the
# marker disambiguates it and lets `check_plan_readme_consistency.py` skip file-count
# matching for the row.
ORG_COUNT_RE = re.compile(r"\(\s*org\s*\)", re.I)
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


PASS_RE = re.compile(r"^\s*(\d+)\s*$")


def parse_pass(text: str):
    """Strict single-integer parse for the Pass column. Deliberately not parse_int()
    (built for thousands-separated record counts, where a comma is part of the number):
    LEADING_INT_RE's `[\\d,]*` swallows a comma in a hand-written multi-pass cell like
    "1,3" too, misparsing it as 13 rather than treating it as unparseable — a plan with
    no pass 13 then fails `--strict` for a README that isn't actually wrong (round 19 of
    PR #406's review, pack 147)."""
    m = PASS_RE.match(text.strip())
    return int(m.group(1)) if m else None


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
                    "pass": col({"pass"}),
                    "operation": col({"operation"}),
                    "externalId": col({"external id", "externalid"}),
                    "records": col({"records"}),
                }
                j = i + 2
                while j < n and lines[j].strip().startswith("|"):
                    # An ignored row is still yielded (with ignored=True, no field data) so
                    # the caller can record its object as "seen" — the missing-object check
                    # (added round 14) otherwise WARNs that an ignored-but-listed object is
                    # "absent from the README object table", since the two markers used to
                    # not compose: IGNORE_MARKER used to skip the row entirely (never
                    # yielded), so it never reached seen_objects either (round 15 of PR
                    # #406's review, pack 147).
                    ignored = IGNORE_MARKER in lines[j]
                    cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    if ci["object"] is not None and ci["object"] < len(cells):
                        name = cells[ci["object"]].strip(" `*")
                        if re.match(r"^[A-Za-z][A-Za-z0-9_]+$", name):
                            yield {
                                "line": j + 1,
                                "object": name,
                                "ignored": ignored,
                                # Populated even when ignored (unlike operation/externalId/records
                                # below): the caller needs the row's own Pass claim to narrow which
                                # SPECIFIC pass an ignored row vouches for, not every pass of the name
                                # (round 20 of PR #406's review, pack 147 — an ignored row used to
                                # exempt the object's every pass via seen_any_pass regardless of which
                                # pass it actually named, reopening round 19's per-pass coverage gap).
                                "pass": cells[ci["pass"]] if ci["pass"] is not None and ci["pass"] < len(cells) else None,
                                "operation": None if ignored else (cells[ci["operation"]] if ci["operation"] is not None and ci["operation"] < len(cells) else None),
                                "externalId": None if ignored else (cells[ci["externalId"]].strip(" `") if ci["externalId"] is not None and ci["externalId"] < len(cells) else None),
                                "records": None if ignored else (cells[ci["records"]] if ci["records"] is not None and ci["records"] < len(cells) else None),
                            }
                    j += 1
                i = j
                continue
        i += 1


# --- checks ---------------------------------------------------------------

def count_variants(row: dict, variants: list[dict]) -> list[dict]:
    """Declarations identified by a row's operation and literal external ID.

    Pass alone is not declaration identity: a pass can contain both writable and
    optional declarations for one object. Prose keys cannot narrow that ambiguity.
    """
    if len(variants) <= 1:
        # Pass already identifies the declaration; metadata mismatches are
        # reported by the existing checks and must not suppress its count check.
        return variants
    operation = norm_op(row["operation"] or "")
    if operation:
        variants = [v for v in variants if norm_op(v["operation"]) == operation]
    external_id = (row["externalId"] or "").replace("`", "").strip()
    if external_id and KEYLIKE_RE.match(external_id):
        variants = [v for v in variants
                    if v["externalId"].replace("`", "").strip() == external_id]
    return variants


def check_count_claims(rel, claims_by_name, counts, errors, suffix="", reserved_counts=None):
    """Match each claimed record count to a DISTINCT actual CSV.

    An object can map to several CSVs — a Pass-1 source plus a smaller
    `objectset_source/object-set-N/` override is common. When those CSVs have
    *different* row counts (e.g. 9 and 5), each claim must consume a distinct
    count, so a README that lists 9/9 is flagged even though 9 is "present".
    When every CSV shares one count (or there's a single CSV), duplicate correct
    claims are fine only if no explicit pass has reserved a source. Under-listing
    (fewer claims than CSVs) is not an error.
    `reserved_counts` contains one count per distinct CSV already matched by
    explicit pass rows, so legacy rows cannot reuse those files.
    """
    for name, claims in claims_by_name.items():
        if name not in counts:
            continue  # phantom / no-CSV handled by the caller
        actual = counts[name]
        label = f"`{name}{suffix}`"
        reserved = (reserved_counts or {}).get(name, [])
        if len(set(actual)) > 1 or reserved:
            avail = Counter(actual)
            avail.subtract(reserved)
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
    data = load_export_data(export_json)
    plan = load_plan(export_json, data=data)
    use_separated = SFDMUValidator._is_js_truthy(data.get("useSeparatedCSVFiles"))
    csvs = csv_index(plan_dir)
    count_cache = {p: csv_row_count(p) for paths in csvs.values() for p in paths}
    counts = {name: [count_cache[p] for p in paths] for name, paths in csvs.items()}
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    rel = os.path.relpath(readme, REPO_ROOT)

    parsed_anything = False
    object_table_found = False

    # 1) Object-table rows
    seen_objects = set()
    # Coverage for the missing-object sweep (below) is tracked per-pass, not just per-name:
    # a row that names a SPECIFIC pass only vouches for that pass, not the object's other
    # passes — an object Upsert in pass 1 and excluded-Delete in pass 2, tabulated only via
    # its pass-2 row, used to silently exempt pass 1's real, unverified Upsert declaration
    # from every check just because SOME row for that name existed (round 19 of PR #406's
    # review, pack 147). `seen_any_pass` covers a row with no Pass cell (ANY-variant match,
    # deliberately ambiguous about which pass) and an IGNORE_MARKER row (no pass info at
    # all) — both vouch for every pass of that name, matching this check's pre-round-19
    # behavior for the common case of a single-pass or undisambiguated table.
    seen_any_pass: set[str] = set()
    seen_specific_passes: dict[str, set[int]] = {}
    table_count_claims: dict[str, list] = {}  # object -> [(line, claimed_count)]
    bound_sources: dict[str, dict[str, int]] = {}  # object -> {CSV path: row count}
    for row in parse_object_tables(lines):
        parsed_anything = True
        object_table_found = True
        name = row["object"]
        seen_objects.add(name)
        if row["ignored"]:
            # Narrow to the row's own Pass claim, same as a checked row below — an
            # ignored row for pass 2 of a multi-pass object must not vouch for the
            # object's other, unchecked passes too (round 20, pack 147). Fall back to
            # ANY-pass (prior behavior) only when the claim is absent or unresolvable;
            # an ignored row's content is never validated, so a bogus Pass claim here
            # doesn't warn the way a checked row's does.
            variants = plan.get(name, [])
            ignored_pass = parse_pass(row["pass"]) if row["pass"] else None
            if ignored_pass is not None and any(v["pass"] == ignored_pass for v in variants):
                seen_specific_passes.setdefault(name, set()).add(ignored_pass)
            else:
                seen_any_pass.add(name)
            continue
        ln = row["line"]
        variants = plan.get(name, [])
        in_plan = bool(variants)
        has_csv = name in counts
        # Narrow to the ONE variant for the row's own Pass cell when it resolves to a
        # pass the object actually has — otherwise fall back to every variant (the
        # pre-existing ANY-variant match, used only when the row has no Pass cell at
        # all). Without this, a multi-pass object whose operation differs per pass
        # (e.g. Upsert in Pass 1, Update in Pass 3 — common in this repo: BillingPolicy,
        # TaxPolicy, etc.) had its Pass column parsed but never compared: operation/
        # externalId matched against the union of every pass regardless of which pass
        # the row claimed, so two rows with their Pass numbers swapped (or corrupted by
        # a bad merge) validated cleanly (round 16 of PR #406's review, pack 147).
        #
        # A row THAT HAS a Pass cell but whose value matches no real pass (a typo, an
        # out-of-range number from a bad merge, or non-numeric garbage like "N/A") must
        # not fall back to the ANY-variant match either — that reintroduces the exact
        # false negative round 16 closed, just for a differently-shaped input. Report the
        # bogus Pass claim itself instead, and compare operation/externalId against
        # nothing (an empty `wants` never matches, so both checks correctly flag rather
        # than silently pass) — the fallback stays reserved for "no Pass cell", not "a
        # Pass cell with a bad value" (round 17).
        #
        # `has_pass_cell`, not `row_pass is None` alone, is what selects the fallback: a
        # non-numeric cell ("N/A") is truthy but parse_int() also returns None for it —
        # indistinguishable from "no Pass cell" without checking the raw text separately
        # (round 18 of PR #406's review, pack 147).
        has_pass_cell = bool(row["pass"])
        row_pass = parse_pass(row["pass"]) if has_pass_cell else None
        if not has_pass_cell:
            compare_variants = variants
            seen_any_pass.add(name)
        elif row_pass is None:
            compare_variants = []
            if in_plan:
                warns.append(f"{rel}:{ln} `{name}` Pass={row['pass']!r} — not a numeric pass "
                             f"(export.json passes: {sorted(v['pass'] for v in variants)})")
        else:
            compare_variants = [v for v in variants if v["pass"] == row_pass]
            if in_plan and not compare_variants:
                warns.append(f"{rel}:{ln} `{name}` Pass={row_pass} — not a pass this object has "
                             f"(export.json passes: {sorted(v['pass'] for v in variants)})")
            elif compare_variants:
                seen_specific_passes.setdefault(name, set()).add(row_pass)
        excluded = in_plan and all(v["excluded"] for v in compare_variants) if compare_variants else False

        # phantom object: a load-table row that isn't an export.json object is drift —
        # the plan won't load it, even if a leftover/supporting CSV happens to exist.
        if not in_plan:
            extra = "" if not has_csv else (
                f" (a {name}.csv exists but the plan doesn't reference it; "
                "add a `<!-- readme-check: ignore -->` marker on the row if intentional)"
            )
            errors.append(f"{rel}:{ln} object table lists `{name}` — not an object in export.json{extra}")
            continue

        # Shared by the operation/externalId checks below: `in_plan` is already
        # guaranteed True here (the `if not in_plan` block above always `continue`s),
        # so the only remaining gate is "not excluded, and the row's Pass claim
        # resolved to a comparable variant" (round 19 of PR #406's review, pack 147 —
        # was duplicated inline as `in_plan and not excluded and ... and compare_variants`
        # in both checks).
        checkable = not excluded and bool(compare_variants)

        # operation — matches if it agrees with ANY pass's operation (excluded objects are descriptive only)
        # load_plan() guarantees "operation" is never "" or None (see its docstring), so
        # `wants` is never empty here — an object with only the implicit Readonly default,
        # which used to fall out of the old `or ""` coercion and skip this check entirely,
        # is now compared against the README's claim like any other operation. Round 12's
        # fix (distinguishing absent from unresolvable) is what enabled this; no currently
        # tracked plan trips it, but a future README claiming a non-Readonly operation for
        # an object that declares none in export.json now correctly WARNs instead of
        # passing silently.
        if checkable and row["operation"]:
            # norm_op(), not a plain .lower(): an "Unresolvable(<raw value>)" sentinel's
            # parenthesized repr (e.g. "unresolvable(true)") never matches norm_op()'s
            # leading-word extraction from the README cell ("unresolvable") — generating a
            # README for such a plan and immediately re-checking it produced a spurious
            # WARN against the generator's own output, live-reproduced with a scratch
            # object carrying `"operation": true`. norm_op() on both sides compares only
            # the leading operation word either way, which is all the sentinel's own
            # comparison-worthy content ever was — the raw value in parens is diagnostic,
            # not something a hand-typed README cell could ever be expected to reproduce.
            wants = {norm_op(v["operation"]) for v in compare_variants}
            got = norm_op(row["operation"])
            if got and got not in wants:
                warns.append(f"{rel}:{ln} `{name}` operation README={row['operation'].strip()!r} export.json={sorted(wants)}")

        # externalId — matches ANY pass; only when the README cell looks like a literal key, not prose.
        # Both this and the operation check above require `compare_variants` non-empty: when the
        # row's Pass cell is bogus (checked above), `compare_variants` is already `[]` and the bogus
        # claim already has its own warn — comparing against an empty `wants` here would just add a
        # second, confusingly-worded "export.json=[]" warn for the same underlying problem.
        if checkable and row["externalId"] and KEYLIKE_RE.match(row["externalId"]):
            wants = {v["externalId"].replace("`", "").strip() for v in compare_variants if v["externalId"]}
            got = row["externalId"].replace("`", "").strip()
            if wants and got not in wants:
                warns.append(f"{rel}:{ln} `{name}` externalId README={got!r} export.json={sorted(wants)}")

        # A live writable Pass binds the count to its effective source CSV, using the
        # same resolver as README generation. Counts for two passes may legitimately
        # reuse one root CSV; a count from another pass's override cannot substitute.
        if row["records"] is not None:
            claimed = parse_int(row["records"])
            is_org_count = bool(ORG_COUNT_RE.search(row["records"]))
            # Which export.json declarations this row's displayed fields match. Unmatched
            # metadata cannot make a uniformly writable pass ambiguous about its source, so
            # fall back to the pass candidates then.
            matched = count_variants(row, compare_variants) or compare_variants
            if is_org_count:
                # `N (org)` is a HUMAN-supplied assertion that the count is org records
                # (target-org resolved), not file rows, so the row is exempt from CSV
                # matching (pack 151). The generator never mints one — offline it has no
                # org count and emits `—` — so an (org) marker is only ever hand-authored.
                # Valid ONLY when every matched declaration is source-free: if ANY matched
                # variant is live-writable, the row also vouches for that pass's loaded file
                # rows, and the marker would let a stale writable count skip validation
                # (PR #445 review, codex 4022218305). Checked whether or not a number is
                # present — a bare `(org)` / `— (org)` cell on a writable row must not slip
                # past just because parse_int() found no leading integer (copilot 4022218776).
                # Evaluate the guard over ALL declarations this row vouches for, NOT the
                # operation-narrowed `matched`: coverage is tracked per PASS (`seen_any_pass`
                # for a blank cell, `seen_specific_passes` for an explicit one), and
                # `compare_variants` is exactly that set — every pass for a blank cell, every
                # declaration in the selected pass otherwise. `count_variants` would narrow
                # `matched` to just the Readonly declaration when the Operation cell names it,
                # hiding a live-writable sibling — whether it lives in another pass (blank cell,
                # copilot 4022398078) or the SAME pass as a duplicate declaration (explicit
                # cell, copilot 4022437332) — so the writable declaration would get neither a
                # validated count nor a missing-row warning. `(org)` is accepted only when every
                # declaration the row covers is source-free.
                any_writable = bool(compare_variants) and any(
                    SFDMUValidator._is_live_writable(v) for v in compare_variants)
                if any_writable:
                    errors.append(f"{rel}:{ln} `{name}` record count README="
                                  f"{row['records'].strip()!r} carries an (org) marker on a "
                                  "writable declaration — (org) is only for a row whose every "
                                  "declaration is source-free (Readonly/Delete/excluded), a "
                                  "count of org records rather than file rows")
                # else: accepted as an org-record count; no CSV comparison.
            elif claimed is not None:
                # A live writable Pass binds the count to its effective source CSV. Source
                # binding needs the row's OWN resolved pass (resolve_pass_csv), so a
                # blank-Pass row cannot bind — it falls to the legacy `has_csv` branch.
                writable = (row_pass is not None and bool(matched) and all(
                    SFDMUValidator._is_live_writable(v) for v in matched))
                if writable:
                    actual, source = resolve_pass_csv(
                        plan_dir, csvs, use_separated, name, row_pass, count_cache)
                    if actual is None:
                        errors.append(f"{rel}:{ln} `{name}` Pass={row_pass} record count README={claimed} "
                                      "— no source CSV for this pass")
                    else:
                        # Source identity is independent of a correct count claim.
                        # Reserve each physical file once, even when multiple
                        # explicit passes legitimately read that same file.
                        bound_sources.setdefault(name, {})[source] = actual
                        if claimed != actual:
                            errors.append(f"{rel}:{ln} `{name}` Pass={row_pass} record count README={claimed} "
                                          f"actual CSV={actual} ({source})")
                elif has_csv:
                    # Optional rows emitted by the generator can share the source
                    # selected by an explicit pass, just like writable rows. Only
                    # accept that binding when the count actually matches; optional
                    # rows may also describe another CSV under the legacy contract.
                    actual, source = (resolve_pass_csv(
                        plan_dir, csvs, use_separated, name, row_pass, count_cache)
                        if row_pass is not None and matched else (None, None))
                    if actual is not None and claimed == actual:
                        bound_sources.setdefault(name, {})[source] = actual
                    elif (row_pass is not None and matched and actual is None
                          and set(counts[name]) == {claimed}):
                        # An explicit optional pass with no source can still
                        # describe the sole available file count (legacy behavior).
                        # It establishes no source identity to reserve. Blank-Pass
                        # rows never qualify for this optional-pass exception.
                        pass
                    else:
                        # No source is required for optional/org-count claims.
                        table_count_claims.setdefault(name, []).append((ln, claimed))

    # Unbound rows retain unordered, distinct-CSV matching.
    check_count_claims(rel, table_count_claims, counts, errors,
                       reserved_counts={name: list(sources.values())
                                        for name, sources in bound_sources.items()})

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
    # READMEs legitimately tabulate a subset — declare that intent with a
    # `<!-- readme-check: omit: Name1, Name2 -->` marker anywhere in the file rather
    # than relying on WARN never being gated; pr_gate.py runs this check --strict.
    if object_table_found:
        omitted = parse_omitted_objects(lines)
        for name, variants in plan.items():
            if name in omitted or name in seen_any_pass:
                continue
            # Per-pass, not per-name: a row naming one specific pass vouches for only that
            # pass (see seen_any_pass/seen_specific_passes above) — a multi-pass object's
            # OTHER, unlisted pass must still be caught even though the name itself was seen.
            missing = sorted(v["pass"] for v in variants
                              if not v["excluded"] and v["pass"] not in seen_specific_passes.get(name, ()))
            if not missing:
                continue
            if not seen_specific_passes.get(name):
                # No row at all, or only rows for passes not in `variants` (can't happen —
                # seen_specific_passes only ever adds a real match) — same wording as before
                # round 19, since there's no "another pass" row to distinguish this from.
                warns.append(f"{rel} object `{name}` is in export.json but absent from the README object table")
            else:
                warns.append(f"{rel} object `{name}` pass(es) {missing} are in export.json but absent from "
                              "the README object table (a row exists for another pass, but not these)")

    return errors, warns, parsed_anything


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
            # Uses _repo_relpath(), not a second hand-rolled case-fold comparison — this
            # site used to lowercase the whole path and re-derive relpath itself, a
            # second independent implementation of the exact case-insensitive-filesystem
            # concept _repo_relpath() already exists to centralize (round 17 of PR #406's
            # review, pack 147; _repo_relpath()'s own docstring already named this call
            # site as the thing it matches, but didn't actually call into it).
            if _repo_relpath(t).startswith(".."):
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
        # Calls validate_sfdmu_v5_datasets.py's own per-segment predicate rather than
        # hand-mirroring it (round 15 of PR #406's review, pack 147: the prior form —
        # `d not in _DISCOVERY_SKIP_DIRS and not d.endswith(".bak")` — was a second,
        # independent copy of _is_skip_segment's own two rules, free to drift from it).
        subdirs[:] = [d for d in subdirs if not _is_skip_segment(d)]
        if "export.json" not in files:
            continue
        (dirs if "README.md" in files else no_readme).append(root)
    return sorted(dirs), sorted(no_readme)


def _repo_relpath(p: str) -> str:
    """Like os.path.relpath(p, REPO_ROOT), but treats a REPO_ROOT prefix that
    differs from p only in case as the SAME directory — used by
    find_plan_dirs()'s explicit-target outside-repo guard (round 17: that call
    site used to re-derive this same case-fold logic independently rather than
    calling in) to admit such a path as "inside the repo" on a
    case-insensitive filesystem (macOS APFS). A plain relpath() on that
    admitted path compares components literally and returns a bogus,
    deeply-'../'-prefixed path (round 15 of PR #406's review, pack 147:
    live-reproduced — `git ls-files` then exits 128, "outside repository",
    which `tracked_paths()`'s `check=True` turns into an uncaught crash
    instead of the clean skip/report this script exists to give bad input).

    Consolidated into `repo_paths.repo_relpath` by todo pack 167 (with
    `tracked_paths` below and `diff_schemas.py`'s former copy); this stays a thin
    wrapper passing the module's own `REPO_ROOT`, which tests monkeypatch to a temp
    git repo, so that monkeypatch still governs the git call underneath."""
    return repo_paths.repo_relpath(p, REPO_ROOT)


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
    grepping doesn't turn up two same-named helpers with different shapes.

    Consolidated into `repo_paths.tracked_paths` by todo pack 167; this stays a thin
    wrapper passing the module's own (monkeypatchable) `REPO_ROOT`. The shared helper's
    `check=True` propagates here on purpose — a gate must never silently look like
    "nothing tracked" — the failure mode `diff_schemas.py` deliberately softens to an
    rglob walk + warning instead."""
    return repo_paths.tracked_paths(paths, REPO_ROOT)


def tracked_plan_dirs(dirs: list[str]) -> list[str]:
    """Subset of `dirs` (plan directories, not export.json paths) whose export.json is
    git-tracked, order preserved. Shared by this module's own no-README report and
    generate_plan_readme.py's --all-missing filter, so the "plan dir -> export.json ->
    tracked_paths()" idiom lives in one place rather than two call sites free to drift
    apart on how a plan dir maps to its tracked-ness check."""
    tracked_set = tracked_paths([os.path.join(d, "export.json") for d in dirs])
    return [d for d in dirs if os.path.join(d, "export.json") in tracked_set]


def build_arg_parser() -> argparse.ArgumentParser:
    """Split out of main() so a test can assert --strict is a real, defined flag by
    parsing with it (tests/test_pr_gate.py) instead of substring-matching --help
    output — which also contains the literal string "--strict" in this module's own
    docstring/Usage block regardless of whether the flag is actually declared below,
    making a --help-text probe a no-op against exactly the regression it exists to
    catch (round 13 of PR #406's review, pack 147: live-reproduced by removing the
    add_argument call and confirming --help still printed "--strict" with exit 0)."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help="Plan dirs to check (default: all under datasets/sfdmu)")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero on warnings too")
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()

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
    # total_err/total_warn were already folded in above (the no-README ERROR print), but
    # the "Checked N" count never included those plans — reads as if N audited READMEs
    # produced X errors, when a no-README plan contributed to X without being one of the
    # N (round 15 of PR #406's review, pack 147). Named separately so the count and the
    # errors it reports stay attributable to the same set of plans.
    summary = f"Checked {len(plan_dirs) - len(skipped)} plan README(s)"
    if tracked_no_readme:
        summary += f" + {len(tracked_no_readme)} tracked plan(s) with no README"
    print(f"{summary}: {total_err} error(s), {total_warn} warning(s)")
    if skipped:
        print(f"Skipped (no parseable object table / file listing): {', '.join(skipped)}")
    if total_err or (args.strict and total_warn):
        print("FAILED — fix the README to match export.json/CSVs (or add a `<!-- readme-check: ignore -->` marker for an intentional deviation).")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
