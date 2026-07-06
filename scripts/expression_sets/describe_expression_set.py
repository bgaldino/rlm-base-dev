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

The Connect GET this reads has **no ``label`` field** — the readable UI title of
each step lives only in the Tooling ``ExpressionSetDefinitionVersion.Metadata``.
Pass ``--labels`` to join those in (one extra Tooling GET): each step then prints
its readable label above the ``name``, and steps whose label is missing or equal
to the spaceless name (the fingerprint of a Connect-created / Connect-clobbered
step) are flagged as drift. See ``metadata-vs-connect.md`` → *Step names vs.
labels*.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Read-only.
Pinned to Release 262 / v67.0.

Usage
-----
    python scripts/expression_sets/describe_expression_set.py \
        --target-org rlm-base__beta \
        --developer-name RLM_DefaultPricingProcedure

    # with full parameter detail per step
    python scripts/expression_sets/describe_expression_set.py \
        --target-org rlm-base__beta \
        --developer-name RLM_DefaultPricingProcedure --params

    # join readable Tooling labels + flag label drift
    python scripts/expression_sets/describe_expression_set.py \
        --target-org rlm-base__beta \
        --developer-name RLM_DefaultPricingProcedure --labels
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
    Transport,
    eprint,
)
from scripts.expression_sets._payload import unescape_value  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
)
from scripts.expression_sets._tooling import (  # noqa: E402
    ToolingError,
    fetch_metadata,
    resolve_esdv,
    step_labels,
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


def _fetch_labels(version: dict, target_org: str, api_version: str) -> Dict[str, Optional[str]]:
    """Join Tooling step labels for a version, keyed by step ``name``.

    The Connect ``version.apiName`` equals the Tooling
    ``ExpressionSetDefinitionVersion.DeveloperName``, so it pins the label read to
    the exact version being described. Returns ``{}`` (and warns) if the Tooling
    read fails — labels are an enrichment, never a reason to fail a read-only
    describe.
    """
    version_api_name = version.get("apiName")
    if not version_api_name:
        eprint("Warning: version has no apiName; cannot join Tooling labels.")
        return {}
    transport = Transport(target_org=target_org, api_version=api_version, logger=eprint)
    try:
        esdv = resolve_esdv(transport, version_api_name=version_api_name)
        metadata = fetch_metadata(transport, esdv["Id"])
    except ToolingError as exc:
        eprint(f"Warning: could not read Tooling labels ({exc}); showing names only.")
        return {}
    return step_labels(metadata)


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
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name", help="ExpressionSetDefinition DeveloperName.")
    ident.add_argument("--expression-set-id", help="Runtime ExpressionSet Id (prefix 9QL).")
    parser.add_argument("--version", dest="version_api_name",
                        help="Version apiName to describe (default: first).")
    parser.add_argument("--params", action="store_true",
                        help="Show each step's parameters and filter criteria.")
    parser.add_argument("--labels", action="store_true",
                        help="Join readable step labels from the Tooling API "
                             "(Connect has none) and flag label==name drift.")
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

    # Tooling label join (opt-in): the Connect GET has no `label`; enrich from
    # the Tooling Metadata. A step is "drift" when its label is missing or equals
    # the spaceless name (Connect-created / Connect-clobbered).
    labels: Dict[str, Optional[str]] = {}
    if args.labels:
        labels = _fetch_labels(version, args.target_org, args.api_version)

    def _drift(step_name):
        label = labels.get(step_name)
        return not label or label == step_name

    if args.json:
        payload = {
            "developerName": definition.get("developerName") or definition.get("apiName"),
            "version": version.get("apiName"),
            "isActive": version.get("enabled") or version.get("isActive"),
            "steps": [
                {"sequenceNumber": s.get("sequenceNumber"), "name": s.get("name"),
                 "parentStep": s.get("parentStep"), "stepType": s.get("stepType"),
                 "actionType": _action_type(s), "depth": s.get("_depth", 0),
                 **({"label": labels.get(s.get("name")),
                     "labelDrift": _drift(s.get("name"))} if args.labels else {})}
                for s in ordered
            ],
            "variables": [{"name": v.get("name"), "dataType": v.get("dataType")}
                          for v in variables],
        }
        if args.labels:
            payload["labelDriftCount"] = sum(1 for s in ordered if _drift(s.get("name")))
        print(json.dumps(payload, indent=2))
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
        step_name = s.get("name")
        if args.labels:
            label = labels.get(step_name)
            drift = " ⚠ no label" if _drift(step_name) else ""
            shown = label if (label and label != step_name) else step_name
            print(f"{indent}{marker}[{seq}] {shown}{drift}")
            print(f"{indent}{'   ' if depth else ''}     name: {step_name}  "
                  f"<{s.get('stepType')}/{_action_type(s)}>")
        else:
            print(f"{indent}{marker}[{seq}] {step_name}  "
                  f"<{s.get('stepType')}/{_action_type(s)}>")
        if args.params:
            _print_params(s, indent)

    if args.labels:
        drifted = [s.get("name") for s in ordered if _drift(s.get("name"))]
        if drifted:
            print(f"\n  ⚠ {len(drifted)} step(s) have no readable label "
                  f"(label missing or == name): {', '.join(drifted)}")
            print("    Set readable labels with relabel_expression_set.py.")
        else:
            print(f"\n  ✓ all {len(ordered)} step(s) have a readable label.")

    if variables:
        print("\n  Variables:")
        for v in sorted(variables, key=lambda x: x.get("name") or ""):
            transient = " transient" if v.get("isTransient") else ""
            print(f"    - {v.get('name')} [{v.get('dataType')}{transient}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
