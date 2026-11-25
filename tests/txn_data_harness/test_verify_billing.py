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
from scripts.txn_data_harness.verify import (
    CHECK_NAMES,
    VerifyError,
    fetch_billing_records,
    ids_from_manifest,
    run_checks,
)

FIXTURES = Path(__file__).parent / "fixtures" / "billing_verify"
LINE_INVOICES = ["3tt000000000001AAA", "3tt000000000002AAA", "3tt000000000003AAA"]
LINE_EXTRA_PAYMENTS = ["0aQ000000000002AAA"]  # Canceled, no applications
HEADER_INVOICES = ["3tt0000000000H1AAA", "3tt0000000000H2AAA"]

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
        "0aQ000000000001AAA", "0aQ000000000002AAA", "0aQ000000000003AAA"}


def test_header_level_fixture_passes_and_skips_line_balances():
    report = _header()
    assert report["failed_checks"] == [], report["failed_checks"]
    assert (report["level"], report["level_source"]) == ("header", "records")
    by_subject = {r["subject"]: r for r in report["checks"]
                  if r["check"] == "invoice_line_balance"}
    assert by_subject["3tt0000000000H1AAA"]["status"] == "skip"
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
            "PaymentId": "0aQ000000000002AAA", "Amount": 0, "Type": "Applied",
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
    (_line, "3tt000000000001AAA"), (_header, "3tt0000000000H1AAA")])
def test_invoice_balance_off_by_one_fails(runner, invoice):
    report = runner(mutate=lambda d: _row(d, "Invoice", invoice).update(
        Balance=_row(d, "Invoice", invoice)["Balance"] + 1))
    assert report["failed_checks"] == ["invoice_balance"]
    failed = [r for r in report["checks"] if r["status"] == "fail"]
    assert [r["subject"] for r in failed] == [invoice]


@pytest.mark.parametrize("runner, invoice", [
    (_line, "3tt000000000003AAA"), (_header, "3tt0000000000H1AAA")])
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
    report = _line(mutate=lambda d: _row(d, "InvoiceLine", "5TV000000000031AAA").update(
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
    (_line, "0aQ000000000002AAA"), (_header, "0aQ0000000000H1AAA")])
def test_payment_balance_off_by_one_fails(runner, payment):
    report = runner(mutate=lambda d: _row(d, "Payment", payment).update(
        Balance=_row(d, "Payment", payment)["Balance"] + 1))
    assert report["failed_checks"] == ["payment_balance"]


def test_payment_net_applied_disagreeing_with_rows_fails():
    def mutate(data):
        _row(data, "Payment", "0aQ0000000000H1AAA").update(NetApplied=300, Balance=200)
    report = _header(mutate=mutate)
    assert report["failed_checks"] == ["payment_balance"]


# ------------------------------------------------------------------ unapplied_rows

def test_dangling_unapplied_row_fails():
    def drop_applied(data):
        data["PaymentLineInvoiceLine"] = [
            r for r in data["PaymentLineInvoiceLine"] if r["Id"] != "1Al000000000002AAA"]
        # Keep balances consistent so only the pairing check can fail: with the
        # Applied row gone the net is -50, so mirror it in the rollups.
        _row(data, "InvoiceLine", "5TV000000000032AAA").update(
            NetPaymentsApplied=-50, Balance=200)
        _row(data, "Invoice", "3tt000000000003AAA").update(
            NetPaymentsApplied=-50, Balance=200)
        _row(data, "Payment", "0aQ000000000003AAA").update(NetApplied=-50, Balance=100)
    report = _line(mutate=drop_applied)
    assert report["failed_checks"] == ["unapplied_rows"]


def test_applied_row_marked_unapplied_without_its_pair_fails():
    def mutate(data):
        data["PaymentLineInvoiceLine"][0]["UnappliedStatus"] = "Yes"
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["unapplied_rows"]


def test_unapplied_pair_whose_applied_row_is_not_marked_fails():
    def mutate(data):
        _row(data, "PaymentLineInvoiceLine", "1Al000000000002AAA")["UnappliedStatus"] = "No"
    report = _line(mutate=mutate)
    assert report["failed_checks"] == ["unapplied_rows"]


# ------------------------------------------------------------------ inputs

def test_unknown_invoice_id_is_an_error():
    with pytest.raises(VerifyError, match="not found"):
        fetch_billing_records(RecordedClient(_load("line_level.json")),
                              ["3tt00000000000ZAAA"])


def test_malformed_id_is_rejected_before_any_query():
    client = RecordedClient({})
    with pytest.raises(VerifyError, match="not a Salesforce id"):
        fetch_billing_records(client, ["3tt' OR Id != '"])
    assert client.queries == []


def test_ids_from_manifest_reads_invoice_and_payment_keys(tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps({
        "run_id": "run", "kind": "sales_txn_quote", "invoice_id": "3tt000000000001AAA",
        "payment_ids": ["0aQ000000000001AAA"]}))
    assert ids_from_manifest(path) == (["3tt000000000001AAA"], ["0aQ000000000001AAA"])


# ------------------------------------------------------------------ CLI

@pytest.fixture
def recorded_org(monkeypatch):
    data = _load("line_level.json")
    client = RecordedClient(data)
    monkeypatch.setattr(cli.SfRestClient, "from_alias",
                        classmethod(lambda cls, *a, **k: client))
    return client


def _manifest(tmp_path, **ids) -> Path:
    path = tmp_path / "DEMO-1.json"
    path.write_text(json.dumps({"run_id": "DEMO-1", "kind": "sales_txn_quote", **ids}))
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
    path = _manifest(tmp_path, invoice_id="3tt000000000002AAA")
    monkeypatch.setattr(cli, "list_manifests", lambda: [path])
    rc = cli.main(["verify", "--org", "fake", "--latest", "--json"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["invoice_ids"] == ["3tt000000000002AAA"]


def test_cli_verify_manifest_without_ids_exits_one(recorded_org, tmp_path, capsys):
    path = _manifest(tmp_path)
    rc = cli.main(["verify", "--org", "fake", "--manifest", str(path)])
    assert rc == 1
    assert "names no invoice or payment id" in capsys.readouterr().err


def test_cli_verify_needs_some_ids(recorded_org, capsys):
    rc = cli.main(["verify", "--org", "fake"])
    assert rc == 1
    assert "verify needs" in capsys.readouterr().err

