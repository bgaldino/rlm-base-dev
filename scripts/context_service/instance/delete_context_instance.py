#!/usr/bin/env python3
"""Evict a runtime context instance, or clear the runtime schema cache (EXPERIMENTAL).

Two mutually-exclusive modes:

* evict — ``DELETE /connect/contexts/{contextId}`` — drop a hydrated runtime
  instance from the cache (frees the ``contextId`` handle).
* clear schema cache — ``--clear-schema-cache --developer-name NAME
  [--mapping-names …]`` → ``DELETE /connect/context-runtime-schema/clear`` — evict
  the cached **runtime schema** for a definition so the next hydration re-reads it
  (use after changing a definition's mappings while testing).

⚠️  **EXPERIMENTAL / verify-live (262 / v67.0).** Not build-critical, not wired
into any CCI flow. This is **not** the design-time definition delete — that is
``delete_context.py`` (deactivate / hard-delete a ContextDefinition). This script
only touches the runtime cache. Auth is delegated to the ``sf`` CLI — no access
token is handled. ``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``),
never the CCI alias.

Usage:
    # evict one instance
    python scripts/context_service/delete_context_instance.py \
        --target-org rlm-base__beta --context-id <uuid>

    # clear the cached runtime schema for a definition (all mappings)
    python scripts/context_service/delete_context_instance.py \
        --target-org rlm-base__beta --clear-schema-cache \
        --developer-name RLM_SalesTransactionContext
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._runtime import RuntimeContextClient  # noqa: E402
from scripts.context_service._runtime_cli import CONTEXT_ID_SCOPE_NOTE, EXPERIMENTAL_BANNER  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Evict a runtime context instance or clear the runtime schema cache "
                    "(EXPERIMENTAL)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--context-id",
                      help="Evict this runtime instance (DELETE /connect/contexts/{id}).")
    mode.add_argument("--clear-schema-cache", action="store_true",
                      help="Clear the cached runtime schema for a definition "
                           "(requires --developer-name).")
    parser.add_argument("--developer-name",
                        help="Definition developerName for --clear-schema-cache "
                             "(the contextDefinitionName query param).")
    parser.add_argument("--mapping-names", nargs="+", metavar="NAME",
                        help="Restrict --clear-schema-cache to these mapping names.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log the intended delete without mutating the org.")
    parser.add_argument("--json", action="store_true",
                        help="Emit the raw response as JSON.")
    args = parser.parse_args(argv)

    eprint(EXPERIMENTAL_BANNER)

    if args.clear_schema_cache and not args.developer_name:
        eprint("Error: --clear-schema-cache requires --developer-name "
               "(the contextDefinitionName to evict).")
        return 2

    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=args.dry_run, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)

    try:
        if args.clear_schema_cache:
            result = client.clear_runtime_schema(
                context_definition_name=args.developer_name,
                mapping_names=args.mapping_names,
            )
            done = f"runtime schema cache for '{args.developer_name}'"
        else:
            eprint(CONTEXT_ID_SCOPE_NOTE)
            result = client.delete_instance(args.context_id)
            done = f"instance {args.context_id}"
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.dry_run:
        eprint(f"[dry-run] delete of {done} only logged — nothing evicted.")
        return 0

    if args.json:
        print(json.dumps(result if isinstance(result, (dict, list)) else {}, indent=2))
    else:
        eprint(f"Cleared {done}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
