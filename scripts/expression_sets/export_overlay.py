#!/usr/bin/env python3
"""Slice step(s) from a live Expression Set into a validated addSteps overlay (read-only).

Bridges ``trace`` and ``apply_overlay``: given one or more step names in a live
procedure, it emits an ``addSteps`` overlay carrying those steps verbatim, with
their three dependency scopes pre-classified (via the same ``_graph`` classifier
``trace --step`` uses) so you know exactly what else must travel with the step:

* **version** dependencies → emitted into the overlay's ``addVariables`` (unless
  ``--no-variables``), so the step's Constants/Locals ship with it.
* **custom** (``__c`` / ``__r``) dependencies → emitted into
  ``externalDependencies`` (the overlay CANNOT create these; the target org must
  already define them). This is advisory metadata the validator cross-checks.
* **standard** dependencies → nothing emitted (context-supplied).

The emitted overlay is HTML-unescaped (so Formula/criteria values are engine-
ready) and run through the package's own ``validate_overlay`` before it is
written — a non-clean validation fails the export (``--allow-warnings`` to
proceed past warnings). The result is ready for
``apply_overlay.py --overlay <file>`` against a clone.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Read-only
(reads the source org; writes only a local file). Pinned to Release 262 / v67.0.

Usage
-----
    # slice one step into an overlay, placed after another step
    python scripts/expression_sets/export_overlay.py \
        --target-org rlm-base__beta \
        --developer-name RLM_DefaultPricingProcedure \
        --step "Apply Discount" --after "Get List Price" \
        --out /tmp/apply_discount.overlay.json

    # slice several steps, keep source sequence, print to stdout
    python scripts/expression_sets/export_overlay.py \
        --target-org rlm-base__beta \
        --developer-name RLM_DefaultPricingProcedure \
        --step "Step A" --step "Step B"
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
from scripts.expression_sets._graph import ExpressionSetGraph  # noqa: E402
from scripts.expression_sets._payload import unescape_value  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_expression_set_id,
)
from scripts.expression_sets._schema import validate_overlay  # noqa: E402
from scripts.expression_sets.export_expression_set import fetch_definition  # noqa: E402


def build_overlay(
    definition: dict,
    step_names: List[str],
    *,
    version_api_name: Optional[str] = None,
    after: Optional[str] = None,
    include_variables: bool = True,
) -> dict:
    """Slice the named steps into an addSteps overlay with scoped dependencies.

    Raises ``ExpressionSetClientError`` if a named step is absent. The overlay's
    ``addSteps`` carry the steps verbatim (HTML-unescaped); the first step gets a
    ``placement.afterStep`` if ``--after`` was given; version-scoped dependencies
    become ``addVariables``; custom-scoped become ``externalDependencies``.
    """
    versions = definition.get("versions") or []
    if version_api_name:
        version = next((v for v in versions if v.get("apiName") == version_api_name), None)
    else:
        version = versions[0] if versions else None
    if not version:
        raise ExpressionSetClientError("Definition has no matching version.")

    steps_by_name: Dict[str, dict] = {
        s.get("name"): s for s in (version.get("steps") or []) if isinstance(s, dict)
    }
    variables_by_name: Dict[str, dict] = {
        v.get("name"): v for v in (version.get("variables") or []) if isinstance(v, dict)
    }
    missing = [n for n in step_names if n not in steps_by_name]
    if missing:
        raise ExpressionSetClientError(
            f"Step(s) not found in the definition: {', '.join(missing)}."
        )

    graph = ExpressionSetGraph(definition, version_api_name)

    add_steps: List[dict] = []
    version_deps: set = set()
    custom_deps: set = set()
    for i, name in enumerate(step_names):
        step = unescape_value(steps_by_name[name])
        step = {k: v for k, v in step.items() if k != "_depth"}
        if i == 0 and after:
            step["placement"] = {"afterStep": after}
        add_steps.append(step)
        closure = graph.step_closure(name)
        for c in closure["consumes"]:
            if c["scope"] == "version":
                version_deps.add(c["name"])
            elif c["scope"] == "custom":
                custom_deps.add(c["name"])

    overlay: dict = {"addSteps": add_steps}
    if include_variables and version_deps:
        overlay["addVariables"] = [
            unescape_value(variables_by_name[n])
            for n in sorted(version_deps)
            if n in variables_by_name
        ]
    if custom_deps:
        # The validator's externalDependencies block is an OBJECT with
        # customFields / contextNodes / contextFields / note. Custom-scoped refs
        # (``__c`` / ``__r``) are custom fields the target org must already
        # define — route them to customFields. The note documents intent.
        overlay["externalDependencies"] = {
            "customFields": sorted(custom_deps),
            "note": (
                "Custom fields consumed by the sliced step(s). The overlay CANNOT "
                "create these — the target org must already define them, mapped "
                "into the bound ContextDefinition."
            ),
        }
    return overlay


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Slice step(s) from a live Expression Set into a validated "
                    "addSteps overlay with scoped dependencies. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    ident = parser.add_mutually_exclusive_group(required=True)
    ident.add_argument("--developer-name", help="ExpressionSetDefinition DeveloperName.")
    ident.add_argument("--expression-set-id", help="Runtime ExpressionSet Id (prefix 9QL).")
    parser.add_argument("--step", action="append", dest="steps", required=True,
                        metavar="NAME", help="Step name to slice (repeatable).")
    parser.add_argument("--after", help="Place the first sliced step after this step "
                                        "(placement.afterStep) in the target.")
    parser.add_argument("--version", dest="version_api_name",
                        help="Source version apiName (default: first).")
    parser.add_argument("--no-variables", action="store_true",
                        help="Do NOT emit version-scoped deps into addVariables.")
    parser.add_argument("--allow-warnings", action="store_true",
                        help="Write the overlay even if validation emits warnings "
                             "(errors always fail).")
    parser.add_argument("--out", help="Output file path (default: stdout).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    args = parser.parse_args(argv)

    try:
        es_id = args.expression_set_id
        if not es_id:
            es_id = resolve_expression_set_id(
                args.developer_name,
                target_org=args.target_org, api_version=args.api_version,
            )
        definition = fetch_definition(es_id, args.target_org, args.api_version)
        overlay = build_overlay(
            definition, args.steps,
            version_api_name=args.version_api_name,
            after=args.after,
            include_variables=not args.no_variables,
        )
    except (ExpressionSetClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    validation = validate_overlay(overlay)
    if not validation.passed:
        eprint("Overlay validation FAILED — not written:\n")
        eprint(validation.format_report())
        return 1
    if validation.warnings:
        eprint(validation.format_report())
        if not args.allow_warnings:
            eprint("\nWarnings present; re-run with --allow-warnings to write anyway.")
            return 1

    # Report the scope breakdown to stderr so --out stdout stays clean JSON.
    ext_fields = (overlay.get("externalDependencies") or {}).get("customFields", [])
    eprint(f"Sliced {len(overlay['addSteps'])} step(s); "
           f"addVariables={len(overlay.get('addVariables', []))}, "
           f"externalDependencies.customFields={len(ext_fields)}.")
    if ext_fields:
        eprint("  externalDependencies.customFields (target org MUST define these — "
               "overlay cannot create them):")
        for d in ext_fields:
            eprint(f"    - {d}")

    payload = json.dumps(overlay, indent=2)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
        eprint(f"Wrote {args.out}.")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
