"""Planning and orchestration for Transaction Data Harness runs."""

from __future__ import annotations

import contextvars
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

from .auth import SfRestClient
from .config import ConfigError, ScenarioSpec
from .config import ProductOption
from .discovery import (
    Account,
    DiscoveryError,
    OrgContext,
    Product,
    attach_usage_bindings,
    resolve_account,
    resolve_product,
    resolve_uom_override,
)
from .failure import classify_exception
from .lifecycle import LifecycleError
from .manifests import manifest_path, write_manifest
from .models import (
    IMPLEMENTED_MAX_STAGE,
    STAGES,
    LineItem,
    Manifest,
    ResolvedOption,
    ResolvedSpec,
    ResolvedUsageSpec,
    ResolvedUsageTarget,
)
from .steps import StepContext, execute_step
from .term import EndDateOverride, Term

log = logging.getLogger("txn_data_harness.runner")

# Per-scenario run id, set by each worker thread so concurrent step logs can be
# attributed to the scenario that emitted them.
current_run_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "txn_data_harness_run_id", default="-"
)

# Scenario-level retry policy. Only "transient" failures (see failure.py) are
# retried, resuming from the last checkpointed stage. Backoff is exponential:
# RETRY_BACKOFF_BASE * 2**attempt, capped at RETRY_BACKOFF_MAX.
DEFAULT_MAX_RETRIES = 2
RETRY_BACKOFF_BASE = 30.0  # seconds; 30s -> 60s -> ...
RETRY_BACKOFF_MAX = 90.0   # cap so a flaky batch can't stall for many minutes


@dataclass
class BatchResult:
    base_run_id: str
    total: int
    failures: int
    manifest_dir: Path


def effective_stage(target_stage: str, account: Account) -> str:
    """Resolve the stage a scenario will actually reach."""
    stage = target_stage
    if STAGES.index(stage) > STAGES.index(IMPLEMENTED_MAX_STAGE):
        stage = IMPLEMENTED_MAX_STAGE
    # Non-billing accounts can still create quotes/orders. Activation generates
    # billing artifacts, so cap before activation when BillingAccount is absent.
    if not account.is_billing_ready and STAGES.index(stage) > STAGES.index("order"):
        stage = "order"
    return stage


def _resolve_usage(
    client: SfRestClient, product: Product, opt: ProductOption
) -> Optional[ResolvedUsageSpec]:
    """Bind a ``UsageSpec`` against the product's discovered resource bindings.

    Fails fast when the product has no bindings, when an explicit ``resource``
    code doesn't exist on the product, or when a ``unit_of_measure`` override
    isn't an active unit in the resource's UoM class.
    """
    if opt.usage is None:
        return None
    spec = opt.usage
    if not product.usage_bindings:
        raise DiscoveryError(
            f"product '{product.sku}' has no ProductUsageResource bindings; "
            f"cannot emit usage journals"
        )
    if spec.resource:
        match = next(
            (b for b in product.usage_bindings if b.resource_code == spec.resource),
            None,
        )
        if match is None:
            codes = ", ".join(b.resource_code for b in product.usage_bindings)
            raise DiscoveryError(
                f"product '{product.sku}' has no usage resource '{spec.resource}' "
                f"(available: {codes})"
            )
        bindings = [match]
    else:
        bindings = list(product.usage_bindings)

    targets: list[ResolvedUsageTarget] = []
    for binding in bindings:
        if spec.unit_of_measure:
            uom_id = resolve_uom_override(client, binding, spec.unit_of_measure)
            uom_code = spec.unit_of_measure
        else:
            if not binding.default_uom_id:
                raise DiscoveryError(
                    f"usage resource '{binding.resource_code}' has no "
                    f"DefaultUnitOfMeasureId and no override was provided"
                )
            uom_id = binding.default_uom_id
            uom_code = binding.default_uom_code
        targets.append(ResolvedUsageTarget(
            resource_id=binding.resource_id,
            resource_code=binding.resource_code,
            uom_id=uom_id,
            uom_code=uom_code,
        ))
    return ResolvedUsageSpec(
        quantity=spec.quantity,
        records_per_line=spec.records_per_line,
        days_back=spec.days_back,
        targets=targets,
    )


_DEFAULT_TERM = Term(count=12, unit="Months")


def _resolve_term(opt: ProductOption, spec: ScenarioSpec, product: Product) -> Optional[Term]:
    """Apply the 4-step term fallback + unit-vs-PSM consistency rule.

    Returns ``None`` for non-TermDefined products so the lifecycle skips both
    EndDate and SubscriptionTerm writes. For TermDefined:

    1. line override (``opt.term``)
    2. scenario default (``spec.term``)
    3. product's discovered ``default_term``
    4. ``Term(12, "Months")`` fallback

    After picking, the unit must equal the resolved PSM's ``PricingTermUnit``.
    A bare-int config (``unit=None``) promotes to the PSM unit. An explicit
    unit that disagrees raises ``ConfigError`` -- switching PSMs is never
    implicit; the author must pin a matching ``selling_model:``.
    """
    if not product.needs_end_date:
        # Evergreen / OneTime: reject explicit term config loudly.
        if opt.term is not None:
            raise ConfigError(
                f"product '{product.sku}' selling model is "
                f"{product.selling_model_type}; 'term' is only valid for "
                f"TermDefined products"
            )
        return None

    chosen = opt.term or spec.term or product.default_term or _DEFAULT_TERM
    # Subtle: an explicit end_date override is incoherent without a cadence
    # (the platform still computes PricingTerm/PricingTermCount off the term
    # fields, so the line still needs a SubscriptionTerm). Falling through to
    # _DEFAULT_TERM when end_date is set but neither line/scenario/PSM declares
    # a term would silently force 12-Months -- demand the author be explicit.
    if (opt.end_date is not None or spec.end_date is not None) and not (
        opt.term or spec.term or product.default_term
    ):
        raise ConfigError(
            f"product '{product.sku}' has an end_date override but no term "
            f"is declared on the line, scenario, or selling model; "
            f"end_date requires an accompanying term: (the platform still "
            f"derives PricingTermCount from SubscriptionTerm)"
        )
    psm_unit = product.pricing_term_unit
    if chosen.unit is None:
        # Bare int from config: count override only; unit follows the PSM.
        # If the PSM doesn't declare a unit either (legacy/incomplete
        # metadata), refuse to guess -- a silent ``Months`` fallback would
        # write the wrong SubscriptionTermUnit on a non-monthly PSM and
        # the platform validation error would point miles from the cause.
        if psm_unit is None:
            raise ConfigError(
                f"product '{product.sku}' was given a bare-int term "
                f"({chosen.count}) but the resolved selling model "
                f"'{product.selling_model_name}' has no PricingTermUnit "
                f"on its metadata, so the harness cannot infer the unit. "
                f"Pin it explicitly with term: {{count: {chosen.count}, "
                f"unit: <Months|Annual|Quarterly|Semi-Annual>}}."
            )
        return Term(count=chosen.count, unit=psm_unit)
    if psm_unit is not None and chosen.unit != psm_unit:
        raise ConfigError(
            f"product '{product.sku}' is bound to selling model "
            f"'{product.selling_model_name}' with PricingTermUnit "
            f"'{psm_unit}', but term.unit was '{chosen.unit}'. Pin a matching "
            f"selling_model: in config or change the unit; the harness will "
            f"not implicitly switch PBEs."
        )
    return chosen


def _resolve_end_date(
    opt: ProductOption, spec: ScenarioSpec, product: Product
) -> Optional[EndDateOverride]:
    """Pick the line's EndDate override: line wins over scenario.

    Rejected on non-TermDefined products (Evergreen / OneTime reject EndDate
    at place time, so we fail loud at config-resolve time instead). Returns
    ``None`` when neither line nor scenario sets one -- the platform derives
    EndDate from StartDate + SubscriptionTerm (Branch A, default).
    """
    chosen = opt.end_date or spec.end_date
    if chosen is None:
        return None
    if not product.needs_end_date:
        raise ConfigError(
            f"product '{product.sku}' selling model is "
            f"{product.selling_model_type}; 'end_date' is only valid for "
            f"TermDefined products (Evergreen/OneTime reject EndDate)"
        )
    return chosen


def resolve_spec(client: SfRestClient, ctx: OrgContext, spec: ScenarioSpec) -> ResolvedSpec:
    """Bind a spec's account + product pool to org records."""
    if spec.account:
        account = resolve_account(client, spec.account)
    else:
        account = ctx.default_account()
    products = [
        (
            resolve_product(client, opt.sku, selling_model=opt.selling_model)
            if opt.sku
            else ctx.default_product()
        )
        for opt in spec.products
    ]
    # Only fetch usage bindings for products that actually opted in.
    usage_products = [
        p for p, opt in zip(products, spec.products) if opt.usage is not None
    ]
    if usage_products:
        attach_usage_bindings(client, usage_products)
    options = [
        ResolvedOption(
            product=product,
            quantity=opt.quantity,
            discount=opt.discount,
            period_boundary=opt.period_boundary,
            billing_frequency=opt.billing_frequency,
            usage=_resolve_usage(client, product, opt),
            term=_resolve_term(opt, spec, product),
            end_date=_resolve_end_date(opt, spec, product),
        )
        for product, opt in zip(products, spec.products)
    ]
    return ResolvedSpec(
        spec=spec,
        account=account,
        options=options,
        effective_stage=effective_stage(spec.target_stage, account),
    )


def draw_start_date(rng: Optional[tuple[date, date]]) -> Optional[date]:
    """Pick one StartDate from a ``(lo, hi)`` range."""
    if rng is None:
        return None
    lo, hi = rng
    span = (hi - lo).days
    return lo if span <= 0 else lo + timedelta(days=random.randint(0, span))


def draw_lines(options: list[ResolvedOption]) -> list[LineItem]:
    """Pick this transaction's lines from the resolved product pool."""
    chosen = [opt for opt in options if random.random() < 0.5]
    if not chosen:
        chosen = [random.choice(options)]
    lines: list[LineItem] = []
    for opt in chosen:
        qlo, qhi = opt.quantity
        quantity = random.randint(qlo, qhi)
        discount = None
        if opt.discount is not None:
            dlo, dhi = opt.discount
            discount = round(random.uniform(dlo, dhi), 2)
        lines.append(LineItem(
            product=opt.product,
            quantity=quantity,
            discount_percent=discount,
            period_boundary=opt.period_boundary,
            billing_frequency=opt.billing_frequency,
            usage=opt.usage,
            term=opt.term,
            end_date=opt.end_date,
        ))
    return lines


def stage_sequence(target_stage: str, with_opportunity: bool) -> list[str]:
    """Return the ordered steps needed to reach ``target_stage``."""
    stop_at = STAGES.index(target_stage)
    steps: list[str] = []
    if with_opportunity or target_stage == "opportunity":
        steps.append("opportunity")
    if stop_at == STAGES.index("opportunity"):
        return steps
    return steps + STAGES[STAGES.index("quote"): stop_at + 1]


def remaining_steps(reached_stage: Optional[str], target_stage: str,
                    with_opportunity: bool) -> list[str]:
    """Return the steps still needed to reach ``target_stage``.

    When ``reached_stage`` is set (a resumed or retried run), continue from the
    step *after* it. When it is None (a fresh run), fall back to the full
    ``stage_sequence``. Shared by ``run_scenario``'s retry path and the CLI
    ``step`` subcommand so both agree on the resume math. Returns ``[]`` when the
    manifest has already reached or passed the target.
    """
    if reached_stage is None:
        return stage_sequence(target_stage, with_opportunity)
    if STAGES.index(reached_stage) >= STAGES.index(target_stage):
        return []
    return STAGES[STAGES.index(reached_stage) + 1: STAGES.index(target_stage) + 1]


def run_steps(step_names: list[str], ctx: StepContext, manifest: Manifest) -> Manifest:
    """Execute a list of named lifecycle steps, checkpointing after each one."""
    for step in step_names:
        manifest = execute_step(step, ctx, manifest)
        write_manifest(manifest)
    return manifest


def _retry_backoff(attempt: int) -> float:
    """Seconds to wait before retry ``attempt`` (1-based), capped."""
    return min(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)), RETRY_BACKOFF_MAX)


def run_scenario(
    client: SfRestClient,
    ctx: OrgContext,
    run_id: str,
    target_stage: str,
    account: Account,
    lines: list[LineItem],
    with_opportunity: bool,
    poll_timeout: int,
    start_date: Optional[date] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    sleep: Callable[[float], None] = time.sleep,
    kind: str = "sales_transaction",
) -> Manifest:
    """Drive one transaction through the requested lifecycle stages.

    Transient failures (network blips, row locks, rate limits — see failure.py)
    are retried up to ``max_retries`` times, resuming from the last checkpointed
    stage rather than re-running completed steps. Deterministic/unknown failures
    fail fast. ``sleep`` is injectable so tests don't wait on backoff.
    """
    current_run_id.set(run_id)
    manifest = Manifest(
        run_id=run_id,
        kind=kind,
        account_id=account.id,
        account_name=account.name,
        start_date=start_date.isoformat() if start_date is not None else None,
        lines=[line.to_manifest_record() for line in lines],
    )

    step_ctx = StepContext(
        client=client,
        org_context=ctx,
        run_id=run_id,
        account=account,
        lines=lines,
        with_opportunity=with_opportunity,
        poll_timeout=poll_timeout,
        start_date=start_date,
        checkpoint=write_manifest,
    )

    stage = effective_stage(target_stage, account)
    attempt = 0
    while True:
        attempt += 1
        manifest.attempts = attempt
        # On the first attempt reached_stage is None -> full sequence. On a retry
        # it resumes from the step after whatever the last attempt checkpointed.
        steps = remaining_steps(manifest.reached_stage, stage, with_opportunity)
        try:
            run_steps(steps, step_ctx, manifest)
            manifest.error = None
            manifest.failure_class = None
            break
        except Exception as exc:  # noqa: BLE001 -- isolate one scenario's failure
            manifest.error = (
                str(exc) if isinstance(exc, LifecycleError)
                else f"{type(exc).__name__}: {exc}"
            )
            manifest.failure_class = classify_exception(exc)
            retryable = manifest.failure_class == "transient" and attempt <= max_retries
            log.error(
                "scenario failed (attempt %d, %s%s): %s",
                attempt, manifest.failure_class,
                "; will retry" if retryable else "",
                manifest.error,
                exc_info=log.isEnabledFor(logging.DEBUG),
            )
            if not retryable:
                break
            delay = _retry_backoff(attempt)
            log.warning("retrying scenario in %.0fs (attempt %d/%d)",
                        delay, attempt + 1, max_retries + 1)
            write_manifest(manifest)
            sleep(delay)

    write_manifest(manifest)
    return manifest


def run_batch(
    client: SfRestClient,
    ctx: OrgContext,
    resolved: list[ResolvedSpec],
    concurrency: int,
    poll_timeout: int,
    on_start: Optional[Callable[[str, int, int], None]] = None,
    on_complete: Optional[Callable[[int, int, Manifest, Path], None]] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> BatchResult:
    """Run all resolved specs with scenario-level concurrency."""
    base_run_id = "DEMO-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jobs: list[tuple[str, ResolvedSpec]] = []
    single = len(resolved) == 1 and resolved[0].spec.count == 1
    for r in resolved:
        for _ in range(r.spec.count):
            run_id = base_run_id if single else f"{base_run_id}-{len(jobs) + 1:03d}"
            jobs.append((run_id, r))

    total = len(jobs)
    worker_count = max(1, min(concurrency, total))
    if on_start is not None:
        on_start(base_run_id, total, worker_count)

    def one(run_id: str, r: ResolvedSpec) -> Manifest:
        return run_scenario(
            client,
            ctx,
            run_id,
            r.spec.target_stage,
            r.account,
            draw_lines(r.options),
            with_opportunity=r.spec.with_opportunity,
            poll_timeout=poll_timeout,
            start_date=draw_start_date(r.start_date_range),
            max_retries=max_retries,
            kind=r.spec.kind,
        )

    failures = 0
    done = 0
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        futures = [pool.submit(one, rid, r) for rid, r in jobs]
        for fut in as_completed(futures):
            manifest = fut.result()
            done += 1
            path = manifest_path(manifest.run_id)
            if on_complete is not None:
                on_complete(done, total, manifest, path)
            if manifest.error:
                failures += 1

    return BatchResult(
        base_run_id=base_run_id,
        total=total,
        failures=failures,
        manifest_dir=manifest_path(base_run_id).parent,
    )
