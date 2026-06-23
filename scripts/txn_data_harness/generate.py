"""CLI entry point for the demo data generator.

    python -m scripts.txn_data_harness.generate --org <sf-alias> [options]

Phase 1 scope: resolve auth + discovery and, under ``--dry-run``, print the
planned account/product/pricebook and the lifecycle calls that *would* run --
without POSTing anything. Live execution (place -> order -> activate ->
invoice -> post) lands in Phase 2 (``lifecycle.py``); until then a non-dry-run
invocation reports clearly that execution is not yet wired.

``--org`` accepts an ``sf`` CLI alias / username ONLY (not a CCI alias). The
CCI alias ``beta`` maps to the sf alias ``rlm-base__beta`` -- pass the sf one.
"""

from __future__ import annotations

import argparse
import contextvars
import json
import logging
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from . import lifecycle
from .auth import DEFAULT_API_VERSION, SfApiError, SfCliError, SfRestClient
from .config import ConfigError, ScenarioSpec, load_scenarios
from .discovery import (
    Account,
    DiscoveryError,
    OrgContext,
    Product,
    discover,
    resolve_account,
    resolve_product,
)
from .lifecycle import LifecycleError, LineItem, Manifest

log = logging.getLogger("txn_data_harness")

# Per-scenario run id, set by each worker thread so concurrent step logs can be
# attributed to the scenario that emitted them. A ContextVar is inherited per
# thread/task without cross-worker bleed (unlike a plain module global).
_current_run_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "txn_data_harness_run_id", default="-"
)

STAGES = ["opportunity", "quote", "order", "activate", "invoice", "post"]

# Full lifecycle implemented as of Phase 3 (through post).
_IMPLEMENTED_MAX_STAGE = "post"

MANIFEST_DIR = os.path.join(os.path.dirname(__file__), "out")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m scripts.txn_data_harness.generate",
        description="Generate realistic Revenue Cloud demo data by driving the "
                    "real transaction lifecycle against a target org.",
    )
    p.add_argument("--org", required=True,
                   help="Target org: sf CLI alias or username (NOT a CCI alias).")
    p.add_argument("--config", help="YAML/JSON config file (all fields optional).")

    # Volume / shape overrides (override config).
    p.add_argument("--count", type=int, help="Number of transactions to generate.")
    p.add_argument("--target-stage", choices=STAGES,
                   help="How far through the lifecycle to run (default: post).")
    p.add_argument("--account", help="Pin the account by Name (else auto-discover).")
    p.add_argument("--product", help="Pin the product by SKU (else auto-discover).")
    p.add_argument("--with-opportunity", action="store_true",
                   help="Prepend an Opportunity the quote links to.")
    p.add_argument("--opportunity-stage", help="Pin the Opportunity StageName.")

    # Execution controls.
    p.add_argument("--concurrency", type=int, default=4,
                   help="Parallel scenario workers (default: 4).")
    p.add_argument("--poll-timeout", type=int, default=180,
                   help="Async poll timeout in seconds (default: 180).")
    p.add_argument("--api-version", default=DEFAULT_API_VERSION,
                   help=f"API version (default: {DEFAULT_API_VERSION}; 'latest' to query).")
    p.add_argument("--transport", choices=["requests", "cli"], default="requests",
                   help="REST transport (default: requests; cli = sf api proxy).")

    # Probe / safety.
    p.add_argument("--no-probe", action="store_true",
                   help="Reserved for future PST probes; currently no-op.")
    p.add_argument("--keep-probes", action="store_true",
                   help="Reserved for future PST probes; currently no-op.")
    p.add_argument("--dry-run", action="store_true",
                   help="Resolve auth+discovery and print planned calls; no writes.")
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="-v for INFO, -vv for DEBUG.")
    return p.parse_args(argv)


class _RunIdFilter(logging.Filter):
    """Attach the current scenario's run id to every record as ``run_id``."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = _current_run_id.get()
        return True


def _setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    # Prefix every line with the emitting scenario's run id so interleaved
    # logs from concurrent workers stay attributable; "-" outside any scenario.
    logging.basicConfig(level=level, format="%(run_id)s | %(message)s")
    for handler in logging.getLogger().handlers:
        handler.addFilter(_RunIdFilter())


def _fmt_qty(qty: tuple[int, int]) -> str:
    lo, hi = qty
    return f"x{lo}" if lo == hi else f"x{lo}–{hi} (random)"


def _fmt_discount(discount: Optional[tuple[float, float]]) -> str:
    if discount is None:
        return ""
    lo, hi = discount
    return f"@ {lo:g}% off" if lo == hi else f"@ {lo:g}–{hi:g}% off (random)"


def _print_plan(
    args: argparse.Namespace, ctx: OrgContext, resolved: list["ResolvedSpec"]
) -> None:
    """Human-readable dry-run summary of what a run would do (no writes)."""
    print("\n=== Transaction Data Harness — DRY RUN (no writes) ===")
    print(f"Org              : {args.org}  (api v{ctx_api(args)})  transport={args.transport}")
    print(f"Pricebook        : {ctx.pricebook_name} ({ctx.pricebook_id})")
    print(f"Legal entity     : {ctx.legal_entity_name}")
    print(f"Opportunity stage: {ctx.opportunity_stage}")
    print(f"Concurrency      : {max(1, args.concurrency)}")

    total = 0
    for i, r in enumerate(resolved):
        # The chain starts at 'opportunity' when one is prepended OR the target
        # stage is 'opportunity' itself; otherwise the minimum is 'quote'. Clamp
        # to effective_stage so a quote-only run never shows an empty range.
        starts_with_opp = r.spec.with_opportunity or r.effective_stage == "opportunity"
        head = "opportunity" if starts_with_opp else "quote"
        if STAGES.index(head) > STAGES.index(r.effective_stage):
            head = r.effective_stage
        stages_run = STAGES[STAGES.index(head): STAGES.index(r.effective_stage) + 1]
        total += r.spec.count
        print(f"\n--- Spec {i + 1}/{len(resolved)}  (x{r.spec.count}) ---")
        print(f"  Account      : {r.account.name} ({r.account.id})  "
              f"billing_ready={r.account.is_billing_ready}")
        pool = len(r.options)
        if pool > 1:
            print(f"  Product pool : {pool} products — a random non-empty subset "
                  f"is placed per transaction (multi-line)")
        for opt in r.options:
            print(f"    • {opt.product.sku} — {opt.product.name}  "
                  f"${opt.product.unit_price} {_fmt_qty(opt.quantity)}  "
                  f"{_fmt_discount(opt.discount)}".rstrip()
                  + f"  (PBE {opt.product.pricebook_entry_id})")
        rng = r.start_date_range
        if rng is not None:
            lo, hi = rng
            print(f"  Start date   : {lo.isoformat()}"
                  + (f" → {hi.isoformat()} (drawn per quote)" if hi != lo else ""))
        if r.effective_stage != r.spec.target_stage:
            print(f"  ⚠  target_stage '{r.spec.target_stage}' capped to "
                  f"'{r.effective_stage}' (billing_ready={r.account.is_billing_ready}).")
        print(f"  Stages       : {' → '.join(stages_run)}")

    print(f"\nWould generate   : {total} transaction(s) total")
    print(f"Billing-ready accounts available: "
          f"{', '.join(a.name for a in ctx.billing_ready_accounts) or '(none)'}")
    print(f"Billable products available     : {len(ctx.products)}")
    print("\n(no records were created — drop --dry-run to execute)\n")


def ctx_api(args: argparse.Namespace) -> str:
    return args.api_version if args.api_version != "latest" else "latest"


def _effective_stage(target_stage: str, account: Account) -> str:
    """Resolve the stage a scenario will actually reach.

    Caps at what's implemented, and at 'order' for accounts that aren't
    billing-ready: such accounts can still go quote -> order (useful pipeline
    demo data), but activation generates BillingSchedules/Assets and needs the
    account's billing setup, so it's capped before 'activate'.
    """
    stage = target_stage
    if STAGES.index(stage) > STAGES.index(_IMPLEMENTED_MAX_STAGE):
        stage = _IMPLEMENTED_MAX_STAGE
    if not account.is_billing_ready and STAGES.index(stage) > STAGES.index("order"):
        stage = "order"
    return stage


@dataclass
class ResolvedOption:
    """A :class:`ProductOption` bound to a concrete org Product."""

    product: Product
    quantity: tuple[int, int]
    discount: Optional[tuple[float, float]]
    period_boundary: Optional[str] = None
    billing_frequency: Optional[str] = None


@dataclass
class ResolvedSpec:
    """A :class:`ScenarioSpec` bound to concrete org records, ready to fan out.

    ``account``/``options`` are resolved once per spec (not per repetition) so a
    ``count: 25`` spec issues its discovery queries twice, not fifty times. Each
    transaction draws a random non-empty subset of ``options`` for its lines.
    """

    spec: ScenarioSpec
    account: Account
    options: list[ResolvedOption]
    effective_stage: str

    @property
    def start_date_range(self) -> Optional[tuple[date, date]]:
        return self.spec.start_date


def _draw_start_date(rng: Optional[tuple[date, date]]) -> Optional[date]:
    """Pick one StartDate from a ``(lo, hi)`` range (uniform over the days).

    ``None`` range => ``None`` (lifecycle defaults to today). ``lo == hi`` returns
    that exact date. Otherwise a day is chosen uniformly across the span, so a
    ``count: N`` spec spreads its quotes across the window.
    """
    if rng is None:
        return None
    lo, hi = rng
    span = (hi - lo).days
    return lo if span <= 0 else lo + timedelta(days=random.randint(0, span))


def _resolve_spec(
    client: SfRestClient, ctx: OrgContext, spec: ScenarioSpec
) -> ResolvedSpec:
    """Bind a spec's account + product pool to org records (raises DiscoveryError)."""
    if spec.account:
        account = resolve_account(client, spec.account)
    else:
        account = ctx.default_account()
    options = [
        ResolvedOption(
            product=(resolve_product(client, opt.sku) if opt.sku
                     else ctx.default_product()),
            quantity=opt.quantity,
            discount=opt.discount,
            period_boundary=opt.period_boundary,
            billing_frequency=opt.billing_frequency,
        )
        for opt in spec.products
    ]
    effective = _effective_stage(spec.target_stage, account)
    return ResolvedSpec(spec=spec, account=account, options=options,
                        effective_stage=effective)


def _draw_lines(options: list["ResolvedOption"]) -> list[LineItem]:
    """Pick this transaction's lines from the resolved product pool.

    Each option is included independently with 50% probability, so a two-product
    pool yields one OR both lines across transactions; if the coin-flips drop
    everything, one option is chosen at random (a quote always needs >= 1 line).
    A single-option pool is therefore always placed (deterministic). Per line,
    quantity and discount are drawn from their ``(min, max)`` ranges.
    """
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
            product=opt.product, quantity=quantity, discount_percent=discount,
            period_boundary=opt.period_boundary,
            billing_frequency=opt.billing_frequency,
        ))
    return lines


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
) -> Manifest:
    """Drive one transaction (one or more lines) through the lifecycle.

    Runs up to ``target_stage``. Records every created id in the manifest as it
    goes -- including on partial failure (PST commits the quote header even on a
    failed place), so cleanup can find orphans.
    """
    _current_run_id.set(run_id)
    m = Manifest(run_id=run_id)
    if start_date is not None:
        m.start_date = start_date.isoformat()
    def _line_record(l: LineItem) -> dict:
        rec = {"sku": l.product.sku, "quantity": l.quantity,
               "discount_percent": l.discount_percent}
        if l.period_boundary is not None:
            rec["period_boundary"] = l.period_boundary
        if l.billing_frequency is not None:
            rec["billing_frequency"] = l.billing_frequency
        return rec

    m.lines = [_line_record(l) for l in lines]
    stage = _effective_stage(target_stage, account)
    stop_at = STAGES.index(stage)
    # target_stage 'opportunity' means "stop after the opportunity", so it
    # implies creating one even when the --with-opportunity prepend flag is off.
    want_opportunity = with_opportunity or stop_at == STAGES.index("opportunity")

    def checkpoint() -> None:
        # Persist the manifest after every stage so a kill (or crash) mid-run
        # still leaves a record of every id created so far -- the only way to
        # find and clean up partials, since Order.Description isn't filterable.
        _write_manifest(m)

    try:
        if want_opportunity and ctx.opportunity_stage:
            m.opportunity_id = lifecycle.create_opportunity(
                client, account, ctx.opportunity_stage, run_id
            )
            m.reached_stage = "opportunity"
            checkpoint()
        if stop_at == STAGES.index("opportunity"):
            return m

        # quote (PST) -- always the minimum
        try:
            m.quote_id = lifecycle.place_sales_transaction(
                client, account, lines, ctx.pricebook_id, run_id,
                opportunity_id=m.opportunity_id, start_date=start_date,
            )
        except LifecycleError as exc:
            # PST may have committed the quote header even on failure -- record
            # the orphan id before re-raising so cleanup can find it.
            if exc.record_id:
                m.quote_id = exc.record_id
                checkpoint()
            raise
        m.reached_stage = "quote"
        checkpoint()
        if stop_at == STAGES.index("quote"):
            return m

        m.order_id, m.order_number = lifecycle.create_order_from_quote(client, m.quote_id)
        m.reached_stage = "order"
        checkpoint()
        if stop_at == STAGES.index("order"):
            return m

        # activate: set shipping first (mandatory), capture timestamp for asset poll
        lifecycle.set_shipping_address(client, m.order_id, account)
        since = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lifecycle.activate_order(client, m.order_id)
        m.reached_stage = "activate"
        m.billing_schedule_ids = lifecycle.poll_billing_schedules(
            client, m.order_id, expected_count=len(lines), timeout=poll_timeout
        )
        m.asset_ids = lifecycle.poll_assets(
            client, account, [l.product for l in lines], since,
            expected_count=len(lines), timeout=poll_timeout
        )
        checkpoint()
        if stop_at == STAGES.index("activate"):
            return m

        # invoice: generate Draft, correlate, tag Description while mutable
        m.invoice_id, m.invoice_number = lifecycle.generate_invoice(
            client, m.billing_schedule_ids, run_id, timeout=poll_timeout
        )
        lifecycle.tag_invoice(client, m.invoice_id, run_id)
        m.reached_stage = "invoice"
        checkpoint()
        if stop_at == STAGES.index("invoice"):
            return m

        # post, then link invoice -> order (ReferenceEntityId is Posted-only)
        m.invoice_number = lifecycle.post_invoice(
            client, m.invoice_id, run_id, timeout=poll_timeout
        )
        m.reached_stage = "post"
        checkpoint()
        lifecycle.link_invoice_to_order(client, m.invoice_id, m.order_id)
    except LifecycleError as exc:
        m.error = str(exc)
        log.error("scenario failed: %s", exc)
    except Exception as exc:  # noqa: BLE001 -- isolate one scenario's failure
        # SfApiError / SfCliError (non-2xx, retries exhausted) and any
        # unexpected error (e.g. KeyError on a malformed response) must be
        # recorded on the manifest, not propagate out of fut.result() and
        # abort the whole batch -- the manifest is how cleanup finds partials.
        m.error = f"{type(exc).__name__}: {exc}"
        log.error("scenario failed: %s", m.error, exc_info=log.isEnabledFor(logging.DEBUG))
    finally:
        # Always flush the final state (records the error field on failure, and
        # the post-link / terminal stage on success).
        checkpoint()
    return m


def _write_manifest(m: Manifest) -> str:
    # Write-then-rename so a kill mid-write never leaves a truncated/corrupt
    # manifest -- checkpointing is only useful if the file on disk is always
    # valid JSON. rename within the same dir is atomic on POSIX.
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    path = os.path.join(MANIFEST_DIR, f"{m.run_id}.json")
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        json.dump(m.to_dict(), f, indent=2)
    os.replace(tmp, path)
    return path


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    _setup_logging(args.verbose)

    try:
        client = SfRestClient.from_alias(
            args.org, api_version=args.api_version, transport=args.transport
        )
    except SfCliError as exc:
        print(f"ERROR: could not authenticate to org '{args.org}':\n  {exc}",
              file=sys.stderr)
        return 2

    try:
        ctx = discover(
            client,
            account_name=args.account,
            sku=args.product,
            opportunity_stage=args.opportunity_stage,
        )
    except (DiscoveryError, SfApiError) as exc:
        print(f"ERROR: discovery failed:\n  {exc}", file=sys.stderr)
        return 3

    # ----- resolve the run plan (specs -> concrete account/product) -----
    try:
        specs = load_scenarios(args)
    except ConfigError as exc:
        print(f"ERROR: bad config:\n  {exc}", file=sys.stderr)
        return 4
    try:
        resolved = [_resolve_spec(client, ctx, s) for s in specs]
    except DiscoveryError as exc:
        print(f"ERROR: could not resolve a scenario's account/product:\n  {exc}",
              file=sys.stderr)
        return 3

    if args.dry_run:
        _print_plan(args, ctx, resolved)
        return 0

    # ----- live execution -----
    for r in resolved:
        if r.effective_stage != r.spec.target_stage:
            skus = "/".join(o.product.sku for o in r.options)
            print(f"Note: capping '{r.account.name}/{skus}' target_stage "
                  f"'{r.spec.target_stage}' -> '{r.effective_stage}' "
                  f"(billing_ready={r.account.is_billing_ready}; "
                  f"implemented through '{_IMPLEMENTED_MAX_STAGE}').",
                  file=sys.stderr)

    # Expand (spec x count) into a flat job list, each with a unique run_id.
    base_run_id = "DEMO-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jobs: list[tuple[str, ResolvedSpec]] = []
    single = len(resolved) == 1 and resolved[0].spec.count == 1
    for r in resolved:
        for _ in range(r.spec.count):
            run_id = base_run_id if single else f"{base_run_id}-{len(jobs) + 1:03d}"
            jobs.append((run_id, r))
    total = len(jobs)

    def _one(run_id: str, r: ResolvedSpec) -> Manifest:
        return run_scenario(
            client, ctx, run_id, r.spec.target_stage, r.account,
            _draw_lines(r.options),
            with_opportunity=r.spec.with_opportunity,
            poll_timeout=args.poll_timeout,
            start_date=_draw_start_date(r.start_date_range),
        )

    concurrency = max(1, min(args.concurrency, total))
    print(f"Running {total} scenario(s) across {len(resolved)} spec(s), "
          f"concurrency={concurrency}, run base {base_run_id} ...")

    failures = 0
    done = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_one, rid, r) for rid, r in jobs]
        for fut in as_completed(futures):
            m = fut.result()
            # run_scenario already checkpointed the manifest to this path (incl.
            # in its finally), so we just report it -- no second write needed.
            path = os.path.join(MANIFEST_DIR, f"{m.run_id}.json")
            done += 1
            status = "OK" if not m.error else "FAILED"
            print(f"[{done}/{total}] {m.run_id}: {status} "
                  f"reached={m.reached_stage} order={m.order_number or '-'} "
                  f"manifest={path}")
            if m.error:
                failures += 1

    print(f"\nDone: {total - failures}/{total} scenario(s) succeeded. "
          f"Manifests in {MANIFEST_DIR}/")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
