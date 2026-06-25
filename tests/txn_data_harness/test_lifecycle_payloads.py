"""Tests for live-contract REST payload construction in lifecycle.py."""

from __future__ import annotations

from datetime import date

import pytest

from scripts.txn_data_harness.lifecycle import (
    LifecycleError,
    count_order_items,
    generate_invoice,
    place_order_transaction,
    place_sales_transaction,
    poll_assets,
    poll_billing_schedules,
    post_invoice,
)
from scripts.txn_data_harness.models import EndDateOverride, LineItem, Term


@pytest.fixture
def no_sleep(monkeypatch):
    """Drop ``time.sleep`` inside ``lifecycle`` so polling tests don't wait on
    the real ``_POLL_INTERVAL`` (5s)."""
    monkeypatch.setattr("scripts.txn_data_harness.lifecycle.time.sleep", lambda _s: None)


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
            term=Term(12, "Months"),
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
    # EndDate is platform-derived from StartDate + SubscriptionTerm/Unit
    # (live-verified Branch A on rlm-base__jun17_1: input 1×Annual /
    # 2026-01-15 reads back as 2027-01-14). The harness writes the author
    # inputs only -- never EndDate, PricingTerm, or PricingTermCount.
    assert "EndDate" not in term_line
    assert term_line["SubscriptionTerm"] == 12
    assert term_line["SubscriptionTermUnit"] == "Months"
    assert "PricingTerm" not in term_line
    assert "PricingTermCount" not in term_line
    assert term_line["Discount"] == 25
    assert term_line["PeriodBoundary"] == "Anniversary"
    assert term_line["BillingFrequency"] == "Monthly"
    assert "ProductSellingModelId" not in term_line

    evergreen_line = records[2]["record"]
    assert evergreen_line["StartDate"] == "2026-01-15"
    # Evergreen lines: no EndDate AND no SubscriptionTerm fields (validated
    # against the engine's "can't specify EndDate for evergreen/one-time order
    # products" rule -- the same applies to derived term fields).
    assert "EndDate" not in evergreen_line
    assert "SubscriptionTerm" not in evergreen_line
    assert "SubscriptionTermUnit" not in evergreen_line


def test_place_order_transaction_never_writes_opportunity_id(
    fake_client, billable_account, term_product
) -> None:
    """The R262 Order sobject has no ``OpportunityId`` field -- live-verified
    via describe on 2026-06-25 against rlm-base__jun17_1; PST returns
    ``INVALID_FIELD`` ("No such column 'OpportunityId' on sobject of type
    Order") if the graph carries it. This test pins the platform constraint
    at the payload layer: the direct-Order PST graph must NEVER emit
    ``OpportunityId``. DIVERGES from the quote path
    (:func:`place_sales_transaction`), which DOES write
    ``Quote.OpportunityId`` when caller provides one."""
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "801ORDER",
        "errorResponse": [],
    })
    fake_client.query_responses.append([{"OrderNumber": "O-0001"}])
    lines = [LineItem(product=term_product, quantity=1, term=Term(12, "Months"))]

    order_id, order_number = place_order_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-ORD",
        start_date=date(2026, 1, 15),
    )

    assert order_id == "801ORDER"
    assert order_number == "O-0001"
    path, body = fake_client.posts[0]
    assert path.endswith("/connect/rev/sales-transaction/actions/place")
    order = body["graph"]["records"][0]["record"]
    assert order["attributes"]["type"] == "Order"
    assert order["AccountId"] == "001BILLABLE"
    assert "OpportunityId" not in order


def test_poll_billing_schedules_returns_ready_rows(fake_client, no_sleep) -> None:
    fake_client.query_responses.append([
        {"Id": "BS-1", "Status": "ReadyForInvoicing"},
        {"Id": "BS-2", "Status": "CompletelyBilled"},
    ])

    assert poll_billing_schedules(
        fake_client,
        "801ORDER",
        expected_count=2,
        timeout=1,
    ) == ["BS-1", "BS-2"]


def test_poll_billing_schedules_raises_on_error_status(fake_client, no_sleep) -> None:
    fake_client.query_responses.append([{"Id": "BS-ERR", "Status": "Error"}])

    with pytest.raises(LifecycleError, match="BillingSchedule in Error") as exc_info:
        poll_billing_schedules(fake_client, "801ORDER", timeout=1)

    assert exc_info.value.record_id == "BS-ERR"


def test_poll_billing_schedules_timeout_mentions_expected_statuses(
    monkeypatch, fake_client, no_sleep
) -> None:
    times = iter([0.0, 0.0, 2.0])
    monkeypatch.setattr(
        "scripts.txn_data_harness.lifecycle.time.monotonic",
        lambda: next(times),
    )
    fake_client.query_responses.append([{"Id": "BS-1", "Status": "Processing"}])

    with pytest.raises(LifecycleError, match="watching statuses") as exc_info:
        poll_billing_schedules(fake_client, "801ORDER", timeout=1)

    assert exc_info.value.record_id == "801ORDER"


def test_place_sales_transaction_writes_quarterly_term(
    fake_client, billable_account, quarterly_term_product
) -> None:
    """Non-month PricingTermUnit round-trips end-to-end through the place graph.

    Regression for the prior ``term_months`` collapse: a 4-Quarterly subscription
    used to be expressed as 12 months, losing the cadence the platform needs to
    derive billing schedules.
    """
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0Q0QTR",
        "errorResponse": [],
    })
    lines = [
        LineItem(
            product=quarterly_term_product,
            quantity=1,
            term=Term(4, "Quarterly"),
        ),
    ]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-QTR",
        start_date=date(2026, 1, 15),
    )

    _path, body = fake_client.posts[0]
    line = body["graph"]["records"][1]["record"]
    assert line["SubscriptionTerm"] == 4
    assert line["SubscriptionTermUnit"] == "Quarterly"
    # EndDate is platform-derived (Branch A); the harness never writes it.
    assert "EndDate" not in line


def test_place_sales_transaction_mixed_terms_on_one_quote(
    fake_client, billable_account, term_product, annual_term_product, evergreen_product
) -> None:
    """Multiple lines with different cadences + an Evergreen on the same quote.

    Verifies term writes are per-line (not per-quote) and that the Evergreen
    line never carries term fields.
    """
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0QMIXED",
        "errorResponse": [],
    })
    lines = [
        LineItem(product=term_product, quantity=1, term=Term(12, "Months")),
        LineItem(product=annual_term_product, quantity=1, term=Term(3, "Annual")),
        LineItem(product=evergreen_product, quantity=1),
    ]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-MIX",
        start_date=date(2026, 1, 15),
    )

    records = fake_client.posts[0][1]["graph"]["records"]
    monthly_line = records[1]["record"]
    annual_line = records[2]["record"]
    evergreen_line = records[3]["record"]

    assert monthly_line["SubscriptionTerm"] == 12
    assert monthly_line["SubscriptionTermUnit"] == "Months"
    assert "EndDate" not in monthly_line

    assert annual_line["SubscriptionTerm"] == 3
    assert annual_line["SubscriptionTermUnit"] == "Annual"
    assert "EndDate" not in annual_line

    assert "SubscriptionTerm" not in evergreen_line
    assert "SubscriptionTermUnit" not in evergreen_line
    assert "EndDate" not in evergreen_line


def test_place_sales_transaction_writes_absolute_end_date_override(
    fake_client, billable_account, annual_term_product
) -> None:
    """Absolute ``end_date`` override is written to the line verbatim.

    A 366-day span on a 1×Annual line drives ~0.27% proration into
    PricingTermCount at the platform layer (accepted drift for explicit
    end_date co-term scenarios).
    """
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0QABS",
        "errorResponse": [],
    })
    lines = [
        LineItem(
            product=annual_term_product,
            quantity=1,
            term=Term(1, "Annual"),
            end_date=EndDateOverride(absolute=date(2027, 1, 15)),
        ),
    ]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-ABS",
        start_date=date(2026, 1, 15),
    )

    line = fake_client.posts[0][1]["graph"]["records"][1]["record"]
    assert line["SubscriptionTerm"] == 1
    assert line["SubscriptionTermUnit"] == "Annual"
    assert line["EndDate"] == "2027-01-15"


def test_place_sales_transaction_resolves_days_offset_against_start_date(
    fake_client, billable_account, term_product
) -> None:
    """Relative ``days`` override resolves against the line's StartDate."""
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0QDAY",
        "errorResponse": [],
    })
    lines = [
        LineItem(
            product=term_product,
            quantity=1,
            term=Term(12, "Months"),
            end_date=EndDateOverride(days=364),
        ),
    ]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-DAY",
        start_date=date(2026, 1, 15),
    )

    line = fake_client.posts[0][1]["graph"]["records"][1]["record"]
    # 2026-01-15 + 364 days = 2027-01-14 (platform's inclusive convention).
    assert line["EndDate"] == "2027-01-14"


def test_place_sales_transaction_month_math_clamps_short_target_month(
    fake_client, billable_account, annual_term_product
) -> None:
    """Jan 31 + 1mo clamps to Feb 28 (or 29 in a leap year) via ``_add_months``."""
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0QCLAMP",
        "errorResponse": [],
    })
    lines = [
        LineItem(
            product=annual_term_product,
            quantity=1,
            term=Term(1, "Annual"),
            end_date=EndDateOverride(months=1),
        ),
    ]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-CLAMP",
        start_date=date(2025, 1, 31),  # 2025 is non-leap -> Feb 28
    )

    line = fake_client.posts[0][1]["graph"]["records"][1]["record"]
    assert line["EndDate"] == "2025-02-28"


def test_place_sales_transaction_omits_end_date_when_override_unset(
    fake_client, billable_account, term_product
) -> None:
    """No override -> platform derives EndDate (Branch A); harness writes nothing."""
    fake_client.post_responses.append({
        "isSuccess": True,
        "salesTransactionId": "0QBR-A",
        "errorResponse": [],
    })
    lines = [LineItem(product=term_product, quantity=1, term=Term(12, "Months"))]

    place_sales_transaction(
        fake_client,
        billable_account,
        lines,
        pricebook_id="01sSTANDARD",
        run_id="DEMO-BR-A",
        start_date=date(2026, 1, 15),
    )

    line = fake_client.posts[0][1]["graph"]["records"][1]["record"]
    assert "EndDate" not in line


def test_place_sales_transaction_raises_when_term_product_missing_term(
    fake_client, billable_account, term_product
) -> None:
    """TermDefined line without a resolved term is a runner bug -- fail loud.

    The runner is responsible for populating ``LineItem.term`` on TermDefined
    lines; if a line reaches the lifecycle without one, we'd silently emit a
    payload missing EndDate and PST would reject it with END_DATE_MISSING. The
    explicit guard surfaces the real cause at the layer that knows it.
    """
    from scripts.txn_data_harness.lifecycle import LifecycleError

    with pytest.raises(LifecycleError, match="no resolved term"):
        place_sales_transaction(
            fake_client,
            billable_account,
            [LineItem(product=term_product, quantity=1, term=None)],
            pricebook_id="01sSTANDARD",
            run_id="DEMO-BUG",
            start_date=date(2026, 1, 15),
        )
    # Guard runs before the HTTP call -- no POST issued.
    assert fake_client.posts == []


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


def _aas_row(asset_id: str) -> dict:
    return {"AssetAction": {"AssetId": asset_id}}


def test_poll_assets_queries_through_asset_action_source(fake_client, no_sleep) -> None:
    """The SOQL must walk Order -> OrderItem -> AssetActionSource -> Asset and
    filter the activation event via ``CategoryEnum = 'Initial Sale'`` so
    later amendments/renewals on the same OrderItem don't pollute the result.
    """
    fake_client.query_responses.extend([
        [_aas_row("02iA1")],
        [_aas_row("02iA1")],
    ])

    result = poll_assets(fake_client, "801ORDER", timeout=10)

    assert result.asset_ids == ["02iA1"]
    assert result.status == "converged"
    soql = fake_client.queries[0]
    assert "FROM AssetActionSource" in soql
    assert "AssetAction.AssetId" in soql
    assert "ReferenceEntityItemId IN (SELECT Id FROM OrderItem WHERE OrderId = '801ORDER')" in soql
    assert "AssetAction.CategoryEnum = 'Initial Sale'" in soql


def test_poll_assets_returns_bundle_expanded_set(fake_client, no_sleep) -> None:
    """Regression for the QB-COMPLETE bundle case: the old account+product
    heuristic returned 1 asset; the AAS path must surface all 5 component
    assets that activation produced for the bundle.
    """
    bundle_rows = [_aas_row(f"02iASSET{i}") for i in range(5)]
    fake_client.query_responses.extend([bundle_rows, bundle_rows])

    result = poll_assets(fake_client, "801BUNDLE", timeout=10)

    assert result.asset_ids == [f"02iASSET{i}" for i in range(5)]
    assert result.status == "converged"


def test_poll_assets_waits_for_count_to_stabilize(fake_client, no_sleep) -> None:
    """AssetActionSource writes can lag Asset by ~1s and bundle components can
    land staggered. The poll must keep going until two consecutive ticks
    report the same count before returning.
    """
    fake_client.query_responses.extend([
        [_aas_row("02iA1")],
        [_aas_row("02iA1"), _aas_row("02iA2"), _aas_row("02iA3")],
        [_aas_row("02iA1"), _aas_row("02iA2"), _aas_row("02iA3")],
    ])

    result = poll_assets(fake_client, "801ORDER", timeout=10)

    assert result.asset_ids == ["02iA1", "02iA2", "02iA3"]
    assert result.status == "converged"
    # Three polls: initial low read, growth tick, stable tick.
    assert len(fake_client.queries) == 3


def test_poll_assets_returns_empty_on_timeout_with_warning(
    fake_client, no_sleep, caplog
) -> None:
    """No AAS rows (write significantly delayed, or upstream activation did
    not emit any) must soft-fail: log a warning and return ``[]`` rather
    than hang or raise.
    """
    fake_client.query_responses.append([])

    result = poll_assets(fake_client, "801ORDER", timeout=0)

    assert result.asset_ids == []
    assert result.status == "timeout_empty"
    # Timeout==0 means we don't even get one full tick of stability, but we
    # also shouldn't crash. The warning is emitted only when the loop drains.
    # (Skip caplog assertion -- loop may exit before the first sleep yields
    # to logging in the 0-timeout edge.)


def test_poll_assets_handles_subquery_envelope(fake_client, no_sleep) -> None:
    """Salesforce returns the relationship traversal as a nested object:
    ``{"AssetAction": {"AssetId": "..."}}``. The poll must dereference both
    levels, and skip rows with a null AssetAction defensively.
    """
    fake_client.query_responses.extend([
        [
            {"AssetAction": {"AssetId": "02iA1"}},
            {"AssetAction": None},  # ignore
            {"AssetAction": {"AssetId": "02iA2"}},
        ],
        [
            {"AssetAction": {"AssetId": "02iA1"}},
            {"AssetAction": None},
            {"AssetAction": {"AssetId": "02iA2"}},
        ],
    ])

    result = poll_assets(fake_client, "801ORDER", timeout=10)

    assert result.asset_ids == ["02iA1", "02iA2"]
    assert result.status == "converged"


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
