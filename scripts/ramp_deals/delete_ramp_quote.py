#!/usr/bin/env python3
"""Delete a ramped quote (MUTATING, destructive).

Deletes the Quote sObject; its QuoteLineGroups and QuoteLineItems cascade by
platform rules. Intended for cleaning up quotes authored on a disposable org
during exploration — NOT for production data.

**Preview by default, AND requires the quote id to be echoed back.** Without
``--confirm`` nothing is deleted. Because deletion is destructive and
irreversible, ``--confirm`` alone is not enough: you must also pass
``--yes-delete <quote-id>`` matching ``--quote-id`` exactly.

Auth is delegated to the ``sf`` CLI (see ``_client.py``). ``--target-org`` is the
*SF CLI* alias, never the CCI alias. Pinned to 264 / v68.0.

Usage
-----
    # preview
    python scripts/ramp_deals/delete_ramp_quote.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0...
    # delete for real (double-confirm)
    python scripts/ramp_deals/delete_ramp_quote.py \
        --target-org rlm-base__sdb39 --quote-id 0Q0... \
        --confirm --yes-delete 0Q0...
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
from scripts.ramp_deals._resolve import ResolveError, read_quote  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete a ramped quote (destructive). Preview by default; "
                    "requires --confirm AND --yes-delete <quote-id> to apply.",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__sdb39) — NOT the CCI alias.")
    parser.add_argument("--quote-id", required=True, help="Quote Id to delete (prefix 0Q0).")
    parser.add_argument("--confirm", action="store_true",
                        help="Required to delete. Still needs --yes-delete to match.")
    parser.add_argument("--yes-delete",
                        help="Must equal --quote-id exactly to authorize the destructive delete.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    authorized = args.confirm and args.yes_delete == args.quote_id
    if args.confirm and not authorized:
        eprint("Refusing to delete: --yes-delete must exactly match --quote-id "
               f"(got --yes-delete={args.yes_delete!r}, --quote-id={args.quote_id!r}).")
        return 1

    preview = not authorized
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = RampLifecycle(transport, logger=eprint)

    try:
        # Read the quote first so a preview shows what would be destroyed and a
        # bad id fails loudly before any delete is attempted.
        quote = read_quote(args.quote_id, transport=transport)
        groups = quote.get("groups") or []
        line_count = sum(len(g.get("lines") or []) for g in groups)
        eprint(f"quote {args.quote_id}: {len(groups)} group(s), {line_count} line(s) "
               f"{'would be' if preview else 'will be'} deleted")
        result = engine.delete_quote(args.quote_id)
    except (ResolveError, RampLifecycleError, RampClientError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] Nothing deleted. Re-run with --confirm --yes-delete "
               f"{args.quote_id} to delete.")
    if args.json:
        print(json.dumps({**result, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
