"""`cli apply-rules` and the rule-based application calls (todo 498), offline.

The response shape is the one measured live on 264 (Line Level, 2026-11-26):
``{"appliedRules": [...], "isSuccess": true, "rulesApplicationSummary": {...}}``
with no ``errors`` key on success; the rows it writes are ordinary Applied rows.
"""

from __future__ import annotations

import pytest

from scripts.txn_data_harness import cli, lifecycle
from scripts.txn_data_harness.auth import SfApiError

ACCOUNT = "001ACCT000000001AA"
PAYMENT, MEMO = "0aQPAY0000000001AA", "50gMEMO000000001AA"
INVOICE_A, INVOICE_B = "3ttINV0000000001AA", "3ttINV0000000002AA"
OK = {"appliedRules": ["Match Balance", "Prioritize Oldest Invoices"], "isSuccess": True,
      "rulesApplicationSummary": {"areAllInvoicesConsidered": True,
                                  "fetchedCreditMemosCount": 1, "fetchedPaymentsCount": 1,
                                  "totalCreditMemoApplications": 1,
                                  "totalPaymentApplications": 1}}


# --------------------------------------------------------------------------- lifecycle

_DEFAULT = object()


class QueryOrg:
    api_version = "68.0"

    def __init__(self, answers=None, post_result=_DEFAULT):
        self.answers = answers or {}
        self.queries: list[str] = []
        self.posts: list[tuple[str, dict]] = []
        self.post_result = OK if post_result is _DEFAULT else post_result

    def query(self, soql: str) -> list[dict]:
        self.queries.append(soql)
        for needle, rows in self.answers.items():
            if needle in soql:
                return rows
        return []

    def post(self, path: str, body: dict, *, retry: bool = True):
        assert retry is False, "the rules application must never be resent by the transport"
        self.posts.append((path, body))
        return self.post_result


def test_resolve_account_id_by_id_and_by_escaped_name():
    org = QueryOrg({"FROM Account": [{"Id": ACCOUNT}]})
    assert lifecycle.resolve_account_id(org, ACCOUNT) == ACCOUNT
    assert org.queries[-1] == f"SELECT Id FROM Account WHERE Id = '{ACCOUNT}'"
    assert lifecycle.resolve_account_id(org, "O'Hare \\ Co") == ACCOUNT
    assert org.queries[-1] == "SELECT Id FROM Account WHERE Name = 'O\\'Hare \\\\ Co'"


def test_resolve_account_id_takes_a_15_character_id_and_returns_the_org_id():
    org = QueryOrg({"FROM Account": [{"Id": ACCOUNT}]})
    assert lifecycle.resolve_account_id(org, ACCOUNT[:15]) == ACCOUNT
    assert org.queries[-1] == f"SELECT Id FROM Account WHERE Id = '{ACCOUNT[:15]}'"


def test_resolve_account_id_reads_a_16_character_name_as_a_name():
    org = QueryOrg({"FROM Account": [{"Id": ACCOUNT}]})
    lifecycle.resolve_account_id(org, "001AAAAAAAAAAAAB")
    assert org.queries[-1] == "SELECT Id FROM Account WHERE Name = '001AAAAAAAAAAAAB'"


def test_resolve_account_id_reads_an_id_with_a_trailing_newline_as_a_name():
    org = QueryOrg({"FROM Account": [{"Id": ACCOUNT}]})
    lifecycle.resolve_account_id(org, "001AAAAAAAAAAAA\n")
    assert org.queries[-1] == "SELECT Id FROM Account WHERE Name = '001AAAAAAAAAAAA\n'"


@pytest.mark.parametrize("rows, found", [([], "no account"),
                                         ([{"Id": "a"}, {"Id": "b"}], "2 accounts")])
def test_resolve_account_id_refuses_none_or_several(rows, found):
    with pytest.raises(lifecycle.SettlementError, match=f"{found} found for 'Acme'"):
        lifecycle.resolve_account_id(QueryOrg({"FROM Account": rows}), "Acme")


def test_open_sources_reads_payments_and_memos_with_a_balance():
    org = QueryOrg({"FROM Payment": [{"Id": PAYMENT}], "FROM CreditMemo": [{"Id": MEMO}]})
    assert lifecycle.open_sources(org, ACCOUNT) == ([PAYMENT], [MEMO])
    assert org.queries == [
        f"SELECT Id FROM Payment WHERE AccountId = '{ACCOUNT}' AND Balance != 0",
        f"SELECT Id FROM CreditMemo WHERE BillingAccountId = '{ACCOUNT}' AND Balance != 0",
    ]


def test_read_source_applications_reads_all_four_objects_and_flattens_relationships():
    org = QueryOrg({
        "FROM PaymentLineInvoiceLine": [{"Id": "1Al1", "Amount": 445.5, "Type": "Applied",
                                         "PaymentId": PAYMENT,
                                         "InvoiceLine": {"InvoiceId": INVOICE_A}}],
        "FROM CreditMemoLineInvoiceLine": [{"Id": "4sG1", "Amount": 49.5, "Type": "Applied",
                                            "CreditMemoLine": {"CreditMemoId": MEMO},
                                            "InvoiceLine": {"InvoiceId": INVOICE_A}}],
        "FROM PaymentLineInvoice": [{"Id": "hdr1", "Amount": 1, "Type": "Applied",
                                     "PaymentId": PAYMENT, "InvoiceId": INVOICE_B}],
    })
    rows = lifecycle.read_source_applications(org, [PAYMENT], [MEMO])
    assert rows == [
        {"id": "1Al1", "object": "PaymentLineInvoiceLine", "kind": "payment",
         "source_id": PAYMENT, "invoice_id": INVOICE_A, "amount": 445.5, "type": "Applied"},
        {"id": "4sG1", "object": "CreditMemoLineInvoiceLine", "kind": "credit",
         "source_id": MEMO, "invoice_id": INVOICE_A, "amount": 49.5, "type": "Applied"},
        {"id": "hdr1", "object": "PaymentLineInvoice", "kind": "payment",
         "source_id": PAYMENT, "invoice_id": INVOICE_B, "amount": 1, "type": "Applied"},
    ]
    assert len(org.queries) == 4
    assert ("FROM CreditMemoLineInvoiceLine WHERE CreditMemoLine.CreditMemoId IN "
            f"('{MEMO}')") in org.queries[1]


def test_read_source_applications_skips_a_kind_with_no_sources_and_chunks():
    org = QueryOrg()
    payments = [f"0aQ{i:015d}" for i in range(201)]
    lifecycle.read_source_applications(org, payments, [])
    assert [q.split(" FROM ")[1].split(" WHERE ")[0] for q in org.queries] == [
        "PaymentLineInvoiceLine", "PaymentLineInvoiceLine",
        "PaymentLineInvoice", "PaymentLineInvoice"]


def test_apply_rules_posts_once_with_the_optional_target_date():
    org = QueryOrg()
    assert lifecycle.apply_rules(org, ACCOUNT) == OK
    lifecycle.apply_rules(org, ACCOUNT, "2026-11-25")
    path = "/services/data/v68.0/revenue/billing/transactions/actions/apply"
    assert org.posts == [(path, {"accountId": ACCOUNT}),
                         (path, {"accountId": ACCOUNT, "targetDate": "2026-11-25"})]


@pytest.mark.parametrize("result", [
    None, [], {"_raw": "<html>"},
    dict(OK, appliedRules=[{"name": "Match Balance"}]),
    dict(OK, appliedRules="Match Balance"),
    dict(OK, rulesApplicationSummary=[1]),
    dict(OK, rulesApplicationSummary={"totalPaymentApplications": "1"}),
    dict(OK, rulesApplicationSummary={"totalCreditMemoApplications": True}),
    {}, {k: v for k, v in OK.items() if k != "isSuccess"}, dict(OK, isSuccess="true"),
    {"isSuccess": True},
    {k: v for k, v in OK.items() if k != "rulesApplicationSummary"},
    dict(OK, rulesApplicationSummary={"totalPaymentApplications": 1}),
    dict(OK, rulesApplicationSummary={"totalPaymentApplications": 1,
                                      "totalCreditMemoApplications": None}),
    dict(OK, rulesApplicationSummary=dict(OK["rulesApplicationSummary"],
                                          totalPaymentApplications="1")),
    dict(OK, rulesApplicationSummary=dict(OK["rulesApplicationSummary"],
                                          totalCreditMemoApplications=True)),
    dict(OK, rulesApplicationSummary=dict(OK["rulesApplicationSummary"],
                                          fetchedPaymentsCount=True)),
    {"isSuccess": False, "rulesApplicationSummary": [1]},
    {"isSuccess": False, "rulesApplicationSummary": {"totalPaymentApplications": "1"}},
])
def test_apply_rules_refuses_a_response_it_cannot_read(result):
    with pytest.raises(lifecycle.SettlementError, match="rules application answered"):
        lifecycle.apply_rules(QueryOrg(post_result=result), ACCOUNT)


def test_apply_rules_names_the_platform_errors_in_an_unexpected_shape():
    result = {"errors": [{"errorCode": "INVALID_ACCOUNT", "message": "m"}]}
    with pytest.raises(lifecycle.SettlementError, match="INVALID_ACCOUNT"):
        lifecycle.apply_rules(QueryOrg(post_result=result), ACCOUNT)


@pytest.mark.parametrize("result", [
    {"isSuccess": False, "errors": [{"errorCode": "X", "message": "m"}]},
    {"errors": [{"message": "We couldn&#39;t find eligible invoices to apply rules-based "
                            "credits and payments. "}], "isSuccess": False},
    dict(OK, isSuccess=False),
    dict(OK, appliedRules=[], rulesApplicationSummary={"totalPaymentApplications": 0,
                                                       "totalCreditMemoApplications": 0}),
])
def test_apply_rules_returns_a_failure_or_a_success_with_both_counts(result):
    assert lifecycle.apply_rules(QueryOrg(post_result=result), ACCOUNT) == result


# --------------------------------------------------------------------------- command

def _row(row_id, kind, source, invoice, amount):
    obj = "PaymentLineInvoiceLine" if kind == "payment" else "CreditMemoLineInvoiceLine"
    return {"id": row_id, "object": obj, "kind": kind, "source_id": source,
            "invoice_id": invoice, "amount": amount, "type": "Applied"}


OLD = _row("1AlOLD", "payment", PAYMENT, INVOICE_B, 10)
NEW_PAY = _row("1AlNEW", "payment", PAYMENT, INVOICE_A, 445.5)
NEW_CREDIT = _row("4sGNEW", "credit", MEMO, INVOICE_A, 49.5)


class Org:
    """The lifecycle calls `cli apply-rules` makes, patched in."""

    def __init__(self, monkeypatch, *, after=(OLD, NEW_PAY, NEW_CREDIT), result=OK,
                 report=None):
        self.reads = [[OLD], list(after)]
        self.result = result
        self.calls: list[tuple] = []
        self.fail: dict[str, Exception] = {}
        self.report = report or {"ok": True, "checked": 2, "skipped": 1, "level": "line",
                                 "level_source": "records", "failed_checks": [],
                                 "checks": []}
        m = monkeypatch
        m.setattr(cli.SfRestClient, "from_alias", classmethod(lambda c, *a, **k: self))
        m.setattr(cli.lifecycle, "resolve_account_id", self._step("resolve", ACCOUNT))
        m.setattr(cli.lifecycle, "open_sources", self._step("sources", ([PAYMENT], [MEMO])))
        m.setattr(cli.lifecycle, "read_source_applications", self._read)
        m.setattr(cli.lifecycle, "apply_rules", self._step("apply", None))
        m.setattr(cli.billing_verify, "fetch_records", self._step("fetch", {}))
        m.setattr(cli.billing_verify, "run_checks", lambda records: self.report)

    def _step(self, name, value):
        def call(*args):
            self.calls.append((name,) + args[1:])
            if name in self.fail:
                raise self.fail[name]
            return self.result if name == "apply" else value
        return call

    def _read(self, client, payments, memos):
        self.calls.append(("read", payments, memos))
        first = len([c for c in self.calls if c[0] == "read"]) == 1
        failing = self.fail.get("first read" if first else "read")
        if failing:
            raise failing
        return self.reads.pop(0)

    def names(self) -> list[str]:
        return [c[0] for c in self.calls]


def _apply_rules(*extra: str) -> int:
    return cli.main(["apply-rules", "--org", "x", "--account", "Infinitech", *extra])


def test_lists_new_rows_and_verifies_only_what_they_touch(monkeypatch, capsys):
    org = Org(monkeypatch)
    assert _apply_rules() == 0
    assert org.names() == ["resolve", "sources", "read", "apply", "read", "fetch"]
    assert ("apply", ACCOUNT, None) in org.calls
    assert ("fetch", [INVOICE_A], [PAYMENT]) in org.calls
    out = capsys.readouterr().out
    assert f"APPLIED: payment {PAYMENT} 445.5 -> invoice {INVOICE_A}" in out
    assert f"APPLIED: credit {MEMO} 49.5 -> invoice {INVOICE_A}" in out
    assert "1AlOLD" not in out
    assert "RULES: Match Balance, Prioritize Oldest Invoices;" in out
    assert (f"APPLY-RULES: pass (account {ACCOUNT}: 2 application(s) made; "
            "2 balance(s) checked, 1 skipped)") in out


def test_verifies_the_invoices_of_credit_rows_too(monkeypatch):
    credit_b = _row("4sGNEW", "credit", MEMO, INVOICE_B, 49.5)
    org = Org(monkeypatch, after=[OLD, NEW_PAY, credit_b])
    assert _apply_rules() == 0
    assert ("fetch", [INVOICE_A, INVOICE_B], [PAYMENT]) in org.calls


def test_passes_the_target_date(monkeypatch):
    org = Org(monkeypatch)
    assert _apply_rules("--target-date", "2026-11-25") == 0
    assert ("apply", ACCOUNT, "2026-11-25") in org.calls


def test_refuses_a_target_date_that_is_not_a_date(monkeypatch, capsys):
    org = Org(monkeypatch)
    with pytest.raises(SystemExit) as exc:
        _apply_rules("--target-date", "11/25/2026")
    assert exc.value.code == 2
    assert "not a date (YYYY-MM-DD)" in capsys.readouterr().err
    assert org.calls == []


def test_nothing_applied_passes_without_verify(monkeypatch, capsys):
    result = dict(OK, rulesApplicationSummary=dict(
        OK["rulesApplicationSummary"], totalPaymentApplications=0,
        totalCreditMemoApplications=0))
    org = Org(monkeypatch, after=[OLD], result=result)
    assert _apply_rules() == 0
    assert "fetch" not in org.names()
    assert "APPLY-RULES: pass (account 001ACCT000000001AA: nothing applied)" in \
        capsys.readouterr().out


def test_counted_applications_with_no_new_row_fail(monkeypatch, capsys):
    org = Org(monkeypatch, after=[OLD])
    assert _apply_rules() == 1
    assert "fetch" not in org.names()
    out = capsys.readouterr().out
    assert ("the response counts 1 payment application(s) but 0 new payment row(s) and "
            "1 credit application(s) but 0 new credit row(s)") in out
    assert "APPLY-RULES: fail" in out


def test_a_counted_kind_with_no_new_row_fails_even_when_another_kind_has_one(
        monkeypatch, capsys):
    org = Org(monkeypatch, after=[OLD, NEW_CREDIT])
    assert _apply_rules() == 1
    assert "fetch" not in org.names()
    out = capsys.readouterr().out
    assert f"APPLIED: credit {MEMO} 49.5" in out
    assert "the response counts 1 payment application(s) but 0 new payment row(s) on" in out


def test_fewer_new_rows_than_the_count_of_their_kind_fail(monkeypatch, capsys):
    result = dict(OK, rulesApplicationSummary=dict(OK["rulesApplicationSummary"],
                                                   totalPaymentApplications=2))
    org = Org(monkeypatch, result=result)
    assert _apply_rules() == 1
    assert "fetch" not in org.names()
    assert "2 payment application(s) but 1 new payment row(s)" in capsys.readouterr().out


def test_more_new_rows_than_the_count_pass(monkeypatch):
    extra = _row("1AlNEW2", "payment", PAYMENT, INVOICE_B, 5)
    Org(monkeypatch, after=[OLD, NEW_PAY, extra, NEW_CREDIT])
    assert _apply_rules() == 0


@pytest.mark.parametrize("result", [
    dict(OK, isSuccess=False),
    dict(OK, errors=[{"errorCode": "X", "message": "m"}]),
    {"errors": [{"message": "We couldn&#39;t find eligible invoices"}], "isSuccess": False},
])
def test_a_reported_failure_fails_before_verify(monkeypatch, capsys, result):
    org = Org(monkeypatch, result=result)
    assert _apply_rules() == 1
    assert "fetch" not in org.names()
    out = capsys.readouterr().out
    assert "FAIL: the platform reported isSuccess" in out
    assert "APPLY-RULES: fail" in out


@pytest.mark.parametrize("report, reason", [
    ({"ok": False, "checked": 2, "failed_checks": ["invoice_balance"]}, "a check failed"),
    ({"ok": True, "checked": 0, "failed_checks": []}, "no balance was checked"),
])
def test_a_failed_or_empty_verify_fails(monkeypatch, capsys, report, reason):
    full = {"skipped": 0, "level": "line", "level_source": "records", "checks": [], **report}
    Org(monkeypatch, report=full)
    assert _apply_rules() == 1
    assert f"APPLY-RULES: fail (account {ACCOUNT}: {reason})" in capsys.readouterr().out


def test_warns_when_not_every_invoice_was_considered(monkeypatch, capsys):
    result = dict(OK, rulesApplicationSummary=dict(OK["rulesApplicationSummary"],
                                                   areAllInvoicesConsidered=False))
    Org(monkeypatch, result=result)
    assert _apply_rules() == 0
    assert "WARNING: the platform did not consider every invoice" in capsys.readouterr().out


@pytest.mark.parametrize("step", ["resolve", "sources", "first read"])
@pytest.mark.parametrize("exc, text", [
    (lifecycle.SettlementError("apply-rules", "no account found for 'X'"),
     "ERROR: apply-rules: [apply-rules] no account found"),
    (SfApiError(401, "[]", "GET", "/query"), "ERROR: apply-rules: Salesforce request failed"),
])
def test_a_read_before_the_call_errors_without_calling(monkeypatch, capsys, step, exc, text):
    org = Org(monkeypatch)
    org.fail[step] = exc
    assert _apply_rules() == 2
    assert "apply" not in org.names()
    assert text in capsys.readouterr().err


def test_a_failed_call_is_an_error(monkeypatch, capsys):
    org = Org(monkeypatch)
    org.fail["apply"] = SfApiError(400, '[{"errorCode": "X"}]', "POST", "/apply")
    assert _apply_rules() == 2
    err = capsys.readouterr().err
    assert "ERROR: apply-rules: Salesforce request failed" in err
    assert "read the account's payments and credit memos before calling again" in err


def test_a_response_it_cannot_read_is_an_error(monkeypatch, capsys):
    org = Org(monkeypatch)
    org.fail["apply"] = lifecycle.SettlementError(
        "apply-rules", "rules application answered an unexpected shape")
    assert _apply_rules() == 2
    assert "read" == org.names()[-2] and org.names()[-1] == "apply"
    err = capsys.readouterr().err
    assert "unexpected shape; read the account's payments and credit memos" in err


def test_a_failed_read_after_the_call_is_an_error(monkeypatch, capsys):
    org = Org(monkeypatch)
    org.fail["read"] = SfApiError(401, "[]", "GET", "/query")
    assert _apply_rules() == 2
    assert "the call returned, but its applications could not be read" in \
        capsys.readouterr().err


def test_a_verify_that_cannot_report_is_an_error(monkeypatch, capsys):
    org = Org(monkeypatch)
    org.fail["fetch"] = SfApiError(500, "[]", "GET", "/query")
    assert _apply_rules() == 2
    assert "(the call applied 2 row(s), listed above)" in capsys.readouterr().err
