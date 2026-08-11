#!/usr/bin/env python3
"""Delete a BRE Decision Table (DESTRUCTIVE, MUTATING).

Deletes the table via the Tooling API setup-object DELETE
(``tooling/sobjects/DecisionTable/{id}``).

**Active-edit guard.** An Active (or activating) table cannot be deleted in place
(same platform lock as an edit: ``FIELD_NOT_UPDATABLE`` / "Can't edit an active
Decision Table"). This tool **refuses** up front on an active table and points at
``deactivate_decision_table.py`` — deactivate it there first, then delete. Keeping
deactivation in its own script (rather than a ``--deactivate-first`` option here)
means one deactivate implementation, and delete has no partial-state to roll back.
Deleting also fails while the table is still referenced by an active Expression
Set / Context Rule / recipe — resolve those references first.

**Destructive — double-gated.** Preview by default: without ``--confirm`` the tool
resolves the id and logs the plan but deletes nothing. ``--confirm`` is REQUIRED
to actually delete (absence of ``--confirm`` IS the dry run).

Delete only disposable tables you created — never a shipped/managed one.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to Release
262 / v67.0. Destructive round-trips run on **scratch orgs only**, never ``beta``.

Usage
-----
    # preview then delete a throwaway table
    python scripts/decision_tables/delete_decision_table.py \
        --target-org rlm-base__scratch --developer-name ZZ_Probe_DT
    python scripts/decision_tables/delete_decision_table.py \
        --target-org rlm-base__scratch --developer-name ZZ_Probe_DT --confirm

    # if the table is Active, deactivate it first (separate script), then delete
    python scripts/decision_tables/deactivate_decision_table.py \
        --target-org rlm-base__scratch --developer-name ZZ_Probe_DT --confirm
    python scripts/decision_tables/delete_decision_table.py \
        --target-org rlm-base__scratch --developer-name ZZ_Probe_DT --confirm
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
from scripts.decision_tables._lifecycle import (  # noqa: E402
    LifecycleEngine,
    LifecycleError,
)
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete a BRE Decision Table. DESTRUCTIVE (preview by default; "
                    "--confirm REQUIRED to delete).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--confirm", action="store_true",
                        help="REQUIRED to actually delete. Without it, only PREVIEWS.")
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
        return fail_json(args.json, f"Error: {exc}",
                         {"action": "delete", "developerName": args.developer_name,
                          "deleted": False})

    record_id = table_row["Id"]
    current = table_row.get("Status")
    eprint(f"\nDelete DecisionTable '{args.developer_name}' ({record_id}), "
           f"currently Status={current}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    try:
        # An Active table cannot be deleted in place — refuse up front (the platform
        # would reject it with FIELD_NOT_UPDATABLE). Deactivation lives in its own
        # script (deactivate_decision_table.py); assert_editable's message points
        # there. delete_tooling is atomic, so there is no partial state to unwind.
        engine.assert_editable(table_row)
        result = engine.delete_tooling(record_id)
    except (DecisionTableClientError, LifecycleError) as exc:
        return fail_json(
            args.json, f"FAILED: {exc}",
            {"action": "delete", "developerName": args.developer_name,
             "id": record_id, "deleted": False})

    if preview:
        eprint("\n[preview] No deletion performed. Re-run with --confirm to delete.")
    else:
        eprint("\nDeletion complete. Verify with list_decision_tables.py "
               "(the table should no longer appear).")
    if args.json:
        result.setdefault("developerName", args.developer_name)
        print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
