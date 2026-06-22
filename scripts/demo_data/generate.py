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
import logging
import sys
from typing import Optional

from .auth import DEFAULT_API_VERSION, SfApiError, SfCliError, SfRestClient
from .discovery import DiscoveryError, OrgContext, discover

log = logging.getLogger("demo_data")

STAGES = ["opportunity", "quote", "order", "activate", "invoice", "post"]


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
    print("\n(no records were created — drop --dry-run to execute once Phase 2 lands)\n")


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

    if args.dry_run:
        try:
            _print_plan(args, ctx)
        except DiscoveryError as exc:
            print(f"ERROR: cannot plan a run:\n  {exc}", file=sys.stderr)
            return 3
        return 0

    # Phase 2 wires lifecycle.py here.
    print("Live execution is not yet wired (Phase 2). Re-run with --dry-run to "
          "preview the plan. See scripts/demo_data/CONTRACTS.md for the locked "
          "lifecycle contracts.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
