"""Settlement stages (credit_applied / payment_applied): graph, config,
payload builders, application-level handling, step behavior and manifest
round-trip. Offline only -- the live contract is in
``scripts/txn_data_harness/docs/contracts-billing-settlement.md``.
"""

from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pytest

from scripts.txn_data_harness import lifecycle, steps
from scripts.txn_data_harness.config import (
    ConfigError,
    CreditSpec,
    PaymentSpec,
    SettlementSpec,
    _coerce_spec,
    settlement_from_dict,
)
from scripts.txn_data_harness.handlers import SCENARIO_HANDLERS
from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import (
    IMPLEMENTED_MAX_STAGE,
    POSTED_STAGES,
    STAGES_INGESTION,
    STAGES_ORDER,
    STAGES_QUOTE,
    Manifest,
)
from scripts.txn_data_harness.report import build_batch_report
from scripts.txn_data_harness.steps import STEP_REGISTRY, StepContext


@pytest.fixture(autouse=True)
def _reset_level_cache():
    lifecycle._level_cache.clear()
    yield
    lifecycle._level_cache.clear()


# -- stage graph --------------------------------------------------------------


def test_settlement_stages_follow_invoice_posted_on_every_kind() -> None:
    for stages in (STAGES_QUOTE, STAGES_ORDER, STAGES_INGESTION):
        assert stages[-3:] == ["invoice_posted", "credit_applied", "payment_applied"]
    assert IMPLEMENTED_MAX_STAGE == "payment_applied"
    assert POSTED_STAGES == {"invoice_posted", "credit_applied", "payment_applied"}


def test_settlement_steps_are_registered() -> None:
    assert STEP_REGISTRY["credit_applied"].handler is steps.run_credit
    assert STEP_REGISTRY["payment_applied"].handler is steps.run_payment


@pytest.mark.parametrize("kind", ["sales_txn_quote", "sales_txn_order"])
def test_pst_handlers_walk_settlement_after_post(kind, billable_account) -> None:
    handler = SCENARIO_HANDLERS[kind]
    seq = handler.stage_sequence("payment_applied", False)
    assert seq[-3:] == ["invoice_posted", "credit_applied", "payment_applied"]
    assert handler.effective_stage("payment_applied", billable_account) == "payment_applied"
    # Resume from a Posted checkpoint runs only the settlement stages.
    assert handler.remaining_steps("invoice_posted", "payment_applied", False) == [
        "credit_applied", "payment_applied",
    ]
    assert handler.remaining_steps("credit_applied", "payment_applied", False) == [
        "payment_applied",
    ]


def test_pst_non_billing_account_still_caps_at_order_draft(pipeline_account) -> None:
    handler = SCENARIO_HANDLERS["sales_txn_quote"]
    assert handler.effective_stage("payment_applied", pipeline_account) == "order_draft"


@pytest.mark.parametrize(
    "reached, target, expected",
    [
        (None, "credit_applied", ["ingest_invoice", "promote_to_posted", "credit_applied"]),
        (None, "payment_applied",
         ["ingest_invoice", "promote_to_posted", "credit_applied", "payment_applied"]),
        ("invoice_draft", "payment_applied",
         ["promote_to_posted", "credit_applied", "payment_applied"]),
        ("invoice_posted", "payment_applied", ["credit_applied", "payment_applied"]),
        ("credit_applied", "payment_applied", ["payment_applied"]),
        ("payment_applied", "payment_applied", []),
        ("payment_applied", "invoice_posted", []),
    ],
)
def test_ingestion_resume_math_covers_settlement(reached, target, expected) -> None:
    handler = SCENARIO_HANDLERS["invoice_ingestion"]
    assert handler.remaining_steps(reached, target, False) == expected


def test_ingestion_ingests_posted_for_settlement_targets(fake_client, billable_account, org_context) -> None:
    captured = {}

    def fake_ingest(client, account, lines, run_id, *, status, **kw):
        captured["status"] = status
        return "3ttINV", "INV-1", ["5TV1"]

    ctx = StepContext(
        client=fake_client, org_context=org_context, run_id="RUN", account=billable_account,
        lines=[], with_opportunity=False, poll_timeout=1, target_stage="payment_applied",
    )
    orig = lifecycle.ingest_invoice
    lifecycle.ingest_invoice = fake_ingest
    try:
        m = steps.run_ingest_invoice(ctx, Manifest(run_id="RUN", kind="invoice_ingestion"))
    finally:
        lifecycle.ingest_invoice = orig
    assert captured["status"] == "Posted"
    assert m.reached_stage == "invoice_posted"


# -- config ---------------------------------------------------------------------


def _pst(**extra):
    return _coerce_spec({"account": "Infinitech", **extra}, "t")


def test_config_parses_full_settlement_block() -> None:
    spec = _pst(
        target_stage="payment_applied",
        settlement={
            "application_level": "line",
            "credit": {"percent": 20, "lines": [0, "QB-API-FLEX"]},
            "payment": {"amount": 150},
        },
    )
    s = spec.settlement
    assert s.application_level == "line"
    assert s.credit == CreditSpec(amount=None, percent=20.0, lines=[0, "QB-API-FLEX"], tax_strategy="auto")
    assert s.payment == PaymentSpec(amount=150.0, percent=None, lines=None)


@pytest.mark.parametrize("payment", [None, "exact", {"amount": "exact"}, {}])
def test_config_payment_defaults_to_exact(payment) -> None:
    spec = _pst(target_stage="payment_applied", settlement={"payment": payment})
    assert spec.settlement.payment.is_exact


def test_config_ingestion_accepts_settlement() -> None:
    spec = _coerce_spec(
        {
            "kind": "invoice_ingestion",
            "target_stage": "payment_applied",
            "invoice_lines": [{"name": "L", "quantity": 1, "unit_price": 10}],
            "settlement": {"payment": {"percent": 50}},
        },
        "t",
    )
    assert spec.settlement.payment.percent == 50.0


@pytest.mark.parametrize(
    "stage, settlement, msg",
    [
        ("payment_applied", None, "needs a 'settlement:' block"),
        ("credit_applied", {"payment": {"amount": 1}}, "needs 'settlement.credit'"),
        ("credit_applied", {"credit": {"amount": 1}, "payment": {"amount": 1}}, "never runs"),
        ("invoice_posted", {"payment": {"amount": 1}}, "only runs at target_stage"),
        ("payment_applied", {"credit": {"amount": 1, "percent": 5}}, "exactly one"),
        ("payment_applied", {"credit": {}}, "exactly one"),
        ("payment_applied", {"credit": {"percent": 120}}, "<= 100"),
        ("payment_applied", {"credit": {"amount": -5}}, "> 0"),
        ("payment_applied", {"credit": {"amount": 5, "tax_strategy": "ManualOverride"}}, "not supported"),
        ("payment_applied", {"payment": {"amount": 5, "percent": 5}}, "not both"),
        ("payment_applied", {"payment": {"percent": 5000}}, "<= 1000"),
        ("payment_applied", {"payment": {"lines": []}}, "lines must be"),
        ("payment_applied", {"payment": {"lines": [-1]}}, ">= 0"),
        ("payment_applied", {"payment": {"bogus": 1}}, "unknown payment field"),
        ("payment_applied", {"application_level": "invoice", "payment": None}, "not valid"),
    ],
)
def test_config_rejects_bad_settlement(stage, settlement, msg) -> None:
    raw = {"target_stage": stage}
    if settlement is not None:
        raw["settlement"] = settlement
    with pytest.raises(ConfigError, match=re.escape(msg)):
        _pst(**raw)


def test_inherited_settlement_dropped_before_settlement_stages(tmp_path) -> None:
    from scripts.txn_data_harness.config import load_scenarios

    cfg = tmp_path / "c.yaml"
    cfg.write_text(
        "defaults:\n"
        "  settlement: {payment: {amount: exact}}\n"
        "scenarios:\n"
        "  - {account: Infinitech, target_stage: invoice_posted}\n"
        "  - {account: Infinitech, target_stage: payment_applied}\n"
    )
    a, b = load_scenarios(SimpleNamespace(config=str(cfg)))
    assert a.settlement is None
    assert b.settlement.payment.is_exact


def test_settlement_round_trips_through_dict() -> None:
    spec = SettlementSpec(
        application_level="header",
        credit=CreditSpec(amount=12.5, lines=["Line B"], tax_strategy="Ignore"),
        payment=PaymentSpec(percent=120.0, lines=[1]),
    )
    data = json.loads(json.dumps(spec.to_dict()))
    assert settlement_from_dict(data) == spec
    exact = SettlementSpec(payment=PaymentSpec())
    assert settlement_from_dict(exact.to_dict()) == exact
    assert settlement_from_dict(None) is None


# -- payload builders and pure helpers ------------------------------------------


def test_build_credit_payload_carries_per_line_strategy() -> None:
    body = lifecycle.build_credit_payload(
        [("5TV1", 40.0), ("5TV2", 10.0)], "RUN", {"5TV1": "Calculate", "5TV2": "Ignore"},
        effective_date="2026-11-25",
    )
    assert body == {
        "type": "POSTED",
        "taxStrategy": "Calculate",
        "effectiveDate": "2026-11-25",
        "description": "RUN credit",
        "invoiceLines": [
            {"invoiceLineId": "5TV1", "amountToCredit": 40.0, "taxStrategy": "Calculate"},
            {"invoiceLineId": "5TV2", "amountToCredit": 10.0, "taxStrategy": "Ignore"},
        ],
    }


def test_build_credit_payload_refuses_empty() -> None:
    with pytest.raises(LifecycleError, match="nothing to credit"):
        lifecycle.build_credit_payload([], "RUN")


def test_build_payment_record_is_external_processed_sale() -> None:
    body = lifecycle.build_payment_record("001A", 100.456, "RUN", currency="USD")
    assert body["AccountId"] == "001A"
    assert body["Amount"] == 100.46
    assert (body["Status"], body["Type"], body["ProcessingMode"]) == ("Processed", "Sale", "External")
    assert body["GatewayRefNumber"] == "RUN-PAY"
    assert body["CurrencyIsoCode"] == "USD"
    assert "CurrencyIsoCode" not in lifecycle.build_payment_record("001A", 1, "RUN")


def test_build_payment_apply_payload() -> None:
    body = lifecycle.build_payment_apply_payload("5TV1", 60, "RUN")
    assert body["appliedToId"] == "5TV1"
    assert body["amount"] == 60.0
    assert body["comments"] == "Transaction Data Harness (RUN)"
    assert "associatedAccountId" not in body
    assert lifecycle.build_payment_apply_payload("3tt", 1, "RUN", "001A")["associatedAccountId"] == "001A"


_TAXED = {"Id": "5TVT", "ChargeAmount": 450.0, "TaxAmount": 45.0, "LineAmount": 495.0, "Balance": 255.0}
_UNTAXED = {"Id": "5TVU", "ChargeAmount": 100.0, "TaxAmount": 0.0, "LineAmount": 100.0, "Balance": 60.0}


def test_line_tax_strategy_auto() -> None:
    assert lifecycle.line_tax_strategy(_TAXED, "auto") == "Calculate"
    assert lifecycle.line_tax_strategy(_UNTAXED, "auto") == "Ignore"
    assert lifecycle.line_tax_strategy(_TAXED, "CopyFromInvoiceLine") == "CopyFromInvoiceLine"


@pytest.mark.parametrize(
    "line, strategy, expected",
    [
        (_TAXED, "auto", 231.81),            # 255 * 450/495 = 231.818.. floored
        (_TAXED, "Calculate", 231.81),
        (_TAXED, "Ignore", 255.0),
        (_TAXED, "CopyFromInvoiceLine", 210.0),  # whole 45 tax is copied on top
        (_UNTAXED, "auto", 60.0),
        (_UNTAXED, "CopyFromInvoiceLine", 60.0),
        ({**_TAXED, "Balance": 495.0}, "Ignore", 450.0),  # capped at charge
        ({**_TAXED, "Balance": 30.0}, "CopyFromInvoiceLine", 0.0),
    ],
)
def test_credit_capacity(line, strategy, expected) -> None:
    assert lifecycle.credit_capacity(line, strategy) == expected


def test_allocate_spreads_in_order_and_caps() -> None:
    lines = [{"Id": "a", "Balance": 30}, {"Id": "b", "Balance": 0}, {"Id": "c", "Balance": 50}]
    cap = lambda r: float(r["Balance"])  # noqa: E731
    assert lifecycle.allocate(60, lines, cap) == [("a", 30.0), ("c", 30.0)]
    assert lifecycle.allocate(500, lines, cap) == [("a", 30.0), ("c", 50.0)]
    assert lifecycle.allocate(0, lines, cap) == []


_LINES = [
    {"Id": "5TV2", "Name": "Line B", "Product2": None},
    {"Id": "5TV1", "Name": "Line A", "Product2": {"StockKeepingUnit": "QB-API-FLEX"}},
]


def test_order_invoice_lines_prefers_ingest_order() -> None:
    assert [r["Id"] for r in lifecycle.order_invoice_lines(_LINES, ["5TV1", "5TV2"])] == ["5TV1", "5TV2"]
    assert [r["Id"] for r in lifecycle.order_invoice_lines(_LINES, [])] == ["5TV1", "5TV2"]


def test_select_invoice_lines() -> None:
    assert lifecycle.select_invoice_lines(_LINES, None) == _LINES
    assert [r["Id"] for r in lifecycle.select_invoice_lines(_LINES, [1])] == ["5TV1"]
    assert [r["Id"] for r in lifecycle.select_invoice_lines(_LINES, ["line b"])] == ["5TV2"]
    assert [r["Id"] for r in lifecycle.select_invoice_lines(_LINES, ["qb-api-flex", 1])] == ["5TV1"]
    with pytest.raises(LifecycleError, match="out of range"):
        lifecycle.select_invoice_lines(_LINES, [5])
    with pytest.raises(LifecycleError, match="no invoice line"):
        lifecycle.select_invoice_lines(_LINES, ["missing"])


@pytest.mark.parametrize(
    "payment, open_amount, expected",
    [
        (PaymentSpec(), 230.0, (230.0, 230.0, "exact")),
        (PaymentSpec(amount=100.0), 445.0, (100.0, 100.0, "partial")),
        (PaymentSpec(amount=500.0), 445.0, (500.0, 445.0, "over")),
        (PaymentSpec(percent=50.0), 270.0, (135.0, 135.0, "partial")),
        (PaymentSpec(percent=120.0), 495.0, (594.0, 495.0, "over")),
        (PaymentSpec(percent=100.0), 495.0, (495.0, 495.0, "exact")),
    ],
)
def test_plan_payment_modes(payment, open_amount, expected) -> None:
    assert steps.plan_payment(payment, open_amount) == expected


# -- application level ------------------------------------------------------------


@pytest.mark.parametrize(
    "xml, expected",
    [
        ("<BillingSettings><enableTransactionsApplicationToInvoices>false"
         "</enableTransactionsApplicationToInvoices></BillingSettings>", "line"),
        ("<records xsi:type='BillingSettings'><enableTransactionsApplicationToInvoices>true"
         "</enableTransactionsApplicationToInvoices></records>", "header"),
        ("<m:enableTransactionsApplicationToInvoices>true</m:enableTransactionsApplicationToInvoices>", "header"),
        ("<BillingSettings/>", None),
        ("", None),
    ],
)
def test_parse_billing_settings_level(xml, expected) -> None:
    assert lifecycle.parse_billing_settings_level(xml) == expected


def test_read_application_level_reads_once(fake_client, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", lambda c: calls.append(1) or "line")
    assert lifecycle.read_application_level(fake_client) == ("line", "billing_settings")
    assert lifecycle.read_application_level(fake_client) == ("line", "billing_settings")
    assert len(calls) == 1


def test_read_application_level_falls_back_to_invoice_evidence(fake_client, monkeypatch) -> None:
    def boom(c):
        raise RuntimeError("no metadata access")

    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", boom)
    fake_client.query_responses = [[{"SettlementLevel": "Invoice"}]]
    assert lifecycle.read_application_level(fake_client) == ("header", "invoice_settlement_level")


def test_read_application_level_errors_when_unknown(fake_client, monkeypatch) -> None:
    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", lambda c: None)
    fake_client.query_responses = [[]]
    with pytest.raises(LifecycleError, match="Pin settlement.application_level"):
        lifecycle.read_application_level(fake_client)


# -- steps against an in-memory org -----------------------------------------------


class SettleOrg:
    """Routes the settlement steps' SOQL/REST calls onto in-memory records."""

    api_version = "68.0"
    instance_url = "https://settle.example"
    access_token = "x"

    def __init__(self, level: str = "line"):
        self.level = level
        self.invoice = {"Id": "3ttINV", "Status": "Posted", "CurrencyIsoCode": "USD",
                        "TotalAmountWithTax": 250.0, "NetCreditsApplied": 0.0,
                        "NetPaymentsApplied": 0.0, "SettlementLevel": None}
        self.lines = [
            {"Id": "5TV1", "Name": "Line A", "Type": "Charge", "ChargeAmount": 100.0,
             "TaxAmount": 0.0, "LineAmount": 100.0, "Balance": 100.0, "Product2": None},
            {"Id": "5TV2", "Name": "Line B", "Type": "Charge", "ChargeAmount": 150.0,
             "TaxAmount": 0.0, "LineAmount": 150.0, "Balance": 150.0, "Product2": None},
        ]
        self.memos: list[dict] = []
        self.payments: list[dict] = []
        self.credit_apps: list[dict] = []   # {"Id","Amount","level","memo"}
        self.payment_apps: list[dict] = []  # {"Id","Amount","level","payment"}
        self.posts: list[tuple[str, dict]] = []

    # helpers
    def _balance(self) -> float:
        return round(sum(r["Balance"] for r in self.lines), 2)

    def _line(self, lid):
        return next(r for r in self.lines if r["Id"] == lid)

    def query(self, soql: str):
        if soql.startswith("SELECT Id, Status, BillingAccountId"):
            return [{**self.invoice, "Balance": self._balance()}]
        if "FROM InvoiceLine" in soql:
            return [dict(r) for r in self.lines]
        if "FROM CreditMemo " in soql:
            return [dict(m) for m in self.memos][-1:]
        if "FROM Payment " in soql:
            return [{"Id": p["Id"]} for p in self.payments]
        if "FROM CreditMemoLineInvoiceLine" in soql:
            return [a for a in self.credit_apps if a["level"] == "line"]
        if "FROM CreditMemoInvApplication" in soql:
            return [a for a in self.credit_apps if a["level"] == "header"]
        if "FROM PaymentLineInvoiceLine" in soql:
            return [a for a in self.payment_apps if a["level"] == "line"]
        if "FROM PaymentLineInvoice " in soql:
            return [a for a in self.payment_apps if a["level"] == "header"]
        raise AssertionError(f"unexpected SOQL: {soql}")

    def post(self, path: str, body: dict):
        self.posts.append((path, body))
        if path.endswith("/actions/credit"):
            memo_id = f"50g{len(self.memos) + 1}"
            total = 0.0
            for ln in body["invoiceLines"]:
                line = self._line(ln["invoiceLineId"])
                line["Balance"] = round(line["Balance"] - ln["amountToCredit"], 2)
                total += ln["amountToCredit"]
                self.credit_apps.append({
                    "Id": f"4sG{len(self.credit_apps) + 1}", "Amount": ln["amountToCredit"],
                    "level": self.level,
                })
            self.memos.append({"Id": memo_id, "Status": "Posted", "Balance": 0.0,
                               "TotalAmountWithTax": total})
            return {"success": True, "requestIdentifier": "r", "statusURL": "", "errors": []}
        if path.endswith("/sobjects/Payment"):
            pid = f"0aQ{len(self.payments) + 1}"
            self.payments.append({"Id": pid, **body})
            return {"id": pid, "success": True, "errors": []}
        if path.endswith("/actions/apply"):
            target = body["appliedToId"]
            if self.level == "line":
                assert target.startswith("5TV"), "line level applies to invoice lines"
                line = self._line(target)
                line["Balance"] = round(line["Balance"] - body["amount"], 2)
            else:
                assert target == self.invoice["Id"], "header level applies to the invoice"
                remaining = body["amount"]
                for line in self.lines:
                    take = min(remaining, line["Balance"])
                    line["Balance"] = round(line["Balance"] - take, 2)
                    remaining -= take
            app_id = f"1Al{len(self.payment_apps) + 1}"
            self.payment_apps.append({"Id": app_id, "Amount": body["amount"], "level": self.level})
            return {"id": app_id, "appliedDate": "2026-11-25T00:00:00Z"}
        raise AssertionError(f"unexpected POST {path}")


def _settle_ctx(org, account, settlement, checkpoints=None):
    return StepContext(
        client=org, org_context=None, run_id="RUN", account=account, lines=[],
        with_opportunity=False, poll_timeout=1,
        checkpoint=(checkpoints.append if checkpoints is not None else None),
        settlement=settlement,
    )


def _posted_manifest(**kw):
    return Manifest(run_id="RUN", kind="invoice_ingestion", invoice_id="3ttINV",
                    invoice_line_ids=["5TV1", "5TV2"], reached_stage="invoice_posted", **kw)


def test_settlement_steps_line_level_end_to_end(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(
        application_level="line",
        credit=CreditSpec(percent=20.0, lines=[0]),
        payment=PaymentSpec(),
    )
    ctx = _settle_ctx(org, billable_account, spec)
    m = steps.run_credit(ctx, _posted_manifest())
    m = steps.run_payment(ctx, m)

    credit_path, credit_body = org.posts[0]
    assert credit_path.endswith("/invoices/3ttINV/actions/credit")
    assert credit_body["invoiceLines"] == [
        {"invoiceLineId": "5TV1", "amountToCredit": 20.0, "taxStrategy": "Ignore"},
    ]
    assert m.application_level == "line" and m.application_level_source == "config"
    assert m.credit_memo_ids == ["50g1"] and m.credit_application_ids == ["4sG1"]
    assert (m.credit_amount_requested, m.credit_amount_applied) == (20.0, 20.0)
    assert m.payment_ids == ["0aQ1"]
    assert org.payments[0]["Amount"] == 230.0 and org.payments[0]["CurrencyIsoCode"] == "USD"
    applies = [b["appliedToId"] for p, b in org.posts if p.endswith("/actions/apply")]
    assert applies == ["5TV1", "5TV2"]
    assert (m.payment_amount, m.payment_apply_target, m.payment_amount_applied) == (230.0, 230.0, 230.0)
    assert m.payment_mode == "exact"
    assert m.payment_application_ids == ["1Al1", "1Al2"]
    assert m.invoice_balance == 0.0
    assert m.reached_stage == "payment_applied"
    assert m.settlement_baseline["balance"] == 250.0
    assert m.settlement["credit"]["percent"] == 20.0
    assert m.settlement_warnings == []


def test_payment_header_level_applies_to_invoice(billable_account) -> None:
    org = SettleOrg("header")
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=100.0, lines=[1]))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    applies = [b for p, b in org.posts if p.endswith("/actions/apply")]
    assert [b["appliedToId"] for b in applies] == ["3ttINV"]
    assert applies[0]["amount"] == 100.0
    assert m.payment_mode == "partial" and m.payment_amount_applied == 100.0
    assert m.invoice_balance == 150.0
    assert any("ignored at Header Level" in w for w in m.settlement_warnings)


def test_credit_header_level_reads_invoice_applications(billable_account) -> None:
    org = SettleOrg("header")
    spec = SettlementSpec(application_level="header", credit=CreditSpec(amount=50.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.credit_application_ids == ["4sG1"]
    assert m.credit_amount_applied == 50.0
    assert m.settlement_warnings == []


def test_rows_at_the_other_level_are_recorded_with_a_warning(billable_account) -> None:
    org = SettleOrg("header")  # the org writes header rows...
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=10.0))  # ...pinned line
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.credit_application_ids == ["4sG1"]
    assert any("found at header level" in w for w in m.settlement_warnings)


def test_auto_level_is_read_from_the_org_and_recorded(billable_account, monkeypatch) -> None:
    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", lambda c: "line")
    org = SettleOrg("line")
    m = steps.run_payment(
        _settle_ctx(org, billable_account, SettlementSpec(payment=PaymentSpec(amount=10.0))),
        _posted_manifest(),
    )
    assert (m.application_level, m.application_level_source) == ("line", "billing_settings")


def test_manifest_level_wins_on_resume(billable_account, monkeypatch) -> None:
    monkeypatch.setattr(
        lifecycle, "_read_billing_settings_level",
        lambda c: pytest.fail("a recorded level must not be re-read"),
    )
    org = SettleOrg("header")
    m = steps.run_payment(
        _settle_ctx(org, billable_account, SettlementSpec(payment=PaymentSpec(amount=10.0))),
        _posted_manifest(application_level="header", application_level_source="billing_settings"),
    )
    assert m.application_level == "header"


def test_over_payment_leaves_balance_and_warns(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(percent=120.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert (m.payment_amount, m.payment_apply_target, m.payment_mode) == (300.0, 250.0, "over")
    assert m.payment_amount_applied == 250.0
    assert any("over-payment leaves 50.0 unapplied" in w for w in m.settlement_warnings)


def test_baseline_records_platform_applications(billable_account) -> None:
    org = SettleOrg("line")
    org.lines[0]["Balance"] = 60.0
    org.invoice["NetPaymentsApplied"] = 40.0
    org.payment_apps.append({"Id": "1AlAUTO", "Amount": 40.0, "level": "line"})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.settlement_baseline["net_payments_applied"] == 40.0
    assert m.settlement_baseline["foreign_payment_application_ids"] == ["1AlAUTO"]
    assert m.payment_amount == 210.0  # the open balance after the platform's 40
    assert any("applied by the platform at post" in w for w in m.settlement_warnings)


def test_credit_retry_polls_instead_of_reposting(billable_account) -> None:
    org = SettleOrg("line")
    org.memos.append({"Id": "50gPRIOR", "Status": "Posted", "Balance": 0.0})
    org.credit_apps.append({"Id": "4sGPRIOR", "Amount": 20.0, "level": "line"})
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(
        _settle_ctx(org, billable_account, spec),
        _posted_manifest(credit_submitted=True, settlement_baseline={"balance": 250.0}),
    )
    assert org.posts == []
    assert m.credit_memo_ids == ["50gPRIOR"]
    assert m.credit_amount_applied == 20.0


def test_payment_retry_applies_only_the_remainder(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)

    # First attempt: the second apply call fails transiently.
    calls = {"n": 0}
    real_post = org.post

    def flaky_post(path, body):
        if path.endswith("/actions/apply"):
            calls["n"] += 1
            if calls["n"] == 2:
                raise SfApiError(503, "unavailable", "POST", path)
        return real_post(path, body)

    org.post = flaky_post
    m = _posted_manifest()
    with pytest.raises(SfApiError):
        steps.run_payment(ctx, m)
    assert m.payment_ids == ["0aQ1"] and m.payment_apply_target == 250.0

    # Retry: same payment, only the unapplied 150 goes out.
    org.post = real_post
    m = steps.run_payment(ctx, m)
    assert len(org.payments) == 1
    applies = [b for p, b in org.posts if p.endswith("/actions/apply")]
    assert [(b["appliedToId"], b["amount"]) for b in applies] == [("5TV1", 100.0), ("5TV2", 150.0)]
    assert m.payment_amount_applied == 250.0 and m.invoice_balance == 0.0


def test_payment_skipped_when_nothing_is_open(billable_account) -> None:
    org = SettleOrg("line")
    for line in org.lines:
        line["Balance"] = 0.0
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=10.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.payments == [] and m.payment_ids == []
    assert m.reached_stage == "payment_applied"
    assert any("payment skipped" in w for w in m.settlement_warnings)


def test_credit_is_capped_at_the_open_balance(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=500.0, lines=["Line A"]))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.posts[0][1]["invoiceLines"][0]["amountToCredit"] == 100.0
    assert any("credit capped" in w for w in m.settlement_warnings)


@pytest.mark.parametrize("step", [steps.run_credit, steps.run_payment])
def test_settlement_steps_noop_without_their_block(step, billable_account) -> None:
    org = SettleOrg("line")
    m = step(_settle_ctx(org, billable_account, None), _posted_manifest())
    assert org.posts == []
    assert m.reached_stage in ("credit_applied", "payment_applied")


def test_settlement_falls_back_to_the_manifest_on_resume(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=25.0))
    m = steps.run_payment(
        _settle_ctx(org, billable_account, None), _posted_manifest(settlement=spec.to_dict())
    )
    assert m.payment_amount == 25.0


# -- manifest, report, cli --------------------------------------------------------


def test_settlement_manifest_fields_round_trip() -> None:
    m = Manifest(
        run_id="RUN", kind="sales_txn_quote", reached_stage="payment_applied",
        settlement={"application_level": "auto", "credit": None, "payment": {"amount": "exact"}},
        application_level="line", application_level_source="billing_settings",
        settlement_baseline={"balance": 495.0, "foreign_payment_application_ids": ["1AlX"]},
        credit_memo_ids=["50g1"], credit_application_ids=["4sG1"], credit_submitted=True,
        credit_amount_requested=45.0, credit_amount_applied=49.5,
        payment_ids=["0aQ1"], payment_application_ids=["1Al1"], payment_amount=445.5,
        payment_apply_target=445.5, payment_amount_applied=445.5, payment_mode="exact",
        invoice_balance=0.0, settlement_warnings=["w"],
    )
    again = Manifest.from_dict(json.loads(json.dumps(m.to_dict())))
    assert again == m
    summary = SCENARIO_HANDLERS["sales_txn_quote"].summarize(again)["settlement"]
    assert summary["payment"]["mode"] == "exact"
    assert summary["credit"]["applied"] == 49.5
    assert SCENARIO_HANDLERS["invoice_ingestion"].summarize(again)["settlement"]["application_level"] == "line"
    assert SCENARIO_HANDLERS["sales_txn_quote"].summarize(Manifest(run_id="X"))["settlement"] is None


def test_report_histogram_counts_settlement_stages() -> None:
    manifests = [
        Manifest(run_id="A", kind="sales_txn_order", reached_stage="payment_applied"),
        Manifest(run_id="B", kind="invoice_ingestion", reached_stage="credit_applied"),
    ]
    report = build_batch_report(manifests)
    assert report["stage_histogram_by_kind"]["sales_txn_order"]["payment_applied"] == 1
    assert report["stage_histogram_by_kind"]["invoice_ingestion"]["credit_applied"] == 1


def test_cli_step_needs_settlement_for_settlement_targets() -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    args = SimpleNamespace(config=None, to_stage="payment_applied")
    with pytest.raises(LifecycleError, match="needs settlement options"):
        _settlement_for_step(args, Manifest(run_id="X"))
    # The manifest's own block is used by the steps; nothing to load.
    assert _settlement_for_step(args, Manifest(run_id="X", settlement={"payment": None})) is None
    assert _settlement_for_step(SimpleNamespace(config=None, to_stage="invoice_posted"), Manifest(run_id="X")) is None


def test_cli_stage_choices_include_settlement() -> None:
    import argparse

    from scripts.txn_data_harness.cli_args import add_scenario_args

    p = argparse.ArgumentParser()
    add_scenario_args(p)
    assert p.parse_args(["--target-stage", "payment_applied"]).target_stage == "payment_applied"


def test_ingestion_retries_transient_settlement_failure_after_post(
    billable_account, org_context, monkeypatch
) -> None:
    """Once the invoice is Posted, a transient settlement failure is retried
    from the checkpoint (the settlement steps are retry-safe)."""
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.handlers import invoice_ingestion as mod
    from scripts.txn_data_harness.models import ResolvedInvoiceIngestionSpec

    calls: list[str] = []

    def fake_execute(step, ctx, manifest):
        calls.append(step)
        if step == "ingest_invoice":
            manifest.invoice_id = "3ttINV"
            manifest.reached_stage = "invoice_posted"
        elif step == "credit_applied" and calls.count("credit_applied") == 1:
            raise SfApiError(503, "unavailable", "POST", "/x")
        else:
            manifest.reached_stage = step if step != "promote_to_posted" else manifest.reached_stage
        return manifest

    monkeypatch.setattr(mod, "execute_step", fake_execute)
    monkeypatch.setattr(mod, "write_manifest", lambda m: None)
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    spec = _coerce_spec(
        {
            "kind": "invoice_ingestion",
            "target_stage": "payment_applied",
            "invoice_lines": [{"name": "L", "quantity": 1, "unit_price": 10}],
            "settlement": {"credit": {"amount": 1}, "payment": None},
        },
        "t",
    )
    resolved = ResolvedInvoiceIngestionSpec(
        spec=spec, account=billable_account, invoice_lines=[], invoice_overrides=None,
        effective_stage="payment_applied",
    )
    m = SCENARIO_HANDLERS["invoice_ingestion"].run(
        None, org_context, "RUN", resolved, poll_timeout=1, max_retries=2
    )
    assert m.reached_stage == "payment_applied" and m.error is None
    assert m.attempts == 2
    assert calls == [
        "ingest_invoice", "promote_to_posted", "credit_applied",
        "credit_applied", "payment_applied",
    ]
    assert m.settlement["credit"]["amount"] == 1.0


@pytest.mark.parametrize(
    "path",
    [
        "scripts/txn_data_harness/scenarios/sales_txn_quote/17-settlement.yaml",
        "scripts/txn_data_harness/scenarios/invoice_ingestion/17-settlement.yaml",
    ],
)
def test_settlement_example_configs_parse(path) -> None:
    from pathlib import Path

    from scripts.txn_data_harness.config import load_scenarios

    root = Path(__file__).resolve().parents[2]
    specs = load_scenarios(SimpleNamespace(config=str(root / path)))
    assert specs and all(s.target_stage == "payment_applied" for s in specs)
    assert all(s.settlement is not None and s.settlement.payment is not None for s in specs)
