#!/usr/bin/env python3
"""Inspect the ramp structure of a quote (READ-ONLY).

Loads a quote's ramped groups + lines via ``_resolve.read_quote`` and prints the
segment table — sort order, segment type, dates, and each line's system-generated
``RampIdentifier`` / ``SegmentIdentifier`` (present iff the ramp went through a
``groupRampAction``). Never mutates.

Auth is delegated to the ``sf`` CLI (see ``_client.py``). ``--target-org`` is the
*SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Usage
-----
    python scripts/ramp_deals/inspect_ramp_quote.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0...
    python scripts/ramp_deals/inspect_ramp_quote.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0... --json
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
from scripts.ramp_deals._resolve import ResolveError, read_quote  # noqa: E402


def _print_quote(quote):
    groups = quote.get("groups") or []
    ramped = [g for g in groups if g.get("IsRamped")]
    print(f"Quote {quote.get('Id')}  TotalPrice={quote.get('TotalPrice')} "
          f"Override={quote.get('TotalPriceOverride')}")
    print(f"  {len(groups)} group(s), {len(ramped)} ramped:\n")
    for g in sorted(groups, key=lambda x: x.get("SortOrder") or 0):
        tag = "RAMPED" if g.get("IsRamped") else "plain"
        print(f"  [{tag}] sort={g.get('SortOrder')} type={g.get('SegmentType')} "
              f"{g.get('StartDate')}..{g.get('EndDate')}  ({g.get('Id')})")
        for ln in g.get("lines") or []:
            rid, sid = ln.get("RampIdentifier"), ln.get("SegmentIdentifier")
            marker = "" if (rid and sid) else "  <- MISSING ramp/segment id"
            print(f"      line {ln.get('Id')} product={ln.get('Product2Id')} "
                  f"total={ln.get('TotalPrice')} ramp={rid} seg={sid}{marker}")
        print()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect the ramp structure of a quote. READ-ONLY.",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--quote-id", required=True, help="Quote Id (prefix 0Q0).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the quote structure as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          logger=eprint)
    try:
        quote = read_quote(args.quote_id, transport=transport)
    except (ResolveError, RampClientError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(quote, indent=2))
    else:
        _print_quote(quote)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
