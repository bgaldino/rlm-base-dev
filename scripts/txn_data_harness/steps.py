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
    since = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lifecycle.activate_order(ctx.client, manifest.order_id)
    manifest.reached_stage = "activate"
    manifest.billing_schedule_ids = lifecycle.poll_billing_schedules(
        ctx.client,
        manifest.order_id,
        expected_count=len(ctx.lines),
        timeout=ctx.poll_timeout,
    )
    manifest.asset_ids = lifecycle.poll_assets(
        ctx.client,
        ctx.account,
        [l.product for l in ctx.lines],
        since,
        expected_count=len(ctx.lines),
        timeout=ctx.poll_timeout,
    )
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
