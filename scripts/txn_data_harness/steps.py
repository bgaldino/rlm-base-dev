"""Composable lifecycle step registry.

The low-level Salesforce calls live in ``lifecycle.py``. This module turns them
into named, stateful steps that operate on a manifest so full runs, resumable
ranges, and AI-facing commands all share the same sequencing rules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Callable, Optional

from . import lifecycle
from .auth import SfRestClient
from .discovery import Account, OrgContext
from .lifecycle import LifecycleError
from .models import (
    LineItem,
    Manifest,
    ResolvedInvoiceLine,
    ResolvedInvoiceOverrides,
)

log = logging.getLogger("txn_data_harness.steps")


@dataclass
class StepContext:
    """Resolved inputs a lifecycle step needs beyond the manifest.

    PST steps read ``lines`` (``LineItem``); the ingestion steps read
    ``invoice_lines`` (``ResolvedInvoiceLine``) and ``invoice_spec``. The two
    line types stay strictly separate per the handler-per-kind split
    (plan §1c / §2). ``target_stage`` lets the ingestion steps tell Draft
    from Posted runs without re-deriving from the manifest.
    """

    client: SfRestClient
    org_context: OrgContext
    run_id: str
    account: Account
    lines: list[LineItem]
    with_opportunity: bool
    poll_timeout: int
    start_date: Optional[date] = None
    checkpoint: Optional[Callable[[Manifest], None]] = None
    target_stage: Optional[str] = None
    billing_success_statuses: Optional[set[str]] = None
    invoice_lines: list[ResolvedInvoiceLine] = field(default_factory=list)
    invoice_spec: Optional[ResolvedInvoiceOverrides] = None
    # Resolved taxable ``TaxTreatment`` id for tax-on Posted ingestion. Set by
    # :class:`InvoiceIngestionHandler` when any ``invoice_lines`` entry has
    # ``taxable=True``; lifecycle stamps it on those InvoiceLine graph records
    # so the related InvoiceLineTax records are accepted.
    taxable_tax_treatment_id: Optional[str] = None


@dataclass(frozen=True)
class StepSpec:
    name: str
    requires: tuple[str, ...]
    outputs: tuple[str, ...]
    handler: Callable[[StepContext, Manifest], Manifest]


def _checkpoint(ctx: StepContext, manifest: Manifest) -> None:
    if ctx.checkpoint is not None:
        ctx.checkpoint(manifest)


def run_opportunity(ctx: StepContext, manifest: Manifest) -> Manifest:
    if ctx.org_context.opportunity_stage:
        manifest.opportunity_id = lifecycle.create_opportunity(
            ctx.client, ctx.account, ctx.org_context.opportunity_stage, ctx.run_id
        )
        manifest.reached_stage = "opportunity_created"
    return manifest


def run_quote(ctx: StepContext, manifest: Manifest) -> Manifest:
    try:
        manifest.quote_id = lifecycle.place_sales_transaction(
            ctx.client,
            ctx.account,
            ctx.lines,
            ctx.org_context.pricebook_id,
            ctx.run_id,
            opportunity_id=manifest.opportunity_id,
            start_date=ctx.start_date,
        )
    except LifecycleError as exc:
        # PST may commit the quote header even on failure. Checkpoint the orphan
        # id before re-raising so cleanup can find it.
        if exc.record_id:
            manifest.quote_id = exc.record_id
            _checkpoint(ctx, manifest)
        raise
    # Re-sync line records if lifecycle stamped resolved_end_date
    if any(line.resolved_end_date for line in ctx.lines):
        manifest.lines = [line.to_manifest_record() for line in ctx.lines]
    manifest.reached_stage = "quote_placed"
    return manifest


def run_order(ctx: StepContext, manifest: Manifest) -> Manifest:
    if not manifest.quote_id:
        raise LifecycleError("order", "quote_id is required before order")
    manifest.order_id, manifest.order_number = lifecycle.create_order_from_quote(
        ctx.client, manifest.quote_id
    )
    manifest.reached_stage = "order_draft"
    return manifest


def run_activate(ctx: StepContext, manifest: Manifest) -> Manifest:
    if not manifest.order_id:
        raise LifecycleError("activate", "order_id is required before activation")
    lifecycle.set_shipping_address(ctx.client, manifest.order_id, ctx.account)
    # OrderItem rows are the materialized line set after server-side bundle
    # expansion -- one input line carrying a bundle SKU produces many
    # OrderItems, and downstream activation produces one BillingSchedule (and
    # typically one Asset) per OrderItem. Using ``len(ctx.lines)`` here would
    # let the polls return as soon as the *input* count is met, before bundle
    # expansion finishes writing the rest -- a real risk on default-configured
    # bundles. See CONTRACTS.md "Bundles -- PST auto-expands ...".
    expected_count = lifecycle.count_order_items(ctx.client, manifest.order_id)
    lifecycle.activate_order(ctx.client, manifest.order_id)
    manifest.billing_schedule_ids = lifecycle.poll_billing_schedules(
        ctx.client,
        manifest.order_id,
        expected_count=expected_count,
        timeout=ctx.poll_timeout,
        success_statuses=ctx.billing_success_statuses,
    )
    # Asset poll is deterministic via AssetActionSource -- no expected_count
    # needed; it converges on a stable per-order set (handles bundle
    # expansion + AAS write lag in one). See CONTRACTS.md "Asset attribution".
    poll_result = lifecycle.poll_assets(
        ctx.client,
        manifest.order_id,
        timeout=ctx.poll_timeout,
    )
    manifest.asset_ids = poll_result.asset_ids
    manifest.asset_poll_status = poll_result.status
    manifest.reached_stage = "order_activated"
    return manifest


def run_usage(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Write TransactionJournal consumption rows for lines with ``usage``.

    Skip silently when no line opts in. Pair assets to lines by ``Product2Id``
    -- ``poll_assets`` returns ids ordered by id, not by quote-line order, so
    a positional zip would misroute journals when SKUs differ. Duplicate-SKU
    lines consume the per-product asset pool 1:1 by popping the head.
    """
    usage_lines = [l for l in ctx.lines if l.usage is not None]
    if not usage_lines:
        manifest.reached_stage = "usage_upload"
        return manifest
    if not manifest.asset_ids:
        raise LifecycleError(
            "usage", "no asset_ids on manifest; activate must run before usage"
        )

    asset_to_product = lifecycle.fetch_assets_product_ids(
        ctx.client, manifest.asset_ids
    )
    product_to_assets: dict[str, list[str]] = {}
    for aid, pid in asset_to_product.items():
        product_to_assets.setdefault(pid, []).append(aid)

    journal_ids: list[str] = []
    for line in usage_lines:
        candidates = product_to_assets.get(line.product.id, [])
        if not candidates:
            raise LifecycleError(
                "usage",
                f"no asset found for usage line {line.product.sku} "
                f"(product {line.product.id})",
            )
        asset_id = candidates.pop(0)
        journal_ids.extend(
            lifecycle.create_usage_journals(
                ctx.client,
                asset_id,
                ctx.account.id,
                line,
                ctx.run_id,
                now=datetime.now(timezone.utc),
            )
        )
    manifest.usage_journal_ids = journal_ids
    manifest.reached_stage = "usage_upload"
    return manifest


def run_invoice(ctx: StepContext, manifest: Manifest) -> Manifest:
    already_submitted = manifest.invoice_generate_submitted

    def _on_post_submitted() -> None:
        manifest.invoice_generate_submitted = True
        _checkpoint(ctx, manifest)

    manifest.invoice_id, manifest.invoice_number = lifecycle.generate_invoice(
        ctx.client, manifest.billing_schedule_ids, ctx.run_id, timeout=ctx.poll_timeout,
        already_submitted=already_submitted,
        on_submitted=_on_post_submitted,
    )
    lifecycle.tag_invoice(ctx.client, manifest.invoice_id, ctx.run_id)
    manifest.reached_stage = "invoice_draft"
    return manifest


def run_post(ctx: StepContext, manifest: Manifest) -> Manifest:
    if not manifest.invoice_id:
        raise LifecycleError("post", "invoice_id is required before post")
    manifest.invoice_number = lifecycle.post_invoice(
        ctx.client, manifest.invoice_id, ctx.run_id, timeout=ctx.poll_timeout
    )
    # Posting is the durable stage barrier. The order back-link is useful for
    # queries, but the lifecycle contract treats it as an optional convenience:
    # surface failures in the manifest/report instead of letting retry math
    # hide or re-post an already Posted invoice.
    if manifest.order_id:
        try:
            lifecycle.link_invoice_to_order(ctx.client, manifest.invoice_id, manifest.order_id)
            manifest.invoice_order_link_status = "linked"
            manifest.invoice_order_link_error = None
        except Exception as exc:  # noqa: BLE001 -- optional post-link warning
            manifest.invoice_order_link_status = "failed"
            manifest.invoice_order_link_error = str(exc)
            log.warning(
                "invoice %s posted but order link failed: %s",
                manifest.invoice_id,
                exc,
            )
    else:
        manifest.invoice_order_link_status = "skipped"
        manifest.invoice_order_link_error = None
    manifest.reached_stage = "invoice_posted"
    return manifest


def run_ingest_invoice(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Ingest one Invoice (Draft or Posted) via the ingest API.

    Step for the ``invoice_ingestion`` handler. Status is derived from
    ``ctx.target_stage`` (``post`` -> Posted, anything else -> Draft) so a
    scenario targeting only ``invoice`` lands a Draft and a scenario targeting
    ``post`` lands a Posted invoice in a single ingest call. The follow-on
    ``promote_to_posted`` step is a no-op in that case (manifest already at
    ``reached_stage=post``); it only does real work on a Draft-then-Posted
    resume.
    """
    status = "Posted" if ctx.target_stage == "invoice_posted" else "Draft"
    try:
        invoice_id, invoice_number, line_ids = lifecycle.ingest_invoice(
            ctx.client,
            ctx.account,
            ctx.invoice_lines,
            ctx.run_id,
            status=status,
            invoice_spec=ctx.invoice_spec,
            tax_treatment_id=ctx.org_context.non_taxable_tax_treatment_id,
            taxable_tax_treatment_id=ctx.taxable_tax_treatment_id,
            timeout=ctx.poll_timeout,
        )
    except LifecycleError as exc:
        if exc.record_id:
            manifest.invoice_id = exc.record_id
            _checkpoint(ctx, manifest)
        raise
    manifest.invoice_id = invoice_id
    manifest.invoice_number = invoice_number
    manifest.invoice_line_ids = list(line_ids)
    manifest.creation_mode = "External"
    # Reuse the existing Manifest.lines slot for the resolved invoice line
    # records. ``summarize_manifest`` dispatches on ``manifest.kind`` so the
    # ingestion summary surfaces these as ``invoice_lines`` while PST
    # manifests keep using ``lines`` for placed QuoteLineItem rows.
    manifest.lines = [
        {
            "name": ln.name,
            "sku": ln.sku,
            "quantity": ln.quantity,
            "unit_price": ln.unit_price,
            "charge_amount": ln.charge_amount,
            "product_id": ln.product.id if ln.product is not None else None,
            "taxable": ln.taxable,
            "tax": (
                {
                    "amount": ln.tax.amount,
                    "rate": ln.tax.rate,
                    "name": ln.tax.name,
                    "code": ln.tax.code,
                }
                if ln.tax is not None
                else None
            ),
        }
        for ln in ctx.invoice_lines
    ]
    manifest.reached_stage = "invoice_posted" if status == "Posted" else "invoice_draft"
    return manifest


def run_promote_to_posted(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Promote a Draft ingested invoice to Posted, reusing its id.

    No-op fast path: if ``ingest_invoice`` already produced a Posted invoice
    in the same run, ``reached_stage`` is already ``invoice_posted`` and
    there's nothing to do. Otherwise:

    1. Read back every ``InvoiceLine.TaxTreatmentId`` on the Draft. If any
       line has no treatment stamped, refuse to proceed -- the post action
       would otherwise resolve the org's default taxable policy and silently
       tax the line (verified live 2026-06-25 on rlm-base__jun17_1: an
       unstamped $100 line posts as a $10 taxable invoice). ``InvoiceLine.
       TaxTreatmentId`` is not updateable per describe, so a PATCH fixup
       is not available; the operator must delete the Draft manifest and
       re-ingest after seeding a non-taxable TaxTreatment.
    2. Call :func:`lifecycle.post_invoice` on the manifest's invoice id --
       the same endpoint the PST flow uses, no new lifecycle call needed.
    """
    if manifest.reached_stage == "invoice_posted":
        return manifest
    if not manifest.invoice_id:
        raise LifecycleError(
            "promote_to_posted",
            "invoice_id is required before promote_to_posted",
        )
    line_rows = ctx.client.query(
        "SELECT Id, TaxTreatmentId FROM InvoiceLine "
        f"WHERE InvoiceId = '{manifest.invoice_id}'"
    )
    untagged = [r["Id"] for r in line_rows if not r.get("TaxTreatmentId")]
    if untagged:
        raise LifecycleError(
            "promote_to_posted",
            f"Draft invoice {manifest.invoice_id} has {len(untagged)} "
            f"InvoiceLine row(s) with no TaxTreatmentId stamped. The post "
            "action would silently apply the org's default taxable policy. "
            "InvoiceLine.TaxTreatmentId is not updateable, so the Draft "
            "cannot be retro-tagged: delete the Draft and re-ingest with "
            "an active non-taxable TaxTreatment present in the org "
            "(Setup -> Tax Treatments, IsTaxable=false, Status=Active).",
            record_id=manifest.invoice_id,
        )
    manifest.invoice_number = lifecycle.post_invoice(
        ctx.client, manifest.invoice_id, ctx.run_id, timeout=ctx.poll_timeout
    )
    manifest.reached_stage = "invoice_posted"
    return manifest


def run_order_direct(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Direct-Order PST: place an Order via the same PST `place` endpoint with
    Order/OrderItem graph entities, then create the AppUsageAssignment row that
    gates the Revenue Cloud assetization pipeline.

    Without the AUA row, ``Order.Status = 'Activated'`` is a silent no-op (no
    BillingSchedule, no Asset, no AsyncOperationTracker). ``createOrderFromQuote``
    writes it implicitly on the quote path; PST place against the Order graph
    does not -- so this step writes it before yielding to ``run_activate``.
    See docs/contracts-sales-txn-order.md §2a.
    """
    try:
        manifest.order_id, manifest.order_number = lifecycle.place_order_transaction(
            ctx.client,
            ctx.account,
            ctx.lines,
            ctx.org_context.pricebook_id,
            ctx.run_id,
            start_date=ctx.start_date,
        )
    except LifecycleError as exc:
        if exc.record_id:
            manifest.order_id = exc.record_id
            _checkpoint(ctx, manifest)
        raise
    if any(line.resolved_end_date for line in ctx.lines):
        manifest.lines = [line.to_manifest_record() for line in ctx.lines]
    lifecycle.create_app_usage_assignment(ctx.client, manifest.order_id)
    manifest.reached_stage = "order_draft"
    return manifest


STEP_REGISTRY: dict[str, StepSpec] = {
    "opportunity_created": StepSpec(
        name="opportunity_created",
        requires=("account", "opportunity_stage"),
        outputs=("opportunity_id",),
        handler=run_opportunity,
    ),
    "quote_placed": StepSpec(
        name="quote_placed",
        requires=("account", "lines", "pricebook_id"),
        outputs=("quote_id",),
        handler=run_quote,
    ),
    # PST quote-path order creation. ``SalesTxnQuoteHandler`` maps public stage
    # ``order_draft`` -> internal step ``order_from_quote`` via its STEP_GRAPH.
    "order_from_quote": StepSpec(
        name="order_from_quote",
        requires=("quote_id",),
        outputs=("order_id", "order_number"),
        handler=run_order,
    ),
    # PST direct-order step used by SalesTxnOrderHandler.
    "order_direct": StepSpec(
        name="order_direct",
        requires=("account", "lines", "pricebook_id"),
        outputs=("order_id", "order_number"),
        handler=run_order_direct,
    ),
    "order_activated": StepSpec(
        name="order_activated",
        requires=("billing_ready_account", "order_id"),
        outputs=("billing_schedule_ids", "asset_ids"),
        handler=run_activate,
    ),
    "usage_upload": StepSpec(
        name="usage_upload",
        requires=("asset_ids",),
        outputs=("usage_journal_ids",),
        handler=run_usage,
    ),
    "invoice_draft": StepSpec(
        name="invoice_draft",
        requires=("billing_schedule_ids",),
        outputs=("invoice_id",),
        handler=run_invoice,
    ),
    "invoice_posted": StepSpec(
        name="invoice_posted",
        requires=("invoice_id",),
        outputs=("invoice_number",),
        handler=run_post,
    ),
    # Invoice-ingestion steps. The ingestion handler's STEP_GRAPH wires them
    # in -- the sales_txn_quote handler never references them.
    "ingest_invoice": StepSpec(
        name="ingest_invoice",
        requires=("account", "invoice_lines"),
        outputs=("invoice_id",),
        handler=run_ingest_invoice,
    ),
    "promote_to_posted": StepSpec(
        name="promote_to_posted",
        requires=("invoice_id",),
        outputs=("invoice_number",),
        handler=run_promote_to_posted,
    ),
}


def execute_step(name: str, ctx: StepContext, manifest: Manifest) -> Manifest:
    """Execute one named step against the manifest."""
    try:
        spec = STEP_REGISTRY[name]
    except KeyError as exc:
        raise LifecycleError("step", f"unknown lifecycle step: {name}") from exc
    return spec.handler(ctx, manifest)
