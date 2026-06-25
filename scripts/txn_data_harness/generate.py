"""CLI entry point for the demo data generator.

    python -m scripts.txn_data_harness.generate --org <sf-alias> [options]

Use ``--dry-run`` to resolve auth + discovery and print the planned
account/product/pricebook plus lifecycle calls without writing records. Without
``--dry-run``, this command drives the live harness lifecycle against the target
org and writes manifests for recovery and verification.

``--org`` accepts an ``sf`` CLI alias / username ONLY (not a CCI alias). The
CCI alias ``beta`` maps to the sf alias ``rlm-base__beta`` -- pass the sf one.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from .auth import SfApiError, SfCliError, SfRestClient
from .cli_args import add_generate_args
from .config import ConfigError, load_scenarios
from .discovery import DiscoveryError, OrgContext, discover
from .handlers import SCENARIO_HANDLERS
from .models import IMPLEMENTED_MAX_STAGE, STAGES, STAGES_QUOTE, Manifest, ResolvedSpec
from .report import build_batch_report, write_batch_report
from .runner import current_run_id, run_batch

log = logging.getLogger("txn_data_harness")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m scripts.txn_data_harness.generate",
        description="Generate realistic Revenue Cloud demo data by driving the "
                    "real transaction lifecycle against a target org.",
    )
    add_generate_args(p)
    p.add_argument("--dry-run", action="store_true",
                   help="Resolve auth+discovery and print planned calls; no writes.")
    return p.parse_args(argv)


class _RunIdFilter(logging.Filter):
    """Attach the current scenario's run id to every record as ``run_id``."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = current_run_id.get()
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


def _print_pst_spec(r: "ResolvedSpec", index: int, total: int) -> int:
    """Render one PST resolved spec; return its transaction count."""
    starts_with_opp = r.spec.with_opportunity or r.effective_stage == "opportunity_created"
    head = "opportunity_created" if starts_with_opp else "quote_placed"
    if STAGES_QUOTE.index(head) > STAGES_QUOTE.index(r.effective_stage):
        head = r.effective_stage
    stages_run = STAGES_QUOTE[STAGES_QUOTE.index(head): STAGES_QUOTE.index(r.effective_stage) + 1]
    print(f"\n--- Spec {index + 1}/{total}  (x{r.spec.count}) ---")
    print(f"  Kind         : sales_txn_quote")
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
    return r.spec.count


def _print_invoice_ingestion_spec(r, index: int, total: int) -> int:
    """Render one invoice-ingestion resolved spec; return its transaction count.

    Ingestion specs ship the same line list on every invoice (no per-tx random
    draw), so the listing is flat rather than a pool. ``effective_stage`` is
    always ``target_stage`` for ingestion -- no billing-ready cap applies.
    """
    spec = r.spec
    target = r.effective_stage  # "invoice_draft" (Draft) or "invoice_posted" (Posted)
    status = "Posted" if target == "invoice_posted" else "Draft"
    print(f"\n--- Spec {index + 1}/{total}  (x{spec.count}) ---")
    print(f"  Kind         : invoice_ingestion ({status})")
    print(f"  Account      : {r.account.name} ({r.account.id})  "
          f"billing_ready={r.account.is_billing_ready}")
    if not r.invoice_lines:
        print("  Invoice lines: (none)")
    for line in r.invoice_lines:
        sku_part = f"{line.sku} — " if line.sku else ""
        bound = (
            f"product2={line.product.id}" if line.product
            else "no Product2 binding (description-only)"
        )
        print(f"    • {sku_part}{line.name}  "
              f"${line.unit_price} x{line.quantity}  "
              f"taxable={line.taxable}  ({bound})")
    if r.invoice_overrides is not None:
        ov = r.invoice_overrides
        bits = []
        if ov.invoice_date:
            bits.append(f"invoice_date={ov.invoice_date.isoformat()}")
        if ov.due_date:
            bits.append(f"due_date={ov.due_date.isoformat()}")
        if ov.posted_date:
            bits.append(f"posted_date={ov.posted_date.isoformat()}")
        if ov.currency:
            bits.append(f"currency={ov.currency}")
        bits.append(f"should_calculate_tax={ov.should_calculate_tax}")
        if ov.tax_calculation_status:
            bits.append(f"tax_calc_status={ov.tax_calculation_status}")
        print(f"  Invoice ov   : {', '.join(bits)}")
    steps = ["ingest_invoice"]
    if target == "invoice_posted":
        steps.append("promote_to_posted")
    print(f"  Steps        : {' → '.join(steps)}")
    return spec.count


def _print_plan(
    args: argparse.Namespace, ctx: OrgContext, resolved: list
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
        if r.spec.kind == "invoice_ingestion":
            total += _print_invoice_ingestion_spec(r, i, len(resolved))
        else:
            total += _print_pst_spec(r, i, len(resolved))

    print(f"\nWould generate   : {total} transaction(s) total")
    print(f"Billing-ready accounts available: "
          f"{', '.join(a.name for a in ctx.billing_ready_accounts) or '(none)'}")
    print(f"Billable products available     : {len(ctx.products)}")
    print("\n(no records were created — drop --dry-run to execute)\n")


def ctx_api(args: argparse.Namespace) -> str:
    return args.api_version if args.api_version != "latest" else "latest"


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
        resolved = [SCENARIO_HANDLERS[s.kind].resolve(client, ctx, s) for s in specs]
    except KeyError as exc:
        print(f"ERROR: unknown scenario kind: {exc}", file=sys.stderr)
        return 4
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
                  f"implemented through '{IMPLEMENTED_MAX_STAGE}').",
                  file=sys.stderr)

    def on_start(base_run_id: str, total_runs: int, worker_count: int) -> None:
        print(f"Running {total_runs} scenario(s) across {len(resolved)} spec(s), "
              f"concurrency={worker_count}, run base {base_run_id} ...")

    manifests: list[Manifest] = []

    def on_complete(done: int, total_runs: int, m: Manifest, path) -> None:
        manifests.append(m)
        status = "OK" if not m.error else "FAILED"
        retried = f" attempts={m.attempts}" if m.attempts > 1 else ""
        print(f"[{done}/{total_runs}] {m.run_id}: {status} "
              f"reached={m.reached_stage} order={m.order_number or '-'}{retried} "
              f"manifest={path}")

    result = run_batch(
        client, ctx, resolved, concurrency=args.concurrency,
        poll_timeout=args.poll_timeout, on_start=on_start, on_complete=on_complete,
        max_retries=max(0, args.max_retries),
    )

    report = build_batch_report(manifests, base_run_id=result.base_run_id)
    json_path, _md_path = write_batch_report(report, result.manifest_dir)

    print(f"\nDone: {result.total - result.failures}/{result.total} scenario(s) "
          f"succeeded. Manifests in {result.manifest_dir}/")
    print(f"Batch report: {json_path}")
    return 1 if result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
