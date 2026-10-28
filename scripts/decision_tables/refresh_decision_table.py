#!/usr/bin/env python3
"""Queue a full or incremental BRE Decision Table refresh.

The command uses the standard ``refreshDecisionTable`` action. Refresh is
asynchronous, previews by default, and requires ``--confirm`` to write.
Versioned CSV tables also require ``--version-number``.

⚠ In Release 264 the request does not fix the type that runs: without
``--incremental`` the platform chooses full or incremental itself (org preference
``AutoSelectRefreshDT``), and it does not consult ``isIncrementalSyncEnabled``. So
completion is the later of ``LastSyncDate`` and ``LastIncrementalSyncDate``.
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
    fail_json,
)
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._resolve import (  # noqa: E402
    ResolveError,
    resolve_decision_table,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Refresh a BRE Decision Table's cached data (asynchronous "
                    "refreshDecisionTable action). MUTATING (preview by default; --confirm).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--incremental", action="store_true",
                        help="Request an incremental refresh (changed rows only). Without "
                             "it, Release 264 chooses full or incremental itself.")
    # Kept so existing invocations still parse. It overrode a refusal on
    # isIncrementalSyncEnabled=false that Release 264 made wrong (issue #587).
    parser.add_argument("--allow-disabled-incremental", action="store_true",
                        help="No effect; kept for compatibility (issue #587).")
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
        return fail_json(args.json, f"Error: {exc}",
                         {"action": "refresh", "developerName": args.developer_name})

    # The REQUESTED mode, kept as "full"/"incremental" for JSON consumers. In
    # Release 264 a full request can run as incremental, which the log line says.
    mode = "incremental" if args.incremental else "full"
    shown = mode if args.incremental else "full requested (264 may run incremental)"
    eprint(f"\nRefresh DecisionTable '{args.developer_name}' ({table_row.get('Id')}), "
           f"mode={shown}, LastSyncDate={table_row.get('LastSyncDate') or 'never'}, "
           f"LastIncrementalSyncDate={table_row.get('LastIncrementalSyncDate') or 'never'}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")
    eprint("Note: asynchronous; completion is the later of LastSyncDate and "
           "LastIncrementalSyncDate, not the returned 'Queued' status. Full-refresh "
           "limits are 40 Standard and 60 Advanced per org/hour; CSV uses "
           "the Advanced pool.")

    # No isIncrementalSyncEnabled gate. This used to refuse --incremental on a
    # table with the flag false; Release 264 does not consult the flag (issue #587).

    try:
        outcome = engine.refresh(
            args.developer_name,
            incremental=args.incremental,
            version_number=args.version_number,
        )
    except (DecisionTableClientError, LifecycleError) as exc:
        return fail_json(args.json, f"FAILED: {exc}",
                         {"action": "refresh", "developerName": args.developer_name,
                          "id": table_row.get("Id"), "mode": mode})

    summary = {"action": "refresh", "developerName": args.developer_name,
               "id": table_row.get("Id"), "mode": mode,
               "result": outcome, "dryRun": preview}
    if preview:
        eprint("\n[preview] No refresh invoked. Re-run with --confirm to invoke.")
    elif outcome.get("isSuccess") is False:
        return fail_json(
            args.json,
            f"FAILED: Salesforce rejected the refresh "
            f"(isSuccess=false, status={outcome.get('status')!r}).",
            summary,
        )
    elif outcome.get("isSuccess") is None:
        return fail_json(
            args.json,
            f"FAILED: Salesforce returned no isSuccess value for the refresh "
            f"(status={outcome.get('status')!r}).",
            summary,
        )
    else:
        status = outcome.get("status")
        if status == "Queued":
            eprint(f"\nRefresh queued (isSuccess=true, status=Queued). Re-check "
                   f"the later of LastSyncDate and LastIncrementalSyncDate with "
                   f"describe_decision_table.py to confirm the "
                   f"sync landed.")
        elif status is None:
            # isSuccess=true but the action reported no Status. The POST already
            # fired, so the refresh was accepted — don't fail conservatively and
            # mislead the user into thinking nothing was queued. Treat as a soft
            # success and point them at the async completion signal.
            eprint(f"\nRefresh accepted (isSuccess=true, no status reported). "
                   f"Re-check the later of LastSyncDate and LastIncrementalSyncDate with "
                   f"describe_decision_table.py to "
                   f"confirm the sync landed.")
        else:
            return fail_json(
                args.json,
                f"FAILED: Salesforce returned isSuccess=true but refresh status "
                f"{status!r}, not 'Queued'.",
                summary,
            )
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
