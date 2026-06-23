"""Composable lifecycle step registry.

The low-level Salesforce calls live in ``lifecycle.py``. This module turns them
into named, stateful steps that operate on a manifest so full runs, resumable
ranges, and AI-facing commands all share the same sequencing rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Callable, Optional

from . import lifecycle
from .auth import SfRestClient
from .discovery import Account, OrgContext
from .lifecycle import LifecycleError
from .models import LineItem, Manifest


@dataclass
class StepContext:
    """Resolved inputs a lifecycle step needs beyond the manifest."""

    client: SfRestClient
    org_context: OrgContext
    run_id: str
    account: Account
    lines: list[LineItem]
    with_opportunity: bool
    poll_timeout: int
    start_date: Optional[date] = None
    checkpoint: Optional[Callable[[Manifest], None]] = None


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
        manifest.reached_stage = "opportunity"
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
    manifest.reached_stage = "quote"
    return manifest


def run_order(ctx: StepContext, manifest: Manifest) -> Manifest:
    if not manifest.quote_id:
        raise LifecycleError("order", "quote_id is required before order")
    manifest.order_id, manifest.order_number = lifecycle.create_order_from_quote(
        ctx.client, manifest.quote_id
    )
    manifest.reached_stage = "order"
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
    manifest.reached_stage = "activate"
    manifest.billing_schedule_ids = lifecycle.poll_billing_schedules(
        ctx.client,
        manifest.order_id,
        expected_count=expected_count,
        timeout=ctx.poll_timeout,
    )
    # Asset poll is deterministic via AssetActionSource -- no expected_count
    # needed; it converges on a stable per-order count (handles bundle
    # expansion + AAS write lag in one). See CONTRACTS.md "Asset attribution".
    manifest.asset_ids = lifecycle.poll_assets(
        ctx.client,
        manifest.order_id,
        timeout=ctx.poll_timeout,
    )
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
        manifest.reached_stage = "usage"
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
    manifest.reached_stage = "usage"
    return manifest


def run_invoice(ctx: StepContext, manifest: Manifest) -> Manifest:
    manifest.invoice_id, manifest.invoice_number = lifecycle.generate_invoice(
        ctx.client, manifest.billing_schedule_ids, ctx.run_id, timeout=ctx.poll_timeout
    )
    lifecycle.tag_invoice(ctx.client, manifest.invoice_id, ctx.run_id)
    manifest.reached_stage = "invoice"
    return manifest


def run_post(ctx: StepContext, manifest: Manifest) -> Manifest:
    if not manifest.invoice_id:
        raise LifecycleError("post", "invoice_id is required before post")
    manifest.invoice_number = lifecycle.post_invoice(
        ctx.client, manifest.invoice_id, ctx.run_id, timeout=ctx.poll_timeout
    )
    manifest.reached_stage = "post"
    if manifest.order_id:
        lifecycle.link_invoice_to_order(ctx.client, manifest.invoice_id, manifest.order_id)
    return manifest


STEP_REGISTRY: dict[str, StepSpec] = {
    "opportunity": StepSpec(
        name="opportunity",
        requires=("account", "opportunity_stage"),
        outputs=("opportunity_id",),
        handler=run_opportunity,
    ),
    "quote": StepSpec(
        name="quote",
        requires=("account", "lines", "pricebook_id"),
        outputs=("quote_id",),
        handler=run_quote,
    ),
    "order": StepSpec(
        name="order",
        requires=("quote_id",),
        outputs=("order_id", "order_number"),
        handler=run_order,
    ),
    "activate": StepSpec(
        name="activate",
        requires=("billing_ready_account", "order_id"),
        outputs=("billing_schedule_ids", "asset_ids"),
        handler=run_activate,
    ),
    "usage": StepSpec(
        name="usage",
        requires=("asset_ids",),
        outputs=("usage_journal_ids",),
        handler=run_usage,
    ),
    "invoice": StepSpec(
        name="invoice",
        requires=("billing_schedule_ids",),
        outputs=("invoice_id",),
        handler=run_invoice,
    ),
    "post": StepSpec(
        name="post",
        requires=("invoice_id",),
        outputs=("invoice_number",),
        handler=run_post,
    ),
}


def execute_step(name: str, ctx: StepContext, manifest: Manifest) -> Manifest:
    """Execute one named step against the manifest."""
    try:
        spec = STEP_REGISTRY[name]
    except KeyError as exc:
        raise LifecycleError("step", f"unknown lifecycle step: {name}") from exc
    return spec.handler(ctx, manifest)
