#!/usr/bin/env python3
"""Verify the ramp invariants of a quote (READ-ONLY).

Loads a quote via ``_resolve.read_quote`` and runs ``_verify.verify_quote`` — at
least one ramped group, SegmentType + dates present, contiguous segments, every
ramped line carrying both system identifiers (proof it went through a
``groupRampAction``, not a raw IsRamped PATCH), the expected segment count, and TCV
reconciliation. Prints a per-check report; exits non-zero if any check fails, so it
is usable as a CI / post-build gate.

Auth is delegated to the ``sf`` CLI (see ``_client.py``). ``--target-org`` is the
*SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Usage
-----
    python scripts/ramp_deals/verify_ramp_quote.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0... --expected-segments 3
    python scripts/ramp_deals/verify_ramp_quote.py \
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
from scripts.ramp_deals._verify import verify_quote  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the ramp invariants of a quote. READ-ONLY. "
                    "Exit 0 = all checks pass, 1 = a check failed or an error.",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--quote-id", required=True, help="Quote Id (prefix 0Q0).")
    parser.add_argument("--expected-segments", type=int,
                        help="Assert the ramped-group count equals this.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the result as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          logger=eprint)
    try:
        quote = read_quote(args.quote_id, transport=transport)
    except (ResolveError, RampClientError) as exc:
        eprint(f"Error: {exc}")
        return 1

    result = verify_quote(quote, expected_segments=args.expected_segments)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Quote {args.quote_id}:")
        print(result.format_report())
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
