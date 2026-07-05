#!/usr/bin/env python3
"""Create or replace a whole BRE Expression Set from a JSON file (MUTATING).

The write half of the export→import round trip. Reads a definition JSON (the
shape ``export_expression_set.py`` writes), auto-detects **create vs replace**
against the target org, and runs the full deactivate→mutate→reactivate lifecycle
via ``_lifecycle.LifecycleEngine``:

* **replace** (the set already exists) → Connect **PATCH**. The version-level
  ``id`` is KEPT but REWRITTEN to the *target* org's version id (an export from a
  source org carries the source id); string leaves are HTML-unescaped. The active
  version is deactivated (with the procedure-plan cascade) before the PATCH and
  reactivated after — unless the PATCH fails, in which case the version is left
  DEACTIVATED (a failed PATCH is not atomic; re-enabling a half-mutated procedure
  is worse than leaving it offline).
* **create** (the set is new) → Connect **POST**. The version-level ``id`` is
  STRIPPED (a source-org id makes the server reject/mis-bind the new version);
  the created version is then activated/deactivated per ``--no-activate``.

**Preview by default.** Without ``--confirm`` the tool resolves ids, validates,
and logs the exact mutation sequence but performs NO write (the transport runs in
dry-run). Re-run with ``--confirm`` to apply.

Quick Rule 8 — never mutate a shipped procedure. Import into a disposable clone
(rename ``apiName``/``developerName`` in the JSON first), never over a
production expression set.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to
Release 262 / v67.0.

Usage
-----
    # preview (no mutation)
    python scripts/expression_sets/import_expression_set.py \
        --target-org rlm-base__july4_ctxPilot --input-file /tmp/clone.json

    # apply
    python scripts/expression_sets/import_expression_set.py \
        --target-org rlm-base__july4_ctxPilot --input-file /tmp/clone.json --confirm
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
from scripts.expression_sets._payload import (  # noqa: E402
    normalize_html_entities,
    rewrite_version_id,
    strip_readonly_fields,
)
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_definition_id,
    resolve_expression_set_id,
    resolve_version_by_es_id,
)
from scripts.expression_sets._schema import validate_definition  # noqa: E402


def _developer_name(payload: dict) -> str:
    name = payload.get("apiName") or payload.get("developerName")
    if not name:
        raise ExpressionSetClientError(
            "Input JSON must contain an 'apiName' (or 'developerName') field."
        )
    return name


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create or replace a whole BRE Expression Set from JSON. MUTATING "
                    "(preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    parser.add_argument("--input-file", required=True,
                        help="Definition JSON (the shape export_expression_set.py writes).")
    parser.add_argument("--no-activate", action="store_true",
                        help="Leave the version DEACTIVATED after import (default: activate).")
    parser.add_argument("--no-cascade", action="store_true",
                        help="Do NOT cascade-deactivate referencing procedure-plan versions.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually perform the import. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    input_path = Path(args.input_file)
    if not input_path.exists():
        eprint(f"Error: input file not found: {input_path}")
        return 2

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        eprint(f"Error: could not read input JSON: {exc}")
        return 2

    try:
        api_name = _developer_name(payload)
    except ExpressionSetClientError as exc:
        eprint(f"Error: {exc}")
        return 2

    # Pre-flight: validate the full definition before any create/replace.
    validation = validate_definition(payload)
    if not validation.passed:
        eprint("Definition validation FAILED — not imported:\n")
        eprint(validation.format_report())
        return 1
    if validation.warnings:
        eprint(validation.format_report() + "\n")

    preview = not args.confirm
    activate_after = not args.no_activate
    cascade = not args.no_cascade
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        # Auto-detect create vs replace.
        try:
            es_def_id = resolve_definition_id(
                api_name, target_org=args.target_org, api_version=args.api_version
            )
            mode = "replace"
        except ResolveError:
            es_def_id = None
            mode = "create"

        eprint(f"Import '{api_name}' → mode={mode}, activate_after={activate_after}, "
               f"cascade={cascade}, {'PREVIEW' if preview else 'CONFIRM'}")

        result = {"action": "import", "expressionSet": api_name, "mode": mode,
                  "dryRun": preview}

        if mode == "replace":
            es_id = resolve_expression_set_id(
                api_name, target_org=args.target_org, api_version=args.api_version
            )
            esv = resolve_version_by_es_id(
                es_id, target_org=args.target_org, api_version=args.api_version,
                logger=eprint,
            )
            engine.ensure_resource_initialization_type(
                es_id, payload.get("resourceInitializationType")
            )

            def mutate():
                patch_payload = strip_readonly_fields(payload)
                patch_payload = rewrite_version_id(patch_payload, esv["Id"])
                patch_payload = normalize_html_entities(patch_payload)
                engine.patch_definition(es_id, patch_payload)
                engine.log(f"PATCHed expression set {es_id}.")

            engine.run_mutation(
                es_def_id=es_def_id, esv=esv, mutate=mutate,
                activate_after=activate_after, cascade=cascade, verb="Import",
            )
            result["expressionSetId"] = es_id
            result["versionId"] = esv["Id"]
        else:  # create
            create_payload = strip_readonly_fields(payload, for_create=True)
            create_payload = normalize_html_entities(create_payload)
            if preview:
                engine.log(f"[preview] Would POST-create expression set '{api_name}'.")
            else:
                post_result = engine.post_definition(create_payload)
                es_id = post_result.get("id") if isinstance(post_result, dict) else None
                if not es_id:
                    raise LifecycleError(
                        "Connect POST returned no expression set id; the create may "
                        f"not have committed. Response: {post_result!r}"
                    )
                engine.log(f"Created expression set {api_name} (Id: {es_id}).")
                esv = resolve_version_by_es_id(
                    es_id, target_org=args.target_org, api_version=args.api_version,
                    logger=eprint,
                )
                desired = activate_after
                if bool(esv.get("IsActive")) is not desired:
                    engine.set_version_active(esv["Id"], desired)
                    engine.wait_for_version_state(esv["Id"], desired)
                result["expressionSetId"] = es_id
                result["versionId"] = esv["Id"]

    except (ExpressionSetClientError, ResolveError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    else:
        eprint(f"\nImport complete for '{api_name}'.")
    if args.json:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
