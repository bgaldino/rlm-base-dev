"""Offline tests for the read-only billing verifier (``cli verify``).

Each fixture under ``fixtures/billing_verify/`` is a set of recorded query results,
one list of rows per object. ``RecordedClient`` answers the verifier's SOQL from
them, filtering on the ``WHERE <field> IN (...)`` clause, so the fetch path runs
too. The clean fixtures must pass every check; each negative test breaks one fact
and asserts that exactly the matching check fails.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.txn_data_harness import cli
from scripts.txn_data_harness.auth import SfApiError, SfCliError
from scripts.txn_data_harness.verify import (
    CHECK_NAMES,
    VerifyError,
    fetch_billing_records,
    ids_from_manifest,
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
    """Answers SELECT ... WHERE f IN (...) from recorded rows; refuses any write."""

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
            if row.get(match["field"]) in wanted:
                out.append({"attributes": {"type": match["obj"]},
                            **{f: row.get(f) for f in fields}})
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
    records = fetch_billing_records(client, invoices, payments)
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
    for check in CHECK_NAMES:
        assert _statuses(report, check) == {"pass"}, check
    # Payments found through application rows, plus the one asked for by id.
    assert set(report["payment_ids"]) == {
        "0aQ000000000001EAA", "0aQ000000000002EAA", "0aQ000000000003EAA"}


def test_header_level_fixture_passes_and_skips_line_balances():
    report = _header()
    assert report["failed_checks"] == [], report["failed_checks"]
    assert (report["level"], report["level_source"]) == ("header", "records")
    by_subject = {r["subject"]: r for r in report["checks"]
                  if r["check"] == "invoice_line_balance"}
    assert by_subject["3tt0000000000H1AAI"]["status"] == "skip"
    # The payment's row on an invoice outside the set still counts for NetApplied.
    payment = next(r for r in report["checks"] if r["check"] == "payment_balance")
    assert payment["status"] == "pass"
    assert report["invoice_ids"] == HEADER_INVOICES


def test_verifier_only_reads():
    data = _load("line_level.json")
    client = RecordedClient(data)
    fetch_billing_records(client, LINE_INVOICES, LINE_EXTRA_PAYMENTS)
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
            "HasBeenUnapplied": "No", "AssociatedPaymentLineId": None})
    report = _line(mutate=add_header_row)
    assert report["level_source"] == "mixed"
    assert "application_level" in report["failed_checks"]


def test_settlement_level_contradicting_expectation_fails():
    report = _line(level="line", mutate=lambda d: _row(
        d, "Invoice", "3tt000000000002AAA").update(SettlementLevel="Invoice"))
    assert report["failed_checks"] == ["application_level"]


# ------------------------------------------------------------------ invoice_balance

@pytest.mark.parametrize("runner, invoice", [
    (_line, "3tt000000000001AAA"), (_header, "3tt0000000000H1AAI")])
def test_invoice_balance_off_by_one_fails(runner, invoice):
    report = runner(mutate=lambda d: _row(d, "Invoice", invoice).update(
        Balance=_row(d, "Invoice", invoice)["Balance"] + 1))
    assert report["failed_checks"] == ["invoice_balance"]
    failed = [r for r in report["checks"] if r["status"] == "fail"]
    assert [r["subject"] for r in failed] == [invoice]


@pytest.mark.parametrize("runner, invoice", [
    (_line, "3tt000000000003AAA"), (_header, "3tt0000000000H1AAI")])
def test_invoice_rollup_disagreeing_with_rows_fails(runner, invoice):
    def mutate(data):
        inv = _row(data, "Invoice", invoice)
        inv.update(NetCreditsApplied=inv["NetCreditsApplied"] - 1,
                   Balance=inv["Balance"] + 1)  # arithmetic still holds
    report = runner(mutate=mutate)
    assert report["failed_checks"] == ["invoice_balance"]
    detail = next(r["detail"] for r in report["checks"] if r["status"] == "fail")
    assert "credit rows" in detail


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
    (_line, "0aQ000000000002EAA"), (_header, "0aQ0000000000H1EAI")])
def test_payment_balance_off_by_one_fails(runner, payment):
    report = runner(mutate=lambda d: _row(d, "Payment", payment).update(
        Balance=_row(d, "Payment", payment)["Balance"] + 1))
    assert report["failed_checks"] == ["payment_balance"]


def test_payment_net_applied_disagreeing_with_rows_fails():
    def mutate(data):
        _row(data, "Payment", "0aQ0000000000H1EAI").update(NetApplied=300, Balance=200)
    report = _header(mutate=mutate)
    assert report["failed_checks"] == ["payment_balance"]


@pytest.mark.parametrize("field", ["NetRefundApplied", "NetPaymentCreditApplied"])
def test_payment_with_unmeasured_field_is_skipped_not_failed(field):
    # Balance deliberately inconsistent: a skip must not hide behind a pass or a fail.
    report = _line(mutate=lambda d: _row(d, "Payment", "0aQ000000000002EAA").update(
        {field: 25, "Balance": 975}))
    assert report["ok"] is True
    result = next(r for r in report["checks"]
                  if r["check"] == "payment_balance" and r["subject"] == "0aQ000000000002EAA")
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


# ------------------------------------------------------------------ unapplied_rows

def test_unapplied_row_with_negative_amount_still_nets_to_zero():
    # The sign of an Unapplied row's Amount is not measured; either sign nets out.
    report = _line(mutate=lambda d: _row(d, "PaymentLineInvoiceLine", "1Al000000000003CAA")
                   .update(Amount=-50))
    assert report["ok"] is True, report["failed_checks"]


def test_header_unapplied_pairs_pass_and_break_on_the_header_flag():
    report = _header()
    subjects = {r["subject"]: r["status"] for r in report["checks"]
                if r["check"] == "unapplied_rows"}
    assert subjects == {"PaymentLineInvoice/0b8000000000004AAA": "pass",
                        "CreditMemoInvApplication/0c0000000000003AAA": "pass"}
    broken = _header(mutate=lambda d: _row(d, "PaymentLineInvoice", "0b8000000000003AAA")
                     .update(HasBeenUnapplied="No"))
    assert broken["failed_checks"] == ["unapplied_rows"]
    dangling = _header(mutate=lambda d: _row(d, "CreditMemoInvApplication",
                                             "0c0000000000003AAA").update(
        AssociatedLineId="0c0000000000099AAA"))
    assert dangling["failed_checks"] == ["unapplied_rows"]


def test_applied_row_marked_unapplied_paired_with_another_applied_row_fails():
    def mutate(data):
        # The partner exists but is Applied, not Unapplied; both still net the same.
        row = _row(data, "PaymentLineInvoiceLine", "1Al000000000003CAA")
        row.update(Type="Applied", Amount=0, UnappliedStatus="NA")
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(NetPaymentsApplied=50,
                                                              Balance=100)
        _row(data, "Invoice", "3tt000000000003AAA").update(NetPaymentsApplied=50, Balance=100)
        _row(data, "Payment", "0aQ000000000003EAA").update(NetApplied=50, Balance=0)
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["unapplied_rows"]
    detail = next(r["detail"] for r in report["checks"] if r["status"] == "fail")
    assert "no Unapplied row" in detail


def test_dangling_unapplied_row_fails():
    def drop_applied(data):
        data["PaymentLineInvoiceLine"] = [
            r for r in data["PaymentLineInvoiceLine"] if r["Id"] != "1Al000000000002CAA"]
        # Keep balances consistent so only the pairing check can fail: with the
        # Applied row gone the net is -50, so mirror it in the rollups.
        _row(data, "InvoiceLine", "5TV000000000032GAA").update(
            NetPaymentsApplied=-50, Balance=200)
        _row(data, "Invoice", "3tt000000000003AAA").update(
            NetPaymentsApplied=-50, Balance=200)
        _row(data, "Payment", "0aQ000000000003EAA").update(NetApplied=-50, Balance=100)
    report = _line(mutate=drop_applied)
    assert report["failed_checks"] == ["unapplied_rows"]


def test_applied_row_marked_unapplied_without_its_pair_fails():
    def mutate(data):
        data["PaymentLineInvoiceLine"][0]["UnappliedStatus"] = "Yes"
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["unapplied_rows"]


def test_unapplied_pair_whose_applied_row_is_not_marked_fails():
    def mutate(data):
        _row(data, "PaymentLineInvoiceLine", "1Al000000000002CAA")["UnappliedStatus"] = "No"
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["unapplied_rows"]


# ------------------------------------------------------------------ inputs

def test_unknown_invoice_id_is_an_error():
    with pytest.raises(VerifyError, match="not found"):
        fetch_billing_records(RecordedClient(_load("line_level.json")),
                              ["3tt00000000000ZAAQ"])


def test_unknown_payment_id_is_an_error():
    with pytest.raises(VerifyError, match="payment ids not found"):
        fetch_billing_records(RecordedClient(_load("line_level.json")),
                              [LINE_INVOICES[1]], ["0aQ00000000000ZEAQ"])


def test_fifteen_character_ids_are_normalized_and_deduplicated():
    data = _load("line_level.json")
    client = RecordedClient(data)
    records = fetch_billing_records(
        client, [LINE_INVOICES[0][:15], LINE_INVOICES[0], LINE_INVOICES[0][:15]],
        [LINE_EXTRA_PAYMENTS[0][:15]])
    assert [r["Id"] for r in records["Invoice"]] == [LINE_INVOICES[0]]
    assert LINE_EXTRA_PAYMENTS[0] in {r["Id"] for r in records["Payment"]}
    assert run_checks(records)["ok"] is True


def test_fifteen_character_id_gets_the_case_safe_suffix():
    # Real 264 org ids: the suffix encodes which of the first 15 characters are upper case.
    assert split_ids(["3ttWt000002lg4H, 0aQWt000000XOLJ"], "ids") == [
        "3ttWt000002lg4HIAQ", "0aQWt000000XOLJMA4"]


def test_eighteen_character_id_with_wrong_suffix_is_rejected():
    with pytest.raises(VerifyError, match="checksum"):
        split_ids(["3ttWt000002lg4HAAA"], "ids")
    # The suffix is case-insensitive.
    assert split_ids(["3ttWt000002lg4Hiaq"], "ids") == ["3ttWt000002lg4HIAQ"]


def test_malformed_id_is_rejected_before_any_query():
    client = RecordedClient({})
    with pytest.raises(VerifyError, match="not a Salesforce id"):
        fetch_billing_records(client, ["3tt' OR Id != '"])
    assert client.queries == []


def test_ids_from_manifest_reads_invoice_and_payment_keys(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({
        "run_id": "run", "kind": "sales_txn_quote", "invoice_id": "3tt000000000001AAA",
        "payment_ids": ["0aQ000000000001EAA"]}))
    assert ids_from_manifest(path) == (["3tt000000000001AAA"], ["0aQ000000000001EAA"])


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
    assert out.strip().endswith("RESULT: pass")


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
    assert rc == 1
    assert err.startswith("ERROR: manifest not found")


@pytest.mark.parametrize("payload", ["[1, 2]", "\"text\"", "{not json"])
def test_cli_verify_manifest_that_is_not_an_object_is_a_clean_error(
        recorded_org, tmp_path, capsys, payload):
    path = tmp_path / "bad.json"
    path.write_text(payload)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path)])
    err = capsys.readouterr().err
    assert rc == 1
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
    assert rc == 1
    assert capsys.readouterr().err.startswith("ERROR: Salesforce request failed")


def test_cli_verify_manifest_without_ids_exits_one(recorded_org, tmp_path, capsys):
    path = _manifest(tmp_path)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path)])
    assert rc == 1
    assert "names no invoice or payment id" in capsys.readouterr().err


def test_cli_verify_needs_some_ids(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake"])
    assert rc == 1
    assert "verify needs" in capsys.readouterr().err

