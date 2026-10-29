#!/usr/bin/env python3
"""Offline unit tests for scripts/backdated_arc/verify_backdated_billing.py (todo 246).

The org-facing steps need a live org; the pieces that decide PASS/FAIL do not:

  1. months_between -- the elapsed-period count the expected amount is built on.
  2. check -- schedule start dates, first invoice line, net amount against the
     signed period amount, the currency-precision tolerance, and the credit-memo
     requirement for a negative invoice.
  3. scenario_defaults -- the asset term and quantity each scenario builds
     (an expired term for renew-expired, quantity 2 for amend-down).
  4. periods_started -- billing periods per schedule term (a UI swap bills annually).
  5. complete_schedules -- waits per billable line, maps OrderItemDetail references,
     and needs a stable poll.
  6. check_shape and the argument rules -- UI-mode orders must match the scenario.

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
    return {"Id": sid, "Quantity": qty, "BillingScheduleStartDate": start, "BillingPeriodAmount": period,
            "BillingTermUnit": "Month", "BillingTerm": 1}


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

# Billing periods follow each schedule's own term (a UI swap bills the incoming line annually).
expect("monthly periods since Aug", vb.periods_started(EFF, vb.TODAY, "Month", 1), 3)
expect("one annual period started", vb.periods_started(EFF, vb.TODAY, "Year", 1), 1)
expect("quarterly: Aug-Oct is one quarter", vb.periods_started(EFF, vb.TODAY, "Quarter", 1), 1)
expect("quarterly: Nov starts a second", vb.periods_started(EFF, dt.date(2026, 11, 2), "Quarter", 1), 2)
expect("milestone plans aren't modelled", vb.periods_started(EFF, vb.TODAY, "BillingMilestonePlan", 1), None)
annual_in = dict(sched(1, "IN", period=3240.0), BillingTermUnit="Year", BillingTerm=1)
ui_swap = lines_for(-270, "OUT") + [line(3240, AUG, "IN")]
expect("UI swap: monthly credit out, annual charge in",
       vb.check([sched(-1, "OUT"), annual_in], [invoice(ui_swap)], EFF, 2), [])

# Ramps: a later segment's schedule starts on its own boundary and bills nothing yet.
Y2 = dt.date(2027, 5, 1)
RAMP = (dt.date(2026, 5, 1),)  # a ramp asset's segments anchor on the asset's start
RENEWAL_RAMP = (EFF,)  # a ramped renewal's segments anchor on the effective date
ramp_cancel = [sched(-1, "Y1", period=12.5), sched(-2, "Y2", start="2027-05-01", period=25.0)]
y1_credit = lines_for(-12.5, "Y1")
expect("ramp cancel: Year-2 credit not yet billable passes",
       vb.check(ramp_cancel, [invoice(y1_credit, MEMO)], EFF, 2, {"Y1": EFF, "Y2": Y2}, RAMP), [])
expect("a later start that isn't its line's start fails",
       has(vb.check(ramp_cancel, [invoice(y1_credit, MEMO)], EFF, 2, {"Y1": EFF, "Y2": EFF}, RAMP),
           "doesn't start on the effective date"), True)
expect("a not-yet-started schedule that was invoiced fails",
       has(vb.check(ramp_cancel, [invoice(y1_credit + [line(-25, "2027-05-01", "Y2")], MEMO)], EFF, 2,
                    {"Y2": Y2}, RAMP), "isn't billable by today but was invoiced"), True)
expect("periods before a future start are zero", vb.periods_started(Y2, vb.TODAY, "Month", 1), 0)

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

# Netted lines: a group's schedules billed as lines with no BillingScheduleId (early renewal).
def gsched(qty, sid, grp="G1", **kw):
    return dict(sched(qty, sid, **kw), BillingScheduleGroupId=grp)


def gline(amount, start, grp="G1"):
    return {"BillingScheduleId": None, "BillingScheduleGroupId": grp, "ChargeAmount": amount,
            "InvoiceLineStartDate": start}


early = [gsched(1, "REN"), gsched(-1, "REF")]
netted = [gline(0, d) for d in (AUG, SEP, OCT)]
expect("early renewal netted to zero passes", vb.check(early, [invoice(netted)], EFF, 2), [])
expect("netted lines that don't net to the schedules fail",
       has(vb.check(early, [invoice([gline(5, AUG)] + netted[1:])], EFF, 2), "netted lines of group G1 billed"), True)
expect("netted lines from another group are stray",
       has(vb.check(early, [invoice(netted + [gline(0, AUG, "G2")])], EFF, 2), "outside the change"), True)
expect("renew-early shape: one refund and a renewal", vb.check_shape("renew-early", early, oa, ACC), [])
expect("renew-early without a refund fails", bool(vb.check_shape("renew-early", early[:1], oa, ACC)), True)
expect("billing-frequency shape: one out, one in", vb.check_shape("billing-frequency", swap_s, oa, ACC), [])

# Usage-resource schedules bill through rating and are left out of the check.
usage = dict(sched(10, "UR", period=0.0), UsageResourceId="1BR0")
expect("a usage-resource schedule is skipped", vb.check([sched(1), usage], [invoice(lines_for(270))], EFF, 2), [])

# complete_schedules(zero_lines=True) waits on a field amendment's quantity-0 line.
def fake_lines(soql_seen):
    def q(org, soql):
        soql_seen.append(soql)
        if "FROM OrderItemDetail" in soql:
            return []
        if "FROM OrderItem" in soql:
            return [{"Id": "L0"}]
        return []
    return q


seen = []
vb.sf_query, real_sleep, vb.time.sleep = fake_lines(seen), vb.time.sleep, (lambda s: None)
real_sched, vb.schedules = vb.schedules, lambda org, ids: [{"Id": "B1", "ReferenceEntityItemId": "L0"}]
vb.complete_schedules("o", ["801A"], zero_lines=True)
expect("zero_lines drops the quantity filter",
       any("FROM OrderItem " in q_ and "Quantity != 0" not in q_ for q_ in seen), True)
vb.sf_query, vb.time.sleep, vb.schedules = real_query, real_sleep, real_sched

# Review round: no false PASS from a late start outside a ramp, or from stray lines.
late = [sched(1, "LATE", start="2026-10-01")]
late_lines = [line(270, "2026-10-01", "LATE")]
expect("non-ramp: a schedule starting late on its own line fails",
       has(vb.check(late, [invoice(late_lines)], EFF, 2, {"LATE": dt.date(2026, 10, 1)}), "doesn't start on"), True)
expect("ramp: a late start off a segment boundary fails",
       has(vb.check(late, [invoice(late_lines)], EFF, 2, {"LATE": dt.date(2026, 10, 1)}, RAMP), "doesn't start on"),
       True)
expect("a line with neither schedule nor group fails",
       has(vb.check([sched(1)], [invoice(lines_for(270) + [gline(0, AUG, None)])], EFF, 2), "neither a schedule"), True)
expect("a schedule without a group isn't matched to orphan lines",
       has(vb.check([sched(1, "NOG")], [invoice([gline(810, AUG, None)])], EFF, 2), "NOG was not invoiced"), True)
mixed_g = [gsched(1, "OWN"), gsched(-1, "NET")]
mixed_lines = [dict(line(270, d, "OWN"), BillingScheduleGroupId="G1") for d in (AUG, SEP, OCT)] + \
              [gline(-270, d) for d in (AUG, SEP, OCT)]
expect("mixed group: own lines and netted lines both check", vb.check(mixed_g, [invoice(mixed_lines, MEMO)], EFF, 2), [])
expect("group tolerance is half a unit per line",
       vb.check(early, [invoice([gline(0.004, d) for d in (AUG, SEP, OCT)])], EFF, 2), [])
expect("and fails beyond it",
       bool(vb.check(early, [invoice([gline(0.01, d) for d in (AUG, SEP, OCT)])], EFF, 2)), True)
expect("a usage-resource schedule with lines fails",
       has(vb.check([usage], [invoice([line(5, AUG, "UR")])], EFF, 2), "usage-resource schedule UR"), True)
expect("usage schedules don't count toward the shape",
       vb.check_shape("amend-up", [sched(1), dict(usage, Quantity=-3)], oa, ACC), [])
expect("segment boundary: a year after the asset start", vb.on_segment_boundary(Y2, RAMP), True)
expect("segment boundary: not five months later", vb.on_segment_boundary(dt.date(2026, 10, 1), RAMP), False)
expect("renewal ramp: Year-2 a year after the effective date", vb.on_segment_boundary(dt.date(2027, 8, 1), RENEWAL_RAMP),
       True)
# A group ramp from a ramped renewal: segments a year on from the renewal (an asset period
# start), not from the asset's own start.
GROUP_RAMP = (dt.date(2026, 5, 1), dt.date(2026, 8, 1), dt.date(2027, 8, 1))
expect("group ramp: Year-2 credit a year after a period start", vb.on_segment_boundary(dt.date(2027, 8, 1), GROUP_RAMP),
       True)
expect("group ramp: but not from the asset start alone", vb.on_segment_boundary(dt.date(2027, 8, 1), RAMP), False)
expect("ramped renew-early isn't offered", args_error("--scenario", "renew-early", "--ramp-years", "2",
                                                      "--ramp-quantities", "1,2"), True)
expect("--ramp-years needs quantities", args_error("--scenario", "cancel", "--ramp-years", "2"), True)
expect("ramp years must be positive", args_error("--scenario", "cancel", "--asset", A18, "--ramp-years", "-1"), True)
expect("renewal ramp years must be positive", args_error("--scenario", "renew-early", "--renewal-ramp-years", "0"),
       True)
expect("ramp quantities must be at least 1",
       args_error("--scenario", "cancel", "--ramp-years", "2", "--ramp-quantities", "0,2"), True)
expect("ramp amend-down needs Year-1 of 2 or more",
       args_error("--scenario", "amend-down", "--ramp-years", "2", "--ramp-quantities", "1,2"), True)
# A ramp cancel must credit every remaining segment in full (Codex on #640).
Y2_START = dt.date(2027, 5, 1)
PERIODS = vb.state_periods([
    {"StartDate": "2026-05-01T00:00:00.000+0000", "EndDate": "2027-04-30T23:59:59.000+0000", "Quantity": 1},
    {"StartDate": "2027-05-01T00:00:00.000+0000", "EndDate": "2028-04-30T23:59:59.000+0000", "Quantity": 2}])
expect("state periods parse to dates", PERIODS[1], (Y2_START, dt.date(2028, 4, 30), 2.0))
cx_y1 = dict(sched(-1, "C1"), BillingScheduleEndDate="2027-04-30")
cx_y2 = dict(sched(-2, "C2", start=Y2_START.isoformat()), BillingScheduleEndDate="2028-04-30")
expect("ramp cancel crediting both segments passes", vb.check_ramp_cancel([cx_y1, cx_y2], EFF, PERIODS), [])
expect("ramp cancel crediting only the current segment fails",
       has(vb.check_ramp_cancel([cx_y1], EFF, PERIODS), "from 2027-05-01 uncredited"), True)
expect("ramp cancel with no credit from the effective date fails",
       has(vb.check_ramp_cancel([cx_y2], EFF, PERIODS), "from 2026-08-01 uncredited"), True)
expect("a partial credit of a later segment fails",
       has(vb.check_ramp_cancel([cx_y1, dict(cx_y2, Quantity=-1)], EFF, PERIODS), "credited -1, expected -2"), True)
expect("a duplicated later credit fails",
       has(vb.check_ramp_cancel([cx_y1, cx_y2, dict(cx_y2, Id="C3")], EFF, PERIODS), "credited -4, expected -2"), True)
expect("a credit ending before its segment's end fails (Codex on #640)",
       has(vb.check_ramp_cancel([dict(cx_y1, BillingScheduleEndDate="2026-08-31"), cx_y2], EFF, PERIODS),
           "ends 2026-08-31, expected the segment's end 2027-04-30"), True)
expect("a credit off the segment boundaries fails",
       has(vb.check_ramp_cancel([cx_y1, cx_y2, sched(-1, "C3", start="2027-01-01")], EFF, PERIODS),
           "off the ramp's segment boundaries"), True)
expect("zero-quantity and usage schedules don't count",
       vb.check_ramp_cancel([cx_y1, cx_y2, sched(0, "Z"), dict(sched(-1, "U", start="2027-01-01"), UsageResourceId="UR")],
                            EFF, PERIODS), [])
# A group ramp made by a ramped renewal: segments from the renewal (08-01), cancel effective 09-01.
RENEWED = vb.state_periods([
    {"StartDate": "2026-05-01", "EndDate": "2026-07-31", "Quantity": 1},
    {"StartDate": "2026-08-01", "EndDate": "2027-07-31", "Quantity": 1},
    {"StartDate": "2027-08-01", "EndDate": "2028-07-31", "Quantity": 1}])
SEP1 = dt.date(2026, 9, 1)
expect("renewed group ramp cancel passes",
       vb.check_ramp_cancel([dict(sched(-1, "R1", start="2026-09-01"), BillingScheduleEndDate="2027-07-31"),
                             dict(sched(-1, "R2", start="2027-08-01"), BillingScheduleEndDate="2028-07-31")],
                            SEP1, RENEWED), [])
# Billing frequency: measured Month/1 out, Quarter/1 in (Codex on #640).
quarterly_in = dict(sched(1, "QI"), BillingTermUnit="Quarter", BillingTerm=1)
# Quantities: the change moves exactly what the scenario asked for.
expect("amend-up +1 passes", vb.check_quantities("amend-up", [sched(1)], 1), [])
expect("amend-up +2 fails", bool(vb.check_quantities("amend-up", [sched(2)], 1)), True)
expect("amend-down -1 passes in UI mode", vb.check_quantities("amend-down", [sched(-1)], None), [])
expect("a cancel of the full quantity passes", vb.check_quantities("cancel", [sched(-2)], 2), [])
expect("a cancel of half the quantity fails", bool(vb.check_quantities("cancel", [sched(-1)], 2)), True)
expect("a swap of the full quantity passes", vb.check_quantities("swap", [sched(-1, "O"), sched(1, "I")], 1), [])
expect("UI mode skips the full-quantity checks", vb.check_quantities("cancel", [sched(-1)], None), [])
expect("swap products match", vb.check_swap_products([sched(-1, "O"), sched(1, "I")], {"O": "A", "I": "B"}, "A", "B"),
       [])
expect("a swap to the wrong product fails",
       has(vb.check_swap_products([sched(-1, "O"), sched(1, "I")], {"O": "A", "I": "C"}, "A", "B"), "bills C"), True)
expect("Monthly -> Quarterly passes", vb.check_frequency([sched(-1, "MO"), quarterly_in], "Quarterly"), [])
expect("Month/3 counts as Quarterly",
       vb.check_frequency([sched(-1, "MO"), dict(quarterly_in, BillingTermUnit="Month", BillingTerm=3)], "Quarterly"),
       [])
expect("an unchanged Monthly cadence fails", has(vb.check_frequency([sched(-1, "MO"), sched(1, "MI")], "Quarterly"),
                                                 "incoming schedule MI"), True)
expect("the wrong new cadence fails", bool(vb.check_frequency([sched(-1, "MO"), quarterly_in], "Annual")), True)
# A segment that ended before today bills only to its end (Codex on #640): Aug only, not Aug-Oct.
ended = dict(sched(-1, "E1"), BillingScheduleEndDate="2026-08-31")
expect("a ramp schedule ending before today counts periods to its end",
       vb.check([ended], [invoice([line(-270, AUG, "E1")], MEMO)], EFF, 2, ramp_anchors=RAMP), [])
expect("and still fails if it bills past its end",
       bool(vb.check([ended], [invoice(lines_for(-270, "E1"), MEMO)], EFF, 2, ramp_anchors=RAMP)), True)
# A ramped renewal must have a renewal schedule from each yearly segment start (Codex on #640).
expect("a 2-year ramped renewal with both segments passes",
       vb.check_renewal_ramp([sched(1, "N1"), sched(1, "N2", start="2027-08-01"), sched(-1, "RF")], EFF, 2), [])
expect("a 2-year ramped renewal missing Year 2 fails",
       has(vb.check_renewal_ramp([sched(1, "N1"), sched(-1, "RF")], EFF, 2), "no segment from 2027-08-01"), True)
expect("a duplicated renewal segment fails",
       has(vb.check_renewal_ramp([sched(1, "N1"), sched(1, "N1B"), sched(1, "N2", start="2027-08-01")], EFF, 2),
           "2 schedules from 2026-08-01"), True)
expect("an expired ramp renewed as a ramp fails the one-year rule",
       has(vb.check_renewal_ramp([sched(1, "N1"), sched(1, "N2", start="2027-08-01")], EFF, 1), "off the 1-year"),
       True)
plain_ended = dict(sched(-1, "P1"), BillingScheduleEndDate="2026-08-31")
expect("outside ramp mode a schedule ending early still fails on its amount",
       bool(vb.check([plain_ended], [invoice([line(-270, AUG, "P1")], MEMO)], EFF, 2)), True)
expect("a renewal schedule off the segment starts fails",
       has(vb.check_renewal_ramp([sched(1, "N1"), sched(1, "N2", start="2027-05-01")], EFF, 2), "off the 2-year"),
       True)
expect("a ramp amend with a zero-quantity later segment passes",
       vb.check_ramp_amend([sched(1, "A1"), sched(0, "A2", start=Y2_START.isoformat())], EFF), [])
expect("a ramp amend that changes a later segment fails",
       has(vb.check_ramp_amend([sched(1, "A1"), sched(1, "A2", start=Y2_START.isoformat())], EFF), "A2"), True)
expect("ramps have no prepare-only mode",
       args_error("--scenario", "cancel", "--prepare-only", "--ramp-years", "2", "--ramp-quantities", "1,2"), True)
expect("--ramp-kind needs a ramp build", args_error("--scenario", "cancel", "--ramp-kind", "group"), True)
expect("--ramp-kind doesn't apply to an existing asset",
       args_error("--scenario", "cancel", "--asset", A18, "--ramp-years", "2", "--ramp-kind", "group"), True)
expect("ramps have no UI-order mode",
       args_error("--scenario", "cancel", "--asset", A18, "--order", O18, "--ramp-years", "2"), True)
expect("a no-op Monthly frequency change is refused",
       args_error("--scenario", "billing-frequency", "--to-frequency", "Monthly"), True)

if _failures:
    print("FAIL")
    for f in _failures:
        print(f"  {f}")
    sys.exit(1)
print("PASS test_verify_backdated_billing")
