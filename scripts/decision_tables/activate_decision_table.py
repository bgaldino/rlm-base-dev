#!/usr/bin/env python3
"""Activate a BRE Decision Table — Status → Active (MUTATING).

Sets the table's ``Metadata.status`` to ``Active`` (Tooling PATCH of the whole
``Metadata`` complexvalue) and then **polls** until ``Status = Active``.
Activation is **asynchronous** (verified 262 / v67.0): the PATCH returns 204 but
the record transits ``ActivationInProgress`` for ~10–15s before settling to
``Active``. This tool waits past that transient; use ``--max-wait`` to raise the
timeout for a large table.

Activation requires a valid definition (e.g. a default dataset mapping for a
multi-object table); the platform rejects an incomplete one. Re-enable a table
left DEACTIVATED by a failed ``update_decision_table.py`` here after
inspecting/restoring it.

**Preview by default.** Without ``--confirm`` the tool logs the planned state
change and performs no write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to Release
262 / v67.0.

Usage
-----
    python scripts/decision_tables/activate_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable
    python scripts/decision_tables/activate_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DecisionTableClientError,
    Transport,
    eprint,
)
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Activate a BRE Decision Table (Status → Active, async poll). "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--max-wait", type=int, default=90,
                        help="Seconds to poll past ActivationInProgress (default 90).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually activate. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint, max_wait_seconds=args.max_wait)

    try:
        table_row = resolve_decision_table(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    record_id = table_row["Id"]
    current = table_row.get("Status")
    eprint(f"\nActivate DecisionTable '{args.developer_name}' ({record_id}), "
           f"currently Status={current}, {'PREVIEW' if preview else 'CONFIRM'}")

    if current == "Active":
        eprint("Table already Active; nothing to do.")
    else:
        try:
            engine.activate(record_id)
        except (DecisionTableClientError, LifecycleError) as exc:
            eprint(f"\nFAILED: {exc}")
            return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({"action": "activate", "developerName": args.developer_name,
                          "id": record_id, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
