#!/usr/bin/env python3
"""
Compare SFDMU CSV content (not just row counts) for qb-pcm, qb-pricing, qb-product-images.
Compares main vs qb-extractdata and main vs qb-migrate with row order normalized.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "datasets/sfdmu/qb/en-US"
EXTRACT = ROOT / "datasets/sfdmu/reconcile/qb-extractdata/en-US"
MIGRATE = ROOT / "datasets/sfdmu/reconcile/qb-migrate/en-US"

PLANS = ["qb-pcm", "qb-pricing", "qb-product-images"]
SKIP = {"MissingParentRecordsReport.csv"}


def load_csv_sorted(path: Path) -> tuple[list[str], list[tuple]] | None:
    """Load CSV; return (header_columns, sorted_rows) or None if missing. Rows sorted by tuple of values."""
    if not path.is_file():
        return None
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            r = csv.reader(f)
            header = next(r, None)
            if not header:
                return None
            rows = [tuple(row) for row in r]
        # Pad rows to header length so comparison is stable
        n = len(header)
        rows = [tuple((r[i] if i < len(r) else "") for i in range(n)) for r in rows]
        rows.sort()
        return (header, rows)
    except Exception:
        return None


def compare_content(plan: str) -> None:
    main_dir = MAIN / plan
    ext_dir = EXTRACT / plan
    mig_dir = MIGRATE / plan
    if not main_dir.is_dir():
        return
    csvs = sorted(f.name for f in main_dir.iterdir() if f.is_file() and f.suffix.lower() == ".csv" and f.name not in SKIP)
    if not csvs:
        return
    print(f"\n## {plan} (content comparison)")
    print("-" * 80)
    for name in csvs:
        main_data = load_csv_sorted(main_dir / name)
        ext_data = load_csv_sorted(ext_dir / name)
        mig_data = load_csv_sorted(mig_dir / name)
        if main_data is None:
            continue
        h_main, rows_main = main_data
        rows_ext = ext_data[1] if ext_data else None
        rows_mig = mig_data[1] if mig_data else None

        def same(a: list, b: list) -> bool:
            return a == b if (a is not None and b is not None) else False

        main_vs_ext = same(rows_main, rows_ext)
        main_vs_mig = same(rows_main, rows_mig)
        ext_vs_mig = same(rows_ext, rows_mig)

        status = []
        if main_vs_ext and main_vs_mig:
            status.append("main = extract = migrate")
        else:
            if not main_vs_ext:
                status.append("main≠extract")
            if not main_vs_mig:
                status.append("main≠migrate")
            if not ext_vs_mig:
                status.append("extract≠migrate")

        n_main, n_ext, n_mig = len(rows_main), len(rows_ext) if rows_ext is not None else 0, len(rows_mig) if rows_mig is not None else 0
        print(f"  {name:<45} rows: main={n_main} ext={n_ext} mig={n_mig}  ->  {'; '.join(status)}")

        if not (main_vs_ext and main_vs_mig):
            # Show first difference
            if rows_ext is not None and rows_main != rows_ext:
                for i, (r1, r2) in enumerate(zip(rows_main, rows_ext)):
                    if r1 != r2:
                        print(f"      First main vs extract diff at row index {i}: main={r1[:3]}... ext={r2[:3]}...")
                        break
                if len(rows_main) != len(rows_ext):
                    print(f"      Row count diff: main {len(rows_main)} vs extract {len(rows_ext)}")
            if rows_mig is not None and rows_main != rows_mig:
                for i, (r1, r2) in enumerate(zip(rows_main, rows_mig)):
                    if r1 != r2:
                        print(f"      First main vs migrate diff at row index {i}: main={r1[:3]}... mig={r2[:3]}...")
                        break
                if len(rows_main) != len(rows_mig):
                    print(f"      Row count diff: main {len(rows_main)} vs migrate {len(rows_mig)}")


def main():
    print("=" * 80)
    print("Content comparison (qb-pcm, qb-pricing, qb-product-images)")
    print("Rows normalized by sorting before compare.")
    print("=" * 80)
    for plan in PLANS:
        compare_content(plan)
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
