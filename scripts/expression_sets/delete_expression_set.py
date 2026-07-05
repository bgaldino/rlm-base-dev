#!/usr/bin/env python3
"""Delete a whole BRE Expression Set, or one version (DESTRUCTIVE, MUTATING).

Two modes:

* **whole set** (no ``--version``) → Connect **DELETE** of the entire expression
  set. A live ``ProcedurePlanDefinitionVersion`` referencing the set can lock its
  version, so the delete cascade-deactivates referencing procedure-plan versions
  first, then the ES version, then DELETEs. If anything between the cascade and
  the DELETE fails, the cluster is rolled back to its exact pre-attempt state (a
  failed DELETE leaves the record byte-identical, so re-enabling is safe).
* **single version** (``--version <apiName>``) → SObject DELETE of one
  ``ExpressionSetVersion``, leaving the set and its other versions intact (the
  post-new-version → delete-old-version workflow). An enabled version is
  deactivated first.

**Destructive — double-gated.** Preview by default: without ``--confirm`` the
tool resolves ids and logs the plan but deletes nothing. ``--confirm`` is
REQUIRED to actually delete (there is no separate ``--dry-run`` flag; absence of
``--confirm`` IS the dry run).

Quick Rule 8 — delete only disposable clones, never a shipped procedure.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to
Release 262 / v67.0.

Usage
-----
    # preview deleting a whole clone
    python scripts/expression_sets/delete_expression_set.py \
        --target-org rlm-base__july4_ctxPilot --expression-set RLM_MyClone

    # actually delete it
    python scripts/expression_sets/delete_expression_set.py \
        --target-org rlm-base__july4_ctxPilot --expression-set RLM_MyClone --confirm

    # delete one old version, keep the set
    python scripts/expression_sets/delete_expression_set.py \
        --target-org rlm-base__july4_ctxPilot \
        --expression-set RLM_MyClone --version RLM_MyClone_V1 --confirm
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
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_definition_id,
    resolve_expression_set_id,
    resolve_version_by_es_id,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete a whole BRE Expression Set or one version. DESTRUCTIVE "
                    "(preview by default; --confirm REQUIRED to delete).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    parser.add_argument("--expression-set", dest="es_api_name", required=True,
                        help="ExpressionSetDefinition DeveloperName.")
    parser.add_argument("--version", dest="version_api_name",
                        help="Delete only this version (leave the set intact).")
    parser.add_argument("--confirm", action="store_true",
                        help="REQUIRED to actually delete. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        es_id = resolve_expression_set_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version
        )

        if args.version_api_name:
            eprint(f"Delete VERSION '{args.version_api_name}' of '{args.es_api_name}' "
                   f"(es_id={es_id}), {'PREVIEW' if preview else 'CONFIRM'}")
            result = engine.delete_single_version(
                args.version_api_name, es_id, args.es_api_name
            )
        else:
            es_def_id = resolve_definition_id(
                args.es_api_name, target_org=args.target_org, api_version=args.api_version
            )
            esv = resolve_version_by_es_id(
                es_id, target_org=args.target_org, api_version=args.api_version, logger=eprint
            )
            eprint(f"Delete WHOLE expression set '{args.es_api_name}' (es_id={es_id}), "
                   f"{'PREVIEW' if preview else 'CONFIRM'}")
            result = engine.delete_expression_set(
                es_id=es_id, es_def_id=es_def_id, esv=esv, api_name=args.es_api_name
            )

    except (ExpressionSetClientError, ResolveError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No deletion performed. Re-run with --confirm to delete.")
    else:
        eprint("\nDeletion complete.")
    if args.json:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
