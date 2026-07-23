"""Tests for the direct-Order PST handler (kind: ``sales_txn_order``).

Mirrors the coverage shape of ``test_handlers.py`` (quote-path) and
``test_invoice_ingestion_handler.py`` for the order path:

* registry registration + identity,
* :attr:`STAGES` omits ``quote_placed`` and :attr:`STEP_GRAPH` maps
  ``order_draft -> order_direct`` (the only divergence from the 1:1
  public-stage-to-internal-step default),
* :meth:`stage_sequence` agrees with the head/tail split (no Quote),
* :meth:`effective_stage` caps non-billing-ready accounts at
  ``order_draft`` -- same rule as the quote path because activation is
  shared,
* :meth:`remaining_steps` resume math for fresh / mid-run / at-target
  manifests,
* :meth:`summarize` shape mirrors the quote-path summary (the base
  handler owns it) but the manifest's ``quote`` slot is None.

Step-level behavior (the AppUsageAssignment POST that the direct-Order
path adds on top of PST place) is covered by
``test_order_direct_step_*`` in ``test_steps.py``; this file pins the
handler-level contract.
"""

from __future__ import annotations

from scripts.txn_data_harness.handlers import (
    SCENARIO_HANDLERS,
    SalesTxnOrderHandler,
)
from scripts.txn_data_harness.models import STAGES_ORDER, Manifest


# ---------------------------------------------------------------------------
# Registry + class-level shape
# ---------------------------------------------------------------------------


def test_sales_txn_order_handler_registered() -> None:
    handler = SCENARIO_HANDLERS["sales_txn_order"]
    assert isinstance(handler, SalesTxnOrderHandler)
    assert handler.kind == "sales_txn_order"


def test_stages_omit_quote_placed() -> None:
    """The order path skips the Quote step entirely. Including
    ``quote_placed`` in :attr:`STAGES` would let a config request
    ``target_stage: quote_placed`` against this kind and produce an
    impossible plan; we guard that here as a structural test instead of
    waiting for a config-layer regression."""
    handler = SalesTxnOrderHandler()
    assert "quote_placed" not in handler.STAGES
    assert handler.STAGES == STAGES_ORDER


def test_step_graph_maps_order_draft_to_order_direct() -> None:
    """``order_direct`` is the internal step name registered in
    :data:`scripts.txn_data_harness.steps.STEP_REGISTRY`; the public
    ``order_draft`` stage maps to it through STEP_GRAPH. The base handler
    falls back to the public name for any stage not listed here, so the
    map must NOT carry identity entries for the shared tail."""
    handler = SalesTxnOrderHandler()
    assert handler.STEP_GRAPH == {"order_draft": "order_direct"}


# ---------------------------------------------------------------------------
# Stage math
# ---------------------------------------------------------------------------


def test_stage_sequence_without_opportunity_starts_at_order_draft() -> None:
    """Without an Opportunity head, the order path's first stage is
    ``order_draft`` (NOT ``quote_placed`` -- there is no Quote)."""
    handler = SalesTxnOrderHandler()
    assert handler.stage_sequence("invoice_posted", with_opportunity=False) == [
        "order_draft", "order_activated", "usage_upload",
        "invoice_draft", "invoice_posted",
    ]


def test_stages_omit_opportunity_created() -> None:
    """The R262 Order sobject has no OpportunityId field (live-verified via
    describe on 2026-06-25 against rlm-base__jun17_1). The direct-Order PST
    graph cannot link an Order to an Opportunity, so the kind's STAGES omit
    ``opportunity_created`` entirely -- a config that requests it is
    rejected at parse time by :data:`_KIND_VALID_STAGES`."""
    handler = SalesTxnOrderHandler()
    assert "opportunity_created" not in handler.STAGES


def test_stage_sequence_ignores_with_opportunity_flag() -> None:
    """``with_opportunity`` is meaningless on the order kind: the Order
    sobject has no OpportunityId field. The flag's only effect on the
    quote path is to prepend the head stage; here the head is suppressed
    regardless. Config rejects ``with_opportunity: true`` upstream, so the
    runtime path is only reachable with False."""
    handler = SalesTxnOrderHandler()
    expected = [
        "order_draft", "order_activated", "usage_upload",
        "invoice_draft", "invoice_posted",
    ]
    assert handler.stage_sequence("invoice_posted", with_opportunity=False) == expected
    # Even if the flag did leak through, the head is structurally absent.
    assert handler.stage_sequence("invoice_posted", with_opportunity=True) == expected


def test_effective_stage_caps_non_billing_account_at_order_draft(pipeline_account) -> None:
    """Same rule as the quote path: activation generates BillingSchedules
    + Assets, which require a BillingAccount on the Account. Without one
    the order-path scenario caps at ``order_draft`` (which is where the
    direct-PST place + AppUsageAssignment happen). The cap math is shared
    on the base handler, but this test pins it for the order path's
    smaller STAGES list so an off-by-one in STAGES_ORDER would surface
    here."""
    handler = SalesTxnOrderHandler()
    assert handler.effective_stage("invoice_posted", pipeline_account) == "order_draft"
    assert handler.effective_stage("order_activated", pipeline_account) == "order_draft"
    assert handler.effective_stage("order_draft", pipeline_account) == "order_draft"


def test_effective_stage_preserves_billable_target(billable_account) -> None:
    handler = SalesTxnOrderHandler()
    assert handler.effective_stage("invoice_posted", billable_account) == "invoice_posted"


def test_remaining_steps_fresh_run_uses_full_sequence() -> None:
    handler = SalesTxnOrderHandler()
    assert handler.remaining_steps(None, "invoice_posted", with_opportunity=False) == [
        "order_draft", "order_activated", "usage_upload",
        "invoice_draft", "invoice_posted",
    ]


def test_remaining_steps_resumes_after_order_draft() -> None:
    """A resumed run that already placed the Order (and wrote the AUA row)
    skips ``order_draft`` and continues from the shared post-Order tail.
    This is the load-bearing resume case: the AUA POST is checkpointed by
    completing ``order_draft``, so a retry must NOT re-place the order."""
    handler = SalesTxnOrderHandler()
    assert handler.remaining_steps(
        "order_draft", "invoice_posted", with_opportunity=False
    ) == [
        "order_activated", "usage_upload", "invoice_draft", "invoice_posted",
    ]


def test_remaining_steps_empty_when_already_at_target() -> None:
    handler = SalesTxnOrderHandler()
    assert handler.remaining_steps(
        "invoice_posted", "invoice_posted", with_opportunity=False
    ) == []
    # And a manifest that overshot the requested target also returns []
    # (e.g. an inspect on a fully-posted run still shows reached_stage =
    # invoice_posted; running step --to-stage order_draft is a no-op).
    assert handler.remaining_steps(
        "invoice_draft", "order_draft", with_opportunity=False
    ) == []


# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------


def test_summarize_carries_order_ids_with_null_quote() -> None:
    """The order path reuses the PST-shaped summary on the base handler so
    inspect/report consumers don't need to branch on kind. The Quote slot
    is always None for this kind; this test pins that shape."""
    handler = SalesTxnOrderHandler()
    m = Manifest(
        run_id="DEMO-ORD-1",
        kind="sales_txn_order",
        account_name="Infinitech",
        order_id="801ORDER",
        billing_schedule_ids=["BS-1"],
        asset_ids=["A-1"],
        invoice_id="inv-1",
        invoice_number="INV-1",
        reached_stage="invoice_posted",
        start_date="2026-06-01",
        lines=[{"sku": "QB-API-FLEX", "quantity": 1}],
    )
    summary = handler.summarize(m)
    assert summary["kind"] == "sales_txn_order"
    assert summary["account"] == "Infinitech"
    assert summary["reached_stage"] == "invoice_posted"
    assert summary["ids"]["order"] == "801ORDER"
    assert summary["ids"]["quote"] is None  # order path never places a Quote
    assert summary["ids"]["opportunity"] is None
    assert summary["ids"]["billing_schedules"] == ["BS-1"]
    assert summary["ids"]["assets"] == ["A-1"]
    assert summary["ids"]["invoice"] == "inv-1"
    assert summary["invoice_number"] == "INV-1"
    assert summary["line_count"] == 1
