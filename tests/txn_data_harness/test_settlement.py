"""Settlement stages (credit_applied / payment_applied): graph, config,
payload builders, application-level handling, step behavior and manifest
round-trip. Offline only -- the live contract is in
``scripts/txn_data_harness/docs/contracts-billing-settlement.md``.
"""

from __future__ import annotations

import json
import re
from types import SimpleNamespace
from typing import Optional

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


@pytest.mark.parametrize("payment", ["exact", {"amount": "exact"}, {}])
def test_config_payment_defaults_to_exact(payment) -> None:
    spec = _pst(target_stage="payment_applied", settlement={"payment": payment})
    assert spec.settlement.payment.is_exact


def test_config_payment_null_is_absent() -> None:
    spec = _pst(target_stage="credit_applied",
                settlement={"credit": {"amount": 5}, "payment": None})
    assert spec.settlement.payment is None


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
        ("payment_applied", {"credit": {"amount": 1}}, "needs 'settlement.payment'"),
        ("payment_applied", {"credit": {"amount": float("nan")}}, "finite"),
        ("payment_applied", {"payment": {"amount": float("inf")}}, "finite"),
        ("payment_applied", {"payment": {"percent": "nan"}}, "finite"),
        ("credit_applied", {"credit": {"percent": float("nan")}}, "finite"),
        ("payment_applied", {"credit": {"amount": 1, "percent": 5}}, "exactly one"),
        ("payment_applied", {"credit": {}}, "exactly one"),
        ("payment_applied", {"credit": {"percent": 120}}, "<= 100"),
        ("payment_applied", {"credit": {"amount": -5}}, "> 0"),
        ("payment_applied", {"credit": {"amount": 5, "tax_strategy": "ManualOverride"}}, "not supported"),
        ("payment_applied", {"payment": {"amount": 5, "percent": 5}}, "not both"),
        ("payment_applied", {"payment": {"amount": 0}}, "> 0"),
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


@pytest.mark.parametrize(
    "spec",
    [
        SettlementSpec(credit=CreditSpec(percent=10.0)),
        SettlementSpec(payment=PaymentSpec(amount=50.0)),
        SettlementSpec(application_level="line", payment=PaymentSpec()),
    ],
)
def test_partial_settlement_round_trips_without_inventing_blocks(spec) -> None:
    data = json.loads(json.dumps(spec.to_dict()))
    assert None not in data.values()
    assert settlement_from_dict(data) == spec


def test_shared_defaults_with_credit_and_payment_allow_credit_only_target(tmp_path) -> None:
    from scripts.txn_data_harness.config import load_scenarios

    cfg = tmp_path / "c.yaml"
    cfg.write_text(
        "defaults:\n"
        "  settlement: {credit: {amount: 5}, payment: {amount: exact}}\n"
        "scenarios:\n"
        "  - {account: Infinitech, target_stage: credit_applied}\n"
        "  - {account: Infinitech, target_stage: payment_applied}\n"
    )
    a, b = load_scenarios(SimpleNamespace(config=str(cfg)))
    assert a.settlement.credit.amount == 5.0 and a.settlement.payment is None
    assert b.settlement.payment.is_exact


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
    body = lifecycle.build_payment_record("001A", 100.456, "RUN", currency="USD", places=2)
    assert body["AccountId"] == "001A"
    assert body["Amount"] == 100.46
    assert (body["Status"], body["Type"], body["ProcessingMode"]) == ("Processed", "Sale", "External")
    assert body["GatewayRefNumber"] == "RUN-PAY"
    assert body["CurrencyIsoCode"] == "USD"
    assert "CurrencyIsoCode" not in lifecycle.build_payment_record("001A", 1, "RUN", places=2)
    assert lifecycle.build_payment_record("001A", 10.0049, "RUN", places=3)["Amount"] == 10.005


def test_build_payment_apply_payload() -> None:
    body = lifecycle.build_payment_apply_payload("5TV1", 60, "RUN", places=2)
    assert body["appliedToId"] == "5TV1"
    assert body["amount"] == 60.0
    assert body["comments"] == "Transaction Data Harness (RUN)"
    assert "associatedAccountId" not in body
    assert lifecycle.build_payment_apply_payload(
        "3tt", 1, "RUN", "001A", places=2
    )["associatedAccountId"] == "001A"
    assert lifecycle.build_payment_apply_payload("5TV1", 1.0051, "RUN", places=3)["amount"] == 1.005


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
    assert lifecycle.credit_capacity(line, strategy, 2) == expected


def test_allocate_spreads_in_order_and_caps() -> None:
    lines = [{"Id": "a", "Balance": 30}, {"Id": "b", "Balance": 0}, {"Id": "c", "Balance": 50}]
    cap = lambda r: float(r["Balance"])  # noqa: E731
    assert lifecycle.allocate(60, lines, cap, 2) == [("a", 30.0), ("c", 30.0)]
    assert lifecycle.allocate(500, lines, cap, 2) == [("a", 30.0), ("c", 50.0)]
    assert lifecycle.allocate(0, lines, cap, 2) == []


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
    assert steps.plan_payment(payment, open_amount, 2) == expected


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
    with pytest.raises(LifecycleError, match=r"--application-level line\|header") as info:
        lifecycle.read_application_level(fake_client)
    assert info.value.failure_class == "deterministic"


# -- steps against an in-memory org -----------------------------------------------


def _ids_in(soql: str, field: str) -> Optional[set[str]]:
    m = re.search(rf"{re.escape(field)} IN \(([^)]*)\)", soql)
    return None if m is None else {x.strip(" '") for x in m.group(1).split(",")}


def _eq(soql: str, field: str) -> Optional[str]:
    m = re.search(rf"(?<![\w.]){re.escape(field)} = '([^']*)'", soql)
    return None if m is None else m.group(1)


class _Row(dict):
    """A record holding only the selected fields; any other read fails."""

    @classmethod
    def project(cls, row: dict, soql: str) -> "_Row":
        select = soql[len("SELECT "):soql.index(" FROM ")]
        fields = {f.strip().split(".")[0] for f in select.split(",")}
        out = cls({f: row.get(f) for f in fields})
        out._fields = fields
        return out

    def _check(self, key):
        if key not in self._fields:
            raise AssertionError(f"field {key!r} read but not selected ({sorted(self._fields)})")

    def get(self, key, default=None):
        self._check(key)
        return super().get(key, default)

    def __getitem__(self, key):
        self._check(key)
        return super().__getitem__(key)


class SettleOrg:
    """In-memory org for the settlement steps.

    Honors the WHERE filters the steps send (tags, ids, invoice), so a step
    that drops a filter sees records it should not. Credit memos can be made
    to appear late (``memo_visible_after`` CreditMemo queries) and to move
    through ``memo_statuses`` (one status per CreditMemo query); a memo's
    application rows appear when it reaches Posted.
    """

    api_version = "68.0"
    instance_url = "https://settle.example"
    access_token = "x"

    def __init__(self, level: str = "line", places: int = 2):
        self.level = level
        self.places = places
        self.org_currency = "USD"
        self.invoice = {"Id": "3ttINV", "Status": "Posted", "CurrencyIsoCode": "USD",
                        "BillingAccountId": "001BILLABLE",
                        "TotalAmountWithTax": 250.0, "NetCreditsApplied": 0.0,
                        "NetPaymentsApplied": 0.0, "SettlementLevel": None}
        self.lines = [
            {"Id": "5TV1", "Name": "Line A", "Type": "Charge", "ChargeAmount": 100.0,
             "TaxAmount": 0.0, "LineAmount": 100.0, "Balance": 100.0, "Product2": None,
             "InvoiceId": "3ttINV"},
            {"Id": "5TV2", "Name": "Line B", "Type": "Charge", "ChargeAmount": 150.0,
             "TaxAmount": 0.0, "LineAmount": 150.0, "Balance": 150.0, "Product2": None,
             "InvoiceId": "3ttINV"},
        ]
        self.memos: list[dict] = []
        self.payments: list[dict] = []
        self.credit_apps: list[dict] = []   # Id, Amount, level, memo, invoice
        self.payment_apps: list[dict] = []  # Id, Amount, level, payment, invoice
        self.posts: list[tuple[str, dict, bool]] = []
        self.memo_statuses: list[str] = ["Posted"]
        self.memo_visible_after = 0
        self.memo_queries = 0
        self.payment_queries = 0
        self.fail_next_post: Optional[Exception] = None
        self._pending_credit: list[tuple[str, float]] = []

    def _line(self, lid):
        return next(r for r in self.lines if r["Id"] == lid)

    @staticmethod
    def _app_row(a: dict) -> dict:
        """An application row as the org returns it: Applied, not reversed,
        unless the test says otherwise."""
        return {"Type": "Applied", "UnappliedStatus": "No", "HasBeenUnapplied": "No", **a}

    def _type_ok(self, soql: str, a: dict) -> bool:
        typ = _eq(soql, "Type")
        return typ is None or self._app_row(a)["Type"] == typ

    def _r(self, value: float) -> float:
        return round(value, self.places)

    def _balance(self) -> float:
        return self._r(sum(r["Balance"] for r in self.lines
                           if r["InvoiceId"] == "3ttINV" and r["Type"] == "Charge"))

    def _post_memo(self, memo: dict) -> None:
        for line_id, amt in memo.pop("_allocs", []):
            line = self._line(line_id)
            line["Balance"] = self._r(line["Balance"] - amt)
            self.credit_apps.append({"Id": f"4sG{len(self.credit_apps) + 1}", "Amount": amt,
                                     "level": self.level, "memo": memo["Id"],
                                     "invoice": line["InvoiceId"]})

    def query(self, soql: str):
        """Rows carrying only the fields the SOQL selects; reading any other
        field fails the test (like a real org's response)."""
        return [_Row.project(r, soql) for r in self._query(soql)]

    def _query(self, soql: str):
        if soql.startswith("SELECT DecimalPlaces FROM CurrencyType"):
            return [{"DecimalPlaces": self.places}]
        if soql.startswith("SELECT DefaultCurrencyIsoCode FROM Organization"):
            return [{"DefaultCurrencyIsoCode": self.org_currency}]
        if soql.startswith("SELECT Id, Status, BillingAccountId"):
            assert _eq(soql, "Id") == self.invoice["Id"]
            # NetCreditsApplied rolls up every credit application on the
            # invoice, as the platform's does.
            credited = sum(a["Amount"] for a in self.credit_apps if a["invoice"] == "3ttINV")
            return [{**self.invoice, "Balance": self._balance(),
                     "NetCreditsApplied": self._r(self.invoice["NetCreditsApplied"] + credited)}]
        if "FROM InvoiceLine " in soql:
            inv, typ = _eq(soql, "InvoiceId"), _eq(soql, "Type")
            return [dict(r) for r in self.lines
                    if r["InvoiceId"] == inv and (typ is None or r["Type"] == typ)]
        if "FROM CreditMemo " in soql:
            self.memo_queries += 1
            ref, desc = _eq(soql, "ReferenceEntityId"), _eq(soql, "Description")
            descs = _ids_in(soql, "Description")
            rows = []
            for m in self.memos:
                if self.memo_queries <= m.get("_visible_after", 0):
                    continue
                if ref is not None and m["ReferenceEntityId"] != ref:
                    continue
                if desc is not None and m["Description"] != desc:
                    continue
                if descs is not None and m["Description"] not in descs:
                    continue
                statuses = m.setdefault("_statuses", list(self.memo_statuses))
                m["Status"] = statuses.pop(0) if len(statuses) > 1 else statuses[0]
                if m["Status"] == "Posted":
                    self._post_memo(m)
                rows.append({k: v for k, v in m.items() if not k.startswith("_")})
            return rows[::-1] if "LIMIT 1" not in soql else rows[-1:]
        if "FROM Payment " in soql:
            self.payment_queries += 1
            acct, tag = _eq(soql, "AccountId"), _eq(soql, "GatewayRefNumber")
            return [{"Id": p["Id"]} for p in self.payments
                    if (acct is None or p["AccountId"] == acct)
                    and (tag is None or p.get("GatewayRefNumber") == tag)
                    and self.payment_queries > p.get("_visible_after", 0)]
        if "FROM CreditMemoLineInvoiceLine" in soql or "FROM CreditMemoInvApplication" in soql:
            level = "line" if "CreditMemoLineInvoiceLine" in soql else "header"
            memos = _ids_in(soql, "CreditMemoId")
            inv = _eq(soql, "InvoiceLine.InvoiceId") or _eq(soql, "InvoiceId")
            return [self._app_row(a) for a in self.credit_apps if a["level"] == level
                    and (memos is None or a["memo"] in memos)
                    and (inv is None or a["invoice"] == inv)
                    and self._type_ok(soql, a)]
        if "FROM PaymentLineInvoiceLine" in soql or "FROM PaymentLineInvoice " in soql:
            level = "line" if "PaymentLineInvoiceLine" in soql else "header"
            pays = _ids_in(soql, "PaymentId")
            inv = _eq(soql, "InvoiceLine.InvoiceId") or _eq(soql, "InvoiceId")
            return [self._app_row(a) for a in self.payment_apps if a["level"] == level
                    and (pays is None or a["payment"] in pays)
                    and (inv is None or a["invoice"] == inv)
                    and self._type_ok(soql, a)]
        raise AssertionError(f"unexpected SOQL: {soql}")

    def post(self, path: str, body: dict, retry: bool = True):
        self.posts.append((path, body, retry))
        if self.fail_next_post is not None:
            exc, self.fail_next_post = self.fail_next_post, None
            if getattr(exc, "_commit_first", False):
                self._do_post(path, body)
            raise exc
        return self._do_post(path, body)

    def _do_post(self, path: str, body: dict):
        if path.endswith("/actions/credit"):
            inv_id = path.split("/invoices/")[1].split("/")[0]
            memo = {"Id": f"50g{len(self.memos) + 1}", "ReferenceEntityId": inv_id,
                    "Description": body["description"], "Status": "Pending", "Balance": 0.0,
                    "TotalAmountWithTax": self._r(sum(ln["amountToCredit"]
                                                      for ln in body["invoiceLines"])),
                    "_visible_after": self.memo_queries + self.memo_visible_after,
                    "_allocs": [(ln["invoiceLineId"], ln["amountToCredit"])
                                for ln in body["invoiceLines"]]}
            self.memos.append(memo)
            return {"success": True, "requestIdentifier": "r", "statusURL": "", "errors": []}
        if path.endswith("/sobjects/Payment"):
            pid = f"0aQ{len(self.payments) + 1}"
            self.payments.append({"Id": pid, **body})
            return {"id": pid, "success": True, "errors": []}
        if path.endswith("/actions/apply"):
            pid = path.split("/payments/")[1].split("/")[0]
            target = body["appliedToId"]
            if self.level == "line":
                assert target.startswith("5TV"), "line level applies to invoice lines"
                line = self._line(target)
                line["Balance"] = self._r(line["Balance"] - body["amount"])
                inv = line["InvoiceId"]
            else:
                assert target.startswith("3tt"), "header level applies to the invoice"
                remaining, inv = body["amount"], target
                for line in self.lines:
                    if line["InvoiceId"] != target:
                        continue
                    take = min(remaining, line["Balance"])
                    line["Balance"] = self._r(line["Balance"] - take)
                    remaining -= take
            app_id = f"1Al{len(self.payment_apps) + 1}"
            self.payment_apps.append({"Id": app_id, "Amount": body["amount"],
                                      "level": self.level, "payment": pid, "invoice": inv})
            return {"id": app_id, "appliedDate": "2026-11-25T00:00:00Z"}
        raise AssertionError(f"unexpected POST {path}")


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(lifecycle.time, "sleep", lambda s: None)
    monkeypatch.setattr(steps.time, "sleep", lambda s: None)
    lifecycle._decimals_cache.clear()
    lifecycle._org_currency_cache.clear()


def _settle_ctx(org, account, settlement, override=None):
    return StepContext(
        client=org, org_context=None, run_id="RUN", account=account, lines=[],
        with_opportunity=False, poll_timeout=1, checkpoint=None,
        settlement=settlement, application_level_override=override,
    )


def _posted_manifest(**kw):
    fields = dict(run_id="RUN", kind="invoice_ingestion", invoice_id="3ttINV",
                  invoice_line_ids=["5TV1", "5TV2"], reached_stage="invoice_posted",
                  account_name="Infinitech")
    return Manifest(**{**fields, **kw})


def _applies(org):
    return [(b["appliedToId"], b["amount"]) for p, b, _ in org.posts if p.endswith("/actions/apply")]


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

    credit_path, credit_body, credit_retry = org.posts[0]
    assert credit_path.endswith("/invoices/3ttINV/actions/credit")
    assert credit_retry is False
    assert credit_body["invoiceLines"] == [
        {"invoiceLineId": "5TV1", "amountToCredit": 20.0, "taxStrategy": "Ignore"},
    ]
    assert all(retry is False for _, _, retry in org.posts), "settlement writes go out once"
    assert m.application_level == "line" and m.application_level_source == "config"
    assert m.credit_memo_ids == ["50g1"] and m.credit_application_ids == ["4sG1"]
    assert (m.credit_amount_requested, m.credit_amount_applied) == (20.0, 20.0)
    assert m.payment_ids == ["0aQ1"]
    assert org.payments[0]["Amount"] == 230.0 and org.payments[0]["CurrencyIsoCode"] == "USD"
    assert _applies(org) == [("5TV1", 80.0), ("5TV2", 150.0)]
    assert (m.payment_amount, m.payment_apply_target, m.payment_amount_applied) == (230.0, 230.0, 230.0)
    assert m.payment_mode == "exact"
    assert m.payment_application_ids == ["1Al1", "1Al2"]
    assert m.invoice_balance == 0.0
    assert m.reached_stage == "payment_applied"
    assert m.settlement_baseline["balance"] == 250.0
    assert m.settlement_baseline["decimal_places"] == 2
    assert m.settlement["credit"]["percent"] == 20.0
    assert m.settlement_warnings == []


def test_payment_header_level_applies_to_invoice(billable_account) -> None:
    org = SettleOrg("header")
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=100.0, lines=[1]))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert _applies(org) == [("3ttINV", 100.0)]
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


@pytest.mark.parametrize("org_level", ["line", "header"])
def test_credit_read_back_needs_no_level(org_level, billable_account, monkeypatch) -> None:
    """The credit reads both junctions by memo id: rows at either level are
    recorded, and the level is never resolved (or read from the org)."""
    monkeypatch.setattr(lifecycle, "read_application_level",
                        lambda c: pytest.fail("the credit must not need the level"))
    org = SettleOrg(org_level)
    spec = SettlementSpec(credit=CreditSpec(amount=10.0))  # application_level: auto
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.credit_application_ids == ["4sG1"] and m.credit_amount_applied == 10.0
    assert m.application_level is None and m.reached_stage == "credit_applied"


def test_payment_rows_at_the_other_level_are_recorded_with_a_warning(billable_account) -> None:
    org = SettleOrg("header")  # the org writes header rows...
    org.payment_apps.append({"Id": "1AlH", "Amount": 5.0, "level": "header", "payment": "0aQ1",
                             "invoice": "3ttINV"})
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 5.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=5.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec),
                          _posted_manifest(payment_ids=["0aQ1"], payment_amount=5.0,
                                           payment_apply_target=5.0, payment_mode="partial",
                                           application_level="line",
                                           settlement_baseline={"balance": 250.0,
                                                                "decimal_places": 2}))
    assert "1AlH" in m.payment_application_ids
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


def test_override_corrects_a_wrong_recorded_level(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(payment=PaymentSpec(amount=10.0))
    m = steps.run_payment(
        _settle_ctx(org, billable_account, spec, override="line"),
        _posted_manifest(application_level="header", application_level_source="billing_settings"),
    )
    assert (m.application_level, m.application_level_source) == ("line", "override")
    assert _applies(org) == [("5TV1", 10.0)]
    assert any("overridden on resume: header -> line" in w for w in m.settlement_warnings)


def test_level_mismatch_on_apply_is_explained(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = None
    real = org._do_post

    def refuse_apply(path, body):
        if path.endswith("/actions/apply"):
            raise SfApiError(
                400,
                '[{"errorCode":"INVALID_FIELD","message":"Specify an InvoiceLineId as the '
                'appliedToId because the Credit Application Level is Invoice Line."}]',
                "POST", path,
            )
        return real(path, body)

    org._do_post = refuse_apply
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=10.0))
    with pytest.raises(LifecycleError) as info:
        steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    text = str(info.value)
    assert "application level is likely wrong" in text
    assert "Processed and unapplied" in text and "start a new run" in text
    assert "INVALID_FIELD: Specify an InvoiceLineId" in text


def test_over_payment_leaves_balance_and_warns(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(percent=120.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert (m.payment_amount, m.payment_apply_target, m.payment_mode) == (300.0, 250.0, "over")
    assert m.payment_amount_applied == 250.0
    assert any("over-payment leaves 50.0 unapplied" in w for w in m.settlement_warnings)


def test_applications_on_another_invoice_are_not_counted(billable_account) -> None:
    """An over-payment's rest absorbed by a second invoice must not inflate this
    scenario's applied amount or make a resume skip a needed apply."""
    org = SettleOrg("line")
    org.lines.append({"Id": "5TV9", "Name": "Other", "Type": "Charge", "ChargeAmount": 40.0,
                      "TaxAmount": 0.0, "LineAmount": 40.0, "Balance": 0.0, "Product2": None,
                      "InvoiceId": "3ttOTHER"})
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 290.0})
    # The platform applied 40 of this payment to the other invoice at its post.
    org.payment_apps.append({"Id": "1AlOTHER", "Amount": 40.0, "level": "line",
                             "payment": "0aQ1", "invoice": "3ttOTHER"})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=290.0))
    m = _posted_manifest(payment_ids=["0aQ1"], payment_amount=290.0,
                         payment_apply_target=250.0, payment_mode="over",
                         settlement_baseline={"balance": 250.0, "decimal_places": 2})
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert _applies(org) == [("5TV1", 100.0), ("5TV2", 150.0)]
    assert "1AlOTHER" not in m.payment_application_ids
    assert m.payment_amount_applied == 250.0


def test_baseline_records_platform_applications(billable_account) -> None:
    org = SettleOrg("line")
    org.lines[0]["Balance"] = 60.0
    org.invoice["NetPaymentsApplied"] = 40.0
    org.payment_apps.append({"Id": "1AlAUTO", "Amount": 40.0, "level": "line",
                             "payment": "0aQOLD", "invoice": "3ttINV"})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.settlement_baseline["net_payments_applied"] == 40.0
    assert m.settlement_baseline["foreign_payment_application_ids"] == ["1AlAUTO"]
    assert m.payment_amount == 210.0  # the open balance after the platform's 40
    assert "1AlAUTO" not in m.payment_application_ids
    assert any("applied by the platform at post" in w for w in m.settlement_warnings)


def test_credit_waits_through_pending(billable_account) -> None:
    org = SettleOrg("line")
    org.memo_statuses = ["Pending", "Pending", "Posted"]
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.credit_memo_ids == ["50g1"]
    assert m.credit_amount_applied == 20.0


def test_accepted_credit_not_yet_visible_is_polled_not_reposted(billable_account) -> None:
    org = SettleOrg("line")
    org.memo_visible_after = 3
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    # The first attempt POSTed and recorded it, then failed before the memo
    # showed up; the retry must poll, not POST again.
    org._do_post("/services/data/v68.0/commerce/invoicing/invoices/3ttINV/actions/credit",
                 lifecycle.build_credit_payload([("5TV1", 20.0)], "RUN", {"5TV1": "Ignore"}))
    m = steps.run_credit(ctx, _posted_manifest(credit_submitted=True,
                                               settlement_baseline={"balance": 250.0}))
    assert org.posts == []
    assert m.credit_memo_ids == ["50g1"]
    assert len(org.memos) == 1


def test_another_runs_memo_on_the_invoice_is_not_reused(billable_account) -> None:
    org = SettleOrg("line")
    org.memos.append({"Id": "50gOTHER", "ReferenceEntityId": "3ttINV",
                      "Description": "OTHER-RUN credit", "Status": "Posted", "Balance": 0.0})
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert len([p for p in org.posts if p[0].endswith("/actions/credit")]) == 1
    assert m.credit_memo_ids == ["50g2"]


def test_another_runs_payment_on_the_account_is_not_reused(billable_account) -> None:
    org = SettleOrg("line")
    org.payments.append({"Id": "0aQOTHER", "AccountId": billable_account.id,
                         "GatewayRefNumber": "OTHER-RUN-PAY", "Amount": 50.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=10.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.payment_ids == ["0aQ2"]


def test_credit_post_failure_that_committed_is_not_resent(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    exc = SfApiError(503, "unavailable", "POST", "/credit")
    exc._commit_first = True
    org.fail_next_post = exc
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert len(org.memos) == 1 and m.credit_memo_ids == ["50g1"]
    assert m.credit_submitted is True


def test_credit_post_failure_without_memo_raises_for_retry(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(503, "unavailable", "POST", "/credit")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError) as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert isinstance(info.value.__cause__, SfApiError)
    assert info.value.failure_class == "deterministic"
    assert "cli step --manifest RUN --to-stage credit_applied" in str(info.value)
    assert "never sent again" in str(info.value) and "start a new run" in str(info.value)
    # Recorded before the POST, so no retry or resume POSTs it again.
    assert m.credit_submitted is True and org.memos == []


def test_credit_refusal_becomes_lifecycle_error(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(
        400,
        '{"enhancedErrorType":"RecordError","message":"Couldn&#39;t create credit memo.",'
        '"output":{"errors":[{"errorCode":"INVALID_API_INPUT","message":"To calculate tax, '
        'the invoice line must have a tax line."}],"success":false}}',
        "POST", "/credit",
    )
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(LifecycleError, match="To calculate tax, the invoice line must have a tax line"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())


def test_payment_retry_applies_only_the_remainder(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    real = org._do_post
    calls = {"n": 0}

    def flaky(path, body):
        if path.endswith("/actions/apply"):
            calls["n"] += 1
            if calls["n"] == 2:
                raise SfApiError(503, "unavailable", "POST", path)
        return real(path, body)

    org._do_post = flaky
    m = _posted_manifest()
    with pytest.raises(SfApiError):
        steps.run_payment(ctx, m)
    assert m.payment_ids == ["0aQ1"] and m.payment_apply_target == 250.0

    org._do_post = real
    org.posts.clear()
    m = steps.run_payment(ctx, m)
    assert len(org.payments) == 1
    assert _applies(org) == [("5TV2", 150.0)]
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


def test_zero_decimal_currency_rounds_to_whole_units(billable_account) -> None:
    org = SettleOrg("line", places=0)
    org.invoice["CurrencyIsoCode"] = "JPY"
    org.lines[0].update(ChargeAmount=1001.0, LineAmount=1001.0, Balance=1001.0)
    spec = SettlementSpec(application_level="line", credit=CreditSpec(percent=15.0, lines=[0]),
                          payment=PaymentSpec(percent=33.0))
    ctx = _settle_ctx(org, billable_account, spec)
    m = steps.run_payment(ctx, steps.run_credit(ctx, _posted_manifest()))
    assert m.settlement_baseline["decimal_places"] == 0
    assert org.posts[0][1]["invoiceLines"][0]["amountToCredit"] == 150.0  # 150.15 -> 150
    assert m.payment_amount == 330.0  # 33% of (851 + 150) = 330.33 -> 330
    assert org.payments[0]["CurrencyIsoCode"] == "JPY"


def test_credit_step_is_a_noop_without_its_block(billable_account) -> None:
    """A payment-only scenario passes through credit_applied."""
    org = SettleOrg("line")
    m = steps.run_credit(_settle_ctx(org, billable_account, None), _posted_manifest())
    assert org.posts == [] and m.reached_stage == "credit_applied"


def test_payment_step_refuses_without_a_payment_block(billable_account) -> None:
    """payment_applied is never reached with nothing written: a manifest that
    reached it could not be given a payment afterwards."""
    org = SettleOrg("line")
    m = _posted_manifest(reached_stage="credit_applied")
    with pytest.raises(LifecycleError,
                       match="cli step --manifest RUN --to-stage payment_applied --config") as info:
        steps.run_payment(_settle_ctx(org, billable_account, None), m)
    assert info.value.failure_class == "deterministic"
    assert org.posts == [] and m.reached_stage == "credit_applied"


def test_settlement_falls_back_to_the_manifest_on_resume(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=25.0))
    m = steps.run_payment(
        _settle_ctx(org, billable_account, None), _posted_manifest(settlement=spec.to_dict())
    )
    assert m.payment_amount == 25.0


def test_credit_only_manifest_resumed_to_payment_is_refused(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(percent=10.0))
    m = _posted_manifest(settlement=json.loads(json.dumps(spec.to_dict())),
                         reached_stage="credit_applied")
    with pytest.raises(LifecycleError, match="recorded settlement block is fixed; start a new run"):
        steps.run_payment(_settle_ctx(org, billable_account, None), m)
    assert org.payments == [] and m.reached_stage == "credit_applied"


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
    assert _settlement_for_step(
        args, Manifest(run_id="X", settlement={"payment": {"amount": "exact"}})) is None
    # A recorded block without a payment cannot reach payment_applied: refused
    # before any step runs.
    with pytest.raises(LifecycleError, match="has no 'payment' and is fixed"):
        _settlement_for_step(args, Manifest(run_id="X", settlement={"credit": {"amount": 1}}))
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
            "settlement": {"credit": {"amount": 1}, "payment": {"amount": 1}},
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
    assert m.settlement is None  # the stubbed steps never started a settlement step


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


@pytest.mark.parametrize("target", ["invoice_posted", "credit_applied", "payment_applied"])
def test_taxable_ingestion_with_settlement_target_builds_tax_record(fake_client, target) -> None:
    """Settlement targets ingest Posted, so a taxable line needs its
    InvoiceLineTax record exactly as for invoice_posted."""
    from datetime import date

    from scripts.txn_data_harness.config import InvoiceLineSpec, ScenarioTaxDefaults
    from scripts.txn_data_harness.handlers.invoice_ingestion import _resolve_invoice_line

    line = _resolve_invoice_line(
        fake_client,
        InvoiceLineSpec(name="Taxed", quantity=1, unit_price=100.0, taxable=True),
        line_index=0,
        target_stage=target,
        run_id="RUN",
        tax_defaults=ScenarioTaxDefaults(rate=0.1, name="Sales Tax", code="TX"),
        invoice_date=date(2026, 11, 25),
    )
    assert line.tax is not None
    assert line.tax.amount == pytest.approx(10.0)


def test_taxable_settlement_config_parses() -> None:
    spec = _coerce_spec(
        {
            "kind": "invoice_ingestion",
            "target_stage": "payment_applied",
            "invoice_lines": [{"name": "L", "quantity": 1, "unit_price": 10, "taxable": True}],
            "tax": {"rate": 0.1, "name": "Sales Tax", "code": "TX"},
            "settlement": {"payment": "exact"},
        },
        "t",
    )
    assert spec.invoice_lines[0].taxable


def test_settlement_concurrency_conflicts() -> None:
    from scripts.txn_data_harness.generate import settlement_concurrency_conflicts

    def r(acct, stage, count=1):
        return SimpleNamespace(account=SimpleNamespace(id=acct, name=acct),
                               spec=SimpleNamespace(count=count), effective_stage=stage)

    assert settlement_concurrency_conflicts([r("A", "payment_applied", 1)]) == []
    assert settlement_concurrency_conflicts([r("A", "payment_applied", 2)]) == ["A"]
    # A sibling on the same account that only posts can still absorb the payment.
    assert settlement_concurrency_conflicts(
        [r("A", "credit_applied"), r("A", "invoice_posted"), r("B", "invoice_posted", 5)]
    ) == ["A"]
    assert settlement_concurrency_conflicts([r("A", "invoice_posted", 3)]) == []


def test_currency_decimal_places_reads_once_and_defaults(fake_client) -> None:
    fake_client.query_responses = [[{"DecimalPlaces": 0}]]
    assert lifecycle.currency_decimal_places(fake_client, "JPY") == 0
    assert lifecycle.currency_decimal_places(fake_client, "JPY") == 0
    assert len(fake_client.queries) == 1
    assert lifecycle.currency_decimal_places(fake_client, None) == 2
    fake_client.query_responses = [[]]
    assert lifecycle.currency_decimal_places(fake_client, "XXX") == 2


def test_api_error_text_shapes() -> None:
    assert lifecycle.api_error_text('[{"errorCode":"X","message":"m"}]') == "X: m"
    body = ('{"message":"top","output":{"errors":[],"referenceLineErrorResults":'
            '[{"errors":[{"errorCode":"E","message":"Couldn&#39;t credit"}]}]}}')
    assert lifecycle.api_error_text(body) == "E: Couldn't credit"
    assert lifecycle.api_error_text('{"message":"only top"}') == "only top"
    assert lifecycle.api_error_text("not json") == "not json"


def _step_cfg(tmp_path, body: str) -> str:
    cfg = tmp_path / "step.yaml"
    cfg.write_text(body)
    return str(cfg)


def test_cli_step_matches_the_manifests_kind_and_account(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n"
        "  - {kind: sales_txn_quote, account: Infinitech, target_stage: payment_applied,\n"
        "     settlement: {payment: {amount: 10}}}\n"
        "  - {kind: invoice_ingestion, account: Infinitech, target_stage: payment_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}],\n"
        "     settlement: {payment: {amount: 20}}}\n"
        "  - {kind: invoice_ingestion, account: Global Media, target_stage: payment_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}],\n"
        "     settlement: {payment: {amount: 30}}}\n"
    ))
    args = SimpleNamespace(config=cfg, to_stage="payment_applied")
    m = Manifest(run_id="X", kind="invoice_ingestion", account_name="Infinitech")
    assert _settlement_for_step(args, m).payment.amount == 20.0
    m = Manifest(run_id="X", kind="sales_txn_quote", account_name="Infinitech")
    assert _settlement_for_step(args, m).payment.amount == 10.0


def test_cli_step_refuses_an_ambiguous_config(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "defaults: {kind: sales_txn_quote, target_stage: payment_applied}\n"
        "scenarios:\n"
        "  - {settlement: {payment: {amount: 10}}}\n"
        "  - {settlement: {payment: {amount: 20}}}\n"
    ))
    with pytest.raises(LifecycleError, match="2 different settlement blocks"):
        _settlement_for_step(
            SimpleNamespace(config=cfg, to_stage="payment_applied"),
            Manifest(run_id="X", kind="sales_txn_quote", account_name="Infinitech"),
        )


def test_cli_step_surfaces_config_errors(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n  - {target_stage: payment_applied, settlement: {payment: {amount: -1}}}\n"
    ))
    with pytest.raises(ConfigError, match="must be > 0"):
        _settlement_for_step(
            SimpleNamespace(config=cfg, to_stage="payment_applied"), Manifest(run_id="X")
        )


def test_cli_step_accepts_application_level_override() -> None:
    from scripts.txn_data_harness.cli import parse_args

    args = parse_args([
        "step", "--org", "o", "--manifest", "m", "--to-stage", "payment_applied",
        "--application-level", "line",
    ])
    assert args.application_level == "line"
    args = parse_args(["step", "--org", "o", "--manifest", "m", "--to-stage", "payment_applied"])
    assert args.application_level is None


# -- review round 2 (todo 275) ---------------------------------------------------


def _other_account():
    from scripts.txn_data_harness.discovery import Account

    return Account(id="001OTHER", name="Infinitech", billing_account_id="BA-2")


def _payment_planned_manifest(**kw):
    """A manifest whose payment was planned and created, but whose checkpoint
    after the create never landed (the Payment exists in the org only)."""
    return _posted_manifest(
        payment_amount=250.0, payment_apply_target=250.0, payment_mode="exact",
        settlement_baseline={"balance": 250.0, "decimal_places": 2}, **kw,
    )


def test_payment_resume_under_another_account_is_refused(billable_account) -> None:
    """A resume whose account name resolves to another Id must not find-or-create
    a payment under that account (a second payment for the invoice)."""
    org = SettleOrg("line")
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 250.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    with pytest.raises(LifecycleError, match="resolves to 001OTHER.*belong to account 001BILLABLE"):
        steps.run_payment(_settle_ctx(org, _other_account(), spec),
                          _payment_planned_manifest(account_id=billable_account.id))
    assert len(org.payments) == 1 and org.posts == []
    with pytest.raises(LifecycleError, match="resolves to 001OTHER"):
        steps.run_credit(
            _settle_ctx(org, _other_account(),
                        SettlementSpec(application_level="line", credit=CreditSpec(amount=5.0))),
            _posted_manifest(),
        )
    assert org.posts == []


def test_payment_uses_the_invoice_account_and_finds_a_committed_payment(billable_account) -> None:
    """Kills: dropping find_payment (a committed-but-unrecorded Payment is
    created again)."""
    org = SettleOrg("line")
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 250.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _payment_planned_manifest())
    assert len(org.payments) == 1 and m.payment_ids == ["0aQ1"]
    assert m.account_id == billable_account.id
    assert m.payment_amount_applied == 250.0


def test_manifest_account_disagreeing_with_the_invoice_is_refused(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    with pytest.raises(LifecycleError, match="invoice belongs to account 001BILLABLE"):
        steps.run_payment(_settle_ctx(org, billable_account, spec),
                          _posted_manifest(account_id="001ELSE"))
    assert org.posts == []


def test_cli_step_resolves_the_manifests_account_by_id(monkeypatch) -> None:
    from scripts.txn_data_harness import cli as cli_mod

    seen = []

    def fake_resolve(client, name, *, account_id=None):
        seen.append((name, account_id))
        return SimpleNamespace(id=account_id or "001BYNAME", name=name)

    monkeypatch.setattr(cli_mod, "resolve_account", fake_resolve)
    m = Manifest(run_id="R", account_id="001REC", account_name="Infinitech")
    acct = cli_mod._resolve_step_account(None, SimpleNamespace(account=None), m)
    assert acct.id == "001REC" and seen[-1] == ("Infinitech", "001REC")
    from scripts.txn_data_harness import discovery

    monkeypatch.setattr(discovery, "account_ids_named", lambda c, name: ["001BYNAME"])
    with pytest.raises(LifecycleError, match="--account 'Infinitech' resolves to 001BYNAME"):
        cli_mod._resolve_step_account(None, SimpleNamespace(account="Infinitech"), m)
    # Names are not unique: the manifest's account among them is accepted.
    monkeypatch.setattr(discovery, "account_ids_named", lambda c, name: ["001OTHER", "001REC"])
    acct = cli_mod._resolve_step_account(None, SimpleNamespace(account="Infinitech"), m)
    assert acct.id == "001REC" and seen[-1] == ("Infinitech", "001REC")
    # Old manifests without an account_id still resolve by name.
    acct = cli_mod._resolve_step_account(
        None, SimpleNamespace(account=None), Manifest(run_id="R", account_name="Infinitech")
    )
    assert acct.id == "001BYNAME"


def test_three_decimal_currency_rounds_every_amount_to_three_places(billable_account) -> None:
    """KWD has 3 decimal places: config amounts, caps, Payment.Amount and apply
    amounts keep the third place (10.005 rounds to 10.0 at 2 places)."""
    org = SettleOrg("line", places=3)
    org.invoice["CurrencyIsoCode"] = "KWD"
    spec = _pst(target_stage="payment_applied", settlement={
        "application_level": "line", "credit": {"amount": 10.005, "lines": [0]}, "payment": "exact",
    }).settlement
    assert spec.credit.amount == 10.005
    ctx = _settle_ctx(org, billable_account, spec)
    m = steps.run_payment(ctx, steps.run_credit(ctx, _posted_manifest()))
    assert m.settlement_baseline["decimal_places"] == 3
    assert org.posts[0][1]["invoiceLines"][0]["amountToCredit"] == 10.005
    assert m.credit_amount_applied == 10.005
    assert org.payments[0]["Amount"] == 239.995
    assert org.payments[0]["CurrencyIsoCode"] == "KWD"
    assert _applies(org) == [("5TV1", 89.995), ("5TV2", 150.0)]
    assert m.payment_amount_applied == 239.995 and m.invoice_balance == 0.0
    line = {"Balance": 10.0051, "ChargeAmount": 20.0, "TaxAmount": 0.0, "LineAmount": 20.0}
    assert lifecycle.credit_capacity(line, "Ignore", 3) == 10.005


# transport: a refusal is a 4xx on both transports


def _cli_proc(stdout: str, rc: int):
    return SimpleNamespace(returncode=rc, stdout=stdout, stderr="")


_CLI_400 = (
    "HTTP/1.1 400\ndate: Wed, 25 Nov 2026 15:11:18 GMT\n"
    "content-type: application/json;charset=UTF-8\nx-request-id: abc\n"
    '[{"errorCode":"INVALID_FIELD","message":"Specify an InvoiceLineId as the appliedToId."}]\n'
)
_CLI_503 = "HTTP/1.1 503\ncontent-type: application/json\n[{\"errorCode\":\"SERVER_UNAVAILABLE\",\"message\":\"down\"}]\n"


def test_parse_cli_response() -> None:
    from scripts.txn_data_harness.auth import parse_cli_response

    status, body = parse_cli_response(_CLI_400)
    assert status == 400 and json.loads(body)[0]["errorCode"] == "INVALID_FIELD"
    assert parse_cli_response('HTTP/1.1 200\nvary: x\n{\n  "id": "1"\n}\n') == (200, '{\n  "id": "1"\n}')
    assert parse_cli_response("HTTP/1.1 204\nvary: x\n") == (204, "")
    assert parse_cli_response('{"id": "1"}') == (None, '{"id": "1"}')


def _client(transport: str):
    from scripts.txn_data_harness.auth import SfRestClient

    return SfRestClient(alias="a", access_token="t", instance_url="https://x.example",
                        transport=transport)


def _fake_requests(client, status: int, text: str):
    calls = []

    class _Session:
        def request(self, method, url, data=None):
            calls.append(url)
            return SimpleNamespace(status_code=status, text=text)

    client._local.session = _Session()
    return calls


@pytest.mark.parametrize("transport", ["cli", "requests"])
def test_refusals_are_told_from_server_errors_on_both_transports(transport, monkeypatch) -> None:
    from scripts.txn_data_harness import auth
    from scripts.txn_data_harness.auth import SfApiError

    client = _client(transport)

    def respond(status: int, cli_out: str, body: str):
        if transport == "cli":
            monkeypatch.setattr(auth.subprocess, "run",
                                lambda *a, **kw: _cli_proc(cli_out, 1))
        else:
            _fake_requests(client, status, body)

    body_400 = _CLI_400.split("\n", 4)[-1].strip()
    respond(400, _CLI_400, body_400)
    with pytest.raises(SfApiError) as info:
        lifecycle.submit_credit(client, "3ttINV", {"invoiceLines": []})
    assert info.value.status == 400 and lifecycle.is_api_refusal(info.value)
    with pytest.raises(LifecycleError, match="application level is likely wrong"):
        lifecycle.apply_payment(client, "0aQ1", {"appliedToId": "3ttINV", "amount": 1})

    respond(503, _CLI_503, '[{"errorCode":"SERVER_UNAVAILABLE","message":"down"}]')
    with pytest.raises(SfApiError) as info:
        lifecycle.submit_credit(client, "3ttINV", {"invoiceLines": []})
    assert info.value.status == 503 and not lifecycle.is_api_refusal(info.value)
    with pytest.raises(SfApiError):
        lifecycle.apply_payment(client, "0aQ1", {"appliedToId": "5TV1", "amount": 1})


def test_cli_transport_success_and_non_api_failure(monkeypatch) -> None:
    from scripts.txn_data_harness import auth
    from scripts.txn_data_harness.auth import SfApiError

    client = _client("cli")
    seen = []

    def run(args, **kw):
        seen.append(args)
        return _cli_proc('HTTP/1.1 201\ncontent-type: application/json\n{"id":"0aQ1","success":true}\n', 0)

    monkeypatch.setattr(auth.subprocess, "run", run)
    assert client.post("/services/data/v68.0/sobjects/Payment", {"a": 1}) == {"id": "0aQ1", "success": True}
    assert "--include" in seen[0]
    monkeypatch.setattr(auth.subprocess, "run",
                        lambda *a, **kw: SimpleNamespace(returncode=1, stdout="", stderr="No authorization"))
    with pytest.raises(SfApiError) as info:
        client.get("/services/data/v68.0/limits")
    assert info.value.status == 1 and not lifecycle.is_api_refusal(info.value)


def test_cli_step_records_api_errors_on_the_manifest(monkeypatch, billable_account) -> None:
    from argparse import Namespace

    from scripts.txn_data_harness import cli as cli_mod
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.discovery import OrgContext

    m = _posted_manifest(account_id=billable_account.id,
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    written = []
    monkeypatch.setattr(cli_mod, "load_manifest", lambda ref: m)
    monkeypatch.setattr(cli_mod, "write_manifest", lambda mm: written.append(mm.error))
    monkeypatch.setattr(cli_mod.SfRestClient, "from_alias", lambda *a, **kw: object())
    monkeypatch.setattr(cli_mod, "resolve_account", lambda *a, **kw: billable_account)
    monkeypatch.setattr(cli_mod, "discover", lambda *a, **kw: OrgContext(
        pricebook_id=None, pricebook_name=None, legal_entity_id=None, legal_entity_name=None,
        opportunity_stage=None, billing_ready_accounts=[], products=[]))

    def boom(step, ctx, manifest):
        raise SfApiError(503, "unavailable", "POST", "/x")

    monkeypatch.setattr(cli_mod, "execute_step", boom)
    args = Namespace(org="o", api_version="68.0", transport="cli", manifest="RUN", account=None,
                     product=None, opportunity_stage=None, with_opportunity=False,
                     to_stage="credit_applied", poll_timeout=1, config=None,
                     application_level=None)
    with pytest.raises(SfApiError):
        cli_mod._cmd_step(args)
    assert m.error and "SfApiError" in m.error and "503" in m.error
    assert written[-1] == m.error


# invoice header / currency reads


class _FlakyClient:
    instance_url = "https://flaky.example"
    api_version = "68.0"

    def __init__(self, *responses):
        self.responses = list(responses)
        self.queries = []

    def query(self, soql):
        self.queries.append(soql)
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def test_invoice_header_retries_without_currency_only_when_the_column_is_missing() -> None:
    from scripts.txn_data_harness.auth import SfApiError

    def invalid_field(column: str) -> SfApiError:
        # The real message echoes the SOQL, which names CurrencyIsoCode
        # whichever column is missing (measured shape, 2026-11-25).
        soql = ("SELECT Id, Status, BillingAccountId, Balance, SettlementLevel, "
                "CurrencyIsoCode FROM Invoice WHERE Id = '3tt'")
        msg = (f"\\n{soql}\\n       ^\\nERROR at Row:1:Column:8\\nNo such column "
               f"'{column}' on entity 'Invoice'. If you are attempting to use a custom "
               "field, be sure to append the '__c' after the custom field name.")
        return SfApiError(400, json.dumps([{"message": msg, "errorCode": "INVALID_FIELD"}]),
                          "GET", "/q")

    c = _FlakyClient(invalid_field("SettlementLevel"), [{"Id": "3tt"}])
    with pytest.raises(SfApiError):
        lifecycle.fetch_invoice_header(c, "3tt")
    missing = invalid_field("CurrencyIsoCode")
    c = _FlakyClient(missing, [{"Id": "3tt", "Balance": 5}])
    assert lifecycle.fetch_invoice_header(c, "3tt")["Id"] == "3tt"
    assert "CurrencyIsoCode" not in c.queries[1]
    c = _FlakyClient(SfApiError(503, "unavailable", "GET", "/q"), [{"Id": "3tt"}])
    with pytest.raises(SfApiError):
        lifecycle.fetch_invoice_header(c, "3tt")
    assert len(c.queries) == 1


def test_transient_currency_errors_raise_and_are_not_cached() -> None:
    from scripts.txn_data_harness.auth import SfApiError

    c = _FlakyClient(SfApiError(503, "unavailable", "GET", "/q"), [{"DecimalPlaces": 3}])
    with pytest.raises(SfApiError):
        lifecycle.currency_decimal_places(c, "KWD")
    assert lifecycle.currency_decimal_places(c, "KWD") == 3
    c = _FlakyClient(SfApiError(400, '[{"errorCode":"INVALID_TYPE","message":"x"}]', "GET", "/q"),
                     [{"DecimalPlaces": 3}], SfApiError(400, '[{"errorCode":"INVALID_TYPE"}]', "GET", "/q"))
    assert lifecycle.currency_decimal_places(c, "EUR") == 2  # ISO 4217 fallback, not cached
    assert lifecycle.currency_decimal_places(c, "EUR") == 3  # read, so it was not cached
    assert lifecycle.currency_decimal_places(c, "JPY") == 0  # ISO 4217 fallback


def test_transient_header_error_does_not_record_a_baseline(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    real = org.query

    def flaky(soql):
        if soql.startswith("SELECT Id, Status, BillingAccountId") and "CurrencyIsoCode" in soql:
            raise SfApiError(503, "unavailable", "GET", "/q")
        return real(soql)

    org.query = flaky
    m = _posted_manifest()
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=5.0))
    with pytest.raises(SfApiError):
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert m.settlement_baseline is None and org.posts == []


# config: a target before the settlement block's stages


def test_config_keeps_a_settlement_block_not_reached_yet() -> None:
    both = {"credit": {"amount": 1}, "payment": {"amount": 1}}
    for stage in ("invoice_draft", "invoice_posted", "credit_applied"):
        spec = _pst(target_stage=stage, settlement=both)
        assert spec.settlement.credit.amount == 1.0 and spec.settlement.payment.amount == 1.0


def test_recipe_run_to_invoice_posted_then_step_to_payment(tmp_path, billable_account) -> None:
    """The documented recipe: `cli run --target-stage invoice_posted` on a
    settlement config (no block is recorded: no settlement step ran), then
    `cli step --to-stage payment_applied --config <file>`."""
    from scripts.txn_data_harness.cli import _settlement_for_step

    m = _posted_manifest(kind="sales_txn_quote", application_level="line")
    assert m.settlement is None
    with pytest.raises(LifecycleError, match="needs settlement options"):
        _settlement_for_step(SimpleNamespace(config=None, to_stage="payment_applied"), m)
    cfg = _step_cfg(tmp_path, (
        "scenarios:\n"
        "  - {kind: sales_txn_quote, account: Infinitech, target_stage: invoice_posted,\n"
        "     products: [{sku: QB-API-FLEX}],\n"
        "     settlement: {credit: {percent: 10}, payment: {amount: exact}}}\n"
    ))
    spec = _settlement_for_step(SimpleNamespace(config=cfg, to_stage="payment_applied"), m)
    assert SCENARIO_HANDLERS["sales_txn_quote"].remaining_steps(
        "invoice_posted", "payment_applied", False) == ["credit_applied", "payment_applied"]
    org = SettleOrg("line")
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.target_stage = "payment_applied"
    m = steps.run_payment(ctx, steps.run_credit(ctx, m))
    assert m.reached_stage == "payment_applied" and m.invoice_balance == 0.0
    assert m.credit_amount_applied == 25.0  # 10% of 250
    assert m.settlement["payment"] == {"amount": "exact", "percent": None, "lines": None}


def test_cli_step_reads_no_config_for_non_settlement_targets(monkeypatch, tmp_path) -> None:
    from scripts.txn_data_harness import cli as cli_mod

    monkeypatch.setattr(cli_mod, "load_scenarios",
                        lambda args: pytest.fail("--config must not be read for this target"))
    for stage in ("invoice_draft", "invoice_posted", "order_activated"):
        args = SimpleNamespace(config=str(tmp_path / "old.yaml"), to_stage=stage)
        assert cli_mod._settlement_for_step(args, Manifest(run_id="OLD")) is None


def test_cli_step_to_invoice_posted_tolerates_a_config_without_settlement(
    monkeypatch, tmp_path, billable_account
) -> None:
    """An old ingestion manifest resumed to invoice_posted with a config whose
    scenario has no usable settlement block builds its context."""
    from scripts.txn_data_harness import cli as cli_mod

    cfg = _step_cfg(tmp_path, "scenarios:\n  - {target_stage: payment_applied}\n")
    args = SimpleNamespace(config=cfg, to_stage="invoice_posted", poll_timeout=1,
                           application_level=None)
    ctx = cli_mod._build_step_context(
        args, SCENARIO_HANDLERS["invoice_ingestion"], None, None, billable_account,
        Manifest(run_id="OLD", kind="invoice_ingestion"),
    )
    assert ctx.settlement is None


# one credit per run


def _failed_memo(status: str) -> dict:
    return {"Id": "50gBAD", "ReferenceEntityId": "3ttINV", "Description": "RUN credit",
            "Status": status, "Balance": 0.0, "_statuses": [status]}


def _submitted(**kw):
    return _posted_manifest(credit_submitted=True, application_level="line",
                            settlement_baseline={"balance": 250.0, "decimal_places": 2}, **kw)


@pytest.mark.parametrize("status", ["Error", "Canceled", "Voided"])
def test_failed_memo_means_a_new_run(status, billable_account) -> None:
    org = SettleOrg("line")
    org.memos.append(_failed_memo(status))
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(LifecycleError, match=f"credit memo in {status}. This run cannot settle; "
                                             "start a new run") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), _submitted())
    assert info.value.failure_class == "deterministic" and org.posts == []


def test_refused_credit_says_options_are_fixed(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(400, '[{"errorCode":"INVALID_API_INPUT","message":"bad"}]',
                                    "POST", "/credit")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError, match="Nothing was created. Rerunning sends the same "
                                             "credit again.*start a new run") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"
    assert m.credit_submitted is False


def test_recorded_block_is_fixed(tmp_path, billable_account) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step, parse_args

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n"
        "  - {kind: invoice_ingestion, account: Infinitech, target_stage: credit_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}],\n"
        "     settlement: {application_level: line, credit: {amount: 7}}}\n"
    ))
    m = _posted_manifest(settlement={"application_level": "line", "credit": {"amount": 999}})
    args = SimpleNamespace(config=cfg, to_stage="credit_applied")
    with pytest.raises(LifecycleError, match=r"differs .* in credit\.amount.*new run"):
        _settlement_for_step(args, m)
    # The steps read only the recorded block, whatever the context carries.
    org = SettleOrg("line")
    other = SettlementSpec(application_level="line", credit=CreditSpec(amount=7.0))
    m = _posted_manifest(settlement={"application_level": "line", "credit": {"amount": 30}})
    m = steps.run_credit(_settle_ctx(org, billable_account, other), m)
    assert org.posts[0][1]["invoiceLines"][0]["amountToCredit"] == 30.0
    assert m.settlement["credit"]["amount"] == 30
    with pytest.raises(SystemExit):
        parse_args(["step", "--org", "o", "--manifest", "m", "--to-stage", "credit_applied",
                    "--resubmit-credit"])


# mutation guards


def test_generate_refuses_a_parallel_settlement_batch_on_one_account(monkeypatch, capsys) -> None:
    from scripts.txn_data_harness import generate

    resolved = [SimpleNamespace(account=SimpleNamespace(id="001A", name="Infinitech"),
                                spec=SimpleNamespace(count=2, kind="sales_txn_quote",
                                                     target_stage="payment_applied"),
                                effective_stage="payment_applied")]
    handler = SimpleNamespace(resolve=lambda client, ctx, s: resolved[0])
    monkeypatch.setattr(generate.SfRestClient, "from_alias", lambda *a, **kw: object())
    monkeypatch.setattr(generate, "discover", lambda *a, **kw: object())
    monkeypatch.setattr(generate, "load_scenarios", lambda args: [resolved[0].spec])
    monkeypatch.setattr(generate, "SCENARIO_HANDLERS", {"sales_txn_quote": handler})
    monkeypatch.setattr(generate, "run_batch",
                        lambda *a, **kw: pytest.fail("a conflicting batch must not run"))
    assert generate.main(["--org", "o", "--concurrency", "2"]) == 4
    assert "needs --concurrency 1" in capsys.readouterr().err


def test_credit_post_failure_waits_for_a_late_memo(billable_account) -> None:
    """Kills: dropping the lookup wait after a failed credit POST (a memo that
    shows up a few reads later would be POSTed again on retry)."""
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.memo_visible_after = 3
    exc = SfApiError(503, "unavailable", "POST", "/credit")
    exc._commit_first = True
    org.fail_next_post = exc
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.poll_timeout = 30
    m = steps.run_credit(ctx, _posted_manifest())
    assert len(org.memos) == 1 and m.credit_memo_ids == ["50g1"] and m.credit_submitted


def test_only_charge_lines_are_credited_or_paid(billable_account) -> None:
    """Kills: dropping `AND Type = 'Charge'` (a tax line would take part of
    the credit and the payment)."""
    org = SettleOrg("line")
    org.lines.insert(0, {"Id": "5TV0", "Name": "Tax", "Type": "Tax", "ChargeAmount": 25.0,
                         "TaxAmount": 0.0, "LineAmount": 25.0, "Balance": 25.0,
                         "Product2": None, "InvoiceId": "3ttINV"})
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=30.0),
                          payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    m = steps.run_payment(ctx, steps.run_credit(ctx, _posted_manifest(invoice_line_ids=[])))
    assert org.posts[0][1]["invoiceLines"] == [
        {"invoiceLineId": "5TV1", "amountToCredit": 30.0, "taxStrategy": "Ignore"}]
    assert _applies(org) == [("5TV1", 70.0), ("5TV2", 150.0)]
    assert m.payment_amount == 220.0


def test_payment_plan_is_checkpointed_before_the_payment_insert(billable_account) -> None:
    """Kills: dropping the checkpoint after planning. A crash after the insert
    must leave the plan on disk, or a resume replans against the balance the
    payment already changed."""
    org = SettleOrg("line")
    saved: list[dict] = []
    real = org._do_post

    def check(path, body):
        if path.endswith("/sobjects/Payment"):
            assert saved, "nothing checkpointed before the Payment insert"
            assert saved[-1]["payment_apply_target"] == 250.0
            assert saved[-1]["payment_amount"] == body["Amount"]
        return real(path, body)

    org._do_post = check
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.checkpoint = lambda mm: saved.append(json.loads(json.dumps(mm.to_dict())))
    steps.run_payment(ctx, _posted_manifest())
    assert org.payments


def test_payment_create_that_committed_then_failed_is_not_created_twice(billable_account) -> None:
    """A 5xx after the insert committed: the payment is looked up by its tag
    (short wait) instead of inserted again."""
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    exc = SfApiError(500, "internal", "POST", "/sobjects/Payment")
    exc._commit_first = True
    org.fail_next_post = exc
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert len(org.payments) == 1 and m.payment_ids == ["0aQ1"] and m.payment_submitted
    assert m.payment_amount_applied == 250.0


def test_apply_that_committed_then_failed_is_not_applied_twice(billable_account) -> None:
    """Kills: ignoring what is already applied when computing the remainder.
    A partial payment, so the line balances alone do not cap the re-apply."""
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=120.0))
    ctx = _settle_ctx(org, billable_account, spec)
    real = org._do_post
    calls = {"n": 0}

    def commit_then_fail(path, body):
        result = real(path, body)
        if path.endswith("/actions/apply"):
            calls["n"] += 1
            if calls["n"] == 1:
                raise SfApiError(500, "internal", "POST", path)
        return result

    org._do_post = commit_then_fail
    m = _posted_manifest()
    with pytest.raises(SfApiError):
        steps.run_payment(ctx, m)
    org.posts.clear()
    m = steps.run_payment(ctx, m)
    assert _applies(org) == [("5TV2", 20.0)]
    assert m.payment_amount_applied == 120.0 and m.invoice_balance == 130.0
    assert sum(a["Amount"] for a in org.payment_apps) == 120.0
    assert len(org.payments) == 1


# -- review round 3 (todo 275): one credit POST per attempt -------------------------


def test_handler_does_not_resend_a_credit_whose_post_committed_late(
    billable_account, org_context, monkeypatch
) -> None:
    """A credit POST that commits but answers 5xx, with the memo showing up only
    after the lookup wait: the scenario retry must not POST again, and the
    stage must not report success."""
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.handlers import invoice_ingestion as mod
    from scripts.txn_data_harness.models import ResolvedInvoiceIngestionSpec

    org = SettleOrg("line")
    org.memo_visible_after = 10 ** 9  # committed, not visible during this run
    exc = SfApiError(503, "unavailable", "POST", "/credit")
    exc._commit_first = True
    org.fail_next_post = exc

    def execute(step, ctx, manifest):
        if step == "ingest_invoice":
            manifest.invoice_id = "3ttINV"
            manifest.reached_stage = "invoice_posted"
            return manifest
        if step == "promote_to_posted":
            return manifest
        return steps.execute_step(step, ctx, manifest)

    monkeypatch.setattr(mod, "execute_step", execute)
    monkeypatch.setattr(mod, "write_manifest", lambda m: None)
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    spec = _coerce_spec({
        "kind": "invoice_ingestion", "target_stage": "payment_applied",
        "invoice_lines": [{"name": "L", "quantity": 1, "unit_price": 10}],
        "settlement": {"application_level": "line", "credit": {"amount": 20},
                       "payment": {"amount": 10}},
    }, "t")
    resolved = ResolvedInvoiceIngestionSpec(
        spec=spec, account=billable_account, invoice_lines=[], invoice_overrides=None,
        effective_stage="payment_applied",
    )
    m = SCENARIO_HANDLERS["invoice_ingestion"].run(
        org, org_context, "RUN", resolved, poll_timeout=1, max_retries=3
    )
    credit_posts = [p for p, _, _ in org.posts if p.endswith("/actions/credit")]
    assert len(credit_posts) == 1 and len(org.memos) == 1
    assert m.attempts == 1 and m.failure_class == "deterministic"
    assert m.reached_stage == "invoice_posted" and m.credit_submitted is True
    assert "never sent again" in m.error
    # A resume once the memo is visible adopts it without a POST.
    org.memos[0]["_visible_after"] = 0
    org.posts.clear()
    m = steps.run_credit(_settle_ctx(org, billable_account, spec.settlement), m)
    assert org.posts == [] and m.credit_memo_ids == ["50g1"] and m.reached_stage == "credit_applied"


def test_unknown_credit_outcome_is_never_classified_transient() -> None:
    from scripts.txn_data_harness.failure import classify_exception

    err = LifecycleError("credit", "HTTP 503 timed out", failure_class="deterministic")
    assert classify_exception(err) == "deterministic"
    assert classify_exception(LifecycleError("credit", "HTTP 503 timed out")) == "transient"


def test_a_second_credit_on_the_invoice_fails_the_stage(billable_account) -> None:
    org = SettleOrg("line")
    real = org._post_memo

    def post_with_duplicate(memo):
        real(memo)
        if not any(a["Id"] == "4sGDUP" for a in org.credit_apps):
            org.credit_apps.append({"Id": "4sGDUP", "Amount": 20.0, "level": "line",
                                    "memo": "50gDUP", "invoice": "3ttINV"})

    org._post_memo = post_with_duplicate
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError, match="NetCreditsApplied rose by 40.0.*applied 20.0") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"
    assert m.reached_stage == "invoice_posted"


def test_platform_credits_before_the_baseline_do_not_trip_the_check(billable_account) -> None:
    org = SettleOrg("line")
    org.invoice["NetCreditsApplied"] = 10.0  # applied at post, before settlement
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.settlement_baseline["net_credits_applied"] == 10.0
    assert m.reached_stage == "credit_applied"


# --config on a manifest that has a settlement block


def _cfg_block(tmp_path, block: str, stage: str = "credit_applied") -> str:
    return _step_cfg(tmp_path, (
        "scenarios:\n"
        f"  - {{kind: invoice_ingestion, account: Infinitech, target_stage: {stage},\n"
        "     invoice_lines: [{name: L, unit_price: 5}],\n"
        f"     settlement: {block}}}\n"
    ))


def test_config_never_adds_to_a_recorded_block(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _cfg_block(tmp_path, "{application_level: line, credit: {amount: 5}, payment: exact}")
    args = SimpleNamespace(config=cfg, to_stage="payment_applied")
    m = _posted_manifest(settlement={"application_level": "line", "credit": {"amount": 5}})
    with pytest.raises(LifecycleError, match="differs .* in payment.*new run"):
        _settlement_for_step(args, m)
    # Run to credit_applied only: the payment part is not part of the comparison.
    args.to_stage = "credit_applied"
    assert _settlement_for_step(args, m) is None


@pytest.mark.parametrize(
    "block, stage, keys",
    [
        ("{application_level: header, credit: {amount: 5}}", "credit_applied", "application_level"),
        ("{application_level: line, credit: {amount: 6}}", "credit_applied", "credit.amount"),
        ("{application_level: line, credit: {amount: 5, lines: [1]}, payment: {amount: 9}}",
         "payment_applied", "credit.lines, payment"),
    ],
)
def test_config_differences_are_refused_by_name(block, stage, keys, tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    args = SimpleNamespace(config=_cfg_block(tmp_path, block), to_stage=stage)
    m = _posted_manifest(settlement={"application_level": "line", "credit": {"amount": 5}})
    with pytest.raises(LifecycleError, match=re.escape(keys)):
        _settlement_for_step(args, m)


def test_identical_config_uses_the_manifest_block(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    args = SimpleNamespace(config=_cfg_block(tmp_path, "{application_level: line, credit: {amount: 5}}"),
                           to_stage="credit_applied")
    m = _posted_manifest(settlement={"application_level": "line", "credit": {"amount": 5}})
    assert _settlement_for_step(args, m) is None


def test_config_matches_a_renamed_account_by_id(tmp_path, fake_client) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n"
        "  - {kind: invoice_ingestion, account: New Name, target_stage: payment_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}], settlement: {payment: {amount: 20}}}\n"
    ))
    args = SimpleNamespace(config=cfg, to_stage="payment_applied")
    m = Manifest(run_id="X", kind="invoice_ingestion", account_name="Old Name",
                 account_id="001REC")
    fake_client.query_responses = [[{"Id": "001OTHER"}, {"Id": "001REC"}]]
    assert _settlement_for_step(args, m, fake_client).payment.amount == 20.0
    assert "Name = 'New Name'" in fake_client.queries[0]
    fake_client.query_responses = [[{"Id": "001OTHER"}]]
    with pytest.raises(LifecycleError, match="has no scenario"):
        _settlement_for_step(args, m, fake_client)


# BillingSettings read goes through the client's transport


def test_billing_settings_read_on_cli_sends_no_token(monkeypatch) -> None:
    from pathlib import Path

    from scripts.txn_data_harness import auth

    client = auth.SfRestClient(alias="a", access_token="SECRET", instance_url="https://x.example",
                               transport="cli")
    seen = []

    def run(args, **kw):
        seen.append(args)
        target = Path(args[args.index("--target-metadata-dir") + 1])
        if "--unzip" not in args:  # sf leaves only the zip without --unzip
            (target / "unpackaged.zip").write_bytes(b"PK\x05\x06" + b"\0" * 18)
            return SimpleNamespace(returncode=0, stdout="{}", stderr="")
        out = target / "unpackaged" / "settings"
        out.mkdir(parents=True)
        (out / "Billing.settings").write_text(
            "<BillingSettings><enableTransactionsApplicationToInvoices>true"
            "</enableTransactionsApplicationToInvoices></BillingSettings>")
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(auth.subprocess, "run", run)
    monkeypatch.setattr(auth.requests.Session, "post",
                        lambda *a, **kw: pytest.fail("cli transport must not POST from Python"))
    assert lifecycle._read_billing_settings_level(client) == "header"
    assert seen[0][:3] == ["sf", "project", "retrieve"]
    assert not any("SECRET" in a for a in seen[0])


def test_billing_settings_read_on_requests_uses_the_session() -> None:
    from scripts.txn_data_harness import auth

    client = auth.SfRestClient(alias="a", access_token="T", instance_url="https://x.example")
    calls = []

    class _Session:
        def post(self, url, data=None, headers=None, timeout=None):
            calls.append((url, data))
            return SimpleNamespace(status_code=200, text=(
                "<x><enableTransactionsApplicationToInvoices>false"
                "</enableTransactionsApplicationToInvoices></x>"))

    client._local.session = _Session()
    assert lifecycle._read_billing_settings_level(client) == "line"
    assert calls[0][0] == "https://x.example/services/Soap/m/68.0"


# -- review round 4 (todo 275) --------------------------------------------------


def _step_args(**kw):
    from argparse import Namespace

    base = dict(org="o", api_version="68.0", transport="requests", manifest="RUN", account=None,
                product=None, opportunity_stage=None, with_opportunity=False,
                to_stage="payment_applied", poll_timeout=1, config=None,
                application_level=None)
    return Namespace(**{**base, **kw})


def _patch_cmd_step(monkeypatch, manifest, billable_account):
    from scripts.txn_data_harness import cli as cli_mod
    from scripts.txn_data_harness.discovery import OrgContext

    ran = []
    monkeypatch.setattr(cli_mod, "load_manifest", lambda ref: manifest)
    monkeypatch.setattr(cli_mod, "write_manifest", lambda m: None)
    monkeypatch.setattr(cli_mod.SfRestClient, "from_alias", lambda *a, **kw: None)
    monkeypatch.setattr(cli_mod, "resolve_account", lambda *a, **kw: billable_account)
    monkeypatch.setattr(cli_mod, "discover", lambda *a, **kw: OrgContext(
        pricebook_id=None, pricebook_name=None, legal_entity_id=None, legal_entity_name=None,
        opportunity_stage=None, billing_ready_accounts=[], products=[]))

    def execute(step, ctx, m):
        ran.append((step, ctx.settlement))
        m.reached_stage = step
        return m

    monkeypatch.setattr(cli_mod, "execute_step", execute)
    return cli_mod, ran


def test_terminal_manifest_never_reruns_a_stage(monkeypatch, tmp_path, billable_account) -> None:
    """A manifest that reached its target runs nothing, and a --config that
    differs from its block is refused rather than ignored."""
    m = _posted_manifest(account_id=billable_account.id, reached_stage="payment_applied",
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    cfg = _cfg_block(tmp_path, "{application_level: line, credit: {amount: 5}, payment: exact}")
    with pytest.raises(LifecycleError, match="differs .* in payment"):
        cli_mod._cmd_step(_step_args(config=cfg))
    assert cli_mod._cmd_step(_step_args()) == 0 and ran == []


def test_config_on_a_terminal_manifest_is_never_ignored(monkeypatch, tmp_path, billable_account) -> None:
    m = _posted_manifest(account_id=billable_account.id, reached_stage="payment_applied",
                         payment_ids=["0aQ1"], payment_apply_target=250.0,
                         settlement={"application_level": "line", "payment": {"amount": "exact"}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    differs = _cfg_block(tmp_path, "{application_level: line, payment: {amount: 9}}", "payment_applied")
    with pytest.raises(LifecycleError, match="differs .* in payment.amount"):
        cli_mod._cmd_step(_step_args(config=differs))
    same = _cfg_block(tmp_path, "{application_level: line, payment: exact}", "payment_applied")
    assert cli_mod._cmd_step(_step_args(config=same)) == 0 and ran == []


def test_credit_gain_below_the_applied_amount_also_fails(billable_account) -> None:
    org = SettleOrg("line")
    real = org._post_memo

    def post_then_reverse(memo):
        had = bool(memo.get("_allocs"))
        real(memo)
        if had:
            org.invoice["NetCreditsApplied"] -= 10.0

    org._post_memo = post_then_reverse
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(LifecycleError, match="rose by 10.0 .* applied 20.0"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())


@pytest.mark.parametrize("answer", [
    {"success": False, "errors": [{"message": "?"}]},
    {"_raw": "not json"},
])
def test_a_2xx_without_success_keeps_the_credit_submitted(answer, billable_account) -> None:
    org = SettleOrg("line")
    real = org._do_post

    def accepted_oddly(path, body):
        if path.endswith("/actions/credit"):
            org.posts.append((path, body, False))
            return answer
        return real(path, body)

    org.post = lambda path, body, retry=True: accepted_oddly(path, body)
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError, match="outcome unknown .*2xx without success") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"
    assert m.credit_submitted is True and len(org.posts) == 1


def test_crash_during_the_credit_post_leaves_submitted_on_disk(tmp_path, billable_account) -> None:
    from scripts.txn_data_harness.manifests import load_manifest, write_manifest

    org = SettleOrg("line")
    org.fail_next_post = KeyboardInterrupt()
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.checkpoint = lambda mm: write_manifest(mm, manifest_dir=tmp_path)
    with pytest.raises(KeyboardInterrupt):
        steps.run_credit(ctx, _posted_manifest())
    on_disk = load_manifest(str(tmp_path / "RUN.json"))
    assert on_disk.credit_submitted is True and on_disk.credit_baseline == 0.0


def test_refusal_clears_submitted_on_disk(tmp_path, billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.manifests import load_manifest, write_manifest

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(400, '[{"errorCode":"INVALID_API_INPUT","message":"no"}]',
                                    "POST", "/credit")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.checkpoint = lambda mm: write_manifest(mm, manifest_dir=tmp_path)
    with pytest.raises(LifecycleError, match="credit refused"):
        steps.run_credit(ctx, _posted_manifest())
    assert load_manifest(str(tmp_path / "RUN.json")).credit_submitted is False


def test_two_memos_under_the_tag_fail(billable_account) -> None:
    org = SettleOrg("line")
    org.memos.append({**_failed_memo("Posted"), "Id": "50gONE"})
    org.memos.append({**_failed_memo("Pending"), "Id": "50gTWO"})
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(LifecycleError, match="2 credit memos carry this run's tag.*start a new run"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.posts == []


def test_billing_settings_retrieve_timeout_falls_back(monkeypatch) -> None:
    import subprocess

    from scripts.txn_data_harness import auth

    seen = {}

    def run(args, **kw):
        seen.update(args=args, kw=kw)
        raise subprocess.TimeoutExpired(args, kw.get("timeout"))

    monkeypatch.setattr(auth.subprocess, "run", run)

    class _Cli(auth.SfRestClient):
        def query(self, soql):
            assert "SettlementLevel" in soql
            return [{"SettlementLevel": "InvoiceLine"}]

    client = _Cli(alias="a", access_token="", instance_url="https://timeout.example", transport="cli")
    assert lifecycle.read_application_level(client) == ("line", "invoice_settlement_level")
    assert seen["kw"]["timeout"] == auth._RETRIEVE_TIMEOUT_S
    assert seen["args"][seen["args"].index("--wait") + 1] == str(auth._RETRIEVE_WAIT_MINUTES)


@pytest.mark.parametrize("code, places", [("JPY", 0), ("KWD", 3), ("USD", 2)])
def test_single_currency_org_uses_the_default_currency_minor_units(code, places, fake_client) -> None:
    fake_client.query_responses = [[{"DefaultCurrencyIsoCode": code}]]
    assert lifecycle.currency_decimal_places(fake_client, None) == places
    assert lifecycle.currency_decimal_places(fake_client, None) == places
    assert len(fake_client.queries) == 1  # cached once read


def test_single_currency_jpy_settles_in_whole_units(billable_account) -> None:
    org = SettleOrg("line", places=0)
    org.org_currency = "JPY"
    del org.invoice["CurrencyIsoCode"]
    org.lines[0].update(ChargeAmount=1001.0, LineAmount=1001.0, Balance=1001.0)
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(percent=33.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.settlement_baseline["decimal_places"] == 0
    assert org.payments[0]["Amount"] == 380.0  # 33% of 1151 = 379.83 -> 380
    assert "CurrencyIsoCode" not in org.payments[0]


@pytest.mark.parametrize("raw, msg", [
    ({"name": "L", "unit_price": float("nan")}, "unit_price must be a finite"),
    ({"name": "L", "unit_price": 1, "quantity": float("inf")}, "quantity must be a finite"),
    ({"name": "L", "unit_price": 1, "charge_amount": "nan"}, "charge_amount must be a finite"),
])
def test_invoice_line_numbers_must_be_finite(raw, msg) -> None:
    with pytest.raises(ConfigError, match=msg):
        _coerce_spec({"kind": "invoice_ingestion", "target_stage": "invoice_posted",
                      "invoice_lines": [raw]}, "t")


def test_discount_must_be_finite() -> None:
    with pytest.raises(ConfigError, match="discount must be a finite"):
        _pst(products=[{"sku": "X", "discount": float("nan")}])


def test_org_default_currency_absent_on_a_multi_currency_org() -> None:
    from scripts.txn_data_harness.auth import SfApiError

    missing = SfApiError(400, json.dumps([{"errorCode": "INVALID_FIELD", "message": (
        "\nSELECT DefaultCurrencyIsoCode FROM Organization\n       ^\nERROR at Row:1:Column:8\n"
        "No such column 'DefaultCurrencyIsoCode' on entity 'Organization'.")}]), "GET", "/q")
    assert lifecycle.single_currency_decimal_places(_FlakyClient(missing)) == (2, None)
    with pytest.raises(SfApiError):
        lifecycle.org_default_currency(_FlakyClient(SfApiError(503, "x", "GET", "/q")))


# -- review round 5 (todo 275): the settlement block is fixed once recorded -------


def test_block_is_recorded_when_the_first_settlement_step_starts(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=5.0),
                          payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.target_stage = "credit_applied"
    m = _posted_manifest()
    assert m.settlement is None
    m = steps.run_credit(ctx, m)
    # The run stops at credit_applied: the payment part is never recorded.
    assert m.settlement == {"application_level": "line",
                            "credit": {"amount": 5.0, "percent": None, "lines": None,
                                       "tax_strategy": "auto"}}


def test_cli_step_evaluates_config_against_to_stage(tmp_path) -> None:
    """A defaults.settlement shared by scenarios that stopped at invoice_posted
    or credit_applied yields the full block for a step to payment_applied."""
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "defaults:\n"
        "  kind: invoice_ingestion\n"
        "  settlement: {application_level: line, credit: {amount: 5}, payment: exact}\n"
        "scenarios:\n"
        "  - {account: Infinitech, target_stage: invoice_posted,\n"
        "     invoice_lines: [{name: L, unit_price: 5}]}\n"
    ))
    m = Manifest(run_id="X", kind="invoice_ingestion", account_name="Infinitech")
    spec = _settlement_for_step(SimpleNamespace(config=cfg, to_stage="payment_applied"), m)
    assert spec.credit.amount == 5.0 and spec.payment.is_exact


def test_settlement_errors_with_503_in_the_run_id_are_not_retried(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(502, "bad gateway", "POST", "/credit")
    run_id = "DEMO-20261125T150342Z-001"
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.run_id = run_id
    with pytest.raises(LifecycleError) as info:
        steps.run_credit(ctx, _posted_manifest(run_id=run_id))
    assert "150342" in str(info.value)  # the run id, holding "503"
    assert classify_exception(info.value) == "deterministic"


def test_every_settlement_raise_is_pinned_deterministic() -> None:
    """Sweep: settlement code raises SettlementError, never a bare
    LifecycleError (whose class the message text would decide)."""
    import inspect

    from scripts.txn_data_harness import cli

    lsrc = inspect.getsource(lifecycle)
    lsec = lsrc[lsrc.index("# Step 7 -- Settlement"):lsrc.index("# Step 6c -- Ingest invoice")]
    ssrc = inspect.getsource(steps)
    ssec = ssrc[ssrc.index("# -- settlement (credit_applied"):ssrc.index("STEP_REGISTRY: dict")]
    csec = "".join(inspect.getsource(f) for f in (
        cli._settlement_for_step, cli._config_settlement))
    for name, sec in (("lifecycle", lsec), ("steps", ssec), ("cli", csec)):
        assert "raise LifecycleError(" not in sec, name
    assert lifecycle.SettlementError("x", "y").failure_class == "deterministic"


def test_successful_step_clears_an_earlier_error(monkeypatch, billable_account) -> None:
    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         error="[credit] earlier failure", failure_class="deterministic",
                         settlement={"application_level": "line", "payment": {"amount": "exact"}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    assert cli_mod._cmd_step(_step_args()) == 0
    assert [s for s, _ in ran] == ["payment_applied"]
    assert m.error is None and m.failure_class is None


def test_failed_step_records_its_failure_class(monkeypatch, billable_account) -> None:
    from scripts.txn_data_harness import cli as cli_mod

    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         settlement={"application_level": "line", "payment": {"amount": "exact"}})
    _patch_cmd_step(monkeypatch, m, billable_account)

    def boom(step, ctx, mm):
        raise lifecycle.SettlementError("payment", "refused at T150342Z")

    monkeypatch.setattr(cli_mod, "execute_step", boom)
    with pytest.raises(LifecycleError):
        cli_mod._cmd_step(_step_args())
    assert m.failure_class == "deterministic" and "refused" in m.error


@pytest.mark.parametrize("quantity", [".nan", ".inf", "[1, .nan]"])
def test_usage_quantity_must_be_finite(quantity, tmp_path) -> None:
    from scripts.txn_data_harness.config import load_scenarios

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n  - target_stage: usage_upload\n    products:\n      - sku: QB-DB\n"
        f"        usage: {{quantity: {quantity}, records_per_line: 1}}\n"
    ))
    with pytest.raises(ConfigError, match="usage.quantity must be a finite"):
        load_scenarios(SimpleNamespace(config=cfg))


@pytest.mark.parametrize("tax", [{"rate": float("nan")}, {"amount": float("inf")}])
def test_tax_numbers_must_be_finite(tax) -> None:
    with pytest.raises(ConfigError, match="must be a finite"):
        _coerce_spec({
            "kind": "invoice_ingestion", "target_stage": "invoice_posted", "account": "Infinitech",
            "tax": {"name": "Sales Tax", "code": "TX", **tax},
            "invoice_lines": [{"name": "API", "quantity": 1, "unit_price": 10, "taxable": True}],
        }, "t")


# -- review round 6 (todo 275) --------------------------------------------------


def test_refused_credit_is_never_resent_by_a_retry_but_a_rerun_sends_it_once(billable_account) -> None:
    """A refusal created nothing and clears credit_submitted: the stage fails
    (new run advised); a plain rerun sends the same credit, under the one tag."""
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(400, '[{"errorCode":"INVALID_API_INPUT","message":"no"}]',
                                    "POST", "/credit")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError, match="credit refused.*start a new run"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    descs = [b["description"] for p, b, _ in org.posts if p.endswith("/actions/credit")]
    assert descs == ["RUN credit", "RUN credit"] and len(org.memos) == 1
    assert m.reached_stage == "credit_applied"


def test_baseline_is_read_just_before_the_post(billable_account) -> None:
    """A credit the platform applies after the settlement baseline but before
    the POST is not counted against this run; the baseline is retaken."""
    org = SettleOrg("line")
    real = org.query

    def query(soql):
        if "FROM InvoiceLine " in soql and not org.posts:
            org.invoice["NetCreditsApplied"] = 5.0  # lands while lines are read
        return real(soql)

    org.query = query
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert m.credit_baseline == 5.0 and m.settlement_baseline["net_credits_applied"] == 0.0
    assert m.reached_stage == "credit_applied"


def test_level_read_transient_failure_is_retryable(fake_client, monkeypatch) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    def unavailable(c):
        raise SfApiError(-1, "retrieve timed out after 90s", "retrieve", "Settings:Billing")

    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", unavailable)
    fake_client.query_responses = [[]]
    with pytest.raises(LifecycleError, match="--application-level line|header") as info:
        lifecycle.read_application_level(fake_client)
    assert classify_exception(info.value) == "transient"
    assert fake_client.instance_url not in lifecycle._level_cache

    def refused(c):
        raise SfApiError(403, "INSUFFICIENT_ACCESS", "POST", "/services/Soap/m")

    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", refused)
    fake_client.query_responses = [[]]
    with pytest.raises(LifecycleError) as info:
        lifecycle.read_application_level(fake_client)
    assert classify_exception(info.value) == "deterministic"


def test_billing_settings_http_errors_split_refused_and_transient() -> None:
    from scripts.txn_data_harness import auth

    client = auth.SfRestClient(alias="a", access_token="T", instance_url="https://x.example")

    def session(status):
        class _S:
            def post(self, *a, **kw):
                return SimpleNamespace(status_code=status, text="x")
        return _S()

    client._local.session = session(403)
    assert client.read_billing_settings_xml() is None
    client._local.session = session(503)
    with pytest.raises(auth.SfApiError) as info:
        client.read_billing_settings_xml()
    assert info.value.status == 503


def test_application_level_cannot_change_after_the_payment_is_planned(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = _posted_manifest(application_level="header", application_level_source="config",
                         payment_amount=250.0, payment_apply_target=250.0, payment_mode="exact",
                         settlement_baseline={"balance": 250.0, "decimal_places": 2})
    with pytest.raises(LifecycleError, match="cannot change on this manifest.*new run"):
        steps.run_payment(_settle_ctx(org, billable_account, spec, override="line"), m)
    assert org.posts == [] and m.application_level == "header"
    # The same level is accepted.
    org = SettleOrg("header")
    m = steps.run_payment(_settle_ctx(org, billable_account, spec, override="header"),
                          _posted_manifest(application_level="header", payment_amount=250.0,
                                           payment_apply_target=250.0, payment_mode="exact",
                                           settlement_baseline={"balance": 250.0, "decimal_places": 2}))
    assert m.reached_stage == "payment_applied"


def test_same_config_accepted_for_an_earlier_target(tmp_path) -> None:
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _cfg_block(tmp_path, "{application_level: line, credit: {amount: 5}, payment: exact}",
                     "payment_applied")
    recorded = {"application_level": "line", "credit": {"amount": 5}, "payment": {"amount": "exact"}}
    m = _posted_manifest(settlement=recorded)
    args = SimpleNamespace(config=cfg, to_stage="credit_applied")
    assert _settlement_for_step(args, m) is None


def test_step_to_a_reached_target_keeps_the_error(monkeypatch, billable_account) -> None:
    """Nothing runs, so nothing changes: only a step that runs and succeeds
    clears error / failure_class."""
    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         error="[payment] no settlement 'payment'", failure_class="deterministic",
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    assert cli_mod._cmd_step(_step_args(to_stage="credit_applied")) == 0
    assert ran == [] and m.error and m.failure_class == "deterministic"


@pytest.mark.parametrize("status, body, expected", [
    (400, '[{"errorCode":"INVALID_QUERY_FILTER_OPERATOR","message":"total 1503.50"}]',
     "deterministic"),
    (400, '[{"errorCode":"UNABLE_TO_LOCK_ROW","message":"busy"}]', "transient"),
    (503, "unavailable", "transient"),
    (-1, "exhausted retries: timed out", "transient"),
    (1, "Error: No authorization information found", "deterministic"),  # cli, no HTTP status
])
def test_settlement_api_errors_are_pinned_at_the_step_boundary(
    status, body, expected, billable_account
) -> None:
    """Every SfApiError leaving a settlement step is classified from its status
    and errorCode only -- never from text such as a run id holding "503"."""
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    org = SettleOrg("line")
    real = org.query

    def query(soql):
        if "FROM PaymentLineInvoiceLine" in soql:
            raise SfApiError(status, body, "GET", "/query?q=...DEMO-20261125T150342Z-PAY")
        return real(soql)

    org.query = query
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    with pytest.raises(lifecycle.SettlementError) as info:
        steps.execute_step("payment_applied", _settle_ctx(org, billable_account, spec),
                           _posted_manifest())
    assert "503" in str(info.value)  # the run id, which must not decide
    assert classify_exception(info.value) == expected


# -- review round 7 (todo 275) --------------------------------------------------


def _reverse(org, kind: str, **fields):
    """Mark the first application row of ``kind`` reversed outside the harness."""
    rows = org.credit_apps if kind == "credit" else org.payment_apps
    rows[0].update(fields)


@pytest.mark.parametrize("fields", [
    {"UnappliedStatus": "Yes"},          # line junction: original row flagged
    {"Type": "Unapplied"},               # the reversal row itself
])
def test_reversed_credit_application_fails_the_stage(fields, billable_account) -> None:
    org = SettleOrg("line")
    real = org._post_memo

    def post_then_reverse(memo):
        real(memo)
        if org.credit_apps:
            _reverse(org, "credit", **fields)

    org._post_memo = post_then_reverse
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(LifecycleError, match="reversed outside the harness.*start a new run") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic" and m.reached_stage == "invoice_posted"


@pytest.mark.parametrize("level, fields", [
    ("header", {"HasBeenUnapplied": "Yes"}),
    ("line", {"Type": "Unapplied"}),
])
def test_reversed_payment_application_fails_the_resume(level, fields, billable_account) -> None:
    """A payment applied earlier, then unapplied in the org: the remainder
    read-back must not trust it."""
    org = SettleOrg(level)
    spec = SettlementSpec(application_level=level, payment=PaymentSpec(amount=100.0))
    ctx = _settle_ctx(org, billable_account, spec)
    m = steps.run_payment(ctx, _posted_manifest())
    _reverse(org, "payment", **fields)
    m.reached_stage = "credit_applied"
    with pytest.raises(LifecycleError, match="reversed outside the harness"):
        steps.run_payment(ctx, m)


def test_is_api_refusal_keeps_retryable_4xx_transient() -> None:
    from scripts.txn_data_harness.auth import SfApiError

    assert lifecycle.is_api_refusal(SfApiError(400, '[{"errorCode":"INVALID_FIELD"}]', "GET", "/q"))
    assert not lifecycle.is_api_refusal(SfApiError(429, "too many", "POST", "/p"))
    assert not lifecycle.is_api_refusal(SfApiError(420, "slow down", "POST", "/p"))
    assert not lifecycle.is_api_refusal(
        SfApiError(400, '[{"errorCode":"UNABLE_TO_LOCK_ROW","message":"x"}]', "GET", "/q"))


def test_429_on_the_payment_insert_stays_transient(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    org = SettleOrg("line")
    real = org._do_post

    def post(path, body):
        if path.endswith("/sobjects/Payment"):
            raise SfApiError(429, "REQUEST_LIMIT_EXCEEDED", "POST", "/sobjects/Payment")
        return real(path, body)

    org._do_post = post
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError) as info:
        steps.execute_step("payment_applied", _settle_ctx(org, billable_account, spec), m)
    assert classify_exception(info.value) == "transient"
    # Nothing was created: the flag is cleared, so the retry inserts once.
    assert m.payment_submitted is False and org.payments == []
    org._do_post = real
    m = steps.execute_step("payment_applied", _settle_ctx(org, billable_account, spec), m)
    assert len(org.payments) == 1 and m.reached_stage == "payment_applied"


def test_lock_error_on_a_settlement_query_stays_transient(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    org = SettleOrg("line")
    real = org.query

    def query(soql):
        if "FROM PaymentLineInvoiceLine" in soql:
            raise SfApiError(400, '[{"errorCode":"UNABLE_TO_LOCK_ROW","message":"busy"}]',
                             "GET", "/query?run=DEMO-20261125T150342Z")
        return real(soql)

    org.query = query
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    with pytest.raises(lifecycle.SettlementError) as info:
        steps.execute_step("payment_applied", _settle_ctx(org, billable_account, spec),
                           _posted_manifest())
    assert classify_exception(info.value) == "transient"


def test_level_read_429_is_retried(fake_client, monkeypatch) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    def limited(c):
        raise SfApiError(429, "REQUEST_LIMIT_EXCEEDED", "POST", "/services/Soap/m")

    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", limited)
    fake_client.query_responses = [[]]
    with pytest.raises(LifecycleError) as info:
        lifecycle.read_application_level(fake_client)
    assert classify_exception(info.value) == "transient"


_SOAP_FAULT = (
    '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope '
    'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
    'xmlns:sf="http://soap.sforce.com/2006/04/metadata"><soapenv:Body><soapenv:Fault>'
    "<faultcode>sf:{code}</faultcode><faultstring>{code}: x</faultstring>"
    "</soapenv:Fault></soapenv:Body></soapenv:Envelope>"
)


@pytest.mark.parametrize("code, refused", [
    ("INVALID_SESSION_ID", True), ("INSUFFICIENT_ACCESS", True), ("INVALID_TYPE", True),
    ("UNKNOWN_EXCEPTION", False),
])
def test_soap_faults_on_http_500(code, refused) -> None:
    """Metadata SOAP faults arrive as HTTP 500 (measured: INVALID_SESSION_ID)."""
    from scripts.txn_data_harness import auth

    client = auth.SfRestClient(alias="a", access_token="T", instance_url="https://x.example")

    class _S:
        def post(self, *a, **kw):
            return SimpleNamespace(status_code=500, text=_SOAP_FAULT.format(code=code))

    client._local.session = _S()
    if refused:
        assert client.read_billing_settings_xml() is None
    else:
        with pytest.raises(auth.SfApiError):
            client.read_billing_settings_xml()


def test_refused_soap_read_without_evidence_is_deterministic(fake_client) -> None:
    from scripts.txn_data_harness.failure import classify_exception

    fake_client.read_billing_settings_xml = lambda: None  # refused (4xx or SOAP refusal)
    fake_client.query_responses = [[]]
    with pytest.raises(LifecycleError, match="--application-level") as info:
        lifecycle.read_application_level(fake_client)
    assert classify_exception(info.value) == "deterministic"


def test_unrelated_scenario_does_not_block_the_resume(tmp_path) -> None:
    """Under `cli step` the --to-stage check runs on the matching scenario
    only: a credit-only scenario for another account must not fail it."""
    from scripts.txn_data_harness.cli import _settlement_for_step

    cfg = _step_cfg(tmp_path, (
        "scenarios:\n"
        "  - {kind: invoice_ingestion, account: Global Media, target_stage: credit_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}], settlement: {credit: {amount: 1}}}\n"
        "  - {kind: invoice_ingestion, account: Infinitech, target_stage: payment_applied,\n"
        "     invoice_lines: [{name: L, unit_price: 5}], settlement: {payment: exact}}\n"
    ))
    m = Manifest(run_id="X", kind="invoice_ingestion", account_name="Infinitech")
    spec = _settlement_for_step(SimpleNamespace(config=cfg, to_stage="payment_applied"), m)
    assert spec.payment.is_exact
    # The matching scenario itself is still checked against --to-stage.
    m = Manifest(run_id="X", kind="invoice_ingestion", account_name="Global Media")
    with pytest.raises(ConfigError, match="needs 'settlement.payment'"):
        _settlement_for_step(SimpleNamespace(config=cfg, to_stage="payment_applied"), m)


def test_billing_settings_429_is_not_a_refusal() -> None:
    from scripts.txn_data_harness import auth

    client = auth.SfRestClient(alias="a", access_token="T", instance_url="https://x.example")

    class _S:
        def post(self, *a, **kw):
            return SimpleNamespace(status_code=429, text="REQUEST_LIMIT_EXCEEDED")

    client._local.session = _S()
    with pytest.raises(auth.SfApiError) as info:
        client.read_billing_settings_xml()
    assert info.value.status == 429


def test_baseline_counts_only_applied_rows(billable_account) -> None:
    """The settlement baseline lists the platform's applications; reversal
    rows (Type Unapplied) on the invoice are not applications."""
    org = SettleOrg("line")
    for level in ("line", "header"):
        org.payment_apps.append({"Id": f"1AlU{level}", "Amount": 5.0, "level": level,
                                 "payment": "0aQOLD", "invoice": "3ttINV", "Type": "Unapplied"})
        org.credit_apps.append({"Id": f"4sGU{level}", "Amount": 5.0, "level": level,
                                "memo": "50gOLD", "invoice": "3ttINV", "Type": "Unapplied"})
    m = _posted_manifest()
    steps._ensure_settlement_baseline(_settle_ctx(org, billable_account, None), m)
    assert m.settlement_baseline["foreign_payment_application_ids"] == []
    assert m.settlement_baseline["foreign_credit_application_ids"] == []


# -- review round 8 (todo 275): one write rule for credit and payment ------------


def test_two_payments_under_the_tag_fail_naming_the_stray(billable_account) -> None:
    org = SettleOrg("line")
    for pid in ("0aQA", "0aQB"):
        org.payments.append({"Id": pid, "AccountId": billable_account.id,
                             "GatewayRefNumber": "RUN-PAY", "Amount": 250.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    with pytest.raises(lifecycle.SettlementError, match="2 payments.*first 0aQA; stray 0aQB.*"
                                                         "start a new run") as info:
        steps.run_payment(_settle_ctx(org, billable_account, spec), _payment_planned_manifest())
    assert info.value.failure_class == "deterministic" and len(org.payments) == 2


def test_payment_never_appearing_after_an_unknown_insert_fails(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(502, "bad gateway", "POST", "/sobjects/Payment")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError, match="payment outcome unknown") as info:
        steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic" and m.payment_submitted
    # A resume never inserts again.
    with pytest.raises(lifecycle.SettlementError, match="payment outcome unknown"):
        steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert org.payments == []


def test_payment_refusal_clears_and_a_rerun_inserts_once(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(400, '[{"errorCode":"FIELD_INTEGRITY_EXCEPTION",'
                                    '"message":"amount 1503.50 too large"}]',
                                    "POST", "/sobjects/Payment")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError, match="payment refused.*Nothing was created"
                                                         ".*Rerunning sends the same payment") as info:
        steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"  # "1503.50" does not read as a 503
    assert m.payment_submitted is False and org.payments == []
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert len(org.payments) == 1 and m.reached_stage == "payment_applied"


def test_payment_submitted_is_on_disk_before_the_insert(tmp_path, billable_account) -> None:
    from scripts.txn_data_harness.manifests import load_manifest, write_manifest

    org = SettleOrg("line")
    org.fail_next_post = KeyboardInterrupt()
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.checkpoint = lambda mm: write_manifest(mm, manifest_dir=tmp_path)
    with pytest.raises(KeyboardInterrupt):
        steps.run_payment(ctx, _posted_manifest())
    assert load_manifest(str(tmp_path / "RUN.json")).payment_submitted is True


def test_429_on_the_credit_post_clears_and_is_retried(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.failure import classify_exception

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(429, "slow down", "POST", "/credit")
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError, match="nothing was created") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert classify_exception(info.value) == "transient" and m.credit_submitted is False
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert len(org.memos) == 1 and m.reached_stage == "credit_applied"


@pytest.mark.parametrize("status, body, refusal", [
    (400, '[{"errorCode":"INVALID_API_INPUT","message":"total 1503.50 exceeds 429"}]', True),
    (400, '{"message":"x","output":{"errors":[{"errorCode":"UNABLE_TO_LOCK_ROW"}]}}', False),
    (404, "not json 503", True),
    (429, '[{"errorCode":"INVALID_API_INPUT"}]', False),
    (420, "", False),
])
def test_refusal_is_decided_by_status_and_error_code_only(status, body, refusal) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    exc = SfApiError(status, body, "POST", "/x")
    assert lifecycle.is_api_refusal(exc) is refusal
    assert lifecycle.is_client_error(exc)


@pytest.mark.parametrize("obj, level, flag", [
    ("credit", "line", "UnappliedStatus"),
    ("credit", "header", "HasBeenUnapplied"),
    ("payment", "line", "UnappliedStatus"),
    ("payment", "header", "HasBeenUnapplied"),
])
def test_reversal_flag_is_read_from_each_objects_own_field(obj, level, flag, billable_account) -> None:
    """Each junction carries its own flag (describe on 264); the fake returns
    only selected fields, so a swapped or unselected flag fails."""
    org = SettleOrg(level)
    if obj == "credit":
        real = org._post_memo

        def post_then_reverse(memo):
            real(memo)
            if org.credit_apps:
                org.credit_apps[0][flag] = "Yes"

        org._post_memo = post_then_reverse
        spec = SettlementSpec(application_level=level, credit=CreditSpec(amount=20.0))
        with pytest.raises(lifecycle.SettlementError, match=f"reversed outside the harness.*{flag} Yes"):
            steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    else:
        spec = SettlementSpec(application_level=level, payment=PaymentSpec(amount=100.0))
        ctx = _settle_ctx(org, billable_account, spec)
        m = steps.run_payment(ctx, _posted_manifest())
        org.payment_apps[0][flag] = "Yes"
        m.reached_stage = "credit_applied"
        with pytest.raises(lifecycle.SettlementError, match=f"reversed outside the harness.*{flag} Yes"):
            steps.run_payment(ctx, m)


# -- review round 9 (todo 275) --------------------------------------------------


def test_step_to_a_reached_target_keeps_an_apply_error(monkeypatch, billable_account) -> None:
    """A payment that exists (id recorded) but was not fully applied: its
    error stays on a step to an already-reached stage."""
    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         error="[payment] apply refused", failure_class="deterministic",
                         payment_submitted=True, payment_ids=["0aQ1"],
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    assert cli_mod._cmd_step(_step_args(to_stage="credit_applied")) == 0
    assert ran == [] and m.error == "[payment] apply refused"


@pytest.mark.parametrize("evidence", ["settlement_level", "application_row"])
def test_level_mismatch_with_evidence_fails_before_the_insert(evidence, billable_account) -> None:
    org = SettleOrg("line")
    if evidence == "settlement_level":
        org.invoice["SettlementLevel"] = "InvoiceLine"
    else:
        org.credit_apps.append({"Id": "4sGX", "Amount": 5.0, "level": "line", "memo": "50gX",
                                "invoice": "3ttINV"})
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=10.0))
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError,
                       match="level is header but .* says line; no payment was inserted"
                             ".*--application-level line") as info:
        steps.run_payment(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"
    assert org.payments == [] and org.posts == [] and m.payment_apply_target is None


def test_level_without_evidence_proceeds(billable_account) -> None:
    org = SettleOrg("header")
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=10.0))
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert len(org.payments) == 1 and m.reached_stage == "payment_applied"
    org = SettleOrg("header")
    org.invoice["SettlementLevel"] = "Invoice"  # agreeing evidence
    m = steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert len(org.payments) == 1


@pytest.mark.parametrize("call", ["credit", "payment", "apply"])
def test_requests_transport_sends_settlement_writes_once(call, monkeypatch) -> None:
    from scripts.txn_data_harness import auth
    from scripts.txn_data_harness.auth import SfApiError

    monkeypatch.setattr(auth.time, "sleep", lambda s: None)
    client = _client("requests")
    calls = _fake_requests(client, 503, "unavailable")
    with pytest.raises(SfApiError):
        if call == "credit":
            lifecycle.submit_credit(client, "3ttINV", {"invoiceLines": []})
        elif call == "payment":
            lifecycle.create_payment(client, {"Amount": 1})
        else:
            lifecycle.apply_payment(client, "0aQ1", {"appliedToId": "3ttINV", "amount": 1})
    assert len(calls) == 1


def test_header_level_apply_that_committed_then_failed_is_not_applied_twice(billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    org = SettleOrg("header")
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=120.0))
    ctx = _settle_ctx(org, billable_account, spec)
    real = org._do_post
    calls = {"n": 0}

    def commit_then_fail(path, body):
        result = real(path, body)
        if path.endswith("/actions/apply"):
            calls["n"] += 1
            if calls["n"] == 1:
                raise SfApiError(500, "internal", "POST", path)
        return result

    org._do_post = commit_then_fail
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError):
        steps.execute_step("payment_applied", ctx, m)
    org.posts.clear()
    m = steps.run_payment(ctx, m)
    assert _applies(org) == []
    assert m.payment_amount_applied == 120.0 and sum(a["Amount"] for a in org.payment_apps) == 120.0


@pytest.mark.parametrize("status, code", [
    (403, "REQUEST_LIMIT_EXCEEDED"),
    (400, "QUERY_TIMEOUT"),
    (400, "TOO_MANY_CONCURRENT_REQUESTS"),
])
def test_each_retryable_error_code_is_not_a_refusal(status, code) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    exc = SfApiError(status, json.dumps([{"errorCode": code, "message": "m"}]), "GET", "/q")
    assert lifecycle.is_retryable_client_error(exc) and not lifecycle.is_api_refusal(exc)


def test_reference_line_error_codes_are_read() -> None:
    from scripts.txn_data_harness.auth import SfApiError

    body = json.dumps({"message": "Couldn't create credit memo.", "output": {
        "errors": [], "referenceLineErrorResults": [
            {"errors": [{"errorCode": "UNABLE_TO_LOCK_ROW", "message": "busy"}]}]}})
    exc = SfApiError(400, body, "POST", "/credit")
    assert lifecycle.api_error_codes(body) == ["UNABLE_TO_LOCK_ROW"]
    assert not lifecycle.is_api_refusal(exc)


def test_submitted_payment_waits_for_a_late_one(billable_account) -> None:
    """A resume after an unknown insert waits briefly for the payment to show
    up by its tag instead of failing at once."""
    org = SettleOrg("line")
    org.payments.append({"Id": "0aQLATE", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 250.0, "_visible_after": 3})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.poll_timeout = 30
    m = steps.run_payment(ctx, _payment_planned_manifest(payment_submitted=True))
    assert m.payment_ids == ["0aQLATE"] and len(org.payments) == 1


def test_payment_refusal_clears_submitted_on_disk(tmp_path, billable_account) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.manifests import load_manifest, write_manifest

    org = SettleOrg("line")
    org.fail_next_post = SfApiError(400, '[{"errorCode":"FIELD_INTEGRITY_EXCEPTION"}]',
                                    "POST", "/sobjects/Payment")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.checkpoint = lambda mm: write_manifest(mm, manifest_dir=tmp_path)
    with pytest.raises(lifecycle.SettlementError, match="payment refused"):
        steps.run_payment(ctx, _posted_manifest())
    assert load_manifest(str(tmp_path / "RUN.json")).payment_submitted is False


# -- review round 10 (todo 275) -------------------------------------------------


def test_payment_target_without_a_recorded_payment_is_refused_before_any_step(
    monkeypatch, billable_account
) -> None:
    """A credit-only recorded block at invoice_posted: stepping to
    payment_applied would write the credit first, so it is refused up front."""
    m = _posted_manifest(account_id=billable_account.id, reached_stage="invoice_posted",
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    with pytest.raises(lifecycle.SettlementError, match="has no 'payment' and is fixed"):
        cli_mod._cmd_step(_step_args(to_stage="payment_applied"))
    assert ran == []


def test_fallback_level_after_a_transient_read_is_not_cached(fake_client, monkeypatch) -> None:
    from scripts.txn_data_harness.auth import SfApiError

    reads = []

    def flaky(c):
        reads.append(1)
        if len(reads) == 1:
            raise SfApiError(503, "unavailable", "POST", "/services/Soap/m")
        return "header"

    monkeypatch.setattr(lifecycle, "_read_billing_settings_level", flaky)
    fake_client.query_responses = [[{"SettlementLevel": "InvoiceLine"}]]
    assert lifecycle.read_application_level(fake_client) == ("line", "invoice_settlement_level")
    assert lifecycle.read_application_level(fake_client) == ("header", "billing_settings")
    assert lifecycle.read_application_level(fake_client) == ("header", "billing_settings")
    assert len(reads) == 2  # the settings read is cached once it succeeds


def test_application_level_flag_is_refused_where_it_cannot_apply(monkeypatch, billable_account) -> None:
    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         settlement={"application_level": "line", "credit": {"amount": 5}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    with pytest.raises(LifecycleError, match="applies only to --to-stage payment_applied"):
        cli_mod._cmd_step(_step_args(to_stage="invoice_posted", application_level="line"))
    # credit_applied on a block with a payment would drop the override silently.
    m.settlement = {"application_level": "line", "credit": {"amount": 5},
                    "payment": {"amount": "exact"}}
    m.reached_stage = "invoice_posted"
    with pytest.raises(LifecycleError, match="applies only to --to-stage payment_applied"):
        cli_mod._cmd_step(_step_args(to_stage="credit_applied", application_level="header"))
    m.reached_stage = "payment_applied"
    with pytest.raises(LifecycleError, match="already reached payment_applied"):
        cli_mod._cmd_step(_step_args(to_stage="payment_applied", application_level="line"))
    assert ran == []


def test_equal_application_level_override_is_ignored(billable_account) -> None:
    org = SettleOrg("line")
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=10.0))
    m = _posted_manifest(application_level="line", application_level_source="billing_settings")
    m = steps.run_payment(_settle_ctx(org, billable_account, spec, override="line"), m)
    assert m.application_level_source == "billing_settings"
    assert not any("overridden" in w for w in m.settlement_warnings)


def test_header_application_row_is_level_evidence(billable_account) -> None:
    org = SettleOrg("line")
    org.credit_apps.append({"Id": "4sGH", "Amount": 5.0, "level": "header", "memo": "50gX",
                            "invoice": "3ttINV"})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec(amount=10.0))
    with pytest.raises(lifecycle.SettlementError, match="level is line but .* says header"):
        steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.payments == []


def test_payment_line_row_is_level_evidence(billable_account) -> None:
    org = SettleOrg("header")
    org.payment_apps.append({"Id": "1AlL", "Amount": 5.0, "level": "line", "payment": "0aQX",
                             "invoice": "3ttINV"})
    spec = SettlementSpec(application_level="header", payment=PaymentSpec(amount=10.0))
    with pytest.raises(lifecycle.SettlementError, match="level is header but .* says line"):
        steps.run_payment(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.payments == []


def test_no_level_check_once_the_insert_was_submitted(billable_account) -> None:
    """After an insert whose outcome was unknown the payment may exist: the
    resume looks it up instead of running the pre-insert check."""
    org = SettleOrg("line")
    org.invoice["SettlementLevel"] = "Invoice"  # would contradict "line"
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 250.0})
    spec = SettlementSpec(application_level="line", payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec),
                          _payment_planned_manifest(payment_submitted=True))
    assert m.payment_ids == ["0aQ1"] and m.reached_stage == "payment_applied"


@pytest.mark.parametrize("level", ["header", "line"])
def test_apply_is_capped_at_the_current_balance_and_warns(level, billable_account) -> None:
    """The plan (250) outlived the balance (now 100): the apply takes what is
    open, and the shortfall is a warning."""
    org = SettleOrg(level)
    org.lines[0]["Balance"] = 0.0
    org.lines[1]["Balance"] = 100.0
    org.payments.append({"Id": "0aQ1", "AccountId": billable_account.id,
                         "GatewayRefNumber": "RUN-PAY", "Amount": 250.0})
    spec = SettlementSpec(application_level=level, payment=PaymentSpec())
    m = steps.run_payment(_settle_ctx(org, billable_account, spec),
                          _payment_planned_manifest(payment_ids=["0aQ1"]))
    target = "3ttINV" if level == "header" else "5TV2"
    assert _applies(org) == [(target, 100.0)]
    assert any("payment applied 100.0 of the 250.0 planned" in w for w in m.settlement_warnings)


def test_memo_not_posted_in_time_names_the_resume(billable_account) -> None:
    org = SettleOrg("line")
    org.memo_statuses = ["Pending"]
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError,
                       match=r"not Posted within 1s. Rerun `cli step --manifest RUN --to-stage "
                             r"credit_applied` to keep waiting"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert m.credit_submitted is True


# -- review round 11 (todo 275) -------------------------------------------------


def test_cli_step_clears_the_error_in_the_write_that_records_the_stage(
    monkeypatch, billable_account
) -> None:
    m = _posted_manifest(account_id=billable_account.id, reached_stage="credit_applied",
                         error="[payment] earlier", failure_class="transient",
                         settlement={"application_level": "line", "payment": {"amount": "exact"}})
    cli_mod, ran = _patch_cmd_step(monkeypatch, m, billable_account)
    writes = []
    monkeypatch.setattr(cli_mod, "write_manifest",
                        lambda mm: writes.append((mm.reached_stage, mm.error, mm.failure_class)))
    assert cli_mod._cmd_step(_step_args()) == 0
    assert writes[0] == ("payment_applied", None, None)


def test_batch_retry_clears_the_error_in_the_write_that_records_the_stage(
    billable_account, org_context, monkeypatch
) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.handlers import invoice_ingestion as mod
    from scripts.txn_data_harness.models import ResolvedInvoiceIngestionSpec

    calls = []

    def execute(step, ctx, manifest):
        calls.append(step)
        if step == "ingest_invoice":
            manifest.invoice_id = "3ttINV"
            manifest.reached_stage = "invoice_posted"
        elif step == "credit_applied" and calls.count("credit_applied") == 1:
            raise SfApiError(503, "unavailable", "POST", "/x")
        elif step != "promote_to_posted":
            manifest.reached_stage = step
        return manifest

    writes = []
    monkeypatch.setattr(mod, "execute_step", execute)
    monkeypatch.setattr(mod, "write_manifest",
                        lambda m: writes.append((m.reached_stage, m.error)))
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    spec = _coerce_spec({
        "kind": "invoice_ingestion", "target_stage": "payment_applied",
        "invoice_lines": [{"name": "L", "quantity": 1, "unit_price": 10}],
        "settlement": {"credit": {"amount": 1}, "payment": {"amount": 1}},
    }, "t")
    resolved = ResolvedInvoiceIngestionSpec(
        spec=spec, account=billable_account, invoice_lines=[], invoice_overrides=None,
        effective_stage="payment_applied",
    )
    SCENARIO_HANDLERS["invoice_ingestion"].run(
        None, org_context, "RUN", resolved, poll_timeout=1, max_retries=2)
    after_retry = writes[writes.index(next(w for w in writes if w[1])) + 1:]
    first_stage_write = next(w for w in after_retry if w[0] == "credit_applied")
    assert first_stage_write == ("credit_applied", None)


@pytest.mark.parametrize("what, block", [
    ("credit", {"credit": {"amount": 0.4}}),
    ("credit", {"credit": {"percent": 0.01}}),
    ("payment", {"payment": {"amount": 0.4}}),
])
def test_amount_below_one_minor_unit_is_refused(what, block, billable_account) -> None:
    org = SettleOrg("line", places=0)
    org.invoice["CurrencyIsoCode"] = "JPY"
    spec = _pst(target_stage="payment_applied" if what == "payment" else "credit_applied",
                settlement={"application_level": "line", **block}).settlement
    run = steps.run_credit if what == "credit" else steps.run_payment
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError,
                       match=f"configured {what} rounds to 0 in JPY \\(0 decimal places\\)") as info:
        run(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic"
    assert org.posts == [] and m.reached_stage == "invoice_posted"


def test_no_open_balance_still_skips_the_credit(billable_account) -> None:
    org = SettleOrg("line")
    for line in org.lines:
        line["Balance"] = 0.0
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=5.0))
    m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.posts == [] and m.reached_stage == "credit_applied"
    assert any("no open balance" in w for w in m.settlement_warnings)


def test_sales_retry_clears_the_error_in_the_write_that_records_the_stage(
    billable_account, org_context, monkeypatch
) -> None:
    from scripts.txn_data_harness.auth import SfApiError
    from scripts.txn_data_harness.handlers import sales_transaction_base as mod
    from scripts.txn_data_harness.models import ResolvedSpec

    calls = []

    def execute(step, ctx, manifest):
        calls.append(step)
        if step == "credit_applied" and calls.count("credit_applied") == 1:
            raise SfApiError(503, "unavailable", "POST", "/x")
        manifest.reached_stage = {"order_from_quote": "order_draft"}.get(step, step)
        return manifest

    from scripts.txn_data_harness import runner

    writes = []
    monkeypatch.setattr(runner, "draw_lines", lambda options: [])
    monkeypatch.setattr(mod, "execute_step", execute)
    monkeypatch.setattr(mod, "write_manifest",
                        lambda m: writes.append((m.reached_stage, m.error)))
    spec = _pst(target_stage="payment_applied",
                settlement={"credit": {"amount": 1}, "payment": {"amount": 1}})
    resolved = ResolvedSpec(spec=spec, account=billable_account, options=[],
                            effective_stage="payment_applied")
    SCENARIO_HANDLERS["sales_txn_quote"].run(
        None, org_context, "RUN", resolved, poll_timeout=1, max_retries=2, sleep=lambda s: None)
    after_retry = writes[writes.index(next(w for w in writes if w[1])) + 1:]
    assert next(w for w in after_retry if w[0] == "credit_applied") == ("credit_applied", None)


# -- review round 12 (todo 275) -------------------------------------------------


def test_credit_only_run_succeeds_when_the_level_cannot_be_read(billable_account, monkeypatch) -> None:
    def unreadable(c):
        raise lifecycle.SettlementError("settlement", "could not read the level")

    monkeypatch.setattr(lifecycle, "read_application_level", unreadable)
    org = SettleOrg("line")
    spec = SettlementSpec(credit=CreditSpec(amount=20.0))
    ctx = _settle_ctx(org, billable_account, spec)
    ctx.target_stage = "credit_applied"
    m = steps.run_credit(ctx, _posted_manifest())
    assert m.reached_stage == "credit_applied" and m.credit_amount_applied == 20.0


def test_fixed_sub_unit_payment_is_refused_before_the_credit_post(billable_account) -> None:
    org = SettleOrg("line", places=0)
    org.invoice["CurrencyIsoCode"] = "JPY"
    spec = _pst(target_stage="payment_applied", settlement={
        "application_level": "line", "credit": {"amount": 50}, "payment": {"amount": 0.4},
    }).settlement
    with pytest.raises(lifecycle.SettlementError, match="configured payment rounds to 0 in JPY"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
    assert org.posts == [] and org.memos == []


# -- review round 13 (todo 275): the memo applies its whole total here ----------


def _post_and_then(org, change):
    real = org._post_memo

    def post(memo):
        had = bool(memo.get("_allocs"))
        real(memo)
        if had:
            change(memo)

    org._post_memo = post


def test_memo_tax_shortfall_fails(billable_account) -> None:
    """Platform tax 0.50 above what was applied: the 0.50 left would settle
    the account's next posted invoice."""
    org = SettleOrg("line")
    _post_and_then(org, lambda memo: memo.update(TotalAmountWithTax=20.5, Balance=0.5))
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    m = _posted_manifest()
    with pytest.raises(lifecycle.SettlementError,
                       match=r"credit memo 50g1 applied 20.0 to this invoice but its total is "
                             r"20.5.*start a new run") as info:
        steps.run_credit(_settle_ctx(org, billable_account, spec), m)
    assert info.value.failure_class == "deterministic" and m.reached_stage == "invoice_posted"


def test_memo_leftover_absorbed_by_another_invoice_fails(billable_account) -> None:
    """Balance 0 because another invoice took the rest: still a failure."""
    org = SettleOrg("line")
    _post_and_then(org, lambda memo: memo.update(TotalAmountWithTax=30.0, Balance=0.0))
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(lifecycle.SettlementError, match="applied 20.0 to this invoice but its total is 30.0"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())


def test_posted_memo_with_nothing_applied_here_fails(billable_account) -> None:
    org = SettleOrg("line")
    org.memos.append({"Id": "50gONLY", "ReferenceEntityId": "3ttINV", "Description": "RUN credit",
                      "Status": "Posted", "Balance": 0.0, "TotalAmountWithTax": 20.0,
                      "_statuses": ["Posted"]})
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    with pytest.raises(lifecycle.SettlementError, match="50gONLY applied 0.0 to this invoice"):
        steps.run_credit(_settle_ctx(org, billable_account, spec), _submitted())


@pytest.mark.parametrize("total, ok", [(20.0, True), (20.01, False), (20.02, False)])
def test_memo_must_apply_exactly_its_total(total, ok, billable_account) -> None:
    """Exact match only: even one minor unit left would settle the account's
    next posted invoice (live: every memo applied exactly its total)."""
    org = SettleOrg("line")
    _post_and_then(org, lambda memo: memo.update(TotalAmountWithTax=total))
    spec = SettlementSpec(application_level="line", credit=CreditSpec(amount=20.0))
    if ok:
        m = steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())
        assert m.reached_stage == "credit_applied" and m.credit_amount_applied == 20.0
    else:
        with pytest.raises(lifecycle.SettlementError, match=f"its total is {total}"):
            steps.run_credit(_settle_ctx(org, billable_account, spec), _posted_manifest())


# -- rebase onto todo 276: never echo raw sf stdout -------------------------------


def test_cli_transport_failure_without_status_never_echoes_stdout(monkeypatch) -> None:
    from scripts.txn_data_harness import auth
    from scripts.txn_data_harness.auth import SfApiError

    client = _client("cli")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **kw: SimpleNamespace(
        returncode=1, stdout="00D...!SECRET-LOOKING-OUTPUT", stderr=""))
    with pytest.raises(SfApiError) as info:
        client.get("/services/data/v68.0/limits")
    assert "SECRET" not in str(info.value) and "not shown" in str(info.value)
    assert info.value.status == 1


def test_billing_settings_retrieve_failure_reports_the_json_error_only(monkeypatch) -> None:
    from scripts.txn_data_harness import auth
    from scripts.txn_data_harness.auth import SfApiError

    client = auth.SfRestClient(alias="a", access_token="", instance_url="https://x.example",
                               transport="cli")
    out = json.dumps({"name": "NoOrgFound", "message": "No authorization found", "extra": "SECRET"})
    monkeypatch.setattr(auth.subprocess, "run",
                        lambda *a, **kw: SimpleNamespace(returncode=1, stdout=out, stderr=""))
    with pytest.raises(SfApiError) as info:
        client.read_billing_settings_xml()
    assert "NoOrgFound: No authorization found" in str(info.value)
    assert "SECRET" not in str(info.value)


def test_cli_exit_0_without_status_line_never_reaches_an_error(monkeypatch, billable_account) -> None:
    """sf exits 0 with no status line and a non-JSON body: the transport
    returns {"_raw": text}; payment errors report its length only."""
    from scripts.txn_data_harness import auth

    client = _client("cli")
    monkeypatch.setattr(auth.subprocess, "run", lambda *a, **kw: SimpleNamespace(
        returncode=0, stdout="SECRET-LOOKING-OUTPUT", stderr=""))
    assert client.post("/services/data/v68.0/sobjects/Payment", {"a": 1}) == {
        "_raw": "SECRET-LOOKING-OUTPUT"}
    for call in (lambda: lifecycle.create_payment(client, {"Amount": 1}),
                 lambda: lifecycle.apply_payment(client, "0aQ1", {"appliedToId": "5TV1", "amount": 1}),
                 lambda: lifecycle.submit_credit(client, "3ttINV", {"invoiceLines": []})):
        with pytest.raises(lifecycle.SettlementError) as info:
            call()
        assert "SECRET" not in str(info.value)
        assert "non-JSON response (21 characters, not shown)" in str(info.value)


def test_describe_response_keeps_json_errors() -> None:
    assert lifecycle.describe_response({"success": False, "errors": [{"message": "m"}]}) == \
        "errors [{'message': 'm'}]"
    assert lifecycle.describe_response(None) == "an empty response"
    assert "keys: ['success']" in lifecycle.describe_response({"success": True})
