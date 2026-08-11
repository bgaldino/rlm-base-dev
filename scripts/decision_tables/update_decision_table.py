#!/usr/bin/env python3
"""Update a BRE Decision Table definition from a canonical spec (MUTATING).

Applies a canonical spec (see ``_schema.py``) to an **existing** table via the
Tooling API. The metadata path is deploy-based (re-run
``create_decision_table.py --path metadata``, which is an idempotent upsert), so
``update`` covers the Tooling REST verb:

* Tooling ``DecisionTable`` PATCH with ``{"Metadata": {…}}`` (the id is in the
  URL). The ``Metadata`` complex value is a **full replace**: send the complete
  definition you want, not a delta. That includes the complete
  ``decisionTableParameters`` and ``decisionTableSourceCriterias`` arrays;
  omitted/empty source criteria mean none. A PATCH is **atomic** — a rejected
  PATCH leaves the record byte-identical.

An Active (or activating) table's definition cannot be edited in place. This
tool sends one Tooling PATCH and returns the platform's
``FIELD_NOT_UPDATABLE`` error unchanged. Run ``deactivate_decision_table.py``
first when the table must be edited, then reactivate it explicitly afterward.

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

    # edit an ACTIVE table: run deactivate, update, then activate as separate commands
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
    fail_json,
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
    parser.add_argument("--confirm", action="store_true",
                        help="Actually apply. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    try:
        spec = _load_spec(args.spec)
    except (OSError, ValueError) as exc:
        return fail_json(args.json, f"Error: could not read spec '{args.spec}': {exc}")

    result = validate_spec(spec)
    eprint(result.format_report())
    if not result.passed:
        return fail_json(args.json, "Spec has errors; not updating. Fix them and retry.",
                         {"action": "update"})

    dev_name = args.developer_name or spec.get("fullName")
    if not dev_name:
        return fail_json(
            args.json,
            "Error: no DeveloperName — pass --developer-name or set fullName in the spec.")

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    summary = {"action": "update", "path": "tooling", "developerName": dev_name,
               "dryRun": preview}

    try:
        table_row = resolve_decision_table(transport, dev_name)
    except (DecisionTableClientError, ResolveError) as exc:
        return fail_json(args.json, f"Error: {exc}", summary)

    record_id = table_row["Id"]
    summary["id"] = record_id
    eprint(f"\nUpdate DecisionTable '{dev_name}' ({record_id}) via Tooling, "
           f"status={table_row.get('Status')}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    # Tooling Metadata PATCH requires status. Reuse the status returned by the
    # resolve query and let Salesforce enforce lifecycle state and payload validity.
    live_status = table_row.get("Status")
    if not live_status:
        return fail_json(
            args.json,
            f"Error: DecisionTable/{record_id} returned no Status; cannot build the "
            "required Metadata payload.",
            summary,
        )
    body = _payload.tooling_metadata_only(spec, live_status=live_status)
    try:
        transport.tooling_sobject("PATCH", "DecisionTable", record_id, body=body)
    except DecisionTableClientError as exc:
        return fail_json(args.json, str(exc), summary)

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
