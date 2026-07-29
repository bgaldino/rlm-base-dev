#!/usr/bin/env python3
"""Build a multi-segment ramped Revenue Cloud quote end-to-end (MUTATING).

Resolves catalog names to ids, sizes the ramp schedule, then runs the full
place → EditGroup → clone×N → verify sequence through :class:`_lifecycle.
RampLifecycle`. This is the top-level authoring verb; ``plan_ramp_schedule`` is its
pure dry-run companion (schedule only, no org).

**Preview by default.** Without ``--confirm`` the tool resolves ids and logs the
planned call sequence but performs no write (the Transport runs ``dry_run=True``,
which short-circuits every mutating verb and skips the status polls). Re-run with
``--confirm`` to actually author the quote.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Lines are given as ``SKU:QTY`` (or ``SKU:QTY:UNITPRICE`` to override list price).
The SKU is resolved to a Product2 + active PricebookEntry in the chosen pricebook.

Usage
-----
    # preview a 3-year yearly ramp of two products
    python scripts/ramp_deals/build_ramp_quote.py \
        --target-org rlm-base__sdb39 \
        --account "Laulima" --pricebook "Standard Price Book" \
        --segment-type Yearly --segments 3 --start-date 2026-01-01 \
        --line SKU-PLATFORM:10 --line SKU-SUPPORT:1

    # ... then author it
    python scripts/ramp_deals/build_ramp_quote.py ... --confirm --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.ramp_deals._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    RampClientError,
    Transport,
    eprint,
)
from scripts.ramp_deals._lifecycle import RampLifecycle, RampLifecycleError  # noqa: E402
from scripts.ramp_deals._payload import PayloadError  # noqa: E402
from scripts.ramp_deals._schedule import ScheduleError, build_schedule  # noqa: E402
from scripts.ramp_deals._resolve import (  # noqa: E402
    ResolveError,
    resolve_account_id,
    resolve_line_ids,
    resolve_pricebook_id,
    resolve_standard_pricebook_id,
)


def _parse_line(spec: str) -> dict:
    """Parse a ``SKU:QTY[:UNITPRICE]`` line spec into a resolver-ready dict."""
    parts = spec.split(":")
    if len(parts) < 2 or not parts[0]:
        raise argparse.ArgumentTypeError(
            f"line {spec!r} must be SKU:QTY or SKU:QTY:UNITPRICE"
        )
    line = {"sku": parts[0]}
    try:
        line["Quantity"] = int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"line {spec!r}: QTY must be an integer")
    if len(parts) >= 3 and parts[2]:
        try:
            line["UnitPrice"] = float(parts[2])
        except ValueError:
            raise argparse.ArgumentTypeError(f"line {spec!r}: UNITPRICE must be a number")
    return line


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a multi-segment ramped quote end-to-end. MUTATING "
                    "(preview by default; --confirm to author).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--account", required=True, help="Account name (or Id).")
    parser.add_argument("--pricebook",
                        help="Pricebook2 name (or Id). Default: the standard pricebook.")
    parser.add_argument("--opportunity", help="Optional Opportunity Id to link.")
    parser.add_argument("--currency", help="Optional CurrencyIsoCode (multi-currency orgs).")
    parser.add_argument("--quote-name", default="Ramped Quote", help="Quote Name.")
    parser.add_argument("--segment-type", required=True,
                        help="Paid-segment type (Custom/Yearly/Prorated). Trial via --trial-months.")
    parser.add_argument("--segments", type=int, required=True,
                        help="Number of PAID segments (trial excluded).")
    parser.add_argument("--start-date", required=True, help="First segment start (YYYY-MM-DD).")
    parser.add_argument("--months-per-segment", type=int, default=12,
                        help="Calendar months per paid segment (ignored for Yearly).")
    parser.add_argument("--trial-months", type=int, default=0,
                        help="Leading FreeTrial length in months; 0 = no trial.")
    parser.add_argument("--line", dest="lines", action="append", type=_parse_line,
                        required=True, metavar="SKU:QTY[:PRICE]",
                        help="A quote line (repeatable).")
    parser.add_argument("--line-scope", default="AllLines",
                        choices=("AllLines", "RampedLinesOnly"),
                        help="Whether clones carry non-ramped lines forward.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually author the quote. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)

    try:
        # 1. size the schedule (pure — fails fast on a bad term before any org call).
        schedule = build_schedule(
            start_date=args.start_date, segment_type=args.segment_type,
            segment_count=args.segments, months_per_segment=args.months_per_segment,
            trial_months=args.trial_months,
        )
        eprint(f"schedule: {len(schedule)} segment(s) "
               f"({args.segments} paid{', +trial' if args.trial_months else ''})")

        # 2. resolve catalog names -> ids (reads execute even under preview).
        account_id = resolve_account_id(args.account, transport=transport)
        pricebook_id = (
            resolve_pricebook_id(args.pricebook, transport=transport)
            if args.pricebook else resolve_standard_pricebook_id(transport=transport)
        )
        lines = [resolve_line_ids(ln, pricebook_id=pricebook_id, transport=transport)
                 for ln in args.lines]
        eprint(f"resolved account={account_id} pricebook={pricebook_id} "
               f"lines={len(lines)}")

        # 3. run the build (mutations are skipped under preview by the Transport).
        engine = RampLifecycle(transport, logger=eprint)
        result = engine.build_ramped_quote(
            account_id=account_id, pricebook_id=pricebook_id, lines=lines,
            schedule=schedule, opportunity_id=args.opportunity, currency=args.currency,
            quote_name=args.quote_name, line_scope=args.line_scope,
            verify=not preview,
        )
    except (ScheduleError, PayloadError, ResolveError, RampLifecycleError,
            RampClientError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No quote authored. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({
            "account": args.account, "accountId": account_id,
            "pricebookId": pricebook_id, "segments": len(schedule),
            "quoteId": result.get("quote_id"), "status": result.get("status"),
            "verified": bool((result.get("verify") or {}).get("passed")),
            "dryRun": preview,
        }, indent=2))
    else:
        eprint(f"\nquote: {result.get('quote_id')}  status={result.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
