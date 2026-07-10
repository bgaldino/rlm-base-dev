#!/usr/bin/env python3
"""Deactivate a BRE Decision Table — Status → Inactive (MUTATING).

Sets the table's ``Metadata.status`` to ``Inactive`` (Tooling PATCH of the whole
``Metadata`` complexvalue). Deactivation is **synchronous** (verified 262 /
v67.0): unlike activation there is no ``InactivationInProgress`` transient — the
record reports ``Inactive`` immediately — but this tool still confirms the
terminal state.

Deactivate a table before editing its definition in place (an Active table's
definition is locked — see ``update_decision_table.py --deactivate-first``), or
to take a table offline. Note the platform blocks deactivation of a table still
referenced by an active Expression Set / Context Rule / recipe; that surfaces as
the underlying platform error.

**Preview by default.** Without ``--confirm`` the tool logs the planned state
change and performs no write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to Release
262 / v67.0.

Usage
-----
    python scripts/decision_tables/deactivate_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable
    python scripts/decision_tables/deactivate_decision_table.py \
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
        description="Deactivate a BRE Decision Table (Status → Inactive, synchronous). "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually deactivate. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        table_row = resolve_decision_table(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    record_id = table_row["Id"]
    current = table_row.get("Status")
    eprint(f"\nDeactivate DecisionTable '{args.developer_name}' ({record_id}), "
           f"currently Status={current}, {'PREVIEW' if preview else 'CONFIRM'}")

    if current in ("Inactive", "Draft"):
        eprint(f"Table already Status={current}; nothing to do.")
    else:
        try:
            engine.deactivate(record_id)
        except (DecisionTableClientError, LifecycleError) as exc:
            eprint(f"\nFAILED: {exc}")
            return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({"action": "deactivate", "developerName": args.developer_name,
                          "id": record_id, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
