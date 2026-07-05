#!/usr/bin/env python3
"""Trace the variable producer→consumer graph of a BRE Expression Set (read-only).

The flagship inspector. It answers the two hardest questions the expression-sets
skill turns on:

* **Safe step removal** — *"if I delete this step, what breaks?"* A step is safe
  to remove only if nothing downstream consumes what it produces. ``--variable X``
  shows who **produces** X (``>``) and who **consumes** it (``<`` / ``?`` / ``~``);
  ``--step X`` shows a step's full dependency closure.
* **Capture dependencies (three scopes)** — *"to move this step to another org,
  what must I ship?"* Every referenced name is classified into:
    - **version**  — a version ``variables[]`` entry → ship in the overlay's
      ``addVariables``.
    - **custom**   — a ``__c`` / ``__r`` custom field/node → the target org must
      already define it; declare in ``externalDependencies`` (the overlay CANNOT
      create it).
    - **standard** — context-supplied → declare nothing.

Validation is **structural, not functional**: the overlay validator confirms a
step is well-formed, NOT that its inputs are actually produced upstream or
supplied by the bound context. ``--orphans`` operationalizes that warning —
consumed-with-no-producer names are removal-danger / undeclared-dependency
signals a structural validate cannot catch.

Role symbols are step-relative:
    >  produces (output Parameter)          <  consumes (input Parameter)
    ?  consumes as a filter criterion       ~  consumes inside a Formula (best-effort)

**Formula edges (``~``) are best-effort.** A Formula param value is tokenized, so
function names and dotted-path segments can appear as phantom consumers. Treat
``~`` edges as hints, not ground truth — same caveat as ``trace_context.py``.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Read-only.
Pinned to Release 262 / v67.0; re-verify the GET shape if the platform changes.

Usage
-----
    # who produces / consumes a variable — the safe-removal view
    python scripts/expression_sets/trace_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --variable NetUnitPrice

    # a step's full dependency closure with scopes — what export_overlay uses
    python scripts/expression_sets/trace_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --step "Apply Discount"

    # reverse: every step that references a field/token
    python scripts/expression_sets/trace_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --field RLM_RampMode__c

    # orphans: consumed-with-no-producer (removal danger), dead outputs, undeclared __c
    python scripts/expression_sets/trace_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --orphans
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    eprint,
)
from scripts.expression_sets._graph import ExpressionSetGraph  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
)
from scripts.expression_sets.export_expression_set import fetch_definition  # noqa: E402

# Removal note operationalizing the skill's "structural, not functional" warning.
_REMOVAL_NOTE = (
    "Removal note: validation is STRUCTURAL, not functional — a well-formed "
    "overlay/definition\n  can still leave a consumer with no producer. Before "
    "removing a step, confirm nothing\n  downstream consumes what it produces "
    "(a variable with producers=[] below after removal is\n  a runtime gap the "
    "validator will NOT catch)."
)


def _fmt_scope(scope: str) -> str:
    return {"version": "version-var", "custom": "CUSTOM", "standard": "std-ctx"}.get(scope, scope)


def _trace_variable(graph: ExpressionSetGraph, name: str) -> dict:
    producers = graph.produced_by(name)
    consumers = graph.consumed_by(name)
    return {
        "variable": name,
        "scope": graph.scope(name),
        "producers": producers,
        "consumers": consumers,
        "safeToRemoveProducers": not consumers,
    }


def _print_variable(result: dict):
    name = result["variable"]
    print(f"Variable '{name}'  [{_fmt_scope(result['scope'])}]\n")
    prods = result["producers"]
    cons = result["consumers"]
    print(f"  produced by ({len(prods)}):")
    for p in prods or ["(none — supplied by context / a version variable / external)"]:
        print(f"    > {p}")
    print(f"\n  consumed by ({len(cons)}):")
    for c in cons or ["(none — dead output, unless read outside this version)"]:
        print(f"    < {c}")
    print()
    if prods and not cons:
        print("  ⚠ produced but never consumed in this version — a candidate DEAD output.\n")
    if cons and not prods and result["scope"] != "version":
        print("  ⚠ consumed with NO in-graph producer — supplied by context/external, "
              "or a GAP.\n")


def _print_step(graph: ExpressionSetGraph, step_name: str):
    closure = graph.step_closure(step_name)
    if not closure["consumes"] and not closure["produces"]:
        print(f"Step '{step_name}': no references found "
              f"(unknown step name, or a pure-constant step).")
        return
    print(f"Step '{step_name}' dependency closure:\n")
    print(f"  produces ({len(closure['produces'])}):")
    for p in closure["produces"] or ["(none)"]:
        print(f"    > {p}")
    print(f"\n  consumes ({len(closure['consumes'])}):")
    if not closure["consumes"]:
        print("    (none)")
    for c in sorted(closure["consumes"], key=lambda x: (x["scope"], x["name"])):
        prod = ",".join(c["producers"]) if c["producers"] else "NO PRODUCER"
        print(f"    {c['role']} {c['name']}  [{_fmt_scope(c['scope'])}]  "
              f"producers: {prod}")
    print()
    # Overlay-capture guidance: what each scope means for a move.
    version_vars = sorted({c["name"] for c in closure["consumes"] if c["scope"] == "version"})
    custom_refs = sorted({c["name"] for c in closure["consumes"] if c["scope"] == "custom"})
    if version_vars:
        print(f"  → ship in addVariables: {', '.join(version_vars)}")
    if custom_refs:
        print(f"  → declare in externalDependencies (target org must define): "
              f"{', '.join(custom_refs)}")
    print()


def _print_field(graph: ExpressionSetGraph, query: str):
    q = query.lower()
    hits = [e for e in graph.edges if q in e.name.lower()]
    print(f"Field/token trace for '{query}' — {len(hits)} reference(s):\n")
    if not hits:
        print("  (no matching reference)")
        return
    for e in sorted(hits, key=lambda x: (x.name, x.step)):
        print(f"    {e.role} {e.name}  in step '{e.step}'  [{_fmt_scope(graph.scope(e.name))}]")
    print()


def _print_orphans(graph: ExpressionSetGraph):
    orphans = graph.orphans()
    cnp = orphans["consumed_no_producer"]
    pu = orphans["produced_unused"]
    uc = orphans["undeclared_custom"]
    print("Orphan analysis:\n")
    print(f"  Consumed with NO producer ({len(cnp)}) — removal danger / dependency gap:")
    for n in cnp or ["(none)"]:
        scope = graph.scope(n) if n != "(none)" else ""
        print(f"    - {n}" + (f"  [{_fmt_scope(scope)}]" if scope else ""))
    print(f"\n  Produced but UNUSED ({len(pu)}) — candidate dead outputs:")
    for n in pu or ["(none)"]:
        print(f"    - {n}")
    print(f"\n  Undeclared CUSTOM refs ({len(uc)}) — externalDependencies gap "
          f"(target org must define, overlay cannot create):")
    for n in uc or ["(none)"]:
        print(f"    - {n}")
    print()
    print("  " + _REMOVAL_NOTE + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Trace the variable producer→consumer graph of a BRE Expression "
                    "Set (safe-removal + three-scope dependency capture). Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name", help="ExpressionSetDefinition DeveloperName.")
    ident.add_argument("--expression-set-id", help="Runtime ExpressionSet Id (prefix 9QL).")

    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--variable", help="Who produces / consumes this variable "
                                             "(the safe-removal view).")
    selector.add_argument("--step", help="A step's full dependency closure, with scopes.")
    selector.add_argument("--field", help="Reverse: every step referencing this "
                                          "field/token (ci substring).")
    selector.add_argument("--orphans", action="store_true",
                          help="Consumed-no-producer / dead-output / undeclared-custom.")

    parser.add_argument("--version", dest="version_api_name",
                        help="Version apiName to trace (default: first).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the result as JSON.")
    args = parser.parse_args(argv)

    try:
        es_id = args.expression_set_id
        if not es_id:
            es_id = resolve_expression_set_id(
                args.developer_name,
                target_org=args.target_org, api_version=args.api_version,
            )
        definition = fetch_definition(es_id, args.target_org, args.api_version)
    except (ExpressionSetClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    graph = ExpressionSetGraph(definition, args.version_api_name)

    if args.json:
        if args.variable is not None:
            print(json.dumps(_trace_variable(graph, args.variable), indent=2))
        elif args.step is not None:
            print(json.dumps(graph.step_closure(args.step), indent=2))
        elif args.field is not None:
            q = args.field.lower()
            print(json.dumps([
                {"role": e.role, "name": e.name, "step": e.step, "scope": graph.scope(e.name)}
                for e in graph.edges if q in e.name.lower()
            ], indent=2))
        elif args.orphans:
            print(json.dumps(graph.orphans(), indent=2))
        else:
            print(json.dumps({
                "version": graph.version_api_name,
                "steps": len(graph.steps),
                "variables": sorted(graph.variable_names),
                "referencedNames": sorted(graph.referenced_names),
            }, indent=2))
        return 0

    if args.variable is not None:
        _print_variable(_trace_variable(graph, args.variable))
    elif args.step is not None:
        _print_step(graph, args.step)
    elif args.field is not None:
        _print_field(graph, args.field)
    elif args.orphans:
        _print_orphans(graph)
    else:
        # Summary.
        print(f"{args.developer_name or es_id}  —  version {graph.version_api_name}")
        print(f"  {len(graph.steps)} step(s), {len(graph.variable_names)} version "
              f"variable(s), {len(graph.referenced_names)} referenced name(s)")
        print(f"  producers: {len(graph.producers)}   consumers: {len(graph.consumers)}")
        print("\n  Use --variable / --step / --field / --orphans to drill in.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
