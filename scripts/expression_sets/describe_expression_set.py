#!/usr/bin/env python3
"""Pretty-print one BRE Expression Set: version → steps → params/variables (read-only).

Renders the Connect GET in **execution order** — steps sorted by their
per-parent ``sequenceNumber``, children nested under their ``parentStep`` — NOT
the alphabetical order the Connect GET serializes top-level steps in. This is the
human-readable companion to ``export_expression_set.py`` (which dumps raw JSON)
and the structural companion to ``trace_expression_set.py`` (which shows the
variable-dependency graph).

For each step it shows: sequence, name, stepType, action type (from
``customElement.definition``), and — with ``--params`` — the input/output/formula
parameters and any ``advancedCondition`` filter criteria. Version variables are
listed with their dataType.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Read-only.
Pinned to Release 262 / v67.0.

Usage
-----
    python scripts/expression_sets/describe_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure

    # with full parameter detail per step
    python scripts/expression_sets/describe_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --params
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    eprint,
)
from scripts.expression_sets._payload import unescape_value  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
)
from scripts.expression_sets.export_expression_set import fetch_definition  # noqa: E402


def _pick_version(definition: dict, version_api_name: Optional[str]) -> dict:
    versions = definition.get("versions") or []
    if not versions:
        return {}
    if version_api_name:
        for v in versions:
            if v.get("apiName") == version_api_name:
                return v
        raise ExpressionSetClientError(
            f"Version '{version_api_name}' not found in the definition."
        )
    return versions[0]


def _action_type(step: dict) -> str:
    ce = step.get("customElement") or {}
    return ce.get("definition") or ce.get("elementSubType") or step.get("stepType") or "?"


def _order_steps(steps: List[dict]) -> List[dict]:
    """Return steps as a flat list in execution order (parents, then children).

    Top-level steps (``parentStep is None``) are ordered by sequenceNumber; each
    parent's children follow it, ordered by their own per-parent sequenceNumber.
    Steps whose parent is missing are appended last so nothing is dropped.
    """
    children: Dict[str, List[dict]] = {}
    top: List[dict] = []
    for s in steps:
        parent = s.get("parentStep")
        if parent:
            children.setdefault(parent, []).append(s)
        else:
            top.append(s)
    top.sort(key=lambda s: s.get("sequenceNumber", 0))
    for kids in children.values():
        kids.sort(key=lambda s: s.get("sequenceNumber", 0))

    ordered: List[dict] = []
    seen = set()

    def emit(step: dict, depth: int):
        name = step.get("name")
        if name in seen:
            return
        seen.add(name)
        step["_depth"] = depth
        ordered.append(step)
        for child in children.get(name, []):
            emit(child, depth + 1)

    for s in top:
        emit(s, 0)
    # Any orphaned children (parent name not present) — surface, don't drop.
    for s in steps:
        if s.get("name") not in seen:
            s["_depth"] = 0
            ordered.append(s)
    return ordered


def _print_params(step: dict, indent: str):
    ce = step.get("customElement") or {}
    for p in ce.get("parameters") or []:
        if not isinstance(p, dict):
            continue
        ptype = p.get("type") or "?"
        io = p.get("dataType") or p.get("parameterType") or ""
        name = p.get("name") or p.get("leftOperand") or "?"
        val = p.get("value")
        val_s = f" = {unescape_value(val)}" if val not in (None, "") else ""
        print(f"{indent}  · [{ptype}] {name}{(' ' + io) if io else ''}{val_s}")
    ac = step.get("advancedCondition") or {}
    for c in ac.get("criteria") or []:
        if isinstance(c, dict) and c.get("sourceFieldName"):
            print(f"{indent}  ? filter: {c.get('sourceFieldName')} "
                  f"{c.get('operator') or ''} {unescape_value(c.get('value', ''))}".rstrip())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Pretty-print a BRE Expression Set in execution order. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name", help="ExpressionSetDefinition DeveloperName.")
    ident.add_argument("--expression-set-id", help="Runtime ExpressionSet Id (prefix 9QL).")
    parser.add_argument("--version", dest="version_api_name",
                        help="Version apiName to describe (default: first).")
    parser.add_argument("--params", action="store_true",
                        help="Show each step's parameters and filter criteria.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the ordered step list as JSON.")
    args = parser.parse_args(argv)

    try:
        es_id = args.expression_set_id
        if not es_id:
            es_id = resolve_expression_set_id(
                args.developer_name,
                target_org=args.target_org, api_version=args.api_version,
            )
        definition = fetch_definition(es_id, args.target_org, args.api_version)
        version = _pick_version(definition, args.version_api_name)
    except (ExpressionSetClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    steps = [s for s in (version.get("steps") or []) if isinstance(s, dict)]
    variables = [v for v in (version.get("variables") or []) if isinstance(v, dict)]
    ordered = _order_steps(steps)

    if args.json:
        print(json.dumps({
            "developerName": definition.get("developerName") or definition.get("apiName"),
            "version": version.get("apiName"),
            "isActive": version.get("enabled") or version.get("isActive"),
            "steps": [
                {"sequenceNumber": s.get("sequenceNumber"), "name": s.get("name"),
                 "parentStep": s.get("parentStep"), "stepType": s.get("stepType"),
                 "actionType": _action_type(s), "depth": s.get("_depth", 0)}
                for s in ordered
            ],
            "variables": [{"name": v.get("name"), "dataType": v.get("dataType")}
                          for v in variables],
        }, indent=2))
        return 0

    name = definition.get("developerName") or definition.get("apiName") or es_id
    active = version.get("enabled")
    if active is None:
        active = version.get("isActive")
    print(f"{name}  —  version {version.get('apiName')}  "
          f"({'ACTIVE' if active else 'inactive'})")
    print(f"  {len(steps)} step(s), {len(variables)} variable(s)\n")

    for s in ordered:
        depth = s.get("_depth", 0)
        indent = "    " + "  " * depth
        seq = s.get("sequenceNumber", "?")
        marker = "└─ " if depth else ""
        print(f"{indent}{marker}[{seq}] {s.get('name')}  "
              f"<{s.get('stepType')}/{_action_type(s)}>")
        if args.params:
            _print_params(s, indent)

    if variables:
        print("\n  Variables:")
        for v in sorted(variables, key=lambda x: x.get("name") or ""):
            transient = " transient" if v.get("isTransient") else ""
            print(f"    - {v.get('name')} [{v.get('dataType')}{transient}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
