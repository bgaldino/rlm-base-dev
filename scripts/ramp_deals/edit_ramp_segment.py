#!/usr/bin/env python3
"""Edit an existing ramp segment's dates / type / sort order (MUTATING).

Runs an ``EditGroup`` groupRampAction against one QuoteLineGroup — the same action
that converts a plain group into the first segment — to change its ``StartDate`` /
``EndDate`` / ``SegmentType`` / ``SortOrder``. The segment stays ramped
(``IsRamped=true``); its lines' system identifiers are preserved by the action.

**Preview by default.** Without ``--confirm`` the tool logs the planned EditGroup
body but performs no write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``). ``--target-org`` is the
*SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Usage
-----
    python scripts/ramp_deals/edit_ramp_segment.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0... --group-id 1C9... \
        --start-date 2026-01-01 --end-date 2026-12-31 --segment-type Custom \
        --confirm
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
from scripts.ramp_deals._schedule import SEGMENT_TYPES  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Edit a ramp segment's dates / type / sort order via EditGroup. "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--quote-id", required=True, help="Quote Id (prefix 0Q0).")
    parser.add_argument("--group-id", required=True,
                        help="QuoteLineGroup Id of the segment to edit (prefix 1C9).")
    parser.add_argument("--start-date", required=True, help="Segment start (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=True, help="Segment end (YYYY-MM-DD).")
    parser.add_argument("--segment-type", required=True,
                        help=f"One of {sorted(SEGMENT_TYPES)} (trial value is 'FreeTrial').")
    parser.add_argument("--sort-order", type=int, default=1,
                        help="Segment sort order (default 1).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually edit the segment. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = RampLifecycle(transport, logger=eprint)

    try:
        result = engine.edit_segment(
            quote_id=args.quote_id, group_id=args.group_id,
            start_date=args.start_date, end_date=args.end_date,
            segment_type=args.segment_type, sort_order=args.sort_order,
        )
    except (PayloadError, RampLifecycleError, RampClientError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No segment edited. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({**result, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
