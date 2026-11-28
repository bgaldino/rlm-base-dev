#!/usr/bin/env python3
"""`qb_usage.py report` labels each bucket's shape and scopes it with --as-of (todo 301).

    python tests/test_qb_usage_report.py   (no org, stdlib only)

Each usage entitlement on a 264 asset carries a term-length wallet and one child under it: a
MONTHLY bucket holding the period's consumption and balance, or an OPEN bucket (null end) carrying
zeros (todo 051). A backdated asset gets a monthly bucket for its first period only. The rows
below are the shapes measured on a 264 qb asset started 2026-10-01; sf_query is stubbed.
"""
import contextlib
import datetime
import importlib.util
import io
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


spec = importlib.util.spec_from_file_location("qb_usage", REPO / "scripts/qb_usage.py")
qb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qb)


def bucket(bid, parent, code, start, end, balance, consumed):
    return {
        "Id": bid, "ParentId": parent,
        "UsageResource": {"Code": code},
        "EffectiveStartDateTime": f"{start}T00:00:00.000+0000",
        "EffectiveEndDateTime": f"{end}T23:59:59.000+0000" if end else None,
        "BucketBalance": balance, "ConsumedEntitlement": consumed,
        "TransactionUsageEntitlement": {
            "Product": {"StockKeepingUnit": "QB-DB-TOKEN"},
            "Account": {"Name": "Kingsbridge Digital"},
            "EntitlementQuantity": 10000 if code == "QB-TOKEN" else 0,
        },
    }


BINDING = "1GvBINDING"  # a grant-binding target, not a bucket
BUCKETS = [
    bucket("TERM1", BINDING, "QB-TOKEN", "2026-10-01", "2027-09-30", 0, None),
    bucket("MON1", "TERM1", "QB-TOKEN", "2026-10-01", "2026-10-31", 10000, 0),
    bucket("TERM2", BINDING, "UR-CPUTIME-TKN", "2026-10-01", "2027-09-30", 0, None),
    bucket("OPEN2", "TERM2", "UR-CPUTIME-TKN", "2026-10-01", None, 0, 0),
]
IDS = {b["Id"] for b in BUCKETS}

print("bucket_shape")
shapes = {b["Id"]: qb.bucket_shape(b, IDS) for b in BUCKETS}
check("the wallet is TERM", shapes["TERM1"] == "TERM" and shapes["TERM2"] == "TERM", str(shapes))
check("the child with an end is MONTHLY", shapes["MON1"] == "MONTHLY", str(shapes))
check("the child with no end is OPEN", shapes["OPEN2"] == "OPEN", str(shapes))

print("overlaps_day")
mon = BUCKETS[1]
check("a day inside the monthly bucket overlaps", qb.overlaps_day(mon, datetime.date(2026, 10, 15)))
check("its last day overlaps", qb.overlaps_day(mon, datetime.date(2026, 10, 31)))
check("the next day does not", not qb.overlaps_day(mon, datetime.date(2026, 11, 1)))
check("the day before it starts does not", not qb.overlaps_day(mon, datetime.date(2026, 9, 30)))
check("an open bucket overlaps any later day", qb.overlaps_day(BUCKETS[3], datetime.date(2030, 1, 1)))


def run_report(as_of):
    def fake_query(org, soql):
        if "FROM UsageEntitlementBucket" in soql:
            return [dict(b) for b in BUCKETS]
        if "COUNT(Id)" in soql:
            return [{"c": 0}]
        return []
    qb.sf_query = fake_query
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        qb.cmd_report(types.SimpleNamespace(org="x", accounts=None, as_of=as_of))
    return out.getvalue()


def bucket_lines(text):
    return [l for l in text.splitlines() if "Kingsbridge Digital " in l and "QB-DB-TOKEN" in l]


print("cmd_report")
everything = run_report(None)
rows = bucket_lines(everything)
check("without --as-of every bucket prints", len(rows) == 4, everything)
check("each row carries its window and shape",
      any("MONTHLY" in l and "2026-10-01..2026-10-31" in l for l in rows)
      and any("OPEN" in l and "2026-10-01..open" in l for l in rows), everything)

october = bucket_lines(run_report(datetime.date(2026, 10, 15)))
check("--as-of inside the first period keeps the monthly bucket",
      len(october) == 4 and any("MONTHLY" in l for l in october), "\n".join(october))

november_text = run_report(datetime.date(2026, 11, 28))
november = bucket_lines(november_text)
check("--as-of past the first period drops the October monthly bucket",
      len(november) == 3 and not any("MONTHLY" in l for l in november), november_text)
check("and says no monthly bucket covers the day",
      "Kingsbridge Digital: no MONTHLY bucket covers this day" in november_text, november_text)

before = bucket_lines(run_report(datetime.date(2026, 9, 30)))
check("--as-of before the asset starts lists nothing", before == [], "\n".join(before))

if FAILURES:
    print(f"\n{len(FAILURES)} failure(s)")
    sys.exit(1)
print("\nall passed")
