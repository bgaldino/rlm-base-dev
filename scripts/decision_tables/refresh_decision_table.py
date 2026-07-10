#!/usr/bin/env python3
"""Refresh a BRE Decision Table's cached data via ``refreshDecisionTable`` (MUTATING).

A Decision Table has **two layers**: the DEFINITION (columns/source-object, in
metadata/Tooling) and the DATA (the source SObject/CSV rows synced into the BRE
engine cache). Editing the source data does NOT update what the engine serves
until a **refresh** re-syncs it. This tool invokes the ``refreshDecisionTable``
standard action to trigger that sync.

* **Full refresh** (default) re-syncs the whole dataset.
* ``--incremental`` re-syncs only changed rows.

Two facts encoded here from live probing (262 / v67.0):

* The accepted action input is ``isDecisionTableIncremental`` (**not**
  ``isIncremental``, which the existing CCI tasks send and the action silently
  ignores → an unintended full refresh).
* The refresh is **asynchronous** and returns ``outputValues.Status = "Queued"``
  — it does **not** create an ``AsyncOperationTracker`` row. The completion
  signal is the table's ``LastSyncDate`` (a.k.a. ``Metadata.lastSyncDate`` /
  ``refreshStatus``) advancing; re-check it with ``describe_decision_table.py``
  or ``list_decision_tables.py``.

⚠ **Rate limit: ~100 refreshes/hour per org.** Batch refreshes accordingly; the
platform rejects excess with a limit error.

**Preview by default.** Without ``--confirm`` the tool logs the planned action
invocation and performs no write. Re-run with ``--confirm`` to invoke.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to Release
262 / v67.0.

Usage
-----
    # full refresh (preview, then confirm)
    python scripts/decision_tables/refresh_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable
    python scripts/decision_tables/refresh_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable --confirm

    # incremental refresh
    python scripts/decision_tables/refresh_decision_table.py \
        --target-org rlm-base__scratch --developer-name RLM_MyTable \
        --incremental --confirm
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
        description="Refresh a BRE Decision Table's cached data (refreshDecisionTable "
                    "action; async, ~100/hr). MUTATING (preview by default; --confirm).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--incremental", action="store_true",
                        help="Incremental refresh (changed rows only). Default: full.")
    parser.add_argument("--version-number", type=int,
                        help="Optional VersionNumber to refresh a specific version.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually invoke the refresh. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)

    # Resolve for a clearer error than a bare action failure, and to echo status.
    try:
        table_row = resolve_decision_table(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    mode = "incremental" if args.incremental else "full"
    eprint(f"\nRefresh DecisionTable '{args.developer_name}' ({table_row.get('Id')}), "
           f"mode={mode}, lastSync={table_row.get('LastSyncDate') or 'never'}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")
    eprint("Note: async + rate-limited to ~100 refreshes/hour per org; watch "
           "LastSyncDate for completion, not the returned 'Queued' status.")

    try:
        outcome = engine.refresh(
            args.developer_name,
            incremental=args.incremental,
            version_number=args.version_number,
        )
    except (DecisionTableClientError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No refresh invoked. Re-run with --confirm to invoke.")
    else:
        eprint(f"\nRefresh queued (isSuccess={outcome.get('isSuccess')}, "
               f"status={outcome.get('status')}). Re-check LastSyncDate with "
               f"describe_decision_table.py to confirm the sync landed.")
    if args.json:
        print(json.dumps({"action": "refresh", "developerName": args.developer_name,
                          "id": table_row.get("Id"), "mode": mode,
                          "result": outcome, "dryRun": preview}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
