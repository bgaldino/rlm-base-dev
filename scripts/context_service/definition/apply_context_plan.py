#!/usr/bin/env python3
"""Apply an additive Context Definition plan to an org.

Live-proven, for **one-off exploration and updates** outside the org build. The
org-*build* path is the CumulusCI task ``manage_context_definition``
(``tasks/rlm_context_service.py``); this standalone script applies the same plan
logic on the ``sf``-CLI transport so context plans can be iterated on without
the CCI runtime. It is **not** wired into ``cumulusci.yml`` or any flow. Auth is
delegated to the ``sf`` CLI — **no access token is ever handled or passed**
(``--target-org`` is the *SF CLI* alias, e.g. ``rlm-base__beta``, never the CCI
alias ``beta``).

It applies the same repo plan format as the CCI task
(``datasets/context_plans/<Name>/manifest.json`` → ``contexts/<plan>.json``):
additive attributes / tags / mappings / traversal hydration, and create-new
definitions (``"create": true``). Payload shaping is the pure, parity-checked
``_payload`` library; ordering is ``_apply.ContextApplier``.

Preflight order (mirrors the skill's Quick Rule 6):
  1. offline lint (``validate_context_plan.validate_manifest``)
  2. ``--validate-only`` (offline lint + org-side node/attr existence check)
  3. ``--dry-run`` (log the intended call sequence, no mutation)
  4. real apply with ``--verify``

Examples
--------
    # dry-run the RampMode plan (no org mutation; prints ordered call sequence)
    python scripts/context_service/definition/apply_context_plan.py \
        --plan-file datasets/context_plans/RampMode/manifest.json \
        --target-org rlm-base__beta --dry-run

    # apply + verify + activate
    python scripts/context_service/definition/apply_context_plan.py \
        --plan-file datasets/context_plans/RampMode/manifest.json \
        --target-org rlm-base__beta --verify --activate
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import ContextApplier, Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service.definition.validate_context_plan import validate_manifest  # noqa: E402


def _load_manifest_plans(manifest_path: Path):
    """Resolve a manifest into a list of merged plan dicts.

    Mirrors the CCI task / validator manifest handling: a ``contexts`` list of
    entries, each either an inline plan or a ``planFile`` reference merged with
    the entry (entry keys win). A manifest with no ``contexts`` list is itself a
    single inline plan.
    """
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")

    contexts = manifest.get("contexts")
    if not isinstance(contexts, list) or not contexts:
        return [manifest]

    plans = []
    for entry in contexts:
        if not isinstance(entry, dict):
            raise ValueError("each contexts entry must be an object")
        plan_file = entry.get("planFile")
        if not plan_file:
            plans.append(entry)
            continue
        plan_path = manifest_path.parent / plan_file
        with open(plan_path, "r", encoding="utf-8") as nested:
            plan_obj = json.load(nested)
        if not isinstance(plan_obj, dict):
            raise ValueError(f"planFile must contain a JSON object: {plan_path}")
        merged = {**plan_obj, **{k: v for k, v in entry.items() if k != "planFile"}}
        plans.append(merged)
    return plans


def _offline_lint(manifest_path: Path) -> bool:
    """Run the offline validator; return True if no ERRORs. Prints a summary."""
    result = validate_manifest(manifest_path)
    errors = result.errors
    warnings = result.warnings
    for issue in result.issues:
        eprint(f"  [{issue.severity.value}] {issue.location}: {issue.message}"
               if issue.location else f"  [{issue.severity.value}] {issue.message}")
    if errors:
        eprint(f"Offline lint: {len(errors)} error(s), {len(warnings)} warning(s) — "
               f"fix errors before applying.")
        return False
    eprint(f"Offline lint OK ({len(warnings)} warning(s)).")
    return True


def _render_verification(verification: dict) -> None:
    if not verification:
        return
    matched = verification.get("matched_rules", [])
    missing = verification.get("missing_rules", [])
    gaps = verification.get("hydration_gaps", [])
    if matched:
        eprint(f"Verification: {len(matched)} mapping rule(s) applied.")
        for item in matched:
            eprint("  " + json.dumps(item))
    for node, attr, mapping, sobject in gaps:
        eprint(f"Verification: missing hydration detail for {node}.{attr} in "
               f"{mapping} (sObject={sobject})")
    if missing:
        eprint(f"Verification: {len(missing)} mapping rule(s) MISSING:")
        for m in missing:
            eprint("  " + json.dumps({"mapping": m[0], "node": m[1], "contextAttribute": m[2]}))
    if verification.get("found_attrs"):
        eprint("Verification: attributes present: " + ", ".join(verification["found_attrs"]))
    if verification.get("found_tags"):
        eprint("Verification: tags present: " + ", ".join(verification["found_tags"]))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply an additive Context Definition plan to an org "
                    "(one-off updates; org build uses manage_context_definition).",
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    parser.add_argument("--plan-file", required=True,
                        help="Path to a context plan manifest.json (or a single inline plan).")
    parser.add_argument("--developer-name",
                        help="Override the target definition developerName (else from the plan).")
    parser.add_argument("--context-definition-id",
                        help="Apply directly to this ContextDefinitionId (skips name resolution).")
    parser.add_argument("--default-mapping",
                        help="Context mapping name to flag as default (isDefault) before "
                             "activation. Required to activate a freshly-created definition "
                             "that has no default mapping yet. Overrides the plan's 'defaultMapping'.")
    parser.add_argument("--activate", action="store_true",
                        help="Activate the definition after applying (overrides plan 'activate').")
    parser.add_argument("--no-activate", action="store_true",
                        help="Do not activate, even if the plan sets activate:true.")
    parser.add_argument("--deactivate-before", action="store_true",
                        help="Deactivate the definition before applying (default: in-place).")
    parser.add_argument("--validate-only", action="store_true",
                        help="Offline lint only (no mutation). Combine with --target-org for context.")
    parser.add_argument("--verify", action="store_true",
                        help="Re-fetch and log verification after applying.")
    parser.add_argument("--no-translate-plan", action="store_true",
                        help="Skip translating mappingRules (apply nodes/attrs/tags/updates only).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log the intended API calls without mutating the org.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--skip-lint", action="store_true",
                        help="Skip the offline validator preflight (not recommended).")
    args = parser.parse_args(argv)

    eprint("apply_context_plan.py — one-off plan apply. The org-build path is "
           "`cci task run manage_context_definition`.")

    manifest_path = Path(args.plan_file)
    if not manifest_path.is_file():
        eprint(f"plan-file not found: {manifest_path}")
        return 2

    # 1. Offline lint preflight.
    if not args.skip_lint:
        if not _offline_lint(manifest_path):
            return 1
    if args.validate_only:
        eprint("validate-only: offline lint complete; no org mutation performed.")
        return 0

    try:
        plans = _load_manifest_plans(manifest_path)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        eprint(f"Failed to load plan: {exc}")
        return 2

    activate = None
    if args.activate:
        activate = True
    if args.no_activate:
        activate = False

    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=args.dry_run, logger=eprint,
    )
    applier = ContextApplier(transport, logger=eprint)

    exit_code = 0
    for plan in plans:
        if args.default_mapping:
            plan = {**plan, "defaultMapping": args.default_mapping}
        dev = args.developer_name or plan.get("developerName") or "(inline)"
        eprint(f"\n=== Applying plan for: {dev} ===")
        try:
            result = applier.apply_plan(
                plan,
                context_id=args.context_definition_id,
                developer_name=args.developer_name,
                translate_plan=not args.no_translate_plan,
                activate=activate,
                deactivate_before=args.deactivate_before,
                verify=args.verify,
            )
        except ContextClientError as exc:
            eprint(f"FAILED for {dev}: {exc}")
            exit_code = 1
            continue
        except ValueError as exc:
            eprint(f"FAILED for {dev}: {exc}")
            exit_code = 1
            continue
        if result.get("skipped"):
            eprint(f"Skipped {dev} (base not available / nothing to do).")
            continue
        eprint(f"Done: context_id={result.get('context_id')} "
               f"created={result.get('created')}"
               + (" [dry-run]" if result.get("dry_run") else ""))
        if args.verify:
            _render_verification(result.get("verification"))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
