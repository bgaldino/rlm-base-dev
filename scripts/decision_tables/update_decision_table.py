#!/usr/bin/env python3
"""Update a BRE Decision Table definition from a canonical spec (MUTATING).

Applies a canonical spec (see ``_schema.py``) to an **existing** table via the
Tooling API. The metadata path is deploy-based (re-run
``create_decision_table.py --path metadata``, which is an idempotent upsert), so
``update`` covers the Tooling REST verb:

* Tooling ``DecisionTable`` PATCH with ``{"Metadata": {…}}`` (the id is in the
  URL). The ``decisionTableParameters`` array is a **full replace**: send the
  complete column set you want, not a delta. A PATCH is **atomic** — a rejected
  PATCH leaves the record byte-identical.

**Active-edit guard.** An Active (or activating) table's definition cannot be
edited in place — the platform returns ``FIELD_NOT_UPDATABLE`` / "Can't edit an
active Decision Table". By default this tool **refuses** up front on an active
table. Pass ``--deactivate-first`` to run the guarded
deactivate → update → reactivate sequence instead: the table is deactivated,
patched, and (unless ``--leave-deactivated``) reactivated. On the atomic Tooling
PATCH a failed edit is still reactivated because the definition remains unchanged.

**Preview by default.** Without ``--confirm`` the tool validates the spec and logs
the planned write but performs no org write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to Release
262 / v67.0. Destructive round-trips run on **scratch orgs only**, never ``beta``.

Usage
-----
    # preview then apply a Tooling-path update
    python scripts/decision_tables/update_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json
    python scripts/decision_tables/update_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json --confirm

    # edit an ACTIVE table: deactivate → patch → reactivate
    python scripts/decision_tables/update_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json \
        --deactivate-first --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables import _payload  # noqa: E402
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DecisionTableClientError,
    Transport,
    eprint,
)
from scripts.decision_tables._lifecycle import (  # noqa: E402
    LifecycleEngine,
    LifecycleError,
    MutationVerificationError,
)
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402
from scripts.decision_tables._schema import validate_spec  # noqa: E402


def _load_spec(path):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Update an existing BRE Decision Table from a canonical spec. "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--spec", required=True,
                        help="Path to the canonical spec JSON ('-' for stdin).")
    parser.add_argument("--developer-name",
                        help="DecisionTable DeveloperName (default: the spec's fullName).")
    parser.add_argument("--deactivate-first", action="store_true",
                        help="If the table is Active, deactivate → update → reactivate "
                             "(the deactivate-first guarded sequence). Without it, an "
                             "active table is REFUSED.")
    parser.add_argument("--leave-deactivated", action="store_true",
                        help="With --deactivate-first: skip the reactivate step, leaving "
                             "the table Inactive after the update.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually apply. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    try:
        spec = _load_spec(args.spec)
    except (OSError, ValueError) as exc:
        eprint(f"Error: could not read spec '{args.spec}': {exc}")
        return 1

    result = validate_spec(spec)
    eprint(result.format_report())
    if not result.passed:
        eprint("\nSpec has errors; not updating. Fix them and retry.")
        return 1

    dev_name = args.developer_name or spec.get("fullName")
    if not dev_name:
        eprint("Error: no DeveloperName — pass --developer-name or set fullName in the spec.")
        return 1

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)
    summary = {"action": "update", "path": "tooling", "developerName": dev_name,
               "dryRun": preview}

    try:
        table_row = resolve_decision_table(transport, dev_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    record_id = table_row["Id"]
    summary["id"] = record_id
    eprint(f"\nUpdate DecisionTable '{dev_name}' ({record_id}) via Tooling, "
           f"status={table_row.get('Status')}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    def _do_mutate():
        # A Tooling Metadata PATCH REQUIRES status. Stamp the table's CURRENT
        # LIVE status — read now, so during a deactivate-first sequence it is the
        # already-deactivated Inactive — never the spec's (often Active, which
        # would re-activate the table mid-edit and defeat --leave-deactivated).
        live_status = engine.get_status(record_id) or table_row.get("Status")
        body = _payload.tooling_metadata_only(spec, live_status=live_status)
        transport.tooling_sobject("PATCH", "DecisionTable", record_id, body=body)
        if not preview:
            written = transport.tooling_sobject("GET", "DecisionTable", record_id)
            live_metadata = written.get("Metadata") if isinstance(written, dict) else None
            if not isinstance(live_metadata, dict):
                raise MutationVerificationError(
                    f"Tooling update verification could not read DecisionTable/{record_id} "
                    "Metadata after PATCH."
                )
            mismatches = _payload.verify_requested_metadata(spec, live_metadata)
            if mismatches:
                raise MutationVerificationError(
                    "Tooling update GET-back did not match the requested definition:\n- "
                    + "\n- ".join(mismatches)
                )

    try:
        if args.deactivate_first:
            engine.run_guarded_update(
                table_row=table_row,
                mutate=_do_mutate,
                activate_after=not args.leave_deactivated,
                verb="update",
            )
        else:
            # Refuse up front on an active table (with actionable guidance).
            engine.assert_editable(table_row)
            _do_mutate()
    except (DecisionTableClientError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    else:
        eprint("\nUpdate complete. Verify with describe_decision_table.py "
               "(parameters are a full replace; GET-back to confirm).")
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
