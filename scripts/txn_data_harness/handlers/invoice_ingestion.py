"""Invoice-ingestion scenario handler.

Drives the standalone-billing invoice ingestion path (Composite Graph ingest
action). Counterpart to :class:`SalesTxnQuoteHandler` /
:class:`SalesTxnOrderHandler`: same protocol, very different lifecycle. The
PST chain walks Opportunity -> Quote -> Order ->
Activate -> Usage -> Invoice -> Post; supported ingestion configs ship one POST
that creates a Draft invoice in a single composite-graph call. The Posted path
creates a Draft then promotes via ``promote_to_posted``, stamping a non-taxable
TaxTreatment and building the InvoiceLineTax graph when required.

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

from datetime import date

from ..auth import SfRestClient
from ..config import (
    InvoiceIngestionScenarioSpec,
    InvoiceLineSpec,
    LineTaxSpec,
    ScenarioTaxDefaults,
)
from ..discovery import (
    Account,
    DiscoveryError,
    OrgContext,
    discover_any_accounts,
    resolve_account,
    resolve_invoice_line_product,
    resolve_taxable_tax_treatment,
)
from ..manifests import write_manifest
from ..models import (
    Manifest,
    ResolvedInvoiceIngestionSpec,
    ResolvedInvoiceLine,
    ResolvedInvoiceLineTax,
    ResolvedInvoiceOverrides,
)
from ..failure import classify_exception
from ..lifecycle import LifecycleError
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
    client: SfRestClient,
    spec: InvoiceLineSpec,
    *,
    line_index: int,
    target_stage: str,
    run_id: str,
    tax_defaults: Optional[ScenarioTaxDefaults],
    invoice_date: date,
) -> ResolvedInvoiceLine:
    """Resolve one config line into its post-resolve dataclass.

    ``sku`` is optional on the API; a SKU that doesn't match an active
    Product2 falls through to a description-only line (no ``product2Id``).
    The harness must never invent a product id, so this stays a soft-lookup.

    For ``taxable: true`` lines on Posted target, builds a
    :class:`ResolvedInvoiceLineTax` from the merged
    (``scenario.tax`` defaults + ``line.tax`` overrides) block. Required
    fields fall back to deterministic per-run defaults so a minimal
    scenario (``taxable: true`` + a scenario-level ``rate``) generates a
    valid payload without re-declaring every field.
    """
    product = (
        resolve_invoice_line_product(client, spec.sku) if spec.sku else None
    )
    unit_price = float(spec.unit_price)
    quantity = float(spec.quantity)
    charge_amount = (
        float(spec.charge_amount)
        if spec.charge_amount is not None
        else unit_price * quantity
    )
    tax_record: Optional[ResolvedInvoiceLineTax] = None
    if spec.taxable and target_stage == "invoice_posted":
        tax_record = _resolve_invoice_line_tax(
            line=spec,
            line_index=line_index,
            run_id=run_id,
            charge_amount=charge_amount,
            tax_defaults=tax_defaults,
            invoice_date=invoice_date,
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
        tax=tax_record,
    )


def _merged_tax_value(
    field: str,
    line_tax: Optional[LineTaxSpec],
    defaults: Optional[ScenarioTaxDefaults],
) -> Any:
    """Return the first non-None ``field`` across line-spec then scenario-default.

    Per-line override wins over scenario default; either ``None`` means the
    handler will reach for its built-in fallback (run-id-derived numbers,
    invoice date, etc.).
    """
    if line_tax is not None:
        v = getattr(line_tax, field, None)
        if v is not None:
            return v
    if defaults is not None:
        return getattr(defaults, field, None)
    return None


def _resolve_invoice_line_tax(
    *,
    line: InvoiceLineSpec,
    line_index: int,
    run_id: str,
    charge_amount: float,
    tax_defaults: Optional[ScenarioTaxDefaults],
    invoice_date: date,
) -> ResolvedInvoiceLineTax:
    """Build a :class:`ResolvedInvoiceLineTax` from merged scenario + line tax.

    ``taxAmount`` precedence: per-line ``amount`` > scenario ``amount`` >
    ``chargeAmount * rate`` (per-line ``rate`` overrides scenario rate). At
    least one of ``amount`` or ``rate`` must be present on the merged
    config; otherwise we can't compute a tax record without inventing data.

    ``taxRate`` is required by the dev guide. When only ``amount`` is
    pinned we back-derive the rate from ``amount / chargeAmount`` (or 0
    when chargeAmount is 0) so the record stays valid.
    """
    line_tax = line.tax

    rate = _merged_tax_value("rate", line_tax, tax_defaults)
    amount = _merged_tax_value("amount", line_tax, tax_defaults)
    if amount is None and rate is None:
        raise LifecycleError(
            "ingest_invoice",
            f"invoice_lines[{line_index}]: taxable line requires either a "
            f"scenario-level 'tax.rate' / 'tax.amount' default or a per-line "
            f"'tax:' block with at least one of them",
        )
    if amount is None:
        amount = round(float(charge_amount) * float(rate), 4)
    elif rate is None:
        rate = (
            round(float(amount) / float(charge_amount), 6)
            if charge_amount > 0
            else 0.0
        )

    name = _merged_tax_value("name", line_tax, tax_defaults)
    if not name:
        raise LifecycleError(
            "ingest_invoice",
            f"invoice_lines[{line_index}]: taxable line requires 'tax.name' "
            f"(e.g. 'Sales Tax') on the line or as a scenario default",
        )
    code = _merged_tax_value("code", line_tax, tax_defaults)
    if not code:
        raise LifecycleError(
            "ingest_invoice",
            f"invoice_lines[{line_index}]: taxable line requires 'tax.code' "
            f"(e.g. 'TX-SALES') on the line or as a scenario default",
        )

    effective_date = (
        _merged_tax_value("effective_date", line_tax, tax_defaults)
        or invoice_date
    )

    # Required ID fields: pin if the scenario set them; otherwise leave None
    # and let ``lifecycle.ingest_invoice`` stamp ``{run_id}-tx{idx}`` /
    # ``{run_id}-doc`` defaults where the real run id is in scope. (The
    # handler's ``resolve()`` runs in the main thread before each worker
    # sets its run-id ContextVar, so we'd see the "-" default here.)
    transaction_number = (
        line_tax.transaction_number if line_tax and line_tax.transaction_number
        else None
    )
    document_number = _merged_tax_value("document_number", line_tax, tax_defaults)

    exempt_amount = _merged_tax_value("exempt_amount", line_tax, tax_defaults)
    description = (
        line_tax.description if line_tax and line_tax.description else None
    )

    return ResolvedInvoiceLineTax(
        amount=float(amount),
        rate=float(rate),
        name=str(name),
        code=str(code),
        effective_date=effective_date,
        transaction_number=str(transaction_number) if transaction_number else None,
        document_number=str(document_number) if document_number else None,
        exempt_amount=float(exempt_amount) if exempt_amount is not None else 0.0,
        description=description,
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
        :class:`SalesTxnQuoteHandler` -- ingestion has no Opportunity
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

        When any line has ``taxable: true`` on Posted target, the handler
        resolves a taxable ``TaxTreatment`` id (auto-discovered, or pinned
        via ``invoice.taxable_tax_treatment_name``) and a fully-resolved
        :class:`ResolvedInvoiceLineTax` per taxable line. Missing
        prerequisites surface here with seed instructions rather than from
        the lifecycle.
        """
        if spec.account:
            account = resolve_account(client, spec.account)
        else:
            account = _default_account(ctx, client)
        run_id = current_run_id.get() or "DEMO"
        # Deterministic per-scenario invoice date for tax effective-date
        # defaults. The lifecycle re-derives the actual invoiceDate header the
        # same way (``spec.invoice_date or date.today()``), so the fallback
        # used in the tax record matches the invoice header when neither is
        # pinned.
        invoice_date = (
            spec.invoice.invoice_date
            if spec.invoice and spec.invoice.invoice_date
            else date.today()
        )
        resolved_lines = [
            _resolve_invoice_line(
                client,
                ln,
                line_index=i,
                target_stage=spec.target_stage,
                run_id=run_id,
                tax_defaults=spec.tax,
                invoice_date=invoice_date,
            )
            for i, ln in enumerate(spec.invoice_lines)
        ]
        overrides = _resolve_invoice_overrides(spec)

        taxable_tt_id: Optional[str] = None
        if any(ln.taxable for ln in resolved_lines):
            pinned_name = (
                spec.invoice.taxable_tax_treatment_name
                if spec.invoice and spec.invoice.taxable_tax_treatment_name
                else None
            )
            if pinned_name:
                taxable_tt_id = resolve_taxable_tax_treatment(client, pinned_name)
                if taxable_tt_id is None:
                    raise LifecycleError(
                        "ingest_invoice",
                        f"no Active taxable TaxTreatment named "
                        f"'{pinned_name}' (need Status=Active and IsTaxable=true). "
                        f"Create one or pin a different invoice.taxable_tax_treatment_name.",
                    )
            else:
                taxable_tt_id = ctx.taxable_tax_treatment_id or (
                    resolve_taxable_tax_treatment(client)
                )
                if taxable_tt_id is None:
                    raise LifecycleError(
                        "ingest_invoice",
                        "tax-on Posted ingestion requires an active taxable "
                        "TaxTreatment in the org. Create one in Setup -> Tax "
                        "Treatments with IsTaxable=true and Status=Active "
                        "(or via 'sf data create record --sobject TaxTreatment "
                        "--values \"Name=Default Tax Policy IsTaxable=true "
                        "Status=Active TaxCode=TX-SALES\"'), then re-run.",
                    )

        return ResolvedInvoiceIngestionSpec(
            spec=spec,
            account=account,
            invoice_lines=resolved_lines,
            invoice_overrides=overrides,
            effective_stage=self.effective_stage(spec.target_stage, account),
            taxable_tax_treatment_id=taxable_tt_id,
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
        ingestion remains unsupported operationally; this retry policy is for
        the supported Draft path.
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
            taxable_tax_treatment_id=resolved.taxable_tax_treatment_id,
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
