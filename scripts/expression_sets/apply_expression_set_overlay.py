#!/usr/bin/env python3
"""Apply a declarative overlay to a live BRE Expression Set (MUTATING).

Merges an overlay (``addSteps`` / ``removeSteps`` / ``updateSteps`` /
``reorderSteps`` / ``addVariables`` / ``removeVariables``) into a live expression
set's active version via a full-graph Connect PATCH, run through the
deactivate→mutate→reactivate lifecycle (``_lifecycle.LifecycleEngine``).

The safety design mirrors the CCI task exactly — **every local check runs BEFORE
any deactivation**, so a bad overlay never leaves a version toggled off:

1. Validate the overlay shape.
2. GET the live definition and cross-check placement/update/reorder/remove
   targets against it (a typo'd target fails locally).
3. Simulate the merge on that snapshot and validate the merged graph.
4. Align ``ResourceInitializationType``.
5. Only then: deactivate (with the procedure-plan cascade) → re-GET → merge →
   validate → PATCH → verify → reactivate. A failed PATCH leaves the version
   DEACTIVATED (not atomic; never reactivated over a corrupted definition).

**Preview by default.** Without ``--confirm`` the tool runs steps 1–3 (all local,
no org mutation) and logs the plan; the transport is in dry-run so nothing is
written. Re-run with ``--confirm`` to apply.

Quick Rule 8 — apply to a disposable clone, never a shipped procedure.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to
Release 262 / v67.0.

Usage
-----
    # preview the merge (no mutation)
    python scripts/expression_sets/apply_expression_set_overlay.py \
        --target-org rlm-base__beta \
        --expression-set RLM_MyClone --overlay /tmp/add_step.overlay.json

    # apply
    python scripts/expression_sets/apply_expression_set_overlay.py \
        --target-org rlm-base__beta \
        --expression-set RLM_MyClone --overlay /tmp/add_step.overlay.json --confirm
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
)
from scripts.expression_sets._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.expression_sets._overlay import (  # noqa: E402
    OverlayError,
    apply_overlay,
    overlay_labels,
)
from scripts.expression_sets._payload import (  # noqa: E402
    normalize_html_entities,
    strip_readonly_fields,
)
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_definition_id,
    resolve_expression_set_id,
    resolve_version_by_es_id,
)
from scripts.expression_sets._schema import (  # noqa: E402
    validate_definition,
    validate_overlay_against_definition,
)
from scripts.expression_sets._tooling import (  # noqa: E402
    capture_labels,
    restore_labels_after_clobber,
)


def _report(result, label):
    """Print a ValidationResult; return True if it passed (errors are fatal)."""
    if result.warnings:
        eprint(f"{label} warnings:\n{result.format_report()}\n")
    if not result.passed:
        eprint(f"{label} FAILED:\n{result.format_report()}")
    return result.passed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply a declarative overlay to a live BRE Expression Set. "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--overlay", required=True, help="Overlay JSON file.")
    parser.add_argument("--expression-set", dest="es_api_name",
                        help="ExpressionSetDefinition DeveloperName (else read from "
                             "the overlay's expressionSetApiName).")
    parser.add_argument("--version", dest="version_api_name",
                        help="Target version apiName (else the overlay's versionApiName, "
                             "else the active version).")
    parser.add_argument("--no-verify", action="store_true",
                        help="Skip the post-PATCH verification re-GET.")
    parser.add_argument("--no-preserve-labels", action="store_true",
                        help="Do NOT auto-restore step labels after the PATCH. By "
                             "default the readable labels the Connect PATCH clobbers "
                             "are captured beforehand and re-applied afterwards (plus "
                             "any labels the overlay carries), via a second "
                             "deactivate→Tooling PATCH→reactivate cycle.")
    parser.add_argument("--no-activate", action="store_true",
                        help="Leave the version DEACTIVATED after apply.")
    parser.add_argument("--no-cascade", action="store_true",
                        help="Do NOT cascade-deactivate referencing procedure-plan versions.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually apply the overlay. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    overlay_path = Path(args.overlay)
    if not overlay_path.exists():
        eprint(f"Error: overlay file not found: {overlay_path}")
        return 2
    try:
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        eprint(f"Error: could not read overlay JSON: {exc}")
        return 2

    es_api_name = args.es_api_name or overlay.get("expressionSetApiName")
    if not es_api_name:
        eprint("Error: --expression-set required (or set expressionSetApiName in the overlay).")
        return 2
    version_api_name = args.version_api_name or overlay.get("versionApiName")

    preview = not args.confirm
    activate_after = not args.no_activate
    cascade = not args.no_cascade
    verify = not args.no_verify
    preserve_labels = not args.no_preserve_labels
    # Default = nothing to restore (preview, --no-preserve-labels, --no-activate, or
    # an empty restore map all leave this untouched → ok). A performed restore
    # overwrites it, and its `ok` gates the exit code / success message below.
    restore_result = {"ok": True, "changed": [], "error": None}
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        es_id = resolve_expression_set_id(
            es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        es_def_id = resolve_definition_id(
            es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        esv = resolve_version_by_es_id(
            es_id, target_org=args.target_org, api_version=args.api_version, logger=eprint
        )

        # ---- local pre-flights (BEFORE any deactivation) ----------------- #
        preflight_def = engine.get_definition(es_id)
        cross = validate_overlay_against_definition(overlay, preflight_def, version_api_name)
        if not _report(cross, "Overlay cross-check"):
            return 1
        simulated = apply_overlay(preflight_def, overlay,
                                  version_api_name=version_api_name, error_cls=OverlayError)
        # Validate the merge in the SAME shape it will be sent — normalized
        # (HTML-unescaped). Validating the raw GET here instead would emit an
        # HTML-entity warning for every pre-existing escaped value in the
        # untouched steps (dozens on a real procedure), none of which the overlay
        # introduced and all of which the send normalizes away.
        if not _report(validate_definition(normalize_html_entities(simulated)),
                       "Simulated merge"):
            return 1

        eprint(f"Apply overlay → '{es_api_name}' (es_id={es_id}, version={esv.get('ApiName')}), "
               f"activate_after={activate_after}, cascade={cascade}, "
               f"{'PREVIEW' if preview else 'CONFIRM'}")

        # A full-graph Connect PATCH resets step labels to their spaceless names
        # (Connect has no label field). Capture the readable labels it is about to
        # clobber (best-effort, non-fatal) so they can be re-applied afterwards,
        # merged with any labels the overlay itself carries (for its new steps).
        # --no-preserve-labels opts out (then this is just informational).
        version_api_name_live = esv.get("ApiName")
        captured = capture_labels(
            transport, version_api_name_live, eprint,
            es_def_id=es_def_id, version_number=esv.get("VersionNumber"),
        ) if preserve_labels else {}
        ov_labels = overlay_labels(overlay) if preserve_labels else {}
        restore_map = {**captured, **ov_labels} if preserve_labels else {}
        if preserve_labels and restore_map:
            eprint(f"Will restore {len(restore_map)} step label(s) after the PATCH "
                   f"(captured {len(captured)}, overlay-supplied "
                   f"{len(ov_labels)}) via a second "
                   f"deactivate→relabel→reactivate cycle. --no-preserve-labels to skip.")
        elif not preserve_labels:
            eprint("--no-preserve-labels: step labels the Connect PATCH clobbers "
                   "will NOT be restored (run relabel_expression_set.py to fix).")

        engine.ensure_resource_initialization_type(
            es_id, preflight_def.get("resourceInitializationType")
        )

        def mutate():
            # Re-GET post-deactivation so the PATCH reflects the deactivated
            # state; re-merge + re-validate as a last guard against drift.
            definition = engine.get_definition(es_id)
            modified = apply_overlay(definition, overlay,
                                     version_api_name=version_api_name, error_cls=OverlayError)
            merged = validate_definition(modified)
            if not merged.passed:
                raise LifecycleError(
                    "Merged definition failed validation post-deactivation:\n"
                    + merged.format_report()
                )
            patch_payload = normalize_html_entities(strip_readonly_fields(modified))
            engine.patch_definition(es_id, patch_payload)
            engine.log(f"PATCHed expression set {es_id}.")
            if verify and not preview:
                _verify(engine, es_id, overlay, version_api_name)

        engine.run_mutation(
            es_def_id=es_def_id, esv=esv, mutate=mutate,
            activate_after=activate_after, cascade=cascade, verb="Overlay apply",
        )

        # The Connect PATCH above clobbered labels; restore them now (a second
        # deactivate→Tooling PATCH→reactivate cycle). Only meaningful when the
        # version was reactivated (activate_after) — a relabel needs the same
        # deactivate window and would leave it off again otherwise. Non-fatal: the
        # overlay already applied, so a restore failure is reported, not raised —
        # but it IS surfaced at the CLI boundary (exit code + JSON) so an operator
        # never reads "Successfully applied" over a version whose labels are stale.
        if preserve_labels and restore_map and activate_after:
            restore_result = restore_labels_after_clobber(
                engine, es_id=es_id, es_def_id=es_def_id,
                version_api_name=version_api_name_live,
                name_to_label=restore_map, cascade=cascade,
            )
        elif preserve_labels and restore_map and not activate_after:
            eprint("Note: --no-activate set — leaving labels un-restored (relabel "
                   "needs to reactivate). Run relabel_expression_set.py when ready.")

    except (ExpressionSetClientError, ResolveError, LifecycleError, OverlayError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    restore_ok = restore_result.get("ok", True)
    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    elif restore_ok:
        eprint(f"\nSuccessfully applied overlay {args.overlay} to {es_api_name}.")
    else:
        eprint(f"\nApplied overlay {args.overlay} to {es_api_name}, but step-label "
               f"RESTORE FAILED ({restore_result.get('error')}). The overlay is live; "
               f"only the readable labels are stale. Re-run relabel_expression_set.py "
               f"--expression-set {es_api_name} to restore them.")
    if args.json:
        print(json.dumps({"action": "apply_overlay", "expressionSet": es_api_name,
                          "expressionSetId": es_id, "dryRun": preview,
                          "labelRestore": restore_result}, indent=2))
    return 0 if restore_ok else 1


def _verify(engine: LifecycleEngine, es_id: str, overlay: dict, version_api_name):
    """Confirm added steps are present and removed steps are gone after the PATCH."""
    definition = engine.get_definition(es_id)
    versions = definition.get("versions") or []
    version = None
    if version_api_name:
        version = next((v for v in versions if v.get("apiName") == version_api_name), None)
    if version is None and versions:
        version = versions[0]
    if version is None:
        raise LifecycleError(
            "Verification failed: post-PATCH definition returned no versions."
        )
    names = {s.get("name") for s in (version.get("steps") or []) if isinstance(s, dict)}

    missing = [s["name"] for s in overlay.get("addSteps", []) if s.get("name") not in names]
    if missing:
        raise LifecycleError(f"Verification failed: added step(s) not present: {missing}.")
    still_there = [s["name"] for s in overlay.get("removeSteps", []) if s.get("name") in names]
    if still_there:
        raise LifecycleError(
            f"Verification failed: removed step(s) still present: {still_there}."
        )
    engine.log("Verified overlay applied (added present, removed absent).")


if __name__ == "__main__":
    raise SystemExit(main())
