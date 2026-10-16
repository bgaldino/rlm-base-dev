#!/usr/bin/env python3
"""Offline unit tests for scripts/renewal_assets/build_renewal_buckets.py.

The month arithmetic (`minus_months`), the even end-date `spread`, and the
`build_plan` window planner are pure functions with no org dependency, but a
dry-run only proves they *run* -- it does not pin month-end/leap-year clamping
or the exact 30/60/90/91 bucket boundaries against regression. These cases do.

Run:  python tests/test_renewal_bucket_planner.py   (no org, no deps beyond stdlib)
"""
import datetime as dt
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "scripts", "renewal_assets", "build_renewal_buckets.py")

spec = importlib.util.spec_from_file_location("renewal_bucket_planner", _SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

_failures = []


def check(label, got, want):
    if got != want:
        _failures.append(f"{label}: got {got!r}, want {want!r}")


# ── minus_months: month-end + leap-year clamping ───────────────────────────
# The bug this guards: a naive fallback returned day 28 for any overflow, so
# 31 May - 1mo became 28 Apr instead of 30 Apr.
check("May31 -1mo",  m.minus_months(dt.date(2026, 5, 31), 1), dt.date(2026, 4, 30))
check("Mar31 -1mo",  m.minus_months(dt.date(2027, 3, 31), 1), dt.date(2027, 2, 28))  # non-leap
check("Mar31 -1mo leap", m.minus_months(dt.date(2028, 3, 31), 1), dt.date(2028, 2, 29))  # leap
check("Mar30 -1mo",  m.minus_months(dt.date(2026, 3, 30), 1), dt.date(2026, 2, 28))
check("Jan31 -1mo",  m.minus_months(dt.date(2026, 1, 31), 1), dt.date(2025, 12, 31))  # year rollback
check("Jul31 -1mo",  m.minus_months(dt.date(2026, 7, 31), 1), dt.date(2026, 6, 30))
check("Dec31 -12mo", m.minus_months(dt.date(2026, 12, 31), 12), dt.date(2025, 12, 31))
check("Jun15 -3mo",  m.minus_months(dt.date(2026, 6, 15), 3), dt.date(2026, 3, 15))  # no clamp needed
check("Dec31 -10mo", m.minus_months(dt.date(2026, 12, 31), 10), dt.date(2026, 2, 28))

# ── spread: even end-dates across [first, last] inclusive ──────────────────
d0, d30 = dt.date(2026, 1, 1), dt.date(2026, 1, 31)
check("spread n=1", m.spread(d0, d30, 1), [d0])
check("spread n=2", m.spread(d0, d30, 2), [d0, d30])           # endpoints
s3 = m.spread(d0, d30, 3)
check("spread n=3 ends", (s3[0], s3[-1]), (d0, d30))
check("spread n=3 mid", s3[1], dt.date(2026, 1, 16))            # midpoint (round)
check("spread n=3 len", len(s3), 3)

# ── build_plan: bucket boundaries + shape ──────────────────────────────────
TODAY = dt.date(2026, 9, 10)
plan = m.build_plan(TODAY, per_bucket=1, far_days=365, term_months=12,
                    skus=["QB-DB"], accounts=["A"])
check("plan len 4x1", len(plan), 4)
labels = [r["bucket"] for r in plan]
check("bucket labels", labels, ["<=30", "30-60", "60-90", ">90"])
# per_bucket=1 -> spread returns [first], i.e. the low edge of each window.
ends = {r["bucket"]: dt.date.fromisoformat(r["end"]) for r in plan}
check("<=30 low edge",  ends["<=30"],  TODAY + dt.timedelta(days=1))
check("30-60 low edge", ends["30-60"], TODAY + dt.timedelta(days=31))
check("60-90 low edge", ends["60-90"], TODAY + dt.timedelta(days=61))
check(">90 low edge",   ends[">90"],   TODAY + dt.timedelta(days=91))
# start = end - term + 1 day
r0 = plan[0]
check("start = end-term+1d",
      dt.date.fromisoformat(r0["start"]),
      m.minus_months(dt.date.fromisoformat(r0["end"]), 12) + dt.timedelta(days=1))

# per_bucket=2 -> each window spans its full [lo, hi] edges.
plan2 = m.build_plan(TODAY, per_bucket=2, far_days=365, term_months=12,
                     skus=["QB-DB"], accounts=["A", "B"])
check("plan2 len 4x2", len(plan2), 8)
b1 = [dt.date.fromisoformat(r["end"]) for r in plan2 if r["bucket"] == "30-60"]
check("30-60 spans 31..60", (b1[0], b1[1]),
      (TODAY + dt.timedelta(days=31), TODAY + dt.timedelta(days=60)))
far = [dt.date.fromisoformat(r["end"]) for r in plan2 if r["bucket"] == ">90"]
check(">90 outer edge = far_days", far[-1], TODAY + dt.timedelta(days=365))
# round-robin account assignment across the flat plan
check("accounts round-robin", [r["account"] for r in plan2[:3]], ["A", "B", "A"])
# sku cycling within a bucket
plan3 = m.build_plan(TODAY, per_bucket=2, far_days=365, term_months=12,
                     skus=["QB-DB", "QB-DAT-THPT"], accounts=["A"])
first_bucket = [r["sku"] for r in plan3 if r["bucket"] == "<=30"]
check("sku cycles in bucket", first_bucket, ["QB-DB", "QB-DAT-THPT"])

# ── future_start_rows: reject a plan whose start back-solves past today ─────
# far_days (365) > ~360-day 12mo term -> the >90 outer edge (end=today+365) yields
# start = today+1, a future-dated asset that is not active yet. per_bucket=1 never
# hits the outer edge, so it is safe; per_bucket>=2 does.
safe = m.build_plan(TODAY, per_bucket=1, far_days=365, term_months=12,
                    skus=["QB-DB"], accounts=["A"])
check("per_bucket=1 no future starts", m.future_start_rows(safe, TODAY), [])
risky = m.build_plan(TODAY, per_bucket=2, far_days=365, term_months=12,
                     skus=["QB-DB"], accounts=["A", "B"])
fsr = m.future_start_rows(risky, TODAY)
check("per_bucket=2 far=365 term=12 -> 1 future start", len(fsr), 1)
check("future start is the >90 outer edge", fsr[0]["bucket"], ">90")
check("future start date = today+1",
      dt.date.fromisoformat(fsr[0]["start"]), TODAY + dt.timedelta(days=1))
# far_days <= term keeps every start on/before today (the documented far=180 fix).
fixed = m.build_plan(TODAY, per_bucket=2, far_days=180, term_months=12,
                     skus=["QB-DB"], accounts=["A", "B"])
check("far=180 term=12 no future starts", m.future_start_rows(fixed, TODAY), [])

if _failures:
    print("FAIL — renewal bucket planner:")
    for f in _failures:
        print("  -", f)
    sys.exit(1)
print("OK — renewal bucket planner: all cases passed")
