"""Invoice-ingestion scenario handler.

Drives the standalone-billing invoice ingestion path (Composite Graph ingest
action). Counterpart to :class:`SalesTransactionHandler`: same protocol, very
different lifecycle. The PST chain walks Opportunity -> Quote -> Order ->
Activate -> Usage -> Invoice -> Post; supported ingestion configs ship one POST
that creates a Draft invoice in a single composite-graph call. The Posted path
remains internal Phase 2 scaffolding until InvoiceLineTax prerequisites are
implemented and live-verified.

The handler owns its own step graph:

    invoice -> [ingest_invoice]
    post    -> [ingest_invoice, promote_to_posted]

``promote_to_posted`` is a no-op when ``ingest_invoice`` already produced a
Posted invoice in the same run (the handler's STEP_GRAPH for ``post`` always
includes both steps so the manifest-level resume math is simple -- the
no-op short-circuit lives in :func:`steps.run_promote_to_posted`).
"""

from __future__ import annotations

import logging
import time
from typing import Any, ClassVar, Optional

from ..auth import SfRestClient
from ..config import InvoiceIngestionScenarioSpec, InvoiceLineSpec
from ..discovery import (
    Account,
    DiscoveryError,
    OrgContext,
    discover_any_accounts,
    resolve_account,
    resolve_invoice_line_product,
)
from ..manifests import write_manifest
from ..models import (
    Manifest,
    ResolvedInvoiceIngestionSpec,
    ResolvedInvoiceLine,
    ResolvedInvoiceOverrides,
)
from ..failure import classify_exception
from ..runner import _retry_backoff, current_run_id
from ..steps import StepContext, execute_step

log = logging.getLogger("txn_data_harness.handlers.invoice_ingestion")


# Canonical ingestion step graph keyed by target stage. The handler owns this
# directly rather than delegating to ``runner.stage_sequence`` because the PST
# graph (in :mod:`scripts.txn_data_harness.models`) has no notion of
# ``ingest_invoice`` or ``promote_to_posted``.
STEP_GRAPH: dict[str, list[str]] = {
    "invoice_draft":  ["ingest_invoice"],
    "invoice_posted": ["ingest_invoice", "promote_to_posted"],
}


# Stage indices used by :meth:`remaining_steps` to compute resume math. The
# ingestion lifecycle has two terminal stages plus the implicit "not started"
# state (``reached_stage is None``); mapping each into a position lets the
# resume logic stay tabular instead of a tangle of conditionals.
_STAGE_INDEX = {
    None: 0,              # nothing checkpointed yet
    "invoice_draft": 1,   # Draft persisted
    "invoice_posted": 2,  # Posted persisted (terminal)
}


def _resolve_invoice_line(
    client: SfRestClient, spec: InvoiceLineSpec
) -> ResolvedInvoiceLine:
    """Resolve one config line into its post-resolve dataclass.

    ``sku`` is optional on the API; a SKU that doesn't match an active
    Product2 falls through to a description-only line (no ``product2Id``).
    The harness must never invent a product id, so this stays a soft-lookup.
    """
    product = (
        resolve_invoice_line_product(client, spec.sku) if spec.sku else None
    )
    return ResolvedInvoiceLine(
        name=spec.name,
        quantity=spec.quantity,
        unit_price=spec.unit_price,
        product=product,
        sku=spec.sku,
        charge_amount=spec.charge_amount,
        line_start_date=spec.line_start_date,
        line_end_date=spec.line_end_date,
        taxable=spec.taxable,
        description=spec.description,
    )


def _resolve_invoice_overrides(
    spec: InvoiceIngestionScenarioSpec,
) -> Optional[ResolvedInvoiceOverrides]:
    """Map an :class:`InvoiceOverrides` config block to its resolved form."""
    if spec.invoice is None:
        return None
    ov = spec.invoice
    return ResolvedInvoiceOverrides(
        invoice_date=ov.invoice_date,
        due_date=ov.due_date,
        posted_date=ov.posted_date,
        currency=ov.currency,
        description=ov.description,
        should_calculate_tax=ov.should_calculate_tax,
        tax_calculation_status=ov.tax_calculation_status,
    )


def _default_account(ctx: OrgContext, client: SfRestClient) -> Account:
    """Pick a default Account when the spec doesn't pin one.

    Unlike PST, ingestion accepts pipeline-only accounts. Prefer a
    billing-ready account if one was already discovered (so demos against a
    fully-configured org behave the same on PST and ingestion) and fall back
    to ``discover_any_accounts`` -- queries Account directly so it works
    against billing-only orgs that have no BillingAccount records.
    """
    if ctx.billing_ready_accounts:
        return ctx.billing_ready_accounts[0]
    candidates = discover_any_accounts(client, limit=25)
    if not candidates:
        raise DiscoveryError(
            "No accounts found in the org. Create an Account or pin one in "
            "config (kind: invoice_ingestion requires only an Account; a "
            "BillingAccount is optional)."
        )
    return candidates[0]


class InvoiceIngestionHandler:
    """Handler for ``kind: invoice_ingestion``.

    Drives standalone-billing demos where a customer ships Draft or Posted
    invoices directly via the Composite Graph ingest API, bypassing the PST
    chain entirely. Implements the :class:`ScenarioHandler` protocol so the
    dispatcher in ``generate.py`` / ``cli.py`` routes through it without
    branching on ``kind``.
    """

    kind: ClassVar[str] = "invoice_ingestion"

    def effective_stage(self, target_stage: str, account: Account) -> str:
        """Ingestion has no PST cap.

        PST's :func:`runner.effective_stage` caps non-billing-ready accounts
        at ``order`` because activation requires a BillingAccount. The
        ingestion path uses ``Account.Id`` directly as
        ``Invoice.BillingAccountId``, so even a pipeline-only account (no
        ``BillingAccount`` row) can ingest. Whatever the spec asks for is
        what we run.
        """
        return target_stage

    def stage_sequence(
        self, target_stage: str, with_opportunity: bool
    ) -> list[str]:
        """Return the ordered ingestion steps for ``target_stage``.

        ``with_opportunity`` is honored only for protocol parity with
        :class:`SalesTransactionHandler` -- ingestion has no Opportunity
        step. A request to prepend one would be silently dropped here; the
        config parser refuses ``with_opportunity: true`` on ingestion specs
        so we never get a True flag in practice.
        """
        del with_opportunity  # PST-only knob, see docstring
        try:
            return list(STEP_GRAPH[target_stage])
        except KeyError as exc:
            raise ValueError(
                f"invoice_ingestion: target_stage '{target_stage}' is not in "
                f"STEP_GRAPH (valid: {', '.join(sorted(STEP_GRAPH))})"
            ) from exc

    def remaining_steps(
        self,
        reached_stage: Optional[str],
        target_stage: str,
        with_opportunity: bool,
    ) -> list[str]:
        """Compute the steps still needed to reach ``target_stage``.

        Resume math for the four meaningful combinations:

            (None,    invoice) -> [ingest_invoice]
            (None,    post)    -> [ingest_invoice, promote_to_posted]
            (invoice, post)    -> [promote_to_posted]
            (post,    post)    -> []                       # already terminal

        A request to step a Posted invoice further (or to step back to
        Draft) yields ``[]`` -- there's nothing for the runner to do.
        """
        del with_opportunity  # PST-only knob
        if target_stage not in STEP_GRAPH:
            raise ValueError(
                f"invoice_ingestion: target_stage '{target_stage}' is not in "
                f"STEP_GRAPH (valid: {', '.join(sorted(STEP_GRAPH))})"
            )
        reached_idx = _STAGE_INDEX.get(reached_stage)
        if reached_idx is None:
            raise ValueError(
                f"invoice_ingestion: reached_stage '{reached_stage}' is not a "
                f"valid ingestion stage (valid: invoice, post)"
            )
        target_idx = _STAGE_INDEX[target_stage]
        if reached_idx >= target_idx:
            return []
        # Each contiguous slot in the graph corresponds to advancing exactly
        # one stage; ingest_invoice promotes 0 -> 1 (or 0 -> 2 directly when
        # target is post), promote_to_posted promotes 1 -> 2.
        full = STEP_GRAPH[target_stage]
        return list(full[reached_idx:])

    def resolve(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        spec: InvoiceIngestionScenarioSpec,
    ) -> ResolvedInvoiceIngestionSpec:
        """Bind the spec's account + invoice lines to org records.

        The spec's ``account`` (name) resolves to a concrete Account via
        :func:`resolve_account` -- works for both billing-ready and
        pipeline-only accounts because ingestion only needs ``Account.Id``.
        When the spec doesn't pin an account, :func:`_default_account`
        picks one (billing-ready if available; otherwise any Account).
        Each :class:`InvoiceLineSpec` resolves to a
        :class:`ResolvedInvoiceLine` whose optional Product2 binding is
        looked up via :func:`resolve_invoice_line_product` (a SKU miss
        falls through to a description-only line).
        """
        if spec.account:
            account = resolve_account(client, spec.account)
        else:
            account = _default_account(ctx, client)
        resolved_lines = [
            _resolve_invoice_line(client, ln) for ln in spec.invoice_lines
        ]
        overrides = _resolve_invoice_overrides(spec)
        return ResolvedInvoiceIngestionSpec(
            spec=spec,
            account=account,
            invoice_lines=resolved_lines,
            invoice_overrides=overrides,
            effective_stage=self.effective_stage(spec.target_stage, account),
        )

    def run(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        run_id: str,
        resolved: ResolvedInvoiceIngestionSpec,
        poll_timeout: int,
        max_retries: int,
    ) -> Manifest:
        """Drive one ingestion scenario through ``ingest_invoice`` (+ optional
        ``promote_to_posted``).

        Draft ingestion retries are intentionally narrow: retry only transient
        failures when no invoice id has been observed. The ingest action uses
        ``uniqueIdentifier=run_id``, but once the org returns an invoice id (or
        the tracker fails with one), the manifest keeps that id and the handler
        stops rather than replaying a partially materialized graph. Posted
        ingestion remains Phase 2 operationally; this retry policy is for the
        supported Draft path.
        """
        current_run_id.set(run_id)
        manifest = Manifest(
            run_id=run_id,
            kind=self.kind,
            account_id=resolved.account.id,
            account_name=resolved.account.name,
        )
        step_ctx = StepContext(
            client=client,
            org_context=ctx,
            run_id=run_id,
            account=resolved.account,
            lines=[],  # PST-only slot; unused on this lifecycle
            with_opportunity=False,
            poll_timeout=poll_timeout,
            checkpoint=write_manifest,
            target_stage=resolved.spec.target_stage,
            invoice_lines=resolved.invoice_lines,
            invoice_spec=resolved.invoice_overrides,
        )
        attempt = 0
        while True:
            attempt += 1
            manifest.attempts = attempt
            try:
                for step in self.remaining_steps(
                    manifest.reached_stage,
                    resolved.spec.target_stage,
                    with_opportunity=False,
                ):
                    manifest = execute_step(step, step_ctx, manifest)
                    write_manifest(manifest)
                manifest.error = None
                manifest.failure_class = None
                break
            except Exception as exc:  # noqa: BLE001 -- isolate one scenario's failure
                from ..lifecycle import LifecycleError

                manifest.error = (
                    str(exc) if isinstance(exc, LifecycleError)
                    else f"{type(exc).__name__}: {exc}"
                )
                manifest.failure_class = classify_exception(exc)
                retryable = (
                    resolved.spec.target_stage == "invoice_draft"
                    and manifest.failure_class == "transient"
                    and not manifest.invoice_id
                    and attempt <= max_retries
                )
                if not retryable:
                    break
                write_manifest(manifest)
                delay = _retry_backoff(attempt)
                log.warning(
                    "%s transient Draft ingest failure (%s); retrying in %.1fs "
                    "(attempt %d/%d)",
                    run_id,
                    manifest.error,
                    delay,
                    attempt + 1,
                    max_retries + 1,
                )
                time.sleep(delay)
        write_manifest(manifest)
        return manifest

    def summarize(self, m: Manifest) -> dict[str, Any]:
        """Return the ingestion-shaped inspect/report summary for ``m``.

        Surfaces only fields that make sense on a standalone-billing run:
        no Opportunity/Quote/Order/BillingSchedule/Asset ids, no
        ``start_date`` (the ingest API has no notion of a quote start). The
        line slot is named ``invoice_lines`` so consumers can tell PST-shaped
        line records apart from raw InvoiceLine records.
        """
        from ..manifests import manifest_path

        return {
            "kind": m.kind,
            "run_id": m.run_id,
            "path": str(manifest_path(m.run_id)),
            "account": m.account_name or m.account_id,
            "reached_stage": m.reached_stage,
            "attempts": m.attempts,
            "failure_class": m.failure_class,
            "error": m.error,
            "line_count": len(m.lines),
            "ids": {
                "invoice": m.invoice_id,
                "invoice_lines": m.invoice_line_ids[:5],
            },
            "invoice_number": m.invoice_number,
            "creation_mode": m.creation_mode,
        }


