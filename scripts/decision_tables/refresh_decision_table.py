#!/usr/bin/env python3
"""Queue a full or incremental BRE Decision Table refresh.

The command uses the standard ``refreshDecisionTable`` action. Refresh is
asynchronous, previews by default, and requires ``--confirm`` to write.
Versioned CSV tables also require ``--version-number``.

``--incremental`` is refused when the table has ``isIncrementalSyncEnabled``
false — the action accepts such a request and then syncs nothing.
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
    get_decision_table_metadata,
    resolve_decision_table,
    tristate_bool,
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
                        help="Incremental refresh (changed rows only). Default: full. "
                             "Refused unless the table has isIncrementalSyncEnabled=true.")
    parser.add_argument("--allow-disabled-incremental", action="store_true",
                        help="With --incremental, queue the refresh anyway when the "
                             "table reports isIncrementalSyncEnabled=false. The action "
                             "accepts that request and syncs nothing. Default: refuse.")
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

    mode = "incremental" if args.incremental else "full"
    signal_field = "LastIncrementalSyncDate" if args.incremental else "LastSyncDate"
    eprint(f"\nRefresh DecisionTable '{args.developer_name}' ({table_row.get('Id')}), "
           f"mode={mode}, {signal_field}={table_row.get(signal_field) or 'never'}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")
    eprint("Note: asynchronous; watch " + signal_field +
           " for completion, not the returned 'Queued' status. Full-refresh "
           "limits are 40 Standard and 60 Advanced per org/hour; CSV uses "
           "the Advanced pool.")

    # ⚠ An incremental request against a table with isIncrementalSyncEnabled =
    # false is ACCEPTED by the action and then syncs nothing: the caller sees
    # isSuccess=true / Status=Queued while the data stays stale. The flag is
    # false on every Decision Table this repo ships, so that no-op is the
    # DEFAULT outcome of --incremental rather than an edge case — hence a
    # pre-check rather than leaving it to the platform, which reports no error
    # here for the toolkit to surface.
    #
    # Refused, not silently downgraded to a full refresh: a full sync is a
    # heavier operation than the caller asked for. This matches the in-org
    # Decision Table Manager's rule
    # (unpackaged/post_utils/classes/RLM_DecisionTableManagerController.cls →
    # refreshTables). The gate runs in PREVIEW too — a preview that reported a
    # queued no-op would be exactly the misreport this guards against.
    if args.incremental:
        try:
            record = get_decision_table_metadata(transport, table_row.get("Id"))
        except (DecisionTableClientError, ResolveError) as exc:
            return fail_json(
                args.json,
                f"Error: could not read the table's Metadata to confirm incremental "
                f"sync is enabled: {exc}",
                {"action": "refresh", "developerName": args.developer_name,
                 "id": table_row.get("Id"), "mode": mode},
            )
        incremental_enabled = tristate_bool(
            (record.get("Metadata") or {}).get("isIncrementalSyncEnabled")
        )
        if incremental_enabled is False and not args.allow_disabled_incremental:
            return fail_json(
                args.json,
                f"FAILED: incremental sync is not enabled on "
                f"'{args.developer_name}' (isIncrementalSyncEnabled=false). An "
                f"incremental refresh there is accepted and then changes nothing. "
                f"Run a full refresh (drop --incremental), enable incremental sync "
                f"on the table first, or pass --allow-disabled-incremental to queue "
                f"the no-op anyway.",
                {"action": "refresh", "developerName": args.developer_name,
                 "id": table_row.get("Id"), "mode": mode,
                 "isIncrementalSyncEnabled": False},
            )
        if incremental_enabled is False:
            eprint("\nWARNING: isIncrementalSyncEnabled=false and "
                   "--allow-disabled-incremental was passed. The action will "
                   "accept this request and sync nothing.")
        elif incremental_enabled is None:
            eprint("\nWARNING: the table reported no isIncrementalSyncEnabled "
                   "value, so the incremental precondition could not be "
                   "confirmed. If incremental sync is disabled, the action "
                   "accepts this request and syncs nothing.")

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
                   f"{signal_field} with describe_decision_table.py to confirm the "
                   f"sync landed.")
        elif status is None:
            # isSuccess=true but the action reported no Status. The POST already
            # fired, so the refresh was accepted — don't fail conservatively and
            # mislead the user into thinking nothing was queued. Treat as a soft
            # success and point them at the async completion signal.
            eprint(f"\nRefresh accepted (isSuccess=true, no status reported). "
                   f"Re-check {signal_field} with describe_decision_table.py to "
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
