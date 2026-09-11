#!/usr/bin/env python3
"""Fan renewal assets out across the four expiry windows, reusing build_quote_to_asset.py.

Purpose
-------
Renewal revenue-insights and renewal-quote testing wants assets whose
``LifecycleEndDate`` lands in each of the four expiry windows the platform's
renewal views bucket by:

    <=30   1-30  days out
    30-60  31-60 days out
    60-90  61-90 days out
    >90    91+   days out

Producing that spread by hand is tedious and error-prone (each asset needs a
back-dated term so an already-aged subscription expires inside its window). This
driver computes the windows from *today*, back-solves a start date per asset,
and drives the existing, org-verified Quote -> Order -> Activation flow once per
asset.

Reuse, not reimplementation
---------------------------
Every asset is built by shelling out to ``scripts/build_quote_to_asset.py`` --
the same Place-Sales-Transaction -> createOrdersFromQuote -> activate path a
seller/admin uses, so ``LifecycleEndDate`` is platform-derived, never hand-set.
This script only *schedules* those runs (which window, which SKU, which start
date); it issues no Quote/Order/Asset DML of its own. For a plain renewal term
product (no usage entitlements) it passes ``--skip-usage-verify`` so a valid
non-usage asset is not failed for carrying zero usage buckets; for a usage-anchor
SKU (QB-DB etc.) drop that by passing ``--verify-usage``.

Accounts must pre-exist
-----------------------
``build_quote_to_asset.py`` resolves accounts by name and does not create them
(mirroring RLM_QuickQuote against an existing Account). Pass ``--accounts`` with
names that already exist in the org; assets are distributed round-robin across
them. Placing more than one asset of the SAME SKU on one account is fine -- each
per-asset run gets ``--allow-existing-asset`` so the post-activation poll waits
for a genuinely NEW asset id rather than matching a prior one.

Product mix
-----------
Pass one SKU (``--skus QB-DB``) for a single-product spread, or several
(``--skus "QB-DB,QB-DAT-THPT"``) to place one distinct product per asset in each
bucket, cycling with repeats when a bucket needs more assets than SKUs given.
Unlike the eng original this driver does not auto-discover products -- you name
the SKUs, which keeps it schema-agnostic and avoids guessing which products this
flow can activate.

Usage
-----
    # dry-run first -- prints the plan, touches nothing
    python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
        --accounts "Infinitech" --skus QB-DB --per-bucket 1 \
        --term-months 12 --selling-model "Term Annual" --billing-frequency Annual --dry-run

    # then execute. NOTE --far-bucket-days 180 (not the 365 default): with 2+ per
    # bucket the >90 window's OUTER edge back-solves a start of end - term + 1 day, so a far
    # edge beyond the term (365 default vs a ~360-day 12-month term) would start the
    # asset in the future. Keep far-bucket-days <= the term, or raise --term-months.
    python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
        --accounts "Infinitech,Kingsbridge Digital" --skus QB-DB \
        --per-bucket 2 --term-months 12 --far-bucket-days 180 \
        --selling-model "Term Annual" --billing-frequency Annual

Exits 0 when every scheduled asset build succeeded, 1 otherwise.
"""
import argparse
import csv
import datetime as dt
import os
import subprocess
import sys

BUILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "build_quote_to_asset.py")

# (label, first day offset, last day offset) from today.
WINDOWS = [("<=30", 1, 30), ("30-60", 31, 60), ("60-90", 61, 90), (">90", 91, None)]


def minus_months(d, months):
    """Return d shifted back `months` calendar months, clamping the day."""
    m = d.month - 1 - months
    year = d.year + m // 12
    month = m % 12 + 1
    # clamp to the last valid day of the target month (e.g. 31 Mar - 1 month ->
    # 28/29 Feb; 31 May - 1 month -> 30 Apr). Try the original day first, then the
    # largest valid day DESCENDING so we land on the month's true last day, not 28.
    for day in (d.day, 31, 30, 29, 28):
        try:
            return d.replace(year=year, month=month, day=day)
        except ValueError:
            continue
    return d.replace(year=year, month=month, day=1)


def spread(first, last, n):
    """n end-dates evenly spaced across [first, last] (inclusive)."""
    span = (last - first).days
    if n <= 1:
        return [first]
    return [first + dt.timedelta(days=round(span * i / (n - 1))) for i in range(n)]


def build_plan(today, per_bucket, far_days, term_months, skus, accounts):
    """Produce the ordered list of per-asset runs. Pure -- no org calls."""
    plan = []
    global_idx = 0
    for label, lo, hi in WINDOWS:
        hi_off = hi if hi is not None else far_days
        first = today + dt.timedelta(days=lo)
        last = today + dt.timedelta(days=hi_off)
        for i, end in enumerate(spread(first, last, per_bucket)):
            start = minus_months(end, term_months) + dt.timedelta(days=1)
            plan.append({
                "bucket": label,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "sku": skus[i % len(skus)],
                "account": accounts[global_idx % len(accounts)],
            })
            global_idx += 1
    return plan


def future_start_rows(plan, today):
    """Rows whose back-solved start date is AFTER today (pure -- no org calls).

    A bucket asset must be CURRENTLY active and merely expiring in its window, but
    start = end - term + 1 day, so when the >90 window's outer edge (far_bucket_days) exceeds
    the term the start lands in the future -- an asset that is not active yet and so
    not renewal-ready. Callers reject a plan with any such row.
    """
    return [r for r in plan if dt.date.fromisoformat(r["start"]) > today]


def run_one(args, row):
    cmd = [
        sys.executable, BUILDER,
        "--org", args.org,
        "--accounts", row["account"],
        "--sku", row["sku"],
        "--start", row["start"],
        "--end", row["end"],
        "--quantity", str(args.quantity),
        "--billing-frequency", args.billing_frequency,
        "--period-boundary", args.period_boundary,
        "--timeout", str(args.timeout),
        "--interval", str(args.interval),
        "--allow-existing-asset",
        # Every bucket asset MUST carry a LifecycleEndDate to fall in a window, so the
        # child must treat a resolved OneTime/Evergreen model (or a missing end) as a
        # hard error, not an exempt skip. The parent's nonblank check cannot see how a
        # NAME resolves; this delegates the authoritative TermDefined/end-date contract
        # to the child, which has the resolved model in hand.
        "--require-term-end",
    ]
    if args.selling_model:
        cmd += ["--selling-model", args.selling_model]
    if not args.verify_usage:
        cmd += ["--skip-usage-verify"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    if p.returncode != 0:
        sys.stdout.write(p.stderr)
    return p.returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", required=True, help="sf CLI alias or username")
    ap.add_argument("--accounts", required=True,
                    help="comma-separated names of PRE-EXISTING accounts to spread assets across")
    ap.add_argument("--skus", default="QB-DB",
                    help="comma-separated SKUs; one distinct product per asset per bucket, "
                         "cycling with repeats (default: QB-DB)")
    ap.add_argument("--per-bucket", type=int, default=1,
                    help="assets per expiry window; total = 4 x this (default: 1)")
    ap.add_argument("--term-months", type=int, default=12,
                    help="subscription term in months; start = end - term + 1 day "
                         "(inclusive term boundaries) (default: 12)")
    ap.add_argument("--selling-model", default="",
                    help="ProductSellingModel NAME (e.g. 'Term Annual') or TYPE; passed "
                         "through to build_quote_to_asset.py. MUST resolve to a TermDefined "
                         "model — expiry windows need a LifecycleEndDate, so Evergreen/OneTime "
                         "models (which produce no end date) are unsupported here. Note the "
                         "NAME must exist for the SKU: e.g. QB-DB offers only 'Term Annual'")
    ap.add_argument("--quantity", type=int, default=1)
    ap.add_argument("--billing-frequency", default="Monthly",
                    choices=["MilestonePlan", "Monthly", "Quarterly", "Semi-Annual", "Annual"])
    ap.add_argument("--period-boundary", default="Anniversary",
                    choices=["AlignToCalendar", "Anniversary", "DayOfPeriod", "LastDayOfPeriod"])
    ap.add_argument("--today", default="",
                    help="anchor date YYYY-MM-DD for the windows (default: real today)")
    ap.add_argument("--far-bucket-days", type=int, default=365,
                    help="outer edge of the >90 window, in days from today (default: 365). "
                         "With --per-bucket >= 2 keep this <= the term (a 12-month term is "
                         "~360 days): a far edge beyond the term back-solves a future start "
                         "date, and the planner rejects any plan whose computed start > today.")
    ap.add_argument("--verify-usage", action="store_true",
                    help="require usage buckets on each asset (for usage-anchor SKUs). "
                         "Default off: plain renewal term products carry none")
    ap.add_argument("--timeout", type=int, default=300, help="per-poll timeout seconds")
    ap.add_argument("--interval", type=int, default=10, help="poll interval seconds")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and exit without building anything")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    skus = [s.strip() for s in args.skus.split(",") if s.strip()]
    accounts = [a.strip() for a in args.accounts.split(",") if a.strip()]
    if not skus or not accounts:
        print("FATAL: --skus and --accounts must each name at least one value.", file=sys.stderr)
        return 1
    if not args.selling_model.strip():
        print("FATAL: --selling-model is required and must resolve to a TermDefined model "
              "(e.g. 'Term Annual'). Expiry windows need a LifecycleEndDate, so an empty or "
              "Evergreen/OneTime model would produce an asset with no end date to bucket by. "
              "The builder verifies the resulting end date matches this row's window.",
              file=sys.stderr)
        return 1
    # Reject the two lifecycle-less TYPE keywords up front — the only values known to be
    # non-TermDefined without an org lookup. A NAME could still resolve to Evergreen/OneTime,
    # but that is caught by the child's --require-term-end check (passed in run_one), which
    # has the resolved model in hand. This is just a fast, obvious-mistake guard.
    if args.selling_model.strip().lower() in ("evergreen", "onetime", "one time"):
        print(f"FATAL: --selling-model {args.selling_model!r} is a lifecycle-less model type; "
              "expiry windows need a TermDefined model with a LifecycleEndDate (e.g. "
              "'Term Annual'). Pass a TermDefined model NAME or type.", file=sys.stderr)
        return 1
    if args.per_bucket < 1:
        print("FATAL: --per-bucket must be >= 1 (0 builds nothing).", file=sys.stderr)
        return 1
    if args.term_months < 1:
        print("FATAL: --term-months must be >= 1.", file=sys.stderr)
        return 1
    if args.far_bucket_days < 91:
        print("FATAL: --far-bucket-days must be >= 91 — the >90 window starts at day 91; "
              "a smaller value would place '>90' assets inside an earlier window.",
              file=sys.stderr)
        return 1

    plan = build_plan(today, args.per_bucket, args.far_bucket_days,
                      args.term_months, skus, accounts)
    print(f"org={args.org}  today={today}  per-bucket={args.per_bucket}  "
          f"total={len(plan)}  skus={skus}  accounts={len(accounts)}")
    print(f"{'#':>3}  {'bucket':6}  {'start':10}  {'end':10}  {'sku':14}  account")
    for i, r in enumerate(plan, 1):
        print(f"{i:>3}  {r['bucket']:6}  {r['start']:10}  {r['end']:10}  "
              f"{r['sku']:14}  {r['account']}")

    # Every bucket asset must be CURRENTLY active and merely expiring in its window.
    # start = end - term + 1 day, so when --far-bucket-days exceeds the term (e.g. far=365 with
    # term-months=12 puts the >90 end a full year out) the back-solved start lands AFTER
    # today -- a future-dated subscription that is not active yet and so not renewal-ready.
    # Reject the whole plan with actionable guidance rather than building such assets.
    future = future_start_rows(plan, today)
    if future:
        worst = max(future, key=lambda r: r["start"])
        print(f"\nFATAL: {len(future)} of {len(plan)} planned asset(s) would start AFTER today "
              f"(latest {worst['start']} in the {worst['bucket']} bucket) — a future-dated start "
              f"is not currently active, so the asset is not renewal-ready. This happens when "
              f"--far-bucket-days ({args.far_bucket_days}) exceeds the term "
              f"(--term-months {args.term_months} ≈ {args.term_months * 30} days). Raise "
              f"--term-months or lower --far-bucket-days so every computed start ≤ today.",
              file=sys.stderr)
        return 1

    if args.dry_run:
        print("\n(dry-run — nothing built)")
        return 0

    results = "/tmp/renewal_bucket_results.csv"
    failures = []
    with open(results, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "bucket", "start", "end", "sku", "account", "status"])
        for i, r in enumerate(plan, 1):
            print(f"\n### Run {i}/{len(plan)}  bucket={r['bucket']}  sku={r['sku']}  "
                  f"account={r['account']}  {r['start']} -> {r['end']} ###")
            ok = run_one(args, r)
            w.writerow([i, r["bucket"], r["start"], r["end"], r["sku"], r["account"],
                        "OK" if ok else "FAIL"])
            if not ok:
                failures.append(i)

    print(f"\n{'=' * 60}")
    print(f"{len(plan) - len(failures)}/{len(plan)} asset build(s) succeeded  "
          f"(log: {results})")
    if failures:
        print(f"  failed run(s): {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
