#!/usr/bin/env python3
"""Check the SFDMU data shapes for two layering hazards (todo 325).

Two checks, both read-only and offline:

* `lookup` (gating): a `$$` lookup-reference column that SFDMU 5.8.0 can't resolve. A column
  such as `Pricebook2.$$Name$IsStandard` resolves only when its parts are exactly the parent
  object's `externalId` in the same pass; that shape loads correctly on built orgs (qb-pricing,
  qb-rates, qb-billing). It fails when the reference is **self-referential** (the parent is the
  same object, as in `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`), or when the plan's
  declaration of the parent keys it differently. This is the live part of "Bug 4"
  (AGENTS.md → SFDMU v5 bugs). A parent the pass doesn't declare is reported too: SFDMU sends
  a lookup whose parent isn't in the same pass as null. An `excluded` parent doesn't count.
  A column with no values in any row is skipped, because it never asks SFDMU to resolve
  anything.

* `shared` (gating on change): a record that more than one data shape writes, with different
  final values.
  The shapes are qb, q3 and mfg (qb/ja is a locale overlay on qb and counts as qb). Whichever
  shape loads last wins on that field, so loading a second shape into one org changes the
  first one's data. See docs/analysis/sfdmu-data-shape-layering.md → Shape ownership. These
  are known and tracked; the check keeps the list current and fails only on a conflict that
  isn't in `KNOWN_SHARED_CONFLICTS`, or on a listed one that no longer conflicts, so a new one
  gets a decision instead of slipping in. A plan's value for a field is the one its last pass
  writes, so Draft-then-Active staging inside one plan isn't a conflict.

What a write is: every declaration that isn't `excluded`, `Readonly` or `Delete`, read from
the CSV SFDMU would read for that pass (the `objectset_source/object-set-N/` override for
pass 2+ when `useSeparatedCSVFiles` is set, the plan root otherwise). Rows are keyed on the
declaration's `externalId`, using its `$$` column for a composite. `#N/A` and blank are both
null. `$$` columns, `Id`, and the key's own fields aren't compared; single-field lookup
columns (`CostBook.Name`) are.

Usage:
    python scripts/ai/check_sfdmu_layering.py              # both checks
    python scripts/ai/check_sfdmu_layering.py --list       # also print every shared conflict

Exit codes: 0 = clean · 1 = findings · 2 = tool error.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import sfdmu_export  # noqa: E402

SFDMU = REPO / "datasets" / "sfdmu"
# Shape roots, relative to datasets/sfdmu. qb/ja is folded into qb: it is a locale overlay that
# reuses qb's keys, so its differences from qb/en-US are translations, not a second shape.
SHAPE_ROOTS = {"qb/en-US": "qb", "qb/ja": "qb", "q3/en-US": "q3", "mfg/en-US": "mfg"}
NULL_TOKENS = frozenset({"", "#n/a", "null", "undefined"})
NOT_WRITTEN = frozenset({"readonly", "delete"})

# Lookup relationship names whose parent object isn't spelled the same as the relationship.
RELATIONSHIP_PARENT = {
    "ParentGroup": "ProductComponentGroup",
    "OverriddenProductAttributeDefinition": "ProductAttributeDefinition",
    "Pricebook": "Pricebook2",
    "ParentElement": "OmniProcessElement",
    "ActiveVersion": "AssessmentQuestionVersion",
    "ChildSellingModel": "ProductSellingModel",
    "ParentSellingModel": "ProductSellingModel",
    "ParentProductSellingModel": "ProductSellingModel",
    "RootProductSellingModel": "ProductSellingModel",
}

# `$$` lookup columns that don't resolve today, in plans no current build loads. Each is
# scoped to the exact plan, CSV and column, so a new one anywhere still fails. Remove an entry
# when its plan is converted.
KNOWN_UNRESOLVED_LOOKUPS = {
    # mfg guided selling (todo 111): self-referential and mis-keyed OmniProcess and
    # AssessmentQuestion references; the plan still uses Insert + deleteOldData.
    ("mfg/en-US/mfg-guidedselling", "AssessmentQuestion.csv", "ActiveVersion"),
    ("mfg/en-US/mfg-guidedselling", "OmniProcessAsmtQuestionVer.csv", "AssessmentQuestionVersion"),
    ("mfg/en-US/mfg-guidedselling", "OmniProcessElement.csv", "ParentElement"),
    # mfg pcm (todo 111): self-referential attribute-definition override.
    ("mfg/en-US/mfg-pcm", "ProductAttributeDefinition.csv", "OverriddenProductAttributeDefinition"),
    # qb/ja refresh (todo 212): self-referential ProductComponentGroup parent.
    ("qb/ja/qb-pcm", "ProductComponentGroup.csv", "ParentGroup"),
    # The pass-2 Update of BillingTreatmentItem carries the parent as a `$$` column, but pass 2
    # declares no BillingTreatment and BillingTreatmentId is create-only (updateable false), so
    # an Update never sends it. Pass 1 sets it through the single-field `BillingTreatment.Name`:
    # a fresh ent-sb0 build had 18 items, none with a null treatment (2026-11-03).
    ("qb/en-US/qb-billing", "objectset_source/object-set-2/BillingTreatmentItem.csv", "BillingTreatment"),
}

# Shared-record conflicts already recorded in the design doc and todo 325, as (object, field).
# A conflict on any other object or field fails the check.
KNOWN_SHARED_CONFLICTS = {
    ("CurrencyType", "ConversionRate"),
    ("CurrencyType", "IsCorporate"),
    ("FulfillmentFalloutRule", "RetriesAllowed"),
    ("FulfillmentStepDefinition", "UsageType"),
    ("FulfillmentStepDefinitionGroup", "UsageType"),
    ("LegalEntity", "CompanyName"),
    ("PriceAdjustmentSchedule", "EffectiveFrom"),
    ("Pricebook2", "CostBook.Name"),
    ("RatingFrequencyPolicy", "RatingDelayDuration"),
    ("TaxPolicy", "DefaultTaxTreatment.Name"),
    ("UnitOfMeasure", "ConversionFactor"),
    ("UnitOfMeasure", "Description"),
    ("UnitOfMeasure", "Name"),
    ("UnitOfMeasure", "Sequence"),
    ("UnitOfMeasure", "Type"),
    ("UnitOfMeasure", "UnitOfMeasureClass.Code"),
    ("UnitOfMeasureClass", "BaseUnitOfMeasure.UnitCode"),
    ("UnitOfMeasureClass", "DefaultUnitOfMeasure.UnitCode"),
    ("UnitOfMeasureClass", "Status"),
}


def plan_dirs(root: Path) -> Iterator[Path]:
    for export in sorted(root.glob("*/*/*/export.json")):
        rel = export.parent.relative_to(root).as_posix()
        if "/test/" in f"/{rel}/" or ".bak" in rel or "extractions" in rel:
            continue
        yield export.parent


def shape_of(plan_rel: str) -> Optional[str]:
    for prefix, shape in SHAPE_ROOTS.items():
        if plan_rel.startswith(prefix + "/"):
            return shape
    return None


def declarations(export: dict) -> Iterator[Tuple[int, dict, str]]:
    """(0-based pass, declaration, object name) for every declaration in the plan."""
    for idx, obj_set in enumerate(sfdmu_export.normalize_object_sets(export)):
        for decl in obj_set.get("objects", []) or []:
            if isinstance(decl, dict):
                name = sfdmu_export.extract_object_name(decl.get("query", ""))
                if name:
                    yield idx, decl, name


def is_written(decl: dict) -> bool:
    if sfdmu_export.is_js_truthy(decl.get("excluded")):
        return False
    op = sfdmu_export.resolve_operation(decl.get("operation", "Readonly"))
    return op not in NOT_WRITTEN


def csv_for(plan: Path, export: dict, pass_idx: int, obj: str) -> Path:
    if pass_idx > 0 and sfdmu_export.is_js_truthy(export.get("useSeparatedCSVFiles")):
        override = plan / "objectset_source" / f"object-set-{pass_idx + 1}" / f"{obj}.csv"
        if override.exists():
            return override
    return plan / f"{obj}.csv"


def read_rows(path: Path) -> Tuple[List[str], List[dict]]:
    if not path.exists():
        return [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def key_parts(external_id: str) -> List[str]:
    return [p.strip() for p in str(external_id or "").split(";") if p.strip()]


def is_null(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in NULL_TOKENS


# ---- lookup check -------------------------------------------------------------------------

def lookup_findings(root: Path = SFDMU, allowed=None) -> Tuple[List[str], Set[tuple]]:
    """(findings, allowlist entries that suppressed a finding)."""
    allowed = KNOWN_UNRESOLVED_LOOKUPS if allowed is None else allowed
    findings, used = [], set()
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        # Per pass: SFDMU resolves a lookup only against a parent declared in the same pass.
        keys_by_pass: Dict[Tuple[int, str], Set[str]] = defaultdict(set)
        for pass_idx, decl, obj in declarations(export):
            if decl.get("externalId") and not sfdmu_export.is_js_truthy(decl.get("excluded")):
                keys_by_pass[(pass_idx, obj)].add(";".join(key_parts(decl["externalId"])))
        seen = set()
        for pass_idx, decl, obj in declarations(export):
            path = csv_for(plan, export, pass_idx, obj)
            if not is_written(decl) or (pass_idx, path) in seen:
                continue
            seen.add((pass_idx, path))
            headers, rows = read_rows(path)
            for col in headers:
                if col.startswith("$$") or ".$$" not in col:
                    continue
                if all(is_null(row.get(col)) for row in rows):
                    continue
                relationship, composite = col.split(".$$", 1)
                parts = ";".join(p for p in composite.split("$") if p)
                parent = RELATIONSHIP_PARENT.get(relationship, relationship)
                csv_rel = path.relative_to(plan).as_posix()
                where = f"{rel}/{csv_rel} column {col}"
                parent_keys = keys_by_pass.get((pass_idx, parent))
                if parent == obj:
                    finding = (f"{where}: self-referential `$$` lookup; use a single-field "
                               f"reference such as `{relationship}.<field>`")
                elif not parent_keys:
                    finding = (f"{where}: pass {pass_idx + 1} declares no {parent} to resolve it "
                               f"against (or add `{relationship}` to RELATIONSHIP_PARENT if its "
                               f"parent object is spelled differently)")
                elif parts not in parent_keys:
                    finding = (f"{where}: parts `{parts}` don't match {parent}'s externalId in "
                               f"pass {pass_idx + 1} ({', '.join(sorted(parent_keys))})")
                else:
                    continue
                # An allowlist entry counts as used only while it still suppresses a finding, so
                # one whose lookup has been fixed is reported stale.
                if (rel, csv_rel, relationship) in allowed:
                    used.add((rel, csv_rel, relationship))
                else:
                    findings.append(finding)
    return findings, used


# ---- shared-record check ------------------------------------------------------------------

def shared_conflicts(root: Path = SFDMU) -> Dict[Tuple[str, str], List[str]]:
    """{(object, field): [example descriptions]} for every cross-shape value conflict.

    Each plan contributes the value its last writing pass sets for a field, so a plan that
    loads Draft in pass 1 and Active in pass 2 contributes Active. A shape's set is the union
    of its plans' final values; a conflict is two shapes whose sets differ.
    """
    final: Dict[Tuple[str, str, str], Dict[str, str]] = defaultdict(dict)  # (obj,key,field)->{plan:v}
    plan_shape: Dict[str, str] = {}
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        shape = shape_of(rel)
        if not shape:
            continue
        plan_shape[rel] = shape
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        for pass_idx, decl, obj in sorted(declarations(export), key=lambda t: t[0]):
            parts = key_parts(decl.get("externalId", ""))
            if not is_written(decl) or not parts:
                continue
            headers, rows = read_rows(csv_for(plan, export, pass_idx, obj))
            key_col = "$$" + "$".join(parts) if len(parts) > 1 else parts[0]
            compared = [h for h in headers if h and h != "Id" and h not in parts
                        and not h.startswith("$$") and ".$$" not in h]
            for row in rows:
                key = row.get(key_col) if key_col in row else ";".join(row.get(p, "") for p in parts)
                if is_null(key):
                    continue
                for field in compared:
                    final[(obj, key, field)][rel] = "" if is_null(row.get(field)) else row[field].strip()
    conflicts: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for (obj, key, field), by_plan in final.items():
        by_shape: Dict[str, Set[str]] = defaultdict(set)
        for rel, value in by_plan.items():
            by_shape[plan_shape[rel]].add(value)
        if len(by_shape) > 1 and len({frozenset(v) for v in by_shape.values()}) > 1:
            shown = "; ".join(f"{s}={sorted(v)}" for s, v in sorted(by_shape.items()))
            conflicts[(obj, field)].append(f"{key}: {shown}")
    return conflicts


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", action="store_true", help="print every shared conflict, known or not")
    args = parser.parse_args(argv)
    try:
        lookups, used = lookup_findings()
        conflicts = shared_conflicts()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    new = {k: v for k, v in conflicts.items() if k not in KNOWN_SHARED_CONFLICTS}
    stale = sorted(KNOWN_SHARED_CONFLICTS - set(conflicts))
    stale_lookups = sorted(KNOWN_UNRESOLVED_LOOKUPS - used)
    for line in lookups:
        print(f"lookup: {line}")
    for (obj, field), examples in sorted(new.items()):
        print(f"shared: {obj}.{field} differs between shapes and isn't in KNOWN_SHARED_CONFLICTS "
              f"(e.g. {examples[0]})")
    for plan, name, relationship in stale_lookups:
        print(f"lookup: {plan}/{name} {relationship} is in KNOWN_UNRESOLVED_LOOKUPS but no longer "
              f"needs it; remove it")
    for obj, field in stale:
        print(f"shared: {obj}.{field} is in KNOWN_SHARED_CONFLICTS but no longer conflicts; remove it")
    if args.list:
        for (obj, field), examples in sorted(conflicts.items()):
            print(f"known: {obj}.{field}: {len(examples)} record(s), e.g. {examples[0]}")
    failed = bool(lookups or new or stale or stale_lookups)
    print(f"{len(lookups)} unresolvable `$$` lookup(s); {len(conflicts)} shared conflict(s), "
          f"{len(new)} new, {len(stale)} stale. {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
