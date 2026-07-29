#!/usr/bin/env python3
"""Offline unit tests for the self-contained ``scripts/ramp_deals/`` toolkit.

No org, no ``sf`` CLI, no pytest — a plain ``check()`` runner matching
``tests/test_expression_sets_toolkit.py``. Exercises the package's PURE modules:
``_schedule`` (calendar-month arithmetic, contiguity, the segment ceiling),
``_payload`` (graph shape, enum + read-only-field rejection for the six
groupRampAction verbs, place-create, clone), and ``_verify`` (status
classification + the read-back ramp invariants).

Run:  python tests/test_ramp_deals_toolkit.py
Exit: 0 = all pass, 1 = one or more failures.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ramp_deals._schedule import (  # noqa: E402
    MAX_SEGMENTS_EXCLUDING_TRIAL,
    ScheduleError,
    add_calendar_months,
    assert_contiguous,
    build_schedule,
    paid_segment_count,
    segment_end,
)
from scripts.ramp_deals._payload import (  # noqa: E402
    CLONE_PATH,
    PLACE_PATH,
    PayloadError,
    build_clone_segment,
    build_edit_group,
    build_group_ramp_action,
    build_place_create,
    make_record,
)
from scripts.ramp_deals._verify import (  # noqa: E402
    FAILURE_STATUSES,
    IN_FLIGHT_STATUSES,
    SUCCESS_STATUSES,
    classify_status,
    verify_quote,
)

_PASS = 0
_FAIL = 0


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {label}" + (f"  ({detail})" if detail else ""))


def _raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
        return False
    except exc:
        return True
    except Exception:  # noqa: BLE001 - wrong exception type is still a failure
        return False


# --------------------------------------------------------------------------- #
# _schedule
# --------------------------------------------------------------------------- #

def test_schedule():
    print("test_schedule")

    # Calendar-month arithmetic, not 365 days.
    check("Jan 1 + 12 months = next Jan 1",
          add_calendar_months(date(2026, 1, 1), 12) == date(2027, 1, 1))
    check("Jan 31 + 1 month clamps to Feb 28 (non-leap)",
          add_calendar_months(date(2026, 1, 31), 1) == date(2026, 2, 28))
    check("Jan 31 + 1 month clamps to Feb 29 (leap)",
          add_calendar_months(date(2028, 1, 31), 1) == date(2028, 2, 29))
    # A yearly segment starting mid-leap-year is NOT 365 days.
    s_end = segment_end(date(2028, 3, 1), 12)  # spans a non-leap-year window
    check("Yearly segment end is day-before next-year start",
          s_end == date(2029, 2, 28), str(s_end))

    # Uniform yearly, 3 paid segments, contiguous.
    segs = build_schedule(start_date="2026-01-01", segment_type="Yearly",
                          segment_count=3)
    check("3 yearly segments built", len(segs) == 3, str(len(segs)))
    check("segment 1 starts on requested date", segs[0]["start_date"] == "2026-01-01")
    check("segment 1 ends 2026-12-31", segs[0]["end_date"] == "2026-12-31",
          segs[0]["end_date"])
    check("segment 2 starts 2027-01-01", segs[1]["start_date"] == "2027-01-01",
          segs[1]["start_date"])
    check("sort orders are 1..3", [s["sort_order"] for s in segs] == [1, 2, 3])
    assert_contiguous(segs)  # raises on failure
    check("build_schedule output is contiguous", True)
    check("paid_segment_count = 3", paid_segment_count(segs) == 3)

    # Trial prepended: sort orders shift, trial excluded from paid count.
    with_trial = build_schedule(start_date="2026-01-01", segment_type="Yearly",
                                segment_count=2, trial_months=1)
    check("trial + 2 paid = 3 segments", len(with_trial) == 3)
    check("trial is sort_order 1 and is_trial", with_trial[0]["sort_order"] == 1
          and with_trial[0]["is_trial"] is True)
    check("trial type is FreeTrial", with_trial[0]["segment_type"] == "FreeTrial",
          with_trial[0]["segment_type"])
    check("first paid segment follows the trial contiguously",
          with_trial[1]["start_date"] == "2026-02-01", with_trial[1]["start_date"])
    check("paid_segment_count excludes trial", paid_segment_count(with_trial) == 2)
    assert_contiguous(with_trial)

    # Ceiling: 12 paid ok, 13 rejected; the trial does not count against it.
    ok = build_schedule(start_date="2026-01-01", segment_type="Yearly",
                        segment_count=MAX_SEGMENTS_EXCLUDING_TRIAL, trial_months=1)
    check("12 paid + trial is allowed", paid_segment_count(ok) == 12)
    check("13 paid segments rejected",
          _raises(ScheduleError, build_schedule, start_date="2026-01-01",
                  segment_type="Yearly", segment_count=13))

    # Bad inputs.
    check("unknown segment type rejected",
          _raises(ScheduleError, build_schedule, start_date="2026-01-01",
                  segment_type="Trial", segment_count=1))
    check("segment_type=FreeTrial rejected (use trial_months)",
          _raises(ScheduleError, build_schedule, start_date="2026-01-01",
                  segment_type="FreeTrial", segment_count=1))
    check("segment_count 0 rejected",
          _raises(ScheduleError, build_schedule, start_date="2026-01-01",
                  segment_type="Custom", segment_count=0))
    check("bad date string rejected",
          _raises(ScheduleError, build_schedule, start_date="not-a-date",
                  segment_type="Yearly", segment_count=1))

    # Non-contiguous detection.
    check("gap between segments detected",
          _raises(ScheduleError, assert_contiguous, [
              {"sort_order": 1, "start_date": "2026-01-01", "end_date": "2026-06-30"},
              {"sort_order": 2, "start_date": "2026-07-05", "end_date": "2026-12-31"},
          ]))


# --------------------------------------------------------------------------- #
# _payload
# --------------------------------------------------------------------------- #

def _sample_line(sku_id="01t000000000001", pbe="01u000000000001"):
    return {"Product2Id": sku_id, "PricebookEntryId": pbe,
            "UnitPrice": 100.0, "Quantity": 1, "StartDate": "2026-01-01",
            "EndDate": "2026-12-31"}


def test_payload_place_create():
    print("test_payload_place_create")
    body = build_place_create(
        account_id="001000000000001", opportunity_id="006000000000001",
        pricebook_id="01s000000000001", lines=[_sample_line(), _sample_line("01t2")],
        quote_name="Ramp", start_date="2026-01-01")
    recs = body["graph"]["records"]
    check("place path pinned to v68.0", "/v68.0/" in PLACE_PATH, PLACE_PATH)
    check("pricingPref defaults to System", body["pricingPref"] == "System")
    check("first record is the Quote POST",
          recs[0]["record"]["attributes"] == {"type": "Quote", "method": "POST"})
    check("second record is the group POST",
          recs[1]["record"]["attributes"]["type"] == "QuoteLineGroup")
    check("group references the quote",
          recs[1]["record"]["QuoteId"] == "@{refQuote.id}")
    check("group is plain CPQQuoteGroup at create (EditGroup ramps it later)",
          recs[1]["record"]["Type"] == "CPQQuoteGroup")
    check("two line records present",
          sum(1 for r in recs if r["record"]["attributes"]["type"] == "QuoteLineItem") == 2)
    line0 = next(r for r in recs if r["referenceId"] == "refLine0")["record"]
    check("line wires QuoteId ref", line0["QuoteId"] == "@{refQuote.id}")
    check("line wires QuoteLineGroupId ref", line0["QuoteLineGroupId"] == "@{refGroup.id}")

    # Guards.
    check("empty lines rejected",
          _raises(PayloadError, build_place_create, account_id="001", lines=[]))
    check("missing account rejected",
          _raises(PayloadError, build_place_create, account_id="", lines=[_sample_line()]))
    check("read-only QuoteLineItem field rejected",
          _raises(PayloadError, build_place_create, account_id="001",
                  lines=[{**_sample_line(), "RampIdentifier": "RDIxxx"}]))
    check("caller-set QuoteId on a line rejected",
          _raises(PayloadError, build_place_create, account_id="001",
                  lines=[{**_sample_line(), "QuoteId": "0Q0"}]))


def test_payload_edit_group():
    print("test_payload_edit_group")
    body = build_edit_group(quote_id="0Q0x", group_id="1C9x",
                            start_date="2026-01-01", end_date="2026-12-31",
                            segment_type="Custom", sort_order=1)
    check("action is EditGroup", body["groupRampAction"] == "EditGroup")
    recs = body["graph"]["records"]
    quote_rec = next(r for r in recs if r["record"]["attributes"]["type"] == "Quote")
    check("quote is PATCH with id",
          quote_rec["record"]["attributes"] == {"type": "Quote", "method": "PATCH", "id": "0Q0x"})
    grp = next(r for r in recs if r["record"]["attributes"]["type"] == "QuoteLineGroup")
    check("group PATCH sets IsRamped true", grp["record"]["IsRamped"] is True)
    check("group PATCH carries SegmentType", grp["record"]["SegmentType"] == "Custom")
    check("group PATCH carries the group id",
          grp["record"]["attributes"]["id"] == "1C9x")
    # Enum guard.
    check("bad segment type rejected",
          _raises(PayloadError, build_edit_group, quote_id="0Q0x", group_id="1C9x",
                  start_date="2026-01-01", end_date="2026-12-31", segment_type="Trial"))
    # PATCH without an id is rejected.
    check("PATCH record without id rejected",
          _raises(PayloadError, make_record, "ref", "Quote", "PATCH"))


def test_payload_clone_and_actions():
    print("test_payload_clone_and_actions")
    clone = build_clone_segment(quote_id="0Q0x", last_segment_group_id="1C9last")
    check("clone path pinned v68.0", "/v68.0/" in CLONE_PATH)
    check("clone recordIds is a single-element list",
          clone["recordIds"] == ["1C9last"])
    check("clone salesTransactionId set", clone["salesTransactionId"] == "0Q0x")
    check("clone lineScope defaults AllLines",
          clone["options"]["lineScope"] == "AllLines")
    check("RampedLinesOnly accepted",
          build_clone_segment(quote_id="0Q0x", last_segment_group_id="x",
                              line_scope="RampedLinesOnly")["options"]["lineScope"]
          == "RampedLinesOnly")
    check("bad lineScope rejected",
          _raises(PayloadError, build_clone_segment, quote_id="0Q0x",
                  last_segment_group_id="x", line_scope="SomeLines"))

    # Generic groupRampAction body.
    rec = make_record("refGroup", "QuoteLineGroup", "PATCH",
                      {"SortOrder": 2}, record_id="1C9x")
    body = build_group_ramp_action("DeleteSegment", records=[rec])
    check("DeleteSegment body carries the action",
          body["groupRampAction"] == "DeleteSegment")
    check("EditGroup routed away from generic builder",
          _raises(PayloadError, build_group_ramp_action, "EditGroup", records=[rec]))
    check("unknown action rejected",
          _raises(PayloadError, build_group_ramp_action, "Frobnicate", records=[rec]))
    check("empty records rejected",
          _raises(PayloadError, build_group_ramp_action, "AddProducts", records=[]))
    check("read-only field rejected via make_record",
          _raises(PayloadError, make_record, "r", "QuoteLineItem", "PATCH",
                  {"TotalPrice": 5}, record_id="x"))


# --------------------------------------------------------------------------- #
# _verify
# --------------------------------------------------------------------------- #

def test_verify_status_sets():
    print("test_verify_status_sets")
    check("CompletedWithTax is success", classify_status("CompletedWithTax") == "success")
    check("TaxCalculationSuccess is success",
          classify_status("TaxCalculationSuccess") == "success")
    check("CloneInProgress is in-flight (264-new)",
          classify_status("CloneInProgress") == "in_flight")
    check("CloneFailed is failure (264-new)",
          classify_status("CloneFailed") == "failure")
    check("GroupRampConfigurationFailed is failure",
          classify_status("GroupRampConfigurationFailed") == "failure")
    check("unknown status is 'unknown', not silently success",
          classify_status("SomeNewStatusValue") == "unknown")
    # Sets are disjoint.
    check("success/failure/in-flight sets are disjoint",
          not (SUCCESS_STATUSES & FAILURE_STATUSES)
          and not (SUCCESS_STATUSES & IN_FLIGHT_STATUSES)
          and not (FAILURE_STATUSES & IN_FLIGHT_STATUSES))


def _good_quote():
    return {
        "Id": "0Q0x", "TotalPrice": 200.0, "TotalPriceOverride": None,
        "groups": [
            {"Id": "g1", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 1,
             "StartDate": "2026-01-01", "EndDate": "2026-12-31",
             "lines": [{"Id": "l1", "RampIdentifier": "RDI1", "SegmentIdentifier": "SEG1",
                        "TotalPrice": 100.0}]},
            {"Id": "g2", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 2,
             "StartDate": "2027-01-01", "EndDate": "2027-12-31",
             "lines": [{"Id": "l2", "RampIdentifier": "RDI1", "SegmentIdentifier": "SEG2",
                        "TotalPrice": 100.0}]},
        ],
    }


def test_verify_quote():
    print("test_verify_quote")
    r = verify_quote(_good_quote(), expected_segments=2)
    check("a well-formed ramped quote passes", r.passed, r.format_report())

    # No ramped group.
    r = verify_quote({"groups": [{"Id": "g", "IsRamped": False}]})
    check("no ramped group fails", not r.passed)

    # Missing identifiers (the raw-IsRamped-PATCH smell, DO-NOT #6).
    q = _good_quote()
    q["groups"][0]["lines"][0]["SegmentIdentifier"] = ""
    r = verify_quote(q)
    check("missing SegmentIdentifier fails (bypassed groupRampAction)", not r.passed)

    # Non-contiguous.
    q = _good_quote()
    q["groups"][1]["StartDate"] = "2027-02-01"
    r = verify_quote(q)
    check("non-contiguous segments fail", not r.passed)

    # Expected-count mismatch.
    r = verify_quote(_good_quote(), expected_segments=3)
    check("wrong expected_segments fails", not r.passed)

    # TCV mismatch beyond tolerance.
    q = _good_quote()
    q["TotalPrice"] = 500.0
    r = verify_quote(q)
    check("TCV mismatch fails", not r.passed)

    # Override present → TCV check skipped, still passes.
    q = _good_quote()
    q["TotalPrice"] = 500.0
    q["TotalPriceOverride"] = 500.0
    r = verify_quote(q)
    check("TCV check skipped when override set", r.passed, r.format_report())


def main():
    for fn in (test_schedule, test_payload_place_create, test_payload_edit_group,
               test_payload_clone_and_actions, test_verify_status_sets,
               test_verify_quote):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
