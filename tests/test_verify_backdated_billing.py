#!/usr/bin/env python3
"""Offline unit tests for scripts/backdated_arc/verify_backdated_billing.py (todo 246).

The org-facing steps need a live org; the pieces that decide PASS/FAIL do not:

  1. months_between -- the elapsed-period count the expected amount is built on.
  2. check -- schedule start dates, first invoice line, net amount against the
     signed period amount, the currency-precision tolerance, and the credit-memo
     requirement for a negative invoice.
  3. scenario_defaults -- the asset term and quantity each scenario builds
     (an expired term for renew-expired, quantity 2 for amend-down).

Run:  python tests/test_verify_backdated_billing.py   (no org, stdlib only)
"""
import datetime as dt
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "..", "scripts", "backdated_arc", "verify_backdated_billing.py")
spec = importlib.util.spec_from_file_location("verify_backdated_billing", _PATH)
vb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vb)
vb.log = lambda msg: None
vb.TODAY = dt.date(2026, 10, 28)

_failures = []


def expect(label, got, want):
    if got != want:
        _failures.append(f"{label}: got {got!r}, want {want!r}")


def sched(qty, sid="S1", start="2026-08-01", period=270.0):
    return {"Id": sid, "Quantity": qty, "BillingScheduleStartDate": start, "BillingPeriodAmount": period}


def line(amount, start, sid="S1"):
    return {"BillingScheduleId": sid, "ChargeAmount": amount, "InvoiceLineStartDate": start}


def invoice(lines, memo=None, number="INV-1", balance=None):
    total = sum(l["ChargeAmount"] for l in lines)
    return {"number": number, "total": total, "balance": 0 if balance is None and total < 0 else balance,
            "lines": lines, "memo": memo}


AUG, SEP, OCT = "2026-08-01", "2026-09-01", "2026-10-01"
EFF = dt.date(2026, 8, 1)
MEMO = {"CreditMemoNumber": "CM-1", "TotalAmount": 810, "Status": "Posted"}


def lines_for(amount, sid="S1", months=(AUG, SEP, OCT)):
    return [line(amount, d, sid) for d in months]


def has(fails, text):
    return any(text in f for f in fails)


# 1. months_between counts the period containing the end date.
expect("same month", vb.months_between(EFF, dt.date(2026, 8, 31)), 1)
expect("aug..oct", vb.months_between(EFF, vb.TODAY), 3)
expect("across a year", vb.months_between(dt.date(2026, 11, 1), dt.date(2027, 1, 15)), 3)

# default_effective: the 1st two months before this month, across a year boundary.
expect("default in October", vb.default_effective(dt.date(2026, 10, 28)), dt.date(2026, 8, 1))
expect("default in January", vb.default_effective(dt.date(2027, 1, 5)), dt.date(2026, 11, 1))
expect("default in February", vb.default_effective(dt.date(2027, 2, 5)), dt.date(2026, 12, 1))
expect("default in March", vb.default_effective(dt.date(2027, 3, 5)), dt.date(2027, 1, 1))

# 2. check
expect("amend-up passes", vb.check([sched(1)], [invoice(lines_for(270))], EFF, 2), [])
expect("cancel with credit memo passes", vb.check([sched(-1)], [invoice(lines_for(-270), MEMO)], EFF, 2), [])
expect("negative invoice without a credit memo fails",
       has(vb.check([sched(-1)], [invoice(lines_for(-270))], EFF, 2), "no credit memo"), True)
expect("negative invoice with an open balance fails",
       has(vb.check([sched(-1)], [invoice(lines_for(-270), MEMO, balance=-810)], EFF, 2), "balance"), True)
expect("schedule starting late fails",
       has(vb.check([sched(1, start=SEP)], [invoice(lines_for(270))], EFF, 2), "doesn't start on the effective date"), True)
fails = vb.check([sched(1)], [invoice(lines_for(270, months=(SEP, OCT)))], EFF, 2)
expect("first line after the effective date fails", has(fails, "first invoice line"), True)
expect("a missing period also fails the amount", has(fails, "billed 540.00"), True)

# Swap: an equal-price swap nets to zero, and each side is checked on its own.
swap = lines_for(-270, "OUT") + lines_for(270, "IN")
expect("swap nets zero", vb.check([sched(-1, "OUT"), sched(1, "IN")], [invoice(swap)], EFF, 2), [])
offset = lines_for(-270, "OUT", (AUG, SEP)) + lines_for(270, "IN", (AUG, SEP))
fails = vb.check([sched(-1, "OUT"), sched(1, "IN")], [invoice(offset)], EFF, 2)
expect("offsetting short billing on both sides fails per schedule", has(fails, "OUT billed") and has(fails, "IN billed"),
       True)

# Partial sets: a schedule with no lines (a transfer target never billed) fails.
fails = vb.check([sched(-1, "SRC"), sched(1, "TGT")], [invoice(lines_for(-270, "SRC"), MEMO)], EFF, 2)
expect("an uninvoiced schedule fails", has(fails, "TGT was not invoiced"), True)
fails = vb.check([sched(1)], [invoice(lines_for(270) + [line(5, AUG, "OTHER")])], EFF, 2)
expect("lines for another schedule fail", has(fails, "outside the change"), True)
expect("a zero-quantity schedule is skipped",
       vb.check([sched(1), sched(0, "Z")], [invoice(lines_for(270))], EFF, 2), [])
expect("a zero-quantity schedule that bills fails",
       has(vb.check([sched(1), sched(0, "Z")], [invoice(lines_for(270) + [line(5, AUG, "Z")])], EFF, 2),
           "zero-quantity schedule Z billed 5.00"), True)

# Currency precision: JPY lines round to whole yen (44,033.42 bills as 44,033).
jpy = [line(44033, d) for d in (AUG, SEP, OCT)]
expect("JPY rounding passes at scale 0", vb.check([sched(1, period=44033.4166)], [invoice(jpy)], EFF, 0), [])
expect("the same rounding fails at scale 2", bool(vb.check([sched(1, period=44033.4166)], [invoice(jpy)], EFF, 2)),
       True)

# 3. scenario_defaults
expect("renew-expired term ends the day before", vb.scenario_defaults("renew-expired", EFF),
       (dt.date(2025, 8, 1), dt.date(2026, 7, 31), 1))
expect("renew-expired across a leap day", vb.scenario_defaults("renew-expired", dt.date(2028, 3, 1)),
       (dt.date(2027, 3, 1), dt.date(2028, 2, 29), 1))
start, end, qty = vb.scenario_defaults("amend-down", EFF)
expect("amend-down builds quantity 2 before the effective date", (start < EFF, end > vb.TODAY, qty),
       (True, True, 2))
start, end, qty = vb.scenario_defaults("cancel", EFF)
expect("cancel term is one year from a 1st", (start.day, (end - start).days in (364, 365), qty), (1, True, 1))
expect("the build starts three months back even after a 62-day pair", vb.scenario_defaults("cancel", dt.date(2026, 9, 1))[0],
       dt.date(2026, 6, 1))
expect("and across a year boundary", vb.scenario_defaults("cancel", dt.date(2027, 2, 1))[0], dt.date(2026, 11, 1))


# 4. complete_schedules waits per billable line, not per order count.
def fake_query(items, scheds, details=()):
    def q(org, soql):
        if "FROM OrderItemDetail" in soql:
            expect("details are scoped to the orders", "OrderItem.OrderId IN" in soql, True)
            return [{"Id": d, "OrderItemId": i} for d, i in details]
        if "FROM OrderItem" in soql:
            expect("zero-quantity lines aren't waited for", "Quantity != 0" in soql, True)
            return [{"Id": i} for i in items]
        return scheds
    return q


real_sleep, vb.time.sleep = vb.time.sleep, lambda s: None  # the stable-poll pause (restored below)

real_query = vb.sf_query
vb.sf_query = fake_query(["L1", "L2"], [{"ReferenceEntityItemId": "L1"}])
expect("one of two lines scheduled is not complete", vb.complete_schedules("o", ["801A"]), None)
vb.sf_query = fake_query(["L1", "L2"], [{"ReferenceEntityItemId": "L1"}, {"ReferenceEntityItemId": "L1"}])
expect("two schedules on one line is still not complete", vb.complete_schedules("o", ["801A"]), None)
both = [{"Id": "B1", "ReferenceEntityItemId": "L1"}, {"Id": "B2", "ReferenceEntityItemId": "L2"}]
vb.sf_query = fake_query(["L1", "L2"], both)
expect("every line scheduled is complete", vb.complete_schedules("o", ["801A"]), both)
mixed = [{"Id": "B1", "ReferenceEntityItemId": "L1"}, {"Id": "B2", "ReferenceEntityItemId": "D2"}]
vb.sf_query = fake_query(["L1", "L2"], mixed, details=[("D2", "L2")])
expect("a schedule on an OrderItemDetail covers its line", vb.complete_schedules("o", ["801A"]), mixed)
polls = iter([both, both + [{"Id": "B3", "ReferenceEntityItemId": "L2"}]])
vb.sf_query = fake_query(["L1", "L2"], None)
real_schedules, vb.schedules = vb.schedules, lambda org, ids: next(polls)
expect("a schedule still arriving on a covered line is not complete", vb.complete_schedules("o", ["801A"]), None)
vb.schedules = real_schedules
vb.sf_query = fake_query([], [])
expect("an order with no billable lines never completes", vb.complete_schedules("o", ["801A"]), None)
vb.sf_query = real_query
vb.time.sleep = real_sleep

# 5. argument checks fail before any org call.
def args_error(*argv):
    sys.argv = ["verify_backdated_billing.py", "--org", "x", "--account", "A", *argv]
    stderr, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        vb.main()
    except SystemExit as exc:
        return exc.code == 2
    finally:
        sys.stderr.close()
        sys.stderr = stderr
    return False


A18, O18, O18B = "02ie60000038WQnAAM", "801e600000BopYrAAJ", "801e600000Bopk9AAB"
expect("UI transfer with one order is refused",
       args_error("--scenario", "transfer", "--asset", A18, "--order", O18), True)
expect("rollback with an order is refused", args_error("--scenario", "rollback", "--asset", A18, "--order", O18),
       True)
expect("rollback prepare-only is refused", args_error("--scenario", "rollback", "--prepare-only"), True)
expect("prepare-only with an asset is refused", args_error("--scenario", "cancel", "--prepare-only", "--asset", A18),
       True)
expect("an order without an asset is refused", args_error("--scenario", "cancel", "--order", O18), True)
expect("a bad id is refused", args_error("--scenario", "cancel", "--asset", "02i';DELETE"), True)
expect("a mid-month effective date is refused", args_error("--scenario", "cancel", "--effective", "2026-08-15"), True)
expect("a future effective date is refused", args_error("--scenario", "cancel", "--effective", "2026-11-01"), True)
expect("an effective date too far back is refused", args_error("--scenario", "cancel", "--effective", "2025-12-01"),
       True)
expect("swap without --to-sku is refused", args_error("--scenario", "swap"), True)
expect("two orders for a non-transfer are refused",
       args_error("--scenario", "cancel", "--asset", A18, "--order", O18, "--order", O18B), True)
expect("a renewal more than a year back is refused", args_error("--scenario", "renew-expired", "--effective", "2025-09-01"),
       True)

# wait_for_order re-reads a 15-character order id as the 18-character one queries return.
vb.sf_query = lambda org, soql: [{"Id": O18, "Status": "Activated"}]
expect("15-character order id is normalised", vb.wait_for_order("o", O18[:15]), O18)
vb.sf_query = real_query

# 6. check_shape: the change must match the scenario and the asset's account.
ACC, OTHER = "001A", "001B"
oa = {"801A": ACC}
expect("amend-up with a + schedule passes", vb.check_shape("amend-up", [sched(1)], oa, ACC), [])
expect("an amend +1 run as cancel fails", bool(vb.check_shape("cancel", [sched(1)], oa, ACC)), True)
expect("an order on another account fails", bool(vb.check_shape("amend-up", [sched(1)], {"801A": OTHER}, ACC)), True)
swap_s = [dict(sched(-1, "OUT"), ReferenceEntityId="801A"), dict(sched(1, "IN"), ReferenceEntityId="801A")]
expect("swap with one out and one in passes", vb.check_shape("swap", swap_s, oa, ACC), [])
expect("swap with only an incoming line fails", bool(vb.check_shape("swap", swap_s[1:], oa, ACC)), True)
tr = [dict(sched(-1, "SRC"), ReferenceEntityId="801A"), dict(sched(1, "TGT"), ReferenceEntityId="801B")]
expect("transfer source on the asset account passes", vb.check_shape("transfer", tr, {"801A": ACC, "801B": OTHER}, ACC),
       [])
expect("transfer with both orders on one account fails",
       bool(vb.check_shape("transfer", tr, {"801A": ACC, "801B": ACC}, ACC)), True)
expect("transfer with orders reversed fails",
       bool(vb.check_shape("transfer", tr, {"801B": ACC, "801A": OTHER}, ACC)), True)

expect("renew with a + schedule passes", vb.check_shape("renew-expired", [sched(1)], oa, ACC), [])
expect("amend-down with a - schedule passes", vb.check_shape("amend-down", [sched(-1)], oa, ACC), [])
expect("amend-down with a + schedule fails", bool(vb.check_shape("amend-down", [sched(1)], oa, ACC)), True)
expect("a zero-quantity extra on a swap is ignored",
       vb.check_shape("swap", swap_s + [dict(sched(0, "Z"), ReferenceEntityId="801A")], oa, ACC), [])

if _failures:
    print("FAIL")
    for f in _failures:
        print(f"  {f}")
    sys.exit(1)
print("PASS test_verify_backdated_billing")
