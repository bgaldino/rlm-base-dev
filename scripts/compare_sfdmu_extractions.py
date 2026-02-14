#!/usr/bin/env python3
"""
Compare SFDMU extractions: main datasets vs qb-extractdata and qb-migrate.
Reports row counts per object CSV and highlights differences.
"""
import os
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "datasets/sfdmu/qb/en-US"
EXTRACT = ROOT / "datasets/sfdmu/reconcile/qb-extractdata/en-US"
MIGRATE = ROOT / "datasets/sfdmu/reconcile/qb-migrate/en-US"

# Plans we extracted (present in both reconcile dirs)
PLANS = [
    "qb-pcm", "qb-pricing", "qb-product-images", "qb-dro", "qb-tax",
    "qb-billing", "qb-rating", "qb-rates", "qb-transactionprocessingtypes",
    "qb-constraints-product", "qb-constraints-component",
]

SKIP_FILES = {"MissingParentRecordsReport.csv"}
SKIP_SUBDIRS = {"target", "source", "objectset_source", "reports", "logs"}


def root_csvs(plan_path: Path) -> set[str]:
    """Return set of root-level CSV names (object data), excluding subdirs and skip list."""
    if not plan_path.is_dir():
        return set()
    out = set()
    for f in plan_path.iterdir():
        if f.is_file() and f.suffix.lower() == ".csv" and f.name not in SKIP_FILES:
            out.add(f.name)
    return out


def count_rows(csv_path: Path) -> int | None:
    """Return number of data rows (lines - 1 for header), or None if missing/unreadable."""
    if not csv_path.is_file():
        return None
    try:
        with open(csv_path, "rb") as f:
            lines = sum(1 for _ in f)
        return max(0, lines - 1)
    except Exception:
        return None


def all_object_csvs_for_plan(plan: str) -> set[str]:
    """Union of root-level object CSVs across main, extract, migrate for this plan."""
    a = root_csvs(MAIN / plan)
    b = root_csvs(EXTRACT / plan)
    c = root_csvs(MIGRATE / plan)
    return a | b | c


def main():
    print("=" * 100)
    print("SFDMU RECONCILIATION: Main vs qb-extractdata vs qb-migrate")
    print("  Main     = datasets/sfdmu/qb/en-US")
    print("  Extract  = datasets/sfdmu/reconcile/qb-extractdata/en-US")
    print("  Migrate  = datasets/sfdmu/reconcile/qb-migrate/en-US")
    print("=" * 100)

    for plan in PLANS:
        main_dir = MAIN / plan
        ext_dir = EXTRACT / plan
        mig_dir = MIGRATE / plan

        if not ext_dir.is_dir() and not mig_dir.is_dir():
            continue

        objects = sorted(all_object_csvs_for_plan(plan))
        if not objects:
            continue

        print(f"\n## {plan}")
        print("-" * 100)
        # Header
        print(f"{'Object':<40} {'Main':>10} {'Extract':>10} {'Migrate':>10}  Notes")
        print("-" * 100)

        for obj in objects:
            r_main = count_rows(main_dir / obj)
            r_ext = count_rows(ext_dir / obj)
            r_mig = count_rows(mig_dir / obj)

            notes = []
            if r_main is None and (r_ext is not None or r_mig is not None):
                notes.append("main missing")
            if r_ext is None and r_main is not None:
                notes.append("extract missing")
            if r_mig is None and r_main is not None:
                notes.append("migrate missing")
            if r_main is not None and r_ext is not None and r_main != r_ext:
                notes.append(f"main≠ext ({r_main - r_ext:+d})")
            if r_main is not None and r_mig is not None and r_main != r_mig:
                notes.append(f"main≠mig ({r_main - r_mig:+d})")
            if r_ext is not None and r_mig is not None and r_ext != r_mig:
                notes.append(f"ext≠mig ({r_ext - r_mig:+d})")

            main_s = str(r_main) if r_main is not None else "-"
            ext_s = str(r_ext) if r_ext is not None else "-"
            mig_s = str(r_mig) if r_mig is not None else "-"
            note_s = "; ".join(notes) if notes else ""
            print(f"{obj:<40} {main_s:>10} {ext_s:>10} {mig_s:>10}  {note_s}")

    # Summary of differences
    print("\n" + "=" * 100)
    print("SUMMARY: Key differences to reconcile")
    print("=" * 100)
    print("""
- qb-pcm: ProductRampSegment has 1 more row in qb-migrate than main/extract.
- qb-pricing: Main has fewer Product2 (152) and no PricebookEntryDerivedPrice (0) vs extract/migrate (164, 2).
- qb-product-images: Main has 105 Product2 vs 164 in both orgs (main is subset).
- qb-dro: Large gaps: main has fewer FulfillmentStepDefinition, FulfillmentStepDefinitionGroup,
  FulfillmentStepDependencyDef, FulfillmentWorkspace(Item), ProductFulfillmentDecompRule,
  ProductFulfillmentScenario, UserAndGroup. Migrate has more than extract in several.
- qb-tax, qb-billing, qb-rating, qb-rates: Main has fewer Product2 rows (subset); billing also
  has GeneralLedgerAccount / GeneralLedgerAcctAsgntRule differences; rating/rates have
  Usage/ProductUsage*/Rate* differences.
- qb-constraints-product, qb-constraints-component: No CSVs in extract/migrate (those plans
  were not run during extraction); main has data.
""")
    print("Done. Use diff/custom logic on specific CSVs for content reconciliation.")
    print("=" * 100)


if __name__ == "__main__":
    main()
