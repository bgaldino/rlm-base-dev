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

**Wait mode** (``--wait``) finishes a ``--no-wait`` submit from
``import_expression_set`` / ``set_step_formula`` / ``apply_expression_set_overlay``:
it polls the version (``--version`` takes its apiName or Id) until ``IsActive=true``
or ``--timeout`` seconds pass, then reactivates the procedure-plan versions named
by ``--plans`` (the ids the submit printed). It writes only those plans, needs no
``--confirm``, is safe to repeat, and exits 1 with the state reached on a timeout.

    python scripts/expression_sets/activate_expression_set.py \
        --target-org rlm-base__beta --expression-set RLM_MyClone \
        --version RLM_MyClone_V1 --wait --timeout 600 [--plans <id>,<id>]
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
from scripts.expression_sets._guards import (  # noqa: E402
    MEASURED_1125,
    VERSION_FIELDS,
    null_rank_reactivation_refusal,
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
    state.add_argument("--wait", action="store_true",
                       help="Wait for a submitted activation (see --timeout), then "
                            "reactivate --plans. No --confirm needed.")
    parser.add_argument("--timeout", type=int, default=600,
                        help="--wait: seconds to poll before giving up (default 600).")
    parser.add_argument("--plans", default="",
                        help="--wait: comma-separated ProcedurePlanDefinitionVersion ids "
                             "to reactivate once the version is active.")
    parser.add_argument("--no-cascade", action="store_true",
                        help="Touch only the ES version; skip the procedure-plan cascade.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually change the state. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    if args.wait:
        return _wait(args)
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
                if args.version_api_name in (v.get("ApiName"), v.get("Id"))
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

        no_rank = "Rank" in esv and esv.get("Rank") is None
        if current == desired_active:
            eprint(f"Version already IsActive={desired_active}; nothing to do.")
        elif desired_active and no_rank:
            raise LifecycleError(null_rank_reactivation_refusal(
                esv, True, alternative=None, target_org=args.target_org,
                es_api_name=args.es_api_name))
        elif desired_active:
            # Activate ES version first, then reactivate referencing plans.
            engine.set_version_active(esv["Id"], True)
            engine.wait_for_version_state(esv["Id"], True)
            if cascade:
                plan_versions = _referencing_plan_versions(engine, es_def_id)
                engine.cascade_reactivate_procedure_plans(plan_versions)
        else:
            if no_rank:
                eprint(f"WARNING: {esv.get('ApiName')} has no Rank. The API refuses to "
                       "activate a version without one (\"Enter a valid rank to enable "
                       f"…\", {MEASURED_1125}), so once deactivated it cannot be turned "
                       "back on this way until it has a Rank.")
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


def _wait(args) -> int:
    """``--wait``: poll the submitted version, then reactivate the named plans."""
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=False, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint, max_wait_seconds=args.timeout,
                             poll_interval_seconds=5)
    plans = [p for p in args.plans.split(",") if p.strip()]
    state = None
    try:
        es_id = resolve_expression_set_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version)
        if args.version_api_name:
            found = [v for v in _list_versions(engine, es_id)
                     if args.version_api_name in (v.get("ApiName"), v.get("Id"))]
            if not found:
                eprint(f"Error: version '{args.version_api_name}' not found under "
                       f"'{args.es_api_name}'.")
                return 1
            esv = found[0]
        else:
            esv = resolve_version_by_es_id(
                es_id, target_org=args.target_org, api_version=args.api_version,
                logger=eprint)
        eprint(f"Waiting up to {args.timeout}s for '{args.es_api_name}' version "
               f"{esv.get('ApiName')} to read IsActive=true.")
        try:
            engine.wait_for_version_state(esv["Id"], True)
            state = True
        except LifecycleError:
            state = engine._version_state(esv["Id"])
            eprint(f"State reached: IsActive={state}. Re-run --wait to keep waiting.")
            raise
        if plans:
            engine.cascade_reactivate_procedure_plans(plans)
    except (ExpressionSetClientError, ResolveError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        if args.json:
            print(json.dumps({"action": "wait", "expressionSet": args.es_api_name,
                              "ok": False, "versionIsActive": state}, indent=2))
        return 1
    if args.json:
        print(json.dumps({"action": "wait", "expressionSet": args.es_api_name,
                          "version": esv.get("ApiName"), "versionId": esv.get("Id"),
                          "ok": True, "versionIsActive": True,
                          "plansReactivated": plans}, indent=2))
    return 0


def _list_versions(engine, es_id):
    return engine.t.soql(
        f"SELECT {VERSION_FIELDS} FROM ExpressionSetVersion "
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
