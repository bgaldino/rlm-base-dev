"""Tests for ``lifecycle.ingest_invoice`` and the two new step handlers (PR 3).

These pin the composite-graph body shape, the Phase 1 tax invariants,
the AsyncOperationTracker reuse, the Draft/Posted branching, the
postedDate default, the readback-by-UniqueIdentifier fallback, and the
two new step handlers (`run_ingest_invoice` and `run_promote_to_posted`).
Nothing is wired through the handler/CLI yet -- the ingestion step
handler is callable directly with an explicit `StepContext`.
"""

from __future__ import annotations

from datetime import date

import pytest

from scripts.txn_data_harness.discovery import Account, InvoiceLineProduct
from scripts.txn_data_harness.lifecycle import (
    LifecycleError,
    ingest_invoice,
)
from scripts.txn_data_harness.models import (
    Manifest,
    ResolvedInvoiceLine,
    ResolvedInvoiceOverrides,
)
from scripts.txn_data_harness.steps import (
    StepContext,
    run_ingest_invoice,
    run_promote_to_posted,
)


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr("scripts.txn_data_harness.lifecycle.time.sleep", lambda _s: None)


def _basic_lines() -> list[ResolvedInvoiceLine]:
    return [
        ResolvedInvoiceLine(
            name="API Flex",
            quantity=10,
            unit_price=25.0,
            product=InvoiceLineProduct(id="01tFLEX", name="API Flex", sku="QB-API-FLEX"),
            sku="QB-API-FLEX",
        ),
    ]


def test_ingest_invoice_draft_body_shape(fake_client, billable_account) -> None:
    # Tracker GET returns Completed immediately so the lifecycle returns.
    fake_client.post_responses.append({
        "invoices": [
            {
                "invoiceId": "1nvDRAFT",
                "success": True,
                "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/AOT-1",
            }
        ]
    })
    fake_client.get_responses.append({"Status": "Completed"})
    # Readback: invoice number + invoice line ids.
    fake_client.query_responses.append([{"InvoiceNumber": None}])  # Draft -> None
    fake_client.query_responses.append([{"Id": "iln1"}, {"Id": "iln2"}])

    lines = _basic_lines() + [
        ResolvedInvoiceLine(
            name="Description-only",
            quantity=1,
            unit_price=100.0,
            product=None,  # no SKU resolution
            sku=None,
            line_start_date=date(2026, 1, 1),
            line_end_date=date(2026, 12, 31),
            description="Onboarding fee",
        ),
    ]
    invoice_id, number, line_ids = ingest_invoice(
        fake_client, billable_account, lines, "DEMO-INGEST",
        status="Draft",
    )
    assert invoice_id == "1nvDRAFT"
    assert number is None
    assert line_ids == ["iln1", "iln2"]

    # POST went to the ingest action endpoint.
    path, body = fake_client.posts[0]
    assert path.endswith("/commerce/invoicing/invoices/collection/actions/ingest")

    # Single-invoice contract: invoices[] always has length 1.
    assert len(body["invoices"]) == 1
    inv = body["invoices"][0]

    # Phase 1 invariant on the top-level invoice envelope.
    assert inv["shouldCalculateTax"] is False
    assert inv["taxCalculationStatus"] == "Pending"
    assert inv["correlationId"] == "DEMO-INGEST"

    # Composite graph node 0 is the Invoice POST.
    records = inv["graph"]["records"]
    assert records[0]["referenceId"] == "refInvoice"
    assert records[0]["method"] == "POST"
    assert records[0]["url"].endswith("/sobjects/Invoice")
    invoice_body = records[0]["body"]
    # Account.Id is the FK target -- NOT BillingAccount.Id.
    assert invoice_body["billingAccountId"] == "001BILLABLE"
    assert invoice_body["uniqueIdentifier"] == "DEMO-INGEST"
    assert invoice_body["status"] == "Draft"
    # Drafts do NOT carry a postedDate.
    assert "postedDate" not in invoice_body

    # Lines: cross-ref invoiceId via @{refInvoice.id}; chargeAmount derives
    # from qty * unitPrice when not explicitly supplied; product2Id is
    # attached only when product is bound.
    line_rec1 = records[1]["body"]
    assert line_rec1["invoiceId"] == "@{refInvoice.id}"
    assert line_rec1["product2Id"] == "01tFLEX"
    assert line_rec1["quantity"] == 10
    assert line_rec1["unitPrice"] == 25.0
    assert line_rec1["chargeAmount"] == 250.0
    assert line_rec1["taxable"] is False  # Phase 1 invariant

    line_rec2 = records[2]["body"]
    assert "product2Id" not in line_rec2  # no product binding
    assert line_rec2["description"] == "Onboarding fee"
    assert line_rec2["lineStartDate"] == "2026-01-01"
    assert line_rec2["lineEndDate"] == "2026-12-31"

    # No InvoiceLineTax records ever in Phase 1.
    assert not any(
        r.get("url", "").endswith("/sobjects/InvoiceLineTax") for r in records
    )


def test_ingest_invoice_posted_defaults_posted_date(fake_client, billable_account) -> None:
    fake_client.post_responses.append({
        "invoices": [{"invoiceId": "1nvPOSTED", "success": True, "statusURL": "/sURL"}]
    })
    fake_client.get_responses.append({"Status": "Completed"})
    fake_client.query_responses.append([{"InvoiceNumber": "INV-0001"}])
    fake_client.query_responses.append([{"Id": "iln1"}])

    invoice_id, number, _ = ingest_invoice(
        fake_client, billable_account, _basic_lines(), "DEMO-POST",
        status="Posted",
    )
    assert invoice_id == "1nvPOSTED"
    assert number == "INV-0001"

    invoice_body = fake_client.posts[0][1]["invoices"][0]["graph"]["records"][0]["body"]
    assert invoice_body["status"] == "Posted"
    # postedDate is defaulted to today for Posted invoices.
    assert invoice_body["postedDate"] == date.today().isoformat()


def test_ingest_invoice_respects_overrides(fake_client, billable_account) -> None:
    fake_client.post_responses.append({
        "invoices": [{"invoiceId": "1nvOV", "success": True, "statusURL": "/sURL"}]
    })
    fake_client.get_responses.append({"Status": "Completed"})
    fake_client.query_responses.append([{"InvoiceNumber": "INV-0002"}])
    fake_client.query_responses.append([])

    overrides = ResolvedInvoiceOverrides(
        invoice_date=date(2026, 3, 1),
        due_date=date(2026, 3, 31),
        posted_date=date(2026, 3, 5),
        currency="USD",
        description="Q1 ingest test",
        tax_calculation_status="Estimated",
    )
    ingest_invoice(
        fake_client, billable_account, _basic_lines(), "DEMO-OV",
        status="Posted",
        invoice_spec=overrides,
    )
    inv = fake_client.posts[0][1]["invoices"][0]
    assert inv["taxCalculationStatus"] == "Estimated"
    invoice_body = inv["graph"]["records"][0]["body"]
    assert invoice_body["invoiceDate"] == "2026-03-01"
    assert invoice_body["dueDate"] == "2026-03-31"
    assert invoice_body["postedDate"] == "2026-03-05"
    assert invoice_body["currencyIsoCode"] == "USD"
    assert invoice_body["description"] == "Q1 ingest test"


def test_ingest_invoice_rejects_invalid_status(fake_client, billable_account) -> None:
    with pytest.raises(LifecycleError, match="invalid status"):
        ingest_invoice(
            fake_client, billable_account, _basic_lines(), "DEMO",
            status="Draft Pending Maybe",
        )


def test_ingest_invoice_rejects_empty_lines(fake_client, billable_account) -> None:
    with pytest.raises(LifecycleError, match="no invoice lines"):
        ingest_invoice(fake_client, billable_account, [], "DEMO")


def test_ingest_invoice_phase1_tax_invariant_rejects_should_calculate_tax(
    fake_client, billable_account
) -> None:
    overrides = ResolvedInvoiceOverrides(should_calculate_tax=True)
    with pytest.raises(LifecycleError, match="shouldCalculateTax must be false"):
        ingest_invoice(
            fake_client, billable_account, _basic_lines(), "DEMO",
            invoice_spec=overrides,
        )


def test_ingest_invoice_phase1_tax_invariant_rejects_taxable_line_on_posted(
    fake_client, billable_account
) -> None:
    taxable_line = ResolvedInvoiceLine(
        name="Taxed", quantity=1, unit_price=10.0, taxable=True
    )
    with pytest.raises(LifecycleError, match="taxable=true lines are not allowed"):
        ingest_invoice(
            fake_client, billable_account, [taxable_line], "DEMO",
            status="Posted",
        )


def test_ingest_invoice_action_failure_surfaces(fake_client, billable_account) -> None:
    fake_client.post_responses.append({
        "invoices": [{
            "success": False,
            "errors": [{"errorCode": "BAD", "message": "nope"}],
        }]
    })
    with pytest.raises(LifecycleError, match="ingest failed"):
        ingest_invoice(fake_client, billable_account, _basic_lines(), "DEMO")


def test_ingest_invoice_tracker_failure_surfaces(
    fake_client, billable_account, no_sleep
) -> None:
    fake_client.post_responses.append({
        "invoices": [{"invoiceId": "1nvX", "success": True, "statusURL": "/sURL"}]
    })
    fake_client.get_responses.append({"Status": "Failed"})
    with pytest.raises(LifecycleError, match="ingest_invoice tracker Failed"):
        ingest_invoice(
            fake_client, billable_account, _basic_lines(), "DEMO",
            status="Posted",
        )


def test_ingest_invoice_falls_back_to_unique_identifier_lookup(
    fake_client, billable_account
) -> None:
    # Action response with NO invoiceId -- exercise the readback-by-
    # UniqueIdentifier fallback path.
    fake_client.post_responses.append({
        "invoices": [{"success": True, "statusURL": "/sURL"}]
    })
    fake_client.get_responses.append({"Status": "Completed"})
    fake_client.query_responses.append(
        [{"Id": "1nvRECOVER", "InvoiceNumber": "INV-FALLBACK"}]
    )
    fake_client.query_responses.append([{"Id": "iln1"}])

    invoice_id, number, line_ids = ingest_invoice(
        fake_client, billable_account, _basic_lines(), "DEMO-FB",
    )
    assert invoice_id == "1nvRECOVER"
    assert number == "INV-FALLBACK"
    assert line_ids == ["iln1"]
    # First SOQL hit looks up by UniqueIdentifier.
    assert "UniqueIdentifier = 'DEMO-FB'" in fake_client.queries[0]


def test_ingest_invoice_works_for_non_billing_ready_account(fake_client) -> None:
    """The signature win of the ingestion path: Global Media etc. ingest fine
    even without a BillingAccount row. Verify ``billingAccountId`` resolves
    to ``Account.id``, not the (None) ``billing_account_id``."""
    pipeline_account = Account(id="001PIPE", name="Global Media", billing_account_id=None)
    fake_client.post_responses.append({
        "invoices": [{"invoiceId": "1nvPIPE", "success": True, "statusURL": "/sURL"}]
    })
    fake_client.get_responses.append({"Status": "Completed"})
    fake_client.query_responses.append([{"InvoiceNumber": None}])
    fake_client.query_responses.append([])

    ingest_invoice(fake_client, pipeline_account, _basic_lines(), "DEMO-PIPE")
    invoice_body = (
        fake_client.posts[0][1]["invoices"][0]["graph"]["records"][0]["body"]
    )
    assert invoice_body["billingAccountId"] == "001PIPE"


# ---------------------------------------------------------------------------
# Step handlers
# ---------------------------------------------------------------------------


def _ingest_ctx(fake_client, billable_account, target_stage, lines=None, spec=None):
    from scripts.txn_data_harness.discovery import OrgContext
    return StepContext(
        client=fake_client,
        org_context=OrgContext(
            pricebook_id="pb",
            pricebook_name="Standard",
            legal_entity_id=None,
            legal_entity_name=None,
            opportunity_stage=None,
            billing_ready_accounts=[],
            products=[],
        ),
        run_id="DEMO-STEP",
        account=billable_account,
        lines=[],
        invoice_lines=lines if lines is not None else _basic_lines(),
        invoice_spec=spec,
        with_opportunity=False,
        poll_timeout=1,
        target_stage=target_stage,
    )


def test_run_ingest_invoice_writes_draft_manifest(
    monkeypatch, fake_client, billable_account
) -> None:
    captured = {}

    def fake_ingest(client, account, lines, run_id, *, status, invoice_spec, timeout):
        captured["status"] = status
        return "1nvDRAFT", None, ["iln1"]

    monkeypatch.setattr("scripts.txn_data_harness.steps.lifecycle.ingest_invoice", fake_ingest)
    manifest = run_ingest_invoice(
        _ingest_ctx(fake_client, billable_account, target_stage="invoice"),
        Manifest(run_id="DEMO-STEP", kind="invoice_ingestion"),
    )
    assert captured["status"] == "Draft"
    assert manifest.invoice_id == "1nvDRAFT"
    assert manifest.invoice_number is None
    assert manifest.reached_stage == "invoice"
    # Resolved line records land on the shared lines slot for PR 3.
    assert manifest.lines and manifest.lines[0]["sku"] == "QB-API-FLEX"


def test_run_ingest_invoice_writes_posted_manifest(
    monkeypatch, fake_client, billable_account
) -> None:
    captured = {}

    def fake_ingest(client, account, lines, run_id, *, status, invoice_spec, timeout):
        captured["status"] = status
        return "1nvPOST", "INV-0042", ["iln1", "iln2"]

    monkeypatch.setattr("scripts.txn_data_harness.steps.lifecycle.ingest_invoice", fake_ingest)
    manifest = run_ingest_invoice(
        _ingest_ctx(fake_client, billable_account, target_stage="post"),
        Manifest(run_id="DEMO-STEP", kind="invoice_ingestion"),
    )
    assert captured["status"] == "Posted"
    assert manifest.invoice_id == "1nvPOST"
    assert manifest.invoice_number == "INV-0042"
    assert manifest.reached_stage == "post"


def test_run_promote_to_posted_is_noop_when_already_posted(
    monkeypatch, fake_client, billable_account
) -> None:
    def boom(*_a, **_kw):
        raise AssertionError("post_invoice should not be called on already-posted manifest")
    monkeypatch.setattr("scripts.txn_data_harness.steps.lifecycle.post_invoice", boom)

    manifest = Manifest(
        run_id="DEMO", kind="invoice_ingestion",
        invoice_id="1nvDONE", reached_stage="post",
    )
    result = run_promote_to_posted(
        _ingest_ctx(fake_client, billable_account, target_stage="post"),
        manifest,
    )
    assert result.reached_stage == "post"
    assert result.invoice_id == "1nvDONE"


def test_run_promote_to_posted_posts_existing_draft_id(
    monkeypatch, fake_client, billable_account
) -> None:
    captured = {}

    def fake_post(client, invoice_id, run_id, timeout):
        captured["invoice_id"] = invoice_id
        return "INV-PROMOTED"

    monkeypatch.setattr("scripts.txn_data_harness.steps.lifecycle.post_invoice", fake_post)
    manifest = Manifest(
        run_id="DEMO", kind="invoice_ingestion",
        invoice_id="1nvDRAFT", reached_stage="invoice",
    )
    result = run_promote_to_posted(
        _ingest_ctx(fake_client, billable_account, target_stage="post"),
        manifest,
    )
    # The existing Draft id is reused -- no second Invoice row.
    assert captured["invoice_id"] == "1nvDRAFT"
    assert result.invoice_id == "1nvDRAFT"
    assert result.invoice_number == "INV-PROMOTED"
    assert result.reached_stage == "post"


def test_run_promote_to_posted_requires_invoice_id(fake_client, billable_account) -> None:
    manifest = Manifest(run_id="DEMO", kind="invoice_ingestion", reached_stage="invoice")
    with pytest.raises(LifecycleError, match="invoice_id is required"):
        run_promote_to_posted(
            _ingest_ctx(fake_client, billable_account, target_stage="post"),
            manifest,
        )
