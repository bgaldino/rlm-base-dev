#!/usr/bin/env python3
"""
Detailed comparison for qb-tax, qb-billing, qb-rating, qb-rates.
Uses first column as key; compares by column name (order-independent).
Reports: row counts, keys only in main, only in extract, only in migrate,
and keys present in multiple but with different values.
"""
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "datasets/sfdmu/qb/en-US"
EXTRACT = ROOT / "datasets/sfdmu/reconcile/qb-extractdata/en-US"
MIGRATE = ROOT / "datasets/sfdmu/reconcile/qb-migrate/en-US"

PLANS = ["qb-tax", "qb-billing", "qb-rating", "qb-rates"]
SKIP = {"MissingParentRecordsReport.csv"}
SKIP_SUBDIRS = {"target", "source", "objectset_source", "reports", "logs"}


def root_csvs(plan_path: Path) -> list[str]:
    if not plan_path.is_dir():
        return []
    return sorted(
        f.name for f in plan_path.iterdir()
        if f.is_file() and f.suffix.lower() == ".csv" and f.name not in SKIP
    )


def load_csv_by_key(path: Path, key_col: str | None = None) -> tuple[list[str], dict[str, dict]] | None:
    """Load CSV as dict keyed by first column (or key_col). Returns (headers, {key: row_dict}) or None."""
    if not path.is_file():
        return None
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            r = csv.DictReader(f)
            headers = r.fieldnames
            if not headers:
                return None
            key_column = key_col or headers[0]
            rows = {}
            for row in r:
                key = row.get(key_column, "")
                # Normalize: use same key for comparison (strip, and ensure string)
                key = str(key).strip() if key else ""
                rows[key] = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        return (headers, rows)
    except Exception:
        return None


def row_diff(a: dict, b: dict) -> list[str]:
    """Return list of column names where a and b differ."""
    all_keys = set(a) | set(b)
    return [k for k in all_keys if a.get(k) != b.get(k)]


def run_plan(plan: str, out: list[str]) -> None:
    main_dir = MAIN / plan
    ext_dir = EXTRACT / plan
    mig_dir = MIGRATE / plan
    if not main_dir.is_dir():
        return
    csv_names = root_csvs(main_dir)
    if not csv_names:
        return

    out.append("")
    out.append("=" * 100)
    out.append(f"PLAN: {plan}")
    out.append("=" * 100)

    for name in csv_names:
        main_data = load_csv_by_key(main_dir / name)
        ext_data = load_csv_by_key(ext_dir / name)
        mig_data = load_csv_by_key(mig_dir / name)

        if main_data is None and ext_data is None and mig_data is None:
            continue

        _, main_rows = main_data or (None, {})
        _, ext_rows = ext_data or (None, {})
        _, mig_rows = mig_data or (None, {})

        main_keys = set(main_rows)
        ext_keys = set(ext_rows)
        mig_keys = set(mig_rows)

        n_main, n_ext, n_mig = len(main_keys), len(ext_keys), len(mig_keys)
        out.append("")
        out.append(f"--- {name} ---")
        out.append(f"  Row counts:  main={n_main}  extract={n_ext}  migrate={n_mig}")

        only_main = main_keys - ext_keys - mig_keys
        only_ext = ext_keys - main_keys
        only_mig = mig_keys - main_keys
        in_main_and_ext = main_keys & ext_keys
        in_main_and_mig = main_keys & mig_keys
        in_all_three = main_keys & ext_keys & mig_keys

        # Keys in extract or migrate but not in main (need to add to main)
        only_in_ext = ext_keys - main_keys
        only_in_mig = mig_keys - main_keys
        only_in_ext_not_mig = only_in_ext - mig_keys
        only_in_mig_not_ext = only_in_mig - ext_keys
        in_both_orgs_not_main = (ext_keys | mig_keys) - main_keys

        # Value differences: key in both but row content differs
        main_vs_ext_diff = [k for k in in_main_and_ext if main_rows.get(k) != ext_rows.get(k)]
        main_vs_mig_diff = [k for k in in_main_and_mig if main_rows.get(k) != mig_rows.get(k)]
        ext_vs_mig_diff = [k for k in (ext_keys & mig_keys) if ext_rows.get(k) != mig_rows.get(k)]

        if only_main:
            out.append(f"  Keys ONLY in main (not in either org): {len(only_main)}")
            for k in sorted(only_main)[:15]:
                out.append(f"    - {k}")
            if len(only_main) > 15:
                out.append(f"    ... and {len(only_main) - 15} more")

        if only_in_ext or only_in_mig:
            out.append(f"  Keys in org(s) but NOT in main (candidates to add to main):")
            if only_in_ext:
                out.append(f"    Only in extract: {len(only_in_ext)}")
                for k in sorted(only_in_ext)[:20]:
                    out.append(f"      ext: {k}")
                if len(only_in_ext) > 20:
                    out.append(f"      ... and {len(only_in_ext) - 20} more")
            if only_in_mig:
                out.append(f"    Only in migrate: {len(only_in_mig)}")
                for k in sorted(only_in_mig)[:20]:
                    out.append(f"      mig: {k}")
                if len(only_in_mig) > 20:
                    out.append(f"      ... and {len(only_in_mig) - 20} more")
            in_both = (ext_keys & mig_keys) - main_keys
            if in_both:
                out.append(f"    In BOTH extract and migrate (not in main): {len(in_both)}")
                for k in sorted(in_both)[:15]:
                    out.append(f"      {k}")
                if len(in_both) > 15:
                    out.append(f"      ... and {len(in_both) - 15} more")

        if main_vs_ext_diff:
            out.append(f"  Keys in main and extract but VALUE DIFFERS: {len(main_vs_ext_diff)}")
            for k in sorted(main_vs_ext_diff)[:5]:
                cols = row_diff(main_rows[k], ext_rows[k])
                out.append(f"    Key: {k}  differing columns: {cols[:8]}{'...' if len(cols) > 8 else ''}")
            if len(main_vs_ext_diff) > 5:
                out.append(f"    ... and {len(main_vs_ext_diff) - 5} more")

        if main_vs_mig_diff:
            out.append(f"  Keys in main and migrate but VALUE DIFFERS: {len(main_vs_mig_diff)}")
            for k in sorted(main_vs_mig_diff)[:5]:
                cols = row_diff(main_rows[k], mig_rows[k])
                out.append(f"    Key: {k}  differing columns: {cols[:8]}{'...' if len(cols) > 8 else ''}")
            if len(main_vs_mig_diff) > 5:
                out.append(f"    ... and {len(main_vs_mig_diff) - 5} more")

        if ext_vs_mig_diff and not (only_in_ext or only_in_mig or main_vs_ext_diff or main_vs_mig_diff):
            out.append(f"  Extract vs migrate VALUE DIFFERS (same key, different data): {len(ext_vs_mig_diff)}")
            for k in sorted(ext_vs_mig_diff)[:5]:
                cols = row_diff(ext_rows[k], mig_rows[k])
                out.append(f"    Key: {k}  differing columns: {cols[:8]}{'...' if len(cols) > 8 else ''}")

        if not (only_main or only_in_ext or only_in_mig or main_vs_ext_diff or main_vs_mig_diff or ext_vs_mig_diff):
            if n_main == n_ext == n_mig and main_keys == ext_keys == mig_keys:
                same = all(main_rows.get(k) == ext_rows.get(k) == mig_rows.get(k) for k in main_keys)
                if same:
                    out.append("  -> Content identical (main = extract = migrate).")
                else:
                    out.append("  -> Row counts and keys match but some values differ (see above).")
            else:
                out.append("  -> No structural diff; check row counts.")

    out.append("")


def main():
    out: list[str] = []
    out.append("DETAILED RECONCILIATION: qb-tax, qb-billing, qb-rating, qb-rates")
    out.append("Key = first column of each CSV. Compare main vs extract vs migrate.")
    out.append("")

    for plan in PLANS:
        run_plan(plan, out)

    report = "\n".join(out)
    print(report)
    report_path = ROOT / "datasets/sfdmu/reconcile/RECONCILE_QB_TAX_BILLING_RATING_RATES.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
