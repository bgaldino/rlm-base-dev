"""CLI entry point for the demo data generator.

    python -m scripts.demo_data.generate --org <sf-alias> [options]

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
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional

from . import lifecycle
from .auth import DEFAULT_API_VERSION, SfApiError, SfCliError, SfRestClient
from .discovery import Account, DiscoveryError, OrgContext, Product, discover
from .lifecycle import LifecycleError, Manifest

log = logging.getLogger("demo_data")

STAGES = ["opportunity", "quote", "order", "activate", "invoice", "post"]

# Full lifecycle implemented as of Phase 3 (through post).
_IMPLEMENTED_MAX_STAGE = "post"

MANIFEST_DIR = os.path.join(os.path.dirname(__file__), "out")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m scripts.demo_data.generate",
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
                   help="Skip the discovery PST probe (trust the config).")
    p.add_argument("--keep-probes", action="store_true",
                   help="Do not delete probe quotes after discovery.")
    p.add_argument("--dry-run", action="store_true",
                   help="Resolve auth+discovery and print planned calls; no writes.")
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="-v for INFO, -vv for DEBUG.")
    return p.parse_args(argv)


def _setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(message)s")


def _print_plan(args: argparse.Namespace, ctx: OrgContext) -> None:
    """Human-readable dry-run summary of what a run would do."""
    target_stage = args.target_stage or "post"
    count = args.count or 1
    acct = ctx.default_account()
    prod = ctx.default_product()
    stages_run = STAGES[STAGES.index("opportunity") if args.with_opportunity
                         else STAGES.index("quote"): STAGES.index(target_stage) + 1]

    print("\n=== Demo Data Generator — DRY RUN (no writes) ===")
    print(f"Org              : {args.org}  (api v{ctx_api(args)})  transport={args.transport}")
    print(f"Pricebook        : {ctx.pricebook_name} ({ctx.pricebook_id})")
    print(f"Legal entity     : {ctx.legal_entity_name}")
    print(f"Opportunity stage: {ctx.opportunity_stage}")
    print(f"\nAccount          : {acct.name} ({acct.id})  "
          f"billing_ready={acct.is_billing_ready}")
    print(f"Product          : {prod.sku} — {prod.name}  "
          f"${prod.unit_price}  (PBE {prod.pricebook_entry_id})")
    print(f"\nWould generate   : {count} transaction(s), target_stage={target_stage}")

    # Cap stage if the account cannot be billed.
    capped = target_stage
    if not acct.is_billing_ready and target_stage in ("invoice", "post"):
        capped = "activate"
        print(f"⚠  Account is not billing-ready (no BillingAccount) — "
              f"would cap at '{capped}' instead of '{target_stage}'.")
        stages_run = STAGES[STAGES.index(stages_run[0]): STAGES.index(capped) + 1]

    print(f"\nLifecycle stages this run would execute:")
    for s in stages_run:
        print(f"  • {s}")
    print(f"\nBilling-ready accounts available: "
          f"{', '.join(a.name for a in ctx.billing_ready_accounts) or '(none)'}")
    print(f"Billable products available     : {len(ctx.products)}")
    if STAGES.index(capped) > STAGES.index(_IMPLEMENTED_MAX_STAGE):
        print(f"\nNote: stages past '{_IMPLEMENTED_MAX_STAGE}' "
              f"(invoice/post) are not yet implemented (Phase 3) — a live run "
              f"would stop at '{_IMPLEMENTED_MAX_STAGE}'.")
    print("\n(no records were created — drop --dry-run to execute)\n")


def ctx_api(args: argparse.Namespace) -> str:
    return args.api_version if args.api_version != "latest" else "latest"


def _effective_stage(target_stage: str, account: Account) -> str:
    """Resolve the stage a scenario will actually reach.

    Caps at what's implemented, and at 'activate' for accounts that aren't
    billing-ready (can't reach invoice/post).
    """
    stage = target_stage
    if STAGES.index(stage) > STAGES.index(_IMPLEMENTED_MAX_STAGE):
        stage = _IMPLEMENTED_MAX_STAGE
    if not account.is_billing_ready and STAGES.index(stage) > STAGES.index("activate"):
        stage = "activate"
    return stage


def run_scenario(
    client: SfRestClient,
    ctx: OrgContext,
    run_id: str,
    target_stage: str,
    account: Account,
    product: Product,
    with_opportunity: bool,
    quantity: int,
    poll_timeout: int,
) -> Manifest:
    """Drive one transaction through the lifecycle up to ``target_stage``.

    Records every created id in the manifest as it goes -- including on partial
    failure (PST commits the quote header even on a failed place), so cleanup
    can find orphans.
    """
    m = Manifest(run_id=run_id)
    stage = _effective_stage(target_stage, account)
    stop_at = STAGES.index(stage)
    try:
        if with_opportunity and ctx.opportunity_stage:
            m.opportunity_id = lifecycle.create_opportunity(
                client, account, ctx.opportunity_stage, run_id
            )
            m.reached_stage = "opportunity"

        # quote (PST) -- always the minimum
        try:
            m.quote_id = lifecycle.place_sales_transaction(
                client, account, product, ctx.pricebook_id, run_id,
                quantity=quantity, opportunity_id=m.opportunity_id,
            )
        except LifecycleError as exc:
            # PST may have committed the quote header even on failure.
            if exc.record_id:
                m.quote_id = exc.record_id
            raise
        m.reached_stage = "quote"
        if stop_at == STAGES.index("quote"):
            return m

        m.order_id, m.order_number = lifecycle.create_order_from_quote(client, m.quote_id)
        m.reached_stage = "order"
        if stop_at == STAGES.index("order"):
            return m

        # activate: set shipping first (mandatory), capture timestamp for asset poll
        lifecycle.set_shipping_address(client, m.order_id, account)
        since = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lifecycle.activate_order(client, m.order_id)
        m.reached_stage = "activate"
        m.billing_schedule_ids = lifecycle.poll_billing_schedules(
            client, m.order_id, timeout=poll_timeout
        )
        m.asset_ids = lifecycle.poll_assets(
            client, account, product, since, timeout=poll_timeout
        )
        if stop_at == STAGES.index("activate"):
            return m

        # invoice: generate Draft, correlate, tag Description while mutable
        m.invoice_id, m.invoice_number = lifecycle.generate_invoice(
            client, m.billing_schedule_ids, run_id, timeout=poll_timeout
        )
        lifecycle.tag_invoice(client, m.invoice_id, run_id)
        m.reached_stage = "invoice"
        if stop_at == STAGES.index("invoice"):
            return m

        # post, then link invoice -> order (ReferenceEntityId is Posted-only)
        m.invoice_number = lifecycle.post_invoice(
            client, m.invoice_id, run_id, timeout=poll_timeout
        )
        m.reached_stage = "post"
        lifecycle.link_invoice_to_order(client, m.invoice_id, m.order_id)
    except LifecycleError as exc:
        m.error = str(exc)
        log.error("scenario %s failed: %s", run_id, exc)
    return m


def _write_manifest(m: Manifest) -> str:
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    path = os.path.join(MANIFEST_DIR, f"{m.run_id}.json")
    with open(path, "w") as f:
        json.dump(m.to_dict(), f, indent=2)
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

    if args.dry_run:
        try:
            _print_plan(args, ctx)
        except DiscoveryError as exc:
            print(f"ERROR: cannot plan a run:\n  {exc}", file=sys.stderr)
            return 3
        return 0

    # ----- live execution (Phase 2: up to activate) -----
    try:
        account = (ctx.default_account() if not args.account
                   else next(a for a in ctx.billing_ready_accounts
                             if a.name == args.account))
        product = ctx.default_product()
    except (DiscoveryError, StopIteration):
        print(f"ERROR: could not resolve a usable account/product for the run.",
              file=sys.stderr)
        return 3

    target_stage = args.target_stage or "post"
    count = args.count or 1
    base_run_id = "DEMO-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    effective = _effective_stage(target_stage, account)
    if effective != target_stage:
        print(f"Note: capping target_stage '{target_stage}' -> '{effective}' "
              f"(account billing_ready={account.is_billing_ready}; "
              f"implemented through '{_IMPLEMENTED_MAX_STAGE}').", file=sys.stderr)

    manifests: list[Manifest] = []
    failures = 0
    for i in range(count):
        run_id = base_run_id if count == 1 else f"{base_run_id}-{i + 1:03d}"
        m = run_scenario(
            client, ctx, run_id, target_stage, account, product,
            with_opportunity=args.with_opportunity,
            quantity=1,
            poll_timeout=args.poll_timeout,
        )
        path = _write_manifest(m)
        manifests.append(m)
        status = "OK" if not m.error else "FAILED"
        print(f"[{i + 1}/{count}] {run_id}: {status} "
              f"reached={m.reached_stage} order={m.order_number or '-'} "
              f"manifest={path}")
        if m.error:
            failures += 1

    print(f"\nDone: {count - failures}/{count} scenario(s) succeeded "
          f"(reached '{effective}'). Manifests in {MANIFEST_DIR}/")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
