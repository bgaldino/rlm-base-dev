"""Tests for the Invoice Ingestion path's discovery + data model (PR 2).

These exercise the "dead code" additions made in PR 2: nothing wires the
ingestion path through dispatch yet, so the tests here pin behavior at the
data-model and resolver level.

* ``InvoiceLineProduct`` round-trips through the resolver,
* ``resolve_invoice_line_product`` returns ``None`` on a miss (not raises),
* ``discover_any_accounts`` queries Account directly and stitches
  ``billing_account_id`` from a second BillingAccount lookup keyed on
  AccountId (the ingestion path bypasses the billing-ready cap),
* ``ResolvedInvoiceLine`` / ``ResolvedInvoiceOverrides`` honour the Phase 1
  tax invariant defaults,
* ``InvoiceLineSpec`` / ``InvoiceOverrides`` config dataclasses construct
  with the documented defaults.
"""

from __future__ import annotations

from datetime import date

from scripts.txn_data_harness.config import InvoiceLineSpec, InvoiceOverrides
from scripts.txn_data_harness.discovery import (
    InvoiceLineProduct,
    discover_any_accounts,
    resolve_invoice_line_product,
)
from scripts.txn_data_harness.models import (
    ResolvedInvoiceLine,
    ResolvedInvoiceOverrides,
)


def test_resolve_invoice_line_product_hit(fake_client) -> None:
    fake_client.query_responses.append(
        [{"Id": "01tINV", "Name": "Cloud License", "StockKeepingUnit": "QB-LIC-CLOUD"}]
    )
    p = resolve_invoice_line_product(fake_client, "QB-LIC-CLOUD")
    assert p == InvoiceLineProduct(
        id="01tINV", name="Cloud License", sku="QB-LIC-CLOUD"
    )
    # SOQL filters by SKU + IsActive=true; no PBE join required.
    soql = fake_client.queries[0]
    assert "StockKeepingUnit = 'QB-LIC-CLOUD'" in soql
    assert "IsActive = true" in soql


def test_resolve_invoice_line_product_miss_returns_none(fake_client) -> None:
    fake_client.query_responses.append([])
    assert resolve_invoice_line_product(fake_client, "DOES-NOT-EXIST") is None


def test_resolve_invoice_line_product_escapes_sku(fake_client) -> None:
    # If a caller ever sneaks an apostrophe through, the resolver must quote it
    # rather than let SOQL break (or worse, run unintended clauses).
    fake_client.query_responses.append([])
    resolve_invoice_line_product(fake_client, "QB'API")
    assert "QB\\'API" in fake_client.queries[0]


def test_discover_any_accounts_stitches_billing_account_id(fake_client) -> None:
    # 1st query: Accounts (any billing state).
    fake_client.query_responses.append(
        [
            {"Id": "001A", "Name": "Infinitech"},
            {"Id": "001B", "Name": "Global Media"},
        ]
    )
    # 2nd query: BillingAccount rows keyed by AccountId. 001A has one, 001B
    # does not (mirrors the pipeline-only Account case).
    fake_client.query_responses.append([{"Id": "BA-1", "AccountId": "001A"}])

    accounts = discover_any_accounts(fake_client, limit=25)

    assert [a.id for a in accounts] == ["001A", "001B"]
    assert accounts[0].name == "Infinitech"
    assert accounts[0].billing_account_id == "BA-1"
    # No BillingAccount row -> billing_account_id stays None; the ingestion
    # path uses Account.Id for Invoice.BillingAccountId anyway.
    assert accounts[1].billing_account_id is None

    # Two SOQL hits: FROM Account, then FROM BillingAccount WHERE AccountId IN (...).
    assert len(fake_client.queries) == 2
    assert " FROM Account " in fake_client.queries[0]
    assert "FROM BillingAccount" in fake_client.queries[1]
    assert "AccountId IN" in fake_client.queries[1]
    assert "'001A'" in fake_client.queries[1]
    assert "'001B'" in fake_client.queries[1]


def test_discover_any_accounts_empty_skips_second_query(fake_client) -> None:
    fake_client.query_responses.append([])
    accounts = discover_any_accounts(fake_client, limit=5)
    assert accounts == []
    # Empty Account result means no AccountIds to filter on -- skip the second
    # query so we don't ship an empty IN-clause to SOQL.
    assert len(fake_client.queries) == 1


def test_invoice_line_spec_defaults_honour_tax_invariant() -> None:
    spec = InvoiceLineSpec(name="Standard Plan")
    assert spec.quantity == 1.0
    assert spec.unit_price == 0.0
    assert spec.sku is None
    assert spec.charge_amount is None
    assert spec.line_start_date is None
    assert spec.line_end_date is None
    # Phase 1 tax invariant: taxable defaults False.
    assert spec.taxable is False


def test_invoice_overrides_defaults_honour_tax_invariant() -> None:
    ov = InvoiceOverrides()
    assert ov.invoice_date is None
    assert ov.due_date is None
    assert ov.posted_date is None
    assert ov.currency is None
    # Phase 1 tax invariant: should_calculate_tax defaults False.
    assert ov.should_calculate_tax is False
    assert ov.tax_calculation_status is None


def test_resolved_invoice_line_round_trip_with_product() -> None:
    product = InvoiceLineProduct(id="01tINV", name="API", sku="QB-API")
    line = ResolvedInvoiceLine(
        name="API charge",
        quantity=2.0,
        unit_price=450.0,
        product=product,
        sku="QB-API",
        line_start_date=date(2026, 1, 1),
        line_end_date=date(2026, 12, 31),
    )
    assert line.product is product
    assert line.taxable is False  # Phase 1 invariant
    assert line.description is None


def test_resolved_invoice_overrides_defaults() -> None:
    ov = ResolvedInvoiceOverrides()
    assert ov.should_calculate_tax is False
    assert ov.invoice_date is None
    assert ov.tax_calculation_status is None
