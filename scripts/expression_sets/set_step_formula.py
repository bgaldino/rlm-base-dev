#!/usr/bin/env python3
"""Set one step's formula on ONE version of a BRE Expression Set (MUTATING).

``import_expression_set.py`` replaces a whole set with one full-graph Connect
PATCH, and on a set with several versions (a platform version chain) that PATCH
cannot target the right version: it is rejected on a version-name collision,
after partially applying. This tool edits a single version instead, through the
version-scoped Tooling ``ExpressionSetDefinitionVersion.Metadata`` PATCH (the
same mechanism ``relabel_expression_set.py`` uses for labels). The formula lives
at::

    Metadata.steps[N].customElement.parameters[name == "formula-section-<S>-input"].value

**Which version.** By default the **executing** version (``_guards.executing_version``):
among the ACTIVE versions whose date window covers now, the highest ``Rank`` (264
object reference); among null Ranks, the earliest created (measured on 264). The
tool notes when the version that runs is not the highest-numbered one. Several versions can
be active at once and only one runs, so editing any other changes no price (todo
pack 175: a constant written into ``_V1`` of a four-version chain changed nothing;
written into the version that ran it changed every price). ``--version-api-name``
targets another version explicitly, with a warning when it is not the executing one.

**Which step.** ``--step NAME``, or ``--parent-step NAME`` to pick the one child
of that parent that carries the formula parameter. The parent is version-stable
where the child's name is not (``Uplift`` in one version, ``CompoundUplift`` in
another).

**Lifecycle.** The PATCH runs inside ``LifecycleEngine.run_mutation``: the
version and its referencing procedure-plan versions are deactivated, the
Metadata is PATCHed, and both are reactivated (a PATCH on an active version is
rejected with ``INVALID_ID_FIELD: LatestVersionSnapshotId not found``). A Tooling
sObject update is atomic, so a failed PATCH leaves the stored Metadata unchanged
and the version is reactivated even on failure (``reactivate_on_failure=True``):
a failed edit must not take a live procedure offline. An inactive target version
stays inactive.

**Checks.** ``ProcedurePlanDefinitionVersion.IsActive`` is read before and after
the run (an inactive plan is silently skipped at pricing time — todo pack 170),
and the formula is read back after the run; a mismatch, or a plan the run left
inactive, exits 1.

**Preview by default.** Without ``--confirm`` it resolves the version and step,
prints the change and the lifecycle it would run, and writes nothing.
``--show`` only prints the current formula.

Quick Rule 8 — try it on a disposable clone first; edit a shipped procedure only
as an intentional, approved change. ``--target-org`` is the *SF CLI* alias, never
the CCI alias. Pinned to Release 264 / v68.0.

Usage
-----
    # read the formula the executing version runs
    python scripts/expression_sets/set_step_formula.py --target-org rlm-base__beta \\
        --expression-set RLM_DefaultPricingProcedure \\
        --parent-step Applyupliftstorampedsubscriptionsitemsduringamendment --show

    # preview, then apply, a new formula
    python scripts/expression_sets/set_step_formula.py --target-org rlm-base__beta \\
        --expression-set RLM_MyClone --step Calculatetotalcostandmargin \\
        --formula 'ItemUnitCost__std * LineItemQuantity' [--confirm]
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    Transport,
    eprint,
    soql_literal,
)
from scripts.expression_sets._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.expression_sets._guards import (  # noqa: E402
    executing_version,
    null_rank_reactivation_refusal,
    rank_order_warning,
)
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    list_versions,
    resolve_definition_id,
    resolve_expression_set_id,
)
from scripts.expression_sets._tooling import (  # noqa: E402
    ToolingError,
    fetch_metadata,
    patch_metadata,
    resolve_esdv,
)


class StepFormulaError(RuntimeError):
    """Raised when the version, step or formula parameter cannot be resolved."""


def formula_parameter_name(section: int) -> str:
    """The customElement parameter that holds formula section ``section``."""
    return f"formula-section-{int(section)}-input"


# ----------------------------------------------------------------------
# Pure helpers (no org; unit-tested)
# ----------------------------------------------------------------------


def select_target_version(
    versions: List[Dict[str, Any]], version_api_name: Optional[str] = None
) -> Dict[str, Any]:
    """The version to edit: the one named, else the executing one.

    Raises :class:`StepFormulaError` when the named version does not exist, or
    when no name is given and no version is active (there is no executing version
    to default to, so the caller must name one). Pure.
    """
    if version_api_name:
        match = [v for v in versions if v.get("ApiName") == version_api_name]
        if not match:
            names = ", ".join(sorted(str(v.get("ApiName")) for v in versions))
            raise StepFormulaError(
                f"Version '{version_api_name}' not found. Versions: {names or '(none)'}."
            )
        return match[0]
    running = executing_version(versions)
    if running is None:
        raise StepFormulaError(
            "No active version of this expression set has a date window covering "
            "now, so there is no executing version to default to. Name one with "
            "--version-api-name."
        )
    return running


def version_table(versions: List[Dict[str, Any]], target: Dict[str, Any]) -> List[str]:
    """One line per version, lowest number first, marking the target and the
    executing version. Pure."""
    running = executing_version(versions)
    lines = []
    for v in sorted(versions, key=lambda r: r.get("VersionNumber") or 0):
        marks = []
        if running is not None and v.get("Id") == running.get("Id"):
            marks.append("executes")
        if v.get("Id") == target.get("Id"):
            marks.append("target")
        rank = v.get("Rank")
        lines.append(
            f"  v{v.get('VersionNumber')}  {'active  ' if v.get('IsActive') else 'inactive'}"
            f"  rank {rank if rank is not None else '-'}"
            f"  {v.get('ApiName')}{'  <- ' + ', '.join(marks) if marks else ''}"
        )
    return lines


def iter_steps(node: Any, path: str = "Metadata"):
    """Yield ``(path, step)`` for every step dict anywhere under ``node``.

    A step is any dict inside a list held by a ``steps`` key. The Tooling
    ``Metadata`` keeps steps flat today, but the walk is recursive so a nested
    shape is found too. Pure.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if key == "steps" and isinstance(value, list):
                for i, step in enumerate(value):
                    if isinstance(step, dict):
                        yield f"{child}[{i}]", step
                        yield from iter_steps(step, f"{child}[{i}]")
            else:
                yield from iter_steps(value, child)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from iter_steps(item, f"{path}[{i}]")


def formula_parameter(step: Dict[str, Any], param_name: str) -> Optional[Dict[str, Any]]:
    """The step's ``customElement.parameters`` entry named ``param_name``. Pure."""
    element = step.get("customElement")
    if not isinstance(element, dict):
        return None
    for param in element.get("parameters") or []:
        if isinstance(param, dict) and param.get("name") == param_name:
            return param
    return None


def locate_step(
    metadata: Dict[str, Any],
    *,
    step: Optional[str] = None,
    parent_step: Optional[str] = None,
    param_name: str = formula_parameter_name(0),
) -> Tuple[str, Dict[str, Any]]:
    """Find the one step to edit; return ``(path, step)``.

    ``step`` matches by name. ``parent_step`` matches the children of that
    parent that carry ``param_name`` (a ListGroup's filter child has none).
    Exactly one match is required; anything else raises
    :class:`StepFormulaError` naming what was found. The returned step must
    carry ``param_name``. Pure.
    """
    if bool(step) == bool(parent_step):
        raise StepFormulaError("Give exactly one of --step or --parent-step.")
    steps = list(iter_steps(metadata))
    if step:
        matches = [(p, s) for p, s in steps if s.get("name") == step]
        what = f"named '{step}'"
    else:
        children = [(p, s) for p, s in steps if s.get("parentStep") == parent_step]
        matches = [(p, s) for p, s in children if formula_parameter(s, param_name)]
        what = f"under parent '{parent_step}' carrying '{param_name}'"
        if not matches:
            names = ", ".join(str(s.get("name")) for _, s in children) or "(none)"
            raise StepFormulaError(
                f"No step {what}. Children of '{parent_step}': {names}."
            )
    if not matches:
        raise StepFormulaError(f"No step {what} in this version.")
    if len(matches) > 1:
        found = ", ".join(f"{s.get('name')} at {p}" for p, s in matches)
        raise StepFormulaError(f"{len(matches)} steps {what}: {found}. Use --step.")
    path, found_step = matches[0]
    if formula_parameter(found_step, param_name) is None:
        params = ", ".join(
            str(p.get("name"))
            for p in (found_step.get("customElement") or {}).get("parameters") or []
            if isinstance(p, dict)
        ) or "(none)"
        raise StepFormulaError(
            f"Step '{found_step.get('name')}' has no '{param_name}' parameter "
            f"(parameters: {params})."
        )
    return path, found_step


def with_formula(
    metadata: Dict[str, Any], step_name: str, param_name: str, formula: str
) -> Dict[str, Any]:
    """A copy of ``metadata`` with ``step_name``'s ``param_name`` set to
    ``formula``. The input is not mutated. Raises :class:`StepFormulaError`
    when the step or parameter is gone. Pure."""
    result = deepcopy(metadata)
    _, step = locate_step(result, step=step_name, param_name=param_name)
    formula_parameter(step, param_name)["value"] = formula
    return result


def current_formula(metadata: Dict[str, Any], step_name: str, param_name: str) -> Optional[str]:
    """The formula ``step_name`` currently carries. Pure."""
    _, step = locate_step(metadata, step=step_name, param_name=param_name)
    return formula_parameter(step, param_name).get("value")


def plans_left_inactive(before: Dict[str, bool], after: Dict[str, Optional[bool]]) -> List[str]:
    """Plan versions active before the run that are not confirmed active after it
    (inactive, or unreadable). Pure."""
    return sorted(vid for vid, was in before.items() if was and after.get(vid) is not True)


# ----------------------------------------------------------------------
# Org reads
# ----------------------------------------------------------------------


def read_plan_states(engine: LifecycleEngine, es_def_id: str) -> Dict[str, Optional[bool]]:
    """``{ProcedurePlanDefinitionVersion Id: IsActive}`` for every plan version
    that references the expression set; ``None`` when a row can't be read."""
    ids = sorted({
        (opt.get("ProcedurePlanSection") or {}).get("ProcedurePlanVersionId")
        for opt in engine.find_referencing_procedure_plans(es_def_id)
    } - {None})
    states: Dict[str, Optional[bool]] = {}
    for vid in ids:
        rows = engine.t.soql(
            "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
            f"WHERE Id = '{soql_literal(vid)}'"
        )
        states[vid] = bool(rows[0].get("IsActive")) if rows else None
    return states


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Set one step's formula on one version of a BRE Expression Set "
                    "via the Tooling Metadata PATCH. MUTATING (preview by default; "
                    "--confirm to apply; --show to read only).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    parser.add_argument("--expression-set", dest="es_api_name", required=True,
                        help="ExpressionSetDefinition DeveloperName.")
    parser.add_argument("--version-api-name",
                        help="Edit this ExpressionSetVersion ApiName instead of the "
                             "executing version (highest Rank among active versions "
                             "in their date window).")
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--step", help="The step's name (spaceless API name).")
    which.add_argument("--parent-step",
                       help="Pick the one child of this parent step that carries the "
                            "formula parameter (stable across versions that rename it).")
    parser.add_argument("--section", type=int, default=0,
                        help="Formula section to set (parameter formula-section-<N>-input; "
                             "default 0).")
    parser.add_argument("--formula", help="The new formula text. Required unless --show.")
    parser.add_argument("--show", action="store_true",
                        help="Print the current formula and exit (read-only).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually write the formula. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    if args.show and (args.formula is not None or args.confirm):
        eprint("Error: --show is read-only; drop --formula and --confirm.")
        return 2
    if not args.show and args.formula is None:
        eprint("Error: --formula is required (or use --show to read).")
        return 2
    if args.section < 0:
        eprint("Error: --section must be 0 or more.")
        return 2

    param_name = formula_parameter_name(args.section)
    preview = not args.confirm
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)
    result: Dict[str, Any] = {"action": "set_step_formula", "expressionSet": args.es_api_name,
                              "parameter": param_name, "dryRun": preview}

    try:
        es_id = resolve_expression_set_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version)
        es_def_id = resolve_definition_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version)
        versions = list_versions(es_id, target_org=args.target_org,
                                 api_version=args.api_version)
        esv = select_target_version(versions, args.version_api_name)
        running = executing_version(versions)
        eprint(f"Versions of '{args.es_api_name}':")
        for line in version_table(versions, esv):
            eprint(line)
        rank_warning = rank_order_warning(versions)
        if rank_warning:
            eprint(f"WARNING: {rank_warning}")
        if running is None or running.get("Id") != esv.get("Id"):
            eprint(f"WARNING: {esv.get('ApiName')} is not the executing version; a "
                   "change to it does not affect pricing until it executes.")

        esdv = resolve_esdv(transport, es_def_id=es_def_id,
                            version_number=esv.get("VersionNumber"),
                            version_api_name=esv.get("ApiName"))
        esdv_id = esdv["Id"]
        metadata = fetch_metadata(transport, esdv_id)
        path, step = locate_step(metadata, step=args.step, parent_step=args.parent_step,
                                 param_name=param_name)
        step_name = step.get("name")
        live = formula_parameter(step, param_name).get("value")
        eprint(f"esdv={esdv_id}  version={esv.get('ApiName')} v{esv.get('VersionNumber')}  "
               f"step={step_name} at {path}  {param_name}:")
        eprint(f"  current: {live!r}")
        result.update({"version": esv.get("ApiName"), "versionNumber": esv.get("VersionNumber"),
                       "executing": running is not None and running.get("Id") == esv.get("Id"),
                       "esdvId": esdv_id, "step": step_name, "path": path, "current": live})

        if args.show:
            if args.json:
                print(json.dumps(result, indent=2))
            return 0
        result["formula"] = args.formula
        eprint(f"  new:     {args.formula!r}")
        if live == args.formula:
            eprint("The formula already matches; nothing to write.")
            result["changed"] = False
            if args.json:
                print(json.dumps(result, indent=2))
            return 0

        plans_before = read_plan_states(engine, es_def_id)
        inactive_before = sorted(v for v, s in plans_before.items() if s is not True)
        if inactive_before:
            eprint(f"WARNING: referencing procedure-plan version(s) already inactive or "
                   f"unreadable before this run: {', '.join(inactive_before)}. An inactive "
                   "plan is skipped at pricing time; this run leaves them as found.")
        was_active = bool(esv.get("IsActive"))
        # Before any write, with the remedy commands filled for this org and set
        # (the lifecycle's own check would refuse too). No run-without-activation
        # option here: an active target is always reactivated.
        refusal = null_rank_reactivation_refusal(esv, was_active,
                                                 target_org=args.target_org,
                                                 es_api_name=args.es_api_name)
        if refusal:
            raise LifecycleError(refusal)

        def mutate():
            # Re-read inside the inactive window, so the PATCH carries the
            # Metadata as stored now rather than as read before deactivation.
            fresh = fetch_metadata(transport, esdv_id)
            patch_metadata(transport, esdv_id,
                           with_formula(fresh, step_name, param_name, args.formula))
            engine.log(f"PATCHed Tooling Metadata for {esdv_id} ({step_name} {param_name}).")

        engine.run_mutation(
            es_def_id=es_def_id, esv=esv, mutate=mutate,
            # Reactivate only a version that was active: an inactive target stays off.
            activate_after=was_active, cascade=True, verb="Set formula",
            # A Tooling sObject PATCH is atomic: a failure leaves the stored
            # Metadata unchanged, so restoring the version is safe and keeps the
            # procedure online.
            reactivate_on_failure=True,
        )
    except (ExpressionSetClientError, ResolveError, LifecycleError, ToolingError,
            StepFormulaError, ValueError) as exc:  # ValueError: an unreadable version date
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
        result["changed"] = False
        if args.json:
            print(json.dumps(result, indent=2))
        return 0

    # Read-back: the live formula and the activation state, after the lifecycle.
    failures: List[str] = []
    try:
        stored = current_formula(fetch_metadata(transport, esdv_id), step_name, param_name)
        version_rows = transport.soql(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE Id = '{soql_literal(esv['Id'])}'")
        version_active = bool(version_rows[0].get("IsActive")) if version_rows else None
        plans_after = read_plan_states(engine, es_def_id)
    except (ExpressionSetClientError, ToolingError, StepFormulaError) as exc:
        eprint(f"\nFAILED: the formula was written, but reading it back failed: {exc}")
        return 1
    result.update({"stored": stored, "versionActive": version_active,
                   "plansAfter": plans_after})
    if stored != args.formula:
        failures.append(f"live formula is {stored!r}, not the intended {args.formula!r}")
    if version_active is not was_active:
        failures.append(f"ExpressionSetVersion {esv['Id']} reads IsActive={version_active}; "
                        f"it was {was_active} before the run")
    left_off = plans_left_inactive(plans_before, plans_after)
    if left_off:
        failures.append("procedure-plan version(s) active before the run are not active now: "
                        + ", ".join(left_off))
        for vid in left_off:
            eprint(f"  restore: sf data update record --target-org {args.target_org} "
                   f"--sobject ProcedurePlanDefinitionVersion --record-id {vid} "
                   "--values \"IsActive=true\"")
    result["changed"] = True
    result["ok"] = not failures
    if failures:
        eprint("\nFAILED read-back: " + "; ".join(failures))
    else:
        eprint(f"\nlive == intended: True. {step_name} on {esv.get('ApiName')} now carries "
               "the new formula; version and plan activation are as before the run.")
    if args.json:
        print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
