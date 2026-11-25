"""Composable lifecycle step registry.

The low-level Salesforce calls live in ``lifecycle.py``. This module turns them
into named, stateful steps that operate on a manifest so full runs, resumable
ranges, and AI-facing commands all share the same sequencing rules.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Callable, Optional

from . import lifecycle
from .auth import SfRestClient
from .config import SettlementSpec, settlement_from_dict
from .discovery import Account, OrgContext
from .lifecycle import LifecycleError, SettlementError
from .models import (
    POSTED_STAGES,
    STAGES_SETTLEMENT,
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
    # Credit/payment options for credit_applied / payment_applied. ``None``
    # falls back to ``Manifest.settlement`` (a resumed run).
    settlement: Optional[SettlementSpec] = None
    # ``cli step --application-level``: replaces the level recorded on the
    # manifest (the way to correct a wrong read). ``None`` keeps it.
    application_level_override: Optional[str] = None


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
    # Any target at or after ``invoice_posted`` (the settlement stages too)
    # needs a Posted invoice, so ingest it Posted in one call.
    status = "Posted" if ctx.target_stage in POSTED_STAGES else "Draft"
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


# -- settlement (credit_applied / payment_applied) ---------------------------
#
# Concurrency: posting an invoice through the post action applies the
# account's open payment and credit balances to it (measured). A payment
# sits Processed and unapplied between its create and apply calls, so a
# sibling scenario posting an invoice for the same account in that gap would
# absorb it. The runner therefore refuses --concurrency > 1 when a batch has a
# settlement target on an account with more than one transaction
# (generate.settlement_concurrency_conflicts).


def _settlement_spec(ctx: StepContext, manifest: Manifest) -> Optional[SettlementSpec]:
    """The settlement block: fixed once it is recorded on the manifest.

    The first settlement step to start records the run's block
    (``ctx.settlement``), trimmed to the parts the run's target reaches (no
    ``payment`` when the target is ``credit_applied``), so the manifest never
    holds options for a stage that is not run. From then on the recorded
    block is used and ``ctx.settlement`` is not read; ``cli step`` refuses a
    ``--config`` that differs from it (changed options = a new run).
    """
    if manifest.settlement is not None:
        return settlement_from_dict(manifest.settlement)
    spec = ctx.settlement
    if spec is None:
        return None
    if ctx.target_stage == "credit_applied" and spec.payment is not None:
        spec = SettlementSpec(
            application_level=spec.application_level, credit=spec.credit, payment=None
        )
    manifest.settlement = spec.to_dict()
    return spec


def _settlement_account_id(ctx: StepContext, manifest: Manifest) -> str:
    """The account the settlement records belong to: the invoice's.

    ``Invoice.BillingAccountId`` (an Account id) is the account whose balance
    the credit and payment settle; ``manifest.account_id`` stands in when the
    invoice does not say. ``cli step`` resolves its account by the manifest's
    ``account_id`` (by name only for an old manifest without one) and refuses
    an ``--account`` with another Id; this check repeats that against the
    invoice for every caller, before anything is written: a payment found or
    created under another account would be a second payment.
    """
    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    invoice_acct = header.get("BillingAccountId")
    account_id = invoice_acct or manifest.account_id
    if not account_id:
        raise SettlementError(
            "settlement",
            "cannot tell the invoice's account: no Invoice.BillingAccountId and no "
            "account_id on the manifest",
            record_id=manifest.invoice_id,
        )
    if invoice_acct and manifest.account_id and manifest.account_id != invoice_acct:
        raise SettlementError(
            "settlement",
            f"the invoice belongs to account {invoice_acct} but the manifest records "
            f"account {manifest.account_id}; settle it in the org by hand",
            record_id=manifest.invoice_id,
        )
    ctx_id = getattr(ctx.account, "id", None)
    if ctx_id and ctx_id != account_id:
        raise SettlementError(
            "settlement",
            f"account '{getattr(ctx.account, 'name', ctx_id)}' resolves to {ctx_id}, but "
            f"the invoice and manifest belong to account {account_id}; resume without "
            "--account (the manifest's account_id is used)",
            record_id=manifest.invoice_id,
        )
    manifest.account_id = account_id
    return account_id


def _ensure_application_level(
    ctx: StepContext, manifest: Manifest, spec: SettlementSpec
) -> str:
    """Resolve the application level once and record it on the manifest.

    Precedence: ``ctx.application_level_override`` (``cli step
    --application-level``, the way to correct a wrongly recorded level) >
    the level already on the manifest > a ``line``/``header`` pin in the
    settlement block > the org's setting, read once.
    """
    override = ctx.application_level_override
    if override and override == manifest.application_level:
        return override  # equal to the recorded level: accepted and ignored
    if override:
        if (
            manifest.payment_apply_target is not None
            and override != manifest.application_level
        ):
            raise SettlementError(
                "payment",
                f"--application-level {override}: the payment was already planned at "
                f"{manifest.application_level} level (amount and apply target are fixed "
                "before the first apply), so the level cannot change on this manifest. "
                "Start a new run with settlement.application_level pinned.",
                record_id=manifest.invoice_id,
            )
        if manifest.application_level and manifest.application_level != override:
            _warn(
                manifest,
                f"application level overridden on resume: {manifest.application_level} "
                f"-> {override}",
            )
        manifest.application_level = override
        manifest.application_level_source = "override"
        return override
    if manifest.application_level:
        return manifest.application_level
    if spec.application_level in (lifecycle.LEVEL_LINE, lifecycle.LEVEL_HEADER):
        level, source = spec.application_level, "config"
    else:
        level, source = lifecycle.read_application_level(ctx.client, manifest.invoice_id)
    manifest.application_level = level
    manifest.application_level_source = source
    return level


def _ensure_settlement_baseline(ctx: StepContext, manifest: Manifest) -> dict:
    """Snapshot the invoice before the harness applies anything.

    Anything already applied here was applied by the platform -- an account's
    unapplied payment and credit balances settle a newly posted invoice when
    Billing Settings turn that on. Also records the invoice currency and its
    decimal places, which every computed amount is rounded to. Recorded once;
    a resume keeps the first snapshot.
    """
    if manifest.settlement_baseline is not None:
        return manifest.settlement_baseline
    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    apps = lifecycle.read_invoice_applications(ctx.client, manifest.invoice_id)
    currency = header.get("CurrencyIsoCode")
    places = lifecycle.currency_decimal_places(ctx.client, currency)
    manifest.settlement_baseline = {
        "balance": lifecycle._money(header.get("Balance"), places),
        "total_amount_with_tax": lifecycle._money(header.get("TotalAmountWithTax"), places),
        "net_credits_applied": lifecycle._money(header.get("NetCreditsApplied"), places),
        "net_payments_applied": lifecycle._money(header.get("NetPaymentsApplied"), places),
        "currency": currency,
        "decimal_places": places,
        "foreign_payment_application_ids": [
            r["Id"] for r in apps["payment_line"] + apps["payment_header"]
        ],
        "foreign_credit_application_ids": [
            r["Id"] for r in apps["credit_line"] + apps["credit_header"]
        ],
    }
    if manifest.settlement_baseline["foreign_payment_application_ids"] or (
        manifest.settlement_baseline["foreign_credit_application_ids"]
    ):
        _warn(
            manifest,
            "invoice already had applications before settlement (applied by the "
            f"platform at post): payments {manifest.settlement_baseline['net_payments_applied']}, "
            f"credits {manifest.settlement_baseline['net_credits_applied']}",
        )
    _checkpoint(ctx, manifest)
    return manifest.settlement_baseline


def _places(manifest: Manifest) -> int:
    baseline = manifest.settlement_baseline or {}
    places = baseline.get("decimal_places")
    return 2 if places is None else int(places)


def _warn(manifest: Manifest, message: str) -> None:
    if message not in manifest.settlement_warnings:
        manifest.settlement_warnings.append(message)
    log.warning("%s: %s", manifest.run_id, message)


def _chosen_lines(
    ctx: StepContext, manifest: Manifest, selector: Optional[list]
) -> list[dict]:
    lines = lifecycle.order_invoice_lines(
        lifecycle.fetch_invoice_lines_for_settlement(ctx.client, manifest.invoice_id),
        manifest.invoice_line_ids,
    )
    return lifecycle.select_invoice_lines(lines, selector)


def _record_applications(
    manifest: Manifest, apps: dict, level: Optional[str], what: str
) -> tuple[list[str], float]:
    """Ids and total of the application rows at both levels.

    With a known ``level``, rows at the other level are recorded too, with a
    warning. The credit passes ``None``: it reads both junctions by memo id
    and needs no level at all.
    """
    if level is None:
        rows = apps.get(lifecycle.LEVEL_LINE, []) + apps.get(lifecycle.LEVEL_HEADER, [])
        total = sum(float(r.get("Amount") or 0) for r in rows)
        return [r["Id"] for r in rows], lifecycle._money(total, _places(manifest))
    other = lifecycle.LEVEL_HEADER if level == lifecycle.LEVEL_LINE else lifecycle.LEVEL_LINE
    if apps.get(other):
        _warn(
            manifest,
            f"{what} applications found at {other} level although the org reads "
            f"{level} level: {[r['Id'] for r in apps[other]]}",
        )
    rows = apps.get(level, []) + apps.get(other, [])
    total = sum(float(r.get("Amount") or 0) for r in rows)
    return [r["Id"] for r in rows], lifecycle._money(total, _places(manifest))


def _poll_applications(read, timeout: int) -> dict:
    """Read application rows until some exist or ``timeout`` passes."""
    deadline = time.monotonic() + timeout
    apps = read()
    while not (apps[lifecycle.LEVEL_LINE] or apps[lifecycle.LEVEL_HEADER]):
        if time.monotonic() >= deadline:
            break
        time.sleep(lifecycle._POLL_INTERVAL)
        apps = read()
    return apps


# How long the credit step waits for the memo after a credit POST whose
# outcome is unknown (5xx / transport / 2xx without success), and the
# payment step for its insert. A convenience only: safety comes from
# credit_submitted / payment_submitted, set before the write and cleared only
# by a 4xx (any 4xx: nothing was created).
_CREDIT_LOOKUP_WINDOW = 15


def _find_memo(ctx: StepContext, manifest: Manifest, wait: bool = False) -> Optional[dict]:
    deadline = time.monotonic() + min(_CREDIT_LOOKUP_WINDOW, ctx.poll_timeout)
    while True:
        memo = lifecycle.find_credit_memo(ctx.client, manifest.invoice_id, ctx.run_id)
        if memo is not None or not wait or time.monotonic() >= deadline:
            return memo
        time.sleep(lifecycle._POLL_INTERVAL)


def _step_command(ctx: StepContext, manifest: Manifest) -> str:
    stage = ctx.target_stage if ctx.target_stage in STAGES_SETTLEMENT else "credit_applied"
    return f"`cli step --manifest {manifest.run_id} --to-stage {stage}`"


def _check_fixed_amounts(spec: SettlementSpec, manifest: Manifest, places: int) -> None:
    """Refuse, before the first write, a fixed amount below one minor unit.

    Both fixed amounts (``credit.amount``, ``payment.amount``) are known once
    the invoice currency is; checking them here keeps a sub-unit payment from
    being refused only after the credit memo was posted. Percent and computed
    amounts are checked where they are computed.
    """
    for what, part in (("credit", spec.credit), ("payment", spec.payment)):
        amount = getattr(part, "amount", None) if part is not None else None
        if amount is not None and lifecycle._money(amount, places) <= 0:
            raise _below_minor_unit(what, manifest, places)


def _check_memo_applied(memo: dict, applied: float, places: int) -> None:
    """Fail unless this run's memo is applied in full to this invoice.

    Every memo the harness creates is for this one invoice, so what was
    applied to it (rows filtered by this invoice) must equal the memo's
    ``TotalAmountWithTax`` exactly (both rounded to the currency's decimal
    places), whatever its ``Balance``: any shortfall, even one minor unit,
    either stays on the memo (it would settle the account's next posted
    invoice) or was already absorbed by another invoice. Measured: every live
    memo applied exactly its total to its own invoice.
    """
    from decimal import Decimal

    total = lifecycle._money(memo.get("TotalAmountWithTax"), places)
    if Decimal(str(lifecycle._money(applied, places))) != Decimal(str(total)):
        raise SettlementError(
            "credit",
            f"credit memo {memo['Id']} applied {applied} to this invoice but its total "
            f"is {total}; the rest is unapplied or went to another invoice. "
            f"{lifecycle.CANNOT_SETTLE}",
            record_id=memo["Id"],
        )


def _below_minor_unit(what: str, manifest: Manifest, places: int):
    """A configured credit/payment that rounds to zero in the invoice currency.

    The lines have an open balance, so skipping would advance the stage with
    nothing written; refuse instead.
    """
    currency = (manifest.settlement_baseline or {}).get("currency") or "the org currency"
    return SettlementError(
        what,
        f"the configured {what} rounds to 0 in {currency} ({places} decimal places), "
        f"so nothing would be {'credited' if what == 'credit' else 'paid'}; use an "
        "amount of at least one minor unit. Start a new run with a larger amount.",
        record_id=manifest.invoice_id,
    )


def _client_error(what: str, exc, manifest: Manifest, detail: str):
    """The ``SettlementError`` for a 4xx: the server created nothing.

    Retryable (420/429, or a retryable ``errorCode``): transient -- a retry
    sends the same write again, which is safe because nothing exists yet.
    Otherwise a refusal: deterministic.
    """
    codes = ", ".join(lifecycle.api_error_codes(exc.body)) or "no errorCode"
    if lifecycle.is_retryable_client_error(exc):
        return SettlementError(
            what,
            f"{what} not accepted for now (HTTP {exc.status}, {codes}); nothing was "
            "created, so a retry sends it again",
            record_id=manifest.invoice_id,
            failure_class="transient",
        )
    return SettlementError(
        what,
        f"{what} refused: {lifecycle.api_error_text(exc.body)}. Nothing was created. "
        f"{detail}",
        record_id=manifest.invoice_id,
    )


_REFUSED_AGAIN = (
    "Rerunning sends the same {what} again and will normally be refused again; to "
    "change the options, start a new run."
)


def _unknown_outcome(what: str, failure: str, ctx: StepContext, manifest: Manifest, tag: str):
    return SettlementError(
        what,
        f"{what} outcome unknown ({failure}) and nothing with tag '{tag}' appeared yet; it "
        f"is never sent again. Rerun {_step_command(ctx, manifest)} to keep looking for "
        f"it; if it never appears, "
        f"{lifecycle.CANNOT_SETTLE[0].lower()}{lifecycle.CANNOT_SETTLE[1:]}",
        record_id=manifest.invoice_id,
    )


def _submit_credit_once(ctx: StepContext, manifest: Manifest, body: dict) -> None:
    """Send the run's one credit POST (the write rule shared with the payment).

    The ``NetCreditsApplied`` baseline and ``credit_submitted`` are
    checkpointed before the POST, so a crash or an unknown outcome leaves a
    manifest that looks the memo up by its tag instead of POSTing again. Any
    HTTP 4xx means nothing was created: it clears ``credit_submitted`` and
    fails the stage (transient when retryable, else a refusal). Anything else
    -- a 5xx, a transport failure, a 2xx without ``success`` -- waits briefly
    for the memo; if none shows up the stage fails for good.
    """
    from .auth import SfApiError

    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    manifest.credit_baseline = lifecycle._money(header.get("NetCreditsApplied"), _places(manifest))
    manifest.credit_submitted = True
    _checkpoint(ctx, manifest)
    try:
        lifecycle.submit_credit(ctx.client, manifest.invoice_id, body)
        return
    except SfApiError as exc:
        if lifecycle.is_client_error(exc):
            manifest.credit_submitted = False
            _checkpoint(ctx, manifest)
            raise _client_error(
                "credit", exc, manifest, _REFUSED_AGAIN.format(what="credit")
            ) from exc
        failure, cause = f"HTTP {exc.status}", exc
    except LifecycleError as exc:  # a 2xx without success
        failure, cause = exc.detail, exc
    if _find_memo(ctx, manifest, wait=True) is not None:
        return
    raise _unknown_outcome(
        "credit", failure, ctx, manifest, lifecycle.credit_tag(ctx.run_id)
    ) from cause


def _find_payment(
    ctx: StepContext, manifest: Manifest, account_id: str, wait: bool = False
) -> Optional[str]:
    deadline = time.monotonic() + min(_CREDIT_LOOKUP_WINDOW, ctx.poll_timeout)
    while True:
        payment_id = lifecycle.find_payment(ctx.client, account_id, ctx.run_id)
        if payment_id is not None or not wait or time.monotonic() >= deadline:
            return payment_id
        time.sleep(lifecycle._POLL_INTERVAL)


def _check_level_evidence(ctx: StepContext, manifest: Manifest, level: str) -> None:
    """Fail before the Payment insert when the org contradicts ``level``.

    A wrong level is otherwise first exercised by the apply, after the
    insert, leaving an unapplied Processed payment. Evidence, when there is
    any: the invoice's ``SettlementLevel`` (set once something was applied,
    e.g. by the credit stage), else the junction of any application row on
    the invoice. No evidence: proceed.
    """
    evidence, source = lifecycle.invoice_level_evidence(ctx.client, manifest.invoice_id)
    if evidence is None or evidence == level:
        return
    if manifest.payment_apply_target is None:
        how = (f"rerun {_step_command(ctx, manifest)[:-1]} --application-level {evidence}` "
               "to correct it")
    else:
        how = ("the payment is already planned, so start a new run with "
               f"settlement.application_level: {evidence}")
    raise SettlementError(
        "payment",
        f"the recorded application level is {level} but {source} says {evidence}; no "
        f"payment was inserted. {how}.",
        record_id=manifest.invoice_id,
    )


def _insert_payment_once(
    ctx: StepContext, manifest: Manifest, account_id: str, places: int
) -> str:
    """The run's one Payment: found by its tag, else inserted once.

    Same write rule as the credit: ``payment_submitted`` is checkpointed
    before the insert; any 4xx (nothing was created) clears it; anything else
    keeps it and the payment is looked up by its ``GatewayRefNumber`` tag
    (short wait) instead of being inserted again. Two payments under the tag
    fail (``lifecycle.find_payment``); none ever appearing after an unknown
    outcome fails too.
    """
    from .auth import SfApiError

    payment_id = _find_payment(ctx, manifest, account_id, wait=manifest.payment_submitted)
    if payment_id is not None:
        return payment_id
    tag = lifecycle.payment_tag(ctx.run_id)
    if manifest.payment_submitted:
        raise _unknown_outcome("payment", "an earlier insert", ctx, manifest, tag)
    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    body = lifecycle.build_payment_record(
        account_id, manifest.payment_amount, ctx.run_id,
        currency=header.get("CurrencyIsoCode"), places=places,
    )
    manifest.payment_submitted = True
    _checkpoint(ctx, manifest)
    try:
        return lifecycle.create_payment(ctx.client, body)
    except SfApiError as exc:
        if lifecycle.is_client_error(exc):
            manifest.payment_submitted = False
            _checkpoint(ctx, manifest)
            raise _client_error(
                "payment", exc, manifest, _REFUSED_AGAIN.format(what="payment")
            ) from exc
        failure, cause = f"HTTP {exc.status}", exc
    except LifecycleError as exc:  # a 2xx without an id
        failure, cause = exc.detail, exc
    payment_id = _find_payment(ctx, manifest, account_id, wait=True)
    if payment_id is not None:
        return payment_id
    raise _unknown_outcome("payment", failure, ctx, manifest, tag) from cause


def _check_no_other_credit(manifest: Manifest, header: dict) -> None:
    """Fail when the invoice gained credits this run's memo does not explain.

    ``NetCreditsApplied`` less the baseline read just before the POST must
    equal what this run's memo applied; any difference (another credit, a
    reversal) fails the stage. A manifest without ``credit_baseline`` falls
    back to ``settlement_baseline``.
    """
    places = _places(manifest)
    baseline = manifest.credit_baseline
    if baseline is None:
        baseline = (manifest.settlement_baseline or {}).get("net_credits_applied") or 0.0
    gained = lifecycle._money(float(header.get("NetCreditsApplied") or 0.0) - baseline, places)
    applied = lifecycle._money(manifest.credit_amount_applied or 0.0, places)
    if gained != applied:
        raise SettlementError(
            "credit",
            f"invoice NetCreditsApplied rose by {gained} since the baseline, but this "
            f"run's credit memo {manifest.credit_memo_ids} applied {applied}: another "
            f"credit was applied to the invoice. {lifecycle.CANNOT_SETTLE}",
            record_id=manifest.invoice_id,
        )


def run_credit(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Credit the Posted invoice (``settlement.credit``) and read back the result.

    One credit memo per run via the credit action, tagged ``<run> credit``.
    The amount is spread over the chosen lines, each capped at its open
    balance, so the memo is fully applied (a memo with an unapplied balance
    would settle the account's next posted invoice).

    What is guaranteed: at most one credit memo is created per run.
    ``credit_submitted`` is checkpointed before the POST; after that neither
    a scenario retry nor a ``cli step`` resume POSTs again -- they look the
    memo up by the tag. Only a 4xx (nothing created) clears it, so a rerun
    after a refusal sends the same credit again. A memo that ends in Error,
    Canceled or Voided, two memos under the tag, a memo not applied in full
    to this invoice, a recorded memo that can no longer be read (deleted, or
    no access), or a ``NetCreditsApplied`` gain the memo does not explain
    fail the stage for good: start a new run.
    """
    spec = _settlement_spec(ctx, manifest)
    if spec is None or spec.credit is None:
        manifest.reached_stage = "credit_applied"
        return manifest
    if not manifest.invoice_id:
        raise SettlementError("credit", "invoice_id is required before credit")
    _settlement_account_id(ctx, manifest)
    # The credit needs no application level: the action targets invoice
    # lines either way, and the read-back covers both junctions by memo id.
    _ensure_settlement_baseline(ctx, manifest)
    places = _places(manifest)
    _check_fixed_amounts(spec, manifest, places)

    if not manifest.credit_memo_ids:
        memo = _find_memo(ctx, manifest, wait=manifest.credit_submitted)
        if memo is None and manifest.credit_submitted:
            # Submitted earlier, outcome unknown, and still no memo: there is
            # nothing to poll for Posted; say so instead of waiting on it.
            raise _unknown_outcome(
                "credit", "it was sent earlier", ctx, manifest, lifecycle.credit_tag(ctx.run_id)
            )
        if memo is None:
            strategy = spec.credit.tax_strategy
            chosen = _chosen_lines(ctx, manifest, spec.credit.lines)

            def capacity(line: dict) -> float:
                return lifecycle.credit_capacity(line, strategy, places)

            open_amount = lifecycle._money(sum(capacity(r) for r in chosen), places)
            requested = lifecycle._money(
                spec.credit.amount if spec.credit.amount is not None
                else open_amount * spec.credit.percent / 100.0,
                places,
            )
            manifest.credit_amount_requested = requested
            if open_amount > 0 and requested <= 0:
                raise _below_minor_unit("credit", manifest, places)
            allocations = lifecycle.allocate(requested, chosen, capacity, places)
            if not allocations:
                _warn(manifest, "credit skipped: the chosen lines have no open balance")
                manifest.reached_stage = "credit_applied"
                return manifest
            total = lifecycle._money(sum(a for _, a in allocations), places)
            if total < requested:
                _warn(
                    manifest,
                    f"credit capped at the open balance of the chosen lines: "
                    f"{total} of {requested} requested",
                )
            body = lifecycle.build_credit_payload(
                allocations,
                ctx.run_id,
                {r["Id"]: lifecycle.line_tax_strategy(r, strategy) for r in chosen},
            )
            _submit_credit_once(ctx, manifest, body)
        try:
            memo = lifecycle.poll_credit_memo(
                ctx.client, manifest.invoice_id, ctx.run_id, timeout=ctx.poll_timeout,
            )
        except LifecycleError as exc:
            if "not Posted within" not in exc.detail:
                raise
            raise SettlementError(
                exc.step,
                f"{exc.detail}. Rerun {_step_command(ctx, manifest)} to keep waiting; the "
                "credit is never sent again.",
                record_id=exc.record_id,
            ) from exc
        manifest.credit_memo_ids = [memo["Id"]]
        _checkpoint(ctx, manifest)

    apps = _poll_applications(
        lambda: lifecycle.read_credit_applications(
            ctx.client, manifest.credit_memo_ids, manifest.invoice_id
        ),
        ctx.poll_timeout,
    )
    ids, applied = _record_applications(manifest, apps, None, "credit")
    manifest.credit_application_ids = ids
    manifest.credit_amount_applied = applied
    # By the recorded Id, not the tag: an edited Description must not skip
    # the check.
    memo_id = manifest.credit_memo_ids[0]
    memo = lifecycle.get_credit_memo(ctx.client, memo_id)
    if memo is None:
        raise SettlementError(
            "credit",
            f"recorded credit memo {memo_id} is not readable in the org (deleted, or "
            f"no access), so its application cannot be checked. {lifecycle.CANNOT_SETTLE}",
            record_id=memo_id,
        )
    _check_memo_applied(memo, applied, places)
    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    manifest.invoice_balance = lifecycle._money(header.get("Balance"), places)
    _check_no_other_credit(manifest, header)
    manifest.reached_stage = "credit_applied"
    return manifest


def _payment_open_amount(
    ctx: StepContext, manifest: Manifest, spec: SettlementSpec, level: str
) -> float:
    places = _places(manifest)
    if level == lifecycle.LEVEL_HEADER:
        if spec.payment.lines is not None:
            _warn(manifest, "payment 'lines' ignored at Header Level (applied to the invoice)")
        header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
        return lifecycle._money(header.get("Balance"), places)
    chosen = _chosen_lines(ctx, manifest, spec.payment.lines)
    return lifecycle._money(sum(float(r.get("Balance") or 0) for r in chosen), places)


def plan_payment(
    spec_payment, open_amount: float, places: int
) -> tuple[float, float, str]:
    """Return ``(payment_amount, apply_target, mode)`` for an open balance.

    ``exact`` pays the open balance; ``amount`` pays that much; ``percent``
    pays that share of the open balance. Amounts are rounded to the
    currency's decimal places. The apply target is capped at the open
    balance; the mode says how the payment compares to it.
    """
    if spec_payment.is_exact:
        amount = open_amount
    elif spec_payment.amount is not None:
        amount = lifecycle._money(spec_payment.amount, places)
    else:
        amount = lifecycle._money(open_amount * spec_payment.percent / 100.0, places)
    target = lifecycle._money(min(amount, open_amount), places)
    if amount == open_amount:
        mode = "exact"
    elif amount < open_amount:
        mode = "partial"
    else:
        mode = "over"
    return amount, target, mode


def run_payment(ctx: StepContext, manifest: Manifest) -> Manifest:
    """Create a processed payment and apply it to the Posted invoice.

    The payment is created only now, after the invoice is posted: a processed
    payment that exists when an invoice posts can be applied to it by the
    platform. At Line Level the amount is spread over the chosen lines (each
    up to its balance, one apply call per line); at Header Level it is applied
    to the invoice. Whatever the payment holds beyond the open balance
    (``over``) stays unapplied on the payment. At most one payment is created
    per run (:func:`_insert_payment_once`, the credit's write rule); each
    apply is sent once, and a retry applies only the part not yet applied to
    this invoice (read back from the application records).
    """
    spec = _settlement_spec(ctx, manifest)
    if spec is None or spec.payment is None:
        # Never advance to payment_applied without a payment.
        if manifest.settlement is None:
            how = (
                f"pass `cli step --manifest {manifest.run_id} --to-stage payment_applied "
                "--config <file>` with a scenario of this kind and account whose "
                "settlement block has 'payment'"
            )
        else:
            how = (
                "the manifest's recorded settlement block is fixed; start a new run "
                "whose block has 'payment'"
            )
        raise SettlementError(
            "payment",
            f"no settlement 'payment', so payment_applied would create nothing: {how}.",
        )
    if not manifest.invoice_id:
        raise SettlementError("payment", "invoice_id is required before payment")
    account_id = _settlement_account_id(ctx, manifest)
    level = _ensure_application_level(ctx, manifest, spec)
    _ensure_settlement_baseline(ctx, manifest)
    places = _places(manifest)
    if not manifest.payment_ids and not manifest.payment_submitted:
        _check_level_evidence(ctx, manifest, level)

    if manifest.payment_apply_target is None:
        open_amount = _payment_open_amount(ctx, manifest, spec, level)
        if open_amount <= 0:
            _warn(manifest, "payment skipped: no open balance on the chosen lines")
            manifest.reached_stage = "payment_applied"
            return manifest
        amount, target, mode = plan_payment(spec.payment, open_amount, places)
        if amount <= 0:
            raise _below_minor_unit("payment", manifest, places)
        manifest.payment_amount = amount
        manifest.payment_apply_target = target
        manifest.payment_mode = mode
        if mode == "over":
            _warn(
                manifest,
                f"over-payment leaves {lifecycle._money(amount - target, places)} unapplied "
                "on the payment; the platform may apply it to the account's next posted invoice",
            )
        _checkpoint(ctx, manifest)

    if not manifest.payment_ids:
        payment_id = _insert_payment_once(ctx, manifest, account_id, places)
        manifest.payment_ids = [payment_id]
        _checkpoint(ctx, manifest)
    payment_id = manifest.payment_ids[0]

    def _read() -> dict:
        return lifecycle.read_payment_applications(
            ctx.client, manifest.payment_ids, manifest.invoice_id
        )

    def _total(apps: dict) -> float:
        rows = apps[lifecycle.LEVEL_LINE] + apps[lifecycle.LEVEL_HEADER]
        return lifecycle._money(sum(float(r.get("Amount") or 0) for r in rows), places)

    remaining = lifecycle._money(manifest.payment_apply_target - _total(_read()), places)
    if remaining > 0:
        if level == lifecycle.LEVEL_LINE:
            chosen = _chosen_lines(ctx, manifest, spec.payment.lines)
            allocations = lifecycle.allocate(
                remaining, chosen, lambda r: lifecycle._money(r.get("Balance"), places), places
            )
            targets = [(line_id, amt) for line_id, amt in allocations]
        else:
            header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
            amt = lifecycle._money(min(remaining, float(header.get("Balance") or 0)), places)
            targets = [(manifest.invoice_id, amt)] if amt > 0 else []
        for applied_to, amt in targets:
            app_id = lifecycle.apply_payment(
                ctx.client,
                payment_id,
                lifecycle.build_payment_apply_payload(
                    applied_to, amt, ctx.run_id, places=places
                ),
            )
            manifest.payment_application_ids.append(app_id)
            _checkpoint(ctx, manifest)

    ids, applied = _record_applications(manifest, _read(), level, "payment")
    manifest.payment_application_ids = ids
    manifest.payment_amount_applied = applied
    target = lifecycle._money(manifest.payment_apply_target, places)
    if lifecycle._money(applied, places) > target:
        raise SettlementError(
            "payment",
            f"payment {payment_id} applied {applied} to this invoice, more than the "
            f"{target} planned: an application outside this run's plan. "
            f"{lifecycle.CANNOT_SETTLE}",
            record_id=payment_id,
        )
    if applied < manifest.payment_apply_target:
        where = "the invoice" if level == lifecycle.LEVEL_HEADER else "the chosen lines"
        rest = lifecycle._money((manifest.payment_amount or 0) - applied, places)
        _warn(
            manifest,
            f"payment applied {applied} of the {manifest.payment_apply_target} planned "
            f"({where} had less open balance than planned); payment {payment_id} keeps "
            f"{rest} unapplied, which the platform may apply to the account's next "
            "posted invoice",
        )
    header = lifecycle.fetch_invoice_header(ctx.client, manifest.invoice_id)
    manifest.invoice_balance = lifecycle._money(header.get("Balance"), places)
    manifest.reached_stage = "payment_applied"
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
    # Settlement steps, shared by every kind (public stage name == step name).
    "credit_applied": StepSpec(
        name="credit_applied",
        requires=("invoice_id", "posted_invoice", "settlement"),
        outputs=(
            "application_level", "credit_memo_ids", "credit_application_ids",
            "credit_amount_applied",
        ),
        handler=run_credit,
    ),
    "payment_applied": StepSpec(
        name="payment_applied",
        requires=("invoice_id", "posted_invoice", "settlement"),
        outputs=(
            "application_level", "payment_ids", "payment_application_ids",
            "payment_amount_applied",
        ),
        handler=run_payment,
    ),
}


def execute_step(name: str, ctx: StepContext, manifest: Manifest) -> Manifest:
    """Execute one named step against the manifest."""
    from .auth import SfApiError

    try:
        spec = STEP_REGISTRY[name]
    except KeyError as exc:
        raise LifecycleError("step", f"unknown lifecycle step: {name}") from exc
    if name not in STAGES_SETTLEMENT:
        return spec.handler(ctx, manifest)
    try:
        return spec.handler(ctx, manifest)
    except SfApiError as exc:
        # Every SfApiError leaving a settlement step is pinned from its
        # structured fields (status, errorCode), so failure.py's text
        # matching never classifies it -- run ids hold digits like "503".
        raise SettlementError(
            name,
            f"{exc.method} {exc.path} failed (HTTP {exc.status}): "
            f"{lifecycle.api_error_text(exc.body)}",
            record_id=manifest.invoice_id,
            failure_class=lifecycle.settlement_failure_class(exc),
        ) from exc
