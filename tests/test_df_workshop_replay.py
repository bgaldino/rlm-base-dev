#!/usr/bin/env python3
"""Offline unit tests for the DF workshop capture/replay scripts.

Two pure/near-pure pieces need pinning against regression without an org:

  1. insert_workshop_quotes._partition_ramp_lines -- splits a quote's lines into
     ramp groups (by RampIdentifier) + plain lines, sorts each group by StartDate,
     and picks the primary. This is the core of the full multi-ramp/mixed replay:
     a wrong split silently drops or mis-groups segments.
  2. extract_workshop_quotes.extract_anchors -- must FAIL on a duplicate seed
     name (not silently pick one), mirroring the quote-name ambiguity guard. We
     stub the sf CLI layer so this runs with no org.

Run:  python tests/test_df_workshop_replay.py   (no org, stdlib only)
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_DF = os.path.join(_HERE, "..", "scripts", "df_workshop")


def _load(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(_DF, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ins = _load("df_insert", "insert_workshop_quotes.py")
ext = _load("df_extract", "extract_workshop_quotes.py")

_failures = []


def check(label, got, want):
    if got != want:
        _failures.append(f"{label}: got {got!r}, want {want!r}")


def expect_raises(label, exc, fn):
    try:
        fn()
    except exc:
        return
    except Exception as e:  # noqa: BLE001 - wrong exception type is a failure
        _failures.append(f"{label}: raised {type(e).__name__}, want {exc.__name__}")
        return
    _failures.append(f"{label}: did not raise {exc.__name__}")


def _line(sku, rid=None, primary=False, start=None, qty=1, seg=None):
    ln = {"Quantity": qty, "_keys": {"Product2Key": sku}}
    if rid is not None:
        ln["RampIdentifier"] = rid
    if primary:
        ln["IsPrimarySegment"] = True
    if start is not None:
        ln["StartDate"] = start
    if seg is not None:
        ln["SegmentName"] = seg
    return ln


# ── _partition_ramp_lines: single ramp (the current shipped data shape) ─────
single = {"lineItems": [
    _line("AI", "R1", start="2027-01-01", seg="Y1", primary=True),
    _line("AI", "R1", start="2028-01-01", seg="Y2"),
    _line("AI", "R1", start="2029-01-01", seg="Y3"),
]}
plain, groups = ins._partition_ramp_lines(single)
check("single: no plain lines", plain, [])
check("single: one group", len(groups), 1)
check("single: 3 segments", len(groups[0]["segs"]), 3)
check("single: primary is Y1", groups[0]["primary"]["SegmentName"], "Y1")

# ── multiple ramp groups in one quote ───────────────────────────────────────
multi = {"lineItems": [
    _line("AI", "R1", start="2027-01-01", seg="A1", primary=True),
    _line("DB", "R2", start="2027-01-01", seg="B1", primary=True),
    _line("AI", "R1", start="2028-01-01", seg="A2"),
    _line("DB", "R2", start="2028-01-01", seg="B2"),
]}
plain, groups = ins._partition_ramp_lines(multi)
check("multi: no plain", plain, [])
check("multi: two groups", len(groups), 2)
check("multi: group order preserved (R1 first)", [g["rid"] for g in groups], ["R1", "R2"])
check("multi: R1 has 2 segs", len(groups[0]["segs"]), 2)
check("multi: R2 has 2 segs", len(groups[1]["segs"]), 2)

# ── mixed: plain non-ramp lines coexist with a ramp group ───────────────────
mixed = {"lineItems": [
    _line("SVC"),                                              # plain, no rid
    _line("AI", "R1", start="2027-01-01", seg="Y1", primary=True),
    _line("AI", "R1", start="2028-01-01", seg="Y2"),
    _line("HW"),                                               # plain, no rid
]}
plain, groups = ins._partition_ramp_lines(mixed)
check("mixed: two plain lines", [p["_keys"]["Product2Key"] for p in plain], ["SVC", "HW"])
check("mixed: one ramp group", len(groups), 1)
check("mixed: ramp group has 2 segs", len(groups[0]["segs"]), 2)

# ── primary fallback: no IsPrimarySegment -> earliest StartDate ─────────────
noflag = {"lineItems": [
    _line("AI", "R1", start="2029-01-01", seg="Y3"),
    _line("AI", "R1", start="2027-01-01", seg="Y1"),
    _line("AI", "R1", start="2028-01-01", seg="Y2"),
]}
_, groups = ins._partition_ramp_lines(noflag)
check("fallback: segs sorted by StartDate", [s["SegmentName"] for s in groups[0]["segs"]],
      ["Y1", "Y2", "Y3"])
check("fallback: primary = earliest when no flag", groups[0]["primary"]["SegmentName"], "Y1")

# ── all plain (no ramp at all): partition yields no groups ──────────────────
allplain = {"lineItems": [_line("A"), _line("B")]}
plain, groups = ins._partition_ramp_lines(allplain)
check("allplain: two plain", len(plain), 2)
check("allplain: no groups", groups, [])


# ── _is_real_id: dry-run placeholders must never reach a SOQL Id filter ─────
check("real 18-char id", ins._is_real_id("001gw0000012345AAA"), True)
check("real 15-char id", ins._is_real_id("001gw0000012345"), True)
check("dry account placeholder", ins._is_real_id("[dry-new-account]"), False)
check("dry contact placeholder", ins._is_real_id("[dry-new-contact]"), False)
check("dry opp placeholder", ins._is_real_id("[dry-new-opp]"), False)
check("none is not real", ins._is_real_id(None), False)
check("empty is not real", ins._is_real_id(""), False)


# ── replay_ramp_quote guards: refuse cases the ordinal match can't do safely ─
# Both guards fire before any org call, so no stubbing is needed. A dict header is
# enough — they raise before _line_record / _place are reached.
def _ramp_spec(lines, attrs=None):
    spec = {"name": "T", "lineItems": lines}
    if attrs:
        spec["childRecords"] = {"QuoteLineItemAttribute": attrs}
    return spec


# Guard A: a ramp/mixed quote carrying configured attributes is refused (not
# silently dropped, which would also wedge _assert_complete on later runs).
expect_raises("ramp + QLIA -> InsertError", ins.InsertError,
              lambda: ins.replay_ramp_quote(
                  "org", _ramp_spec(
                      [_line("AI", "R1", start="2027-01-01", seg="Y1", primary=True),
                       _line("AI", "R1", start="2028-01-01", seg="Y2")],
                      attrs=[{"AttributeName": "Color"}]),
                  header={}, pricebook_name="PB", currency="USD", dry_run=True))

# Guard B: two ramp groups sharing a SKU in one quote defeat the SKU-verified
# ordinal match -> refuse.
expect_raises("same-SKU multi-ramp -> InsertError", ins.InsertError,
              lambda: ins.replay_ramp_quote(
                  "org", _ramp_spec(
                      [_line("AI", "R1", start="2027-01-01", seg="A1", primary=True),
                       _line("AI", "R2", start="2027-01-01", seg="B1", primary=True),
                       _line("AI", "R1", start="2028-01-01", seg="A2"),
                       _line("AI", "R2", start="2028-01-01", seg="B2")]),
                  header={}, pricebook_name="PB", currency="USD", dry_run=True))

# Guard B also fires when a plain line shares the primary's SKU.
expect_raises("plain line shares primary SKU -> InsertError", ins.InsertError,
              lambda: ins.replay_ramp_quote(
                  "org", _ramp_spec(
                      [_line("AI"),                                            # plain, same SKU
                       _line("AI", "R1", start="2027-01-01", seg="Y1", primary=True),
                       _line("AI", "R1", start="2028-01-01", seg="Y2")]),
                  header={}, pricebook_name="PB", currency="USD", dry_run=True))

# Distinct-SKU multi-ramp (+ distinct-SKU plain) passes both guards: dry_run returns
# None after printing, without raising. Stub resolve_pbe so building the (previewed)
# place payload does not touch an org.
def _distinct_sku_dry_run():
    orig = ins.resolve_pbe
    ins.resolve_pbe = lambda org, sku, pb, cur, sm: {
        "pbeId": f"pbe-{sku}", "productId": f"prod-{sku}", "unitPrice": 100}
    try:
        return ins.replay_ramp_quote(
            "org", _ramp_spec(
                [_line("SVC"),
                 _line("AI", "R1", start="2027-01-01", seg="A1", primary=True),
                 _line("DB", "R2", start="2027-01-01", seg="B1", primary=True),
                 _line("AI", "R1", start="2028-01-01", seg="A2")]),
            header={}, pricebook_name="PB", currency="USD", dry_run=True)
    finally:
        ins.resolve_pbe = orig


check("distinct-SKU multi-ramp passes guards", _distinct_sku_dry_run(), None)


# ── extract_anchors: FAIL on duplicate seed name (not silently pick one) ────
# Stub the sf query layer so no org is touched. extract_anchors resolves each
# seed name via ext.sf_query; a >1 row result must raise ExtractError.
def _run_anchors(opp_rows, acct_rows, seed_opps=(), seed_accounts=()):
    calls = {"opp": opp_rows, "acct": acct_rows}

    def fake_query(org, soql):
        # The seed-resolution queries filter by Name; the fetch/resolve_key queries
        # filter by Id. Both hit the same tables -- return the canned rows either way.
        if "FROM Opportunity" in soql:
            return calls["opp"]
        if "FROM Account" in soql:
            return [{**r, "Name": r.get("Name", "Acme")} for r in calls["acct"]]
        return []

    orig_query, orig_fields = ext.sf_query, ext.queryable_fields
    ext.sf_query = fake_query
    ext.queryable_fields = lambda org, sobject: ["Id", "Name", "AccountId"]
    try:
        return ext.extract_anchors("stub-org", quotes=[], seed_opps=seed_opps,
                                   seed_accounts=seed_accounts)
    finally:
        ext.sf_query, ext.queryable_fields = orig_query, orig_fields


expect_raises("dup seed opp -> ExtractError", ext.ExtractError,
              lambda: _run_anchors(
                  opp_rows=[{"Id": "1", "AccountId": "a"}, {"Id": "2", "AccountId": "b"}],
                  acct_rows=[], seed_opps=["Dup Opp"]))

expect_raises("dup seed account -> ExtractError", ext.ExtractError,
              lambda: _run_anchors(
                  opp_rows=[], acct_rows=[{"Id": "1"}, {"Id": "2"}],
                  seed_accounts=["Dup Acct"]))

expect_raises("missing seed opp -> ExtractError", ext.ExtractError,
              lambda: _run_anchors(opp_rows=[], acct_rows=[], seed_opps=["Gone"]))

# A single unambiguous match resolves cleanly (opp pulls its account in too).
res = _run_anchors(opp_rows=[{"Id": "o1", "AccountId": "acc1"}],
                   acct_rows=[{"Id": "acc1", "Name": "Acme"}],
                   seed_opps=["Starter"])
check("single seed opp: opp captured", len(res["opportunities"]), 1)
check("single seed opp: its account pulled in", len(res["accounts"]), 1)


if _failures:
    print("FAIL — df workshop replay:")
    for f in _failures:
        print("  -", f)
    sys.exit(1)
print("OK — df workshop replay: all cases passed")
