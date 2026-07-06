#!/usr/bin/env python3
"""Activate or deactivate a BRE Expression Set version (MUTATING).

Standalone activation control: flip an ``ExpressionSetVersion.IsActive`` on or
off, with the referencing ``ProcedurePlanDefinitionVersion`` cascade (a live
procedure plan cannot point at a deactivated expression set). Use this to
re-enable a version left DEACTIVATED by a failed ``apply_expression_set_overlay`` /
``import_expression_set`` (after inspecting/restoring it), or to take a version
offline for maintenance.

On **--deactivate**: cascade-deactivate referencing procedure-plan versions
first, then the ES version. On **--activate**: activate the ES version first,
then reactivate the procedure-plan versions this org previously had active — but
because a standalone activate does not know which plans were deactivated, the
cascade on activate is best-effort over the plans *currently* referencing the
set; pass ``--no-cascade`` to touch only the ES version.

**Preview by default.** Without ``--confirm`` the tool logs the planned state
change and performs no write. Re-run with ``--confirm`` to apply.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to
Release 262 / v67.0.

Usage
-----
    # deactivate (preview, then confirm)
    python scripts/expression_sets/activate_expression_set.py \
        --target-org rlm-base__beta \
        --expression-set RLM_MyClone --deactivate
    python scripts/expression_sets/activate_expression_set.py \
        --target-org rlm-base__beta \
        --expression-set RLM_MyClone --deactivate --confirm

    # reactivate a version left off by a failed apply
    python scripts/expression_sets/activate_expression_set.py \
        --target-org rlm-base__beta \
        --expression-set RLM_MyClone --activate --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    Transport,
    eprint,
    soql_literal,
)
from scripts.expression_sets._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_definition_id,
    resolve_expression_set_id,
    resolve_version_by_es_id,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Activate/deactivate a BRE Expression Set version (+ procedure-plan "
                    "cascade). MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--expression-set", dest="es_api_name", required=True,
                        help="ExpressionSetDefinition DeveloperName.")
    parser.add_argument("--version", dest="version_api_name",
                        help="Target a specific version apiName (default: active/latest).")
    state = parser.add_mutually_exclusive_group(required=True)
    state.add_argument("--activate", action="store_true", help="Set IsActive=true.")
    state.add_argument("--deactivate", action="store_true", help="Set IsActive=false.")
    parser.add_argument("--no-cascade", action="store_true",
                        help="Touch only the ES version; skip the procedure-plan cascade.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually change the state. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    desired_active = bool(args.activate)
    preview = not args.confirm
    cascade = not args.no_cascade
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        es_id = resolve_expression_set_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        es_def_id = resolve_definition_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        if args.version_api_name:
            versions = [
                v for v in _list_versions(engine, es_id)
                if v.get("ApiName") == args.version_api_name
            ]
            if not versions:
                eprint(f"Error: version '{args.version_api_name}' not found under "
                       f"'{args.es_api_name}'.")
                return 1
            esv = versions[0]
        else:
            esv = resolve_version_by_es_id(
                es_id, target_org=args.target_org, api_version=args.api_version, logger=eprint
            )

        current = bool(esv.get("IsActive"))
        eprint(f"{'Activate' if desired_active else 'Deactivate'} '{args.es_api_name}' "
               f"version {esv.get('ApiName')} (currently IsActive={current}), "
               f"cascade={cascade}, {'PREVIEW' if preview else 'CONFIRM'}")

        if current == desired_active:
            eprint(f"Version already IsActive={desired_active}; nothing to do.")
        elif desired_active:
            # Activate ES version first, then reactivate referencing plans.
            engine.set_version_active(esv["Id"], True)
            engine.wait_for_version_state(esv["Id"], True)
            if cascade:
                plan_versions = _referencing_plan_versions(engine, es_def_id)
                engine.cascade_reactivate_procedure_plans(plan_versions)
        else:
            # Deactivate referencing plans first, then the ES version.
            if cascade:
                engine.cascade_deactivate_procedure_plans(es_def_id)
            engine.set_version_active(esv["Id"], False)
            engine.wait_for_version_state(esv["Id"], False)

    except (ExpressionSetClientError, ResolveError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({
            "action": "activate" if desired_active else "deactivate",
            "expressionSet": args.es_api_name, "expressionSetId": es_id,
            "version": esv.get("ApiName"), "versionId": esv.get("Id"),
            "dryRun": preview,
        }, indent=2))
    return 0


def _list_versions(engine, es_id):
    return engine.t.soql(
        "SELECT Id, ApiName, IsActive, VersionNumber FROM ExpressionSetVersion "
        f"WHERE ExpressionSetId = '{soql_literal(es_id)}' "
        "ORDER BY IsActive DESC, VersionNumber DESC"
    )


def _referencing_plan_versions(engine, es_def_id):
    """Distinct ProcedurePlanDefinitionVersion ids referencing this ES definition."""
    options = engine.find_referencing_procedure_plans(es_def_id)
    ids = set()
    for opt in options:
        section = opt.get("ProcedurePlanSection") or {}
        vid = section.get("ProcedurePlanVersionId")
        if vid:
            ids.add(vid)
    return sorted(ids)


if __name__ == "__main__":
    raise SystemExit(main())
