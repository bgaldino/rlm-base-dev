#!/usr/bin/env python3
"""Query / inspect a runtime Context Service instance (read-only).

Two read modes against a live ``contextId``:

* records — ``POST /connect/contexts/query-record?children=true|false`` — the
  hydrated node/attribute tree (Query Context Record Result). Flattened to rows
  with a ``depth`` column; stringified compound values (e.g. Address) are decoded
  in the human view (left raw in ``--json``).
* tags — ``--tags TAG …`` → ``POST /connect/contexts/query-tags`` (or
  ``/query-tags-leaner`` with ``--leaner``) — read attribute values by tag.

Read-only against the org (though it POSTs, it does not mutate) — so it runs even
under a dry-run session. Auth is delegated to the ``sf`` CLI — no access token is
handled. ``--target-org`` is the SF CLI alias (e.g. ``rlm-base__beta``), never the
CCI alias.

The ``contextId`` is request-scoped (see the note this prints) — an id minted by a
separate ``create_context_instance.py`` call is only queryable here if the org's
Instance-Reuse setting is on and you are within contextTtl; otherwise use
``context_session.py``.

Usage:
    python scripts/context_service/instance/query_context_instance.py \
        --target-org rlm-base__beta --context-id <uuid>
    python scripts/context_service/instance/query_context_instance.py \
        --target-org rlm-base__beta --context-id <uuid> --tags Price__c Discount__c --leaner
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._apply import Transport  # noqa: E402
from scripts.context_service._client import ContextClientError, DEFAULT_API_VERSION, eprint  # noqa: E402
from scripts.context_service._runtime import RuntimeContextClient, decode_compound_fields, flatten_query_records  # noqa: E402
from scripts.context_service._runtime_cli import CONTEXT_ID_SCOPE_NOTE  # noqa: E402


def _print_records_human(result: dict) -> None:
    print(f"contextId: {result.get('contextId')}  "
          f"isSuccess={result.get('isSuccess')}  isDone={result.get('isDone')}")
    rows = flatten_query_records(result)
    if not rows:
        print("(no query records)")
        return
    print(f"\n{len(rows)} record(s):")
    for row in rows:
        indent = "  " + "  " * int(row.get("depth", 0))
        bot = row.get("businessObjectType") or row.get("nodeName") or "?"
        rec_id = row.get("id") or row.get("recordId") or ""
        print(f"{indent}- {bot}" + (f" (id={rec_id})" if rec_id else ""))
        decoded = decode_compound_fields(row)
        values = decoded.get("attributesAndValues")
        if isinstance(values, dict):
            for name, value in values.items():
                rendered = json.dumps(value) if isinstance(value, (dict, list)) else value
                print(f"{indent}    {name} = {rendered}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Query / inspect a runtime Context Service instance (read-only)."
    )
    parser.add_argument("--target-org", required=True,
                        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.")
    parser.add_argument("--context-id", required=True,
                        help="Runtime contextId (opaque request-scoped handle).")
    parser.add_argument("--no-children", action="store_true",
                        help="query-record with children=false (top node only).")
    parser.add_argument("--attributes", nargs="+", metavar="NAME",
                        help="Restrict query-record to these attribute names.")
    parser.add_argument("--business-object-type-filter", metavar="NAME",
                        help="query-record businessObjectTypeFilter.")
    parser.add_argument("--query-path", nargs="+", metavar="NODE",
                        help="query-record queryPath (ordered node names).")
    parser.add_argument("--tags", nargs="+", metavar="TAG",
                        help="Read these tags (switches to query-tags mode).")
    parser.add_argument("--leaner", action="store_true",
                        help="Use query-tags-leaner (66.0) instead of query-tags.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the raw response as JSON (compound values left raw).")
    args = parser.parse_args(argv)

    eprint(CONTEXT_ID_SCOPE_NOTE)

    # Reads never mutate — force dry_run False on the transport so this also runs
    # cleanly if someone threads a dry-run flag in. (This script has no --dry-run.)
    transport = Transport(target_org=args.target_org, api_version=args.api_version,
                          dry_run=False, logger=eprint)
    client = RuntimeContextClient(transport, logger=eprint)

    try:
        if args.tags:
            result = client.query_tags(
                context_id=args.context_id, tags=args.tags, leaner=args.leaner
            )
            # Tag results are a flat name→value shape; JSON is the clear rendering
            # for both modes.
            print(json.dumps(result, indent=2))
            return 0

        result = client.query_record(
            context_id=args.context_id,
            children=not args.no_children,
            attributes=args.attributes,
            business_object_type_filter=args.business_object_type_filter,
            query_path=args.query_path,
        )
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    result = result if isinstance(result, dict) else {}
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    _print_records_human(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
