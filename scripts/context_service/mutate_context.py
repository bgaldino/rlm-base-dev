#!/usr/bin/env python3
"""Mutate one Context Definition artifact in place (EXPERIMENTAL).

⚠️  **Experimental / non-build-critical.** The production path for context
changes is a plan applied by ``cci task run manage_context_definition`` (or
``apply_context_plan.py``); this script is a *granular* companion for one-off
edits to an **existing** definition — flip an attribute's ``IsTransient``,
re-designate the default context mapping, or add / remove a single tag. It runs
on the ``sf``-CLI transport — **no access token is ever handled** (``--target-org``
is the *SF CLI* alias, e.g. ``rlm-base__beta``, never the CCI alias). It is
**not** wired into ``cumulusci.yml`` or any flow.

Safety model (see ``_mutate.py``, all live-verified on v67.0):
  * **Op-specific inheritance guard.** ``set-transient`` and ``remove-tag``
    refuse an inherited (standard-base) artifact; ``set-default-mapping`` and
    ``add-tag`` legitimately target inherited mappings/attributes.
  * **Op-specific active-state guard (the add/mutate/delete asymmetry).** Only
    ``remove-tag`` (a delete) is blocked while the version is active and needs
    ``--deactivate-first``; the in-place mutates apply on an active version.
  * **No-op detection.** Setting a value that already holds is reported and
    skipped, not re-PATCHed.
  * **Preview by default.** Without ``--confirm`` every op prints the planned
    change and exits (dry-run) — nothing is mutated.

Ops (mutually exclusive):
  --set-transient NODE.ATTR {true|false}   Flip an attribute's IsTransient.
  --set-default-mapping NAME               Designate the default context mapping.
  --add-tag NODE.ATTR TAGNAME              Add a tag to an attribute (custom __c,
                                           definition-unique name).
  --remove-tag TAGNAME                     Remove a custom tag (delete; blocked
                                           while active — use --deactivate-first).

Examples
--------
    # preview flipping a custom attribute to transient (no mutation)
    python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --set-transient SalesTransactionItem.RampMode__c true

    # actually set it (in place, on the active version)
    python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --set-transient SalesTransactionItem.RampMode__c true --confirm

    # re-designate the default mapping
    python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
        --developer-name RLM_QuoteDocGenContext \
        --set-default-mapping QuoteEntitiesMapping --confirm

    # add a custom tag alias to an attribute
    python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --add-tag SalesTransactionItem.RampMode__c RampModeAlias__c --confirm

    # remove a custom tag (a delete — deactivate first, then reactivate)
    python scripts/context_service/mutate_context.py --target-org rlm-base__beta \
        --developer-name RLM_SalesTransactionContext \
        --remove-tag RampModeAlias__c --deactivate-first --reactivate --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _apply import Transport  # noqa: E402
from _client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from _mutate import ContextMutator, MutatePreflightError  # noqa: E402


def _clean(summary):
    """Drop internal (``_``-prefixed) keys before emitting."""
    if isinstance(summary, dict):
        return {k: v for k, v in summary.items() if not k.startswith("_")}
    return summary


def _as_bool(text: str) -> bool:
    v = str(text).strip().lower()
    if v in ("true", "1", "yes", "y"):
        return True
    if v in ("false", "0", "no", "n"):
        return False
    raise argparse.ArgumentTypeError(f"expected true/false, got '{text}'")


def _describe_plan(change):
    """Human-readable one-liner for a planned single change."""
    op = change["op"]
    if op == "set-transient":
        return (f"set-transient {change['target']}: {change['from']} -> {change['to']}"
                + ("  (no-op)" if change["noop"] else ""))
    if op == "set-default-mapping":
        prev = change["from_default"]
        return (f"set-default-mapping -> {change['target']}"
                + (f"  (was: {prev})" if prev and prev != change['target'] else "")
                + ("  (no-op, already default)" if change["noop"] else ""))
    if op == "add-tag":
        return (f"add-tag '{change['tag']}' -> {change['target']}"
                + ("  (no-op, already present)" if change["noop"] else ""))
    return op


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Mutate one Context Definition artifact in place (EXPERIMENTAL).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name", help="DeveloperName of the definition.")
    ident.add_argument("--context-definition-id", help="ContextDefinitionId.")

    op = parser.add_mutually_exclusive_group(required=True)
    op.add_argument("--set-transient", nargs=2, metavar=("NODE.ATTR", "BOOL"),
                    help="Flip an attribute's IsTransient (true|false).")
    op.add_argument("--set-default-mapping", metavar="NAME",
                    help="Designate NAME as the default context mapping.")
    op.add_argument("--add-tag", nargs=2, metavar=("NODE.ATTR", "TAGNAME"),
                    help="Add a tag to an attribute (custom __c, definition-unique).")
    op.add_argument("--remove-tag", metavar="TAGNAME",
                    help="Remove a custom tag (a delete; blocked while active).")

    parser.add_argument("--deactivate-first", action="store_true",
                        help="Deactivate before the op (required for --remove-tag on an "
                             "active definition; harmless for in-place mutates).")
    parser.add_argument("--reactivate", action="store_true",
                        help="Reactivate the definition after the op (pairs with "
                             "--deactivate-first).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually perform the mutation. Without it, the op only "
                             "PREVIEWS the planned change (no mutation).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the result summary as JSON.")
    args = parser.parse_args(argv)

    eprint("⚠️  EXPERIMENTAL: mutate_context.py is not build-critical. The production "
           "path for context changes is a plan via manage_context_definition; this "
           "makes one granular in-place edit.")

    # Resolve the op name for the guards.
    if args.set_transient:
        op_name = "set-transient"
    elif args.set_default_mapping:
        op_name = "set-default-mapping"
    elif args.add_tag:
        op_name = "add-tag"
    else:
        op_name = "remove-tag"

    preview = not args.confirm
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    mut = ContextMutator(transport, logger=eprint)

    try:
        context_id = args.context_definition_id
        if not context_id:
            context_id = mut.resolve_definition_id(args.developer_name)
            if not context_id:
                eprint(f"Error: no context definition found with developerName "
                       f"'{args.developer_name}' in org '{args.target_org}'.")
                return 1
        detail = mut.fetch_detail(context_id)
        active = mut.is_active(detail)
        eprint(f"Definition {context_id} — active={active}, op={op_name}")

        # ---- plan (pure; also runs the inheritance guard) ---------------- #
        remove_plan = None
        if op_name == "set-transient":
            node_attr, val = args.set_transient
            change = mut.plan_set_transient(detail, node_attr, _as_bool(val))
            eprint("\nPlanned change:\n  " + _describe_plan(change))
        elif op_name == "set-default-mapping":
            change = mut.plan_set_default_mapping(detail, args.set_default_mapping)
            eprint("\nPlanned change:\n  " + _describe_plan(change))
        elif op_name == "add-tag":
            node_attr, tag = args.add_tag
            change = mut.plan_add_tag(detail, node_attr, tag)
            eprint("\nPlanned change:\n  " + _describe_plan(change))
            eprint("  note: " + change["_note"])
        else:  # remove-tag
            remove_plan = mut.plan_remove_tag(detail, context_id, args.remove_tag)
            eprint(f"\nPlanned change:\n  remove-tag '{args.remove_tag}' "
                   f"({len(remove_plan)} artifact(s), child→parent):")
            for art in remove_plan:
                eprint(f"    - {art['kind']:12s} {art['name']}  (id={art['id']})")

        # ---- preview stops here ------------------------------------------ #
        if preview:
            hint = ""
            if op_name == "remove-tag" and active:
                hint = " (and --deactivate-first, since a tag delete is blocked while active)"
            eprint(f"\n[preview] No mutation performed. Re-run with --confirm{hint}.")
            return 0

        # ---- active-state guard (op-specific) ---------------------------- #
        detail = mut.guard_active_state(
            op_name, detail, context_id=context_id,
            auto_deactivate=args.deactivate_first)
        # Belt-and-suspenders: honor --deactivate-first for in-place ops too.
        deactivated = False
        if args.deactivate_first and mut.is_active(detail):
            mut.deactivate(context_id)
            deactivated = True
            if not mut.dry_run:
                detail = mut.fetch_detail(context_id)

        # ---- execute ----------------------------------------------------- #
        if op_name == "set-transient":
            summary = mut.execute_set_transient(change)
        elif op_name == "set-default-mapping":
            summary = mut.execute_set_default_mapping(context_id, detail, change)
        elif op_name == "add-tag":
            summary = mut.execute_add_tag(context_id, change)
        else:  # remove-tag
            summary = mut.execute_remove_tag(remove_plan)

        # ---- optional reactivate ----------------------------------------- #
        if args.reactivate and (deactivated or args.deactivate_first):
            mut.activate(context_id)
            summary["reactivated"] = True

        summary["context_id"] = context_id
        eprint(f"\nDone. {json.dumps(_clean(summary))}")
        if args.json:
            print(json.dumps(_clean(summary), indent=2))
        return 0

    except MutatePreflightError as exc:
        eprint(f"\nRefused: {exc}")
        return 1
    except ContextClientError as exc:
        eprint(f"\nFAILED: {exc}")
        return 1
    except (ValueError, argparse.ArgumentTypeError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
