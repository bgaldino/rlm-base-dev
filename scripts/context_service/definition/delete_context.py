#!/usr/bin/env python3
"""Delete Context Definition artifacts from an org (DESTRUCTIVE — HARD DELETE).

⚠️  **DESTRUCTIVE.** There is no org-build CCI "delete-a-context" task; the
supported lifecycle verb is *deactivation* (soft-disable), which this script
does by default. A hard delete is **strictly opt-in** via ``--confirm-delete``
and cannot be undone. Live-proven, for one-off teardown. This standalone script
runs on the ``sf``-CLI transport — **no access token is ever handled or passed**
(``--target-org`` is the *SF CLI* alias, e.g. ``rlm-base__beta``, never the CCI
alias ``beta``). It is **not** wired into ``cumulusci.yml`` or any flow.

Safety model (see ``_delete.py``):
  * **Prefer deactivate.** With no ``--confirm-delete`` the script deactivates
    the definition and stops — the reversible, recommended teardown.
  * **Reverse-order teardown.** Granular deletes run child→parent using the
    by-id resources; the whole-definition delete is one DELETE (platform cascade).
  * **``baseReference`` guard.** Inherited (standard-base) artifacts cannot be
    deleted — the script refuses them up front with an actionable message
    instead of surfacing the opaque platform error.
  * **Active-state guard (live-verified).** The platform blocks *every* delete
    while the version is active. The script refuses up front and points you to
    ``--deactivate-first`` (deactivate, then delete in one run).

Modes (mutually exclusive):
  --deactivate-only          Soft-disable the definition; delete nothing (DEFAULT
                             when no delete flag is given).
  --custom-teardown          Delete every custom (__c) artifact, leaving the
                             inherited base intact (inverse of an additive apply).
  --delete-artifact K NAME   Delete one artifact (K = node|attribute|tag|mapping|
                             node-mapping|attr-mapping); add --cascade for its
                             custom dependents.
  --delete-definition        Delete the WHOLE definition (platform cascade).

Preview first: without ``--confirm-delete`` every delete mode prints the ordered
teardown plan and exits (a dry-run preview) — nothing is mutated.

Examples
--------
    # safe default: just deactivate (reversible)
    python scripts/context_service/delete_context.py --target-org rlm-base__beta \
        --developer-name RLM_QuoteDocGenContext

    # preview what a custom teardown would remove (no mutation)
    python scripts/context_service/delete_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --custom-teardown

    # actually strip custom artifacts (deactivating first if needed)
    python scripts/context_service/delete_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext --custom-teardown \
        --deactivate-first --confirm-delete

    # delete one custom attribute + its tag/attr-mapping
    python scripts/context_service/delete_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --delete-artifact attribute SalesTransactionItem.RampMode__c \
        --cascade --deactivate-first --confirm-delete

    # nuke a create-new definition entirely
    python scripts/context_service/delete_context.py --target-org rlm-base__beta \
        --developer-name RLM_QuoteDocGenContext --delete-definition --confirm-delete
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._delete import (  # noqa: E402
    ContextDeleter,
    DeletePreflightError,
    build_artifact_catalog,
    partition_by_inheritance,
)


def _print_plan(ordered, header):
    eprint(f"\n{header} ({len(ordered)} artifact(s), child→parent order):")
    if not ordered:
        eprint("  (nothing to delete)")
        return
    for art in ordered:
        eprint(f"  - {art['kind']:14s} {art['name']}  (id={art['id']})")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete / deactivate a Context Definition (DESTRUCTIVE).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--developer-name", help="DeveloperName of the definition.")
    group.add_argument("--context-definition-id", help="ContextDefinitionId.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--deactivate-only", action="store_true",
                      help="Soft-disable the definition; delete nothing (default).")
    mode.add_argument("--custom-teardown", action="store_true",
                      help="Delete every custom (__c) artifact; keep the inherited base.")
    mode.add_argument("--delete-artifact", nargs=2, metavar=("KIND", "NAME"),
                      help="Delete one artifact: KIND in "
                           "{node,attribute,tag,mapping,node-mapping,attr-mapping}, "
                           "NAME its (qualified) name.")
    mode.add_argument("--delete-definition", action="store_true",
                      help="Delete the WHOLE definition (platform cascade).")

    parser.add_argument("--cascade", action="store_true",
                        help="With --delete-artifact, also delete the target's custom dependents.")
    parser.add_argument("--deactivate-first", action="store_true",
                        help="Deactivate the definition before deleting (deletes are "
                             "blocked while active). Otherwise an active definition is refused.")
    parser.add_argument("--confirm-delete", action="store_true",
                        help="Actually perform the hard delete. Without it, delete modes "
                             "only PREVIEW the teardown plan (no mutation).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the result summary as JSON.")
    args = parser.parse_args(argv)

    eprint("⚠️  delete_context.py performs DESTRUCTIVE hard deletes. The supported "
           "teardown is deactivation; a hard delete requires --confirm-delete and "
           "cannot be undone.")

    # A delete mode without --confirm-delete is a preview; drive the transport in
    # dry_run so even the (guarded) deactivate/delete calls are logged, not run.
    is_delete_mode = bool(args.custom_teardown or args.delete_artifact or args.delete_definition)
    preview = is_delete_mode and not args.confirm_delete
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    deleter = ContextDeleter(transport, logger=eprint)

    try:
        context_id = args.context_definition_id
        if not context_id:
            context_id = deleter.resolve_definition_id(args.developer_name)
            if not context_id:
                eprint(f"Error: no context definition found with developerName "
                       f"'{args.developer_name}' in org '{args.target_org}'.")
                return 1
        detail = deleter.fetch_detail(context_id)
        active = deleter.is_active(detail)
        eprint(f"Definition {context_id} — active={active}")

        # ---- default / explicit deactivate-only ------------------------- #
        if not is_delete_mode:
            if not active:
                eprint("Already inactive; nothing to do (no delete flag given).")
                summary = {"context_id": context_id, "action": "none", "active": False}
            else:
                deleter.deactivate(context_id)
                eprint("Deactivated (reversible). Re-run with a delete mode + "
                       "--confirm-delete to hard-delete.")
                summary = {"context_id": context_id, "action": "deactivated"}
            return _emit(summary, args)

        # ---- build the delete plan -------------------------------------- #
        catalog = build_artifact_catalog(detail, context_id)

        if args.delete_definition:
            custom, inherited = partition_by_inheritance(catalog)
            eprint(f"Whole-definition delete: {len(catalog)} artifact(s) "
                   f"({len(custom)} custom / {len(inherited)} inherited) will be "
                   f"removed by platform cascade.")
            if inherited:
                eprint("  Note: this definition extends a standard base; deleting "
                       "the whole definition removes YOUR extension, not the base.")
            ordered = None  # single cascade delete, not a per-artifact list
        elif args.custom_teardown:
            ordered = deleter.plan_custom_teardown(catalog)
            _print_plan(ordered, "Custom teardown plan")
        else:  # --delete-artifact
            kind, name = args.delete_artifact
            ordered = deleter.plan_target_deletion(
                catalog, kind=kind, name=name, cascade=args.cascade)
            _print_plan(ordered, f"Delete plan for {kind} '{name}'")

        # ---- preview stops here ----------------------------------------- #
        if preview:
            eprint("\n[preview] No mutation performed. Re-run with --confirm-delete "
                   "to execute" + (" (and --deactivate-first if active)." if active else "."))
            return 0

        # ---- active-state guard (live-verified block) ------------------- #
        detail = deleter.guard_active_state(
            detail, context_id=context_id, auto_deactivate=args.deactivate_first)

        # ---- execute ---------------------------------------------------- #
        if args.delete_definition:
            summary = deleter.delete_definition(context_id)
        else:
            summary = deleter.execute(ordered)
            summary["context_id"] = context_id
        eprint(f"\nDone. {json.dumps(summary)}")
        return _emit(summary, args)

    except DeletePreflightError as exc:
        eprint(f"\nRefused: {exc}")
        return 1
    except ContextClientError as exc:
        eprint(f"\nFAILED: {exc}")
        return 1
    except ValueError as exc:
        eprint(f"\nFAILED: {exc}")
        return 2


def _emit(summary, args) -> int:
    if args.json:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
