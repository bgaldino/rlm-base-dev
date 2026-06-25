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
    _account_currency_map,
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
    # 3rd query: default Contact lookup (required for the ingestion path's
    # ``BillToContactId``). 001A has a Contact, 001B does not.
    fake_client.query_responses.append([{"Id": "003C-1", "AccountId": "001A"}])
    # 4th query: CurrencyIsoCode probe (multi-currency orgs need
    # ``Invoice.currencyIsoCode``). 001A has USD; 001B has none in the row.
    fake_client.query_responses.append([{"Id": "001A", "CurrencyIsoCode": "USD"}])
    # 5th query: address lookup (Billing + Shipping for both accounts). 001A
    # has a complete address; 001B has none -- discovery still emits the
    # account, the ingest path raises later when it sees the missing fields.
    fake_client.query_responses.append([
        {
            "Id": "001A",
            "BillingStreet": "1 Market", "BillingCity": "SF", "BillingState": "CA",
            "BillingPostalCode": "94104", "BillingCountry": "US",
            "ShippingStreet": "1 Market", "ShippingCity": "SF", "ShippingState": "CA",
            "ShippingPostalCode": "94104", "ShippingCountry": "US",
        },
    ])

    accounts = discover_any_accounts(fake_client, limit=25)

    assert [a.id for a in accounts] == ["001A", "001B"]
    assert accounts[0].name == "Infinitech"
    assert accounts[0].billing_account_id == "BA-1"
    assert accounts[0].bill_to_contact_id == "003C-1"
    assert accounts[0].currency_iso_code == "USD"
    assert accounts[0].billing_address is not None
    assert accounts[0].billing_address.is_complete
    assert accounts[0].shipping_address is not None
    # No BillingAccount row -> billing_account_id stays None; the ingestion
    # path uses Account.Id for Invoice.BillingAccountId anyway.
    assert accounts[1].billing_account_id is None
    # No Contact -> bill_to_contact_id stays None; ingestion will surface a
    # clear LifecycleError at the ingest step rather than silently fail.
    assert accounts[1].bill_to_contact_id is None
    assert accounts[1].currency_iso_code is None
    # No address row for 001B in the stubbed response -> stays None; ingest
    # raises a clear error rather than letting the org reject the payload.
    assert accounts[1].billing_address is None
    assert accounts[1].shipping_address is None

    # Five SOQL hits: FROM Account, FROM BillingAccount, FROM Contact,
    # CurrencyIsoCode probe, and the address lookup.
    assert len(fake_client.queries) == 5
    assert " FROM Account " in fake_client.queries[0]
    assert "FROM BillingAccount" in fake_client.queries[1]
    assert "AccountId IN" in fake_client.queries[1]
    assert "'001A'" in fake_client.queries[1]
    assert "'001B'" in fake_client.queries[1]
    assert "FROM Contact" in fake_client.queries[2]
    assert "AccountId IN" in fake_client.queries[2]
    assert "CurrencyIsoCode" in fake_client.queries[3]
    assert "BillingStreet" in fake_client.queries[4]
    assert "ShippingStreet" in fake_client.queries[4]


def test_discover_any_accounts_empty_skips_second_query(fake_client) -> None:
    fake_client.query_responses.append([])
    accounts = discover_any_accounts(fake_client, limit=5)
    assert accounts == []
    # Empty Account result means no AccountIds to filter on -- skip the
    # BillingAccount + Contact lookups so we don't ship empty IN-clauses to
    # SOQL.
    assert len(fake_client.queries) == 1


def test_account_currency_probe_cache_is_scoped_by_org_identity() -> None:
    class CurrencyClient:
        api_version = "67.0"
        alias = "same-local-alias"

        def __init__(self, instance_url: str, responses: list[object]):
            self.instance_url = instance_url
            self.responses = responses
            self.queries: list[str] = []

        def query(self, soql: str):
            self.queries.append(soql)
            response = self.responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

    single_currency = CurrencyClient(
        "https://single.example",
        [Exception("INVALID_FIELD: No such column 'CurrencyIsoCode' on Account")],
    )
    multi_currency = CurrencyClient(
        "https://multi.example",
        [[{"Id": "001B", "CurrencyIsoCode": "USD"}]],
    )

    assert _account_currency_map(single_currency, ["001A"]) == {}
    assert _account_currency_map(multi_currency, ["001B"]) == {"001B": "USD"}

    # The single-currency result is cached only for its own org key. A second
    # probe against that same org skips SOQL, but it did not suppress the
    # multi-currency org above even though both clients shared the same alias.
    assert _account_currency_map(single_currency, ["001A"]) == {}
    assert len(single_currency.queries) == 1
    assert len(multi_currency.queries) == 1


def test_account_currency_probe_does_not_cache_without_stable_org_identity() -> None:
    class AnonymousClient:
        api_version = "67.0"

        def __init__(self):
            self.queries: list[str] = []

        def query(self, soql: str):
            self.queries.append(soql)
            return [{"Id": "001A", "CurrencyIsoCode": "USD"}]

    client = AnonymousClient()

    assert _account_currency_map(client, ["001A"]) == {"001A": "USD"}
    assert _account_currency_map(client, ["001A"]) == {"001A": "USD"}
    assert len(client.queries) == 2


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
