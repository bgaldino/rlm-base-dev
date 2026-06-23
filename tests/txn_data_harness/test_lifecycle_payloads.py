"""Tests for live-contract REST payload construction in lifecycle.py."""

from __future__ import annotations

from datetime import date

from scripts.txn_data_harness.lifecycle import (
    count_order_items,
    generate_invoice,
    place_sales_transaction,
    post_invoice,
)
from scripts.txn_data_harness.models import LineItem


def test_place_sales_transaction_builds_quote_graph_payload(
    fake_client, billable_account, term_product, evergreen_product
) -> None:
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0Q0QUOTE",
        "errorResponse": [],
    })
    lines = [
        LineItem(
            product=term_product,
            quantity=2,
            discount_percent=25,
            period_boundary="Anniversary",
            billing_frequency="Monthly",
        ),
        LineItem(product=evergreen_product, quantity=1),
    ]

    quote_id = place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-1",
        opportunity_id="006OPP",
        start_date=date(2026, 1, 15),
    )

    assert quote_id == "0Q0QUOTE"
    path, body = fake_client.posts[0]
    assert path.endswith("/connect/rev/sales-transaction/actions/place")
    records = body["graph"]["records"]
    quote = records[0]["record"]
    assert quote["QuoteAccountId"] == "001BILLABLE"
    assert quote["OpportunityId"] == "006OPP"
    assert "AccountId" not in quote

    term_line = records[1]["record"]
    assert term_line["StartDate"] == "2026-01-15"
    assert term_line["EndDate"] == "2027-01-10"
    assert term_line["Discount"] == 25
    assert term_line["PeriodBoundary"] == "Anniversary"
    assert term_line["BillingFrequency"] == "Monthly"
    assert "ProductSellingModelId" not in term_line

    evergreen_line = records[2]["record"]
    assert evergreen_line["StartDate"] == "2026-01-15"
    assert "EndDate" not in evergreen_line


def test_generate_invoice_posts_draft_request_and_polls_by_billing_schedule(fake_client) -> None:
    fake_client.post_responses.append({"success": True, "requestIdentifier": "REQ-1"})
    fake_client.query_responses.append([
        {
            "InvoiceId": "INV-ID",
            "Invoice": {"Status": "Draft", "InvoiceNumber": None},
        }
    ])

    invoice_id, number = generate_invoice(
        fake_client, ["BS-1", "BS-2"], "DEMO-1", timeout=1
    )

    assert invoice_id == "INV-ID"
    assert number is None
    path, body = fake_client.posts[0]
    assert path.endswith("/commerce/invoicing/invoices/collection/actions/generate")
    assert body["billingScheduleIds"] == ["BS-1", "BS-2"]
    assert body["action"] == "Draft"
    assert body["correlationId"] == "DEMO-1"
    assert "InvoiceLine WHERE BillingScheduleId IN ('BS-1', 'BS-2')" in fake_client.queries[0]


def test_generate_invoice_finds_invoice_when_first_schedule_has_no_invoice_line(fake_client) -> None:
    """Bundles activate into one BS per component; the first BS may be $0 with
    no InvoiceLine. The poller must query across all schedules and pick up the
    invoice via whichever one has a line.
    """
    fake_client.post_responses.append({"success": True, "requestIdentifier": "REQ-1"})
    # SOQL `IN (BS-0, BS-1, BS-2)` returns rows for BS-1 and BS-2 only -- BS-0
    # is the zero-amount slot and has no InvoiceLine. Our fake_client doesn't
    # filter by WHERE, so we just return the two real rows.
    fake_client.query_responses.append([
        {
            "InvoiceId": "INV-ID",
            "Invoice": {"Status": "Draft", "InvoiceNumber": None},
            "BillingScheduleId": "BS-1",
        },
        {
            "InvoiceId": "INV-ID",
            "Invoice": {"Status": "Draft", "InvoiceNumber": None},
            "BillingScheduleId": "BS-2",
        },
    ])

    invoice_id, _ = generate_invoice(
        fake_client, ["BS-0", "BS-1", "BS-2"], "DEMO-BUNDLE", timeout=1
    )

    assert invoice_id == "INV-ID"
    assert "BillingScheduleId IN ('BS-0', 'BS-1', 'BS-2')" in fake_client.queries[0]


def test_generate_invoice_single_schedule_still_polls_with_in_clause(fake_client) -> None:
    """Regression guard for the simple-product case: a single BS id polls with
    ``IN ('BS-1')`` (not the prior ``= 'BS-1'``), and behavior is unchanged.
    """
    fake_client.post_responses.append({"success": True, "requestIdentifier": "REQ-1"})
    fake_client.query_responses.append([
        {
            "InvoiceId": "INV-ID",
            "Invoice": {"Status": "Draft", "InvoiceNumber": None},
        }
    ])

    invoice_id, _ = generate_invoice(fake_client, ["BS-1"], "DEMO-SIMPLE", timeout=1)

    assert invoice_id == "INV-ID"
    assert "BillingScheduleId IN ('BS-1')" in fake_client.queries[0]


def test_count_order_items_returns_total_from_count_query(fake_client) -> None:
    fake_client.query_responses.append([{"total": 7}])

    n = count_order_items(fake_client, "801ORDER")

    assert n == 7
    assert (
        "SELECT COUNT(Id) total FROM OrderItem WHERE OrderId = '801ORDER'"
        in fake_client.queries[0]
    )


def test_count_order_items_falls_back_to_one_on_empty_result(fake_client) -> None:
    # Defensive: an order with zero OrderItems is a deterministic failure
    # downstream anyway, but the helper should not crash on an empty record list.
    fake_client.query_responses.append([])

    assert count_order_items(fake_client, "801ORDER") == 1


def test_count_order_items_handles_expr0_alias(fake_client) -> None:
    # Some SF responses surface COUNT(Id) under the auto-generated ``expr0``
    # key if the alias is dropped; the helper falls back to it defensively.
    fake_client.query_responses.append([{"expr0": 5}])

    assert count_order_items(fake_client, "801ORDER") == 5


def test_post_invoice_uses_status_url_and_reads_invoice_number(fake_client) -> None:
    fake_client.post_responses.append({
        "success": True,
        "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/TRACKER",
    })
    fake_client.get_responses.append({"Status": "Completed"})
    fake_client.query_responses.append([{"InvoiceNumber": "INV-0001"}])

    number = post_invoice(fake_client, "INV-ID", "DEMO-1", timeout=1)

    assert number == "INV-0001"
    path, body = fake_client.posts[0]
    assert path.endswith("/commerce/invoicing/invoices/collection/actions/post")
    assert body == {"invoiceIds": ["INV-ID"], "correlationId": "DEMO-1"}
    assert fake_client.gets == ["/services/data/v67.0/sobjects/AsyncOperationTracker/TRACKER"]
    assert "SELECT InvoiceNumber FROM Invoice WHERE Id = 'INV-ID'" in fake_client.queries[0]
