"""Offline tests for the read-only billing verifier (``cli verify``).

Each fixture under ``fixtures/billing_verify/`` is a set of recorded query results,
one list of rows per object. ``RecordedClient`` answers the verifier's SOQL from
them, filtering on the ``WHERE <field> IN (...)`` clause, so the fetch path runs
too. Like the API, it refuses a selected field that a recorded row does not have, so
every fixture row lists every field the verifier selects (null where unmeasured). The
clean fixtures must pass every check; each negative test breaks one fact and asserts
that exactly the matching check fails.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import requests

from scripts.txn_data_harness import auth, cli
from scripts.txn_data_harness import verify as verify_mod
from scripts.txn_data_harness.auth import SfApiError, SfCliError
from scripts.txn_data_harness.verify import (
    CHECK_NAMES,
    VerifyError,
    _check_ids,
    fetch_records,
    ids_from_manifest,
    render_text,
    run_checks,
    split_ids,
)

FIXTURES = Path(__file__).parent / "fixtures" / "billing_verify"
LINE_INVOICES = ["3tt000000000001AAA", "3tt000000000002AAA", "3tt000000000003AAA"]
LINE_EXTRA_PAYMENTS = ["0aQ000000000002EAA"]  # Canceled, no applications
HEADER_INVOICES = ["3tt0000000000H1AAI", "3tt0000000000H2AAI"]

_SOQL_RE = re.compile(
    r"^SELECT (?P<fields>.+?) FROM (?P<obj>\w+) WHERE (?P<field>\w+) IN \((?P<ids>[^)]*)\)$"
)


def _load(name: str) -> dict:
    data = json.loads((FIXTURES / name).read_text())
    data.pop("_about", None)
    return data


class RecordedClient:
    """Answers SELECT ... WHERE f IN (...) from recorded rows; refuses any write.

    A selected or filtered field missing from a recorded row raises, as the API's
    INVALID_FIELD would, instead of answering None.
    """

    def __init__(self, data: dict):
        self.data = data
        self.queries: list[str] = []
        self.writes: list[tuple] = []

    def query(self, soql: str) -> list[dict]:
        self.queries.append(soql)
        match = _SOQL_RE.match(soql)
        assert match, f"unexpected SOQL shape: {soql}"
        wanted = {i.strip().strip("'") for i in match["ids"].split(",")}
        fields = [f.strip() for f in match["fields"].split(",")]
        out = []
        for row in self.data.get(match["obj"], []):
            unknown = [f for f in fields + [match["field"]] if f not in row]
            if unknown:
                raise AssertionError(f"{match['obj']} row {row.get('Id')} has no "
                                     f"{', '.join(unknown)}: {soql}")
            if row[match["field"]] in wanted:
                out.append({"attributes": {"type": match["obj"]},
                            **{f: row[f] for f in fields}})
        return out

    def post(self, *args):  # pragma: no cover - a call is the failure
        self.writes.append(("post", args))

    def patch(self, *args):  # pragma: no cover
        self.writes.append(("patch", args))

    def delete(self, *args):  # pragma: no cover
        self.writes.append(("delete", args))


def _row(data: dict, obj: str, row_id: str) -> dict:
    return next(r for r in data[obj] if r["Id"] == row_id)


def _verify(data: dict, invoices: list[str], payments=None, level="auto") -> dict:
    client = RecordedClient(data)
    records = fetch_records(client, invoices, payments)
    assert client.writes == []
    return run_checks(records, level)


def _line(level="auto", mutate=None) -> dict:
    data = _load("line_level.json")
    if mutate:
        mutate(data)
    return _verify(data, LINE_INVOICES, LINE_EXTRA_PAYMENTS, level)


def _header(level="auto", mutate=None) -> dict:
    data = _load("header_level.json")
    if mutate:
        mutate(data)
    return _verify(data, HEADER_INVOICES, None, level)


def _statuses(report: dict, check: str) -> set[str]:
    return {r["status"] for r in report["checks"] if r["check"] == check}


# ------------------------------------------------------------------ clean fixtures

def test_line_level_fixture_passes_every_check():
    report = _line()
    assert report["failed_checks"] == [], report["failed_checks"]
    assert report["ok"] is True
    assert (report["level"], report["level_source"]) == ("line", "records")
    assert _statuses(report, "invoice_balance") == {"pass"}
    assert _statuses(report, "payment_balance") == {"pass"}
    # INV2 has no application rows and no SettlementLevel: no evidence of its own, so
    # its level and line balances are skipped; INV1 and INV3 show line level.
    for check in ("application_level", "invoice_line_balance"):
        by_invoice = {r["subject"][:18]: r["status"] for r in report["checks"]
                      if r["check"] == check}
        assert by_invoice == {"3tt000000000001AAA": "pass", "3tt000000000002AAA": "skip",
                              "3tt000000000003AAA": "pass"}, check
    # Payments found through application rows, plus the one asked for by id.
    assert set(report["payment_ids"]) == {"0aQ000000000001EAA", "0aQ000000000002EAA"}


def test_header_level_fixture_skips_every_balance_check():
    # Header Level was never measured: only application_level runs on header evidence.
    report = _header()
    assert report["failed_checks"] == [], report["failed_checks"]
    assert (report["level"], report["level_source"]) == ("header", "records")
    by_key = {(r["check"], r["subject"][:18]): r for r in report["checks"]}
    assert by_key[("application_level", "3tt0000000000H1AAI")]["status"] == "pass"
    for check in ("invoice_balance", "invoice_line_balance"):
        assert by_key[(check, "3tt0000000000H1AAI")]["status"] == "skip", check
    assert "includes header level" in by_key[("invoice_balance", "3tt0000000000H1AAI")]["detail"]
    payment = by_key[("payment_balance", "0aQ0000000000H1EAI")]
    assert payment["status"] == "skip" and "2 header-level application row(s)" in payment["detail"]
    # INVH2 is unpaid (no rows, no SettlementLevel): its invoice balance still runs.
    assert by_key[("invoice_balance", "3tt0000000000H2AAI")]["status"] == "pass"
    assert report["invoice_ids"] == HEADER_INVOICES


def test_header_level_balances_skip_even_when_wrong():
    def mutate(data):
        _row(data, "Invoice", "3tt0000000000H1AAI")["Balance"] = 1
        _row(data, "Payment", "0aQ0000000000H1EAI")["Balance"] = 1
    report = _header(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    statuses = {(r["check"], r["subject"]): r["status"] for r in report["checks"]}
    assert statuses[("invoice_balance", "3tt0000000000H1AAI")] == "skip"
    assert statuses[("payment_balance", "0aQ0000000000H1EAI")] == "skip"


def test_settlement_level_invoice_alone_skips_invoice_balance():
    report = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000002AAA").update(
        SettlementLevel="Invoice", Balance=1))
    result = next(r for r in report["checks"] if r["check"] == "invoice_balance"
                  and r["subject"] == "3tt000000000002AAA")
    assert result["status"] == "skip" and "includes header level" in result["detail"]


def test_payment_rows_on_invoices_outside_the_set_count_for_net_applied():
    # Only INV2 is verified; payment 0aQ...1's row is on INV1, read by payment id.
    report = _verify(_load("line_level.json"), ["3tt000000000002AAA"],
                     ["0aQ000000000001EAA"])
    result = next(r for r in report["checks"] if r["check"] == "payment_balance")
    assert result["status"] == "pass", result["detail"]


def test_verifier_only_reads():
    data = _load("line_level.json")
    client = RecordedClient(data)
    fetch_records(client, LINE_INVOICES, LINE_EXTRA_PAYMENTS)
    assert client.writes == []
    assert client.queries and all(q.startswith("SELECT ") for q in client.queries)


def test_no_applications_leaves_level_undetermined_and_passes():
    data = _load("line_level.json")
    report = _verify(data, ["3tt000000000002AAA"])
    assert report["level"] is None and report["level_source"] == "undetermined"
    assert _statuses(report, "application_level") == {"skip"}
    assert report["ok"] is True


# ------------------------------------------------------------------ application_level

@pytest.mark.parametrize("runner, wrong", [(_line, "header"), (_header, "line")])
def test_wrong_expected_level_fails_level_check_only(runner, wrong):
    report = runner(level=wrong)
    assert report["failed_checks"] == ["application_level"]
    assert report["level_source"] == "argument"


def test_header_row_on_line_level_invoice_is_mixed():
    def add_header_row(data):
        data["PaymentLineInvoice"].append({
            "Id": "0b8000000000099AAA", "InvoiceId": "3tt000000000002AAA",
            "PaymentId": "0aQ000000000002EAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
    report = _line(mutate=add_header_row)
    assert report["level_source"] == "mixed"
    assert report["failed_checks"] == ["application_level"]
    level = {r["subject"]: r["status"] for r in report["checks"]
             if r["check"] == "application_level"}
    # INV2 shows the header row; INV1 and INV3 show line rows; all three have rows.
    assert level == {"3tt000000000001AAA": "fail", "3tt000000000002AAA": "fail",
                     "3tt000000000003AAA": "fail"}


def test_mixed_level_skips_invoices_with_no_rows():
    def mutate(data):
        data["PaymentLineInvoice"].append({
            "Id": "0b8000000000099AAA", "InvoiceId": "3tt000000000001AAA",
            "PaymentId": "0aQ000000000002EAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
    report = _line(mutate=mutate)
    level = {r["subject"]: r for r in report["checks"] if r["check"] == "application_level"}
    assert level["3tt000000000002AAA"]["status"] == "skip"
    assert level["3tt000000000001AAA"]["status"] == "fail"
    assert "both levels" in level["3tt000000000001AAA"]["detail"]
    assert level["3tt000000000003AAA"]["status"] == "fail"


def test_settlement_level_contradicting_expectation_fails():
    report = _line(level="line", mutate=lambda d: _row(
        d, "Invoice", "3tt000000000002AAA").update(SettlementLevel="Invoice"))
    assert report["failed_checks"] == ["application_level"]


# ------------------------------------------------------------------ invoice_balance

@pytest.mark.parametrize("runner, invoice", [
    (_line, "3tt000000000001AAA"), (_line, "3tt000000000002AAA"),
    (_header, "3tt0000000000H2AAI")])
def test_invoice_balance_off_by_one_fails(runner, invoice):
    report = runner(mutate=lambda d: _row(d, "Invoice", invoice).update(
        Balance=_row(d, "Invoice", invoice)["Balance"] + 1))
    assert report["failed_checks"] == ["invoice_balance"]
    failed = [r for r in report["checks"] if r["status"] == "fail"]
    assert [r["subject"] for r in failed] == [invoice]


@pytest.mark.parametrize("invoice, rollup, rows", [
    ("3tt000000000003AAA", "NetCreditsApplied", "credit rows"),
    ("3tt000000000001AAA", "NetPaymentsApplied", "payment rows"),
])
def test_invoice_rollup_disagreeing_with_rows_fails(invoice, rollup, rows):
    # The invoice arithmetic still holds and the lines are untouched: only the
    # comparison of the rollup with the application rows can fail.
    def mutate(data):
        inv = _row(data, "Invoice", invoice)
        inv.update({rollup: inv[rollup] - 1, "Balance": inv["Balance"] + 1})
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_balance"]
    detail = next(r["detail"] for r in report["checks"] if r["status"] == "fail")
    assert f"{rollup} " in detail and rows in detail


# ------------------------------------------------------------------ invoice_line_balance

def test_line_balance_off_by_one_fails():
    report = _line(mutate=lambda d: _row(d, "InvoiceLine", "5TV000000000031GAA").update(
        Balance=1))
    assert report["failed_checks"] == ["invoice_line_balance"]


def test_line_rollup_disagreeing_with_line_rows_fails():
    def mutate(data):
        data["CreditMemoLineInvoiceLine"][1]["Amount"] = 59
    report = _line(mutate=mutate)
    assert "invoice_line_balance" in report["failed_checks"]
    assert "invoice_balance" in report["failed_checks"]


# ------------------------------------------------------------------ payment_balance

@pytest.mark.parametrize("runner, payment", [
    (_line, "0aQ000000000001EAA"), (_line, "0aQ000000000002EAA")])
def test_payment_balance_off_by_one_fails(runner, payment):
    report = runner(mutate=lambda d: _row(d, "Payment", payment).update(
        Balance=_row(d, "Payment", payment)["Balance"] + 1))
    assert report["failed_checks"] == ["payment_balance"]


def test_payment_net_applied_disagreeing_with_rows_fails():
    def mutate(data):
        _row(data, "Payment", "0aQ000000000001EAA").update(NetApplied=300, Balance=700)
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["payment_balance"]


@pytest.mark.parametrize("payment", ["0aQ000000000002EAA", "0aQ000000000001EAA"])
@pytest.mark.parametrize("field", ["NetRefundApplied", "NetPaymentCreditApplied"])
def test_payment_with_unmeasured_field_is_skipped_not_failed(field, payment):
    # Canceled (no rows) and Processed (with rows). Balance deliberately inconsistent:
    # a skip must not hide behind a pass or a fail.
    report = _line(mutate=lambda d: _row(d, "Payment", payment).update(
        {field: 25, "Balance": 975}))
    assert report["ok"] is True
    result = next(r for r in report["checks"]
                  if r["check"] == "payment_balance" and r["subject"] == payment)
    assert result["status"] == "skip"
    assert field in result["detail"]


@pytest.mark.parametrize("value", [0, None])
def test_payment_with_zero_or_null_unmeasured_fields_is_checked(value):
    def mutate(data):
        for row in data["Payment"]:
            row.update(NetRefundApplied=value, NetPaymentCreditApplied=value)
        _row(data, "Payment", "0aQ000000000002EAA")["Balance"] = 999
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["payment_balance"]


def test_amounts_compare_exactly_without_assuming_cents():
    # A three-decimal currency: a 0.001 difference is a real difference.
    report = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000002AAA").update(
        Balance=495.001))
    assert report["failed_checks"] == ["invoice_balance"]
    detail = next(r["detail"] for r in report["checks"] if r["status"] == "fail")
    assert "495.001" in detail
    # Zero-decimal amounts print without invented cents.
    clean = _line()
    passed = next(r["detail"] for r in clean["checks"]
                  if r["check"] == "invoice_balance" and r["subject"] == "3tt000000000002AAA")
    assert passed == "495 = 495 - 0 - 0"


# ------------------------------------------------------------------ unmeasured fields

def _invoice_checks_on(report: dict, invoice: str) -> dict:
    """Every result for one invoice and its lines, keyed by (check, subject)."""
    return {(r["check"], r["subject"]): r for r in report["checks"]
            if r["subject"].startswith(invoice)}


@pytest.mark.parametrize("field", ["TotalConvertedNegAmount", "WriteOffTotalChargeAmount",
                                   "WriteOffTotalTaxAmount", "TotalAdjustmentAmount"])
def test_invoice_with_unmeasured_field_skips_both_invoice_checks(field):
    # A written-off line-level invoice: Balance 0 while its line still reads 3950. No
    # invoice-level skip may leave the line check to fail on the same invoice.
    report = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000001AAA").update(
        {field: -3950, "Balance": 0}))
    assert report["ok"] is True, report["failed_checks"]
    results = _invoice_checks_on(report, "3tt000000000001AAA")
    assert all(r["status"] != "fail" for r in results.values())
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000001AAA")]
        assert result["status"] == "skip" and field in result["detail"], check


@pytest.mark.parametrize("write_off", ["Completed", "InProgress", "Failed"])
def test_invoice_with_write_off_status_skips_both_invoice_checks(write_off):
    report = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000001AAA").update(
        WriteOffStatus=write_off, Balance=0))
    assert report["ok"] is True, report["failed_checks"]
    results = _invoice_checks_on(report, "3tt000000000001AAA")
    assert all(r["status"] != "fail" for r in results.values())
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000001AAA")]
        assert result["status"] == "skip" and f"WriteOffStatus {write_off}" in result["detail"]


def test_invoice_with_line_and_header_evidence_skips_invoice_balance():
    # INV1 has line rows and SettlementLevel InvoiceLine; one header row makes both.
    def mutate(data):
        data["PaymentLineInvoice"].append({
            "Id": "0b8000000000099AAA", "InvoiceId": "3tt000000000001AAA",
            "PaymentId": "0aQ000000000002EAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
    report = _line(mutate=mutate)
    results = _invoice_checks_on(report, "3tt000000000001AAA")
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000001AAA")]
        assert result["status"] == "skip" and "includes header level" in result["detail"]


@pytest.mark.parametrize("field", ["ConvertedNegAmount", "ChargeConvertedNegAmount",
                                   "AdjustmentAmount"])
def test_line_with_unmeasured_field_is_skipped_not_failed(field):
    # An unmeasured line makes its invoice unmeasured: both invoice checks skip.
    report = _line(mutate=lambda d: _row(d, "InvoiceLine", "5TV000000000032GAA").update(
        {field: -5, "Balance": 1}))
    assert report["ok"] is True, report["failed_checks"]
    results = _invoice_checks_on(report, "3tt000000000003AAA")
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000003AAA")]
        assert result["status"] == "skip" and field in result["detail"], check


@pytest.mark.parametrize("line_type", ["Adjustment", "Tax", None, "Surcharge"])
def test_line_whose_type_is_not_charge_is_skipped(line_type):
    # Allow-list: only Charge lines are measured; null and unknown Types included.
    report = _line(mutate=lambda d: _row(d, "InvoiceLine", "5TV000000000032GAA").update(
        Type=line_type, Balance=1))
    assert report["ok"] is True, report["failed_checks"]
    results = _invoice_checks_on(report, "3tt000000000003AAA")
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000003AAA")]
        assert result["status"] == "skip", check
        assert f"has Type {line_type or 'null'}" in result["detail"], check


@pytest.mark.parametrize("value", [0, None])
def test_zero_or_null_unmeasured_invoice_and_line_fields_are_still_checked(value):
    def mutate(data):
        for row in data["Invoice"]:
            row.update({f: value for f in ("TotalConvertedNegAmount", "WriteOffTotalChargeAmount",
                                           "WriteOffTotalTaxAmount", "TotalAdjustmentAmount",
                                           "TotalTaxesCapturedAtHeader")},
                       WriteOffStatus=None)
        for row in data["InvoiceLine"]:
            row.update({f: value for f in ("ConvertedNegAmount", "ChargeConvertedNegAmount",
                                           "AdjustmentAmount")})
        _row(data, "Invoice", "3tt000000000003AAA")["Balance"] = 494
        _row(data, "InvoiceLine", "5TV000000000032GAA")["Balance"] = 494
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_balance", "invoice_line_balance"]


# ------------------------------------------------------------------ nulls, lines, chunks

def test_null_balance_fails_even_when_the_expected_value_is_null():
    def mutate(data):
        _row(data, "Invoice", "3tt000000000003AAA").update(TotalAmountWithTax=None,
                                                           Balance=None)
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(LineAmount=None, Balance=None)
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_balance", "invoice_line_balance"]


def test_invoice_with_no_lines_fails_the_line_check():
    def mutate(data):
        # Line evidence (SettlementLevel InvoiceLine) but no lines read.
        _row(data, "Invoice", "3tt000000000002AAA")["SettlementLevel"] = "InvoiceLine"
        data["InvoiceLine"] = [r for r in data["InvoiceLine"]
                               if r["InvoiceId"] != "3tt000000000002AAA"]
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_line_balance"]
    result = next(r for r in report["checks"] if r["status"] == "fail")
    assert result["subject"] == "3tt000000000002AAA" and "no lines" in result["detail"]


def test_more_ids_than_one_chunk_are_all_read():
    from scripts.txn_data_harness.verify import _id18
    n = 450
    invoices, lines, payments, rows = [], [], [], []
    unmeasured_invoice = dict.fromkeys(verify_mod._UNMEASURED_INVOICE_FIELDS)
    unmeasured_line = dict.fromkeys(verify_mod._UNMEASURED_LINE_FIELDS)
    for i in range(n):
        iid, lid, pid = (_id18(f"3tt{i:012d}"), _id18(f"5TV{i:012d}"),
                         _id18(f"0aQ{i:012d}"))
        invoices.append({"Id": iid, "Status": "Posted", "SettlementLevel": "InvoiceLine",
                         "TotalAmountWithTax": 10, "NetCreditsApplied": 0,
                         "NetPaymentsApplied": 4, "Balance": 6, "WriteOffStatus": None,
                         **unmeasured_invoice})
        lines.append({"Id": lid, "InvoiceId": iid, "Type": "Charge",
                      "LineAmount": 10, "NetCreditsApplied": 0, "NetPaymentsApplied": 4,
                      "Balance": 6, **unmeasured_line})
        payments.append({"Id": pid, "Status": "Processed", "Amount": 4, "NetApplied": 4,
                         "Balance": 0, "NetRefundApplied": None,
                         "NetPaymentCreditApplied": None})
        rows.append({"Id": _id18(f"1Al{i:012d}"), "InvoiceLineId": lid, "PaymentId": pid,
                     "Amount": 4, "Type": "Applied", "UnappliedStatus": "No",
                     "RelatedPaymentLineInvcLineId": None})
    data = {"Invoice": invoices, "InvoiceLine": lines, "Payment": payments,
            "PaymentLineInvoiceLine": rows}
    client = RecordedClient(data)
    records = fetch_records(client, [r["Id"] for r in invoices])
    assert len(records["Invoice"]) == n and len(records["InvoiceLine"]) == n
    assert sum(1 for q in client.queries if " FROM Invoice " in q) == 3
    # Payments are found through the rows, read in chunks, and their rows read again by
    # payment id: the merge must not count a row twice.
    assert len(records["Payment"]) == n
    assert sum(1 for q in client.queries if " FROM Payment " in q) == 3
    assert len(records["PaymentLineInvoiceLine"]) == n
    report = run_checks(records)
    assert report["ok"] is True, report["failed_checks"]
    assert _statuses(report, "payment_balance") == {"pass"}


# ------------------------------------------------------------------ inputs

def test_unknown_invoice_id_is_an_error():
    with pytest.raises(VerifyError, match="not found"):
        fetch_records(RecordedClient(_load("line_level.json")),
                      ["3tt00000000000ZAAQ"])


def test_unknown_payment_id_is_an_error():
    with pytest.raises(VerifyError, match="payment ids not found"):
        fetch_records(RecordedClient(_load("line_level.json")),
                      [LINE_INVOICES[1]], ["0aQ00000000000ZEAQ"])


def test_fifteen_character_ids_are_normalized_and_deduplicated():
    data = _load("line_level.json")
    client = RecordedClient(data)
    records = fetch_records(
        client, [LINE_INVOICES[0][:15], LINE_INVOICES[0], LINE_INVOICES[0][:15]],
        [LINE_EXTRA_PAYMENTS[0][:15]])
    assert [r["Id"] for r in records["Invoice"]] == [LINE_INVOICES[0]]
    assert LINE_EXTRA_PAYMENTS[0] in {r["Id"] for r in records["Payment"]}
    assert run_checks(records)["ok"] is True


def test_fifteen_character_id_gets_the_case_safe_suffix():
    # Real 264 org ids: the suffix encodes which of the first 15 characters are upper case.
    assert split_ids(["3ttWt000002lg4H, 0aQWt000000XOLJ"], "ids") == [
        "3ttWt000002lg4HIAQ", "0aQWt000000XOLJMA4"]


@pytest.mark.parametrize("typed", ["3TTWT000002LG4HIAQ", "3ttwt000002lg4hiaq",
                                   "3ttWt000002lg4Hiaq", "3ttWt000002lg4HIAQ"])
def test_eighteen_character_id_case_is_restored_from_its_suffix(typed):
    # As Salesforce does: the suffix says which characters are upper case.
    assert split_ids([typed], "ids") == ["3ttWt000002lg4HIAQ"]


@pytest.mark.parametrize("bad", [
    "3tt000000000001BAA",  # B marks the first character, a digit, as upper case
    "3tt000000000001AA9",  # 9 is outside the suffix alphabet
])
def test_eighteen_character_id_whose_suffix_fits_no_casing_is_refused(bad):
    with pytest.raises(VerifyError, match="matches no casing") as raised:
        split_ids([bad], "ids")
    assert "expected" not in str(raised.value)  # never suggest a different record


def test_malformed_id_is_rejected_before_any_query():
    client = RecordedClient({})
    with pytest.raises(VerifyError, match="not a Salesforce id"):
        fetch_records(client, ["3tt' OR Id != '"])
    assert client.queries == []


def test_ids_from_manifest_reads_invoice_and_payment_keys(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({
        "run_id": "run", "kind": "sales_txn_quote", "invoice_id": "3tt000000000001AAA",
        "payment_ids": ["0aQ000000000001EAA"]}))
    assert ids_from_manifest(path) == (["3tt000000000001AAA"], ["0aQ000000000001EAA"])


def test_selected_field_missing_from_recorded_rows_fails(monkeypatch):
    # A field the org may not have (CurrencyIsoCode exists only with multi-currency)
    # must not read as None: the recorded client refuses it like INVALID_FIELD.
    monkeypatch.setattr(verify_mod, "INVOICE_FIELDS",
                        verify_mod.INVOICE_FIELDS + ("CurrencyIsoCode",))
    with pytest.raises(AssertionError, match="CurrencyIsoCode"):
        fetch_records(RecordedClient(_load("line_level.json")), LINE_INVOICES)


def test_no_selected_field_is_multi_currency_only():
    selected = set(verify_mod.INVOICE_FIELDS + verify_mod.INVOICE_LINE_FIELDS
                   + verify_mod.PAYMENT_FIELDS)
    for obj in verify_mod.APP_OBJECTS:
        selected |= set(obj.fields)
    assert "CurrencyIsoCode" not in selected


def test_ids_from_manifest_reads_all_four_keys(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({
        "invoice_id": "3tt000000000001AAA",
        "invoice_ids": ["3tt000000000002AAA", "3tt000000000003AAA"],
        "payment_id": "0aQ000000000001EAA",
        "payment_ids": ["0aQ000000000002EAA"]}))
    assert ids_from_manifest(path) == (
        ["3tt000000000001AAA", "3tt000000000002AAA", "3tt000000000003AAA"],
        ["0aQ000000000001EAA", "0aQ000000000002EAA"])


@pytest.mark.parametrize("key", ["invoice_id", "invoice_ids", "payment_id", "payment_ids"])
@pytest.mark.parametrize("value", [12345, ["3tt000000000001AAA", 7], {"id": "x"}, True])
def test_ids_from_manifest_rejects_non_string_ids(tmp_path, key, value):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({key: value}))
    with pytest.raises(VerifyError, match=f"{key} must be a string id"):
        ids_from_manifest(path)


def test_check_ids_normalizes_deduplicates_and_keeps_order():
    a, b = LINE_INVOICES[0], LINE_INVOICES[1]
    assert _check_ids([b, a[:15], " ", a, b[:15], a[:15] + "aaa", None], "ids") == [b, a]


def test_settlement_level_alone_sets_the_level():
    # No application rows on INV2: only its SettlementLevel names a level.
    data = _load("line_level.json")
    _row(data, "Invoice", "3tt000000000002AAA")["SettlementLevel"] = "InvoiceLine"
    report = _verify(data, ["3tt000000000002AAA"])
    assert (report["level"], report["level_source"]) == ("line", "records")
    assert _statuses(report, "application_level") == {"pass"}
    # A SettlementLevel naming the other level makes the set mixed.
    mixed = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000002AAA").update(
        SettlementLevel="Invoice"))
    assert mixed["level_source"] == "mixed"
    assert mixed["failed_checks"] == ["application_level"]


def test_header_rows_only_invoice_skips_line_balances_even_at_line_level():
    # Forced line level on header rows: a header application rolled onto the line
    # must not be judged against line rows that do not exist.
    def mutate(data):
        _row(data, "InvoiceLine", "5TV00000000H11AGAS").update(NetPaymentsApplied=300,
                                                              Balance=800)
    report = _header(level="line", mutate=mutate)
    assert report["failed_checks"] == ["application_level"]
    result = next(r for r in report["checks"] if r["check"] == "invoice_line_balance"
                  and r["subject"] == "3tt0000000000H1AAI")
    assert result["status"] == "skip" and "includes header level" in result["detail"]


@pytest.mark.parametrize("status", ["Draft", "Canceled", None])
def test_invoice_that_is_not_posted_is_skipped_not_failed(status):
    # Balances deliberately inconsistent: rollups are measured on Posted invoices only.
    def mutate(data):
        _row(data, "Invoice", "3tt000000000003AAA").update(Status=status, Balance=1)
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(Balance=1)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    skipped = [r for r in report["checks"] if r["subject"].startswith("3tt000000000003AAA")
               and r["check"] in ("invoice_balance", "invoice_line_balance")]
    assert {r["status"] for r in skipped} == {"skip"} and len(skipped) == 2
    assert all(f"Status {status or 'null'}" in r["detail"]
               and "Posted invoices only" in r["detail"] for r in skipped)


@pytest.mark.parametrize("level", ["line", "header"])
def test_forced_level_skips_an_invoice_with_no_evidence(level):
    # INV2: no application rows, SettlementLevel null. A forced level is not evidence.
    report = _verify(_load("line_level.json"), ["3tt000000000002AAA"], level=level)
    assert report["level_source"] == "argument"
    result = next(r for r in report["checks"] if r["check"] == "application_level")
    assert result["status"] == "skip" and "no application rows" in result["detail"]
    assert report["ok"] is True


def test_forced_level_fails_on_one_row_of_the_other_level():
    # SettlementLevel null, so only the row count can fail it.
    def mutate(data):
        data["PaymentLineInvoice"].append({
            "Id": "0b8000000000099AAA", "InvoiceId": "3tt000000000002AAA",
            "PaymentId": "0aQ000000000002EAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
    report = _line(level="line", mutate=mutate)
    assert report["failed_checks"] == ["application_level"]
    failed = [r for r in report["checks"] if r["status"] == "fail"]
    assert [r["subject"] for r in failed] == ["3tt000000000002AAA"]
    assert "1 header-level row(s)" in failed[0]["detail"]
    assert "SettlementLevel is" not in failed[0]["detail"]


def test_tax_lines_skip_the_invoice_balance_checks():
    def mutate(data):
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(Type="Tax", Balance=1)
        _row(data, "Invoice", "3tt000000000003AAA").update(Balance=1)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    for check in ("invoice_balance", "invoice_line_balance"):
        result = next(r for r in report["checks"] if r["check"] == check
                      and r["subject"].startswith("3tt000000000003AAA"))
        assert result["status"] == "skip" and "has Type Tax" in result["detail"], check


def test_header_tax_skips_the_invoice_balance_checks():
    def mutate(data):
        _row(data, "Invoice", "3tt000000000003AAA").update(TotalTaxesCapturedAtHeader=45,
                                                           Balance=1)
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(Balance=1)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    for check in ("invoice_balance", "invoice_line_balance"):
        result = next(r for r in report["checks"] if r["check"] == check
                      and r["subject"].startswith("3tt000000000003AAA"))
        assert (result["status"] == "skip"
                and "TotalTaxesCapturedAtHeader 45" in result["detail"]), check


@pytest.mark.parametrize("status", ["Draft", "Pending", "Failed", None])
def test_payment_with_unmeasured_status_is_skipped_not_failed(status):
    report = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000001EAA").update(
        Status=status, Balance=7))
    assert report["ok"] is True, report["failed_checks"]
    result = next(r for r in report["checks"] if r["check"] == "payment_balance"
                  and r["subject"] == "0aQ000000000001EAA")
    assert result["status"] == "skip" and f"Status {status or 'null'}" in result["detail"]


def test_canceled_payment_with_applications_is_skipped_not_failed():
    report = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000001EAA").update(
        Status="Canceled", Balance=7))
    assert report["ok"] is True, report["failed_checks"]
    result = next(r for r in report["checks"] if r["check"] == "payment_balance"
                  and r["subject"] == "0aQ000000000001EAA")
    assert result["status"] == "skip"
    assert "Status Canceled with 1 application row(s)" in result["detail"]


def test_processed_and_canceled_unapplied_payments_are_checked():
    report = _line()
    statuses = {r["subject"]: r["status"] for r in report["checks"]
                if r["check"] == "payment_balance"}
    # 0aQ...1 Processed; 0aQ...2 Canceled with no applications.
    assert statuses == {"0aQ000000000001EAA": "pass", "0aQ000000000002EAA": "pass"}


def test_undetermined_level_skips_line_balances():
    # INV2 alone: no rows, no SettlementLevel. Line Balance is measured at Line Level
    # only, so an inconsistent line must skip, not fail.
    data = _load("line_level.json")
    _row(data, "InvoiceLine", "5TV000000000021GAA")["Balance"] = 1
    report = _verify(data, ["3tt000000000002AAA"])
    assert report["level_source"] == "undetermined"
    result = next(r for r in report["checks"] if r["check"] == "invoice_line_balance")
    assert result["status"] == "skip" and "shows no level" in result["detail"]
    assert report["ok"] is True


def test_header_rows_are_read_for_every_invoice():
    # H1's header rows come second: a fetch that read only the first invoice's rows
    # would miss them (and the payment found through them).
    client = RecordedClient(_load("header_level.json"))
    records = fetch_records(client, list(reversed(HEADER_INVOICES)))
    for obj in ("PaymentLineInvoice", "CreditMemoInvApplication"):
        assert "3tt0000000000H1AAI" in {r["InvoiceId"] for r in records[obj]}, obj
    assert [r["Id"] for r in records["Payment"]] == ["0aQ0000000000H1EAI"]
    assert run_checks(records)["ok"] is True


def test_mixed_set_skips_line_balances_of_an_invoice_with_no_level_of_its_own():
    # INV1 line rows, INV3 a header row: mixed. INV2 has neither, so its line
    # (deliberately inconsistent) is skipped rather than held to the Line formula.
    def mutate(data):
        data["PaymentLineInvoice"].append({
            "Id": "0b8000000000099AAA", "InvoiceId": "3tt000000000003AAA",
            "PaymentId": "0aQ000000000002EAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
        _row(data, "InvoiceLine", "5TV000000000021GAA")["Balance"] = 1
    report = _line(mutate=mutate)
    assert report["level_source"] == "mixed"
    assert report["failed_checks"] == ["application_level"]
    line_checks = {r["subject"]: r for r in report["checks"]
                   if r["check"] == "invoice_line_balance"}
    assert line_checks["3tt000000000002AAA"]["status"] == "skip"
    assert "shows no level" in line_checks["3tt000000000002AAA"]["detail"]
    # INV3 now has line and header rows: both levels, skipped.
    assert line_checks["3tt000000000003AAA"]["status"] == "skip"
    assert "includes header level" in line_checks["3tt000000000003AAA"]["detail"]
    # INV1's own evidence is still line level alone: it runs inside a mixed set.
    assert line_checks["3tt000000000001AAA/5TV000000000011GAA"]["status"] == "pass"


def test_credit_rows_alone_are_evidence_of_the_wrong_level():
    # INV2: one header credit application, no payment rows, SettlementLevel null.
    def mutate(data):
        data["CreditMemoInvApplication"].append({
            "Id": "0c0000000000099AAA", "InvoiceId": "3tt000000000002AAA",
            "CreditMemoId": "50g000000000099AAA", "Amount": 0, "Type": "Applied",
            "HasBeenUnapplied": "No"})
        data["CreditMemo"].append({"Id": "50g000000000099AAA", "Status": "Posted"})
    report = _line(level="line", mutate=mutate)
    result = next(r for r in report["checks"] if r["check"] == "application_level"
                  and r["subject"] == "3tt000000000002AAA")
    assert result["status"] == "fail" and "1 header-level row(s)" in result["detail"]


def test_line_balances_follow_each_invoices_own_evidence_not_the_forced_level():
    # Forced header on a line-level set: the level check fails, but INV1 and INV3
    # show line level themselves, so their line balances still run.
    report = _line(level="header")
    assert report["failed_checks"] == ["application_level"]
    statuses = {r["subject"][:18]: r["status"] for r in report["checks"]
                if r["check"] == "invoice_line_balance"}
    assert statuses == {"3tt000000000001AAA": "pass", "3tt000000000002AAA": "skip",
                        "3tt000000000003AAA": "pass"}


@pytest.mark.parametrize("settlement, runs", [("InvoiceLine", True), ("Invoice", False)])
def test_settlement_level_alone_decides_whether_line_balances_run(settlement, runs):
    # INV2 has no rows; its line Balance is deliberately inconsistent.
    def mutate(data):
        _row(data, "Invoice", "3tt000000000002AAA")["SettlementLevel"] = settlement
        _row(data, "InvoiceLine", "5TV000000000021GAA")["Balance"] = 1
    report = _line(mutate=mutate)
    results = [r for r in report["checks"] if r["check"] == "invoice_line_balance"
               and r["subject"].startswith("3tt000000000002AAA")]
    if runs:
        assert [r["status"] for r in results] == ["fail"]
    else:
        assert [r["status"] for r in results] == ["skip"]
        assert "includes header level" in results[0]["detail"]


@pytest.mark.parametrize("how", ["unapplied_row", "flag_only", "null_type"])
def test_unapplied_rows_skip_invoice_line_and_payment_balances(how):
    # Rollups left as they were, so any check that still ran would have to guess.
    def mutate(data):
        applied = _row(data, "PaymentLineInvoiceLine", "1Al000000000001CAA")
        if how == "unapplied_row":
            # The Type alone triggers the skip: the Applied row's flag stays "No".
            data["PaymentLineInvoiceLine"].append({
                "Id": "1Al000000000009CAA", "InvoiceLineId": "5TV000000000011GAA",
                "PaymentId": "0aQ000000000001EAA", "Amount": 400, "Type": "Unapplied",
                "UnappliedStatus": "NA", "RelatedPaymentLineInvcLineId": None})
        elif how == "flag_only":
            applied["UnappliedStatus"] = "Yes"
            _row(data, "Invoice", "3tt000000000001AAA")["Balance"] = 1
        else:
            # A Type that is not Applied is not measured either: skip, not a silent 0.
            applied["Type"] = None
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    skipped = [r for r in report["checks"]
               if r["subject"].startswith(("3tt000000000001AAA", "0aQ000000000001EAA"))
               and r["check"] != "application_level"]
    assert {r["check"] for r in skipped} == {"invoice_balance", "invoice_line_balance",
                                             "payment_balance"}
    assert all(r["status"] == "skip" and "application row" in r["detail"]
               and "measured on 264" in r["detail"] for r in skipped)


def test_unapplied_credit_row_alone_skips_the_invoice_balances():
    # Only a credit-memo line row is flagged; INV3's balances are made inconsistent.
    def mutate(data):
        _row(data, "CreditMemoLineInvoiceLine", "4sG000000000001EAA")["UnappliedStatus"] = "Yes"
        _row(data, "Invoice", "3tt000000000003AAA")["Balance"] = 1
        _row(data, "InvoiceLine", "5TV000000000031GAA")["Balance"] = 1
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    skipped = [r for r in report["checks"] if r["subject"].startswith("3tt000000000003AAA")
               and r["check"] in ("invoice_balance", "invoice_line_balance")]
    assert len(skipped) == 2 and all(r["status"] == "skip" for r in skipped)


def test_canceled_payment_with_rows_makes_its_invoice_unmeasured():
    report = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000001EAA").update(
        Status="Canceled"))
    assert report["ok"] is True, report["failed_checks"]
    results = _invoice_checks_on(report, "3tt000000000001AAA")
    for check in ("invoice_balance", "invoice_line_balance"):
        result = results[(check, "3tt000000000001AAA")]
        assert result["status"] == "skip", check
        assert result["detail"].startswith(
            "linked payment 0aQ000000000001EAA; origin payment 0aQ000000000001EAA: "
            "Status Canceled with 1 application row(s)"), check


def test_payment_on_a_header_settled_invoice_is_unmeasured():
    report = _line(mutate=lambda d: _row(d, "Invoice", "3tt000000000001AAA").update(
        SettlementLevel="Invoice"))
    result = next(r for r in report["checks"] if r["check"] == "payment_balance"
                  and r["subject"] == "0aQ000000000001EAA")
    assert result["status"] == "skip"
    assert result["detail"].startswith(
        "linked invoice 3tt000000000001AAA; origin invoice 3tt000000000001AAA: this "
        "invoice's own evidence includes header level")


def test_clean_line_level_invoice_and_its_processed_payment_are_checked():
    # Guard against over-skipping: the measured case still runs and can fail.
    clean = _line()
    statuses = {(r["check"], r["subject"]): r["status"] for r in clean["checks"]}
    assert statuses[("invoice_balance", "3tt000000000001AAA")] == "pass"
    assert statuses[("invoice_line_balance", "3tt000000000001AAA/5TV000000000011GAA")] == "pass"
    assert statuses[("payment_balance", "0aQ000000000001EAA")] == "pass"
    broken = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000001EAA").update(Balance=5))
    assert broken["failed_checks"] == ["payment_balance"]


def test_payment_with_an_unmeasured_row_on_an_invoice_outside_the_set_skips():
    # INV1 is not read, so nothing propagates: the payment's own row must skip it.
    data = _load("line_level.json")
    _row(data, "PaymentLineInvoiceLine", "1Al000000000001CAA")["UnappliedStatus"] = "Yes"
    _row(data, "Payment", "0aQ000000000001EAA")["Balance"] = 7
    report = _verify(data, ["3tt000000000002AAA"], ["0aQ000000000001EAA"])
    result = next(r for r in report["checks"] if r["check"] == "payment_balance")
    assert result["status"] == "skip" and "UnappliedStatus Yes" in result["detail"]


def test_processed_payment_without_rows_is_unmeasured():
    data = _load("line_level.json")
    _row(data, "Payment", "0aQ000000000002EAA").update(Status="Processed", Balance=7)
    report = _verify(data, ["3tt000000000002AAA"], ["0aQ000000000002EAA"])
    result = next(r for r in report["checks"] if r["check"] == "payment_balance")
    assert result["status"] == "skip" and "Status Processed with 0" in result["detail"]


def _chain(invoices: dict, payments: dict, memos: dict = None) -> dict:
    """A consistent line-level set. ``invoices``: name -> Status; ``payments``: name ->
    invoice names it pays (10 each); ``memos``: name -> (Status, invoice names, 5 each).
    Returns records keyed like a fetch, plus "ids": name -> 18-character id."""
    from scripts.txn_data_harness.verify import _id18
    memos = memos or {}
    ids = {name: _id18(f"3tt0000000{i:05d}") for i, name in enumerate(invoices)}
    ids.update({name: _id18(f"0aQ0000000{i:05d}") for i, name in enumerate(payments)})
    ids.update({name: _id18(f"50g0000000{i:05d}") for i, name in enumerate(memos)})
    blank_inv = dict.fromkeys(verify_mod._UNMEASURED_INVOICE_FIELDS)
    blank_line = dict.fromkeys(verify_mod._UNMEASURED_LINE_FIELDS)
    data = {k: [] for k in ("Invoice", "InvoiceLine", "Payment", "PaymentLineInvoiceLine",
                            "CreditMemoLineInvoiceLine", "PaymentLineInvoice",
                            "CreditMemoInvApplication", "CreditMemoLine", "CreditMemo")}
    paid = {name: 10 * sum(name in targets for targets in payments.values())
            for name in invoices}
    credited = {name: 5 * sum(name in targets for _, targets in memos.values())
                for name in invoices}
    for name, status in invoices.items():
        balance = 100 - paid[name] - credited[name]
        line = {"NetCreditsApplied": credited[name], "NetPaymentsApplied": paid[name],
                "Balance": balance}
        data["Invoice"].append({"Id": ids[name], "Status": status,
                                "SettlementLevel": "InvoiceLine", "TotalAmountWithTax": 100,
                                "WriteOffStatus": None, **line, **blank_inv})
        data["InvoiceLine"].append({"Id": ids[name][:3].replace("3tt", "5TV") + ids[name][3:15] + "AAA",
                                    "InvoiceId": ids[name], "Type": "Charge",
                                    "LineAmount": 100, **line, **blank_line})
    line_of = {r["InvoiceId"]: r["Id"] for r in data["InvoiceLine"]}
    for i, (name, targets) in enumerate(payments.items()):
        data["Payment"].append({"Id": ids[name], "Status": "Processed",
                                "Amount": 10 * len(targets), "NetApplied": 10 * len(targets),
                                "Balance": 0, "NetRefundApplied": None,
                                "NetPaymentCreditApplied": None})
        for j, target in enumerate(targets):
            data["PaymentLineInvoiceLine"].append({
                "Id": f"1Al{i:06d}{j:06d}AAA", "InvoiceLineId": line_of[ids[target]],
                "PaymentId": ids[name], "Amount": 10, "Type": "Applied",
                "UnappliedStatus": "No", "RelatedPaymentLineInvcLineId": None})
    for i, (name, (status, targets)) in enumerate(memos.items()):
        data["CreditMemo"].append({"Id": ids[name], "Status": status})
        memo_line = f"9yx{i:012d}AAA"
        data["CreditMemoLine"].append({"Id": memo_line, "CreditMemoId": ids[name]})
        for j, target in enumerate(targets):
            data["CreditMemoLineInvoiceLine"].append({
                "Id": f"4sG{i:06d}{j:06d}AAA", "InvoiceLineId": line_of[ids[target]],
                "CreditMemoLineId": memo_line, "Amount": 5, "Type": "Applied",
                "UnappliedStatus": "No", "RelatedCrMemoLineInvcLineId": None})
    report = _verify(data, [ids[n] for n in invoices], [ids[n] for n in payments])
    report["ids"] = ids
    return report


def _balance_skips(report: dict) -> dict:
    """Subject id -> detail of every skipped balance check at record level."""
    return {r["subject"]: r["detail"] for r in report["checks"]
            if r["check"] in ("invoice_balance", "payment_balance") and r["status"] == "skip"}


def test_chain_fixture_is_clean_when_everything_is_measured():
    report = _chain({"A": "Posted", "B": "Posted", "C": "Posted"},
                    {"P1": ["A", "B"], "P2": ["B", "C"]}, {"M": ("Posted", ["A", "C"])})
    assert report["ok"] is True and report["skipped"] == 0, report["failed_checks"]


def test_propagation_reaches_a_record_an_earlier_link_already_passed():
    # Links sort (P1,B), (P2,A), (P2,B): one pass reaches P2 and B but not P1.
    report = _chain({"A": "Draft", "B": "Posted"}, {"P1": ["B"], "P2": ["A", "B"]})
    ids, skips = report["ids"], _balance_skips(report)
    assert set(skips) == {ids["A"], ids["B"], ids["P1"], ids["P2"]}
    assert f"origin invoice {ids['A']}: Status Draft" in skips[ids["P1"]]
    assert skips[ids["P1"]].startswith(f"linked invoice {ids['B']}; ")


def test_propagation_along_a_chain_names_the_origin_at_every_hop():
    # A - P1 - B - P2 - C, with C Draft: four hops back to A.
    report = _chain({"A": "Posted", "B": "Posted", "C": "Draft"},
                    {"P1": ["A", "B"], "P2": ["B", "C"]})
    ids, skips = report["ids"], _balance_skips(report)
    assert set(skips) == {ids[n] for n in ("A", "B", "C", "P1", "P2")}
    for name in ("A", "B", "P1", "P2"):
        assert f"origin invoice {ids['C']}: Status Draft" in skips[ids[name]], name
    assert skips[ids["A"]].startswith(f"linked payment {ids['P1']}; ")


def test_propagation_through_a_credit_memo_links_two_invoices():
    report = _chain({"A": "Draft", "B": "Posted"}, {"P1": ["B"]},
                    {"M": ("Posted", ["A", "B"])})
    ids, skips = report["ids"], _balance_skips(report)
    assert skips[ids["B"]].startswith(f"linked credit memo {ids['M']}; origin invoice "
                                      f"{ids['A']}: Status Draft")
    assert f"origin invoice {ids['A']}" in skips[ids["P1"]]


@pytest.mark.parametrize("status", ["Voided", "Draft", "Canceled", None])
def test_credit_memo_that_is_not_posted_skips_its_invoices(status):
    report = _chain({"A": "Posted", "B": "Posted", "C": "Posted"}, {},
                    {"M": (status, ["A", "B"])})
    ids, skips = report["ids"], _balance_skips(report)
    assert set(skips) == {ids["A"], ids["B"]}
    assert skips[ids["A"]] == (f"linked credit memo {ids['M']}; origin credit memo "
                               f"{ids['M']}: Status {status or 'null'}; only Posted credit "
                               "memos are measured")
    assert report["ok"] is True


def test_report_counts_checked_and_skipped_balance_checks():
    report = _line()
    assert (report["checked"], report["skipped"]) == (8, 1)
    assert render_text(report).endswith("RESULT: pass (8 checked, 1 skipped)")
    data = _load("line_level.json")
    _row(data, "Invoice", "3tt000000000002AAA")["Status"] = "Draft"
    none_run = _verify(data, ["3tt000000000002AAA"])
    assert (none_run["ok"], none_run["checked"], none_run["skipped"]) == (True, 0, 2)
    assert render_text(none_run).endswith("RESULT: pass (no balances checked; 2 skipped)")
    failed = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000001EAA").update(Balance=5))
    assert render_text(failed).endswith("RESULT: fail (payment_balance; 8 checked, 1 skipped)")


# ------------------------------------------------------------------ CLI

@pytest.fixture
def recorded_org(monkeypatch):
    data = _load("line_level.json")
    client = RecordedClient(data)
    monkeypatch.setattr(cli.SfRestClient, "from_alias",
                        classmethod(lambda cls, *a, **k: client))
    return client


def _manifest(tmp_path, name="DEMO-1", **ids) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps({"run_id": name, "kind": "sales_txn_quote", **ids}))
    return path


def test_cli_verify_manifest_json_passes(recorded_org, tmp_path, capsys):
    path = _manifest(tmp_path, invoice_id="3tt000000000001AAA")
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path), "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 0, report["failed_checks"]
    assert report["invoice_ids"] == ["3tt000000000001AAA"]
    assert recorded_org.writes == []


def test_cli_verify_invoice_ids_text_output(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids",
                   ",".join(LINE_INVOICES), "--payment-ids", LINE_EXTRA_PAYMENTS[0]])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip().endswith("RESULT: pass (8 checked, 1 skipped)")


def test_cli_verify_forced_wrong_level_exits_one_naming_the_check(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0],
                   "--expect-level", "header", "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert report["failed_checks"] == ["application_level"]


def test_cli_verify_latest_uses_newest_manifest(recorded_org, tmp_path, monkeypatch, capsys):
    # list_manifests returns newest first; the newest must win, not the last entry.
    newest = _manifest(tmp_path, "NEW", invoice_id="3tt000000000002AAA")
    middle = _manifest(tmp_path, "MID", invoice_id="3tt000000000003AAA")
    oldest = _manifest(tmp_path, "OLD", invoice_id="3tt000000000001AAA")
    monkeypatch.setattr(cli, "list_manifests", lambda: [newest, middle, oldest])
    rc = cli.main(["verify", "--org", "fake", "--latest", "--json"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["invoice_ids"] == ["3tt000000000002AAA"]


def test_cli_verify_empty_manifest_is_not_fatal_with_other_ids(recorded_org, tmp_path,
                                                               monkeypatch, capsys):
    empty = _manifest(tmp_path, "EMPTY")
    monkeypatch.setattr(cli, "list_manifests", lambda: [empty])
    rc = cli.main(["verify", "--org", "fake", "--latest", "--manifest", str(empty),
                   "--invoice-ids", LINE_INVOICES[1], "--json"])
    captured = capsys.readouterr()
    assert rc == 0
    assert json.loads(captured.out)["invoice_ids"] == [LINE_INVOICES[1]]
    assert "WARNING: manifest" in captured.err


def test_cli_verify_missing_manifest_is_a_clean_error(recorded_org, tmp_path, capsys):
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(tmp_path / "nope.json")])
    err = capsys.readouterr().err
    assert rc == 2
    assert err.startswith("ERROR: manifest not found")


@pytest.mark.parametrize("payload", ["[1, 2]", "\"text\"", "{not json"])
def test_cli_verify_manifest_that_is_not_an_object_is_a_clean_error(
        recorded_org, tmp_path, capsys, payload):
    path = tmp_path / "bad.json"
    path.write_text(payload)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path)])
    err = capsys.readouterr().err
    assert rc == 2
    assert err.startswith("ERROR: manifest") and "Traceback" not in err


@pytest.mark.parametrize("exc", [
    SfApiError(400, "INVALID_FIELD: No such column 'NetApplied'", "GET", "/query"),
    SfCliError("sf org display failed"),
])
def test_cli_verify_refused_read_is_a_clean_error(monkeypatch, capsys, exc):
    class Refusing(RecordedClient):
        def query(self, soql):
            raise exc
    monkeypatch.setattr(cli.SfRestClient, "from_alias",
                        classmethod(lambda cls, *a, **k: Refusing({})))
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0]])
    assert rc == 2
    assert capsys.readouterr().err.startswith("ERROR: Salesforce request failed")


def test_cli_verify_manifest_without_ids_exits_two(recorded_org, tmp_path, capsys):
    path = _manifest(tmp_path)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path)])
    assert rc == 2
    assert "names no invoice or payment id" in capsys.readouterr().err


def test_cli_verify_error_with_json_prints_an_error_object(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", "3tt00000000000ZAAQ",
                   "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["ok"] is False and "not found" in out["error"]


def test_cli_verify_payment_ids_only(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake", "--payment-ids", "0aQ000000000001EAA",
                   "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 0, report["failed_checks"]
    assert report["invoice_ids"] == []
    assert report["payment_ids"] == ["0aQ000000000001EAA"]
    assert {r["check"] for r in report["checks"]} == {"payment_balance"}


def test_cli_verify_needs_some_ids(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake"])
    assert rc == 2
    assert "verify needs" in capsys.readouterr().err



def _assert_error_exit(rc, capsys, fragment):
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err.startswith("ERROR: ") and fragment in captured.err
    assert "Traceback" not in captured.err
    out = json.loads(captured.out)
    assert out["ok"] is False and fragment in out["error"]


@pytest.mark.parametrize("ids", [{"invoice_id": 3}, {"payment_ids": [None]}])
def test_cli_verify_manifest_with_non_string_id_exits_two(recorded_org, tmp_path,
                                                          capsys, ids):
    path = _manifest(tmp_path, **ids)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path), "--json"])
    _assert_error_exit(rc, capsys, "must be a string id")


def test_cli_verify_manifest_that_is_not_utf8_exits_two(recorded_org, tmp_path, capsys):
    path = tmp_path / "latin1.json"
    path.write_bytes(b'{"invoice_id": "caf\xe9"}')
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path), "--json"])
    _assert_error_exit(rc, capsys, "could not be read as JSON")


@pytest.mark.parametrize("exc", [requests.ConnectionError("connection refused"),
                                 requests.HTTPError("401 Client Error")])
def test_cli_verify_latest_api_version_lookup_failure_exits_two(monkeypatch, capsys, exc):
    monkeypatch.setattr(auth, "resolve_auth", lambda alias: ("token", "https://x.invalid"))

    def refuse(self):
        raise exc
    monkeypatch.setattr(auth.SfRestClient, "_latest_api_version", refuse)
    rc = cli.main(["verify", "--org", "fake", "--api-version", "latest",
                   "--invoice-ids", LINE_INVOICES[0], "--json"])
    _assert_error_exit(rc, capsys, "Salesforce request failed")


def test_cli_verify_without_sf_on_path_exits_two(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("PATH", str(tmp_path))
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0], "--json"])
    _assert_error_exit(rc, capsys, "sf CLI was not found")


def test_cli_verify_other_os_error_exits_two(monkeypatch, capsys):
    def boom(alias):
        raise PermissionError(13, "Permission denied", "sf")
    monkeypatch.setattr(auth, "resolve_auth", boom)
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0], "--json"])
    _assert_error_exit(rc, capsys, "could not run a command or read a file")


@pytest.mark.parametrize("argv, fragment", [
    (["verify", "--invoice-ids", "x", "--json"], "--org"),
    (["verify", "--org", "fake", "--expect-level", "both", "--json"], "--expect-level"),
])
def test_cli_verify_usage_error_with_json_prints_an_error_object(capsys, argv, fragment):
    with pytest.raises(SystemExit) as raised:
        cli.main(argv)
    captured = capsys.readouterr()
    assert raised.value.code == 2
    assert "usage:" in captured.err and fragment in captured.err
    out = json.loads(captured.out)
    assert out["ok"] is False and fragment in out["error"]


def test_cli_verify_usage_error_without_json_prints_no_object(capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(["verify", "--invoice-ids", "x"])
    captured = capsys.readouterr()
    assert raised.value.code == 2 and captured.out == ""
    assert "usage:" in captured.err


@pytest.mark.parametrize("argv, fragment", [
    (["verify", "--org", "x", "--json", "--bogus"], "unrecognized arguments: --bogus"),
    (["verify", "--org", "x", "--json", "extra"], "unrecognized arguments: extra"),
    (["verify", "--org", "x", "--json", "--expect"], "unrecognized arguments: --expect"),
])
def test_cli_verify_top_level_usage_errors_print_one_json_object(capsys, argv, fragment):
    with pytest.raises(SystemExit) as raised:
        cli.main(argv)
    captured = capsys.readouterr()
    assert raised.value.code == 2
    assert "usage:" in captured.err and fragment in captured.err
    out = json.loads(captured.out)  # exactly one object: a second would not parse
    assert out == {"ok": False, "error": f"usage: {fragment}"}


def test_cli_verify_refuses_abbreviated_json(capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(["verify", "--org", "x", "--invoice-ids", LINE_INVOICES[0], "--jso"])
    captured = capsys.readouterr()
    assert raised.value.code == 2
    assert "unrecognized arguments: --jso" in captured.err and captured.out == ""


def test_other_subcommands_keep_plain_usage_errors_and_abbreviations(capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(["prune", "--older-than", "7d", "--json"])
    captured = capsys.readouterr()
    assert raised.value.code == 2 and captured.out == ""
    assert "unrecognized arguments: --json" in captured.err
    args = cli.parse_args(["prune", "--older", "7d"])  # abbreviation still accepted
    assert args.older_than == "7d"


def test_cli_verify_unexpected_value_error_exits_two(monkeypatch, capsys):
    # Undecodable sf output: a ValueError main() would otherwise report as exit 1.
    def bad_output(alias):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
    monkeypatch.setattr(auth, "resolve_auth", bad_output)
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0], "--json"])
    _assert_error_exit(rc, capsys, "unexpected UnicodeDecodeError")


def test_cli_verify_latest_api_version_with_odd_body_exits_two(monkeypatch, capsys):
    # A non-list body from /services/data/ makes [-1] a KeyError, not a traceback.
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"versions": []}

    class Session:
        def get(self, url):
            return Response()

    monkeypatch.setattr(auth, "resolve_auth", lambda alias: ("token", "https://x.invalid"))
    monkeypatch.setattr(auth.SfRestClient, "_session", property(lambda self: Session()))
    rc = cli.main(["verify", "--org", "fake", "--api-version", "latest",
                   "--invoice-ids", LINE_INVOICES[0], "--json"])
    _assert_error_exit(rc, capsys, "unexpected KeyError")


def test_cli_verify_closed_stdout_keeps_the_exit_code(recorded_org, monkeypatch):
    # `verify --json | head -1`: the reader closes the pipe; no traceback, and the
    # exit code is still the checks' result.
    class ClosedPipe:
        def write(self, text):
            raise BrokenPipeError(32, "Broken pipe")

        def flush(self):
            raise BrokenPipeError(32, "Broken pipe")

        def fileno(self):
            raise ValueError("no descriptor")

    monkeypatch.setattr(sys, "stdout", ClosedPipe())
    assert cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0],
                     "--json"]) == 0
    assert cli.main(["verify", "--org", "fake", "--invoice-ids", LINE_INVOICES[0],
                     "--expect-level", "header"]) == 1
    assert cli.main(["verify", "--org", "fake", "--invoice-ids", "3tt00000000000ZAAQ",
                     "--json"]) == 2


def test_cli_verify_json_usage_error_on_a_closed_pipe_exits_two(monkeypatch):
    # `verify --json --bogus | true`: the JSON error object meets a closed pipe.
    class ClosedPipe:
        def write(self, text):
            raise BrokenPipeError(32, "Broken pipe")

        def flush(self):
            raise BrokenPipeError(32, "Broken pipe")

        def fileno(self):
            raise ValueError("no descriptor")

    monkeypatch.setattr(sys, "stdout", ClosedPipe())
    with pytest.raises(SystemExit) as raised:
        cli.main(["verify", "--org", "x", "--json", "--bogus"])
    assert raised.value.code == 2


@pytest.mark.parametrize("drop, message", [
    (("CreditMemoLine", "9yx000000000001AAA"), "credit memo line ids not found"),
    (("CreditMemo", "50g000000000011AAA"), "credit memo ids not found"),
])
def test_cli_verify_unreadable_credit_memo_exits_two(monkeypatch, capsys, drop, message):
    data = _load("line_level.json")
    obj, record_id = drop
    data[obj] = [r for r in data[obj] if r["Id"] != record_id]
    monkeypatch.setattr(cli.SfRestClient, "from_alias",
                        classmethod(lambda cls, *a, **k: RecordedClient(data)))
    rc = cli.main(["verify", "--org", "fake", "--invoice-ids", "3tt000000000003AAA", "--json"])
    _assert_error_exit(rc, capsys, message)


def test_header_credit_rows_read_their_memo():
    # The memo is reached only through a CreditMemoInvApplication row.
    data = _load("header_level.json")
    records = fetch_records(RecordedClient(data), ["3tt0000000000H1AAI"])
    assert [r["Id"] for r in records["CreditMemo"]] == ["50g000000000001AAA"]
    assert records["CreditMemoLine"] == []


def test_level_line_names_the_source_only_when_it_differs():
    assert render_text(_line()).startswith("Level: line (records)\n")
    undetermined = _verify(_load("line_level.json"), ["3tt000000000002AAA"])
    assert render_text(undetermined).startswith("Level: undetermined\n")


def test_split_ids_accepts_spaces_commas_and_repeats():
    a, b, c = LINE_INVOICES
    assert split_ids([f"{a} {b}", f"{c},{a}"], "ids") == [a, b, c]
    assert split_ids([f" {a}\t{b} ,  {c} "], "ids") == [a, b, c]


def test_cli_verify_json_error_on_a_really_closed_pipe_exits_two():
    # A real child process whose stdout reader is gone: without redirecting the
    # descriptor, the interpreter's final flush fails and the exit code becomes 120.
    import subprocess
    root = Path(__file__).resolve().parents[2]
    proc = subprocess.Popen(
        [sys.executable, "-m", "scripts.txn_data_harness.cli", "verify", "--org", "x",
         "--json", "--bogus"],
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.stdout.close()
    stderr = proc.stderr.read().decode()
    proc.stderr.close()
    assert proc.wait(timeout=60) == 2, stderr
    assert "Exception ignored" not in stderr and "Traceback" not in stderr


def test_cli_verify_latest_without_manifests_says_so(monkeypatch, capsys):
    monkeypatch.setattr(cli, "list_manifests", lambda: [])
    rc = cli.main(["verify", "--org", "fake", "--latest", "--json"])
    _assert_error_exit(rc, capsys, "No manifests found.")


@pytest.mark.parametrize("level", ["both", "", None])
def test_run_checks_rejects_an_unknown_expected_level(level):
    with pytest.raises(VerifyError, match="expect_level must be auto, line or header"):
        run_checks({"Invoice": []}, level)


def test_line_payment_rollup_on_the_wrong_line_fails():
    # INV1 gets a second line. The payment row stays on line 11 while the rollup sits
    # on line 12; each line's Balance matches its own rollup and the invoice totals
    # are untouched, so only the per-line payment comparison can fail.
    def mutate(data):
        _row(data, "InvoiceLine", "5TV000000000011GAA").update(NetPaymentsApplied=0,
                                                              Balance=4950)
        data["InvoiceLine"].append({
            "Id": "5TV000000000012GAA", "InvoiceId": "3tt000000000001AAA", "Type": "Charge",
            "LineAmount": 0, "NetCreditsApplied": 0, "NetPaymentsApplied": 1000,
            "Balance": -1000, **dict.fromkeys(verify_mod._UNMEASURED_LINE_FIELDS)})
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_line_balance"]
    failed = {r["subject"]: r["detail"] for r in report["checks"] if r["status"] == "fail"}
    assert set(failed) == {"3tt000000000001AAA/5TV000000000011GAA",
                           "3tt000000000001AAA/5TV000000000012GAA"}
    assert all("PaymentLineInvoiceLine rows" in d for d in failed.values())


@pytest.mark.parametrize("obj, record_id, update, check, subject", [
    # Each null is placed where reading it as 0 would make the check pass.
    ("Invoice", "3tt000000000003AAA", {"TotalAmountWithTax": 100, "Balance": None},
     "invoice_balance", "3tt000000000003AAA"),
    ("Invoice", "3tt000000000002AAA", {"TotalAmountWithTax": None, "Balance": 0},
     "invoice_balance", "3tt000000000002AAA"),
    ("InvoiceLine", "5TV000000000031GAA", {"Balance": None},
     "invoice_line_balance", "3tt000000000003AAA/5TV000000000031GAA"),
    ("InvoiceLine", "5TV000000000032GAA", {"LineAmount": None, "Balance": 0},
     "invoice_line_balance", "3tt000000000003AAA/5TV000000000032GAA"),
    ("Payment", "0aQ000000000001EAA", {"Balance": None},
     "payment_balance", "0aQ000000000001EAA"),
    ("Payment", "0aQ000000000001EAA", {"Amount": None, "Balance": -1000},
     "payment_balance", "0aQ000000000001EAA"),
])
def test_null_amount_fails_instead_of_reading_as_zero(obj, record_id, update, check, subject):
    report = _line(mutate=lambda d: _row(d, obj, record_id).update(update))
    result = next(r for r in report["checks"]
                  if r["check"] == check and r["subject"] == subject)
    assert result["status"] == "fail" and "null" in result["detail"]


def test_cli_verify_checks_the_payment_ids_a_manifest_names(recorded_org, tmp_path, capsys):
    # 0aQ...2 has no application rows: only the manifest's payment_ids can bring it in.
    path = _manifest(tmp_path, invoice_id="3tt000000000002AAA",
                     payment_ids=["0aQ000000000002EAA"])
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path), "--json"])
    report = json.loads(capsys.readouterr().out)
    assert rc == 0, report["failed_checks"]
    assert report["payment_ids"] == ["0aQ000000000002EAA"]


def test_fetch_with_no_ids_is_an_error():
    client = RecordedClient({})
    with pytest.raises(VerifyError, match="no invoice or payment ids to verify"):
        fetch_records(client, [], [])
    assert client.queries == []


def test_failed_checks_follow_the_check_order():
    def mutate(data):
        _row(data, "Payment", "0aQ000000000002EAA")["Balance"] = 1
        _row(data, "Invoice", "3tt000000000002AAA")["Balance"] = 1
        _row(data, "InvoiceLine", "5TV000000000031GAA")["Balance"] = 1
    report = _line(level="header", mutate=mutate)
    assert report["failed_checks"] == list(CHECK_NAMES)


# -- todo 490: a measured unapply pair is checked, not skipped -------------------

def _unapply_payment_row(data, *, amount=1000, related="1Al000000000001CAA", reversals=1):
    """INV1's payment row unapplied as measured live: the original flagged Yes, a
    positive Unapplied row pointing at it, and the rollups back to unpaid."""
    _row(data, "PaymentLineInvoiceLine", "1Al000000000001CAA")["UnappliedStatus"] = "Yes"
    for n in range(reversals):
        data["PaymentLineInvoiceLine"].append({
            "Id": f"1Al00000000009{n}CAA", "InvoiceLineId": "5TV000000000011GAA",
            "PaymentId": "0aQ000000000001EAA", "Amount": amount, "Type": "Unapplied",
            "UnappliedStatus": "NA", "RelatedPaymentLineInvcLineId": related})
    for obj, rid in (("Invoice", "3tt000000000001AAA"), ("InvoiceLine", "5TV000000000011GAA")):
        _row(data, obj, rid).update(NetPaymentsApplied=0, Balance=4950)
    _row(data, "Payment", "0aQ000000000001EAA").update(NetApplied=0, Balance=1000)


def _inv1_and_payment(report) -> dict:
    return {(r["check"], r["subject"]): r for r in report["checks"]
            if r["subject"].startswith(("3tt000000000001AAA", "0aQ000000000001EAA"))
            and r["check"] != "application_level"}


def test_a_reversed_payment_pair_is_checked_and_nets_to_zero():
    report = _line(mutate=_unapply_payment_row)
    assert report["ok"] is True, report["failed_checks"]
    results = _inv1_and_payment(report)
    assert {k[0] for k in results} == {"invoice_balance", "invoice_line_balance",
                                       "payment_balance"}
    assert all(r["status"] == "pass" for r in results.values()), results
    assert results[("payment_balance", "0aQ000000000001EAA")]["detail"].endswith(
        "1000 = 1000 - 0")


def test_a_reversed_pair_with_a_stale_rollup_fails():
    # The pair nets to zero, so a rollup still showing the payment applied disagrees.
    def mutate(data):
        _unapply_payment_row(data)
        _row(data, "Invoice", "3tt000000000001AAA").update(NetPaymentsApplied=1000,
                                                           Balance=3950)
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["invoice_balance"]
    assert "NetPaymentsApplied 1000 != payment rows 0" in next(
        r["detail"] for r in report["checks"] if r["check"] == "invoice_balance"
        and r["subject"] == "3tt000000000001AAA")


def _unflag(data):
    _row(data, "PaymentLineInvoiceLine", "1Al000000000001CAA")["UnappliedStatus"] = "No"


def _move_reversal(data):
    _row(data, "PaymentLineInvoiceLine", "1Al000000000090CAA")["InvoiceLineId"] = (
        "5TV000000000021GAA")


def _flag_reversal(data):
    _row(data, "PaymentLineInvoiceLine", "1Al000000000090CAA")["UnappliedStatus"] = "Yes"


def _other_payment(data):
    _row(data, "PaymentLineInvoiceLine", "1Al000000000090CAA")["PaymentId"] = (
        "0aQ000000000002EAA")


@pytest.mark.parametrize("kwargs, after, why", [
    ({"amount": 999}, None, "an Unapplied row of another amount"),
    ({"related": "1Al000000000099CAA"}, None, "an Unapplied row reversing another row"),
    ({"reversals": 2}, None, "two Unapplied rows for one Applied row"),
    ({}, _unflag, "the reversed Applied row not flagged Yes"),
    ({}, _move_reversal, "the Unapplied row on another invoice line"),
    ({}, _other_payment, "the Unapplied row on another payment"),
    ({}, _flag_reversal, "the Unapplied row itself flagged Yes"),
])
def test_a_pair_that_is_not_the_measured_shape_is_skipped(kwargs, after, why):
    def mutate(data):
        _unapply_payment_row(data, **kwargs)
        if after:
            after(data)
    report = _line(mutate=mutate)
    assert report["ok"] is True, (why, report["failed_checks"])
    results = _inv1_and_payment(report)
    assert all(r["status"] == "skip" and "measured on 264" in r["detail"]
               for r in results.values()), why


def test_a_reversed_credit_pair_is_checked():
    def mutate(data):
        _row(data, "CreditMemoLineInvoiceLine", "4sG000000000001EAA")["UnappliedStatus"] = "Yes"
        data["CreditMemoLineInvoiceLine"].append({
            "Id": "4sG000000000009EAA", "InvoiceLineId": "5TV000000000031GAA",
            "CreditMemoLineId": _row(data, "CreditMemoLineInvoiceLine",
                                     "4sG000000000001EAA")["CreditMemoLineId"],
            "Amount": 40, "Type": "Unapplied", "UnappliedStatus": "NA",
            "RelatedCrMemoLineInvcLineId": "4sG000000000001EAA"})
        _row(data, "Invoice", "3tt000000000003AAA").update(NetCreditsApplied=60, Balance=190)
        _row(data, "InvoiceLine", "5TV000000000031GAA").update(NetCreditsApplied=60, Balance=40)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    inv3 = [r for r in report["checks"] if r["subject"].startswith("3tt000000000003AAA")
            and r["check"] in ("invoice_balance", "invoice_line_balance")]
    assert inv3 and all(r["status"] == "pass" for r in inv3), inv3


def test_a_credit_pair_on_another_memo_line_is_skipped():
    def mutate(data):
        applied = _row(data, "CreditMemoLineInvoiceLine", "4sG000000000001EAA")
        applied["UnappliedStatus"] = "Yes"
        memo = _row(data, "CreditMemoLine", applied["CreditMemoLineId"])["CreditMemoId"]
        data["CreditMemoLine"].append({"Id": "9yx000000000099EAA", "CreditMemoId": memo})
        data["CreditMemoLineInvoiceLine"].append({
            "Id": "4sG000000000009EAA", "InvoiceLineId": "5TV000000000031GAA",
            "CreditMemoLineId": "9yx000000000099EAA", "Amount": 40, "Type": "Unapplied",
            "UnappliedStatus": "NA", "RelatedCrMemoLineInvcLineId": "4sG000000000001EAA"})
        _row(data, "Invoice", "3tt000000000003AAA").update(NetCreditsApplied=60, Balance=190)
        _row(data, "InvoiceLine", "5TV000000000031GAA").update(NetCreditsApplied=60, Balance=40)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    inv3 = [r for r in report["checks"] if r["subject"].startswith("3tt000000000003AAA")
            and r["check"] in ("invoice_balance", "invoice_line_balance")]
    assert inv3 and all(r["status"] == "skip" for r in inv3), inv3


def test_every_pair_reversed_on_one_invoice_checks_with_settlement_level_null():
    # As measured: everything unapplied, SettlementLevel back to null; the flagged
    # rows still show the level.
    def mutate(data):
        for rid, new_id, amount in (("4sG000000000001EAA", "4sG000000000009EAA", 40),
                                    ("4sG000000000002EAA", "4sG000000000008EAA", 60)):
            applied = _row(data, "CreditMemoLineInvoiceLine", rid)
            applied["UnappliedStatus"] = "Yes"
            data["CreditMemoLineInvoiceLine"].append({
                "Id": new_id,
                "InvoiceLineId": applied["InvoiceLineId"],
                "CreditMemoLineId": applied["CreditMemoLineId"], "Amount": amount,
                "Type": "Unapplied", "UnappliedStatus": "NA",
                "RelatedCrMemoLineInvcLineId": rid})
        _row(data, "Invoice", "3tt000000000003AAA").update(
            NetCreditsApplied=0, Balance=250, SettlementLevel=None)
        _row(data, "InvoiceLine", "5TV000000000031GAA").update(NetCreditsApplied=0, Balance=100)
    report = _line(mutate=mutate)
    assert report["ok"] is True, report["failed_checks"]
    inv3 = {(r["check"], r["subject"]): r["status"] for r in report["checks"]
            if r["subject"].startswith("3tt000000000003AAA")}
    assert inv3[("application_level", "3tt000000000003AAA")] == "pass"
    assert inv3[("invoice_balance", "3tt000000000003AAA")] == "pass"
    assert inv3[("invoice_line_balance", "3tt000000000003AAA/5TV000000000031GAA")] == "pass"


def test_a_reversed_payment_absorbed_by_another_invoice_nets_both():
    # As measured: the reversed payment's open amount applied to the account's next
    # invoice (outside the set); its rows net 1000 - 1000 + 495.
    data = _load("line_level.json")
    _unapply_payment_row(data)
    data["PaymentLineInvoiceLine"].append({
        "Id": "1Al000000000080CAA", "InvoiceLineId": "5TV000000000021GAA",
        "PaymentId": "0aQ000000000001EAA", "Amount": 495, "Type": "Applied",
        "UnappliedStatus": "No", "RelatedPaymentLineInvcLineId": None})
    _row(data, "Payment", "0aQ000000000001EAA").update(NetApplied=495, Balance=505)
    report = _verify(data, ["3tt000000000001AAA"], ["0aQ000000000001EAA"])
    assert report["ok"] is True, report["failed_checks"]
    result = next(r for r in report["checks"] if r["check"] == "payment_balance")
    assert result["status"] == "pass" and result["detail"].endswith("505 = 1000 - 495")
