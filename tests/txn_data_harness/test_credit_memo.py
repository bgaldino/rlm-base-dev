"""``cli credit-memo``, its lifecycle calls, and the verify credit memo and
negative-line checks (todo 520), offline.

Shapes follow the 2026-11-28 measurements on 264 (Line Level): generate and post
answer ``success`` with a ``requestIdentifier`` (post adds a tracker ``statusURL``),
the generated memo is found by its description in Draft, and the memo-level apply
answers ``applyCreditResults`` of ``{appliedToId, id, success}``.
"""

from __future__ import annotations

import pytest

from scripts.txn_data_harness import cli, lifecycle
from scripts.txn_data_harness import verify as verify_mod
from scripts.txn_data_harness.lifecycle import SettlementError

from .test_verify_billing import RecordedClient, _load, _row, _verify

ACCOUNT = "001ACCT000000001AA"
INVOICE = "3tt000000000001AAA"
PRODUCT = "01tPROD000000001AA"
MEMO = "50gMEMO000000001AA"
OK = {"errors": [], "requestIdentifier": "r-1", "success": True}
APPLIED = {"applyCreditResults": [{"appliedToId": "5TV000000000011GAA",
                                   "errors": None, "id": "4sGROW000000001AA",
                                   "success": True}]}


class FakeOrg:
    api_version = "68.0"

    def __init__(self, answers=None, posts=None):
        self.answers = answers or {}
        self.queries: list[str] = []
        self.posts: list[tuple[str, dict]] = []
        self.post_results = list(posts or [])

    def query(self, soql):
        self.queries.append(soql)
        for needle, rows in self.answers.items():
            if needle in soql:
                return rows() if callable(rows) else rows
        return []

    def post(self, path, body, *, retry=True):
        assert retry is False, "a credit memo call must never be resent by the transport"
        self.posts.append((path, body))
        result = self.post_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


# --------------------------------------------------------------------------- lifecycle

def test_generate_posts_one_draft_charge_line_with_tax_ignored():
    org = FakeOrg(posts=[OK])
    lifecycle.generate_credit_memo(org, ACCOUNT, PRODUCT, 25.0, "CM-1 standalone credit",
                                   "USD")
    path, body = org.posts[0]
    assert path == "/services/data/v68.0/commerce/invoicing/credit-memos/actions/generate"
    assert body == {"billingAccountId": ACCOUNT, "type": "Draft",
                    "description": "CM-1 standalone credit", "taxStrategy": "Ignore",
                    "charges": [{"chargeAmount": 25.0, "productId": PRODUCT}],
                    "currencyIsoCode": "USD"}


def test_generate_sends_no_currency_on_a_single_currency_org():
    org = FakeOrg(posts=[OK])
    lifecycle.generate_credit_memo(org, ACCOUNT, PRODUCT, 25.0, "CM-1", None)
    assert "currencyIsoCode" not in org.posts[0][1]


@pytest.mark.parametrize("result", [{"success": False, "errors": ["no"]}, None, []])
def test_generate_without_success_raises(result):
    with pytest.raises(SettlementError, match="generate answered"):
        lifecycle.generate_credit_memo(FakeOrg(posts=[result]), ACCOUNT, PRODUCT, 1.0, "t")


def test_find_tagged_credit_memo_reads_by_account_and_escaped_description():
    org = FakeOrg({"FROM CreditMemo": [{"Id": MEMO, "Status": "Draft"}]})
    assert lifecycle.find_tagged_credit_memo(org, ACCOUNT, "O'Hare credit")["Id"] == MEMO
    assert (f"WHERE BillingAccountId = '{ACCOUNT}' AND Description = 'O\\'Hare credit'"
            in org.queries[0])


def test_two_memos_under_one_description_raise():
    org = FakeOrg({"FROM CreditMemo": [{"Id": MEMO}, {"Id": "50gMEMO000000002AA"}]})
    with pytest.raises(SettlementError, match="2 credit memos carry"):
        lifecycle.find_tagged_credit_memo(org, ACCOUNT, "t")


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(lifecycle.time, "sleep", lambda s: None)


def test_wait_returns_the_memo_once_it_reaches_the_status(no_sleep):
    seen = iter([None, {"Id": MEMO, "Status": "Pending"}, {"Id": MEMO, "Status": "Posted"}])
    assert lifecycle.wait_credit_memo(None, lambda: next(seen), "Posted")["Id"] == MEMO


@pytest.mark.parametrize("status", ["Error", "Canceled", "Voided"])
def test_wait_fails_on_a_failed_memo(no_sleep, status):
    with pytest.raises(SettlementError, match=f"credit memo in {status}"):
        lifecycle.wait_credit_memo(None, lambda: {"Id": MEMO, "Status": status}, "Posted")


def test_wait_times_out_saying_what_it_saw(no_sleep, monkeypatch):
    clock = iter([0, 0, 500])
    monkeypatch.setattr(lifecycle.time, "monotonic", lambda: next(clock))
    with pytest.raises(SettlementError, match=r"not Posted within 180s \(it is Draft\)"):
        lifecycle.wait_credit_memo(None, lambda: {"Id": MEMO, "Status": "Draft"}, "Posted")


def test_post_sends_the_one_memo():
    org = FakeOrg(posts=[{**OK, "statusURL": "/services/data/v68.0/sobjects/X/1"}])
    lifecycle.post_credit_memo(org, MEMO)
    assert org.posts == [("/services/data/v68.0/commerce/invoicing/credit/collection/"
                          "actions/post", {"creditMemoIds": [MEMO]})]


def test_apply_sends_the_invoice_id_and_returns_the_results():
    org = FakeOrg(posts=[APPLIED])
    assert lifecycle.apply_credit_memo(org, MEMO, INVOICE, 25.0) == APPLIED["applyCreditResults"]
    assert org.posts == [(f"/services/data/v68.0/commerce/invoicing/credit-memos/{MEMO}/"
                          "actions/apply",
                          {"applications": [{"appliedToId": INVOICE, "amount": 25.0}]})]


@pytest.mark.parametrize("result", [
    {"applyCreditResults": [{"success": False, "errors": [{"message": "no"}]}]},
    {"applyCreditResults": []}, {}, None,
])
def test_apply_without_success_raises(result):
    with pytest.raises(SettlementError, match="apply answered"):
        lifecycle.apply_credit_memo(FakeOrg(posts=[result]), MEMO, INVOICE, 1.0)


# --------------------------------------------------------------------------- cli

class CliOrg:
    """The calls ``cli credit-memo`` makes, with what each returned."""

    def __init__(self, monkeypatch, *, invoice=None, product=PRODUCT, fail=None,
                 report=None):
        self.calls: list[tuple] = []
        self.invoice = {"Id": INVOICE, "Status": "Posted", "BillingAccountId": ACCOUNT,
                        "Balance": 100.0, "CurrencyIsoCode": "USD", **(invoice or {})}
        self.report = report or {"ok": True, "checked": 3, "skipped": 0, "level": "line",
                                 "level_source": "records", "failed_checks": [],
                                 "checks": []}
        self.fail = fail or {}
        statuses = iter(["Draft", "Posted"])

        def call(name, result=None):
            def fn(*args, **kwargs):
                self.calls.append((name,) + args[1:])
                if name in self.fail:
                    raise self.fail[name]
                return result(*args) if callable(result) else result
            return fn

        m = monkeypatch
        m.setattr(cli.SfRestClient, "from_alias", classmethod(lambda c, *a, **k: self))
        m.setattr(lifecycle, "fetch_invoice_header", call("header", lambda *a: self.invoice))
        m.setattr(lifecycle, "currency_decimal_places", lambda client, iso: 2)
        m.setattr(lifecycle, "first_invoice_product", call("product", product))
        m.setattr(lifecycle, "generate_credit_memo", call("generate"))
        m.setattr(lifecycle, "wait_credit_memo",
                  call("wait", lambda *a: {"Id": MEMO, "Status": next(statuses)}))
        m.setattr(lifecycle, "post_credit_memo", call("post"))
        m.setattr(lifecycle, "apply_credit_memo",
                  call("apply", APPLIED["applyCreditResults"]))
        m.setattr(cli.billing_verify, "fetch_records", call("fetch", {}))
        m.setattr(cli.billing_verify, "run_checks", lambda records: self.report)
        m.setattr(cli.billing_verify, "render_text", lambda report: "RESULT: stub")

    def names(self):
        return [c[0] for c in self.calls]


def _run(*extra):
    return cli.main(["credit-memo", "--org", "fake", "--invoice", INVOICE, *extra])


def test_generates_posts_applies_and_verifies_the_memo(monkeypatch, capsys):
    org = CliOrg(monkeypatch)
    assert _run("--amount", "25") == 0
    out = capsys.readouterr().out
    assert org.names() == ["header", "product", "generate", "wait", "post", "wait", "apply",
                           "fetch"]
    generate = next(c for c in org.calls if c[0] == "generate")
    assert generate[1:3] == (ACCOUNT, PRODUCT) and generate[3] == 25.0
    assert generate[4].endswith(" standalone credit") and generate[5] == "USD"
    assert [c[1] for c in org.calls if c[0] == "wait"][0] is not None
    assert next(c for c in org.calls if c[0] == "apply")[1:] == (MEMO, INVOICE, 25.0)
    assert next(c for c in org.calls if c[0] == "fetch")[1:] == ([INVOICE], None, [MEMO])
    assert f"POSTED: credit memo {MEMO}" in out
    assert out.strip().endswith(f"CREDIT-MEMO: pass (credit memo {MEMO} applied to "
                                f"invoice {INVOICE})")


def test_a_given_product_is_used_without_reading_the_invoice_lines(monkeypatch):
    org = CliOrg(monkeypatch)
    assert _run("--amount", "25", "--product", "01tOTHER00000001AA") == 0
    assert "product" not in org.names()
    assert next(c for c in org.calls if c[0] == "generate")[2] == "01tOTHER00000001AA"


def test_the_amount_is_rounded_to_the_currency(monkeypatch):
    org = CliOrg(monkeypatch)
    assert _run("--amount", "25.004") == 0
    assert next(c for c in org.calls if c[0] == "generate")[3] == 25.0


@pytest.mark.parametrize("invoice, amount, product, text", [
    ({"Status": "Draft"}, "25", PRODUCT, "is Draft, not Posted"),
    ({}, "100.01", PRODUCT, "at most the invoice balance 100.0"),
    ({}, "0.001", PRODUCT, "must be above 0"),
    ({}, "25", None, "no Charge line with a product"),
])
def test_refuses_before_any_write(monkeypatch, capsys, invoice, amount, product, text):
    org = CliOrg(monkeypatch, invoice=invoice, product=product)
    assert _run("--amount", amount) == 2
    assert "generate" not in org.names()
    assert text in capsys.readouterr().err


@pytest.mark.parametrize("amount", ["0", "-5", "nan", "inf", "ten"])
def test_an_amount_that_is_not_above_zero_is_a_usage_error(amount, capsys):
    with pytest.raises(SystemExit) as exc:
        _run("--amount", amount)
    assert exc.value.code == 2
    assert "not an amount above 0" in capsys.readouterr().err


def test_a_malformed_invoice_id_is_refused(capsys):
    assert cli.main(["credit-memo", "--org", "fake", "--invoice", "nope'",
                     "--amount", "1"]) == 2
    assert "ERROR: credit-memo:" in capsys.readouterr().err


def test_a_failed_generate_wrote_nothing_so_is_an_error(monkeypatch, capsys):
    org = CliOrg(monkeypatch, fail={"generate": SettlementError("credit-memo", "refused")})
    assert _run("--amount", "25") == 2
    assert org.names()[-1] == "generate"
    err = capsys.readouterr().err
    assert "refused" in err and f"look on account {ACCOUNT} for a credit memo described 'CM-" in err


@pytest.mark.parametrize("step", ["post", "apply"])
def test_a_failed_step_after_the_generate_names_the_memo(monkeypatch, capsys, step):
    org = CliOrg(monkeypatch, fail={step: SettlementError("credit-memo", "said no")})
    assert _run("--amount", "25") == 1
    out = capsys.readouterr().out
    assert "fetch" not in org.names()
    assert f"credit memo {MEMO} stays on the account with its balance" in out
    assert out.strip().endswith(f"CREDIT-MEMO: fail (invoice {INVOICE})")


def test_a_memo_that_never_appears_is_named_by_its_description(monkeypatch, capsys):
    CliOrg(monkeypatch, fail={"wait": SettlementError("credit-memo", "did not appear")})
    assert _run("--amount", "25") == 1
    out = capsys.readouterr().out
    assert "the memo described 'CM-" in out and "did not appear" in out


@pytest.mark.parametrize("report, reason", [
    ({"ok": False, "checked": 3}, "a check failed"),
    ({"ok": True, "checked": 0}, "no balance was checked"),
])
def test_a_failed_or_empty_verify_fails(monkeypatch, capsys, report, reason):
    CliOrg(monkeypatch, report={"skipped": 0, "level": "line", "level_source": "records",
                                "failed_checks": [], "checks": [], **report})
    assert _run("--amount", "25") == 1
    assert capsys.readouterr().out.strip().endswith(f"{INVOICE}: {reason})")


def test_a_verify_that_cannot_report_is_an_error(monkeypatch, capsys):
    CliOrg(monkeypatch, fail={"fetch": verify_mod.VerifyError("unreadable")})
    assert _run("--amount", "25") == 2
    assert f"credit memo {MEMO} was applied" in capsys.readouterr().err


# --------------------------------------------------------------------------- verify

def _memo_results(report):
    return {r["subject"]: r for r in report["checks"] if r["check"] == "credit_memo_balance"}


def test_every_memo_balance_is_checked_against_its_rows():
    report = _verify(_load("line_level.json"), ["3tt000000000003AAA"])
    results = _memo_results(report)
    assert {r["status"] for r in results.values()} == {"pass"}
    assert results["50g000000000011AAA"]["detail"] == "Status Posted; 0 = 40 - 40"


@pytest.mark.parametrize("change, text", [
    ({"Balance": 5}, "Balance 5 != TotalAmountWithTax 40 - NetCreditsApplied 40 = 0"),
    ({"NetCreditsApplied": 30, "Balance": 10}, "NetCreditsApplied 30 != application rows 40"),
    ({"Balance": None}, "Balance null"),
])
def test_a_memo_balance_that_does_not_add_up_fails(change, text):
    data = _load("line_level.json")
    _row(data, "CreditMemo", "50g000000000011AAA").update(change)
    report = _verify(data, ["3tt000000000003AAA"])
    assert report["failed_checks"] == ["credit_memo_balance"]
    assert text in _memo_results(report)["50g000000000011AAA"]["detail"]


def test_a_memo_row_on_an_invoice_outside_the_set_counts_for_the_memo():
    # The memo is read with all its rows, so NetCreditsApplied covers rows elsewhere.
    data = _load("line_level.json")
    data["CreditMemoLineInvoiceLine"].append({
        "Id": "4sG000000000077EAA", "InvoiceLineId": "5TV0000000000X1GAA",
        "CreditMemoLineId": "9yx000000000001AAA", "Amount": 10, "Type": "Applied",
        "UnappliedStatus": "No", "RelatedCrMemoLineInvcLineId": None})
    _row(data, "CreditMemo", "50g000000000011AAA").update(TotalAmountWithTax=50,
                                                         NetCreditsApplied=50)
    report = _verify(data, ["3tt000000000003AAA"])
    assert report["ok"] is True, report["failed_checks"]
    assert _memo_results(report)["50g000000000011AAA"]["detail"] == "Status Posted; 0 = 50 - 50"


def _memo_only(status, rows=False, **fields):
    """A memo passed by id alone (verify --credit-memo-ids), as generated in Draft."""
    memo = verify_mod._id18("50g000000000077")
    data = {"CreditMemo": [{"Id": memo, "Status": status, "TotalAmountWithTax": 30,
                            "NetCreditsApplied": 0, "Balance": 30, "NetRefundsApplied": 0,
                            **fields}],
            "CreditMemoLine": [{"Id": "9yxLINE000000001AA", "CreditMemoId": memo}],
            "CreditMemoLineInvoiceLine": [], "CreditMemoInvApplication": []}
    if rows:
        data["CreditMemoLineInvoiceLine"].append({
            "Id": "4sGROW000000001AA", "InvoiceLineId": "5TVLINE000000001AA",
            "CreditMemoLineId": "9yxLINE000000001AA", "Amount": 0, "Type": "Applied",
            "UnappliedStatus": "No", "RelatedCrMemoLineInvcLineId": None})
    client = RecordedClient(data)
    report = verify_mod.run_checks(verify_mod.fetch_records(client, [], [], [memo]))
    return _memo_results(report)[memo]


@pytest.mark.parametrize("status", ["Draft", "Posted"])
def test_a_memo_with_no_applications_is_checked_by_id(status):
    result = _memo_only(status)
    assert result["status"] == "pass" and result["detail"] == f"Status {status}; 30 = 30 - 0"


@pytest.mark.parametrize("status, rows, fields, text", [
    ("Draft", True, {}, "Status Draft with 1 application row(s)"),
    ("Pending", False, {}, "Status Pending with 0"),
    ("Voided", False, {}, "Status Voided"),
    ("Posted", False, {"NetRefundsApplied": 5}, "NetRefundsApplied 5"),
])
def test_an_unmeasured_memo_is_skipped(status, rows, fields, text):
    result = _memo_only(status, rows, **fields)
    assert result["status"] == "skip" and text in result["detail"]


def test_a_memo_with_header_rows_is_skipped():
    report = _verify(_load("header_level.json"), ["3tt0000000000H1AAI"])
    result = _memo_results(report)["50g000000000001AAA"]
    assert result["status"] == "skip" and "1 header-level application row(s)" in result["detail"]


def test_cli_verify_takes_credit_memo_ids_alone(monkeypatch, capsys):
    data = _load("line_level.json")
    client = RecordedClient(data)
    monkeypatch.setattr(cli.SfRestClient, "from_alias",
                        classmethod(lambda cls, *a, **k: client))
    assert cli.main(["verify", "--org", "fake", "--credit-memo-ids",
                     "50g000000000011AAA"]) == 0
    out = capsys.readouterr().out
    assert "PASS credit_memo_balance  50g000000000011AAA" in out


def _convert(data, *, converted=50, charge=50, total_converted=50, line_balance=0,
             invoice_balance=None):
    """INV2 as measured after posting with a -50 line: the line converted whole, a
    50 conversion memo applied to the positive line, the invoice balance unchanged."""
    inv = _row(data, "Invoice", "3tt000000000002AAA")
    data["InvoiceLine"].append({
        "Id": "5TV000000000029GAA", "InvoiceId": "3tt000000000002AAA", "Type": "Charge",
        "LineAmount": -50, "NetCreditsApplied": 0, "NetPaymentsApplied": 0,
        "Balance": line_balance, "ConvertedNegAmount": converted,
        "ChargeConvertedNegAmount": charge, "AdjustmentAmount": None})
    positive = _row(data, "InvoiceLine", "5TV000000000021GAA")
    positive.update(NetCreditsApplied=50, Balance=positive["LineAmount"] - 50)
    inv.update(TotalAmountWithTax=inv["TotalAmountWithTax"] - 50, NetCreditsApplied=50,
               TotalConvertedNegAmount=total_converted, SettlementLevel="InvoiceLine",
               Balance=(inv["TotalAmountWithTax"] - 50 if invoice_balance is None
                        else invoice_balance))
    data["CreditMemo"].append({"Id": "50g000000000050AAA", "Status": "Posted",
                               "TotalAmountWithTax": 50, "NetCreditsApplied": 50,
                               "Balance": 0, "NetRefundsApplied": 0})
    data["CreditMemoLine"].append({"Id": "9yx000000000050AAA",
                                   "CreditMemoId": "50g000000000050AAA"})
    data["CreditMemoLineInvoiceLine"].append({
        "Id": "4sG000000000050EAA", "InvoiceLineId": "5TV000000000021GAA",
        "CreditMemoLineId": "9yx000000000050AAA", "Amount": 50, "Type": "Applied",
        "UnappliedStatus": "No", "RelatedCrMemoLineInvcLineId": None})
    return _verify(data, ["3tt000000000002AAA"])


def _inv2(report):
    return {(r["check"], r["subject"]): r for r in report["checks"]
            if r["subject"].startswith("3tt000000000002AAA")}


def test_a_converted_negative_line_is_checked_with_the_converted_amount():
    report = _convert(_load("line_level.json"))
    assert report["ok"] is True and report["skipped"] == 0, report["failed_checks"]
    results = _inv2(report)
    assert results[("invoice_balance", "3tt000000000002AAA")]["detail"] == (
        "445 = 445 - 50 - 0 + 50")
    assert results[("invoice_line_balance", "3tt000000000002AAA/5TV000000000029GAA")][
        "detail"] == "0 = -50 - 0 - 0 + 50"


def test_a_converted_invoice_balance_without_the_converted_amount_fails():
    report = _convert(_load("line_level.json"), invoice_balance=395)
    assert report["failed_checks"] == ["invoice_balance"]
    assert "+ TotalConvertedNegAmount 50" in _inv2(report)[
        ("invoice_balance", "3tt000000000002AAA")]["detail"]


@pytest.mark.parametrize("kwargs, text", [
    ({"converted": 20, "charge": 20, "total_converted": 20, "line_balance": -30},
     "only a negative line converted whole"),
    ({"charge": 45}, "only a negative line converted whole with no tax part"),
    ({"total_converted": 60}, "is not the lines' ConvertedNegAmount total 50"),
])
def test_a_conversion_other_than_the_measured_shape_is_skipped(kwargs, text):
    report = _convert(_load("line_level.json"), **kwargs)
    assert report["ok"] is True, report["failed_checks"]
    result = _inv2(report)[("invoice_balance", "3tt000000000002AAA")]
    assert result["status"] == "skip" and text in result["detail"]
