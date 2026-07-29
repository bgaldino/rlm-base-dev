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
from scripts.ramp_deals import _payload, _resolve  # noqa: E402
from scripts.ramp_deals._resolve import ResolveError  # noqa: E402
from scripts.ramp_deals._lifecycle import (  # noqa: E402
    RampLifecycle,
    RampLifecycleError,
    _extract_id,
)
from scripts.ramp_deals._schedule import build_schedule  # noqa: E402

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


# --------------------------------------------------------------------------- #
# _resolve + _lifecycle (against a fake transport — no org)
# --------------------------------------------------------------------------- #

class FakeTransport:
    """Stand-in for _client.Transport: canned SOQL answers + recorded connect calls.

    ``soql_map`` maps a substring-of-query → the records list to return (first
    matching substring wins). ``connect`` appends (method, path, body) to
    ``self.calls`` and returns ``connect_return`` (or a value popped from a queue).
    """

    def __init__(self, soql_map=None, connect_return=None, soql_default=None,
                 dry_run=False):
        self.soql_map = soql_map or {}
        self.soql_default = soql_default
        self.connect_return = connect_return or {}
        self.dry_run = dry_run
        self.logger = lambda *a, **k: None
        self.calls = []
        self.soql_log = []

    def soql(self, query):
        self.soql_log.append(query)
        for needle, rows in self.soql_map.items():
            if needle in query:
                return rows
        if self.soql_default is not None:
            return self.soql_default
        return []

    def connect(self, method, path, body=None, **kwargs):
        self.calls.append((method, path, body))
        return self.connect_return


def test_resolve():
    print("test_resolve")
    t = FakeTransport(soql_map={
        "FROM Account": [{"Id": "001acc"}],
        "IsStandard = true": [{"Id": "01sstd"}],
        "FROM Pricebook2 WHERE Name": [{"Id": "01spb"}],
        "StockKeepingUnit": [{"Id": "01tprod"}],
        "FROM PricebookEntry": [{"Id": "01uPBE", "UnitPrice": 42.0}],
    })
    check("resolve account", _resolve.resolve_account_id("Acme", transport=t) == "001acc")
    check("resolve standard pricebook",
          _resolve.resolve_standard_pricebook_id(transport=t) == "01sstd")
    check("resolve product by SKU",
          _resolve.resolve_product_id("SKU-1", transport=t) == "01tprod")
    pbe = _resolve.resolve_pricebook_entry(product_id="01tprod", pricebook_id="01spb",
                                           transport=t)
    check("resolve PBE id+price", pbe == {"Id": "01uPBE", "UnitPrice": 42.0}, str(pbe))

    # Not-found and ambiguous.
    empty = FakeTransport(soql_default=[])
    check("account not found raises",
          _raises(ResolveError, _resolve.resolve_account_id, "Nope", transport=empty))
    dup = FakeTransport(soql_map={"FROM Account": [{"Id": "a"}, {"Id": "b"}]})
    check("ambiguous account raises",
          _raises(ResolveError, _resolve.resolve_account_id, "Dup", transport=dup))

    # Line resolution fills Product2Id / PricebookEntryId / UnitPrice and drops helper keys.
    line = _resolve.resolve_line_ids({"sku": "SKU-1", "Quantity": 2}, pricebook_id="01spb",
                                     transport=t)
    check("line gains Product2Id", line["Product2Id"] == "01tprod")
    check("line gains PricebookEntryId", line["PricebookEntryId"] == "01uPBE")
    check("line defaults UnitPrice from PBE", line["UnitPrice"] == 42.0)
    check("line keeps Quantity", line["Quantity"] == 2)
    check("line drops 'sku' helper key", "sku" not in line)
    check("line with neither id nor sku raises",
          _raises(ResolveError, _resolve.resolve_line_ids, {"Quantity": 1},
                  pricebook_id="01spb", transport=t))

    # read_quote stitches groups + lines into the _verify shape.
    rq = FakeTransport(soql_map={
        "FROM Quote WHERE Id": [{
            "Id": "0Qx", "TotalPrice": 200.0, "TotalPriceOverride": None,
            "QuoteLineGroups": {"records": [
                {"Id": "g1", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 1,
                 "StartDate": "2026-01-01", "EndDate": "2026-12-31"},
            ]}}],
        "FROM QuoteLineItem": [
            {"Id": "l1", "Product2Id": "01tprod", "QuoteLineGroupId": "g1",
             "RampIdentifier": "RDI1", "SegmentIdentifier": "SEG1", "TotalPrice": 200.0},
        ],
    })
    quote = _resolve.read_quote("0Qx", transport=rq)
    check("read_quote top-level shape",
          quote["Id"] == "0Qx" and quote["TotalPrice"] == 200.0)
    check("read_quote nests one group", len(quote["groups"]) == 1)
    check("read_quote stitches line under its group",
          quote["groups"][0]["lines"][0]["SegmentIdentifier"] == "SEG1")
    # The read-back must satisfy verify_quote (proves the shapes agree).
    check("read_quote output passes verify_quote",
          verify_quote(quote, expected_segments=1).passed)
    check("read_quote of missing quote raises",
          _raises(ResolveError, _resolve.read_quote, "nope",
                  transport=FakeTransport(soql_default=[])))


def test_lifecycle_extract_id():
    print("test_lifecycle_extract_id")
    # graphs[].graphResponse.compositeResponse[]
    resp = {"graphs": [{"graphResponse": {"compositeResponse": [
        {"referenceId": "refQuote", "body": {"id": "0Qnew"}},
        {"referenceId": "refGroup", "body": {"id": "g1new"}},
    ]}}]}
    check("extract quote id from graphs shape", _extract_id(resp, "refQuote") == "0Qnew")
    check("extract group id from graphs shape", _extract_id(resp, "refGroup") == "g1new")
    # flat compositeResponse
    check("extract from flat compositeResponse",
          _extract_id({"compositeResponse": [{"referenceId": "refQuote",
                                              "id": "0Qflat"}]}, "refQuote") == "0Qflat")
    # direct map
    check("extract from direct map", _extract_id({"refQuote": "0Qmap"}, "refQuote") == "0Qmap")
    check("missing ref returns None", _extract_id({"graphs": []}, "refQuote") is None)


def test_lifecycle_polling():
    print("test_lifecycle_polling")
    # Success on first poll.
    t = FakeTransport(soql_map={
        "CalculationStatus FROM Quote": [{"CalculationStatus": "CompletedWithTax"}]})
    lc = RampLifecycle(t, sleep=lambda *_: None)
    check("settled returns success status", lc.wait_until_settled("0Qx") == "CompletedWithTax")

    # Failure raises.
    tf = FakeTransport(soql_map={
        "CalculationStatus FROM Quote": [{"CalculationStatus": "CloneFailed"}]})
    check("failure status raises",
          _raises(RampLifecycleError, RampLifecycle(tf, sleep=lambda *_: None).wait_until_settled, "0Qx"))

    # Unknown raises (does not silently pass).
    tu = FakeTransport(soql_map={
        "CalculationStatus FROM Quote": [{"CalculationStatus": "SomethingNew"}]})
    check("unknown status raises",
          _raises(RampLifecycleError, RampLifecycle(tu, sleep=lambda *_: None).wait_until_settled, "0Qx"))

    # In-flight forever → times out.
    ti = FakeTransport(soql_map={
        "CalculationStatus FROM Quote": [{"CalculationStatus": "PriceCalculationInProgress"}]})
    lc_timeout = RampLifecycle(ti, sleep=lambda *_: None, max_wait_seconds=10,
                               poll_interval_seconds=5)
    check("perpetual in-flight times out",
          _raises(RampLifecycleError, lc_timeout.wait_until_settled, "0Qx"))

    # Dry-run short-circuits with no poll at all.
    td = FakeTransport(dry_run=True)
    check("dry-run returns nominal status without polling",
          RampLifecycle(td).wait_until_settled("0Qx") == "CompletedWithPricing")
    check("dry-run issued no SOQL", td.soql_log == [])


def test_lifecycle_build():
    print("test_lifecycle_build")
    schedule = build_schedule(start_date="2026-01-01", segment_type="Yearly",
                              segment_count=3)
    # place returns ids; every settle poll succeeds; clone-source re-read returns a group.
    t = FakeTransport(
        soql_map={
            "CalculationStatus FROM Quote": [{"CalculationStatus": "CompletedWithPricing"}],
            "IsRamped = true ORDER BY SortOrder DESC": [{"Id": "gLast", "SortOrder": 3}],
            "FROM Quote WHERE Id": [{
                "Id": "0Qx", "TotalPrice": 300.0, "TotalPriceOverride": None,
                "QuoteLineGroups": {"records": [
                    {"Id": "g1", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 1,
                     "StartDate": "2026-01-01", "EndDate": "2026-12-31"},
                    {"Id": "g2", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 2,
                     "StartDate": "2027-01-01", "EndDate": "2027-12-31"},
                    {"Id": "g3", "IsRamped": True, "SegmentType": "Yearly", "SortOrder": 3,
                     "StartDate": "2028-01-01", "EndDate": "2028-12-31"},
                ]}}],
            "FROM QuoteLineItem": [
                {"Id": f"l{i}", "Product2Id": "01tprod", "QuoteLineGroupId": g,
                 "RampIdentifier": "RDI1", "SegmentIdentifier": f"SEG{i}",
                 "TotalPrice": 100.0}
                for i, g in enumerate(("g1", "g2", "g3"), start=1)
            ],
        },
        connect_return={"graphs": [{"graphResponse": {"compositeResponse": [
            {"referenceId": "refQuote", "body": {"id": "0Qx"}},
            {"referenceId": "refGroup", "body": {"id": "g1"}},
        ]}}]},
    )
    lc = RampLifecycle(t, sleep=lambda *_: None)
    out = lc.build_ramped_quote(
        account_id="001acc", pricebook_id="01spb",
        lines=[{"Product2Id": "01tprod", "PricebookEntryId": "01uPBE",
                "UnitPrice": 100.0, "Quantity": 1}],
        schedule=schedule)
    check("build returns the quote id", out["quote_id"] == "0Qx", str(out))
    check("build verified the quote", out["verify"] and out["verify"]["passed"])
    # 1 place + 1 EditGroup + 2 clones = 4 connect calls.
    check("issued place + EditGroup + 2 clones", len(t.calls) == 4, str(len(t.calls)))
    check("first call is place",
          t.calls[0][1] == _payload.PLACE_PATH and t.calls[0][0] == "POST")
    check("last two calls are clones",
          all(c[1] == _payload.CLONE_PATH for c in t.calls[2:]))

    # Empty schedule rejected.
    check("empty schedule raises",
          _raises(RampLifecycleError, lc.build_ramped_quote, account_id="001acc",
                  pricebook_id="01spb", lines=[{"Product2Id": "x", "PricebookEntryId": "y",
                                                "UnitPrice": 1, "Quantity": 1}],
                  schedule=[]))


def test_lifecycle_single_ops():
    print("test_lifecycle_single_ops")
    settled = {"CalculationStatus FROM Quote": [{"CalculationStatus": "CompletedWithPricing"}]}

    # add_segment: reads the last group when not given one, then clones.
    t = FakeTransport(soql_map={
        **settled,
        "IsRamped = true ORDER BY SortOrder DESC": [{"Id": "gLast", "SortOrder": 2}],
    })
    lc = RampLifecycle(t, sleep=lambda *_: None)
    out = lc.add_segment(quote_id="0Qx")
    check("add_segment resolves clone source", out["cloned_from"] == "gLast", str(out))
    check("add_segment issued one clone",
          len(t.calls) == 1 and t.calls[0][1] == _payload.CLONE_PATH)

    # add_segment with an explicit source skips the lookup.
    t2 = FakeTransport(soql_map=settled)
    out2 = RampLifecycle(t2, sleep=lambda *_: None).add_segment(
        quote_id="0Qx", last_segment_group_id="gExplicit")
    check("add_segment uses explicit source", out2["cloned_from"] == "gExplicit")

    # add_segment on a non-ramped quote (no last group) raises.
    t3 = FakeTransport(soql_map=settled, soql_default=[])
    check("add_segment with no ramped segment raises",
          _raises(RampLifecycleError,
                  RampLifecycle(t3, sleep=lambda *_: None).add_segment, quote_id="0Qx"))

    # edit_segment issues one EditGroup (POST to place path) and polls.
    t4 = FakeTransport(soql_map=settled)
    out4 = RampLifecycle(t4, sleep=lambda *_: None).edit_segment(
        quote_id="0Qx", group_id="g1", start_date="2026-01-01",
        end_date="2026-12-31", segment_type="Custom")
    check("edit_segment posts to place path",
          len(t4.calls) == 1 and t4.calls[0][1] == _payload.PLACE_PATH)
    check("edit_segment carries EditGroup action",
          t4.calls[0][2]["groupRampAction"] == "EditGroup")
    check("edit_segment returns settled status", out4["status"] == "CompletedWithPricing")

    # edit_segment with a bad enum is rejected by the payload builder.
    check("edit_segment bad segment type raises",
          _raises(Exception, RampLifecycle(FakeTransport(), sleep=lambda *_: None).edit_segment,
                  quote_id="0Qx", group_id="g1", start_date="2026-01-01",
                  end_date="2026-12-31", segment_type="Trial"))

    # delete_quote issues a DELETE on the Quote sObject.
    t5 = FakeTransport()
    out5 = RampLifecycle(t5, sleep=lambda *_: None).delete_quote("0Qx")
    check("delete_quote issues a DELETE",
          t5.calls == [("DELETE", "sobjects/Quote/0Qx", None)], str(t5.calls))
    check("delete_quote reports deleted", out5["deleted"] is True)

    # Dry-run: delete is skipped and reported as not deleted.
    td = FakeTransport(dry_run=True)
    outd = RampLifecycle(td).delete_quote("0Qx")
    check("dry-run delete reports not deleted", outd["deleted"] is False)


def main():
    for fn in (test_schedule, test_payload_place_create, test_payload_edit_group,
               test_payload_clone_and_actions, test_verify_status_sets,
               test_verify_quote, test_resolve, test_lifecycle_extract_id,
               test_lifecycle_polling, test_lifecycle_build,
               test_lifecycle_single_ops):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
