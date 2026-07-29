#!/usr/bin/env python3
"""Add one ramp segment to an existing ramped quote by cloning (MUTATING).

Clones the quote's **last** ramp segment (only the last can be cloned; the clone
assigns the new segment's dates automatically). Use ``--line-scope RampedLinesOnly``
to drop non-ramped one-time products from the new segment.

**Preview by default.** Without ``--confirm`` the tool resolves the clone source
and logs the planned call but performs no write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``). ``--target-org`` is the
*SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Usage
-----
    python scripts/ramp_deals/add_ramp_segment.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0... --confirm
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Add one ramp segment by cloning the quote's last segment. "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--quote-id", required=True, help="Quote Id (prefix 0Q0).")
    parser.add_argument("--last-segment-group-id",
                        help="Clone source (default: the quote's highest-SortOrder ramped group).")
    parser.add_argument("--line-scope", default="AllLines",
                        choices=("AllLines", "RampedLinesOnly"),
                        help="Whether the clone carries non-ramped lines forward.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually clone the segment. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = RampLifecycle(transport, logger=eprint)

    try:
        result = engine.add_segment(
            quote_id=args.quote_id,
            last_segment_group_id=args.last_segment_group_id,
            line_scope=args.line_scope,
        )
    except (PayloadError, RampLifecycleError, RampClientError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No segment added. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({**result, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
